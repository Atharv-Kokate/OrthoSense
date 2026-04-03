import sys

builder_code = '''import React, { useState, useEffect } from 'react';
import { PlusCircle, Search, Layers, ChevronRight, Activity, Save, Settings, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ProgramBuilder() {
  const navigate = useNavigate();
  const [programName, setProgramName] = useState("Knee Replacement Protocol");
  const [phases, setPhases] = useState([
    { name: "Early Mobility", days: 14, target: 90, exercises: ['Squat'] },
    { name: "Stability & Load", days: 28, target: 110, exercises: ['Squat', 'Lunge'] }
  ]);

  return (
    <div className="flex h-screen bg-slate-50 relative overflow-hidden">
      {/* Sidebar Library */}
      <div className="w-80 bg-white border-r border-slate-200 flex flex-col p-6 z-10 shadow-xl">
        <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-700 to-emerald-600 mb-8">Clinical Studio</h2>
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 text-slate-400 w-5 h-5" />
            <input type="text" placeholder="Search exercises..." className="w-full pl-10 pr-4 py-3 bg-slate-100 rounded-xl outline-none focus:ring-2 ring-indigo-500/50 placeholder-slate-400 transition-all font-medium" />
          </div>
          
          <div className="mt-8 space-y-3">
            <h3 className="text-xs font-black uppercase text-slate-400 tracking-widest pl-1 mb-2">Available Exercises</h3>
            {['AI Tracking Squat', 'Front Lunge', 'Hip Abduction'].map(ex => (
              <div key={ex} className="group p-4 bg-white border border-slate-200 rounded-2xl cursor-pointer hover:border-indigo-500 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                      <Activity size={20}/>
                    </div>
                    <span className="font-semibold text-slate-700">{ex}</span>
                  </div>
                  <ChevronRight size={18} className="text-slate-300 group-hover:text-indigo-500" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Builder Canvas */}
      <div className="flex-1 overflow-auto bg-slate-50/50 backdrop-blur pb-20">
        <div className="max-w-4xl mx-auto p-10 pt-12">
            
            <header className="flex justify-between items-start mb-12">
                <div>
                    <input 
                        value={programName}
                        onChange={e => setProgramName(e.target.value)}
                        className="text-4xl font-extrabold text-slate-800 bg-transparent border-b border-transparent hover:border-slate-300 focus:border-indigo-500 outline-none w-[500px] transition-colors pb-1"
                    />
                    <p className="text-slate-500 mt-3 flex items-center gap-2"><Layers size={16}/> 12-Week AI Recovery Template</p>
                </div>
                <button className="flex items-center gap-2 px-6 py-3 bg-slate-900 text-white rounded-xl font-bold shadow-xl hover:bg-slate-800 hover:scale-105 active:scale-95 transition-all">
                    <Save size={18}/> Publish Pathway
                </button>
            </header>

            {/* Phases Timeline */}
            <div className="space-y-8 relative">
                {/* Timeline vertical bar */}
                <div className="absolute top-0 bottom-0 left-6 w-1 bg-gradient-to-b from-indigo-500 to-slate-200 rounded-full z-0"></div>

                {phases.map((phase, idx) => (
                    <div key={idx} className="relative z-10 pl-16">
                        {/* Number Bubble */}
                        <div className="absolute left-1 top-6 w-11 h-11 bg-white border-4 border-indigo-500 rounded-full flex items-center justify-center font-black text-indigo-700 shadow-xl shadow-indigo-200">
                            {idx + 1}
                        </div>

                        <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-200 hover:shadow-xl transition-shadow group">
                            <div className="flex justify-between mb-6 border-b border-slate-100 pb-6">
                                <div>
                                    <h3 className="text-2xl font-bold text-slate-800">{phase.name}</h3>
                                    <p className="text-slate-500 mt-1 font-medium">{phase.days} Days duration</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-xs uppercase font-bold text-emerald-500 tracking-wider mb-2">Graduation Criteria</p>
                                    <div className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 px-4 py-2 rounded-xl font-bold">
                                        Max ROM > {phase.target}°
                                    </div>
                                </div>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4">
                                {phase.exercises.map(ex => (
                                    <div key={ex} className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-slate-200">
                                        <div className="flex items-center gap-3">
                                            <Play className="text-indigo-500" size={16}/>
                                            <span className="font-semibold text-slate-700">{ex}</span>
                                        </div>
                                        <span className="text-sm font-bold text-slate-400 bg-slate-200 px-3 py-1 rounded-lg">3 x 10</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Add Phase Button */}
                <div className="pl-16 pt-4 relative z-10">
                    <button className="flex items-center gap-3 text-indigo-600 font-bold hover:text-indigo-800 transition-colors w-full p-6 border-2 border-dashed border-indigo-200 rounded-3xl hover:bg-indigo-50/50 justify-center">
                        <PlusCircle size={24}/>
                        Add New Recovery Phase
                    </button>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
'''
with open('frontend/src/pages/doctor/ProgramBuilder.jsx', 'w') as f:
    f.write(builder_code)
print("Created ProgramBuilder.jsx")