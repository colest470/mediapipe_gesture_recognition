import cv2
import numpy as np
import mediapipe as mp
import pytesseract

def main():
    # cam = cv2.VideoCapture(0)
    # if not cam.isOpened():
    #     print("Error opening the camera!")
    #     return

    # mp_hands = mp.solutions.hands
    # mp_drawing = mp.solutions.drawing_utils
    # hands = mp_hands.Hands(
    #     static_image_mode=False,
    #     max_num_hands=2,
    #     min_detection_confidence=0.7,
    #     min_tracking_confidence=0.5
    # )

    try:
        # fps = cam.get(cv2.CAP_PROP_FPS)
        # print(f"FPS: {fps}")

        # while True:
        #     ret, frame = cam.read()

        #     if not ret:
        #         print("Error capturing real time video!")
        #         break

        #     h, w = frame.shape[:2]

        #     frame = cv2.flip(frame, 1)

        #     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #     results = hands.process(rgb)

        #     if results.multi_hand_landmarks:
        #         for hand_landmarks in results.multi_hand_landmarks:
        #             mp_drawing.draw_landmarks(
        #                 frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
        #             )

        #     cv2.imshow("Gaming HUD", frame)

        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

        pass

    finally:
        # cam.release()
        # cv2.destroyAllWindows()
        # hands.close()
        
        pic_to_img()

def pic_to_img():
    try:
        img_path = "/home/mark/Pictures/Screenshot_2026-03-18_16_53_49.png"
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Error: Could not load image from {img_path}")
            return
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        _, img_bin = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        gray = cv2.bitwise_not(img_bin)
        
        kernel = np.ones((2, 1), np.uint8)
        img_eroded = cv2.erode(gray, kernel, iterations=1)
        img_dilated = cv2.dilate(img_eroded, kernel, iterations=1)
        
        text = pytesseract.image_to_string(img_dilated)
        
        print(text)
        
    except Exception as e:
        print(f"Error in pic_to_img: {e}")

if __name__ == "__main__":
    main()