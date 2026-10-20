#!/usr/bin/env python
"""s124 (P-69 / H-20, H-06): are the pharma plant-part drawings grouped by page (and by jar)?

PRE-REGISTERED: this file, tools/plant_regions.py (imported unchanged) and every input image/model are hashed in
s124_page_grouping.prereg.sha256 before any real Voynich or control image is read by this script.

Run (scratchpad venv with torch + transformers + cv2 + sklearn, from the project root, `python -I`):
    python -I tools/s124_page_grouping.py --stage fixture          # synthetic gate only (runs/s124/fixture/)
    python -I tools/s124_page_grouping.py --stage crops            # gate, then real crops (no scoring) + handcheck sheet
    python -I tools/s124_page_grouping.py --stage score            # gate, then score Voynich + controls -> results file
    python -I tools/s124_page_grouping.py --stage stubfiles        # print the input file list for the stub (no reading)

DESIGN (fixed before hashing)
(1) Objects.  Voynich: the 17 P panels of tools/plant_regions.PANELS (16 ZL pages; f101v appears on two canvases
    and its two panels are kept as separate units, so a doubly imaged drawing can never count as a within-unit pair).
    Each panel is loaded with plant_regions.load_panel (black scan border trimmed).  Objects = plant_regions
    .paint_components (work scale WORK_H = 1000 px; CIELAB chroma > DAB = 10 from the median parchment, opened 5 px,
    dilated 15 px, 8-connected), kept with the s48 size rules (bbox area >= MIN_AREA = 0.2 % of the panel, min side
    >= MIN_SIDE = 3.5 % of the panel height, <= MAX_FRAC = 85 % of either side) plus one s124 rule: a component whose
    bbox lies within 1.5 % of a panel border AND whose long/short side ratio > 4 is a page edge/gutter strip, dropped.
    jar_like = the s48 rule (h/w >= 1.6 and h >= 0.12 H, or h/w >= 1.2 and x-centre in the left 20 %).  Jars are
    containers, not plant parts: they are removed from the shape set and used only to define jar groups.
    Writing is masked by construction: the silhouette of an object is the undilated chroma (paint) mask inside that
    component's own label region, holes filled; brown/black ink writing has no chroma and does not enter it.  Known
    limit (stated before scoring): unpainted ink-only drawings (some roots) are not detected.
    Silhouettes with < 150 work-scale pixels are dropped.
(2) Shape embedding (primary): silhouette black on white, padded square, 224 px, DINOv2 ViT-B/14 CLS
    (data/external/models/dinov2-base), 8 views (4 rotations x hflip; orientation-free), each L2-normalised, averaged,
    re-normalised; GPU.  Secondary A: classical silhouette descriptor (7 signed-log Hu moments, solidity, extent,
    log aspect of the min-area rectangle), z-scored within the set.  Secondary B: DINOv2 on the colour crop (the
    panel pixels inside the component bbox, padded with parchment).  Calls come from the primary only.
(3) Statistic.  Units u (Voynich: panel; controls: page image), strata q (Voynich: quire, O or S; all P pages are
    Davis hand 1, so quire x hand = quire; controls: consecutive blocks of 8 selected pages).  S = cosine similarity.
    Size control: S is residualised by OLS over all same-stratum pairs i<j on |dlog area|, log area_i + log area_j,
    |dlog aspect| (area = silhouette pixels / panel pixels; aspect = bbox h/w); R = residual.
    T = mean R over same-unit pairs - mean R over different-unit same-stratum pairs.
    Null: unit labels permuted across objects within stratum (unit sizes kept), N_PERM = 2000, seed SEED.
    p = (1 + #{T_null >= T}) / (1 + N_PERM).  Effect for cross-manuscript comparison: AUC = P(R_within > R_between).
    Scan control (Voynich, reported, no call): canvases holding >= 2 P panels (161, 177, 179): T_canvas = mean R
    within panel - mean R between panels of the same canvas; null permutes labels within canvas.
    Clustering: agglomerative, cosine, average linkage on the primary embedding, k = number of units in the set
    (rule fixed now); ARI(clusters, units); null = the same within-stratum permutations of the unit labels.
    Jar groups (Voynich, secondary, no call): each plant part is assigned to the jar of its panel with the nearest
    vertical centre; only panels with >= 2 jars.  T_jar = mean R same jar group - mean R same panel other jar group;
    null permutes labels within panel.  T_jar_vs_rest: labels = jar group where defined, else panel; T = mean R
    same label - mean R different label same quire; null permutes these labels within quire.
(4) CALL (primary).  NOT_MEASURABLE if < 8 units with >= 4 objects or < 80 objects.  Else GROUPED_BY_PAGE if
    p <= 0.01, else NOT_GROUPED.  Comparison: Voynich AUC against the [min, max] AUC of the real control sets
    (ABOVE / WITHIN / BELOW RANGE).  Shuffled Voynich: 10 within-quire label shuffles (seeds SEED+1..SEED+10) run
    through the same statistic; their calls and AUCs are printed.
(5) Real controls (no object-row pharma manuscript exists on disk; these are illustrated herbals, one plant or a few
    per page, so page grouping there holds by construction: a ceiling-type reference, not a pharma analogue):
    sloane4016, ljs419/iiif, bsb_clm5905, bl_add41623, anchor_A0 Canon. Misc. 408.  Per manuscript: jpgs sorted by
    name, the first 4 and last 4 skipped; a page is eligible if it yields >= 4 objects; eligible pages taken in order
    are dealt round-robin into 3 disjoint sets and each set truncated to its first 16 pages (pseudo-strata of 8).
    Sets with < 8 eligible pages are skipped.
(6) Fixture gate (synthetic, before any real image): 17 pages (strata 6 + 11), 15-30 painted shapes per page from 10
    shape families with random size, rotation, aspect, colour; per-page parchment tint and fake ink text lines.
    STRONG: each page draws all its objects from 2 families of its own.  ABSENT: every object from any family.
    WEAK (reported, not gated): 40 % of objects from the page's 2 families.  10 seeds each.  Gate: STRONG called
    GROUPED_BY_PAGE >= 8/10 and ABSENT called NOT_GROUPED >= 8/10.  If the gate fails, real stages refuse to run.
(7) Descriptive table (no call): per Voynich panel, the count of its objects in each cluster.
"""
from __future__ import annotations

