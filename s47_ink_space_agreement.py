#!/usr/bin/env python
"""s47: does the ink agree with the transcribers' word spaces?  (word half of O-048)

PRE-REGISTRATION (frozen in s47_ink_space_agreement.prereg.sha256 before the scoring run; the stub
also pins tools/segment_scans.py and vparse.py, which this script imports).  No agreement number was
computed before freezing: the code was exercised only on a synthetic in-memory two-page fixture
(--selftest).

Commission design (verbatim, 23:34 claim of prefix s47):
- Unit: every between-glyph position inside a ZL3b paragraph line on the 127 clean s45 pages
  (|Δ lines| ≤ 2) where the s45 alignment maps the adjacent glyphs to ink with confidence at or above
  the s45 default (state the threshold used). Transcription class per position: certain space `.`,
  uncertain space `,`, no space. Ink class: measured gap width at that position relative to the
  page's s45 word-gap threshold, binned as ink-space (≥ threshold) vs ink-no-space (< threshold);
  also report the raw width distribution per transcription class.
- Statistics: Cohen's κ between ink class and {certain space} vs {no space}, with uncertain spaces
  excluded (κ_certain); κ with uncertain spaces counted as spaces (κ_comma=space) and as no-space
  (κ_comma=join); ROC AUC of raw gap width separating certain space from no space; median gap widths
  per class with page-bootstrap 95 % intervals (B=1000); the same for positions adjacent to gallows
  (k,t,p,f, and ckh/cth/cph/cfh) vs not.
- Fixed predictions: P1 κ_certain ≥ 0.6 (the phase-4-units criterion) → ink agrees with the certain
  spaces; P2 uncertain-space median width lies strictly between the certain-space and no-space
  medians (intervals non-overlapping with both) → commas are physically intermediate (as R–T 2026 and
  P4-U1 suggest); P3 at internal gallows positions marked as no-space by ZL, the share of ink-space
  calls is at least twice the share at non-gallows no-space positions → the s38 pen-lift effect is a
  physical gap, not a transcription artefact.
- Reading rule: if P1 holds, the s45 P2/P3 failures are attributed to s45's alignment noise, and the
  transcription's spaces stand as the word unit; if P1 fails, report the κ and state that word-level
  metrics depend on a boundary choice the ink does not settle. Report P2 and P3 independently. Print
  margins.

Operational definitions (fixed here, before scoring):
  Inputs (read only): runs/s45/segment_summary.json (clean_ids), runs/s45/pages/<id>.json,
    data/ZL3b-n.txt (re-parsed keeping `.` / `,` / `<->`; the word lists must equal vparse.load()
    word lists record by record or the run aborts), the Yale JPEGs named in each page JSON
    (data/external/yale_scans/pages/, already local; only used to recover raw ink-run gaps).
  Lines: s45 alignment rows with op "1:1" (one ink line <-> one ZL3b P locus).  s45 applies no
    confidence cut (every aligned line enters its S1 stream), so the s45 default threshold is
    conf ≥ 0.0 (CONF_MIN); conf ≥ 0.9 is reported as a sensitivity row only.  Multi-line groups
    (1:2, 2:1, ...) and misses are excluded.  A line is also excluded if re-running s45's own
    word DP (tools/segment_scans.resegment_line / align) does not reproduce the stored reseg tokens.
  Glyphs: tools/segment_scans.py glyphs (GLYPHS_PLUS units: ch, sh, cth, ckh, cph, cfh, iin, ...).
    Positions = boundaries between consecutive glyphs within the line.  Excluded: positions at a
    drawing interruption `<->`, positions adjacent to a glyph that is not [a-z]+ (e.g. `?`), and
    positions inside or bordering a DP group that has no ink or no words (skip ops).
  Ink class (the s45 call, from the stored ink tokens; tokens are runs merged across gaps < the page
    threshold thr):
    - boundary between two consecutive mapped DP groups -> ink-space; width = the stored gap
      between the two ink tokens (≥ thr by construction);
    - inside a group with one ink token -> ink-no-space (this includes ZL spaces merged by the ink);
    - inside a group of one word and ≥ 2 ink tokens -> the s45 split rule (split_token, cut at the
      glyph boundary nearest the cumulative ink-width share) gives the ink-space positions, width =
      the stored inter-token gap; other positions ink-no-space.  If split_token returns None the
      word's internal positions are excluded.
  Raw width at ink-no-space positions: the s45 page JSON keeps tokens, not raw runs, so the raw runs
    are re-derived by a numpy/scipy port of segment_scans step C (cv2 RGB2GRAY fixed-point
    weights, Gaussian adaptive threshold 51/σ=8/C=18 with replicated border, 3x3 opening, polygon
    mask, baseline band with the stored pitch, speck drop).  Reproduction gate per line: the port
    must give the stored n_runs and, merged at the stored thr, the same number of ink tokens with
    every x0/x1 within ±2 px.  Lines failing the gate keep their ink class (κ, P1, P3) but give no
    raw widths.  On gate lines the width at an ink-no-space position = the widest raw inter-run gap
    inside the token whose span intersects [x - h, x + h], x = glyph-share position of the boundary
    within its ink token, h = half a glyph (token width / glyphs in it / 2); 0 px if none (ink
    continuous).  Widths are analysed as r = width / thr (page-normalised); px are also printed.
  Classes: D = certain space `.`, C = uncertain space `,` (a `.,` / `,.` run counts as D),
    N = no space (word-internal).
  κ = Cohen's κ on the 2x2 table; κ_certain uses D vs N (C excluded); κ_comma=space uses D+C vs N;
    κ_comma=join uses D vs C+N.  AUC = Mann-Whitney AUC of r (ties 0.5), D vs N, gate lines only.
  Bootstrap: pages resampled with replacement, B = 1000, seed 20261017; percentile 95 % intervals.
  Gallows-adjacent: either flanking glyph in {k, t, p, f, ckh, cth, cph, cfh}.
  P1: κ_certain (all eligible positions, conf ≥ CONF_MIN) ≥ 0.6; margin = κ - 0.6.
  P2 (gate lines, r): median_N < median_C < median_D and CI_C.lo > CI_N.hi and CI_C.hi < CI_D.lo;
    margins = CI_C.lo - CI_N.hi and CI_D.lo - CI_C.hi (both must be > 0).
  P3: share(ink-space | N, gallows-adjacent) / share(ink-space | N, not gallows-adjacent) ≥ 2;
    margin = ratio - 2; page-bootstrap interval of the ratio reported.
  Reported, not predictions: κ_certain on lines whose ink-token count equals the ZL word count
    (s45 then pairs tokens 1:1 without a DP, so agreement there is by construction) vs on lines
    where the counts differ (the DP had to choose); conf ≥ 0.9 row; per-class width quantiles.

Outputs: results_s47.txt; runs/s47/positions.tsv (one row per position); runs/s47/lines.tsv (line
gate log).  Run: python -I s47_ink_space_agreement.py   (--selftest runs the synthetic fixture only).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SELF = ROOT / "s47_ink_space_agreement.py"
STUB = ROOT / "s47_ink_space_agreement.prereg.sha256"
OUT = ROOT / "results_s47.txt"
S45 = ROOT / "runs" / "s45"
RUN = ROOT / "runs" / "s47"
SCANS = ROOT / "data" / "external" / "yale_scans" / "pages"
ZL = ROOT / "data" / "ZL3b-n.txt"

CONF_MIN = 0.0
CONF_SENS = 0.9
GATE_PX = 2
B = 1000
SEED = 20261017
KAPPA_MIN = 0.6
P3_RATIO = 2.0
GALLOWS = {"k", "t", "p", "f", "ckh", "cth", "cph", "cfh"}
AZ = re.compile(r"[a-z]+")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SEG = _load("segment_scans_s47", ROOT / "tools" / "segment_scans.py")
import vparse  # noqa: E402


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        return subprocess.run(["date"], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001
        return "clock unavailable"


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


# ----------------------------------------------------------------------------- ZL3b with separators
def clean_seps(text):
    """vparse.clean, but keeping separator classes: returns (words, seps) with len(seps) = len(words)-1,
    seps in {'D' (certain .), 'C' (uncertain ,), 'I' (drawing interruption <->)}."""
    text = re.sub(r"<![^>]*>", "", text)
    text = re.sub(r"<->", "|", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", text)
    text = re.sub(r"@\d+;", "?", text)
    text = text.replace("{", "").replace("}", "").replace("'", "")
    parts = re.split(r"([.,|])", text)
    words, seps, pend = [], [], ""
    for p in parts:
        if p in (".", ",", "|"):
            pend += p
        elif p:
            if words:
                seps.append("I" if "|" in pend else ("D" if "." in pend else "C"))
            words.append(p)
            pend = ""
    return words, seps


def zl_with_seps():
    """Records in vparse.load() order with separator lists; asserts identical word lists."""
    recs = vparse.load()
    mine = []
    for raw in ZL.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        if vparse.PAGE_RE.match(raw):
            continue
        m = vparse.LINE_RE.match(raw)
        if not m:
            continue
        page, n, _, unit, text = m.groups()
        w, s = clean_seps(text)
        mine.append((page, int(n), w, s))
    assert len(mine) == len(recs), (len(mine), len(recs))
    for r, (pg, n, w, s) in zip(recs, mine):
        assert r["page"] == pg and r["line"] == n and r["words"] == w, (pg, n, r["words"], w)
    return {(pg, n): s for pg, n, w, s in mine}


# ----------------------------------------------------------------------------- step C port
def gray_cv2(rgb):
    r, g, b = (rgb[..., k].astype(np.int32) for k in range(3))
    return ((r * 4899 + g * 9617 + b * 1868 + 8192) >> 14).astype(np.uint8)


def binarize(gray):
    from scipy import ndimage
    bs, C = SEG.PARAMS["block_size"], SEG.PARAMS["C"]
    sigma = 0.3 * ((bs - 1) * 0.5 - 1) + 0.8
    rad = bs // 2
    xs = np.arange(-rad, rad + 1, dtype=np.float64)
    k = np.exp(-xs ** 2 / (2 * sigma ** 2)); k /= k.sum()
    f = gray.astype(np.float32)
    m = ndimage.correlate1d(f, k.astype(np.float32), axis=0, mode="nearest")
    m = ndimage.correlate1d(m, k.astype(np.float32), axis=1, mode="nearest")
    mean = np.floor(m + 0.5).astype(np.int32)
    ink = gray.astype(np.int32) - mean <= -C
    st = np.ones((3, 3), bool)
    er = ndimage.binary_erosion(ink, structure=st, border_value=1)
    return ndimage.binary_dilation(er, structure=st, border_value=0)


def poly_mask(shape, polys, off):
    from PIL import Image, ImageDraw
    h, w = shape
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    for poly in polys:
        pts = [(float(x - off[0]), float(y - off[1])) for x, y in poly]
        d.polygon(pts, fill=1, outline=1)
    return np.asarray(im) > 0


def ink_runs_port(binimg, line, pitch):
    """Port of segment_scans.ink_runs + drop_specks on a stored page-JSON line."""
    x0, y0, x1, y1 = line["bbox"]
    H, W = binimg.shape
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1 + 1), min(H, y1 + 1)
    if x1 <= x0 or y1 <= y0:
        return []
    mask = poly_mask((y1 - y0, x1 - x0), line["polys"], (x0, y0))
    crop = binimg[y0:y1, x0:x1] & mask
    cs = np.zeros((crop.shape[0] + 1, crop.shape[1]), np.int32)
    cs[1:] = np.cumsum(crop, axis=0)
    up, down = SEG.PARAMS["band"]
    prof = np.zeros(crop.shape[1], np.int32)
    for bl, poly in zip(line["baselines"], line["polys"]):
        bl = np.asarray(bl, float); pa = np.asarray(poly)
        bx, by = bl[:, 0] - x0, bl[:, 1] - y0
        o = np.argsort(bx); bx, by = bx[o], by[o]
        px0, px1 = int(pa[:, 0].min()), int(pa[:, 0].max())
        cx0, cx1 = max(0, px0 - x0), min(crop.shape[1], px1 - x0 + 1)
        if cx1 <= cx0:
            continue
        xs = np.arange(cx0, cx1)
        yb = np.interp(xs, bx, by)
        lo = np.clip(np.round(yb - up * pitch).astype(int), 0, crop.shape[0])
        hi = np.clip(np.round(yb + down * pitch).astype(int), 0, crop.shape[0])
        prof[xs] = np.maximum(prof[xs], cs[hi, xs] - cs[lo, xs])
    ink = prof >= SEG.PARAMS["col_min_ink"]
    runs, i, n = [], 0, len(ink)
    while i < n:
        if ink[i]:
            j = i
            while j < n and ink[j]:
                j += 1
            runs.append([x0 + i, x0 + j, int(prof[i:j].sum())])
            i = j
        else:
            i += 1
    runs, _ = SEG.drop_specks(runs)
    return runs


def gate(runs, line, thr):
    if len(runs) != line["n_runs"]:
        return False
    toks = SEG.tokens_from_runs(runs, thr)
    st = line["tokens"]
    if len(toks) != len(st):
        return False
    return all(abs(a["x0"] - b["x0"]) <= GATE_PX and abs(a["x1"] - b["x1"]) <= GATE_PX for a, b in zip(toks, st))


# ----------------------------------------------------------------------------- positions on one line
def word_groups(ink, words):
    """s45's word alignment groups (as resegment_line), plus the reseg tokens it produces."""
    if len(ink) == len(words):
        groups = [((k, k + 1), (k, k + 1)) for k in range(len(words))]
    else:
        widths = [float(t["w"]) for t in ink]
        chars = [float(len(SEG.glyphs(w))) for w in words]
        ppc = sum(widths) / max(sum(chars), 1.0)
        a = [w / ppc for w in widths]
        P = SEG.PARAMS["dp_word"]
        groups, _ = SEG.align(a, chars, P["skip"], P["merge_pen"], P["max_group"])
    new = SEG.resegment_line(ink, words)[0]
    return groups, new


