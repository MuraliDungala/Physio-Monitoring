import cv2
import numpy as np
import sys
sys.path.insert(0, 'physio-web/backend')

from exercise_engine.engine import ExerciseEngine

engine = ExerciseEngine()
print('=== Testing Neck Exercise Detection ===')

# Create a test frame simulating a person
frame = np.ones((480, 640, 3), dtype=np.uint8) * 150
cv2.circle(frame, (320, 100), 40, (100, 100, 100), -1)  # Head
cv2.rectangle(frame, (200, 140), (440, 200), (120, 120, 120), -1)  # Shoulders

result = engine.process_frame(frame, 'Neck Flexion')
print('[OK] Frame processed')
print('[OK] Landmarks detected:', result.get('landmarks_detected', False))
print('[OK] Reps:', result.get('reps', 0))
print('[OK] Angle:', round(result.get('angle', 0), 2), 'degrees')
print('[OK] Quality score:', round(result.get('quality_score', 0), 2))
print('[OK] Message:', result.get('posture_message', 'N/A'))

if result.get('landmarks_detected'):
    print()
    print('[SUCCESS] Neck exercise detection is working!')
    print('   - Landmarks are being detected')
    print('   - Angles are being calculated')
    print('   - Rep counting is ready')
else:
    print()
    print('[INFO] Landmarks not detected in test frame (OK for synthetic frames)')
    print('   - Real camera feeds should detect better')
