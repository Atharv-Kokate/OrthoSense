import React, { useEffect, useRef } from 'react';
import { useWebRTC } from '../hooks/useWebRTC';
import { PhoneOff, Video, Mic, MicOff, User } from 'lucide-react';

export default function VideoConsultation({ roomId, isInitiator, onEndCall, customClass, sharedStream }) {
  const { localStream, remoteStream, isConnected, initializeConnection, endCall } = useWebRTC(roomId, isInitiator, sharedStream || null);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);

  useEffect(() => {
    initializeConnection();
  }, [initializeConnection]);

  useEffect(() => {
    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream]);

  useEffect(() => {
    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  const handleEndCall = () => {
    endCall();
    if (onEndCall) onEndCall();
  };

  // Check if streams have video tracks
  const hasLocalVideo = localStream && localStream.getVideoTracks().length > 0; 
  const hasRemoteVideo = remoteStream && remoteStream.getVideoTracks().length > 0;

  return (
    <div className={`bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border border-slate-700 relative w-full flex flex-col ${customClass || 'h-[600px]'}`}> 
      <div className="flex-1 relative flex items-center justify-center bg-black">
        {/* Remote Video (Full Size) */}
        {remoteStream ? (
          hasRemoteVideo ? (
            <video
              ref={remoteVideoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <div className="w-32 h-32 bg-slate-800 rounded-full flex items-center justify-center mb-6">
                <User size={64} className="text-indigo-400" />
              </div>
              <p className="text-xl font-semibold">Patient Audio Only</p>
              <p className="text-sm mt-2 opacity-50">Camera unavailable or muted</p>
              <audio ref={remoteVideoRef} autoPlay />
            </div>
          )
        ) : null}

        {/* Local Video (Picture-in-Picture) */}
        <div className="absolute bottom-24 right-6 w-48 h-64 bg-slate-800 rounded-xl overflow-hidden shadow-xl border-2 border-slate-600 z-10 aspect-[3/4]">
          {hasLocalVideo ? (
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover bg-black"
            />
          ) : localStream ? (
            /* Audio-only mode: show avatar */
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <div className="w-16 h-16 rounded-full bg-indigo-500/30 flex items-center justify-center mb-2">
                <User size={32} className="text-indigo-300" />
              </div>
              <p className="text-slate-400 text-xs">Audio Only</p>
              <div className="flex items-center gap-1 mt-1">
                <div className="w-1 h-3 bg-indigo-400 rounded-full animate-pulse"></div>
                <div className="w-1 h-4 bg-indigo-400 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
                <div className="w-1 h-2 bg-indigo-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500 text-sm">
              Camera Off
            </div>
          )}
        </div>
      </div>

      {/* Controls Bar */}
      <div className="absolute bottom-0 w-full h-20 bg-gradient-to-t from-slate-900 to-transparent flex items-center justify-center gap-6 pb-4">
        <button className="w-12 h-12 rounded-full bg-slate-700/80 backdrop-blur-md flex items-center justify-center text-white hover:bg-slate-600 transition-colors">
          <Mic size={24} />
        </button>
        <button className="w-12 h-12 rounded-full bg-slate-700/80 backdrop-blur-md flex items-center justify-center text-white hover:bg-slate-600 transition-colors">
          <Video size={24} />
        </button>
        <button 
          onClick={handleEndCall}
          className="w-14 h-14 rounded-full bg-red-500 flex items-center justify-center text-white shadow-lg hover:bg-red-600 transition-all hover:scale-105"
        >
          <PhoneOff size={28} />
        </button>
      </div>

      {/* Status Overlay */}
      <div className="absolute top-4 left-4 flex gap-2">
        <div className="px-3 py-1 rounded-full bg-slate-800/80 backdrop-blur-md border border-slate-600 text-white text-sm flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`}></div>
          {isConnected ? 'Secure Connection' : 'Connecting...'}
        </div>
      </div>
    </div>
  );
}
