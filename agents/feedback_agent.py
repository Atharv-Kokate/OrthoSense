FEEDBACK_MAP = {
    "forward_lean": "Keep your chest up and back straight.",
    "knee_too_deep": "Do not bend your knees too much.",
    "imbalance": "Balance your weight evenly on both legs.",
    "dtw_deviation": "You are deviating from your Golden Rep benchmark! Reset your form."
}

def generate(decision):
    """
    Translates raw decision codes into human-readable strings and visual levels.
    """
    if not decision:
        return None
        
    error_type = decision.get("type")
    
    text = FEEDBACK_MAP.get(error_type, "Adjust your posture.")
    
    # Yellow for lower severity warnings, Red for critical
    level = "warning" if decision.get("severity", 0) < 0.8 else "critical"
    
    return {
        "text": text,
        "level": level
    }
