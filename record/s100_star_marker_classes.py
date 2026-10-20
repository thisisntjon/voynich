#!/usr/bin/env python3
"""
s100_star_marker_classes.py — Automated Recipe Star-Marker Classes from the Yale Scans
======================================================================================
Run ID:        s100
Agent:         Argon (Antigravity session 8f895804-e797-4e9e-b1a6-c197860eb591)
Lead:          voynich-08 (b3796192)
Phase:         Phase 6 (Prerequisite for External Prediction X2)
Rules:         D-063, D-064, D-065

STRICT TEXT-INDEPENDENCE (D-065)
--------------------------------
This script NEVER loads, inspects, or uses any manuscript text, transliteration, token,
or character data. It operates exclusively on:
  1. Yale Beinecke MS 408 high-resolution RGB page scans in Quire 20:
     data/external/yale_scans/pages/182_103r.jpg .. 205_116v.jpg
     (Note: folios 109 and 110 are missing leaves in the manuscript; f103r..f116r are the
     23 recipe text pages; f116v is the final non-recipe charm/drawing page with no s45 JSON.)
  2. Text-free Kraken line bounding-box geometry from s45:
     runs/s45/pages/f103r.json .. f116r.json (reading ONLY 'file', 'size', 'pitch', and
     each line's geometric 'yb' and 'bbox').

CALIBRATION PAGES & FIXED SETTINGS (FROZEN BEFORE FULL RUN)
-----------------------------------------------------------
All detection, classical measurement (Method A), and GPU embedding + clustering (Method B)
settings were calibrated and fixed on ONLY 3 calibration pages (47 stars total):
  - f103r (19 stars: 7 filled, 12 hollow; 1 tailed [#19], 18 plain)
  - f107v (15 stars: 8 filled, 7 hollow; 15 tailed, 0 plain)
  - f114r (13 stars: 7 filled, 6 hollow; 13 tailed, 0 plain)

Fixed Settings:
  1. Physical Scan Scale:
     - sc = H / 3750.0 (normalizes across scan height H ~ 3750 px).
  2. Text-Block Left Margin Line xt(y):
     - Select wide left-starting text lines (bbox_w > 4.0 * pitch and bbox_x0 < 0.35 * W).
     - Split sorted line baselines yb into 4 vertical quartiles; fit linear xt(y) to the
       75th percentile of bbox_x0 in each quartile (100% immune to Kraken merging a left-margin
       star into a paragraph-initial line box).
  3. Rectified Left-Margin Strip & Star Peak Detection:
     - Extract horizontal offset strip u in [round(18*sc), round(155*sc)] to the left of xt(y),
       vertically bounded by y_top = max(trim_top + round(28*sc), round(min(yb) - 40*sc)) and
       y_bot = min(trim_bot - round(28*sc), round(max(yb) + 40*sc)), where trim_top/trim_bot
       are the page parchment bounds ((gray > 90).mean(axis=1) > 0.5).
     - Vertical background filter win_y = round(140*sc) | 1:
       bg_y = percentile_filter(gray, 75, size=(win_y, 1))
       dark = max(0, bg_y - gray), masked to 0 where gray < 65 (ignores scan borders & holes).
       grad_exc = max(0, sobel_mag - percentile_filter(sobel_mag, 50, size=(win_y, 1))).
       energy = dark + 0.25 * grad_exc (masked to 0 where gray < 65).
     - Star column track u_center(y) of width win_u = round(88*sc) interpolated between top-half
       and bottom-half horizontal energy peaks (regularized toward whole-page peak if |u_top - u_bot| > 35*sc).
     - Row profile prof_y(r) = 80th percentile of energy in [u_center(r) - win_u/2, u_center(r) + win_u/2],
       smoothed with Gaussian sigma = 18.0 * sc -> prof_smooth.
     - Greedy 1D non-maximum suppression (local maxima in window 11, min_dist = round(50*sc))
       with adaptive threshold thr = max(33.0, p20(prof_smooth) + 0.25 * (p95(prof_smooth) - p20(prof_smooth))).
     - Two-stage binary-ink (dark >= 20.0) centroid refinement in [-36*sc, +36*sc] then [-30*sc, +30*sc]
       around each detected peak -> star center (cy_r, cx_r).
  4. Method A — Classical Image Measurement (Thresholding & Morphology):
     - Filled vs Hollow:
       rg_exc = max(0, (R - G) - percentile_filter(R - G, 50, size=(win_y, 1))), masked at gray < 65.
       comb = dark + 2.0 * rg_exc.
       Inside core disc r <= 10.0 * sc:
         fill_ratio   = mean(comb >= 48.0)
         core_ink_val = mean(comb)
       Classification rule: filled_A = 'filled' (1) iff core_ink_val >= 55.0 else 'hollow' (0).
     - Tailed vs Plain:
       Horizontal/vertical median ridge filters on Gaussian-smoothed (sigma=1.0) gray:
         ridge_h = max(0, median_filter(gray_s, size=(3, 25)) - gray_s)
         ridge_v = max(0, median_filter(gray_s, size=(25, 3)) - gray_s)
         ridge_med = max(ridge_h, ridge_v), masked at gray < 65.
       Downward tail window y in [cy + round(48*sc), min(H_r, cy + round(88*sc), round(cy_{k+1} - 54*sc))],
       x in [cx - round(25*sc), cx + round(25*sc)]: count rows (bot_rows) with max(ridge_h) >= 14.5 and
       stroke width at ridge_h >= 12.0 of <= 15 px, stopping after 5 consecutive empty rows.
       If truncated by a close lower neighbor (4 <= win_t <= 12 and bot_rows >= max(4, int(0.8 * win_t))),
       bot_score = max(bot_rows, 11.0 * bot_rows / win_t); else bot_score = float(bot_rows).
       For the bottom star on a page (k == len(centers) - 1), also scan upward-left window
       y in [cy - round(52*sc) down to max(0, cy - round(92*sc), round(cy_{k-1} + 56*sc))],
       x in [cx - round(42*sc), cx + round(12*sc)] using ridge_med >= 14.5 -> top_rows.
       tail_rows = max(bot_rows, top_rows); tail_score = max(bot_score, float(top_rows)).
       Classification rule: tailed_A = 'tailed' (1) iff tail_score >= 9.5 else 'plain' (0).
     - Ray Count, Size, and Ink Colour/Density:
       ray_count     = number of circular local maxima (min separation 6 bins = 30 deg, height >= 0.25 * max)
                       in 72-bin polar angular profile of (dark >= 18.0) within annulus r in [13*sc, 42*sc],
                       circularly smoothed with Gaussian sigma = 1.2 bins.
       size_px       = pixel count of (dark >= 18.0) within r <= 46.0 * sc.
       equiv_diam_px = sqrt(4 * size_px / pi).
       ink_density   = mean((bg_y - gray) / max(bg_y, 1.0)) over star ink pixels (dark >= 18.0, r <= 42*sc).
       ink_redness   = mean(rg_exc) over star core + body ink pixels ((comb >= 30.0) & (r <= 42*sc)).
  5. Method B — GPU Image Embeddings with Unsupervised Clustering:
     - Backbone: Local DINOv2-base (data/external/models/dinov2-base) on CUDA (NVIDIA RTX 5080),
       batch size 32, calling torch.cuda.empty_cache() after every batch.
     - View 1 (Filled vs Hollow): Continuous column-normalized RGB core crop of radius round(11*sc)
       around (cy, cx), resized bicubically to 224x224 -> DINOv2 CLS embedding (768-D, L2-normalized)
       -> PCA(n_components=3, random_state=100) -> KMeans(n_clusters=2, n_init=20, random_state=100).
       Cluster with higher mean core_ink_val on the 3 calibration pages is anchored as 'filled' (1).
     - View 2 (Tailed vs Plain): Continuous threshold-free horizontal Difference-of-Gaussians
       dog_h = max(0, gaussian_filter(gray, (1.5, 9.0)) - gaussian_filter(gray, (1.0, 1.0)))
       in the Voronoi-safe tail window y in [cy + round(53*sc), min(H_r, cy + round(88*sc), round(cy_{k+1} - 53*sc))],
       x in [cx - round(22*sc), cx + round(22*sc)] (or upper-left window for k == len(centers) - 1 if higher sum),
       rendered continuously as clip(220 - 5 * dog_h, 0, 255) and resized bicubically to 224x224
       -> DINOv2 CLS embedding (768-D, L2-normalized) -> PCA(n_components=3, random_state=100)
       -> KMeans(n_clusters=2, n_init=20, random_state=100).
       Cluster with higher mean tail_score on the 3 calibration pages is anchored as 'tailed' (1).

PRE-REGISTERED DECISION RULE & VERDICT THRESHOLD
------------------------------------------------
  - Expected count: ~285 recipe paragraph stars across Quire 20 (per next-steps-external-prediction-2026-10-18.md).
  - Reliability rule: Each binary class ('filled_vs_hollow', 'tailed_vs_plain') is declared RELIABLE
    iff Cohen's kappa(Method A, Method B) >= 0.60 across the full Quire 20 star set.
"""

