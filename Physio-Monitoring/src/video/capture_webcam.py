import cv2

def capture_webcam():
    # Open default webcam (0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Webcam not accessible")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        # Display the frame
        cv2.imshow("Camera Feed - Press Q to Exit", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run directly
if __name__ == "__main__":
    capture_webcam()
