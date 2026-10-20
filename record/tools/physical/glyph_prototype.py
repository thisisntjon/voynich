#!/usr/bin/env python
"""Phase 7.4 part 2 (D-069) PROTOTYPE: transcription-free glyph segmentation and clustering from the Yale scans.

DESIGN AND PROTOTYPE ONLY. Not pre-registered, not a results_* file, files no claim. The lead freezes the full-run
design (data/physical/glyphs/README.md, "Draft frozen design") after review.

What it does (about 20 pages, fixed selection rule below):
  1. Page selection (deterministic, seed 7069): single-folio Yale canvases with a Rozanova/voynichese box file, an
     s45 page (runs/s45/pages) with >= 3 counts-equal line groups of conf >= 0.8, and >= 80 ZL3b tokens in the VKB;
     quota by Davis hand {1:6, 2:4, 3:4, 4:3, 5:3}, shortfall to hand 1 (hand 4 had no eligible page); per hand the
     first 1 (hand 1: 2) picks after a seeded shuffle are HELD OUT.
  2. Words: the s45 ink tokens (kraken baselines + ink-gap word boundaries; no transcription used). A word owns
     the connected components whose centroid lies inside its x-range and within [yb - 0.6, yb + 0.3] line pitches
     of the kraken baseline. Rozanova boxes are registered (global affine by FFT correlation) only as a
     DIAGNOSTIC (box_diag); the prototype showed global registration fails on about half the pages.
  3. Ink: local-mean threshold on the full-resolution greyscale; connected components (8-connectivity) over the
     page. Words touching a drawing-sized component are dropped.
     Level A = connected components (strokes joined by ink).
     Level B = A with components merged when their x-extents overlap >= MERGE_OV of the narrower one
               (broken strokes, plumes, stacked fragments).
     Level C = B with wide units (> SPLIT_W * x-height) split at column-profile valleys whose ink is
               <= SPLIT_INK * stroke width (thin ligatures), recursively.
  4. Known-answer labels (never used to segment): in s45 line groups with counts_equal and conf >= 0.8, ink token
     k <-> ZL3b word k; a label is dropped if the token's width per EVA character is outside 0.7-1.43x the page
     median. Units: U1 = corpora.GLYPHS tokenization (cth ckh cph cfh ch sh single; = VKB n_glyphs);
     U0 = EVA characters; U2 = GLYPHS_PLUS (iin, in, ir, ee also single).
  5. Embedding: candidates of the level chosen on TRAIN pages (best exact count agreement with U1) are cropped
     to 48x48 (side = 2.4 x-heights, own-component mask), and a small CNN is trained self-supervised (SimCLR,
     NT-Xent) on TRAIN-page candidates only, on the GPU (memory capped at 4 GB). Baseline: PCA of raw pixels.
  6. Clustering: k-means (K in KS) fitted on TRAIN embeddings, applied to HELD-OUT candidates.
Gates printed (prototype, unverified):
  G-count  per-word candidate count vs U1 / U0 counts (exact rate, mean diff, Spearman), per level, held-out pages.
  G-units  least-squares coefficients count_level ~ sum_g beta_g * n_g(word) over U1 units (bootstrap CI):
           beta ~ 1 means the image treats that EVA unit as one ink unit, ~2 as two.
  G-purity held-out cluster purity vs U1 labels on words whose candidate count equals the U1 count
           (positional labels), against a label-permutation null; NMI.
  G-hand   (descriptive) leave-one-page-out nearest-centroid Davis-hand classification from per-glyph-type
           mean shape embeddings, against a hand-label permutation null.
  G-gap    word-boundary agreement: ink gaps inside words vs between adjacent words of the same line.
           NOT independent in this prototype: s45 word boundaries are themselves ink gaps.

Compute discipline: 1 CPU thread, BelowNormal priority, free RAM >= 4 GB, GPU free memory checked with nvidia-smi
before use and torch memory fraction capped to 4 GB.

Usage (project root):  python -u tools/physical/glyph_prototype.py [--out DIR] [--epochs N] [--pages f1r,...]
Outputs go to a new timestamped directory under data/physical/glyphs/prototype/ (never overwritten).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import time
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import psutil
from PIL import Image
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import boxes as rbox  # noqa: E402  (MIT Rozanova/voynichese boxes loader)
import corpora  # noqa: E402

SCANS = ROOT / "data" / "external" / "yale_scans"
VKB = ROOT / "data" / "vkb" / "vkb.sqlite"
OUT_BASE = ROOT / "data" / "physical" / "glyphs" / "prototype"

PARAMS = dict(
    seed=7069,
    hand_quota={"1": 6, "2": 4, "3": 4, "4": 3, "5": 3},
    heldout_per_hand={"1": 2, "2": 1, "3": 1, "4": 1, "5": 1},
    min_tokens=80, min_label_rows=3,   # page needs >= 3 s45 counts-equal line groups with conf >= label_conf
    reg_ds=6, reg_scales=(3.0, 6.0, 0.04), reg_aniso=(-0.04, 0.04, 0.01),
    snap_px=15,
    band_up=0.6, band_down=0.3,
    label_conf=0.8, label_wratio=(0.7, 1.43),  # label kept if s45 row conf >= label_conf and width/EVA-chars within ratio x page median   # s45 words own components with centroid in [yb - band_up*pitch, yb + band_down*pitch]
    bin_block=51, bin_C=15,
    speck_frac=0.04,          # components with area < speck_frac * xh^2 are dropped
    drawing_h=4.0, drawing_w=7.0,   # component taller than drawing_h*xh or wider than drawing_w*xh -> word dropped
    merge_ov=0.5,
    split_w=1.5, split_ink=1.5, split_edge=0.3,
    crop=48, crop_side_xh=2.4,
    emb_dim=64, epochs=40, batch=512, lr=2e-3, temp=0.2,
    ks=(24, 32, 48), n_perm=200, n_boot=200,
    gpu_cap_gb=4.0, min_free_ram_gb=4.0,
)


# ----------------------------------------------------------------------------------------------- utilities
def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def preflight():
    p = psutil.Process()
    try:
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception as e:  # non-Windows
        print("priority not set:", e)
    ram = psutil.virtual_memory().available / 2**30
    print(f"free RAM {ram:.1f} GB")
    if ram < PARAMS["min_free_ram_gb"]:
        sys.exit(f"ABORT: free RAM {ram:.1f} GB < {PARAMS['min_free_ram_gb']}")
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30).stdout.strip().splitlines()[0]
        used, total = (float(v) for v in q.split(","))
        free_gb = (total - used) / 1024
        print(f"GPU used {used:.0f} MiB of {total:.0f} MiB; free {free_gb:.1f} GB")
        if free_gb < PARAMS["gpu_cap_gb"] + 0.5:
            sys.exit(f"ABORT: GPU free {free_gb:.1f} GB < cap + 0.5")
        return total / 1024
    except FileNotFoundError:
        sys.exit("ABORT: nvidia-smi not found")


def collapse(w):
    return rbox.collapse(w)


def units(word, plus=False):
    """List of U1 units (corpora.GLYPHS multi-letter glyphs single) of an EVA word."""
    gl = sorted(corpora.GLYPHS_PLUS if plus else corpora.GLYPHS, key=len, reverse=True)
    out, i = [], 0
    while i < len(word):
        for g in gl:
            if word.startswith(g, i):
                out.append(g); i += len(g); break
        else:
            out.append(word[i]); i += 1
    return out


# ----------------------------------------------------------------------------------------------- data
def vkb():
    return sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)


def canvas_map():
    idx = json.loads((SCANS / "pages_index.json").read_text(encoding="utf-8"))
    lab = Counter(e["label"] for e in idx)
    return {"f" + e["label"]: e for e in idx if re.fullmatch(r"\d+[rv]", e["label"]) and lab[e["label"]] == 1}


def select_pages():
    con = vkb()
    rows = con.execute("select f.folio, f.hand_davis, f.currier_lang, f.section, count(t.word) from folios f "
                       "left join tokens t on t.folio=f.folio and t.translit='ZL3b' group by f.folio").fetchall()
    cm = canvas_map()
    have = set(rbox.box_folios())
    elig = defaultdict(list)
    for f, h, lang, sec, nt in rows:
        sp = ROOT / "runs" / "s45" / "pages" / f"{f}.json"
        if not (f in cm and f in have and sp.exists() and h in PARAMS["hand_quota"] and (nt or 0) >= PARAMS["min_tokens"]):
            continue
        al = json.loads(sp.read_text(encoding="utf-8"))["alignment"]
        if sum(1 for a in al if a.get("counts_equal") and a.get("conf", 0) >= PARAMS["label_conf"]) >= PARAMS["min_label_rows"]:
            elig[h].append(dict(folio=f, hand=h, lang=lang, section=sec, n_tokens=nt))
    rng = np.random.default_rng(PARAMS["seed"])
    sel = []
    quota = dict(PARAMS["hand_quota"])
    short = sum(max(0, q - len(elig[h])) for h, q in quota.items())
    quota["1"] += short                     # shortfall (hands with too few eligible pages) goes to hand 1
    for h in sorted(quota):
        cand = sorted(elig[h], key=lambda d: d["folio"])
        order = rng.permutation(len(cand))
        pick = [cand[i] for i in order[:quota[h]]]
        for j, d in enumerate(pick):
            d["split"] = "heldout" if j < PARAMS["heldout_per_hand"][h] else "train"
        sel += pick
    return sel, {h: len(v) for h, v in elig.items()}


def zl_tokens(folio):
    con = vkb()
    return [r[0] for r in con.execute(
        "select word from tokens where translit='ZL3b' and folio=? order by rowid", (folio,)).fetchall()]


# ----------------------------------------------------------------------------------------------- image
def load_gray(folio):
    e = canvas_map()[folio]
    return np.asarray(Image.open(SCANS / "pages" / e["file"]).convert("L"), dtype=np.float32)


def binarize(g):
    loc = ndi.uniform_filter(g, PARAMS["bin_block"])
    ink = g < (loc - PARAMS["bin_C"])
    return ndi.binary_opening(ink, structure=np.ones((2, 2), bool))


def register(g, bx):
    ds = PARAMS["reg_ds"]
    H, W = g.shape
    sm = np.asarray(Image.fromarray(g).resize((W // ds, H // ds), Image.BILINEAR), dtype=np.float32)
    ink = (sm < ndi.uniform_filter(sm, 15) - 12).astype(np.float32)
    h, w = ink.shape
    P = (2 * h, 2 * w)
    FI = np.fft.rfft2(ink - ink.mean(), P)

    def score(sx, sy):
        m = np.zeros((h, w), np.float32)
        for b in bx:
            y0, y1 = int(b["y"] * sy / ds), int((b["y"] + b["h"]) * sy / ds) + 1
            x0, x1 = int(b["x"] * sx / ds), int((b["x"] + b["w"]) * sx / ds) + 1
            m[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = 1
        c = np.fft.irfft2(FI * np.conj(np.fft.rfft2(m, P)), P)
        i = np.unravel_index(np.argmax(c), c.shape)
        ty = i[0] if i[0] < h else i[0] - P[0]
        tx = i[1] if i[1] < w else i[1] - P[1]
        return c[i] / max(m.sum(), 1), tx * ds, ty * ds

    a, b_, st = PARAMS["reg_scales"]
    best = max(((score(s, s), s, s) for s in np.arange(a, b_ + 1e-9, st)), key=lambda t: t[0][0])
    (sc, tx, ty), s0, _ = best
    lo, hi, st = PARAMS["reg_aniso"]
    best2 = max(((score(s0 * (1 + ex), s0 * (1 + ey)), s0 * (1 + ex), s0 * (1 + ey))
                 for ex in np.arange(lo, hi + 1e-9, st) for ey in np.arange(lo, hi + 1e-9, st)), key=lambda t: t[0][0])
    (sc, tx, ty), sx, sy = best2
    return dict(sx=float(sx), sy=float(sy), tx=float(tx), ty=float(ty), score=float(sc), ink_mean=float(ink.mean()))


def stroke_width(ink_crop):
    runs = []
    for row in ink_crop[:: max(1, ink_crop.shape[0] // 40)]:
        d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
        s, e = np.where(d == 1)[0], np.where(d == -1)[0]
        runs += list(e - s)
    return float(np.median(runs)) if runs else 4.0


# ----------------------------------------------------------------------------------------------- segmentation
def page_segment(folio):
    g = load_gray(folio)
    bx = rbox.load_boxes(folio)
    reg = register(g, bx)
    ink = binarize(g)
    lab, n = ndi.label(ink, structure=np.ones((3, 3), bool))
    objs = ndi.find_objects(lab)
    area = np.bincount(lab.ravel())
    # snapped full-res word rects
    rects = []
    S = PARAMS["snap_px"]
    ii = ink.astype(np.int32).cumsum(0).cumsum(1)

    def isum(y0, x0, y1, x1):
        y0, x0 = max(y0, 0), max(x0, 0); y1, x1 = min(y1, ink.shape[0] - 1), min(x1, ink.shape[1] - 1)
        if y1 <= y0 or x1 <= x0:
            return 0
        return ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]

    for b in bx:
        x0 = int(b["x"] * reg["sx"] + reg["tx"]); x1 = int((b["x"] + b["w"]) * reg["sx"] + reg["tx"])
        y0 = int(b["y"] * reg["sy"] + reg["ty"]); y1 = int((b["y"] + b["h"]) * reg["sy"] + reg["ty"])
        best = max(((isum(y0 + dy, x0 + dx, y1 + dy, x1 + dx), dx, dy)
                    for dy in range(-S, S + 1, 3) for dx in range(-S, S + 1, 3)))
        _, dx, dy = best
        rects.append((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    # component table
    comps = []
    for k, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        ys, xs = sl
        comps.append(dict(id=k, y0=ys.start, y1=ys.stop, x0=xs.start, x1=xs.stop, area=int(area[k])))
    hs = np.array([c["y1"] - c["y0"] for c in comps]); ar = np.array([c["area"] for c in comps])
    # x-height: median height of mid-sized components inside boxes
    cy = np.array([(c["y0"] + c["y1"]) / 2 for c in comps]); cx = np.array([(c["x0"] + c["x1"]) / 2 for c in comps])
    inside = np.zeros(len(comps), int) - 1
    for wi, (x0, y0, x1, y1) in enumerate(rects):
        m = (cx >= x0) & (cx < x1) & (cy >= y0) & (cy < y1) & (inside < 0)
        inside[m] = wi
    sel = (inside >= 0) & (ar > 30)
    xh = float(np.median(hs[sel])) if sel.sum() > 20 else 30.0
    sw = stroke_width(ink[int(np.median(cy[sel])) - 200:int(np.median(cy[sel])) + 200]) if sel.sum() > 20 else 4.0
    words = []
    for wi, r in enumerate(rects):
        cs = [comps[j] for j in np.where(inside == wi)[0]]
        cs = [c for c in cs if c["area"] >= PARAMS["speck_frac"] * xh * xh]
        drawing = any((c["y1"] - c["y0"]) > PARAMS["drawing_h"] * xh or (c["x1"] - c["x0"]) > PARAMS["drawing_w"] * xh
                      for c in cs)
        cs.sort(key=lambda c: (c["x0"] + c["x1"]) / 2)
        words.append(dict(i=wi, box_word=bx[wi]["word"], rect=r, comps=cs, drawing=drawing))
    return dict(folio=folio, reg=reg, xh=xh, sw=sw, words=words, n_comp=len(comps)), g, lab



S45_PAGES = ROOT / "runs" / "s45" / "pages"
_ZL = None


def zl_loci(folio):
    """ZL3b records of one page in file order (the loci list s45 aligned against)."""
    global _ZL
    if _ZL is None:
        import vparse
        _ZL = defaultdict(list)
        for r in vparse.load():
            _ZL[r["page"]].append(r)
    return _ZL[folio]


def baseline_y(line, x):
    """Kraken baseline y at column x (piecewise linear over the line's baseline polylines)."""
    pts = sorted((px, py) for bl in line["baselines"] for px, py in bl)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return float(np.interp(x, xs, ys)) if pts else float(line["yb"])


def page_segment_s45(folio):
    """Words from the s45 ink tokens (kraken lines + ink-gap word boundaries; no transcription used).
    Labels (known answer only): in s45 line groups with counts_equal, ink token k <-> ZL3b word k."""
    js = json.loads((S45_PAGES / f"{folio}.json").read_text(encoding="utf-8"))
    g = load_gray(folio)
    ink = binarize(g)
    lab, n = ndi.label(ink, structure=np.ones((3, 3), bool))
    objs = ndi.find_objects(lab)
    area = np.bincount(lab.ravel())
    comps = []
    for k, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        ys, xs = sl
        comps.append(dict(id=k, y0=ys.start, y1=ys.stop, x0=xs.start, x1=xs.stop, area=int(area[k])))
    cx = np.array([(c["x0"] + c["x1"]) / 2 for c in comps]); cy = np.array([(c["y0"] + c["y1"]) / 2 for c in comps])
    hs = np.array([c["y1"] - c["y0"] for c in comps]); ar = np.array([c["area"] for c in comps])
    pitch = float(js["pitch"])
    loci = zl_loci(folio)
    labels = {}
    for ri, row in enumerate(js["alignment"]):
        if not row.get("counts_equal") or not row.get("det"):
            continue
        words = [w for j in row["loci"] for w in loci[j]["words"]]
        toks = [(i, t) for i in row["det"] for t in range(len(js["lines"][i]["tokens"]))]
        if len(words) != len(toks) or row.get("conf", 0) < PARAMS["label_conf"]:
            continue
        for k, (key, w) in enumerate(zip(toks, words)):
            labels[key] = (w, ri, k)
    owner = np.full(len(comps), -1)
    words = []
    for li, line in enumerate(js["lines"]):
        for ti, t in enumerate(line["tokens"]):
            yb = baseline_y(line, (t["x0"] + t["x1"]) / 2)
            m = ((cx >= t["x0"]) & (cx < t["x1"] + 1) & (cy >= yb - PARAMS["band_up"] * pitch)
                 & (cy < yb + PARAMS["band_down"] * pitch) & (owner < 0))
            idx = np.where(m)[0]
            owner[idx] = len(words)
            lw = labels.get((li, ti))
            ok = lw is not None and not re.search(r"[^a-z]", lw[0])
            words.append(dict(i=len(words), rect=(t["x0"], int(yb - pitch), t["x1"], int(yb + 0.3 * pitch)),
                              cidx=idx, eva=lw[0] if ok else None, adj=(lw[1], lw[2]) if lw else None, line=li))
    wr = [(t1 - t0) / len(w["eva"]) for w in words if w["eva"] for t0, _, t1, _ in [w["rect"]]]
    if wr:
        med = float(np.median(wr)); lo, hi = PARAMS["label_wratio"]
        for w in words:
            if w["eva"] and not (lo <= (w["rect"][2] - w["rect"][0]) / len(w["eva"]) / med <= hi):
                w["eva"] = None
    own = owner >= 0
    sel = own & (ar > 30)
    xh = float(np.median(hs[sel])) if sel.sum() > 20 else 0.4 * pitch
    ymid = int(np.median(cy[sel])) if sel.sum() > 20 else g.shape[0] // 2
    sw = stroke_width(ink[max(0, ymid - 300):ymid + 300])
    for w in words:
        cs = [comps[j] for j in w.pop("cidx")]
        cs = [c for c in cs if c["area"] >= PARAMS["speck_frac"] * xh * xh]
        w["drawing"] = any((c["y1"] - c["y0"]) > PARAMS["drawing_h"] * xh or (c["x1"] - c["x0"]) > PARAMS["drawing_w"] * xh
                           for c in cs)
        cs.sort(key=lambda c: (c["x0"] + c["x1"]) / 2)
        w["comps"] = cs
    return dict(folio=folio, xh=xh, sw=sw, pitch=pitch, words=words, n_comp=len(comps)), g, lab


def box_diag(folio, g, seg):
    """Diagnostic only: how well do the Rozanova/voynichese word boxes register to this scan?
    Global affine by FFT correlation; then, for s45-labelled words whose string is unique on the page and in the
    box file, the distance between the registered box centre and the s45 ink-token centre, in line pitches."""
    bx = rbox.load_boxes(folio)
    if not bx:
        return None
    reg = register(g, bx)
    cnt = Counter(b["word"] for b in bx)
    bc = {b["word"]: (b["cx"] * reg["sx"] + reg["tx"], b["cy"] * reg["sy"] + reg["ty"], b["h"] * reg["sy"])
          for b in bx if cnt[b["word"]] == 1}
    wc = Counter(w["eva"] for w in seg["words"] if w["eva"])
    d, hh = [], []
    for w in seg["words"]:
        if w["eva"] and wc[w["eva"]] == 1 and w["eva"] in bc:
            x0, y0, x1, y1 = w["rect"]
            bx_, by_, bh = bc[w["eva"]]
            d.append(np.hypot(bx_ - (x0 + x1) / 2, by_ - (y0 + 0.7 * (y1 - y0)))); hh.append(bh)
    if not d:
        return dict(reg=reg, n=0)
    p = seg["pitch"]
    d = np.array(d) / p
    return dict(reg=reg, n=len(d), med_dist_pitch=float(np.median(d)), frac_within_half=float(np.mean(d < 0.5)),
                med_box_h_pitch=float(np.median(hh) / p))

def level_units(word, lab, xh, sw):
    """Return dict level -> list of units; each unit = dict(x0,x1,y0,y1,ids) (left to right)."""
    A = [dict(x0=c["x0"], x1=c["x1"], y0=c["y0"], y1=c["y1"], ids=[c["id"]]) for c in word["comps"]]
    B = []
    for u in A:
        merged = False
        for v in B:
            ov = min(u["x1"], v["x1"]) - max(u["x0"], v["x0"])
            if ov >= PARAMS["merge_ov"] * min(u["x1"] - u["x0"], v["x1"] - v["x0"]):
                v.update(x0=min(u["x0"], v["x0"]), x1=max(u["x1"], v["x1"]), y0=min(u["y0"], v["y0"]),
                         y1=max(u["y1"], v["y1"]), ids=v["ids"] + u["ids"]); merged = True; break
        if not merged:
            B.append(dict(u))
    B.sort(key=lambda u: (u["x0"] + u["x1"]) / 2)
    C = []

    def split(u, depth=0):
        w = u["x1"] - u["x0"]
        if w <= PARAMS["split_w"] * xh or depth > 4:
            C.append(u); return
        m = np.isin(lab[u["y0"]:u["y1"], u["x0"]:u["x1"]], u["ids"])
        prof = m.sum(0)
        e = int(PARAMS["split_edge"] * xh)
        if w - 2 * e < 3:
            C.append(u); return
        inner = prof[e:w - e]
        j = int(np.argmin(inner)) + e
        if prof[j] > PARAMS["split_ink"] * sw:
            C.append(u); return
        split(dict(u, x1=u["x0"] + j), depth + 1)
        split(dict(u, x0=u["x0"] + j), depth + 1)

    for u in B:
        split(u)
    return dict(A=A, B=B, C=C)


def crop_unit(lab, u, xh):
    side = int(PARAMS["crop_side_xh"] * xh)
    cy, cx = (u["y0"] + u["y1"]) // 2, (u["x0"] + u["x1"]) // 2
    y0, x0 = cy - side // 2, cx - side // 2
    H, W = lab.shape
    win = np.zeros((side, side), np.float32)
    ys0, xs0 = max(y0, 0), max(x0, 0); ys1, xs1 = min(y0 + side, H), min(x0 + side, W)
    sub = lab[ys0:ys1, xs0:xs1]
    m = np.isin(sub, u["ids"])
    # restrict to the unit's own x-range (level C splits share component ids)
    xx = np.arange(xs0, xs1)[None, :]
    m &= (xx >= u["x0"]) & (xx < u["x1"])
    win[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = m
    im = Image.fromarray((win * 255).astype(np.uint8)).resize((PARAMS["crop"], PARAMS["crop"]), Image.BILINEAR)
    return np.asarray(im, dtype=np.uint8)


# ----------------------------------------------------------------------------------------------- labels
def label_words(seg):
    zl = zl_tokens(seg["folio"])
    bw = [w["box_word"] for w in seg["words"]]
    sm = SequenceMatcher(a=[collapse(w) for w in bw], b=[collapse(w) for w in zl], autojunk=False)
    for a0, b0, n in sm.get_matching_blocks():
        for k in range(n):
            w = seg["words"][a0 + k]
            if bw[a0 + k] == zl[b0 + k] and "?" not in zl[b0 + k] and "*" not in zl[b0 + k]:
                w["eva"] = zl[b0 + k]
                w["zl_idx"] = b0 + k


# ----------------------------------------------------------------------------------------------- embedding
def train_simclr(X, total_gb, epochs):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    torch.set_num_threads(1)
    dev = "cuda"
    torch.cuda.set_per_process_memory_fraction(min(1.0, PARAMS["gpu_cap_gb"] / total_gb), 0)
    torch.manual_seed(PARAMS["seed"])

    class Net(nn.Module):
        def __init__(self, d):
            super().__init__()
            def blk(i, o):
                return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(),
                                     nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(), nn.MaxPool2d(2))
            self.f = nn.Sequential(blk(1, 32), blk(32, 64), blk(64, 128), nn.AdaptiveAvgPool2d(1), nn.Flatten())
            self.emb = nn.Linear(128, d)
            self.proj = nn.Sequential(nn.ReLU(), nn.Linear(d, d))

        def forward(self, x):
            e = self.emb(self.f(x))
            return e, self.proj(e)

    def aug(x):
        n = x.shape[0]
        ang = (torch.rand(n, device=dev) - 0.5) * 0.2
        sc = 1 + (torch.rand(n, device=dev) - 0.5) * 0.2
        sh = (torch.rand(n, device=dev) - 0.5) * 0.3
        t = (torch.rand(n, 2, device=dev) - 0.5) * 0.12
        th = torch.zeros(n, 2, 3, device=dev)
        th[:, 0, 0] = sc * torch.cos(ang); th[:, 0, 1] = -torch.sin(ang) + sh; th[:, 0, 2] = t[:, 0]
        th[:, 1, 0] = torch.sin(ang); th[:, 1, 1] = sc * torch.cos(ang); th[:, 1, 2] = t[:, 1]
        g = F.affine_grid(th, x.shape, align_corners=False)
        y = F.grid_sample(x, g, align_corners=False)
        r = torch.rand(n, device=dev)
        y = torch.where((r < 0.25)[:, None, None, None], F.max_pool2d(y, 3, 1, 1), y)       # thicker stroke
        y = torch.where((r > 0.75)[:, None, None, None], -F.max_pool2d(-y, 3, 1, 1), y)     # thinner stroke
        return y + 0.05 * torch.randn_like(y)

    net = Net(PARAMS["emb_dim"]).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=PARAMS["lr"], weight_decay=1e-4)
    Xt = torch.tensor(X[:, None] / 255.0, dtype=torch.float32)
    bs = PARAMS["batch"]
    for ep in range(epochs):
        perm = torch.randperm(len(Xt))
        tot = 0.0
        for i in range(0, len(Xt) - bs + 1, bs):
            x = Xt[perm[i:i + bs]].to(dev)
            _, z1 = net(aug(x)); _, z2 = net(aug(x))
            z = F.normalize(torch.cat([z1, z2]), dim=1)
            s = z @ z.T / PARAMS["temp"]
            s.fill_diagonal_(-1e9)
            tgt = torch.cat([torch.arange(bs, 2 * bs), torch.arange(0, bs)]).to(dev)
            loss = F.cross_entropy(s, tgt)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()
        if ep % 10 == 0 or ep == epochs - 1:
            print(f"  simclr epoch {ep} loss {tot / max(1, len(Xt) // bs):.3f}  "
                  f"gpu peak {torch.cuda.max_memory_allocated() / 2**30:.2f} GB", flush=True)
    net.eval()

    def embed(Xn):
        out = []
        with torch.no_grad():
            for i in range(0, len(Xn), 2048):
                x = torch.tensor(Xn[i:i + 2048, None] / 255.0, dtype=torch.float32, device=dev)
                out.append(F.normalize(net(x)[0], dim=1).cpu().numpy())
        return np.concatenate(out) if out else np.zeros((0, PARAMS["emb_dim"]))
    return embed