def widest_gap(runs_in, x, h):
    best = 0
    for a, b in zip(runs_in, runs_in[1:]):
        g0, g1 = a[1], b[0]
        if g1 > g0 and g0 <= x + h and g1 >= x - h:
            best = max(best, g1 - g0)
    return best


def line_positions(ink, words, seps, runs):
    """Positions for one 1:1 line.  runs = gate-passing raw runs or None.
    Returns list of dict(cls, ink, w_px, gal) and an exclusion counter."""
    groups, _ = word_groups(ink, words)
    gl = [SEG.glyphs(w) for w in words]
    out, excl = [], dict(skip_group=0, split_none=0, interruption=0, nonaz=0)

    def emit(lg, rg, cls, inkc, w):
        if cls == "I":
            excl["interruption"] += 1; return
        if not (AZ.fullmatch(lg) and AZ.fullmatch(rg)):
            excl["nonaz"] += 1; return
        out.append(dict(cls=cls, ink=inkc, w_px=w, gal=(lg in GALLOWS or rg in GALLOWS)))

    def tok_runs(t):
        if runs is None:
            return None
        return [r for r in runs if r[0] >= t["x0"] - GATE_PX and r[1] <= t["x1"] + GATE_PX]

    def inside_token(t, gseq, bounds, clsseq):
        """gseq glyphs mapped to one ink token; bounds = internal boundary indices 1..n-1 with classes."""
        n = len(gseq)
        rin = tok_runs(t)
        for b, cls in zip(bounds, clsseq):
            w = None
            if rin is not None:
                x = t["x0"] + b / n * t["w"]
                w = widest_gap(rin, x, 0.5 * t["w"] / n)
            emit(gseq[b - 1], gseq[b], cls, 0, w)

    mapped = [(gi, g) for gi, g in enumerate(groups) if g[0][1] > g[0][0] and g[1][1] > g[1][0]]
    excl["skip_group"] += sum(1 for g in groups if not (g[0][1] > g[0][0] and g[1][1] > g[1][0]))
    for gi, ((i0, i1), (j0, j1)) in mapped:
        ni, nj = i1 - i0, j1 - j0
        if ni == 1:
            gseq, clsseq, bounds = [], [], []
            for j in range(j0, j1):
                if j > j0:
                    bounds.append(len(gseq)); clsseq.append(seps[j - 1])
                for k, g in enumerate(gl[j]):
                    if k > 0:
                        bounds.append(len(gseq)); clsseq.append("N")
                    gseq.append(g)
            inside_token(ink[i0], gseq, bounds, clsseq)
        else:  # ni >= 2, nj == 1
            g = gl[j0]
            toks = ink[i0:i1]
            ws = [t["w"] for t in toks]; tot = sum(ws)
            fr = (np.cumsum(ws)[:-1] / tot).tolist()
            pieces = SEG.split_token(words[j0], fr)
            if pieces is None:
                excl["split_none"] += max(0, len(g) - 1)
                continue
            s = 0
            for k, pc in enumerate(pieces):
                pg = SEG.glyphs(pc)
                inside_token(toks[k], pg, list(range(1, len(pg))), ["N"] * (len(pg) - 1))
                s += len(pg)
                if k < len(pieces) - 1:
                    w = toks[k + 1]["x0"] - toks[k]["x1"]
                    emit(g[s - 1], g[s], "N", 1, w if runs is not None else None)
        # boundary to the next group
        if gi + 1 < len(groups):
            (ni0, ni1), (nj0, nj1) = groups[gi + 1]
            if ni1 > ni0 and nj1 > nj0:
                w = ink[ni0]["x0"] - ink[i1 - 1]["x1"]
                emit(gl[j1 - 1][-1], gl[nj0][0], seps[j1 - 1], 1, w if runs is not None else None)
            else:
                excl["skip_group"] += 1
    return out, excl, groups


