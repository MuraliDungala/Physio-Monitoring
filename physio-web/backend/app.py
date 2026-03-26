import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import json
import logging
import asyncio
import base64
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, List, Optional

from fastapi.security import OAuth2PasswordRequestForm
from config import settings

# Import existing modules
from database import User, Exercise, ExerciseSession, VoiceFeedbackLog, RehabSession, get_db, engine, Base, create_tables
from models import (
    UserCreate,
    UserResponse,
    ExerciseResponse,
    ExerciseSessionCreate,
    ExerciseSessionResponse,
    ChatMessage,
    ChatResponse,
    AIChatRequest,
    AIChatResponse,
    Token,
    ClassifyRequest,
    ClassifyResponse,
    ClassificationResult,
    LandmarksData,
    RehabPlanRequest,
    RehabPlanResponse,
    RehabDayPlan,
    RehabExercise,
    RehabSessionCreate,
    RehabSessionUpdate,
    RehabSessionResponse,
    RehabProgressResponse,
)
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_password_hash,
    create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from exercise_engine.engine import ExerciseEngine
from ml_models.advanced_classifier import advanced_classifier  # Production models
from ml_models.simple_classifier import simple_classifier  # Fallback
from ml_models.feature_extractor import FeatureExtractor
from ml_models.inference_service import ml_service
from voice.exercise_voice_guidance import voice_guidance, ExerciseVoiceGuidance
from chatbot.ai_engine import ai_chatbot

# Voice assistant - will be loaded after logging is configured
voice_assistant = None
exercise_voice_integration = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load voice assistant modules
try:
    from voice.voice_assistant import voice_assistant as va, VoiceEvent, VoiceEventType
    from voice.exercise_voice_integration import exercise_voice_integration as evi
    voice_assistant = va
    exercise_voice_integration = evi
    logger.info("✅ Voice assistant modules loaded successfully")
except Exception as e:
    logger.warning(f"Voice assistant modules not available: {e}")
    voice_assistant = None
    exercise_voice_integration = None

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intelligent Physiotherapy Monitoring System")

# Mount static files
_frontend_dir = (Path(__file__).resolve().parent.parent / "frontend")
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")

