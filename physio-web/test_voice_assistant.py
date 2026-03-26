#!/usr/bin/env python3
"""
Voice Assistant System - Demo & Testing Script
Demonstrates all voice assistant functionality
"""

import sys
import time
import argparse
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from voice.voice_assistant import voice_assistant, VoiceEventType, VoiceEvent
from voice.exercise_voice_integration import exercise_voice_integration


def demo_basic_voice():
    """Demonstrate basic voice functionality"""
    print("\n" + "="*60)
    print("DEMO: Basic Voice Messages")
    print("="*60)
    
    print("\n1️⃣  Testing basic speak...")
    voice_assistant.speak("Hello! This is the voice assistant system.", priority="high")
    time.sleep(3)
    
    print("\n2️⃣  Testing disabled voice (should not speak)...")
    voice_assistant.disable()
    voice_assistant.speak("This message should not be heard because voice is disabled.", priority="normal")
    print("   (Voice is disabled - message queued but not spoken)")
    
    print("\n3️⃣  Re-enabling voice...")
    voice_assistant.enable()
    voice_assistant.speak("Voice is now enabled again.", priority="high")
    time.sleep(2)
    
    print("\n✅ Basic voice demo complete!")


def demo_exercise_start():
    """Demonstrate exercise start announcements"""
    print("\n" + "="*60)
    print("DEMO: Exercise Start Announcements")
    print("="*60)
    
    exercises = [
        "Shoulder Flexion",
        "Elbow Flexion",
        "Knee Flexion",
        "Body Weight Squat",
    ]
    
    for exercise in exercises:
        print(f"\n📋 Starting exercise: {exercise}")
        exercise_voice_integration.on_exercise_start("demo_user", exercise)
        time.sleep(4)  # Wait for speech to finish
    
    print("\n✅ Exercise start demo complete!")


def demo_rep_counting():
    """Demonstrate rep counting and feedback"""
    print("\n" + "="*60)
    print("DEMO: Rep Counting with Quality Feedback")
    print("="*60)
    
    exercise_voice_integration.on_exercise_start("demo_user", "Shoulder Abduction")
    time.sleep(2)
    
    # Simulate 5 reps
    quality_scores = [0.95, 0.92, 0.85, 0.88, 0.91]
    
    print("\nSimulating 5 repetitions...")
    for i, quality in enumerate(quality_scores, 1):
        print(f"\n  Rep {i}:")
        print(f"    Quality: {quality:.1%}")
        exercise_voice_integration.on_rep_completed("demo_user", i, quality=quality)
        time.sleep(4)  # Wait for speech + cooldown
    
    print("\nCompleting exercise...")
    exercise_voice_integration.on_exercise_complete("demo_user")
    time.sleep(2)
    
    print("\n✅ Rep counting demo complete!")


def demo_posture_corrections():
    """Demonstrate posture correction feedback"""
    print("\n" + "="*60)
    print("DEMO: Posture Correction Alerts")
    print("="*60)
    
    corrections = [
        ("keep_back_straight", "User slouching"),
        ("keep_elbow_bent", "User over-extending arm"),
        ("slower_movement", "User moving too fast"),
        ("maintain_position", "User losing balance"),
    ]
    
    exercise_voice_integration.on_exercise_start("demo_user", "Elbow Flexion")
    time.sleep(2)
    
    print("\nDemonstrating different posture corrections...")
    for error_code, description in corrections:
        print(f"\n⚠️  {description}")
        exercise_voice_integration.on_posture_error("demo_user", error_code)
        time.sleep(5)  # Wait for speech
    
    exercise_voice_integration.on_exercise_complete("demo_user")
    
    print("\n✅ Posture correction demo complete!")


def demo_fatigue_detection():
    """Demonstrate fatigue detection alerts"""
    print("\n" + "="*60)
    print("DEMO: Fatigue Detection")
    print("="*60)
    
    exercise_voice_integration.on_exercise_start("demo_user", "Body Weight Squat")
    time.sleep(2)
    
    print("\nSimulating exercise with fatigue detection...")
    
    # Simulate reps with decreasing quality
    for i in range(1, 16):
        quality = max(0.5, 1.0 - (i * 0.05))  # Quality decreases over time
        print(f"\n  Rep {i}: Quality {quality:.1%}")
        exercise_voice_integration.on_rep_completed("demo_user", i, quality=quality)
        time.sleep(2)
        
        # Simulate fatigue at rep 12
        if i == 12:
            print("\n  🚨 Fatigue detected!")
            exercise_voice_integration.on_fatigue_detected("demo_user", i)
            time.sleep(4)
    
    exercise_voice_integration.on_exercise_complete("demo_user")
    time.sleep(2)
    
    print("\n✅ Fatigue detection demo complete!")


def demo_voice_settings():
    """Demonstrate voice settings controls"""
    print("\n" + "="*60)
    print("DEMO: Voice Settings")
    print("="*60)
    
    # Print current status
    status = exercise_voice_integration.get_voice_status()
    print("\n📊 Current Voice Status:")
    print(f"   Enabled: {status['enabled']}")
    print(f"   Speed: {status['speed']} WPM")
    print(f"   Volume: {status['volume']}")
    print(f"   Gender: {status['gender']}")
    print(f"   Total Messages: {status['total_messages']}")
    print(f"   Suppressed: {status['suppressed']}")
    
    # Test speed adjustment
    print("\n🎤 Testing different speech speeds...")
    for speed in [100, 150, 200]:
        print(f"\n   Setting speed to {speed} WPM...")
        exercise_voice_integration.adjust_voice_speed(speed)
        voice_assistant.speak(f"Speaking at {speed} words per minute", priority="high")
        time.sleep(3)
    
    # Test volume adjustment
    print("\n\n🔊 Testing different volumes...")
    for volume in [0.3, 0.6, 1.0]:
        print(f"\n   Setting volume to {volume:.1%}...")
        exercise_voice_integration.adjust_voice_volume(volume)
        voice_assistant.speak(f"Volume is at {int(volume*100)} percent", priority="high")
        time.sleep(2)
    
    # Final status
    status = exercise_voice_integration.get_voice_status()
    print(f"\n\n✅ Final Status:")
    print(f"   Total messages spoken: {status['total_messages']}")
    print(f"   Messages suppressed (cooldown): {status['suppressed']}")
    
    print("\n✅ Voice settings demo complete!")


