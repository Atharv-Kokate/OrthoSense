from collections import deque
import pandas as pd
import numpy as np

class TemporalBuffer:
    def __init__(self, maxlen=30):
        self.history = deque(maxlen=maxlen)
        self.rep_metrics = [] # Track form score/ROM per completed rep
        
    def add(self, features):
        """Append latest feature set to the temporal buffer."""
        self.history.append(features)
        
    def add_rep_metric(self, max_rom, form_score):
        """Store the performance of a completed rep to detect fatigue."""
        self.rep_metrics.append({
            "max_rom": max_rom,
            "form_score": form_score
        })
        
    def check_fatigue_degradation(self, window=3, threshold=15.0):
        """
        Check if form score or ROM has degraded significantly over the last `window` reps.
        Returns True if the patient is fatiguing.
        """
        n = len(self.rep_metrics)
        if n < window * 2:
            # Need enough reps to calculate a baseline and compare against the window
            return False, {}
            
        # Compare initial average (baseline) vs latest window average
        initial_reps = self.rep_metrics[0:window]
        latest_reps = self.rep_metrics[-window:]
        
        baseline_score = sum(r["form_score"] for r in initial_reps) / window
        latest_score = sum(r["form_score"] for r in latest_reps) / window
        
        decline_percentage = 0
        if baseline_score > 0:
            decline_percentage = ((baseline_score - latest_score) / baseline_score) * 100
            
        is_fatigued = decline_percentage > threshold
        return is_fatigued, {
            "baseline_score": baseline_score,
            "latest_score": latest_score,
            "decline_percentage": decline_percentage
        }
        return list(self.history)
        
    def get_latest(self):
        """Return the latest feature set."""
        if self.history:
            return self.history[-1]
        return None

    def get_lstm_sequence(self):
        """
        Transforms the real-time history into the 9-feature 30-frame numpy array 
        expected by the BiLSTM. Returns None if the buffer is still filling up.
        """
        if len(self.history) < self.history.maxlen:
            return None
            
        # Convert list of dicts to a fast DataFrame for window calculations
        df = pd.DataFrame(self.history)
        
        # 1. Real-Time Velocities
        df['left_knee_vel'] = df['left_knee_angle'].diff().fillna(0)
        df['right_knee_vel'] = df['right_knee_angle'].diff().fillna(0)
        df['back_vel'] = df['back_angle'].diff().fillna(0)

        # 2. Real-Time Moving Averages (Smooths out jitter)
        df['left_knee_smooth'] = df['left_knee_angle'].rolling(window=5, min_periods=1).mean()
        df['back_smooth'] = df['back_angle'].rolling(window=5, min_periods=1).mean()

        # Ensure exact feature order corresponding to training weights
        features = [
            'left_knee_angle', 'right_knee_angle', 'back_angle', 'symmetry_score',
            'left_knee_vel', 'right_knee_vel', 'back_vel', 
            'left_knee_smooth', 'back_smooth'
        ]
        
        return df[features].values # Returns shape: (30, 9)
