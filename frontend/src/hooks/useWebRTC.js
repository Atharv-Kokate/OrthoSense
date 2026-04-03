import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebRTC(roomId, isInitiator) {
    const [localStream, setLocalStream] = useState(null);
    const [remoteStream, setRemoteStream] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    
    const peerConnection = useRef(null);
    const socket = useRef(null);
    
    // Config for ICE servers
    const config = {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ]
    };

    const initializeConnection = useCallback(async () => {
        try {
            // 1. Get Local Stream
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            setLocalStream(stream);

            // 2. Setup Peer Connection
            peerConnection.current = new RTCPeerConnection(config);
            
            // Add local tracks to peer connection
            stream.getTracks().forEach(track => {
                peerConnection.current.addTrack(track, stream);
            });

            // Handle incoming remote tracks
            peerConnection.current.ontrack = (event) => {
                setRemoteStream(event.streams[0]);
                setIsConnected(true);
            };

            // 3. Setup WebSocket Signaling
            const clientId = Math.random().toString(36).substring(7);
            const wsUrl = \ws://\:8000/ws/signaling/\/\\;
            socket.current = new WebSocket(wsUrl);

            // Handle ICE candidates
            peerConnection.current.onicecandidate = (event) => {
                if (event.candidate && socket.current.readyState === WebSocket.OPEN) {
                    socket.current.send(JSON.stringify({ type: 'candidate', candidate: event.candidate }));
                }
            };

            socket.current.onopen = async () => {
                if (isInitiator) {
                    // Create Offer
                    const offer = await peerConnection.current.createOffer();
                    await peerConnection.current.setLocalDescription(offer);
                    socket.current.send(JSON.stringify({ type: 'offer', offer }));
                }
            };

            socket.current.onmessage = async (event) => {
                const message = JSON.parse(event.data);

                if (message.type === 'offer' && !isInitiator) {
                    await peerConnection.current.setRemoteDescription(new RTCSessionDescription(message.offer));
                    const answer = await peerConnection.current.createAnswer();
                    await peerConnection.current.setLocalDescription(answer);
                    socket.current.send(JSON.stringify({ type: 'answer', answer }));
                } else if (message.type === 'answer' && isInitiator) {
                    await peerConnection.current.setRemoteDescription(new RTCSessionDescription(message.answer));
                } else if (message.type === 'candidate') {
                    await peerConnection.current.addIceCandidate(new RTCIceCandidate(message.candidate));
                }
            };
            
        } catch (error) {
            console.error('Error initializing WebRTC:', error);
        }
    }, [roomId, isInitiator]);

    const endCall = useCallback(() => {
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
        }
        if (peerConnection.current) {
            peerConnection.current.close();
        }
        if (socket.current) {
            socket.current.close();
        }
        setLocalStream(null);
        setRemoteStream(null);
        setIsConnected(false);
    }, [localStream]);

    return { localStream, remoteStream, isConnected, initializeConnection, endCall };
}
