import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/api';

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState('patient');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // For doctor registration optional view
  const [isRegistering, setIsRegistering] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  useEffect(() => {
    // If already logged in, redirect to correct dashboard
    const token = localStorage.getItem('token');
    const existingRole = localStorage.getItem('role');
    if (token && existingRole) {
      navigate(`/${existingRole}/dashboard`, { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (role === 'doctor' && isRegistering) {
        await authService.registerDoctor(firstName, lastName, email, password);
        navigate('/doctor/dashboard');
      } else {
        const data = await authService.login(email, password);
        // data contains role and user_id. We navigate based on returned role
        if (data.role === 'doctor') {
          navigate('/doctor/dashboard');
        } else {
          navigate('/patient/dashboard');
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRoleSwitch = (newRole) => {
    setRole(newRole);
    setIsRegistering(false); // Reset to login when switching
    setError(null);
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">
        {isRegistering ? 'Register as Doctor' : 'Welcome Back'}
      </h2>

      <div className="flex bg-slate-100 p-1 rounded-lg mb-6">
        <button
          type="button"
          onClick={() => handleRoleSwitch('patient')}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
            role === 'patient' ? 'bg-white shadow text-indigo-700' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Patient
        </button>
        <button
          type="button"
          onClick={() => handleRoleSwitch('doctor')}
          className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
            role === 'doctor' ? 'bg-white shadow text-indigo-700' : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Doctor
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4">
            {error}
          </div>
        )}

        {role === 'doctor' && isRegistering && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
              />
            </div>
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition disabled:opacity-50"
        >
          {isLoading ? 'Processing...' : (isRegistering ? 'Complete Registration' : `Sign In As ${role.charAt(0).toUpperCase() + role.slice(1)}`)}
        </button>

        {role === 'doctor' && (
          <div className="text-center mt-4">
            <button
              type="button"
              onClick={() => setIsRegistering(!isRegistering)}
              className="text-sm text-indigo-600 hover:text-indigo-800"
            >
              {isRegistering ? 'Already registered? Sign in' : 'Need an account? Register Doctor'}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
