"""
Exercise Voice Integration Module - Now Event-Driven
Connects voice assistant with exercise engine using event-based triggering.
Replaces frame-based repetitive voice with meaningful event-driven feedback.
"""

from typing import Optional, Dict, List, Callable
import logging
from datetime import datetime
from threading import Thread

from .voice_assistant import voice_assistant
from .voice_event_engine import voice_event_engine, VoiceEventPriority
from .prediction_smoother import PredictionSmoother

logger = logging.getLogger(__name__)


class ExerciseVoiceIntegration:
    """
    Integrates voice feedback with exercise tracking
    
    Handles:
    - Exercise-specific voice guidance
    - Rep counting announcements
    - Posture correction feedback
    - Fatigue detection alerts
    - Form quality feedback
    """
    
    # Exercise-specific starting instructions
    EXERCISE_INSTRUCTIONS = {
        "Shoulder Flexion": "Raise your arm forward and up. Keep your back straight.",
        "Shoulder Extension": "Move your arm backward. Maintain control.",
        "Shoulder Abduction": "Raise your arm sideways. Keep it smooth.",
        "Shoulder Adduction": "Lower your arm to your body. Controlled movement.",
        "Shoulder Internal Rotation": "Rotate your arm inward. Slow and steady.",
        "Shoulder External Rotation": "Rotate your arm outward. Maintain your posture.",
        "Elbow Flexion": "Bend your elbow toward your shoulder. Keep your arm stable.",
        "Elbow Extension": "Straighten your arm. No locking at the elbow.",
        "Knee Flexion": "Bend your knee toward your body. Move slowly.",
        "Knee Extension": "Straighten your leg. Controlled movement.",
        "Hip Abduction": "Move your leg outward. Keep your torso steady.",
        "Hip Flexion": "Raise your leg upward. No back arching.",
        "Hip Extension": "Move your leg backward. Engage your core.",
        "Ankle Dorsiflexion": "Point your toes upward. Feel the stretch.",
        "Ankle Plantarflexion": "Point your toes downward. Slow movement.",
        "Ankle Inversion": "Turn your sole inward. Small controlled movements.",
        "Ankle Eversion": "Turn your sole outward. Maintain balance.",
        "Body Weight Squat": "Bend your knees and lower your body. Back straight.",
        "Wall Sit": "Lower your back against the wall. Strong stance.",
        "Sumo Squat": "Wide stance, bend your knees. Keep chest up.",
        "Partial Squat": "Slightly bend your knees. Controlled movement.",
        "Calf Raises": "Rise up on your toes. Balance is important.",
        "Wrist Flexion": "Bend your wrist downward. Slow and steady.",
        "Wrist Extension": "Bend your wrist upward. Maintain control.",
        "Neck Flexion": "Bend your neck forward. Don't force the movement.",
        "Neck Extension": "Bend your neck backward. Take it easy.",
        "Neck Rotation": "Turn your head side to side. Smooth motion.",
        "Back Extension": "Arch your back carefully. Engage your core.",
    }
    
    # Posture correction messages
    POSTURE_CORRECTIONS = {
        "keep_back_straight": "Keep your back straight. Shoulders back.",
        "keep_elbow_bent": "Keep your elbow bent. Maintain the position.",
        "slower_movement": "Slow down. More controlled movements please.",
        "fuller_range": "Increase your range of motion. Go a bit further.",
        "maintain_position": "Hold this position steady. Engage your core.",
        "level_shoulders": "Keep your shoulders level. No shrugging.",
        "core_engaged": "Engage your core. Tighten your abs.",
        "head_straight": "Keep your head in neutral position.",
        "no_jerking": "Smooth movements. Avoid jerky motions.",
        "control_descent": "Control the downward movement. Don't drop suddenly.",
        "stabilize": "Stabilize your body. Use your core.",
    }
    
    # Form quality feedback
    FORM_FEEDBACK = {
        "excellent": [
            "Excellent form!",
            "Perfect form! Keep it up!",
            "Outstanding form! Well done!",
            "Great form! Continue like this!",
        ],
        "good": [
            "Good form. Keep going.",
            "Nice form. Well done.",
            "Good movement. Continue.",
            "You're doing well.",
        ],
        "poor": [
            "Check your form. Pay attention to your posture.",
            "Adjust your form. Focus more carefully.",
            "Watch your form. Try to improve.",
            "Check your alignment. Be more careful.",
        ],
    }
    
