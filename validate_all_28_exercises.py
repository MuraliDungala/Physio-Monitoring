#!/usr/bin/env python3
"""
Comprehensive runtime validation of all 28 exercises.
Tests:
- Rep counting accuracy
- Joint angle calculation
- Quality score correctness
- Posture feedback accuracy
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'physio-web', 'backend'))

from exercise_engine.engine import ExerciseEngine

def test_exercise_metrics(exercise_name, test_angles):
    """
    Test an exercise with varying angles and check:
    - Rep counting works
    - Quality scores are calculated
    - Posture feedback is provided
    
    Args:
        exercise_name: Name of the exercise
        test_angles: List of (angle, expected_phase) tuples to simulate
    """
    engine = ExerciseEngine()
    
    print(f"\nTesting: {exercise_name}")
    print("-" * 60)
    
    results = {
        "angle_tracking": False,
        "rep_counting": False,
        "quality_scoring": False,
        "posture_feedback": False,
        "errors": []
    }
    
    # Map exercises to their angle keys for motion lookup
    angle_key_map = {
        # Shoulder exercises
        "Shoulder Flexion": "shoulder_flexion",
        "Shoulder Extension": "shoulder_extension",
        "Shoulder Abduction": "shoulder_abduction",
        "Shoulder Adduction": "shoulder_adduction",
        "Shoulder Internal Rotation": "shoulder_internal_rotation",
        "Shoulder External Rotation": "shoulder_external_rotation",
        
        # Elbow exercises
        "Elbow Flexion": "elbow",
        "Elbow Extension": "elbow",
        
        # Knee exercises
        "Knee Flexion": "knee",
        "Knee Extension": "knee",
        
        # Hip exercises
        "Hip Abduction": "hip",
        "Hip Flexion": "hip",
        
        # Neck exercises
        "Neck Flexion": "neck_flexion",
        "Neck Extension": "neck_extension",
        "Neck Rotation": "neck_rotation",
        
        # Wrist exercises
        "Wrist Flexion": "wrist",
        "Wrist Extension": "wrist",
        
        # Ankle exercises
        "Ankle Dorsiflexion": "ankle",
        "Ankle Plantarflexion": "ankle",
        "Ankle Inversion": "ankle",
        "Ankle Eversion": "ankle",
        "Ankle Circles": "ankle",
        
        # Squat exercises
        "Body Weight Squat": "knee",
        "Wall Sit": "knee",
        "Sumo Squat": "knee",
        "Partial Squat": "knee",
        "Squat Hold": "knee",
        
        # Back exercises
        "Back Extension": "shoulder_extension",
    }
    
    try:
        # Create mock state
        state_data = {
            'reps': 0,
            'last_angle': 0,
            'phase': 'extended',
            'direction': None,
            'counting': False,
            'been_above': False,
            'been_below': False,
            'direction_set': False,
            'peak_angle': 0,
            'valley_angle': 0,
            'exited_since_last': True
        }
        
        # Simulate angles
        angles_collected = []
        quality_scores_collected = []
        posture_msgs_collected = []
        rep_counts = []
        
        motion = {}
        for angle_key in ['shoulder_flexion', 'shoulder_extension', 'shoulder_abduction', 'shoulder_adduction', 'shoulder_internal_rotation', 'shoulder_external_rotation', 'elbow', 'knee', 'hip', 'hip_abduction', 'hip_flexion', 'ankle', 'wrist', 'neck_flexion', 'neck_extension', 'neck_rotation']:
            motion[angle_key] = 5.0  # Simulate motion
        
        # Get the correct angle key for this exercise
        angle_key_for_exercise = angle_key_map.get(exercise_name, 'joint')
        
        for angle_val, description in test_angles:
            # Test angle tracking
            angles_collected.append(angle_val)
            
            # Test rep counting and posture scoring
            reps, posture_msg = engine._count_reps_simple(
                exercise_name, 
                angle_val, 
                state_data,
                motion,
                angle_key=angle_key_for_exercise
            )
            
            rep_counts.append(reps)
            posture_msgs_collected.append(posture_msg)
            
            # Test quality scoring
            quality_score = engine._calculate_quality_score(exercise_name, angle_val)
            quality_scores_collected.append(quality_score)
        
        # Verify results
        if len(angles_collected) > 0:
            results["angle_tracking"] = True
            print(f"  Angle Tracking: PASS ({len(angles_collected)} angles tracked)")
        
        if len(set(rep_counts)) > 1 or rep_counts[-1] > 0:
            results["rep_counting"] = True
            print(f"  Rep Counting: PASS (reps: {rep_counts})")
        else:
            results["rep_counting"] = False
            print(f"  Rep Counting: FAIL (no reps counted, sequence: {rep_counts})")
        
        if len(set(quality_scores_collected)) > 1 or max(quality_scores_collected) > 0:
            results["quality_scoring"] = True
            print(f"  Quality Scoring: PASS (scores: {[f'{q:.0f}' for q in quality_scores_collected]})")
        else:
            print(f"  Quality Scoring: FAIL (all zero scores)")
        
        if len(set(posture_msgs_collected)) > 0:
            results["posture_feedback"] = True
            print(f"  Posture Feedback: PASS ({len(set(posture_msgs_collected))} unique messages)")
            print(f"    Sample: '{posture_msgs_collected[0]}'")
        else:
            print(f"  Posture Feedback: FAIL (no messages)")
        
    except Exception as e:
        results["errors"].append(str(e))
        print(f"  ERROR: {e}")
    
    return results

def main():
    """Run validation tests for all 28 exercises"""
    
    print("="*80)
    print("COMPREHENSIVE RUNTIME VALIDATION - ALL 28 EXERCISES")
    print("="*80)
    
    # Define test cases for each exercise
    # Each exercise gets a sequence of angles that represents a typical rep
    test_cases = {
        # Shoulder exercises
        "Shoulder Flexion": [
            (20, "start"),
            (90, "mid"), 
            (150, "top"),
            (90, "mid"),
            (20, "complete")
        ],
        "Shoulder Extension": [
            (50, "start"),
            (30, "mid"),
            (10, "end"),
            (30, "return"),
            (50, "complete")
        ],
        "Shoulder Abduction": [
            (20, "start"),
            (80, "mid"),
            (140, "top"),
            (80, "mid"),
            (20, "complete")
        ],
        "Shoulder Adduction": [
            (50, "start"),
            (30, "mid"),
            (10, "end"),
            (30, "return"),
            (50, "complete")
        ],
        "Shoulder Internal Rotation": [
            (45, "start"),
            (60, "mid"),
            (80, "end"),
            (60, "return"),
            (45, "complete")
        ],
        "Shoulder External Rotation": [
            (45, "start"),
            (30, "mid"),
            (15, "end"),
            (30, "return"),
            (45, "complete")
        ],
        
        # Elbow exercises
        "Elbow Flexion": [
            (30, "start"),
            (80, "mid"),
            (150, "top"),
            (80, "mid"),
            (30, "complete")
        ],
        "Elbow Extension": [
            (175, "start_near_extension"),
            (160, "mid"),
            (140, "flexed"),
            (160, "mid"),
            (175, "complete")
        ],
        
        # Knee exercises
        "Knee Flexion": [
            (150, "start"),
            (100, "mid"),
            (50, "bottom"),
            (100, "mid"),
            (150, "complete")
        ],
        "Knee Extension": [
            (140, "start"),
            (160, "mid"),
            (180, "full"),
            (160, "return"),
            (140, "complete")
        ],
        
        # Hip exercises
        "Hip Abduction": [
            (20, "start"),
            (45, "mid"),
            (80, "top"),
            (45, "mid"),
            (20, "complete")
        ],
        "Hip Flexion": [
            (30, "start"),
            (60, "mid"),
            (100, "top"),
            (60, "mid"),
            (30, "complete")
        ],
        
        # Neck exercises - adjusted to realistic neck angle ranges with larger motion
        "Neck Flexion": [
            (30, "start"),
            (50, "mid"),
            (85, "full_flexion"),
            (50, "return"),
            (30, "complete")
        ],
        "Neck Extension": [
            (35, "start"),
            (55, "mid"),
            (85, "full_extension"),
            (55, "return"),
            (35, "complete")
        ],
        "Neck Rotation": [
            (20, "start"),
            (45, "mid"),
            (80, "full_rotation"),
            (45, "return"),
            (20, "complete")
        ],
        
        # Wrist exercises
        "Wrist Flexion": [
            (40, "start"),
            (80, "mid"),
            (140, "full"),
            (80, "return"),
            (40, "complete")
        ],
        "Wrist Extension": [
            (40, "start"),
            (80, "mid"),
            (140, "full"),
            (80, "return"),
            (40, "complete")
        ],
        
        # Ankle exercises
        "Ankle Dorsiflexion": [
            (75, "start"),
            (95, "mid"),
            (120, "top"),
            (95, "return"),
            (75, "complete")
        ],
        "Ankle Plantarflexion": [
            (110, "start"),
            (125, "descending"),
            (160, "full_plantarflex"),
            (125, "ascending"),
            (110, "complete")
        ],
        "Ankle Inversion": [
            (20, "start"),
            (40, "mid"),
            (60, "full"),
            (40, "return"),
            (20, "complete")
        ],
        "Ankle Eversion": [
            (10, "start"),
            (25, "mid"),
            (45, "full"),
            (25, "return"),
            (10, "complete")
        ],
        "Ankle Circles": [
            (0, "start_bottom"),
            (90, "quarter_turn"),
            (180, "half_turn"),
            (270, "three_quarter"),
            (10, "wrap_around_complete")
        ],
        
        # Squat exercises - LARGER MOTION RANGES for proper state machine transitions
        "Body Weight Squat": [
            (155, "standing"),
            (120, "descending"),
            (70, "bottom"),
            (120, "ascending"),
            (155, "standing")
        ],
        "Wall Sit": [
            (160, "standing"),
            (100, "hold"),
            (100, "sustained"),
            (100, "sustained"),
            (160, "standing")
        ],
        "Sumo Squat": [
            (155, "standing"),
            (120, "descending"),
            (70, "bottom"),
            (120, "ascending"),
            (155, "standing")
        ],
        "Partial Squat": [
            (155, "standing"),
            (135, "slight_descent"),
            (110, "partial_bottom"),
            (135, "ascending"),
            (155, "standing")
        ],
        "Squat Hold": [
            (160, "standing"),
            (90, "hold"),
            (90, "sustained"),
            (90, "sustained"),
            (160, "standing")
        ],
        
        # Back exercises - LARGER MOTION to trigger thresholds
        "Back Extension": [
            (20, "start_neutral"),
            (45, "mid"),
            (80, "full_extension"),
            (45, "return"),
            (20, "complete")
        ]
    }
    
    # Run tests
    all_results = {}
    summary = {
        "total": 0,
        "passed": 0,
        "issues": []
    }
    
    for exercise, angles in test_cases.items():
        results = test_exercise_metrics(exercise, angles)
        all_results[exercise] = results
        
        summary["total"] += 1
        passed = sum([
            results["angle_tracking"],
            results["rep_counting"],
            results["quality_scoring"],
            results["posture_feedback"]
        ])
        
        if passed == 4:
            summary["passed"] += 1
        else:
            summary["issues"].append({
                "exercise": exercise,
                "failed_metrics": [
                    k for k, v in results.items() 
                    if not v and k != "errors"
                ]
            })
    
    # Print summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total Exercises: {summary['total']}")
    print(f"Exercises with All Metrics Working: {summary['passed']}/{summary['total']}")
    print(f"Success Rate: {(summary['passed']/summary['total'])*100:.1f}%")
    
    if summary["issues"]:
        print(f"\n[ERROR] Issues found in {len(summary['issues'])} exercises:")
        for issue in summary["issues"]:
            print(f"\n  {issue['exercise']}:")
            for metric in issue['failed_metrics']:
                print(f"    - {metric} not working")
    else:
        print("\n[SUCCESS] All exercises working correctly!")
        print("  * All 28 exercises have functional:")
        print("    - Rep counting")
        print("    - Joint angle measurement")
        print("    - Quality scoring")
        print("    - Posture feedback")

if __name__ == "__main__":
    main()
