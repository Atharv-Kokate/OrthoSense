import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Settings, CheckCircle } from 'lucide-react';

export default function ClinicalOnboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [patientData, setPatientData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    condition: 'Post-Op ACL Reconstruction',
    dateOfSurgery: '',
  });

  const handleNext = (e) => {
    e.preventDefault();
    if (step === 1) setStep(2);
    else if (step === 2) {
      // Setup the Golden Rep Capture Session
      navigate('/doctor/capture-golden-rep', { state: { patient: patientData } });
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-800">New Patient Onboarding</h2>
        <p className="text-slate-500">Register a patient and capture their biometric baseline.</p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-4 mb-8">
        <div className={`flex items-center gap-2 ${step >= 1 ? 'text-indigo-600 font-bold' : 'text-slate-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-indigo-100' : 'bg-slate-100'}`}>1</div>
          <span>Patient Details</span>
        </div>
        <div className="flex-1 h-1 bg-slate-200"><div className={`h-full bg-indigo-600 transition-all ${step >= 2 ? 'w-full' : 'w-0'}`}></div></div>
        <div className={`flex items-center gap-2 ${step >= 2 ? 'text-indigo-600 font-bold' : 'text-slate-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-indigo-100' : 'bg-slate-100'}`}>2</div>
          <span>Supervised Golden Rep</span>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <form onSubmit={handleNext} className="space-y-6">
          {step === 1 && (
            <div className="space-y-4 animate-in fade-in">
              <h3 className="text-lg font-bold text-slate-800 mb-4 border-b pb-2">Step 1: Clinical Profile</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                  <input type="text" required className="w-full px-4 py-2 border rounded-lg bg-slate-50 focus:ring-2 focus:ring-indigo-500" 
                    value={patientData.firstName} onChange={(e) => setPatientData({...patientData, firstName: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                  <input type="email" required className="w-full px-4 py-2 border rounded-lg bg-slate-50 focus:ring-2 focus:ring-indigo-500"
                    placeholder="alex@example.com"
                    value={patientData.email} onChange={(e) => setPatientData({...patientData, email: e.target.value})} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Clinical Condition</label>
                  <select className="w-full px-4 py-2 border rounded-lg bg-slate-50"
                    value={patientData.condition} onChange={(e) => setPatientData({...patientData, condition: e.target.value})}>
                    <option>Post-Op ACL Reconstruction</option>
                    <option>Total Knee Arthroplasty (TKA)</option>
                    <option>Meniscus Repair</option>
                    <option>General Knee Osteoarthritis</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Date of Surgery</label>
                  <input type="date" required className="w-full px-4 py-2 border rounded-lg bg-slate-50"
                    value={patientData.dateOfSurgery} onChange={(e) => setPatientData({...patientData, dateOfSurgery: e.target.value})} />
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-in slide-in-from-right-4">
              <h3 className="text-lg font-bold text-slate-800 mb-4 border-b pb-2">Step 2: Initialize Clinical Baseline</h3>
              <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 flex gap-4 items-start">
                <Settings className="text-indigo-600 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-bold text-indigo-900">Prepare for "Golden Rep" Calibration</h4>
                  <p className="text-indigo-700 mt-2 text-sm">
                    In the next step, please guide {patientData.firstName} into the camera frame. 
                    Ask them to perform <b>3 perfect, maximal-effort, pain-free repetitions</b>. 
                    The OrthoSense Deep Learning engine will establish their baseline target Range Of Motion (ROM) and biomechanical symmetry based exclusively on these supervised reps.
                  </p>
                </div>
              </div>
              
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" defaultChecked className="w-5 h-5 rounded text-indigo-600 border-slate-300 focus:ring-indigo-500" />
                  <div>
                    <p className="font-bold text-slate-700">Enable AI Auto-Adaptation</p>
                    <p className="text-sm text-slate-500">The platform will dynamically adjust their target ROM parameters by ±2° per week based on their at-home compliance and error rates.</p>
                  </div>
                </label>
              </div>
            </div>
          )}

          <div className="pt-6 flex justify-end gap-3">
            {step > 1 && (
              <button type="button" onClick={() => setStep(1)} className="px-6 py-2 border rounded-lg font-semibold text-slate-600 hover:bg-slate-50">
                Back
              </button>
            )}
            <button type="submit" className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-bold shadow-sm hover:bg-indigo-700 flex items-center gap-2">
              {step === 1 ? 'Continue to Calibration' : <><CheckCircle size={18}/> Launch Clinic Camera</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}