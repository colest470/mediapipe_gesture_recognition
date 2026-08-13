import mediapipe as mp
from . import constants
import pynput as pyn

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=constants.MIN_DET_CONF,
    min_tracking_confidence=constants.MIN_TRACK_CONF,
)

keyboard = pyn.keyboard.Controller()

key_state = { pyn.keyboard.Key.left: False, pyn.keyboard.Key.right: False, pyn.keyboard.Key.up: False, pyn.keyboard.Key.down: False}

def set_key(key, should_be_down):
    if should_be_down and not key_state[key]:
        keyboard.press(key)
        key_state[key] = True
    elif not should_be_down and key_state[key]:
        keyboard.release(key)
        key_state[key] = False


def release_all():
    for k in list(key_state.keys()):
        set_key(k, False)
