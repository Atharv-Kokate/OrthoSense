import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Users, CheckCircle, Clock } from 'lucide-react';
import { clinicalService } from '../../services/api';

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const doctorId = localStorage.getItem('user_id');
        if (!doctorId) {
          navigate('/login');
          return;
        }
        
        const dashboardData = await clinicalService.getDoctorDashboard(doctorId);
        setData(dashboardData);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, [navigate]);

  if (isLoading) return <div className="p-8 text-center text-slate-500">Loading Clinical Dashboard...</div>;
  if (error) return <div className="p-8 text-center text-red-500">Error loading dashboard: {error}</div>;
  if (!data) return null;

  const flaggedCount = data.patients.filter(p => p.needs_attention).length;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">{data.doctor_name}'s Clinic Dashboard</h2>
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
              <p className="text-slate-500 text-sm font-medium">Total Registered</p>
              <p className="text-2xl font-bold text-slate-800">{data.total_active_patients}</p>
            </div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-amber-100 rounded-xl">
              <Activity className="text-amber-600" size={24} />
            </div>
            <div>
              <p className="text-slate-500 text-sm font-medium">Flagged Forms / Needs Attention</p>
              <p className="text-2xl font-bold text-slate-800">{flaggedCount} Patients</p>   
            </div>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-xl">
              <Clock className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-slate-500 text-sm font-medium">System Status</p>
              <p className="text-2xl font-bold text-slate-800">Online</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="font-semibold text-slate-800 text-lg">Active Patients</h3>
        </div>
        <div className="divide-y divide-slate-100">
          {data.patients.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No patients registered. Click "Register New Patient" to begin clinical onboarding.</div>
          ) : data.patients.map((patient) => (
            <div
              key={patient.patient_profile_id}
              onClick={() => navigate(`/doctor/patient/${patient.patient_profile_id}`)}
              className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 cursor-pointer transition"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-600">
                  {patient.patient_name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-medium text-slate-800">{patient.patient_name}</h4>
                  <p className="text-sm text-slate-500">
                    {patient.condition} • Last active: {patient.latest_session_date ? new Date(patient.latest_session_date).toLocaleDateString() : 'Never'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                {patient.needs_attention ? (
                  <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                    Needs Attention
                  </span>
                ) : (
                  <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                    On Track
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


