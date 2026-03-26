# "Start Exercise from Rehab Plan" Feature Guide

## Overview
This document describes the new "Start Exercise from Rehab Plan" feature that enables users to start exercises directly from their personalized rehabilitation plan and track completion progress in real-time.

## Features Implemented

### 1. **Exercise Status Indicators** ✨
Each exercise now displays its completion status:
- **✔ Completed** (Green): Exercise successfully completed with quality score ≥ 70%
- **❌ Incomplete** (Red): Exercise attempted but quality < 70%
- **⏳ Pending** (Yellow): Exercise not yet started
- **⊘ Skipped** (Gray): Exercise skipped/marked as skip

Status persists across sessions and loads when viewing rehab plan.

### 2. **Start Exercise Buttons** 🎬
- Each exercise row now includes a "Start Exercise" button with play icon
- Clicking button:
  - Records which exercise is being started from rehab plan context
  - Navigates to exercise camera view
  - Starts MediaPipe pose detection
  - Automatically enables for real-time tracking

### 3. **Progress Tracking Per Day** 📊
- Each day shows a visual progress bar
- Displays completion percentage (e.g., "2/4 exercises completed = 50%")
- Progress bar fills as exercises are completed
- Easy visual indicator of plan progress

### 4. **Rehab Session Persistence** 💾
New `updateRehabSessionStatus()` function automatically:
- Finds or creates rehab session record for exercise+day
- Records: reps completed, quality score, completion status
- Stores notes indicating exercise came from rehab plan
- Updates backend database synchronously

### 5. **Smart Navigation** 🔄
- After completing an exercise from rehab plan:
  - User automatically returns to rehab plan view
  - Status immediately updates to show completion
  - Progress bars refresh instantly
  - Can see updated plan and start next exercise

## Technical Implementation

### Backend Changes
**No backend changes required** - all APIs already existed:
- `POST /rehab-sessions` - Create new rehab session record
- `PUT /rehab-sessions/{session_id}` - Update session with reps/quality/status
- `GET /rehab-sessions` - Fetch all sessions for current user
- `GET /rehab-sessions/day/{day_number}` - Get sessions for specific day

### Frontend Changes

#### 1. HTML Structure (index.html)
- No new HTML elements added - uses existing `planDays` container
- Renders dynamically from JavaScript

#### 2. CSS Styling (style.css - Added)
```css
/* Progress bar styling */
.plan-day-progress { ... }
.progress-bar { ... }
.progress-fill { ... }

/* Status indicators */
.plan-ex-actions { ... }
.plan-ex-status { ... }
.status-completed { background: #d1fae5; color: #059669; }
.status-incomplete { background: #fee2e2; color: #dc2626; }
.status-pending { background: #fef3c7; color: #b45309; }
.status-skipped { background: #e5e7eb; color: #6b7280; }

/* Action buttons */
.btn-sm { padding: 6px 14px; font-size: 13px; }
```

#### 3. JavaScript Functions (script.js - Added/Modified)

##### New Functions:
1. **`loadRehabStatus(plan)`** (Line 4533)
   - Fetches existing rehab sessions from backend
   - Indexes by exercise_name-day for quick lookup
   - Passes to render function

2. **`renderRehabPlanWithStatus(plan, rehabSessions)`** (Line 4554)
   - Renders plan with status indicators and Start buttons
   - Calculates day completion percentages
   - Shows reps/quality for completed exercises

3. **`startRehabExercise(exerciseName, day, planName)`** (Line 4655)
   - Records rehab context: `window._rehabContext`
   - Sets current exercise name and plan info
   - Navigates to exercise page
   - Starts camera for pose detection

4. **`updateRehabSessionStatus(exerciseName, reps, quality, status)`** (Line 4673)
   - Determines if session is create or update
   - Saves to backend `/rehab-sessions` endpoint
   - Calculates status based on quality score
   - Logs success to console

##### Modified Functions:
1. **`exitExercise()`** (Line 3238)
   - Added check for `window._rehabContext` after session save
   - Automatically calls `updateRehabSessionStatus()` with final reps/quality
   - Navigates back to rehab plan instead of categories
   - Reloads plan to show updated status

2. **`renderRehabPlan(plan)`** (Line 4481)
   - Now calls `loadRehabStatus()` to fetch prior session data
   - Delegates rendering to `renderRehabPlanWithStatus()`

### Global State
New global variable added:
```javascript
window._rehabContext = {
    exerciseName: "Shoulder Press",
    day: 1,
    planName: "Rotator Cuff Rehabilitation"
}
```
- Set when starting exercise from rehab plan
- Cleared after returning from exercise
- Used to determine if we should save to rehab_sessions table

## User Workflow

### 1. User Generates Rehab Plan
```
1. Navigate to Rehab Plan page
2. Select injury location (e.g., "Shoulder")
3. Select goals (e.g., "Reduce Pain", "Increase ROM")
4. Click "Generate My Rehab Plan"
```

### 2. View Plan with Status
```
1. Plan displays with Day sections
2. Each day shows:
   - Day title & goal
   - Progress bar (e.g., "0/4 exercises" = 0%)
   - Exercise list with status badges
```

### 3. Start Exercise
```
1. Click "Start" button on any exercise row
2. Camera view opens with exercise name visible
3. MediaPipe pose detection starts automatically
4. Rep counter, angle display, quality score shown
```

### 4. Complete Exercise
```
1. Perform exercise while visible to camera
2. Rep counter increments on full cycles
3. Quality score updates in real-time
4. Exercise completes when reps reached or stopped manually
```

