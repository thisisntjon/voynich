"""s126 calibration (dev): blue chroma floor and min component size on pages OUTSIDE quire M only.
Usage: python tools/s126_calib.py  -> sweep table; masks to runs/s126/calib/."""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s123_colour import load_rgb, rgb_to_lab

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = "data/external/yale_scans/pages/"
POS = ["157_85v_and_86r_foldout", "124_69r", "120_67r", "160_88r"]
NEG = ["002_1r", "118_66r", "205_116v"]
for n in POS + NEG:
    assert not (134 <= int(n[:3]) <= 153), "quire M not allowed"
CB = [4, 5, 6, 7, 8, 9]
MC = [500, 1000, 2000]
L_MIN, H_SPLIT, H_B_HI = 35.0, 200.0, 310.0


def blue_mask(L, C, h, cmin, mincomp, close=5):
    b = (L >= L_MIN) & (C >= cmin) & (h >= H_SPLIT) & (h <= H_B_HI)
    closed = ndi.binary_closing(b, structure=np.ones((close, close), bool))
    lab, n = ndi.label(closed)
    s = np.bincount(lab.ravel()); big = s >= mincomp; big[0] = False
    return big[lab] & b


print("page kind " + " ".join(f"C{c}/m{m}" for c in CB for m in MC))
for n in POS + NEG:
    rgb = load_rgb(os.path.join(ROOT, PG + n + ".jpg"))
    L, a, b, C, h = rgb_to_lab(rgb)
    row = []
    for c in CB:
        for m in MC:
            row.append(int(blue_mask(L, C, h, c, m).sum()))
    print(n, "POS" if n in POS else "NEG", " ".join(str(x) for x in row), flush=True)
    raw = (L >= L_MIN) & (C >= 3) & (h >= 150) & (h <= H_B_HI)
    hh, _ = np.histogram(h[raw], bins=32, range=(150, 310))
    print("   hue hist C>=3 (5deg from 150):", " ".join(str(x) for x in hh))
    cc, _ = np.histogram(C[raw & (h >= H_SPLIT)], bins=12, range=(0, 24))
    print("   chroma hist hue>=200 (2-unit bins):", " ".join(str(x) for x in cc))
    tiles = [rgb]
    for c, m in ((5, 1000), (6, 1000), (7, 1000), (9, 2000)):
        k = blue_mask(L, C, h, c, m)
        v = np.full(rgb.shape, 255, np.uint8); v[k] = (0, 0, 220)
        tiles.append(v)
    im = Image.fromarray(np.concatenate(tiles, axis=1)); im.thumbnail((2000, 700))
    im.save(os.path.join(ROOT, "runs", "s126", "calib", f"bluemask_{n}.png"))
