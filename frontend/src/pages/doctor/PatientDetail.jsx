import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Calendar, Award, AlertTriangle, ArrowLeft, Video } from 'lucide-react';
import VideoConsultation from '../../components/VideoConsultation';

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [showConsultation, setShowConsultation] = useState(false);

  // Simulated Medical Telemetry Data fetched from Postgres
  const [telemetryData, setTelemetryData] = useState([]);

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
          <button className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none flex items-center justify-center gap-2">
            Export Report
          </button>
          <button onClick={() => setShowConsultation(true)} className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-500 hover:bg-indigo-400 focus:outline-none flex items-center justify-center gap-2">
            <Video size={16} /> Live Consultation
          </button>
          <button className="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-700 hover:bg-indigo-800 focus:outline-none">
            Adjust Prescription
          </button>
        </div>
      </div>

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

      {/* KPI Cards */}
      <div className="grid border border-gray-200 bg-white rounded-xl shadow-sm mb-8 sm:grid-cols-4 overflow-hidden">
        <div className="p-6 border-b sm:border-b-0 sm:border-r border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <Activity className="h-4 w-4 mr-2 text-indigo-500" /> Target ROM
          </div>
          <div className="text-3xl font-bold text-gray-900">90&deg;</div>
          <p className="text-sm text-green-600 mt-1 flex items-center">&darr; 30&deg; Improvement</p>
        </div>
        <div className="p-6 border-b sm:border-b-0 sm:border-r border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <Award className="h-4 w-4 mr-2 text-indigo-500" /> Form Accuracy
          </div>
          <div className="text-3xl font-bold text-gray-900">98%</div>
          <p className="text-sm text-green-600 mt-1">&uarr; +16% since start</p>
        </div>
        <div className="p-6 border-b sm:border-b-0 sm:border-r border-gray-200">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <Calendar className="h-4 w-4 mr-2 text-indigo-500" /> Total Sessions
          </div>
          <div className="text-3xl font-bold text-gray-900">24</div>
          <p className="text-sm text-gray-500 mt-1">High compliance</p>
        </div>
        <div className="p-6">
          <div className="flex items-center text-sm font-medium text-gray-500 mb-2">
            <AlertTriangle className="h-4 w-4 mr-2 text-red-500" /> Knee Cave Risks
          </div>
          <div className="text-3xl font-bold text-gray-900">0</div>
          <p className="text-sm text-green-600 mt-1">Fully resolved</p>
        </div>
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Chart 1: ROM Improvement */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Range of Motion (ROM) Progression</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryData}>
                <defs>
                  <linearGradient id="colorRom" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dy={10} />
                {/* Reversed Y Axis because lower angle = deeper squat */}
                <YAxis domain={[80, 130]} reversed={true} axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dx={-10} />
                <Tooltip 
                  contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
                  formatter={(value) => [`${value}°`, 'Deepest Squat Angle']}
                />
                <Area type="monotone" dataKey="maxRom" stroke="#4f46e5" strokeWidth={3} fillOpacity={1} fill="url(#colorRom)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="text-sm text-gray-500 mt-4 text-center">Lower angle indicates deeper, healthier squat depth over time.</p>
        </div>

        {/* Chart 2: Form Accuracy vs Errors */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">BiLSTM AI Form Tracking</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetryData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dy={10} />
                <YAxis domain={[0, 100]} yAxisId="left" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dx={-10} />
                <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{fill: '#EF4444', fontSize: 12}} dx={10} />
                <Tooltip 
                   contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
                />
                <Line yAxisId="left" type="monotone" name="Overall Accuracy %" dataKey="avgScore" stroke="#10b981" strokeWidth={3} dot={{r: 4, fill: '#10b981'}} />
                <Line yAxisId="right" type="monotone" name="Major Errors" dataKey="majorErrors" stroke="#ef4444" strokeWidth={3} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
    </div>
  );
}