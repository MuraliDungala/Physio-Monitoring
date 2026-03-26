#!/usr/bin/env python3
"""
List all configured exercises and their tracking status
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "physio-web" / "backend"))

def check_exercise_configuration():
    """Check which exercises are configured for tracking"""
    
    print("=" * 80)
    print("EXERCISE CONFIGURATION STATUS")
    print("=" * 80 + "\n")
    
    # All configured exercises from the engine
    configured_exercises = {
        "Shoulder Exercises": [
            "Shoulder Flexion",
            "Shoulder Extension", 
            "Shoulder Abduction",
            "Shoulder Adduction",
            "Shoulder Internal Rotation",
            "Shoulder External Rotation",
            "Shoulder Horizontal Abduction",
            "Shoulder Horizontal Adduction",
            "Shoulder Circumduction",
        ],
        "Elbow Exercises": [
            "Elbow Flexion",
            "Elbow Extension",
        ],
        "Knee Exercises": [
            "Knee Flexion",
            "Knee Extension",
        ],
        "Hip Exercises": [
            "Hip Abduction",
            "Hip Flexion",
        ],
        "Squat Exercises": [
            "Body Weight Squat",
            "Wall Sit",
            "Sumo Squat",
            "Partial Squat",
            "Squat Hold",
        ],
        "Ankle Exercises": [
            "Ankle Dorsiflexion",
            "Ankle Plantarflexion",
            "Ankle Inversion",
            "Ankle Eversion",
            "Ankle Circles",
        ],
        "Wrist Exercises": [
            "Wrist Flexion",
            "Wrist Extension",
        ],
        "Neck Exercises": [
            "Neck Flexion",
            "Neck Extension",
            "Neck Rotation",
        ],
        "Back Exercises": [
            "Back Extension",
        ],
    }
    
    # Exercises with rep counting ranges
    exercise_ranges = {
        "Shoulder Flexion": (10, 140),
        "Shoulder Extension": (10, 60),
        "Shoulder Abduction": (10, 140),
        "Shoulder Adduction": (10, 60),
        "Shoulder Internal Rotation": (40, 80),
        "Shoulder External Rotation": (10, 50),
        "Elbow Flexion": (30, 150),
        "Elbow Extension": (140, 180),
        "Knee Flexion": (40, 160),
        "Knee Extension": (140, 180),
        "Hip Abduction": (0, 85),
        "Hip Flexion": (5, 120),
        "Body Weight Squat": (60, 110),
        "Wall Sit": (80, 110),
        "Sumo Squat": (60, 110),
        "Partial Squat": (100, 130),
        "Squat Hold": (70, 100),
        "Ankle Dorsiflexion": (70, 120),
        "Ankle Plantarflexion": (100, 160),
        "Ankle Inversion": (10, 60),
        "Ankle Eversion": (0, 50),
        "Ankle Circles": (0, 360),
        "Wrist Flexion": (20, 140),
        "Wrist Extension": (20, 140),
        "Neck Flexion": (25, 90),
        "Neck Extension": (25, 90),
        "Neck Rotation": (15, 85),
        "Back Extension": (10, 80),
    }
    
    # Quality score ranges
    quality_ranges = {
        "Shoulder Flexion": (60, 120),
        "Shoulder Extension": (20, 60),
        "Shoulder Abduction": (60, 120),
        "Shoulder Adduction": (20, 60),
        "Shoulder Internal Rotation": (50, 75),
        "Shoulder External Rotation": (20, 45),
        "Elbow Flexion": (60, 140),
        "Elbow Extension": (150, 180),
        "Knee Flexion": (80, 160),
        "Knee Extension": (160, 180),
        "Hip Abduction": (30, 70),
        "Hip Flexion": (50, 100),
        "Body Weight Squat": (80, 110),
        "Wall Sit": (90, 110),
        "Sumo Squat": (80, 110),
        "Partial Squat": (110, 130),
        "Squat Hold": (80, 100),
        "Ankle Dorsiflexion": (90, 120),
        "Ankle Plantarflexion": (130, 160),
        "Ankle Inversion": (30, 60),
        "Ankle Eversion": (20, 45),
        "Ankle Circles": (0, 360),
        "Wrist Flexion": (60, 140),
        "Wrist Extension": (60, 140),
        "Neck Flexion": (50, 80),
        "Neck Extension": (50, 80),
        "Neck Rotation": (40, 80),
        "Back Extension": (30, 80),
    }
    
    total_exercises = 0
    configured_count = 0
    missing_ranges = []
    missing_quality = []
    
    for category, exercises in configured_exercises.items():
        print(f"\n{category}")
        print("-" * 80)
        print(f"{'Exercise':<40} {'Rep Range':<20} {'Quality':<15} Status")
        print("-" * 80)
        
        for exercise in exercises:
            total_exercises += 1
            
            has_range = exercise in exercise_ranges
            has_quality = exercise in quality_ranges
            
            if has_range and has_quality:
                configured_count += 1
                status = "✓ CONFIGURED"
                rep_range = f"{exercise_ranges[exercise][0]}-{exercise_ranges[exercise][1]}°"
                quality = f"{quality_ranges[exercise][0]}-{quality_ranges[exercise][1]}°"
            else:
                status = "✗ INCOMPLETE"
                rep_range = exercise_ranges.get(exercise, "MISSING")
                if isinstance(rep_range, tuple):
                    rep_range = f"{rep_range[0]}-{rep_range[1]}°"
                quality = quality_ranges.get(exercise, "MISSING")
                if isinstance(quality, tuple):
                    quality = f"{quality[0]}-{quality[1]}°"
            
            if not has_range:
                missing_ranges.append(exercise)
            if not has_quality:
                missing_quality.append(exercise)
            
            print(f"{exercise:<40} {str(rep_range):<20} {str(quality):<15} {status}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total exercises configured: {configured_count}/{total_exercises}")
    
    if missing_ranges:
        print(f"\nExercises missing rep counting ranges ({len(missing_ranges)}):")
        for ex in missing_ranges:
            print(f"  - {ex}")
    else:
        print("\n✓ All exercises have rep counting ranges configured")
    
    if missing_quality:
        print(f"\nExercises missing quality ranges ({len(missing_quality)}):")
        for ex in missing_quality:
            print(f"  - {ex}")
    else:
        print("✓ All exercises have quality scoring configured")
    
    print("\n" + "=" * 80)
    if configured_count == total_exercises:
        print("✓ ALL EXERCISES FULLY CONFIGURED FOR TRACKING")
    else:
        print(f"⚠ {total_exercises - configured_count} exercises need configuration")
    print("=" * 80)
    
    return configured_count == total_exercises

if __name__ == "__main__":
    success = check_exercise_configuration()
    sys.exit(0 if success else 1)