import argparse
import ctypes
import glob
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import plant_regions as PR  # noqa: E402  (imported unchanged)

OUT = ROOT / "runs" / "s124"
MODELS = ROOT / "data" / "external" / "models"
SEED = 20261019
N_PERM = 2000
P = dict(PR.PARAMS)
EDGE_STRIP = 0.015
STRIP_RATIO = 4.0
MIN_SIL = 150
EMB = 224
QUIRE = {"f88r": "O", "f88v": "O", "f89r1": "O", "f89r2": "O", "f89v2": "O", "f89v1": "O",
         "f99r": "S", "f99v": "S", "f100r": "S", "f100v": "S", "f101r": "S", "f101v": "S",
         "f102r1": "S", "f102r2": "S", "f102v2": "S", "f102v1": "S"}  # VKB folios (quire; hand_davis = 1 for all)
CONTROLS = {"sloane4016": "data/herbals_period/sloane4016/*.jpg",
            "ljs419": "data/herbals_period/ljs419/iiif/*.jpg",
            "bsb_clm5905": "data/herbals_alchemical/bsb_clm5905/*.jpg",
            "bl_add41623": "data/herbals_alchemical/bl_add41623/*.jpg",
            "canon_misc_408": "data/anchor_A0/bodleian_canon_misc_408/images/*.jpg"}


def low_priority():
    try:
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x4000)  # BELOW_NORMAL
    except Exception:
        pass
    try:
        import cv2
        cv2.setNumThreads(1)
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------- objects
def detect_objects(arr, with_jars=True):
    """arr: RGB panel (trimmed).  Returns list of dict(sil, color, bbox_frac, area_frac, aspect, jar_like, parch)."""
    import cv2
    from scipy.ndimage import binary_fill_holes
    _, _, parch, _, _ = PR.masks(arr, P)
    sc = P["WORK_H"] / arr.shape[0]
    ws = (max(1, int(arr.shape[1] * sc)), P["WORK_H"])
    small = cv2.resize(arr, ws, interpolation=cv2.INTER_AREA)
    pa, _ = PR.chroma_mask(small, P)
    pa_o = cv2.morphologyEx(pa.astype(np.uint8), cv2.MORPH_OPEN,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (P["OPEN"], P["OPEN"])))
    m = cv2.dilate(pa_o, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (P["DIL"], P["DIL"])))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    Hs, Ws = m.shape
    out = []
    for i in range(1, n):
        x, y, w, h, a = (int(t) for t in st[i])
        if w * h < P["MIN_AREA"] * Hs * Ws or min(w, h) < P["MIN_SIDE"] * Hs:
            continue
        if w > P["MAX_FRAC"] * Ws or h > P["MAX_FRAC"] * Hs:
            continue
        near = (x <= EDGE_STRIP * Ws or y <= EDGE_STRIP * Hs or x + w >= (1 - EDGE_STRIP) * Ws
                or y + h >= (1 - EDGE_STRIP) * Hs)
        if near and max(w, h) / max(1, min(w, h)) > STRIP_RATIO:
            continue
        asp = h / max(w, 1)
        jar = bool(with_jars and (((asp >= P["JAR_ASPECT"]) and (h >= P["JAR_H"] * Hs)) or
                                  ((asp >= P["JAR_ASPECT_EDGE"]) and (x + w / 2 < P["JAR_EDGE"] * Ws))))
        reg = lab[y:y + h, x:x + w] == i
        sil = binary_fill_holes((pa_o[y:y + h, x:x + w] > 0) & reg)
        npx = int(sil.sum())
        if npx < MIN_SIL and not jar:
            continue
        col = small[y:y + h, x:x + w]
        out.append(dict(sil=sil, color=col, bbox_frac=[x / Ws, y / Hs, w / Ws, h / Hs],
                        area_frac=npx / (Hs * Ws), aspect=asp, jar_like=jar, parch=[int(t) for t in parch]))
    return out


