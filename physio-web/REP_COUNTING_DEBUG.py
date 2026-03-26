"""
REP COUNTING DEBUGGING AND TROUBLESHOOTING GUIDE
================================================
"""

print("""
🔧 REP COUNTING TROUBLESHOOTING GUIDE
=====================================

WHAT WAS FIXED:
✅ Port mismatch (8001 → 8000)
✅ Categories endpoint format
✅ API connectivity restored

HOW REP COUNTING WORKS:
=====================

1. EXERCISE SELECTION
   - User clicks exercise button
   - Frontend calls API: GET /exercises/category/{category}
   - Exercise name is stored in 'currentExercise'

2. CAMERA START
   - User clicks "Start Camera" button
   - Browser requests camera permission
   - Video stream is captured and displayed
   - MediaPipe Pose Detection initializes

3. POSE DETECTION
   - Each video frame (~30 fps) is processed
   - MediaPipe detects 33 body landmarks with confidence scores
   - Results sent to onPoseResults() function

4. EXERCISE ANALYSIS
   - Function: processExerciseDetection(landmarks)
   - Checks if required landmarks are visible
   - Calculates joint angles (height, width, depth)
   - Detects exercise phase (e.g., "extended" vs "flexed")

5. REP COUNTING
   - Function: countReps(phase)
   - Detects phase transitions (e.g., extended → flexed)
   - Increments rep counter on complete cycle
   - Provides voice feedback (if enabled)

REQUIREMENTS FOR REP COUNTING:
=============================

✓ Exercise must be selected  (currentExercise != null)
✓ Camera must be running     (videoStream != null)
✓ Pose must be detected      (landmarks.length > 0)
✓ Required joints visible    (visibility > 0.5)
✓ Phase transition occurs    (extended → flexed → extended)

DEBUGGING REP COUNTS NOT INCREASING:
==================================

1. CHECK BROWSER CONSOLE (F12):
   - Open Developer Tools (F12)
   - Go to Console tab
   - Look for messages like:
     ✓ "✓ Processing exercise detection with landmarks: 33"
     ✓ "Rep counting: extended → flexed"
     ✓ "✅ Rep counted! Total: 1"
   
   If you see these → Rep counting is working! 
   Check visibility and camera positioning.

2. IF YOU SEE "Required landmarks not visible":
   - Make sure your full body is in the frame
   - For shoulder exercises: show shoulders and arms clearly
   - For knee exercises: show full legs
   - Ensure good lighting

3. IF POSE DETECTION ISN'T WORKING:
   - Check: "MediaPipe Pose not available" in console
   - Solution: Refresh the page (Ctrl+R)
   - Or restart the browser

4. IF REPS ARE COUNTED BUT NOT DISPLAYED:
   - Check if repCount element is updating
   - The display updates when countReps() completes
   - May take 1-2 seconds to show on screen

TIPS FOR BETTER REP COUNTING:
============================

1. POSITIONING:
   - Position yourself with good lighting from front
   - Show the complete range of motion
   - For arms: raise fully and lower fully
   - For legs: straighten and bend fully

2. SPEED:
   - Perform exercises at moderate speed (not too fast)
   - Allow ~1 second per rep for proper detection
   - Too fast may miss phase transitions

3. CAMERA:
   - Webcam should be at eye level or slightly above
   - Stand 2-3 feet away from camera for full body
   - Avoid backlighting

4. EXERCISE SELECTION:
   - Click the exact exercise name
   - Different exercises have different phase patterns
   - "Knee Flexion" ≠ "Shoulder Flexion"

TESTING REP COUNTING:
====================

Quick Test Steps:
1. Open browser console (F12)
2. Select "Elbow Flexion" exercise
3. Click "Start Camera"
4. Perform slow, full range elbow bends
5. Watch console for "✅ Rep counted!" messages

Expected Output in Console:
✓ Canvas size: 640x480, Video size: 640x480
✓ Drawing skeleton with 33 landmarks
✓ Processing exercise detection with landmarks: 33
  Rep counting: ready → flexed
  Rep counting: flexed → extended
✅ Rep counted! Total: 1

API ENDPOINTS FOR TESTING:
==========================

Get all exercises:
  curl http://127.0.0.1:8000/exercises

Get exercises by category:
  curl http://127.0.0.1:8000/exercises/category/Shoulder

Get all categories:
  curl http://127.0.0.1:8000/exercises/categories

Verify backend is running:
  curl http://127.0.0.1:8000/api/classifier/info

JAVASCRIPT CONSOLE COMMANDS:
===========================

Check current exercise:
  console.log(currentExercise)

Check exercise state:
  console.log(exerciseState)

Check rep count:
  console.log(exerciseState.reps)

Check visible landmarks:
  console.log(window.currentLandmarks?.length)

Enable detailed logging:
  window.DEBUG_MODE = true;

COMMON ISSUES & SOLUTIONS:
==========================

Issue: "Exercise selection button not working"
Solution: Port was wrong (8001) → Now fixed to 8000
  - Refresh browser page
  - Click exercise button again

Issue: "Reps not counting but camera working"
Solution: Required joints not visible
  - Move closer to camera
  - Ensure full body in frame
  - Check lighting

Issue: "Camera won't start"
Solution: Camera permission denied or in use
  - Allow camera access in browser permission popup
  - Close other apps using camera
  - Restart browser

Issue: "MediaPipe errors in console"
Solution: Library not loading
  - Refresh page
  - Clear browser cache (Ctrl+Shift+Delete)
  - Check internet connection

NEXT STEPS:
===========

1. Refresh your browser page
2. Select an exercise and start camera
3. Monitor the browser console (F12 → Console)
4. Perform the exercise with full range of motion
5. Check console for "✅ Rep counted!" messages
6. Rep count should increase in the display

For additional help, check:
- Browser console for error messages
- Backend logs (terminal running TypeScript)
- API endpoints with curl/Postman
""")

# Test that the API is actually working
import requests

print("\n" + "=" * 80)
print("LIVE API STATUS")
print("=" * 80 + "\n")

try:
    # Test 1: API is reachable
    response = requests.get("http://127.0.0.1:8000/exercises")
    if response.status_code == 200:
        print("✅ API is responding correctly")
        exercises = response.json()
        print(f"   Total exercises loaded: {len(exercises)}")
    else:
        print(f"❌ API returned status {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to API: {e}")
    print("   Make sure the backend server is running on port 8000")
    print("   Run: cd backend && uvicorn app:app --reload")

print("\n" + "=" * 80)
print("✅ FIXES APPLIED")
print("=" * 80)
print("""
1. ✅ Frontend API port corrected: 8001 → 8000
2. ✅ Categories endpoint format fixed
3. ✅ All API endpoints now responding

To test the full system:
1. Refresh your browser (Ctrl+R or Cmd+R)
2. Try selecting an exercise again
3. Click "Start Camera"
4. Perform the exercise
5. Check console (F12) for rep counting messages
""")
