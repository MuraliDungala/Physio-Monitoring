import pyttsx3
import threading
import queue
import time
from typing import Optional
import logging

class TTSEngine:
    def __init__(self):
        self.engine = None
        self.voice_queue = queue.Queue()
        self.is_speaking = False
        self.current_thread = None
        self.initialize_engine()
        
    def initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice (often preferred for guidance)
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 150)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.8)
            
            logging.info("TTS engine initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def speak_async(self, message: str):
        """Speak message asynchronously without blocking"""
        if not self.engine:
            logging.warning("TTS engine not available")
            return
            
        # Add message to queue
        self.voice_queue.put(message)
        
        # Start processing thread if not running
        if self.current_thread is None or not self.current_thread.is_alive():
            self.current_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.current_thread.start()
    
    def _process_queue(self):
        """Process voice queue in separate thread"""
        while not self.voice_queue.empty():
            try:
                message = self.voice_queue.get_nowait()
                self._speak_sync(message)
                time.sleep(0.1)  # Small delay between messages
            except queue.Empty:
                break
    
    def _speak_sync(self, message: str):
        """Speak message synchronously"""
        try:
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Error speaking message: {e}")
    
    def speak_sync(self, message: str):
        """Speak message synchronously (blocking)"""
        if not self.engine:
            logging.warning("TTS engine not available")
            return
            
        self._speak_sync(message)
    
    def stop(self):
        """Stop current speech and clear queue"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        
        # Clear queue
        while not self.voice_queue.empty():
            try:
                self.voice_queue.get_nowait()
            except queue.Empty:
                break

# Predefined voice messages for different events
class VoiceMessages:
    EXERCISE_START = {
        "Shoulder Flexion": "You are performing shoulder flexion. Raise your arm forward.",
        "Shoulder Extension": "You are performing shoulder extension. Move your arm backward.",
        "Shoulder Abduction": "You are performing shoulder abduction. Raise your arm sideways.",
        "Shoulder Adduction": "You are performing shoulder adduction. Lower your arm to your body.",
        "Shoulder Internal Rotation": "You are performing shoulder internal rotation. Rotate your arm inward.",
        "Shoulder External Rotation": "You are performing shoulder external rotation. Rotate your arm outward.",
        "Elbow Flexion": "You are performing elbow flexion. Bend your elbow.",
        "Elbow Extension": "You are performing elbow extension. Straighten your arm.",
        "Knee Flexion": "You are performing knee flexion. Bend your knee.",
        "Hip Abduction": "You are performing hip abduction. Move your leg sideways."
    }
    
    POSTURE_CORRECTION = [
        "Keep your elbow straight.",
        "Maintain proper posture.",
        "Adjust your position.",
        "Keep your back straight.",
        "Focus on your form.",
        "Slow and controlled movements."
    ]
    
    REP_COMPLETION = [
        "One repetition completed.",
        "Good form. Continue.",
        "Excellent. Keep going.",
        "Well done. Next repetition.",
        "Perfect form."
    ]
    
    EXERCISE_END = [
        "Exercise completed. Great job!",
        "Excellent work! Session finished.",
        "Well done! Take a rest.",
        "Great session! You did well."
    ]
    
    MOTIVATION = [
        "You're doing great!",
        "Keep up the good work!",
        "Excellent form!",
        "You're making progress!",
        "Stay focused!"
    ]

# Global TTS instance
tts_engine = TTSEngine()
