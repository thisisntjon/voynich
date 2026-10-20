"""s115-A1 text masking for blind image classification (no transliteration, no word boxes used).

Image-only. Detection at half scan resolution: ink = pixels darker than a local median background by
INK_D grey levels. Ink connected components that are glyph-sized (height <= GLYPH_H px, width <=
GLYPH_W px at half res), not touching paint (paint dilated NEAR_R px, enclosed holes included) and not part of a long line
(vertical/horizontal opening, LINE_LEN px) are painted with the local background. The result is
downscaled so the long side is LONG (single page) or LONG_FOLD (wide/multi-panel scans) and written to
data/anchor_A1/masked/<stem>.png (never overwritten). Known cost: unpainted fine hatching that is
glyph-sized (for example some unpainted root hatching or small unpainted outlines) can be thinned too.
Usage: python s115_a1_mask.py [stem ...]   (no args = all images). S115_MASK_OUT overrides the output dir
(used for parameter tuning only, written to a scratch directory).
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "data", "external", "yale_scans", "pages")
OUT = os.environ.get("S115_MASK_OUT") or os.path.join(ROOT, "data", "anchor_A1", "masked")
LONG, LONG_FOLD = 1200, 1600
INK_D = 22            # ink: background minus luminance above this (grey levels)
PAINT_DS = 0.16       # paint: HSV saturation above parchment saturation + PAINT_DS
NEAR_R = 12           # paint dilation (px, half res); holes of the dilated paint are protected too
PAINT_OPEN = 9         # paint must survive a 9x9 opening (removes saturated thin ink strokes)
GLYPH_H, GLYPH_W = 70, 300   # glyph component max height / width (px, half res)
LINE_LEN = 70         # horizontal opening length marking long straight drawn lines, kept
INK_WEAK = 12         # weaker ink threshold used only to find long lines and arcs
BIG_WEAK = 150        # weak component size (px, half res, both axes) counted as drawing
ARC_LEN = 45          # oriented line-opening length (px, half res) for arcs and stems


# circular-diagram images (policy M0): folios.section in {A, Z, C} with a mapped scan, plus the
# unmapped foldout scans of quires 67-72 and 85-86 (astronomical/cosmological foldouts)
M0_STEMS = {"113_57v", "124_69r", "128_71r", "132_73r", "133_73v",
            "120_67r", "121_67v", "122_68r", "123_68v", "125_69v_and_70r", "126_70v_part",
            "127_70v_part", "129_71v_and_72r", "130_72v_part", "131_72v_part",
            "154_85r_part_p8586", "155_85r_part_86v_part_p8586", "156_86v_part_p8586",
            "157_85v_and_86r_foldout"}


def line_fp(n, ang):
    """1-px line footprint of length n at angle ang (degrees, 0 = horizontal)."""
    t = np.deg2rad(ang)
    xs = np.round(np.cos(t) * (np.arange(n) - n // 2)).astype(int)
    ys = np.round(np.sin(t) * (np.arange(n) - n // 2)).astype(int)
    fp = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1), bool)
    fp[ys - ys.min(), xs - xs.min()] = True
    return fp


def keep_text(stem, W, H):
    """Policy M0 (downscale only, no glyph erasure) for circular-diagram images, where the drawn
    figures and circles are unpainted outlines in the same pen as the text and component erasure
    removes them (checked on f73r and f69v). Decided from folios.section (A, Z, C) and the
    file name of unmapped foldout scans, never from text."""
    return stem in M0_STEMS


def mask_one(stem):
    out = os.path.join(OUT, stem + ".png")
    if os.path.exists(out):
        return stem + "	exists"
    im = Image.open(os.path.join(SRC, stem + ".jpg")).convert("RGB")
    W, H = im.size
    long_ = LONG_FOLD if (W > 1.3 * H or max(W, H) > 5000) else LONG
    if keep_text(stem, W, H):
        s = long_ / max(W, H)
        img = im.resize((round(W * s), round(H * s)), Image.LANCZOS)
        img.save(out)
        return f"{stem}	M0	{img.size[0]}x{img.size[1]}	0	0.000"
    im = im.resize((W // 2, H // 2), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    L = a.mean(2)
    h, w = L.shape
    sm = ndi.median_filter(L[::4, ::4], size=9)
    bgL = np.asarray(Image.fromarray(sm).resize((w, h), Image.BILINEAR))
    ink = (bgL - L) > INK_D
    hsv = np.asarray(im.convert("HSV")).astype(np.float32)
    hue, sat = hsv[..., 0] * (360.0 / 255.0), hsv[..., 1] / 255.0
    core = (slice(h // 6, 5 * h // 6), slice(w // 6, 5 * w // 6))
    ps = np.median(sat[core])
    # paint: (a) hues away from the parchment/ink band 15-45 deg (greens, blues), (b) saturated reds,
    # (c) any strongly saturated broad area (tan/yellow washes), which must survive a PAINT_OPEN opening
    hue_paint = (((hue >= 45) & (hue <= 300) & (sat > 0.12)) |
                 (((hue < 15) | (hue > 300)) & (sat > 0.35))) & (L > 40)
    hue_paint = ndi.binary_opening(hue_paint, structure=np.ones((3, 3)))
    wash = ndi.binary_opening((sat > ps + PAINT_DS) & (L > 50), structure=np.ones((PAINT_OPEN, PAINT_OPEN)))
    paint = hue_paint | wash
    near = ndi.binary_fill_holes(ndi.binary_dilation(paint, iterations=NEAR_R))
    # long drawn lines and arcs (stems, rims, compass circles): openings of a weaker ink mask with
    # 1-px line footprints of length ARC_LEN at angles 20..160 deg (near-horizontal excluded, where text
    # baselines run), plus straight horizontal runs of LINE_LEN on the normal ink mask
    weak = (bgL - L) > INK_WEAK
    longl = ndi.binary_opening(ink, structure=np.ones((1, LINE_LEN)))
    for ang in range(20, 161, 10):
        longl |= ndi.binary_opening(weak, structure=line_fp(ARC_LEN, ang))
    # weak-ink components spanning more than BIG_WEAK px in both directions are drawings (outline
    # figures, compass circles joined by faint strokes); their strong ink is kept
    wl, wn = ndi.label(weak, structure=np.ones((3, 3)))
    big = np.zeros(wn + 1, bool)
    for i, sl in enumerate(ndi.find_objects(wl), 1):
        if sl is not None and sl[0].stop - sl[0].start > BIG_WEAK and sl[1].stop - sl[1].start > BIG_WEAK:
            big[i] = True
    longl |= big[wl]
    longl = ndi.binary_dilation(longl, iterations=2)
    lab, n = ndi.label(ink, structure=np.ones((3, 3)))
    objs = ndi.find_objects(lab)
    erase = np.zeros_like(ink)
    nt = 0
    for i, sl in enumerate(objs, 1):
        if sl is None:
            continue
        bh, bw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if bh > GLYPH_H or bw > GLYPH_W:
            continue
        m = lab[sl] == i
        if (near[sl] & m).any() or (longl[sl] & m).any():
            continue
        erase[sl] |= m
        nt += 1
    erase = ndi.binary_dilation(erase, iterations=2) & ~paint & ~longl
    # fill: local background colour (median of non-ink pixels, coarse grid)
    fill = np.empty_like(a)
    for k in range(3):
        ch = a[..., k].copy()
        ch[ink | erase] = np.nan
        g = ch[::4, ::4]
        g = np.where(np.isnan(g), np.nanmedian(g), g)
        g = ndi.median_filter(g, size=7)
        fill[..., k] = np.asarray(Image.fromarray(g).resize((w, h), Image.BILINEAR))
    res = a.copy()
    res[erase] = fill[erase]
    img = Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))
    s = long_ / max(w, h)
    img = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
    img.save(out)
    return f"{stem}	M1	{img.size[0]}x{img.size[1]}	{nt}	{erase.mean():.3f}"


def _init():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


if __name__ == "__main__":
    from multiprocessing import Pool
    os.makedirs(OUT, exist_ok=True)
    stems = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(SRC) if f.endswith(".jpg"))
    _init()
    print("stem	policy	size	components_erased	erased_frac", flush=True)
    with Pool(4, initializer=_init) as pool:
        for line in pool.imap(mask_one, stems):
            print(line, flush=True)
