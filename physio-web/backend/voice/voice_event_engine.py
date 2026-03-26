"""
Voice Event Engine - Event-Driven Voice Management
Manages state machine and decides when to trigger voice based on exercise progression.
Eliminates repeated voice by only triggering on meaningful state changes.
"""

from enum import Enum
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ExerciseState(Enum):
    """Exercise progression states"""
    IDLE = "idle"
    EXERCISE_READY = "exercise_ready"
    EXERCISE_IN_PROGRESS = "in_progress"
    REP_ASCENDING = "rep_ascending"  # Moving up/increasing angle
    REP_DESCENDING = "rep_descending"  # Moving down/decreasing angle
    REP_COMPLETED = "rep_completed"  # Rep cycle finished
    POSTURE_ERROR = "posture_error"  # Incorrect posture detected
    FATIGUE_ALERT = "fatigue_alert"
    EXERCISE_PAUSED = "paused"
    EXERCISE_FINISHED = "finished"


class VoiceEventPriority(Enum):
    """Voice event priority levels"""
    CRITICAL = 0  # Posture errors, safety alerts
    HIGH = 1      # Rep completion, exercise start
    NORMAL = 2    # General feedback
    LOW = 3       # Motivation, form feedback


@dataclass
class ExerciseSession:
    """Track an exercise session state"""
    exercise_name: str
    session_state: ExerciseState
    reps_completed: int = 0
    current_angle: float = 0.0
    previous_angle: float = 0.0
    quality_score: float = 0.0
    posture_correct: bool = True
    fatigue_detected: bool = False
    
    # State transition tracking
    last_state_change_time: datetime = None
    last_voice_event_time: datetime = None
    last_event_type: str = None
    
    # Angle progression tracking
    angle_direction: str = "none"  # "up", "down", "none"
    peak_angle: float = 0.0
    valley_angle: float = 0.0
    
    def __post_init__(self):
        if self.last_state_change_time is None:
            self.last_state_change_time = datetime.now()
        if self.last_voice_event_time is None:
            self.last_voice_event_time = datetime.now() - timedelta(seconds=10)