def sil_image(sil):
    h, w = sil.shape
    s = max(h, w) + 8
    c = np.full((s, s), 255, np.uint8)
    y0, x0 = (s - h) // 2, (s - w) // 2
    c[y0:y0 + h, x0:x0 + w][sil] = 0
    return Image.fromarray(c).convert("RGB").resize((EMB, EMB), Image.BILINEAR)


def color_image(col, parch):
    return PR.square(Image.fromarray(col), parch, EMB)


def classical(sil):
    import cv2
    s8 = sil.astype(np.uint8)
    hu = cv2.HuMoments(cv2.moments(s8, True)).ravel()
    hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-30)
    cnts, _ = cv2.findContours(s8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    allp = np.vstack(cnts) if cnts else np.zeros((1, 1, 2), np.int32)
    hull = cv2.convexHull(allp)
    ha = max(cv2.contourArea(hull), 1.0)
    solidity = sil.sum() / ha
    extent = sil.sum() / sil.size
    (_, _), (rw, rh), _ = cv2.minAreaRect(allp)
    lasp = np.log((max(rw, rh) + 1) / (min(rw, rh) + 1))
    return np.concatenate([hu, [solidity, extent, lasp]]).astype(np.float64)


class Embedder:
    def __init__(self):
        import torch
        from transformers import AutoModel
        self.torch = torch
        self.dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.m = AutoModel.from_pretrained(str(MODELS / "dinov2-base"), use_safetensors=True).to(self.dev).eval()
        self.mean = torch.tensor((0.485, 0.456, 0.406), device=self.dev).view(1, 3, 1, 1)
        self.std = torch.tensor((0.229, 0.224, 0.225), device=self.dev).view(1, 3, 1, 1)

    def __call__(self, imgs, bs=16):
        torch = self.torch
        out = []
        with torch.no_grad():
            for k in range(0, len(imgs), bs):
                vs = [np.asarray(v, dtype=np.float32) / 255.0 for im in imgs[k:k + bs] for v in PR.views(im)]
                x = torch.from_numpy(np.stack(vs)).permute(0, 3, 1, 2).to(self.dev)
                x = (x - self.mean) / self.std
                with torch.autocast("cuda", dtype=torch.float16, enabled=self.dev.startswith("cuda")):
                    f = self.m(pixel_values=x).last_hidden_state[:, 0]
                f = torch.nn.functional.normalize(f.float(), dim=-1).view(-1, 8, f.shape[-1]).mean(1)
                out.append(torch.nn.functional.normalize(f, dim=-1).cpu().numpy())
        return np.concatenate(out) if out else np.zeros((0, 768))


# ----------------------------------------------------------------------------------------------- statistics
def cos(E):
    E = E / np.linalg.norm(E, axis=1, keepdims=True).clip(1e-12)
    return E @ E.T


def residualise(S, area, aspect, strata):
    n = len(area)
    iu, ju = np.triu_indices(n, 1)
    keep = strata[iu] == strata[ju]
    iu, ju = iu[keep], ju[keep]
    la, lasp = np.log(area), np.log(aspect)
    X = np.column_stack([np.ones(len(iu)), np.abs(la[iu] - la[ju]), la[iu] + la[ju], np.abs(lasp[iu] - lasp[ju])])
    y = S[iu, ju]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    R = np.zeros_like(S)
    r = y - X @ beta
    R[iu, ju] = r
    R[ju, iu] = r
    return R, beta


def onehot(lab):
    u, inv = np.unique(lab, return_inverse=True)
    G = np.zeros((len(lab), len(u)))
    G[np.arange(len(lab)), inv] = 1
    return G


def within_between(R, lab, strata, sameS_sum, sameS_n):
    G = onehot(lab)
    cnt = G.sum(0)
    w_sum = float(np.trace(G.T @ R @ G)) - float(np.trace(R))  # ordered pairs, diag of R is 0 anyway
    w_n = float((cnt * (cnt - 1)).sum())
    b_sum, b_n = sameS_sum - w_sum, sameS_n - w_n
    return w_sum / max(w_n, 1), b_sum / max(b_n, 1)


def perm_within(lab, strata, rng):
    lab = lab.copy()
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        lab[idx] = lab[rng.permutation(idx)]
    return lab


def stat_test(R, lab, strata, rng, n_perm=N_PERM):
    sameS = (strata[:, None] == strata[None, :]) & ~np.eye(len(lab), dtype=bool)
    sS, nS = float(R[sameS].sum()), float(sameS.sum())
    w, b = within_between(R, lab, strata, sS, nS)
    T = w - b
    null = np.empty(n_perm)
    for k in range(n_perm):
        w2, b2 = within_between(R, perm_within(lab, strata, rng), strata, sS, nS)
        null[k] = w2 - b2
    p = (1 + (null >= T).sum()) / (1 + n_perm)
    same = (lab[:, None] == lab[None, :]) & sameS
    diff = sameS & ~same
    iu = np.triu(np.ones_like(R, dtype=bool), 1)
    rw, rb = R[same & iu], R[diff & iu]
    auc = auc_mw(rw, rb)
    return dict(T=T, p=p, null_mean=float(null.mean()), null_sd=float(null.std()), auc=auc,
                n_within=int(len(rw)), n_between=int(len(rb)))


def auc_mw(a, b):
    from scipy.stats import rankdata
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    r = rankdata(np.concatenate([a, b]))
    return float((r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b)))


