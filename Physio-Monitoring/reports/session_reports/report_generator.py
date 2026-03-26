import csv
import os
from datetime import datetime

class SessionReport:
    def __init__(self, exercise_name="Knee Flexion"):
        self.exercise_name = exercise_name
        self.start_time = datetime.now()
        self.total_frames = 0
        self.correct_frames = 0
        self.total_reps = 0

    def update(self, posture_ok, reps):
        """
        Update session statistics every frame
        """
        self.total_frames += 1
        if posture_ok:
            self.correct_frames += 1
        self.total_reps = reps

    def generate_report(self):
        """
        Generate CSV report and return summary stats
        """
        end_time = datetime.now()
        duration_sec = (end_time - self.start_time).seconds

        accuracy = 0.0
        if self.total_frames > 0:
            accuracy = (self.correct_frames / self.total_frames) * 100

        report_data = {
            "Exercise": self.exercise_name,
            "Start Time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (sec)": duration_sec,
            "Total Repetitions": self.total_reps,
            "Correct Frames": self.correct_frames,
            "Total Frames": self.total_frames,
            "Accuracy (%)": round(accuracy, 2)
        }

        os.makedirs("reports/session_reports", exist_ok=True)

        filename = f"session_{self.start_time.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join("reports/session_reports", filename)

        with open(filepath, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(report_data.keys())
            writer.writerow(report_data.values())

        # ✅ RETURN VALUES FOR STEP 10
        return filepath, duration_sec, self.total_reps, accuracy
