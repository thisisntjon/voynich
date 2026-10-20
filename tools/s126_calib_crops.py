"""s126: validation crops from the calibration pages (outside quire M) at the s126 settings; negative-page check."""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s126_colour import load_rgb, rgb_to_lab, water_mask, densest_crops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = os.path.join(ROOT, "data/external/yale_scans/pages")
OUT = os.path.join(ROOT, "runs/s126/calib")
PAGES = ["019_9v", "004_2r", "157_85v_and_86r_foldout", "124_69r", "120_67r", "160_88r", "002_1r", "118_66r", "205_116v"]
for n in PAGES:
    assert not (134 <= int(n[:3]) <= 153)
    rgb = load_rgb(os.path.join(PG, n + ".jpg"))
    L, a, b, C, h = rgb_to_lab(rgb)
    g, bl = water_mask(L, C, h)
    print(n, "green px", int(g.sum()), "blue px", int(bl.sum()))
    vis = np.full(rgb.shape, 255, np.uint8); vis[g] = (0, 160, 0); vis[bl] = (0, 0, 220)
    im = Image.fromarray(np.concatenate([rgb, vis], axis=1)); im.thumbnail((2000, 900))
    im.save(os.path.join(OUT, f"s126mask_{n}.png"))
    for cls, mk in (("green", g), ("blue", bl)):
        if mk.sum() < 500:
            continue
        for i, ((y, x), arr) in enumerate(densest_crops(rgb, mk, k=2)):
            Image.fromarray(arr).save(os.path.join(OUT, f"cal_{cls}_{n}_{i}.png"))
            print("  crop", cls, n, i, "at", y, x)