def cluster_ari(E, lab, strata, rng, n_perm=N_PERM):
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import adjusted_rand_score
    k = len(np.unique(lab))
    cl = AgglomerativeClustering(n_clusters=k, metric="cosine", linkage="average").fit_predict(E)
    ari = adjusted_rand_score(lab, cl)
    null = np.array([adjusted_rand_score(perm_within(lab, strata, rng), cl) for _ in range(n_perm)])
    return dict(k=k, ari=float(ari), p=float((1 + (null >= ari).sum()) / (1 + n_perm)),
                null_mean=float(null.mean()), null_sd=float(null.std())), cl


def call_of(n_units_ok, n_obj, p):
    if n_units_ok < 8 or n_obj < 80:
        return "NOT_MEASURABLE"
    return "GROUPED_BY_PAGE" if p <= 0.01 else "NOT_GROUPED"


def analyse(objs, units, strata, emb, rng, extra=False):
    """objs: list of object dicts (non-jar); units/strata arrays. Returns primary result dict."""
    units, strata = np.asarray(units), np.asarray(strata)
    area = np.array([o["area_frac"] for o in objs])
    aspect = np.array([o["aspect"] for o in objs])
    sil_imgs = [sil_image(o["sil"]) for o in objs]
    E = emb(sil_imgs)
    R, beta = residualise(cos(E), area, aspect, strata)
    res = stat_test(R, units, strata, rng)
    uu, cc = np.unique(units, return_counts=True)
    res["n_obj"] = len(objs)
    res["n_units"] = len(uu)
    res["n_units_ok"] = int((cc >= 4).sum())
    res["call"] = call_of(res["n_units_ok"], res["n_obj"], res["p"])
    res["beta"] = [float(b) for b in beta]
    out = dict(primary=res, E=E, R=R)
    if extra:
        C = np.stack([classical(o["sil"]) for o in objs])
        C = (C - C.mean(0)) / C.std(0).clip(1e-9)
        Rc, _ = residualise(cos(C), area, aspect, strata)
        out["classical"] = stat_test(Rc, units, strata, rng)
        Ec = emb([color_image(o["color"], o["parch"]) for o in objs])
        Rb, _ = residualise(cos(Ec), area, aspect, strata)
        out["colour"] = stat_test(Rb, units, strata, rng)
        out["ari"], out["clusters"] = cluster_ari(E, units, strata, rng)
    return out


