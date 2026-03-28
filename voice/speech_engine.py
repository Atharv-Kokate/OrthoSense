import pyttsx3
import threading

class SpeechEngine:
    def __init__(self):
        self.last_spoken = None
        self.lock = threading.Lock()
        
    def _speak_worker(self, text):
        """Worker function to execute TTS in a separate thread to prevent blocking OpenCV."""
        try:
            # Re-initialize pyttsx3 per thread to avoid COM initialization threading errors on Windows
            engine = pyttsx3.init()
            # Slow down speech rate slightly for better coaching clarity
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 20)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
            
    def speak(self, text):
        """
        Triggers non-blocking speech.
        Implements anti-repetition to prevent spamming the exact same sentence.
        """
        if not text:
            return
            
        with self.lock:
            # Anti-repetition check natively
            if text == self.last_spoken:
                return
            self.last_spoken = text
            
        # Spawn a daemon thread so the camera frame loop isn't paused while it speaks
        t = threading.Thread(target=self._speak_worker, args=(text,), daemon=True)
        t.start()
