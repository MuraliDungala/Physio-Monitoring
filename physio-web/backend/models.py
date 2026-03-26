from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

# User models
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordResetRequest(BaseModel):
    username: str
    email: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Exercise models
class ExerciseBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    target_reps: int = 10
    target_angle_min: Optional[float] = None
    target_angle_max: Optional[float] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int
    
    class Config:
        from_attributes = True

# Exercise Session models
class ExerciseSessionBase(BaseModel):
    exercise_name: str
    total_reps: int = 0
    average_joint_angle: Optional[float] = None
    quality_score: float = 0.0
    duration_seconds: int = 0
    posture_correctness: float = 100.0

class ExerciseSessionCreate(ExerciseSessionBase):
    pass  # user_id comes from the authenticated JWT token, not from the request body

class ExerciseSessionResponse(ExerciseSessionBase):
    id: int
    user_id: int
    date: datetime
    
    class Config:
        from_attributes = True

# WebSocket message models
class WSFrameData(BaseModel):
    frame_data: str  # base64 encoded image
    selected_exercise: Optional[str] = None

class WSFeedback(BaseModel):
    exercise: str
    reps: int
    angle: float
    posture_message: str
    quality_score: float
    confidence: Optional[float] = None
    voice_message: Optional[str] = None

class VoiceFeedbackLog(BaseModel):
    message: str
    feedback_type: str
    session_id: Optional[int] = None

# Chatbot models
class ChatMessage(BaseModel):
    message: str
    exercise_context: Optional[str] = None
    rep_count: Optional[int] = None
    quality_score: Optional[float] = None
    joint_angle: Optional[float] = None
    posture_feedback: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    is_voice: bool = False

# AI Chat endpoint (POST /chat)
class AIChatRequest(BaseModel):
    user_message: str = ""
    exercise: Optional[str] = None
    rep_count: Optional[str] = None
    quality_score: Optional[str] = None
    joint_angle: Optional[str] = None
    posture_feedback: Optional[str] = None

class AIChatResponse(BaseModel):
    response: str

# ML Classification models
class ClassifyRequest(BaseModel):
    frame_data: str  # base64 encoded image
    exercise_name: Optional[str] = None  # Optional: hint for biomechanics
    extract_features_only: bool = False  # Optional: return features without classification

class LandmarksData(BaseModel):
    landmarks: dict  # Landmark name -> (x, y, z, visibility)
    confidence: float

class ClassificationResult(BaseModel):
    exercise: str
    confidence: float
    method: str  # 'ML_HIGH_CONFIDENCE', 'BIOMECHANICS_FALLBACK', etc.
    all_predictions: Optional[dict] = None
    extracted_features: Optional[list] = None
    processing_time_ms: float

class ClassifyResponse(BaseModel):
    success: bool
    result: Optional[ClassificationResult] = None
    landmarks: Optional[LandmarksData] = None
    error: Optional[str] = None


# Rehabilitation Plan models
class RehabPlanRequest(BaseModel):
    injury_location: str  # e.g. "Shoulder", "Knee", "Elbow", etc.
    rehab_goals: List[str]  # e.g. ["Pain Reduction", "Increase ROM"]
    difficulty: Optional[str] = "Beginner"  # Beginner / Intermediate / Advanced

class RehabExercise(BaseModel):
    name: str
    description: str
    sets: int
    reps: int
    hold_seconds: Optional[int] = None
    rest_seconds: int = 30
    notes: Optional[str] = None

class RehabDayPlan(BaseModel):
    day: int
    title: str
    focus: str
    exercises: List[RehabExercise]
    daily_goal: str

class RehabPlanResponse(BaseModel):
    injury_location: str
    rehab_goals: List[str]
    difficulty: str
    duration_weeks: int
    plan_name: str
    overview: str
    days: List[RehabDayPlan]

# Rehab Session models
class RehabSessionCreate(BaseModel):
    exercise_name: str
    day: int
    target_reps: int
    reps_done: int
    quality_score: float
    status: str  # pending, completed, incomplete, skipped
    notes: Optional[str] = None

class RehabSessionUpdate(BaseModel):
    reps_done: int
    quality_score: float
    status: str
    notes: Optional[str] = None

class RehabSessionResponse(BaseModel):
    id: int
    exercise_name: str
    day: int
    target_reps: int
    reps_done: int
    quality_score: float
    status: str
    date: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class RehabProgressResponse(BaseModel):
    total_exercises: int
    completed_exercises: int
    pending_exercises: int
    skipped_exercises: int
    completion_rate: float
    by_day: dict  # day -> {completed, total, exercises}
