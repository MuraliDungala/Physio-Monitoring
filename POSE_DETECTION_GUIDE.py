"""
LANDMARK POSE DETECTION - SETUP & FIX GUIDE
Complete guide to enable metrics for all 28 exercises
"""

print("""
================================================================================
LANDMARK POSE DETECTION - COMPLETE GUIDE
================================================================================

WHAT WE FOUND:
✓ MediaPipe is properly installed and initialized
✓ ExerciseEngine is correctly configured
✓ All 28 exercises have angle mappings, rep counting, quality scoring
✓ WebSocket transmission is working
✓ Frontend correctly displays metrics when they arrive
✗ Metrics show ZERO because NO POSE is detected (no person visible)

================================================================================
THE PROBLEM IN ONE SENTENCE:
================================================================================

Your system requires a REAL PERSON visible in the camera frame for pose 
detection to work. Without detected landmarks, all metrics default to ZERO.

================================================================================
STEP 1: VERIFY CAMERA IS WORKING
================================================================================

1. Open the web interface in your browser (http://127.0.0.1:8000)

2. Look for video element on the page - you should see:
   - Your face/body from the camera
   - Real-time video feed
   
3. If you see NO video:
   ✗ Camera permission denied
   ✗ Camera already in use by another app (Zoom, Teams, WebEx, etc.)
   ✗ Browser doesn't have camera permission
   
   FIX:
   - Close all other apps using camera
   - Grant camera permission in browser (settings/preferences)
   - Refresh the page

TESTING:
Run this test to verify camera access:
  python verify_camera.py

================================================================================
STEP 2: POSITION YOURSELF CORRECTLY
================================================================================

MediaPipe needs to see your body to detect landmarks. Requirements:

✓ VISIBILITY
  - Stand 3-6 feet away from camera (for upper body exercises)
  - For leg exercises: position camera to see hips to ankles
  - Entire exercising area should be visible
  
✓ LIGHTING
  - Good, even lighting from front (not backlighting)
  - No dark shadows on body
  - Natural window light works well
  - Avoid bright sun directly in camera
  
✓ CLOTHING
  - Wear contrasting color to background (not black on black)
  - Avoid reflective or transparent clothing
  - Short sleeves better (bare arms more visible)

✓ BACKGROUND
  - Simple background is better (not too busy/cluttered)
  - Avoid moving background or people
  - Plain wall or curtain is ideal

TESTING:
Stand clearly in frame for 5 seconds, then:
  python test_engine_detection.py
  
If you see "Detected 33 landmarks" → YOU'RE READY!
If you see "[NO] No landmarks detected" → Adjust position/lighting

================================================================================
STEP 3: ENABLE METRICS DISPLAY
================================================================================

Once pose is detected, metrics should appear automatically:

✓ Rep Counter - increments as you complete motion
✓ Joint Angle - shows current angle in degrees  
✓ Quality Score - % score based on form (100% = perfect)
✓ Posture Feedback - specific correction messages

Timeline:
1. Start recording/monitoring in web interface
2. Select an exercise (or use auto-detect)
3. Stand clearly in camera frame
4. When detected: skeleton overlay appears (green lines/dots)
5. Metrics display and update in real-time

If metrics show ZERO:
→ Skeleton overlay not visible = No pose detected
→ Check your position, lighting, and visibility

================================================================================
STEP 4: FINE-TUNE IF NEEDED
================================================================================

If pose detection is still unreliable, try these adjustments:

OPTION A: Lower Detection Threshold
=========================================
File: physio-web/backend/exercise_engine/engine.py
Line: ~35

Change from:
  min_detection_confidence=0.5,
  min_tracking_confidence=0.5

Change to:
  min_detection_confidence=0.3,
  min_tracking_confidence=0.3

This makes MediaPipe detect poses with lower certainty.
Trade-off: More false detections if no person visible.

OPTION B: Improve Frame Quality
=========================================
If WebSocket compression is too aggressive:

File: physio-web/frontend/script.js
Line: ~2327

Change from:
  canvas.toBlob(function(blob) {
    ...
  }, 'image/jpeg', 0.8);

Change to:
  canvas.toBlob(function(blob) {
    ...
  }, 'image/jpeg', 0.95);

This sends higher quality frames (less compression).
Trade-off: Larger frames, slightly higher bandwidth.

OPTION C: Adjust Frame Resolution
=========================================
File: physio-web/frontend/script.js
Line: ~2318-2319

Change from:
  canvas.width = 640;
  canvas.height = 480;

Change to:
  canvas.width = 1280;
  canvas.height = 960;

This sends higher resolution to backend.
Trade-off: More bandwidth, longer processing time.

================================================================================
STEP 5: TEST ALL 28 EXERCISES
================================================================================

Once pose detection is working, ALL exercises will show metrics:

SHOULDER (6):
  ✓ Shoulder Flexion → Up/down motion
  ✓ Shoulder Extension → Back/front motion
  ✓ Shoulder Abduction → Out/in motion
  ✓ Shoulder Adduction → In/out motion
  ✓ Shoulder Internal Rotation → Internal rotation
  ✓ Shoulder External Rotation → External rotation

ELBOW (2):
  ✓ Elbow Flexion → Bend/straighten
  ✓ Elbow Extension → Straighten/bend

KNEE (2):
  ✓ Knee Flexion → Bend/straighten
  ✓ Knee Extension → Straighten/bend

HIP (2):
  ✓ Hip Abduction → Out/in motion
  ✓ Hip Flexion → Up/down motion

ANKLE (5):
  ✓ Ankle Dorsiflexion → Toes up/down
  ✓ Ankle Plantarflexion → Toes down/up
  ✓ Ankle Inversion → Sole in/out
  ✓ Ankle Eversion → Sole out/in
  ✓ Ankle Circles → Circular motion

SQUAT (5):
  ✓ Body Weight Squat → Full squat
  ✓ Wall Sit → Against wall
  ✓ Sumo Squat → Wide stance
  ✓ Partial Squat → Half squat
  ✓ Squat Hold → Hold position

WRIST (2):
  ✓ Wrist Flexion → Up/down
  ✓ Wrist Extension → Down/up

NECK (3):
  ✓ Neck Flexion → Forward/back
  ✓ Neck Extension → Back/forward
  ✓ Neck Rotation → Side to side

BACK (1):
  ✓ Back Extension → Arch/straighten

================================================================================
TROUBLESHOOTING
================================================================================

PROBLEM: Video plays but skeleton never appears
CAUSE: No pose detected
SOLUTIONS:
  1. Move closer to camera (3-6 feet)
  2. Improve lighting
  3. Wear lighter clothing if background is dark
  4. Lower detection threshold (see Step 4)
  5. Ensure entire body/limbs visible for selected exercise

PROBLEM: Skeleton appears sometimes but not always
CAUSE: Pose detection intermittent (borderline lighting/position)
SOLUTIONS:
  1. Better lighting
  2. Move further from camera
  3. Clearer background
  4. Steady position during exercise

PROBLEM: Angles show but are always ZERO
CAUSE: Bug in angle computation
SOLUTION: Not applicable - if skeleton visible, angles should compute

PROBLEM: Rep counter doesn't increment
CAUSE: Angle range not met
SOLUTIONS:
  1. Perform full motion (don't partial movements)
  2. Slower, complete movements (MediaPipe needs time to track)
  3. Verify angle is changing (check "Joint Angle" display)

PROBLEM: Quality score is always 0%
CAUSE: Form too far from ideal
SOLUTIONS:
  1. Focus on proper form
  2. Adjust position for better visibility
  3. Refer to exercise guide for ideal positioning

================================================================================
QUICK VERIFICATION CHECKLIST
================================================================================

Before troubleshooting, verify:

[ ] Browser has camera permission
[ ] Only one app using camera (not Zoom/Teams/etc)
[ ] I'm standing clearly in frame, 3-6 feet away
[ ] Good lighting on my body (no shadows)
[ ] Simple background behind me
[ ] Wearing lighter colored clothing
[ ] Entire body (or relevant limbs) visible
[ ] Camera not flipped/inverted
[ ] Browser tab is focused (not minimized)
[ ] WebSocket connection shows connected (check console)

If all checked and still no pose detected → provide detailed debug log:
  python diagnose_pose_detection.py > debug.log
  
================================================================================
EXPECTED BEHAVIOR
================================================================================

Timeline for first successful detection:

1. Open browser, grant camera permission
2. Position yourself clearly in front of camera
3. Wait 1-2 seconds for skeleton overlay to appear (green lines)
4. Once skeleton visible: all metrics should activate
5. Start exercise: rep counter increments, angle/quality update
6. Complete rep: rep count increases by 1

If skeleton NEVER appears after 5+ seconds in good lighting:
→ Pose detection issue (reinstall MediaPipe or adjust thresholds)

If skeleton appears but metrics stay ZERO:
→ Backend processing issue (check server logs)

If metrics appear but don't update:
→ Frame transmission issue (check WebSocket connection)

================================================================================
SUPPORT: Getting Help
================================================================================

1. Run diagnostics:
   python diagnose_pose_detection.py

2. Test system:
   python test_engine_detection.py

3. Check that 28 exercises are configured:
   python test_all_metrics.py

4. Check backend logs for errors:
   cd physio-web/backend
   python app.py  # Watch console for errors

5. Check browser console for WebSocket errors:
   Open DevTools (F12) → Console tab
   Look for red error messages

================================================================================
NEXT STEPS
================================================================================

1. Verify camera setup (Step 1-2)
2. Test with your actual pose (Step 3)
3. If successful → All 28 exercises ready to use
4. If unsuccessful → Apply fixes from Step 4
5. Refer to troubleshooting (Step 5)

ALL INFRASTRUCTURE IS READY.
You just need a clear pose in frame with good lighting.
""")
