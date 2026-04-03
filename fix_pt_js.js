const fs = require('fs');
let content = fs.readFileSync('frontend/src/pages/patient/PatientDashboard.jsx', 'utf8');
content = content.replace(/fetch\((http:\/\/.*?)\)/g, 'fetch($1)');
content = content.replace(/fetch\(http:\/\/localhost:8000\/api\/patients\/(.*?)\/journey\)/g, 'fetch(http://localhost:8000/api/patients//journey)');
fs.writeFileSync('frontend/src/pages/patient/PatientDashboard.jsx', content, 'utf8');
console.log('Fixed js!');