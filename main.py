import src.constants as constants
import cv2
import time
import src.setup as setup
import src.landmark as landmark
import src.hud as hud
import src.wheel as wheel
import pynput as pyn

def main():
    cap = cv2.VideoCapture(constants.CAMERA_INDEX, cv2.CAP_ANY)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        return

    missing_steer_frames = 0
    missing_gas_frames = 0
    steer_state_text = "CENTER"
    gas_state_text = "NEUTRAL"
    current_angle = 0.0
    smoothed_angle = 0.0
    speed = 0.0
    SWAP_HANDS = constants.SWAP_HANDS
    DEAD_ZONE_DEG = constants.DEAD_ZONE_DEG

    prev_t = time.time()
    fps = 0.0
    start_t = time.time()
    snapshot_flash_until = 0.0

    try:
        while True:
            ret, frame = cap.read() # frame is a numpy array
            if not ret:
                break

            if constants.FLIP_CAMERA:
                frame = cv2.flip(frame, 1)

            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = setup.hands.process(rgb)

            now = time.time()
            dt = now - prev_t
            fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, dt))
            prev_t = now

            found_steer = False
            found_gas = False

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks, results.multi_handedness
                ):
                    raw_label = handedness.classification[0].label
                    label = landmark.on_screen_label(raw_label)
                    lm = hand_landmarks.landmark

                    if label == constants.STEERING_HAND:
                        found_steer = True
                        missing_steer_frames = 0
                        raw_angle = landmark.steering_tilt_angle(lm)
                        smoothed_angle = (constants.STEER_SMOOTHING * smoothed_angle
                                          + (1 - constants.STEER_SMOOTHING) * raw_angle)
                        angle = smoothed_angle
                        current_angle = angle

                        if angle > DEAD_ZONE_DEG:
                            setup.set_key(pyn.keyboard.Key.right, True)
                            setup.set_key(pyn.keyboard.Key.left, False)
                            steer_state_text = "RIGHT"
                        elif angle < -DEAD_ZONE_DEG:
                            setup.set_key(pyn.keyboard.Key.left, True)
                            setup.set_key(pyn.keyboard.Key.right, False)
                            steer_state_text = "LEFT"
                        else:
                            setup.set_key(pyn.keyboard.Key.left, False)
                            setup.set_key(pyn.keyboard.Key.right, False)
                            steer_state_text = "CENTER"

                        wheel_color = constants.COL_GREEN if steer_state_text == "CENTER" else constants.COL_AMBER
                        wheel.draw_wheel_on_hand(frame, lm, angle, w, h, wheel_color)

                    elif label == constants.GAS_BRAKE_HAND:
                        found_gas = True
                        missing_gas_frames = 0

                        if landmark.is_fist(lm):
                            setup.set_key(pyn.keyboard.Key.up, True)
                            setup.set_key(pyn.keyboard.Key.down, False)
                            gas_state_text = "ACCEL (fist)"
                            wheel.draw_fist_burst(frame, lm, w, h, constants.COL_GREEN)
                        elif landmark.is_one_finger(lm):
                            setup.set_key(pyn.keyboard.Key.down, True)
                            setup.set_key(pyn.keyboard.Key.up, False)
                            gas_state_text = "BRAKE (1 finger)"
                            wheel.draw_fist_burst(frame, lm, w, h, constants.COL_RED)
                        else:
                            setup.set_key(pyn.keyboard.Key.up, False)
                            setup.set_key(pyn.keyboard.Key.down, False)
                            gas_state_text = "NEUTRAL"

                        setup.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, setup.mp_hands.HAND_CONNECTIONS,
                            setup.mp_styles.get_default_hand_landmarks_style(),
                            setup.mp_styles.get_default_hand_connections_style(),
                        )

            if not found_steer:
                missing_steer_frames += 1
                if missing_steer_frames > constants.GRACE_FRAMES:
                    setup.set_key(pyn.keyboard.Key.left, False)
                    setup.set_key(pyn.keyboard.Key.right, False)
                    steer_state_text = "NO HAND"
                    current_angle = 0.0

            if not found_gas:
                missing_gas_frames += 1
                if missing_gas_frames > constants.GRACE_FRAMES:
                    setup.set_key(pyn.keyboard.Key.up, False)
                    setup.set_key(pyn.keyboard.Key.down, False)
                    gas_state_text = "NO HAND"

            # cosmetic speed simulation for the speedometer dial
            if gas_state_text.startswith("ACCEL"):
                speed = min(constants.MAX_SPEED, speed + constants.SPEED_ACCEL_RATE * dt)
            elif gas_state_text.startswith("BRAKE"):
                speed = max(0.0, speed - constants.SPEED_BRAKE_RATE * dt)
            else:
                speed = max(0.0, speed - constants.SPEED_DECAY_RATE * dt)

            hud.draw_dashboard(frame, steer_state_text, gas_state_text, current_angle,
                            SWAP_HANDS, fps, speed, now - start_t,
                            DEAD_ZONE_DEG, now - start_t)

            # snapshot flash feedback
            if now < snapshot_flash_until:
                flash = frame.copy()
                flash[:] = (255, 255, 255)
                cv2.addWeighted(flash, 0.25, frame, 0.75, 0, frame)

            cv2.imshow("Virtual Steering Wheel v3 - Gaming HUD", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("s"):
                SWAP_HANDS = not SWAP_HANDS
                wheel.wheerelease_all()
            elif key == ord("c"):
                fname = time.strftime("steering_snapshot_%Y%m%d_%H%M%S.png")
                cv2.imwrite(fname, frame)
                snapshot_flash_until = now + 0.15
                print(f"[SNAPSHOT] saved {fname}")
            elif key in (ord("+"), ord("=")):
                DEAD_ZONE_DEG = min(45, DEAD_ZONE_DEG + constants.SENSITIVITY_STEP)
            elif key == ord("-"):
                DEAD_ZONE_DEG = max(0, DEAD_ZONE_DEG - constants.SENSITIVITY_STEP)

    finally:
        setup.release_all()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()