import ctypes
import datetime
import json
import math
import os
import pathlib
import subprocess
import sys

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import numpy as np
import torch
from PIL import Image
from scipy import ndimage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from transformers import AutoImageProcessor, AutoModel

torch.set_num_threads(2)

ROOT = pathlib.Path(__file__).resolve().parent
SCAN_DIR = ROOT / "data" / "external" / "yale_scans" / "pages"
S45_DIR = ROOT / "runs" / "s45" / "pages"
DINO_DIR = ROOT / "data" / "external" / "models" / "dinov2-base"
OUT_DIR = ROOT / "runs" / "s100"
CROPS_DIR = OUT_DIR / "crops"
TSV_PATH = OUT_DIR / "star_classes.tsv"
RESULTS_PATH = ROOT / "results_s100.txt"

CALIB_PAGES = ("f103r", "f107v", "f114r")
QUIRE20_RECIPE_PAGES = (
    "f103r", "f103v", "f104r", "f104v",
    "f105r", "f105v", "f106r", "f106v",
    "f107r", "f107v", "f108r", "f108v",
    # f109 and f110 are missing leaves in MS 408
    "f111r", "f111v", "f112r", "f112v",
    "f113r", "f113v", "f114r", "f114v",
    "f115r", "f115v", "f116r",
)
KAPPA_THRESHOLD = 0.60
EXPECTED_PARAGRAPHS = 285


def set_below_normal_priority() -> None:
    if sys.platform == "win32":
        try:
            BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS)
        except Exception:
            pass


def check_free_ram_gb(min_gb: float = 4.0) -> float:
    if sys.platform == "win32":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(stat)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        free_gb = stat.ullAvailPhys / (1024.0 ** 3)
        if free_gb < min_gb:
            raise RuntimeError(f"Insufficient free RAM: {free_gb:.2f} GB < {min_gb:.2f} GB required (D-064).")
        return free_gb
    return 16.0


