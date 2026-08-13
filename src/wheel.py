from . import landmark
from . import constants
import numpy as np
import cv2
import math

def draw_wheel_on_hand(frame, landmarks, angle_deg, w, h, glow_color):
    wrist = landmarks[landmark.LM.WRIST]
    cx, cy = int(wrist.x * w), int(wrist.y * h)
    span = landmark.hand_span_px(landmarks, w, h)
    radius = int(np.clip(span * constants.WHEEL_SCALE, constants.WHEEL_MIN_RADIUS, constants.WHEEL_MAX_RADIUS))

    overlay = frame.copy()
    cv2.circle(overlay, (cx, cy), radius + 10, glow_color, thickness=2)
    cv2.circle(overlay, (cx, cy), radius, (50, 50, 50), thickness=10)
    cv2.circle(overlay, (cx, cy), radius, glow_color, thickness=3)

    display_angle = max(-60, min(60, angle_deg))
    rad = math.radians(display_angle)

    for spoke_offset in (0, 120, 240):
        a = rad + math.radians(spoke_offset - 90)
        x2 = int(cx + radius * math.cos(a))
        y2 = int(cy + radius * math.sin(a))
        cv2.line(overlay, (cx, cy), (x2, y2), glow_color, thickness=7)
        cv2.line(overlay, (cx, cy), (x2, y2), (255, 255, 255), thickness=2)

    for deg in range(0, 360, 30):
        a = math.radians(deg) + rad
        gx = int(cx + radius * math.cos(a))
        gy = int(cy + radius * math.sin(a))
        cv2.circle(overlay, (gx, gy), 4, (255, 255, 255), thickness=-1)

    cv2.circle(overlay, (cx, cy), 16, glow_color, thickness=-1)
    cv2.circle(overlay, (cx, cy), 16, (255, 255, 255), thickness=2)

    cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)


def draw_fist_burst(frame, landmarks, w, h, color):
    wrist = landmarks[landmark.LM.WRIST]
    cx, cy = int(wrist.x * w), int(wrist.y * h)
    overlay = frame.copy()
    for deg in range(0, 360, 45):
        a = math.radians(deg)
        x1 = int(cx + 55 * math.cos(a))
        y1 = int(cy + 55 * math.sin(a))
        x2 = int(cx + 80 * math.cos(a))
        y2 = int(cy + 80 * math.sin(a))
        cv2.line(overlay, (x1, y1), (x2, y2), color, thickness=4)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
