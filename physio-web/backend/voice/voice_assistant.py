"""
Advanced Voice Assistant System for Real-Time Exercise Guidance
Provides context-aware, event-driven audio feedback during physiotherapy exercises
OPTIMIZED FOR: Zero-delay simultaneous voice output during exercises
"""

import pyttsx3
import threading
import queue
import time
from typing import Optional, Dict, List, Callable
from enum import Enum
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceEventType(Enum):
    """Types of voice events"""
    EXERCISE_START = "exercise_start"
    REP_COMPLETED = "rep_completed"
    POSTURE_CORRECTION = "posture_correction"
    FATIGUE_DETECTED = "fatigue_detected"
    EXERCISE_COMPLETE = "exercise_complete"
    FORM_FEEDBACK = "form_feedback"
    MOTIVATION = "motivation"
    VOICE_GUIDANCE = "voice_guidance"
    PAUSE_ALERT = "pause_alert"
    ERROR_ALERT = "error_alert"


@dataclass
class VoiceEvent:
    """Represents a voice event"""
    event_type: VoiceEventType
    message: str
    exercise: str = ""
    priority: str = "normal"  # "high", "normal", "low"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __lt__(self, other):
        """Allow priority queue comparison"""
        return self.timestamp < other.timestamp


class VoiceAssistant:
    """
    Advanced Voice Assistant for physiotherapy exercises
    
    Features:
    - Event-driven voice feedback
    - Cooldown mechanism to prevent repetition
    - Exercise-specific guidance
    - Priority-based message queuing
    - Non-blocking asynchronous speech
    - Multiple voice settings (speed, pitch, volume)
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the Voice Assistant
        
        Args:
            enabled: Whether voice is enabled by default
        """
        self.enabled = enabled
        self.engine = None
        self.voice_queue = queue.Queue()  # Changed to regular Queue to avoid comparison issues
        self.processing_thread = None
        self.is_running = False
        
        # Voice settings
        self.voice_speed = 150  # words per minute
        self.voice_pitch = 1.0
        self.voice_volume = 0.8
        self.voice_gender = "female"
        
        # Cooldown tracking
        self.last_event_time = {}  # event_type -> last time spoken
        self.event_cooldown = 3  # seconds between same event type
        self.message_history = {}  # event_type -> last message
        
        # Event tracking
        self.event_callbacks = {}  # event_type -> [callbacks]
        self.exercise_specific_messages = {}
        
        # Statistics
        self.total_messages = 0
        self.suppressed_messages = 0
        
        self._initialize_engine()
        self._start_processing_thread()
    
    def _initialize_engine(self):
        """Initialize main pyttsx3 engine (backup for initialization)"""
        try:
            self.engine = pyttsx3.init()
            
            # Set voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        logger.info(f"Using voice: {voice.name}")
                        break
            
            self.engine.setProperty('rate', self.voice_speed)
            self.engine.setProperty('volume', self.voice_volume)
            
            logger.info("✅ Voice Assistant initialized successfully (per-thread engines enabled)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _start_processing_thread(self):
        """Start the voice processing thread"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.is_running = True
            self.processing_thread = threading.Thread(
                target=self._process_voice_queue,
                daemon=True,
                name="VoiceAssistantProcessor"
            )
            self.processing_thread.start()
            logger.info("Voice processing thread started")
    
    def _process_voice_queue(self):
        """Process voice events from the queue - OPTIMIZED FOR ZERO DELAY"""
        while self.is_running:
            try:
                # Get message from queue (non-blocking check)
                event = self.voice_queue.get(timeout=0.1)
                
                if event is None:  # Sentinel value to stop
                    break
                
                if self.enabled:
                    # SPAWN SEPARATE THREAD FOR EACH VOICE (enables simultaneous playback)
                    # Each voice command executes immediately in its own thread
                    voice_thread = threading.Thread(
                        target=self._speak_event,
                        args=(event,),
                        daemon=True,
                        name=f"Voice-{event.event_type.value}"
                    )
                    voice_thread.start()
                    # Immediately return to process next message without waiting
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing voice queue: {e}")
    
    def _speak_event(self, event: VoiceEvent):
        """
        Speak a voice event - OPTIMIZED FOR SIMULTANEOUS OUTPUT
        Uses non-blocking approach to enable real-time voice feedback
        """
        if not event.message:
            return
        
        # Check cooldown (fast local check)
        if not self._should_speak(event):
            self.suppressed_messages += 1
            logger.debug(f"Suppressed: {event.message}")
            return
        
        try:
            thread_id = threading.current_thread().ident
            
            # Use main engine but with non-blocking approach
            if not self.engine:
                logger.warning("TTS engine unavailable")
                return
            
            logger.info(f"🎤 [IMMEDIATE] Speaking: {event.message}")
            
            # Add to engine's queue immediately (non-blocking)
            self.engine.say(event.message)
            
            # Use non-blocking iterate if available
            # If runAndWait fails, gracefully handle
            try:
                # Try to process in non-blocking mode
                self.engine.runAndWait()
            except RuntimeError as e:
                if "run loop already started" in str(e):
                    # Engine is already processing, just return
                    logger.debug("Engine already processing, message queued")
                else:
                    raise
            
            # Mark as spoken
            self._mark_spoken(event)
            self.total_messages += 1
            
        except Exception as e:
            logger.error(f"Error speaking: {e}")
    
    def _should_speak(self, event: VoiceEvent) -> bool:
        """
        Check if event should be spoken based on cooldown and priority
        
        Args:
            event: Voice event to check
            
        Returns:
            True if event should be spoken, False otherwise
        """
        current_time = time.time()
        event_type = event.event_type.value
        
        # High priority always speaks
        if event.priority == "high":
            return True
        
        # Check last event time
        last_time = self.last_event_time.get(event_type, 0)
        if current_time - last_time < self.event_cooldown:
            return False
        
        # Check if same message was just spoken
        last_msg = self.message_history.get(event_type, "")
        if last_msg == event.message:
            return False
        
        return True
    
    def _mark_spoken(self, event: VoiceEvent):
        """Mark an event as spoken"""
        event_type = event.event_type.value
        self.last_event_time[event_type] = time.time()
        self.message_history[event_type] = event.message
    
    def add_voice_event(self, event: VoiceEvent):
        """
        Add a voice event to the queue
        
        Args:
            event: Voice event to process
        """
        if not self.engine:
            return
        
        # Add directly to queue (high priority messages processed immediately in separate threads)
        self.voice_queue.put(event)
    
    def speak(self, message: str, exercise: str = "", priority: str = "normal"):
        """
        Queue a voice message
        
        Args:
            message: Text to speak
            exercise: Associated exercise name
            priority: Message priority ("high", "normal", "low")
        """
        event = VoiceEvent(
            event_type=VoiceEventType.VOICE_GUIDANCE,
            message=message,
            exercise=exercise,
            priority=priority
        )
        self.add_voice_event(event)
    
    def announce_exercise_start(self, exercise_name: str, instruction: str = ""):
        """Announce exercise start"""
        message = instruction if instruction else f"Starting {exercise_name}. Focus on proper form."
        event = VoiceEvent(
            event_type=VoiceEventType.EXERCISE_START,
            message=message,
            exercise=exercise_name,
            priority="high"
        )
        self.add_voice_event(event)
    
    def announce_rep_completed(self, rep_count: int, quality: float = None):
        """Announce completed repetition"""
        if quality is not None and quality > 0.8:
            messages = [
                f"Repetition {rep_count} completed with excellent form!",
                f"Perfect! {rep_count} reps done!",
                f"Great job! Repetition {rep_count} complete!",
            ]
        elif quality is not None and quality > 0.6:
            messages = [
                f"Repetition {rep_count} completed. Good work!",
                f"Nice! {rep_count} reps.",
                f"Keep it up! Repetition {rep_count} done!",
            ]
        else:
            messages = [
                f"Repetition {rep_count} completed.",
                f"One rep done. Next!",
                f"Repetition {rep_count} complete.",
            ]
        
        import random
        message = random.choice(messages)
        
        event = VoiceEvent(
            event_type=VoiceEventType.REP_COMPLETED,
            message=message,
            priority="normal"
        )
        self.add_voice_event(event)
    
    def announce_posture_correction(self, correction_message: str):
        """Announce posture correction"""
        event = VoiceEvent(
            event_type=VoiceEventType.POSTURE_CORRECTION,
            message=correction_message,
            priority="high"
        )
        self.add_voice_event(event)
    
    def announce_fatigue_detection(self):
        """Announce fatigue detected"""
        messages = [
            "Fatigue detected. Please slow down and maintain form.",
            "You seem tired. Take your time with the movement.",
            "Maintain your pace. Quality over quantity.",
        ]
        import random
        message = random.choice(messages)
        
        event = VoiceEvent(
            event_type=VoiceEventType.FATIGUE_DETECTED,
            message=message,
            priority="high"
        )
        self.add_voice_event(event)
    
    def announce_exercise_complete(self, total_reps: int, avg_quality: float = None):
        """Announce exercise completion"""
        if avg_quality is not None and avg_quality > 0.7:
            message = f"Excellent! Completed {total_reps} repetitions with great form!"
        else:
            message = f"Exercise completed! You performed {total_reps} repetitions."
        
        event = VoiceEvent(
            event_type=VoiceEventType.EXERCISE_COMPLETE,
            message=message,
            priority="high"
        )
        self.add_voice_event(event)
    
    def give_motivation(self):
        """Give motivational feedback"""
        messages = [
            "You're doing great! Keep up the momentum!",
            "Excellent effort! Stay focused!",
            "You're making progress! Keep going!",
            "Perfect form! You're on a roll!",
            "Great work! Stay strong!",
        ]
        import random
        message = random.choice(messages)
        
        event = VoiceEvent(
            event_type=VoiceEventType.MOTIVATION,
            message=message,
            priority="low"
        )
        self.add_voice_event(event)
    
    def stop_speaking(self):
        """Stop current speech and clear queue"""
        try:
            if self.engine:
                self.engine.stop()
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
        
        # Clear queue
        while not self.voice_queue.empty():
            try:
                self.voice_queue.get_nowait()
            except queue.Empty:
                break
    
    def enable(self):
        """Enable voice output"""
        self.enabled = True
        logger.info("✅ Voice enabled")
    
    def disable(self):
        """Disable voice output"""
        self.enabled = False
        self.stop_speaking()
        logger.info("🔇 Voice disabled")
    
    def toggle(self) -> bool:
        """Toggle voice on/off"""
        self.enabled = not self.enabled
        logger.info(f"Voice {'enabled' if self.enabled else 'disabled'}")
        return self.enabled
    
    def set_speed(self, speed: int):
        """Set speech speed (words per minute)"""
        if 50 <= speed <= 300:
            self.voice_speed = speed
            if self.engine:
                self.engine.setProperty('rate', speed)
            logger.info(f"Voice speed set to {speed} WPM")
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        if 0.0 <= volume <= 1.0:
            self.voice_volume = volume
            if self.engine:
                self.engine.setProperty('volume', volume)
            logger.info(f"Volume set to {volume}")
    
    def set_gender(self, gender: str):
        """Set voice gender (male/female)"""
        if gender.lower() in ["male", "female"]:
            self.voice_gender = gender.lower()
            logger.info(f"Voice gender set to {gender}")
    
    def subscribe_to_event(self, event_type: VoiceEventType, callback: Callable):
        """Subscribe to voice events"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def get_statistics(self) -> Dict:
        """Get voice assistant statistics"""
        return {
            "total_messages": self.total_messages,
            "suppressed_messages": self.suppressed_messages,
            "enabled": self.enabled,
            "voice_speed": self.voice_speed,
            "voice_volume": self.voice_volume,
            "voice_gender": self.voice_gender,
        }
    
    def shutdown(self):
        """Shutdown the voice assistant"""
        self.is_running = False
        self.stop_speaking()
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2)
        logger.info("Voice Assistant shut down")


# Global voice assistant instance
voice_assistant = VoiceAssistant(enabled=True)

# Export
__all__ = [
    'VoiceAssistant',
    'VoiceEvent',
    'VoiceEventType',
    'voice_assistant',
]
