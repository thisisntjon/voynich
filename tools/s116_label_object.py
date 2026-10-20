#!/usr/bin/env python
"""s116 (D-066 (w)), A2 label-to-object: does the text of a Voynich label resemble the text of other labels whose drawn
objects look alike?  Partial Mantel of label-text similarity against object-image similarity over every registrable
label in the book.  A foothold test, not a translation.

QUESTION (frozen).  Rivals: labels name (or describe) the object they sit on (content-bearing; H-06/H-14/H-16), so
picture-similar objects carry text-similar labels beyond page, bifolio, quire, adjacency, section, hand, label-length
and crop-size confounds; vs labels carry no object information beyond those confounds (H-05/H-07, or a reference too
indirect for this test).

UNITS (built by --build-units; written to runs/s116/units.tsv, hashed in the stub; no text-image statistic is computed)
  Label locus = ZL3b (data/ZL3b-n.txt, vparse.load) unit whose code starts with 'L', on a page that has a voynichese
  word-box file (tools/boxes.py), with >= 1 token string-matched to a box by tools/boxes.align_page.  Label point =
  mean centre of its matched boxes (box-canvas px).  Label tokens: ZL words made only of a-z (others dropped); a locus
  with no such token is dropped.
  Box -> scan registration (box files are on a ~600 px reference canvas; scans data/external/yale_scans/pages).
    Candidate scans: the scan whose label is exactly the folio (e.g. '88r' for f88r), else every scan whose label
    contains the folio number+side as a whole token (e.g. f70v2 -> '70v (part)' x2; f72r1 -> '71v and 72r').
    Ink map: scan decoded at 1/4 (JPEG draft), grey L, background = median filter (size 9 on a 1/16 grid) upsampled,
    ink = bg - L > INK_T; ink components kept only if glyph-sized (bbox <= GH x GW px at 1/4).  Template: box rects
    +1/n_box, gaps inside the box extent -1/n_gap (s78 REG-A template); score = in-box minus in-gap ink density.
    Coarse search on the 1/8 map over isotropic scale SCALES (scan px per box px) x anisotropy ANIS, then a refine on
    the 1/4 map (scale x 0.985..1.015 step 0.005, anisotropy x {0.99, 1, 1.01}, offset within +-64 scan px).  The
    candidate scan with the highest refined score wins.
    Acceptance (label-free): the boxes are split at their median y into a top and a bottom half (each >= MIN_HALF
    boxes); each half is registered independently by the same full search on the winning scan; the page is accepted
    when both half-transforms map the four corners of the full box extent within REG_TOL scan px of the full transform
    and the full scale is not at the coarse search edge.  REG_TOL set before freezing from a registration-only check
    against s78 REG-A on 15 s78 herbal pages (3 gross misregistrations had half deviations >= 195 px; pages within
    ~120 px of s78 had half deviations <= 71 px); no text or similarity statistic was involved.
  Object: work image = scan at 1/4.  Drawing mask D = (ink (bg - L > INK_T, unfiltered) or paint (HSV saturation >
    page median + PAINT_DS, V > V_MIN)) inside the page area (rows/cols mostly V > 0.35), minus every word box of the
    page (all units) padded PAD_BOX box px (the label's own boxes PAD_OWN), binary closing CLOSE_IT iterations;
    components of D with bbox >= MIN_COMP work px in both directions are drawings (word-sized ink is smaller).
    The object = the drawing component nearest the label point (pixel distance), if within R_SEARCH box px.  Crop =
    bbox of that component's pixels within R_CROP box px of the label point, padded 5 %, at full scan resolution;
    pixels outside the component (dilated 3 work px) and inside any padded word box are painted with the crop's
    parchment median (pixels neither ink, paint nor box).  Crop -> padded square (parchment colour) -> 224 px bicubic;
    saved runs/s116/crops/<uid>.png, sha256 in the unit table.  Unit without a component in range: dropped (counted).
  Covariates from ZL3b page headers: section $I, quire $Q, bifolio ($Q, $B), hand $H, page index in ZL3b order.

TEXT
  Transliterations ZL3b (primary), RF1b (data/external/voynich-nu-ivtff/RF1b-er.txt), IT2a (.../IT2a-n.txt) through
  vparse.load(path=...); a unit's text in RF1b/IT2a = the same locus (page, line number, unit code); missing -> empty.
  Tokens: a-z only.  Segmenter 1 (primary): SlotSegmenter (scoreboard/metrics_new.py, defaults) fitted on all P-unit
  tokens of that transliteration; label doc = cores of its tokens.  Segmenter 2: raw whole word (ZL3b).
  Text similarity = tf-idf cosine (s115-A0 tfidf_sim, imported unchanged); empty doc -> similarity 0.

PICTURES.  DINOv2 ViT-B/14 CLS + SigLIP B/16-224, 8 views, as s48/s78/s115-A0 (Embedder imported unchanged from
  tools/s115_a0_real_link_control.py, CUDA when available); picture similarity = mean of the two per-model cosine
  matrices z-scored over the off-diagonal upper triangle (A0 picture_matrices).

STATISTIC.  Partial Mantel r (A0 partial_mantel, imported unchanged): Pearson r of picture and text similarity residuals
  after OLS on [1, same page, same bifolio, same quire, adjacent page (|page index diff| == 1), same section, same hand,
  same ZL unit code, |label glyph-length diff|, |token-count diff|, |log crop-area diff|, plus one same-level indicator
  per A2-eligible A1 category (below)].  Null: NPERM permutations of the text matrix within section x quire strata;
  one-sided p = (1 + #{r* >= r}) / (NPERM + 1).  CI: delete-one-page jackknife, r +- 1.96 SE.
  A1/A1b categories only as strata: the run reads data/anchor_A1b/kappa_cross_model.txt line 'A2-eligible: ...'.
  For each eligible category c, the unit's level = data/anchor_A1/labels.tsv value of the unit's scan image (NA and
  DISAGREE:* = no level); a pair indicator same_c = both have the same level enters the covariates, and r per level
  of each eligible category with >= 30 units is printed (descriptive).  If none is eligible, section (already a
  stratum and a covariate) is the stratum.  Without the A1b file the real run refuses to start.

POWER GATE (--power; A0 real-herbal corpus, read-only, A0 functions imported unchanged; written before freezing)
  A0 units (820 captioned units, runs/s115_a0/20261018T203952_embed.npz).  Each caption is cut to label length: k drawn
  from the empirical token-count distribution of the s116 units, min(k, caption length) tokens kept at random (order
  kept); then A0 NOISE.  N = s116 unit count (capped at 820).  Two samplers: uniform units, and whole A0 pages added in
  random order until N (within-page clustering, like Voynich labels).  R_POW subsamples each, NPERM_POW permutations,
  A0 covariates and ms x side strata.  Shuffled control: captions deranged within strata before cutting.
  POWER_PASS = both samplers power (share p < 0.05) >= 0.80 and both shuffled shares <= 0.10.  The real run refuses to
  start unless runs/s116/power.txt says POWER_PASS=True.  The smaller of the two powers is POWER used in NULL below.

FIXTURE (--fixture; synthetic, Voynich-shaped: the real unit table's pages, sections, quires, bifolios, hands, unit
  codes and token counts; no real text or image).  150 subjects; label words = subject name with random prefix/suffix
  from small sets; 2 x 64-d image embeddings = 0.9 subject + 0.8 quire drift + 0.5 page + N(0, 1).  Quire drift is
  also put in the text (quire-specific prefix) in both fixtures.  Planted: label subject = object subject.  No-link:
  label subject independent.  R_FIX = 50 each, NPERM_FIX permutations.  FIXTURE_PASS = planted share p < 0.01 >= 0.80
  and no-link share p < 0.05 <= 0.10.  The real run refuses to start unless runs/s116/fixture.txt says
  FIXTURE_PASS=True.

DECISION RULE (frozen; printed CALL line)
  LINK  if p < 0.01 on ZL3b cores, and p < 0.05 on RF1b cores and on IT2a cores, and p < 0.05 under the second
        segmenter (ZL3b raw whole word).
  NULL  if POWER >= 0.9 and p >= 0.05 in all four, and the jackknife 95 % CI upper bound of r < 0.05 in all four.
  INCONCLUSIVE otherwise.
  Reported beside the call, not part of it: r and p with same-quire pairs removed (ZL3b cores); real-data shuffled-text
  control (text deranged within strata); per-section r; per-category-level r.

PROCESS.  python -I tools/s116_label_object.py --build-units | --power | --fixture | --real.  The real run verifies
  the stub (s116_label_object.prereg.sha256: this script, runs/s116/units.tsv), the power and fixture files, every
  crop sha256, sets BelowNormal priority, <= 4 CPU threads, GPU when free, writes results_s116_<YYYYmmddTHHMMSS>.txt
  (never overwrites) and runs/s116/<stamp>_*.npz.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scoreboard"))
import boxes as bm  # noqa: E402
import vparse  # noqa: E402

STUB = ROOT / "s116_label_object.prereg.sha256"
RUNS = ROOT / "runs" / "s116"
UNITS = RUNS / "units.tsv"
PAGES = RUNS / "pages.tsv"
CROPS = RUNS / "crops"
SCANS = ROOT / "data" / "external" / "yale_scans" / "pages"
A0_SCRIPT = ROOT / "tools" / "s115_a0_real_link_control.py"
A0_EMBED = ROOT / "runs" / "s115_a0" / "20261018T203952_embed.npz"
A1_LABELS = ROOT / "data" / "anchor_A1" / "labels.tsv"
A1_IMAGES = ROOT / "data" / "anchor_A1" / "images.tsv"
A1B_KAPPA = ROOT / "data" / "anchor_A1b" / "kappa_cross_model.txt"
TRANSLITS = [("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
             ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"),
             ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt")]

SEED = 116_20261018
# registration
INK_T = 18
GH, GW = 30, 90
SCALES = np.arange(2.6, 6.51, 0.04)
ANIS = (0.94, 0.97, 1.0, 1.03, 1.06)
MIN_HALF = 8
REG_TOL = 120.0
# object
PAINT_DS, V_MIN = 0.10, 0.18
PAD_BOX, PAD_OWN = 3, 6
CLOSE_IT = 2
MIN_COMP = 25
R_SEARCH, R_CROP = 80.0, 150.0
# statistics
ALPHA_LINK, ALPHA = 0.01, 0.05
NPERM = 9999
NPERM_POW, R_POW = 499, 200
NPERM_FIX, R_FIX = 199, 50
POWER_MIN, SHUFFLE_MAX, POWER_NULL, CI_MAX = 0.80, 0.10, 0.90, 0.05
LETTERS = "abcdefghijklmnopqrstuvwxyz"

try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
except Exception:  # noqa: BLE001
    Image = None


def load_a0():
    spec = importlib.util.spec_from_file_location("s115_a0", A0_SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def set_low_priority():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:  # noqa: BLE001
        pass


def clock() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


# ======================================================================================================== metadata
HDR_RE = re.compile(r"^<(f\w+)>\s+<!(.*)>")
VAR_RE = re.compile(r"\$(\w)=(\w+)")


def page_meta():
    meta, order = {}, []
    for raw in (ROOT / "data" / "ZL3b-n.txt").read_text(encoding="ascii", errors="replace").splitlines():
        m = HDR_RE.match(raw)
        if m:
            v = dict(VAR_RE.findall(m.group(2)))
            meta[m.group(1)] = v
            order.append(m.group(1))
    for i, p in enumerate(order):
        meta[p]["idx"] = i
    return meta


def az_tokens(words):
    return [w for w in words if w and re.fullmatch(r"[a-z]+", w)]


# ======================================================================================================== registration
def scan_index():
    return json.loads((SCANS.parent / "pages_index.json").read_text(encoding="utf-8"))


def candidate_scans(page, idx):
    m = re.match(r"f(\d+)([rv])", page)
    if not m:
        return []
    key = m.group(1) + m.group(2)
    exact = [r["file"] for r in idx if r["label"].strip() == key and page == "f" + key]
    if exact:
        return exact
    return [r["file"] for r in idx if re.search(r"(?<!\d)" + key + r"(?!\d)", r["label"])]


def _work(path, red=4):
    im = Image.open(path)
    W0, H0 = im.size
    im.draft("RGB", (W0 // red, H0 // red))
    im = im.convert("RGB")
    return im, im.size[0] / W0, (W0, H0)


def _ink(Lgrey):
    from scipy import ndimage as ndi
    sm = ndi.median_filter(Lgrey[::4, ::4], size=9)
    bg = np.asarray(Image.fromarray(sm).resize(Lgrey.shape[::-1], Image.BILINEAR))
    return (bg - Lgrey) > INK_T


def glyph_ink(ink):
    from scipy import ndimage as ndi
    lab, n = ndi.label(ink, structure=np.ones((3, 3)))
    keep = np.zeros(n + 1, bool)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is not None and (sl[0].stop - sl[0].start) <= GH and (sl[1].stop - sl[1].start) <= GW:
            keep[i] = True
    return keep[lab].astype(np.float32)


def _template(bx, kx, ky):
    mh = int(max(b["y"] + b["h"] for b in bx) * ky) + 2
    mw = int(max(b["x"] + b["w"] for b in bx) * kx) + 2
    M = np.zeros((mh, mw), np.float32)
    for b in bx:
        M[int(b["y"] * ky):int((b["y"] + b["h"]) * ky) + 1, int(b["x"] * kx):int((b["x"] + b["w"]) * kx) + 1] = 1
    x0 = int(min(b["x"] for b in bx) * kx)
    y0 = int(min(b["y"] for b in bx) * ky)
    ext = np.zeros_like(M, bool)
    ext[y0:, x0:] = True
    nb, ng = M.sum(), (ext & (M == 0)).sum()
    Tm = np.zeros_like(M)
    Tm[M > 0] = 1 / nb
    Tm[ext & (M == 0)] = -1 / max(ng, 1)
    return Tm


def _search(T, f, bx, scales, anis, near=None, win=64.0):
    from scipy.signal import fftconvolve
    best = None
    for s in scales:
        for a in anis:
            Tm = _template(bx, s * f, s * a * f)
            mh, mw = Tm.shape
            P = np.zeros((T.shape[0] + 2 * mh, T.shape[1] + 2 * mw), np.float32)
            P[mh:mh + T.shape[0], mw:mw + T.shape[1]] = T
            if near is not None:
                cx, cy = int(round(near[0] * f)) + mw, int(round(near[1] * f)) + mh
                w = int(round(win * f))
                bx0, by0 = max(0, cx - w), max(0, cy - w)
                sub = P[by0:min(P.shape[0], cy + w + mh), bx0:min(P.shape[1], cx + w + mw)]
            else:
                bx0 = by0 = 0
                sub = P
            if sub.shape[0] < mh or sub.shape[1] < mw:
                continue
            r = fftconvolve(sub, Tm[::-1, ::-1], mode="valid")
            k = int(np.argmax(r))
            yy, xx = divmod(k, r.shape[1])
            c = (float(r.flat[k]), float(s), float(s * a), (xx + bx0 - mw) / f, (yy + by0 - mh) / f)
            if best is None or c[0] > best[0]:
                best = c
    return best


def _register_maps(T4, T8, fx, bx):
    c = _search(T8, fx / 2, bx, SCALES, ANIS)
    if c is None:
        return None
    c2 = _search(T4, fx, bx, c[1] * np.arange(0.985, 1.0151, 0.005), [c[2] / c[1] * k for k in (0.99, 1.0, 1.01)],
                 near=(c[3], c[4]), win=64.0)
    c2 = c2 or c
    return dict(score=c2[0], sx=c2[1], sy=c2[2], ox=c2[3], oy=c2[4], coarse_sx=c[1])


def _maps(path):
    im, fx, _ = _work(path)
    L = np.asarray(im.convert("L"), np.float32)
    T4 = glyph_ink(_ink(L))
    h2, w2 = T4.shape[0] // 2 * 2, T4.shape[1] // 2 * 2
    T8 = T4[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).mean((1, 3))
    return T4, T8, fx


def corner_dev(A, B, bx):
    xs = [min(b["x"] for b in bx), max(b["x"] + b["w"] for b in bx)]
    ys = [min(b["y"] for b in bx), max(b["y"] + b["h"] for b in bx)]
    return max(max(abs(A["sx"] * u + A["ox"] - (B["sx"] * u + B["ox"])) for u in xs),
               max(abs(A["sy"] * v + A["oy"] - (B["sy"] * v + B["oy"])) for v in ys))


def register_page(page):
    """Returns dict(page, scan, ok, why, sx, sy, ox, oy, score, dev_top, dev_bot)."""
    set_low_priority()
    bx = bm.load_boxes(page)
    cands = candidate_scans(page, scan_index())
    out = dict(page=page, scan="", ok=False, why="", sx=0, sy=0, ox=0, oy=0, score=0, dev_top=-1, dev_bot=-1)
    if not bx or not cands:
        out["why"] = "no boxes" if not bx else "no candidate scan"
        return out
    best = None
    for fn in cands:
        T4, T8, fx = _maps(SCANS / fn)
        r = _register_maps(T4, T8, fx, bx)
        if r and (best is None or r["score"] > best[0]["score"]):
            best = (r, fn, T4, T8, fx)
    r, fn, T4, T8, fx = best
    out.update(scan=fn, sx=r["sx"], sy=r["sy"], ox=r["ox"], oy=r["oy"], score=r["score"])
    ymed = float(np.median([b["cy"] for b in bx]))
    top = [b for b in bx if b["cy"] <= ymed]
    bot = [b for b in bx if b["cy"] > ymed]
    if len(top) < MIN_HALF or len(bot) < MIN_HALF:
        out["why"] = f"halves too small ({len(top)}/{len(bot)})"
        return out
    rt, rb = _register_maps(T4, T8, fx, top), _register_maps(T4, T8, fx, bot)
    dt_, db = corner_dev(r, rt, bx), corner_dev(r, rb, bx)
    out.update(dev_top=dt_, dev_bot=db)
    edge = r["coarse_sx"] <= SCALES[0] + 1e-9 or r["coarse_sx"] >= SCALES[-1] - 1e-9
    out["ok"] = bool(dt_ <= REG_TOL and db <= REG_TOL and not edge)
    out["why"] = f"half devs {dt_:.0f}/{db:.0f} px (tol {REG_TOL:.0f})" + (", scale at search edge" if edge else "")
    return out


# ======================================================================================================== objects
def hsv_sv(arr):
    hsv = np.asarray(Image.fromarray(arr).convert("HSV")).astype(np.float32) / 255.0
    return hsv[..., 1], hsv[..., 2]


def page_area(v):
    bright = v > 0.35
    rows = np.where(bright.mean(1) > 0.5)[0]
    cols = np.where(bright.mean(0) > 0.5)[0]
    m = np.zeros_like(v, bool)
    if len(rows) < 10 or len(cols) < 10:
        m[:] = True
    else:
        m[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1] = True
    return m


def box_rects(bx, R, pad):
    return [(R["sx"] * (b["x"] - pad) + R["ox"], R["sy"] * (b["y"] - pad) + R["oy"],
             R["sx"] * (b["x"] + b["w"] + pad) + R["ox"], R["sy"] * (b["y"] + b["h"] + pad) + R["oy"]) for b in bx]


def objects_for_page(page, R, labels):
    """labels: list of dict(uid, pts=[(cx, cy) box px], own=[box dicts]).  Writes crops; returns {uid: info}."""
    from scipy import ndimage as ndi
    set_low_priority()
    bx = bm.load_boxes(page)
    path = SCANS / R["scan"]
    im, fx, (W0, H0) = _work(path)
    a = np.asarray(im)
    L = a.astype(np.float32).mean(2)
    s, v = hsv_sv(a)
    area = page_area(v)
    valid = v > V_MIN
    paint = (s > float(np.median(s[valid & area])) + PAINT_DS) & valid
    ink = _ink(L)
    boxm = np.zeros(L.shape, bool)
    h, w = L.shape
    for x0, y0, x1, y1 in box_rects(bx, R, PAD_BOX):
        boxm[max(0, int(y0 * fx)):max(0, int(np.ceil(y1 * fx))), max(0, int(x0 * fx)):max(0, int(np.ceil(x1 * fx)))] = True
    out = {}
    full = None
    for lab in labels:
        own = np.zeros_like(boxm)
        for x0, y0, x1, y1 in box_rects(lab["own"], R, PAD_OWN):
            own[max(0, int(y0 * fx)):max(0, int(np.ceil(y1 * fx))), max(0, int(x0 * fx)):max(0, int(np.ceil(x1 * fx)))] = True
        D = (ink | paint) & area & ~boxm & ~own
        D = ndi.binary_closing(D, iterations=CLOSE_IT) & area & ~boxm & ~own
        cx = np.mean([p[0] for p in lab["pts"]])
        cy = np.mean([p[1] for p in lab["pts"]])
        px, py = (R["sx"] * cx + R["ox"]) * fx, (R["sy"] * cy + R["oy"]) * fx
        rs = R_SEARCH * R["sx"] * fx
        rc = R_CROP * R["sx"] * fx
        y0w, y1w = max(0, int(py - rc)), min(h, int(py + rc) + 1)
        x0w, x1w = max(0, int(px - rc)), min(w, int(px + rc) + 1)
        if y1w <= y0w or x1w <= x0w:
            out[lab["uid"]] = dict(ok=False, why="label point off scan")
            continue
        sub = D[y0w:y1w, x0w:x1w]
        comp, n = ndi.label(sub, structure=np.ones((3, 3)))
        yy, xx = np.mgrid[y0w:y1w, x0w:x1w]
        dist = np.hypot(yy - py, xx - px)
        inr = dist <= rc
        best, bd = None, None
        for i, sl in enumerate(ndi.find_objects(comp), 1):
            if sl is None:
                continue
            m = (comp[sl] == i)
            if (sl[0].stop - sl[0].start) < MIN_COMP or (sl[1].stop - sl[1].start) < MIN_COMP:
                # the component may be larger than the window; test its size inside the window only
                continue
            d = float(dist[sl][m].min())
            if d <= rs and (bd is None or d < bd):
                best, bd = i, d
        if best is None:
            out[lab["uid"]] = dict(ok=False, why="no drawing component in range")
            continue
        cm = (comp == best) & inr
        ys, xs = np.where(cm)
        by0, by1, bx0, bx1 = ys.min() + y0w, ys.max() + y0w + 1, xs.min() + x0w, xs.max() + x0w + 1
        ph, pw = 0.05 * (by1 - by0), 0.05 * (bx1 - bx0)
        X0, Y0 = max(0, int((bx0 - pw) / fx)), max(0, int((by0 - ph) / fx))
        X1, Y1 = min(W0, int(np.ceil((bx1 + pw) / fx))), min(H0, int(np.ceil((by1 + ph) / fx)))
        if full is None:
            full = Image.open(path).convert("RGB")
        crop = np.asarray(full.crop((X0, Y0, X1, Y1))).copy()
        ch, cw = crop.shape[:2]
        # object mask at full res: component (dilated 3 work px) resized
        keep_w = np.zeros((h, w), bool)
        keep_w[y0w:y1w, x0w:x1w] = ndi.binary_dilation(cm, iterations=3)
        keep_w &= ~boxm & ~own
        kw = keep_w[int(Y0 * fx):int(np.ceil(Y1 * fx)), int(X0 * fx):int(np.ceil(X1 * fx))]
        keep = np.asarray(Image.fromarray(kw.astype(np.uint8) * 255).resize((cw, ch), Image.NEAREST)) > 0
        bgsel = ~np.asarray(Image.fromarray((D | boxm | own)[int(Y0 * fx):int(np.ceil(Y1 * fx)),
                                                            int(X0 * fx):int(np.ceil(X1 * fx))].astype(np.uint8) * 255)
                            .resize((cw, ch), Image.NEAREST)).astype(bool)
        parch = np.median(crop[bgsel & ~keep], axis=0) if (bgsel & ~keep).sum() >= 50 else np.median(crop.reshape(-1, 3), 0)
        crop[~keep] = parch.astype(np.uint8)
        side = max(ch, cw)
        can = Image.new("RGB", (side, side), tuple(int(t) for t in parch))
        can.paste(Image.fromarray(crop), ((side - cw) // 2, (side - ch) // 2))
        can = can.resize((224, 224), Image.BICUBIC)
        CROPS.mkdir(parents=True, exist_ok=True)
        cp = CROPS / f"{lab['uid']}.png"
        can.save(cp)
        out[lab["uid"]] = dict(ok=True, why="", lx=px / fx, ly=py / fx, x0=X0, y0=Y0, x1=X1, y1=Y1,
                               crop_area=(X1 - X0) * (Y1 - Y0), comp_px=int(cm.sum()), dist=bd / fx,
                               crop_sha=sha(cp))
    return out


def label_loci():
    recs = vparse.load()
    pages, _ = bm.align_all(recs)
    out = defaultdict(list)
    for page, pl in pages.items():
        for r, ln in pl:
            if not r["unit"].startswith("L"):
                continue
            toks = az_tokens(r["words"])
            if not toks:
                continue
            m = [t for t in ln["tokens"] if t["matched"]]
            if not m:
                continue
            uid = f"{page}.{r['line']}.{r['unit']}"
            own = [dict(x=t["cx"] - t["w"] / 2, y=t["cy"] - t["h"] / 2, w=t["w"], h=t["h"]) for t in ln["tokens"]]
            out[page].append(dict(uid=uid, page=page, line=r["line"], unit=r["unit"], toks=toks,
                                  pts=[(t["cx"], t["cy"]) for t in m], own=own))
    return out


def _page_job(args):
    page, labels = args
    R = register_page(page)
    objs = objects_for_page(page, R, labels) if R["ok"] else {}
    return R, objs


def build_units():
    set_low_priority()
    if UNITS.exists():
        sys.exit(f"{UNITS} exists; never overwritten")
    RUNS.mkdir(parents=True, exist_ok=True)
    meta = page_meta()
    loci = label_loci()
    n_all = sum(len(v) for v in loci.values())
    print(f"{clock()} label loci with >= 1 matched box and >= 1 a-z token: {n_all} on {len(loci)} pages", flush=True)
    from multiprocessing import Pool
    jobs = sorted(loci.items(), key=lambda kv: kv[0])
    regs, objs = [], {}
    with Pool(3, initializer=set_low_priority) as pool:
        for R, o in pool.imap_unordered(_page_job, jobs):
            regs.append(R)
            objs.update(o)
            print(f"{clock()} {R['page']} {R['scan']} ok={R['ok']} {R['why']} score {R['score']:.3f} "
                  f"s {R['sx']:.3f}/{R['sy']:.3f}; objects {sum(v['ok'] for v in o.values())}/{len(o)}", flush=True)
    regs.sort(key=lambda r: r["page"])
    with open(PAGES, "x", encoding="utf-8", newline="\n") as f:
        cols = ["page", "scan", "ok", "why", "sx", "sy", "ox", "oy", "score", "dev_top", "dev_bot"]
        f.write("\t".join(cols) + "\n")
        for R in regs:
            f.write("\t".join(f"{R[c]:.4f}" if isinstance(R[c], float) else str(R[c]) for c in cols) + "\n")
    regok = {R["page"]: R for R in regs if R["ok"]}
    rows, drop = [], Counter()
    for page, labs in jobs:
        for lab in labs:
            if page not in regok:
                drop["page not registered"] += 1
                continue
            o = objs.get(lab["uid"])
            if not o or not o["ok"]:
                drop[o["why"] if o else "no object result"] += 1
                continue
            mt = meta[page]
            rows.append(dict(uid=lab["uid"], page=page, line=lab["line"], unit=lab["unit"], section=mt.get("I", "?"),
                             quire=mt.get("Q", "?"), bifolio=mt.get("Q", "?") + "-" + mt.get("B", "?"),
                             hand=mt.get("H", "?"), lang=mt.get("L", "?"), page_idx=mt["idx"],
                             zl_text=".".join(lab["toks"]), n_tok=len(lab["toks"]),
                             n_glyph=sum(len(t) for t in lab["toks"]), scan=regok[page]["scan"],
                             lx=round(o["lx"], 1), ly=round(o["ly"], 1), x0=o["x0"], y0=o["y0"], x1=o["x1"], y1=o["y1"],
                             crop_area=o["crop_area"], comp_px=o["comp_px"], dist=round(o["dist"], 1),
                             crop_sha=o["crop_sha"]))
    rows.sort(key=lambda r: (r["page_idx"], r["line"], r["uid"]))
    cols = list(rows[0].keys())
    with open(UNITS, "x", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    by = Counter(r["section"] for r in rows)
    print(f"{clock()} pages registered {len(regok)}/{len(regs)}; units {len(rows)} by section {dict(sorted(by.items()))}; "
          f"dropped {dict(drop)}", flush=True)


def read_units():
    with open(UNITS, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


# ======================================================================================================== text
def translit_docs(units):
    """{(name, seg): list of docs} for ZL3b/RF1b/IT2a cores and ZL3b raw words."""
    from metrics_new import SlotSegmenter
    out = {}
    for name, path in TRANSLITS:
        recs = vparse.load(path=path)
        loc = {(r["page"], int(r["line"]), r["unit"]): az_tokens(r["words"]) for r in recs}
        fit = [t for r in recs if r["unit"].startswith("P") for t in az_tokens(r["words"])]
        seg = SlotSegmenter(fit)
        toks = [loc.get((u["page"], int(u["line"]), u["unit"]), []) for u in units]
        out[(name, "core")] = [[seg.segment(t)[1] for t in d] for d in toks]
        if name == "ZL3b":
            out[(name, "word")] = toks
    return out


def tfidf(a0, docs):
    T = a0.tfidf_sim([d if d else ["\x00empty%d" % i] for i, d in enumerate(docs)])
    for i, d in enumerate(docs):
        if not d:
            T[i, :] = 0
            T[:, i] = 0
    return T


# ======================================================================================================== covariates
def covariates_units(units, a1cats=None):
    def eq(key):
        v = np.array([u[key] for u in units])
        return (v[:, None] == v[None, :]).astype(float)
    pidx = np.array([int(u["page_idx"]) for u in units])
    ng = np.array([float(u["n_glyph"]) for u in units])
    nt = np.array([float(u["n_tok"]) for u in units])
    la = np.log(np.array([float(u["crop_area"]) for u in units]))
    covs = [eq("page"), eq("bifolio"), eq("quire"), (np.abs(pidx[:, None] - pidx[None, :]) == 1).astype(float),
            eq("section"), eq("hand"), eq("unit"), np.abs(ng[:, None] - ng[None, :]), np.abs(nt[:, None] - nt[None, :]),
            np.abs(la[:, None] - la[None, :])]
    for lv in (a1cats or {}).values():
        v = np.array(lv, dtype=object)
        has = np.array([x is not None for x in lv])
        covs.append(((v[:, None] == v[None, :]) & has[:, None] & has[None, :]).astype(float))
    return covs


def strata_units(units):
    keys = {}
    return np.array([keys.setdefault((u["section"], u["quire"]), len(keys)) for u in units])


def jackknife_ci(a0, P, T, covs, units):
    """Delete-one-page jackknife CI of the partial Mantel r (no permutations)."""
    pages = sorted({u["page"] for u in units})
    pg = np.array([u["page"] for u in units])
    rng = np.random.default_rng(0)
    st = np.zeros(len(units), int)
    rs = []
    for p in pages:
        keep = np.where(pg != p)[0]
        r, _, _, _ = a0.partial_mantel(P[np.ix_(keep, keep)], T[np.ix_(keep, keep)],
                                       [c[np.ix_(keep, keep)] for c in covs], st[keep], rng, nperm=1)
        rs.append(r)
    rs = np.array(rs)
    n = len(rs)
    r_full, _, _, _ = a0.partial_mantel(P, T, covs, st, rng, nperm=1)
    se = np.sqrt((n - 1) / n * ((rs - rs.mean()) ** 2).sum())
    return r_full, r_full - 1.96 * se, r_full + 1.96 * se


# ======================================================================================================== power gate
def cut_to_label_length(toks, kdist, rng):
    k = int(rng.choice(kdist))
    k = max(1, min(k, len(toks)))
    keep = np.sort(rng.choice(len(toks), size=k, replace=False))
    return [toks[i] for i in keep]


def do_power():
    set_low_priority()
    out = RUNS / "power.txt"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    a0 = load_a0()
    units_v = read_units()
    kdist = np.array([int(u["n_tok"]) for u in units_v])
    N = min(len(units_v), 820)
    au = a0.load_units()
    d = np.load(A0_EMBED)
    Pz, _ = a0.picture_matrices([d["dino"], d["siglip"]])
    pages = defaultdict(list)
    for i, u in enumerate(au):
        pages[u["ms"] + "|" + u["page"]].append(i)
    pkeys = sorted(pages)
    rng = np.random.default_rng(SEED)
    lines = [f"s116 power gate on the s115-A0 real-herbal corpus; {clock()}; script sha256 {sha(Path(__file__))}",
             f"A0 units {len(au)}; s116 units {len(units_v)} -> N = {N}; label token-count distribution "
             f"{dict(sorted(Counter(kdist.tolist()).items()))} (mean {kdist.mean():.3f}); NOISE {a0.NOISE}; "
             f"R {R_POW}; NPERM {NPERM_POW}"]
    print("\n".join(lines), flush=True)
    res = {}
    for sampler in ("uniform", "page_clustered"):
        for shuffle in (False, True):
            ps, rs = [], []
            for _ in range(R_POW):
                if sampler == "uniform":
                    sub = np.sort(rng.choice(len(au), size=N, replace=False))
                else:
                    sel = []
                    for k in rng.permutation(len(pkeys)):
                        sel += pages[pkeys[k]]
                        if len(sel) >= N:
                            break
                    sub = np.sort(np.array(sel[:N]))
                us = [au[i] for i in sub]
                st = a0.strata_of(us)
                docs = [list(u["toks"]) for u in us]
                if shuffle:
                    perm = a0.strat_derange(st, rng)
                    docs = [docs[j] for j in perm]
                docs = [a0.add_noise(cut_to_label_length(x, kdist, rng), rng) for x in docs]
                T = a0.tfidf_sim(docs)
                r, p, _, _ = a0.partial_mantel(Pz[np.ix_(sub, sub)], T, a0.covariates(us), st, rng, NPERM_POW)
                ps.append(p)
                rs.append(r)
            ps, rs = np.array(ps), np.array(rs)
            res[(sampler, shuffle)] = (ps < ALPHA).mean()
            s = (f"[{sampler} {'shuffled' if shuffle else 'real'}] N={N} share p<{ALPHA} = {(ps < ALPHA).mean():.3f}; "
                 f"share p<{ALPHA_LINK} = {(ps < ALPHA_LINK).mean():.3f}; r median {np.median(rs):+.4f} "
                 f"IQR [{np.quantile(rs, .25):+.4f}, {np.quantile(rs, .75):+.4f}]")
            print(s, flush=True)
            lines.append(s)
    pw = min(res[("uniform", False)], res[("page_clustered", False)])
    sh = max(res[("uniform", True)], res[("page_clustered", True)])
    ok = bool(pw >= POWER_MIN and sh <= SHUFFLE_MAX)
    lines.append(f"POWER={pw:.3f} (min of samplers); SHUFFLED={sh:.3f} (max of samplers)")
    lines.append(f"POWER_PASS={ok}")
    lines.append(f"end {clock()}")
    print("\n".join(lines[-3:]), flush=True)
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


# ======================================================================================================== fixture
def fixture_data(units, rng, planted: bool):
    n = len(units)
    K = 150
    subj_img = rng.integers(K, size=n)
    subj_txt = subj_img if planted else rng.integers(K, size=n)
    names = ["".join(LETTERS[int(c)] for c in rng.integers(26, size=5)) for _ in range(K)]
    quires = sorted({u["quire"] for u in units})
    qpre = {q: "".join(LETTERS[int(c)] for c in rng.integers(26, size=2)) for q in quires}
    sufs = ["y", "dy", "ol", "aiin", "ar"]
    docs = []
    for i, u in enumerate(units):
        k = int(u["n_tok"])
        d = [qpre[u["quire"]] + names[subj_txt[i]] + sufs[int(rng.integers(len(sufs)))]]
        d += ["".join(LETTERS[int(c)] for c in rng.integers(26, size=4)) for _ in range(k - 1)]
        docs.append(d)
    dim = 64
    S = rng.normal(size=(K, dim))
    Q = {q: rng.normal(size=dim) for q in quires}
    pg = {p: rng.normal(size=dim) for p in {u["page"] for u in units}}
    E = []
    for _ in range(2):
        e = np.stack([0.9 * S[subj_img[i]] + 0.8 * Q[u["quire"]] + 0.5 * pg[u["page"]] + rng.normal(size=dim)
                      for i, u in enumerate(units)])
        E.append(e / np.linalg.norm(e, axis=1, keepdims=True))
    return docs, E


def do_fixture():
    set_low_priority()
    out = RUNS / "fixture.txt"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    a0 = load_a0()
    units = read_units()
    covs = covariates_units(units)
    st = strata_units(units)
    lines = [f"s116 fixture (synthetic, Voynich-shaped: real unit table structure); {clock()}; script sha256 "
             f"{sha(Path(__file__))}; N {len(units)}; R {R_FIX}; NPERM {NPERM_FIX}"]
    res = {}
    for planted in (True, False):
        rng = np.random.default_rng(SEED + int(planted))
        ps, rs = [], []
        for _ in range(R_FIX):
            docs, E = fixture_data(units, rng, planted)
            Pz, _ = a0.picture_matrices(E)
            r, p, _, _ = a0.partial_mantel(Pz, tfidf(a0, docs), covs, st, rng, NPERM_FIX)
            ps.append(p)
            rs.append(r)
        ps, rs = np.array(ps), np.array(rs)
        res[planted] = ((ps < ALPHA_LINK).mean(), (ps < ALPHA).mean())
        s = (f"fixture planted={planted}: share p<{ALPHA_LINK} = {res[planted][0]:.2f}; share p<{ALPHA} = "
             f"{res[planted][1]:.2f}; r median {np.median(rs):+.4f}")
        print(s, flush=True)
        lines.append(s)
    ok = bool(res[True][0] >= POWER_MIN and res[False][1] <= SHUFFLE_MAX)
    lines.append(f"FIXTURE_PASS={ok}")
    print(lines[-1], flush=True)
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


# ======================================================================================================== real
def verify_stub():
    if not STUB.exists():
        return False, ["no stub"]
    ok, msgs = True, []
    for line in STUB.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        hx, fn = line.split(None, 1)
        fn = fn.lstrip("*").strip()
        good = (ROOT / fn).exists() and sha(ROOT / fn) == hx
        ok &= good
        if not good:
            msgs.append(f"MISMATCH {fn}")
    need = {"tools/s116_label_object.py", "runs/s116/units.tsv"}
    have = {l.split(None, 1)[1].lstrip("*").strip() for l in STUB.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")}
    if not need <= have:
        ok = False
        msgs.append(f"stub lacks {need - have}")
    return ok, msgs


def a1_strata(units):
    """Eligible categories from the A1b file -> {cat: [level or None per unit]}; None if file absent/unparseable."""
    if not A1B_KAPPA.exists():
        return None, "A1b file absent"
    m = [l for l in A1B_KAPPA.read_text(encoding="utf-8").splitlines() if l.startswith("A2-eligible:")]
    if len(m) != 1:
        return None, "A1b file has no single 'A2-eligible:' line"
    rest = m[0].split(":", 1)[1].strip()
    cats = [] if rest == "(none)" else rest.split()
    rows = {}
    with open(A1_LABELS, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows[r["stem"] + ".jpg"] = r
    out = {}
    for c in cats:
        lv = []
        for u in units:
            v = rows.get(u["scan"], {}).get(c)
            lv.append(None if (v is None or v == "NA" or v.startswith("DISAGREE")) else v)
        out[c] = lv
    return out, f"A2-eligible categories: {cats if cats else '(none) -> section is the stratum'}"


def do_real():
    set_low_priority()
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_path = ROOT / f"results_s116_{stamp}.txt"
    for fx_, key in ((RUNS / "power.txt", "POWER_PASS=True"), (RUNS / "fixture.txt", "FIXTURE_PASS=True")):
        if not fx_.exists() or key not in fx_.read_text(encoding="utf-8"):
            sys.exit(f"{fx_.name}: {key} not found; refusing to run")
    ok_stub, msgs = verify_stub()
    if not ok_stub:
        sys.exit("stub verification failed: " + "; ".join(msgs))
    units = read_units()
    bad = [u["uid"] for u in units if sha(CROPS / f"{u['uid']}.png") != u["crop_sha"]]
    if bad:
        sys.exit(f"crop sha mismatch: {bad[:5]}")
    a1, a1msg = a1_strata(units)
    if a1 is None:
        sys.exit(f"A1b strata unavailable ({a1msg}); refusing to run")
    a0 = load_a0()
    pw_line = [l for l in (RUNS / "power.txt").read_text(encoding="utf-8").splitlines() if l.startswith("POWER=")][0]
    POWER = float(re.match(r"POWER=([0-9.]+)", pw_line).group(1))
    f = open(out_path, "x", encoding="utf-8", newline="\n")

    def w(s=""):
        print(s, flush=True)
        f.write(s + "\n")

    w(f"s116 A2 label-to-object partial Mantel; script sha256={sha(Path(__file__))}")
    w(f"run start {clock()} (datetime.now); stub_match={ok_stub}")
    for fx_ in ("power.txt", "fixture.txt"):
        w(f"--- {fx_}")
        w((RUNS / fx_).read_text(encoding="utf-8").strip())
    by = Counter(u["section"] for u in units)
    w(f"units {len(units)} by section {dict(sorted(by.items()))}; pages {len({u['page'] for u in units})}")
    w(a1msg)
    t0 = time.time()
    emb = a0.Embedder()
    imgs = [Image.open(CROPS / f"{u['uid']}.png").convert("RGB") for u in units]
    E = [emb(imgs, "dino"), emb(imgs, "siglip")]
    w(f"embedded on {emb.dev} in {time.time() - t0:.0f}s")
    del emb
    np.savez_compressed(RUNS / f"{stamp}_embed.npz", dino=E[0], siglip=E[1])
    Pz, _ = a0.picture_matrices(E)
    covs = covariates_units(units, a1)
    st = strata_units(units)
    docs = translit_docs(units)
    rng = np.random.default_rng(SEED)
    res = {}
    for key in (("ZL3b", "core"), ("RF1b", "core"), ("IT2a", "core"), ("ZL3b", "word")):
        T = tfidf(a0, docs[key])
        nonempty = sum(1 for d in docs[key] if d)
        r, p, nm, q99 = a0.partial_mantel(Pz, T, covs, st, rng, NPERM)
        _, lo, hi = jackknife_ci(a0, Pz, T, covs, units)
        res[key] = (r, p, lo, hi)
        w(f"[{key[0]} {key[1]}] units with text {nonempty}/{len(units)}; r={r:+.4f} p={p:.4f} null mean {nm:+.4f} "
          f"q99 {q99:+.4f}; jackknife 95% CI [{lo:+.4f}, {hi:+.4f}]")
    # ---- descriptive
    w("\n--- descriptive (not part of the call)")
    T = tfidf(a0, docs[("ZL3b", "core")])
    q = np.array([u["quire"] for u in units])
    sq = q[:, None] == q[None, :]
    Pq = np.where(sq, np.nan, Pz)
    # same-quire pairs removed: set their residual contribution aside by restricting to cross-quire pairs via a mask
    iu0, iu1 = np.triu_indices(len(units), 1)
    keep = ~sq[iu0, iu1]
    cols = [np.ones(keep.sum())] + [c[iu0, iu1][keep] for c in covs if c[iu0, iu1][keep].std() > 0]
    Qm, _ = np.linalg.qr(np.column_stack(cols))
    pv, tv = Pz[iu0, iu1][keep], T[iu0, iu1][keep]
    ep, et = pv - Qm @ (Qm.T @ pv), tv - Qm @ (Qm.T @ tv)
    r_x = float(ep @ et / max(np.linalg.norm(ep) * np.linalg.norm(et), 1e-12))
    null = []
    for _ in range(999):
        pi = a0.strat_perm(st, rng)
        tv2 = T[pi][:, pi][iu0, iu1][keep]
        et2 = tv2 - Qm @ (Qm.T @ tv2)
        null.append(float(ep @ et2 / max(np.linalg.norm(ep) * np.linalg.norm(et2), 1e-12)))
    p_x = (1 + sum(v >= r_x for v in null)) / 1000
    w(f"[ZL3b core, same-quire pairs removed] pairs {int(keep.sum())}; r={r_x:+.4f} p={p_x:.4f} (999 perms)")
    del Pq
    perm = a0.strat_derange(st, rng)
    Tsh = tfidf(a0, [docs[("ZL3b", "core")][j] for j in perm])
    r_s, p_s, _, _ = a0.partial_mantel(Pz, Tsh, covs, st, rng, 999)
    w(f"[ZL3b core, shuffled-text control (deranged within strata)] r={r_s:+.4f} p={p_s:.4f}")
    sec = np.array([u["section"] for u in units])
    for s_ in sorted(set(sec)):
        idx = np.where(sec == s_)[0]
        if len(idx) < 30:
            w(f"[section {s_}] n={len(idx)} (< 30, skipped)")
            continue
        r_, p_, _, _ = a0.partial_mantel(Pz[np.ix_(idx, idx)], T[np.ix_(idx, idx)], [c[np.ix_(idx, idx)] for c in covs],
                                         st[idx], rng, 999)
        w(f"[section {s_}] n={len(idx)} r={r_:+.4f} p={p_:.4f}")
    for c, lv in a1.items():
        for level in sorted({x for x in lv if x is not None}):
            idx = np.array([i for i, x in enumerate(lv) if x == level])
            if len(idx) < 30:
                continue
            r_, p_, _, _ = a0.partial_mantel(Pz[np.ix_(idx, idx)], T[np.ix_(idx, idx)],
                                             [cc[np.ix_(idx, idx)] for cc in covs], st[idx], rng, 999)
            w(f"[A1 {c}={level}] n={len(idx)} r={r_:+.4f} p={p_:.4f}")
    # ---- call
    zl, rf, it, wd = (res[k] for k in (("ZL3b", "core"), ("RF1b", "core"), ("IT2a", "core"), ("ZL3b", "word")))
    link = zl[1] < ALPHA_LINK and rf[1] < ALPHA and it[1] < ALPHA and wd[1] < ALPHA
    null_ = POWER >= POWER_NULL and all(x[1] >= ALPHA for x in res.values()) and all(x[3] < CI_MAX for x in res.values())
    call = "LINK" if link else ("NULL" if null_ else "INCONCLUSIVE")
    w("\n=== CALL (rule frozen in the docstring) ===")
    w(f"POWER (A0 gate) = {POWER:.3f}; p: ZL3b core {zl[1]:.4f}, RF1b core {rf[1]:.4f}, IT2a core {it[1]:.4f}, "
      f"ZL3b word {wd[1]:.4f}; CI upper: {zl[3]:+.4f} {rf[3]:+.4f} {it[3]:+.4f} {wd[3]:+.4f}")
    w(f"CALL={call}")
    w(f"run end {clock()}")
    f.close()
    np.savez_compressed(RUNS / f"{stamp}_stats.npz", **{f"{a}_{b}": np.array(v) for (a, b), v in res.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--build-units", action="store_true")
    g.add_argument("--power", action="store_true")
    g.add_argument("--fixture", action="store_true")
    g.add_argument("--real", action="store_true")
    a = ap.parse_args()
    if a.build_units:
        build_units()
    elif a.power:
        do_power()
    elif a.fixture:
        do_fixture()
    else:
        do_real()
