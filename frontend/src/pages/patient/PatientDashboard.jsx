import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlayCircle, Award, Calendar, Activity, Video, Lock, Unlock, CheckCircle } from 'lucide-react';
import { clinicalService, callService } from '../../services/api';
import IncomingCallModal from '../../components/IncomingCallModal';

const fetchJourney = async (patientId) => {
  const res = await fetch(`http://localhost:8000/api/patients/${patientId}/journey`);
  if (!res.ok) {
      if (res.status === 404) return { status: 'no_active_program' };
      throw new Error('Unable to load journey map');
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
          console.warn('Journey map not found', e);
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
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <IncomingCallModal 
        patientId={data?.patient_id} 
        onAccept={(roomId) => navigate(`/patient/tele-rehab/${roomId}`)} 
        onDismiss={() => {}} 
      />
      
      <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 bg-gradient-to-br from-indigo-50 to-white">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Welcome back, {data?.patient_name}!</h1>
        <p className="text-slate-500 text-lg">Your recovery condition: <span className="font-semibold text-slate-700">{data?.condition}</span></p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4">
            <span className="text-slate-500 font-medium flex items-center gap-2"><Award size={18} className="text-indigo-500"/> Average Form Score</span>
          </div>
          <div>
            <h3 className="text-4xl font-bold text-slate-800">{data?.average_form_score_7d || 0}%</h3>
            <p className="text-sm text-green-600 mt-1 font-medium bg-green-50 inline-block px-2 py-1 rounded-md">Last 7 days</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4">
            <span className="text-slate-500 font-medium flex items-center gap-2"><Calendar size={18} className="text-indigo-500"/> Sessions Completed</span>
          </div>
          <div>
            <h3 className="text-4xl font-bold text-slate-800">{data?.recent_sessions?.length || 0}</h3>
            <p className="text-sm text-slate-500 mt-1">Keep up the good work!</p>
          </div>
        </div>
      </div>

      <div className="bg-white border text-center border-slate-100 rounded-3xl p-6 shadow-sm overflow-hidden mt-6">
          <h2 className="text-xl font-bold text-slate-800 mb-4 text-left border-b pb-4">Open Workouts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button onClick={() => navigate('/patient/session/squat')} className="p-6 bg-slate-50 hover:bg-indigo-50 border border-slate-100 rounded-2xl transition-all group text-left">
                  <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                          <Activity size={24} />
                      </div>
                      <div>
                          <h4 className="font-bold text-slate-800 group-hover:text-indigo-800">Deep Squats</h4>
                          <p className="text-sm text-slate-500">Free Practice</p>
                      </div>
                  </div>
              </button>
              <button onClick={() => navigate('/patient/session/lunge')} className="p-6 bg-slate-50 hover:bg-emerald-50 border border-slate-100 rounded-2xl transition-all group text-left">
                  <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                          <Activity size={24} />
                      </div>
                      <div>
                          <h4 className="font-bold text-slate-800 group-hover:text-emerald-800">Forward Lunges</h4>
                          <p className="text-sm text-slate-500">Free Practice</p>
                      </div>
                  </div>
              </button>
          </div>
      </div>

      {journeyData && journeyData.status !== 'no_active_program' ? (
        <div className="bg-indigo-50 border border-indigo-100 rounded-3xl p-8 shadow-inner relative overflow-hidden">
            <h2 className="text-2xl font-bold text-indigo-900 mb-6">Your Recovery Journey</h2>

            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-12 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-1 before:bg-gradient-to-b before:from-indigo-400 before:via-indigo-200 before:to-slate-200">
                {journeyData.phases?.map((phase, idx) => {
                    const isCompleted = idx < journeyData.phases.findIndex(p => p.is_current);
                    const isCurrent = phase.is_current;
                    const isLocked = !isCompleted && !isCurrent;
                    
                    return (
                        <div key={idx} className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${isCurrent ? 'is-active' : ''}`}>
                            <div className={`flex items-center justify-center w-24 h-24 rounded-full border-4 shadow-xl shrink-0 z-10 ${isCompleted ? 'bg-emerald-500 border-emerald-200 text-white' : isCurrent ? 'bg-indigo-600 border-indigo-200 text-white ring-4 ring-indigo-100 animate-pulse' : 'bg-slate-200 border-slate-300 text-slate-400'} md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2`}>
                                {isCompleted ? <CheckCircle size={32}/> : isCurrent ? <Unlock size={32}/> : <Lock size={32}/>}
                            </div>

                            <div className="w-[calc(100%-7rem)] md:w-[calc(50%-4rem)] p-6 bg-white rounded-3xl shadow flex flex-col gap-3">
                                <span className={`font-black uppercase tracking-wider text-xs ${isCompleted ? 'text-emerald-500' : isCurrent ? 'text-indigo-600' : 'text-slate-400'}`}>Phase {phase.phase_order}</span>
                                <h3 className="font-bold text-xl text-slate-800">{phase.name}</h3>
                                <p className="text-slate-500 text-sm leading-relaxed">{phase.description}</p>
                                
                                {isCurrent && (
                                    <button
                                        onClick={() => navigate(`/patient/session/${phase.exercises[0]?.type || 'squat'}`)}
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
