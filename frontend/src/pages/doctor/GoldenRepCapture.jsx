import React, { useRef, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { Target, CheckCircle, Save, Loader2, AlertTriangle, Activity } from 'lucide-react';
import { usePoseEngine } from '../../hooks/usePoseEngine';
import { clinicalService } from '../../services/api';

export default function GoldenRepCapture() {
  const navigate = useNavigate();
  const location = useLocation();
  const patient = location.state?.patient || { firstName: 'Patient' };

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  // 'positioning' -> 'stabilizing' -> 'recording' -> 'reviewing' -> 'success' -> 'saving'
  const [phase, setPhase] = useState('positioning');
  const [acceptedRoms, setAcceptedRoms] = useState([]);
  
  const [lowestAngleThisRep, setLowestAngleThisRep] = useState(180);
  const [isInRep, setIsInRep] = useState(false);
  const [pendingRepROM, setPendingRepROM] = useState(null);
  const [stableFrames, setStableFrames] = useState(0);

  // Establish the "Golden Baseline" via local CV feedback with strict doctor constraints.
  const handlePoseComputed = useCallback((telemetryPayload) => {
    // Only analyze pose if we are trying to stabilize or record
    if (phase !== 'stabilizing' && phase !== 'recording') return;

    if (!telemetryPayload) return;

    const currentAngle = telemetryPayload.left_knee_angle;
    if (!currentAngle) return;

    // Phase: Stabilizing - Patient must be standing straight before a rep can begin
    if (phase === 'stabilizing') {
      if (currentAngle > 160) {
        setStableFrames(prev => {
          const next = prev + 1;
          if (next > 15) { // Roughly 0.5 - 1 second of stable standing
            setPhase('recording');
            if ('speechSynthesis' in window) {
              window.speechSynthesis.speak(new SpeechSynthesisUtterance("Stabilized. Begin your repetition."));
            }
            return 0;
          }
          return next;
        });
      } else {
        setStableFrames(0); // Reset if they bend their knees during stabilization
      }
      return;
    }

    // Phase: Recording - Patient is actively performing the repetition
    if (phase === 'recording') {
      // Ensure they don't just trigger it by slightly shifting; must drop below 150
      if (currentAngle < 150 && !isInRep) {
        setIsInRep(true);
        setLowestAngleThisRep(currentAngle);
      }

      if (isInRep && currentAngle < lowestAngleThisRep) {
        setLowestAngleThisRep(currentAngle);
      }

      // They must return to a full standing posture to complete the rep
      if (currentAngle > 160 && isInRep) {
        setIsInRep(false);
        setPendingRepROM(lowestAngleThisRep);
        setPhase('reviewing'); // Pause tracking and wait for Doctor's strict approval
        setLowestAngleThisRep(180); 
      }
    }
  }, [phase, isInRep, lowestAngleThisRep]);

  usePoseEngine(webcamRef, canvasRef, handlePoseComputed);

  const handleAcceptRep = () => {
    const newRoms = [...acceptedRoms, pendingRepROM];
    setAcceptedRoms(newRoms);
    setPendingRepROM(null);

    if (newRoms.length === 3) {
      setPhase('success');
      if ('speechSynthesis' in window) {
        window.speechSynthesis.speak(new SpeechSynthesisUtterance("All Golden reps captured successfully."));
      }
    } else {
      setPhase('stabilizing'); // MUST restabilize before the next rep!
    }
  };

  const handleDiscardRep = () => {
    setPendingRepROM(null);
    setPhase('stabilizing'); // Must restabilize before trying again
  };

  const handleSaveBaseline = async () => {
    try {
      setPhase('saving');
      const targetROM = acceptedRoms.reduce((a, b) => a + b, 0) / acceptedRoms.length;
      
      const res = await clinicalService.onboardNewPatient(patient, targetROM, true);
      alert(`Success! Generated Profile ID #${res.patient_profile_id} for ${patient.firstName}.`);
      navigate('/doctor/dashboard');
    } catch (e) {
      alert(`API Error: ${e.message}`);
      setPhase('success');
    }
  };

  const targetROM = acceptedRoms.length > 0 
    ? (acceptedRoms.reduce((a, b) => a + b, 0) / acceptedRoms.length).toFixed(1)
    : 0;

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col max-w-6xl mx-auto rounded-3xl overflow-hidden shadow-2xl border-4 border-indigo-100 bg-slate-900">       
      
      {/* Header Bar */}
      <div className="bg-white p-4 flex items-center justify-between z-20 shadow-sm relative">
        <div>
          <h2 className="text-xl font-bold text-indigo-900">Clinical Baseline Capture</h2>
          <p className="text-sm text-indigo-600 font-medium">Patient: {patient.firstName} {patient.lastName}</p>
        </div>

        <div className="flex gap-2 items-center">
          <span className="text-sm font-bold text-slate-500 mr-2">ACCEPTED:</span>
          {Array.from({length: 3}).map((_, i) => (
            <div key={i} className={`w-12 h-3 rounded-full ${i < acceptedRoms.length ? 'bg-emerald-500 shadow-md' : 'bg-slate-200'}`} />
          ))}
        </div>
      </div>

      <div className="relative flex-1 group bg-black">
        <Webcam ref={webcamRef} className="absolute inset-0 w-full h-full object-cover" />
        <canvas ref={canvasRef} width={640} height={480} className="absolute inset-0 w-full h-full object-cover z-10" />

        {/* Step 1 Overlay: Positioning */}
        {phase === 'positioning' && (
          <div className="absolute inset-0 z-30 bg-indigo-900/80 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">Doctor Calibration Required</h2>
            <p className="text-indigo-100 text-xl max-w-2xl mb-8 leading-relaxed">
              Ensure the patient is in full view. The system will strictly enforce standing stabilization before allowing a rep stroke. You will have the option to manually accept or discard each measured rep.
            </p>
            <button
              onClick={() => {
                if ('speechSynthesis' in window) {
                  window.speechSynthesis.speak(new SpeechSynthesisUtterance("Please stand straight to stabilize the camera matrix."));
                }
                setPhase('stabilizing');
              }}
              className="px-8 py-4 bg-emerald-500 text-white rounded-2xl font-bold text-xl hover:bg-emerald-600 shadow-xl shadow-emerald-500/20 transform transition"
            >
              Start Clinical Sequence
            </button>
          </div>
        )}

        {/* Step 2 Overlay: Stabilizing HUD */}
        {phase === 'stabilizing' && (
          <div className="absolute top-10 left-1/2 -translate-x-1/2 z-20 bg-amber-500/90 backdrop-blur border-2 border-amber-300 text-white px-8 py-4 rounded-full shadow-2xl flex items-center gap-4 animate-pulse">
            <AlertTriangle size={28} />
            <span className="font-bold tracking-widest uppercase">Patient must stand straight to stabilize</span>
          </div>
        )}

        {/* Step 3 Overlay: Recording HUD */}
        {phase === 'recording' && (
          <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20 bg-white/95 backdrop-blur border-2 border-indigo-200 p-6 rounded-3xl shadow-2xl flex gap-12 items-center text-center">
            <div>
              <p className="text-slate-500 font-semibold mb-1 text-sm uppercase tracking-wider flex items-center justify-center gap-2"><Activity size={16} className="text-indigo-500 animate-pulse"/> LIVE TRACKING</p>
              <p className="text-3xl font-black text-indigo-700">Patient Executing Rep...</p>
            </div>
            <div className="w-px h-16 bg-slate-300" />
            <div>
              <p className="text-slate-500 font-semibold mb-1 text-sm uppercase tracking-wider">Lowest Angle</p>
              <p className="text-5xl font-black text-slate-800">{lowestAngleThisRep === 180 ? '--' : lowestAngleThisRep.toFixed(0)}°</p>
            </div>
          </div>
        )}

        {/* Step 4 Overlay: Doctor Review Modal */}
        {phase === 'reviewing' && pendingRepROM !== null && (
          <div className="absolute inset-0 z-40 bg-slate-900/80 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center animate-in fade-in">
            <div className="bg-white rounded-3xl shadow-2xl border flex flex-col max-w-lg w-full overflow-hidden p-8">
               <h3 className="text-2xl font-bold text-slate-800 mb-2">Doctor Validation Required</h3>
               <p className="text-slate-500 mb-6">A full cycle was detected (Standing ? Squat ? Standing). Do you approve this rep's depth as the patient's baseline?</p>
               
               <div className="bg-slate-50 border border-slate-100 rounded-2xl p-6 mb-8">
                  <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Measured Joint ROM</p>
                  <p className="text-6xl font-black text-indigo-600">{pendingRepROM.toFixed(1)}°</p>
               </div>

               <div className="flex gap-4">
                  <button onClick={handleDiscardRep} className="flex-1 px-4 py-4 rounded-xl font-bold border-2 border-red-100 bg-red-50 text-red-600 hover:bg-red-100 transition">
                    Reject / Recalibrate
                  </button>
                  <button onClick={handleAcceptRep} className="flex-1 px-4 py-4 rounded-xl font-bold bg-emerald-500 text-white hover:bg-emerald-600 shadow-lg shadow-emerald-500/20 transition">
                    Accept Golden Rep
                  </button>
               </div>
            </div>
          </div>
        )}

        {/* Step 5 Overlay: Success! */}
        {phase === 'success' && (
          <div className="absolute inset-0 z-40 bg-emerald-900/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center animate-in fade-in">
            <div className="w-24 h-24 bg-emerald-500 rounded-full flex items-center justify-center animate-bounce mb-6 shadow-2xl shadow-emerald-500/50">       
              <CheckCircle size={48} className="text-white" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-2 tracking-tight">Clinical Baseline Validated</h2>
            <div className="bg-emerald-800/50 px-8 py-6 rounded-2xl my-8 border border-emerald-400">
              <p className="text-emerald-100 uppercase tracking-widest text-sm font-bold mb-2">Averaged Golden Target ROM</p>
              <p className="text-6xl font-black text-white">{targetROM}°</p>
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
              {phase === 'saving' ? 'Encrypting & Saving...' : 'Sign & Submit to Backend'}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}


