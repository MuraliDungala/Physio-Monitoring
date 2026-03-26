from src.repetition.rep_counter import RepetitionCounter

counter = RepetitionCounter(min_angle=60, max_angle=160)

angles = [170, 150, 120, 80, 60, 80, 120, 150, 170]

for a in angles:
    reps = counter.update(a, posture_ok=True)
    print(f"Angle: {a}, Reps: {reps}")
