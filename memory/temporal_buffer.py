from collections import deque

class TemporalBuffer:
    def __init__(self, maxlen=30):
        self.history = deque(maxlen=maxlen)
        
    def add(self, features):
        """Append latest feature set to the temporal buffer."""
        self.history.append(features)
        
    def get_history(self):
        """Return full history as a list."""
        return list(self.history)
        
    def get_latest(self):
        """Return the latest feature set."""
        if self.history:
            return self.history[-1]
        return None
