#!/usr/bin/env python
"""s53: one pre-registered retry of the same-plant image anchor (s48 failed its known-pair control).

PRE-REGISTERED: this file's sha256 is frozen in s53_same_plant_parts.prereg.sha256 before any scoring run on real
pairs.  Before freezing, only the --selftest path (random embeddings, scratch output) was run on scoring code.

Hypothesis tested (s48 diagnosis, untested there): pharma sketches are partial subsets of the herbal plant (Stolfi:
"a proper subset"), s48's pharma crops fragment, and whole-plant herbal embeddings dilute the match.

Run (scratchpad venv with torch + transformers, from the project root, `python -I`):
    python -I s53_same_plant_parts.py --stage embed     # images -> runs/s53/embed.npz (no labels, no pairs)
    python -I s53_same_plant_parts.py --stage score     # pairs, null, P1 -> results_s53.txt
    python -I s53_same_plant_parts.py --selftest DIR    # scoring code on random embeddings, writes only to DIR
Inputs (read only): runs/s48/crops.json (s48 herbal plant bboxes, s48 pharma crops + jar flags), the Yale scans,
runs/s45/pages/*.json (kraken line boxes for text whitening), tools/plant_regions.py helpers (imported, unchanged),
data/external/models/{dinov2-base, siglip-base-patch16-224}.

DESIGN (fixed before hashing)
(1) Herbal side, part level.  Pool = the 123 herbal pages of s48 (every H_* crop in runs/s48/crops.json).  The panel
    is rebuilt at full resolution exactly as tools/plant_regions.herbal_crop does (text inside padded s45 line boxes
    whitened to parchment; f90r1/r2/v1/v2 have no line boxes) and the plant bbox is s48's bbox_canvas.  Windows:
    - tiles: for scale s in (0.25, 0.40, 0.60), window = s*W x s*H of the plant bbox (W, H), stride s/2 per axis,
      n = ceil((1-s)/(s/2)) + 1 positions per axis evenly spaced from 0 to 1-s (49 + 16 + 9 tiles), plus the whole
      bbox (scale 1.0): 75 tiles per page;
    - colour regions (rule, on the bbox resized to max side 600 px; chroma = CIELAB a*b* distance from the panel
      parchment > DAB = 10; hue from HSV in degrees):
        leaf   = chroma & hue in [60, 170);  flower = chroma & S > 0.25 & (hue in [170, 300) or hue < 12 or hue >= 330);
        each mask opened (3 px disc), dilated (9 px disc), connected components with area >= 0.5 % of the bbox and
        min side >= 24 px; the 3 largest per kind are kept; each region = component bbox padded 10 % per side;
      root   = bottom 30 % band of the bbox, cropped horizontally (and from the top of the band) to the extent of
               foreground pixels (chroma or ink: L* < L*_parch - 25) in that band, padded 10 %, if >= 24 px per side.
    All windows are kept (no emptiness filter).
(2) Pharma side.  Input = s48 non-jar pharma crops (the s48 jar filter is kept: jar-like crops never enter).  On
    each panel, crops whose work-scale bboxes (panel height = 1000 px) are within GAP = 40 px (gap = max of the
    x and y interval gaps, 0 when overlapping) are merged by single linkage into one sketch, pairs taken in order
    of increasing gap; a merge is refused when the union bbox would exceed MAX_SK = 0.60 of the panel width or
    height (set from the s53 overview images before freezing: plain linkage chained the whole top row of f100r).
    Because merging at a fixed gap also joins neighbouring plants on packed pages, every member crop of a
    multi-crop group is kept as an additional sketch ("part", same padding); singletons appear once.  The sketch
    set of a pharma page = its groups + parts; the pair score takes the max over all of them.  The sketch image = the
    union bbox padded by 10 % of its longer side (clipped to the panel), cut from the full-resolution panel.
(3) Embeddings and statistics.  Every image is padded to a square with the parchment colour, resized to 224.
    CLS: DINOv2 ViT-B/14 CLS and SigLIP B/16 image features, 8 views (4 rotations x hflip), L2-normalised per view,
    averaged, re-normalised (as s48).  Window score w(s, x) = cosine(sketch s, window x); mean model = (dino +
    siglip) / 2 per window.  Page score P(s, h) = max over the windows x of page h.
    MNN: DINOv2 patch tokens (identity view only, 16 x 16 patches, L2-normalised).  A patch is foreground if
    >= 10 % of its pixels are chroma or ink (as in (1), against that image's parchment colour).  Between sketch s
    and window x, count mutual nearest neighbours among foreground patches (cosine); w_mnn(s, x) = count /
    n_fg(s); windows or sketches with < 4 foreground patches get 0.  P_mnn(s, h) = max over windows of page h.
    Centring (label-free): C(s, h) = P(s, h) - mean over all pharma sketches of P(., h) (herbal-page hubness),
    then Z(s, h) = (C(s, h) - mean_h C(s, .)) / sd_h C(s, .) (per-sketch scale).
    Pair score (pharma page(s) Q, herbal h) = max over the sketches on Q.  Rank of the true page among the 123
    (1 + #pages strictly higher), MRR, top-5, median percentile, as s48.
    PRIMARY statistic: mean-model CLS, centred (Z), "mean_cls_centred".
    Secondary (reported, no pass/fail): mean_cls_raw, dino_cls_raw, siglip_cls_raw, dino_cls_centred,
    siglip_cls_centred, mnn_raw, mnn_centred.
(4) Pairs, pool, null, P1: as s48.  The 13 ZL pairs (pharma <- herbal): f102r1 <- f1v, f37v ; f100v <- f3v ;
    f102r2 <- f18v, f23r, f32v, f47v ; f102v1 <- f19r ; f89v2 <- f48r ; f89v1+f89v2 <- f48v ; f100r <- f90v1, f90v2 ;
    f99r <- f96v.  Null: 10,000 random permutations of the herbal page labels, one per draw applied jointly to all
    pairs, seed 20261017; P = (1 + #null MRR >= obs) / 10,001.
    P1 (primary statistic only): MRR > null 99th percentile AND >= 5 of 13 true pages in the top 5 -> PASS.
(5) Only if P1 passes: runs/s53/predictions.json for every sketch that is not the primary-statistic argmax sketch
    of a known pair: top-3 herbal pages (primary Z and raw mean cosine) and the pharma label tokens nearest the
    sketch (s48 rule: word-box centres vs sketch centre, both normalised to their own page extent; pages without a
    box file get the page's labels in ZL locus order, flagged).  Its sha256 is appended to the prereg stub as a
    "predictions frozen" amendment line before any text is examined.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "runs" / "s53"
S48 = ROOT / "runs" / "s48"
STUB = ROOT / "s53_same_plant_parts.prereg.sha256"
BOXES = (ROOT / "data" / "external" / "word-coordinates" / "lrozanova-voynich-units-main" / "voynich-units-main" /
         "data" / "voynich-units" / "morphometry_voynichese" / "voynichese_boxes")
SEED, NPERM = 20261017, 10000
SCALES = (0.25, 0.40, 0.60)
GAP, MAX_SK, SK_PAD, REG_PAD, REG_MAX, REG_MIN, REG_AREA, ROOT_BAND = 40, 0.60, 0.10, 0.10, 600, 24, 0.005, 0.30
FG_FRAC, FG_MIN, INK_DL, DAB = 0.10, 4, 25.0, 10.0
PRIMARY = "mean_cls_centred"
STATS = ["mean_cls_centred", "mean_cls_raw", "dino_cls_raw", "siglip_cls_raw", "dino_cls_centred",
         "siglip_cls_centred", "mnn_raw", "mnn_centred"]

PAIRS = [  # (pharma pages, herbal page, source) -- identical to s48
    (["f102r1"], "f1v", "ZL f102r1[3,2] (Petersen, Stolfi)"),
    (["f100v"], "f3v", "ZL f100v[1,1] root (Petersen)"),
    (["f102r2"], "f18v", "ZL f102r2[3,1] ? (FSG, Stolfi)"),
    (["f102v1"], "f19r", "ZL f102v1[2,2] ? (Stolfi); Stolfi 2025 'f102v-2.3'"),
    (["f102r2"], "f23r", "ZL f102r2[3,1] (FSG, GL); Stolfi 2025 3.2"),
    (["f102r2"], "f32v", "ZL f102r2[1,2] ? (FSG, Stolfi)"),
    (["f102r1"], "f37v", "ZL f102r1[3,1] ? (Stolfi)"),
    (["f102r2"], "f47v", "ZL f102r2[1,1] (Petersen)"),
    (["f89v2"], "f48r", "ZL f89v2[3,4] ? (Stolfi)"),
    (["f89v1", "f89v2"], "f48v", "ZL f89v[1,4] ? (Stolfi)"),
    (["f100r"], "f90v2", "ZL f100r[1,3] ? (Stolfi)"),
    (["f100r"], "f90v1", "ZL f100r[1,3] ? (Stolfi)"),
    (["f99r"], "f96v", "ZL f99r[4,1] ? (GL)"),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def now():
    return subprocess.run(["date"], capture_output=True, text=True).stdout.strip() or time.ctime()


# ----------------------------------------------------------------------------------------------- images
def pr():
    sys.path.insert(0, str(ROOT / "tools"))
    import plant_regions  # noqa: E402
    return plant_regions


def lab_of(rgb):
    import cv2
    lab = cv2.cvtColor(np.asarray(rgb, dtype=np.uint8).reshape(1, 1, 3), cv2.COLOR_RGB2LAB).astype(np.float32)[0, 0]
    return lab[0] * 100 / 255, lab[1] - 128, lab[2] - 128


def fg_mask(arr, parch):
    """chroma (a*b* distance from parchment > DAB) or ink (L* < L*_parch - INK_DL)."""
    import cv2
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0] * 100 / 255, lab[..., 1] - 128, lab[..., 2] - 128
    L0, a0, b0 = lab_of(parch)
    chroma = np.hypot(A - a0, B - b0) > DAB
    ink = L < L0 - INK_DL
    return chroma, ink


def herbal_panel(P, rec, s45, panels):
    pid = rec["page"]
    js = s45 / f"{pid}.json"
    if js.exists():
        d = json.loads(js.read_text(encoding="utf-8"))
        fname, a, b, lines = d["file"], 0.0, 1.0, d.get("lines")
    else:
        fname, a, b = panels[pid]
        lines = None
    arr, off, _ = P.load_panel(fname, a, b)
    arr = arr.copy()
    prm = P.PARAMS
    _, _, parch, _, _ = P.masks(arr, prm)
    if lines:
        paint, _ = P.chroma_mask(arr, prm)
        for ln in lines:
            bx0, by0, bx1, by1 = ln["bbox"]
            pad = int(prm["TEXT_PAD"] * (by1 - by0))
            X0, Y0 = max(0, bx0 - off[0] - pad), max(0, by0 - off[1] - pad)
            X1, Y1 = min(arr.shape[1], bx1 - off[0] + pad), min(arr.shape[0], by1 - off[1] + pad)
            if X1 > X0 and Y1 > Y0:
                sub = arr[Y0:Y1, X0:X1]
                sub[~paint[Y0:Y1, X0:X1]] = parch
    x, y, w, h = rec["bbox_canvas"]
    x, y = x - off[0], y - off[1]
    return arr[y:y + h, x:x + w], parch


def tiles(W, H):
    out = []
    for s in SCALES:
        n = math.ceil((1 - s) / (s / 2)) + 1
        pos = np.linspace(0, 1 - s, n)
        for py in pos:
            for px in pos:
                out.append((f"s{int(round(s * 100))}", int(px * W), int(py * H), max(1, int(s * W)), max(1, int(s * H))))
    out.append(("full", 0, 0, W, H))
    return out


def colour_regions(plant, parch):
    """leaf / flower / root regions (bboxes in plant coords), rule in the module docstring."""
    import cv2
    H, W = plant.shape[:2]
    sc = REG_MAX / max(H, W)
    sm = cv2.resize(plant, (max(1, int(W * sc)), max(1, int(H * sc))), interpolation=cv2.INTER_AREA)
    h, w = sm.shape[:2]
    chroma, ink = fg_mask(sm, parch)
    hsv = cv2.cvtColor(sm, cv2.COLOR_RGB2HSV).astype(np.float32)
    hue, sat = hsv[..., 0] * 2, hsv[..., 1] / 255
    masks = {"leaf": chroma & (hue >= 60) & (hue < 170),
             "flower": chroma & (sat > 0.25) & (((hue >= 170) & (hue < 300)) | (hue < 12) | (hue >= 330))}
    out = []
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    k_dil = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

    def padbox(x0, y0, x1, y1):
        px, py = REG_PAD * (x1 - x0), REG_PAD * (y1 - y0)
        X0, Y0 = max(0, int(x0 - px)), max(0, int(y0 - py))
        X1, Y1 = min(w, int(x1 + px)), min(h, int(y1 + py))
        return (int(X0 / sc), int(Y0 / sc), max(1, int((X1 - X0) / sc)), max(1, int((Y1 - Y0) / sc)))

    for kind, m in masks.items():
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, k_open)
        m = cv2.dilate(m, k_dil)
        n, _, st, _ = cv2.connectedComponentsWithStats(m, 8)
        comps = [st[i] for i in range(1, n) if st[i][4] >= REG_AREA * h * w and min(st[i][2], st[i][3]) >= REG_MIN]
        comps.sort(key=lambda s: -s[4])
        for s in comps[:3]:
            out.append((kind,) + padbox(s[0], s[1], s[0] + s[2], s[1] + s[3]))
    y0 = int((1 - ROOT_BAND) * h)
    band = (chroma | ink)[y0:]
    ys, xs = np.where(band)
    if len(xs):
        x0_, x1_, yy0, yy1 = xs.min(), xs.max() + 1, ys.min() + y0, ys.max() + 1 + y0
        if x1_ - x0_ >= REG_MIN and yy1 - yy0 >= REG_MIN:
            out.append(("root",) + padbox(x0_, yy0, x1_, yy1))
    return out


def pharma_panels(P):
    """(page, panel_no) -> (canvas, x0, x1), the same numbering as tools/plant_regions.stage_crops."""
    res, cnt = {}, {}
    for fname, panels in P.PANELS.items():
        for pid, a, b, s in panels:
            if s != "P":
                continue
            cnt[pid] = cnt.get(pid, 0) + 1
            res[(pid, cnt[pid])] = (fname, a, b)
    return res


def merge_groups(boxes, Ws, Hs=1000):
    """single linkage on work-px boxes (x, y, w, h), pairs taken in order of increasing gap (gap = max(x gap,
    y gap) <= GAP); a merge is refused if the union bbox of the two groups would exceed MAX_SK of the panel width
    or height (stops chaining across a packed row of plants)."""
    n = len(boxes)
    par = list(range(n))
    ext = {i: [b[0], b[1], b[0] + b[2], b[1] + b[3]] for i, b in enumerate(boxes)}

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    cand = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = boxes[i], boxes[j]
            dx = max(0, b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]))
            dy = max(0, b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
            if max(dx, dy) <= GAP:
                cand.append((max(dx, dy), i, j))
    for _, i, j in sorted(cand):
        ri, rj = f(i), f(j)
        if ri == rj:
            continue
        a, b = ext[ri], ext[rj]
        u = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
        if u[2] - u[0] > MAX_SK * Ws or u[3] - u[1] > MAX_SK * Hs:
            continue
        par[ri] = rj
        ext[rj] = u
    g = {}
    for i in range(n):
        g.setdefault(f(i), []).append(i)
    return sorted(g.values(), key=lambda m: (min(boxes[i][1] for i in m), min(boxes[i][0] for i in m)))


def square(img, parch, size=224):
    from PIL import Image
    w, h = img.size
    s = max(w, h)
    c = Image.new("RGB", (s, s), tuple(int(t) for t in parch))
    c.paste(img, ((s - w) // 2, (s - h) // 2))
    return c.resize((size, size), Image.BICUBIC)


class Embedder:
    def __init__(self):
        import torch
        from transformers import AutoModel, SiglipModel
        self.t = torch
        M = ROOT / "data" / "external" / "models"
        self.dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.dino = AutoModel.from_pretrained(str(M / "dinov2-base"), use_safetensors=True).to(self.dev).eval().half()
        self.sig = SiglipModel.from_pretrained(str(M / "siglip-base-patch16-224"),
                                               use_safetensors=True).to(self.dev).eval().half()
        self.norm = {"dino": ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), "siglip": ((0.5,) * 3, (0.5,) * 3)}

    def __call__(self, sq_imgs, parchs):
        """sq_imgs: list of 224 PIL squares.  Returns dino CLS, siglip feat (n, d), dino patch tokens (n, 256, 768)
        fp16, fg patch mask (n, 256)."""
        t = self.t
        from PIL import Image
        arrs = []
        fgm = []
        for im, pa in zip(sq_imgs, parchs):
            a = np.asarray(im)
            ch, ink = fg_mask(a, pa)
            f = (ch | ink).reshape(16, 14, 16, 14).mean((1, 3)).reshape(-1) >= FG_FRAC
            fgm.append(f)
            for flip in (False, True):
                b = im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
                for k in range(4):
                    arrs.append(np.asarray(b.rotate(90 * k, expand=True), dtype=np.float32) / 255.0)
        x = t.from_numpy(np.stack(arrs)).permute(0, 3, 1, 2).to(self.dev)
        n = len(sq_imgs)
        out = {}
        with t.no_grad():
            for name in ("dino", "siglip"):
                m, s = self.norm[name]
                xn = ((x - t.tensor(m, device=self.dev).view(1, 3, 1, 1)) /
                      t.tensor(s, device=self.dev).view(1, 3, 1, 1)).half()
                if name == "dino":
                    hs = self.dino(pixel_values=xn).last_hidden_state
                    f = hs[:, 0]
                    tok = hs.view(n, 8, hs.shape[1], hs.shape[2])[:, 0, 1:]  # identity view = index 0
                    out["tok"] = t.nn.functional.normalize(tok.float(), dim=-1).half()
                else:
                    f = self.sig.get_image_features(pixel_values=xn)
                f = t.nn.functional.normalize(f.float(), dim=-1).view(n, 8, -1).mean(1)
                out[name] = t.nn.functional.normalize(f, dim=-1).cpu().numpy()
        out["fg"] = np.stack(fgm)
        return out


def mnn_frac(tS, mS, tW, mW, torch):
    """tS (ns,256,d), mS (ns,256) bool; tW (nw,256,d), mW (nw,256).  Returns (ns, nw) count / n_fg(sketch)."""
    sim = torch.einsum("ipd,jqd->ijpq", tS, tW).float()                # ns, nw, 256, 256
    neg = torch.tensor(-1e4, device=sim.device)
    valid = mS[:, None, :, None] & mW[None, :, None, :]
    sim = torch.where(valid, sim, neg)
    a2b = sim.argmax(3)                                                   # ns, nw, 256 (sketch patch -> window)
    b2a = sim.argmax(2)                                                   # ns, nw, 256 (window patch -> sketch)
    back = torch.gather(b2a, 2, a2b)
    idx = torch.arange(sim.shape[2], device=sim.device).view(1, 1, -1)
    mutual = (back == idx) & mS[:, None, :] & mW.any(1)[None, :, None]
    cnt = mutual.sum(2).float()
    nS = mS.sum(1).float()
    nW = mW.sum(1)
    res = cnt / nS.clamp(min=1)[:, None]
    res[(nS < FG_MIN)] = 0
    res[:, (nW < FG_MIN)] = 0
    return res


def stage_embed():
    import torch
    from PIL import Image, ImageDraw
    t0 = time.time()
    P = pr()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "overview").mkdir(exist_ok=True)
    meta = json.loads((S48 / "crops.json").read_text(encoding="utf-8"))
    crops = meta["crops"]
    herb = [c for c in crops if c["kind"] == "herbal"]
    comp_h = {pid: (f, a, b) for f, pans in P.PANELS.items() for pid, a, b, s in pans if s == "H"}
    emb = Embedder()

    # ---- pharma sketches
    pp = pharma_panels(P)
    sketches, sk_imgs, sk_parch = [], [], []
    for (pid, pno), (fname, a, b) in pp.items():
        cs = [c for c in crops if c["kind"] == "pharma" and c["page"] == pid and c["panel"] == pno]
        nonjar = [c for c in cs if not c["jar_like"]]
        arr, off, _ = P.load_panel(fname, a, b)
        Ht, Wt = arr.shape[:2]
        sc = 1000 / Ht
        Ws = max(1, int(Wt * sc))
        wb = [(c["bbox_panel_frac"][0] * Ws, c["bbox_panel_frac"][1] * 1000,
               c["bbox_panel_frac"][2] * Ws, c["bbox_panel_frac"][3] * 1000) for c in nonjar]
        groups = merge_groups(wb, Ws) if wb else []
        ov = Image.fromarray(arr).resize((Ws, 1000))
        d = ImageDraw.Draw(ov)
        for c in cs:
            if c["jar_like"]:
                f = c["bbox_panel_frac"]
                d.rectangle([f[0] * Ws, f[1] * 1000, (f[0] + f[2]) * Ws, (f[1] + f[3]) * 1000], outline="blue", width=2)
        units = [("group", g) for g in groups] + [("part", [i]) for g in groups if len(g) > 1 for i in g]
        for gi, (role, g) in enumerate(units):
            x0 = min(wb[i][0] for i in g); y0 = min(wb[i][1] for i in g)
            x1 = max(wb[i][0] + wb[i][2] for i in g); y1 = max(wb[i][1] + wb[i][3] for i in g)
            pad = SK_PAD * max(x1 - x0, y1 - y0)
            X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(Ws, x1 + pad), min(1000, y1 + pad)
            fx0, fy0, fx1, fy1 = int(X0 / sc), int(Y0 / sc), int(X1 / sc), int(Y1 / sc)
            parch = nonjar[g[0]]["parch"]
            sid = f"S_{pid}_p{pno}_{gi:02d}" + ("" if role == "group" else "_part")
            img = Image.fromarray(arr[fy0:fy1, fx0:fx1])
            sketches.append(dict(sketch=sid, page=pid, panel=pno, role=role, members=[nonjar[i]["crop"] for i in g],
                                 bbox_canvas=[fx0 + off[0], fy0 + off[1], fx1 - fx0, fy1 - fy0],
                                 bbox_panel_frac=[round(x0 / Ws, 4), round(y0 / 1000, 4),
                                                  round((x1 - x0) / Ws, 4), round((y1 - y0) / 1000, 4)],
                                 parch=parch))
            sk_imgs.append(square(img, parch))
            sk_parch.append(parch)
            if role == "group":
                d.rectangle([X0, Y0, X1, Y1], outline="red", width=3)
                d.text((X0 + 4, Y0 + 4), f"{gi:02d}" + (f"({len(g)})" if len(g) > 1 else ""), fill="red")
        ov.save(OUT / "overview" / f"{pid}_p{pno}.png")
    print(f"sketches: {len(sketches)} ({sum(s['role'] == 'group' for s in sketches)} groups) "
          f"({time.time() - t0:.0f}s)")
    SK = {"dino": [], "siglip": []}
    tokS, fgS = [], []
    for i in range(0, len(sk_imgs), 32):
        o = emb(sk_imgs[i:i + 32], sk_parch[i:i + 32])
        SK["dino"].append(o["dino"]); SK["siglip"].append(o["siglip"])
        tokS.append(o["tok"]); fgS.append(o["fg"])
    tS = torch.cat(tokS)
    mS = torch.from_numpy(np.concatenate(fgS)).to(tS.device)

    # ---- herbal windows
    windows, WD, WS, MNN = [], [], [], []
    for k, rec in enumerate(herb):
        plant, parch = herbal_panel(P, rec, ROOT / "runs" / "s45" / "pages", comp_h)
        H, W = plant.shape[:2]
        wins = tiles(W, H) + colour_regions(plant, parch)
        pim = Image.fromarray(plant)
        imgs = []
        for (kind, x, y, w, h) in wins:
            imgs.append(square(pim.crop((x, y, min(W, x + w), min(H, y + h))), parch))
            windows.append(dict(page=rec["page"], kind=kind, box=[int(x), int(y), int(w), int(h)]))
        for i in range(0, len(imgs), 32):
            o = emb(imgs[i:i + 32], [parch] * len(imgs[i:i + 32]))
            WD.append(o["dino"]); WS.append(o["siglip"])
            mW = torch.from_numpy(o["fg"]).to(tS.device)
            cols = []
            for j in range(0, o["tok"].shape[0], 4):
                cols.append(mnn_frac(tS, mS, o["tok"][j:j + 4], mW[j:j + 4], torch))
            MNN.append(torch.cat(cols, 1).cpu().numpy())
        if k % 10 == 0:
            print(f"  herbal {k + 1}/{len(herb)} {rec['page']}: {len(wins)} windows "
                  f"({sum(1 for w_ in wins if w_[0] in ('leaf', 'flower', 'root'))} colour) {time.time() - t0:.0f}s")
    np.savez(OUT / "embed.npz", sk_dino=np.concatenate(SK["dino"]), sk_siglip=np.concatenate(SK["siglip"]),
             win_dino=np.concatenate(WD), win_siglip=np.concatenate(WS),
             mnn=np.concatenate(MNN, 1).astype(np.float32), sk_nfg=mS.sum(1).cpu().numpy())
    (OUT / "sketches.json").write_text(json.dumps(dict(script_sha256=sha(__file__), sketches=sketches,
                                                       windows=windows, embed_date=now(),
                                                       embed_elapsed=round(time.time() - t0, 1),
                                                       plant_regions_sha256=sha(ROOT / "tools" / "plant_regions.py")),
                                                  indent=0), encoding="utf-8", newline="\n")
    from collections import Counter
    print(f"windows: {len(windows)} {dict(Counter(w['kind'] for w in windows))}; elapsed {time.time() - t0:.0f}s")


# ----------------------------------------------------------------------------------------------- scoring
def page_max(Wsim, win_page_idx, N):
    """Wsim (ns, nwin) -> (ns, N) max over each page's windows."""
    out = np.full((Wsim.shape[0], N), -np.inf)
    for h in range(N):
        out[:, h] = Wsim[:, win_page_idx == h].max(1)
    return out


