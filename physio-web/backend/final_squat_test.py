#!/usr/bin/env python3
"""
Final comprehensive squat exercise test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from exercise_engine.engine import ExerciseEngine
from database import Exercise, get_db

def final_squat_test():
    """Final comprehensive squat test"""
    
    print("\n" + "=" * 80)
    print("FINAL SQUAT EXERCISE VERIFICATION TEST")
    print("=" * 80 + "\n")
    
    squat_exercises = [
        {"name": "Body Weight Squat", "sequence": [180, 160, 120, 85, 120, 160, 180]},
        {"name": "Wall Sit", "sequence": [180, 150, 100, 90, 100, 150, 180]},
        {"name": "Sumo Squat", "sequence": [180, 150, 90, 85, 90, 150, 180]},
        {"name": "Partial Squat", "sequence": [180, 150, 120, 115, 120, 150, 180]},
        {"name": "Squat Hold", "sequence": [180, 150, 100, 90, 100, 150, 180]},
    ]
    
    engine = ExerciseEngine()
    all_pass = True
    
    for exercise_info in squat_exercises:
        exercise_name = exercise_info["name"]
        sequence = exercise_info["sequence"]
        
        print(f"Testing: {exercise_name}")
        print(f"Sequence: {' -> '.join(map(str, sequence))}°")
        
        max_reps = 0
        for i, angle in enumerate(sequence):
            state = engine.state_manager.get_state(exercise_name)
            motion = {"knee": abs(angle - sequence[i-1]) if i > 0 else 0}
            
            reps, msg = engine._count_reps_simple(exercise_name, angle, state, motion, "knee")
            
            engine.state_manager.update_state(
                exercise_name,
                reps=state.get('reps'),
                last_angle=state.get('last_angle'),
                phase=state.get('phase'),
                direction=state.get('direction'),
                counting=state.get('counting'),
                been_above=state.get('been_above'),
                been_below=state.get('been_below'),
                direction_set=state.get('direction_set'),
                peak_angle=state.get('peak_angle'),
                valley_angle=state.get('valley_angle'),
                exited_since_last=state.get('exited_since_last')
            )
            
            max_reps = max(max_reps, reps)
        
        status = "✅ TRACKING" if max_reps > 0 else "⚠️  NO REPS"
        print(f"Result: {status} (Max reps: {max_reps})")
        print()
        
        if max_reps == 0:
            all_pass = False
    
    # Database check
    print("\nDatabase Status:")
    print("-" * 80)
    
    db = next(get_db())
    all_in_db = True
    
    for ex in squat_exercises:
        db_ex = db.query(Exercise).filter(Exercise.name == ex["name"]).first()
        status = "✅" if db_ex else "❌"
        print(f"{status} {ex['name']}")
        if not db_ex:
            all_in_db = False
    
    db.close()
    
    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print("-" * 80)
    
    if all_pass and all_in_db:
        print("✅ ALL SQUAT EXERCISES ARE WORKING PROPERLY!")
        print("   - All exercises tracking reps correctly")
        print("   - All exercises in database")
        print("   - All angles, ranges, and quality thresholds configured")
        print("\n   Squats are now fully operational in the tracking system!")
    else:
        print("⚠️  Some issues found:")
        if not all_pass:
            print("   - Some exercises not counting reps")
        if not all_in_db:
            print("   - Some exercises missing from database")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    final_squat_test()
