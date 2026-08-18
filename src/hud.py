import numpy as np
import cv2
from . import constants
import math

def apply_vignette(frame, strength=0.55):
    h, w = frame.shape[:2]
    kx = cv2.getGaussianKernel(w, w * 0.6)
    ky = cv2.getGaussianKernel(h, h * 0.6)
    mask = ky @ kx.T
    mask = mask / mask.max()
    mask = (mask * (1 - strength) + strength)
    out = frame.astype(np.float32)
    for c in range(3):
        out[:, :, c] *= mask
    return np.clip(out, 0, 255).astype(np.uint8)


def draw_scanlines(frame, alpha=0.08, gap=4):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    for y in range(0, h, gap):
        cv2.line(overlay, (0, y), (w, y), (0, 0, 0), 1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_corner_brackets(frame, color, length=45, thick=4, margin=14):
    h, w = frame.shape[:2]
    pts = [(margin, margin), (w - margin, margin), (margin, h - margin), (w - margin, h - margin)]
    dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    for (x, y), (dx, dy) in zip(pts, dirs):
        cv2.line(frame, (x, y), (x + dx * length, y), color, thick)
        cv2.line(frame, (x, y), (x, y + dy * length), color, thick)


def glow_text(frame, text, org, font_scale, color, thickness=2, glow=6):
    overlay = frame.copy()
    cv2.putText(overlay, text, org, cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness + glow, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness, cv2.LINE_AA)


def rounded_panel(frame, x, y, w_, h_, color=(20, 12, 8), alpha=0.55, border=None):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w_, y + h_), color, thickness=-1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    if border:
        cv2.rectangle(frame, (x, y), (x + w_, y + h_), border, thickness=2)


def status_pill(frame, x, y, label, value, color, active):
    dot_color = color if active else (80, 80, 80)
    cv2.circle(frame, (x, y), 7, dot_color, thickness=-1)
    cv2.circle(frame, (x, y), 7, (255, 255, 255), thickness=1)
    cv2.putText(frame, label, (x + 16, y + 5), cv2.FONT_HERSHEY_PLAIN, 0.55, constants.COL_TEXT, 1, cv2.LINE_AA)
    (tw, _), _ = cv2.getTextSize(value, cv2.FONT_HERSHEY_PLAIN, 0.6, 2)
    cv2.putText(frame, value, (x + 210 - tw, y + 5), cv2.FONT_HERSHEY_PLAIN, 0.6, dot_color, 2, cv2.LINE_AA)


def draw_speedometer(frame, cx, cy, radius, speed, max_speed, color):
    # """Big semicircular speedometer dial, bottom-center of the window."""
    # cv2.ellipse(frame, (cx, cy), (radius, radius), 0, 180, 360, (55, 55, 55), 14)
    # frac = min(1.0, speed / max_speed)
    # end_angle = 180 + int(180 * frac)
    # dial_color = color if frac < 0.85 else constants.COL_RED
    # cv2.ellipse(frame, (cx, cy), (radius, radius), 0, 180, end_angle, dial_color, 14)
    #
    # # tick marks
    # for i in range(0, 11):
    #     a = math.radians(180 + i * 18)
    #     x1 = int(cx + (radius - 20) * math.cos(a))
    #     y1 = int(cy + (radius - 20) * math.sin(a))
    #     x2 = int(cx + (radius - 5) * math.cos(a))
    #     y2 = int(cy + (radius - 5) * math.sin(a))
    #     cv2.line(frame, (x1, y1), (x2, y2), (150, 150, 150), 2)
    #
    # # needle
    # needle_angle = math.radians(180 + 180 * frac)
    # nx = int(cx + (radius - 25) * math.cos(needle_angle))
    # ny = int(cy + (radius - 25) * math.sin(needle_angle))
    # cv2.line(frame, (cx, cy), (nx, ny), constants.COL_YELLOW, 3)
    # cv2.circle(frame, (cx, cy), 8, constants.COL_YELLOW, -1)
    #
    # glow_text(frame, f"{int(speed)}", (cx - 38, cy - 18), 1.1, (255, 255, 255), 2, glow=4)
    # cv2.putText(frame, "KM/H", (cx - 26, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, constants.COL_DIM, 1, cv2.LINE_AA)
    pass


