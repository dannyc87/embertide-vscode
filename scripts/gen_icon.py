#!/usr/bin/env python3
"""Generates icon.png: a diagonal gradient sweeping cool -> ink black -> warm,
the same teal-to-ember identity as the palette itself. Requires Pillow + numpy
(not otherwise needed by this repo) -- run in a venv:

    python3 -m venv /tmp/iconenv && /tmp/iconenv/bin/pip install Pillow numpy
    /tmp/iconenv/bin/python3 scripts/gen_icon.py
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STOPS = [
    (0.00, (10, 214, 255)),    # Sky Flash
    (0.42, (0, 18, 25)),       # Ink Black
    (0.75, (238, 155, 0)),     # Golden Orange
    (1.00, (194, 54, 38)),     # Crimson Ember
]

SIZE = 512
OUT_SIZE = 128


def gradient_color(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return tuple(c0[i] + (c1[i] - c0[i]) * f for i in range(3))
    return STOPS[-1][1]


def main():
    ramp = np.array([gradient_color(t) for t in np.linspace(0, 1, 2 * SIZE - 1)], dtype=np.uint8)
    xx, yy = np.meshgrid(np.arange(SIZE), np.arange(SIZE))
    idx = xx + yy  # diagonal position, 0..2*SIZE-2
    img_arr = ramp[idx]
    img = Image.fromarray(img_arr, mode="RGB")
    img = img.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    out_path = os.path.join(ROOT, "icon.png")
    img.save(out_path)
    print("wrote", out_path, f"({OUT_SIZE}x{OUT_SIZE})")


if __name__ == "__main__":
    main()