def utc_date_stamp() -> str:
    git_date = pathlib.Path(r"C:\Program Files\Git\usr\bin\date.exe")
    if git_date.exists():
        out = subprocess.check_output([str(git_date), "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip()
        return out
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def count_star_rays(dark_patch: np.ndarray, dist_patch: np.ndarray, dy_patch: np.ndarray, dx_patch: np.ndarray, sc: float) -> int:
    annulus = (dist_patch >= 13.0 * sc) & (dist_patch <= 42.0 * sc)
    ink_ann = (dark_patch >= 18.0) & annulus
    if ink_ann.sum() < 15:
        return 0
    angles = np.arctan2(dy_patch, dx_patch)  # [-pi, pi]
    n_bins = 72
    bins = np.linspace(-np.pi, np.pi, n_bins + 1)
    prof = np.zeros(n_bins, dtype=np.float32)
    for b in range(n_bins):
        mask_b = annulus & (angles >= bins[b]) & (angles < bins[b + 1])
        if mask_b.any():
            prof[b] = float((dark_patch[mask_b] >= 18.0).mean())
    prof_s = ndimage.gaussian_filter1d(prof, sigma=1.2, mode="wrap")
    pmax = float(prof_s.max())
    if pmax <= 0.05:
        return 0
    # Circular local maxima with min distance of 6 bins (30 degrees)
    max_filt = ndimage.maximum_filter1d(prof_s, size=5, mode="wrap")
    cands = np.where((prof_s == max_filt) & (prof_s >= 0.25 * pmax))[0]
    order = cands[np.argsort(prof_s[cands])[::-1]]
    kept = []
    for c in order:
        if all(min(abs(int(c) - int(k)), n_bins - abs(int(c) - int(k))) >= 6 for k in kept):
            kept.append(int(c))
    return len(kept)


def process_page(pid: str):
    meta_path = S45_DIR / f"{pid}.json"
    d = json.loads(meta_path.read_text(encoding="utf-8"))
    scan_file = d["file"]
    im_pil = Image.open(SCAN_DIR / scan_file).convert("RGB")
    im = np.asarray(im_pil, dtype=np.float32)
    H, W, _ = im.shape
    sc = H / 3750.0
    pitch = float(d["pitch"])

    # 1. Text-block left boundary xt(y) from 4 quartiles (75th pct of wide left-starting line x0)
    left_lines = [
        ln for ln in d["lines"]
        if (ln["bbox"][2] - ln["bbox"][0]) > 4.0 * pitch and ln["bbox"][0] < 0.35 * W
    ]
    all_ybs = np.array([float(ln["yb"]) for ln in d["lines"]], dtype=float)
    ybs = np.array([float(ln["yb"]) for ln in left_lines], dtype=float)
    raw_x0 = np.array([float(ln["bbox"][0]) for ln in left_lines], dtype=float)
    qs = np.array_split(np.argsort(ybs), 4)
    qy = np.array([np.median(ybs[q]) for q in qs])
    qx = np.array([np.percentile(raw_x0[q], 75) for q in qs])
    slope, intercept = np.polyfit(qy, qx, 1)
    ys = np.arange(H, dtype=float)
    xt = intercept + slope * ys

    # 2. Rectified margin strip extraction
    gray_full = 0.299 * im[:, :, 0] + 0.587 * im[:, :, 1] + 0.114 * im[:, :, 2]
    bright_rows = np.where((gray_full > 90.0).mean(axis=1) > 0.5)[0]
    trim_top, trim_bot = int(bright_rows[0]), int(bright_rows[-1])
    u_min, u_max = int(round(18.0 * sc)), int(round(155.0 * sc))
    U = u_max - u_min
    y_top = max(trim_top + int(round(28.0 * sc)), int(round(ybs.min() - 40.0 * sc)))
    y_bot = min(trim_bot - int(round(28.0 * sc)), int(round(ybs.max() + 40.0 * sc)))
    H_r = y_bot - y_top

    rect = np.zeros((H_r, U, 3), dtype=np.float32)
    x_lefts = np.zeros(H_r, dtype=np.int32)
    for y in range(y_top, y_bot):
        x_right = int(round(xt[y])) - u_min
        x_left = max(0, x_right - U)
        x_lefts[y - y_top] = x_left
        rect[y - y_top] = im[y, x_left:x_left + U, :]

    gray = 0.299 * rect[:, :, 0] + 0.587 * rect[:, :, 1] + 0.114 * rect[:, :, 2]
    win_y = int(round(140.0 * sc)) | 1
    bg_y = ndimage.percentile_filter(gray, 75, size=(win_y, 1))
    dark = np.maximum(0.0, bg_y - gray)
    dark[gray < 65.0] = 0.0

    rg = rect[:, :, 0] - rect[:, :, 1]
    rg_bg = ndimage.percentile_filter(rg, 50, size=(win_y, 1))
    rg_exc = np.maximum(0.0, rg - rg_bg)
    rg_exc[gray < 65.0] = 0.0

    grad = np.hypot(ndimage.sobel(gray, axis=1), ndimage.sobel(gray, axis=0))
    grad_exc = np.maximum(0.0, grad - ndimage.percentile_filter(grad, 50, size=(win_y, 1)))
    energy = dark + 0.25 * grad_exc
    energy[gray < 65.0] = 0.0

    # 3. Star column center track & 1D peak detection
    win_u = int(round(88.0 * sc))
    u_all = int(np.argmax(ndimage.uniform_filter1d(energy.mean(axis=0), size=win_u)))
    u_top = int(np.argmax(ndimage.uniform_filter1d(energy[:H_r // 2].mean(axis=0), size=win_u)))
    u_bot = int(np.argmax(ndimage.uniform_filter1d(energy[H_r // 2:].mean(axis=0), size=win_u)))
    if abs(u_top - u_bot) > int(round(35.0 * sc)):
        u_top = int(round(0.5 * (u_top + u_all)))
        u_bot = int(round(0.5 * (u_bot + u_all)))
    u_center = np.linspace(u_top, u_bot, H_r)

    prof_y = np.array([
        np.percentile(
            energy[
                r,
                int(np.clip(round(u_center[r] - win_u / 2), 0, U - win_u)):
                int(np.clip(round(u_center[r] - win_u / 2), 0, U - win_u)) + win_u
            ],
            80,
        )
        for r in range(H_r)
    ])
    prof_smooth = ndimage.gaussian_filter1d(prof_y, sigma=18.0 * sc)
    local_max = prof_smooth == ndimage.maximum_filter1d(prof_smooth, size=11)
    cand_y = np.where(local_max)[0]
    cand_v = prof_smooth[cand_y]
    order = np.argsort(cand_v)[::-1]
    min_dist = int(round(50.0 * sc))
    bg_p20 = float(np.percentile(prof_smooth, 20))
    pk_p95 = float(np.percentile(prof_smooth, 95))
    thr = max(33.0, bg_p20 + 0.25 * (pk_p95 - bg_p20))

    kept = []
    for idx in order:
        y0, v0 = int(cand_y[idx]), float(cand_v[idx])
        if v0 >= thr and all(abs(y0 - yk) >= min_dist for yk, _ in kept):
            kept.append((y0, v0))
    kept.sort(key=lambda t: t[0])

    # 4. Binary-ink centroid refinement
    bin_ink = (dark >= 20.0).astype(np.float32)
    centers = []
    for py, pv in kept:
        u0 = int(np.clip(round(u_center[py] - win_u / 2), 0, U - win_u))
        sy0, sy1 = max(0, py - int(round(36.0 * sc))), min(H_r, py + int(round(36.0 * sc)))
        sx0, sx1 = max(0, u0 + 4), min(U, u0 + win_u - 4)
        sub_b = bin_ink[sy0:sy1, sx0:sx1]
        yy_s, xx_s = np.indices(sub_b.shape)
        cy_r = sy0 + float((yy_s * sub_b).sum() / (sub_b.sum() + 1e-6))
        cx_r = sx0 + float((xx_s * sub_b).sum() / (sub_b.sum() + 1e-6))

        sy0b, sy1b = max(0, int(round(cy_r - 30.0 * sc))), min(H_r, int(round(cy_r + 31.0 * sc)))
        sx0b, sx1b = max(0, int(round(cx_r - 30.0 * sc))), min(U, int(round(cx_r + 31.0 * sc)))
        sub_b2 = bin_ink[sy0b:sy1b, sx0b:sx1b]
        yy2, xx2 = np.indices(sub_b2.shape)
        cy_r = sy0b + float((yy2 * sub_b2).sum() / (sub_b2.sum() + 1e-6))
        cx_r = sx0b + float((xx2 * sub_b2).sum() / (sub_b2.sum() + 1e-6))
        centers.append((cy_r, cx_r, pv))

    # Auxiliary maps for Method A & Method B
    bg_rgb = np.stack([ndimage.percentile_filter(rect[:, :, c], 75, size=(win_y, 1)) for c in range(3)], axis=-1)
    norm_rgb = np.clip(215.0 - np.maximum(0.0, bg_rgb - rect), 0.0, 255.0)
    norm_rgb[gray < 65.0] = 215.0

    gray_s = ndimage.gaussian_filter(gray, sigma=1.0)
    ridge_h = np.maximum(0.0, ndimage.median_filter(gray_s, size=(3, 25)) - gray_s)
    ridge_v = np.maximum(0.0, ndimage.median_filter(gray_s, size=(25, 3)) - gray_s)
    ridge_med = np.maximum(ridge_h, ridge_v)
    ridge_h[gray < 65.0] = 0.0
    ridge_med[gray < 65.0] = 0.0

    # Continuous linear Difference-of-Gaussians map for Method B tail crops (threshold-free)
    g_s1 = ndimage.gaussian_filter(gray, sigma=(1.0, 1.0))
    g_s2 = ndimage.gaussian_filter(gray, sigma=(1.5, 9.0))
    dog_h = np.maximum(0.0, g_s2 - g_s1)
    dog_h[gray < 65.0] = 0.0

    page_records = []
    page_core_imgs = []
    page_tail_imgs = []

    for k, (cy_r, cx_r, pv) in enumerate(centers):
        cy, cx = int(round(cy_r)), int(round(cx_r))
        cy_page = int(round(y_top + cy_r))
        row_idx = int(np.clip(cy, 0, H_r - 1))
        cx_page = int(round(x_lefts[row_idx] + cx_r))

        # Nearest Kraken line index & yb (geometry only)
        nearest_line_idx = int(np.argmin(np.abs(all_ybs - cy_page))) + 1
        nearest_line_yb = float(all_ybs[nearest_line_idx - 1])

        # Audit crop from full scan (160x160 scaled by sc)
        half_crop = int(round(80.0 * sc))
        cy0, cy1 = max(0, cy_page - half_crop), min(H, cy_page + half_crop)
        cx0, cx1 = max(0, cx_page - half_crop), min(W, cx_page + half_crop)
        crop_rel = f"runs/s100/crops/{pid}_star{k+1:02d}.png"
        Image.fromarray(im[cy0:cy1, cx0:cx1].astype(np.uint8)).save(ROOT / crop_rel)

        # Method A: Filled vs Hollow, Ray Count, Size, Ink Density & Redness
        R_box = int(round(46.0 * sc))
        by0, by1 = max(0, cy - R_box), min(H_r, cy + R_box + 1)
        bx0, bx1 = max(0, cx - R_box), min(U, cx + R_box + 1)
        yy, xx = np.ogrid[by0:by1, bx0:bx1]
        dy_p = yy - cy_r
        dx_p = xx - cx_r
        dist = np.hypot(dy_p, dx_p)

        sd = dark[by0:by1, bx0:bx1]
        sr = rg_exc[by0:by1, bx0:bx1]
        sg = gray[by0:by1, bx0:bx1]
        sbg = bg_y[by0:by1, bx0:bx1]
        comb = sd + 2.0 * sr

        core_mask = dist <= (10.0 * sc)
        fill_ratio = float((comb[core_mask] >= 48.0).mean())
        core_ink_val = float(comb[core_mask].mean())
        filled_A = 1 if core_ink_val >= 55.0 else 0

        # Ray count
        ray_count = count_star_rays(sd, dist, dy_p, np.broadcast_to(dx_p, dist.shape), sc)

        # Size (area in px and equivalent diameter)
        body_ink_mask = (sd >= 18.0) & (dist <= 46.0 * sc)
        size_px = int(body_ink_mask.sum())
        equiv_diam_px = float(math.sqrt(4.0 * size_px / math.pi))

        # Ink optical density & redness
        ink_zone = (sd >= 18.0) & (dist <= 42.0 * sc)
        if ink_zone.any():
            ink_density = float(np.mean((sbg[ink_zone] - sg[ink_zone]) / np.maximum(sbg[ink_zone], 1.0)))
        else:
            ink_density = 0.0
        red_zone = (comb >= 30.0) & (dist <= 42.0 * sc)
        ink_redness = float(np.mean(sr[red_zone])) if red_zone.any() else 0.0

        # Method A: Tailed vs Plain
        y0_t = cy + int(round(48.0 * sc))
        y1_t = min(H_r, cy + int(round(88.0 * sc)))
        if k + 1 < len(centers):
            y1_t = min(y1_t, int(round(centers[k + 1][0] - 54.0 * sc)))
        x0_t, x1_t = max(0, cx - int(round(25.0 * sc))), min(U, cx + int(round(25.0 * sc)) + 1)
        bot_rows = 0
        empty_run = 0
        for ry in range(y0_t, y1_t):
            row = ridge_h[ry, x0_t:x1_t]
            if len(row) == 0:
                break
            rmax = float(row.max())
            if rmax >= 14.5:
                xs_hit = np.where(row >= 12.0)[0]
                if len(xs_hit) > 0 and (xs_hit[-1] - xs_hit[0]) <= 15:
                    bot_rows += 1
                empty_run = 0
            else:
                empty_run += 1
                if empty_run >= 5:
                    break
        win_t = max(0, y1_t - y0_t)
        bot_score = float(bot_rows)
        if 4 <= win_t <= 12 and bot_rows >= max(4, int(0.8 * win_t)):
            bot_score = max(bot_score, 11.0 * (bot_rows / float(win_t)))

        top_rows = 0
        if k == len(centers) - 1:
            y0_u = cy - int(round(52.0 * sc))
            y1_u = max(0, cy - int(round(92.0 * sc)))
            if k > 0:
                y1_u = max(y1_u, int(round(centers[k - 1][0] + 56.0 * sc)))
            x0_u, x1_u = max(0, cx - int(round(42.0 * sc))), min(U, cx + int(round(12.0 * sc)) + 1)
            empty_run = 0
            for ry in range(y0_u, y1_u, -1):
                row = ridge_med[ry, x0_u:x1_u]
                if len(row) == 0:
                    break
                if float(row.max()) >= 14.5:
                    top_rows += 1
                    empty_run = 0
                else:
                    empty_run += 1
                    if empty_run >= 5:
                        break
        tail_rows = int(max(bot_rows, top_rows))
        tail_score = float(max(bot_score, float(top_rows)))
        tailed_A = 1 if tail_score >= 9.5 else 0

        # Method B continuous crops (224x224)
        # 1) Core RGB crop
        rc = int(round(11.0 * sc))
        c_patch = norm_rgb[max(0, cy - rc):min(H_r, cy + rc + 1), max(0, cx - rc):min(U, cx + rc + 1)]
        core_pil = Image.fromarray(c_patch.astype(np.uint8)).resize((224, 224), Image.BICUBIC)
        page_core_imgs.append(core_pil)

        # 2) Continuous DoG tail-window crop
        y0_tb = cy + int(round(53.0 * sc))
        y1_tb = min(H_r, cy + int(round(88.0 * sc)))
        if k + 1 < len(centers):
            y1_tb = min(y1_tb, int(round(centers[k + 1][0] - 53.0 * sc)))
        x0_tb, x1_tb = max(0, cx - int(round(22.0 * sc))), min(U, cx + int(round(22.0 * sc)) + 1)
        patch_tb = dog_h[y0_tb:max(y0_tb + 1, y1_tb), x0_tb:x1_tb]
        if patch_tb.size == 0:
            patch_tb = np.zeros((35, 45), dtype=np.float32)
        if k == len(centers) - 1:
            y0_ub = max(0, cy - int(round(88.0 * sc)))
            if k > 0:
                y0_ub = max(y0_ub, int(round(centers[k - 1][0] + 55.0 * sc)))
            y1_ub = max(y0_ub + 1, cy - int(round(53.0 * sc)))
            x0_ub, x1_ub = max(0, cx - int(round(38.0 * sc))), min(U, cx + int(round(8.0 * sc)) + 1)
            patch_ub = dog_h[y0_ub:y1_ub, x0_ub:x1_ub]
            if patch_ub.sum() > patch_tb.sum():
                patch_tb = patch_ub
        vis_tb = np.clip(220.0 - 5.0 * patch_tb, 0.0, 255.0).astype(np.uint8)
        tail_pil = Image.fromarray(np.stack([vis_tb] * 3, axis=-1)).resize((224, 224), Image.BICUBIC)
        page_tail_imgs.append(tail_pil)

        page_records.append({
            "folio": pid,
            "star_idx": k + 1,
            "scan_file": scan_file,
            "cx_page": cx_page,
            "cy_page": cy_page,
            "crop_x0": cx0,
            "crop_y0": cy0,
            "crop_x1": cx1,
            "crop_y1": cy1,
            "nearest_line_idx": nearest_line_idx,
            "nearest_line_yb": round(nearest_line_yb, 1),
            "peak_energy": round(pv, 2),
            "fill_ratio": round(fill_ratio, 4),
            "core_ink_val": round(core_ink_val, 2),
            "tail_rows": tail_rows,
            "tail_score": round(tail_score, 2),
            "ray_count": ray_count,
            "size_px": size_px,
            "equiv_diam_px": round(equiv_diam_px, 2),
            "ink_density": round(ink_density, 4),
            "ink_redness": round(ink_redness, 2),
            "filled_A_num": filled_A,
            "tailed_A_num": tailed_A,
            "crop_path": crop_rel,
        })

    return page_records, page_core_imgs, page_tail_imgs


def embed_images_dinov2(imgs, batch_size: int = 32) -> np.ndarray:
    check_free_ram_gb(4.0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    proc = AutoImageProcessor.from_pretrained(str(DINO_DIR), local_files_only=True)
    model = AutoModel.from_pretrained(str(DINO_DIR), local_files_only=True).to(device).eval()
    embs = []
    with torch.no_grad():
        for i in range(0, len(imgs), batch_size):
            batch = imgs[i:i + batch_size]
            inp = proc(images=batch, return_tensors="pt").to(device)
            out = model(**inp).last_hidden_state[:, 0, :].detach().cpu().numpy()
            embs.append(out)
            if device == "cuda":
                torch.cuda.empty_cache()
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    X = np.vstack(embs)
    X_norm = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X_norm


def main() -> None:
    if RESULTS_PATH.exists():
        raise FileExistsError(f"Refusing to overwrite existing {RESULTS_PATH} (D-063 / binding rules).")

    set_below_normal_priority()
    free_ram_start = check_free_ram_gb(4.0)
    t_start = utc_date_stamp()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CROPS_DIR.mkdir(parents=True, exist_ok=True)

    all_records = []
    all_core_imgs = []
    all_tail_imgs = []
    per_page_counts = {}

    for pid in QUIRE20_RECIPE_PAGES:
        check_free_ram_gb(4.0)
        recs, c_imgs, t_imgs = process_page(pid)
        per_page_counts[pid] = len(recs)
        all_records.extend(recs)
        all_core_imgs.extend(c_imgs)
        all_tail_imgs.extend(t_imgs)

    # Assign global_idx 1..N
    for g_idx, r in enumerate(all_records, start=1):
        r["global_idx"] = g_idx

    # Method B: GPU Embeddings (DINOv2-base on RTX 5080) + PCA(3) + KMeans(2)
    emb_core = embed_images_dinov2(all_core_imgs, batch_size=32)
    pca_core = PCA(n_components=3, random_state=100).fit_transform(emb_core)
    km_core = KMeans(n_clusters=2, n_init=20, random_state=100).fit(pca_core)
    labs_core = km_core.labels_.copy()

    # Anchor cluster polarity using the 3 calibration pages ONLY
    calib_mask = np.array([r["folio"] in CALIB_PAGES for r in all_records], dtype=bool)
    core_vals = np.array([r["core_ink_val"] for r in all_records], dtype=float)
    if core_vals[calib_mask & (labs_core == 1)].mean() < core_vals[calib_mask & (labs_core == 0)].mean():
        labs_core = 1 - labs_core
        pca1_fill_sign = -1.0
    else:
        pca1_fill_sign = 1.0

    emb_tail = embed_images_dinov2(all_tail_imgs, batch_size=32)
    pca_tail = PCA(n_components=3, random_state=100).fit_transform(emb_tail)
    km_tail = KMeans(n_clusters=2, n_init=20, random_state=100).fit(pca_tail)
    labs_tail = km_tail.labels_.copy()

    tail_scores = np.array([r["tail_score"] for r in all_records], dtype=float)
    if tail_scores[calib_mask & (labs_tail == 1)].mean() < tail_scores[calib_mask & (labs_tail == 0)].mean():
        labs_tail = 1 - labs_tail
        pca1_tail_sign = -1.0
    else:
        pca1_tail_sign = 1.0

    for i, r in enumerate(all_records):
        fb = int(labs_core[i])
        tb = int(labs_tail[i])
        fa = int(r["filled_A_num"])
        ta = int(r["tailed_A_num"])
        r["filled_B_num"] = fb
        r["tailed_B_num"] = tb
        r["pca1_fill_B"] = round(float(pca1_fill_sign * pca_core[i, 0]), 4)
        r["pca1_tail_B"] = round(float(pca1_tail_sign * pca_tail[i, 0]), 4)
        r["filled_A"] = "filled" if fa == 1 else "hollow"
        r["filled_B"] = "filled" if fb == 1 else "hollow"
        r["filled_agree"] = 1 if fa == fb else 0
        r["tailed_A"] = "tailed" if ta == 1 else "plain"
        r["tailed_B"] = "tailed" if tb == 1 else "plain"
        r["tailed_agree"] = 1 if ta == tb else 0

    # Write runs/s100/star_classes.tsv
    tsv_cols = [
        "global_idx", "folio", "star_idx", "scan_file",
        "cx_page", "cy_page", "crop_x0", "crop_y0", "crop_x1", "crop_y1",
        "nearest_line_idx", "nearest_line_yb", "peak_energy",
        "fill_ratio", "core_ink_val", "tail_rows", "tail_score",
        "ray_count", "size_px", "equiv_diam_px", "ink_density", "ink_redness",
        "pca1_fill_B", "pca1_tail_B",
        "filled_A", "filled_B", "filled_agree",
        "tailed_A", "tailed_B", "tailed_agree",
        "crop_path",
    ]
    tsv_lines = ["\t".join(tsv_cols)]
    for r in all_records:
        tsv_lines.append("\t".join(str(r[c]) for c in tsv_cols))
    TSV_PATH.write_bytes(("\n".join(tsv_lines) + "\n").encode("utf-8"))

    # Compute agreement statistics
    fa_all = np.array([r["filled_A_num"] for r in all_records], dtype=int)
    fb_all = np.array([r["filled_B_num"] for r in all_records], dtype=int)
    ta_all = np.array([r["tailed_A_num"] for r in all_records], dtype=int)
    tb_all = np.array([r["tailed_B_num"] for r in all_records], dtype=int)

    kappa_fill_calib = float(cohen_kappa_score(fa_all[calib_mask], fb_all[calib_mask]))
    kappa_tail_calib = float(cohen_kappa_score(ta_all[calib_mask], tb_all[calib_mask]))
    kappa_fill_all = float(cohen_kappa_score(fa_all, fb_all))
    kappa_tail_all = float(cohen_kappa_score(ta_all, tb_all))

    cm_fill = confusion_matrix(fa_all, fb_all, labels=[1, 0])
    cm_tail = confusion_matrix(ta_all, tb_all, labels=[1, 0])

    fill_disagreements = [r for r in all_records if r["filled_agree"] == 0]
    tail_disagreements = [r for r in all_records if r["tailed_agree"] == 0]

    fill_reliable = kappa_fill_all >= KAPPA_THRESHOLD
    tail_reliable = kappa_tail_all >= KAPPA_THRESHOLD
    if fill_reliable and tail_reliable:
        verdict_str = (
            f"VERDICT: BOTH binary star-marker classes are RELIABLE "
            f"(filled_vs_hollow kappa = {kappa_fill_all:.4f} >= 0.60; "
            f"tailed_vs_plain kappa = {kappa_tail_all:.4f} >= 0.60; "
            f"N = {len(all_records)} stars across 23 Quire 20 recipe pages, zero text used)."
        )
    elif fill_reliable or tail_reliable:
        rel_name = "filled_vs_hollow" if fill_reliable else "tailed_vs_plain"
        unrel_name = "tailed_vs_plain" if fill_reliable else "filled_vs_hollow"
        verdict_str = (
            f"VERDICT: PARTIAL — {rel_name} is RELIABLE (kappa >= 0.60) but {unrel_name} is UNRELIABLE "
            f"(filled_vs_hollow kappa = {kappa_fill_all:.4f}; tailed_vs_plain kappa = {kappa_tail_all:.4f}; "
            f"N = {len(all_records)} stars)."
        )
    else:
        verdict_str = (
            f"VERDICT: NEITHER binary class met kappa >= 0.60 "
            f"(filled_vs_hollow kappa = {kappa_fill_all:.4f}; tailed_vs_plain kappa = {kappa_tail_all:.4f})."
        )

    t_end = utc_date_stamp()
    free_ram_end = check_free_ram_gb(1.0)

    # Build results_s100.txt report
    out = []
    out.append("=" * 88)
    out.append("RUN s100: RECIPE STAR-MARKER CLASSES MEASURED FROM THE YALE SCANS (PHASE 6 / X2 PREREQ)")
    out.append("=" * 88)
    out.append(f"Agent:               Argon (Antigravity session 8f895804-e797-4e9e-b1a6-c197860eb591)")
    out.append(f"Lead:                voynich-08 (b3796192)")
    out.append(f"Start Time (UTC):    {t_start}")
    out.append(f"End Time (UTC):      {t_end}")
    out.append(f"Free RAM (Start/End): {free_ram_start:.2f} GB / {free_ram_end:.2f} GB")
    out.append(f"GPU Device:          {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    out.append(f"Text Independence:   STRICT (Zero text/transliteration files read or inspected; D-065)")
    out.append("")
    out.append("PRE-REGISTERED THRESHOLDS & DECISION RULES (WRITTEN BEFORE FULL RUN)")
    out.append("-" * 88)
    out.append(f"  Calibration pages (3):     {', '.join(CALIB_PAGES)} (47 stars total)")
    out.append(f"  Expected paragraph count:  ~{EXPECTED_PARAGRAPHS} (workflow/research/next-steps-external-prediction-2026-10-18.md)")
    out.append(f"  Method A filled threshold: core_ink_val >= 55.0 inside r <= 10.0*sc (comb = dark + 2.0*rg_exc)")
    out.append(f"  Method A tailed threshold: tail_score >= 9.5 narrow-ridge rows in Voronoi-bounded tail window")
    out.append(f"  Method B classifier:       dinov2-base GPU CLS embeddings -> L2-norm -> PCA(3, seed=100) -> KMeans(2, n_init=20, seed=100)")
    out.append(f"  Reliability decision rule: Class is RELIABLE iff Cohen's kappa(Method A, Method B) >= {KAPPA_THRESHOLD:.2f}")
    out.append("")
    out.append("1. STAR COUNTS FOUND VS EXPECTED (~285)")
    out.append("-" * 88)
    out.append(f"  Total Quire 20 recipe stars detected: {len(all_records)} (expected ~{EXPECTED_PARAGRAPHS}; delta = {len(all_records) - EXPECTED_PARAGRAPHS:+d}, {100.0 * len(all_records) / EXPECTED_PARAGRAPHS:.1f}% of ~285)")
    out.append("  Note on Quire 20 leaves: folios 109 and 110 are missing leaves in MS 408; f103r..f116r are the")
    out.append("  23 recipe pages; f116v (205_116v.jpg) is the final charm/drawing page with 0 left-margin recipe stars.")
    out.append("")
    out.append("  Per-Folio Star Counts:")
    for pid in QUIRE20_RECIPE_PAGES:
        recs_p = [r for r in all_records if r["folio"] == pid]
        fa_p = sum(r["filled_A_num"] for r in recs_p)
        ta_p = sum(r["tailed_A_num"] for r in recs_p)
        fb_p = sum(r["filled_B_num"] for r in recs_p)
        tb_p = sum(r["tailed_B_num"] for r in recs_p)
        cal_tag = " [CALIBRATION PAGE]" if pid in CALIB_PAGES else ""
        out.append(
            f"    {pid:6s}: {len(recs_p):2d} stars | "
            f"Method A: {fa_p:2d} filled, {len(recs_p)-fa_p:2d} hollow; {ta_p:2d} tailed, {len(recs_p)-ta_p:2d} plain | "
            f"Method B: {fb_p:2d} filled, {len(recs_p)-fb_p:2d} hollow; {tb_p:2d} tailed, {len(recs_p)-tb_p:2d} plain{cal_tag}"
        )
    out.append("")
    out.append("2. PER-CLASS DISTRIBUTIONS & CONTINUOUS FEATURE SUMMARY (N = {})".format(len(all_records)))
    out.append("-" * 88)
    n_tot = len(all_records)
    n_fa1, n_fa0 = int(fa_all.sum()), int((1 - fa_all).sum())
    n_fb1, n_fb0 = int(fb_all.sum()), int((1 - fb_all).sum())
    n_ta1, n_ta0 = int(ta_all.sum()), int((1 - ta_all).sum())
    n_tb1, n_tb0 = int(tb_all.sum()), int((1 - tb_all).sum())
    out.append(f"  Filled vs Hollow:")
    out.append(f"    Method A (Classical):  filled = {n_fa1:3d} ({100.0*n_fa1/n_tot:5.1f}%), hollow = {n_fa0:3d} ({100.0*n_fa0/n_tot:5.1f}%)")
    out.append(f"    Method B (GPU DINOv2): filled = {n_fb1:3d} ({100.0*n_fb1/n_tot:5.1f}%), hollow = {n_fb0:3d} ({100.0*n_fb0/n_tot:5.1f}%)")
    out.append(f"  Tailed vs Plain:")
    out.append(f"    Method A (Classical):  tailed = {n_ta1:3d} ({100.0*n_ta1/n_tot:5.1f}%), plain  = {n_ta0:3d} ({100.0*n_ta0/n_tot:5.1f}%)")
    out.append(f"    Method B (GPU DINOv2): tailed = {n_tb1:3d} ({100.0*n_tb1/n_tot:5.1f}%), plain  = {n_tb0:3d} ({100.0*n_tb0/n_tot:5.1f}%)")
    out.append("")
    out.append("  4-Way Joint Subclass Distribution (filled x tailed):")
    for label_src, f_arr, t_arr in [("Method A", fa_all, ta_all), ("Method B", fb_all, tb_all)]:
        ft = int(((f_arr == 1) & (t_arr == 1)).sum())
        fp = int(((f_arr == 1) & (t_arr == 0)).sum())
        ht = int(((f_arr == 0) & (t_arr == 1)).sum())
        hp = int(((f_arr == 0) & (t_arr == 0)).sum())
        out.append(
            f"    {label_src:8s}: filled+tailed={ft:3d} ({100.0*ft/n_tot:4.1f}%), "
            f"filled+plain={fp:3d} ({100.0*fp/n_tot:4.1f}%), "
            f"hollow+tailed={ht:3d} ({100.0*ht/n_tot:4.1f}%), "
            f"hollow+plain={hp:3d} ({100.0*hp/n_tot:4.1f}%)"
        )
    out.append("")
    out.append("  Continuous Measured Features Across All Stars:")
    for feat in ["fill_ratio", "core_ink_val", "tail_rows", "tail_score", "ray_count", "size_px", "equiv_diam_px", "ink_density", "ink_redness"]:
        vals = np.array([float(r[feat]) for r in all_records], dtype=float)
        q25, q50, q75 = np.percentile(vals, [25, 50, 75])
        out.append(
            f"    {feat:14s}: mean={vals.mean():8.3f}, sd={vals.std():8.3f}, "
            f"median={q50:8.3f}, IQR=[{q25:8.3f}, {q75:8.3f}], min={vals.min():8.3f}, max={vals.max():8.3f}"
        )
    out.append("")
    out.append("3. INTER-METHOD AGREEMENT (COHEN'S KAPPA & CONFUSION MATRICES)")
    out.append("-" * 88)
    out.append(f"  Calibration Set Only (3 pages: f103r, f107v, f114r; n = {int(calib_mask.sum())}):")
    out.append(f"    filled_vs_hollow: Cohen's kappa = {kappa_fill_calib:.4f}, agreement = {100.0 * (fa_all[calib_mask] == fb_all[calib_mask]).mean():.1f}%")
    out.append(f"    tailed_vs_plain:  Cohen's kappa = {kappa_tail_calib:.4f}, agreement = {100.0 * (ta_all[calib_mask] == tb_all[calib_mask]).mean():.1f}%")
    out.append("")
    out.append(f"  Full Quire 20 Set (23 recipe pages; N = {n_tot}):")
    out.append(
        f"    filled_vs_hollow: Cohen's kappa = {kappa_fill_all:.4f}, "
        f"agreement = {n_tot - len(fill_disagreements)}/{n_tot} ({100.0 * (n_tot - len(fill_disagreements)) / n_tot:.2f}%) "
        f"-> {'RELIABLE (kappa >= 0.60)' if fill_reliable else 'UNRELIABLE (kappa < 0.60)'}"
    )
    out.append(
        f"      Confusion Matrix [A\\B] (rows=Method A, cols=Method B): "
        f"A_filled/B_filled={cm_fill[0,0]}, A_filled/B_hollow={cm_fill[0,1]}, "
        f"A_hollow/B_filled={cm_fill[1,0]}, A_hollow/B_hollow={cm_fill[1,1]}"
    )
    out.append(
        f"    tailed_vs_plain:  Cohen's kappa = {kappa_tail_all:.4f}, "
        f"agreement = {n_tot - len(tail_disagreements)}/{n_tot} ({100.0 * (n_tot - len(tail_disagreements)) / n_tot:.2f}%) "
        f"-> {'RELIABLE (kappa >= 0.60)' if tail_reliable else 'UNRELIABLE (kappa < 0.60)'}"
    )
    out.append(
        f"      Confusion Matrix [A\\B] (rows=Method A, cols=Method B): "
        f"A_tailed/B_tailed={cm_tail[0,0]}, A_tailed/B_plain={cm_tail[0,1]}, "
        f"A_plain/B_tailed={cm_tail[1,0]}, A_plain/B_plain={cm_tail[1,1]}"
    )
    out.append("")
    out.append("4. LIST OF DISAGREEMENTS BETWEEN METHOD A AND METHOD B")
    out.append("-" * 88)
    out.append(f"  4a. Filled vs Hollow Disagreements (n = {len(fill_disagreements)} of {n_tot}):")
    if not fill_disagreements:
        out.append("      None (100% agreement).")
    else:
        for r in fill_disagreements:
            out.append(
                f"      global_idx={r['global_idx']:3d} {r['folio']} #{r['star_idx']:2d} "
                f"(cx={r['cx_page']}, cy={r['cy_page']}): "
                f"filled_A={r['filled_A']:6s}, filled_B={r['filled_B']:6s} | "
                f"fill_ratio={r['fill_ratio']:.3f}, core_ink_val={r['core_ink_val']:.1f}, "
                f"ink_redness={r['ink_redness']:.1f}, pca1_fill_B={r['pca1_fill_B']:+.3f}"
            )
    out.append("")
    out.append(f"  4b. Tailed vs Plain Disagreements (n = {len(tail_disagreements)} of {n_tot}):")
    if not tail_disagreements:
        out.append("      None (100% agreement).")
    else:
        for r in tail_disagreements:
            out.append(
                f"      global_idx={r['global_idx']:3d} {r['folio']} #{r['star_idx']:2d} "
                f"(cx={r['cx_page']}, cy={r['cy_page']}): "
                f"tailed_A={r['tailed_A']:6s}, tailed_B={r['tailed_B']:6s} | "
                f"tail_rows={r['tail_rows']:2d}, tail_score={r['tail_score']:5.1f}, "
                f"pca1_tail_B={r['pca1_tail_B']:+.3f}"
            )
    out.append("")
    out.append("5. FINAL VERDICT")
    out.append("-" * 88)
    out.append(f"  {verdict_str}")
    out.append("=" * 88)

    RESULTS_PATH.write_bytes(("\n".join(out) + "\n").encode("utf-8"))
    print("\n".join(out))


if __name__ == "__main__":
    main()