def draw_gear_indicator(frame, x, y, gear, color):
    rounded_panel(frame, x - 35, y - 35, 70, 70, color=(15, 15, 15), alpha=0.6, border=color)
    (tw, th), _ = cv2.getTextSize(gear, cv2.FONT_HERSHEY_PLAIN, 1.1, 3)
    cv2.putText(frame, gear, (x - tw // 2, y + th // 2),
                cv2.FONT_HERSHEY_PLAIN, 1.1, color, 3, cv2.LINE_AA)


def draw_dashboard(frame, steer_state, gas_state, angle, swap_on, fps, speed, t,
                    dead_zone, elapsed):
    h, w = frame.shape[:2]

    frame[:] = apply_vignette(frame, strength=0.75)
    draw_scanlines(frame, alpha=0.06)

    pulse = 0.5 + 0.5 * math.sin(t * 3)
    title_color = tuple(int(c * (0.6 + 0.4 * pulse)) for c in constants.COL_CYAN)
    draw_corner_brackets(frame, title_color)

    # top title bar
    rounded_panel(frame, w // 2 - 190, 8, 380, 40, color=(10, 10, 10), alpha=0.5, border=title_color)
    glow_text(frame, "VIRTUAL RACING HUD", (w // 2 - 172, 36), 0.75, title_color, 2, glow=4)

    # left status panel
    rounded_panel(frame, 14, 60, 260, 156, color=(10, 10, 10), alpha=0.55, border=constants.COL_CYAN)
    cv2.putText(frame, "STATUS", (28, 82), cv2.FONT_HERSHEY_PLAIN, 0.55, constants.COL_CYAN, 1, cv2.LINE_AA)

    steer_color = constants.COL_GREEN if steer_state == "CENTER" else constants.COL_AMBER if steer_state != "NO HAND" else constants.COL_RED
    gas_color = constants.COL_GREEN if gas_state.startswith("ACCEL") else constants.COL_RED if gas_state.startswith("BRAKE") else constants.COL_DIM

    status_pill(frame, 34, 110, "STEER", steer_state, steer_color, steer_state != "NO HAND")
    status_pill(frame, 34, 138, "PEDAL", gas_state, gas_color, gas_state != "NO HAND")
    status_pill(frame, 34, 166, "SWAP-S", "ON" if swap_on else "OFF", constants.COL_MAGENTA, swap_on)

    mins, secs = divmod(int(elapsed), 60)
    cv2.putText(frame, f"SESSION {mins:02d}:{secs:02d}", (34, 194),
                cv2.FONT_HERSHEY_PLAIN, 0.5, constants.COL_DIM, 1, cv2.LINE_AA)

    # top-right decorative steering angle gauge
    gauge_cx, gauge_cy = w - 80, 100
    cv2.ellipse(frame, (gauge_cx, gauge_cy), (55, 55), 0, 135, 405, (60, 60, 60), 10)
    frac = min(1.0, abs(angle) / 60.0)
    end_angle = 135 + int(270 * frac)
    cv2.ellipse(frame, (gauge_cx, gauge_cy), (55, 55), 0, 135, end_angle, constants.COL_CYAN, 10)
    cv2.putText(frame, f"{int(abs(angle))}", (gauge_cx - 20, gauge_cy + 8),
                cv2.FONT_HERSHEY_PLAIN, 0.8, constants.COL_TEXT, 2, cv2.LINE_AA)
    cv2.putText(frame, "DEG", (gauge_cx - 16, gauge_cy + 28), cv2.FONT_HERSHEY_PLAIN, 0.4, constants.COL_DIM, 1, cv2.LINE_AA)

    # bottom-center speedometer (removed)
    # draw_speedometer(frame, w // 2, h - 15, 95, speed, constants.MAX_SPEED, constants.COL_CYAN)

    # gear indicator next to speedometer
    gear = "D" if gas_state.startswith("ACCEL") else "R" if gas_state.startswith("BRAKE") else "N"
    gear_color = constants.COL_GREEN if gear == "D" else constants.COL_RED if gear == "R" else constants.COL_DIM
    draw_gear_indicator(frame, w // 2 + 150, h - 60, gear, gear_color)

    # bottom-left FPS + hints
    cv2.putText(frame, f"FPS {fps:.0f}  |  DEADZONE {dead_zone}deg", (14, h - 15),
                cv2.FONT_HERSHEY_PLAIN, 0.5, constants.COL_DIM, 1, cv2.LINE_AA)
    cv2.putText(frame, "Q QUIT  S SWAP  C SNAPSHOT  +/- SENSITIVITY", (14, h - 34),
                cv2.FONT_HERSHEY_PLAIN, 0.45, constants.COL_DIM, 1, cv2.LINE_AA)

