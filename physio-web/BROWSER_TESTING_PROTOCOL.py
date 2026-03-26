#!/usr/bin/env python3
"""
BROWSER TESTING PROTOCOL
Complete guide for testing shoulder/knee fixes in the actual web interface
"""

def print_section(title):
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)

def main():
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 88 + "║")
    print("║" + "SHOULDER & KNEE EXERCISE FIX - BROWSER TESTING PROTOCOL".center(88) + "║")
    print("║" + " " * 88 + "║")
    print("╚" + "=" * 88 + "╝")
    
    print_section("WHAT WAS FIXED")
    print("""
✅ API Port Configuration:
   - Frontend was trying port 8001, backend is on 8000
   - FIXED: Updated API_BASE and WebSocket URL to port 8000

✅ Shoulder Angle Calculation:
   - OLD: Used virtual point above shoulder (incorrect)
   - NEW: Uses hip → shoulder → elbow (body reference approach)
   - This provides proper biomechanical measurement

✅ Landmark Requirements:
   - Shoulder exercises now include hip landmarks (23, 24)
   - Enables proper body axis reference for angle calculation

✅ Configuration Ranges:
   - Shoulder Flexion: 70°-140° range instead of 45°-120°
   - Knee Flexion: 45°-140° range (adjusted from 60°-140°)
   - These match the actual angle values from the new calculation method
    """)
    
    print_section("BEFORE YOU START TESTING")
    print("""
1. MAKE SURE BACKEND IS RUNNING:
   Terminal 1 (already running?):
   $ cd physio-web
   $ python -m uvicorn backend.app:app --reload
   
   Expected output: "Application startup complete"

2. MAKE SURE FRONTEND WEB SERVER IS RUNNING:
   Terminal 2 (already running?):
   $ cd physio-web/frontend
   $ python -m http.server 3000
   
   Expected output: "Serving HTTP on 0.0.0.0 port 3000"

3. Browser open at: http://localhost:3000
    """)
    
    print_section("CRITICAL: HARD REFRESH BROWSER CACHE")
    print("""
You MUST do a hard refresh to load the updated script.js with fixes:

Windows/Linux:  Ctrl + Shift + R
Mac:            Cmd + Shift + R

Do NOT just press F5 or Ctrl+R - this won't clear script.js cache!

Alternative if hard refresh doesn't work:
- Press F12 (open Developer Tools)
- Right-click refresh button → "Empty cache and hard refresh"
- Or go to DevTools Settings → Network → "Disable cache"
    """)
    
    print_section("TEST 1: SHOULDER FLEXION EXERCISE")
    print("""
PURPOSE: Verify shoulder angle calculation and rep counting work

STEPS:
1. In browser: Select "Shoulder Flexion" from exercise list
2. Click: "Start Camera" button
3. Wait: Camera initializes (should show your video)
4. Action: Slowly raise arm from side to overhead (full range motion)
   - Start with arm at rest by your side
   - Gradually raise arm forward and up
   - Complete one full cycle: down → up → down
   
MONITORING:
- Open Browser Console: Press F12 → click "Console" tab
- Look for messages like:
  ✓ "shoulderLeft: 90.5°" (or similar number)
  ✓ "Phase: down" → "Phase: up" (transitions)
  ✓ "✅ Rep counted! Total: 1" (when completing cycle)

EXPECTED RESULTS:
✅ Angle values: 70° → 140° (arm resting to overhead)
✅ Phase transitions: "down" when arm down, "up" when arm raised
✅ Rep count: Increments to 1 when you complete full motion
✅ Quality score: Should display with ROM, Smoothness, Control %
✅ Posture feedback: Shows alignment tips

WHAT TO LOOK FOR IN CONSOLE:
┌──────────────────────────────────────────────────────────┐
│ [Exercise] Shoulder Flexion detected                     │
│ Landmarks visible:                                       │
│   ✓ Hip (23, 24): VISIBLE                                │
│   ✓ Shoulder (11, 12): VISIBLE                           │
│   ✓ Elbow (13, 14): VISIBLE                              │
│ shoulderLeft: 88.3° optimal: 70-140 phase: down         │
│ Phase Detection: READY to count                          │
│ [Rep Counter] Threshold crossed: down → up               │
│ ✅ Rep counted! Total: 1                                 │
│ Quality Score: ROM: 95% Smoothness: 87% Control: 91%    │
│ Overall Score: 91% (EXCELLENT)                          │
│ Posture: Keep shoulders relaxed, core engaged           │
└──────────────────────────────────────────────────────────┘

TROUBLESHOOTING:
Problem: "Landmarks visible: ✗ Hip not detected"
→ Solution: Raise camera higher to show your hips/waist

Problem: "angle: 0°" or "angle: NaN"
→ Solution: Make sure hips, shoulder, elbow visible in camera

Problem: "Phase: down" but no transitions happening
→ Solution: Move arm slower and through full range

Problem: "✗ Quality: Not enough visible" appears
→ Solution: Ensure entire arm and hip visible in camera frame
    """)
    
    print_section("TEST 2: KNEE FLEXION EXERCISE")
    print("""
PURPOSE: Verify knee angle calculation works for leg exercises

STEPS:
1. In browser: Select "Knee Flexion" from exercise list
2. Click: "Start Camera" button
3. Wait: Camera initializes
4. Action: Sit down so you can show your leg
   - Start with leg straight out
   - Slowly bend knee (bring foot toward butt)
   - Complete one full cycle: extended → flexed → extended

MONITORING:
- Keep Browser Console open (F12 → Console)
- Look for messages like:
  ✓ "kneeLeft: 140.2°" (or similar number)
  ✓ "Phase: extended" → "Phase: flexed"
  ✓ "✅ Rep counted! Total: 1"

EXPECTED RESULTS:
✅ Angle values: 140° (straight) → 45° (bent) → 140° (straight)
✅ Phase transitions: "extended" when straight, "flexed" when bent
✅ Rep count: Increments when you complete full motion
✅ Quality score: Displays properly
✅ Posture feedback: Shows alignment tips for proper form

WHAT TO LOOK FOR IN CONSOLE:
┌──────────────────────────────────────────────────────────┐
│ [Exercise] Knee Flexion detected                         │
│ Landmarks visible:                                       │
│   ✓ Hip (23, 24): VISIBLE                                │
│   ✓ Knee (25, 26): VISIBLE                               │
│   ✓ Ankle (27, 28): VISIBLE                              │
│ kneeLeft: 142.1° optimal: 45-140 phase: extended        │
│ Phase Detection: READY to count                          │
│ [Rep Counter] Threshold crossed: extended → flexed       │
│ ✅ Rep counted! Total: 1                                 │
│ Quality Score: ROM: 92% Smoothness: 89% Control: 88%    │
│ Overall Score: 90% (EXCELLENT)                          │
│ Posture: Keep knee aligned over foot, core engaged      │
└──────────────────────────────────────────────────────────┘

TROUBLESHOOTING:
Problem: Angle shows 180° constantly
→ Solution: Bend your leg more through fuller range

Problem: "kneeLeft: 0°" or "NaN"
→ Solution: Make sure hip, knee, ankle visible in camera

Problem: Phase not detecting transitions
→ Solution: Move slowly through FULL range (straight to bent)

Problem: "Quality: Not enough visible"
→ Solution: Ensure entire leg visible in camera frame
    """)
    
    print_section("TEST 3: ELBOW FLEXION (FOR COMPARISON - ALREADY WORKING)")
    print("""
PURPOSE: Verify the fixes don't break the already-working elbow exercise

STEPS:
1. In browser: Select "Elbow Flexion" from exercise list
2. Click: "Start Camera"
3. Action: Raise and lower arm (bend and straighten elbow)

EXPECTED: Everything works perfectly (as before)
✅ Angle shows: 60°-140° range
✅ Phase transitions: "extended" → "flexed"
✅ Reps count
✅ Quality scores display

If elbow suddenly STOPS working after the fix:
→ Something went wrong - contact support immediately
- The angle calculation order is: shoulder(11,12) → elbow(13,14) → wrist(15,16)
- These landmarks weren't changed, so it should always work
    """)
    
    print_section("REPORTING RESULTS")
    print("""
After testing, please report:

MINIMUM REPORT (if working):
────────────────────────────────────────────────────────────
✅ Shoulder Flexion: Reps counted, angle showing, quality score displaying
✅ Knee Flexion: Reps counted, angle showing, quality score displaying
✅ Elbow Flexion: Still working (unchanged)
────────────────────────────────────────────────────────────

DETAILED REPORT (if having issues):
────────────────────────────────────────────────────────────
❌ Exercise: [Shoulder Flexion / Knee Flexion / Other]
❌ Issue: [Cannot detect landmarks / No angle showing / No rep counting / etc]
❌ Console Messages: [Copy any error messages from F12 console]
❌ Angle Values: [What numbers appear in console? 0? NaN? Wrong range?]
❌ Phase Messages: [Does it show phase transitions?]
❌ Screenshots: [If possible, capture browser console showing the error]
────────────────────────────────────────────────────────────

COMMON ISSUES & QUICK FIXES:

1. "Nothing appears to work"
   → Did you hard refresh? (Ctrl+Shift+R) Not F5!
   → Are backend/frontend servers actually running?
   
2. "Only Elbow works, Shoulder/Knee don't"
   → Landmark visibility issue - make sure hips visible
   → Hard refresh to load new script.js
   
3. "Elbow stopped working"
   → Something went wrong - the elbow calculation wasn't changed
   → Need to debug the changes made
   
4. "Angles show wrong numbers"
   → May need to adjust EXERCISE_CONFIG ranges
   → Report the actual numbers you see in console
   
5. "Browser console shows red errors"
   → Copy the error message exactly and report it
   → These tell us what went wrong
    """)
    
    print_section("TIMELINE & NEXT STEPS")
    print("""
YOUR TESTING → REPORT RESULTS → FIXES APPLIED → FINAL DEPLOYMENT

Step 1: NOW (Testing - you do this)
        - Hard refresh browser
        - Test shoulder exercise
        - Test knee exercise
        - Note any issues
        
Step 2: REPORT (5-10 minutes)
        - Tell us what works/what doesn't
        - Provide console messages if issues
        - Share angle values you see

Step 3: ADJUSTMENT (if needed - 5-15 minutes)
        - If angles are wrong range: adjust EXERCISE_CONFIG
        - If landmarks not detected: debug visibility
        - If phase not detecting: adjust thresholds

Step 4: RE-TEST (if adjusted - 5-10 minutes)
        - Hard refresh again
        - Test the fixes again
        - Confirm working before final deployment

Step 5: PRODUCTION READY
        - System ready for real patients
        - Full physiotherapy monitoring active
        - Real-time rep counting, quality scoring, posture feedback
    """)
    
    print_section("QUESTIONS BEFORE YOU START?")
    print("""
❓ "What's a 'hard refresh'?"
→ It's Ctrl+Shift+R (not Ctrl+R). Forces browser to download script.js again.

❓ "My angle values look wrong"
→ That's OK - we may need to adjust configuration. Report the numbers!

❓ "Do I need to move slowly?"
→ Yes, moderately slow movement helps the system detect phase transitions.

❓ "What if I can't see my hips in the camera?"
→ Raise the camera position - it needs to see your waist/hip area.

❓ "How fast should I do the exercises?"
→ Normal rehabilitation pace - about 1-2 seconds per rep.

❓ "Can I test standing up?"
→ Shoulder: Yes, stand up. Knee: Sit down to show leg better.
    """)
    
    print_section("YOU'RE READY - START TESTING!")
    print("""
Remember the workflow:
1. Hard refresh browser (Ctrl+Shift+R)
2. Open console (F12)
3. Test each exercise
4. Watch for angle values and rep counting
5. Report results

LET'S GO! 🚀
    """)

if __name__ == '__main__':
    main()
