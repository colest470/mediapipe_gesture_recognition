import cv2
import numpy as np
import mediapipe as mp
import panel

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

            cv2.imshow("Gaming HUD", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cam.release()
        cv2.destroyAllWindows()
        hands.close()

def pic_to_img():
    img = cv2.imread("/home/mark/Pictures/Screenshot_2026-03-18_16_53_49.png")
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray, img_bin = cv2.threshhold(gray, 128, 225, cv2.THRESH_BINARY)
    gray = cv2.bitwise_not(img, img_bin)

    kernel = np.ones((2, 1), np.uint8)
    img = cv2.erode(gray, kernel, iterations=1)
    img = cv2.dilate(img, kernel, iterations=1)

    text = pytesseract.image_to_string(img)

    panel.fit(f"text", border_style="white")

if __name__ == "__main__":
    main()