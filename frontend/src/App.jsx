import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';
import Login from './pages/auth/Login';
import DoctorDashboard from './pages/doctor/DoctorDashboard';
import ClinicalOnboarding from './pages/doctor/ClinicalOnboarding';
import PatientDashboard from './pages/patient/PatientDashboard';
import PatientDetail from './pages/doctor/PatientDetail';
import ProgramBuilder from './pages/doctor/ProgramBuilder';
import GoldenRepCapture from './pages/doctor/GoldenRepCapture';
import CameraView from './components/CameraView';
import TeleRehabRoom from './pages/patient/TeleRehabRoom';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          {/* Auth Flow */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Navigate to={localStorage.getItem('role') === 'doctor' ? '/doctor/dashboard' : localStorage.getItem('role') === 'patient' ? '/patient/dashboard' : '/login'} replace />} />
          </Route>

          {/* Doctor Flow */}
          <Route element={<DashboardLayout role="doctor" />}>
            <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
            <Route path="/doctor/onboard" element={<ClinicalOnboarding />} />
            <Route path="/doctor/capture-golden-rep" element={<GoldenRepCapture />} />
            <Route path="/doctor/patient/:id" element={<PatientDetail />} />
            <Route path="/doctor/program-builder" element={<ProgramBuilder />} />          </Route>

          {/* Patient Flow */}
          <Route element={<DashboardLayout role="patient" />}>
            <Route path="/patient/dashboard" element={<PatientDashboard />} />
            {/* The Tele-Rehab Standalone Room */}
            <Route path="/patient/tele-rehab/:roomId" element={<TeleRehabRoom />} />
            {/* The AI Session view */}
            <Route path="/patient/session/:exerciseType" element={<ErrorBoundary><CameraView /></ErrorBoundary>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