class VoiceEventEngine:
    """
    Event-driven voice management system.
    
    Core responsibility:
    - Only trigger voice on meaningful state changes
    - Maintain cooldown between voice events
    - Detect rep completion from angle progression
    - Manage posture error states
    """
    
    def __init__(self, 
                 cooldown_seconds: Dict[str, float] = None,
                 angle_threshold: float = 10.0):
        """
        Initialize event engine.
        
        Args:
            cooldown_seconds: Dict of event_type -> min_seconds between voice for that event
            angle_threshold: Minimum angle change to register movement (degrees)
        """
        # Cooldown periods for different event types
        self.cooldown_seconds = cooldown_seconds or {
            "rep_completed": 2.0,      # Can announce reps every 2 seconds
            "posture_correction": 5.0,  # Don't repeat posture corrections too often
            "exercise_start": 30.0,     # Don't restart same exercise within 30 sec
            "fatigue": 10.0,            # Don't warn about fatigue too often
            "feedback": 3.0,            # General feedback cooldown
        }
        
        self.angle_threshold = angle_threshold  # Movement threshold to detect activity
        
        # Session tracking
        self.user_sessions: Dict[str, ExerciseSession] = {}
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        logger.info(f"VoiceEventEngine initialized with cooldown policy: {self.cooldown_seconds}")
    
    def process_frame(self, 
                     user_id: str,
                     exercise_name: str,
                     current_angle: float,
                     quality_score: float = 0.0,
                     posture_correct: bool = True) -> Dict:
        """
        Process a new frame for a user.
        
        Returns:
            Dict with:
            - event_triggered: bool (True if voice event should fire)
            - event_type: str (type of event)
            - event_priority: VoiceEventPriority
            - message: str (what to say)
            - metadata: Dict (additional context)
        """
        # Get or create session
        session = self._get_or_create_session(user_id, exercise_name)
        
        # Update session state
        session.previous_angle = session.current_angle
        session.current_angle = current_angle
        session.quality_score = quality_score
        session.posture_correct = posture_correct
        
        # Detect state transitions
        events = []
        
        # 1. Check for exercise change
        if session.exercise_name != exercise_name:
            event = self._handle_exercise_change(session, exercise_name)
            if event:
                events.append(event)
        
        # 2. Check for movement
        angle_delta = abs(session.current_angle - session.previous_angle)
        is_moving = angle_delta > self.angle_threshold
        
        # 3. Update angle direction
        if is_moving:
            if session.current_angle > session.previous_angle:
                session.angle_direction = "up"
                session.peak_angle = max(session.peak_angle, session.current_angle)
            else:
                session.angle_direction = "down"
                session.valley_angle = min(session.valley_angle, session.current_angle)
        
        # 4. Check for posture error
        if not posture_correct and session.posture_correct:
            event = self._handle_posture_error(session)
            if event:
                events.append(event)
        
        session.posture_correct = posture_correct
        
        # 5. Check for rep completion (angle peak -> valley transition)
        rep_event = self._detect_rep_completion(session)
        if rep_event:
            events.append(rep_event)
        
        # 6. Check for idle/no movement
        if not is_moving:
            if session.session_state not in [ExerciseState.IDLE, ExerciseState.EXERCISE_PAUSED]:
                # User is idle - not moving
                self._transition_state(session, ExerciseState.EXERCISE_PAUSED)
        
        # Filter events by cooldown
        valid_events = self._filter_by_cooldown(session, events)
        
        # Return the highest priority event if any
        if valid_events:
            valid_events.sort(key=lambda x: x["priority"].value)
            event = valid_events[0]
            session.last_voice_event_time = datetime.now()
            session.last_event_type = event["event_type"]
            
            logger.info(f"Voice event triggered for user {user_id}: {event['event_type']} - {event['message']}")
            
            # Fire callbacks
            self._fire_callbacks(event["event_type"], event)
            
            return {
                "event_triggered": True,
                "event_type": event["event_type"],
                "priority": event["priority"],
                "message": event["message"],
                "metadata": event.get("metadata", {}),
            }
        
        return {
            "event_triggered": False,
            "event_type": None,
            "priority": None,
            "message": None,
            "metadata": {},
        }
    
    def _get_or_create_session(self, user_id: str, exercise_name: str) -> ExerciseSession:
        """Get session or create new one if exercise changed"""
        if user_id not in self.user_sessions:
            session = ExerciseSession(exercise_name, ExerciseState.EXERCISE_READY)
            self.user_sessions[user_id] = session
            logger.info(f"Created new session for user {user_id}: {exercise_name}")
            return session
        
        return self.user_sessions[user_id]
    
    def _handle_exercise_change(self, session: ExerciseSession, new_exercise: str) -> Optional[Dict]:
        """Handle exercise change event"""
        old_exercise = session.exercise_name
        
        # Reset session for new exercise
        session.exercise_name = new_exercise
        session.reps_completed = 0
        session.peak_angle = 0.0
        session.valley_angle = 0.0
        
        self._transition_state(session, ExerciseState.EXERCISE_READY)
        
        # Check cooldown for exercise start
        if self._can_trigger_event(session, "exercise_start"):
            return {
                "event_type": "exercise_start",
                "priority": VoiceEventPriority.HIGH,
                "message": f"Starting {new_exercise}. Focus on proper form.",
                "metadata": {"exercise": new_exercise, "previous_exercise": old_exercise},
            }
        
        return None
    
    def _detect_rep_completion(self, session: ExerciseSession) -> Optional[Dict]:
        """
        Detect rep completion based on angle progression.
        
        Rep = peak angle -> valley angle -> back to peak (one cycle)
        """
        # Need minimum angle range to detect movement
        angle_range = abs(session.peak_angle - session.valley_angle)
        if angle_range < self.angle_threshold:
            return None
        
        # Detect completion: going down after going up, and crossed the valley
        if (session.angle_direction == "down" and 
            session.previous_angle > session.current_angle and
            session.peak_angle > session.valley_angle + self.angle_threshold):
            
            # Check if we've descended enough to signal rep completion
            # A rep is complete when angle drops to ~20% of the range below peak
            midpoint = session.valley_angle + (session.peak_angle - session.valley_angle) * 0.3
            
            if session.current_angle <= midpoint:
                # This looks like a rep completion
                session.reps_completed += 1
                
                if self._can_trigger_event(session, "rep_completed"):
                    # Reset peak/valley for next rep
                    session.peak_angle = session.current_angle
                    session.valley_angle = session.current_angle
                    
                    return {
                        "event_type": "rep_completed",
                        "priority": VoiceEventPriority.HIGH,
                        "message": f"Rep {session.reps_completed} complete. Great job!",
                        "metadata": {
                            "rep_count": session.reps_completed,
                            "quality": session.quality_score,
                            "angle": session.current_angle,
                        },
                    }
        
        return None
    
    def _handle_posture_error(self, session: ExerciseSession) -> Optional[Dict]:
        """Handle posture error transition"""
        self._transition_state(session, ExerciseState.POSTURE_ERROR)
        
        if self._can_trigger_event(session, "posture_correction"):
            return {
                "event_type": "posture_correction",
                "priority": VoiceEventPriority.CRITICAL,
                "message": "Correct your posture. Keep your back straight.",
                "metadata": {"session_state": session.session_state.value},
            }
        
        return None
    
    def _transition_state(self, session: ExerciseSession, new_state: ExerciseState):
        """Transition to new state"""
        if session.session_state != new_state:
            old_state = session.session_state
            session.session_state = new_state
            session.last_state_change_time = datetime.now()
            logger.debug(f"State transition: {old_state.value} → {new_state.value}")
    
    def _can_trigger_event(self, session: ExerciseSession, event_type: str) -> bool:
        """Check if event can be triggered based on cooldown"""
        if event_type not in self.cooldown_seconds:
            return True
        
        cooldown = self.cooldown_seconds[event_type]
        time_since_last = (datetime.now() - session.last_voice_event_time).total_seconds()
        
        return time_since_last >= cooldown
    
    def _filter_by_cooldown(self, session: ExerciseSession, events: List[Dict]) -> List[Dict]:
        """Filter events by cooldown - only allow if enough time has passed"""
        filtered = []
        
        for event in events:
            event_type = event["event_type"]
            if self._can_trigger_event(session, event_type):
                filtered.append(event)
        
        return filtered
    
    def reset_session(self, user_id: str):
        """Reset session for a user"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            logger.info(f"Session reset for user {user_id}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for event type"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
    
    def _fire_callbacks(self, event_type: str, event: Dict):
        """Fire registered callbacks for event"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in callback for {event_type}: {e}")
    
    def get_session_state(self, user_id: str) -> Optional[Dict]:
        """Get current session state for debugging"""
        if user_id not in self.user_sessions:
            return None
        
        session = self.user_sessions[user_id]
        return {
            "exercise": session.exercise_name,
            "state": session.session_state.value,
            "reps": session.reps_completed,
            "angle": session.current_angle,
            "quality": session.quality_score,
            "posture_correct": session.posture_correct,
            "angle_direction": session.angle_direction,
            "time_since_last_voice": (datetime.now() - session.last_voice_event_time).total_seconds(),
        }


# Global singleton instance
voice_event_engine = VoiceEventEngine()
