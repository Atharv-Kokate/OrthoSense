// src/services/api.js
const API_URL = 'http://localhost:8000/api';

/**
 * A reusable API service designed for a scalable front-end architecture.
 * Features built-in try/catch, standardized JSON headers, and future-proof JWT handling hooks.
 */
export const clinicalService = {
  // Save Golden Rep Baseline for new clinical patients
  onboardNewPatient: async (patientData, targetRomDegrees, isAutoAdaptive) => {
    try {
      const payload = {
        first_name: patientData.firstName,
        last_name: patientData.lastName,
        email: patientData.email,
        condition: patientData.condition,
        date_of_surgery: patientData.dateOfSurgery,
        target_rom_degrees: targetRomDegrees,
        auto_adaptive: isAutoAdaptive,
        doctor_id: 1 // Defaulted to internal mock doctor 1 for now
      };

      const res = await fetch(`${API_URL}/patients/onboard`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Future Auth: 'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || 'Failed to persist patient baseline data.');
      }
      
      return await res.json();
    } catch (e) {
      console.error('API Error in clinicalService:', e);
      throw e;
    }
  }
};
