export const API_URL = 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

export const authService = {
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString()
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('user_id', data.user_id);
    return data;
  },

  registerDoctor: async (firstName, lastName, email, password) => {
    const res = await fetch(`${API_URL}/auth/register-doctor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password
      })
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('user_id', data.user_id);
    return data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
  }
};

export const clinicalService = {
  onboardNewPatient: async (patientData, targetRomDegrees, isAutoAdaptive) => {
    const doctorId = localStorage.getItem('user_id');
    const payload = {
      first_name: patientData.firstName,
      last_name: patientData.lastName,
      email: patientData.email,
      condition: patientData.condition,
      date_of_surgery: patientData.dateOfSurgery,
      target_rom_degrees: targetRomDegrees,
      auto_adaptive: isAutoAdaptive,
      doctor_id: parseInt(doctorId) || null
    };

    const res = await fetch(`${API_URL}/patients/onboard`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || 'Failed to persist patient baseline data.');
    }

    return await res.json();
  },

  getDoctorDashboard: async (doctorId) => {
    const res = await fetch(`${API_URL}/doctors/${doctorId}/dashboard`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to load dashboard');
    return await res.json();
  },

  getPatientDashboard: async (patientId) => {
    const res = await fetch(`${API_URL}/patients/${patientId}/dashboard`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to load patient dashboard');
    return await res.json();
  }
};

export const callService = {
  initiateCall: async (patientId, doctorName) => {
    const res = await fetch(`${API_URL}/calls/initiate?patient_id=${patientId}&doctor_name=${encodeURIComponent(doctorName)}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to initiate call');
    return await res.json();
  },

  checkIncomingCall: async (patientId) => {
    const res = await fetch(`${API_URL}/calls/check/${patientId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return { has_call: false };
    return await res.json();
  },

  acceptCall: async (patientId) => {
    const res = await fetch(`${API_URL}/calls/accept/${patientId}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to accept call');
    return await res.json();
  },

  dismissCall: async (patientId) => {
    const res = await fetch(`${API_URL}/calls/dismiss/${patientId}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return await res.json();
  }
};