def centre(Pm):
    C = Pm - Pm.mean(0, keepdims=True)
    sd = C.std(1, keepdims=True)
    return (C - C.mean(1, keepdims=True)) / np.where(sd > 0, sd, 1)


def statistics(skd, sks, wd, ws, mnn, win_page_idx, N):
    cd, cs = skd @ wd.T, sks @ ws.T
    raw = {"dino": page_max(cd, win_page_idx, N), "siglip": page_max(cs, win_page_idx, N),
           "mean": page_max((cd + cs) / 2, win_page_idx, N), "mnn": page_max(mnn, win_page_idx, N)}
    st = {"mean_cls_centred": centre(raw["mean"]), "mean_cls_raw": raw["mean"], "dino_cls_raw": raw["dino"],
          "siglip_cls_raw": raw["siglip"], "dino_cls_centred": centre(raw["dino"]),
          "siglip_cls_centred": centre(raw["siglip"]), "mnn_raw": raw["mnn"], "mnn_centred": centre(raw["mnn"])}
    best_win = {"mean": (cd + cs) / 2, "mnn": mnn}
    return st, best_win


def ranks_for(Sm, rows_by_pair, true_idx):
    sc = np.stack([Sm[r].max(0) for r in rows_by_pair])
    tv = sc[np.arange(len(true_idx)), true_idx]
    return 1 + (sc > tv[:, None]).sum(1), sc


