import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Users, CheckCircle, Clock } from 'lucide-react';

const mockPatients = [
  { id: 1, name: 'Sarah Jenkins', compliance: 95, unreadAlerts: 0, lastSession: 'Today' },
  { id: 2, name: 'Michael Chen', compliance: 42, unreadAlerts: 2, lastSession: '3 days ago' },
];

export default function DoctorDashboard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Clinic Dashboard</h2>
          <p className="text-slate-500">Overview of patient tele-rehab progress.</p>
        </div>
        <button 
          onClick={() => navigate('/doctor/onboard')}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700 transition"
        >
          <Users size={18} />
          <span>Register New Patient</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-100 rounded-xl">
              <CheckCircle className="text-emerald-600" size={24} />
            </div>
            <div>
              <p className="text-slate-500 text-sm font-medium">Avg Compliance</p>
              <p className="text-2xl font-bold text-slate-800">82%</p>
            </div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-100 rounded-xl">
              <Activity className="text-amber-600" size={24} />
            </div>
            <div>
              <p className="text-slate-500 text-sm font-medium">Flagged Forms</p>
              <p className="text-2xl font-bold text-slate-800">2 Patients</p>
            </div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-xl">
              <Clock className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-slate-500 text-sm font-medium">Sessions Today</p>
              <p className="text-2xl font-bold text-slate-800">14</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="font-semibold text-slate-800 text-lg">Active Patients</h3>
        </div>
        <div className="divide-y divide-slate-100">
          {mockPatients.map((patient) => (
            <div 
              key={patient.id} 
              onClick={() => navigate(`/doctor/patient/${patient.id}`)}
              className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 cursor-pointer transition"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-600">
                  {patient.name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-medium text-slate-800">{patient.name}</h4>
                  <p className="text-sm text-slate-500">Last active: {patient.lastSession}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-sm font-medium text-slate-800">{patient.compliance}% Compliance</div>
                  <div className="w-24 h-2 bg-slate-200 rounded-full mt-1">
                    <div 
                      className={`h-full rounded-full ${patient.compliance > 80 ? 'bg-emerald-500' : 'bg-red-500'}`} 
                      style={{ width: `${patient.compliance}%` }} 
                    />
                  </div>
                </div>
                {patient.unreadAlerts > 0 && (
                  <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-bold">
                    {patient.unreadAlerts} Error flagged
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