# ----------------------------------------------------------------------------------------------- stats
def purity(cl, y):
    tab = defaultdict(Counter)
    for c, l in zip(cl, y):
        tab[c][l] += 1
    return sum(max(v.values()) for v in tab.values()) / max(1, len(y))


def beta_fit(rows, level, vocab, n_boot, rng):
    X = np.array([[Counter(r["u1"])[g] for g in vocab] for r in rows], float)
    yv = np.array([r["cnt"][level] for r in rows], float)
    b = np.linalg.lstsq(X, yv, rcond=None)[0]
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(rows), len(rows))
        bs.append(np.linalg.lstsq(X[i], yv[i], rcond=None)[0])
    bs = np.array(bs)
    return b, np.percentile(bs, 2.5, 0), np.percentile(bs, 97.5, 0), X.sum(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--epochs", type=int, default=PARAMS["epochs"])
    ap.add_argument("--pages", default=None, help="smoke-test override (comma list; the last page is held out)")
    args = ap.parse_args()
    t0 = time.time()
    total_gb = preflight()
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = Path(args.out) if args.out else OUT_BASE / stamp
    if out.exists():
        sys.exit(f"ABORT: {out} exists (never overwrite)")
    out.mkdir(parents=True)
    log = open(out / "gate.txt", "w", encoding="utf-8", newline="\n")

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True); log.write(s + "\n"); log.flush()

    P(f"# glyph_prototype (D-069 part 2) PROTOTYPE, not pre-registered, files no claim. start {now()}")
    P(f"preflight passed: free RAM >= {PARAMS['min_free_ram_gb']} GB, GPU free >= cap + 0.5 GB; GPU total {total_gb:.1f} GB")
    sel, elig = select_pages()
    if args.pages:
        fs = args.pages.split(",")
        hd = dict(vkb().execute("select folio, hand_davis from folios").fetchall())
        sel = [dict(folio=f, hand=hd.get(f, "?"), split="heldout" if i == len(fs) - 1 else "train")
               for i, f in enumerate(fs)]
    P("eligible pages per hand:", dict(sorted(elig.items())))
    P("selected:", " ".join(f"{d['folio']}(h{d['hand']},{d['split'][0]})" for d in sel))
    (out / "params.json").write_text(json.dumps(dict(PARAMS=PARAMS, pages=sel, epochs=args.epochs), indent=1,
                                                 default=str), encoding="utf-8")

    # ---- segmentation + labels
    rows, crops = [], {"A": [], "B": [], "C": []}
    unit_meta = {"A": [], "B": [], "C": []}
    gaps = []
    box_diags = []
    for d in sel:
        ts = time.time()
        seg, g, lab = page_segment_s45(d["folio"])
        bd = box_diag(d["folio"], g, seg)
        box_diags.append((d["folio"], bd))
        nlab = 0
        prev = None
        for w in seg["words"]:
            if w["drawing"] or not w["comps"]:
                prev = None; continue
            lv = level_units(w, lab, seg["xh"], seg["sw"])
            r = dict(folio=d["folio"], hand=d["hand"], split=d["split"], i=w["i"], eva=w["eva"],
                     cnt={k: len(v) for k, v in lv.items()})
            if r["eva"]:
                r["u1"] = units(r["eva"]); r["u0"] = list(r["eva"]); r["u2"] = units(r["eva"], plus=True)
                nlab += 1
            rows.append(r)
            for k, us in lv.items():
                pos_labels = r.get("u1") if (r["eva"] and len(us) == len(r["u1"])) else None
                for j, u in enumerate(us):
                    crops[k].append(crop_unit(lab, u, seg["xh"]))
                    unit_meta[k].append(dict(folio=d["folio"], hand=d["hand"], split=d["split"], word=w["i"],
                                             j=j, lab=pos_labels[j] if pos_labels else None,
                                             x0=u["x0"], y0=u["y0"], x1=u["x1"], y1=u["y1"]))
            # gaps (level B units): within-word gaps and the gap to the previous word on the same row
            us = lv["B"]
            for a, b in zip(us, us[1:]):
                gaps.append(dict(split=d["split"], kind="in", g=(b["x0"] - a["x1"]) / seg["xh"]))
            if prev is not None and w["adj"] and prev[2] and w["adj"][0] == prev[2][0] and \
                    w["adj"][1] == prev[2][1] + 1 and prev[3] == w["line"] and us[0]["x0"] > prev[0]:
                gaps.append(dict(split=d["split"], kind="between", g=(us[0]["x0"] - prev[0]) / seg["xh"]))
            prev = (us[-1]["x1"], (us[-1]["y0"] + us[-1]["y1"]) / 2, w["adj"], w["line"])
        bds = (f"box reg: n {bd['n']}, median centre error {bd.get('med_dist_pitch', float('nan')):.2f} pitch, "
               f"within 0.5 pitch {bd.get('frac_within_half', float('nan')):.2f}, "
               f"box h {bd.get('med_box_h_pitch', float('nan')):.2f} pitch" if bd else "no box file")
        P(f"  {d['folio']} h{d['hand']} {d['split']}: {bds}; pitch {seg['pitch']:.0f}px xh {seg['xh']:.0f}px "
          f"sw {seg['sw']:.1f}px; ink words {len(seg['words'])}, labelled {nlab}, "
          f"drawing-dropped {sum(w['drawing'] for w in seg['words'])}  ({time.time() - ts:.0f}s)")
        del g, lab
    with open(out / "words.tsv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("folio\thand\tsplit\tbox\teva\tn_u1\tn_u0\tn_A\tn_B\tn_C\n")
        for r in rows:
            fh.write(f"{r['folio']}\t{r['hand']}\t{r['split']}\t{r['i']}\t{r['eva'] or ''}\t"
                     f"{len(r['u1']) if r['eva'] else ''}\t{len(r['u0']) if r['eva'] else ''}\t"
                     f"{r['cnt']['A']}\t{r['cnt']['B']}\t{r['cnt']['C']}\n")

    # ---- G-count
    P("\n## G-count: per-word candidate count vs EVA counts (labelled words only)")
    lab_rows = [r for r in rows if r["eva"]]
    best_level = None
    for split in ("train", "heldout"):
        rr = [r for r in lab_rows if r["split"] == split]
        P(f"  {split}: n words {len(rr)}")
        for lv in "ABC":
            for un in ("u1", "u0", "u2"):
                c = np.array([r["cnt"][lv] for r in rr]); e = np.array([len(r[un]) for r in rr])
                ex = float(np.mean(c == e)); md = float(np.mean(c - e)); rho = spearmanr(c, e)[0]
                P(f"    level {lv} vs {un}: exact {ex:.3f}  within1 {np.mean(abs(c - e) <= 1):.3f}  "
                  f"mean(cand-eva) {md:+.2f}  spearman {rho:.3f}")
                if split == "train" and un == "u1" and (best_level is None or ex > best_level[1]):
                    best_level = (lv, ex)
    P(f"  level chosen on TRAIN (best exact vs U1): {best_level[0]} ({best_level[1]:.3f})")
    P("  (u1 = corpora.GLYPHS units = VKB n_glyphs; u0 = EVA characters; u2 = GLYPHS_PLUS: iin/in/ir/ee single)")

    # ---- G-units
    P("\n## G-units: count_level ~ sum_g beta_g n_g(word), all labelled words, bootstrap 95% CI")
    rng = np.random.default_rng(PARAMS["seed"])
    voc = [g for g, n in Counter(u for r in lab_rows for u in r["u1"]).most_common() if n >= 30]
    lab_rows_v = [r for r in lab_rows if all(u in voc for u in r["u1"])]
    for lv in "ABC":
        b, lo, hi, n = beta_fit(lab_rows_v, lv, voc, PARAMS["n_boot"], rng)
        P(f"  level {lv} (n words {len(lab_rows_v)}): " + "  ".join(
            f"{g}:{b[i]:.2f}[{lo[i]:.2f},{hi[i]:.2f}]" for i, g in enumerate(voc)))

    # ---- embedding + clustering at the chosen level
    lv = best_level[0]
    X = np.stack(crops[lv]); M = unit_meta[lv]
    np.save(out / f"crops_{lv}.npy", X)
    with open(out / f"units_{lv}.tsv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("idx\tfolio\thand\tsplit\tword\tj\tlab\tx0\ty0\tx1\ty1\n")
        for i, m in enumerate(M):
            fh.write(f"{i}\t{m['folio']}\t{m['hand']}\t{m['split']}\t{m['word']}\t{m['j']}\t{m['lab'] or ''}\t"
                     f"{m['x0']}\t{m['y0']}\t{m['x1']}\t{m['y1']}\n")
    tr = np.array([m["split"] == "train" for m in M]); ho = ~tr
    P(f"\n## Embedding (level {lv}): {tr.sum()} train units, {ho.sum()} held-out units; SimCLR {args.epochs} epochs")
    ts = time.time()
    embed = train_simclr(X[tr], total_gb, args.epochs)
    E = embed(X)
    np.save(out / f"emb_{lv}.npy", E.astype(np.float32))
    P(f"  trained+embedded in {time.time() - ts:.0f}s")
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import normalized_mutual_info_score as nmi
    pca = PCA(32, random_state=0).fit(X[tr].reshape(tr.sum(), -1).astype(np.float32))
    R = pca.transform(X.reshape(len(X), -1).astype(np.float32))
    labm = np.array([m["lab"] is not None for m in M])
    yl = np.array([m["lab"] or "" for m in M])
    P("\n## G-purity: held-out units with positional U1 labels (words whose count equals the U1 count)")
    hl = ho & labm
    P(f"  n labelled held-out units {hl.sum()}; label types {len(set(yl[hl]))}; majority-label share "
      f"{Counter(yl[hl]).most_common(1)[0][1] / hl.sum():.3f}")
    clusters = {}
    for name, F_ in (("simclr", E), ("pca-pixels", R)):
        for K in PARAMS["ks"]:
            km = KMeans(K, n_init=4, random_state=0).fit(F_[tr])
            cl = km.predict(F_)
            clusters[(name, K)] = cl
            p = purity(cl[hl], yl[hl])
            null = [purity(cl[hl], rng.permutation(yl[hl])) for _ in range(PARAMS["n_perm"])]
            P(f"  {name:10s} K={K}: purity {p:.3f}  null {np.mean(null):.3f} (max {np.max(null):.3f})  "
              f"NMI {nmi(yl[hl], cl[hl]):.3f}")
    # composition of SimCLR K=32 clusters on held-out
    cl = clusters[("simclr", 32)]
    P("  simclr K=32 cluster composition (held-out labelled, top labels):")
    for c in range(32):
        cc = Counter(yl[hl & (cl == c)])
        nn_ = sum(cc.values())
        if nn_:
            P(f"    c{c:02d} n={nn_:4d}: " + ", ".join(f"{k}:{v / nn_:.2f}" for k, v in cc.most_common(4)))
    # where do the multi-stroke EVA glyphs go?
    P("  multi-stroke EVA units, held-out: share in their modal cluster / that cluster's purity for them")
    for gname in ("ch", "sh", "cth", "ckh", "k", "t", "p", "f"):
        m = hl & (yl == gname)
        if m.sum() >= 5:
            c0, n0 = Counter(cl[m]).most_common(1)[0]
            P(f"    {gname}: n {m.sum()}, modal cluster c{c0:02d} holds {n0 / m.sum():.2f}; "
              f"{gname} share of c{c0:02d} {n0 / (hl & (cl == c0)).sum():.2f}")

    # ---- G-hand (descriptive)
    P("\n## G-hand (descriptive, 20 pages, confounded with section/scan): LOPO nearest-centroid by shape")
    pages = [d["folio"] for d in sel]
    hands = {d["folio"]: d["hand"] for d in sel}
    types = [g for g, n in Counter(yl[labm]).most_common() if n >= 40][:12]
    V = []
    for f in pages:
        v = []
        for g in types:
            m = labm & (yl == g) & np.array([mm["folio"] == f for mm in M])
            v.append(E[m].mean(0) if m.sum() >= 3 else np.full(E.shape[1], np.nan))
        V.append(np.concatenate(v))
    V = np.array(V)
    V = np.where(np.isnan(V), np.nanmean(V, 0), V)
    hv = np.array([hands[f] for f in pages])

    def lopo(hlab):
        ok = 0
        for i in range(len(pages)):
            cents = {h: V[(hlab == h) & (np.arange(len(pages)) != i)].mean(0) for h in set(hlab)
                     if ((hlab == h) & (np.arange(len(pages)) != i)).sum()}
            pred = min(cents, key=lambda h: np.linalg.norm(V[i] - cents[h]))
            ok += pred == hlab[i]
        return ok / len(pages)
    acc = lopo(hv)
    null = [lopo(rng.permutation(hv)) for _ in range(PARAMS["n_perm"])]
    P(f"  glyph types used: {types}")
    P(f"  LOPO accuracy {acc:.3f}; permutation null mean {np.mean(null):.3f}, p = "
      f"{(1 + sum(n >= acc for n in null)) / (1 + len(null)):.3f}")

    # ---- G-gap
    P("\n## G-gap: inter-unit ink gaps (level B, in x-heights): inside words vs between adjacent words")
    gi = np.array([x["g"] for x in gaps if x["kind"] == "in" and x["split"] == "train"])
    gb = np.array([x["g"] for x in gaps if x["kind"] == "between" and x["split"] == "train"])
    cand = np.linspace(0, 3, 301)
    acc_t = [(np.mean(gi < t) * len(gi) + np.mean(gb >= t) * len(gb)) / (len(gi) + len(gb)) for t in cand]
    thr = cand[int(np.argmax(acc_t))]
    hi_ = np.array([x["g"] for x in gaps if x["kind"] == "in" and x["split"] == "heldout"])
    hb = np.array([x["g"] for x in gaps if x["kind"] == "between" and x["split"] == "heldout"])
    tp = np.sum(hb >= thr); fp = np.sum(hi_ >= thr); fn = np.sum(hb < thr); tn = np.sum(hi_ < thr)
    n = tp + fp + fn + tn
    po = (tp + tn) / n; pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / n**2
    P(f"  train: in-word median {np.median(gi):.2f}, between median {np.median(gb):.2f}; threshold {thr:.2f} xh")
    P(f"  held-out: n in {len(hi_)}, between {len(hb)}; boundary recall {tp / max(1, tp + fn):.3f}, "
      f"precision {tp / max(1, tp + fp):.3f}, kappa {(po - pe) / (1 - pe):.3f}")
    P(f"\n# end {now()}  elapsed {time.time() - t0:.0f}s  out {out}")
    log.close()


if __name__ == "__main__":
    main()
