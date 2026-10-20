#!/usr/bin/env python
"""s103 (D-066 (i)): do Voynich herbal plants match plants of the period illustrated-herbal tradition, and if so as
whole plants (copying drift) or via a consistent part-wise mapping (deliberate disguise)?

PRE-REGISTERED.  The sha256 of this file, of the image manifest (runs/s103/image_manifest.txt: every image and
caption file used, with sha256) are frozen in s103_herbal_tradition_matching.prereg.sha256 before the real run.
D-066 (i) thresholds (copied, not changed): recovery gate first (same species across the comparison herbals
retrieved above chance; if it fails, the Voynich comparison is not run: HOLD); Voynich-to-tradition top-1/top-5
retrieval better than a page-permutation null with p < 0.05 in BOTH representations = match signal, MDE stated;
mode decided by which representation carries the matches; no match at adequate power -> copying drift excluded
at this resolution, do not vary features afterwards; matches -> candidate cribs for a separately frozen test.

DATA
  Voynich: the 123 s48 herbal crops runs/s48/crops/H_<page>.png (text inside s45 line boxes whitened to parchment;
    parchment colour in runs/s48/crops.json).
  Tradition (new evidence, untrusted data, read only as images/JSON):
    ljs419    Penn Oversize LJS 419 'Erbario' (N. Italy, 15th c.), Penn IIIF, 1024 px high, Public Domain Mark 1.0.
    sloane4016 BL Sloane MS 4016 (Lombardy c.1440), BL IIIF 769x1024, 'Public Domain in most countries other than
      the UK' (manifest usage terms).
    Plant boxes and caption names: data/herbals_period/<ms>/captions_s103.json, a visual transcription of the plant
    name written on the page (Claude subagents; the name is taken only from the writing, never from the picture;
    unverified against a printed edition).  Morgan M.873: no open licence found -> not used.
  Species key of a tradition plant = first word of (latin_equiv or name_key), lower-case, letters only, after
    dropping a leading 'herba/erba/radix/semen/flos/flores/de'; plants with confidence 'low' or no name get no key.
    Keys are matched exactly (genus/lemma level: 'aristolochia longa' and 'aristolochia rotunda' share a key).
  S = keys present in both herbals (the shared set).

SEGMENTATION (simple, documented; same for every source)
  Crop (tradition: caption bbox expanded 2 % per side; Voynich: the s48 crop) resized to max side 512.
  Background = median RGB of the outer 4 % border.  dE = CIELAB distance from background; T = max(FG_DE (18),
  Otsu(dE)); fg = dE > T or L* < L*_bg - max(FG_DL (25), T).  Closed with a disc of 1 % of the max side,
  components < 2 % of the largest dropped (no hole filling) -> silhouette.  [revision 2]  Plant box = silhouette bbox.  Parts by height of the plant box: flower = top 30 %,
  stem/leaf = middle 40 %, root = bottom 30 % (position rule; no colour, so ink-only drawings segment the same way).

REPRESENTATIONS
  A (part-level, style-suppressed): for each part's binary silhouette (cropped to its own bbox):
    handcrafted: 7 log-Hu moments, log aspect, solidity, extent, log compactness, log1p #components,
      16 contour-Fourier magnitudes (centroid-distance signature, 64 samples, |F_1..16|/|F_0|),
      16-bin row-fill and 16-bin column-fill profiles (60 dims);
    style-normalized embedding: DINOv2 ViT-B/14 CLS of the silhouette drawn black on white (views: identity +
      hflip, averaged).
    Each block z-scored over all items, then centred per source (Voynich / LJS / Sloane mean subtracted: removes
    the manuscript-level style offset), L2-normalised.  part sim = (cos_hand + cos_dino) / 2;
    plant sim A = mean of the three part sims.
  B (whole-plant): DINOv2 CLS + SigLIP B/16 image features of the colour crop (plant box, padded square with the
    background colour; identity + hflip), each centred per source and L2-normalised; sim B = mean of the 2 cosines.

GATE 1 (recovery; run first; per representation)
  Queries: every keyed LJS plant whose key is in S (gallery: all keyed Sloane plants) and every keyed Sloane plant
  whose key is in S (gallery: all keyed LJS plants).  rank = 1 + #gallery items with sim strictly above the best
  same-key gallery item.  MRR over all queries.  Null: 10,000 joint permutations of the key labels over each
  gallery (seed 20261018).  p = (1 + #null MRR >= obs) / 10,001.
  GATE_<rep> = p < 0.05.  Gate 1 passes (Voynich comparison run) iff GATE_A or GATE_B.  A representation whose own
  gate fails is reported as uncalibrated (its negative is not at adequate power).  If |S| < 5 the gate fails.

VOYNICH COMPARISON (only if gate 1 passes)
  For a query q: per key k in S, score_L(k) = max sim(q, LJS plants with key k), score_S(k) likewise for Sloane
  (query itself excluded from the galleries).  hit1(q) = [argmax_L == argmax_S] (the two independent herbals
  identify the same species); hit5(q) = mean([rank_S(argmax_L) <= 5], [rank_L(argmax_S) <= 5]).
  Groups: V = Voynich pages; C (style-controlled null population) = keyed tradition plants whose key is NOT in S
  (real period drawings of species outside the shared set); P (positive control) = keyed tradition plants with key
  in S.  Statistic d = mean_V - mean_C for hit1 and hit5.  Page-permutation null: 10,000 permutations of the group
  label over the pooled V+C pages; p = (1 + #null d >= obs) / 10,001.
  MDE (printed before the Voynich scores, from C only): (1.645 + 0.842) * sd_C * sqrt(1/nV + 1/nC) per statistic.
  Adequate power for rep r: GATE_r and MDE(hit1) <= 0.20 (a fifth of the Voynich pages agreeing more often than
  the control rate would be detected).  [Pre-freeze revision 1, after the synthetic fixture: the first rule used
  mean_P - mean_C, but P queries lose their own drawing from their own herbal (self-exclusion), so P is biased
  low by construction (fixture: P hit1 0.03 vs C 0.78); P is now printed descriptively only.]  SIGNAL_r = p_hit1 < 0.05 or p_hit5 < 0.05.  MATCH = SIGNAL_A and SIGNAL_B (D-066 (i) (2)).
  Part-wise (rep A only, per part p): key_p(q) = argmax_k (score_L,p(k) + score_S,p(k)) / 2, hit1_p as above.
    mixed(q) = some two parts are each cross-herbal consistent (hit1_p) with different keys.
    p_mixed: V vs C page-permutation as above.  repeat: share of mixed V pages whose ordered (root key, stem/leaf
    key, flower key) pattern, restricted to the consistent parts, recurs on another V page; null = same share under
    10,000 permutations of each part's keys across the mixed V pages (independent per part); p_repeat.
  MODE (only if MATCH; D-066 (i) (3), which representation carries the matches): z_r = (d_obs - null mean) /
    null sd for hit1.  z_B >= z_A -> 'whole-plant (copying drift)'; z_A > z_B -> 'part-wise', with
    '(consistent mapping: deliberate disguise)' appended if p_repeat < 0.05, else '(no consistent mapping)'.
    p_mixed is printed (descriptive).  [Revision 1: the fixture showed the p_mixed test does not detect planted
    part chimeras (p_mixed 0.30) while p_repeat does (0.0001); part chimeras also lower hit1 in both reps, so this
    design has low power for a pure part-wise disguise: a negative does not exclude disguise.]
  Cribs (only if MATCH): Voynich pages with hit1 in both reps, listed with the agreed key and the two herbals'
  captions, as candidates for a separately frozen later test.  No reading claim.
VERDICT rules (follow the printed calls):
  gate fails -> 'HOLD: recovery gate failed'; MATCH -> 'MATCH: <mode>'; no MATCH with adequate power in both
  reps -> 'NO MATCH at adequate power: copying drift excluded at this resolution'; otherwise 'NO MATCH,
  underpowered (<reps>)'.

Usage (scratchpad venv with torch + transformers + cv2; run with -I):
    python -I s103_herbal_tradition_matching.py --fixture    -> runs/s103/fixture_run<k>.txt (never overwritten)
    python -I s103_herbal_tradition_matching.py --manifest   -> runs/s103/image_manifest.txt (before freezing)
    python -I s103_herbal_tradition_matching.py --real       -> results_s103.txt (never overwritten)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "runs" / "s103"
HP = ROOT / "data" / "herbals_period"
MODELS = ROOT / "data" / "external" / "models"
STUB = ROOT / "s103_herbal_tradition_matching.prereg.sha256"
RESULTS = ROOT / "results_s103.txt"
SEED, NPERM = 20261018, 10000
FG_DE, FG_DL = 18.0, 25.0
WORK = 512
PARTS = ("flower", "stemleaf", "root")
BANDS = {"flower": (0.0, 0.30), "stemleaf": (0.30, 0.70), "root": (0.70, 1.0)}
DROP = {"herba", "erba", "radix", "semen", "flos", "flores", "de", "la", "el", "lo", "il"}
MSS = {"ljs419": HP / "ljs419" / "iiif", "sloane4016": HP / "sloane4016"}


def log(fh, s=""):
    print(s, flush=True)
    if fh is not None:
        fh.write(s + "\n")
        fh.flush()


def now():
    return subprocess.run(["date"], capture_output=True, text=True).stdout.strip()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ----------------------------------------------------------------------------------------------------------- keys
def species_key(rec):
    if rec.get("confidence") == "low":
        return None
    name = rec.get("latin_equiv") or rec.get("name_key")
    if not name:
        return None
    words = [w for w in re.sub(r"[^a-z ]", " ", name.lower().replace("j", "i").replace("v", "u")).split()]
    while words and words[0] in DROP:
        words = words[1:]
    if not words or len(words[0]) < 3:
        return None
    return words[0]


# --------------------------------------------------------------------------------------------------- segmentation
def silhouette(rgb):
    """rgb uint8 (h, w, 3) at work scale -> (mask bool, bg rgb)."""
    import cv2
    h, w = rgb.shape[:2]
    b = max(2, int(0.04 * min(h, w)))
    border = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3),
                             rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
    bg = np.median(border, axis=0).astype(np.uint8)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    lbg = cv2.cvtColor(bg.reshape(1, 1, 3), cv2.COLOR_RGB2LAB).astype(np.float32)[0, 0]
    L = lab[..., 0] * 100 / 255
    Lb = lbg[0] * 100 / 255
    de = np.sqrt(((lab[..., 0] - lbg[0]) * 100 / 255) ** 2 + (lab[..., 1] - lbg[1]) ** 2 + (lab[..., 2] - lbg[2]) ** 2)
    # revision 2 (pre-freeze, after a visual check of 12 Sloane + 6 Voynich crops: fixed thresholds and hole
    # filling turned uneven parchment into solid blocks and dropped thin stems): adaptive threshold
    # max(FG_DE, Otsu(dE)), no hole filling, components kept down to 2 % of the largest.
    de8 = np.clip(de * 2, 0, 255).astype(np.uint8)
    otsu, _ = cv2.threshold(de8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    T = max(FG_DE, otsu / 2)
    fg = (de > T) | (L < Lb - max(FG_DL, T))
    k = max(3, int(0.01 * max(h, w)) | 1)
    m = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lab_cc, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return np.zeros((h, w), bool), bg
    areas = st[1:, 4]
    keep = np.where(areas >= 0.02 * areas.max())[0] + 1
    m = np.isin(lab_cc, keep)
    return m, bg


def bbox(mask):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def to_work(img):
    from PIL import Image
    w, h = img.size
    s = WORK / max(w, h)
    return np.asarray(img.convert("RGB").resize((max(1, int(w * s)), max(1, int(h * s))), Image.BILINEAR))


def segment(rgb):
    """-> dict(colour crop rgb, bg, sil (plant box), parts{name: binary crop or None})."""
    m, bg = silhouette(rgb)
    bb = bbox(m)
    if bb is None:
        return None
    x0, y0, x1, y1 = bb
    sil = m[y0:y1, x0:x1]
    col = rgb[y0:y1, x0:x1]
    H = sil.shape[0]
    parts = {}
    for p, (a, b) in BANDS.items():
        band = sil[int(a * H):max(int(a * H) + 1, int(b * H))]
        pb = bbox(band)
        parts[p] = None if (pb is None or band.sum() < 0.01 * sil.sum() + 4) else band[pb[1]:pb[3], pb[0]:pb[2]]
    return {"col": col, "bg": bg, "sil": sil, "parts": parts}


# ------------------------------------------------------------------------------------------------------- features
def hand_features(b):
    import cv2
    f = np.zeros(60, np.float32)
    if b is None or b.sum() < 4:
        return f, False
    u = b.astype(np.uint8)
    hu = cv2.HuMoments(cv2.moments(u, True)).ravel()
    f[:7] = -np.sign(hu) * np.log10(np.abs(hu) + 1e-30)
    f[:7] = np.clip(f[:7], -40, 40)
    h, w = u.shape
    cs, _ = cv2.findContours(u, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    area = float(u.sum())
    hull = cv2.convexHull(c)
    ha = max(cv2.contourArea(hull), 1.0)
    per = max(cv2.arcLength(c, True), 1.0)
    f[7] = np.log(h / w)
    f[8] = min(area / ha, 1.0)
    f[9] = area / (h * w)
    f[10] = np.log(per ** 2 / area)
    f[11] = np.log1p(len(cs))
    pts = c[:, 0, :].astype(np.float32)
    if len(pts) >= 8:
        cen = pts.mean(0)
        r = np.linalg.norm(pts - cen, axis=1)
        idx = np.linspace(0, len(r) - 1, 64).astype(int)
        F = np.abs(np.fft.fft(r[idx]))
        f[12:28] = F[1:17] / max(F[0], 1e-6)
    rows = u.mean(1)
    cols = u.mean(0)
    f[28:44] = np.interp(np.linspace(0, len(rows) - 1, 16), np.arange(len(rows)), rows)
    f[44:60] = np.interp(np.linspace(0, len(cols) - 1, 16), np.arange(len(cols)), cols)
    return f, True


def sil_image(b, size=224):
    from PIL import Image
    if b is None:
        return Image.new("RGB", (size, size), (255, 255, 255))
    h, w = b.shape
    s = max(h, w)
    can = np.full((s, s), 255, np.uint8)
    can[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w][b] = 0
    return Image.fromarray(can).convert("RGB").resize((size, size), Image.BILINEAR)


def col_image(col, bg, size=224):
    from PIL import Image
    h, w = col.shape[:2]
    s = max(h, w)
    can = np.empty((s, s, 3), np.uint8)
    can[:] = bg
    can[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = col
    return Image.fromarray(can).resize((size, size), Image.BICUBIC)


class Embedder:
    def __init__(self):
        import torch
        from transformers import AutoModel, SiglipModel
        self.t = torch
        self.dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.dino = AutoModel.from_pretrained(str(MODELS / "dinov2-base"), use_safetensors=True).to(self.dev).eval()
        self.sig = SiglipModel.from_pretrained(str(MODELS / "siglip-base-patch16-224"),
                                               use_safetensors=True).to(self.dev).eval()
        self.norms = {"dino": ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), "siglip": ((0.5,) * 3, (0.5,) * 3)}

    def __call__(self, imgs, model, bs=64):
        from PIL import Image
        t = self.t
        out = []
        m, s = self.norms[model]
        mt = t.tensor(m, device=self.dev).view(1, 3, 1, 1)
        st = t.tensor(s, device=self.dev).view(1, 3, 1, 1)
        with t.no_grad():
            for i in range(0, len(imgs), bs):
                chunk = imgs[i:i + bs]
                arr = []
                for im in chunk:
                    arr.append(np.asarray(im, np.float32) / 255.0)
                    arr.append(np.asarray(im.transpose(Image.FLIP_LEFT_RIGHT), np.float32) / 255.0)
                x = t.from_numpy(np.stack(arr)).permute(0, 3, 1, 2).to(self.dev)
                x = (x - mt) / st
                f = self.dino(pixel_values=x).last_hidden_state[:, 0] if model == "dino" else \
                    self.sig.get_image_features(pixel_values=x)
                f = t.nn.functional.normalize(f.float(), dim=-1).view(len(chunk), 2, -1).mean(1)
                out.append(t.nn.functional.normalize(f, dim=-1).cpu().numpy())
                del x, f
                if self.dev.startswith("cuda"):
                    t.cuda.empty_cache()
        return np.concatenate(out)


def featurize(segs, emb):
    """segs: list of segment dicts -> dict of raw feature blocks."""
    n = len(segs)
    F = {"hand": np.zeros((len(PARTS), n, 60), np.float32), "present": np.zeros((len(PARTS), n), bool)}
    sil_imgs = {p: [] for p in PARTS}
    col_imgs = []
    for i, s in enumerate(segs):
        for j, p in enumerate(PARTS):
            F["hand"][j, i], F["present"][j, i] = hand_features(s["parts"][p])
            sil_imgs[p].append(sil_image(s["parts"][p]))
        col_imgs.append(col_image(s["col"], s["bg"]))
    F["sil_dino"] = np.stack([emb(sil_imgs[p], "dino") for p in PARTS])
    F["col_dino"] = emb(col_imgs, "dino")
    F["col_sig"] = emb(col_imgs, "siglip")
    return F


def l2(x):
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-9)


def build_reps(F, src):
    """z-score, centre per source, L2.  Returns A_hand (3,n,d), A_dino (3,n,d), B_dino, B_sig (n,d), present."""
    src = np.asarray(src)
    out = {}
    for name in ("hand", "sil_dino"):
        X = F[name].astype(np.float64).copy()
        for j in range(len(PARTS)):
            pres = F["present"][j]
            mu = X[j][pres].mean(0)
            sd = X[j][pres].std(0) + 1e-6
            Z = (X[j] - mu) / sd if name == "hand" else X[j] - mu
            for s in np.unique(src):
                sel = (src == s) & pres
                if sel.any():
                    Z[src == s] -= Z[sel].mean(0)
            Z[~pres] = 0.0
            X[j] = l2(Z) * pres[:, None]
        out[name] = X
    for name in ("col_dino", "col_sig"):
        X = F[name].astype(np.float64).copy()
        X -= X.mean(0)
        for s in np.unique(src):
            X[src == s] -= X[src == s].mean(0)
        out[name] = l2(X)
    out["present"] = F["present"]
    return out


def sims(R, qi, gi):
    """similarity matrices (|qi| x |gi|) per rep: 'A' (plant), 'A_parts' (3, q, g), 'B'."""
    parts = np.stack([(R["hand"][j][qi] @ R["hand"][j][gi].T + R["sil_dino"][j][qi] @ R["sil_dino"][j][gi].T) / 2
                      for j in range(len(PARTS))])
    return {"A": parts.mean(0), "A_parts": parts,
            "B": (R["col_dino"][qi] @ R["col_dino"][gi].T + R["col_sig"][qi] @ R["col_sig"][gi].T) / 2}


# ------------------------------------------------------------------------------------------------------- stats
def gate_stat(R, keys, src, rng, fh, label):
    """Gate 1 per representation.  Returns dict rep -> (mrr, p, top1, top5, nq)."""
    keys = np.asarray(keys, dtype=object)
    src = np.asarray(src)
    kL = set(k for k, s in zip(keys, src) if k and s == "ljs419")
    kS = set(k for k, s in zip(keys, src) if k and s == "sloane4016")
    Sset = sorted(kL & kS)
    log(fh, f"[{label}] keyed plants: ljs419 {sum(1 for k, s in zip(keys, src) if k and s == 'ljs419')}, "
            f"sloane4016 {sum(1 for k, s in zip(keys, src) if k and s == 'sloane4016')}; shared keys |S| = {len(Sset)}")
    log(fh, f"[{label}] S = {', '.join(Sset)}")
    res = {}
    if len(Sset) < 5:
        log(fh, f"[{label}] |S| < 5 -> gate fails")
        return {r: (float('nan'), 1.0, 0, 0, 0) for r in ("A", "B")}, Sset
    gal = {m: np.where((src == m) & np.array([k is not None for k in keys]))[0] for m in ("ljs419", "sloane4016")}
    other = {"ljs419": "sloane4016", "sloane4016": "ljs419"}
    for rep in ("A", "B"):
        blocks = []  # (sim rows (q x g), gallery keys, query keys)
        for m in ("ljs419", "sloane4016"):
            q = np.array([i for i in gal[m] if keys[i] in Sset])
            g = gal[other[m]]
            S = sims(R, q, g)[rep]
            blocks.append((S, keys[g], keys[q]))

        def mrr_of(perm_keys_list):
            rr, t1, t5 = [], 0, 0
            for (S, gk, qk), pk in zip(blocks, perm_keys_list):
                for a in range(S.shape[0]):
                    same = pk == qk[a]
                    if not same.any():
                        rr.append(0.0)
                        continue
                    best = S[a][same].max()
                    rank = 1 + int((S[a] > best).sum())
                    rr.append(1.0 / rank)
                    t1 += rank == 1
                    t5 += rank <= 5
            return float(np.mean(rr)), t1, t5, len(rr)

        obs, t1, t5, nq = mrr_of([b[1] for b in blocks])
        null = np.empty(NPERM)
        for i in range(NPERM):
            null[i] = mrr_of([rng.permutation(b[1]) for b in blocks])[0]
        p = (1 + int((null >= obs).sum())) / (NPERM + 1)
        log(fh, f"[{label}] rep {rep}: MRR={obs:.4f} null mean={null.mean():.4f} q95={np.quantile(null, .95):.4f} "
                f"P={p:.4f} top1={t1}/{nq} top5={t5}/{nq}")
        res[rep] = (obs, p, t1, t5, nq)
    return res, Sset


def query_scores(R, qi, keys, src, Sset, exclude_self=True):
    """per query: hit1, hit5 for reps A and B, plus part-level (key, consistent) for rep A."""
    keys = np.asarray(keys, dtype=object)
    src = np.asarray(src)
    gal = {m: np.array([i for i in range(len(keys)) if src[i] == m and keys[i] in Sset]) for m in ("ljs419", "sloane4016")}
    Sidx = {k: i for i, k in enumerate(Sset)}
    out = {"A": {"hit1": [], "hit5": []}, "B": {"hit1": [], "hit5": []}, "parts": [], "top": []}
    sm = {m: sims(R, np.asarray(qi), gal[m]) for m in gal}

    def keyscores(S, m, a, q):
        ks = np.full(len(Sset), -np.inf)
        for col, gidx in enumerate(gal[m]):
            if exclude_self and gidx == q:
                continue
            k = Sidx[keys[gidx]]
            ks[k] = max(ks[k], S[a, col])
        return ks

    def hits(kL, kS):
        aL, aS = int(np.argmax(kL)), int(np.argmax(kS))
        rS = 1 + int((kS > kS[aL]).sum())
        rL = 1 + int((kL > kL[aS]).sum())
        return float(aL == aS), 0.5 * (rS <= 5) + 0.5 * (rL <= 5), aL, aS

    for a, q in enumerate(qi):
        tops = {}
        for rep in ("A", "B"):
            kL = keyscores(sm["ljs419"][rep], "ljs419", a, q)
            kS = keyscores(sm["sloane4016"][rep], "sloane4016", a, q)
            h1, h5, aL, aS = hits(kL, kS)
            out[rep]["hit1"].append(h1)
            out[rep]["hit5"].append(h5)
            tops[rep] = (Sset[aL], Sset[aS])
        pr = []
        for j in range(len(PARTS)):
            kL = keyscores(sm["ljs419"]["A_parts"][j], "ljs419", a, q)
            kS = keyscores(sm["sloane4016"]["A_parts"][j], "sloane4016", a, q)
            h1, _, aL, aS = hits(kL, kS)
            pr.append((Sset[int(np.argmax((kL + kS) / 2))], bool(h1)))
        out["parts"].append(pr)
        out["top"].append(tops)
    for rep in ("A", "B"):
        for k in ("hit1", "hit5"):
            out[rep][k] = np.asarray(out[rep][k])
    return out


def perm_diff(xV, xC, rng):
    pool = np.concatenate([xV, xC])
    nV = len(xV)
    obs = xV.mean() - xC.mean()
    null = np.empty(NPERM)
    for i in range(NPERM):
        pi = rng.permutation(len(pool))
        null[i] = pool[pi[:nV]].mean() - pool[pi[nV:]].mean()
    p = (1 + int((null >= obs).sum())) / (NPERM + 1)
    return obs, p, null


def mixed_flags(parts):
    fl = []
    for pr in parts:
        cons = [k for k, ok in pr if ok]
        fl.append(float(len(cons) >= 2 and len(set(cons)) >= 2))
    return np.asarray(fl)


def repeat_share(patterns):
    if len(patterns) < 2:
        return 0.0
    c = {}
    for p in patterns:
        c[p] = c.get(p, 0) + 1
    return float(np.mean([c[p] >= 2 for p in patterns]))


def compare(R, keys, src, Sset, vi, rng, fh, label, captions=None):
    keys = np.asarray(keys, dtype=object)
    src = np.asarray(src)
    trad = np.where(src != "voynich")[0]
    ci = np.array([i for i in trad if keys[i] is not None and keys[i] not in Sset])
    pi_ = np.array([i for i in trad if keys[i] is not None and keys[i] in Sset])
    QC = query_scores(R, ci, keys, src, Sset)
    QP = query_scores(R, pi_, keys, src, Sset)
    nV = len(vi)
    log(fh, f"[{label}] groups: V = {nV} Voynich pages; C (keyed, key not in S) = {len(ci)}; P (key in S) = {len(pi_)}")
    log(fh, f"[{label}] MDE (one-sided alpha 0.05, power 0.80; from C only, before the Voynich scores):")
    mde, adequate = {}, {}
    for rep in ("A", "B"):
        for st in ("hit1", "hit5"):
            c = QC[rep][st]
            mde[(rep, st)] = (1.645 + 0.842) * c.std(ddof=1) * np.sqrt(1 / nV + 1 / len(c))
            log(fh, f"   rep {rep} {st}: mean_C={c.mean():.4f} mean_P={QP[rep][st].mean():.4f} "
                    f"P-C={QP[rep][st].mean() - c.mean():+.4f} MDE={mde[(rep, st)]:.4f}")
        adequate[rep] = bool(mde[(rep, "hit1")] <= 0.20)
        log(fh, f"   POWER_{rep} (MDE hit1 <= 0.20) = {adequate[rep]}   (P printed descriptively; self-exclusion bias)")
    QV = query_scores(R, np.asarray(vi), keys, src, Sset, exclude_self=False)
    log(fh, f"[{label}] Voynich vs C (page-permutation null, {NPERM} perms):")
    sig, eff = {}, {}
    for rep in ("A", "B"):
        ps = {}
        for st in ("hit1", "hit5"):
            d, p, null = perm_diff(QV[rep][st], QC[rep][st], rng)
            z = (d - null.mean()) / (null.std() + 1e-12)
            ps[st] = p
            eff[(rep, st)] = z
            log(fh, f"   rep {rep} {st}: mean_V={QV[rep][st].mean():.4f} mean_C={QC[rep][st].mean():.4f} d={d:+.4f} "
                    f"P={p:.4f} z={z:+.2f}  (MDE {mde[(rep, st)]:.4f})")
        sig[rep] = ps["hit1"] < 0.05 or ps["hit5"] < 0.05
        log(fh, f"   SIGNAL_{rep} = {sig[rep]}")
    match = sig["A"] and sig["B"]
    log(fh, f"   MATCH (SIGNAL_A and SIGNAL_B) = {match}")
    mV, mC = mixed_flags(QV["parts"]), mixed_flags(QC["parts"])
    dm, pm, _ = perm_diff(mV, mC, rng)
    log(fh, f"[{label}] part-wise mixed: V {mV.mean():.4f} C {mC.mean():.4f} d={dm:+.4f} P_mixed={pm:.4f}")
    pats = [tuple(k if ok else None for k, ok in pr) for pr, f in zip(QV["parts"], mV) if f]
    obs_r = repeat_share(pats)
    null = np.empty(NPERM)
    cols = list(zip(*pats)) if pats else [(), (), ()]
    for i in range(NPERM):
        perm = list(zip(*[rng.permutation(np.array(c, dtype=object)) for c in cols])) if pats else []
        null[i] = repeat_share([tuple(x) for x in perm])
    pr_ = (1 + int((null >= obs_r).sum())) / (NPERM + 1)
    log(fh, f"[{label}] repeat share among {len(pats)} mixed V pages = {obs_r:.4f} null mean {null.mean():.4f} "
            f"P_repeat={pr_:.4f}")
    mode = None
    if match:
        if eff[("B", "hit1")] >= eff[("A", "hit1")]:
            mode = "whole-plant (copying drift)"
        elif pr_ < 0.05:
            mode = "part-wise (consistent mapping: deliberate disguise)"
        else:
            mode = "part-wise (no consistent mapping)"
    log(fh, f"   MODE = {mode}")
    log(fh, f"   carrier: z hit5 A={eff[('A', 'hit5')]:+.2f} B={eff[('B', 'hit5')]:+.2f}; "
            f"hit1 A={eff[('A', 'hit1')]:+.2f} B={eff[('B', 'hit1')]:+.2f}")
    return {"match": match, "sig": sig, "adequate": adequate, "mode": mode, "QV": QV, "mde": mde,
            "p_mixed": pm, "p_repeat": pr_}


# ------------------------------------------------------------------------------------------------------- fixture
def synth_plant(rng, sp, style):
    """sp: dict of species params; style 0 filled green, 1 ink outline, 2 'voynich' (other hues, thick)."""
    import cv2
    H, W = 480, 360
    img = np.full((H, W, 3), (230, 215, 185) if style != 1 else (240, 232, 214), np.uint8)
    col = [(70, 140, 60), (60, 50, 40), (40, 110, 150)][style]
    th = [-1, 2, -1][style]
    cx = W // 2 + int(rng.integers(-15, 16))
    top, bot = 60 + int(rng.integers(-8, 9)), 330 + int(rng.integers(-8, 9))
    cv2.line(img, (cx, top), (cx, bot), col, 4 if style != 1 else 2)
    for i in range(sp["nleaf"]):
        y = int(top + (i + 1) * (bot - top) / (sp["nleaf"] + 1))
        for sgn in (-1, 1):
            L = int(sp["leaflen"] * (1 + 0.1 * rng.standard_normal()))
            c = (cx + sgn * L // 2, y)
            if sp["leaftype"] == 0:
                cv2.ellipse(img, c, (L // 2, sp["leafw"]), sgn * sp["leafang"], 0, 360, col, th)
            elif sp["leaftype"] == 1:
                pts = np.array([[cx, y], [cx + sgn * L, y - sp["leafw"]], [cx + sgn * L // 2, y + sp["leafw"]]])
                cv2.fillPoly(img, [pts], col) if th < 0 else cv2.polylines(img, [pts], True, col, th)
            else:
                cv2.rectangle(img, (min(cx, cx + sgn * L), y - sp["leafw"] // 2), (max(cx, cx + sgn * L),
                              y + sp["leafw"] // 2), col, th)
    fcol = [(200, 60, 60), (60, 50, 40), (150, 60, 160)][style]
    if sp["flower"] == 0:
        cv2.circle(img, (cx, top), sp["fsize"], fcol, th)
    elif sp["flower"] == 1:
        for k in range(5):
            a = 2 * np.pi * k / 5
            cv2.ellipse(img, (int(cx + sp["fsize"] * np.cos(a)), int(top + sp["fsize"] * np.sin(a))),
                        (sp["fsize"] // 2, sp["fsize"] // 4), np.degrees(a), 0, 360, fcol, th)
    else:
        pts = np.array([[cx, top - sp["fsize"]], [cx - sp["fsize"], top + sp["fsize"] // 2],
                        [cx + sp["fsize"], top + sp["fsize"] // 2]])
        cv2.fillPoly(img, [pts], fcol) if th < 0 else cv2.polylines(img, [pts], True, fcol, th)
    rcol = [(120, 90, 60), (60, 50, 40), (110, 70, 50)][style]
    if sp["root"] == 0:
        cv2.ellipse(img, (cx, bot + 40), (sp["rsize"], 40), 0, 0, 360, rcol, th)
    elif sp["root"] == 1:
        for k in range(sp["nroot"]):
            ang = np.pi / 2 + (k - (sp["nroot"] - 1) / 2) * 0.35
            cv2.line(img, (cx, bot), (int(cx + 110 * np.cos(ang)), int(bot + 110 * np.sin(ang))), rcol, 5)
    else:
        cv2.rectangle(img, (cx - sp["rsize"] // 2, bot), (cx + sp["rsize"] // 2, bot + 100), rcol, th)
    return img


def synth_species(rng):
    return {"nleaf": int(rng.integers(2, 7)), "leaflen": int(rng.integers(40, 140)), "leafw": int(rng.integers(8, 35)),
            "leafang": int(rng.integers(-35, 36)), "leaftype": int(rng.integers(0, 3)), "flower": int(rng.integers(0, 3)),
            "fsize": int(rng.integers(12, 40)), "root": int(rng.integers(0, 3)), "rsize": int(rng.integers(20, 80)),
            "nroot": int(rng.integers(2, 6))}


def run_fixture():
    OUT.mkdir(parents=True, exist_ok=True)
    k = 2
    while (OUT / f"fixture_run{k}.txt").exists():
        k += 1
    # never overwrite: runs/s103/fixture.txt holds run 1 of the revision-1 script (run 0, pre-revision, was
    # overwritten by run 1 before this guard existed; its key lines are quoted in data/herbals_period/README.md)
    fh = open(OUT / f"fixture_run{k}.txt", "x", encoding="utf-8", newline="\n")
    log(fh, f"s103 fixture (synthetic plants), {now()}")
    rng = np.random.default_rng(SEED)
    emb = Embedder()
    nS, nOnly = 30, 30
    species = [synth_species(rng) for _ in range(nS + 2 * nOnly + 40)]
    segs, keys, src = [], [], []
    for i in range(nS):  # shared species, drawn in both herbals
        for st, m in ((0, "ljs419"), (1, "sloane4016")):
            segs.append(segment(synth_plant(rng, species[i], st))); keys.append(f"sp{i}"); src.append(m)
    for i in range(nS, nS + nOnly):
        segs.append(segment(synth_plant(rng, species[i], 0))); keys.append(f"sp{i}"); src.append("ljs419")
    for i in range(nS + nOnly, nS + 2 * nOnly):
        segs.append(segment(synth_plant(rng, species[i], 1))); keys.append(f"sp{i}"); src.append("sloane4016")
    base = len(segs)
    scen = {}
    # scenario M: Voynich = members drawn in style 2;  I: invented species;  D: part chimeras with a fixed mapping
    v_members = [segment(synth_plant(rng, species[int(rng.integers(0, nS))], 2)) for _ in range(40)]
    v_invented = [segment(synth_plant(rng, species[nS + 2 * nOnly + k], 2)) for k in range(40)]
    v_disg = []
    pairs = [(int(rng.integers(0, nS)), int(rng.integers(0, nS)), int(rng.integers(0, nS))) for _ in range(5)]
    for k in range(40):
        a, b, c = pairs[k % 5]
        sp = dict(species[b])
        for f in ("flower", "fsize"):
            sp[f] = species[a][f]
        for f in ("root", "rsize", "nroot"):
            sp[f] = species[c][f]
        v_disg.append(segment(synth_plant(rng, sp, 2)))
    for name, vs in (("M members", v_members), ("I invented", v_invented), ("D part-chimera", v_disg)):
        allsegs = segs + vs
        F = featurize(allsegs, emb)
        s2 = src + ["voynich"] * len(vs)
        k2 = keys + [None] * len(vs)
        R = build_reps(F, s2)
        g, Sset = gate_stat(R, k2, s2, np.random.default_rng(SEED), fh, f"fixture {name} gate")
        res = compare(R, k2, s2, Sset, list(range(base, base + len(vs))), np.random.default_rng(SEED + 1), fh,
                      f"fixture {name}")
        scen[name] = (g, res)
    ok_gate = all(scen[n][0][r][1] < 0.05 for n in scen for r in ("A", "B"))
    ok_M = scen["M members"][1]["match"]
    ok_I = not scen["I invented"][1]["match"]
    log(fh, f"FIXTURE gate recovered (both reps, all scenarios) = {ok_gate}")
    log(fh, f"FIXTURE members detected (MATCH) = {ok_M}")
    log(fh, f"FIXTURE invented not matched = {ok_I}")
    log(fh, f"FIXTURE disguise: SIGNAL_A={scen['D part-chimera'][1]['sig']['A']} "
            f"SIGNAL_B={scen['D part-chimera'][1]['sig']['B']} p_mixed={scen['D part-chimera'][1]['p_mixed']:.4f} "
            f"p_repeat={scen['D part-chimera'][1]['p_repeat']:.4f} (descriptive)")
    fh.close()


# ------------------------------------------------------------------------------------------------------- real data
def load_tradition():
    items = []
    for ms, d in MSS.items():
        caps = json.loads((HP / ms / "captions_s103.json").read_text(encoding="utf-8"))
        for page in caps:
            for j, pl in enumerate(page.get("plants", [])):
                bb = pl.get("bbox")
                if not bb or len(bb) != 4:
                    continue
                items.append({"ms": ms, "file": page["file"], "j": j, "bbox": bb, "caption": pl.get("caption", ""),
                              "key": species_key(pl), "rec": pl})
    return items


def load_voynich():
    meta = json.loads((ROOT / "runs" / "s48" / "crops.json").read_text(encoding="utf-8"))
    return [r for r in meta["crops"] if r["kind"] == "herbal"]


def make_manifest():
    OUT.mkdir(parents=True, exist_ok=True)
    lines = []
    for r in load_voynich():
        p = ROOT / "runs" / "s48" / "crops" / f"{r['crop']}.png"
        lines.append(f"{sha(p)}  {p.relative_to(ROOT).as_posix()}")
    lines.append(f"{sha(ROOT / 'runs' / 's48' / 'crops.json')}  runs/s48/crops.json")
    files = set()
    for it in load_tradition():
        files.add(MSS[it["ms"]] / it["file"])
    for p in sorted(files):
        lines.append(f"{sha(p)}  {p.relative_to(ROOT).as_posix()}")
    for ms in MSS:
        p = HP / ms / "captions_s103.json"
        lines.append(f"{sha(p)}  {p.relative_to(ROOT).as_posix()}")
    out = OUT / "image_manifest.txt"
    if out.exists():
        sys.exit(f"{out} exists; not overwritten")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"manifest: {len(lines)} files -> {out}")


def stub_ok():
    """Python equivalent of `grep -v "^#" STUB | tr -d '\\r' | sha256sum -c -`."""
    if not STUB.exists():
        return False, "stub missing"
    ok, msgs = True, []
    for ln in STUB.read_text(encoding="utf-8").replace("\r", "").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        f = f.lstrip("*")
        good = (ROOT / f).exists() and sha(ROOT / f) == h
        ok &= good
        msgs.append(f"{f}: {'OK' if good else 'FAILED'}")
    return ok, "\n".join(msgs)


def run_real():
    from PIL import Image
    if RESULTS.exists():
        sys.exit("results_s103.txt exists; never overwritten (use an amendment file)")
    ok, msg = stub_ok()
    fh = open(RESULTS, "x", encoding="utf-8", newline="\n")
    log(fh, f"s103_herbal_tradition_matching.py sha256={sha(Path(__file__))}")
    log(fh, f"stub_match={ok}")
    log(fh, msg)
    log(fh, f"run start: {now()}")
    t0 = time.time()
    trad = load_tradition()
    voy = load_voynich()
    segs, keys, src, meta = [], [], [], []
    nfail = 0
    for it in trad:
        im = Image.open(MSS[it["ms"]] / it["file"])
        W, H = im.size
        x0, y0, x1, y1 = it["bbox"]
        dx, dy = 0.02, 0.02
        box = (max(0, int((x0 - dx) * W)), max(0, int((y0 - dy) * H)), min(W, int((x1 + dx) * W)), min(H, int((y1 + dy) * H)))
        if box[2] - box[0] < 16 or box[3] - box[1] < 16:
            nfail += 1
            continue
        s = segment(to_work(im.crop(box)))
        if s is None:
            nfail += 1
            continue
        segs.append(s); keys.append(it["key"]); src.append(it["ms"]); meta.append(it)
    vstart = len(segs)
    for r in voy:
        s = segment(to_work(Image.open(ROOT / "runs" / "s48" / "crops" / f"{r['crop']}.png")))
        if s is None:
            nfail += 1
            continue
        segs.append(s); keys.append(None); src.append("voynich"); meta.append({"ms": "voynich", "page": r["page"]})
    vi = list(range(vstart, len(segs)))
    log(fh, f"items: tradition {vstart} plant drawings (ljs419 {src.count('ljs419')}, sloane4016 "
            f"{src.count('sloane4016')}); Voynich {len(vi)} pages; segmentation failures {nfail}")
    missing = np.zeros(3, int)
    for s in segs:
        for j, p in enumerate(PARTS):
            missing[j] += s["parts"][p] is None
    log(fh, f"parts missing (flower, stem/leaf, root): {missing.tolist()}")
    emb = Embedder()
    F = featurize(segs, emb)
    R = build_reps(F, src)
    np.savez(OUT / "features.npz", **{k: v for k, v in F.items()}, src=np.array(src),
             keys=np.array([k or "" for k in keys]))
    log(fh, f"embedded on {emb.dev}, {time.time() - t0:.0f}s")
    log(fh, "")
    log(fh, "=" * 100)
    log(fh, "GATE 1 (recovery across the comparison herbals)")
    log(fh, "=" * 100)
    g, Sset = gate_stat(R, keys, src, np.random.default_rng(SEED), fh, "gate1")
    gate = {r: bool(g[r][1] < 0.05) for r in ("A", "B")}
    for r in ("A", "B"):
        log(fh, f"GATE_{r} = {gate[r]}")
    gate1 = gate["A"] or gate["B"]
    log(fh, f"GATE1_PASS = {gate1}")
    side = {"gate": {r: list(map(float, g[r])) for r in g}, "S": Sset}
    if not gate1:
        log(fh, "VERDICT: HOLD: recovery gate failed (Voynich comparison not run)")
        (OUT / "summary.json").write_text(json.dumps(side, indent=1), encoding="utf-8")
        log(fh, f"run end: {now()}")
        fh.close()
        return
    log(fh, "")
    log(fh, "=" * 100)
    log(fh, "VOYNICH COMPARISON")
    log(fh, "=" * 100)
    res = compare(R, keys, src, Sset, vi, np.random.default_rng(SEED + 1), fh, "voynich")
    for r in ("A", "B"):
        log(fh, f"ADEQUATE_{r} (gate_{r} and power_{r}) = {gate[r] and res['adequate'][r]}")
    cribs = []
    QV = res["QV"]
    for a, i in enumerate(vi):
        tA, tB = QV["top"][a]["A"], QV["top"][a]["B"]
        if QV["A"]["hit1"][a] and QV["B"]["hit1"][a]:
            cribs.append((meta[i]["page"], tA[0], tB[0]))
    if res["match"]:
        log(fh, "")
        log(fh, "CANDIDATE CRIBS (for a separately frozen later test; NOT readings):")
        capt = {}
        for m_, k_ in zip(meta, keys):
            if k_:
                capt.setdefault((m_["ms"], k_), []).append(m_["caption"])
        for page, kA, kB in cribs:
            log(fh, f"   {page}: rep A key '{kA}', rep B key '{kB}'; captions LJS {capt.get(('ljs419', kA), [])[:2]} "
                    f"Sloane {capt.get(('sloane4016', kA), [])[:2]}")
        if not cribs:
            log(fh, "   (no page with hit1 in both reps)")
    pages = []
    for a, i in enumerate(vi):
        pages.append({"page": meta[i]["page"], "A": {k: float(QV["A"][k][a]) for k in ("hit1", "hit5")},
                      "B": {k: float(QV["B"][k][a]) for k in ("hit1", "hit5")}, "top": QV["top"][a],
                      "parts": QV["parts"][a]})
    (OUT / "voynich_pages.json").write_text(json.dumps(pages, indent=1), encoding="utf-8")
    side.update({"match": res["match"], "sig": res["sig"], "adequate": {r: bool(res["adequate"][r]) for r in "AB"},
                 "mode": res["mode"], "p_mixed": res["p_mixed"], "p_repeat": res["p_repeat"], "cribs": cribs})
    (OUT / "summary.json").write_text(json.dumps(side, indent=1, default=str), encoding="utf-8")
    adequate_both = all(gate[r] and res["adequate"][r] for r in "AB")
    if res["match"]:
        v = f"MATCH: {res['mode']}"
    elif adequate_both:
        v = "NO MATCH at adequate power: copying drift excluded at this resolution"
    else:
        under = [r for r in "AB" if not (gate[r] and res["adequate"][r])]
        v = f"NO MATCH, underpowered ({', '.join(under)})"
    log(fh, "")
    log(fh, f"VERDICT: {v}")
    log(fh, f"run end: {now()}  ({time.time() - t0:.0f}s)")
    fh.close()


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture", action="store_true")
    g.add_argument("--manifest", action="store_true")
    g.add_argument("--real", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.fixture:
        run_fixture()
    elif a.manifest:
        make_manifest()
    else:
        run_real()


if __name__ == "__main__":
    main()
