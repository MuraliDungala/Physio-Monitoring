"""
Session Manager
Handles saving and loading exercise sessions from database
"""

from database import ExerciseSession, get_db
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def save_exercise_session(user_id: int, exercise_name: str, reps: int, 
                         avg_angle: float = 0.0, quality_score: float = 0.0, 
                         duration_seconds: int = 0, posture_score: float = 100.0) -> bool:
    """
    Save exercise session to database
    Returns True if successful, False otherwise
    """
    try:
        db = next(get_db())
        
        # Create session record
        session = ExerciseSession(
            user_id=user_id,
            exercise_name=exercise_name,
            total_reps=reps,
            average_joint_angle=avg_angle,
            quality_score=quality_score,
            duration_seconds=duration_seconds,
            posture_correctness=posture_score,
            date=datetime.utcnow()
        )
        
        db.add(session)
        db.commit()
        
        logger.info(f"Saved session: User={user_id}, Exercise={exercise_name}, Reps={reps}")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Error saving exercise session: {e}")
        return False

def get_user_sessions(user_id: int, limit: int = 50) -> list:
    """Get recent exercise sessions for a user"""
    try:
        db = next(get_db())
        
        sessions = db.query(ExerciseSession).filter(
            ExerciseSession.user_id == user_id
        ).order_by(ExerciseSession.date.desc()).limit(limit).all()
        
        db.close()
        return sessions
        
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return []

def get_exercise_stats(user_id: int, exercise_name: str) -> dict:
    """Get statistics for a specific exercise"""
    try:
        db = next(get_db())
        
        sessions = db.query(ExerciseSession).filter(
            ExerciseSession.user_id == user_id,
            ExerciseSession.exercise_name == exercise_name
        ).all()
        
        if not sessions:
            db.close()
            return {
                "total_sessions": 0,
                "total_reps": 0,
                "avg_reps": 0,
                "max_reps": 0,
                "avg_quality": 0
            }
        
        total_reps = sum(s.total_reps for s in sessions)
        avg_quality = sum(s.quality_score for s in sessions) / len(sessions)
        max_reps = max(s.total_reps for s in sessions)
        
        stats = {
            "total_sessions": len(sessions),
            "total_reps": total_reps,
            "avg_reps": total_reps / len(sessions),
            "max_reps": max_reps,
            "avg_quality": avg_quality
        }
        
        db.close()
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return {}