### 5. Auto-Return to Rehab Plan
```
1. Click exit or complete exercise
2. App automatically:
   - Saves session to database
   - Updates rehab session status (completed/incomplete)
   - Navigates back to rehab plan
   - Plan reloads showing updated status
```

## Status Determination Logic

### Quality Score Threshold
```javascript
Status = quality_score >= 70 ? 'completed' : 'incomplete'
```

### Quality Score Calculation
```
Quality = (angleAccuracy * 40%) + 
          (symmetry * 25%) + 
          (stability * 15%) +
          (posture * 15%) +
          (ROM * 5%)
```

## API Integration

### Request: Create/Update Rehab Session
```javascript
POST /rehab-sessions
{
    "exercise_name": "Shoulder Press",
    "day": 1,
    "target_reps": 10,
    "reps_done": 9,
    "quality_score": 75,
    "status": "completed",
    "notes": "Completed from rehab plan: Rotator Cuff Rehabilitation"
}

PUT /rehab-sessions/{session_id}
{
    "reps_done": 10,
    "quality_score": 78,
    "status": "completed"
}
```

### Response: Fetch Sessions
```javascript
GET /rehab-sessions
Returns: [
    {
        "id": 1,
        "user_id": 5,
        "exercise_name": "Shoulder Press",
        "day": 1,
        "target_reps": 10,
        "reps_done": 9,
        "quality_score": 75,
        "status": "completed",
        "date": "2025-01-15",
        "notes": "..."
    },
    ...
]
```

## Data Flow Diagram

```
User clicks "Start Exercise" (Rehab Plan)
         ↓
startRehabExercise() sets window._rehabContext
         ↓
User performs exercise (Camera tracking)
         ↓
exitExercise() detects _rehabContext
         ↓
updateRehabSessionStatus() called with:
   - exerciseName
   - reps_done
   - quality_score
   - status (completed/incomplete)
         ↓
POST/PUT to /rehab-sessions API
         ↓
Navigate back to Rehab Plan
         ↓
loadRehabStatus() fetches updated sessions
         ↓
renderRehabPlanWithStatus() displays with:
   - Status badges (✔/❌/⏳)
   - Progress bars updated
```

## Error Handling

### Failed to Load Sessions
```javascript
try {
    // GET /rehab-sessions
} catch (error) {
    console.warn('Could not load rehab sessions:', error);
    // Continue with empty sessions, all shows as "Pending"
}
```

### Failed to Save Session
```javascript
try {
    // POST/PUT /rehab-sessions
} catch (error) {
    console.error('Error updating rehab session:', error);
    // User still returns to plan, but data not saved
    // Next iteration should retry
}
```

## File Changes Summary

| File | Change Type | Lines | Description |
|------|-------------|-------|-------------|
| script.js | Added Functions | 4481-4730 | New rehab rendering + session update |
| script.js | Modified | 3238-3260 | Exit function integration |
| style.css | Added Styles | After 1107 | Progress bar, status, action styles |

## Testing Checklist

- [ ] Generate rehab plan
- [ ] Click "Start" button on first exercise
- [ ] Camera view opens for correct exercise
- [ ] After completing exercise, automatically returns to rehab plan
- [ ] Status shows as "✔ Completed" for finished exercises
- [ ] Progress bar shows updated percentage
- [ ] Click second exercise and verify it starts
- [ ] Verify all exercises save independently
- [ ] Check browser console for no errors
- [ ] Verify database has rehab_sessions records
- [ ] Test with multiple days in plan
- [ ] Test incomplete status (quality < 70%)

## Browser Console Debug Commands

```javascript
// Check rehab context
console.log(window._rehabContext);

// Check loaded sessions
console.log(rehabSessions);

// Force reload plan
loadRehabPlanData();

// Check exercise state
console.log(exerciseState);

// Check API response
fetch(`${API_BASE}/rehab-sessions`, {
    headers: {'Authorization': `Bearer ${authToken}`}
}).then(r => r.json()).then(console.log);
```

## Known Limitations

1. **Progress Bar Colors**: Currently uses teal-to-blue gradient, not customizable per day focus
2. **Session Lookup**: Uses exercise_name + day as unique key (case-sensitive)
3. **Target Reps**: Hardcoded to 10 when creating new session (should read from plan)
4. **Voice Assistant**: Removed from UI but voice functions may still be in script

## Future Enhancements

1. Add skip button to mark exercise as skipped
2. Show previous session reps/quality when resuming
3. Allow editing target reps per exercise
4. Add notes field for user feedback
5. Implement rest timer between sets
6. Add audio cues for form errors
7. Create PDF report of plan progress
8. Add percentage-based quality threshold per exercise

## Troubleshooting

### Status Not Updating
- Check browser console for API errors
- Verify user is authenticated (check authToken)
- Ensure backend `/rehab-sessions` endpoints are accessible
- Try hard refresh (Ctrl+Shift+R) to clear cache

### Exercise Button Not Working
- Check if `currentUser` and `authToken` are set
- Verify exercise name matches exactly (case-sensitive)
- Check browser console for JavaScript errors
- Ensure camera permissions are granted

### Progress Bar Not Showing
- Verify plan.days array has exercises
- Check if CSS styles loaded (inspect element)
- Ensure browser supports CSS flexbox (all modern browsers)

### Returns to Categories Instead of Plan
- Check if `window._rehabContext` is properly set before exercise
- Verify `previousPage` variable state
- Check browser console for navigation errors

## Support & Questions

For issues or questions about this feature:
1. Check browser console (F12) for error messages
2. Review data in Network tab when saving sessions
3. Verify database records with direct SQL query
4. Check auth token validity (localStorage → authToken)
