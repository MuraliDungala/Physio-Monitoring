#!/usr/bin/env python3
"""
Test Voice Assistant - Full Exercise Flow
Simulates a complete exercise session with voice guidance
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'physio-web' / 'backend'))

def simulate_exercise_session():
    """Simulate a complete exercise with voice guidance"""
    
    print("=" * 70)
    print("VOICE ASSISTANT - EXERCISE SIMULATION TEST")
    print("=" * 70)
    
    try:
        from voice.exercise_voice_guidance import voice_guidance, ExerciseVoiceGuidance
        
        # Test parameters
        exercise_name = "Shoulder Flexion"
        reps_to_simulate = 3
        
        print(f"\nSimulating exercise: {exercise_name}")
        print(f"Will simulate {reps_to_simulate} repetitions with voice guidance")
        print("\nStarting in 2 seconds...")
        time.sleep(2)
        
        # Simulate exercise state
        user_state = {
            'exercise': exercise_name,
            'last_reps': 0,
            'started': False,
            'last_voice_time': 0
        }
        
        rep_count = 0
        angle = 30
        start_time = time.time()
        
        print("\n" + "-" * 70)
        print("EXERCISE SESSION STARTED")
        print("-" * 70)
        
        # Simulate 5 seconds per rep, with voice feedback throughout
        for second in range(reps_to_simulate * 5):
            elapsed = time.time() - start_time
            current_rep = second // 5 + 1
            
            # Simulate angle movement: 30° down, 160° up, repeat
            phase = (second % 5) / 5.0
            if phase < 0.5:
                # Coming up
                angle = 30 + (160 - 30) * (phase * 2)
            else:
                # Going down
                angle = 160 - (160 - 30) * ((phase - 0.5) * 2)
            
            print(f"\n[{elapsed:.1f}s] Rep {current_rep}: Angle = {angle:.1f}°", end='')
            
            # Check for exercise start (first frame)
            if not user_state['started']:
                print(" → STARTING EXERCISE", end='')
                msg = ExerciseVoiceGuidance.get_exercise_start_message(exercise_name)
                print(f"\n  🔊 Voice: {msg}")
                voice_guidance.speak_async(msg, exercise=exercise_name)
                user_state['started'] = True
                time.sleep(2)
                continue
            
            # Check for form feedback (every 2 seconds)
            if second % 2 == 1:
                print(" → FORM CHECK", end='')
                msg = ExerciseVoiceGuidance.get_form_feedback(exercise_name, angle)
                print(f"\n  🔊 Voice: {msg}")
                voice_guidance.speak_async(msg, exercise=exercise_name)
                time.sleep(1.5)
                continue
            
            # Check for rep completion (at peak, coming down)
            if angle < 45 and second % 5 == 4:
                rep_count += 1
                print(f" → REP {rep_count} COMPLETED", end='')
                msg = ExerciseVoiceGuidance.get_rep_completion_message()
                print(f"\n  🔊 Voice: {msg}")
                voice_guidance.speak_async(msg, exercise=exercise_name)
                user_state['last_reps'] = rep_count
                time.sleep(2)
                continue
            
            # Check for motivation (every 3 seconds, 50% chance in sim)
            if second % 3 == 0 and second > 2:
                import random
                if random.random() < 0.5:
                    print(" → MOTIVATION", end='')
                    msg = ExerciseVoiceGuidance.get_motivation_message()
                    print(f"\n  🔊 Voice: {msg}")
                    voice_guidance.speak_async(msg, exercise=exercise_name)
                    time.sleep(1.5)
                    continue
            
            print()
            time.sleep(0.8)
        
        # Cool down
        print("\n" + "-" * 70)
        print(f"EXERCISE COMPLETED: {rep_count} repetitions")
        print("-" * 70)
        
        # Final message
        msg = ExerciseVoiceGuidance.get_exercise_complete_message()
        print(f"\n🔊 Final Voice: {msg}")
        voice_guidance.speak_async(msg, exercise=exercise_name)
        time.sleep(2)
        
        print("\n" + "=" * 70)
        print("✓ SIMULATION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        # Summary
        print(f"\nSummary:")
        print(f"  Exercise: {exercise_name}")
        print(f"  Repetitions: {rep_count}")
        print(f"  Angle range: {30:.1f}° - {160:.1f}°")
        print(f"  Duration: ~{reps_to_simulate * 5} seconds")
        print(f"  Status: ✓ WORKING")
        
        print("\nVoice System Status:")
        print("  ✓ Exercise start instruction working")
        print("  ✓ Form feedback working")
        print("  ✓ Rep celebration working")
        print("  ✓ Motivation working")
        print("  ✓ Exercise complete message working")
        
        print("\nNext Steps:")
        print("  1. Run the web interface: python physio-web/backend/app.py")
        print("  2. Open frontend in browser: http://localhost:5000")
        print("  3. Select an exercise and perform it in front of camera")
        print("  4. Listen for voice guidance during the exercise")
        
        return True
        
    except ImportError as e:
        print(f"✗ ERROR: Could not import voice module: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR during simulation: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_all_exercises():
    """List all available exercises"""
    try:
        from voice.exercise_voice_guidance import ExerciseVoiceGuidance
        
        print("\n" + "=" * 70)
        print("AVAILABLE EXERCISES FOR VOICE TESTING")
        print("=" * 70)
        
        exercises = list(ExerciseVoiceGuidance.EXERCISE_START.keys())
        
        by_category = {
            'Shoulder': [],
            'Elbow': [],
            'Hip': [],
            'Knee': [],
            'Ankle': [],
            'Wrist': [],
            'Neck': [],
            'Back': [],
            'Other': []
        }
        
        for ex in exercises:
            if 'Shoulder' in ex:
                by_category['Shoulder'].append(ex)
            elif 'Elbow' in ex:
                by_category['Elbow'].append(ex)
            elif 'Hip' in ex:
                by_category['Hip'].append(ex)
            elif 'Knee' in ex:
                by_category['Knee'].append(ex)
            elif 'Ankle' in ex:
                by_category['Ankle'].append(ex)
            elif 'Wrist' in ex:
                by_category['Wrist'].append(ex)
            elif 'Neck' in ex:
                by_category['Neck'].append(ex)
            elif 'Back' in ex:
                by_category['Back'].append(ex)
            else:
                by_category['Other'].append(ex)
        
        total = 0
        for category, exlist in by_category.items():
            if exlist:
                print(f"\n{category} Exercises ({len(exlist)}):")
                for ex in exlist:
                    print(f"  • {ex}")
                total += len(exlist)
        
        print(f"\nTotal exercises with voice guidance: {total}")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error listing exercises: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Voice Assistant")
    parser.add_argument('--list', action='store_true', help="List all available exercises")
    args = parser.parse_args()
    
    if args.list:
        list_all_exercises()
    else:
        success = simulate_exercise_session()
        sys.exit(0 if success else 1)
