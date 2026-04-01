import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState('patient');

  const handleLogin = (e) => {
    e.preventDefault();
    if (role === 'doctor') {
      navigate('/doctor/dashboard');
    } else {
      navigate('/patient/dashboard');
    }
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Welcome Back</h2>
      
      <div className="flex bg-slate-100 p-1 rounded-lg mb-6">
        <button
          type="button"
          onClick={() => setRole('patient')}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
            role === 'patient' ? 'bg-white shadow text-indigo-700' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Patient
        </button>
        <button
          type="button"
          onClick={() => setRole('doctor')}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
            role === 'doctor' ? 'bg-white shadow text-indigo-700' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Doctor
        </button>
      </div>

      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            type="email"
            value={role === 'doctor' ? 'doctor@orthosense.ai' : 'patient@demo.com'}
            readOnly
            className="w-full px-4 py-2 border border-slate-200 rounded-lg bg-slate-50 text-slate-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input
            type="password"
            value="*********"
            readOnly
            className="w-full px-4 py-2 border border-slate-200 rounded-lg bg-slate-50 text-slate-500"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition"
        >
          Sign In As {role.charAt(0).toUpperCase() + role.slice(1)}
        </button>
      </form>
    </div>
  );
}
