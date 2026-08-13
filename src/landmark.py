from . import setup
from . import constants
import math

LM = setup.mp_hands.HandLandmark


def on_screen_label(handedness_label: str) -> str:
    if constants.SWAP_HANDS:
        return "Left" if handedness_label == "Right" else "Right"
    return handedness_label

def steering_tilt_angle(landmarks) -> float:
    """Angle of the line across the knuckles (index MCP -> pinky MCP), folded
    so that a level/flat hand always reads as ~0 degrees.

    atan2(dy, dx) on this line gives an angle near 0 deg when the hand is
    flat with the palm facing the camera, but near +-180 deg when the hand
    is flat with the *back* of the hand facing the camera (which is the
    natural way people hold a "steering wheel" grip). That +-180 baseline
    was being read as a real tilt, so the wheel looked like it defaulted to
    RIGHT even when the hand was straight. Since the knuckle line has no
    inherent direction, we fold anything past +-90 deg back by 180 deg so
    both hand orientations agree on what "flat" (0 deg, forward) means.
    """
    idx_mcp = landmarks[LM.INDEX_FINGER_MCP]
    pinky_mcp = landmarks[LM.PINKY_MCP]
    dx = pinky_mcp.x - idx_mcp.x
    dy = pinky_mcp.y - idx_mcp.y
    angle = math.degrees(math.atan2(dy, dx))

    if angle > 90:
        angle -= 180
    elif angle <= -90:
        angle += 180

    return angle


def finger_is_extended(landmarks, tip_idx, pip_idx) -> bool:
    return landmarks[tip_idx].y < landmarks[pip_idx].y


def is_fist(landmarks) -> bool:
    fingers = [
        (LM.INDEX_FINGER_TIP, LM.INDEX_FINGER_PIP),
        (LM.MIDDLE_FINGER_TIP, LM.MIDDLE_FINGER_PIP),
        (LM.RING_FINGER_TIP, LM.RING_FINGER_PIP),
        (LM.PINKY_TIP, LM.PINKY_PIP),
    ]
    return all(not finger_is_extended(landmarks, tip, pip) for tip, pip in fingers)


def is_one_finger(landmarks) -> bool:
    index_up = finger_is_extended(landmarks, LM.INDEX_FINGER_TIP, LM.INDEX_FINGER_PIP)
    middle_down = not finger_is_extended(landmarks, LM.MIDDLE_FINGER_TIP, LM.MIDDLE_FINGER_PIP)
    ring_down = not finger_is_extended(landmarks, LM.RING_FINGER_TIP, LM.RING_FINGER_PIP)
    pinky_down = not finger_is_extended(landmarks, LM.PINKY_TIP, LM.PINKY_PIP)
    return index_up and middle_down and ring_down and pinky_down


def hand_span_px(landmarks, w, h) -> float:
    idx_mcp = landmarks[LM.INDEX_FINGER_MCP]
    pinky_mcp = landmarks[LM.PINKY_MCP]
    dx = (pinky_mcp.x - idx_mcp.x) * w
    dy = (pinky_mcp.y - idx_mcp.y) * h
    return math.hypot(dx, dy)

