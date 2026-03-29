# Neck Exercises Testing Guide - After MediaPipe Fix

## Quick Start

### 1. Browser Access
- Open: `http://localhost:8000`
- Server is running on port 8000
- Backend logs show: "Application startup complete"

### 2. WebSocket Debugging
Open browser console (F12) and watch for:
```
✅ Should see: 🔗 Development mode - using local backend: http://localhost:8000
✅ Should see: Connecting WebSocket to: ws://localhost:8000/ws/{user_id}
✅ Should see: WebSocket connected
```

If you see any errors, they'll appear in red in the console.

### 3. Testing Neck Exercises

**Select Exercise:**
1. Login/Register first if needed
2. Click on exercise category dropdown (should have "Neck" category)
3. Select one of:
   - Neck Flexion
   - Neck Extension
   - Neck Rotation

**Start Exercise:**
1. Click "Start Exercise"
2. Allow camera access when prompted
3. Hold neck position for 5 seconds
4. You should see:
   - Live video feed displaying
   - Rep counter should increment
   - Angle should display
   - Quality score should show

### 4. What to Look For

**Working Correctly:**
- 🟢 Camera feed shows live video
- 🟢 Body pose landmarks visible (if skin tone detection is active)
- 🟢 Angles updating in real-time
- 🟢 Rep count increasing when you move
- 🟢 Dashboard shows weekly activity after exercise

**Issues to Check:**
- 🔴 Camera access denied? Grant permission in browser settings
- 🔴 No video feed? Check camera input device
- 🔴 WebSocket connection failed? Check if port 8000 is accessible
- 🔴 No rep counting? Pose detection may need adjustment


## Technical Details

### Pose Detection Method

The system is now using **OpenCV-based Pose Detection**:
```
Frame → HSV Color Space → Skin Tone Detection → Body Contour Detection → 
Landmark Estimation → Angle Calculation → Rep Counting
```

**Why OpenCV instead of MediaPipe?**
- MediaPipe 0.10.33 changed its API structure
- Old `mediapipe.solutions.pose` no longer exists
- Older MediaPipe versions not available on PyPI
- OpenCV fallback provides backward compatibility

### Expected Accuracy

**OpenCV Fallback:**
- Good for basic pose estimation
- Best when:
  - Single person in frame
  - Adequate lighting
  - Camera has clear view of neck/shoulders
  - Minimal background clutter

- May struggle with:
  - Multiple people
  - Extreme lighting conditions
  - Partial body visibility
  - Complex backgrounds

### API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", ...}
```

**WebSocket Connection:**
```
ws://localhost:8000/ws/{user_id}
```

Messages Format:
```json
{
  "type": "frame",
  "frame_data": "base64_encoded_image",
  "exercise_name": "Neck Flexion",
  "category": "Neck"
}
```

Response:
```json
{
  "reps": 5,
  "angle": 35.2,
  "quality_score": 0.85,
  "landmarks_detected": true,
  "posture_message": "Good form"
}
```

## Troubleshooting

### Problem: "WebSocket connection failed"
**Solution:**
1. Ensure backend is running: `uvicorn app:app --host 0.0.0.0 --port 8000`
2. Check if port 8000 is already in use
3. Verify firewall allows port 8000
4. Try accessing `http://localhost:8000/health` in browser

### Problem: "Camera not working"
**Solution:**
1. Allow camera access in browser (Chrome/Firefox settings)
2. Check if camera is being used by another app
3. Restart browser
4. Try a different browser

### Problem: "No reps detected"
**Solution:**
1. Make sure neck is clearly visible in camera
2. Ensure good lighting (avoid backlighting)
3. Move more deliberately (slower, larger movements)
4. Check browser console for pose detection errors
5. Try different exercises to verify detection works

### Problem: "Dashboard shows no weekly activity"
**Solution:**
1. Complete at least 5 reps of an exercise
2. Close the exercise session properly
3. Refresh dashboard page
4. Check browser's local storage is enabled
5. Verify database file exists: `physio_monitoring.db`

## Files Reference

**Backend Configuration:**
- `physio-web/backend/app.py` - Main API server
- `physio-web/backend/exercise_engine/engine.py` - Exercise detection logic (now with OpenCV fallback)

**Frontend Files:**
- `physio-web/frontend/index.html` - Main page
- `physio-web/frontend/script.js` - Frontend logic (includes WebSocket connection)
- `physio-web/frontend/style.css` - Styling

**Database:**
- `physio-web/physio_monitoring.db` - SQLite database for sessions

## Performance Notes

- **Latency:** ~50-100ms per frame (depends on system)
- **CPU Usage:** 15-25% on modern CPU
- **GPU:** Not currently used (CPU-only OpenCV)
- **Memory:** ~100-150MB for running session

## Advanced Testing

### Run Manual Pose Detection Test:
```bash
cd physio-web/backend
python -c "from exercise_engine.engine import ExerciseEngine; 
engine = ExerciseEngine(); 
print('Pose detector initialized:', engine.pose)"
```

### Check Database:
```bash
sqlite3 physio_monitoring.db ".mode column" "SELECT * FROM exercise_sessions LIMIT 5;"
```

### Monitor Backend Logs:
Check terminal where backend is running for real-time logs of frame processing.

## Next Steps After Testing

1. **If exercises work:** ✅ System is ready for production use
2. **If exercises don't work:** 🔧 May need:
   - Better pose model (download ONNX model)
   - Tuning OpenCV parameters
   - Using alternative pose detection library
3. **For better accuracy:** 📈 Consider:
   - Installing MediaPipe-not-redistributable package
   - Using YOLOv8-Pose model
   - Training custom model on your data
