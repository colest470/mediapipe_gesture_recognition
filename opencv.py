import cv2
import mediapipe as mp

def main():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error opening the camera!")
        return

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )

    try:
        fps = cam.get(cv2.CAP_PROP_FPS)
        print(f"FPS: {fps}")

        while True:
            ret, frame = cam.read()

            if not ret:
                print("Error capturing real time video!")
                break

            h, w = frame.shape[:2]

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )

            cv2.imshow(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cam.release()
        cv2.destroyAllWindows()
        hands.close()

if __name__ == "__main__":
    main()