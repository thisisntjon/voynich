#!/usr/bin/env python
"""Phase 7.4 part 1 (D-069), step 2: blob-level mirrored-offset matching with a held-out gate.

Design frozen in data/physical/contact_map/README.md section 8 BEFORE this file was written; the
held-out set is data/physical/contact_map/step2/heldout_facing_pairs.tsv (sha256 checked below).
Prototype, files no claim.  Helpers (trim, gutter crop, Lab, stain features) are imported from
tools/physical/contact_prototype.py (v4) by path.

    python -I tools/physical/contact_blobs.py [--out DIR]

1 CPU thread at BelowNormal; GPU memory capped at 1 GB; aborts if free RAM < 4 GB.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage, stats  # noqa: E402

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("contact_prototype", HERE / "contact_prototype.py")
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)
ROOT = cp.ROOT
CMAP = ROOT / "data" / "physical" / "contact_map"
HELDOUT = CMAP / "step2" / "heldout_facing_pairs.tsv"
HELDOUT_SHA = "0e1b64b2e09c01426d57502cab5cbd3f7bcf4dfdaf0c796083b76829b1fcd8be"
DEV_QUIRES = set("BEHM")

Q = dict(  # frozen in README section 8
    DRAFT_DIV=4, WORK_W=384, WORK_H=544,
    DAB_STRONG=16.0, FOOT_CH=8.0, FOOT_DIL=2,
    BLOCK_DIL=6, SHOW_DIL=8, GHOST_DL=8.0, HP_SIGMA=40.0,
    MAD_K=4.0, GHOST_MIN=1.5, MIN_AREA=12,
    GUTTER_EXCL=0.06, EDGE_EXCL=0.03, MAX_BLOBS=40,
    LAG=40, GPU_CAP_GB=1.0, PERM=10000, SEED=20261018,
)
CLASSES = ("green", "blue")


def base_features(path, side):
    im = Image.open(path)
    im.draft("RGB", (im.width // Q["DRAFT_DIV"], im.height // Q["DRAFT_DIV"]))
    arr = cp.gutter_crop(cp.page_trim(np.asarray(im.convert("RGB"))), side)
    arr = np.asarray(Image.fromarray(arr).resize((Q["WORK_W"], Q["WORK_H"]), Image.BOX))
    L, A, B = cp.srgb_to_lab(arr)
    valid = L > 25
    a0, b0 = float(np.median(A[valid])), float(np.median(B[valid]))
    Lmed = float(np.median(L[valid]))
    ch = np.stack([np.maximum(a0 - A, 0), np.maximum(b0 - B, 0)])  # green, blue
    strong = (np.hypot(A - a0, B - b0) > Q["DAB_STRONG"]) & valid
    ink = (L < Lmed - 22.0) & valid
    foot = np.stack([ndimage.binary_dilation(strong & (c > Q["FOOT_CH"]), iterations=Q["FOOT_DIL"]) for c in ch])
    block = ndimage.binary_dilation(strong | ink, iterations=Q["BLOCK_DIL"]) | ~valid
    hp = np.stack([c - ndimage.gaussian_filter(c, Q["HP_SIGMA"]) for c in ch])
    near = np.abs(L - Lmed) < Q["GHOST_DL"]
    return dict(foot=foot, strong=strong, block=block, hp=hp, near=near, side=side)


def ghost_blobs(f, show_mask):
    H, W = Q["WORK_H"], Q["WORK_W"]
    elig = ~f["block"] & ~show_mask & f["near"]
    blobs = []
    for c in range(len(CLASSES)):
        v = f["hp"][c]
        e = v[elig]
        if e.size < 100:
            continue
        med = np.median(e)
        mad = np.median(np.abs(e - med))
        thr = max(med + Q["MAD_K"] * mad, Q["GHOST_MIN"])
        lab, n = ndimage.label(elig & (v > thr))
        if n == 0:
            continue
        objs = ndimage.find_objects(lab)
        for k, sl in enumerate(objs, start=1):
            m = lab[sl] == k
            area = int(m.sum())
            if area < Q["MIN_AREA"]:
                continue
            ys, xs = np.nonzero(m)
            cy, cx = ys.mean() + sl[0].start, xs.mean() + sl[1].start
            gut = cx / W if f["side"] == "r" else 1 - cx / W
            if gut < Q["GUTTER_EXCL"] or (1 - gut) < Q["EDGE_EXCL"] or cy / H < Q["EDGE_EXCL"] or 1 - cy / H < Q["EDGE_EXCL"]:
                continue
            mass = float(v[sl][m].sum())
            blobs.append(dict(c=c, y0=sl[0].start, x0=sl[1].start, mask=m, area=area, mass=mass))
    blobs.sort(key=lambda b: -b["mass"])
    return blobs[:Q["MAX_BLOBS"]]


def blob_scores(torch, feats, blobs, geom):
    """Directed matrix D[a,b] = max_t sum_g w_g IoU_g(t) / sum_g w_g over ghost blobs g of receiver b."""
    import torch.nn.functional as Fn
    N = len(feats)
    M = Q["LAG"]
    Fo = torch.from_numpy(np.stack([f["foot"] for f in feats]).astype(np.float32))
    if geom == "hflip":
        Fo = torch.flip(Fo, dims=[-1])
    elif geom == "rot180":
        Fo = torch.flip(Fo, dims=[-1, -2])
    Fo = Fn.pad(Fo, (M, M, M, M)).cuda()
    D = np.zeros((N, N), np.float32)
    for b in range(N):
        bl = blobs[b]
        if not bl:
            continue
        acc = torch.zeros(N, 2 * M + 1, 2 * M + 1, device="cuda")
        wsum = 0.0
        for g in bl:
            h, w = g["mask"].shape
            P = Fo[:, g["c"], g["y0"]:g["y0"] + h + 2 * M, g["x0"]:g["x0"] + w + 2 * M].unsqueeze(1)
            m = torch.from_numpy(g["mask"].astype(np.float32)).cuda()[None, None]
            inter = Fn.conv2d(P, m)[:, 0]
            fsum = Fn.conv2d(P, torch.ones_like(m))[:, 0]
            iou = inter / (g["area"] + fsum - inter).clamp_min(1.0)
            acc += g["mass"] * iou
            wsum += g["mass"]
        D[:, b] = (acc.flatten(1).max(1).values / wsum).cpu().numpy()
    return D


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    t0 = time.time()
    cp.below_normal()
    ram = cp.free_ram_gb()
    gfree, gused, gtot = cp.gpu_free_gb()
    print(f"preflight: free RAM {ram:.1f} GB; GPU used {gused:.1f}/{gtot:.1f} GB, free {gfree:.1f} GB")
    if ram < 4.0:
        sys.exit("ABORT: free RAM < 4 GB")
    if gfree < Q["GPU_CAP_GB"] + 1.0:
        sys.exit("ABORT: GPU free memory < cap + 1 GB")
    sha = hashlib.sha256(HELDOUT.read_bytes()).hexdigest()
    if sha != HELDOUT_SHA:
        sys.exit(f"ABORT: held-out list hash mismatch {sha}")
    import torch
    torch.set_num_threads(1)
    torch.cuda.set_per_process_memory_fraction(Q["GPU_CAP_GB"] / gtot)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = Path(a.out) if a.out else CMAP / "step2" / stamp
    out.mkdir(parents=True, exist_ok=False)

    folios = cp.load_folios()
    pages = sorted([p for p, r in folios.items() if r["image"] and cp.folio_key(p) and not cp.folio_key(p)[2]],
                   key=lambda p: (cp.folio_key(p)[0], cp.folio_key(p)[1]))
    N = len(pages)
    pos = {p: i for i, p in enumerate(pages)}
    print(f"{N} surfaces; features (1 CPU thread)")
    feats, stain_feats, hashes = [], [], {}
    for p in pages:
        path = ROOT / folios[p]["image"]
        hashes[p] = hashlib.sha256(path.read_bytes()).hexdigest()
        side = cp.folio_key(p)[1]
        feats.append(base_features(path, side))
        stain_feats.append(cp.features(path, side)["stain"])
    t_feat = time.time() - t0
    blobs = []
    for i, p in enumerate(pages):
        other = p[:-1] + ("v" if p.endswith("r") else "r")
        if other in pos:
            show = ndimage.binary_dilation(feats[pos[other]]["strong"][:, ::-1], iterations=Q["SHOW_DIL"])
        else:
            show = np.zeros_like(feats[i]["strong"])
        blobs.append(ghost_blobs(feats[i], show))
    nblobs = np.array([len(b) for b in blobs])
    print(f"ghost blobs per surface: median {np.median(nblobs):.0f}, zero on {(nblobs == 0).sum()} surfaces")

    torch.cuda.reset_peak_memory_stats()
    t1 = time.time()
    Dh = blob_scores(torch, feats, blobs, "hflip")
    Dr = blob_scores(torch, feats, blobs, "rot180")
    # secondary: stain T (prototype v4 features, scale 1), side-mean subtracted
    st = np.stack(stain_feats)
    sides = np.array([cp.folio_key(p)[1] for p in pages])
    for s in "rv":
        st[sides == s] -= st[sides == s].mean(0, keepdims=True)
    stn = torch.from_numpy(st[:, None])
    T = cp.ncc_matrix(torch, torch.flip(stn, dims=[-1]), stn, cp.P["MAX_SHIFT"])
    torch.cuda.synchronize()
    t_gpu = time.time() - t1
    peak = torch.cuda.max_memory_allocated() / 2**30

    leaf = np.array([cp.folio_key(p)[0] for p in pages])
    cand = leaf[:, None] != leaf[None, :]
    iu = np.triu(cand, 1)

    def norm_sym(D):
        Dn = D.copy()
        for b in range(N):
            Dn[:, b] -= np.median(D[cand[:, b], b])
        return Dn + Dn.T

    Bh, Br = norm_sym(Dh), norm_sym(Dr)
    Ts = T + T.T
    z = lambda X: (X - X[iu].mean()) / (X[iu].std() + 1e-9)  # noqa: E731
    scores = {"B_primary": Bh, "B_rot180_control": Br, "B_mirror_excess": Bh - Br, "B_plus_T": z(Bh) + z(Ts),
              "T_stain": Ts}

    def rankmat(S):
        R = np.full((N, N), 10**6, dtype=np.int64)
        for i in range(N):
            c = np.where(cand[i])[0]
            s = S[i, c]
            R[i, c] = (s[None, :] >= s[:, None]).sum(1)
        return np.maximum(R, R.T)  # both-ends rank

    heldout = [ln.split("\t")[:2] for ln in HELDOUT.read_text().splitlines()[2:] if ln.strip()]
    links = [(x, y) for x, y, _ in cp.KNOWN_LINKS]
    bif = {}
    for p, r in folios.items():
        k = cp.folio_key(p)
        if k and not k[2] and r["conjugate"]:
            bif.setdefault(tuple(sorted((k[0], int(r["conjugate"][1:])))), r["quire"])
    sheets = [(x, y, q) for (x, y), q in sorted(bif.items())
              if all(f"f{n}{s}" in pos for n in (x, y) for s in "rv")]
    rng = np.random.default_rng(Q["SEED"])
    res = dict(stamp=stamp, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               prototype_sha256=hashlib.sha256((HERE / "contact_prototype.py").read_bytes()).hexdigest(),
               heldout_sha256=sha, params=Q, n_surfaces=N, n_candidates=int(cand.sum(1).max()),
               blobs_median=float(np.median(nblobs)), surfaces_without_blobs=int((nblobs == 0).sum()),
               timing_s=dict(features=t_feat, gpu=t_gpu), gpu_peak_gb=peak, image_sha256=hashes, by_score={})
    lines = [f"contact_blobs {stamp}  N={N} surfaces, {res['n_candidates']} candidates each; "
             f"features {t_feat:.0f}s, GPU {t_gpu:.0f}s, peak {peak:.2f} GB",
             f"ghost blobs/surface median {np.median(nblobs):.0f}; surfaces without blobs {(nblobs == 0).sum()}", ""]
    for name, S in scores.items():
        R = rankmat(S)
        k1 = [(x, y, int(R[pos[x], pos[y]])) for x, y in links]
        k1_hits = sum(r <= 5 for *_, r in k1)
        ho = [(x, y, int(R[pos[x], pos[y]])) for x, y in heldout]
        hits = sum(r <= 5 for *_, r in ho)
        # permutation null: random partner from the left page's candidates
        lefts = np.array([pos[x] for x, _ in heldout])
        null = np.zeros(Q["PERM"], np.int64)
        for li in lefts:
            c = np.where(cand[li])[0]
            js = rng.choice(c, size=Q["PERM"])
            null += (R[li, js] <= 5)
        p_k2 = float(((null >= hits).sum() + 1) / (Q["PERM"] + 1))
        inner = np.array([S[pos[f"f{x}v"], pos[f"f{y}r"]] for x, y, _ in sheets])
        outer = np.array([S[pos[f"f{x}r"], pos[f"f{y}v"]] for x, y, _ in sheets])
        w_all = stats.wilcoxon(inner - outer, alternative="greater")
        hq = np.array([q not in DEV_QUIRES for *_, q in sheets])
        w_ho = stats.wilcoxon(inner[hq] - outer[hq], alternative="greater")
        hv = [S[pos[x], pos[y]] for x, y in heldout]
        hset = {tuple(sorted((pos[x], pos[y]))) for x, y in heldout}
        rnd = [S[u, v] for u, v in zip(*np.where(iu)) if (u, v) not in hset]
        auc = float(stats.mannwhitneyu(hv, rnd, alternative="greater").statistic / (len(hv) * len(rnd)))
        d = dict(K1_dev=k1, K1_hits=k1_hits, K1_pass=k1_hits >= 4,
                 K2_ranks=ho, K2_hits=hits, K2_rate=hits / len(ho), K2_null_mean=float(null.mean()),
                 K2_p=p_k2, K2_pass=(hits / len(ho) >= 0.5) and p_k2 < 0.001,
                 K2_median_rank=float(np.median([r for *_, r in ho])),
                 K3_n=len(sheets), K3_inner_gt_outer=int((inner > outer).sum()), K3_p_all=float(w_all.pvalue),
                 K3_n_heldout=int(hq.sum()), K3_p_heldout_quires=float(w_ho.pvalue), K3_pass=float(w_all.pvalue) < 0.05,
                 auc_heldout_vs_random=auc)
        res["by_score"][name] = d
        lines.append(f"[{name}]")
        lines.append("  K1 (development) both-end ranks: " + ", ".join(f"{x}|{y} {r}" for x, y, r in k1)
                     + f"  -> {k1_hits}/5 top-5  PASS={d['K1_pass']}")
        lines.append(f"  K2 (held-out, n={len(ho)}): top-5 both ends {hits} ({100 * d['K2_rate']:.1f}%), null mean "
                     f"{null.mean():.2f}, p={p_k2:.5f}, median rank {d['K2_median_rank']:.0f}  PASS={d['K2_pass']}")
        lines.append(f"  K3 (n={len(sheets)} bifolia): inner>outer {d['K3_inner_gt_outer']}/{len(sheets)}, Wilcoxon p={w_all.pvalue:.4f}"
                     f" (held-out quires n={hq.sum()}: p={w_ho.pvalue:.4f})  PASS={d['K3_pass']}")
        lines.append(f"  AUC held-out facing vs random pairs {auc:.3f}")
        lines.append("")
    txt = "\n".join(lines)
    print(txt)
    res["timing_s"]["total"] = time.time() - t0
    np.savez_compressed(out / "matrices.npz", pages=np.array(pages), D_hflip=Dh, D_rot180=Dr, T=T)
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline="\n")
    (out / "results.txt").write_text(txt + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