# ----------------------------------------------------------------------------- statistics
def kappa(a, b):
    a = np.asarray(a, bool); b = np.asarray(b, bool)
    n = len(a)
    if n == 0:
        return float("nan")
    po = np.mean(a == b)
    pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def auc(pos, neg):
    from scipy.stats import rankdata
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def boot(per_page, fn, rng, B=B):
    """per_page: list of per-page payloads; fn(list of payloads) -> float.  Percentile 95 % CI."""
    P = len(per_page)
    vals = []
    for _ in range(B):
        idx = rng.integers(0, P, P)
        vals.append(fn([per_page[i] for i in idx]))
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return (float("nan"), float("nan"))
    return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))


def analyse(pos_pages, emit, rng, label=""):
    """pos_pages: list (one per page) of structured arrays/dicts of positions with keys cls, ink, r, w_px, gal, ce, conf."""
    def cat(pages, key, sel=None):
        xs = []
        for p in pages:
            m = p["mask"] if sel is None else sel(p)
            xs.append(p[key][m])
        return np.concatenate(xs) if xs else np.zeros(0)

    def kap_fn(pages, mode, extra=None):
        cls = np.concatenate([p["cls"] for p in pages]); ink = np.concatenate([p["ink"] for p in pages])
        m = np.ones(len(cls), bool)
        if extra is not None:
            m &= np.concatenate([extra(p) for p in pages])
        if mode == "certain":
            m &= cls != "C"; t = cls == "D"
        elif mode == "space":
            t = (cls == "D") | (cls == "C")
        else:
            t = cls == "D"
        return kappa(ink[m] == 1, t[m])

    res = {}
    n = {c: int(sum((p["cls"] == c).sum() for p in pos_pages)) for c in "DCN"}
    emit(f"{label}positions: D(certain .)={n['D']}  C(uncertain ,)={n['C']}  N(no space)={n['N']}  pages={len(pos_pages)}")
    for c in "DCN":
        k1 = int(sum(((p["cls"] == c) & (p["ink"] == 1)).sum() for p in pos_pages))
        emit(f"{label}  ink-space calls in {c}: {k1}/{n[c]} = {k1 / max(n[c], 1):.4f}")
    for mode, nm in (("certain", "kappa_certain"), ("space", "kappa_comma=space"), ("join", "kappa_comma=join")):
        res[nm] = kap_fn(pos_pages, mode)
    ci = boot(pos_pages, lambda pg: kap_fn(pg, "certain"), rng)
    res["kappa_certain_ci"] = ci
    emit(f"{label}kappa_certain={res['kappa_certain']:.4f} [page-boot 95% {ci[0]:.4f}, {ci[1]:.4f}]  "
         f"kappa_comma=space={res['kappa_comma=space']:.4f}  kappa_comma=join={res['kappa_comma=join']:.4f}")
    # raw widths (gate lines)
    def wsel(c):
        return lambda p: (p["cls"] == c) & p["haw"]
    nr = {c: int(sum(wsel(c)(p).sum() for p in pos_pages)) for c in "DCN"}
    rD, rN = cat(pos_pages, "r", wsel("D")), cat(pos_pages, "r", wsel("N"))
    pD, pN = cat(pos_pages, "w_px", wsel("D")), cat(pos_pages, "w_px", wsel("N"))
    res["auc_r"] = auc(rD, rN); res["auc_px"] = auc(pD, pN)
    emit(f"{label}raw-width positions (gate lines): D={nr['D']} C={nr['C']} N={nr['N']}")
    emit(f"{label}AUC D vs N: r=width/thr {res['auc_r']:.4f}   px {res['auc_px']:.4f}")
    for c in "DCN":
        r = cat(pos_pages, "r", wsel(c)); px = cat(pos_pages, "w_px", wsel(c))
        if len(r) == 0:
            emit(f"{label}  {c}: no raw widths"); res[f"med_{c}"] = (float("nan"), (float("nan"),) * 2); continue
        med = float(np.median(r))
        ci = boot(pos_pages, lambda pg, c=c: (lambda z: float(np.median(z)) if len(z) else float("nan"))(
            np.concatenate([p["r"][wsel(c)(p)] for p in pg])), rng)
        res[f"med_{c}"] = (med, ci)
        q = np.percentile(r, [10, 25, 50, 75, 90]); qp = np.percentile(px, [10, 25, 50, 75, 90])
        emit(f"{label}  {c}: median r={med:.4f} [page-boot 95% {ci[0]:.4f}, {ci[1]:.4f}]  "
             f"r q10/25/50/75/90={'/'.join(f'{v:.3f}' for v in q)}  px q10/25/50/75/90={'/'.join(f'{v:.1f}' for v in qp)}  "
             f"share r=0 (continuous ink)={np.mean(r == 0):.3f}")
    return res


