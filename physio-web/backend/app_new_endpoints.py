"""
PhysioMonitor New API Endpoints
Features: Chatbot, Therapist Dashboard, Injury Prediction, Voice Events
To be integrated into backend/app.py
"""

# ===== CHATBOT ENDPOINTS =====
@app.post("/chat")
async def chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """AI Chatbot endpoint"""
    try:
        user_message = request.user_message
        exercise_context = request.exercise
        
        # Get chatbot response
        response = ai_chatbot.get_response(
            message=user_message,
            exercise=exercise_context,
            context={
                "username": current_user.username,
                "user_id": current_user.id
            }
        )
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail="Chatbot error")


# ===== PROGRESS & ANALYTICS ENDPOINTS ===== 
@app.get("/progress/stats")
def get_progress_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user progress statistics"""
    try:
        sessions = db.query(ExerciseSession).filter(
            ExerciseSession.user_id == current_user.id
        ).all()
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_reps": 0,
                "average_quality": 0,
                "days_active": 0,
                "current_streak": 0,
                "total_duration": 0
            }
        
        # Calculate statistics
        total_reps = sum(s.total_reps for s in sessions)
        avg_quality = sum(s.quality_score for s in sessions) / len(sessions)
        
        # Days active
        unique_dates = set(s.date.date() for s in sessions)
        days_active = len(unique_dates)
        
        # Current streak
        sorted_dates = sorted(unique_dates)
        current_streak = 1
        if sorted_dates:
            today = datetime.now().date()
            for i in range(len(sorted_dates) - 1, 0, -1):
                if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                    current_streak += 1
                else:
                    break
        
        # Total duration
        total_duration_seconds = sum(s.duration_seconds for s in sessions)
        
        return {
            "total_sessions": len(sessions),
            "total_reps": total_reps,
            "average_quality": round(avg_quality, 1),
            "days_active": days_active,
            "current_streak": current_streak,
            "total_duration": round(total_duration_seconds / 3600, 1)  # Hours
        }
    except Exception as e:
        logger.error(f"Progress stats error: {e}")
        raise HTTPException(status_code=500, detail="Error getting progress stats")


@app.get("/progress/weekly")
def get_weekly_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly activity data"""
    try:
        # Last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        sessions = db.query(ExerciseSession).filter(
            ExerciseSession.user_id == current_user.id,
            ExerciseSession.date >= seven_days_ago
        ).all()
        
        # Group by date
        daily_reps = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).date()
            daily_reps[date.isoformat()] = 0
        
        for session in sessions:
            date = session.date.date().isoformat()
            if date in daily_reps:
                daily_reps[date] += session.total_reps
        
        return {
            "dates": list(daily_reps.keys()),
            "reps": list(daily_reps.values())
        }
    except Exception as e:
        logger.error(f"Weekly progress error: {e}")
        raise HTTPException(status_code=500, detail="Error getting weekly progress")


