import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

class DTWEngine:
    def __init__(self, threshold=300.0):
        # The DTW distance threshold above which the form is considered "incorrect"
        self.threshold = threshold
        
    def process_sequence(self, raw_history):
        """
        Converts the list of feature dictionaries into a 2D numpy array for DTW computation.
        """
        sequence = []
        for frame in raw_history:
            if not frame:
                continue
            # Extract the core biomechanical angles that define the movement
            vec = [
                frame.get("left_knee_angle", 180),
                frame.get("right_knee_angle", 180),
                frame.get("back_angle", 0)
            ]
            sequence.append(vec)
        return np.array(sequence)

    def measure_deviation(self, live_history, golden_history):
        """
        Calculates the Dynamic Time Warping distance between the user's live motion 
        and the predefined "Golden Rep" baseline.
        Returns the raw distance deviation score.
        """
        if not live_history or not golden_history:
            return float('inf')
            
        live_seq = self.process_sequence(live_history)
        golden_seq = self.process_sequence(golden_history)
        
        # DTW needs at least a few frames to compare temporal curves securely
        if len(live_seq) < 5 or len(golden_seq) < 5:
            return float('inf')
            
        # Computes the fast dynamic time warping alignment distance
        distance, path = fastdtw(live_seq, golden_seq, dist=euclidean)
        return distance
