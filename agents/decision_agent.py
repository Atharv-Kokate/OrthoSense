import time

class DecisionAgent:
    def __init__(self, cooldown=2.0):
        self.last_feedback_time = 0
        self.cooldown = cooldown

    def decide(self, diagnosis, history):
        """
        Determines if feedback should be generated based on severity and cooldown to prevent spam.
        """
        if not diagnosis or not diagnosis.get("errors"):
            return None
            
        current_time = time.time()
        
        # Enforce cooldown
        if current_time - self.last_feedback_time < self.cooldown:
            return None
            
        # Select the most critical error to correct first
        errors = diagnosis["errors"]
        highest_severity_error = max(errors, key=lambda e: e["severity"])
        
        self.last_feedback_time = current_time
        return highest_severity_error
