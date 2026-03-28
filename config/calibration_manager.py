import json
import os

class CalibrationManager:
    def __init__(self, save_dir="config/calibrations"):
        self.save_dir = save_dir
        # Ensure the calibration directory exists inside the project
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
            
    def get_filepath(self, exercise):
        return os.path.join(self.save_dir, f"{exercise}_golden.json")
        
    def save_golden_rep(self, exercise, history):
        """
        Persists the optimal 3D feature array recording to the local disk.
        """
        filepath = self.get_filepath(exercise)
        try:
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=4)
            print(f"[{exercise.upper()}] Golden Baseline Rep physically committed to {filepath}")
            return True
        except Exception as e:
            print(f"Failed saving rep: {e}")
            return False
        
    def load_golden_rep(self, exercise):
        """
        Pulls the user's pre-recorded mathematical baseline into memory for the DTW Engine.
        """
        filepath = self.get_filepath(exercise)
        if not os.path.exists(filepath):
            return None
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Corrupted calibration file read error: {e}")
            return None
