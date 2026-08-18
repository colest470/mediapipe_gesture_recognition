import importlib
import mediapipe as mp
from . import constants
import pynput as pyn

# Some installations of MediaPipe (or different packaging) don't expose
# `mp.solutions` on the top-level package. Try to use the attribute when
# available, otherwise import a likely submodule and attach it so the rest
# of the code can assume `mp.solutions` exists.
try:
    _solutions = mp.solutions
except Exception:
    _solutions = None

if _solutions is None:
    for candidate in ("mediapipe.python.solutions", "mediapipe.solutions"):
        try:
            _solutions = importlib.import_module(candidate)
            # Attach to the top-level module for downstream code that expects it
            setattr(mp, "solutions", _solutions)
            break
        except Exception:
            _solutions = None

if _solutions is None:
    raise ImportError("cannot find MediaPipe 'solutions' module; please run with the project venv or install a MediaPipe package that provides 'solutions'.")

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