# CORS middleware
cors_origins = settings.get_cors_origins()
logger.info(f"Configuring CORS for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML models
print("🤖 Loading ML models...")
try:
    if advanced_classifier.is_ready:
        print("✅ Advanced ML models loaded!")
        print(f"   Models: {', '.join(advanced_classifier.models.keys())}")
        model_info = advanced_classifier.get_model_info()
        print(f"   Exercises: {len(model_info['classes'])}")
    else:
        print("⚠️ Advanced models not ready, using simple classifier fallback")
except Exception as e:
    print(f"⚠️ ML model loading error: {e}")
    print("🔄 Using fallback detection...")

# Initialize exercise engine
# Global engine removed - instantiated per connection
# exercise_engine = ExerciseEngine()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_exercise_state: Dict[str, Dict] = {}  # user -> exercise states for all categories
        
        # 8 main exercise categories
        self.EXERCISE_CATEGORIES = [
            "Neck", "Shoulder", "Elbow", "Wrist", 
            "Hip", "Knee", "Ankle", "Squat"
        ]
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Initialize state for all categories
        if user_id not in self.user_exercise_state:
            self.user_exercise_state[user_id] = {}
            for category in self.EXERCISE_CATEGORIES:
                self.user_exercise_state[user_id][category] = {
                    'active': True,
                    'exercises': {},
                    'last_detected': None,
                    'last_reps': 0,
                    'started': False,
                    'last_voice_time': 0,
                    'session_reps': {}
                }
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_exercise_state:
            del self.user_exercise_state[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except:
                # Connection might be closed
                self.disconnect(user_id)
    
    def get_user_state(self, user_id: str, category: str = None) -> Dict:
        """Get exercise state for specific category or all categories"""
        if user_id not in self.user_exercise_state:
            self.user_exercise_state[user_id] = {}
            for cat in self.EXERCISE_CATEGORIES:
                self.user_exercise_state[user_id][cat] = {
                    'active': True,
                    'exercises': {},
                    'last_detected': None,
                    'last_reps': 0,
                    'started': False,
                    'last_voice_time': 0,
                    'session_reps': {}
                }
        
        if category:
            if category not in self.user_exercise_state[user_id]:
                self.user_exercise_state[user_id][category] = {
                    'active': True,
                    'exercises': {},
                    'last_detected': None,
                    'last_reps': 0,
                    'started': False,
                    'last_voice_time': 0,
                    'session_reps': {}
                }
            return self.user_exercise_state[user_id][category]
        return self.user_exercise_state[user_id]
    
    def update_category_state(self, user_id: str, category: str, **kwargs):
        """Update state for specific category"""
        state = self.get_user_state(user_id, category)
        for key, value in kwargs.items():
            if key in state:
                state[key] = value

manager = ConnectionManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Create database tables
@app.on_event("startup")
async def startup_event():
    create_tables()
    # Initialize default exercises
    await init_default_exercises()

async def init_default_exercises():
    """Initialize default exercises in database"""
    db = next(get_db())
    try:
        # Get existing exercises
        existing_exercises = db.query(Exercise).all()
        existing_names = {ex.name for ex in existing_exercises}
        
        # Add missing exercises
        missing_exercises = []
        
        # Neck exercises
        if "Neck Flexion" not in existing_names:
            missing_exercises.append(Exercise(name="Neck Flexion", category="Neck",
                    description="Tuck chin to chest",
                    instructions="Sit tall, gently tuck chin to chest, hold briefly"))
        if "Neck Extension" not in existing_names:
            missing_exercises.append(Exercise(name="Neck Extension", category="Neck",
                    description="Look upward gently",
                    instructions="Sit tall, look upward gently, hold briefly"))
        if "Neck Rotation" not in existing_names:
            missing_exercises.append(Exercise(name="Neck Rotation", category="Neck",
                    description="Turn head side to side",
                    instructions="Sit tall, turn head to right, then left, gently"))
        
        # Shoulder exercises
        if "Shoulder Flexion" not in existing_names:
            missing_exercises.append(Exercise(name="Shoulder Flexion", category="Shoulder", 
                    description="Raise arm forward and upward", 
                    instructions="Keep arm straight, raise forward to shoulder height or higher"))
        if "Shoulder Extension" not in existing_names:
            missing_exercises.append(Exercise(name="Shoulder Extension", category="Shoulder",
                    description="Move arm backward",
                    instructions="Keep arm straight, move backward behind body"))
        if "Shoulder Abduction" not in existing_names:
            missing_exercises.append(Exercise(name="Shoulder Abduction", category="Shoulder",
                    description="Raise arm sideways",
                    instructions="Keep arm straight, raise to side to shoulder height"))
        if "Shoulder Adduction" not in existing_names:
            missing_exercises.append(Exercise(name="Shoulder Adduction", category="Shoulder",
                    description="Lower arm to body",
                    instructions="Lower arm from raised position back to side"))
        if "Shoulder Internal Rotation" not in existing_names:
            missing_exercises.append(Exercise(name="Shoulder Internal Rotation", category="Shoulder",
                    description="Rotate arm inward",
                    instructions="Keep elbow at side, bend 90°, rotate inward"))
        if "Shoulder External Rotation" not in existing_names:
            missing_exercises.append(Exercise(name="Shoulder External Rotation", category="Shoulder",
                    description="Rotate arm outward",
                    instructions="Keep elbow at side, bend 90°, rotate outward"))
        
        # Elbow exercises
        if "Elbow Flexion" not in existing_names:
            missing_exercises.append(Exercise(name="Elbow Flexion", category="Elbow",
                    description="Bend elbow",
                    instructions="Bend elbow bringing hand toward shoulder"))
        if "Elbow Extension" not in existing_names:
            missing_exercises.append(Exercise(name="Elbow Extension", category="Elbow",
                    description="Straighten arm",
                    instructions="Straighten elbow from bent position"))
        
        # Knee exercises
        if "Knee Flexion" not in existing_names:
            missing_exercises.append(Exercise(name="Knee Flexion", category="Knee",
                    description="Bend knee",
                    instructions="Bend knee bringing heel toward buttock"))
        if "Knee Extension" not in existing_names:
            missing_exercises.append(Exercise(name="Knee Extension", category="Knee",
                    description="Straighten knee",
                    instructions="Straighten knee from bent position, hold briefly"))
        
        # Hip exercises
        if "Hip Abduction" not in existing_names:
            missing_exercises.append(Exercise(name="Hip Abduction", category="Hip",
                    description="Move leg sideways",
                    instructions="Move leg straight out to side"))
        if "Hip Flexion" not in existing_names:
            missing_exercises.append(Exercise(name="Hip Flexion", category="Hip",
                    description="Raise leg forward",
                    instructions="Raise leg forward while keeping knee straight"))
        
        # Wrist exercises
        if "Wrist Flexion" not in existing_names:
            missing_exercises.append(Exercise(name="Wrist Flexion", category="Wrist",
                    description="Bend wrist downward",
                    instructions="Bend wrist downward, hold briefly, return to neutral"))
        if "Wrist Extension" not in existing_names:
            missing_exercises.append(Exercise(name="Wrist Extension", category="Wrist",
                    description="Bend wrist upward",
                    instructions="Bend wrist upward, hold briefly, return to neutral"))
        
        # Back exercises
        if "Back Extension" not in existing_names:
            missing_exercises.append(Exercise(name="Back Extension", category="Back",
                    description="Arch back gently",
                    instructions="Lie on stomach, gently arch back, hold briefly"))
        
        # Ankle exercises
        if "Ankle Dorsiflexion" not in existing_names:
            missing_exercises.append(Exercise(name="Ankle Dorsiflexion", category="Ankle",
                    description="Pull toes upward",
                    instructions="Sit tall, pull toes upward toward shin, hold briefly"))
        if "Ankle Plantarflexion" not in existing_names:
            missing_exercises.append(Exercise(name="Ankle Plantarflexion", category="Ankle",
                    description="Point toes downward",
                    instructions="Sit tall, point toes downward away from body, hold briefly"))
        if "Ankle Inversion" not in existing_names:
            missing_exercises.append(Exercise(name="Ankle Inversion", category="Ankle",
                    description="Turn foot inward",
                    instructions="Sit tall, turn sole of foot inward, hold briefly"))
        if "Ankle Eversion" not in existing_names:
            missing_exercises.append(Exercise(name="Ankle Eversion", category="Ankle",
                    description="Turn foot outward",
                    instructions="Sit tall, turn sole of foot outward, hold briefly"))
        if "Ankle Circles" not in existing_names:
            missing_exercises.append(Exercise(name="Ankle Circles", category="Ankle",
                    description="Rotate ankle in circles",
                    instructions="Sit tall, rotate ankle clockwise, then counterclockwise"))
        
        # Squat exercises
        if "Body Weight Squat" not in existing_names:
            missing_exercises.append(Exercise(name="Body Weight Squat", category="Squat",
                    description="Basic squat movement",
                    instructions="Stand with feet shoulder-width apart, lower hips as if sitting, keep back straight"))
        if "Wall Sit" not in existing_names:
            missing_exercises.append(Exercise(name="Wall Sit", category="Squat",
                    description="Isometric wall squat",
                    instructions="Lean against wall, slide down to 90-degree angle, hold position"))
        if "Sumo Squat" not in existing_names:
            missing_exercises.append(Exercise(name="Sumo Squat", category="Squat",
                    description="Wide-stance squat",
                    instructions="Stand with wide stance, toes out, lower hips, keep chest up"))
        if "Partial Squat" not in existing_names:
            missing_exercises.append(Exercise(name="Partial Squat", category="Squat",
                    description="Half-range squat",
                    instructions="Squat only halfway down (45 degrees), focus on control"))
        if "Squat Hold" not in existing_names:
            missing_exercises.append(Exercise(name="Squat Hold", category="Squat",
                    description="Isometric squat hold",
                    instructions="Lower to squat position, hold for several seconds, return to standing"))
        
        # Add missing exercises to database
        if missing_exercises:
            for exercise in missing_exercises:
                db.add(exercise)
            db.commit()
            logger.info(f"Added {len(missing_exercises)} missing exercises to database")
        else:
            logger.info("All exercises already exist in database")
            
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        logger.info(f"Attempting to register user: {user.username}")
        
        # Validate password length (bcrypt max is 72 bytes)
        password_bytes = user.password.encode('utf-8')
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=400, 
                detail="Password is too long. Maximum 72 bytes allowed."
            )
        
        # Validate email format
        if "@" not in user.email or "." not in user.email:
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user.username:
                logger.warning(f"Username already registered: {user.username}")
                raise HTTPException(
                    status_code=400,
                    detail="Username already registered"
                )
            else:
                logger.warning(f"Email already registered: {user.email}")
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
        
        db_user = create_user(db, user)
        logger.info(f"User registered successfully: {user.username}")
        return db_user
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration error for user {user.username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@app.post("/reset-password")
def reset_password(request_data: dict, db: Session = Depends(get_db)):
    """Reset user password by verifying username and email"""
    try:
        username = request_data.get("username", "").strip()
        email = request_data.get("email", "").strip()
        new_password = request_data.get("new_password", "")

        if not username or not email or not new_password:
            raise HTTPException(status_code=400, detail="All fields are required")

        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        # Find user by username
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="No account found with that username")

        # Verify email matches
        if user.email.lower() != email.lower():
            raise HTTPException(status_code=400, detail="Email does not match the account on file")

        # Update password
        from auth import get_password_hash
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        logger.info(f"Password reset successful for user: {username}")
        return {"message": "Password reset successful. You can now log in with your new password."}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Password reset failed. Please try again.")


@app.post("/change-password")
def change_password(
    request_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change password for the authenticated user."""
    try:
        from auth import get_password_hash, verify_password

        current_password = request_data.get("current_password", "")
        new_password = request_data.get("new_password", "")

        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Both current and new passwords are required")
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        current_user.hashed_password = get_password_hash(new_password)
        db.commit()
        logger.info(f"Password changed for user: {current_user.username}")
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Password change failed")


@app.delete("/delete-account")
def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Permanently delete the authenticated user's account and all data."""
    try:
        uid = current_user.id
        # Delete related records first
        db.query(ExerciseSession).filter(ExerciseSession.user_id == uid).delete()
        db.query(VoiceFeedbackLog).filter(VoiceFeedbackLog.user_id == uid).delete()
        db.query(User).filter(User.id == uid).delete()
        db.commit()
        logger.info(f"Account deleted: user_id={uid}")
        return {"message": "Account deleted permanently"}
    except Exception as e:
        db.rollback()
        logger.error(f"Delete account error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Account deletion failed")


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

# Exercise endpoints
@app.get("/exercises", response_model=List[ExerciseResponse])
def get_exercises(db: Session = Depends(get_db)):
    """Get all available exercises"""
    exercises = db.query(Exercise).all()
    return exercises

@app.get("/exercises/category/{category}", response_model=List[ExerciseResponse])
def get_exercises_by_category(category: str, db: Session = Depends(get_db)):
    """Get exercises by category"""
    exercises = db.query(Exercise).filter(Exercise.category == category).all()
    return exercises

@app.get("/exercises/categories")
def get_exercise_categories(db: Session = Depends(get_db)):
    """Get all exercise categories"""
    categories = db.query(Exercise.category).distinct().all()
    category_list = [cat[0] for cat in categories if cat[0] and cat[0].strip()]
    return category_list

# Exercise session endpoints
@app.post("/sessions", response_model=ExerciseSessionResponse)
def create_session(session: ExerciseSessionCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Create a new exercise session"""
    db_session = ExerciseSession(
        user_id=current_user.id,
        exercise_name=session.exercise_name,
        total_reps=session.total_reps,
        average_joint_angle=session.average_joint_angle,
        quality_score=session.quality_score,
        duration_seconds=session.duration_seconds,
        posture_correctness=session.posture_correctness
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@app.get("/sessions", response_model=List[ExerciseSessionResponse])
def get_user_sessions(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's exercise sessions"""
    sessions = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).order_by(ExerciseSession.date.desc()).all()
    return sessions

@app.get("/sessions/history", response_model=List[ExerciseSessionResponse])
def get_sessions_by_date(date: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's sessions for a specific date (YYYY-MM-DD)"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    sessions = db.query(ExerciseSession).filter(
        ExerciseSession.user_id == current_user.id,
        ExerciseSession.date >= datetime.combine(target_date, datetime.min.time()),
        ExerciseSession.date < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
    ).order_by(ExerciseSession.date.desc()).all()
    return sessions

@app.get("/sessions/{exercise_name}", response_model=List[ExerciseSessionResponse])
def get_sessions_by_exercise(exercise_name: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's sessions for specific exercise"""
    sessions = db.query(ExerciseSession).filter(
        ExerciseSession.user_id == current_user.id,
        ExerciseSession.exercise_name == exercise_name
    ).order_by(ExerciseSession.date.desc()).all()
    return sessions

@app.get("/progress/stats")
def get_progress_stats(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get comprehensive progress statistics for user"""
    sessions = db.query(ExerciseSession).filter(ExerciseSession.user_id == current_user.id).all()
    
    if not sessions:
        return {
            "total_sessions": 0,
            "total_reps": 0,
            "avg_quality_score": 0,
            "avg_posture_correctness": 0,
            "total_duration_seconds": 0,
            "days_active": 0,
            "exercises_completed": [],
            "latest_session": None,
            "best_exercise": None,
            "weekly_reps": 0
        }
    
    from datetime import timedelta
    
    # Calculate stats
    total_reps = sum(s.total_reps for s in sessions)
    avg_quality = sum(s.quality_score for s in sessions) / len(sessions) if sessions else 0
    avg_posture = sum(s.posture_correctness for s in sessions) / len(sessions) if sessions else 0
    total_duration = sum(s.duration_seconds for s in sessions)
    
    # Get unique days active
    unique_days = len(set(s.date.date() for s in sessions))
    
    # Get exercises breakdown
    exercises_dict = {}
    for session in sessions:
        if session.exercise_name not in exercises_dict:
            exercises_dict[session.exercise_name] = {"count": 0, "reps": 0, "quality": 0}
        exercises_dict[session.exercise_name]["count"] += 1
        exercises_dict[session.exercise_name]["reps"] += session.total_reps
        exercises_dict[session.exercise_name]["quality"] += session.quality_score
    
    # Calculate average quality per exercise
    for exercise in exercises_dict:
        exercises_dict[exercise]["avg_quality"] = exercises_dict[exercise]["quality"] / exercises_dict[exercise]["count"]
    
    # Find best exercise (most reps)
    best_exercise = max(exercises_dict.items(), key=lambda x: x[1]["reps"]) if exercises_dict else None
    
    # Get weekly reps (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_sessions = [s for s in sessions if s.date >= week_ago]
    weekly_reps = sum(s.total_reps for s in weekly_sessions)
    
    # Get latest session
    latest = sessions[0] if sessions else None
    latest_session_dict = {
        "id": latest.id,
        "exercise_name": latest.exercise_name,
        "date": latest.date.isoformat(),
        "total_reps": latest.total_reps,
        "quality_score": latest.quality_score,
        "posture_correctness": latest.posture_correctness
    } if latest else None
    
    return {
        "total_sessions": len(sessions),
        "total_reps": total_reps,
        "avg_quality_score": round(avg_quality, 2),
        "avg_posture_correctness": round(avg_posture, 2),
        "total_duration_seconds": total_duration,
        "days_active": unique_days,
        "exercises_completed": [
            {
                "name": name,
                "sessions": data["count"],
                "total_reps": data["reps"],
                "avg_quality": round(data.get("avg_quality", 0), 2)
            }
            for name, data in sorted(exercises_dict.items(), key=lambda x: x[1]["reps"], reverse=True)
        ],
        "latest_session": latest_session_dict,
        "best_exercise": best_exercise[0] if best_exercise else None,
        "weekly_reps": weekly_reps
    }

# ============================================================================
# REHAB SESSION ENDPOINTS
# ============================================================================

@app.post("/rehab-sessions", response_model=RehabSessionResponse)
def create_rehab_session(session: RehabSessionCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Create a new rehab session tracking exercise completion from rehab plan"""
    try:
        # Determine status based on reps and quality
        if session.status == "pending":
            if session.reps_done >= session.target_reps and session.quality_score >= 70:
                status = "completed"
            elif session.reps_done > 0:
                status = "incomplete"
            else:
                status = "pending"
        else:
            status = session.status
        
        db_session = RehabSession(
            user_id=current_user.id,
            exercise_name=session.exercise_name,
            day=session.day,
            target_reps=session.target_reps,
            reps_done=session.reps_done,
            quality_score=session.quality_score,
            status=status,
            notes=session.notes
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        logger.info(f"Rehab session created: user={current_user.id}, exercise={session.exercise_name}, status={status}")
        return db_session
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating rehab session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create rehab session")

@app.put("/rehab-sessions/{session_id}", response_model=RehabSessionResponse)
def update_rehab_session(session_id: int, update: RehabSessionUpdate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Update a rehab session (mark as completed, update reps/quality)"""
    try:
        db_session = db.query(RehabSession).filter(
            RehabSession.id == session_id,
            RehabSession.user_id == current_user.id
        ).first()
        
        if not db_session:
            raise HTTPException(status_code=404, detail="Rehab session not found")
        
        # Update fields
        db_session.reps_done = update.reps_done
        db_session.quality_score = update.quality_score
        db_session.status = update.status
        db_session.notes = update.notes
        
        db.commit()
        db.refresh(db_session)
        logger.info(f"Rehab session updated: id={session_id}, status={update.status}")
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating rehab session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update rehab session")

@app.get("/rehab-sessions", response_model=List[RehabSessionResponse])
def get_rehab_sessions(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get all rehab sessions for current user"""
    sessions = db.query(RehabSession).filter(
        RehabSession.user_id == current_user.id
    ).order_by(RehabSession.date.desc()).all()
    return sessions

@app.get("/rehab-sessions/day/{day}", response_model=List[RehabSessionResponse])
def get_rehab_sessions_by_day(day: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get rehab sessions for a specific day of the plan"""
    sessions = db.query(RehabSession).filter(
        RehabSession.user_id == current_user.id,
        RehabSession.day == day
    ).order_by(RehabSession.date.desc()).all()
    return sessions

@app.get("/rehab-progress", response_model=RehabProgressResponse)
def get_rehab_progress(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get overall rehab compliance and progress metrics"""
    sessions = db.query(RehabSession).filter(
        RehabSession.user_id == current_user.id
    ).all()
    
    total = len(sessions)
    completed = len([s for s in sessions if s.status == "completed"])
    pending = len([s for s in sessions if s.status == "pending"])
    skipped = len([s for s in sessions if s.status == "skipped"])
    incomplete = len([s for s in sessions if s.status == "incomplete"])
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    # Group by day
    by_day = {}
    for session in sessions:
        day = session.day
        if day not in by_day:
            by_day[day] = {"completed": 0, "total": 0, "exercises": []}
        by_day[day]["total"] += 1
        if session.status == "completed":
            by_day[day]["completed"] += 1
        by_day[day]["exercises"].append({
            "name": session.exercise_name,
            "status": session.status,
            "reps": session.reps_done,
            "target": session.target_reps,
            "quality": session.quality_score
        })
    
    return {
        "total_exercises": total,
        "completed_exercises": completed,
        "pending_exercises": pending,
        "skipped_exercises": skipped,
        "completion_rate": round(completion_rate, 2),
        "by_day": by_day
    }

# ============================================================================
# ML CLASSIFICATION ENDPOINTS
# ============================================================================

# Initialize feature extractor
feature_extractor = FeatureExtractor()

def extract_landmarks_from_frame(frame_data_b64: str) -> Optional[Dict]:
    """Extract landmarks from base64-encoded frame"""
    try:
        # Decode frame
        frame_data = base64.b64decode(frame_data_b64)
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return None
        
        # Process with MediaPipe
        temp_engine = ExerciseEngine()
        result = temp_engine.process_frame(frame, selected_exercise=None)
        
        if result["landmarks_detected"]:
            return result.get("skeleton_data")
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error extracting landmarks: {e}")
        return None


@app.post("/api/classify", response_model=ClassifyResponse)
def classify_exercise(request: ClassifyRequest):
    """
    Classify exercise from video frame using trained ML models.
    
    Args:
        frame_data: Base64-encoded video frame
        exercise_name: Optional exercise hint for biomechanics context
        extract_features_only: If true, return features without classification
    
    Returns:
        Classification result with exercise type and confidence
    """
    import time as time_module
    
    try:
        start_time = time_module.time()
        
        # Extract landmarks from frame
        landmarks = extract_landmarks_from_frame(request.frame_data)
        
        if not landmarks:
            return ClassifyResponse(
                success=False,
                error="Could not detect pose landmarks in frame",
                processing_time_ms=(time_module.time() - start_time) * 1000
            )
        
        # Extract features from landmarks
        features = feature_extractor.extract_features(landmarks)
        
        # Return features only if requested
        if request.extract_features_only:
            return ClassifyResponse(
                success=True,
                landmarks=LandmarksData(
                    landmarks=landmarks,
                    confidence=0.8
                ),
                result=ClassificationResult(
                    exercise="Unknown",
                    confidence=0.0,
                    method="FEATURES_ONLY",
                    extracted_features=features.tolist(),
                    processing_time_ms=(time_module.time() - start_time) * 1000
                ),
                processing_time_ms=(time_module.time() - start_time) * 1000
            )
        
        # Prepare biomechanics info if exercise hint provided
        biomechanics_info = None
        if request.exercise_name:
            biomechanics_info = {
                'exercise': request.exercise_name,
                'confidence': 0.7,
                'quality_score': 75,
                'posture_valid': True,
                'reps_count': 0
            }
        
        # Classify using ML models
        classification = ml_service.classify_exercise(
            features=features,
            biomechanics_info=biomechanics_info
        )
        
        result = ClassificationResult(
            exercise=classification['exercise'],
            confidence=classification['confidence'],
            method=classification['method'],
            all_predictions=classification['details'].get('ml_scores'),
            extracted_features=features.tolist() if hasattr(features, 'tolist') else list(features),
            processing_time_ms=(time_module.time() - start_time) * 1000
        )
        
        return ClassifyResponse(
            success=True,
            result=result,
            landmarks=LandmarksData(
                landmarks=landmarks,
                confidence=0.8
            ),
            processing_time_ms=(time_module.time() - start_time) * 1000
        )
        
    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        return ClassifyResponse(
            success=False,
            error=f"Classification failed: {str(e)}",
            processing_time_ms=0
        )


@app.post("/api/classify/batch")
def classify_batch(frames_data: List[ClassifyRequest]):
    """
    Classify multiple frames in batch.
    
    Args:
        frames_data: List of ClassifyRequest objects
    
    Returns:
        List of ClassifyResponse objects
    """
    results = []
    for request in frames_data:
        result = classify_exercise(request)
        results.append(result)
    
    return {
        'success': all(r.success for r in results),
        'results': results,
        'total_frames': len(results),
        'successful_classifications': sum(1 for r in results if r.success)
    }


@app.get("/api/classifier/info")
def get_classifier_info():
    """Get information about loaded ML models"""
    try:
        info = advanced_classifier.get_model_info()
        return {
            'status': 'ready' if info['is_ready'] else 'not_ready',
            'models': info['models_loaded'],
            'num_models': len(info['models_loaded']),
            'confidence_threshold': info['confidence_threshold'],
            'num_features': info['num_features'],
            'num_classes': info['num_classes'],
            'classes': info['classes']
        }
    except Exception as e:
        logger.error(f"Error getting classifier info: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'models': list(advanced_classifier.models.keys()) if hasattr(advanced_classifier, 'models') else [],
            'num_classes': 0,
            'classes': []
        }


@app.put("/api/classifier/threshold")
def update_classifier_threshold(threshold: float):
    """Update confidence threshold for ML fallback logic"""
    if not (0.0 <= threshold <= 1.0):
        raise HTTPException(status_code=400, detail="Threshold must be between 0.0 and 1.0")
    
    try:
        advanced_classifier.set_confidence_threshold(threshold)
        return {
            'success': True,
            'new_threshold': threshold,
            'message': f'Confidence threshold updated to {threshold:.2f}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update threshold: {str(e)}")

# WebSocket endpoint for real-time exercise monitoring
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    # Instantiate per-connection engine
    current_engine = ExerciseEngine()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "frame":
                # Process single frame for selected exercise
                await process_frame(message, user_id, current_engine)
            
            elif message.get("type") == "select_category":
                # Set category for tracking
                category = message.get("category")
                if category in manager.EXERCISE_CATEGORIES:
                    manager.get_user_state(user_id, category)["active"] = True
                    logger.info(f"User {user_id} enabled category: {category}")
            
            elif message.get("type") == "select_exercise":
                # Select single exercise for tracking
                exercise_name = message.get("exercise_name")
                category = message.get("category")
                if category in manager.EXERCISE_CATEGORIES:
                    state = manager.get_user_state(user_id, category)
                    state["current_exercise"] = exercise_name
                    state["started"] = True
                logger.info(f"User {user_id} selected exercise: {exercise_name}")
            
            elif message.get("type") == "reset":
                # Reset single exercise tracking
                category = message.get("category")
                if category in manager.EXERCISE_CATEGORIES:
                    state = manager.get_user_state(user_id, category)
                    state["exercises"] = {}
                    state["started"] = False
                    state["session_reps"] = {}
                
                await manager.send_personal_message({
                    "type": "exercise_reset",
                    "category": category,
                    "message": "Exercise tracking reset"
                }, user_id)
                
    except WebSocketDisconnect:
        # Save exercise sessions before disconnecting
        try:
            for category in manager.EXERCISE_CATEGORIES:
                state = manager.get_user_state(user_id, category)
                if state.get("exercises"):
                    db = next(get_db())
                    for exercise_name, exercise_data in state["exercises"].items():
                        if exercise_data.get("reps", 0) > 0:
                            session = ExerciseSession(
                                user_id=int(user_id),
                                exercise_name=exercise_name,
                                total_reps=exercise_data.get("reps", 0),
                                average_joint_angle=exercise_data.get("last_angle", 0),
                                quality_score=exercise_data.get("quality_score", 0.0),
                                duration_seconds=0,
                                posture_correctness=100.0
                            )
                            db.add(session)
                    db.commit()
                    db.close()
        except Exception as e:
            logger.error(f"Error saving exercise sessions: {e}")
        
        manager.disconnect(user_id)
        current_engine.cleanup()

def analyze_exercise_frame(engine: ExerciseEngine, frame_data_b64: str, user_id: str = None, exercise_name: str = None):
    """
    Process a single frame for a single exercise.
    Integrates voice feedback through event-driven system (NO repeated voice).
    """
    try:
        # Decode frame
        frame_data = base64.b64decode(frame_data_b64)
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return None
        
        # Process frame for the specified exercise
        result = engine.process_frame(frame, selected_exercise=exercise_name)
        
        if not result.get("landmarks_detected"):
            return {
                "type": "exercise_feedback",
                "exercise": exercise_name,
                "landmarks_detected": False,
                "message": "No pose detected. Please face the camera clearly."
            }
        
        feedback = {
            "type": "exercise_feedback",
            "exercise": exercise_name,
            "reps": result.get("reps", 0),
            "angle": result.get("angle", 0),
            "joint_tracked": result.get("joint_tracked", ""),
            "quality_score": result.get("quality_score", 0),
            "confidence": result.get("confidence", 0),
            "posture_message": result.get("posture_message", "Ready"),
            "landmarks_detected": True,
            "skeleton_image": result.get("skeleton_image"),
            "voice_event": None  # May be populated by voice system
        }
        
        # Process voice events (NEW EVENT-DRIVEN SYSTEM)
        # Only trigger voice on meaningful events, NOT on every frame
        if exercise_voice_integration and user_id:
            try:
                voice_result = exercise_voice_integration.process_frame(
                    user_id=user_id,
                    exercise_name=exercise_name,
                    current_angle=result.get("angle", 0),
                    quality_score=result.get("quality_score", 0),
                    confidence=result.get("confidence", 0),
                    posture_correct=(result.get("posture_message", "Ready") == "Ready")
                )
                
                # Include voice event in feedback if triggered
                if voice_result.get("event_triggered"):
                    feedback["voice_event"] = {
                        "event_type": voice_result["event_type"],
                        "message": voice_result["message"],
                        "priority": voice_result["priority"].value if voice_result["priority"] else None,
                    }
                    logger.info(f"Voice event for user {user_id}: {voice_result['event_type']} - {voice_result['message']}")
            except Exception as e:
                logger.debug(f"Voice event processing error: {e}")
        
        logger.info(f"Exercise {exercise_name}: {result.get('reps', 0)} reps, "
                  f"angle={result.get('angle', 0):.1f}°, "
                  f"quality={result.get('quality_score', 0):.0f}")
        
        return feedback
        
    except Exception as e:
        logger.error(f"Error in analyze_exercise_frame: {e}")
        return None

async def process_frame(message: dict, user_id: str, engine: ExerciseEngine):
    """Process a single frame for exercise monitoring"""
    try:
        exercise_name = message.get("exercise_name")
        
        # Offload to thread
        feedback = await asyncio.to_thread(
            analyze_exercise_frame,
            engine,
            message["frame_data"],
            user_id,
            exercise_name
        )
        
        if not feedback:
            return
        
        # Send feedback to user
        await manager.send_personal_message(feedback, user_id)
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "Error processing frame"
        }, user_id)

# ================================================================
#   AI CHATBOT ENDPOINTS
# ================================================================

# POST /chat  – primary AI chatbot endpoint (per spec)
@app.post("/chat", response_model=AIChatResponse)
async def chat_endpoint(request: AIChatRequest):
    """AI Physiotherapy Assistant — main chat endpoint.
    Accepts user message + optional exercise context and returns AI guidance.
    No authentication required so the floating widget works for all users."""
    try:
        rep_count = int(request.rep_count) if request.rep_count else None
        quality_score = float(request.quality_score) if request.quality_score else None
        joint_angle = float(request.joint_angle) if request.joint_angle else None

        response_text = ai_chatbot.get_response(
            user_message=request.user_message,
            exercise=request.exercise,
            rep_count=rep_count,
            quality_score=quality_score,
            joint_angle=joint_angle,
            posture_feedback=request.posture_feedback,
        )
        return AIChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return AIChatResponse(
            response="I'm having trouble responding right now. Please try again."
        )


# POST /chatbot  – legacy endpoint (for backward compatibility with existing UI)
@app.post("/chatbot")
async def chat_with_bot(message: ChatMessage):
    """Chat with physiotherapy assistant (legacy endpoint).
    Now uses the full AI engine instead of simple_chatbot."""
    try:
        response_text = ai_chatbot.get_response(
            user_message=message.message,
            exercise=message.exercise_context,
            rep_count=message.rep_count,
            quality_score=message.quality_score,
            joint_angle=message.joint_angle,
            posture_feedback=message.posture_feedback,
        )
        return ChatResponse(response=response_text, is_voice=False)
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return ChatResponse(
            response="I'm having trouble responding right now. Please try again.",
            is_voice=False,
        )


@app.get("/chatbot/exercises")
async def get_exercise_list():
    """Get list of all available exercises from the knowledge base."""
    try:
        from chatbot.knowledge_base import knowledge_base
        exercises = knowledge_base.get_exercise_names()
        return {"exercises": exercises}
    except Exception as e:
        logger.error(f"Error getting exercise list: {e}")
        return {"exercises": []}


@app.get("/chatbot/exercises/{exercise_name}")
async def get_exercise_detail(exercise_name: str):
    """Get detailed information about a specific exercise."""
    try:
        from chatbot.knowledge_base import knowledge_base
        data = knowledge_base.get_exercise(exercise_name)
        if data:
            return {"found": True, "exercise": exercise_name, "data": data}
        return {"found": False, "exercise": exercise_name, "data": None}
    except Exception as e:
        logger.error(f"Error getting exercise detail: {e}")
        return {"found": False, "error": str(e)}


@app.get("/chatbot/safety-tip")
async def get_safety_tip():
    """Get a random safety tip from the knowledge base."""
    try:
        from chatbot.knowledge_base import knowledge_base
        return {"tip": knowledge_base.get_random_safety_tip()}
    except Exception as e:
        logger.error(f"Error getting safety tip: {e}")
        return {"tip": "Always exercise safely and stop if you feel pain."}


@app.get("/chatbot/motivation")
async def get_motivation():
    """Get a random motivational message."""
    try:
        from chatbot.knowledge_base import knowledge_base
        return {"message": knowledge_base.get_random_motivation()}
    except Exception as e:
        logger.error(f"Error getting motivation: {e}")
        return {"message": "Keep up the great work!"}


@app.post("/chatbot/coaching")
async def get_session_coaching(request: AIChatRequest):
    """Get real-time coaching feedback during an exercise session."""
    try:
        rep_count = int(request.rep_count) if request.rep_count else 0
        quality_score = float(request.quality_score) if request.quality_score else 0.0
        joint_angle = float(request.joint_angle) if request.joint_angle else 0.0

        message = ai_chatbot.get_session_coaching(
            exercise=request.exercise or "exercise",
            rep_count=rep_count,
            quality_score=quality_score,
            joint_angle=joint_angle,
            posture_feedback=request.posture_feedback or "",
        )
        return {"coaching": message}
    except Exception as e:
        logger.error(f"Coaching error: {e}")
        return {"coaching": "Keep going, you're doing well!"}


# ================================================================
#   REHABILITATION PLAN GENERATOR
# ================================================================

# Comprehensive exercise library keyed by (injury_location, goal)
REHAB_EXERCISE_LIBRARY = {
    # ─── SHOULDER ───
    ("Shoulder", "Pain Reduction"): [
        {"name": "Pendulum Swing", "description": "Lean forward, let arm hang and swing in small circles", "sets": 3, "reps": 15, "hold_seconds": None, "rest_seconds": 30, "notes": "Keep movements gentle and pain-free"},
        {"name": "Shoulder Shrugs", "description": "Raise shoulders toward ears, hold briefly, then release", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 30, "notes": "Avoid jerky movements"},
        {"name": "Cross-Body Stretch", "description": "Pull one arm across chest with the opposite hand", "sets": 3, "reps": 10, "hold_seconds": 15, "rest_seconds": 20, "notes": "Stretch gently, no sharp pain"},
        {"name": "Ice/Heat Application", "description": "Apply ice for 15 min after exercises to reduce inflammation", "sets": 1, "reps": 1, "hold_seconds": 900, "rest_seconds": 0, "notes": "Use a towel between ice and skin"},
    ],
    ("Shoulder", "Increase ROM"): [
        {"name": "Shoulder Flexion", "description": "Raise arm forward and overhead as far as comfortable", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Use wall slide if needed for support"},
        {"name": "Shoulder Abduction", "description": "Raise arm out to the side up to shoulder height or above", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Keep thumb pointing upward"},
        {"name": "Shoulder External Rotation", "description": "Elbow at side, rotate forearm outward", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 30, "notes": "Use a towel roll under the arm"},
        {"name": "Wall Climb", "description": "Walk fingers up a wall to increase overhead reach", "sets": 3, "reps": 10, "hold_seconds": 10, "rest_seconds": 30, "notes": "Mark progress height each session"},
    ],
    ("Shoulder", "Strength Building"): [
        {"name": "Shoulder Flexion with Band", "description": "Raise arm forward against resistance band tension", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 45, "notes": "Slow 3-second up, 3-second down"},
        {"name": "Shoulder Abduction with Band", "description": "Raise arm sideways against resistance band tension", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 45, "notes": "Don't shrug the shoulder"},
        {"name": "Shoulder Extension", "description": "Pull arm backward against band resistance", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 45, "notes": "Keep elbow straight"},
        {"name": "Isometric Shoulder Press", "description": "Push upward against a doorframe and hold", "sets": 3, "reps": 8, "hold_seconds": 10, "rest_seconds": 45, "notes": "Build to maximum comfortable effort"},
    ],
    ("Shoulder", "Daily Mobility"): [
        {"name": "Arm Circles", "description": "Small to large circles with arms extended", "sets": 2, "reps": 15, "hold_seconds": None, "rest_seconds": 20, "notes": "Both clockwise and counter-clockwise"},
        {"name": "Doorway Stretch", "description": "Place arms on doorframe and lean forward to stretch chest/shoulders", "sets": 3, "reps": 5, "hold_seconds": 20, "rest_seconds": 20, "notes": "Feel stretch across the chest"},
        {"name": "Behind-Back Reach", "description": "Reach one arm up and the other behind the back, try to touch fingers", "sets": 2, "reps": 8, "hold_seconds": 10, "rest_seconds": 20, "notes": "Use a towel to bridge the gap"},
        {"name": "Shoulder Rolls", "description": "Roll shoulders forward and backward in smooth circles", "sets": 2, "reps": 15, "hold_seconds": None, "rest_seconds": 15, "notes": "Great for daily desk breaks"},
    ],

    # ─── KNEE ───
    ("Knee", "Pain Reduction"): [
        {"name": "Quad Sets", "description": "Tighten thigh muscle while pressing knee down into surface", "sets": 3, "reps": 15, "hold_seconds": 5, "rest_seconds": 20, "notes": "Can be done lying down"},
        {"name": "Straight Leg Raise", "description": "Lying down, lift leg 12 inches keeping knee straight", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 30, "notes": "Tighten quad before lifting"},
        {"name": "Heel Slides", "description": "Slide heel toward buttocks bending the knee gently", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 30, "notes": "Use a towel under heel for smooth sliding"},
        {"name": "Ankle Pumps", "description": "Move foot up and down to promote blood circulation", "sets": 3, "reps": 20, "hold_seconds": None, "rest_seconds": 15, "notes": "Helps reduce swelling"},
    ],
    ("Knee", "Increase ROM"): [
        {"name": "Knee Flexion Stretch", "description": "Sit and gently bend knee as far as comfortable", "sets": 3, "reps": 10, "hold_seconds": 15, "rest_seconds": 30, "notes": "Use hands to assist if needed"},
        {"name": "Knee Extension Stretch", "description": "Sit with leg on a stool, press knee gently toward straight", "sets": 3, "reps": 10, "hold_seconds": 15, "rest_seconds": 30, "notes": "Place a small towel under ankle"},
        {"name": "Prone Knee Flexion", "description": "Lie face down, bend knee bringing heel toward buttocks", "sets": 3, "reps": 10, "hold_seconds": 10, "rest_seconds": 30, "notes": "Use a strap to assist if needed"},
        {"name": "Stationary Bike", "description": "Gentle cycling with low resistance to improve ROM", "sets": 1, "reps": 1, "hold_seconds": 600, "rest_seconds": 0, "notes": "10 minutes, raise seat if knee is stiff"},
    ],
    ("Knee", "Strength Building"): [
        {"name": "Wall Sit", "description": "Lean against wall, slide down to 45-degree knee bend and hold", "sets": 3, "reps": 5, "hold_seconds": 20, "rest_seconds": 45, "notes": "Keep knees behind toes"},
        {"name": "Step-Ups", "description": "Step onto a low platform leading with the affected leg", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 45, "notes": "Use 4-6 inch step to start"},
        {"name": "Mini Squats", "description": "Partial squats to 45 degrees with feet shoulder-width apart", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 45, "notes": "Hold onto a chair for balance"},
        {"name": "Hamstring Curl", "description": "Standing on one leg, curl the other heel toward buttocks", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 45, "notes": "Use ankle weight for progression"},
    ],
    ("Knee", "Daily Mobility"): [
        {"name": "Seated Knee Extension", "description": "Sitting in a chair, straighten one knee and hold", "sets": 2, "reps": 12, "hold_seconds": 5, "rest_seconds": 20, "notes": "Perfect for office breaks"},
        {"name": "Standing Quad Stretch", "description": "Pull heel to buttocks while standing, hold balance", "sets": 2, "reps": 6, "hold_seconds": 20, "rest_seconds": 20, "notes": "Hold a wall for support"},
        {"name": "Calf Raises", "description": "Rise on toes, then slowly lower heels below step level", "sets": 2, "reps": 15, "hold_seconds": None, "rest_seconds": 20, "notes": "Supports knee joint stability"},
        {"name": "Walking Program", "description": "Walk on flat surface at comfortable pace", "sets": 1, "reps": 1, "hold_seconds": 900, "rest_seconds": 0, "notes": "15 min walk, increase gradually"},
    ],

    # ─── ELBOW ───
    ("Elbow", "Pain Reduction"): [
        {"name": "Wrist Extensor Stretch", "description": "Extend arm, pull fingers downward with other hand", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "Common for tennis elbow relief"},
        {"name": "Wrist Flexor Stretch", "description": "Extend arm, pull fingers upward with other hand", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "Common for golfer's elbow relief"},
        {"name": "Forearm Pronation/Supination", "description": "Hold a pen, slowly rotate forearm palm-up to palm-down", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 20, "notes": "Keep elbow at side"},
        {"name": "Elbow Flexion/Extension", "description": "Gently bend and straighten the elbow through full range", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 20, "notes": "No resistance — mobility only"},
    ],
    ("Elbow", "Increase ROM"): [
        {"name": "Active Elbow Flexion", "description": "Bend elbow fully bringing hand to shoulder", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Assist with other hand if stiff"},
        {"name": "Elbow Extension Stretch", "description": "Straighten arm fully and gently press with other hand", "sets": 3, "reps": 10, "hold_seconds": 15, "rest_seconds": 30, "notes": "Do not force past comfort"},
        {"name": "Towel Wringing", "description": "Wring a towel with both hands — twisting forearm", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 30, "notes": "Alternate wring direction"},
        {"name": "Forearm Roll with Dowel", "description": "Roll a dowel/stick between hands working forearm rotation", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 30, "notes": "Light, controlled movements"},
    ],
    ("Elbow", "Strength Building"): [
        {"name": "Wrist Curls", "description": "Rest forearm on table, curl light weight upward", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 45, "notes": "Start with 1-2 lb weight"},
        {"name": "Reverse Wrist Curls", "description": "Rest forearm on table palm-down, lift weight upward", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 45, "notes": "Strengthens extensors"},
        {"name": "Elbow Flexion with Band", "description": "Bicep curl with resistance band anchored underfoot", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 45, "notes": "Control both up and down phases"},
        {"name": "Grip Strengthening", "description": "Squeeze a stress ball or grip trainer and hold", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Builds forearm and hand strength"},
    ],
    ("Elbow", "Daily Mobility"): [
        {"name": "Elbow Circles", "description": "Place hand on shoulder and draw circles with elbow", "sets": 2, "reps": 12, "hold_seconds": None, "rest_seconds": 15, "notes": "Both clockwise and counter-clockwise"},
        {"name": "Prayer Stretch", "description": "Press palms together in front, lower until stretch is felt", "sets": 2, "reps": 8, "hold_seconds": 15, "rest_seconds": 15, "notes": "Stretches wrist and forearm"},
        {"name": "Finger Spread", "description": "Open and close fingers wide against a rubber band", "sets": 2, "reps": 15, "hold_seconds": None, "rest_seconds": 15, "notes": "Improves dexterity and grip"},
        {"name": "Desk Forearm Stretch", "description": "Place palm flat on desk fingers toward you, lean gently", "sets": 2, "reps": 6, "hold_seconds": 15, "rest_seconds": 15, "notes": "Great for computer users"},
    ],

    # ─── HIP ───
    ("Hip", "Pain Reduction"): [
        {"name": "Supine Hip Flexor Stretch", "description": "Lying on back, hug one knee to chest gently", "sets": 3, "reps": 8, "hold_seconds": 20, "rest_seconds": 30, "notes": "Keep lower back flat"},
        {"name": "Piriformis Stretch", "description": "Cross ankle over opposite knee, pull thigh toward chest", "sets": 3, "reps": 8, "hold_seconds": 20, "rest_seconds": 30, "notes": "Common for sciatica-like pain"},
        {"name": "Gentle Hip Circles", "description": "Stand on one leg, draw small circles with the other knee", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 20, "notes": "Hold a wall for balance"},
        {"name": "Hip Adductor Stretch", "description": "Sit with soles of feet together, gently press knees down", "sets": 3, "reps": 6, "hold_seconds": 20, "rest_seconds": 20, "notes": "Butterfly position — gentle pressure only"},
    ],
    ("Hip", "Increase ROM"): [
        {"name": "Hip Flexion", "description": "Standing, lift knee toward chest as high as comfortable", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Keep spine neutral"},
        {"name": "Hip Abduction", "description": "Lying on side, lift top leg upward keeping it straight", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Don't rotate the hip"},
        {"name": "Hip Internal Rotation", "description": "Seated, rotate shin outward keeping knee in place", "sets": 3, "reps": 10, "hold_seconds": 10, "rest_seconds": 30, "notes": "Gentle controlled rotation"},
        {"name": "Hip External Rotation", "description": "Seated, rotate shin inward keeping knee in place", "sets": 3, "reps": 10, "hold_seconds": 10, "rest_seconds": 30, "notes": "Keep back straight"},
    ],
    ("Hip", "Strength Building"): [
        {"name": "Clamshells", "description": "Lying on side, knees bent, open top knee like a clamshell", "sets": 3, "reps": 15, "hold_seconds": None, "rest_seconds": 45, "notes": "Add a resistance band for progression"},
        {"name": "Glute Bridge", "description": "Lying on back, push hips upward squeezing glutes", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 45, "notes": "Don't arch lower back excessively"},
        {"name": "Side-Lying Leg Lift", "description": "Lying on side, raise top leg and hold", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 45, "notes": "Keep toes pointed forward"},
        {"name": "Standing Hip Extension", "description": "Stand and extend leg backward against band resistance", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 45, "notes": "Don't lean forward"},
    ],
    ("Hip", "Daily Mobility"): [
        {"name": "Standing Hip Circles", "description": "Large circles with the hip, hands on waist", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Both directions"},
        {"name": "Figure-4 Stretch", "description": "Cross ankle over knee while seated, lean forward", "sets": 2, "reps": 6, "hold_seconds": 20, "rest_seconds": 20, "notes": "Great for desk workers"},
        {"name": "Hip Flexor Lunge Stretch", "description": "Kneel on one knee, push hips forward gently", "sets": 2, "reps": 6, "hold_seconds": 20, "rest_seconds": 20, "notes": "Counteracts sitting posture"},
        {"name": "Leg Swings", "description": "Hold a wall, swing one leg forward and backward", "sets": 2, "reps": 12, "hold_seconds": None, "rest_seconds": 15, "notes": "Dynamic warm-up exercise"},
    ],

    # ─── NECK ───
    ("Neck", "Pain Reduction"): [
        {"name": "Neck Flexion Stretch", "description": "Gently tilt chin toward chest, hold", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "No bouncing — slow and steady"},
        {"name": "Neck Extension Stretch", "description": "Gently tilt head backward and look at ceiling", "sets": 3, "reps": 8, "hold_seconds": 10, "rest_seconds": 20, "notes": "Stop if dizzy"},
        {"name": "Upper Trap Stretch", "description": "Tilt ear to shoulder, gently press with hand for stretch", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "Keep opposite shoulder down"},
        {"name": "Chin Tucks", "description": "Pull chin straight back creating a 'double chin', hold", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 15, "notes": "Corrects forward head posture"},
    ],
    ("Neck", "Increase ROM"): [
        {"name": "Neck Rotation", "description": "Slowly turn head to look over each shoulder", "sets": 3, "reps": 10, "hold_seconds": 5, "rest_seconds": 20, "notes": "Move within pain-free range"},
        {"name": "Neck Lateral Flexion", "description": "Tilt ear toward shoulder on each side", "sets": 3, "reps": 10, "hold_seconds": 5, "rest_seconds": 20, "notes": "Keep shoulders level"},
        {"name": "Neck Flexion/Extension", "description": "Nod head forward then tilt backward through full range", "sets": 3, "reps": 10, "hold_seconds": 3, "rest_seconds": 20, "notes": "Smooth, continuous movement"},
        {"name": "Neck Circles", "description": "Roll head in a gentle half-circle (ear to ear via chin)", "sets": 2, "reps": 8, "hold_seconds": None, "rest_seconds": 20, "notes": "Avoid full circles backward"},
    ],
    ("Neck", "Strength Building"): [
        {"name": "Isometric Neck Flexion", "description": "Push forehead into palm, resist with the hand — no movement", "sets": 3, "reps": 8, "hold_seconds": 8, "rest_seconds": 30, "notes": "Build effort gradually"},
        {"name": "Isometric Neck Extension", "description": "Push back of head into clasped hands, resist — no movement", "sets": 3, "reps": 8, "hold_seconds": 8, "rest_seconds": 30, "notes": "Keep neck neutral"},
        {"name": "Isometric Lateral Resist", "description": "Push side of head into palm, resist — no movement", "sets": 3, "reps": 8, "hold_seconds": 8, "rest_seconds": 30, "notes": "Both sides"},
        {"name": "Scapular Retraction", "description": "Squeeze shoulder blades together and hold", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 30, "notes": "Supports neck posture"},
    ],
    ("Neck", "Daily Mobility"): [
        {"name": "Clock Neck Stretches", "description": "Tilt head to 12, 3, 6, and 9 o'clock positions", "sets": 2, "reps": 5, "hold_seconds": 5, "rest_seconds": 15, "notes": "Great for hourly desk breaks"},
        {"name": "Seated Chin Tucks", "description": "Pull chin back while seated at desk", "sets": 2, "reps": 10, "hold_seconds": 5, "rest_seconds": 10, "notes": "Can do anytime while working"},
        {"name": "Shoulder Blade Squeeze", "description": "Pull shoulders back and squeeze blade together", "sets": 2, "reps": 10, "hold_seconds": 5, "rest_seconds": 15, "notes": "Counteracts forward posture"},
        {"name": "Head Glides", "description": "Slide head forward and backward keeping chin level", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Improves cervical posture awareness"},
    ],

    # ─── WRIST ───
    ("Wrist", "Pain Reduction"): [
        {"name": "Wrist Flexor Stretch", "description": "Extend arm, pull fingers back with other hand", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "Arm stays straight"},
        {"name": "Wrist Extensor Stretch", "description": "Extend arm, press fingers down with other hand", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "Relieves wrist tension"},
        {"name": "Nerve Glides", "description": "Extend arm and fingers, flex and extend wrist slowly", "sets": 3, "reps": 10, "hold_seconds": None, "rest_seconds": 20, "notes": "Helps with carpal tunnel symptoms"},
        {"name": "Wrist Circles", "description": "Rotate wrist gently in both directions", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Keep movements controlled"},
    ],
    ("Wrist", "Increase ROM"): [
        {"name": "Wrist Flexion", "description": "Bend wrist forward as far as comfortable", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 20, "notes": "Support forearm on a table"},
        {"name": "Wrist Extension", "description": "Bend wrist backward as far as comfortable", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 20, "notes": "Keep elbow stable"},
        {"name": "Radial/Ulnar Deviation", "description": "Move wrist side to side (toward thumb then pinky)", "sets": 3, "reps": 10, "hold_seconds": 5, "rest_seconds": 20, "notes": "Forearm stays still"},
        {"name": "Forearm Rotation", "description": "Turn palm up and then palm down with arm at side", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 20, "notes": "Full rotation range"},
    ],
    ("Wrist", "Strength Building"): [
        {"name": "Wrist Curls", "description": "Hold a light weight, curl wrist upward", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 30, "notes": "Start with 1 lb"},
        {"name": "Reverse Wrist Curls", "description": "Hold weight palm-down, lift wrist upward", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 30, "notes": "Strengthens extensors"},
        {"name": "Ball Squeeze", "description": "Squeeze a stress ball firmly, hold, then release", "sets": 3, "reps": 15, "hold_seconds": 5, "rest_seconds": 30, "notes": "Builds grip strength"},
        {"name": "Rubber Band Extensions", "description": "Place rubber band around fingers, spread them apart", "sets": 3, "reps": 15, "hold_seconds": 3, "rest_seconds": 30, "notes": "Works finger extensors"},
    ],
    ("Wrist", "Daily Mobility"): [
        {"name": "Prayer Stretch", "description": "Press palms together, lower until stretch is felt", "sets": 2, "reps": 6, "hold_seconds": 15, "rest_seconds": 15, "notes": "Great desk break stretch"},
        {"name": "Reverse Prayer", "description": "Press back of hands together, lift until stretch", "sets": 2, "reps": 6, "hold_seconds": 15, "rest_seconds": 15, "notes": "Stretches wrist extensors"},
        {"name": "Finger Taps", "description": "Tap each fingertip to thumb in sequence rapidly", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 10, "notes": "Improves coordination"},
        {"name": "Wrist Rolls", "description": "Make fists and roll wrists in circles", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 10, "notes": "Do every hour at desk"},
    ],

    # ─── ANKLE ───
    ("Ankle", "Pain Reduction"): [
        {"name": "Ankle Alphabet", "description": "Trace the alphabet with your big toe in the air", "sets": 2, "reps": 2, "hold_seconds": None, "rest_seconds": 30, "notes": "Gentle full-range motion"},
        {"name": "Ankle Pumps", "description": "Point toes down then pull toes up repeatedly", "sets": 3, "reps": 20, "hold_seconds": None, "rest_seconds": 20, "notes": "Promotes circulation and reduces swelling"},
        {"name": "Ice Elevation", "description": "Elevate foot and apply ice pack for 15 minutes", "sets": 1, "reps": 1, "hold_seconds": 900, "rest_seconds": 0, "notes": "Essential for acute injury"},
        {"name": "Towel Toe Curls", "description": "Scrunch a towel with your toes on the floor", "sets": 3, "reps": 12, "hold_seconds": 3, "rest_seconds": 20, "notes": "Activates foot arch muscles"},
    ],
    ("Ankle", "Increase ROM"): [
        {"name": "Ankle Dorsiflexion Stretch", "description": "Stand facing wall, lean forward keeping heel on ground", "sets": 3, "reps": 8, "hold_seconds": 20, "rest_seconds": 30, "notes": "Stretches calf and Achilles"},
        {"name": "Ankle Plantarflexion", "description": "Point toes as far down as possible", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 20, "notes": "Use a strap to assist"},
        {"name": "Ankle Inversion/Eversion", "description": "Turn sole of foot inward then outward", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 20, "notes": "Keep knee still"},
        {"name": "Calf Stretch on Step", "description": "Drop heel off a step edge and hold stretch", "sets": 3, "reps": 6, "hold_seconds": 20, "rest_seconds": 30, "notes": "Hold railing for balance"},
    ],
    ("Ankle", "Strength Building"): [
        {"name": "Calf Raises", "description": "Rise up on toes, then slowly lower down", "sets": 3, "reps": 15, "hold_seconds": None, "rest_seconds": 45, "notes": "Progress to single leg"},
        {"name": "Ankle Band Exercises", "description": "Push foot against resistance band in all four directions", "sets": 3, "reps": 12, "hold_seconds": None, "rest_seconds": 30, "notes": "Dorsiflexion, plantarflexion, inversion, eversion"},
        {"name": "Single-Leg Balance", "description": "Stand on one foot and hold balance", "sets": 3, "reps": 4, "hold_seconds": 30, "rest_seconds": 30, "notes": "Close eyes for progression"},
        {"name": "Heel Walking", "description": "Walk on heels with toes lifted for 30 seconds", "sets": 3, "reps": 3, "hold_seconds": 30, "rest_seconds": 30, "notes": "Strengthens tibialis anterior"},
    ],
    ("Ankle", "Daily Mobility"): [
        {"name": "Ankle Circles", "description": "Rotate ankle in circles while seated", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 10, "notes": "Both directions each foot"},
        {"name": "Toe Raises", "description": "While seated, lift toes off the ground keeping heels down", "sets": 2, "reps": 15, "hold_seconds": None, "rest_seconds": 15, "notes": "Can do under desk"},
        {"name": "Marble Pickup", "description": "Pick up marbles with toes and place in a cup", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Improves toe dexterity"},
        {"name": "Standing Calf Stretch", "description": "Lean against wall in lunge position, stretch back calf", "sets": 2, "reps": 6, "hold_seconds": 20, "rest_seconds": 15, "notes": "Keep back heel on floor"},
    ],

    # ─── BACK ───
    ("Back", "Pain Reduction"): [
        {"name": "Cat-Cow Stretch", "description": "On all fours, alternate arching and rounding the back", "sets": 3, "reps": 10, "hold_seconds": 5, "rest_seconds": 20, "notes": "Slow, rhythmic movements"},
        {"name": "Child's Pose", "description": "Kneel and reach arms forward, sitting hips back to heels", "sets": 3, "reps": 5, "hold_seconds": 20, "rest_seconds": 20, "notes": "Relaxes the lower back"},
        {"name": "Pelvic Tilts", "description": "Lying on back, flatten lower back to floor by tilting pelvis", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 20, "notes": "Gently activates core"},
        {"name": "Knee-to-Chest Stretch", "description": "Pull one knee to chest while lying on back", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 20, "notes": "Alternate legs"},
    ],
    ("Back", "Increase ROM"): [
        {"name": "Trunk Rotation Stretch", "description": "Seated, rotate torso to one side, hold chair for leverage", "sets": 3, "reps": 8, "hold_seconds": 15, "rest_seconds": 30, "notes": "Both sides"},
        {"name": "Back Extension", "description": "Lying face down, press up on hands arching the back", "sets": 3, "reps": 10, "hold_seconds": 5, "rest_seconds": 30, "notes": "McKenzie extension — stop if pain radiates"},
        {"name": "Standing Side Bend", "description": "Stand with arm overhead, lean sideways", "sets": 3, "reps": 10, "hold_seconds": 10, "rest_seconds": 20, "notes": "Both sides equally"},
        {"name": "Thread the Needle", "description": "On all fours, reach one arm under body rotating spine", "sets": 3, "reps": 8, "hold_seconds": 10, "rest_seconds": 30, "notes": "Excellent thoracic mobility"},
    ],
    ("Back", "Strength Building"): [
        {"name": "Bird Dog", "description": "On all fours, extend opposite arm and leg simultaneously", "sets": 3, "reps": 10, "hold_seconds": 5, "rest_seconds": 45, "notes": "Keep core tight, hips level"},
        {"name": "Dead Bug", "description": "Lying on back, extend opposite arm and leg while core braces", "sets": 3, "reps": 10, "hold_seconds": 3, "rest_seconds": 45, "notes": "Press lower back into floor"},
        {"name": "Glute Bridge", "description": "Push hips upward while lying on back, squeeze glutes at top", "sets": 3, "reps": 12, "hold_seconds": 5, "rest_seconds": 45, "notes": "Supports lower back via glutes"},
        {"name": "Plank Hold", "description": "Hold forearm plank position with body in straight line", "sets": 3, "reps": 3, "hold_seconds": 20, "rest_seconds": 45, "notes": "Build up duration gradually"},
    ],
    ("Back", "Daily Mobility"): [
        {"name": "Seated Spinal Twist", "description": "Sit in chair, rotate torso to each side", "sets": 2, "reps": 8, "hold_seconds": 10, "rest_seconds": 15, "notes": "Great desk break exercise"},
        {"name": "Standing Cat-Cow", "description": "Hands on knees, round and arch the back standing", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Office-friendly version"},
        {"name": "Hip Hinge", "description": "Push hips back while keeping flat back, return to stand", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Teaches safe bending mechanics"},
        {"name": "Wall Angel", "description": "Stand with back to wall, slide arms up and down like snow angel", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 15, "notes": "Improves thoracic posture"},
    ],
}

GOAL_DESCRIPTIONS = {
    "Pain Reduction": "Gentle exercises focused on relieving pain and reducing inflammation",
    "Increase ROM": "Stretching and mobility exercises to restore full range of motion",
    "Strength Building": "Progressive resistance exercises to rebuild muscle strength",
    "Daily Mobility": "Functional exercises to improve everyday movement and independence",
}

INJURY_ICONS = {
    "Shoulder": "fa-hand-rock",
    "Knee": "fa-shoe-prints",
    "Elbow": "fa-hand-point-right",
    "Hip": "fa-person-walking",
    "Neck": "fa-head-side-virus",
    "Wrist": "fa-hand-paper",
    "Ankle": "fa-socks",
    "Back": "fa-person",
}


@app.post("/rehab-plan", response_model=RehabPlanResponse)
async def generate_rehab_plan(request: RehabPlanRequest):
    """Generate a personalized rehabilitation plan based on injury location and goals"""
    location = request.injury_location.strip().title()
    goals = [g.strip() for g in request.rehab_goals]
    difficulty = request.difficulty or "Beginner"

    valid_locations = ["Shoulder", "Knee", "Elbow", "Hip", "Neck", "Wrist", "Ankle", "Back"]
    valid_goals = ["Pain Reduction", "Increase ROM", "Strength Building", "Daily Mobility"]

    if location not in valid_locations:
        raise HTTPException(status_code=400, detail=f"Invalid injury location '{location}'. Choose from: {', '.join(valid_locations)}")

    for g in goals:
        if g not in valid_goals:
            raise HTTPException(status_code=400, detail=f"Invalid goal '{g}'. Choose from: {', '.join(valid_goals)}")

    if not goals:
        raise HTTPException(status_code=400, detail="At least one rehabilitation goal is required")

    # Build a multi-day plan
    days = []
    day_number = 1

    # Difficulty multipliers
    diff_mult = {"Beginner": 1.0, "Intermediate": 1.3, "Advanced": 1.6}.get(difficulty, 1.0)

    for goal in goals:
        key = (location, goal)
        exercises_data = REHAB_EXERCISE_LIBRARY.get(key, [])

        if not exercises_data:
            # Fallback: use generic exercises
            exercises_data = [
                {"name": f"{location} Gentle Movement", "description": f"Gentle movement exercise for {location.lower()}", "sets": 2, "reps": 10, "hold_seconds": None, "rest_seconds": 30, "notes": "Move within pain-free range"},
                {"name": f"{location} Stretch", "description": f"Stretching exercise for {location.lower()} area", "sets": 2, "reps": 8, "hold_seconds": 15, "rest_seconds": 30, "notes": "Hold stretch gently"},
            ]

        # Split exercises across 2 days per goal for variety
        mid = len(exercises_data) // 2 or 1
        day_groups = [exercises_data[:mid], exercises_data[mid:]]

        for di, group in enumerate(day_groups):
            rehab_exercises = []
            for ex in group:
                adj_sets = max(1, int(ex["sets"] * diff_mult))
                adj_reps = max(1, int(ex["reps"] * diff_mult))
                rehab_exercises.append(RehabExercise(
                    name=ex["name"],
                    description=ex["description"],
                    sets=adj_sets,
                    reps=adj_reps,
                    hold_seconds=ex.get("hold_seconds"),
                    rest_seconds=ex.get("rest_seconds", 30),
                    notes=ex.get("notes"),
                ))
            days.append(RehabDayPlan(
                day=day_number,
                title=f"Day {day_number}: {goal} — Session {di + 1}",
                focus=goal,
                exercises=rehab_exercises,
                daily_goal=GOAL_DESCRIPTIONS.get(goal, "Follow the exercises below with proper form"),
            ))
            day_number += 1

    duration_weeks = max(1, (len(days) + 6) // 7)  # round up to weeks
    plan_name = f"{location} Rehabilitation — {', '.join(goals)}"
    overview = (
        f"This personalized {difficulty.lower()} level rehabilitation plan targets your "
        f"{location.lower()} injury with a focus on {', '.join(g.lower() for g in goals)}. "
        f"Follow the {len(days)}-day program, completing each day's exercises in order. "
        f"Rest at least one day per week. Listen to your body and stop if you feel sharp pain."
    )

    return RehabPlanResponse(
        injury_location=location,
        rehab_goals=goals,
        difficulty=difficulty,
        duration_weeks=duration_weeks,
        plan_name=plan_name,
        overview=overview,
        days=days,
    )


@app.get("/rehab-plan/options")
async def get_rehab_plan_options():
    """Return available injury locations and rehabilitation goals"""
    return {
        "injury_locations": [
            {"id": "Shoulder", "label": "Shoulder", "icon": "fa-hand-rock", "description": "Rotator cuff, frozen shoulder, impingement"},
            {"id": "Knee", "label": "Knee", "icon": "fa-shoe-prints", "description": "ACL, meniscus, patella, arthritis"},
            {"id": "Elbow", "label": "Elbow", "icon": "fa-hand-point-right", "description": "Tennis elbow, golfer's elbow, strain"},
            {"id": "Hip", "label": "Hip", "icon": "fa-person-walking", "description": "Hip flexor, bursitis, labrum tear"},
            {"id": "Neck", "label": "Neck", "icon": "fa-head-side-virus", "description": "Cervical strain, whiplash, stiffness"},
            {"id": "Wrist", "label": "Wrist", "icon": "fa-hand-paper", "description": "Carpal tunnel, sprain, tendonitis"},
            {"id": "Ankle", "label": "Ankle", "icon": "fa-socks", "description": "Sprain, Achilles tendon, instability"},
            {"id": "Back", "label": "Back", "icon": "fa-person", "description": "Lower back, disc, sciatica, posture"},
        ],
        "rehab_goals": [
            {"id": "Pain Reduction", "label": "Pain Reduction", "icon": "fa-heart-pulse", "description": "Relieve pain and reduce inflammation"},
            {"id": "Increase ROM", "label": "Increase ROM", "icon": "fa-arrows-left-right", "description": "Restore full range of motion"},
            {"id": "Strength Building", "label": "Strength Building", "icon": "fa-dumbbell", "description": "Rebuild muscle strength progressively"},
            {"id": "Daily Mobility", "label": "Daily Mobility", "icon": "fa-person-walking-arrow-right", "description": "Improve everyday functional movement"},
        ],
        "difficulty_levels": ["Beginner", "Intermediate", "Advanced"],
    }


# ================================================================
#   VOICE ASSISTANT ENDPOINTS
# ================================================================

@app.post("/voice/toggle")
async def toggle_voice(current_user: User = Depends(get_current_active_user)):
    """Toggle voice assistance on/off"""
    if not exercise_voice_integration:
        raise HTTPException(status_code=503, detail="Voice assistant not available")
    try:
        is_enabled = exercise_voice_integration.toggle_voice()
        return {
            "success": True,
            "enabled": is_enabled,
            "message": f"Voice {'enabled' if is_enabled else 'disabled'}"
        }
    except Exception as e:
        logger.error(f"Error toggling voice: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle voice")


@app.post("/voice/enable")
async def enable_voice(current_user: User = Depends(get_current_active_user)):
    """Enable voice assistance"""
    if not exercise_voice_integration:
        raise HTTPException(status_code=503, detail="Voice assistant not available")
    try:
        exercise_voice_integration.enable_voice()
        return {
            "success": True,
            "enabled": True,
            "message": "Voice enabled"
        }
    except Exception as e:
        logger.error(f"Error enabling voice: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable voice")


@app.post("/voice/disable")
async def disable_voice(current_user: User = Depends(get_current_active_user)):
    """Disable voice assistance"""
    if not exercise_voice_integration:
        raise HTTPException(status_code=503, detail="Voice assistant not available")
    try:
        exercise_voice_integration.disable_voice()
        return {
            "success": True,
            "enabled": False,
            "message": "Voice disabled"
        }
    except Exception as e:
        logger.error(f"Error disabling voice: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable voice")


@app.post("/voice/speed")
async def set_voice_speed(speed: int, current_user: User = Depends(get_current_active_user)):
    """Set voice speed (words per minute: 50-300)"""
    if not exercise_voice_integration:
        raise HTTPException(status_code=503, detail="Voice assistant not available")
    try:
        if not 50 <= speed <= 300:
            raise HTTPException(status_code=400, detail="Speed must be between 50 and 300 WPM")
        
        exercise_voice_integration.adjust_voice_speed(speed)
        return {
            "success": True,
            "speed": speed,
            "message": f"Voice speed set to {speed} WPM"
        }
    except Exception as e:
        logger.error(f"Error setting voice speed: {e}")
        raise HTTPException(status_code=500, detail="Failed to set voice speed")


@app.post("/voice/volume")
async def set_voice_volume(volume: float, current_user: User = Depends(get_current_active_user)):
    """Set voice volume (0.0 to 1.0)"""
    if not exercise_voice_integration:
        raise HTTPException(status_code=503, detail="Voice assistant not available")
    try:
        if not 0.0 <= volume <= 1.0:
            raise HTTPException(status_code=400, detail="Volume must be between 0.0 and 1.0")
        
        exercise_voice_integration.adjust_voice_volume(volume)
        return {
            "success": True,
            "volume": volume,
            "message": f"Volume set to {volume}"
        }
    except Exception as e:
        logger.error(f"Error setting voice volume: {e}")
        raise HTTPException(status_code=500, detail="Failed to set voice volume")


@app.get("/voice/status")
async def get_voice_status(current_user: User = Depends(get_current_active_user)):
    """Get current voice assistant status"""
    if not exercise_voice_integration:
        raise HTTPException(status_code=503, detail="Voice assistant not available")
    try:
        status = exercise_voice_integration.get_voice_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting voice status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice status")


@app.get("/voice/debug/{user_id}")
async def get_voice_debug(user_id: str, current_user: User = Depends(get_current_active_user)):
    """Get debug info for voice event engine (for troubleshooting)"""
    if not exercise_voice_integration:
        return {"success": False, "message": "Voice system not available"}
    try:
        session_state = exercise_voice_integration.event_engine.get_session_state(user_id)
        
        return {
            "success": True,
            "data": {
                "session_state": session_state,
                "voice_enabled": exercise_voice_integration.is_voice_enabled(),
                "event_engine_active": exercise_voice_integration.event_engine is not None,
            }
        }
    except Exception as e:
        logger.error(f"Error getting voice debug info: {e}")
        return {"success": False, "message": str(e)}

# Health check

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Physiotherapy Monitoring System is running"}

# Serve frontend
@app.get("/")
async def root():
    """Serve frontend index page"""
    try:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        with open(frontend_dir / "index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"message": "Frontend not found. Please ensure frontend/index.html exists"}

@app.get("/style.css")
async def get_css():
    """Serve CSS file"""
    try:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        with open(frontend_dir / "style.css", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="text/css")
    except FileNotFoundError:
        return {"error": "CSS file not found"}

@app.get("/script.js")
async def get_js():
    """Serve JavaScript file"""
    try:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        with open(frontend_dir / "script.js", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    except FileNotFoundError:
        return {"error": "JavaScript file not found"}

@app.get("/voice-assistant.js")
async def get_voice_assistant_js():
    """Serve voice assistant module"""
    try:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        with open(frontend_dir / "voice-assistant.js", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    except FileNotFoundError:
        return {"error": "Voice assistant JavaScript file not found"}

@app.get("/ui-enhancements.js")
async def get_ui_enhancements_js():
    """Serve UI enhancements module"""
    try:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        with open(frontend_dir / "ui-enhancements.js", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    except FileNotFoundError:
        return {"error": "UI enhancements JavaScript file not found"}

@app.get("/test-validator.js")
async def get_test_validator():
    """Serve test validator file"""
    try:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        with open(frontend_dir / "test-validator.js", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    except FileNotFoundError:
        return {"error": "Test validator file not found"}

if __name__ == "__main__":
    import uvicorn
    port = settings.PORT
    host = settings.HOST
    
    print(f"🚀 Starting Physiotherapy Monitoring Backend")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {settings.is_development()}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        reload=settings.is_development()
    )