def null_mrr(sc, true_idx, rng):
    n, N = sc.shape
    order = -np.sort(-sc, axis=1)
    rank_all = np.stack([1 + np.searchsorted(-order[i], -sc[i], side="left") for i in range(n)])
    out = np.empty(NPERM)
    for k in range(NPERM):
        perm = rng.permutation(N)
        out[k] = np.mean(1.0 / rank_all[np.arange(n), perm[true_idx]])
    return out


def evaluate(st, sk_pages, hpages):
    N = len(hpages)
    rows_by_pair, true_idx, scored = [], [], []
    for pages, hp, src in PAIRS:
        r = [i for i, p in enumerate(sk_pages) if p in pages]
        if not r or hp not in hpages:
            continue
        scored.append((pages, hp, src)); rows_by_pair.append(np.array(r)); true_idx.append(hpages.index(hp))
    true_idx = np.array(true_idx)
    res = {}
    for name in STATS:
        rk, sc = ranks_for(st[name], rows_by_pair, true_idx)
        mrr = float(np.mean(1.0 / rk))
        nul = null_mrr(sc, true_idx, np.random.default_rng(SEED))
        q99 = float(np.quantile(nul, 0.99))
        res[name] = dict(mrr=mrr, q99=q99, null_mean=float(nul.mean()),
                         p=(1 + int((nul >= mrr).sum())) / (NPERM + 1), top5=int((rk <= 5).sum()),
                         top1=int((rk == 1).sum()), ranks=rk.tolist(),
                         median_pct=float(np.median((rk - 1) / (N - 1))))
    return res, scored, rows_by_pair, true_idx