def to_arrays(rows):
    cls = np.array([r["cls"] for r in rows], dtype="<U1")
    ink = np.array([r["ink"] for r in rows], dtype=np.int8)
    haw = np.array([r["w_px"] is not None for r in rows], bool)
    w = np.array([r["w_px"] if r["w_px"] is not None else np.nan for r in rows], float)
    thr = np.array([r["thr"] for r in rows], float)
    return dict(cls=cls, ink=ink, haw=haw, w_px=w, r=w / thr, gal=np.array([r["gal"] for r in rows], bool),
                ce=np.array([r["ce"] for r in rows], bool), conf=np.array([r["conf"] for r in rows], float),
                mask=np.ones(len(rows), bool))


def subset(pages, f):
    out = []
    for p in pages:
        m = f(p)
        out.append({k: (v[m] if isinstance(v, np.ndarray) else v) for k, v in p.items()})
    return out


# ----------------------------------------------------------------------------- driver
def collect(page_iter, seps_of, zmap, rows_out, lines_out, excl_tot, image_loader):
    pos_pages = []
    for pj in page_iter:
        pid = pj["id"]
        loci = zmap[pid]["loci"]
        thr = float(pj["threshold"]["thr"])
        binimg = None
        rows = []
        # walk alignment rows and consume reseg_lines entries in order
        ri = 0
        for ar in pj["alignment"]:
            nent = len(ar["loci"]) if ar["op"] == "miss" else len(ar["det"])
            ents = pj["reseg_lines"][ri:ri + nent]; ri += nent
            if ar["op"] != "1:1" or len(ar["det"]) != 1 or len(ar["loci"]) != 1:
                excl_tot["not_1to1_rows"] += 1
                continue
            conf = float(ar.get("conf", 0.0))
            if conf < CONF_MIN:
                excl_tot["below_conf"] += 1; continue
            line = pj["lines"][ar["det"][0]]
            loc = loci[ar["loci"][0]]
            words = loc["words"]
            seps = seps_of[(pid, loc["line"])]
            ink = line["tokens"]
            groups, new = word_groups(ink, words)
            if [e["tokens"] for e in ents] != [new]:
                excl_tot["reseg_mismatch"] += 1
                lines_out.append(f"{pid}\t{loc['line']}\treseg_mismatch\t-\t{conf:.3f}")
                continue
            if binimg is None:
                binimg = image_loader(pj)
            runs = ink_runs_port(binimg, line, float(pj["pitch"])) if binimg is not None else None
            ok = runs is not None and gate(runs, line, thr)
            lines_out.append(f"{pid}\t{loc['line']}\t{'gate_ok' if ok else 'gate_fail'}\t{int(len(ink) == len(words))}\t{conf:.3f}")
            pos, excl, _ = line_positions(ink, words, seps, runs if ok else None)
            for k, v in excl.items():
                excl_tot[k] += v
            excl_tot["lines_used"] += 1; excl_tot["lines_gate_ok"] += int(ok)
            for p in pos:
                p.update(thr=thr, ce=len(ink) == len(words), conf=conf)
                rows.append(p)
                rows_out.append(f"{pid}\t{loc['line']}\t{p['cls']}\t{p['ink']}\t"
                                f"{'' if p['w_px'] is None else p['w_px']}\t{thr:.3f}\t{int(p['gal'])}\t{int(p['ce'])}\t{conf:.3f}")
        if rows:
            d = to_arrays(rows); d["page"] = pid
            pos_pages.append(d)
    return pos_pages


