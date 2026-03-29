"""
Enhanced Voice Guidance System for Physical Rehabilitation
Provides real-time audio feedback during exercises
"""
import pyttsx3
import threading
import queue
import time
from typing import Optional, Dict, List
import logging

class EnhancedVoiceGuidance:
    """Enhanced voice guidance for rehabilitation exercises"""
    
    def __init__(self):
        self.engine = None
        self.voice_queue = queue.Queue()
        self.is_speaking = False
        self.current_thread = None
        self.initialize_engine()
        
        # Track spoken messages to prevent repetition
        self.last_spoken_messages = {}
        self.message_cooldown = {}  # Exercise -> last message time
        self.COOLDOWN_SECONDS = 3  # Don't repeat same message within 3 seconds
        
    def initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice (often preferred for guidance)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'clara' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 150)  # Slightly fast for clear guidance
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.85)
            
            logging.info("Enhanced TTS engine initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def can_speak(self, exercise: str, message: str) -> bool:
        """Check if message should be spoken (avoid repetition)"""
        if not self.engine:
            return False
        
        current_time = time.time()
        
        # Check if enough time has passed since last message
        last_time = self.message_cooldown.get(exercise, 0)
        if current_time - last_time < self.COOLDOWN_SECONDS:
            return False
        
        # Check if it's the same message as last time
        last_msg = self.last_spoken_messages.get(exercise, "")
        if last_msg == message:
            return False
        
        return True
    
    def mark_spoken(self, exercise: str, message: str):
        """Mark a message as spoken"""
        self.last_spoken_messages[exercise] = message
        self.message_cooldown[exercise] = time.time()
    
    def speak_async(self, message: str, exercise: str = ""):
        """Speak message asynchronously without blocking"""
        if not self.engine or not message:
            return
        
        # Check if we should speak this
        if exercise and not self.can_speak(exercise, message):
            return
        
        # Add message to queue
        self.voice_queue.put((message, exercise))
        
        # Start processing thread if not running
        if self.current_thread is None or not self.current_thread.is_alive():
            self.current_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.current_thread.start()
    
    def _process_queue(self):
        """Process voice queue in separate thread"""
        while not self.voice_queue.empty():
            try:
                message, exercise = self.voice_queue.get_nowait()
                self._speak_sync(message)
                if exercise:
                    self.mark_spoken(exercise, message)
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
    
    def speak_sync(self, message: str, exercise: str = ""):
        """Speak message synchronously (blocking)"""
        if not self.engine or not message:
            return
        
        if exercise and not self.can_speak(exercise, message):
            return
        
        self._speak_sync(message)
        if exercise:
            self.mark_spoken(exercise, message)
    
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


class ExerciseVoiceGuidance:
    """Provides voice guidance specific to each exercise"""
    
    # Exercise-specific starting instructions
    EXERCISE_START = {
        "Shoulder Flexion": "Starting shoulder flexion. Raise your arm forward and up.",
        "Shoulder Extension": "Starting shoulder extension. Move your arm backward.",
        "Shoulder Abduction": "Starting shoulder abduction. Raise your arm sideways.",
        "Shoulder Adduction": "Starting shoulder adduction. Lower your arm to your body.",
        "Shoulder Internal Rotation": "Starting shoulder internal rotation. Rotate your arm inward.",
        "Shoulder External Rotation": "Starting shoulder external rotation. Rotate your arm outward.",
        "Elbow Flexion": "Starting elbow flexion. Bend your elbow toward your shoulder.",
        "Elbow Extension": "Starting elbow extension. Straighten your arm.",
        "Knee Flexion": "Starting knee flexion. Bend your knee toward your body.",
        "Knee Extension": "Starting knee extension. Straighten your leg.",
        "Hip Abduction": "Starting hip abduction. Move your leg outward.",
        "Hip Flexion": "Starting hip flexion. Raise your leg upward.",
        "Ankle Dorsiflexion": "Starting ankle dorsiflexion. Point your toes upward.",
        "Ankle Plantarflexion": "Starting ankle plantarflexion. Point your toes downward.",
        "Ankle Inversion": "Starting ankle inversion. Turn your sole inward.",
        "Ankle Eversion": "Starting ankle eversion. Turn your sole outward.",
        "Body Weight Squat": "Starting body weight squat. Bend your knees and lower your body.",
        "Wall Sit": "Starting wall sit. Lower your back against the wall, bending your knees.",
        "Sumo Squat": "Starting sumo squat. Wide stance, bend your knees.",
        "Partial Squat": "Starting partial squat. Slightly bend your knees.",
        "Squat Hold": "Starting squat hold. Maintain a squat position.",
        "Wrist Flexion": "Starting wrist flexion. Bend your wrist downward.",
        "Wrist Extension": "Starting wrist extension. Bend your wrist upward.",
        "Back Extension": "Starting back extension. Arch your back carefully.",
    }
    
    # Form feedback based on angle
    FORM_FEEDBACK = {
        "Shoulder Flexion": {
            "low": "Raise higher. You're not reaching full range.",
            "high": "You're going good. Maintain this range.",
            "good": "Perfect form. Great job!"
        },
        "Elbow Flexion": {
            "low": "Bend more. Bring your hand closer to your shoulder.",
            "high": "Good full bend. Keep it steady.",
            "good": "Excellent elbow bend. You're doing great!"
        },
        "Knee Flexion": {
            "low": "Bend your knee more for better range.",
            "high": "Good knee bend. Keep the form.",
            "good": "Perfect knee bend. Well done!"
        },
        "Hip Abduction": {
            "low": "Move your leg wider.",
            "high": "Good abduction. Nice movement.",
            "good": "Excellent hip abduction. Great form!"
        },
    }
    
    # Rep completion feedback
    REP_COMPLETION = [
        "One repetition completed. Great work!",
        "Excellent. Keep the form. Next rep.",
        "Good form. Well done. Continue.",
        "Perfect repetition. Keep going!",
        "One down. You're doing great!",
        "Nice form. Keep it up!",
        "Well executed. Next one!",
        "Excellent balance. Continue.",
    ]
    
    # Motivation during exercise
    MOTIVATION = [
        "You're doing great! Keep up the momentum!",
        "Excellent form! Stay focused!",
        "You're making progress! Keep going!",
        "Great effort! Almost there!",
        "Perfect! You're on a roll!",
        "Nice job! Stay strong!",
        "You've got this! Keep moving!",
        "Impressive effort! Keep going!",
    ]
    
    # Posture correction feedback
    POSTURE_CORRECTION = {
        "keep_back_straight": "Keep your back straight. Good posture.",
        "keep_elbow_bent": "Keep your elbow bent properly.",
        "slower_movement": "Slow down. More controlled movements.",
        "fuller_range": "Increase your range of motion.",
        "better_form": "Focus on your form.",
        "maintain_position": "Hold this position steady.",
        "level_shoulders": "Keep your shoulders level.",
        "core_engaged": "Engage your core for stability.",
    }
    
    # Exercise completion
    EXERCISE_COMPLETE = [
        "Exercise completed! Great job! Take a break.",
        "Well done! You completed the set!",
        "Excellent work! Session finished!",
        "Perfect! You did a great job.",
        "Session complete! You did well!",
    ]
    
    @staticmethod
    def get_exercise_instruction(exercise: str) -> str:
        """Get starting instruction for an exercise"""
        return ExerciseVoiceGuidance.EXERCISE_START.get(
            exercise,
            f"Starting {exercise}. Focus on proper form."
        )
    
    @staticmethod
    def get_form_feedback(exercise: str, angle: float, ideal_range: tuple) -> Optional[str]:
        """Get form feedback based on current angle"""
        if exercise not in ExerciseVoiceGuidance.FORM_FEEDBACK:
            return None
        
        min_angle, max_angle = ideal_range
        mid_angle = (min_angle + max_angle) / 2
        
        feedback = ExerciseVoiceGuidance.FORM_FEEDBACK[exercise]
        
        if angle < min_angle:
            return feedback.get("low", "Increase your range of motion.")
        elif angle > max_angle:
            return feedback.get("high", "Reduce the range slightly.")
        else:
            return feedback.get("good", "Good form!")
    
    @staticmethod
    def get_rep_feedback() -> str:
        """Get feedback for completed rep"""
        import random
        return random.choice(ExerciseVoiceGuidance.REP_COMPLETION)
    
    @staticmethod
    def get_motivation() -> str:
        """Get motivational message"""
        import random
        return random.choice(ExerciseVoiceGuidance.MOTIVATION)
    
    @staticmethod
    def get_completion_message() -> str:
        """Get exercise completion message"""
        import random
        return random.choice(ExerciseVoiceGuidance.EXERCISE_COMPLETE)


# Global voice guidance instance
voice_guidance = EnhancedVoiceGuidance()

# Export for use in other modules
__all__ = [
    'EnhancedVoiceGuidance',
    'ExerciseVoiceGuidance',
    'voice_guidance',
]
