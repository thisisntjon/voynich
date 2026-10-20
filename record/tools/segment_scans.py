#!/usr/bin/env python
"""s45 pipeline: ink-derived line and word boundaries from the Yale scans (O-048).

Not pre-registered (pipeline step); every parameter is logged to runs/s45/segment_params.json.
Run from the project root with the scratchpad venv (kraken + system torch):

    <venv_s45>/Scripts/python.exe -I tools/segment_scans.py [--limit N] [--pages f1r,f2r] [--device cuda:0]

Steps
  A. Map Yale canvases (data/external/yale_scans/pages_index.json, labels like "1r") to ZL3b page ids.
     Only single-folio labels "<n>r|v" that name exactly one ZL3b page are used; composite canvases
     ("69v and 70r", "70v (part)", "67r" when ZL3b has f67r1+f67r2) are recorded as unmatched.
  B. Line segmentation per page with kraken's blla baseline model on the GPU (baselines + boundary
     polygons).  Fragments on the same row (|dy| < ROW_TOL * line height, horizontally disjoint) are
     merged into one line (the transliteration keeps a line across a drawing interruption).  Lines are
     ordered top-to-bottom by baseline y.
  C. Word boundaries from ink: adaptive-threshold binarisation of the page, column ink profile inside the
     line polygon restricted to a band around the kraken baseline (BAND x line pitch), ink runs separated by
     zero-ink gaps; specks (< SPECK_FRAC of the median run mass)
     are dropped; a 3-component Gaussian mixture (EM, 1-D, on log gap width >= 3 px: stroke, glyph and
     word gaps) per page separates intra-word from inter-word gaps; threshold = posterior-0.5 crossing
     between the two upper components.
     Ink token = run of ink between inter-word gaps, carrying pixel width, mass and both flanking gaps.
  D. Alignment to the transliteration (no glyph is read from the image): detected lines <-> ZL3b loci
     by a monotone DP on total ink width vs glyph count (page pixels-per-glyph; 1:1, 1:2, 2:1, skips); within aligned P-lines, ink tokens <-> ZL3b
     tokens by the same DP on width/char counts (pixels-per-char from the line totals).  Confidence per
     line = 1 - mean normalised size residual of the chosen operations.
  E. Sidecars (runs/s45/): ink_ZL3b.meta.json (ZL3b glyph strings re-segmented by the ink gaps:
     merges concatenate, splits cut at the glyph boundary nearest the ink width share) and
     ink_lines_ZL3b.meta.json (ink line breaks, tokens unchanged).  Tokens containing '?' are dropped
     at output time, as metrics_new.voynich_pages does.  Per-page JSON (lines, ink tokens, gaps,
     thresholds, alignment) in runs/s45/pages/<id>.json; summary table in runs/s45/segment_summary.json.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import vparse  # noqa: E402
from corpora import GLYPHS_PLUS  # noqa: E402

SCANS = ROOT / "data" / "external" / "yale_scans"
OUT = ROOT / "runs" / "s45"
PAGES_OUT = OUT / "pages"

PARAMS = dict(
    segmenter="kraken blla.mlmodel (package default), blla.segment(device=cuda:0), full-resolution JPEG",
    row_tol=0.45,           # same-row fragment merge: x-disjoint segments whose facing baseline ends differ by < ROW_TOL * pitch
    pitch="median spacing of consecutive baselines among segments wider than half the widest segment",
    band=(0.55, 0.15),      # ink profile band around the baseline: [yb - 0.55*pitch, yb + 0.15*pitch], inside the polygon
    binarize="cv2.adaptiveThreshold GAUSSIAN_C, blockSize=51, C=18, THRESH_BINARY_INV; opening 3x3 (1 iter)",
    block_size=51, C=18,
    col_min_ink=2,          # a column counts as ink if >= this many ink pixels inside the polygon
    speck_frac=0.15,        # ink runs with mass < speck_frac * median run mass are dropped (become gap)
    min_run_width=4,
    mixture="3-component Gaussian EM on log(gap px) for gaps >= 3 px (stroke / glyph / word gaps; 1-2 px gaps "
            "are stroke breaks); threshold = posterior-0.5 crossing between the two upper components; "
            "quantile init, sd floor 0.15, 300 iters",
    mix_K=3,
    mix_min_gap=3,
    margin_filter="drop kraken segments narrower than 0.6*pitch, or narrower than 2*pitch and lying outside "
                  "the text block (x1 < L + 0.5*pitch or x0 > R - 0.5*pitch; L/R = 10th/90th pct of x0/x1 of "
                  "segments wider than 5*pitch): margin stars, folio numbers, quire marks",
    thr_clip_px=(4, 80),    # fallback if the mixture threshold falls outside this range: 2 x median gap
    dp_line=dict(skip=0.7, merge_pen=0.15, max_group=3),
    dp_word=dict(skip=1.0, merge_pen=0.10, max_group=3),
    clean_rule="|detected lines - ZL3b loci| <= 2",
)


# ----------------------------------------------------------------------------- A. page mapping
def zl_pages():
    """ZL3b records grouped by page in file order: list of dict(id, meta, loci=[rec...])."""
    recs = vparse.load()
    pages, cur = [], None
    for r in recs:
        if cur is None or cur["id"] != r["page"]:
            cur = dict(id=r["page"], section=r["illus"], hand=r["hand"], lang=r["lang"], quire=r["quire"], loci=[])
            pages.append(cur)
        cur["loci"].append(r)
    return pages


def map_canvases(index, zl):
    ids = {p["id"] for p in zl}
    matched, unmatched = [], []
    for row in index:
        m = re.fullmatch(r"(\d+)([rv])", row["label"].strip())
        if not m:
            unmatched.append((row["label"], row["file"], "composite/partial canvas label"))
            continue
        base = f"f{m.group(1)}{m.group(2)}"
        cands = sorted(i for i in ids if i == base or re.fullmatch(re.escape(base) + r"\d", i))
        if cands == [base]:
            matched.append((base, row))
        elif not cands:
            unmatched.append((row["label"], row["file"], "no ZL3b page"))
        else:
            unmatched.append((row["label"], row["file"], f"ZL3b splits this canvas into {','.join(cands)}"))
    return matched, unmatched


# ----------------------------------------------------------------------------- B. kraken lines
def kraken_lines(im, model, device):
    from kraken import blla
    seg = blla.segment(im, model=model, device=device)
    out = []
    for ln in seg.lines:
        bl = np.asarray(ln.baseline, dtype=float)
        poly = np.asarray(ln.boundary, dtype=np.int32)
        if len(poly) < 3:
            continue
        o = np.argsort(bl[:, 0])
        out.append(dict(baseline=bl.tolist(), poly=poly.tolist(), y_left=float(bl[o[0], 1]), y_right=float(bl[o[-1], 1]),
                        x0=int(poly[:, 0].min()), x1=int(poly[:, 0].max()),
                        y0=int(poly[:, 1].min()), y1=int(poly[:, 1].max()),
                        yb=float(bl[:, 1].mean())))
    return out


def line_pitch(lines):
    """Median spacing between consecutive distinct baselines (fragments on one row collapse)."""
    if not lines:
        return 100.0
    wmax = max(ln["x1"] - ln["x0"] for ln in lines)
    wide = [ln for ln in lines if ln["x1"] - ln["x0"] > 0.5 * wmax]
    ys = sorted(ln["yb"] for ln in wide)
    h = float(np.median([ln["y1"] - ln["y0"] for ln in lines]))
    d = [b - a for a, b in zip(ys, ys[1:]) if b - a > 0.25 * h]
    return float(np.median(d)) if d else h


def drop_margin_marks(lines, pitch):
    """Remove short segments outside the text block (margin stars, folio numbers, quire marks)."""
    wide = [ln for ln in lines if ln["x1"] - ln["x0"] > 5 * pitch]
    if not wide:
        return lines, 0
    L = float(np.percentile([ln["x0"] for ln in wide], 10)); R = float(np.percentile([ln["x1"] for ln in wide], 90))
    keep = []
    for ln in lines:
        w = ln["x1"] - ln["x0"]
        if w < 0.6 * pitch:
            continue
        if w < 2 * pitch and (ln["x1"] < L + 0.5 * pitch or ln["x0"] > R - 0.5 * pitch):
            continue
        keep.append(ln)
    return keep, len(lines) - len(keep)


def merge_rows(lines, row_tol, pitch):
    """Merge horizontally disjoint fragments on the same row; returns lines in reading order."""
    if not lines:
        return [], 0
    lines = sorted(lines, key=lambda ln: ln["yb"])
    rows = []
    for ln in lines:
        placed = False
        for row in rows:
            rx0, rx1 = min(m["x0"] for m in row), max(m["x1"] for m in row)
            w = ln["x1"] - ln["x0"]
            if ln["x0"] >= rx1 - 0.1 * w:        # new segment lies to the right of the row
                ref = max(row, key=lambda m: m["x1"])
                dy = abs(ref["y_right"] - ln["y_left"])
            elif ln["x1"] <= rx0 + 0.1 * w:      # to the left
                ref = min(row, key=lambda m: m["x0"])
                dy = abs(ref["y_left"] - ln["y_right"])
            else:
                continue
            if dy < row_tol * pitch:
                row.append(ln)
                placed = True
                break
        if not placed:
            rows.append([ln])
    merged = 0
    out = []
    for row in rows:
        row.sort(key=lambda m: m["x0"])
        if len(row) > 1:
            merged += len(row) - 1
        out.append(dict(parts=row, yb=float(np.mean([m["yb"] for m in row])),
                        x0=min(m["x0"] for m in row), x1=max(m["x1"] for m in row),
                        y0=min(m["y0"] for m in row), y1=max(m["y1"] for m in row)))
    out.sort(key=lambda r: r["yb"])
    return out, merged


# ----------------------------------------------------------------------------- C. ink profile
def binarize(gray):
    import cv2
    b = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                              PARAMS["block_size"], PARAMS["C"])
    k = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(b, cv2.MORPH_OPEN, k, iterations=1)


def ink_runs(binimg, row, pitch):
    """Column ink profile inside the row's polygons, restricted to a band around each part's baseline
    -> list of raw runs (x0, x1, mass)."""
    import cv2
    x0, x1, y0, y1 = row["x0"], row["x1"], row["y0"], row["y1"]
    H, W = binimg.shape
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1 + 1), min(H, y1 + 1)
    if x1 <= x0 or y1 <= y0:
        return [], np.zeros(0)
    mask = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for p in row["parts"]:
        poly = np.asarray(p["poly"], np.int32) - np.array([x0, y0], np.int32)
        cv2.fillPoly(mask, [poly], 1)
    crop = (binimg[y0:y1, x0:x1] > 0) & (mask > 0)
    cs = np.zeros((crop.shape[0] + 1, crop.shape[1]), np.int32)
    cs[1:] = np.cumsum(crop, axis=0)
    up, down = PARAMS["band"]
    prof = np.zeros(crop.shape[1], np.int32)
    for p in row["parts"]:
        bl = np.asarray(p["baseline"], float)
        bx, by = bl[:, 0] - x0, bl[:, 1] - y0
        order = np.argsort(bx); bx, by = bx[order], by[order]
        cx0, cx1 = max(0, p["x0"] - x0), min(crop.shape[1], p["x1"] - x0 + 1)
        xs = np.arange(cx0, cx1)
        yb = np.interp(xs, bx, by)
        lo = np.clip(np.round(yb - up * pitch).astype(int), 0, crop.shape[0])
        hi = np.clip(np.round(yb + down * pitch).astype(int), 0, crop.shape[0])
        prof[xs] = np.maximum(prof[xs], cs[hi, xs] - cs[lo, xs])
    ink = prof >= PARAMS["col_min_ink"]
    runs = []
    i = 0
    n = len(ink)
    while i < n:
        if ink[i]:
            j = i
            while j < n and ink[j]:
                j += 1
            runs.append([x0 + i, x0 + j, int(prof[i:j].sum())])
            i = j
        else:
            i += 1
    return runs, prof


def drop_specks(runs):
    if not runs:
        return runs, 0
    masses = np.array([r[2] for r in runs], float)
    med = float(np.median(masses))
    keep = [r for r in runs if r[2] >= PARAMS["speck_frac"] * med and (r[1] - r[0]) >= PARAMS["min_run_width"]]
    return keep, len(runs) - len(keep)


def gaps_of(runs):
    return [runs[k + 1][0] - runs[k][1] for k in range(len(runs) - 1)]


def em_mixture(x, K=3, iters=300):
    """1-D K-Gaussian EM on log widths; returns dict(mu, sd, w, thr), thr (linear units) = posterior-0.5
    crossing between the two upper components."""
    x = np.asarray(x, float)
    lx = np.log(np.maximum(x, 1.0))
    if len(lx) < 20 or np.ptp(lx) < 1e-6:
        return None
    mu = np.percentile(lx, np.linspace(100 / (K + 1), 100 * K / (K + 1), K))
    sd = np.full(K, max(lx.std() / K, 0.15)); w = np.full(K, 1.0 / K)
    for _ in range(iters):
        ll = -0.5 * ((lx[:, None] - mu) / sd) ** 2 - np.log(sd) + np.log(w)
        ll -= ll.max(axis=1, keepdims=True)
        r = np.exp(ll); r /= r.sum(axis=1, keepdims=True)
        nk = r.sum(axis=0) + 1e-9
        mu_new = (r * lx[:, None]).sum(axis=0) / nk
        sd = np.maximum(np.sqrt((r * (lx[:, None] - mu_new) ** 2).sum(axis=0) / nk), 0.15)
        w = nk / len(lx)
        if np.abs(mu_new - mu).max() < 1e-6:
            mu = mu_new
            break
        mu = mu_new
    order = np.argsort(mu)
    mu, sd, w = mu[order], sd[order], w[order]
    grid = np.linspace(mu[-2], mu[-1], 2000)
    post1 = np.exp(-0.5 * ((grid - mu[-1]) / sd[-1]) ** 2) / sd[-1] * w[-1]
    post0 = np.exp(-0.5 * ((grid - mu[-2]) / sd[-2]) ** 2) / sd[-2] * w[-2]
    cross = np.where(post1 >= post0)[0]
    thr_log = float(grid[cross[0]]) if len(cross) else float((mu[-2] + mu[-1]) / 2)
    return dict(mu=np.exp(mu).tolist(), sd=sd.tolist(), w=w.tolist(), thr=float(math.exp(thr_log)))


def page_threshold(all_gaps):
    mix = em_mixture([g for g in all_gaps if g >= PARAMS["mix_min_gap"]], K=PARAMS["mix_K"])
    lo, hi = PARAMS["thr_clip_px"]
    med = float(np.median(all_gaps)) if all_gaps else 10.0
    if mix is None or not (lo <= mix["thr"] <= hi) or mix["w"][-1] < 0.05:
        return dict(thr=float(np.clip(2 * med, lo, hi)), source="fallback 2*median", mix=mix, n=len(all_gaps))
    return dict(thr=mix["thr"], source="mixture", mix=mix, n=len(all_gaps))


def tokens_from_runs(runs, thr):
    """Merge runs across gaps < thr -> ink tokens with width, mass and flanking gaps."""
    if not runs:
        return []
    toks = [dict(x0=runs[0][0], x1=runs[0][1], mass=runs[0][2], nruns=1)]
    for k in range(1, len(runs)):
        g = runs[k][0] - runs[k - 1][1]
        if g < thr:
            t = toks[-1]
            t["x1"] = runs[k][1]; t["mass"] += runs[k][2]; t["nruns"] += 1
        else:
            toks.append(dict(x0=runs[k][0], x1=runs[k][1], mass=runs[k][2], nruns=1))
    for k, t in enumerate(toks):
        t["w"] = t["x1"] - t["x0"]
        t["gap_l"] = None if k == 0 else toks[k]["x0"] - toks[k - 1]["x1"]
        t["gap_r"] = None if k == len(toks) - 1 else toks[k + 1]["x0"] - toks[k]["x1"]
    return toks


# ----------------------------------------------------------------------------- D. alignment DP
def align(a, b, skip, merge_pen, max_group=3):
    """Monotone alignment of sizes a (ink) to sizes b (transliteration).
    Ops: (i_count, j_count) in {(1,1),(1,2..G),(2..G,1),(1,0),(0,1)}.
    Cost of a group = |sum a - sum b| / max(sum a, sum b, 1) + merge_pen * (extra members).
    Returns list of (ia_slice, jb_slice) groups and the mean cost over non-skip ops."""
    n, m = len(a), len(b)
    INF = float("inf")
    D = np.full((n + 1, m + 1), INF); D[0, 0] = 0.0
    back = {}
    ca = np.concatenate([[0.0], np.cumsum(a)]); cb = np.concatenate([[0.0], np.cumsum(b)])
    for i in range(n + 1):
        for j in range(m + 1):
            d = D[i, j]
            if d == INF:
                continue
            if i < n and D[i + 1, j] > d + skip:
                D[i + 1, j] = d + skip; back[(i + 1, j)] = (i, j)
            if j < m and D[i, j + 1] > d + skip:
                D[i, j + 1] = d + skip; back[(i, j + 1)] = (i, j)
            for p in range(1, max_group + 1):
                for q in range(1, max_group + 1):
                    if p > 1 and q > 1:
                        continue
                    if i + p > n or j + q > m:
                        continue
                    sa = ca[i + p] - ca[i]; sb = cb[j + q] - cb[j]
                    c = abs(sa - sb) / max(sa, sb, 1.0) + merge_pen * (p + q - 2)
                    if D[i + p, j + q] > d + c:
                        D[i + p, j + q] = d + c; back[(i + p, j + q)] = (i, j)
    groups = []
    i, j = n, m
    while (i, j) != (0, 0):
        pi, pj = back[(i, j)]
        groups.append(((pi, i), (pj, j)))
        i, j = pi, pj
    groups.reverse()
    costs = []
    for (i0, i1), (j0, j1) in groups:
        if i1 > i0 and j1 > j0:
            sa = ca[i1] - ca[i0]; sb = cb[j1] - cb[j0]
            costs.append(abs(sa - sb) / max(sa, sb, 1.0))
    return groups, (float(np.mean(costs)) if costs else 1.0)


GLYPH_RE = re.compile("|".join(sorted(map(re.escape, GLYPHS_PLUS), key=len, reverse=True)) + "|.")


def glyphs(tok):
    return GLYPH_RE.findall(tok)


def split_token(tok, fracs):
    """Cut tok at glyph boundaries nearest the cumulative width fractions (len(fracs) = pieces - 1)."""
    g = glyphs(tok)
    cuts, prev = [], 0
    for f in fracs:
        c = int(round(f * len(g)))
        c = min(max(c, prev + 1), len(g) - (len(fracs) - len(cuts) - 1) - 1)
        if c <= prev or c >= len(g):
            return None
        cuts.append(c); prev = c
    pieces, s = [], 0
    for c in cuts + [len(g)]:
        pieces.append("".join(g[s:c])); s = c
    return pieces


def resegment_line(ink_toks, words):
    """Returns (new_tokens, n_merge, n_split, n_dropped_ink, confidence, counts_equal)."""
    if not ink_toks or not words:
        return list(words), 0, 0, len(ink_toks), 0.0, False
    if len(ink_toks) == len(words):
        return list(words), 0, 0, 0, 1.0, True
    widths = [float(t["w"]) for t in ink_toks]
    chars = [float(len(glyphs(w))) for w in words]
    ppc = sum(widths) / max(sum(chars), 1.0)
    a = [w / ppc for w in widths]
    groups, cost = align(a, chars, PARAMS["dp_word"]["skip"], PARAMS["dp_word"]["merge_pen"], PARAMS["dp_word"]["max_group"])
    out, nm, ns, ndrop = [], 0, 0, 0
    for (i0, i1), (j0, j1) in groups:
        ni, nj = i1 - i0, j1 - j0
        if nj == 0:
            ndrop += ni
        elif ni == 0:
            out.extend(words[j0:j1])          # transliteration token with no ink: kept as is
        elif ni == 1 and nj == 1:
            out.append(words[j0])
        elif ni == 1:
            out.append("".join(words[j0:j1])); nm += nj - 1
        else:                                  # ni >= 2 ink tokens for one word: split by width share
            ws = widths[i0:i1]; tot = sum(ws)
            fr = np.cumsum(ws)[:-1] / tot
            pieces = split_token(words[j0], fr.tolist())
            if pieces is None:
                out.append(words[j0])
            else:
                out.extend(pieces); ns += len(pieces) - 1
    return out, nm, ns, ndrop, max(0.0, 1.0 - cost), False


# ----------------------------------------------------------------------------- per page
def process_page(pid, row, zpage, model, device, log):
    import cv2
    from PIL import Image
    t0 = time.time()
    path = SCANS / "pages" / row["file"]
    im = Image.open(path).convert("RGB")
    lines_raw = kraken_lines(im, model, device)
    pitch = line_pitch(lines_raw)
    lines_kept, n_margin_dropped = drop_margin_marks(lines_raw, pitch)
    rows, n_row_merged = merge_rows(lines_kept, PARAMS["row_tol"], pitch)
    gray = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY)
    binimg = binarize(gray)
    all_gaps, per_row, n_specks = [], [], 0
    for r in rows:
        runs, _ = ink_runs(binimg, r, pitch)
        runs, ns = drop_specks(runs)
        n_specks += ns
        per_row.append(runs)
        all_gaps.extend(gaps_of(runs))
    thr = page_threshold(all_gaps)
    det = []
    for r, runs in zip(rows, per_row):
        toks = tokens_from_runs(runs, thr["thr"])
        det.append(dict(yb=r["yb"], bbox=[r["x0"], r["y0"], r["x1"], r["y1"]], n_parts=len(r["parts"]),
                        baselines=[p["baseline"] for p in r["parts"]], polys=[p["poly"] for p in r["parts"]],
                        n_runs=len(runs), tokens=toks))
    det = [d for d in det if d["tokens"]]
    loci = zpage["loci"]
    b = [float(sum(len(glyphs(w)) for w in l["words"])) for l in loci]
    wsum = [float(sum(t["w"] for t in d["tokens"])) for d in det]
    ppg = sum(wsum) / max(sum(b), 1.0)
    a = [w / ppg for w in wsum]
    groups, line_cost = align(a, b, PARAMS["dp_line"]["skip"], PARAMS["dp_line"]["merge_pen"], PARAMS["dp_line"]["max_group"])
    # word-level alignment within P-line groups
    reseg_lines, relined_lines, align_rows = [], [], []
    tot = dict(merge=0, split=0, drop_ink=0, lines_1to1=0, lines_aligned=0, lines_P=0, lines_unaligned=0,
               line_groups_merge=0, line_groups_split=0, det_skipped=0, loci_skipped=0)
    for (i0, i1), (j0, j1) in groups:
        ni, nj = i1 - i0, j1 - j0
        if nj == 0:
            tot["det_skipped"] += ni
            continue
        units = [loci[j]["unit"] for j in range(j0, j1)]
        is_P = all(u.startswith("P") for u in units)
        words_all = [w for j in range(j0, j1) for w in loci[j]["words"]]
        if not is_P:
            if ni == 0:
                tot["loci_skipped"] += nj
            continue
        tot["lines_P"] += nj
        if ni == 0:
            tot["loci_skipped"] += nj; tot["lines_unaligned"] += nj
            for j in range(j0, j1):
                reseg_lines.append(dict(tokens=list(loci[j]["words"]), src="translit", conf=0.0))
                relined_lines.append(dict(tokens=list(loci[j]["words"]), src="translit"))
            align_rows.append(dict(det=[], loci=list(range(j0, j1)), op="miss"))
            continue
        ink = [t for i in range(i0, i1) for t in det[i]["tokens"]]
        tot["lines_aligned"] += nj
        if ni == 1 and nj == 1:
            tot["lines_1to1"] += 1
        elif ni == 1:
            tot["line_groups_merge"] += 1
        else:
            tot["line_groups_split"] += 1
        new, nm, ns, nd, conf, eq = resegment_line(ink, words_all)
        tot["merge"] += nm; tot["split"] += ns; tot["drop_ink"] += nd
        # ink-resegmented tokens, re-lined by the ink line breaks: distribute by cumulative ink-token count
        counts = [len(det[i]["tokens"]) for i in range(i0, i1)]
        reseg_lines.extend(_distribute(new, counts, src="ink", conf=conf))
        relined_lines.extend(_distribute(words_all, counts, src="ink"))
        align_rows.append(dict(det=list(range(i0, i1)), loci=list(range(j0, j1)), op=f"{ni}:{nj}",
                               n_ink=len(ink), n_words=len(words_all), conf=round(conf, 3), counts_equal=eq))
    n_loci = len(loci)
    delta = len(det) - n_loci
    rec = dict(id=pid, file=row["file"], label=row["label"], size=[im.width, im.height],
               section=zpage["section"], hand=zpage["hand"], lang=zpage["lang"], quire=zpage["quire"],
               n_kraken_lines=len(lines_raw), n_margin_dropped=n_margin_dropped, n_row_merged=n_row_merged, n_detected=len(det), n_loci=n_loci,
               n_P=sum(1 for l in loci if l["unit"].startswith("P")), delta=delta, clean=abs(delta) <= 2,
               n_specks=n_specks, threshold=thr, pitch=round(pitch, 1), px_per_glyph=round(ppg, 2), line_align_cost=round(line_cost, 4), totals=tot,
               elapsed=round(time.time() - t0, 1))
    page_json = dict(rec, lines=det, alignment=align_rows,
                     reseg_lines=reseg_lines, relined_lines=relined_lines)
    (PAGES_OUT / f"{pid}.json").write_text(json.dumps(page_json), encoding="utf-8")
    log(f"{pid:8} det={len(det):3d} loci={n_loci:3d} P={rec['n_P']:3d} d={delta:+3d} {'ok ' if rec['clean'] else 'FLAG'} "
        f"thr={thr['thr']:5.1f}px({thr['source'][:4]}) gaps={thr['n']:5d} merge={tot['merge']:3d} split={tot['split']:3d} "
        f"1to1={tot['lines_1to1']:3d}/{tot['lines_P']:3d} conf={line_cost:.2f} {rec['elapsed']:.0f}s")
    return rec, reseg_lines, relined_lines


def _distribute(tokens, counts, **extra):
    """Split a token list over len(counts) lines in proportion to the ink-token counts."""
    if len(counts) == 1:
        return [dict(tokens=list(tokens), **extra)]
    tot = sum(counts); n = len(tokens)
    cuts = [int(round(n * sum(counts[:k + 1]) / tot)) for k in range(len(counts) - 1)]
    out, s = [], 0
    for c in cuts + [n]:
        out.append(dict(tokens=list(tokens[s:c]), **extra)); s = c
    return out


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pages", help="comma-separated ZL3b ids to run (debug)")
    ap.add_argument("--resume", action="store_true", help="skip pages whose runs/s45/pages/<id>.json exists")
    args = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True); PAGES_OUT.mkdir(exist_ok=True)
    logf = (OUT / "segment_scans.log").open("a", encoding="utf-8")

    def log(s=""):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()

    import subprocess
    try:
        clock = subprocess.run(["date"], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001
        clock = "clock unavailable"
    log(f"=== segment_scans.py start {clock} device={args.device}")
    (OUT / "segment_params.json").write_text(json.dumps(PARAMS, indent=1), encoding="utf-8")

    index = json.loads((SCANS / "pages_index.json").read_text(encoding="utf-8"))
    zl = zl_pages()
    zmap = {p["id"]: p for p in zl}
    matched, unmatched = map_canvases(index, zl)
    log(f"canvases: {len(index)}; matched single-folio pages: {len(matched)}; unmatched: {len(unmatched)}")
    for lbl, f, why in unmatched:
        log(f"  unmatched canvas {lbl!r} ({f}): {why}")
    zl_unmatched = sorted(set(zmap) - {pid for pid, _ in matched})
    log(f"ZL3b pages without a usable canvas ({len(zl_unmatched)}): {' '.join(zl_unmatched)}")
    if args.pages:
        want = set(args.pages.split(","))
        matched = [(p, r) for p, r in matched if p in want]
    if args.limit:
        matched = matched[: args.limit]

    import torch
    from kraken.lib import vgsl
    import kraken, os
    model = vgsl.TorchVGSLModel.load_model(os.path.join(os.path.dirname(kraken.__file__), "blla.mlmodel"))
    log(f"torch {torch.__version__} cuda={torch.cuda.is_available()} model=kraken/blla.mlmodel")

    recs, reseg, relined = [], [], []
    t0 = time.time()
    for k, (pid, row) in enumerate(matched, 1):
        zpage = zmap[pid]
        if not any(l["unit"].startswith("P") for l in zpage["loci"]):
            log(f"{pid:8} no P lines in ZL3b; skipped"); continue
        pj = PAGES_OUT / f"{pid}.json"
        if args.resume and pj.exists():
            d = json.loads(pj.read_text(encoding="utf-8"))
            rec = {k2: v for k2, v in d.items() if k2 not in ("lines", "alignment", "reseg_lines", "relined_lines")}
            rl, ll = d["reseg_lines"], d["relined_lines"]
            log(f"{pid:8} resumed from {pj.name}")
        else:
            try:
                rec, rl, ll = process_page(pid, row, zpage, model, args.device, log)
            except Exception as e:  # noqa: BLE001
                log(f"{pid:8} ERROR {type(e).__name__}: {e}"); continue
        recs.append(rec)
        meta = dict(id=pid, section=zpage["section"], hand=zpage["hand"], lang=zpage["lang"], quire=zpage["quire"])
        reseg.append(dict(meta, lines=[[t for t in ln["tokens"] if "?" not in t] for ln in rl]))
        relined.append(dict(meta, lines=[[t for t in ln["tokens"] if "?" not in t] for ln in ll]))
        if k % 10 == 0:
            log(f"--- {k}/{len(matched)} pages, {(time.time() - t0) / 60:.1f} min")

    # summary + sidecars
    clean = [r for r in recs if r["clean"]]
    summ = dict(params=PARAMS, n_pages=len(recs), n_clean=len(clean), clean_ids=[r["id"] for r in clean],
                unmatched_canvases=[dict(label=l, file=f, why=w) for l, f, w in unmatched],
                zl_pages_without_canvas=zl_unmatched, pages=recs)
    (OUT / "segment_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    for name, pages in (("ink_ZL3b", reseg), ("ink_lines_ZL3b", relined)):
        side = dict(name=name, source="tools/segment_scans.py (kraken blla on Yale IIIF scans + data/ZL3b-n.txt)",
                    pages=[dict(p, lines=[ln for ln in p["lines"] if ln]) for p in pages])
        side["pages"] = [p for p in side["pages"] if p["lines"]]
        (OUT / f"{name}.meta.json").write_text(json.dumps(side, indent=1), encoding="utf-8")
    T = {k: sum(r["totals"][k] for r in recs) for k in recs[0]["totals"]} if recs else {}
    log(f"=== done: {len(recs)} pages, clean={len(clean)}; merges={T.get('merge')} splits={T.get('split')} "
        f"P-lines={T.get('lines_P')} aligned={T.get('lines_aligned')} 1to1={T.get('lines_1to1')}; "
        f"{(time.time() - t0) / 60:.1f} min")
    logf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