# ----------------------------------------------------------------------------------------------- fixture
def shape_mask(fam, size, rng):
    import cv2
    S = int(size * 1.6) + 10
    c = np.zeros((S, S), np.uint8)
    cx = cy = S // 2
    r = size / 2
    t = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    if fam == 0:  # ellipse
        pts = np.c_[r * np.cos(t), 0.5 * r * np.sin(t)]
    elif fam == 1:  # 5-star
        rr = r * (0.55 + 0.45 * (np.cos(5 * t) > 0))
        pts = np.c_[rr * np.cos(t), rr * np.sin(t)]
    elif fam == 2:  # 9-lobed rosette
        rr = r * (0.7 + 0.3 * np.cos(9 * t))
        pts = np.c_[rr * np.cos(t), rr * np.sin(t)]
    elif fam == 3:  # leaf (pointed)
        pts = np.c_[r * np.cos(t), 0.35 * r * np.sin(t) * np.abs(np.sin(t)) ** 0.2 * (1 + 0.3 * np.cos(t))]
    elif fam == 4:  # rectangle
        pts = np.array([[-r, -0.4 * r], [r, -0.4 * r], [r, 0.4 * r], [-r, 0.4 * r]])
    elif fam == 5:  # triangle
        pts = np.array([[0, -r], [0.9 * r, 0.7 * r], [-0.9 * r, 0.7 * r]])
    elif fam == 6:  # cross
        a, b = r, 0.25 * r
        pts = np.array([[-b, -a], [b, -a], [b, -b], [a, -b], [a, b], [b, b], [b, a], [-b, a], [-b, b], [-a, b],
                        [-a, -b], [-b, -b]])
    elif fam == 7:  # crescent
        pts = np.c_[r * np.cos(t), r * np.sin(t)]
    elif fam == 8:  # heart
        pts = np.c_[r * 0.06 * 16 * np.sin(t) ** 3,
                    -r * 0.06 * (13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))]
    else:  # forked root
        pts = None
    if pts is not None:
        pts = pts + [cx, cy]
        cv2.fillPoly(c, [pts.astype(np.int32)], 1)
        if fam == 7:
            cv2.circle(c, (int(cx + 0.45 * r), cy), int(0.85 * r), 0, -1)
    else:
        th = max(3, int(0.12 * r))
        cv2.line(c, (cx, int(cy - r)), (cx, int(cy + 0.1 * r)), 1, th)
        for dx in (-0.8, -0.3, 0.3, 0.8):
            cv2.line(c, (cx, int(cy + 0.1 * r)), (int(cx + dx * r), int(cy + r)), 1, max(2, th - 1))
    ang = rng.uniform(0, 360)
    M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
    M[:, :2] *= [[rng.uniform(0.85, 1.15)], [rng.uniform(0.85, 1.15)]]
    c = cv2.warpAffine(c, M, (S, S), flags=cv2.INTER_NEAREST)
    ys, xs = np.where(c)
    return c[ys.min():ys.max() + 1, xs.min():xs.max() + 1] if len(ys) else c


COLOURS = [(70, 140, 90), (170, 60, 50), (190, 140, 60), (60, 90, 150), (120, 150, 70)]


def synth_page(mode, fams_page, rng, H=1000, W=700):
    import cv2
    tint = rng.integers(-12, 13, 3)
    base = np.clip(np.array([205, 185, 160]) + tint, 0, 255)
    arr = (base + rng.normal(0, 3, (H, W, 3))).clip(0, 255).astype(np.uint8)
    n = int(rng.integers(15, 31))
    rows = int(np.ceil(n / 5))
    k = 0
    for ri in range(rows):
        y0 = 40 + ri * (H - 80) // rows
        for ci in range(5):
            if k >= n:
                break
            if mode == "strong" or (mode == "weak" and rng.random() < 0.4):
                fam = int(rng.choice(fams_page))
            else:
                fam = int(rng.integers(0, 10))
            size = rng.uniform(45, 95)
            m = shape_mask(fam, size, rng)
            h, w = m.shape
            x = 30 + ci * (W - 60) // 5 + int(rng.integers(0, 10))
            y = y0 + int(rng.integers(0, 10))
            h, w = min(h, H - y - 1), min(w, W - x - 1)
            col = np.array(COLOURS[int(rng.integers(0, len(COLOURS)))]) + rng.integers(-15, 16, 3)
            sub = arr[y:y + h, x:x + w]
            sub[m[:h, :w] > 0] = col.clip(0, 255)
            k += 1
        # fake ink text line under each row (unpainted, dark brown)
        ty = y0 + (H - 80) // rows - 12
        for xx in range(30, W - 30, 9):
            if rng.random() < 0.8:
                cv2.line(arr, (xx, ty), (xx + 4, ty - 7), (60, 45, 35), 1)
    return arr


