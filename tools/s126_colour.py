"""s126 segmentation: green as s123 (C >= 14, components >= 2000 px), blue recalibrated outside quire M
(tools/s126_calib.py, runs/s126/calib): L >= 25, C >= 4, hue 200-310, components >= 200 px (1/2 resolution).
Colour conversion reused from tools/s123_colour.py (imported, unchanged)."""
import os, sys
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s123_colour import load_rgb, rgb_to_lab, DEV  # noqa: F401

GREEN = dict(L_MIN=35.0, C_MIN=14.0, H_LO=105.0, H_HI=200.0, MIN_COMP=2000, CLOSE=5)
BLUE = dict(L_MIN=25.0, C_MIN=4.0, H_LO=200.0, H_HI=310.0, MIN_COMP=200, CLOSE=5)


def class_mask(L, C, h, p):
    raw = (L >= p["L_MIN"]) & (C >= p["C_MIN"]) & (h >= p["H_LO"]) & (h < p["H_HI"])
    closed = ndi.binary_closing(raw, structure=np.ones((p["CLOSE"], p["CLOSE"]), bool))
    lab, n = ndi.label(closed)
    s = np.bincount(lab.ravel())
    big = s >= p["MIN_COMP"]
    big[0] = False
    return big[lab] & raw


def water_mask(L, C, h):
    return class_mask(L, C, h, GREEN), class_mask(L, C, h, BLUE)


def densest_crops(rgb, mk, k=1, win=400, sep=400):
    """Up to k crops (scan | magenta overlay) at the densest windows of mask mk, windows at least sep px apart."""
    dens = ndi.uniform_filter(mk.astype(np.float32), 201)
    out = []
    for _ in range(k):
        if dens.max() <= 0:
            break
        y, x = np.unravel_index(int(np.argmax(dens)), dens.shape)
        y0, x0 = max(0, y - win // 2), max(0, x - win // 2)
        crop = rgb[y0:y0 + win, x0:x0 + win]
        ov = crop.copy()
        sub = mk[y0:y0 + win, x0:x0 + win]
        ov[sub] = (ov[sub] * 0.3 + np.array([255, 0, 255]) * 0.7).astype(np.uint8)
        out.append(((y, x), np.concatenate([crop, ov], axis=1)))
        dens[max(0, y - sep):y + sep, max(0, x - sep):x + sep] = 0
    return out
