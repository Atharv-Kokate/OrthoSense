import React, { useRef, useState, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { useLocation, useParams } from 'react-router-dom';
import { Activity, AlertTriangle, CheckCircle, Video, Target, Mic, MicOff } from 'lucide-react';
import { useTelemetrySocket } from '../hooks/useTelemetrySocket';
import { usePoseEngine } from '../hooks/usePoseEngine';

export default function CameraView() {
  const location = useLocation();
  const { exerciseType } = useParams();
  const patientId = location.state?.patientId || localStorage.getItem('user_id') || 1;
    const exercise = exerciseType || location.state?.exercise || 'squat';

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  // Capture the webcam's MediaStream so it can be SHARED with WebRTC (avoid 'Device in use' error)
  const [webcamStream, setWebcamStream] = useState(null);

  useEffect(() => {
    // Poll until react-webcam has initialized the video and its srcObject is available
    const interval = setInterval(() => {
      const video = webcamRef.current?.video;
      if (video && video.srcObject) {
        setWebcamStream(video.srcObject);
        clearInterval(interval);
      }
    }, 300);
    return () => clearInterval(interval);
  }, []);

  // Add a state to manage pre-session calibration
  const [isCalibrated, setIsCalibrated] = useState(false);
  const [calibrationHints, setCalibrationHints] = useState("Stand back so your full body is visible.");

  // 1. Establish WebSocket link with the AI Brain API (Mute voice if in Tele-Rehab mode)
  const { status, telemetry, sendJsonMessage, isListening, startListening } = useTelemetrySocket(patientId, exercise);
  const { repCount, feedback, errors } = telemetry;
  // 2. Wire the extracted biomechanical data directly into the socket hook safely
  const handlePoseComputed = useCallback((telemetryPayload) => {
    
    // --- Pre-Session Calibration Logic ---
    if (!isCalibrated) {
      if (telemetryPayload.raw_landmarks) {
        const { left_ankle, right_ankle, left_hip, left_shoulder } = telemetryPayload.raw_landmarks;
        // Basic visibility check: are key joints appearing on screen with decent confidence?
        const isAnkleVisible = left_ankle.visibility > 0.6 || right_ankle.visibility > 0.6;
        const isHipVisible = left_hip.visibility > 0.6;
        const isShoulderVisible = left_shoulder.visibility > 0.6;

        if (isAnkleVisible && isHipVisible && isShoulderVisible) {
          setIsCalibrated(true);
          // Trigger a welcome voice prompt
          if ('speechSynthesis' in window) {
            let u = new SpeechSynthesisUtterance("Calibration successful. Let's begin your squats.");
            u.rate = 1.0;
            u.pitch = 1.1;
            window.speechSynthesis.speak(u);
          }
        } else if (!isAnkleVisible) {
          setCalibrationHints("Please step back to ensure your feet are visible.");
        } else if (!isShoulderVisible) {
          setCalibrationHints("Please step back to ensure your upper body is visible.");
        }
      }
      return; // Block telemetry sending until calibrated
    }

    // Only blast data over the wire if we're actively talking to the backend
    if (status === 'connected' || status === 'tracking' || status === 'buffering') {
      sendJsonMessage(telemetryPayload);
    }
  }, [status, sendJsonMessage, isCalibrated]);

  // 3. Boot up the Heavy Deep-learning Browser Engine
  usePoseEngine(webcamRef, canvasRef, handlePoseComputed);

  return (
    <div className="flex flex-col md:flex-row gap-6 p-6 max-w-7xl mx-auto h-screen bg-slate-50">
      
      {/* LEFT COLUMN: Camera & Overlay */}
      <div className="flex-1 bg-white rounded-2xl shadow-xl overflow-hidden shadow-slate-200 border border-slate-100 flex flex-col">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Video className="text-indigo-600" size={24} />
            <h2 className="text-xl font-bold font-sans text-slate-800">OrthoSense AI Camera</h2>
          </div>
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              {(status === 'tracking' || status === 'connected') && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              )}
              <span className={`relative inline-flex rounded-full h-3 w-3 ${status === 'connected' || status === 'tracking' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
            </span>
            <span className="text-sm font-semibold capitalize text-slate-500">
              {!isCalibrated ? 'Calibrating...' : status}
            </span>
          </div>
        </div>

        <div className="relative flex-1 bg-slate-900 group">
          <Webcam
            ref={webcamRef}
            className="absolute inset-0 w-full h-full object-cover"
          />
          <canvas
            ref={canvasRef}
            width={640}
            height={480}
            className="absolute inset-0 w-full h-full object-cover z-10"
          />
          
          {/* Calibration Overlay */}
          {!isCalibrated && (
            <div className="absolute inset-0 z-30 bg-indigo-900/60 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center">
              <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center animate-pulse mb-6">
                <Target size={48} className="text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">Camera Calibration</h2>
              <p className="text-indigo-100 text-xl">{calibrationHints}</p>
            </div>
          )}

          {/* AI LLM HUD overlay (hidden during calibration) */}
          {isCalibrated && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-11/12 max-w-xl z-20">
              <div className={`p-4 rounded-xl backdrop-blur-md shadow-2xl border transition-all duration-300 ${
                errors.length > 0 ? 'bg-red-500/80 border-red-400' : 'bg-emerald-500/80 border-emerald-400'
              }`}>
                <div className="flex gap-4 items-center">
                  {errors.length > 0 ? <AlertTriangle className="text-white flex-shrink-0" size={32} /> : <CheckCircle className="text-white flex-shrink-0" size={32} />}
                  <p className="text-white font-medium text-lg leading-tight tracking-wide">"{feedback}"</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT COLUMN: Telemetry Sidebar */}
      <div className="w-full md:w-96 flex flex-col gap-4">

        

        {/* REPS CARD */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex flex-col items-center justify-center relative">
          <h3 className="text-slate-500 font-semibold mb-2">Total Repetitions</h3>
          <div className="text-7xl font-bold text-indigo-600 tracking-tighter"> 
            {repCount}
          </div>
          <p className="text-sm text-slate-400 mt-2">Squat Target: 10</p>
          
          <button 
            onClick={startListening}
            className={`mt-4 px-4 py-2 rounded-full flex items-center gap-2 transition-all ${
              isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {isListening ? <Mic size={20} /> : <MicOff size={20} />}
            <span className="font-medium text-sm">
              {isListening ? 'Listening...' : 'Talk to AI'}
            </span>
          </button>
        </div>

        {/* ACTIVE ERRORS CARD */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex-1">
          <div className="flex items-center gap-2 mb-6">
            <Activity className="text-slate-400" size={20} />
            <h3 className="text-slate-700 font-bold">Biometric Telemetry</h3>
          </div>
          
          <div className="space-y-4">
            {errors.length === 0 ? (
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center">
                <p className="text-slate-500">No biomechanical errors detected.</p>
              </div>
            ) : (
              errors.map((error, idx) => (
                <div key={idx} className="p-4 bg-red-50 rounded-xl border border-red-100 flex flex-col gap-1">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-red-700 capitalize">{error.type.replace('_', ' ')}</span>
                    <span className="text-xs font-bold text-red-500 bg-red-100 px-2 py-1 rounded-full">{(error.severity * 100).toFixed(0)}% Severity</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}