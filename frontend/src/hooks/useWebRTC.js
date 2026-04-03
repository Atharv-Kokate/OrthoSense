import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebRTC(roomId, isInitiator, externalStream = null) {
    const [localStream, setLocalStream] = useState(null);
    const [remoteStream, setRemoteStream] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    
    const peerConnection = useRef(null);
    const socket = useRef(null);
    const localStreamRef = useRef(null);
    const mountedRef = useRef(false);
    const ownsStream = useRef(false);
    
    // Config for ICE servers
    const config = {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ]
    };

    const endCall = useCallback(() => {
        console.log('[WebRTC] endCall() invoked');
        if (localStreamRef.current && ownsStream.current) {
            localStreamRef.current.getTracks().forEach(track => track.stop());
        }
        localStreamRef.current = null;
        ownsStream.current = false;
        
        if (peerConnection.current) {
            peerConnection.current.close();
            peerConnection.current = null;
        }
        if (socket.current) {
            socket.current.close();
            socket.current = null;
        }
        setLocalStream(null);
        setRemoteStream(null);
        setIsConnected(false);
    }, []);

    const initializeConnection = useCallback(async () => {
        if (peerConnection.current || socket.current) {
            console.log('[WebRTC] Skipping duplicate initialization');
            return;
        }

        mountedRef.current = true;

        try {
            let stream = null;

            if (externalStream) {
                // Patient side: reuse the webcam stream already open for MediaPipe
                console.log('[WebRTC] Using SHARED external stream (camera already open)');
                stream = externalStream;
                ownsStream.current = false;
            } else {
                // Doctor side or standalone — try to get our own camera
                // Use graceful fallback: video+audio → audio-only → receive-only
                try {
                    // Try full media for both sides by default
                    let constraints = { video: true, audio: true };
                    console.log(`[WebRTC] Requesting media with constraints:`, constraints);
                    
                    try {
                        stream = await navigator.mediaDevices.getUserMedia(constraints);
                    } catch (e) {
                         console.warn('Camera busy or unavailable (likely testing on same device), falling back to audio only.', e);
                         constraints = { video: false, audio: true };
                         stream = await navigator.mediaDevices.getUserMedia(constraints);
                    }
                    
                    ownsStream.current = true;
                } catch (mediaErr) {
                    console.warn(`[WebRTC] getUserMedia failed: ${mediaErr.message}. Proceeding in receive-only mode.`);
                    // Proceed without local media — we can still RECEIVE the other party's video/audio
                    stream = null;
                    ownsStream.current = false;
                }
            }
            
            if (!mountedRef.current) {
                console.log('[WebRTC] Component unmounted during setup, cleaning up');
                if (stream && ownsStream.current) {
                    stream.getTracks().forEach(track => track.stop());
                }
                return;
            }

            if (stream) {
                setLocalStream(stream);
                localStreamRef.current = stream;
            }

            // 2. Setup Peer Connection (always, even without local media)
            const pc = new RTCPeerConnection(config);
            peerConnection.current = pc;
            
            // Add local tracks IF we have them
            if (stream) {
                stream.getTracks().forEach(track => {
                    pc.addTrack(track, stream);
                });
            }

            // Handle incoming remote tracks
            pc.ontrack = (event) => {
                console.log('[WebRTC] Remote track received!', event.track.kind);
                setRemoteStream(event.streams[0]);
                setIsConnected(true);
            };

            pc.onconnectionstatechange = () => {
                console.log('[WebRTC] Connection state:', pc.connectionState);
                if (pc.connectionState === 'connected') setIsConnected(true);
                if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') setIsConnected(false);
            };

            pc.oniceconnectionstatechange = () => {
                console.log('[WebRTC] ICE connection state:', pc.iceConnectionState);
            };

            // 3. Setup WebSocket Signaling
            const clientId = `${isInitiator ? 'doctor' : 'patient'}_${Math.random().toString(36).substring(7)}`;
            const wsUrl = `ws://${window.location.hostname}:8000/ws/signaling/${roomId}/${clientId}`;
            console.log(`[WebRTC] Connecting to signaling server: ${wsUrl}`);
            const ws = new WebSocket(wsUrl);
            socket.current = ws;
            
            const pendingCandidates = [];
            let offerCreated = false;

            pc.onicecandidate = (event) => {
                if (event.candidate && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
                }
            };

            ws.onopen = async () => {
                console.log(`[WebRTC] Signaling WebSocket OPEN. isInitiator=${isInitiator}, roomId=${roomId}`);
                ws.send(JSON.stringify({ type: 'hello' }));
            };

            ws.onerror = (err) => {
                console.error('[WebRTC] Signaling WebSocket ERROR:', err);
            };

            ws.onclose = (event) => {
                console.log(`[WebRTC] Signaling WebSocket CLOSED. code=${event.code}`);
            };

            ws.onmessage = async (event) => {
                const message = JSON.parse(event.data);
                console.log(`[WebRTC] Received signal: ${message.type}`);

                if (message.type === 'hello') {
                    if (isInitiator && !offerCreated) {
                        offerCreated = true;
                        console.log('[WebRTC] Creating SDP offer (initiator)...');
                        const offer = await pc.createOffer({
                            offerToReceiveVideo: true,
                            offerToReceiveAudio: true
                        });
                        await pc.setLocalDescription(offer);
                        ws.send(JSON.stringify({ type: 'offer', offer }));
                    } else if (!isInitiator) {
                        ws.send(JSON.stringify({ type: 'ready' }));
                    }
                } else if (message.type === 'ready') {
                    if (isInitiator && !offerCreated) {
                        offerCreated = true;
                        console.log('[WebRTC] Peer ready, creating SDP offer...');
                        const offer = await pc.createOffer({
                            offerToReceiveVideo: true,
                            offerToReceiveAudio: true
                        });
                        await pc.setLocalDescription(offer);
                        ws.send(JSON.stringify({ type: 'offer', offer }));
                    }
                } else if (message.type === 'offer' && !isInitiator) {
                    console.log('[WebRTC] Setting remote offer & creating answer...');
                    await pc.setRemoteDescription(new RTCSessionDescription(message.offer));
                    const answer = await pc.createAnswer(); 
                    await pc.setLocalDescription(answer);   
                    ws.send(JSON.stringify({ type: 'answer', answer }));
                    
                    while (pendingCandidates.length > 0) {
                        await pc.addIceCandidate(pendingCandidates.shift());
                    }
                } else if (message.type === 'answer' && isInitiator) {
                    console.log('[WebRTC] Setting remote answer...');
                    await pc.setRemoteDescription(new RTCSessionDescription(message.answer));
                    
                    while (pendingCandidates.length > 0) {
                        await pc.addIceCandidate(pendingCandidates.shift());
                    }
                } else if (message.type === 'candidate') {
                    const candidate = new RTCIceCandidate(message.candidate);
                    if (pc.remoteDescription) {
                        await pc.addIceCandidate(candidate);
                    } else {
                        pendingCandidates.push(candidate);
                    }
                }
            };
        } catch (error) {
            console.error('[WebRTC] Error initializing WebRTC:', error);
        }
    }, [roomId, isInitiator, externalStream]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            console.log('[WebRTC] useEffect cleanup (unmount)');
            mountedRef.current = false;
            endCall();
        };
    }, [endCall]);

    return { localStream, remoteStream, isConnected, initializeConnection, endCall };
}
