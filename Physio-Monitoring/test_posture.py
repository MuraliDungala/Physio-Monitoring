from src.analysis.posture_analysis import check_knee_posture

angle = 45
status, message = check_knee_posture(angle)

print(status, message)
