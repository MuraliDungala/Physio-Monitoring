#!/usr/bin/env python3
"""
Test Voice Assistant - Basic Functionality Test
Tests if the voice system is working properly
"""

import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'physio-web' / 'backend'))

def test_voice_basic():
    """Test basic voice output"""
    print("=" * 60)
    print("VOICE ASSISTANT - BASIC TEST")
    print("=" * 60)
    
    try:
        # Import voice guidance
        from voice.exercise_voice_guidance import voice_guidance, ExerciseVoiceGuidance
        print("✓ Voice guidance module imported successfully")
        
        # Test 1: Basic message
        print("\n[Test 1] Testing basic voice output...")
        print("  Expected: You should hear 'Starting test'")
        voice_guidance.speak_async("Starting test")
        time.sleep(2)
        
        # Test 2: Exercise start instruction
        print("\n[Test 2] Testing exercise instruction...")
        print("  Expected: You should hear shoulder flexion instruction")
        msg = ExerciseVoiceGuidance.get_exercise_start_message("Shoulder Flexion")
        print(f"  Message: {msg}")
        voice_guidance.speak_async(msg)
        time.sleep(3)
        
        # Test 3: Form feedback
        print("\n[Test 3] Testing form feedback...")
        print("  Expected: You should hear form feedback message")
        msg = ExerciseVoiceGuidance.get_form_feedback("Shoulder Flexion", 50)
        print(f"  Message: {msg}")
        voice_guidance.speak_async(msg)
        time.sleep(3)
        
        # Test 4: Rep celebration
        print("\n[Test 4] Testing rep completion message...")
        print("  Expected: You should hear celebration message")
        msg = ExerciseVoiceGuidance.get_rep_completion_message()
        print(f"  Message: {msg}")
        voice_guidance.speak_async(msg)
        time.sleep(2)
        
        # Test 5: Motivation
        print("\n[Test 5] Testing motivation message...")
        print("  Expected: You should hear motivation message")
        msg = ExerciseVoiceGuidance.get_motivation_message()
        print(f"  Message: {msg}")
        voice_guidance.speak_async(msg)
        time.sleep(2)
        
        # Test 6: Multiple exercises
        print("\n[Test 6] Testing different exercises...")
        exercises_to_test = [
            "Elbow Flexion",
            "Knee Extension",
            "Hip Abduction",
            "Ankle Dorsiflexion",
            "Neck Flexion"
        ]
        
        for exercise in exercises_to_test:
            msg = ExerciseVoiceGuidance.get_exercise_start_message(exercise)
            print(f"  {exercise}: Playing...", end='', flush=True)
            voice_guidance.speak_async(msg)
            time.sleep(2.5)
            print(" ✓")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nVOICE SYSTEM STATUS: WORKING")
        print("You should have heard 5 test messages plus 5 exercise instructions")
        print("\nNext step: Run the web interface and test with actual exercises")
        
        return True
        
    except ImportError as e:
        print(f"✗ ERROR: Could not import voice module: {e}")
        print("\nMake sure:")
        print("  1. You're in the workspace root directory")
        print("  2. pyttsx3 is installed: pip install pyttsx3")
        print("  3. exercise_voice_guidance.py exists in physio-web/backend/voice/")
        return False
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_voice_basic()
    sys.exit(0 if success else 1)