def run_fixture(emb, log):
    strata = ["O"] * 6 + ["S"] * 11
    rows = []
    summary = {}
    for mode in ("strong", "absent", "weak"):
        calls = []
        for s in range(10):
            rng = np.random.default_rng(SEED + 1000 * (1 + ["strong", "absent", "weak"].index(mode)) + s)
            objs, units, st = [], [], []
            for u in range(17):
                fams = rng.choice(10, 2, replace=False)
                arr = synth_page(mode, fams, rng)
                for o in detect_objects(arr, with_jars=False):
                    objs.append(o); units.append(f"u{u}"); st.append(strata[u])
            r = analyse(objs, units, st, emb, np.random.default_rng(SEED + s))["primary"]
            calls.append(r["call"])
            rows.append(f"FIXTURE {mode:6s} seed {s}: n_obj {r['n_obj']} T {r['T']:+.4f} p {r['p']:.4f} "
                        f"AUC {r['auc']:.3f} -> {r['call']}")
            log(rows[-1])
        summary[mode] = calls
    ok_strong = sum(c == "GROUPED_BY_PAGE" for c in summary["strong"])
    ok_absent = sum(c == "NOT_GROUPED" for c in summary["absent"])
    weak_g = sum(c == "GROUPED_BY_PAGE" for c in summary["weak"])
    gate = ok_strong >= 8 and ok_absent >= 8
    lines = rows + [f"FIXTURE strong GROUPED {ok_strong}/10 (need >= 8); absent NOT_GROUPED {ok_absent}/10 "
                    f"(need >= 8); weak GROUPED {weak_g}/10 (reported)",
                    f"FIXTURE_GATE {'PASS' if gate else 'FAIL'}"]
    log(lines[-2]); log(lines[-1])
    (OUT / "fixture").mkdir(parents=True, exist_ok=True)
    (OUT / "fixture" / "fixture_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return gate, lines


# ----------------------------------------------------------------------------------------------- real data
def voynich_objects():
    objs, jars = [], []
    panel_no = {}
    for fname, panels in PR.PANELS.items():
        for pid, a, b, s in panels:
            if s != "P":
                continue
            panel_no[pid] = panel_no.get(pid, 0) + 1
            unit = f"{pid}_p{panel_no[pid]}"
            arr, off, _ = PR.load_panel(fname, a, b)
            for i, o in enumerate(detect_objects(arr)):
                o.update(unit=unit, page=pid, canvas=fname, quire=QUIRE[pid], idx=i)
                (jars if o["jar_like"] else objs).append(o)
    return objs, jars


def assign_jars(objs, jars):
    for o in objs:
        js = [j for j in jars if j["unit"] == o["unit"]]
        if len(js) < 2:
            o["jar_group"] = None
            continue
        yc = o["bbox_frac"][1] + o["bbox_frac"][3] / 2
        d = [abs(yc - (j["bbox_frac"][1] + j["bbox_frac"][3] / 2)) for j in js]
        o["jar_group"] = f"{o['unit']}_jar{js[int(np.argmin(d))]['idx']:02d}"


def control_sets(name, pattern):
    files = sorted(glob.glob(str(ROOT / pattern)))[4:-4]
    elig = []
    for f in files:
        arr = np.asarray(Image.open(f).convert("RGB"))
        x0, y0, x1, y1 = PR.page_trim(arr)
        arr = arr[y0:y1, x0:x1]
        if arr.shape[0] < 200 or arr.shape[1] < 150:
            continue
        ob = detect_objects(arr, with_jars=False)
        if len(ob) >= 4:
            elig.append((Path(f).name, ob))
    sets = [elig[k::3][:16] for k in range(3)]
    return [s for s in sets if len(s) >= 8], len(files), len(elig)


def save_handcheck(objs, jars):
    hc = OUT / "handcheck"
    hc.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    pick = sorted(rng.choice(len(objs), 10, replace=False).tolist())
    lines = []
    for k, i in enumerate(pick):
        o = objs[i]
        a = Image.fromarray(o["color"]).resize((256, int(256 * o["color"].shape[0] / o["color"].shape[1])) if
                                                o["color"].shape[1] >= o["color"].shape[0] else
                                                (int(256 * o["color"].shape[1] / o["color"].shape[0]), 256))
        b = Image.fromarray(np.where(o["sil"], 0, 255).astype(np.uint8)).convert("RGB").resize(a.size)
        c = Image.new("RGB", (a.size[0] * 2 + 8, a.size[1]), "white")
        c.paste(a, (0, 0)); c.paste(b, (a.size[0] + 8, 0))
        c.save(hc / f"hc{k:02d}_{o['unit']}_{o['idx']:02d}.png")
        lines.append(f"hc{k:02d} {o['unit']} obj {o['idx']:02d} bbox_frac {[round(t, 3) for t in o['bbox_frac']]} "
                     f"area_frac {o['area_frac']:.4f}")
    # overviews with object boxes (blue = jar)
    ov = OUT / "overview"
    ov.mkdir(parents=True, exist_ok=True)
    panel_no = {}
    for fname, panels in PR.PANELS.items():
        for pid, a_, b_, s in panels:
            if s != "P":
                continue
            panel_no[pid] = panel_no.get(pid, 0) + 1
            unit = f"{pid}_p{panel_no[pid]}"
            arr, _, _ = PR.load_panel(fname, a_, b_)
            im = Image.fromarray(arr)
            im = im.resize((int(im.size[0] * 1000 / im.size[1]), 1000))
            d = ImageDraw.Draw(im)
            W, H = im.size
            for o in [x for x in objs + jars if x["unit"] == unit]:
                x, y, w, h = o["bbox_frac"]
                col = "blue" if o["jar_like"] else "red"
                d.rectangle([x * W, y * H, (x + w) * W, (y + h) * H], outline=col, width=3)
                d.text((x * W + 3, y * H + 3), f"{o['idx']:02d}", fill=col)
            im.save(ov / f"{unit}.png")
    (hc / "handcheck_list.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["fixture", "crops", "score", "stubfiles"])
    a = ap.parse_args(argv)
    if a.stage == "stubfiles":
        fs = ["tools/s124_page_grouping.py", "tools/plant_regions.py",
              "data/external/models/dinov2-base/model.safetensors", "data/external/models/dinov2-base/config.json"]
        fs += sorted(f"data/external/yale_scans/pages/{k}" for k, v in PR.PANELS.items() if any(p[3] == "P" for p in v))
        for pat in CONTROLS.values():
            fs += sorted(str(Path(f).relative_to(ROOT)).replace("\\", "/") for f in glob.glob(str(ROOT / pat)))
        print("\n".join(fs))
        return
    low_priority()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    logf = open(OUT / f"log_{a.stage}.txt", "a", encoding="utf-8")

    def log(s):
        print(s, flush=True)
        logf.write(s + "\n"); logf.flush()

    emb = Embedder()
    log(f"s124 stage {a.stage} device {emb.dev}")
    gate, fx_lines = run_fixture(emb, log)
    if a.stage == "fixture" or not gate:
        if not gate:
            log("CALL FIXTURE_GATE_FAILED: real stages refused")
        return
    objs, jars = voynich_objects()
    assign_jars(objs, jars)
    log(f"Voynich: {len(objs)} plant-part objects, {len(jars)} jar-like, units {len(set(o['unit'] for o in objs))}")
    if a.stage == "crops":
        for l in save_handcheck(objs, jars):
            log(l)
        meta = [dict(unit=o["unit"], page=o["page"], canvas=o["canvas"], quire=o["quire"], idx=o["idx"],
                     jar_like=o["jar_like"], jar_group=o.get("jar_group"),
                     bbox_frac=[round(t, 4) for t in o["bbox_frac"]], area_frac=o["area_frac"],
                     aspect=o["aspect"]) for o in objs + jars]
        (OUT / "objects.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        log(f"elapsed {time.time() - t0:.0f}s")
        return
    # ---- score
    rng = np.random.default_rng(SEED)
    units = np.array([o["unit"] for o in objs])
    strata = np.array([o["quire"] for o in objs])
    V = analyse(objs, units, strata, emb, rng, extra=True)
    pr = V["primary"]
    L = [f"s124 page grouping of pharma plant-part drawings; SEED {SEED}; N_PERM {N_PERM}; device {emb.dev}"]
    L += fx_lines
    L.append(f"Voynich objects {pr['n_obj']} in {pr['n_units']} units ({pr['n_units_ok']} with >= 4); jars {len(jars)}")
    L.append(f"PRIMARY (DINOv2 silhouette, size-residualised): T {pr['T']:+.4f} null {pr['null_mean']:+.4f} "
             f"+- {pr['null_sd']:.4f} p {pr['p']:.4f} AUC {pr['auc']:.3f} (within pairs {pr['n_within']}, "
             f"between {pr['n_between']}); OLS beta {[round(b, 4) for b in pr['beta']]}")
    for key in ("classical", "colour"):
        r = V[key]
        L.append(f"SECONDARY {key}: T {r['T']:+.4f} p {r['p']:.4f} AUC {r['auc']:.3f}")
    ar = V["ari"]
    L.append(f"CLUSTERS k={ar['k']} ARI {ar['ari']:.4f} null {ar['null_mean']:.4f} +- {ar['null_sd']:.4f} p {ar['p']:.4f}")
    # scan control: multi-panel canvases
    R = V["R"]
    can = np.array([o["canvas"] for o in objs])
    multi = [c for c in np.unique(can) if len(set(units[can == c])) >= 2]
    sel = np.isin(can, multi)
    if sel.sum() > 10:
        rc = stat_test(R[np.ix_(sel, sel)], units[sel], can[sel], np.random.default_rng(SEED + 7))
        L.append(f"SCAN CONTROL (same canvas, {len(multi)} canvases {multi}, {int(sel.sum())} objects): "
                 f"T_canvas {rc['T']:+.4f} p {rc['p']:.4f} AUC {rc['auc']:.3f}")
    # jar groups
    jg = np.array([o.get("jar_group") or "" for o in objs])
    js = jg != ""
    if js.sum() > 10:
        rj = stat_test(R[np.ix_(js, js)], jg[js], units[js], np.random.default_rng(SEED + 8))
        L.append(f"JAR (secondary) within-panel: {len(set(jg[js]))} jar groups in {len(set(units[js]))} panels, "
                 f"{int(js.sum())} objects: T_jar {rj['T']:+.4f} p {rj['p']:.4f} AUC {rj['auc']:.3f}")
        jl = np.where(js, jg, units)
        rj2 = stat_test(R, jl, strata, np.random.default_rng(SEED + 9))
        L.append(f"JAR (secondary) vs other units (labels = jar group where defined, else panel): "
                 f"T {rj2['T']:+.4f} p {rj2['p']:.4f} AUC {rj2['auc']:.3f}")
    # shuffled Voynich
    sh = []
    for k in range(1, 11):
        lab = perm_within(units, strata, np.random.default_rng(SEED + k))
        r = stat_test(R, lab, strata, np.random.default_rng(SEED + 100 + k))
        r["call"] = call_of(pr["n_units_ok"], pr["n_obj"], r["p"])
        sh.append(r)
        L.append(f"SHUFFLED-VOYNICH {k}: T {r['T']:+.4f} p {r['p']:.4f} AUC {r['auc']:.3f} -> {r['call']}")
    # real controls
    caucs = []
    for name, pat in CONTROLS.items():
        sets, nfiles, nel = control_sets(name, pat)
        L.append(f"CONTROL {name}: {nfiles} candidate images, {nel} eligible (>= 4 objects), {len(sets)} sets")
        for si, s in enumerate(sets):
            cobjs, cu, cs = [], [], []
            for pi, (fn, ob) in enumerate(s):
                for o in ob:
                    cobjs.append(o); cu.append(fn); cs.append(f"b{pi // 8}")
            r = analyse(cobjs, cu, cs, emb, np.random.default_rng(SEED + 200 + si))["primary"]
            caucs.append(r["auc"])
            L.append(f"CONTROL {name} set {si}: pages {len(s)} objects {r['n_obj']} T {r['T']:+.4f} p {r['p']:.4f} "
                     f"AUC {r['auc']:.3f} -> {r['call']}")
    # descriptive table
    L.append("DESCRIPTIVE (no call): objects per cluster for each panel (cluster ids from the k-unit clustering)")
    cl = V["clusters"]
    for u in sorted(set(units), key=lambda s: (QUIRE[s.split('_')[0]], s)):
        c = cl[units == u]
        vals, cnt = np.unique(c, return_counts=True)
        L.append(f"  {u:10s} n={len(c):3d} " + " ".join(f"c{v}:{n}" for v, n in sorted(zip(vals, cnt), key=lambda t: -t[1])))
    # calls
    L.append(f"CALL s124 primary: {pr['call']} (p {pr['p']:.4f}, AUC {pr['auc']:.3f})")
    if caucs:
        lo, hi = min(caucs), max(caucs)
        pos = "ABOVE" if pr["auc"] > hi else ("BELOW" if pr["auc"] < lo else "WITHIN")
        L.append(f"CALL s124 vs real herbal controls: {pos} RANGE (Voynich AUC {pr['auc']:.3f}; controls "
                 f"[{lo:.3f}, {hi:.3f}] over {len(caucs)} sets)")
    else:
        L.append("CALL s124 vs real herbal controls: NOT_MEASURABLE (no control set)")
    ng = sum(r["call"] == "GROUPED_BY_PAGE" for r in sh)
    L.append(f"CALL s124 shuffled Voynich: {ng}/10 GROUPED_BY_PAGE; AUC range "
             f"[{min(r['auc'] for r in sh):.3f}, {max(r['auc'] for r in sh):.3f}]")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    res = ROOT / f"results_s124_{stamp}.txt"
    if res.exists():
        raise SystemExit(f"{res} exists; refusing to overwrite")
    res.write_text("\n".join(L) + "\n", encoding="utf-8")
    np.savez(OUT / f"score_{stamp}.npz", E=V["E"], units=units, clusters=cl)
    for l in L:
        log(l)
    log(f"wrote {res.name}; elapsed {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
