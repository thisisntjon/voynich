"""s123 calibration (dev): hue/chroma distributions on calibration pages OUTSIDE quire M only.
Usage: python tools/s123_calib.py <folio> [<folio> ...]  -> prints histograms; refuses any quire-M folio."""
import os, sys, sqlite3
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s123_colour import load_rgb, rgb_to_lab

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "vkb", "vkb.sqlite")

c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
for fol in sys.argv[1:]:
    q, = c.execute("SELECT quire FROM folios WHERE folio=?", (fol,)).fetchone()
    if q == "M":
        raise SystemExit("quire M is not allowed in calibration")
    p, = c.execute("SELECT image_path FROM panel_images WHERE folio=?", (fol,)).fetchone()
    L, a, b, C, h = rgb_to_lab(load_rgb(os.path.join(ROOT, p)))
    v = L > 35
    print(f"== {fol} ({q}) {p} px {L.size} L>35 {v.mean():.3f}")
    print("chroma pctiles (L>35):", np.percentile(C[v], [10, 50, 90, 99]).round(1))
    print("hue pctiles C<15 (parchment-ish):", np.percentile(h[v & (C < 15)], [10, 50, 90]).round(1))
    for cmin in (8, 12, 16, 20):
        m = v & (C >= cmin)
        hist, edges = np.histogram(h[m], bins=36, range=(0, 360))
        print(f"C>={cmin}: n={m.sum()} hue hist(10deg bins from 0):", " ".join(str(x) for x in hist))
    # chroma histogram of greenish/bluish hue pixels
    for lo, hi in ((100, 200), (200, 300)):
        m = v & (h >= lo) & (h < hi)
        hist, _ = np.histogram(C[m], bins=12, range=(0, 48))
        print(f"hue {lo}-{hi}: chroma hist(4-unit bins):", " ".join(str(x) for x in hist))
