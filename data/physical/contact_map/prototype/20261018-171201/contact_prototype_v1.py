#!/usr/bin/env python
"""Phase 7.4 part 1 (D-069): leaf contact / offset / stain map -- PROTOTYPE ONLY.

Not pre-registered, not a frozen run, files no claim.  It exists so the lead can judge whether the
method can pass a known-answer gate before the full-run design is frozen in D-066.
Design notes, data sources and licences: data/physical/contact_map/README.md.

Question: which page surfaces touched each other in an earlier binding, from physical evidence alone
(no text, no transliteration, no section labels are read).

Signals, each scored for every ordered pair of page surfaces (src -> rcv) on the GPU:
  O  mirrored pigment offset: src's own paint (CIELAB chroma channels green / blue / red) mirrored
     about the gutter (horizontal flip) against rcv's FAINT pigment ("ghost") with rcv's own strong
     paint and ink masked out; multichannel normalised cross-correlation, max over +-MAX_SHIFT px.
  T  stain continuity: band-passed parchment luminance (text and paint removed by a median filter,
     side-mean subtracted), src mirrored against rcv, same NCC.
  U  gutter continuity: paint-mass profile along the gutter strip of each page (drawings that cross
     the fold of an opened bifolio, e.g. 78v|81r streams); 1-D NCC, max over +-MAX_SHIFT.
Geometry: two facing surfaces touch mirror-wise about the fold, so the contact transform is a
horizontal flip (gutter onto gutter).  Controls: the same scores with a 180-degree rotation and with
no flip (geometries a contact cannot produce).  Same-leaf pairs (recto vs verso of one leaf) are not
candidates (show-through has the same mirror geometry) and are reported only as a control.

Known answers (Layfield & Davis 2026, Digital Medievalist 19, CC BY 4.0, doi:10.4000/16k0a):
10v|15r splash stain, 33v|40r blue petals, 58v|65r green leaf, 76v|83r nymph's arm in the upper
gutter, 78v|81r streams crossing the gutter.  All five are inner faces of one bifolio (singulion
contact), so they are known-answer checks of the scorer, not discoveries.

Run (project root; scans are untrusted downloads, so isolated mode):
    python -I tools/physical/contact_prototype.py [--pages f10v,f15r,...] [--out DIR]
Resources: 1 CPU thread at BelowNormal priority, GPU memory capped at 3.5 GB (aborts if the GPU has
< 4.5 GB free or the machine < 4 GB free RAM).  Never overwrites: output dir is new (stamped).
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "vkb" / "vkb.sqlite"
OUT_BASE = ROOT / "data" / "physical" / "contact_map" / "prototype"

P = dict(
    DRAFT_DIV=8,          # JPEG draft downscale (about 370 x 470 px)
    WORK_W=160, WORK_H=224,
    MAX_SHIFT=16,         # +-px lag window at work scale (~10% of width)
    V_MIN=0.25,           # valid parchment: L > 25 (0..100)
    DAB_STRONG=16.0,      # chroma distance from parchment = own strong paint
    GHOST_CAP=12.0,       # ghost channel clipped here (faint pigment only)
    STRONG_DILATE=3,      # px dilation of rcv's own strong paint before masking
    INK_DL=22.0,          # ink: L below page median by this much
    HP_SIGMA=20.0,        # high-pass for ghost maps (removes broad tint gradients)
    STAIN_MED=9, STAIN_LO=2.0, STAIN_HI=25.0,
    GUTTER_FRAC=0.08,     # gutter strip width (fraction of page width)
    PROF_SIGMA=2.0,
    GPU_MEM_FRAC_GB=3.5,
)

# ~42 surfaces: quire B whole, outer bifolios of E, H-1/H-2, M-2/M-3/M-4 -- every known link,
# its conjugate outer faces, and 15 current facing pairs.
SUBSET42 = ("f9r f9v f10r f10v f11r f11v f13r f13v f14r f14v f15r f15v f16r f16v "
            "f33r f33v f34r f34v f39r f39v f40r f40v "
            "f57r f57v f58r f58v f65r f65v f66r f66v "
            "f76r f76v f77r f77v f78r f78v f81r f81v f82r f82v f83r f83v").split()

KNOWN_LINKS = [  # (left surface, right surface, evidence as described by Layfield & Davis 2026)
    ("f10v", "f15r", "splashed stain (sec. 7)"),
    ("f33v", "f40r", "blue petals (sec. 7)"),
    ("f58v", "f65r", "bit of green leaf (sec. 7)"),
    ("f76v", "f83r", "nymph's right arm in the upper gutter (sec. 7)"),
    ("f78v", "f81r", "two streams crossing the centre gutter (sec. 6)"),
]


# ----------------------------------------------------------------------------------- preflight
def below_normal():
    if os.name == "nt":
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    else:
        os.nice(5)


def free_ram_gb():
    import psutil
    return psutil.virtual_memory().available / 2**30


def gpu_free_gb():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=30).stdout.strip().splitlines()[0]
    used, total = (float(x) for x in out.split(","))
    return (total - used) / 1024, used / 1024, total / 1024


# ----------------------------------------------------------------------------------- page table
def folio_key(f):
    m = re.match(r"^f(\d+)([rv])(\d*)$", f)
    return (int(m.group(1)), m.group(2), m.group(3)) if m else None


def load_folios():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    rows = con.execute("select folio, quire, bifolio, conjugate, image_path from folios").fetchall()
    con.close()
    return {r[0]: dict(folio=r[0], quire=r[1], bifolio=r[2], conjugate=r[3], image=r[4]) for r in rows}


def current_facing(folios):
    """(Nv, next existing leaf r) in the current foliation order; foldout sub-panels skipped."""
    leaves = sorted({folio_key(f)[0] for f in folios if folio_key(f) and not folio_key(f)[2]})
    pairs = []
    for a, b in zip(leaves, leaves[1:]):
        if f"f{a}v" in folios and f"f{b}r" in folios:
            pairs.append((f"f{a}v", f"f{b}r"))
    return pairs


# ----------------------------------------------------------------------------------- features
def srgb_to_lab(rgb):
    c = rgb.astype(np.float32) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    return L, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])


def page_trim(arr):
    v = arr.max(axis=2) / 255.0
    bright = v > 0.35
    rows = np.where(bright.mean(1) > 0.5)[0]
    cols = np.where(bright.mean(0) > 0.5)[0]
    if len(rows) < 10 or len(cols) < 10:
        return arr
    return arr[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]


def features(path, side):
    im = Image.open(path)
    im.draft("RGB", (im.width // P["DRAFT_DIV"], im.height // P["DRAFT_DIV"]))
    arr = page_trim(np.asarray(im.convert("RGB")))
    arr = np.asarray(Image.fromarray(arr).resize((P["WORK_W"], P["WORK_H"]), Image.BOX))
    L, A, B = srgb_to_lab(arr)
    valid = L > 100 * P["V_MIN"]
    a0, b0 = float(np.median(A[valid])), float(np.median(B[valid]))
    Lmed = float(np.median(L[valid]))
    chans = np.stack([np.maximum(a0 - A, 0), np.maximum(b0 - B, 0), np.maximum(A - a0, 0)])  # green, blue, red
    dab = np.hypot(A - a0, B - b0)
    strong = (dab > P["DAB_STRONG"]) & valid
    ink = (L < Lmed - P["INK_DL"]) & valid
    # source: own strong paint, continuous
    src = chans * strong[None]
    # receiver ghost: faint pigment, own paint/ink masked, high-passed
    block = ndimage.binary_dilation(strong | ink, iterations=P["STRONG_DILATE"]) | ~valid
    ghost = np.minimum(chans, P["GHOST_CAP"])
    ghost = np.stack([g - ndimage.gaussian_filter(g, P["HP_SIGMA"]) for g in ghost]) * (~block)[None]
    # stain: parchment luminance with text/paint replaced, band-passed, darker = positive
    Lf = np.where(block, Lmed, L)
    Lbg = ndimage.median_filter(Lf, size=P["STAIN_MED"])
    stain = -(ndimage.gaussian_filter(Lbg, P["STAIN_LO"]) - ndimage.gaussian_filter(Lbg, P["STAIN_HI"]))
    stain = stain * valid
    # gutter profile: paint mass in the gutter strip (recto: left edge, verso: right edge)
    gw = max(2, int(P["GUTTER_FRAC"] * P["WORK_W"]))
    pm = (chans * strong[None]).sum(0)
    strip = pm[:, :gw] if side == "r" else pm[:, -gw:]
    prof = ndimage.gaussian_filter1d(strip.sum(1), P["PROF_SIGMA"])
    return dict(src=src.astype(np.float32), ghost=ghost.astype(np.float32), stain=stain.astype(np.float32),
                prof=prof.astype(np.float32), valid=valid, rgb=arr, strong_frac=float(strong.mean()))


# ----------------------------------------------------------------------------------- GPU scoring
def ncc_matrix(torch, S, G, M):
    """S, G: [N,C,H,W] float32 (already geometry-transformed S).  Returns [N,N] max-over-lag NCC
    of S_i against G_j (lags |dy|,|dx| <= M), normalised by the global norms."""
    dev = "cuda"
    N, C, H, W = S.shape
    S = S - S.mean(dim=(2, 3), keepdim=True)
    G = G - G.mean(dim=(2, 3), keepdim=True)
    ns = S.flatten(1).norm(dim=1).clamp_min(1e-6)
    ng = G.flatten(1).norm(dim=1).clamp_min(1e-6)
    Hp, Wp = H + 2 * M, W + 2 * M
    FS = torch.fft.rfft2(S.to(dev), s=(Hp, Wp))
    FG = torch.fft.rfft2(G.to(dev), s=(Hp, Wp))
    out = torch.empty(N, N, device=dev)
    idx_y = torch.cat([torch.arange(0, M + 1), torch.arange(Hp - M, Hp)]).to(dev)
    idx_x = torch.cat([torch.arange(0, M + 1), torch.arange(Wp - M, Wp)]).to(dev)
    for i in range(N):
        r = torch.fft.irfft2((FS[i:i + 1].conj() * FG).sum(1), s=(Hp, Wp))  # [N,Hp,Wp]
        r = r.index_select(1, idx_y).index_select(2, idx_x)
        out[i] = r.flatten(1).max(1).values
    return (out / (ns.to(dev)[:, None] * ng.to(dev)[None, :])).cpu().numpy()


def ncc_1d(torch, a, b, M):
    a = a - a.mean(1, keepdim=True)
    b = b - b.mean(1, keepdim=True)
    na, nb = a.norm(dim=1).clamp_min(1e-6), b.norm(dim=1).clamp_min(1e-6)
    n = a.shape[1] + 2 * M
    Fa, Fb = torch.fft.rfft(a.cuda(), n=n), torch.fft.rfft(b.cuda(), n=n)
    r = torch.fft.irfft(Fa.conj()[:, None, :] * Fb[None, :, :], n=n)  # [N,N,n]
    idx = torch.cat([torch.arange(0, M + 1), torch.arange(n - M, n)]).cuda()
    m = r.index_select(2, idx).max(2).values
    return (m / (na.cuda()[:, None] * nb.cuda()[None, :])).cpu().numpy()


# ----------------------------------------------------------------------------------- evaluation
def zscore(Mx, cand):
    v = Mx[cand]
    return (Mx - v.mean()) / (v.std() + 1e-9)


def rank_of(score_row, cand_row, j):
    """1-based rank of column j among candidate columns (ties counted against j)."""
    s = score_row[cand_row]
    return int((s >= score_row[j]).sum())


def auc(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    return float(((a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default=",".join(SUBSET42))
    ap.add_argument("--out", default=None)
    ap.add_argument("--perm", type=int, default=2000, help="random-pair permutations for the rank null")
    a = ap.parse_args(argv)
    t0 = time.time()
    below_normal()
    ram = free_ram_gb()
    gfree, gused, gtot = gpu_free_gb()
    print(f"preflight: free RAM {ram:.1f} GB; GPU used {gused:.1f}/{gtot:.1f} GB, free {gfree:.1f} GB")
    if ram < 4.0:
        sys.exit("ABORT: free RAM < 4 GB")
    if gfree < P["GPU_MEM_FRAC_GB"] + 1.0:
        sys.exit("ABORT: GPU free memory < cap + 1 GB")
    import torch
    torch.set_num_threads(1)
    torch.cuda.set_per_process_memory_fraction(P["GPU_MEM_FRAC_GB"] / gtot)

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = Path(a.out) if a.out else OUT_BASE / stamp
    out.mkdir(parents=True, exist_ok=False)

    folios = load_folios()
    pages = [p for p in a.pages.split(",") if p]
    missing = [p for p in pages if p not in folios or not folios[p]["image"]]
    if missing:
        sys.exit(f"ABORT: no image for {missing}")
    N = len(pages)
    print(f"{N} surfaces; extracting features (1 CPU thread)")
    feats, hashes = [], {}
    for p in pages:
        path = ROOT / folios[p]["image"]
        hashes[p] = hashlib.sha256(path.read_bytes()).hexdigest()
        feats.append(features(path, folio_key(p)[1]))
    t_feat = time.time() - t0

    # side-mean subtraction for stain (systematic scan/lighting pattern per recto/verso)
    sides = np.array([folio_key(p)[1] for p in pages])
    st = np.stack([f["stain"] for f in feats])
    for s in "rv":
        st[sides == s] -= st[sides == s].mean(0, keepdims=True)

    src = torch.from_numpy(np.stack([f["src"] for f in feats]))
    gho = torch.from_numpy(np.stack([f["ghost"] for f in feats]))
    stn = torch.from_numpy(st[:, None])
    prof = torch.from_numpy(np.stack([f["prof"] for f in feats]))
    geo = {"hflip": lambda x: torch.flip(x, dims=[-1]),
           "rot180": lambda x: torch.flip(x, dims=[-1, -2]),
           "none": lambda x: x}
    M = P["MAX_SHIFT"]
    torch.cuda.reset_peak_memory_stats()
    t1 = time.time()
    O = {g: ncc_matrix(torch, f(src), gho, M) for g, f in geo.items()}
    T = {g: ncc_matrix(torch, f(stn), stn, M) for g, f in geo.items()}
    U = ncc_1d(torch, prof, prof, M)
    U_rev = ncc_1d(torch, prof, torch.flip(prof, dims=[1]), M)  # control: one profile upside down
    torch.cuda.synchronize()
    t_gpu = time.time() - t1
    peak = torch.cuda.max_memory_allocated() / 2**30

    leaf = np.array([folio_key(p)[0] for p in pages])
    cand = (leaf[:, None] != leaf[None, :])  # excludes self and same leaf
    iu = np.triu(cand, 1)

    def sym(Mx):
        return Mx + Mx.T

    comps = {"O_offset": sym(O["hflip"]), "T_stain": sym(T["hflip"]), "U_gutter": sym(U)}
    ctrl = {"O_offset": sym(O["rot180"]), "T_stain": sym(T["rot180"]), "U_gutter": sym(U_rev)}
    comps["combined"] = sum(zscore(v, iu) for v in comps.values())
    ctrl["combined"] = sum(zscore(ctrl[k], iu) for k in ("O_offset", "T_stain", "U_gutter"))

    pos = {p: i for i, p in enumerate(pages)}
    facing = [(x, y) for x, y in current_facing(folios) if x in pos and y in pos]
    known = [(x, y, e) for x, y, e in KNOWN_LINKS if x in pos and y in pos]
    conj_outer = []  # conjugate outer faces (Xr, Yv): same sheet, never in contact as a singulion
    for x, y, _ in known:
        xr, yv = x[:-1] + "r", y[:-1] + "v"
        if xr in pos and yv in pos:
            conj_outer.append((xr, yv))
    facing_set = {tuple(sorted((pos[x], pos[y]))) for x, y in facing}
    known_set = {tuple(sorted((pos[x], pos[y]))) for x, y, _ in known}
    conj_set = {tuple(sorted((pos[x], pos[y]))) for x, y in conj_outer}

    res = dict(stamp=stamp, pages=pages, n=N, params=P, image_sha256=hashes, preflight=dict(
        free_ram_gb=ram, gpu_used_gb=gused, gpu_free_gb=gfree), timing_s=dict(
        features=t_feat, gpu=t_gpu, total=None), gpu_peak_alloc_gb=peak, n_candidates_per_page=None,
        known=[], facing_vs_random={}, conjugate_outer=[], same_leaf={})
    ncand = cand.sum(1)
    res["n_candidates_per_page"] = dict(min=int(ncand.min()), max=int(ncand.max()))

    def ranks_for(Sx, x, y, exclude_facing=False):
        i, j = pos[x], pos[y]
        ci, cj = cand[i].copy(), cand[j].copy()
        if exclude_facing:
            for (u, v) in facing_set:
                if (u, v) != tuple(sorted((i, j))):
                    if u == i: ci[v] = False
                    if v == i: ci[u] = False
                    if u == j: cj[v] = False
                    if v == j: cj[u] = False
        r1, r2 = rank_of(Sx[i], ci, j), rank_of(Sx[j], cj, i)
        vals = Sx[iu]
        g = int((vals >= Sx[i, j]).sum())
        return dict(rank_from_left=r1, rank_from_right=r2, worst=max(r1, r2), best=min(r1, r2),
                    global_rank=g, global_of=int(iu.sum()), n_cand_left=int(ci.sum()))

    for x, y, e in known:
        row = dict(link=f"{x}|{y}", evidence=e, currently_facing=tuple(sorted((pos[x], pos[y]))) in facing_set)
        for k, Sx in comps.items():
            row[k] = ranks_for(Sx, x, y)
            row[k + "_excl_current"] = ranks_for(Sx, x, y, exclude_facing=True)
            row[k + "_control_rot"] = ranks_for(ctrl[k], x, y)
        row["raw_O_hflip_vs_rot180_vs_none"] = [float(O[g][pos[x], pos[y]] + O[g][pos[y], pos[x]]) for g in geo]
        res["known"].append(row)

    # random-pair rank null: chance that a random candidate partner is in the top-5 = 5/n_cand
    rng = np.random.default_rng(20261018)
    for k, Sx in comps.items():
        f_ = [Sx[u, v] for (u, v) in facing_set]
        knownv = [Sx[u, v] for (u, v) in known_set]
        conjv = [Sx[u, v] for (u, v) in conj_set]
        other = [Sx[u, v] for u, v in zip(*np.where(iu)) if (u, v) not in facing_set | known_set | conj_set]
        # top-5 null for the known links: random partner pairs, same left pages
        top5_known = sum(1 for r in res["known"] if r[k]["worst"] <= 5)
        null = []
        lefts = [pos[x] for x, _, _ in known]
        for _ in range(a.perm):
            c = 0
            for i in lefts:
                js = np.where(cand[i])[0]
                j = rng.choice(js)
                ri = rank_of(Sx[i], cand[i], j)
                rj = rank_of(Sx[j], cand[j], i)
                c += max(ri, rj) <= 5
            null.append(c)
        null = np.array(null)
        res["facing_vs_random"][k] = dict(
            n_facing=len(f_), n_random=len(other),
            facing_mean=float(np.mean(f_)) if f_ else None, facing_median=float(np.median(f_)) if f_ else None,
            random_mean=float(np.mean(other)), random_median=float(np.median(other)),
            random_p95=float(np.percentile(other, 95)),
            auc_facing_vs_random=auc(f_, other), auc_known_vs_random=auc(knownv, other),
            auc_conjouter_vs_random=auc(conjv, other),
            known_top5_both_ends=top5_known,
            null_top5_both_ends_mean=float(null.mean()),
            p_known_top5=float(((null >= top5_known).sum() + 1) / (len(null) + 1)))
    for x, y in conj_outer:
        res["conjugate_outer"].append({"pair": f"{x}|{y}", **{k: ranks_for(Sx, x, y) for k, Sx in comps.items()}})
    # same-leaf show-through control (not candidates): mean raw O hflip vs random
    sl = [(i, j) for i in range(N) for j in range(N) if i < j and leaf[i] == leaf[j]]
    res["same_leaf"] = dict(n=len(sl), O_hflip_mean=float(np.mean([sym(O["hflip"])[i, j] for i, j in sl])),
                            O_hflip_random_mean=float(np.mean(sym(O["hflip"])[iu])))
    res["timing_s"]["total"] = time.time() - t0
    np.savez_compressed(out / "matrices.npz", pages=np.array(pages),
                        **{f"O_{g}": O[g] for g in geo}, **{f"T_{g}": T[g] for g in geo}, U=U, U_rev=U_rev)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline="\n")

    # printed summary
    lines = [f"contact_prototype {stamp}  N={N}  candidates/page {res['n_candidates_per_page']}",
             f"timing: features {t_feat:.1f}s, GPU {t_gpu:.1f}s, total {res['timing_s']['total']:.1f}s; "
             f"GPU peak alloc {peak:.2f} GB", ""]
    for k in comps:
        lines.append(f"[{k}] known links: rank from left / from right (excl. current facing) | rot180 control")
        for r in res["known"]:
            q, qe, qc = r[k], r[k + "_excl_current"], r[k + "_control_rot"]
            lines.append(f"  {r['link']:10s} {q['rank_from_left']:3d}/{q['rank_from_right']:3d} of {q['n_cand_left']}"
                         f"  ({qe['rank_from_left']:3d}/{qe['rank_from_right']:3d})  | rot {qc['rank_from_left']:3d}/{qc['rank_from_right']:3d}"
                         f"  global {q['global_rank']}/{q['global_of']}")
        fv = res["facing_vs_random"][k]
        tops = lambda s: sum(1 for r in res["known"] if r[k][s] == 1)  # noqa: E731
        lines.append(f"  top-1 (both ends) {tops('worst')}/5, top-1 (either end) {tops('best')}/5; "
                     f"top-5 both ends {fv['known_top5_both_ends']}/5 (null mean {fv['null_top5_both_ends_mean']:.2f}, p={fv['p_known_top5']:.4f})")
        lines.append(f"  facing (n={fv['n_facing']}) mean {fv['facing_mean']:.3f} median {fv['facing_median']:.3f} | random (n={fv['n_random']}) "
                     f"mean {fv['random_mean']:.3f} median {fv['random_median']:.3f} p95 {fv['random_p95']:.3f}")
        lines.append(f"  AUC facing>random {fv['auc_facing_vs_random']:.3f}; known>random {fv['auc_known_vs_random']:.3f}; "
                     f"conjugate-outer>random {fv['auc_conjouter_vs_random']:.3f}")
        lines.append("")
    lines.append(f"same-leaf show-through control: O_hflip mean {res['same_leaf']['O_hflip_mean']:.3f} vs random {res['same_leaf']['O_hflip_random_mean']:.3f}")
    txt = "\n".join(lines)
    print(txt)
    (out / "results.txt").write_text(txt + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
