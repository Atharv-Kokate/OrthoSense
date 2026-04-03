import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Calendar, Award, AlertTriangle, ArrowLeft, Video, TrendingUp, Clock, FileText, CheckCircle, Flame, ShieldAlert, HeartPulse } from 'lucide-react';
import RecordExerciseModal from '../../components/RecordExerciseModal';
import VideoConsultation from '../../components/VideoConsultation';
import { callService, clinicalService } from '../../services/api';

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [showConsultation, setShowConsultation] = useState(false);
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [recordingState, setRecordingState] = useState('idle');
  const [isApproving, setIsApproving] = useState(false);

  // Simulated Medical Telemetry Data fetched from Postgres
  const [telemetryData, setTelemetryData] = useState([]);
  
  // AI Biomechanical Errors Data
  const [biomechanicalErrors, setBiomechanicalErrors] = useState([]);
  
  // Patient Timeline & Alerts
  const [timelineEvents, setTimelineEvents] = useState([]);

  useEffect(() => {
    // In production: fetch(`/api/patients/${id}/telemetry`)
    setTimeout(() => {
      setTelemetryData([
        { date: 'Mar 15', maxRom: 120, avgScore: 82, majorErrors: 3 },
        { date: 'Mar 18', maxRom: 115, avgScore: 85, majorErrors: 2 },
        { date: 'Mar 21', maxRom: 108, avgScore: 89, majorErrors: 2 },
        { date: 'Mar 25', maxRom: 102, avgScore: 92, majorErrors: 1 },
        { date: 'Mar 28', maxRom: 95, avgScore: 96, majorErrors: 0 },
        { date: 'Current', maxRom: 90, avgScore: 98, majorErrors: 0 },
      ]);
      
      setBiomechanicalErrors([
        { name: 'Knee Valgus (Inward Cave)', frequency: 2, trend: 'down', critical: true },
        { name: 'Heel Lift', frequency: 15, trend: 'down', critical: false },
        { name: 'Asymmetric Weight Shift', frequency: 8, trend: 'stable', critical: false },
        { name: 'Inadequate Depth', frequency: 5, trend: 'down', critical: false }
      ]);

      setTimelineEvents([
        { id: 1, type: 'milestone', date: 'Today, 10:00 AM', title: 'Target Depth Reached', desc: 'Achieved 90° knee flexion for the first time without compensation.' },
        { id: 2, type: 'alert', date: 'Yesterday, 4:30 PM', title: 'Session Aborted', desc: 'Patient stopped set 3 early. Self-reported pain level 6/10.' },
        { id: 3, type: 'system', date: 'Oct 2, 2023', title: 'AI Phase Recommendation', desc: 'Consistent >90% form score. Recommended for Phase 3 promotion.' },
        { id: 4, type: 'exercise', date: 'Oct 1, 2023', title: 'Completed Weekly Routine', desc: 'Finished 4/4 prescribed sessions for the week.' },
      ]);
      
      setLoading(false);
    }, 600);
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => navigate('/doctor/dashboard')}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="h-6 w-6 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Sarah Jenkins</h1>
            <p className="text-gray-500">Post-Op ACL Reconstruction (Squat Recovery)</p>
          </div>
        </div>
        <div className="flex space-x-3">
          
            <button 
              onClick={async () => {
                if (isApproving) return;
                setIsApproving(true);
                try {
                  await clinicalService.approvePhasePromotion(id);
                  alert('Phase successfully approved and updated for the patient!');
                  window.location.reload(); // Refresh the data
                } catch (error) {
                  alert(error.message || 'Failed to approve phase promotion');
                } finally {
                  setIsApproving(false);
                }
              }}
              className={`px-4 py-2 border border-emerald-500 rounded-lg shadow-sm text-sm font-bold text-white ${isApproving ? 'bg-emerald-400' : 'bg-emerald-500 hover:bg-emerald-600'} focus:outline-none flex items-center justify-center gap-2 ${!isApproving && 'animate-bounce'}`}
            >
              {isApproving ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                <CheckCircle size={16}/>
              )}
              {isApproving ? 'Approving...' : 'Approve Phase'}
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none flex items-center justify-center gap-2">
            Export Report
          </button>
          <button onClick={async () => {
            // Notify the patient's dashboard about the incoming call
            try {
              await callService.initiateCall(parseInt(id), 'Dr. Smith');
            } catch (err) {
              console.warn('Could not send call notification:', err);
            }
            setShowConsultation(true);
          }} className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-500 hover:bg-indigo-400 focus:outline-none flex items-center justify-center gap-2">
            <Video size={16} /> Live Consultation
          </button>
          <button className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-700 hover:bg-indigo-800 focus:outline-none">
                          Adjust Prescription
            </button>
            <button onClick={() => setShowRecordModal(true)} className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none flex items-center justify-center gap-2">
              <Activity size={16} /> Record Exercise
            </button>
          </div>
        </div>

        {/* Modal for recording custom exercise */}
        {showRecordModal && (
           <RecordExerciseModal 
             patientId={id} 
             patientName={telemetryData ? 'Sarah Jenkins' : 'Patient'} 
             onClose={() => setShowRecordModal(false)} 
           />
        )}



      {showConsultation && (
        <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
              Live Tele-Rehab Session
            </h3>
            <button 
              onClick={() => setShowConsultation(false)}
              className="text-gray-500 hover:text-gray-700 transition font-medium"
            >
              Close Consultation
            </button>
          </div>
          <VideoConsultation 
            roomId={id} // The patient ID acts as the unique room
            isInitiator={true} // Doctor initiates the call
            onEndCall={() => setShowConsultation(false)} 
          />
        </div>
      )}

      {telemetryData.length > 0 && (
        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-8 rounded-r-xl">
          <h3 className="text-amber-800 font-bold">Latest AI Target Adaptation Note</h3>
          <p className="text-amber-700 text-sm mt-1">
            Patient is &gt; 60 days post-op (Strengthening phase). Form score remains solid at 98%. Progressing target depth by 5°.
          </p>
        </div>
      )}

      {/* KPI Cards (Replaced existing ones dynamically) */}
      <div className="grid border border-gray-200 bg-white rounded-xl shadow-sm mb-8 sm:grid-cols-4 overflow-hidden">
        <div className="p-6 border-b sm:border-b-0 sm:border-r border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <Activity className="h-4 w-4 mr-2 text-indigo-500" /> Current Rehab Phase
          </div>
          <div className="text-2xl font-bold text-gray-900 truncate">Strengthening</div>
          <p className="text-sm text-gray-600 mt-1 flex items-center">Day 14 / 21 Target</p>
        </div>
        <div className="p-6 border-b sm:border-b-0 sm:border-r border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <TrendingUp className="h-4 w-4 mr-2 text-indigo-500" /> Avg Form Quality
          </div>
          <div className="text-3xl font-bold text-gray-900">88%</div>
          <p className="text-sm text-green-600 mt-1 flex items-center">&uarr; 5% vs last week</p>
        </div>
        <div className="p-6 border-b sm:border-b-0 sm:border-r border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <Calendar className="h-4 w-4 mr-2 text-indigo-500" /> Program Adherence
          </div>
          <div className="text-3xl font-bold text-gray-900">4<span className="text-xl text-gray-400">/5</span></div>
          <p className="text-sm text-gray-500 mt-1">Sessions this week</p>
        </div>
        <div className="p-6">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <HeartPulse className="h-4 w-4 mr-2 text-red-500" /> Avg Pain (Self-Report)
          </div>
          <div className="text-3xl font-bold text-gray-900">3<span className="text-xl text-gray-400">/10</span></div>
          <p className="text-sm text-green-600 mt-1">&darr; Decreasing trend</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column (2/3 width) - Charts & Errors */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Split Charts Side-by-Side internally */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Chart 1: ROM Improvement */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
              <h2 className="text-md font-semibold text-gray-900 mb-4">ROM Progression</h2>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={telemetryData}>
                    <defs>
                      <linearGradient id="colorRom" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 10}} dy={10} />
                    <YAxis domain={[80, 130]} reversed={true} axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 10}} dx={-10} />
                    <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}} formatter={(value) => [`${value}°`, 'Squat Angle']} />
                    <Area type="monotone" dataKey="maxRom" stroke="#4f46e5" strokeWidth={3} fillOpacity={1} fill="url(#colorRom)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Form Accuracy vs Errors */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
              <h2 className="text-md font-semibold text-gray-900 mb-4">BiLSTM Form Tracking</h2>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={telemetryData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 10}} dy={10} />
                    <YAxis domain={[0, 100]} yAxisId="left" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 10}} dx={-10} width={30} />
                    <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{fill: '#EF4444', fontSize: 10}} dx={10} width={20} />
                    <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}} />
                    <Line yAxisId="left" type="monotone" name="Accuracy %" dataKey="avgScore" stroke="#10b981" strokeWidth={3} dot={{r: 3, fill: '#10b981'}} />
                    <Line yAxisId="right" type="monotone" name="Errors" dataKey="majorErrors" stroke="#ef4444" strokeWidth={3} strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* AI Biomechanical Insights (Error Analysis) */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-500" />
              AI Compensation Analysis
            </h2>
            <div className="space-y-5">
              {biomechanicalErrors.map((error, idx) => (
                <div key={idx}>
                  <div className="flex justify-between items-end mb-1">
                    <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
                      {error.name} 
                      {error.critical && <span className="px-2 py-0.5 rounded text-[10px] bg-red-100 text-red-700 font-bold uppercase">Critical</span>}
                    </span>
                    <span className="text-sm font-semibold text-gray-900">{error.frequency}% of reps</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${error.critical ? 'bg-red-500' : 'bg-indigo-400'}`} 
                      style={{ width: `${Math.min(error.frequency, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 capitalize flex items-center gap-1">
                    Trend: <span className={error.trend === 'down' ? 'text-green-600 font-medium' : 'text-gray-500 font-medium'}>{error.trend}</span>
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (1/3 width) - Timeline & Protocol */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Current Protocol */}
          <div className="bg-white rounded-xl shadow-sm border border-indigo-100 overflow-hidden">
            <div className="bg-indigo-50 px-5 py-4 border-b border-indigo-100 flex items-center justify-between">
              <h2 className="text-md font-bold text-indigo-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600" />
                Active Protocol
              </h2>
            </div>
            <div className="p-5">
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-indigo-700">1</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">Bodyweight Squats</p>
                    <p className="text-xs text-gray-500 mt-0.5">3 sets × 12 reps • Target 90°</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-indigo-700">2</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">Forward Lunges</p>
                    <p className="text-xs text-gray-500 mt-0.5">2 sets × 10 reps (per leg)</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-indigo-700">3</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">Single Leg Balance</p>
                    <p className="text-xs text-gray-500 mt-0.5">3 sets × 30 sec holds</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 h-full">
            <h2 className="text-md font-semibold text-gray-900 mb-5 flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-400" />
              Patient Journey & Alerts
            </h2>
            <div className="relative border-l-2 border-gray-100 ml-3 space-y-6 pb-2">
              {timelineEvents.map((event) => (
                <div key={event.id} className="relative pl-6">
                  {/* Timeline Node Icon */}
                  <span className={`absolute -left-[13px] top-0.5 w-6 h-6 rounded-full flex items-center justify-center ${
                    event.type === 'milestone' ? 'bg-green-100 text-green-600 ring-4 ring-white' :
                    event.type === 'alert' ? 'bg-red-100 text-red-600 ring-4 ring-white' :
                    event.type === 'system' ? 'bg-indigo-100 text-indigo-600 ring-4 ring-white' :
                    'bg-gray-100 text-gray-600 ring-4 ring-white'
                  }`}>
                    {event.type === 'milestone' && <Award size={12} />}
                    {event.type === 'alert' && <ShieldAlert size={12} />}
                    {event.type === 'system' && <Activity size={12} />}
                    {event.type === 'exercise' && <CheckCircle size={12} />}
                  </span>
                  
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold text-gray-500 mb-1">{event.date}</span>
                    <h4 className={`text-sm font-bold ${
                      event.type === 'alert' ? 'text-red-700' : 'text-gray-900'
                    }`}>{event.title}</h4>
                    <p className="text-xs text-gray-600 mt-1 max-w-[200px] leading-relaxed">
                      {event.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
      
    </div>
  );
}