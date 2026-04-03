import sys
content = open('frontend/src/App.jsx').read()

if 'ProgramBuilder' not in content:
    content = content.replace("import PatientDetail from './pages/doctor/PatientDetail';", "import PatientDetail from './pages/doctor/PatientDetail';\nimport ProgramBuilder from './pages/doctor/ProgramBuilder';")
    content = content.replace('<Route path="/doctor/patient/:id" element={<PatientDetail />} />', '<Route path="/doctor/patient/:id" element={<PatientDetail />} />\n            <Route path="/doctor/program-builder" element={<ProgramBuilder />} />')
    
    with open('frontend/src/App.jsx', 'w') as f:
        f.write(content)