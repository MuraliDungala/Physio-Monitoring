from src.feedback.audio_feedback import AudioFeedback
import time

audio = AudioFeedback()

audio.speak("Correct posture")
time.sleep(3)
audio.speak("Excessive knee flexion")
