import React, { useState, useRef, useCallback } from 'react';
import { Camera, Save, Activity, Play, Square, Plus, Trash2 } from 'lucide-react';
import { usePoseEngine } from '../../hooks/usePoseEngine';
import api from '../../services/api';

const JOINT_DICTS = [
  'nose', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
  'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee',
  'right_knee', 'left_ankle', 'right_ankle'
];

export default function CustomExerciseCreator() {
  const [exerciseName, setExerciseName] = useState('');
  const [trackedAngles, setTrackedAngles] = useState([{ name: 'elbow_angle', p1: 'left_shoulder', p2: 'left_elbow', p3: 'left_wrist' }]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [goldenRep, setGoldenRep] = useState([]);
  const [saveStatus, setSaveStatus] = useState('');

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  // Accumulate frames when recording
  const handlePose = useCallback((payload) => {
    if (isRecording && payload.raw_landmarks) {
      setGoldenRep(prev => [...prev, payload]);
    }
  }, [isRecording]);

  usePoseEngine(webcamRef, canvasRef, handlePose);

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
    } else {
      setGoldenRep([]);
      setIsRecording(true);
    }
  };

  const addAngle = () => {
    setTrackedAngles([...trackedAngles, { name: `angle_${trackedAngles.length + 1}`, p1: 'left_hip', p2: 'left_knee', p3: 'left_ankle' }]);
  };

  const updateAngle = (index, field, value) => {
    const newAngles = [...trackedAngles];
    newAngles[index][field] = value;
    setTrackedAngles(newAngles);
  };

  const removeAngle = (index) => {
    const newAngles = [...trackedAngles];
    newAngles.splice(index, 1);
    setTrackedAngles(newAngles);
  };

  const handleSave = async () => {
    if (!exerciseName) return alert("Please enter an exercise name");
    if (goldenRep.length < 10) return alert("Please record a longer Golden Rep (at least 10 frames).");

    // Format tracked angles for backend {"elbow_angle": ["left_shoulder", "left_elbow", "left_wrist"]}
    const formattedAngles = {};
    trackedAngles.forEach(a => {
      formattedAngles[a.name] = [a.p1, a.p2, a.p3];
    });

    try {
      setSaveStatus('Saving...');
      const response = await api.post('/exercises/custom', {
        name: exerciseName,
        tracked_angles: formattedAngles,
        golden_rep_data: goldenRep.map(frame => {
          // Just extract the raw landmarks out for the Golden Rep calibration
          return frame.raw_landmarks || {};
        })
      });
      setSaveStatus('✅ Exercise Saved Successfully!');
      setGoldenRep([]);
      setExerciseName('');
    } catch (err) {
      console.error(err);
      setSaveStatus('❌ Error saving exercise.');
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto h-screen bg-slate-50 flex flex-col md:flex-row gap-8">
      {/* LEFT: Configuration Form */}
      <div className="flex-1 bg-white p-6 rounded-2xl shadow-xl flex flex-col gap-6">
        <h2 className="text-2xl font-bold flex items-center gap-2"><Activity className="text-indigo-600" /> AI Exercise Studio</h2>
        
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-1">Exercise Name</label>
          <input 
            type="text" value={exerciseName} onChange={e => setExerciseName(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-indigo-500" 
            placeholder="e.g., Left Bicep Curl" 
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-semibold text-slate-700">Tracked Angles</label>
            <button onClick={addAngle} className="text-sm bg-indigo-50 text-indigo-600 px-3 py-1 rounded flex items-center gap-1 hover:bg-indigo-100"><Plus size={16}/> Add Joint</button>
          </div>
          
          {trackedAngles.map((angle, idx) => (
            <div key={idx} className="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-3 relative">
              <div className="flex justify-between items-center mb-2">
                <input 
                  type="text" value={angle.name} onChange={e => updateAngle(idx, 'name', e.target.value)}
                  className="p-1 border rounded w-1/2 text-sm font-semibold" 
                  placeholder="Angle Name"
                />
                <button onClick={() => removeAngle(idx)} className="text-red-500 hover:text-red-700"><Trash2 size={16}/></button>
              </div>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <select value={angle.p1} onChange={e => updateAngle(idx, 'p1', e.target.value)} className="p-1 rounded border">
                  {JOINT_DICTS.map(j => <option key={j} value={j}>{j}</option>)}
                </select>
                <select value={angle.p2} onChange={e => updateAngle(idx, 'p2', e.target.value)} className="p-1 rounded border">
                  {JOINT_DICTS.map(j => <option key={j} value={j}>{j}</option>)}
                </select>
                <select value={angle.p3} onChange={e => updateAngle(idx, 'p3', e.target.value)} className="p-1 rounded border">
                  {JOINT_DICTS.map(j => <option key={j} value={j}>{j}</option>)}
                </select>
              </div>
              <div className="text-xs text-slate-400 mt-2 text-center">Point 1 (Origin) â†’ Point 2 (Vertex) â†’ Point 3 (End)</div>
            </div>
          ))}
        </div>

        <button 
          onClick={handleSave}
          disabled={!exerciseName || goldenRep.length === 0}
          className="mt-auto w-full bg-indigo-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-indigo-700 disabled:opacity-50 flex justify-center items-center gap-2"
        >
          <Save /> Save & Publish Medical Model
        </button>
        {saveStatus && <p className="text-center font-semibold mt-2">{saveStatus}</p>}
      </div>

      {/* RIGHT: Live Camera & Calibration Recording */}
      <div className="flex-1 bg-white p-6 rounded-2xl shadow-xl flex flex-col gap-4">
        <h2 className="text-xl font-bold flex items-center gap-2"><Camera className="text-indigo-600" /> Golden Rep Recorder</h2>
        <div className="relative bg-black rounded-lg overflow-hidden flex-1 flex items-center justify-center min-h-[400px]">
          <video ref={webcamRef} className="absolute w-full h-full object-cover opacity-80" autoPlay playsInline muted />
          <canvas ref={canvasRef} className="absolute w-full h-full object-cover z-10" width="640" height="480" />
          
          {isRecording && (
            <div className="absolute top-4 right-4 bg-red-600 text-white px-3 py-1 rounded-full animate-pulse font-bold flex items-center gap-2 z-20">
              <span className="w-3 h-3 bg-white rounded-full"></span> REC
            </div>
          )}
        </div>

        <div className="flex items-center justify-between bg-slate-100 p-4 rounded-xl">
          <div>
            <p className="font-semibold text-slate-800">Frames Captured</p>
            <p className="text-2xl font-bold text-indigo-600">{goldenRep.length}</p>
          </div>
          <button 
            onClick={toggleRecording}
            className={`px-6 py-3 rounded-lg font-bold flex items-center gap-2 shadow-md transition-all ${isRecording ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-emerald-500 text-white hover:bg-emerald-600'}`}
          >
            {isRecording ? <><Square fill="currentColor" /> Stop Recording</> : <><Play fill="currentColor" /> Start Golden Rep</>}
          </button>
        </div>
        <p className="text-sm text-slate-500 text-center">Perform exactly one perfect repetition while recording to establish the DTW algorithmic baseline for your patients.</p>
      </div>
    </div>
  );
}