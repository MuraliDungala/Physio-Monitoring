#!/usr/bin/env python3
"""
Verify all exercises are properly configured in both backend engine and database
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import Exercise, get_db
from exercise_engine.engine import ExerciseEngine

def verify_exercise_configuration():
    """Verify all exercises are configured"""
    
    print("=" * 80)
    print("EXERCISE CONFIGURATION VERIFICATION")
    print("=" * 80 + "\n")
    
    # Get database exercises
    db = next(get_db())
    db_exercises = db.query(Exercise).all()
    db_by_category = {}
    db_exercises_set = set()
    
    for exercise in db_exercises:
        if exercise.category not in db_by_category:
            db_by_category[exercise.category] = []
        db_by_category[exercise.category].append(exercise.name)
        db_exercises_set.add(exercise.name)
    
    # Get engine configuration
    engine = ExerciseEngine()
    
    # Test with dummy angles to access the engine's configuration
    test_angles = {k: 45 for k in ['shoulder_flexion', 'elbow', 'knee', 'hip_abduction', 'hip_flexion', 
                                     'ankle', 'wrist', 'neck_flexion']}
    
    # Check angle map (from engine)
    engine_exercises = set()
    
    # Read the engine file to extract exercise names from angle_map
    engine_file = os.path.join(os.path.dirname(__file__), 'exercise_engine', 'engine.py')
    with open(engine_file, 'r') as f:
        content = f.read()
        
    # Extract exercise names from angle_map
    import re
    angle_map_match = re.search(r'angle_map = \{(.*?)\}', content, re.DOTALL)
    if angle_map_match:
        angle_map_content = angle_map_match.group(1)
        # Find all quoted exercise names
        exercise_names = re.findall(r'"([^"]+)":\s*\[', angle_map_content)
        engine_exercises = set(exercise_names)
    
    print("📊 DATABASE EXERCISES")
    print("-" * 80)
    total_db = 0
    for category in sorted(db_by_category.keys()):
        exercises = db_by_category[category]
        total_db += len(exercises)
        print(f"\n{category} ({len(exercises)}):")
        for ex in sorted(exercises):
            status = "✅" if ex in engine_exercises else "⚠️"
            print(f"  {status} {ex}")
    
    print(f"\n\nTotal in Database: {total_db}")
    
    print("\n" + "=" * 80)
    print("📊 ENGINE EXERCISES (angle_map)")
    print("-" * 80)
    print(f"Total in Engine: {len(engine_exercises)}\n")
    
    # Group by category
    category_map = {
        "Shoulder": ["Shoulder Flexion", "Shoulder Extension", "Shoulder Abduction", 
                     "Shoulder Adduction", "Shoulder Internal Rotation", "Shoulder External Rotation",
                     "Shoulder Horizontal Abduction", "Shoulder Horizontal Adduction", "Shoulder Circumduction"],
        "Elbow": ["Elbow Flexion", "Elbow Extension"],
        "Knee": ["Knee Flexion", "Knee Extension"],
        "Hip": ["Hip Abduction", "Hip Flexion"],
        "Squat": ["Body Weight Squat", "Wall Sit", "Sumo Squat", "Partial Squat", "Squat Hold"],
        "Ankle": ["Ankle Dorsiflexion", "Ankle Plantarflexion", "Ankle Inversion", "Ankle Eversion", "Ankle Circles"],
        "Wrist": ["Wrist Flexion", "Wrist Extension"],
        "Back": ["Back Extension"],
    }
    
    for category in sorted(category_map.keys()):
        exercises = category_map[category]
        configured_count = len([e for e in exercises if e in engine_exercises])
        print(f"{category}: {configured_count}/{len(exercises)} configured")
        for ex in exercises:
            status = "✅" if ex in engine_exercises else "❌"
            in_db = "📁" if ex in db_exercises_set else "⚠️"
            print(f"  {status} {in_db} {ex}")
    
    print("\n" + "=" * 80)
    print("✅ SUMMARY")
    print("=" * 80)
    
    # Check for mismatches
    in_db_not_engine = db_exercises_set - engine_exercises
    in_engine_not_db = engine_exercises - db_exercises_set
    in_both = db_exercises_set & engine_exercises
    
    print(f"\n✅ Exercises in BOTH Database and Engine: {len(in_both)}")
    print(f"⚠️  Exercises in Database only: {len(in_db_not_engine)}")
    if in_db_not_engine:
        for ex in sorted(in_db_not_engine):
            print(f"    - {ex}")
    
    print(f"⚠️  Exercises in Engine only: {len(in_engine_not_db)}")
    if in_engine_not_db:
        for ex in sorted(in_engine_not_db):
            print(f"    - {ex}")
    
    print(f"\n📊 TOTAL CONFIGURED FOR TRACKING: {len(in_both)}")
    
    if len(in_db_not_engine) == 0 and len(in_engine_not_db) == 0:
        print("\n🎉 ALL EXERCISES FULLY CONFIGURED!")
    else:
        print("\n⚠️  Some exercises need configuration")
    
    db.close()

if __name__ == "__main__":
    verify_exercise_configuration()