def report(pos_pages, emit, excl_tot):
    rng = np.random.default_rng(SEED)
    emit("=== exclusions / line log ===")
    emit("  " + "  ".join(f"{k}={v}" for k, v in excl_tot.items()))
    emit(f"  confidence threshold used: conf >= {CONF_MIN} (s45 default: no cut)")
    emit("")
    emit("=== all eligible positions (primary) ===")
    R = analyse(pos_pages, emit, rng)
    emit("")
    emit("=== gallows-adjacent positions ===")
    G = analyse(subset(pos_pages, lambda p: p["gal"]), emit, rng, "  [gal] ")
    emit("=== not gallows-adjacent ===")
    NG = analyse(subset(pos_pages, lambda p: ~p["gal"]), emit, rng, "  [non] ")
    emit("")
    emit("=== reported caveat rows (not predictions) ===")
    analyse(subset(pos_pages, lambda p: p["ce"]), emit, rng, "  [counts equal, 1:1 by construction] ")
    analyse(subset(pos_pages, lambda p: ~p["ce"]), emit, rng, "  [counts differ, DP placed] ")
    analyse(subset(pos_pages, lambda p: p["conf"] >= CONF_SENS), emit, rng, f"  [conf>={CONF_SENS}] ")
    emit("")
    # P3
    def share(pages, gal):
        num = sum(((p["cls"] == "N") & (p["gal"] == gal) & (p["ink"] == 1)).sum() for p in pages)
        den = sum(((p["cls"] == "N") & (p["gal"] == gal)).sum() for p in pages)
        return num / den if den else float("nan"), int(num), int(den)

    def _rat(a, b):
        if not (np.isfinite(a) and np.isfinite(b)):
            return float("nan")
        return a / b if b > 0 else (float("inf") if a > 0 else float("nan"))

    def ratio(pages):
        return _rat(share(pages, True)[0], share(pages, False)[0])
    sg, ng_, dg = share(pos_pages, True); sn, nn_, dn = share(pos_pages, False)
    rat = _rat(sg, sn)
    rci = boot(pos_pages, ratio, rng)

    emit("=== fixed predictions ===")
    k = R["kappa_certain"]
    p1 = k >= KAPPA_MIN
    emit(f"P1 kappa_certain = {k:.4f} [95% {R['kappa_certain_ci'][0]:.4f}, {R['kappa_certain_ci'][1]:.4f}] vs >= {KAPPA_MIN}: "
         f"margin {k - KAPPA_MIN:+.4f} -> {'HOLDS' if p1 else 'FAILS'}")
    (mD, cD), (mC, cC), (mN, cN) = R["med_D"], R["med_C"], R["med_N"]
    m1, m2 = cC[0] - cN[1], cD[0] - cC[1]
    p2 = (mN < mC < mD) and m1 > 0 and m2 > 0
    emit(f"P2 median r: N={mN:.4f} [{cN[0]:.4f},{cN[1]:.4f}]  C={mC:.4f} [{cC[0]:.4f},{cC[1]:.4f}]  D={mD:.4f} [{cD[0]:.4f},{cD[1]:.4f}]; "
         f"order N<C<D: {mN < mC < mD}; margins CI_C.lo-CI_N.hi={m1:+.4f}, CI_D.lo-CI_C.hi={m2:+.4f} -> {'HOLDS' if p2 else 'FAILS'}")
    p3 = bool(np.isfinite(rat) or rat == float("inf")) and rat >= P3_RATIO
    emit(f"P3 ink-space share at N positions: gallows-adjacent {ng_}/{dg}={sg:.4f}, not {nn_}/{dn}={sn:.4f}; "
         f"ratio={rat:.3f} [95% {rci[0]:.3f}, {rci[1]:.3f}] vs >= {P3_RATIO}: margin {rat - P3_RATIO:+.3f} -> {'HOLDS' if p3 else 'FAILS'}")
    emit("")
    if p1:
        emit("READING: P1 holds -> the ink agrees with the certain spaces; the s45 P2/P3 failures are attributed to "
             "s45's alignment noise, and the transcription's spaces stand as the word unit.")
    else:
        emit(f"READING: P1 fails (kappa_certain={k:.4f}) -> word-level metrics depend on a boundary choice the ink "
             "does not settle.")
    emit(f"  P2 (commas physically intermediate): {'HOLDS' if p2 else 'FAILS'};  P3 (gallows pen-lift is a physical gap): {'HOLDS' if p3 else 'FAILS'}")
    return dict(R=R, G=G, NG=NG, p1=p1, p2=p2, p3=p3)


