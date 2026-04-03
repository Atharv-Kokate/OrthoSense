import sys

dashboard_code = '''import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlayCircle, Award, Calendar, Activity, Video, Lock, Unlock, CheckCircle } from 'lucide-react';
import { clinicalService } from '../../services/api';
import IncomingCallModal from '../../components/IncomingCallModal';

// Dummy static fetch for journey map due to db constraints
const fetchJourney = async (patientId) => {
  const res = await fetch(http://localhost:8000/api/patients/{patientId}/journey);
  if (!res.ok) {
      if (res.status === 404) return { status: "no_active_program" };
      throw new Error("Unable to load journey map");
  }
  return await res.json();
};

export default function PatientDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [journeyData, setJourneyData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const userId = localStorage.getItem('user_id');
        if (!userId) {
          navigate('/login');
          return;
        }
        const dashboardData = await clinicalService.getPatientDashboard(userId);
        setData(dashboardData);
        
        try {
          const journey = await fetchJourney(userId);
          setJourneyData(journey);
        } catch (e) {
          console.warn("Journey map not found for this user", e);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, [navigate]);

  if (isLoading) return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-slate-500 font-medium">Loading your recovery plan...</p>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* HEADER */}
      <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Welcome back, {data?.patient_name}!</h1>
        <p className="text-slate-500 text-lg">Your recovery condition: <span className="font-semibold text-slate-700">{data?.condition}</span></p>
      </div>

      {journeyData && journeyData.status !== "no_active_program" ? (
        <div className="bg-indigo-50 border border-indigo-100 rounded-3xl p-8 shadow-inner relative overflow-hidden">
            <h2 className="text-2xl font-bold text-indigo-900 mb-6">Your Recovery Journey</h2>

            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-12 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-1 before:bg-gradient-to-b before:from-indigo-400 before:via-indigo-200 before:to-slate-200">
                {journeyData.phases?.map((phase, idx) => {
                    const isCompleted = idx < journeyData.phases.findIndex(p => p.is_current);
                    const isCurrent = phase.is_current;
                    const isLocked = !isCompleted && !isCurrent;
                    
                    return (
                        <div key={idx} className={elative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active}>
                            {/* Icon */}
                            <div className={lex items-center justify-center w-24 h-24 rounded-full border-4 shadow-xl shrink-0 z-10 
                                \
                                md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2}>
                                {isCompleted ? <CheckCircle size={32}/> : isCurrent ? <Unlock size={32}/> : <Lock size={32}/>}
                            </div>

                            {/* Card Content */}
                            <div className="w-[calc(100%-7rem)] md:w-[calc(50%-4rem)] p-6 bg-white rounded-3xl shadow flex flex-col gap-3">
                                <span className={ont-black uppercase tracking-wider text-xs \}>Phase {phase.phase_order}</span>
                                <h3 className="font-bold text-xl text-slate-800">{phase.name}</h3>
                                <p className="text-slate-500 text-sm leading-relaxed">{phase.description}</p>
                                
                                {/* Start Button if active */}
                                {isCurrent && (
                                    <button
                                        onClick={() => navigate(\/patient/session/\\)}
                                        className="mt-4 flex items-center gap-2 justify-center w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl transition-all shadow-md hover:shadow-lg active:scale-95"
                                    >
                                        <PlayCircle size={20} />
                                        Start Phase Workout
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
            
            {journeyData.is_ready_for_next_phase && (
                <div className="mt-12 bg-white/80 backdrop-blur border border-emerald-500/30 rounded-2xl p-6 text-center shadow-lg">
                    <Award size={48} className="text-emerald-500 mx-auto mb-3 animate-bounce"/>
                    <h3 className="text-xl font-bold text-emerald-900 mb-1">Phase Graduated!</h3>
                    <p className="text-emerald-700">Excellent form and consistency. Your doctor has been notified to unlock your next phase!</p>
                </div>
            )}
        </div>
      ) : (
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 text-center">
              <Calendar className="mx-auto text-slate-300 w-16 h-16 mb-4" />
              <h2 className="text-xl font-semibold text-slate-700">No Program Assigned Yet</h2>
              <p className="text-slate-500 mt-2">Your doctor will assign a gamified journey here soon.</p>
          </div>
      )}
    </div>
  );
}
'''
with open('frontend/src/pages/patient/PatientDashboard.jsx', 'w') as f:
    f.write(dashboard_code)
print("Updated Patient Dashboard JSX")