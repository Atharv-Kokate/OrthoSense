import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Video } from 'lucide-react';
import { usePoseEngine } from '../hooks/usePoseEngine';

export default function RecordExerciseModal({ patientId, patientName, onClose }) {
  const [recordingState, setRecordingState] = useState('idle'); // idle, recording, saved
  const [goldenRepData, setGoldenRepData] = useState([]);
  
  const [exerciseName, setExerciseName] = useState('');
  const [description, setDescription] = useState('');
  const [reps, setReps] = useState(10);
  const [rom, setRom] = useState(90);

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  const handleTelemetry = useCallback((data) => {
    // Only capture frames when actually recording
    if (recordingState === 'recording' && data?.raw_landmarks) {
       setGoldenRepData(prev => [...prev, data.raw_landmarks]);
    }
  }, [recordingState]);

  // Hook up MediaPipe Engine directly!
  usePoseEngine(webcamRef, canvasRef, handleTelemetry);

  const startRecording = () => {
    setGoldenRepData([]);
    setRecordingState('recording');
    setTimeout(() => {
      setRecordingState('saved');
    }, 3500); // Capture for 3.5 seconds
  };

  const saveExercise = async () => {
    if (!exerciseName) {
      alert("Please enter an Exercise Name");
      return;
    }
    if (goldenRepData.length === 0) {
       alert("No motion data detected! Please make sure your camera is positioned properly and the rep was recorded.");
       return;
    }
    
    try {
       // MOCK BACKEND PUSH
       const payload = {
           name: exerciseName,
           description,
           reps: parseInt(reps, 10),
           target_rom: parseInt(rom, 10),
           golden_rep_data: goldenRepData // Pass the MediaPipe Skeleton data!
       };
       console.log("Submitting new Custom Exercise payload to PostgreSQL via FastAPI:", payload);
       
       alert(`Exercise "${exerciseName}" successfully saved for ${patientName}!\n\nCaptured: ${goldenRepData.length} 3D MediaPipe skeletons for AI comparison.`);
       onClose();
    } catch (e) {
       alert("Error saving exercise.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-gray-900 bg-opacity-75 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6 border-b pb-4">
          <h3 className="text-2xl font-bold text-gray-900">Record Specific Exercise: {patientName || 'Patient'}</h3>
          <button onClick={onClose} className="text-red-500 font-semibold hover:text-red-700 p-2 rounded-lg bg-red-50">
            Cancel / Close
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Exercise Details</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Exercise Name</label>
                <input type="text" className="w-full border border-gray-300 rounded-lg p-2" placeholder="e.g. Lateral Lunge Hold" value={exerciseName} onChange={e => setExerciseName(e.target.value)} />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Description (For Patient Dashboard)</label>
                <textarea className="w-full border border-gray-300 rounded-lg p-2" rows="3" placeholder="Explain how to do it..." value={description} onChange={e => setDescription(e.target.value)}></textarea>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Prescribed Reps</label>
                  <input type="number" className="w-full border border-gray-300 rounded-lg p-2" value={reps} onChange={e => setReps(e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Target ROM (Degrees)</label>
                  <input type="number" className="w-full border border-gray-300 rounded-lg p-2" value={rom} onChange={e => setRom(e.target.value)} />
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col">
            <h4 className="font-semibold text-gray-700 mb-2">Recording Studio</h4>
            <div className="flex-1 bg-black rounded-xl border-4 border-gray-100 flex items-center justify-center aspect-video mb-4 relative overflow-hidden ring-4 ring-offset-2 ring-gray-100">
              
              <Webcam
                ref={webcamRef}
                className="absolute inset-0 w-full h-full object-cover"
                mirrored={true}
              />
              <canvas
                ref={canvasRef}
                className="absolute inset-0 w-full h-full object-cover z-10 pointer-events-none"
              />

              {recordingState === 'idle' ? (
                <div className="text-center text-white bg-black/60 p-3 rounded-lg z-20 absolute inset-x-8 bottom-4 backdrop-blur-sm border border-white/20">
                  <Video size={24} className="mx-auto mb-1 text-white/90" /> 
                  <p className="text-sm font-medium">Camera active & AI Tracking initializing.<br/>Start Recording for Golden Rep.</p>
                </div>
              ) : recordingState === 'recording' ? (
                <div className="text-center text-white font-bold animate-pulse bg-red-600/90 p-4 rounded-xl z-20 absolute inset-x-8 bottom-4 backdrop-blur-sm border-2 border-red-400 shadow-xl shadow-red-500/20">
                  ● RECORDING GOLDEN REP
                </div>
              ) : (
                <div className="text-center text-white font-bold bg-emerald-600/90 p-4 rounded-xl z-20 absolute inset-x-8 bottom-4 backdrop-blur-sm border-2 border-emerald-400 shadow-xl shadow-emerald-500/20">  
                  ✓ Golden Rep Captured ({goldenRepData.length} tracking frames saved)
                </div>
              )}
            </div>

            <div className="flex justify-between mt-auto relative z-20 pt-2">
              {recordingState === 'idle' ? (
                <button
                  onClick={startRecording}
                  className="w-full bg-red-600 text-white font-bold py-4 rounded-xl hover:bg-red-700 transition shadow-lg flex items-center justify-center gap-2 text-lg"
                >
                  <div className="w-4 h-4 rounded-full bg-white animate-pulse" />
                  Start Recording (3s)
                </button>
              ) : recordingState === 'recording' ? (
                <button disabled className="w-full bg-slate-800 text-slate-300 font-bold py-4 rounded-xl cursor-wait text-lg border-2 border-slate-700">
                  Recording your movement...
                </button>
              ) : (
                <div className="w-full flex gap-4">
                  <button onClick={() => setRecordingState('idle')} className="flex-1 bg-slate-200 text-slate-800 hover:bg-slate-300 font-bold py-4 rounded-xl transition text-lg border-2 border-slate-300">
                    Retake
                  </button>
                  <button onClick={saveExercise} className="flex-[2] bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl transition shadow-lg text-lg border-b-4 border-emerald-700 active:border-b-0 active:translate-y-1">
                    Save & Assign
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}