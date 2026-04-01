import React, { useRef, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { Target, CheckCircle, Save, Loader2 } from 'lucide-react';
import { usePoseEngine } from '../../hooks/usePoseEngine';
import { clinicalService } from '../../services/api';

export default function GoldenRepCapture() {
  const navigate = useNavigate();
  const location = useLocation();
  const patient = location.state?.patient || { firstName: 'Patient' };

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  const [phase, setPhase] = useState('positioning'); // 'positioning' | 'recording' | 'success' | 'saving'
  const [repsCaptured, setRepsCaptured] = useState(0);
  const [targetROM, setTargetROM] = useState(0);

  const [lowestAngleThisRep, setLowestAngleThisRep] = useState(180);
  const [isInRep, setIsInRep] = useState(false);

  // We reuse the exact same Deep Learning Computer Vision engine,
  // but instead of sending data to the WebSocket AI, we analyze it LOCALLY
  // to establish the "Golden Baseline".
  const handlePoseComputed = useCallback((telemetryPayload) => {
    if (phase !== 'recording') return;
    
    // Safety check if no data
    if (!telemetryPayload) return;

    // Use left knee for squat baseline logic for now
    const currentAngle = telemetryPayload.left_knee_angle; 
    if (!currentAngle) return;

    // Local Rep Counting State Machine for Golden Reps
    if (currentAngle < 130 && !isInRep) {
      setIsInRep(true);
    }
    
    if (isInRep && currentAngle < lowestAngleThisRep) {
      setLowestAngleThisRep(currentAngle);
    }

    if (currentAngle > 150 && isInRep) {
      // Rep completed!
      setIsInRep(false);
      setRepsCaptured(prev => {
        const nextCount = prev + 1;
        // Average out the max depths (ROM) to get the target. Wait since setTargetROM takes a setter fn
        // we can just handle the math inside the effect safely.
        setTargetROM(oldRom => oldRom === 0 ? currentAngle : (oldRom + currentAngle) / 2);
        
        if (nextCount === 3) { // Trigger only exactly when reaching 3
          setPhase('success');
          // Optional: Speak completion
          if ('speechSynthesis' in window) {
            let u = new SpeechSynthesisUtterance("Golden reps established successfully.");
            setTimeout(() => window.speechSynthesis.speak(u), 500); 
          }
        }
        return nextCount;
      });
      setLowestAngleThisRep(180); // reset for next rep
    }
  }, [phase, isInRep, lowestAngleThisRep]);

  usePoseEngine(webcamRef, canvasRef, handlePoseComputed);

  const handleSaveBaseline = async () => {
    try {
      setPhase('saving');
      
      // Auto-Adaptive flag should technically be passed from Step 2, mock it True for this demo
      const res = await clinicalService.onboardNewPatient(patient, targetROM, true);
      console.log('Saved baseline safely:', res);
      
      alert(`Success! Generated Profile ID #${res.patient_profile_id} for ${patient.firstName}.`);
      navigate('/doctor/dashboard');
    } catch (e) {
      alert(`API Error: ${e.message}`);
      setPhase('success'); // Revert allowing them to try again
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col max-w-6xl mx-auto rounded-3xl overflow-hidden shadow-2xl border-4 border-indigo-100 bg-slate-900">
      
      {/* Header Bar */}
      <div className="bg-white p-4 flex items-center justify-between z-20 shadow-sm relative">
        <div>
          <h2 className="text-xl font-bold text-indigo-900">Clinical Baseline Capture</h2>
          <p className="text-sm text-indigo-600 font-medium">Patient: {patient.firstName} {patient.lastName}</p>
        </div>
        
        <div className="flex gap-2">
          {Array.from({length: 3}).map((_, i) => (
            <div key={i} className={`w-12 h-3 rounded-full ${i < repsCaptured ? 'bg-indigo-600' : 'bg-slate-200'}`} />
          ))}
        </div>
      </div>

      <div className="relative flex-1 group bg-black">
        <Webcam ref={webcamRef} className="absolute inset-0 w-full h-full object-cover" />
        <canvas ref={canvasRef} width={640} height={480} className="absolute inset-0 w-full h-full object-cover z-10" />
        
        {/* Step 1 Overlay: Positioning */}
        {phase === 'positioning' && (
          <div className="absolute inset-0 z-30 bg-indigo-900/60 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center">
            <h2 className="text-3xl font-bold text-white mb-2">Ensure Full Body Visibility</h2>
            <p className="text-indigo-100 text-xl max-w-lg mb-8">
              Clinical validation requires a clear view of the patient's ankles, knees, and shoulders to establish a safe baseline.
            </p>
            <button 
              onClick={() => {
                if ('speechSynthesis' in window) {
                  window.speechSynthesis.speak(new SpeechSynthesisUtterance("Begin your baseline reps whenever you are ready."));
                }
                setPhase('recording');
              }}
              className="px-8 py-4 bg-emerald-500 text-white rounded-2xl font-bold text-xl hover:bg-emerald-600 transform transition"
            >
              Start Baseline Recording
            </button>
          </div>
        )}

        {/* Step 2 Overlay: Recording HUD */}
        {phase === 'recording' && (
          <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 bg-white/90 backdrop-blur border-2 border-indigo-200 p-6 rounded-3xl shadow-2xl flex gap-12 items-center text-center">
            <div>
              <p className="text-slate-500 font-semibold mb-1 text-sm uppercase tracking-wider">Golden Reps</p>
              <p className="text-5xl font-black text-indigo-700">{repsCaptured}<span className="text-3xl text-indigo-300">/3</span></p>
            </div>
            <div className="w-px h-16 bg-slate-300" />
            <div>
              <p className="text-slate-500 font-semibold mb-1 text-sm uppercase tracking-wider">Live Knee Angle</p>
              <p className="text-5xl font-black text-slate-800">{lowestAngleThisRep === 180 ? '--' : lowestAngleThisRep.toFixed(0)}°</p>
            </div>
          </div>
        )}

        {/* Step 3 Overlay: Success! */}
        {phase === 'success' && (
          <div className="absolute inset-0 z-40 bg-emerald-900/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center animate-in fade-in">
            <div className="w-24 h-24 bg-emerald-500 rounded-full flex items-center justify-center animate-bounce mb-6 shadow-2xl shadow-emerald-500/50">
              <CheckCircle size={48} className="text-white" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-2 tracking-tight">Baseline Established!</h2>
            <div className="bg-emerald-800/50 px-8 py-6 rounded-2xl my-8 border border-emerald-400">
              <p className="text-emerald-100 uppercase tracking-widest text-sm font-bold mb-2">Calculated Target ROM</p>
              <p className="text-6xl font-black text-white">{targetROM.toFixed(1)}°</p>
              <p className="text-emerald-200 text-sm mt-4 max-w-sm">The OrthoSense engine will now dynamically adapt around this biometric signature during at-home sessions.</p>
            </div>
            <button 
              onClick={handleSaveBaseline}
              disabled={phase === 'saving'}
              className={`px-8 py-4 bg-white text-emerald-800 rounded-2xl font-bold text-xl transform transition flex items-center gap-2 ${
                phase === 'saving' ? 'opacity-80 cursor-wait' : 'hover:bg-emerald-50'
              }`}
            >
              {phase === 'saving' ? <Loader2 size={24} className="animate-spin" /> : <Save size={24} />}
              {phase === 'saving' ? 'Encrypting & Saving...' : 'Save to Patient Profile'}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}