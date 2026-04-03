import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

class DTWEngine:
    def __init__(self, threshold=300.0, tracked_features=None):
        # The DTW distance threshold above which the form is considered "incorrect"
        self.threshold = threshold
        # The exact list of angular keys the DTW algorithm should measure over time
        self.tracked_features = tracked_features or ["left_knee_angle", "right_knee_angle", "back_angle"]
        
    def process_sequence(self, raw_history):
        """
        Converts the list of feature dictionaries into a 2D numpy array for DTW computation.
        """
        sequence = []
        for frame in raw_history:
            if not frame:
                continue
            
            # Dynamically pull the exact features needed, using 0 as a default fallback
            vec = [frame.get(feature_key, 0) for feature_key in self.tracked_features]
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
