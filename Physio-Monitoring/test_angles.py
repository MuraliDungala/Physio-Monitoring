from src.analysis.angle_calculation import knee_angle

# Dummy normalized coordinates
hip = (0.5, 0.3)
knee = (0.5, 0.5)
ankle = (0.5, 0.8)

angle = knee_angle(hip, knee, ankle)
print("Knee Angle:", int(angle))