@app.get("/progress/quality-trend")
def get_quality_trend(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quality score trend"""
    try:
        # Last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sessions = db.query(ExerciseSession).filter(
            ExerciseSession.user_id == current_user.id,
            ExerciseSession.date >= thirty_days_ago
        ).order_by(ExerciseSession.date).all()
        
        return {
            "dates": [s.date.isoformat() for s in sessions],
            "quality_scores": [s.quality_score for s in sessions]
        }
    except Exception as e:
        logger.error(f"Quality trend error: {e}")
        raise HTTPException(status_code=500, detail="Error getting quality trend")


# ===== THERAPIST ENDPOINTS =====
@app.get("/therapist/patients")
async def get_therapist_patients(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of patients for therapist"""
    try:
        # In a full implementation, you'd have a therapist_patients table
        # For now, return all users (simplified)
        patients = db.query(User).all()
        
        patients_data = []
        for patient in patients:
            sessions = db.query(ExerciseSession).filter(
                ExerciseSession.user_id == patient.id
            ).all()
            
            avg_quality = sum(s.quality_score for s in sessions) / len(sessions) if sessions else 0
            
            patients_data.append({
                "id": patient.id,
                "full_name": patient.full_name,
                "email": patient.email,
                "sessions_count": len(sessions),
                "avg_quality": round(avg_quality, 1),
                "total_reps": sum(s.total_reps for s in sessions)
            })
        
        return {"patients": patients_data}
    except Exception as e:
        logger.error(f"Get therapist patients error: {e}")
        raise HTTPException(status_code=500, detail="Error getting patient list")


@app.get("/therapist/patients/{patient_id}/progress")
async def get_patient_progress(
    patient_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific patient"""
    try:
        patient = db.query(User).filter(User.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        sessions = db.query(ExerciseSession).filter(
            ExerciseSession.user_id == patient_id
        ).order_by(ExerciseSession.date.desc()).all()
        
        exercise_history = [{
            "name": s.exercise_name,
            "reps": s.total_reps,
            "quality": s.quality_score,
            "angle": s.average_joint_angle,
            "date": s.date.isoformat()
        } for s in sessions[:20]]  # Last 20 sessions
        
        return {
            "id": patient.id,
            "full_name": patient.full_name,
            "email": patient.email,
            "sessions_count": len(sessions),
            "total_reps": sum(s.total_reps for s in sessions),
            "avg_quality": round(sum(s.quality_score for s in sessions) / len(sessions), 1) if sessions else 0,
            "days_active": len(set(s.date.date() for s in sessions)),
            "exercise_history": exercise_history
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get patient progress error: {e}")
        raise HTTPException(status_code=500, detail="Error getting patient progress")


@app.post("/therapist/assign-exercise")
async def assign_exercise(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Assign exercise to patient"""
    try:
        patient_id = request.get("patient_id")
        exercise_name = request.get("exercise_name")
        target_reps = request.get("target_reps", 10)
        instructions = request.get("instructions", "")
        
        # In a full implementation, you'd save this to a therapist_assignments table
        # For now, just return success
        
        return {
            "success": True,
            "message": f"Exercise {exercise_name} assigned to patient {patient_id}"
        }
    except Exception as e:
        logger.error(f"Assign exercise error: {e}")
        raise HTTPException(status_code=500, detail="Error assigning exercise")


# ===== VOICE EVENTS ENDPOINTS =====
@app.post("/voice/event")
async def record_voice_event(
    event_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record voice event for auditing"""
    try:
        event_type = event_data.get("type")
        exercise = event_data.get("exercise")
        message = event_data.get("message")
        
        # Log voice event
        voice_log = VoiceFeedbackLog(
            user_id=current_user.id,
            message=message,
            feedback_type=event_type
        )
        db.add(voice_log)
        db.commit()
        
        return {"success": True, "event_logged": True}
    except Exception as e:
        logger.error(f"Voice event error: {e}")
        raise HTTPException(status_code=500, detail="Error logging voice event")


# ===== REHAB PLAN ENDPOINTS =====
@app.get("/rehab-plan/options")
async def get_rehab_options():
    """Get available rehab plan options"""
    return {
        "plans": [
            {
                "id": 1,
                "name": "Shoulder Recovery",
                "duration": 4,
                "exercises": ["Shoulder Flexion", "Shoulder Abduction", "Shoulder Rotation"]
            },
            {
                "id": 2,
                "name": "Knee Rehabilitation",
                "duration": 6,
                "exercises": ["Knee Flexion", "Knee Extension", "Leg Raise"]
            },
            {
                "id": 3,
                "name": "General Fitness",
                "duration": 8,
                "exercises": ["Squats", "Lunges", "Planks"]
            },
            {
                "id": 4,
                "name": "Balance Training",
                "duration": 4,
                "exercises": ["Single Leg Stand", "Heel to Toe", "Balance Board"]
            }
        ]
    }


@app.post("/rehab-plan")
async def create_rehab_plan(
    plan_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new rehab plan for user"""
    try:
        plan_id = plan_data.get("plan_id")
        # In a full implementation, save to database
        return {
            "success": True,
            "plan_id": plan_id,
            "message": "Rehab plan created successfully"
        }
    except Exception as e:
        logger.error(f"Rehab plan error: {e}")
        raise HTTPException(status_code=500, detail="Error creating rehab plan")


# ===== INJURY PREDICTION ENDPOINTS =====
@app.post("/analysis/injury-risk")
async def predict_injury_risk(
    session_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Predict injury risk based on exercise metrics"""
    try:
        risk_score = session_data.get("quality_score", 70)
        angle = session_data.get("angle", 90)
        exercise = session_data.get("exercise", "unknown")
        reps = session_data.get("reps", 10)
        
        # Simple risk calculation
        if risk_score < 50:
            risk_level = "HIGH"
            risk_factors = ["Poor form", "Inadequate control"]
        elif risk_score < 70:
            risk_level = "MEDIUM"
            risk_factors = ["Moderate form issues", "Consider corrections"]
        else:
            risk_level = "LOW"
            risk_factors = ["Good form"]
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score / 100,
            "risk_factors": risk_factors,
            "recommendations": [
                "Maintain proper form",
                "Take regular breaks",
                "Consult therapist if pain occurs"
            ]
        }
    except Exception as e:
        logger.error(f"Injury prediction error: {e}")
        raise HTTPException(status_code=500, detail="Error predicting injury risk")


# ===== CHATBOT SAFETY TIPS =====
@app.get("/chatbot/safety-tip")
async def get_safety_tip():
    """Get random safety tip"""
    safety_tips = [
        "Always warm up for 5-10 minutes before exercising",
        "Maintain proper posture throughout your exercises",
        "Stop if you experience sharp pain or discomfort",
        "Hydrate well during and after exercise",
        "Don't skip rest days - recovery is important",
        "Listen to your body and modify exercises as needed",
        "Stretch gently after your workout",
        "Focus on quality over quantity of repetitions"
    ]
    import random
    return {"tip": random.choice(safety_tips)}


@app.get("/chatbot/motivation")
async def get_motivation(current_user: User = Depends(get_current_active_user)):
    """Get motivational message"""
    motivations = [
        "You're doing great! Keep up the good work!",
        "Every rep gets you closer to your goals!",
        "Your dedication is inspiring!",
        "Progress, not perfection!",
        "You've got this!",
        "Stay focused and stay motivated!",
        "Today's effort builds tomorrow's strength!",
        "Your health is worth the effort!"
    ]
    import random
    return {
        "message": random.choice(motivations),
        "user": current_user.full_name
    }
