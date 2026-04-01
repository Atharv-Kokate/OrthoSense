import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';
import Login from './pages/auth/Login';
import DoctorDashboard from './pages/doctor/DoctorDashboard';
import ClinicalOnboarding from './pages/doctor/ClinicalOnboarding';
import PatientDashboard from './pages/patient/PatientDashboard';
import GoldenRepCapture from './pages/doctor/GoldenRepCapture';
import CameraView from './components/CameraView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Flow */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Route>

        {/* Doctor Flow */}
        <Route element={<DashboardLayout role="doctor" />}>
          <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
          <Route path="/doctor/onboard" element={<ClinicalOnboarding />} />
          <Route path="/doctor/capture-golden-rep" element={<GoldenRepCapture />} />
          {/* Patient Detail route can be added later */}
        </Route>

        {/* Patient Flow */}
        <Route element={<DashboardLayout role="patient" />}>
          <Route path="/patient/dashboard" element={<PatientDashboard />} />
          {/* The AI Session view */}
          <Route path="/patient/session/:exerciseType" element={<CameraView />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
