import sys
import re

content = open('frontend/src/pages/doctor/PatientDetail.jsx').read()

import_replacement = '''import VideoConsultation from '../../components/VideoConsultation';
import { callService } from '../../services/api';'''

if 'Approve Phase' not in content:
    content = content.replace(import_replacement, import_replacement + "\nimport { CheckCircle } from 'lucide-react';")
    
    # Adding approve button next to export report
    btn_target = '<button className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none flex items-center justify-center gap-2">'
    new_btn = '''
            <button className="px-4 py-2 border border-emerald-500 rounded-lg shadow-sm text-sm font-bold text-white bg-emerald-500 hover:bg-emerald-600 focus:outline-none flex items-center justify-center gap-2 animate-bounce">
              <CheckCircle size={16}/> Approve Phase
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none flex items-center justify-center gap-2">'''
            
    content = content.replace(btn_target, new_btn)
    with open('frontend/src/pages/doctor/PatientDetail.jsx', 'w') as f:
        f.write(content)