def label_tokens(page):
    sys.path.insert(0, str(ROOT))
    import vparse
    recs = [r for r in vparse.load() if r["page"] == page and r["unit"].startswith("L")]
    return [(f"{page}.{r['line']}", w) for r in recs for w in r["words"]]


def nearest_labels(page, sk_on_panel, sk, k=3):
    labs = label_tokens(page)
    f = BOXES / f"{page}.js"
    if not f.exists():
        return dict(method="no word boxes on disk: page labels in ZL3b locus order",
                    labels=[dict(locus=l, word=w) for l, w in labs])
    vocab, boxes = json.loads(f.read_text(encoding="utf-8"))
    words = [(vocab[b[0]][0], b[1] + b[3] / 2, b[2] + b[4] / 2) for b in boxes]
    xs = [b[1] for b in boxes] + [b[1] + b[3] for b in boxes]
    ys = [b[2] for b in boxes] + [b[2] + b[4] for b in boxes]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    labset = {w for _, w in labs}
    cand = [(w, (x - bx0) / (bx1 - bx0), (y - by0) / (by1 - by0)) for w, x, y in words if w in labset]
    fr = np.array([c["bbox_panel_frac"] for c in sk_on_panel])
    cx0, cy0 = fr[:, 0].min(), fr[:, 1].min()
    cx1, cy1 = (fr[:, 0] + fr[:, 2]).max(), (fr[:, 1] + fr[:, 3]).max()
    x, y, w, h = sk["bbox_panel_frac"]
    px, py = (x + w / 2 - cx0) / max(cx1 - cx0, 1e-9), (y + h / 2 - cy0) / max(cy1 - cy0, 1e-9)
    d = sorted((float(np.hypot(px - a, py - b)), wd) for wd, a, b in cand)
    return dict(method="word-box centres vs sketch centre, both normalised to own page extent (approximate)",
                nearest=[dict(word=wd, dist=round(dd, 3)) for dd, wd in d[:k]],
                n_label_boxes=len(cand), n_label_tokens_zl=len(labs))


