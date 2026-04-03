import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlayCircle, Award, Calendar, Activity, Video } from 'lucide-react';
import { clinicalService } from '../../services/api';
import IncomingCallModal from '../../components/IncomingCallModal';

export default function PatientDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
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
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, [navigate]);

  // When patient accepts an incoming call, navigate to session with tele-rehab enabled
  const handleAcceptCall = (roomId) => {
    navigate('/patient/session/squat', { 
      state: { 
        patientId: data?.patient_id || localStorage.getItem('user_id'), 
        isTeleRehab: true 
      } 
    });
  };

  if (isLoading) return <div className="p-8 text-center text-slate-500">Loading Patient Dashboard...</div>;
  if (error) return <div className="p-8 text-center text-red-500">Error loading dashboard: {error}</div>;
  if (!data) return null;

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Incoming Call Notification - polls the backend */}
      <IncomingCallModal 
        patientId={data.patient_id} 
        onAccept={handleAcceptCall}
      />

      <div className="bg-gradient-to-br from-indigo-600 to-blue-500 rounded-3xl p-8 text-white shadow-lg shadow-indigo-200">
        <h2 className="text-3xl font-bold mb-2">Good morning, {data.patient_name.split(' ')[0]}!</h2>       
        <p className="text-indigo-100 mb-8 max-w-lg leading-relaxed">
          You're doing great with your {data.condition} recovery. You have 1 exercise prescribed today to help improve your mobility.
        </p>

        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6">      
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-inner">
              <PlayCircle className="text-indigo-600" size={32} />
            </div>
            <div>
              <h3 className="text-xl font-bold tracking-tight">Deep Squats</h3> 
              <p className="text-indigo-100 flex items-center gap-2 mt-1">      
                <span>3 Sets of {data.current_reps_per_set} Reps</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-300"></span>
                <span>Target ROM: {data.current_target_rom}°</span>
              </p>
              <div className="mt-2 text-xs font-bold bg-indigo-500/40 border border-indigo-400 text-indigo-50 px-3 py-1 rounded-full inline-block">
                🎯 Goal dynamically sized by your Auto-Adaptation Engine!
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-2 w-full md:w-auto">
            <button
              onClick={() => navigate('/patient/session/squat', { state: { patientId: data.patient_id } })}
              className="w-full md:w-auto bg-white text-indigo-700 px-8 py-3 rounded-xl font-bold hover:bg-indigo-50 hover:shadow-lg transition flex items-center justify-center gap-2"
            >
              Start Session
            </button>
            <button
              onClick={() => navigate('/patient/session/squat', { state: { patientId: data.patient_id, isTeleRehab: true } })}
              className="w-full md:w-auto bg-indigo-500 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-400 border border-indigo-400 hover:shadow-lg transition flex items-center justify-center gap-2 shadow-inner"
            >
              <Video size={20} />
              Join Live Tele-Rehab
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4 text-slate-500">
            <Award className="text-emerald-500" />
            <h3 className="font-semibold text-slate-800">Your Average Form Score (7 Days)</h3>
          </div>
          <div className="text-3xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-4 py-1">
            {data.average_form_score_7d}%
          </div>
          <p className="mt-3 text-sm text-slate-500 flex items-center gap-2">
             Great accuracy! Keep hitting that standard.
          </p>
        </div>
        
        <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4 text-slate-500">
            <Activity className="text-blue-500" />
            <h3 className="font-semibold text-slate-800">Recent Sessions</h3>
          </div>
          <ul className="space-y-4">
            {data.recent_sessions.length === 0 ? (
              <li className="text-slate-500 italic text-sm">No sessions captured yet. Start one above!</li>
            ) : data.recent_sessions.map(session => (
              <li key={session.session_id} className="flex justify-between items-center border-b border-slate-50 pb-2 last:border-0 last:pb-0">
                <div>
                  <div className="text-sm font-bold text-slate-700">{new Date(session.session_date).toLocaleDateString()}</div>
                  <div className="text-xs text-slate-500">{session.total_reps_completed} Reps Completed</div>
                </div>
                <div className="bg-slate-100 px-3 py-1 rounded text-sm text-slate-600 font-semibold shadow-sm">
                  {session.overall_form_score}% Score
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