class ExerciseVoiceIntegration:
    """
    Event-Driven Voice Feedback Integration.
    
    Provides voice feedback ONLY when meaningful exercise changes occur:
    - Exercise start
    - Rep completion
    - Posture errors
    - State transitions
    
    NOT frame-based (no repeated voice every frame).
    Uses PredictionSmoother for stable exercise detection.
    Uses VoiceEventEngine for state machine and event management.
    """
    
    # Exercise-specific instructions
    EXERCISE_INSTRUCTIONS = {
        "Shoulder Flexion": "Raise your arm forward and up. Keep your back straight.",
        "Shoulder Extension": "Move your arm backward. Maintain control.",
        "Shoulder Abduction": "Raise your arm sideways. Keep it smooth.",
        "Shoulder Adduction": "Lower your arm to your body. Controlled movement.",
        "Shoulder Internal Rotation": "Rotate your arm inward. Slow and steady.",
        "Shoulder External Rotation": "Rotate your arm outward. Maintain your posture.",
        "Elbow Flexion": "Bend your elbow toward your shoulder. Keep your arm stable.",
        "Elbow Extension": "Straighten your arm. No locking at the elbow.",
        "Knee Flexion": "Bend your knee toward your body. Move slowly.",
        "Knee Extension": "Straighten your leg. Controlled movement.",
        "Hip Abduction": "Move your leg outward. Keep your torso steady.",
        "Hip Flexion": "Raise your leg upward. No back arching.",
        "Hip Extension": "Move your leg backward. Engage your core.",
        "Ankle Dorsiflexion": "Point your toes upward. Feel the stretch.",
        "Ankle Plantarflexion": "Point your toes downward. Slow movement.",
        "Ankle Inversion": "Turn your sole inward. Small controlled movements.",
        "Ankle Eversion": "Turn your sole outward. Maintain balance.",
        "Body Weight Squat": "Bend your knees and lower your body. Back straight.",
        "Wall Sit": "Lower your back against the wall. Strong stance.",
        "Sumo Squat": "Wide stance, bend your knees. Keep chest up.",
        "Partial Squat": "Slightly bend your knees. Controlled movement.",
        "Calf Raises": "Rise up on your toes. Balance is important.",
        "Wrist Flexion": "Bend your wrist downward. Slow and steady.",
        "Wrist Extension": "Bend your wrist upward. Maintain control.",
        "Neck Flexion": "Bend your neck forward. Don't force the movement.",
        "Neck Extension": "Bend your neck backward. Take it easy.",
        "Neck Rotation": "Turn your head side to side. Smooth motion.",
        "Back Extension": "Arch your back carefully. Engage your core.",
    }
    
    def __init__(self, 
                 smoothing_window: int = 10,
                 confidence_threshold: float = 0.70,
                 angle_threshold: float = 10.0):
        """
        Initialize event-driven voice integration.
        
        Args:
            smoothing_window: Frames to smooth over (default 10)
            confidence_threshold: Min confidence for stable prediction (0-1)
            angle_threshold: Min angle movement to register (degrees)
        """
        # Per-user smoothers
        self.user_smoothers: Dict[str, PredictionSmoother] = {}
        
        # Voice event engine
        self.event_engine = voice_event_engine
        
        # Configuration
        self.smoothing_window = smoothing_window
        self.confidence_threshold = confidence_threshold
        self.angle_threshold = angle_threshold
        
        # User session tracking
        self.user_sessions: Dict[str, Dict] = {}
        
        # Register voice callback
        self._setup_voice_callbacks()
        
        logger.info("✅ ExerciseVoiceIntegration initialized (Event-Driven)")
    
    def process_frame(self,
                     user_id: str,
                     exercise_name: str,
                     current_angle: float,
                     quality_score: float = 0.0,
                     confidence: float = 1.0,
                     posture_correct: bool = True) -> Dict:
        """
        Process a single frame for voice feedback.
        
        THIS IS THE MAIN ENTRY POINT FOR VOICE INTEGRATION.
        
        Args:
            user_id: User identifier
            exercise_name: Current exercise name
            current_angle: Joint angle in degrees
            quality_score: Form quality (0-1)
            confidence: Exercise detection confidence (0-1)
            posture_correct: Whether posture is acceptable
        
        Returns:
            Dict with voice events:
            - event_triggered: bool
            - event_type: str
            - message: str (what to say)
            - priority: str
        """
        # Get or create smoother for this user
        if user_id not in self.user_smoothers:
            self.user_smoothers[user_id] = PredictionSmoother(
                window_size=self.smoothing_window,
                confidence_threshold=self.confidence_threshold
            )
        
        smoother = self.user_smoothers[user_id]
        
        # Smooth the prediction
        smooth_result = smoother.update(
            exercise=exercise_name,
            confidence=confidence,
            angle=current_angle,
            quality_score=quality_score
        )
        
        # Only proceed if prediction is stable
        if not smooth_result["is_stable"]:
            return {
                "event_triggered": False,
                "event_type": None,
                "message": None,
                "priority": None,
            }
        
        # Use smoothed values
        stable_exercise = smooth_result["exercise"]
        stable_confidence = smooth_result["confidence"]
        avg_angle = smooth_result["angle"] or current_angle
        
        # Process through event engine
        event_result = self.event_engine.process_frame(
            user_id=user_id,
            exercise_name=stable_exercise,
            current_angle=avg_angle,
            quality_score=quality_score,
            posture_correct=posture_correct
        )
        
        return event_result
    
    def _setup_voice_callbacks(self):
        """Set up callbacks for voice events"""
        def on_event(event: Dict):
            """Callback when event is triggered"""
            if event["event_type"] == "exercise_start":
                self._speak_exercise_start(event)
            elif event["event_type"] == "rep_completed":
                self._speak_rep_completed(event)
            elif event["event_type"] == "posture_correction":
                self._speak_posture_correction(event)
            else:
                # Generic event
                if event["message"]:
                    voice_assistant.speak(event["message"], priority="normal")
        
        # Register callback
        self.event_engine.register_callback("exercise_start", on_event)
        self.event_engine.register_callback("rep_completed", on_event)
        self.event_engine.register_callback("posture_correction", on_event)
    
    def _speak_exercise_start(self, event: Dict):
        """Speak exercise start instruction"""
        exercise = event["metadata"]["exercise"]
        
        instruction = self.EXERCISE_INSTRUCTIONS.get(
            exercise,
            f"Starting {exercise}. Focus on proper form."
        )
        
        voice_assistant.speak(instruction, priority="high")
    
    def _speak_rep_completed(self, event: Dict):
        """Speak rep completion announcement"""
        rep_count = event["metadata"]["rep_count"]
        message = event["message"]
        
        voice_assistant.speak(message, priority="high")
    
    def _speak_posture_correction(self, event: Dict):
        """Speak posture correction"""
        message = event["message"]
        voice_assistant.speak(message, priority="high")
    
    def reset_user_session(self, user_id: str):
        """Reset session for user (e.g., when exercise changed)"""
        if user_id in self.user_smoothers:
            del self.user_smoothers[user_id]
        
        self.event_engine.reset_session(user_id)
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        logger.info(f"User session reset: {user_id}")
    
    # Voice control methods
    def enable_voice(self):
        """Enable voice"""
        voice_assistant.enable()
        logger.info("Voice enabled")
    
    def disable_voice(self):
        """Disable voice"""
        voice_assistant.disable()
        logger.info("Voice disabled")
    
    def toggle_voice(self) -> bool:
        """Toggle voice on/off"""
        return voice_assistant.toggle()
    
    def is_voice_enabled(self) -> bool:
        """Check if voice is enabled"""
        return voice_assistant.enabled
    
    def adjust_voice_speed(self, speed: int):
        """Adjust speech speed (WPM: 50-300)"""
        voice_assistant.set_speed(speed)
    
    def adjust_voice_volume(self, volume: float):
        """Adjust voice volume (0-1)"""
        voice_assistant.set_volume(volume)
    
    def get_voice_status(self) -> Dict:
        """Get current voice status"""
        stats = voice_assistant.get_statistics() if hasattr(voice_assistant, 'get_statistics') else {}
        return {
            "enabled": voice_assistant.enabled,
            "speed": voice_assistant.voice_speed if hasattr(voice_assistant, 'voice_speed') else 150,
            "volume": voice_assistant.voice_volume if hasattr(voice_assistant, 'voice_volume') else 0.8,
            "total_messages": getattr(voice_assistant, 'total_messages', 0),
        }
    
    def get_session_summary(self, user_id: str) -> Dict:
        """Get current session summary for user"""
        session_state = self.event_engine.get_session_state(user_id)
        
        if not session_state:
            return {}
        
        return {
            "exercise": session_state.get("exercise"),
            "reps_completed": session_state.get("reps", 0),
            "quality_score": session_state.get("quality", 0.0),
            "current_angle": session_state.get("angle", 0.0),
            "posture_correct": session_state.get("posture_correct", True),
        }


# Global integration instance
exercise_voice_integration = ExerciseVoiceIntegration()

# Export
__all__ = [
    'ExerciseVoiceIntegration',
    'exercise_voice_integration',
]