def report(st, best_win, res, scored, rows_by_pair, true_idx, sk_ids, hpages, windows, win_page_idx, w):
    N = len(hpages)
    w("statistics (pair score = max over the pharma page's sketches; rank among N; null = 10,000 label perms):")
    for name in STATS:
        r = res[name]
        tag = "PRIMARY" if name == PRIMARY else "secondary"
        w(f"  [{name:<19}] {tag:<9} MRR={r['mrr']:.4f}  null mean={r['null_mean']:.4f} q99={r['q99']:.4f}  "
          f"P={r['p']:.4f}  top5={r['top5']}/{len(true_idx)}  top1={r['top1']}  median pct={r['median_pct']:.3f}")
    w("")
    w(f"per-pair ranks (/{N}); columns = " + ", ".join(STATS))
    w("  best sketch / best window = argmax for the true page under the primary statistic and mean-model raw cosine")
    for j, ((pages, hp, src), r) in enumerate(zip(scored, rows_by_pair)):
        h = true_idx[j]
        bs = r[np.argmax(st[PRIMARY][r, h])]
        cols = np.where(win_page_idx == h)[0]
        bw = cols[np.argmax(best_win["mean"][bs, cols])]
        rr = " ".join(f"{res[n]['ranks'][j]:>3}" for n in STATS)
        w(f"  {'+'.join(pages):<12} <- {hp:<6} {rr}   sketch {sk_ids[bs]} window {windows[bw]['kind']} "
          f"cos={best_win['mean'][bs, bw]:.3f}  [{src}]")


