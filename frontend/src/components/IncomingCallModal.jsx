import React, { useState, useEffect } from 'react';
import { Phone, PhoneOff, Video } from 'lucide-react';
import { callService } from '../services/api';

export default function IncomingCallModal({ patientId, onAccept, onDismiss }) {
  const [incomingCall, setIncomingCall] = useState(null);
  const [ringAudio] = useState(() => {
    // Create a simple oscillating ring tone
    if (typeof window !== 'undefined' && 'AudioContext' in window) {
      return new (window.AudioContext || window.webkitAudioContext)();
    }
    return null;
  });

  // Poll for incoming calls every 3 seconds
  useEffect(() => {
    if (!patientId) return;

    const checkForCalls = async () => {
      try {
        const result = await callService.checkIncomingCall(patientId);
        if (result.has_call) {
          setIncomingCall(result);
        } else {
          setIncomingCall(null);
        }
      } catch (err) {
        // Silently fail — patient might just not have network
      }
    };

    // Check immediately, then poll
    checkForCalls();
    const interval = setInterval(checkForCalls, 3000);
    return () => clearInterval(interval);
  }, [patientId]);

  const handleAccept = async () => {
    try {
      await callService.acceptCall(patientId);
      if (onAccept) onAccept(incomingCall.room_id);
    } catch (err) {
      console.error('Error accepting call:', err);
    }
  };

  const handleDismiss = async () => {
    try {
      await callService.dismissCall(patientId);
      setIncomingCall(null);
      if (onDismiss) onDismiss();
    } catch (err) {
      console.error('Error dismissing call:', err);
    }
  };

  if (!incomingCall) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-sm w-full mx-4 flex flex-col items-center gap-6 animate-bounce-in">
        {/* Pulsing Video Icon */}
        <div className="relative">
          <div className="absolute inset-0 bg-indigo-500 rounded-full animate-ping opacity-30" style={{ animationDuration: '1.5s' }}></div>
          <div className="relative w-20 h-20 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-200">
            <Video size={36} className="text-white" />
          </div>
        </div>

        {/* Call Info */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-1">Incoming Call</h2>
          <p className="text-slate-500 text-lg">
            <span className="font-semibold text-indigo-600">{incomingCall.doctor_name}</span> wants to start a Tele-Rehab session
          </p>
        </div>

        {/* Accept / Reject Buttons */}
        <div className="flex gap-6">
          <button
            onClick={handleDismiss}
            className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center text-white shadow-lg hover:bg-red-600 transition-all hover:scale-110 active:scale-95"
            title="Decline"
          >
            <PhoneOff size={28} />
          </button>
          <button
            onClick={handleAccept}
            className="w-16 h-16 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-lg hover:bg-emerald-600 transition-all hover:scale-110 active:scale-95 animate-pulse"
            title="Accept"
          >
            <Phone size={28} />
          </button>
        </div>
      </div>

      <style>{`
        @keyframes bounce-in {
          0% { transform: scale(0.3); opacity: 0; }
          50% { transform: scale(1.05); }
          70% { transform: scale(0.95); }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-bounce-in { animation: bounce-in 0.5s ease-out; }
        .animate-fade-in { animation: fade-in 0.3s ease-out; }
      `}</style>
    </div>
  );
}
