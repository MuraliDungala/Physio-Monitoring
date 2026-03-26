#!/usr/bin/env python3
"""
Test script to check which exercises return proper metrics
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'physio-web', 'backend'))

from exercise_engine.engine import ExerciseEngine
import numpy as np

def test_exercise_metrics():
    """Test which exercises return metrics"""
    engine = ExerciseEngine()
    
    exercises = [
        # Shoulders
        "Shoulder Flexion",
        "Shoulder Extension",
        "Shoulder Abduction",
        
        # Elbow
        "Elbow Flexion",
        "Elbow Extension",
        
        # Neck
        "Neck Flexion",
        "Neck Extension",
        "Neck Rotation",
        
        # Wrist
        "Wrist Flexion",
        "Wrist Extension",
        
        # Hip
        "Hip Abduction",
        "Hip Flexion",
        
        # Knee
        "Knee Flexion",
        "Knee Extension",
        
        # Ankle
        "Ankle Dorsiflexion",
        "Ankle Plantarflexion",
        
        # Squat
        "Body Weight Squat",
    ]
    
    print("="*100)
    print("EXERCISE METRICS TEST")
    print("="*100)
    print()
    
    results = {
        "working": [],
        "angle_zero": [],
        "no_landmarks": []
    }
    
    # Try to process a dummy frame (will fail landmarks but shows structure)
    # Create a blank frame
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    for exercise in exercises:
        print(f"Testing: {exercise:<30}", end=" | ")
        
        # Process frame with selected exercise
        result = engine.process_frame(blank_frame, selected_exercise=exercise)
        
        # Check what we got
        has_reps = result.get("reps", 0) is not None
        has_angle = result.get("angle", 0) is not None
        has_quality = result.get("quality_score", 0) is not None
        has_posture = result.get("posture_message") is not None
        landmarks = result.get("landmarks_detected", False)
        
        angle = result.get("angle", 0)
        
        if landmarks and angle > 0:
            status = "[OK] WORKING"
            results["working"].append(exercise)
        elif not landmarks:
            status = "[NO] NO LANDMARKS"
            results["no_landmarks"].append(exercise)
        elif angle == 0:
            status = "[ZERO] ANGLE=0"
            results["angle_zero"].append(exercise)
        else:
            status = "[PARTIAL]"
        
        print(f"{status}")
        print(f"  Reps:{result.get('reps',0)} | Angle:{result.get('angle',0):.1f} deg | Quality:{result.get('quality_score',0):.0f}% | Posture:{result.get('posture_message','N/A')}")
        print()
    
    print("="*100)
    print("SUMMARY")
    print("="*100)
    print(f"[OK] Fully Working: {len(results['working'])} exercises")
    if results['working']:
        for ex in results['working']:
            print(f"   - {ex}")
    
    print(f"\n[ZERO] Angle = 0: {len(results['angle_zero'])} exercises")
    if results['angle_zero']:
        for ex in results['angle_zero']:
            print(f"   - {ex}")
    
    print(f"\n[NO] No Landmarks: {len(results['no_landmarks'])} exercises")
    if results['no_landmarks']:
        for ex in results['no_landmarks']:
            print(f"   - {ex}")

if __name__ == "__main__":
    test_exercise_metrics()
