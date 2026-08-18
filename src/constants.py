"""
Based on the idea from jayesh-cmd/virtual-steering-wheel, extended with:

1. RIGHT hand only  -> steering (tilt right hand left/right, like a wheel).
   Hand held flat/level = CENTER (forward), tilt right = RIGHT,
   tilt left = LEFT. Works correctly whether your palm or the back of
   your hand faces the camera.
2. LEFT  hand fist -> accelerator (UP arrow held)
3. LEFT  hand 1 finger (index only) -> brake/reverse (DOWN arrow held)
4. Steering wheel graphic anchored to your actual right hand (wrist),
   sized to your hand, rotates with your tilt.
5. Full-window cyberpunk racing dashboard: corner HUD brackets, scanlines,
   vignette, animated glowing title, speedometer dial, gear indicator,
   side status panels.
6. Live sensitivity tuning: press +/- to widen/narrow the steering dead
   zone without editing the code.
7. Snapshot: press C to save the current HUD frame as a PNG.
8. Session timer shown in the status panel.

Press Q to quit, S to toggle hand swap.
"""

import numpy as np
import mediapipe as mp
from pynput.keyboard import Controller as KeyboardController

CAMERA_INDEX = 0
FLIP_CAMERA = True
DEAD_ZONE_DEG = 10
GRACE_FRAMES = 8
MIN_DET_CONF = 0.7
MIN_TRACK_CONF = 0.5

STEERING_HAND = "Right"
GAS_BRAKE_HAND = "Left"
SWAP_HANDS = False

WHEEL_MIN_RADIUS = 40
WHEEL_MAX_RADIUS = 110
WHEEL_SCALE = 1.8            # hand-span multiplier (lower = smaller wheel)

SENSITIVITY_STEP = 2         # degrees changed per +/- key press
STEER_SMOOTHING = 0.4        # 0 = no smoothing, closer to 1 = smoother/laggier

# Neon theme colours (BGR)
COL_CYAN = (0, 0, 0)
COL_MAGENTA =  COL_CYAN #(200, 40, 255)
COL_GREEN = COL_CYAN #(90, 0, 0)
COL_RED = COL_CYAN #(60, 60, 255)
COL_AMBER = COL_CYAN #(0, 190, 255)
COL_YELLOW = COL_CYAN #(0, 230, 255)
COL_TEXT = COL_CYAN #(235, 235, 235)
COL_DIM = COL_CYAN #(110, 110, 110)

MAX_SPEED = 220          # purely cosmetic speedometer top value
SPEED_ACCEL_RATE = 90    # units/sec while accelerating
SPEED_BRAKE_RATE = 160   # units/sec while braking
SPEED_DECAY_RATE = 55    # units/sec natural decay when neutral