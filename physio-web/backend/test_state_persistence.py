#!/usr/bin/env python3
"""
Test state manager persistence for rep counting
This simulates the actual backend flow where state needs to persist across multiple frames
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'Physio-Monitoring')))

from exercise_state_manager import ExerciseStateManager

class MockEngine:
    """Mock engine to test state manager integration"""
    
    def __init__(self):
        self.state_manager = ExerciseStateManager()
    
    def _count_reps_simple(self, exercise, angle, state):
        """Simplified rep counting - matches backend implementation"""
        reps = state['reps']
        target_min, target_max = 20, 120
        
        # Initialize phase if not present
        if 'phase' not in state:
            if angle > (target_min + target_max) / 2:
                state['phase'] = 'flexed'
            else:
                state['phase'] = 'extended'
            state['last_angle'] = angle
            return reps, f"Ready ({angle:.0f}°)"
        
        # Skip if not enough movement
        angle_delta = abs(angle - state.get('last_angle', angle))
        if angle_delta < 3:
            return reps, f"Ready ({angle:.0f}°)"
        
        state['last_angle'] = angle
        
        # Two-phase hysteresis
        midpoint = (target_min + target_max) / 2
        
        if state['phase'] == 'extended':
            if angle > midpoint + (target_max - midpoint) * 0.4:
                state['phase'] = 'flexed'
                return reps, f"Good flex! ({angle:.0f}°)"
            else:
                return reps, f"Return to start... ({angle:.0f}°)"
        
        elif state['phase'] == 'flexed':
            if angle < midpoint - (midpoint - target_min) * 0.4:
                reps += 1
                state['phase'] = 'extended'
                state['reps'] = reps
                return reps, f"Rep {reps} complete! ({angle:.0f}°)"
            else:
                return reps, f"Return to start... ({angle:.0f}°)"
        
        return reps, ""
    
    def process_frame(self, exercise, angle):
        """Simulate processing a frame - same as backend _track_selected_exercise"""
        # Get state from manager
        state = self.state_manager.get_state(exercise)
        
        # Count reps
        reps, posture_msg = self._count_reps_simple(exercise, angle, state)
        
        # PERSIST ALL STATE BACK (this is what was broken)
        self.state_manager.update_state(exercise,
            reps=state.get('reps', 0),
            last_angle=state.get('last_angle', 0),
            phase=state.get('phase', 'extended'),
            been_above=state.get('been_above', False),
            been_below=state.get('been_below', False),
            direction_set=state.get('direction_set', False),
            peak_angle=state.get('peak_angle', 0),
            valley_angle=state.get('valley_angle', 0)
        )
        
        return reps, posture_msg


def test_state_persistence():
    """Test that state persists across multiple frame calls"""
    print("="*60)
    print("TEST: State Persistence Across Multiple Frames")
    print("="*60)
    
    engine = MockEngine()
    exercise = "Shoulder Flexion"
    
    # Simulate one complete rep over multiple frames
    angles = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30]
    
    print(f"\nProcessing {len(angles)} frames for {exercise}")
    print("Angle sequence: 20→120→30 (should count as 1 rep)")
    print("-"*60)
    
    results = []
    for i, angle in enumerate(angles):
        reps, msg = engine.process_frame(exercise, angle)
        results.append((i, angle, reps, msg))
        
        if i % 2 == 0 or i == len(angles) - 1:
            print(f"Frame {i:2d}: {angle:3.0f}° | Reps: {reps} | {msg}")
    
    final_reps = results[-1][2]
    
    print("-"*60)
    print(f"\nFinal rep count: {final_reps}")
    print(f"Expected: 1 rep")
    
    if final_reps == 1:
        print("✓ PASS: State persisted correctly across frames!")
        return True
    else:
        print(f"✗ FAIL: Got {final_reps} reps instead of 1")
        print("\nDEBUG - Full frame sequence:")
        for i, angle, reps, msg in results:
            print(f"  Frame {i:2d}: {angle:3.0f}° → {reps} reps")
        return False


def test_multiple_reps_persistence():
    """Test that multiple reps persist correctly"""
    print("\n" + "="*60)
    print("TEST: Multiple Reps with State Persistence")
    print("="*60)
    
    engine = MockEngine()
    exercise = "Shoulder Abduction"
    
    # Two complete reps
    angles = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30,  # Rep 1
              50, 80, 110, 120, 100, 70, 40, 25]              # Rep 2
    
    print(f"\nProcessing {len(angles)} frames for 2 complete reps")
    print("-"*60)
    
    for i, angle in enumerate(angles):
        reps, msg = engine.process_frame(exercise, angle)
        
        if "complete" in msg.lower() or i == len(angles) - 1:
            print(f"Frame {i:2d}: {angle:3.0f}° → {reps} reps | {msg}")
    
    # Get final count
    final_state = engine.state_manager.get_state(exercise)
    final_reps = final_state['reps']
    
    print("-"*60)
    print(f"\nFinal rep count: {final_reps}")
    print(f"Expected: 2 reps")
    
    if final_reps == 2:
        print("✓ PASS: Multiple reps persisted correctly!")
        return True
    else:
        print(f"✗ FAIL: Got {final_reps} reps instead of 2")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("STATE MANAGER PERSISTENCE TEST")
    print("="*60)
    
    results = []
    
    try:
        results.append(("State Persistence", test_state_persistence()))
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        results.append(("State Persistence", False))
    
    try:
        results.append(("Multiple Reps", test_multiple_reps_persistence()))
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Multiple Reps", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-"*60)
    print(f"Result: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("✓ STATE MANAGER FIXES VERIFIED!")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
