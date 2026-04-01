import React from 'react';
import { useNavigate } from 'react-router-dom';
import { PlayCircle, Award, Calendar } from 'lucide-react';

export default function PatientDashboard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="bg-gradient-to-br from-indigo-600 to-blue-500 rounded-3xl p-8 text-white shadow-lg shadow-indigo-200">
        <h2 className="text-3xl font-bold mb-2">Good morning, Sarah!</h2>
        <p className="text-indigo-100 mb-8 max-w-lg leading-relaxed">
          You're doing great. You have 1 exercise prescribed by Dr. Smith today to help improve your knee mobility.
        </p>

        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-inner">
              <PlayCircle className="text-indigo-600" size={32} />
            </div>
            <div>
              <h3 className="text-xl font-bold tracking-tight">Deep Squats</h3>
              <p className="text-indigo-100 flex items-center gap-2 mt-1">
                <span>3 Sets of 10 Reps</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-300"></span>
                <span>Target ROM: 100°</span>
              </p>
              {/* Dynamic Auto-Adapt Message */}
              <div className="mt-2 text-xs font-bold bg-indigo-500/40 border border-indigo-400 text-indigo-50 px-3 py-1 rounded-full inline-block">
                ✨ Goal auto-adjusted -2° today based on your progress!
              </div>
            </div>
          </div>
          
          <button 
            onClick={() => navigate('/patient/session/squat')}
            className="w-full md:w-auto px-8 py-3 bg-white text-indigo-700 hover:bg-slate-50 transition rounded-xl font-bold shadow-md transform hover:-translate-y-0.5 active:translate-y-0"
          >
            Start AI Session
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex items-center gap-4">
          <div className="p-4 bg-emerald-100 rounded-2xl">
            <Award className="text-emerald-600" size={28} />
          </div>
          <div>
            <h4 className="text-slate-500 font-medium text-sm">Weekly Streak</h4>
            <p className="text-2xl font-bold text-slate-800">4 Days</p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex items-center gap-4">
          <div className="p-4 bg-blue-100 rounded-2xl">
            <Calendar className="text-blue-600" size={28} />
          </div>
          <div>
            <h4 className="text-slate-500 font-medium text-sm">Next Check-in</h4>
            <p className="text-2xl font-bold text-slate-800">Oct 24, 2026</p>
          </div>
        </div>
      </div>
    </div>
  );
}
