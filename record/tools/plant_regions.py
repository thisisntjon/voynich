#!/usr/bin/env python
"""s48 pipeline: plant / sketch regions on the Yale scans, plus frozen-model embeddings (not scored).

Run from the project root (scratchpad venv with torch + transformers, `python -I`):

    <venv_s45>/Scripts/python.exe -I tools/plant_regions.py [--stage crops|embed|all]

A. Page -> canvas mapping.
   Herbal pages: every ZL3b page with $I=H that has a single-folio canvas in runs/s45/pages/<id>.json
   (s45 mapping, tools/segment_scans.py).  Four f90 panels are added from composite canvases (see PANELS).
   Pharma pages (ZL ids f88r..f89v1, f99r..f102v1, $I=P): all are on composite or single canvases; the
   panel x-ranges in PANELS were set by eye on thumbnails, and panel identity follows ZL3b label/jar counts
   and the layout of the word boxes in data/external/word-coordinates (Rozanova voynichese_boxes):
     161 '88v and 89r'   -> f88v | f89r1 | f89r2            (3 / 2-3 / 3 jars; f89r2 has the most labels)
     162 '89v (part)'    -> f89v2                          (labels-para-labels-para-plants layout, 12 Lf)
     163 '89v (part) and 90r' -> f89v1 | f90v2 | f90r2      (f89v1: one big paragraph; f90v2 8 lines with
                                                             <-> gaps around the stems; f90r2 6 lines)
     164 '90r' -> f90r1 (9 lines, folio number 90); 165 '90v (part)' -> f90v1 (11 lines, quire mark)
     177 '100v and 101r' -> f100v | f101r ; 178 '101v (part)' and the left panel of 179 -> f101v
     179 '101v (part) and 102r' -> f101v | f102r1 | f102r2
     180 '102v (part)' -> f102v2 ; 181 '102v (part)' -> f102v1 (ZL3b f102v1 carries 'gathering number 19',
                             and canvas 181 shows a '19' at the foot; two label rows each, as ZL3b)
   These identities are inferences, unverified against a foliation reference.

B. Masks (work scale: panel resized so its height is WORK_H px).
   parchment = per-panel medians of HSV S and V over non-black pixels;
   paint = S > medS + PAINT_DS and V > V_MIN ; ink = V < medV - INK_DV and V > V_MIN.
   Herbal: inside the s45 kraken line boxes (padded TEXT_PAD x line height) every non-paint pixel is set to
     the parchment colour (text removal that keeps paint crossing the text); then the same paint components
     as for pharma (below); the plant = union bbox of components (<= MAX_FRAC of the panel, >= MIN_AREA, x-centre
     not within EDGE of the left/right panel edge: page edges, neighbouring leaves)
     with area >= HERB_KEEP x the largest.  Crop = that bbox of the text-whitened panel.  f90r1/r2/v1/v2
     (composite canvases) have no s45 line boxes: their text stays in the crop.
   Pharma: sketch mask = work-scale (area-averaged) CIELAB chroma distance from the panel's median parchment
     a*b* > DAB (green, red, blue and ochre paint; thin brown text averages out), opened with an OPEN px disc
     (removes text strokes and thin outlines), dilated DIL px, connected components; components wider or
     taller than MAX_FRAC of the panel are dropped (page edges, whole-page stains); every component with bbox area >= MIN_AREA of
     the panel and min side >= MIN_SIDE x panel height is a candidate crop (kept with bbox, full-res coords).
     jar_like = (h/w >= JAR_ASPECT and h >= JAR_H x panel height) or (h/w >= JAR_ASPECT_EDGE and x-centre in
     the left JAR_EDGE of the panel) (painted containers stand at the left margin); jar-like
     crops are kept on disk but flagged.  Crops are numbered top-to-bottom by bbox top.  Cell (row, col)
     assignment for P2 is done in s48_same_plant_images.py from bbox_panel_frac, not here.
C. Embeddings: each crop is padded to a square with the parchment colour, resized to 224, and embedded by
   DINOv2 ViT-B/14 (CLS token, data/external/models/dinov2-base) and SigLIP ViT-B/16-224
   (get_image_features, data/external/models/siglip-base-patch16-224); 8 views (4 rotations x hflip),
   L2-normalised per view, averaged, re-normalised.  Output: runs/s48/embeddings.npz + runs/s48/crops.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCANS = ROOT / "data" / "external" / "yale_scans"
S45 = ROOT / "runs" / "s45" / "pages"
OUT = ROOT / "runs" / "s48"
CROPS = OUT / "crops"
MODELS = ROOT / "data" / "external" / "models"

PARAMS = dict(WORK_H=1000, PAINT_DS=0.10, INK_DV=0.30, V_MIN=0.18, CLOSE=15, HERB_KEEP=0.05,
              TEXT_PAD=0.25, DAB=10.0, OPEN=5, DIL=15, MAX_FRAC=0.85, EDGE=0.06, MIN_AREA=0.002, MIN_SIDE=0.035,
              JAR_ASPECT=1.6, JAR_H=0.12, JAR_ASPECT_EDGE=1.2, JAR_EDGE=0.2,  CROP_SAVE_MAX=512, EMB_SIZE=224)

# canvas file -> list of (page id, x0 frac, x1 frac, section)
PANELS = {
    "160_88r.jpg": [("f88r", 0.0, 1.0, "P")],
    "161_88v_and_89r.jpg": [("f88v", 0.05, 0.31, "P"), ("f89r1", 0.31, 0.58, "P"), ("f89r2", 0.58, 0.99, "P")],
    "162_89v_part.jpg": [("f89v2", 0.04, 0.95, "P")],
    "163_89v_part_and_90r.jpg": [("f89v1", 0.08, 0.385, "P"), ("f90v2", 0.385, 0.69, "H"), ("f90r2", 0.69, 0.98, "H")],
    "164_90r.jpg": [("f90r1", 0.04, 0.97, "H")],
    "165_90v_part.jpg": [("f90v1", 0.06, 0.97, "H")],
    "174_99r.jpg": [("f99r", 0.0, 1.0, "P")],
    "175_99v.jpg": [("f99v", 0.0, 1.0, "P")],
    "176_100r.jpg": [("f100r", 0.0, 1.0, "P")],
    "177_100v_and_101r.jpg": [("f100v", 0.08, 0.39, "P"), ("f101r", 0.39, 0.98, "P")],
    "178_101v_part.jpg": [("f101v", 0.0, 1.0, "P")],
    "179_101v_part_and_102r.jpg": [("f101v", 0.04, 0.35, "P"), ("f102r1", 0.35, 0.645, "P"), ("f102r2", 0.645, 0.99, "P")],
    "180_102v_part.jpg": [("f102v2", 0.05, 0.97, "P")],
    "181_102v_part.jpg": [("f102v1", 0.0, 1.0, "P")],
}
PHARMA_IDS = ["f88r", "f88v", "f89r1", "f89r2", "f89v2", "f89v1", "f99r", "f99v", "f100r", "f100v", "f101r",
              "f101v", "f102r1", "f102r2", "f102v2", "f102v1"]


def zl_sections():
    sec = {}
    for line in (ROOT / "data" / "ZL3b-n.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^<(f\d+[rv]\d*)>\s+<!.*\$I=(\w)", line)
        if m:
            sec[m.group(1)] = m.group(2)
    return sec


def hsv(arr):
    import cv2
    h = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
    return h[..., 1] / 255.0, h[..., 2] / 255.0


def page_trim(arr):
    """Drop the black scan background: bbox of pixels with V > 0.25 on rows/cols that are mostly bright."""
    _, v = hsv(arr)
    bright = v > 0.35
    rows = np.where(bright.mean(1) > 0.5)[0]
    cols = np.where(bright.mean(0) > 0.5)[0]
    if len(rows) < 10 or len(cols) < 10:
        return 0, 0, arr.shape[1], arr.shape[0]
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def masks(arr, P):
    s, v = hsv(arr)
    valid = v > P["V_MIN"]
    medS, medV = float(np.median(s[valid])), float(np.median(v[valid]))
    paint = (s > medS + P["PAINT_DS"]) & valid
    ink = (v < medV - P["INK_DV"]) & valid
    parch = np.median(arr[valid & ~paint & ~ink], axis=0).astype(np.uint8)
    return paint, ink, parch, medS, medV


def cc_boxes(mask):
    import cv2
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    return [tuple(int(t) for t in st[i]) for i in range(1, n)]  # x, y, w, h, area


def load_panel(fname, x0f, x1f):
    im = Image.open(SCANS / "pages" / fname).convert("RGB")
    W, H = im.size
    pan = im.crop((int(x0f * W), 0, int(x1f * W), H))
    arr = np.asarray(pan)
    tx0, ty0, tx1, ty1 = page_trim(arr)
    off = (int(x0f * W) + tx0, ty0)
    return arr[ty0:ty1, tx0:tx1], off, (W, H)


def save_crop(arr, box, path, P):
    x, y, w, h = box
    c = Image.fromarray(arr[y:y + h, x:x + w])
    c.thumbnail((P["CROP_SAVE_MAX"], P["CROP_SAVE_MAX"]))
    c.save(path)


def chroma_mask(arr, P):
    """CIELAB a*b* distance from the median parchment a*b* > DAB; returns (mask, L)."""
    import cv2
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0] * 100 / 255, lab[..., 1] - 128, lab[..., 2] - 128
    valid = L > 100 * P["V_MIN"]
    a0, b0 = float(np.median(A[valid])), float(np.median(B[valid]))
    return (np.hypot(A - a0, B - b0) > P["DAB"]) & valid, valid


def paint_components(arr, P):
    """Work-scale paint mask -> opened, dilated -> component boxes (work coords), scale, shape."""
    import cv2
    sc = P["WORK_H"] / arr.shape[0]
    ws = (max(1, int(arr.shape[1] * sc)), P["WORK_H"])
    small = cv2.resize(arr, ws, interpolation=cv2.INTER_AREA)
    pa, _ = chroma_mask(small, P)
    pa = cv2.morphologyEx(pa.astype(np.uint8), cv2.MORPH_OPEN,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (P["OPEN"], P["OPEN"])))
    m = cv2.dilate(pa, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (P["DIL"], P["DIL"])))
    return cc_boxes(m), sc, m.shape, ws


def herbal_crop(pid, fname, x0f, x1f, lines, P):
    arr, off, _ = load_panel(fname, x0f, x1f)
    arr = arr.copy()
    _, _, parch, _, _ = masks(arr, P)
    # text removal: inside the padded s45 line boxes, every non-paint pixel becomes parchment
    nlines = 0
    if lines:
        paint, _ = chroma_mask(arr, P)
        for ln in lines:
            bx0, by0, bx1, by1 = ln["bbox"]
            pad = int(P["TEXT_PAD"] * (by1 - by0))
            X0, Y0 = max(0, bx0 - off[0] - pad), max(0, by0 - off[1] - pad)
            X1, Y1 = min(arr.shape[1], bx1 - off[0] + pad), min(arr.shape[0], by1 - off[1] + pad)
            if X1 > X0 and Y1 > Y0:
                sub = arr[Y0:Y1, X0:X1]
                sub[~paint[Y0:Y1, X0:X1]] = parch
                nlines += 1
    boxes, sc, (Hs, Ws), _ = paint_components(arr, P)
    boxes = [b for b in boxes if b[2] <= P["MAX_FRAC"] * Ws and b[3] <= P["MAX_FRAC"] * Hs
             and b[2] * b[3] >= P["MIN_AREA"] * Hs * Ws
             and P["EDGE"] * Ws < b[0] + b[2] / 2 < (1 - P["EDGE"]) * Ws]
    if not boxes:
        return None
    big = max(b[4] for b in boxes)
    keep = [b for b in boxes if b[4] >= P["HERB_KEEP"] * big]
    x0 = min(b[0] for b in keep); y0 = min(b[1] for b in keep)
    x1 = max(b[0] + b[2] for b in keep); y1 = max(b[1] + b[3] for b in keep)
    box = (int(x0 / sc), int(y0 / sc), int((x1 - x0) / sc), int((y1 - y0) / sc))
    cid = f"H_{pid}"
    save_crop(arr, box, CROPS / f"{cid}.png", P)
    return dict(crop=cid, page=pid, kind="herbal", canvas=fname, n_text_lines_removed=nlines,
                bbox_canvas=[box[0] + off[0], box[1] + off[1], box[2], box[3]], n_components=len(keep),
                parch=[int(t) for t in parch], text_lines_source="s45 kraken line boxes" if lines else "none")


def pharma_crops(pid, fname, x0f, x1f, panel_no, P):
    arr, off, _ = load_panel(fname, x0f, x1f)
    _, _, parch, _, _ = masks(arr, P)
    boxes, sc, (Hs, Ws), ws = paint_components(arr, P)
    out = []
    for (x, y, w, h, a) in boxes:
        if w * h < P["MIN_AREA"] * Hs * Ws or min(w, h) < P["MIN_SIDE"] * Hs:
            continue
        if w > P["MAX_FRAC"] * Ws or h > P["MAX_FRAC"] * Hs:
            continue  # page edge / whole-page stain
        asp = h / max(w, 1)
        jar = ((asp >= P["JAR_ASPECT"]) and (h >= P["JAR_H"] * Hs)) or \
              ((asp >= P["JAR_ASPECT_EDGE"]) and (x + w / 2 < P["JAR_EDGE"] * Ws))
        out.append(dict(x=x, y=y, w=w, h=h, area=a, jar_like=bool(jar)))
    recs = []
    out.sort(key=lambda o: (o["y"], o["x"]))
    for i, o in enumerate(out):
        box = (int(o["x"] / sc), int(o["y"] / sc), int(o["w"] / sc), int(o["h"] / sc))
        cid = f"P_{pid}_p{panel_no}_{i:02d}"
        save_crop(arr, box, CROPS / f"{cid}.png", P)
        recs.append(dict(crop=cid, page=pid, kind="pharma", canvas=fname, panel=panel_no,
                         bbox_canvas=[box[0] + off[0], box[1] + off[1], box[2], box[3]],
                         bbox_panel_frac=[round(o["x"] / Ws, 4), round(o["y"] / Hs, 4),
                                          round(o["w"] / Ws, 4), round(o["h"] / Hs, 4)],
                         jar_like=o["jar_like"],
                         parch=[int(t) for t in parch]))
    # debug overview with crop indices
    from PIL import ImageDraw
    ov = Image.fromarray(arr).resize(ws)
    d = ImageDraw.Draw(ov)
    for r, o in zip(recs, out):
        col = "blue" if o["jar_like"] else "red"
        d.rectangle([o["x"], o["y"], o["x"] + o["w"], o["y"] + o["h"]], outline=col, width=3)
        d.text((o["x"] + 4, o["y"] + 4), r["crop"][-2:], fill=col)
    ov.save(OUT / "overview" / f"{pid}_p{panel_no}.png")
    return recs


def stage_crops(P):
    CROPS.mkdir(parents=True, exist_ok=True)
    (OUT / "overview").mkdir(parents=True, exist_ok=True)
    sec = zl_sections()
    recs = []
    composite_herbal = {}
    for fname, panels in PANELS.items():
        for pid, a, b, s in panels:
            if s == "H":
                composite_herbal[pid] = (fname, a, b)
    herbal_ids = sorted(p for p, s in sec.items() if s == "H")
    n_skip = []
    for pid in herbal_ids:
        js = S45 / f"{pid}.json"
        if js.exists():
            d = json.loads(js.read_text(encoding="utf-8"))
            r = herbal_crop(pid, d["file"], 0.0, 1.0, d.get("lines"), P)
        elif pid in composite_herbal:
            f, a, b = composite_herbal[pid]
            r = herbal_crop(pid, f, a, b, None, P)
        else:
            n_skip.append(pid)
            continue
        if r:
            recs.append(r)
    panel_no = {}
    for fname, panels in PANELS.items():
        for pid, a, b, s in panels:
            if s != "P":
                continue
            panel_no[pid] = panel_no.get(pid, 0) + 1
            recs.extend(pharma_crops(pid, fname, a, b, panel_no[pid], P))
    meta = dict(params=P, panels={k: v for k, v in PANELS.items()}, herbal_without_canvas=n_skip,
                n_herbal=sum(r["kind"] == "herbal" for r in recs),
                n_pharma=sum(r["kind"] == "pharma" for r in recs), crops=recs)
    (OUT / "crops.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"herbal crops {meta['n_herbal']} (no canvas: {len(n_skip)}), pharma crops {meta['n_pharma']}")
    for pid in PHARMA_IDS:
        cs = [r for r in recs if r["page"] == pid]
        print(f"  {pid}: {len(cs)} crops ({sum(r['jar_like'] for r in cs)} jar-like)")


def views(img):
    out = []
    for flip in (False, True):
        b = img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img
        for k in range(4):
            out.append(b.rotate(90 * k, expand=True))
    return out


def square(img, parch, size):
    w, h = img.size
    s = max(w, h)
    c = Image.new("RGB", (s, s), tuple(parch))
    c.paste(img, ((s - w) // 2, (s - h) // 2))
    return c.resize((size, size), Image.BICUBIC)


def stage_embed(P):
    import torch
    from transformers import AutoModel, SiglipModel
    meta = json.loads((OUT / "crops.json").read_text(encoding="utf-8"))
    recs = meta["crops"]
    dev = "cuda:0" if torch.cuda.is_available() else "cpu"
    dino = AutoModel.from_pretrained(str(MODELS / "dinov2-base"), use_safetensors=True).to(dev).eval()
    sig = SiglipModel.from_pretrained(str(MODELS / "siglip-base-patch16-224"), use_safetensors=True).to(dev).eval()
    norms = {"dino": ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), "siglip": ((0.5,) * 3, (0.5,) * 3)}
    E = {"dino": [], "siglip": []}
    S = P["EMB_SIZE"]
    with torch.no_grad():
        for r in recs:
            img = square(Image.open(CROPS / f"{r['crop']}.png").convert("RGB"), r["parch"], S)
            x = torch.from_numpy(np.stack([np.asarray(v, dtype=np.float32) / 255.0 for v in views(img)]))
            x = x.permute(0, 3, 1, 2).to(dev)
            for name in ("dino", "siglip"):
                m, s = norms[name]
                xn = (x - torch.tensor(m, device=dev).view(1, 3, 1, 1)) / torch.tensor(s, device=dev).view(1, 3, 1, 1)
                if name == "dino":
                    f = dino(pixel_values=xn).last_hidden_state[:, 0]
                else:
                    f = sig.get_image_features(pixel_values=xn)
                f = torch.nn.functional.normalize(f.float(), dim=-1).mean(0)
                E[name].append(torch.nn.functional.normalize(f, dim=-1).cpu().numpy())
    np.savez(OUT / "embeddings.npz", ids=np.array([r["crop"] for r in recs]),
             dino=np.stack(E["dino"]), siglip=np.stack(E["siglip"]))
    print(f"embedded {len(recs)} crops x 8 views on {dev}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["crops", "embed", "all"])
    a = ap.parse_args(argv)
    t = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.stage in ("crops", "all"):
        stage_crops(PARAMS)
    if a.stage in ("embed", "all"):
        stage_embed(PARAMS)
    print(f"elapsed {time.time() - t:.1f}s")


if __name__ == "__main__":
    main()
