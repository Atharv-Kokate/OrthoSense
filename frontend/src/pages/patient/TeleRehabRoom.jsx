import React, { useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import VideoConsultation from '../../components/VideoConsultation';

export default function TeleRehabRoom() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const patientId = location.state?.patientId || localStorage.getItem('user_id');

  const handleEndCall = () => {
    navigate('/patient/dashboard');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
            Live Tele-Rehab Consultation
          </h2>
          <p className="text-slate-500 mt-1">
            Connected securely to your physical therapist.
          </p>
        </div>
        <button
          onClick={handleEndCall}
          className="px-6 py-2 bg-slate-100 text-slate-700 hover:bg-red-50 hover:text-red-600 rounded-xl font-bold transition-all focus:ring-4 focus:ring-red-100"
        >
          Leave Room
        </button>
      </div>

      <div className="bg-slate-900 rounded-2xl shadow-2xl overflow-hidden aspect-video relative flex flex-col items-center justify-center border border-slate-800">
        <VideoConsultation
          roomId={roomId || patientId?.toString()}
          isInitiator={false}
          onEndCall={handleEndCall}
          customClass="w-full h-full"
        />
      </div>
    </div>
  );
}
