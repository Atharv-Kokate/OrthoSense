import sys

with open('frontend/src/pages/patient/PatientDashboard.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('await fetch(http://localhost:8000/api/patients/{patientId}/journey);', 'await fetch(http://localhost:8000/api/patients//journey);')
text = text.replace("navigate(/patient/session/{phase.exercises[0]?.type || 'squat'})", "navigate(/patient/session/)")

with open('frontend/src/pages/patient/PatientDashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed JSX Syntax')