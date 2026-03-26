#!/usr/bin/env python3
"""
Populate exercises database with default physiotherapy exercises
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import create_tables, get_db, Exercise
from sqlalchemy.orm import Session

def populate_exercises():
    """Populate database with default exercises"""
    
    # Create tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    # Check if exercises already exist
    existing_exercises = db.query(Exercise).count()
    if existing_exercises > 0:
        print(f"✅ {existing_exercises} exercises already exist in database")
        return
    
    # Default exercises
    exercises = [
        # Shoulder Exercises
        Exercise(
            name="Shoulder Flexion",
            description="Raise arm forward and upward",
            category="Shoulder",
            instructions="Stand straight, raise your arm forward and upward as high as possible, then lower slowly",
            target_reps=10,
            rest_time_seconds=30,
            difficulty="Beginner"
        ),
        Exercise(
            name="Shoulder Extension",
            description="Move arm backward behind body",
            category="Shoulder", 
            instructions="Stand straight, move your arm backward behind your body, then return to starting position",
            target_reps=10,
            rest_time_seconds=30,
            difficulty="Beginner"
        ),
        Exercise(
            name="Shoulder Abduction",
            description="Raise arm sideways away from body",
            category="Shoulder",
            instructions="Stand straight, raise your arm sideways away from your body to shoulder height, then lower slowly",
            target_reps=10,
            rest_time_seconds=30,
            difficulty="Beginner"
        ),
        Exercise(
            name="Shoulder Internal Rotation",
            description="Rotate arm inward toward body",
            category="Shoulder",
            instructions="Keep elbow at 90 degrees, rotate your arm inward across your body",
            target_reps=10,
            rest_time_seconds=30,
            difficulty="Intermediate"
        ),
        Exercise(
            name="Shoulder External Rotation", 
            description="Rotate arm outward away from body",
            category="Shoulder",
            instructions="Keep elbow at 90 degrees, rotate your arm outward away from your body",
            target_reps=10,
            rest_time_seconds=30,
            difficulty="Intermediate"
        ),
        
        # Elbow Exercises
        Exercise(
            name="Elbow Flexion",
            description="Bend elbow to bring hand toward shoulder",
            category="Elbow",
            instructions="Bend your elbow to bring your hand toward your shoulder, then straighten slowly",
            target_reps=15,
            rest_time_seconds=20,
            difficulty="Beginner"
        ),
        Exercise(
            name="Elbow Extension",
            description="Straighten elbow from bent position",
            category="Elbow",
            instructions="Start with elbow bent, straighten your arm completely, then bend slowly",
            target_reps=15,
            rest_time_seconds=20,
            difficulty="Beginner"
        ),
        
        # Knee Exercises
        Exercise(
            name="Knee Flexion",
            description="Bend knee to bring heel toward buttock",
            category="Knee",
            instructions="Stand or lie down, bend your knee to bring your heel toward your buttock",
            target_reps=15,
            rest_time_seconds=20,
            difficulty="Beginner"
        ),
        Exercise(
            name="Knee Extension",
            description="Straighten knee from bent position",
            category="Knee", 
            instructions="Sit with knee bent, straighten your leg completely, then bend slowly",
            target_reps=15,
            rest_time_seconds=20,
            difficulty="Beginner"
        ),
        
        # Hip Exercises
        Exercise(
            name="Hip Abduction",
            description="Move leg sideways away from body",
            category="Hip",
            instructions="Stand straight, move your leg sideways away from your body, then return to starting position",
            target_reps=12,
            rest_time_seconds=25,
            difficulty="Beginner"
        ),
        Exercise(
            name="Hip Flexion",
            description="Raise leg forward and upward",
            category="Hip",
            instructions="Stand straight, raise your leg forward and upward, then lower slowly",
            target_reps=12,
            rest_time_seconds=25,
            difficulty="Beginner"
        ),
        
        # Neck Exercises
        Exercise(
            name="Neck Flexion",
            description="Bring chin toward chest",
            category="Neck",
            instructions="Slowly bring your chin toward your chest, hold for 2 seconds, then return to neutral",
            target_reps=10,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Neck Extension",
            description="Tilt head backward",
            category="Neck",
            instructions="Slowly tilt your head backward, hold for 2 seconds, then return to neutral",
            target_reps=10,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Neck Rotation",
            description="Turn head to look over shoulder",
            category="Neck",
            instructions="Slowly turn your head to look over your shoulder, hold for 2 seconds, then switch sides",
            target_reps=8,
            rest_time_seconds=20,
            difficulty="Beginner"
        ),
        
        # Back Exercises
        Exercise(
            name="Back Extension",
            description="Arch backward gently",
            category="Back",
            instructions="Lie on stomach, gently arch your back upward, hold for 3 seconds, then relax",
            target_reps=8,
            rest_time_seconds=30,
            difficulty="Intermediate"
        ),
        
        # Squat Exercises
        Exercise(
            name="Body Weight Squat",
            description="Squat down and stand back up",
            category="Squat",
            instructions="Stand with feet shoulder-width apart, squat down until knees are at 60-110 degrees, then stand back up",
            target_reps=12,
            rest_time_seconds=30,
            difficulty="Intermediate"
        ),
        Exercise(
            name="Wall Sit",
            description="Hold squat position against wall",
            category="Squat",
            instructions="Stand with back against wall, slide down until knees are at 90 degrees, hold for time",
            target_reps=1,
            rest_time_seconds=60,
            difficulty="Intermediate"
        ),
        Exercise(
            name="Sumo Squat",
            description="Squat with wide stance",
            category="Squat",
            instructions="Stand with feet wider than shoulder-width, squat down keeping chest upright, then stand back up",
            target_reps=12,
            rest_time_seconds=30,
            difficulty="Intermediate"
        ),
        Exercise(
            name="Partial Squat",
            description="Shallow squat movement",
            category="Squat",
            instructions="Stand with feet shoulder-width apart, squat down slightly to 100-130 degrees, then stand back up",
            target_reps=15,
            rest_time_seconds=20,
            difficulty="Beginner"
        ),
        Exercise(
            name="Squat Hold",
            description="Hold squat position",
            category="Squat",
            instructions="Stand with feet shoulder-width apart, squat down to 70-100 degrees, hold the position",
            target_reps=1,
            rest_time_seconds=45,
            difficulty="Beginner"
        ),
        
        # Ankle Exercises
        Exercise(
            name="Ankle Dorsiflexion",
            description="Point toes toward shin",
            category="Ankle",
            instructions="Sit or lie down, point your toes toward your shin, hold for 2 seconds, then relax",
            target_reps=15,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Ankle Plantarflexion",
            description="Point toes away from body",
            category="Ankle",
            instructions="Sit or lie down, point your toes away from your body, hold for 2 seconds, then relax",
            target_reps=15,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Ankle Inversion",
            description="Turn sole of foot inward",
            category="Ankle",
            instructions="Sit with foot off ground, turn the sole of your foot inward, hold for 2 seconds, then return",
            target_reps=12,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Ankle Eversion",
            description="Turn sole of foot outward",
            category="Ankle",
            instructions="Sit with foot off ground, turn the sole of your foot outward, hold for 2 seconds, then return",
            target_reps=12,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Ankle Circles",
            description="Rotate ankle in circles",
            category="Ankle",
            instructions="Lift one foot slightly off ground, rotate your ankle in circles, change direction",
            target_reps=10,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        
        # Wrist Exercises
        Exercise(
            name="Wrist Flexion",
            description="Bend wrist downward",
            category="Wrist",
            instructions="Hold arm straight, bend wrist downward, hold for 2 seconds, then return to neutral",
            target_reps=15,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
        Exercise(
            name="Wrist Extension",
            description="Bend wrist upward",
            category="Wrist",
            instructions="Hold arm straight, bend wrist upward, hold for 2 seconds, then return to neutral",
            target_reps=15,
            rest_time_seconds=15,
            difficulty="Beginner"
        ),
    ]
    
    # Add exercises to database
    for exercise in exercises:
        db.add(exercise)
    
    db.commit()
    print(f"✅ Successfully populated {len(exercises)} exercises in database")
    
    # Display added exercises
    print("\n📋 Added Exercises:")
    for exercise in exercises:
        print(f"  - {exercise.name} ({exercise.category})")
    
    db.close()

if __name__ == "__main__":
    populate_exercises()
