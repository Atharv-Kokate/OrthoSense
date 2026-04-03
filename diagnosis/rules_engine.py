from config.exercise_config import EXERCISE_CONFIG
from diagnosis.dtw_engine import DTWEngine

# Instantiate the DTW baseline sequence comparator
dtw = DTWEngine(threshold=250.0)

def is_persistent(history, condition, frames=10):
    """
    Checks if a specific condition is True for at least a certain number of frames in history.
    Reduces noise and false positives.
    """
    return sum(1 for h in history if h and condition(h)) >= frames

def analyze(features, history, exercise, golden_rep=None):
    """
    Evaluates current biomechanical features against thresholds using temporal logic and true 3D Sequence Matching.
    Returns a dictionary with a list of active errors.
    """
    errors = []
    
    if not features or not history:
        return {"errors": errors}
        
    # --- PHASE 3: DTW HEURISTIC COMPARISON ---
    if golden_rep:
        # Compute multi-dimensional deviation between current motion and the benchmark rep
        deviation_score = dtw.measure_deviation(history, golden_rep)
        if deviation_score > dtw.threshold:
            errors.append({"type": "dtw_deviation", "severity": 0.85})
            
    config = EXERCISE_CONFIG.get(exercise)
    if not config:
        return {"errors": errors}
        
    if exercise == "squat":
        # Check deep knee
        if features.get("left_knee_angle", 180) < config["knee_angle_min"]:
            if is_persistent(history, lambda h: h.get("left_knee_angle", 180) < config["knee_angle_min"], frames=10):
                errors.append({"type": "knee_too_deep", "severity": 0.8})
                
        # Check forward lean
        if features.get("back_angle", 180) < config.get("back_angle_min", 90):
            if is_persistent(history, lambda h: h.get("back_angle", 180) < config.get("back_angle_min", 90), frames=10):
                errors.append({"type": "forward_lean", "severity": 0.7})
                
        # Check symmetry imbalance
        if features.get("symmetry_score", 0) > config["symmetry_threshold"]:
            if is_persistent(history, lambda h: h.get("symmetry_score", 0) > config["symmetry_threshold"], frames=10):
                errors.append({"type": "imbalance", "severity": 0.9})
                
    elif exercise == "lunge":
        # Lunge specific checks
        if features.get("symmetry_score", 0) > config["symmetry_threshold"]:
            if is_persistent(history, lambda h: h.get("symmetry_score", 0) > config["symmetry_threshold"], frames=10):
                errors.append({"type": "imbalance", "severity": 0.9})
                
    return {"errors": errors}
