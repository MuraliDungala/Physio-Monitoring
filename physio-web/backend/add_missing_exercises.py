#!/usr/bin/env python3
"""
Add missing squat and ankle exercises to the database
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import create_tables, get_db, Exercise

def add_missing_exercises():
    """Add missing exercises to database"""
    
    # Create tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    # Missing exercises
    missing_exercises = [
        # Squat Exercises
        {
            "name": "Body Weight Squat",
            "description": "Squat down and stand back up",
            "category": "Squat",
            "instructions": "Stand with feet shoulder-width apart, squat down until knees are at 60-110 degrees, then stand back up",
            "target_reps": 12,
            "rest_time_seconds": 30,
            "difficulty": "Intermediate"
        },
        {
            "name": "Wall Sit",
            "description": "Hold squat position against wall",
            "category": "Squat",
            "instructions": "Stand with back against wall, slide down until knees are at 90 degrees, hold for time",
            "target_reps": 1,
            "rest_time_seconds": 60,
            "difficulty": "Intermediate"
        },
        {
            "name": "Sumo Squat",
            "description": "Squat with wide stance",
            "category": "Squat",
            "instructions": "Stand with feet wider than shoulder-width, squat down keeping chest upright, then stand back up",
            "target_reps": 12,
            "rest_time_seconds": 30,
            "difficulty": "Intermediate"
        },
        {
            "name": "Partial Squat",
            "description": "Shallow squat movement",
            "category": "Squat",
            "instructions": "Stand with feet shoulder-width apart, squat down slightly to 100-130 degrees, then stand back up",
            "target_reps": 15,
            "rest_time_seconds": 20,
            "difficulty": "Beginner"
        },
        {
            "name": "Squat Hold",
            "description": "Hold squat position",
            "category": "Squat",
            "instructions": "Stand with feet shoulder-width apart, squat down to 70-100 degrees, hold the position",
            "target_reps": 1,
            "rest_time_seconds": 45,
            "difficulty": "Beginner"
        },
        
        # Ankle Exercises
        {
            "name": "Ankle Dorsiflexion",
            "description": "Point toes toward shin",
            "category": "Ankle",
            "instructions": "Sit or lie down, point your toes toward your shin, hold for 2 seconds, then relax",
            "target_reps": 15,
            "rest_time_seconds": 15,
            "difficulty": "Beginner"
        },
        {
            "name": "Ankle Plantarflexion",
            "description": "Point toes away from body",
            "category": "Ankle",
            "instructions": "Sit or lie down, point your toes away from your body, hold for 2 seconds, then relax",
            "target_reps": 15,
            "rest_time_seconds": 15,
            "difficulty": "Beginner"
        },
        {
            "name": "Ankle Inversion",
            "description": "Turn sole of foot inward",
            "category": "Ankle",
            "instructions": "Sit with foot off ground, turn the sole of your foot inward, hold for 2 seconds, then return",
            "target_reps": 12,
            "rest_time_seconds": 15,
            "difficulty": "Beginner"
        },
        {
            "name": "Ankle Eversion",
            "description": "Turn sole of foot outward",
            "category": "Ankle",
            "instructions": "Sit with foot off ground, turn the sole of your foot outward, hold for 2 seconds, then return",
            "target_reps": 12,
            "rest_time_seconds": 15,
            "difficulty": "Beginner"
        },
        {
            "name": "Ankle Circles",
            "description": "Rotate ankle in circles",
            "category": "Ankle",
            "instructions": "Lift one foot slightly off ground, rotate your ankle in circles, change direction",
            "target_reps": 10,
            "rest_time_seconds": 15,
            "difficulty": "Beginner"
        },
    ]
    
    added_count = 0
    
    for exercise_data in missing_exercises:
        # Check if exercise already exists
        existing = db.query(Exercise).filter(Exercise.name == exercise_data["name"]).first()
        if existing:
            print(f"⏭️  Skipping '{exercise_data['name']}' - already exists")
            continue
        
        # Add new exercise
        new_exercise = Exercise(
            name=exercise_data["name"],
            description=exercise_data["description"],
            category=exercise_data["category"],
            instructions=exercise_data["instructions"],
            target_reps=exercise_data["target_reps"],
            rest_time_seconds=exercise_data["rest_time_seconds"],
            difficulty=exercise_data["difficulty"]
        )
        db.add(new_exercise)
        added_count += 1
        print(f"✅ Added '{exercise_data['name']}' ({exercise_data['category']})")
    
    if added_count > 0:
        db.commit()
        print(f"\n✅ Successfully added {added_count} exercises to database")
    else:
        print("\n✓ All exercises are already in the database")
    
    # Display all exercises by category
    print("\n📋 Current Exercises by Category:")
    categories = db.query(Exercise.category).distinct().all()
    for cat_tuple in sorted(categories):
        category = cat_tuple[0]
        if category and category.strip():
            count = db.query(Exercise).filter(Exercise.category == category).count()
            print(f"  {category}: {count} exercises")
    
    db.close()

if __name__ == "__main__":
    add_missing_exercises()