def demo_all_exercises():
    """Quick demo with multiple exercises"""
    print("\n" + "="*60)
    print("DEMO: Multiple Exercises Overview")
    print("="*60)
    
    exercises = [
        "Shoulder Flexion",
        "Shoulder Abduction",
        "Elbow Flexion",
        "Knee Extension",
    ]
    
    print(f"\nDemonstrating {len(exercises)} different exercises...")
    
    for exercise in exercises:
        print(f"\n▶️  {exercise}")
        exercise_voice_integration.on_exercise_start("demo_user", exercise)
        time.sleep(1)
        
        # Quick 3 reps
        for i in range(1, 4):
            exercise_voice_integration.on_rep_completed("demo_user", i, quality=0.85)
            time.sleep(2)
        
        exercise_voice_integration.on_exercise_complete("demo_user")
        time.sleep(1)
    
    print("\n✅ Multiple exercises demo complete!")


def demo_cooldown_mechanism():
    """Demonstrate the cooldown mechanism"""
    print("\n" + "="*60)
    print("DEMO: Cooldown Mechanism")
    print("="*60)
    
    print("\nThe cooldown mechanism prevents repetitive announcements.")
    print("E.g., same message within 3 seconds won't be repeated.\n")
    
    # Test with same message
    print("1️⃣  Sending same message twice (3 second cooldown)...")
    voice_assistant.speak("Test message", priority="normal")
    print("   ✓ First message: SPOKEN")
    time.sleep(1)
    
    voice_assistant.speak("Test message", priority="normal")
    print("   ✗ Second message: SUPPRESSED (same message within 3 seconds)")
    
    print("\n2️⃣  Waiting for cooldown...")
    time.sleep(2)
    
    voice_assistant.speak("Test message", priority="normal")
    print("   ✓ Third message: SPOKEN (after 3 second cooldown)")
    
    time.sleep(2)
    
    stats = voice_assistant.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Suppressed: {stats['suppressed_messages']}")
    
    print("\n✅ Cooldown mechanism demo complete!")


def main():
    """Main demo runner"""
    parser = argparse.ArgumentParser(
        description="Voice Assistant System Demo & Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_voice_assistant.py --all           # Run all demos
  python test_voice_assistant.py --basic         # Basic voice demo
  python test_voice_assistant.py --exercise      # Exercise demos
  python test_voice_assistant.py --reps          # Rep counting demo
  python test_voice_assistant.py --posture       # Posture feedback demo
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all voice assistant demos'
    )
    parser.add_argument(
        '--basic',
        action='store_true',
        help='Test basic voice functionality'
    )
    parser.add_argument(
        '--exercise',
        action='store_true',
        help='Demo exercise start announcements'
    )
    parser.add_argument(
        '--reps',
        action='store_true',
        help='Demo rep counting and feedback'
    )
    parser.add_argument(
        '--posture',
        action='store_true',
        help='Demo posture correction alerts'
    )
    parser.add_argument(
        '--fatigue',
        action='store_true',
        help='Demo fatigue detection'
    )
    parser.add_argument(
        '--settings',
        action='store_true',
        help='Demo voice settings controls'
    )
    parser.add_argument(
        '--cooldown',
        action='store_true',
        help='Demo cooldown mechanism'
    )
    
    args = parser.parse_args()
    
    print("\n" + "█"*60)
    print("  🎤 Voice Assistant System - Demo & Test")
    print("█"*60)
    
    try:
        if args.all:
            demo_basic_voice()
            demo_exercise_start()
            demo_rep_counting()
            demo_posture_corrections()
            demo_fatigue_detection()
            demo_voice_settings()
            demo_cooldown_mechanism()
        else:
            if args.basic:
                demo_basic_voice()
            if args.exercise:
                demo_exercise_start()
            if args.reps:
                demo_rep_counting()
            if args.posture:
                demo_posture_corrections()
            if args.fatigue:
                demo_fatigue_detection()
            if args.settings:
                demo_voice_settings()
            if args.cooldown:
                demo_cooldown_mechanism()
            if not any([args.basic, args.exercise, args.reps, args.posture, 
                       args.fatigue, args.settings, args.cooldown]):
                # Default: show help
                parser.print_help()
                return
        
        print("\n" + "█"*60)
        print("  ✅ All Demos Complete!")
        print("█"*60 + "\n")
        
        # Final statistics
        stats = voice_assistant.get_statistics()
        print("📊 Final Statistics:")
        print(f"   Total Messages: {stats['total_messages']}")
        print(f"   Suppressed: {stats['suppressed_messages']}")
        print(f"   Voice Enabled: {stats['enabled']}")
        print(f"   Speed: {stats['voice_speed']} WPM")
        print(f"   Volume: {stats['voice_volume']}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        voice_assistant.shutdown()
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        voice_assistant.shutdown()


if __name__ == "__main__":
    main()
