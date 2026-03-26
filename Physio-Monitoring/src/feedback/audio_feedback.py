import sys, os
import pyttsx3
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

class AudioFeedback:
    """
    Provides audio feedback for exercise monitoring.
    Uses text-to-speech to give real-time posture and exercise feedback.
    """
    def __init__(self, cooldown=2):
        """
        Initialize audio feedback system.
        
        Args:
            cooldown: Minimum seconds between consecutive audio messages
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # speech rate
        self.cooldown = cooldown
        self.last_speak_time = datetime.min
        
    def speak(self, text):
        """
        Speak text if cooldown period has elapsed.
        
        Args:
            text: Message to speak
        """
        now = datetime.now()
        if (now - self.last_speak_time).total_seconds() >= self.cooldown:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                self.last_speak_time = now
            except Exception as e:
                print(f"⚠ Audio error: {e}")
    
    def speak_exercise(self, exercise_name):
        """Announce exercise detection."""
        self.speak(f"{exercise_name.replace('_', ' ')} detected")
    
    def speak_posture(self, posture_status):
        """Announce posture status."""
        if posture_status == "Correct":
            self.speak("Correct posture")
        else:
            self.speak(f"Incorrect posture: {posture_status}")
    
    def speak_milestone(self, reps):
        """Announce repetition milestones (every 5 reps)."""
        if reps > 0 and reps % 5 == 0:
            self.speak(f"Completed {reps} repetitions")
