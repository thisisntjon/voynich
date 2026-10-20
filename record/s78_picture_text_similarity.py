#!/usr/bin/env python
"""
S78: do herbal pages whose pictures look alike also have text whose cores look alike, once Davis hand,
quire, bifolio and Currier language are controlled?  (Meaning side; no reading-order assumption: the
test compares PAIRS of pages, so page order, reading direction and word order on a page are never used.)

PRE-REGISTRATION (frozen in s78_picture_text_similarity.prereg.sha256 before the real run; the stub
covers this file and its local imports: tools/boxes.py, tools/ivtff_to_meta.py, tools/plant_regions.py,
vparse.py, corpora.py, scoreboard/metrics_new.py).  Before freezing, only the --fixture path (synthetic
images + synthetic text, written to runs/s78/fixture.txt) was run on this code.

Prediction under content: if word cores carry content about what is drawn, look-alike pictures have
look-alike core distributions beyond hand/quire/bifolio/language.  A page-pool generator predicts no
link beyond hand and quire.

DATA
  Pages: ZL3b ($I=H) herbal pages that have (a) a Yale scan with an s48 plant crop (runs/s48/crops.json,
    kind=herbal; the s48 crop box is the fixed crop rule), (b) an s45 page record (runs/s45/pages/<id>.json:
    canvas file, kraken text lines and line<->locus alignment), (c) a Rozanova voynichese box file
    (tools/boxes.py), (d) a successful box->scan registration (below) and (e) >= 1 paragraph token in
    each of ZL3b, RF1b and IT2a.  N is reported with every exclusion and its reason.
  Box->scan registration (the box files are on a ~600 px reference canvas, not the Yale pixels):
    REG-A, text-map template: a text map is drawn from the s45 kraken tokens (x0..x1, from yb-0.55 pitch
      to yb+0.15 pitch, all detected lines; plant ink is not in it).  The box mask is matched to it by
      cross-correlation with a zero-sum template (boxes +1/n_box, gaps -1/n_gap inside the box extent)
      over isotropic scale 2.70..3.90 (step 0.03) x anisotropy {0.94,0.97,1,1.03,1.06} at 1/8 scan
      resolution, then refined at 1/2 resolution within +-64 scan px of the coarse offset (scale x
      0.985..1.015 step 0.005, anisotropy x {0.99,1,1.01}).
    REG-B, line correspondences: for every s45 1:1 line<->locus alignment whose ZL locus is also aligned
      to boxes (tools/boxes.align_page), the box line's left/right extent and token centres (when token
      counts agree) map to the kraken token extents/centres, and the box line's median y to the kraken
      baseline yb; RANSAC (400 draws, seed fixed, scale in (2.6, 4.0), |sx/sy-1| < 0.12, tolerance 35 px y
      / 70 px x) then least squares on the inlier lines (>= 3 needed).
    REG-A is used.  A page is accepted when REG-A's in-box minus in-gap text-map contrast >= REG_MIN_CONTRAST
      = 0.25 and its isotropic scale is not at the search edge (< 2.75 or > 3.85); otherwise excluded.
      REG-B is a reported cross-check only (max deviation at the four corners of the box extent): overlay
      inspection before freezing (f1v, f8r, f15r, f21v, f33v, f96v; registration only, no similarity or
      text statistic computed) showed REG-A on the text wherever REG-A and REG-B disagreed.
  Davis hand $H, quire $Q, bifolio ($Q,$B), Currier language $L: ZL3b page headers.
  Text: P loci of ZL3b (data/ZL3b-n.txt), RF1b (data/external/voynich-nu-ivtff/RF1b-er.txt) and IT2a
    (data/external/voynich-nu-ivtff/IT2a-n.txt) parsed by tools/ivtff_to_meta.convert (scoreboard rules).

PICTURE SIMILARITY (text masked)
  Every word box (all units, labels too) is mapped to scan pixels, padded PAD_BOX = 3 box-file px on each
  side (about 10 scan px; the padding is in box-file units, the boxes' native grid), and painted with
  the local background median: the RGB median of pixels in a ring of width max(box height, 12 px) around
  the padded box that lie outside every padded box and are neither paint nor ink (plant_regions.masks
  rules on the page); fewer than 50 such pixels -> the page parchment median.  Crop = s48 herbal
  bbox_canvas of the masked canvas, thumbnail 512, padded square with the s48 parchment colour, 224 px,
  8 views (4 rotations x hflip), DINOv2 ViT-B/14 CLS and SigLIP B/16-224 image features (as s48),
  L2-normalised per view, averaged, renormalised.  Per model: cosine matrix, z-scored over the
  off-diagonal upper-triangle values; picture similarity = mean of the two z matrices.
  Sensitivity variant TEXT-IN: identical but the raw canvas crop (no box masking, no kraken whitening).
  Masking check: mean same-page cosine masked vs text-in per model; Pearson r between the masked and
  text-in similarity matrices; same-hand minus different-hand mean picture similarity in each.

TEXT SIMILARITY
  SlotSegmenter (scoreboard/metrics_new.py, default parameters) fitted per transliteration on the P
  tokens of ALL its herbal pages ($I=H, 128 pages).  Fitting on all pages is acceptable here: nothing is
  predicted out of sample; the segmenter only defines the core unit.  Page vectors: counts of cores
  (primary), of whole word types (variant), of frames "prefix|suffix" (control: should carry hand, not
  content).  tf-idf: tf = raw count, idf = ln((1+N)/(1+df)) + 1 over the N scored pages, rows
  L2-normalised; similarity = cosine.

STATISTIC
  Over all page pairs i<j: partial Mantel r = Pearson correlation of the residuals of the picture and
  text similarities after OLS on [1, same hand, same quire, same bifolio, same Currier language].
  P-value: 10,000 stratified permutations (seed SEED) of page labels within hand x quire strata, applied
  to the text matrix (covariates stay with the positions); one-sided p = (1 + #{r_perm >= r}) / 10,001.
  The same permutation set is used for every test of a page set.  Variant NOBIF: same-bifolio pairs
  (same folio included) are dropped (the same-bifolio covariate is then constant and removed).

CONTROLS (ZL3b, cores, scored identically, all-pairs variant decides; NOBIF reported)
  C+ : real masked pictures; KMeans (k = 12, n_init = 10, seed) on the concatenated masked DINOv2+SigLIP
       embeddings gives groups.  Per replicate, each group gets a core pool: POOL_TYPES = 20 core types
       drawn uniformly without replacement from the herbal core types with ZL3b count >= 3, used with
       equal weights (a content vocabulary, not the frequent function cores).  [Pool design set on the
       fixture only: 40 count-weighted types gave 2-6/20 detections at s = 0.20, 40 equal-weight types
       16/20; 20 equal-weight types adopted before any real-data scoring.]  Each page keeps its real number of core tokens; each token comes from the
       page's group pool with probability s, else from the page's real hand pool (all ZL3b herbal cores
       of that Davis hand).  s = 0.20 is the control; 20 replicates; PASS if >= 18/20 reach p < 0.01.
       Power curve: s = 0.05, 0.10, 0.20, 0.40, 20 replicates each.
  C- : the real ZL3b core texts reassigned by a random derangement within hand x quire strata (pages in
       singleton strata keep their text); 20 replicates; PASS if <= 2/20 reach p < 0.01.
  If either fails: verdict "inconclusive: controls failed".

PRE-REGISTERED VERDICT
  "picture-linked cores": ZL3b cores r > 0 with p < 0.01 in both ALL and NOBIF; RF1b and IT2a cores r > 0
     in both ALL and NOBIF; and ZL3b frames not significant (p >= 0.01, the same threshold) in both ALL
     and NOBIF.
  "no picture link detected": controls pass and ZL3b cores p >= 0.05 in both ALL and NOBIF.  The minimum
     detectable effect is the smallest C+ strength with >= 18/20 detections (p < 0.01, ALL).
  Otherwise "mixed".

DESCRIPTIVE (no verdict): words variant; TEXT-IN pictures; DINOv2-only and SigLIP-only pictures; pharma
  pages (s48 crops: containers and plants, page picture = renormalised mean of its crop embeddings per
  model; s48 pharma crops are paint-chroma components, not box-masked; text = all ZL3b loci of the page,
  P and labels, via vparse; segmenter fitted on those pharma tokens); biological section ($I=B pages with
  s45 records, boxes and registration: whole trimmed page, box-masked; P text; segmenter fitted on the
  biological P tokens); and the 10 most similar herbal picture pairs with their core overlap.

Outputs: results_s78.txt; runs/s78/ (embeddings.npz, matrices.npz, registration.json, pairs.json, ...).
Usage (scratchpad venv with torch + transformers; run with -I from anywhere):
    python -I s78_picture_text_similarity.py --fixture      (synthetic only -> runs/s78/fixture.txt)
    python -I s78_picture_text_similarity.py                (real data -> results_s78.txt)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scoreboard"))
import boxes as boxmod  # noqa: E402
import ivtff_to_meta  # noqa: E402
import plant_regions as pr  # noqa: E402
import vparse  # noqa: E402
from metrics_new import SlotSegmenter  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

OUT = ROOT / "runs" / "s78"
STUB = ROOT / "s78_picture_text_similarity.prereg.sha256"
S45 = ROOT / "runs" / "s45" / "pages"
S48 = ROOT / "runs" / "s48"
SCANS = ROOT / "data" / "external" / "yale_scans" / "pages"
TRANSLITS = [("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
             ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"),
             ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt")]
LOCAL_IMPORTS = ["s78_picture_text_similarity.py", "tools/boxes.py", "tools/ivtff_to_meta.py",
                 "tools/plant_regions.py", "vparse.py", "corpora.py", "scoreboard/metrics_new.py"]

SEED = 20261018
NPERM = 10000
K_GROUPS = 12
NREP = 20
STRENGTHS = [0.05, 0.10, 0.20, 0.40]
CPLUS_S = 0.20
POOL_TYPES = 20
POOL_MINCOUNT = 3
PAD_BOX = 3
REG_MIN_CONTRAST = 0.25
ALPHA, ALPHA_NO = 0.01, 0.05

LOG: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return time.strftime("%Y-%m-%d %H:%M:%S") + " (time.strftime)"


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
    missing = [f for f in LOCAL_IMPORTS if f not in want]
    if bad or missing or not want:
        return f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"
    return "True"


# =============================================================== registration
def text_map(rec, f):
    W, H = rec["size"]
    T = np.zeros((int(H * f) + 1, int(W * f) + 1), np.float32)
    pitch = rec.get("pitch") or 50.0
    for L in rec["lines"]:
        y0, y1 = L["yb"] - 0.55 * pitch, L["yb"] + 0.15 * pitch
        for t in L["tokens"]:
            T[max(0, int(y0 * f)):int(y1 * f) + 1, max(0, int(t["x0"] * f)):int(t["x1"] * f) + 1] = 1.0
    return T


def box_template(bx, kx, ky):
    mh = int(max(b["y"] + b["h"] for b in bx) * ky) + 2
    mw = int(max(b["x"] + b["w"] for b in bx) * kx) + 2
    M = np.zeros((mh, mw), np.float32)
    for b in bx:
        M[int(b["y"] * ky):int((b["y"] + b["h"]) * ky) + 1, int(b["x"] * kx):int((b["x"] + b["w"]) * kx) + 1] = 1
    # restrict the gap region to the box extent
    x0 = int(min(b["x"] for b in bx) * kx); y0 = int(min(b["y"] for b in bx) * ky)
    nb = M.sum()
    Tm = np.zeros_like(M)
    ext = np.zeros_like(M, dtype=bool); ext[y0:, x0:] = True
    ng = (ext & (M == 0)).sum()
    Tm[M > 0] = 1.0 / nb
    Tm[ext & (M == 0)] = -1.0 / max(ng, 1)
    return Tm


def template_search(T, bx, f, scales, anis, near=None, win=64.0):
    """Best (score, sx, sy, ox, oy) over scales x anisotropies; offsets in scan px.  near=(ox, oy) restricts
    the offset search to +-win scan px around it."""
    import cv2
    best = None
    for s in scales:
        for a in anis:
            Tm = box_template(bx, s * f, s * a * f)
            mh, mw = Tm.shape
            P = np.zeros((T.shape[0] + 2 * mh, T.shape[1] + 2 * mw), np.float32)
            P[mh:mh + T.shape[0], mw:mw + T.shape[1]] = T
            if near is None:
                r = cv2.matchTemplate(P, Tm, cv2.TM_CCORR)
                bx0 = by0 = 0
            else:
                cx, cy = int(round(near[0] * f)) + mw, int(round(near[1] * f)) + mh
                w = int(round(win * f))
                bx0, by0 = max(0, cx - w), max(0, cy - w)
                sub = P[by0:min(P.shape[0], cy + w + mh), bx0:min(P.shape[1], cx + w + mw)]
                if sub.shape[0] < mh or sub.shape[1] < mw:
                    continue
                r = cv2.matchTemplate(sub, Tm, cv2.TM_CCORR)
            _, mx, _, loc = cv2.minMaxLoc(r)
            c = (float(mx), float(s), float(s * a), (loc[0] + bx0 - mw) / f, (loc[1] + by0 - mh) / f)
            if best is None or c[0] > best[0]:
                best = c
    return best


def reg_lines(rec, bx, zl_recs, rng):
    lines, _ = boxmod.align_page(zl_recs, bx)
    C = []
    for a in rec.get("alignment", []):
        if a.get("op") != "1:1" or not a.get("det") or not a.get("loci"):
            continue
        L = rec["lines"][a["det"][0]]
        bl = lines[a["loci"][0]]
        if not bl["aligned"] or len(bl["tokens"]) < 2 or not L["tokens"]:
            continue
        kt = L["tokens"]
        bb = [(t["cx"] - t["w"] / 2, t["cx"] + t["w"] / 2) for t in bl["tokens"]]
        xs = [(min(u for u, _ in bb), min(t["x0"] for t in kt)), (max(v for _, v in bb), max(t["x1"] for t in kt))]
        if len(kt) == len(bb):
            xs += [((u + v) / 2, (t["x0"] + t["x1"]) / 2) for (u, v), t in zip(bb, kt)]
        C.append(dict(x=xs, y=(float(np.median([t["cy"] for t in bl["tokens"]])), float(L["yb"]))))
    if len(C) < 3:
        return None, len(C)
    best = None
    for _ in range(400):
        i, j = rng.choice(len(C), 2, replace=False)
        yi, yj = C[i]["y"], C[j]["y"]
        if abs(yi[0] - yj[0]) < 20:
            continue
        sy = (yj[1] - yi[1]) / (yj[0] - yi[0]); oy = yi[1] - sy * yi[0]
        X = np.array(C[i]["x"][:2] + C[j]["x"][:2])
        if np.ptp(X[:, 0]) < 50:
            continue
        sx, ox = np.polyfit(X[:, 0], X[:, 1], 1)
        if not (2.6 < sx < 4.0 and 2.6 < sy < 4.0 and abs(sx / sy - 1) < 0.12):
            continue
        inl = [k for k, c in enumerate(C) if abs(sy * c["y"][0] + oy - c["y"][1]) < 35
               and all(abs(sx * u + ox - v) < 70 for u, v in c["x"][:2])]
        if best is None or len(inl) > len(best):
            best = inl
    if not best or len(best) < 3:
        return None, len(C)
    X = np.array([xy for k in best for xy in C[k]["x"]]); Y = np.array([C[k]["y"] for k in best])
    sx, ox = np.polyfit(X[:, 0], X[:, 1], 1); sy, oy = np.polyfit(Y[:, 0], Y[:, 1], 1)
    return dict(sx=float(sx), ox=float(ox), sy=float(sy), oy=float(oy), n_inl=len(best)), len(C)


def register(pid, rec, bx, zl_recs, rng):
    T8 = text_map(rec, 0.125)
    c = template_search(T8, bx, 0.125, np.arange(2.70, 3.901, 0.03), [0.94, 0.97, 1.0, 1.03, 1.06])
    T2 = text_map(rec, 0.5)
    c = template_search(T2, bx, 0.5, c[1] * np.arange(0.985, 1.0151, 0.005), [c[2] / c[1] * k for k in (0.99, 1.0, 1.01)],
                        near=(c[3], c[4]), win=64.0)
    A = dict(sx=c[1], sy=c[2], ox=c[3], oy=c[4])
    contrast = c[0]  # mean text-map value in boxes minus in gaps
    B, n_lines = reg_lines(rec, bx, zl_recs, rng)
    xs = [min(b["x"] for b in bx), max(b["x"] + b["w"] for b in bx)]
    ys = [min(b["y"] for b in bx), max(b["y"] + b["h"] for b in bx)]
    dev = None
    if B is not None:
        dev = max(max(abs(A["sx"] * u + A["ox"] - (B["sx"] * u + B["ox"])) for u in xs),
                  max(abs(A["sy"] * v + A["oy"] - (B["sy"] * v + B["oy"])) for v in ys))
    edge = A["sx"] < 2.75 or A["sx"] > 3.85
    ok = contrast >= REG_MIN_CONTRAST and not edge
    why = (f"REG-A contrast {contrast:.3f}" + ("" if contrast >= REG_MIN_CONTRAST else f" < {REG_MIN_CONTRAST}")
           + (", scale at search edge" if edge else "") + "; REG-B cross-check "
           + (f"max corner deviation {dev:.0f} px" if dev is not None else f"unavailable ({n_lines} usable lines)"))
    return dict(page=pid, ok=bool(ok), why=why, A=A, B=B, contrast=contrast, dev=dev, n_box=len(bx))


# =============================================================== masking + embedding
def mask_boxes(arr, scan_boxes):
    """arr: full canvas RGB uint8.  scan_boxes: list of (x0, y0, x1, y1) padded, scan px.  Returns copy."""
    P = dict(pr.PARAMS)
    paint, ink, parch, _, _ = pr.masks(arr, P)
    H, W = arr.shape[:2]
    U = np.zeros((H, W), bool)
    bb = []
    for x0, y0, x1, y1 in scan_boxes:
        x0, y0 = max(0, int(np.floor(x0))), max(0, int(np.floor(y0)))
        x1, y1 = min(W, int(np.ceil(x1))), min(H, int(np.ceil(y1)))
        if x1 > x0 and y1 > y0:
            U[y0:y1, x0:x1] = True
            bb.append((x0, y0, x1, y1))
    good = ~U & ~paint & ~ink
    out = arr.copy()
    n_fallback = 0
    for x0, y0, x1, y1 in bb:
        r = max(y1 - y0, 12)
        X0, Y0, X1, Y1 = max(0, x0 - r), max(0, y0 - r), min(W, x1 + r), min(H, y1 + r)
        g = good[Y0:Y1, X0:X1]
        if g.sum() >= 50:
            col = np.median(arr[Y0:Y1, X0:X1][g], axis=0).astype(np.uint8)
        else:
            col = parch; n_fallback += 1
        out[y0:y1, x0:x1] = col
    return out, dict(n_boxes=len(bb), frac_area=float(U.mean()), n_fallback=n_fallback,
                     ink_in_boxes_before=float(ink[U].mean()) if U.any() else 0.0,
                     ink_in_boxes_after=float(pr.masks(out, P)[1][U].mean()) if U.any() else 0.0)


def prep(img_arr, parch):
    from PIL import Image
    im = Image.fromarray(img_arr)
    im.thumbnail((pr.PARAMS["CROP_SAVE_MAX"], pr.PARAMS["CROP_SAVE_MAX"]))
    return pr.square(im, parch, pr.PARAMS["EMB_SIZE"])


class Embedder:
    def __init__(self):
        import torch
        from transformers import AutoModel, SiglipModel
        self.torch = torch
        self.dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        M = pr.MODELS
        self.dino = AutoModel.from_pretrained(str(M / "dinov2-base"), use_safetensors=True).to(self.dev).eval()
        self.sig = SiglipModel.from_pretrained(str(M / "siglip-base-patch16-224"), use_safetensors=True).to(self.dev).eval()
        self.norms = {"dino": ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), "siglip": ((0.5,) * 3, (0.5,) * 3)}

    def __call__(self, img):
        torch = self.torch
        with torch.no_grad():
            x = torch.from_numpy(np.stack([np.asarray(v, dtype=np.float32) / 255.0 for v in pr.views(img)]))
            x = x.permute(0, 3, 1, 2).to(self.dev)
            out = {}
            for name in ("dino", "siglip"):
                m, s = self.norms[name]
                xn = (x - torch.tensor(m, device=self.dev).view(1, 3, 1, 1)) / torch.tensor(s, device=self.dev).view(1, 3, 1, 1)
                f = self.dino(pixel_values=xn).last_hidden_state[:, 0] if name == "dino" else \
                    self.sig.get_image_features(pixel_values=xn)
                f = torch.nn.functional.normalize(f.float(), dim=-1).mean(0)
                out[name] = torch.nn.functional.normalize(f, dim=-1).cpu().numpy()
        return out


def zsim(E):
    """E: dict model -> (N, d) L2-normalised.  Returns mean of per-model z-scored cosine matrices + parts."""
    parts = {}
    N = next(iter(E.values())).shape[0]
    iu = np.triu_indices(N, 1)
    for m, X in E.items():
        C = X @ X.T
        v = C[iu]
        Z = (C - v.mean()) / v.std()
        np.fill_diagonal(Z, 0.0)
        parts[m] = Z
    return sum(parts.values()) / len(parts), parts


# =============================================================== text
def tfidf_cos(counters):
    vocab = sorted({k for c in counters for k in c})
    ix = {k: i for i, k in enumerate(vocab)}
    N = len(counters)
    M = np.zeros((N, len(vocab)))
    for r, c in enumerate(counters):
        for k, v in c.items():
            M[r, ix[k]] = v
    df = (M > 0).sum(0)
    idf = np.log((1 + N) / (1 + df)) + 1
    X = M * idf
    nrm = np.linalg.norm(X, axis=1, keepdims=True)
    nrm[nrm == 0] = 1
    X = X / nrm
    S = X @ X.T
    np.fill_diagonal(S, 0.0)
    return S


def segment_pages(tokens_by_page, fit_tokens):
    seg = SlotSegmenter(fit_tokens)
    cores, words, frames = {}, {}, {}
    for p, toks in tokens_by_page.items():
        tr = [seg.segment(w) for w in toks]
        cores[p] = Counter(k for _, k, _ in tr)
        words[p] = Counter(toks)
        frames[p] = Counter(f"{a}|{c}" for a, _, c in tr)
    return seg, cores, words, frames


# =============================================================== statistic
class PairSpace:
    def __init__(self, meta, pages, rng, nperm=NPERM):
        """meta: page -> dict(hand, quire, bif, lang)."""
        self.pages = list(pages)
        N = len(self.pages)
        self.N = N
        iu, ju = np.triu_indices(N, 1)
        g = lambda k: np.array([meta[p][k] for p in self.pages], dtype=object)  # noqa: E731
        h, q, b, l = g("hand"), g("quire"), g("bif"), g("lang")
        cov = dict(hand=(h[iu] == h[ju]), quire=(q[iu] == q[ju]), bif=(b[iu] == b[ju]), lang=(l[iu] == l[ju]))
        self.cov = cov
        self.iu_all, self.ju_all = iu, ju
        strata = defaultdict(list)
        for i, p in enumerate(self.pages):
            strata[(meta[p]["hand"], meta[p]["quire"])].append(i)
        self.strata = [np.array(v) for v in strata.values()]
        self.n_strata_perm = sum(len(v) >= 2 for v in self.strata)
        self.n_pages_perm = sum(len(v) for v in self.strata if len(v) >= 2)
        perms = np.tile(np.arange(N), (nperm, 1))
        for s in self.strata:
            if len(s) < 2:
                continue
            for k in range(nperm):
                perms[k, s] = s[rng.permutation(len(s))]
        self.perms = perms
        self.variants = {}
        for name, keep in (("ALL", np.ones(len(iu), bool)), ("NOBIF", ~cov["bif"])):
            cols = [np.ones(keep.sum())]
            for k in ("hand", "quire", "bif", "lang"):
                v = cov[k][keep].astype(float)
                if v.std() > 0:
                    cols.append(v)
            X = np.stack(cols, 1)
            U, S, _ = np.linalg.svd(X, full_matrices=False)
            Q = U[:, S > S[0] * 1e-9]  # orthonormal basis of the covariate column space (collinear columns ok)
            self.variants[name] = dict(keep=keep, Q=Q, iu=iu[keep], ju=ju[keep], n_pairs=int(keep.sum()),
                                       n_cov=X.shape[1] - 1)

    def resid(self, v, Q):
        return v - Q @ (Q.T @ v)

    def test(self, Pm, Tm, variant="ALL", batch=500):
        V = self.variants[variant]
        iu, ju, Q = V["iu"], V["ju"], V["Q"]
        rp = self.resid(Pm[iu, ju], Q)
        rt = self.resid(Tm[iu, ju], Q)
        nrp = np.linalg.norm(rp)
        r = float(rp @ rt / (nrp * np.linalg.norm(rt))) if nrp > 0 and np.linalg.norm(rt) > 0 else 0.0
        null = np.empty(len(self.perms))
        for s in range(0, len(self.perms), batch):
            pb = self.perms[s:s + batch]
            Tv = Tm[pb[:, iu], pb[:, ju]]                      # (B, M)
            num = Tv @ rp                                      # rp is orthogonal to Q
            proj = Tv @ Q                                      # (B, k)
            den = np.sqrt(np.maximum((Tv * Tv).sum(1) - (proj * proj).sum(1), 1e-300))
            null[s:s + batch] = num / (nrp * den)
        p = (1 + int((null >= r - 1e-12).sum())) / (len(null) + 1)
        return dict(r=r, p=p, null_mean=float(null.mean()), null_sd=float(null.std()),
                    null_q99=float(np.quantile(null, 0.99)), n_pairs=V["n_pairs"])


# =============================================================== controls
def kmeans_groups(Emask, k, seed):
    from sklearn.cluster import KMeans
    F = np.concatenate([Emask["dino"], Emask["siglip"]], 1)
    return KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(F)


def synth_cplus(cores, pages, meta, groups, s, rng, all_herbal_core_counts, hand_pool):
    types = [c for c, n in all_herbal_core_counts.items() if n >= POOL_MINCOUNT]
    pools = {}
    for g in sorted(set(groups)):
        pick = rng.choice(len(types), size=min(POOL_TYPES, len(types)), replace=False)
        ks = [types[i] for i in pick]
        pools[g] = (ks, np.full(len(ks), 1.0 / len(ks)))
    out = []
    for i, p in enumerate(pages):
        n = sum(cores[p].values())
        hk, hw = hand_pool[meta[p]["hand"]]
        from_g = rng.random(n) < s
        gk, gw = pools[groups[i]]
        a = rng.choice(len(gk), size=int(from_g.sum()), p=gw)
        b = rng.choice(len(hk), size=int((~from_g).sum()), p=hw)
        out.append(Counter([gk[j] for j in a] + [hk[j] for j in b]))
    return out


def derange_within(ps: PairSpace, rng):
    perm = np.arange(ps.N)
    for s in ps.strata:
        if len(s) < 2:
            continue
        while True:
            q = rng.permutation(len(s))
            if not np.any(q == np.arange(len(s))):
                break
        perm[s] = s[q]
    return perm


# =============================================================== analysis core
def analyse(label, pages, meta, P, Pparts, P_textin, texts, segfit, emask, rng, fixture=False,
            hand_pools=None, all_core_counts=None):
    """texts: translit -> page -> token list (all of the translit's fit pages available in segfit)."""
    res = dict(label=label, N=len(pages))
    ps = PairSpace(meta, pages, rng)
    emit(f"[{label}] N pages = {len(pages)}; pairs ALL = {ps.variants['ALL']['n_pairs']}, NOBIF = "
         f"{ps.variants['NOBIF']['n_pairs']}; hand x quire strata = {len(ps.strata)} "
         f"({ps.n_strata_perm} with >= 2 pages, {ps.n_pages_perm} pages permutable)")
    emit(f"   covariates (share of ALL pairs): same hand {ps.cov['hand'].mean():.3f}, same quire "
         f"{ps.cov['quire'].mean():.3f}, same bifolio {ps.cov['bif'].mean():.3f}, same language "
         f"{ps.cov['lang'].mean():.3f}")
    seg_by = {}
    TM = {}
    for tr in texts:
        seg, cores, words, frames = segment_pages({p: texts[tr][p] for p in pages}, segfit[tr])
        seg_by[tr] = (seg, cores)
        TM[(tr, "cores")] = tfidf_cos([cores[p] for p in pages])
        TM[(tr, "words")] = tfidf_cos([words[p] for p in pages])
        TM[(tr, "frames")] = tfidf_cos([frames[p] for p in pages])
        emit(f"   {tr}: segmenter prefixes {len(seg.prefixes)} suffixes {len(seg.suffixes)}; tokens on scored pages "
             f"{sum(len(texts[tr][p]) for p in pages)}; core types {len({k for p in pages for k in cores[p]})}")
    rows = []
    emit("")
    emit(f"   main table (partial Mantel r; one-sided stratified p, {NPERM} perms):")
    emit(f"   {'translit':<6} {'text':<7} {'picture':<8} {'variant':<6} {'r':>8} {'p':>8} {'null mean':>10} {'null q99':>9} pairs")
    combos = []
    for tr in texts:
        for unit in ("cores", "words", "frames"):
            combos.append((tr, unit, "masked"))
    combos += [("ZL3b", "cores", "text-in"), ("ZL3b", "cores", "dino"), ("ZL3b", "cores", "siglip")]
    if not fixture:
        combos += [("ZL3b", "frames", "text-in")]
    for tr, unit, pic in combos:
        if tr not in texts:
            continue
        Pm = {"masked": P, "text-in": P_textin, "dino": Pparts["dino"], "siglip": Pparts["siglip"]}[pic]
        if Pm is None:
            continue
        for var in ("ALL", "NOBIF"):
            t = ps.test(Pm, TM[(tr, unit)], var)
            t.update(translit=tr, unit=unit, picture=pic, variant=var)
            rows.append(t)
            emit(f"   {tr:<6} {unit:<7} {pic:<8} {var:<6} {t['r']:>+8.4f} {t['p']:>8.4f} {t['null_mean']:>+10.4f} "
                 f"{t['null_q99']:>+9.4f} {t['n_pairs']}")
    res["rows"] = rows
    res["TM"] = TM
    res["ps"] = ps
    res["seg_by"] = seg_by
    return res


def get(rows, **kw):
    for r in rows:
        if all(r[k] == v for k, v in kw.items()):
            return r
    return None


def run_controls(res, pages, meta, emask, rng, hand_pools, all_core_counts):
    ps = res["ps"]
    P = res["P"]
    _, cores = res["seg_by"]["ZL3b"]
    groups = kmeans_groups({k: emask[k] for k in ("dino", "siglip")}, K_GROUPS, SEED)
    gc = Counter(groups.tolist())
    emit(f"   C+ groups (KMeans k={K_GROUPS} on masked embeddings): sizes {sorted(gc.values(), reverse=True)}")
    power = {}
    for s in STRENGTHS:
        det = {"ALL": 0, "NOBIF": 0}
        rs = {"ALL": [], "NOBIF": []}
        for rep in range(NREP):
            syn = synth_cplus(cores, pages, meta, groups, s, rng, all_core_counts, hand_pools)
            Tm = tfidf_cos(syn)
            for var in ("ALL", "NOBIF"):
                t = ps.test(P, Tm, var)
                rs[var].append(t["r"])
                det[var] += t["p"] < ALPHA
        power[s] = dict(det=det, r_mean={k: float(np.mean(v)) for k, v in rs.items()},
                        r_min={k: float(np.min(v)) for k, v in rs.items()})
        emit(f"   C+ s={s:.2f}: detected (p<{ALPHA}) ALL {det['ALL']}/{NREP}, NOBIF {det['NOBIF']}/{NREP}; "
             f"mean r ALL {np.mean(rs['ALL']):+.4f} (min {np.min(rs['ALL']):+.4f}), NOBIF {np.mean(rs['NOBIF']):+.4f}")
    real_T = res["TM"][("ZL3b", "cores")]
    neg = {"ALL": 0, "NOBIF": 0}
    nr = []
    for rep in range(NREP):
        perm = derange_within(ps, rng)
        Tm = real_T[np.ix_(perm, perm)]
        for var in ("ALL", "NOBIF"):
            t = ps.test(P, Tm, var)
            neg[var] += t["p"] < ALPHA
            if var == "ALL":
                nr.append(t["r"])
    emit(f"   C- (derangement within hand x quire): reached p<{ALPHA}: ALL {neg['ALL']}/{NREP}, NOBIF {neg['NOBIF']}/{NREP}; "
         f"mean r ALL {np.mean(nr):+.4f}")
    cplus_pass = power[CPLUS_S]["det"]["ALL"] >= 18
    cminus_pass = neg["ALL"] <= 2
    mde = next((s for s in STRENGTHS if power[s]["det"]["ALL"] >= 18), None)
    emit(f"   controls: C+ (s={CPLUS_S:.2f}) {'PASS' if cplus_pass else 'FAIL'} ({power[CPLUS_S]['det']['ALL']}/{NREP} >= 18); "
         f"C- {'PASS' if cminus_pass else 'FAIL'} ({neg['ALL']}/{NREP} <= 2)")
    emit(f"   minimum detectable effect (smallest s with >= 18/20, ALL): "
         + (f"s = {mde:.2f} (mean r there {power[mde]['r_mean']['ALL']:+.4f})" if mde is not None else "> 0.40"))
    return dict(power={str(k): v for k, v in power.items()}, neg=neg, cplus_pass=cplus_pass,
                cminus_pass=cminus_pass, mde=mde, groups=groups.tolist())


def verdict(res, ctl):
    rows = res["rows"]
    if not (ctl["cplus_pass"] and ctl["cminus_pass"]):
        return "inconclusive: controls failed", []
    zl = [get(rows, translit="ZL3b", unit="cores", picture="masked", variant=v) for v in ("ALL", "NOBIF")]
    fr = [get(rows, translit="ZL3b", unit="frames", picture="masked", variant=v) for v in ("ALL", "NOBIF")]
    others = [get(rows, translit=t, unit="cores", picture="masked", variant=v)
              for t in ("RF1b", "IT2a") for v in ("ALL", "NOBIF")]
    c1 = all(x["r"] > 0 and x["p"] < ALPHA for x in zl)
    c2 = all(x is not None and x["r"] > 0 for x in others)
    c3 = all(x["p"] >= ALPHA for x in fr)
    why = [f"ZL3b cores r>0 & p<{ALPHA} in ALL and NOBIF: {c1}",
           f"RF1b and IT2a cores r>0 in ALL and NOBIF: {c2}",
           f"ZL3b frames p>={ALPHA} in ALL and NOBIF: {c3}"]
    if c1 and c2 and c3:
        return "picture-linked cores", why
    no = all(x["p"] >= ALPHA_NO for x in zl)
    why.append(f"ZL3b cores p>={ALPHA_NO} in ALL and NOBIF: {no}")
    if no:
        return "no picture link detected", why
    return "mixed", why


def top_pairs(res, pages, meta, k=10):
    P = res["P"]
    N = len(pages)
    iu, ju = np.triu_indices(N, 1)
    v = P[iu, ju]
    order = np.argsort(-v)[:k]
    Tc = res["TM"][("ZL3b", "cores")]
    tv = Tc[iu, ju]
    _, cores = res["seg_by"]["ZL3b"]
    out = []
    emit(f"   10 most similar picture pairs (masked; z-avg), with ZL3b core tf-idf cosine and its percentile among "
         f"all {len(v)} pairs:")
    for o in order:
        a, b = pages[iu[o]], pages[ju[o]]
        shared = sorted(set(cores[a]) & set(cores[b]), key=lambda c: -min(cores[a][c], cores[b][c]))
        pct = float((tv < tv[o]).mean())
        flags = "".join(x for x, kk in (("H", "hand"), ("Q", "quire"), ("B", "bif"), ("L", "lang"))
                        if meta[a][kk] == meta[b][kk])
        out.append(dict(a=a, b=b, pic=float(v[o]), core_cos=float(tv[o]), core_pct=pct, n_shared=len(shared),
                        shared_top=shared[:6], same=flags, hands=(meta[a]["hand"], meta[b]["hand"]),
                        quires=(meta[a]["quire"], meta[b]["quire"])))
        emit(f"   {a:>6} {b:>6}  pic z {v[o]:+.2f}  core cos {tv[o]:.3f} (pct {pct:.2f})  shared core types "
             f"{len(shared):>3}  same[{flags:<4}] hands {meta[a]['hand']}/{meta[b]['hand']} quires "
             f"{meta[a]['quire']}/{meta[b]['quire']}  top shared {' '.join(shared[:6])}")
    return out


# =============================================================== real data
def zl_headers():
    out = {}
    for raw in vparse.DATA.read_text(encoding="ascii", errors="replace").splitlines():
        m = vparse.PAGE_RE.match(raw)
        if not m:
            continue
        v = dict(vparse.VAR_RE.findall(m.group(2)))
        out[m.group(1)] = dict(hand=v.get("H", "?"), quire=v.get("Q", "?"), bif=v.get("Q", "?") + ":" + v.get("B", "?"),
                               lang=v.get("L", "?"), illus=v.get("I", "?"))
    return out


def load_texts(section):
    texts, fit = {}, {}
    for tr, path in TRANSLITS:
        d = ivtff_to_meta.convert(path)
        pg = {p["id"]: [w for ln in p["lines"] for w in ln] for p in d["pages"] if p["section"] == section}
        texts[tr] = pg
        fit[tr] = [w for v in pg.values() for w in v]
    return texts, fit


def scan_boxes_for(bx, A):
    return [(A["sx"] * (b["x"] - PAD_BOX) + A["ox"], A["sy"] * (b["y"] - PAD_BOX) + A["oy"],
             A["sx"] * (b["x"] + b["w"] + PAD_BOX) + A["ox"], A["sy"] * (b["y"] + b["h"] + PAD_BOX) + A["oy"]) for b in bx]


def embed_pages(page_list, emb, crop_fn):
    """crop_fn(pid) -> (masked_arr, textin_arr, parch, mask_info).  Returns embeddings and mask infos."""
    Em = {"dino": [], "siglip": []}
    Et = {"dino": [], "siglip": []}
    infos = {}
    for pid in page_list:
        m_arr, t_arr, parch, info = crop_fn(pid)
        a = emb(prep(m_arr, parch)); b = emb(prep(t_arr, parch))
        for k in Em:
            Em[k].append(a[k]); Et[k].append(b[k])
        infos[pid] = info
    return {k: np.stack(v) for k, v in Em.items()}, {k: np.stack(v) for k, v in Et.items()}, infos


def masking_check(Em, Et, P, Pt, pages, meta, label):
    N = len(pages)
    iu, ju = np.triu_indices(N, 1)
    emit(f"   masking check [{label}]: mean same-page cosine masked vs text-in: DINOv2 "
         f"{np.mean((Em['dino'] * Et['dino']).sum(1)):.4f}, SigLIP {np.mean((Em['siglip'] * Et['siglip']).sum(1)):.4f}")
    emit(f"   r(picture sim masked, picture sim text-in) over pairs = {np.corrcoef(P[iu, ju], Pt[iu, ju])[0, 1]:.4f}")
    h = np.array([meta[p]["hand"] for p in pages], dtype=object)
    same = h[iu] == h[ju]
    for nm, M in (("masked", P), ("text-in", Pt)):
        v = M[iu, ju]
        emit(f"   same-hand minus different-hand mean picture z ({nm}): {v[same].mean() - v[~same].mean():+.4f}")


def real_main(t0):
    OUT.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    rng = np.random.default_rng(SEED)
    hdr = zl_headers()
    crops = json.loads((S48 / "crops.json").read_text(encoding="utf-8"))["crops"]
    herb_crop = {c["page"]: c for c in crops if c["kind"] == "herbal"}
    zl_recs = defaultdict(list)
    for r in vparse.load():
        zl_recs[r["page"]].append(r)
    texts_H, fit_H = load_texts("H")
    herbal_all = sorted(p for p, v in hdr.items() if v["illus"] == "H")
    box_have = set(boxmod.box_folios())
    excl = []
    cand = []
    for p in herbal_all:
        if p not in herb_crop:
            excl.append((p, "no s48 plant crop (no single-folio canvas)")); continue
        if not (S45 / f"{p}.json").exists():
            excl.append((p, "no s45 page record (composite canvas): no registration anchor")); continue
        if p not in box_have:
            excl.append((p, "no word-box file")); continue
        if not all(texts_H[tr].get(p) for tr, _ in TRANSLITS):
            excl.append((p, "no P text in a transliteration")); continue
        cand.append(p)
    emit(f"herbal pages ($I=H, ZL3b): {len(herbal_all)}; candidates before registration: {len(cand)}")
    # ---- registration
    reg = {}
    rrng = np.random.default_rng(SEED + 1)
    for p in cand:
        rec = json.loads((S45 / f"{p}.json").read_text(encoding="utf-8"))
        reg[p] = register(p, rec, boxmod.load_boxes(p), zl_recs[p], rrng)
    pages = [p for p in cand if reg[p]["ok"]]
    for p in cand:
        if not reg[p]["ok"]:
            excl.append((p, "registration rejected: " + reg[p]["why"]))
    devs = np.array([reg[p]["dev"] for p in pages if reg[p]["dev"] is not None])
    emit(f"registration: accepted {len(pages)}/{len(cand)}; REG-A contrast median "
         f"{np.median([reg[p]['contrast'] for p in pages]):.3f}, min {np.min([reg[p]['contrast'] for p in pages]):.3f}; "
         f"REG-B cross-check on {len(devs)} pages: corner deviation median {np.median(devs):.0f} px, "
         f"<= 60 px on {int((devs <= 60).sum())}, > 100 px on {int((devs > 100).sum())}")
    emit(f"N (herbal pages scored) = {len(pages)}; excluded {len(excl)}:")
    for p, why in excl:
        emit(f"   {p}: {why}")
    (OUT / "registration.json").write_text(json.dumps(reg, indent=1, default=str), encoding="utf-8", newline="\n")

    emb = Embedder()

    def herbal_crop(pid):
        rec = json.loads((S45 / f"{pid}.json").read_text(encoding="utf-8"))
        arr = np.asarray(Image.open(SCANS / rec["file"]).convert("RGB"))
        sb = scan_boxes_for(boxmod.load_boxes(pid), reg[pid]["A"])
        marr, info = mask_boxes(arr, sb)
        c = herb_crop[pid]
        x, y, w, h = c["bbox_canvas"]
        info["crop_box_overlap"] = float(np.mean([max(0, min(b[2], x + w) - max(b[0], x)) * max(0, min(b[3], y + h) - max(b[1], y)) > 0
                                                  for b in sb]))
        return marr[y:y + h, x:x + w], arr[y:y + h, x:x + w], c["parch"], info

    te = time.time()
    Em, Et, infos = embed_pages(pages, emb, herbal_crop)
    emit(f"embedding: {len(pages)} pages x 2 variants x 8 views on {emb.dev}, {time.time() - te:.0f}s")
    P, Pparts = zsim(Em)
    Pt, _ = zsim(Et)
    fa = [infos[p]["frac_area"] for p in pages]
    emit(f"masking: boxes painted per page median {np.median([infos[p]['n_boxes'] for p in pages]):.0f}; share of canvas "
         f"area masked median {np.median(fa):.3f}; dark-ink share inside boxes before {np.mean([infos[p]['ink_in_boxes_before'] for p in pages]):.4f} "
         f"-> after {np.mean([infos[p]['ink_in_boxes_after'] for p in pages]):.4f}; share of boxes touching the plant crop "
         f"{np.mean([infos[p]['crop_box_overlap'] for p in pages]):.3f}; ring-median fallbacks {sum(infos[p]['n_fallback'] for p in pages)}")
    meta = {p: hdr[p] for p in pages}
    masking_check(Em, Et, P, Pt, pages, meta, "herbal")
    np.savez(OUT / "embeddings.npz", pages=np.array(pages), dino_masked=Em["dino"], siglip_masked=Em["siglip"],
             dino_textin=Et["dino"], siglip_textin=Et["siglip"])
    # sample masked crops for inspection
    for p in pages[:6]:
        m_arr, t_arr, parch, _ = herbal_crop(p)
        prep(m_arr, parch).save(OUT / f"sample_masked_{p}.png")
        prep(t_arr, parch).save(OUT / f"sample_textin_{p}.png")

    emit("")
    emit("=" * 100)
    emit("HERBAL (pre-registered)")
    emit("=" * 100)
    res = analyse("herbal", pages, meta, P, Pparts, Pt, {tr: texts_H[tr] for tr, _ in TRANSLITS}, fit_H, Em, rng)
    res["P"] = P
    # pools for C+
    seg_zl = SlotSegmenter(fit_H["ZL3b"])
    allc = Counter()
    hand_c = defaultdict(Counter)
    for p, toks in texts_H["ZL3b"].items():
        cs = [seg_zl.segment(w)[1] for w in toks]
        allc.update(cs)
        hand_c[hdr[p]["hand"]].update(cs)
    hand_pools = {}
    for h, c in hand_c.items():
        ks = sorted(c)
        w = np.array([c[k] for k in ks], float)
        hand_pools[h] = (ks, w / w.sum())
    emit("")
    emit("   controls (ZL3b cores, scored identically):")
    ctl = run_controls(res, pages, meta, Em, rng, hand_pools, allc)
    v, why = verdict(res, ctl)
    emit("")
    emit(f"   VERDICT (pre-registered): {v}")
    for w in why:
        emit(f"     - {w}")
    emit("")
    tp = top_pairs(res, pages, meta)
    np.savez(OUT / "matrices.npz", pages=np.array(pages), picture_masked=P, picture_textin=Pt,
             picture_dino=Pparts["dino"], picture_siglip=Pparts["siglip"],
             **{f"text_{tr}_{u}": res["TM"][(tr, u)] for tr, _ in TRANSLITS for u in ("cores", "words", "frames")})

    # ---- descriptive: pharma
    emit("")
    emit("=" * 100)
    emit("DESCRIPTIVE (no verdict)")
    emit("=" * 100)
    E48 = np.load(S48 / "embeddings.npz")
    idx = {c: i for i, c in enumerate(E48["ids"].tolist())}
    ph_pages = [p for p in pr.PHARMA_IDS if any(c["kind"] == "pharma" and c["page"] == p for c in crops)]
    ph_pages = [p for p in ph_pages if p in hdr and zl_recs.get(p)]
    Eph = {}
    for m in ("dino", "siglip"):
        rows = []
        for p in ph_pages:
            ii = [idx[c["crop"]] for c in crops if c["kind"] == "pharma" and c["page"] == p]
            v_ = E48[m][ii].mean(0)
            rows.append(v_ / np.linalg.norm(v_))
        Eph[m] = np.stack(rows)
    Pph, Pph_parts = zsim(Eph)
    ph_txt = {p: [w for r in zl_recs[p] for w in r["words"] if "?" not in w] for p in ph_pages}
    ph_fit = [w for v_ in ph_txt.values() for w in v_]
    emit(f"PHARMA: {len(ph_pages)} pages ({', '.join(ph_pages)}); picture = mean of all s48 crops (containers + plants); "
         f"text = all ZL3b loci (P + labels); segmenter fitted on these {len(ph_fit)} tokens")
    meta_ph = {p: hdr[p] for p in ph_pages}
    res_ph = analyse("pharma", ph_pages, meta_ph, Pph, Pph_parts, None, {"ZL3b": ph_txt}, {"ZL3b": ph_fit}, None,
                     rng, fixture=True)
    # ---- descriptive: biological
    emit("")
    texts_B, fit_B = load_texts("B")
    bio = sorted(p for p, v in hdr.items() if v["illus"] == "B" and (S45 / f"{p}.json").exists() and p in box_have
                 and texts_B["ZL3b"].get(p))
    breg = {}
    for p in bio:
        rec = json.loads((S45 / f"{p}.json").read_text(encoding="utf-8"))
        breg[p] = register(p, rec, boxmod.load_boxes(p), zl_recs[p], rrng)
    bio_ok = [p for p in bio if breg[p]["ok"]]
    emit(f"BIOLOGICAL: {len(bio)} $I=B pages with s45 record + boxes + text; registration accepted {len(bio_ok)}; "
         f"picture = whole trimmed page, box-masked; text = ZL3b P loci; segmenter fitted on biological P tokens")
    for p in bio:
        if not breg[p]["ok"]:
            emit(f"   {p}: excluded, {breg[p]['why']}")
    res_bio = None
    if len(bio_ok) >= 6:
        def bio_crop(pid):
            rec = json.loads((S45 / f"{pid}.json").read_text(encoding="utf-8"))
            arr = np.asarray(Image.open(SCANS / rec["file"]).convert("RGB"))
            sb = scan_boxes_for(boxmod.load_boxes(pid), breg[pid]["A"])
            marr, info = mask_boxes(arr, sb)
            tx0, ty0, tx1, ty1 = pr.page_trim(arr)
            parch = [int(t) for t in pr.masks(arr, pr.PARAMS)[2]]
            return marr[ty0:ty1, tx0:tx1], arr[ty0:ty1, tx0:tx1], parch, info
        Emb, Etb, _ = embed_pages(bio_ok, emb, bio_crop)
        Pb, Pb_parts = zsim(Emb)
        Pbt, _ = zsim(Etb)
        meta_b = {p: hdr[p] for p in bio_ok}
        masking_check(Emb, Etb, Pb, Pbt, bio_ok, meta_b, "biological")
        res_bio = analyse("biological", bio_ok, meta_b, Pb, Pb_parts, Pbt, {"ZL3b": texts_B["ZL3b"]}, {"ZL3b": fit_B["ZL3b"]},
                          None, rng, fixture=True)
        np.savez(OUT / "bio.npz", pages=np.array(bio_ok), picture_masked=Pb, picture_textin=Pbt,
                 text_cores=res_bio["TM"][("ZL3b", "cores")], dino=Emb["dino"], siglip=Emb["siglip"])
    pj = dict(verdict=v, why=why, controls={k: v_ for k, v_ in ctl.items() if k != "groups"}, groups=ctl["groups"],
              pages=pages, excluded=excl, rows=[{k: x for k, x in r.items()} for r in res["rows"]], top_pairs=tp,
              pharma_rows=res_ph["rows"], bio_rows=(res_bio["rows"] if res_bio else None))
    (OUT / "summary.json").write_text(json.dumps(pj, indent=1, default=str), encoding="utf-8", newline="\n")
    return v


# =============================================================== fixture
def fixture_main(t0):
    """Synthetic images + synthetic text.  Two worlds: LINK (cores planted by picture group) and NOLINK."""
    from PIL import Image, ImageDraw
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    N, G = 72, 6
    hands = ["1", "2", "3"]
    meta, pages = {}, []
    for i in range(N):
        p = f"x{i:03d}"
        pages.append(p)
        q = "ABCDEF"[i // 12]
        meta[p] = dict(hand=hands[(i // 12) % 3], quire=q, bif=f"{q}:{(i % 12) // 4}", lang="A" if (i // 12) % 3 == 0 else "B")
    group = rng.integers(0, G, N)
    shapes = ["ellipse", "rect", "tri", "star", "cross", "ring"]
    cols = [(60, 140, 90), (150, 60, 50), (60, 80, 160), (170, 140, 60), (90, 160, 160), (120, 70, 140)]

    def draw_page(i):
        W, H = 600, 800
        im = Image.new("RGB", (W, H), (205, 185, 150))
        d = ImageDraw.Draw(im)
        g = group[i]
        cx, cy = 300 + rng.integers(-40, 40), 520 + rng.integers(-40, 40)
        r = 120 + rng.integers(-25, 25)
        col = tuple(int(c + rng.integers(-20, 20)) for c in cols[g])
        sh = shapes[g]
        if sh == "ellipse":
            d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=col)
        elif sh == "rect":
            d.rectangle([cx - r, cy - r * 0.5, cx + r, cy + r * 0.5], fill=col)
        elif sh == "tri":
            d.polygon([(cx, cy - r), (cx - r, cy + r * 0.7), (cx + r, cy + r * 0.7)], fill=col)
        elif sh == "star":
            pts = [(cx + (r if k % 2 == 0 else r * 0.4) * np.cos(k * np.pi / 5), cy + (r if k % 2 == 0 else r * 0.4) * np.sin(k * np.pi / 5)) for k in range(10)]
            d.polygon(pts, fill=col)
        elif sh == "cross":
            d.rectangle([cx - r, cy - 25, cx + r, cy + 25], fill=col); d.rectangle([cx - 25, cy - r, cx + 25, cy + r], fill=col)
        else:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=30)
        d.line([(cx, cy + r), (cx, 790)], fill=(110, 80, 50), width=6)
        # text: hand-specific stroke style in box rows across the plant region too (to test masking)
        hb = []
        hs = {"1": 3, "2": 5, "3": 7}[meta[pages[i]]["hand"]]
        y = 60
        while y < 700:
            x = 40
            while x < 540:
                w = int(rng.integers(30, 90))
                for k in range(x, min(x + w, 560), hs + 4):
                    d.line([(k, y + 4), (k + hs, y + 16)], fill=(70, 50, 35), width=2)
                hb.append(dict(x=x, y=y, w=w, h=20))
                x += w + int(rng.integers(8, 20))
            y += 34 if y < 300 else 120
        return np.asarray(im), hb

    imgs = [draw_page(i) for i in range(N)]
    emb = Embedder()

    def crop_fn(pid):
        i = pages.index(pid)
        arr, hb = imgs[i]
        sb = [(b["x"] - PAD_BOX, b["y"] - PAD_BOX, b["x"] + b["w"] + PAD_BOX, b["y"] + b["h"] + PAD_BOX) for b in hb]
        marr, info = mask_boxes(arr, sb)
        return marr, arr, [205, 185, 150], info

    Em, Et, infos = embed_pages(pages, emb, crop_fn)
    P, Pparts = zsim(Em)
    Pt, _ = zsim(Et)
    emit(f"fixture: {N} synthetic pages, {G} picture groups (shape+colour), 3 hands x 6 quires; text strokes hand-styled")
    emit(f"masking: ink share inside boxes before {np.mean([v['ink_in_boxes_before'] for v in infos.values()]):.4f} -> after "
         f"{np.mean([v['ink_in_boxes_after'] for v in infos.values()]):.4f}")
    masking_check(Em, Et, P, Pt, pages, meta, "fixture")
    iu, ju = np.triu_indices(N, 1)
    sg = group[iu] == group[ju]
    emit(f"   picture z same-group minus different-group (masked): {P[iu, ju][sg].mean() - P[iu, ju][~sg].mean():+.3f}")
    # synthetic vocabulary: prefix + core + suffix
    pre = ["q", "o", "ch", "sh", "qo"]
    suf = ["y", "dy", "aiin", "ol", "am"]
    core_pool = [a + b for a in ["k", "t", "p", "f", "d", "l", "r", "s"] for b in ["e", "ee", "a", "o", "ai", "eo"]]
    hand_core = {h: rng.dirichlet(np.ones(len(core_pool)) * 0.5) for h in hands}
    grp_cores = {g: rng.choice(len(core_pool), 8, replace=False) for g in range(G)}
    hand_frame = {h: (rng.dirichlet(np.ones(5)), rng.dirichlet(np.ones(5))) for h in hands}

    def make_text(link, noise_rate):
        tx = {}
        for i, p in enumerate(pages):
            h = meta[p]["hand"]
            toks = []
            for _ in range(int(rng.integers(80, 160))):
                if link and rng.random() < 0.30:
                    c = core_pool[rng.choice(grp_cores[group[i]])]
                else:
                    c = core_pool[rng.choice(len(core_pool), p=hand_core[h])]
                a = pre[rng.choice(5, p=hand_frame[h][0])]; b = suf[rng.choice(5, p=hand_frame[h][1])]
                w = a + c + b
                if rng.random() < noise_rate:
                    w = w + "y"
                toks.append(w)
            tx[p] = toks
        return tx

    for world, link in (("LINK (30% of cores planted by picture group)", True), ("NOLINK", False)):
        emit("")
        emit("=" * 100)
        emit(f"FIXTURE WORLD: {world}")
        emit("=" * 100)
        base = make_text(link, 0.0)
        texts = {"ZL3b": base,
                 "RF1b": {p: [w if rng.random() > 0.05 else w[:-1] or w for w in v] for p, v in base.items()},
                 "IT2a": {p: [w if rng.random() > 0.05 else w + "o" for w in v] for p, v in base.items()}}
        fit = {tr: [w for v in texts[tr].values() for w in v] for tr in texts}
        res = analyse("fixture", pages, meta, P, Pparts, Pt, texts, fit, Em, rng, fixture=True)
        res["P"] = P
        seg = SlotSegmenter(fit["ZL3b"])
        allc = Counter(); hc = defaultdict(Counter)
        for p, toks in texts["ZL3b"].items():
            cs = [seg.segment(w)[1] for w in toks]
            allc.update(cs); hc[meta[p]["hand"]].update(cs)
        hand_pools = {h: (sorted(c), np.array([c[k] for k in sorted(c)], float) / sum(c.values())) for h, c in hc.items()}
        ctl = run_controls(res, pages, meta, Em, rng, hand_pools, allc)
        v, why = verdict(res, ctl)
        emit(f"   fixture verdict: {v}  (expected: {'picture-linked cores' if link else 'no picture link detected'})")
        for w in why:
            emit(f"     - {w}")
        top_pairs(res, pages, meta, k=5)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    start = clock()
    me = sha256(Path(__file__))
    sm = stub_match()
    emit(f"s78_picture_text_similarity.py sha256={me}")
    emit(f"stub_match={sm}")
    emit(f"run start: {start}")
    emit(f"mode: {'FIXTURE (synthetic only)' if a.fixture else 'REAL DATA'}; seed {SEED}; perms {NPERM}; "
         f"controls {NREP} reps; C+ s={CPLUS_S}, k={K_GROUPS}, pool {POOL_TYPES} types (count >= {POOL_MINCOUNT})")
    emit("")
    if a.fixture:
        fixture_main(t0)
        target = OUT / "fixture.txt"
    else:
        real_main(t0)
        target = ROOT / "results_s78.txt"
    emit("")
    emit(f"run end: {clock()}; elapsed {time.time() - t0:.0f}s")
    target.write_text("\n".join(LOG) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
