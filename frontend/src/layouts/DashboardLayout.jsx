import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';

export default function DashboardLayout({ role }) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 font-sans flex flex-col">
      <nav className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-50">
        <div 
          className="flex items-center gap-3 cursor-pointer" 
          onClick={() => navigate(role === 'doctor' ? '/doctor/dashboard' : '/patient/dashboard')}
        >
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span className="text-white font-bold tracking-tight">OS</span>
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-700 to-blue-500 bg-clip-text text-transparent hidden sm:block">
            OrthoSense Clinical AI
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="px-4 py-2 rounded-full bg-slate-100 text-slate-600 font-medium text-sm hidden sm:block">
            {role === 'doctor' ? 'Dr. Smith' : 'Sarah Jenkins'}
          </div>
          <button 
            onClick={() => navigate('/login')}
            className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg font-semibold text-sm hover:bg-slate-50 transition"
          >
            Log Out
          </button>
        </div>
      </nav>
      
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  );
}