def score_core(E, sk, wins, w):
    hpages = sorted({x["page"] for x in wins}, key=lambda p: [x["page"] for x in wins].index(p))
    win_page_idx = np.array([hpages.index(x["page"]) for x in wins])
    N = len(hpages)
    st, best_win = statistics(E["sk_dino"], E["sk_siglip"], E["win_dino"], E["win_siglip"], E["mnn"],
                              win_page_idx, N)
    sk_pages = [s["page"] for s in sk]
    res, scored, rows_by_pair, true_idx = evaluate(st, sk_pages, hpages)
    report(st, best_win, res, scored, rows_by_pair, true_idx, [s["sketch"] for s in sk], hpages, wins,
           win_page_idx, w)
    r = res[PRIMARY]
    p1 = (r["mrr"] > r["q99"]) and (r["top5"] >= 5)
    w("")
    w(f"P1 ({PRIMARY}): MRR {r['mrr']:.4f} {'>' if r['mrr'] > r['q99'] else '<='} null q99 {r['q99']:.4f}; "
      f"top-5 count {r['top5']} (need >= 5) -> {'PASS: image matching recovers known pairs' if p1 else 'FAIL'}")
    return p1, st, res, scored, rows_by_pair, true_idx, hpages


def selftest(d):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(1)
    hp = sorted({p for _, h, _ in PAIRS for p in [h]}) + [f"fX{i}" for i in range(110)]
    wins = [dict(page=p, kind="s25", box=[0, 0, 1, 1]) for p in hp for _ in range(7)]
    skp = ["f102r1", "f100v", "f102r2", "f102v1", "f89v2", "f89v1", "f100r", "f99r", "f88r"]
    sk = [dict(sketch=f"S_{p}_{i}", page=p) for p in skp for i in range(5)]

    def nz(a):
        return a / np.linalg.norm(a, axis=1, keepdims=True)
    for planted in (False, True):
        E = dict(sk_dino=nz(rng.normal(size=(len(sk), 16))), sk_siglip=nz(rng.normal(size=(len(sk), 16))),
                 win_dino=nz(rng.normal(size=(len(wins), 16))), win_siglip=nz(rng.normal(size=(len(wins), 16))),
                 mnn=rng.random((len(sk), len(wins))))
        if planted:  # copy one sketch embedding into one window of each true page
            for pages, h, _ in PAIRS:
                si = [i for i, s in enumerate(sk) if s["page"] in pages][0]
                wi = [i for i, x in enumerate(wins) if x["page"] == h][0]
                for m in ("dino", "siglip"):
                    E[f"win_{m}"][wi] = E[f"sk_{m}"][si]
        L = []
        p1, *_ = score_core(E, sk, wins, lambda s: (L.append(s), print(s)))
        (d / f"selftest_{'planted' if planted else 'random'}.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"selftest planted={planted}: P1={'PASS' if p1 else 'FAIL'}\n")


def stage_score():
    t0 = time.time()
    me = sha(__file__)
    stub_match = STUB.exists() and any(line.split()[:2] == [me, Path(__file__).name]
                                       for line in STUB.read_text(encoding="utf-8").splitlines()
                                       if not line.startswith("#") and line.strip())
    meta = json.loads((OUT / "sketches.json").read_text(encoding="utf-8"))
    E = dict(np.load(OUT / "embed.npz"))
    sk, wins = meta["sketches"], meta["windows"]
    L = []

    def w(s=""):
        L.append(s)
        print(s)
    from collections import Counter
    kinds = Counter(x["kind"] for x in wins)
    w(f"embed stage: run {meta['embed_date']}, script sha256 {meta['script_sha256']} "
      f"({'same as scoring script' if meta['script_sha256'] == me else 'DIFFERENT from scoring script'}), "
      f"plant_regions.py sha256 {meta['plant_regions_sha256']}, elapsed {meta['embed_elapsed']}s")
    w(f"pharma sketches: {len(sk)} = {sum(s['role'] == 'group' for s in sk)} merged groups from "
      f"{sum(len(s['members']) for s in sk if s['role'] == 'group')} non-jar s48 crops + "
      f"{sum(s['role'] == 'part' for s in sk)} member crops of multi-crop groups "
      f"(multi-crop sketches: {sum(len(s['members']) > 1 for s in sk)}; GAP={GAP} work px, MAX_SK={MAX_SK}, pad {SK_PAD})")
    w(f"herbal windows: {len(wins)} over {len({x['page'] for x in wins})} pages; by kind {dict(kinds)}")
    w(f"models: DINOv2 ViT-B/14 CLS + SigLIP B/16 (8 views averaged); MNN on DINOv2 patch tokens (identity view, "
      f"fg patch >= {FG_FRAC:.0%} chroma/ink)")
    w("")
    p1, st, res, scored, rows_by_pair, true_idx, hpages = score_core(E, sk, wins, w)
    w("")
    pred_line = "predictions: not written (P1 failed)"
    if p1:
        known = set()
        for (pages, hp, src), r, h in zip(scored, rows_by_pair, true_idx):
            known.add(sk[r[np.argmax(st[PRIMARY][r, h])]]["sketch"])
        preds = []
        for i, s in enumerate(sk):
            if s["sketch"] in known:
                continue
            z = st[PRIMARY][i]
            top = np.argsort(-z)[:3]
            same = [x for x in sk if x["page"] == s["page"] and x["panel"] == s["panel"]]
            preds.append(dict(sketch=s["sketch"], page=s["page"], panel=s["panel"], members=s["members"],
                              bbox_canvas=s["bbox_canvas"],
                              top3=[dict(herbal=hpages[j], z=round(float(z[j]), 4),
                                         cos_mean_raw=round(float(st["mean_cls_raw"][i, j]), 4)) for j in top],
                              labels=nearest_labels(s["page"], same, s)))
        pj = dict(note="s53 frozen predictions (primary: mean_cls_centred); written before any text test",
                  script_sha256=me, known_pair_sketches=sorted(known), n=len(preds), predictions=preds)
        pf = OUT / "predictions.json"
        pf.write_text(json.dumps(pj, indent=1), encoding="utf-8", newline="\n")
        ph = sha(pf)
        with STUB.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"# amendment {now()}: predictions frozen (runs/s53/predictions.json written by the scoring run "
                    f"after P1 passed, before any text was examined)\n{ph}  runs/s53/predictions.json\n")
        pred_line = f"predictions: FROZEN runs/s53/predictions.json ({len(preds)} sketches) sha256={ph} (stub amended)"
    w(pred_line)
    (OUT / "pairs_table.json").write_text(json.dumps(dict(primary=PRIMARY, results=res, herbal_pool=hpages,
                                                          pairs=[dict(pharma=p, herbal=h, src=s) for p, h, s in scored]),
                                                     indent=1), encoding="utf-8", newline="\n")
    head = [f"date: {now()}", f"s53_same_plant_parts.py sha256={me}", f"stub_match={stub_match}",
            f"elapsed: score {time.time() - t0:.1f}s + embed {meta['embed_elapsed']}s", ""]
    (ROOT / "results_s53.txt").write_text("\n".join(head + L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(head))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["embed", "score"])
    ap.add_argument("--selftest")
    a = ap.parse_args()
    if a.selftest:
        selftest(a.selftest)
    elif a.stage == "embed":
        stage_embed()
    elif a.stage == "score":
        stage_score()


if __name__ == "__main__":
    main()
