import cv2

def draw_hud(frame, exercise, reps, angle, posture, quality=0):
    """
    Draw HUD with exercise info, reps, angle, posture, and quality score.
    
    Args:
        frame: video frame (numpy array)
        exercise: exercise name (str)
        reps: repetition count (int)
        angle: joint angle (float)
        posture: posture status (str, 'Correct' or 'Incorrect')
        quality: quality score 0-100 (int, default 0)
    """
    y = 30
    gap = 32

    cv2.putText(frame, f"Exercise: {exercise}", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    y += gap

    cv2.putText(frame, f"Reps: {reps}", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y += gap

    cv2.putText(frame, f"Angle: {int(angle)} deg", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y += gap

    color = (0, 255, 0) if posture == "Correct" else (0, 0, 255)
    cv2.putText(frame, f"Posture: {posture}", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    y += gap

    cv2.putText(frame, f"Quality: {int(quality)}%", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
