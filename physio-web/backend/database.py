from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./physio_monitoring.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exercise_sessions = relationship("ExerciseSession", back_populates="user")
    voice_feedback_logs = relationship("VoiceFeedbackLog", back_populates="user")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)  # Neck, Elbow, Shoulder, Wrist, Hip, Knee, Ankle, Squats
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    target_reps = Column(Integer, default=10)
    target_angle_min = Column(Float, nullable=True)
    target_angle_max = Column(Float, nullable=True)
    rest_time_seconds = Column(Integer, default=30)
    difficulty = Column(String, default="Beginner")

class ExerciseSession(Base):
    __tablename__ = "exercise_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now)
    total_reps = Column(Integer, default=0)
    average_joint_angle = Column(Float, nullable=True)
    quality_score = Column(Float, default=0.0)
    duration_seconds = Column(Integer, default=0)
    posture_correctness = Column(Float, default=100.0)  # percentage
    
    # Relationships
    user = relationship("User", back_populates="exercise_sessions")

class VoiceFeedbackLog(Base):
    __tablename__ = "voice_feedback_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("exercise_sessions.id"), nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    feedback_type = Column(String, nullable=False)  # exercise_start, posture_correction, rep_completion, exercise_end
    
    # Relationships
    user = relationship("User", back_populates="voice_feedback_logs")

class RehabSession(Base):
    __tablename__ = "rehab_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    day = Column(Integer, default=1)  # Which day of the plan
    target_reps = Column(Integer, nullable=False)
    reps_done = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending, completed, incomplete, skipped
    date = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
