#!/usr/bin/env python
"""s48 (D-052): can frozen image embeddings recover the known pharma-sketch -> herbal-page "same plant" pairs?

PRE-REGISTERED (this file's sha256 is frozen in s48_same_plant_images.prereg.sha256 before any scoring run).
Pipeline (not scored): tools/plant_regions.py -> runs/s48/crops.json, runs/s48/embeddings.npz
(DINOv2 ViT-B/14 CLS + SigLIP ViT-B/16-224 image features, 8 views averaged, L2-normalised).

Ground truth (workflow/research/phase-4-internal-anchors.md section 2; data/ZL3b-n.txt "# Same plant as" comments):
  ZL pairs, pharma page <- herbal page, page level:
    f102r1 <- f1v, f37v ; f100v <- f3v (root) ; f102r2 <- f18v, f23r, f32v, f47v ; f102v1 <- f19r ;
    f89v2 <- f48r ; f89v (ZL '[1,4]', no panel given: crops of f89v1 and f89v2 together) <- f48v ;
    f100r <- f90v1, f90v2 ; f99r <- f96v.          (13 pairs)
  Excluded: f39r -> f95r2 (herbal-to-herbal, f95r2 has no canvas crop).
  Stolfi's 2025 seven: section 2 names only f19r (f102v '2.3') and f23r (f102r2 '3.2') explicitly, plus "all
  onto f102r1 and f102r2 except f19r"; at page level both coincide with ZL pairs already listed, so the page-level
  set stays 13 (the other Stolfi pairs are not enumerated on disk; not invented here).
  A pair is scored only if its pharma page has >= 1 non-jar crop.  Herbal pool = every herbal page with a crop.

Statistic: sim(c, h) = cosine(crop c, herbal crop h) per model; mean model = (cos_dino + cos_siglip) / 2.
  score(P, h) = max over non-jar crops c on pharma page P of sim(c, h).  rank of the true herbal page among the
  pool by score(P, .) (1 = best; rank = 1 + #pages with a strictly higher score).  MRR = mean 1/rank; percentile
  = (rank - 1) / (N - 1); median percentile reported.  Null: 10,000 random permutations of the herbal page labels
  (one permutation per draw, applied to all pairs jointly), seed 20261017; P = (1 + #null MRR >= obs) / 10,001.

P1 (decision on the mean model): MRR > 99th percentile of the null MRR AND >= 5 scored pairs with the true herbal
  page in the top 5 -> "image matching recovers known pairs".  Otherwise P1 fails.  DINOv2-only and SigLIP-only
  numbers are reported, not decisive.
P2 (descriptive, no pass/fail) Stolfi vs ZL cells, mean model, rank of the herbal page by the single crop that fills
  the cell (cell = row y-range below; cols = left-to-right x-centre order of the row's non-jar crops whose bbox
  area >= 0.25 x the row's largest; rows set from the pipeline overview images before scoring, rows count the
  label rows of ZL3b):
    f23r : f102r2 row 3 = y-centre frac > 0.72 ; ZL [3,1] vs Stolfi [3,2].
    f19r : f102v1 row 2 = y-centre frac in (0.45, 0.75) ; ZL [2,2] vs Stolfi '2.3' read as [2,3];
           alternative reading 'f102v2 [2,3]' with f102v2 row 2 = (0.35, 0.65) also reported.
  Report which cell ranks the herbal page higher.
Predictions (only if P1 passes; written to runs/s48/predictions.json before any text comparison): for every non-jar
  pharma crop that is not the mean-model argmax crop of a known pair's true herbal page, the top-3 herbal pages
  (mean-model cosine) and the pharma label tokens nearest the crop.  Nearest = Euclidean distance between the crop
  bbox centre and word-box centres, both normalised to [0,1] over their own page extents (word boxes: extent of
  all boxes in data/external/word-coordinates/.../voynichese_boxes/<page>.js; crops: extent of all crops on the
  panel); label tokens = box words equal to a word of that page's ZL3b label loci (unit L*).  Pages without a box
  file (f101r, f101v): the page's labels in ZL locus order, flagged.  The coordinate mapping is approximate.
  The hash of predictions.json is appended to the prereg stub as an amendment line.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import vparse  # noqa: E402

OUT = ROOT / "runs" / "s48"
BOXES = (ROOT / "data" / "external" / "word-coordinates" / "lrozanova-voynich-units-main" / "voynich-units-main" /
         "data" / "voynich-units" / "morphometry_voynichese" / "voynichese_boxes")
STUB = ROOT / "s48_same_plant_images.prereg.sha256"
SEED, NPERM = 20261017, 10000

PAIRS = [  # (pharma pages, herbal page, source)
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
P2 = [
    ("f23r", "f102r2", (0.72, 1.01), {"ZL": 1, "Stolfi": 2}),
    ("f19r", "f102v1", (0.45, 0.75), {"ZL": 2, "Stolfi": 3}),
    ("f19r", "f102v2", (0.35, 0.65), {"Stolfi(alt f102v2)": 3}),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ranks_for(S, rows_by_pair, true_idx):
    """S: (n_crops, N) sims; returns ranks (1-based) of the true page per pair and the score matrix."""
    sc = np.stack([S[r].max(0) for r in rows_by_pair])  # (n_pairs, N)
    tv = sc[np.arange(len(true_idx)), true_idx]
    rk = 1 + (sc > tv[:, None]).sum(1)
    return rk, sc


def null_mrr(sc, true_idx, rng):
    n, N = sc.shape
    # rank of every column within each row (1 = best; ties share the better rank)
    order = -np.sort(-sc, axis=1)
    rank_all = np.stack([1 + np.searchsorted(-order[i], -sc[i], side="left") for i in range(n)])
    out = np.empty(NPERM)
    for k in range(NPERM):
        perm = rng.permutation(N)
        out[k] = np.mean(1.0 / rank_all[np.arange(n), perm[true_idx]])
    return out


def label_tokens(page):
    recs = [r for r in vparse.load() if r["page"] == page and r["unit"].startswith("L")]
    return [(f"{page}.{r['line']}", w) for r in recs for w in r["words"]]


def nearest_labels(page, crops_on_panel, crop, k=3):
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
    fr = np.array([c["bbox_panel_frac"] for c in crops_on_panel])
    cx0, cy0 = fr[:, 0].min(), fr[:, 1].min()
    cx1, cy1 = (fr[:, 0] + fr[:, 2]).max(), (fr[:, 1] + fr[:, 3]).max()
    x, y, w, h = crop["bbox_panel_frac"]
    px, py = (x + w / 2 - cx0) / (cx1 - cx0), (y + h / 2 - cy0) / (cy1 - cy0)
    d = sorted((float(np.hypot(px - a, py - b)), wd) for wd, a, b in cand)
    return dict(method="word-box centres vs crop centre, both normalised to own page extent (approximate)",
                nearest=[dict(word=wd, dist=round(dd, 3)) for dd, wd in d[:k]],
                n_label_boxes=len(cand), n_label_tokens_zl=len(labs))


def main():
    t0 = time.time()
    run_date = subprocess.run(["date"], capture_output=True, text=True).stdout.strip() or time.ctime()
    me = sha(__file__)
    stub_match = STUB.exists() and any(line.split()[:2] == [me, Path(__file__).name]
                                       for line in STUB.read_text(encoding="utf-8").splitlines()
                                       if not line.startswith("#") and line.strip())
    meta = json.loads((OUT / "crops.json").read_text(encoding="utf-8"))
    crops = meta["crops"]
    E = np.load(OUT / "embeddings.npz")
    idx = {c: i for i, c in enumerate(E["ids"].tolist())}
    herb = [c for c in crops if c["kind"] == "herbal"]
    hpages = [c["page"] for c in herb]
    hrows = np.array([idx[c["crop"]] for c in herb])
    ph = [c for c in crops if c["kind"] == "pharma" and not c["jar_like"]]
    prow = np.array([idx[c["crop"]] for c in ph])
    S = {}
    for m in ("dino", "siglip"):
        S[m] = E[m][prow] @ E[m][hrows].T
    S["mean"] = (S["dino"] + S["siglip"]) / 2
    N = len(hpages)

    scored, rows_by_pair, true_idx = [], [], []
    for pages, hp, src in PAIRS:
        r = [i for i, c in enumerate(ph) if c["page"] in pages]
        if not r or hp not in hpages:
            continue
        scored.append((pages, hp, src))
        rows_by_pair.append(np.array(r))
        true_idx.append(hpages.index(hp))
    true_idx = np.array(true_idx)

    L = []
    def w(s=""):
        L.append(s)
        print(s)

    w(f"s48_same_plant_images.py sha256={me}  prereg stub_match={stub_match}")
    w(f"run: {run_date}")
    w(f"crops: herbal pool N={N}; pharma non-jar crops={len(ph)} (jar-like excluded: "
      f"{sum(c['jar_like'] for c in crops if c['kind'] == 'pharma')}); pairs scored={len(scored)}/{len(PAIRS)}")
    w("models: DINOv2 ViT-B/14 (facebook/dinov2-base, CLS) + SigLIP ViT-B/16-224 (google/siglip-base-patch16-224); "
      "8 views averaged")
    res = {}
    table = []
    for m in ("mean", "dino", "siglip"):
        rk, sc = ranks_for(S[m], rows_by_pair, true_idx)
        mrr = float(np.mean(1.0 / rk))
        pct = (rk - 1) / (N - 1)
        nul = null_mrr(sc, true_idx, np.random.default_rng(SEED))
        q99 = float(np.quantile(nul, 0.99))
        p = (1 + int((nul >= mrr).sum())) / (NPERM + 1)
        top5 = int((rk <= 5).sum())
        res[m] = dict(mrr=mrr, q99=q99, null_mean=float(nul.mean()), p=p, top5=top5, ranks=rk.tolist(),
                      median_pct=float(np.median(pct)))
        w(f"[{m}] MRR={mrr:.4f}  null mean={nul.mean():.4f} q99={q99:.4f}  P={p:.4f}  top5={top5}/{len(rk)}  "
          f"top1={int((rk == 1).sum())}  median percentile={np.median(pct):.3f}")
        for (pages, hp, src), r, rr in zip(scored, rows_by_pair, rk):
            best = r[np.argmax(S[m][r, hpages.index(hp)])]
            table.append(dict(model=m, pharma="+".join(pages), herbal=hp, rank=int(rr), N=N, src=src,
                              best_crop=ph[best]["crop"], best_sim=round(float(S[m][best, hpages.index(hp)]), 4)))
    w("")
    w("per-pair ranks (rank / N; best-matching crop, mean model):")
    for t in table:
        if t["model"] == "mean":
            other = {x["model"]: x["rank"] for x in table if x["herbal"] == t["herbal"] and x["pharma"] == t["pharma"]}
            w(f"  {t['pharma']:<13} <- {t['herbal']:<6} mean {t['rank']:>3}/{N}  dino {other['dino']:>3}  "
              f"siglip {other['siglip']:>3}  best crop {t['best_crop']} cos={t['best_sim']}   [{t['src']}]")
    m = res["mean"]
    p1 = (m["mrr"] > m["q99"]) and (m["top5"] >= 5)
    w("")
    w(f"P1 (mean model): MRR {m['mrr']:.4f} {'>' if m['mrr'] > m['q99'] else '<='} null q99 {m['q99']:.4f}; "
      f"top-5 count {m['top5']} (need >= 5) -> {'PASS: image matching recovers known pairs' if p1 else 'FAIL'}")

    # P2
    w("")
    w("P2 (descriptive): rank of the herbal page by the crop filling each cell (mean model)")
    p2out = []
    for hp, page, (y0, y1), cells in P2:
        r = [i for i, c in enumerate(ph) if c["page"] == page
             and y0 < c["bbox_panel_frac"][1] + c["bbox_panel_frac"][3] / 2 < y1]
        if not r:
            w(f"  {hp} on {page}: no crops in row range")
            continue
        area = {i: ph[i]["bbox_panel_frac"][2] * ph[i]["bbox_panel_frac"][3] for i in r}
        big = max(area.values())
        cols = sorted([i for i in r if area[i] >= 0.25 * big],
                      key=lambda i: ph[i]["bbox_panel_frac"][0] + ph[i]["bbox_panel_frac"][2] / 2)
        h = hpages.index(hp)
        allrk = {}
        for i in r:
            s = S["mean"][i]
            allrk[ph[i]["crop"]] = int(1 + (s > s[h]).sum())
        w(f"  {hp} on {page}: row crops (rank of {hp} among {N} by that crop alone): "
          + ", ".join(f"{k}:{v}" for k, v in allrk.items()) + f"; cols = {[ph[i]['crop'] for i in cols]}")
        for who, col in cells.items():
            if col <= len(cols):
                c = ph[cols[col - 1]]["crop"]
                w(f"    {who} cell col {col}: {c} rank {allrk[c]}")
                p2out.append(dict(herbal=hp, page=page, who=who, col=col, crop=c, rank=allrk[c]))
            else:
                w(f"    {who} cell col {col}: not present (only {len(cols)} cols)")
                p2out.append(dict(herbal=hp, page=page, who=who, col=col, crop=None, rank=None))
    for hp in ("f23r", "f19r"):
        z = [x for x in p2out if x["herbal"] == hp and x["who"] == "ZL" and x["rank"]]
        s_ = [x for x in p2out if x["herbal"] == hp and x["who"].startswith("Stolfi") and x["rank"]]
        if z and s_:
            best_s = min(s_, key=lambda x: x["rank"])
            verdict = "ZL" if z[0]["rank"] < best_s["rank"] else ("Stolfi" if best_s["rank"] < z[0]["rank"] else "tie")
            w(f"  P2 {hp}: ZL cell rank {z[0]['rank']} vs Stolfi cell rank {best_s['rank']} ({best_s['page']}) "
              f"-> higher: {verdict}")

    # predictions
    w("")
    known = set()
    for (pages, hp, src), r in zip(scored, rows_by_pair):
        known.add(ph[r[np.argmax(S["mean"][r, hpages.index(hp)])]]["crop"])
    if p1:
        preds = []
        for i, c in enumerate(ph):
            if c["crop"] in known:
                continue
            s = S["mean"][i]
            top = np.argsort(-s)[:3]
            same_panel = [x for x in crops if x["kind"] == "pharma" and x["page"] == c["page"]
                          and x["panel"] == c["panel"]]
            preds.append(dict(crop=c["crop"], page=c["page"], panel=c["panel"], bbox_canvas=c["bbox_canvas"],
                              top3=[dict(herbal=hpages[j], cos_mean=round(float(s[j]), 4)) for j in top],
                              labels=nearest_labels(c["page"], same_panel, c)))
        pj = dict(note="s48 frozen predictions (mean of DINOv2 + SigLIP cosine); written before any text test",
                  script_sha256=me, known_pair_crops=sorted(known), n=len(preds), predictions=preds)
        (OUT / "predictions.json").write_text(json.dumps(pj, indent=1), encoding="utf-8", newline="\n")
        w(f"predictions: runs/s48/predictions.json ({len(preds)} crops) sha256={sha(OUT / 'predictions.json')}")
    else:
        w("predictions: not written (P1 failed)")

    (OUT / "pairs_table.json").write_text(json.dumps(dict(results=res, table=table, p2=p2out,
                                                          herbal_pool=hpages), indent=1), encoding="utf-8")
    w(f"elapsed: {time.time() - t0:.1f}s")
    (ROOT / "results_s48.txt").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
