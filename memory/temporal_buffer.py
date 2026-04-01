from collections import deque
import pandas as pd
import numpy as np

class TemporalBuffer:
    def __init__(self, maxlen=30):
        self.history = deque(maxlen=maxlen)
        
    def add(self, features):
        """Append latest feature set to the temporal buffer."""
        self.history.append(features)
        
    def get_history(self):
        """Return full history as a list of dicts."""
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
