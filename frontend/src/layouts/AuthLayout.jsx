import React from 'react';
import { Outlet } from 'react-router-dom';
import { Activity } from 'lucide-react';

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center mx-auto mb-4">
            <Activity className="text-white" size={28} />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-700 to-blue-500 bg-clip-text text-transparent">
            OrthoSense
          </h1>
          <p className="text-slate-500 mt-2">Clinical AI Motion Tracking</p>
        </div>
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200 border border-slate-100 overflow-hidden">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