def real_loader(pj):
    from PIL import Image
    path = SCANS / pj["file"]
    if not path.exists():
        return None
    rgb = np.asarray(Image.open(path).convert("RGB"))
    return binarize(gray_cv2(rgb))


def selftest():
    """Synthetic two-page fixture: drawn glyph boxes on a white page; checks the port, the gate,
    the position logic and that the statistics run.  No real page is touched."""
    from collections import Counter
    rng = np.random.default_rng(1)
    pages, zmap, seps_of, imgs = [], {}, {}, {}
    for pi, pid in enumerate(("fx1", "fx2")):
        H, W = 400, 1400
        img = np.full((H, W, 3), 235, np.uint8)
        words_l = [["daiin", "chol", "qokedy"], ["otol", "shey", "ckhy", "dar"]]
        seps_l = [["D", "C"], ["D", "D", "C"]]
        lines, align_rows, reseg, loci = [], [], [], []
        for li, (words, seps) in enumerate(zip(words_l, seps_l)):
            yb = 100 + 150 * li
            x = 60
            toks = []
            merge_second = (pi == 1 and li == 0)
            for wi, w in enumerate(words):
                g = SEG.glyphs(w)
                tx0 = x
                for gi_, _ in enumerate(g):
                    img[yb - 30:yb, x:x + 14] = 20
                    x += 14 + ((25 if (pi == 1 and li == 1 and wi == 1 and gi_ == 1) else 2) if gi_ < len(g) - 1 else 0)
                tx1 = x
                toks.append([tx0, tx1])
                if wi < len(words) - 1:
                    x += 4 if (merge_second and wi == 0) else 30
            # merge tokens closer than thr
            thr = 12.0
            merged = [toks[0][:]]
            for t in toks[1:]:
                if t[0] - merged[-1][1] < thr:
                    merged[-1][1] = t[1]
                else:
                    merged.append(t[:])
            poly = [[40, yb - 60], [x + 20, yb - 60], [x + 20, yb + 20], [40, yb + 20]]
            line = dict(bbox=[40, yb - 60, x + 20, yb + 20], polys=[poly], baselines=[[[40, yb], [x + 20, yb]]], tokens=[])
            for k, t in enumerate(merged):
                line["tokens"].append(dict(x0=t[0], x1=t[1], w=t[1] - t[0], mass=0, nruns=0,
                                           gap_l=None if k == 0 else t[0] - merged[k - 1][1],
                                           gap_r=None if k == len(merged) - 1 else merged[k + 1][0] - t[1]))
            lines.append(line)
            loci.append(dict(line=li + 1, unit="P0", words=words))
            seps_of[(pid, li + 1)] = seps
            align_rows.append(dict(det=[li], loci=[li], op="1:1", conf=0.95))
            reseg.append(dict(tokens=SEG.resegment_line(line["tokens"], words)[0]))
        b = binarize(gray_cv2(img))
        for line, words in zip(lines, words_l):
            runs = ink_runs_port(b, line, 100.0)
            line["n_runs"] = len(runs)
            line["tokens"] = SEG.tokens_from_runs(runs, 12.0)
        reseg = [dict(tokens=SEG.resegment_line(line["tokens"], words)[0]) for line, words in zip(lines, words_l)]
        imgs[pid] = b
        zmap[pid] = dict(loci=loci)
        pages.append(dict(id=pid, threshold=dict(thr=12.0), pitch=100.0, lines=lines, alignment=align_rows,
                          reseg_lines=reseg, file="none"))
    rows_out, lines_out, excl = [], [], Counter()
    pp = collect(pages, seps_of, zmap, rows_out, lines_out, excl, lambda pj: imgs[pj["id"]])
    print("selftest lines:", lines_out)
    print("selftest excl:", dict(excl))
    for r in rows_out:
        print("  ", r)
    assert all("gate_ok" in l for l in lines_out), lines_out
    report(pp, print, excl)
    assert clean_seps("<%>kooiin.cheo,pchor.otaiin,odain.chor<->dair.shty")[1] == ["D", "C", "D", "C", "D", "I", "D"]
    print("SELFTEST OK")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        selftest(); return 0
    from collections import Counter
    t0 = time.time()
    lines_txt = []

    def emit(s=""):
        print(s, flush=True); lines_txt.append(s)

    start = clock()
    RUN.mkdir(parents=True, exist_ok=True)
    emit("s47: ink vs transcribers' word spaces (O-048 word half) — pre-registered in the docstring")
    emit(f"run: {start}")
    emit(f"s47_ink_space_agreement.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    seps_of = zl_with_seps()
    zmap = {p["id"]: p for p in SEG.zl_pages()}
    summ = json.loads((S45 / "segment_summary.json").read_text(encoding="utf-8"))
    ids = summ["clean_ids"]
    emit(f"clean s45 pages: {len(ids)}")

    def pages():
        for pid in ids:
            yield json.loads((S45 / "pages" / f"{pid}.json").read_text(encoding="utf-8"))
    rows_out = ["page\tline\tcls\tink\tw_px\tthr\tgallows\tcounts_equal\tconf"]
    lines_out = ["page\tline\tstatus\tcounts_equal\tconf"]
    excl = Counter()
    pp = collect(pages(), seps_of, zmap, rows_out, lines_out, excl, real_loader)
    (RUN / "positions.tsv").write_text("\n".join(rows_out) + "\n", encoding="utf-8")
    (RUN / "lines.tsv").write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    emit(f"lines used={excl['lines_used']}  raw-width gate passed={excl['lines_gate_ok']} "
         f"({excl['lines_gate_ok'] / max(excl['lines_used'], 1):.3f})")
    report(pp, emit, excl)
    emit("")
    emit(f"paths: {OUT}  {RUN / 'positions.tsv'}  {RUN / 'lines.tsv'}")
    emit(f"end: {clock()}  elapsed={time.time() - t0:.1f}s")
    OUT.write_text("\n".join(lines_txt) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
