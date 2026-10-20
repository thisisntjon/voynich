#!/usr/bin/env python3
"""
s106_x2_star_first_line.py -- X2 (D-066 (f), (f-precondition), lead pre-freeze amendment f-amend):
does a recipe paragraph's first line predict its star-marker class on held-out bifolios beyond
position, alternation, scribe and page baselines?

Stages (run in this order; each refuses to overwrite its outputs):
  prep     TEXT-FREE.  Reads runs/s100/star_classes.tsv, the geometry fields of runs/s45/pages/<pid>.json
           (size, pitch, lines[*].yb, lines[*].bbox, alignment[*].det / alignment[*].loci indices only),
           and from data/ZL3b-n.txt ONLY page-header variables ($B bifolio, $H hand) and, per locus, its
           order index and whether the locus carries the paragraph-start marker '<%>'.  No glyph text read.
           Writes runs/s106/prep_assignment.tsv and runs/s106/prep_report.txt (n per class, MDE, subset choice).
  fixture  Synthetic positive/negative controls through the same model code (no manuscript text).
  real     Reads text (ZL3b primary; RF1b, IT2a descriptive), scores, writes results_s106.txt.

GEOMETRIC ASSIGNMENT RULE (written before the prep stage was first run):
  G1 Candidate lines: s45 detected lines with bbox width > 2*pitch, bbox_x0 < 0.5*W, and present in s45 alignment.
  G2 Each s100 star goes to the candidate line minimising |cy - yb|; accepted iff |cy - yb| <= 0.75*pitch,
     otherwise SPURIOUS (dropped).
  G3 Line -> transliteration locus: loci[0] of the s45 alignment group containing that detected line.
  G4 Duplicates: if > 1 accepted star maps to one locus, keep the star with the smallest |cy - yb|; others DUPLICATE.
  G5 Label: consensus where Method A == Method B (filled_agree / tailed_agree == 1); else DISAGREE (not scored,
     but kept in the page star sequence; its class counts as 'unknown' for the previous-star feature).
  G6 para_start = the assigned locus carries '<%>' in ZL3b; otherwise the star sits beside a mid-block line.
  Star order on a page = ascending cy among kept (non-spurious, non-duplicate) stars (physical top-to-bottom).
  PRE-FREEZE REVISION 1 (13:37 PDT, after the first text-free prep showed 72 stars landing one locus above and 46
  one locus below a '<%>' line, i.e. s45 det->locus alignment slips by one line; geometry and markup only):
  G3b Snap: if the G3 locus L is not '<%>' and L-1 or L+1 is, move the star to that '<%>' locus (if both, the one
      whose aligned detected lines have mean yb nearest cy).  Exact '<%>' hits claim loci first; a snapped star
      whose target is already claimed stays at L (mid-block).  G4 duplicates are then resolved as before.
      First-run outputs (prep_report.txt, prep_assignment.tsv) are kept; revision outputs carry the suffix _rev1.

NON-TEXT BASELINE (filled/hollow, per f-amend item 1):
  leaf number (scaled), recto/verso, star rank on page, rank fraction, rank parity, page-top indicator,
  previous-star class (+1 filled, -1 hollow, 0 unknown/none), vertical position cy/H, para_start, stars on page.
  Scribe: all Quire 20 pages are hand 3 (f115r '?' -> 3, as s77) -> constant, reported and dropped.
  Page-level class rate in training bifolios: a held-out page has no training rate of its own, so this term
  reduces to the training-fold intercept (it is the model intercept).
  Tailed/plain (descriptive only, f-amend item 4): same features plus previous-star tailed class and the page's
  leave-one-out tailed rate among the other consensus stars of the same page (page term).
TEXT MODELS: baseline + binary first-line features, vocabulary = items present in >= 2 training first lines.
  (A) SlotSegmenter cores (scoreboard.metrics_new.SlotSegmenter fit on all ZL3b tokens, as s97).
  (B) segmenter-free glyph 3-grams of '#' + '.'.join(tokens) + '#'.
  Classifier: sklearn LogisticRegression(C=1.0, liblinear, L2), baseline features z-scored on the training fold.
DESIGN: leave-one-bifolio-out (6 folds, ZL $B 1..6); pooled out-of-fold AUC.
  Statistic delta = AUC_text - AUC_base.  Null: permute first-line representations among scored stars WITHIN PAGE
  (baseline features and labels fixed), refit the whole CV; N_PERM = 1000; p = (1 + #{delta_perm >= delta}) / (1 + N).
ACCEPTANCE (D-066 f): primary class filled/hollow, subset chosen at prep (rule below); PASS iff delta > 0 and
  p < 0.05 in BOTH representations.  Secondary class and the other subset: descriptive.
SUBSET RULE (f-amend item 2): use (b) paragraph-start stars iff n_b >= 150 and residual deviations in (b) >= 15
  and residual MDE_b <= 0.72; otherwise (a) all stars.
RESIDUAL MDE (f-amend item 3): deviation = consensus label != alternation rule (page-top -> filled, else opposite
  of previous star; stars whose previous star is unknown are excluded).  MDE_res = 0.5 + (z_.95 + z_.80) *
  SE_HanleyMcNeil(n_dev, n_nondev) * sqrt(DEFF), DEFF = 1 + (m - 1) * max(0, ICC_bifolio(deviation)).
  HOLD iff MDE_res of the chosen subset > 0.72 (upper end of D-066 (f)'s expected AUC range): text models not run.
CONTROLS: fixture (synthetic) and real-line planted controls: labels follow the alternation rule except that a star
  whose first line contains core c* is forced 'filled' (content override); null: alternation with random deviations
  at the observed rate.  controls_ok iff planted detected (delta > 0, p < 0.05) in both reps and null detected in
  neither.  Real-line c* = core whose first-line document frequency among scored stars is closest to 15%.
VERDICT: HOLD | INCONCLUSIVE (controls fail) | POSITIVE (both reps pass) | NEGATIVE (stop the marker-prediction line).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import psutil  # noqa: E402
from scipy import sparse  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "runs" / "s106"
STAR_TSV = ROOT / "runs" / "s100" / "star_classes.tsv"
S45 = ROOT / "runs" / "s45" / "pages"
ZL_RAW = ROOT / "data" / "ZL3b-n.txt"
META = {n: ROOT / "data" / "translit" / f"{n}.meta.json" for n in ("ZL3b_eva", "RF1b", "IT2a")}
RESULTS = ROOT / "results_s106.txt"

SEED = 106
N_PERM = 1000
C_REG = 1.0
MIN_DF = 2
ALPHA = 0.05
MDE_BAR = 0.72
TOL_PITCH = 0.75
SUBSET_MIN_N = 150
SUBSET_MIN_DEV = 15
PLANT_DF = 0.15
Z_A, Z_B = 1.6448536, 0.8416212

LOG: list[str] = []


def emit(s=""):
    print(s, flush=True)
    LOG.append(s)


def now():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def guard_compute():
    p = psutil.Process()
    try:
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    free = psutil.virtual_memory().available / 1e9
    if free < 4.0:
        sys.exit(f"ABORT: free RAM {free:.2f} GB < 4 GB")
    return free


def write_new(path: Path, text: str):
    if path.exists():
        sys.exit(f"ABORT: {path} exists; never overwrite")
    path.write_bytes(text.encode("utf-8"))


# ----------------------------------------------------------------------------------------------- text-free prep
def zl_markup():
    """Page header vars ($B, $H) and per-locus order + '<%>' flag. Glyph text is never stored."""
    page_re = re.compile(r"^<(f\d+[rv]\d*)>\s+<!(.*)>")
    var_re = re.compile(r"\$(\w)=(\S+)")
    loc_re = re.compile(r"^<(f\d+[rv]\d*)\.(\d+),")
    hdr, para = {}, defaultdict(list)
    for raw in ZL_RAW.read_text(encoding="ascii", errors="replace").splitlines():
        m = page_re.match(raw)
        if m:
            hdr[m.group(1)] = dict(var_re.findall(m.group(2)))
            continue
        m = loc_re.match(raw)
        if m:
            para[m.group(1)].append("<%>" in raw)
    return hdr, para


def load_stars():
    with STAR_TSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def prep():
    free = guard_compute()
    rep_path, tsv_path = OUT / "prep_report_rev1.txt", OUT / "prep_assignment_rev1.tsv"
    hdr, para = zl_markup()
    stars = load_stars()
    by_page = defaultdict(list)
    for s in stars:
        by_page[s["folio"]].append(s)
    rows, stat = [], Counter()
    for pid in sorted(by_page, key=lambda p: (int(re.match(r"f(\d+)", p).group(1)), p[-1])):
        g = json.loads((S45 / f"{pid}.json").read_text(encoding="utf-8"))
        W, H = g["size"]
        pitch = float(g["pitch"])
        det2loc = {}
        for grp in g["alignment"]:
            for d in grp["det"]:
                det2loc[int(d)] = int(grp["loci"][0])
        cands = []
        for i, ln in enumerate(g["lines"]):
            x0, y0, x1, y1 = ln["bbox"]
            if (x1 - x0) > 2 * pitch and x0 < 0.5 * W and i in det2loc:
                cands.append((i, float(ln["yb"])))
        recs = []
        for s in by_page[pid]:
            cy = float(s["cy_page"])
            i, yb = min(cands, key=lambda c: abs(cy - c[1]))
            dy = abs(cy - yb)
            r = dict(gidx=int(s["global_idx"]), folio=pid, cy=cy, H=H, pitch=pitch, det=i, dy=round(dy, 1),
                     locus=det2loc[i], filled_A=s["filled_A"], filled_B=s["filled_B"],
                     tailed_A=s["tailed_A"], tailed_B=s["tailed_B"],
                     f_agree=int(s["filled_agree"]), t_agree=int(s["tailed_agree"]))
            r["status"] = "ok" if dy <= TOL_PITCH * pitch else "SPURIOUS"
            recs.append(r)
        loc_yb = defaultdict(list)
        for grp in g["alignment"]:
            for d in grp["det"]:
                loc_yb[int(grp["loci"][0])].append(float(g["lines"][int(d)]["yb"]))
        pf = para[pid]
        claimed = {r["locus"] for r in recs if r["status"] == "ok" and pf[r["locus"]]}
        for r in recs:
            r["locus_g3"], r["snap"] = r["locus"], 0
        for r in sorted(recs, key=lambda r: r["dy"]):
            L = r["locus"]
            if r["status"] != "ok" or pf[L]:
                continue
            opts = [L + d for d in (-1, 1) if 0 <= L + d < len(pf) and pf[L + d] and (L + d) not in claimed]
            if not opts:
                continue
            tgt = min(opts, key=lambda k: abs(r["cy"] - np.mean(loc_yb[k])) if loc_yb[k] else 1e9)
            r["locus"], r["snap"] = tgt, tgt - L
            claimed.add(tgt)
        stat_snap = sum(1 for r in recs if r["snap"])
        stat["snapped"] += stat_snap
        best = {}
        for r in recs:
            if r["status"] != "ok":
                continue
            k = r["locus"]
            if k not in best or r["dy"] < best[k]["dy"]:
                best[k] = r
        for r in recs:
            if r["status"] == "ok" and best[r["locus"]] is not r:
                r["status"] = "DUPLICATE"
        kept = sorted([r for r in recs if r["status"] == "ok"], key=lambda r: r["cy"])
        hv = hdr[pid]
        for rank, r in enumerate(kept):
            r["rank"], r["n_page"] = rank, len(kept)
            r["para_start"] = int(para[pid][r["locus"]])
            r["bifolio"] = int(hv["B"])
            r["hand"] = hv.get("H", "?") if hv.get("H", "?") in "12345" else "3"
            r["filled"] = (1 if r["filled_A"] == "filled" else 0) if r["f_agree"] else -1
            r["tailed"] = (1 if r["tailed_A"] == "tailed" else 0) if r["t_agree"] else -1
        for r in recs:
            stat[r["status"]] += 1
            stat["status_" + r["status"]] += 0
        rows.extend(recs)
    kept = [r for r in rows if r["status"] == "ok"]
    cols = ["gidx", "folio", "bifolio", "hand", "cy", "H", "pitch", "det", "dy", "locus_g3", "snap", "locus", "status", "rank", "n_page",
            "para_start", "filled_A", "filled_B", "f_agree", "filled", "tailed_A", "tailed_B", "t_agree", "tailed"]
    tsv = "\t".join(cols) + "\n" + "".join("\t".join(str(r.get(c, "")) for c in cols) + "\n" for r in rows)
    write_new(tsv_path, tsv)
    emit(f"s106 PREP rev1 (text-free)  {now()}  free RAM {free:.2f} GB")
    emit(f"stars in s100: {len(rows)}; status counts: {dict(stat)}")
    emit(f"kept stars: {len(kept)}; ZL3b '<%>' paragraphs on these pages: "
         f"{sum(sum(para[p]) for p in by_page)}")
    emit(f"kept stars beside '<%>' lines: {sum(r['para_start'] for r in kept)}; beside mid-block lines: "
         f"{sum(1 - r['para_start'] for r in kept)}")
    ps_hit = {(r['folio'], r['locus']) for r in kept if r['para_start']}
    n_unstarred = sum(1 for p in by_page for j, f in enumerate(para[p]) if f and (p, j) not in ps_hit)
    emit(f"ZL3b '<%>' lines with no kept star: {n_unstarred}")
    emit(f"hands on kept stars: {dict(Counter(r['hand'] for r in kept))} (constant -> scribe term dropped)")
    dys = np.array([r["dy"] / r["pitch"] for r in kept])
    emit(f"|cy-yb|/pitch of kept: median {np.median(dys):.2f}, p90 {np.percentile(dys, 90):.2f}, max {dys.max():.2f}")
    emit(f"filled/hollow: consensus {sum(r['filled'] >= 0 for r in kept)}, DISAGREE dropped "
         f"{sum(r['filled'] < 0 for r in kept)}; filled {sum(r['filled'] == 1 for r in kept)}, "
         f"hollow {sum(r['filled'] == 0 for r in kept)}")
    emit(f"tailed/plain:  consensus {sum(r['tailed'] >= 0 for r in kept)}, DISAGREE dropped "
         f"{sum(r['tailed'] < 0 for r in kept)}; tailed {sum(r['tailed'] == 1 for r in kept)}, "
         f"plain {sum(r['tailed'] == 0 for r in kept)}")
    for sub in ("a", "b"):
        sel = [r for r in kept if r["filled"] >= 0 and (sub == "a" or r["para_start"])]
        emit(f"subset ({sub}) filled/hollow n={len(sel)}: filled {sum(r['filled'] for r in sel)}, "
             f"hollow {sum(1 - r['filled'] for r in sel)}")
    pages = defaultdict(list)
    for r in kept:
        pages[r["folio"]].append(r)
    res = {}
    for sub in ("a", "b"):
        d = residual_stats(pages, sub)
        res[sub] = d
        emit(f"subset ({sub}) residual: rule-scorable {d['n']}, deviations {d['n_dev']} "
             f"({d['n_dev'] / max(d['n'], 1):.3f}); ICC_bifolio {d['icc']:+.3f}, m {d['m']:.1f}, DEFF {d['deff']:.2f}; "
             f"SE_HM {d['se']:.4f}; MDE_res AUC {d['mde']:.3f}; full-label MDE AUC (n1/n0, DEFF=1) {d['mde_full']:.3f}")
    b = res["b"]
    use_b = b["n_lab"] >= SUBSET_MIN_N and b["n_dev"] >= SUBSET_MIN_DEV and b["mde"] <= MDE_BAR
    chosen = "b" if use_b else "a"
    emit(f"SUBSET CHOICE: ({chosen})  [rule: (b) iff n_b >= {SUBSET_MIN_N} and dev_b >= {SUBSET_MIN_DEV} "
         f"and MDE_b <= {MDE_BAR}]")
    hold = res[chosen]["mde"] > MDE_BAR
    emit(f"CALL hold = {hold}  (MDE_res[{chosen}] = {res[chosen]['mde']:.3f} vs bar {MDE_BAR})")
    write_new(rep_path, "\n".join(LOG) + "\n")


def alternation_rule(seq):
    """seq: page labels in order (1/0/-1 unknown). Returns predicted label per position or None."""
    out = []
    for i, y in enumerate(seq):
        if i == 0:
            out.append(1)
        else:
            out.append(None if seq[i - 1] < 0 else 1 - seq[i - 1])
    return out


def residual_stats(pages, sub):
    devs, grp, n_lab = [], [], 0
    for pid, rs in pages.items():
        seq = [r["filled"] for r in rs]
        pred = alternation_rule(seq)
        for r, pr in zip(rs, pred):
            if r["filled"] < 0 or (sub == "b" and not r["para_start"]):
                continue
            n_lab += 1
            if pr is None:
                continue
            devs.append(int(r["filled"] != pr))
            grp.append(r["bifolio"])
    devs, grp = np.array(devs), np.array(grp)
    n, n1 = len(devs), int(devs.sum())
    n0 = n - n1
    icc, m = icc_oneway(devs, grp)
    deff = 1 + (m - 1) * max(0.0, icc)
    se = math.sqrt((n1 + n0 + 1) / (12.0 * max(n1, 1) * max(n0, 1)))
    mde = 0.5 + (Z_A + Z_B) * se * math.sqrt(deff)
    # full-label MDE: labels in subset
    lab = []
    for rs in pages.values():
        lab += [r["filled"] for r in rs if r["filled"] >= 0 and (sub == "a" or r["para_start"])]
    l1 = sum(lab)
    l0 = len(lab) - l1
    se_f = math.sqrt((l1 + l0 + 1) / (12.0 * l1 * l0))
    return dict(n=n, n_dev=n1, icc=icc, m=m, deff=deff, se=se, mde=mde, n_lab=n_lab,
                mde_full=0.5 + (Z_A + Z_B) * se_f)


def icc_oneway(y, g):
    groups = [y[g == k] for k in np.unique(g)]
    k = len(groups)
    N = len(y)
    sizes = np.array([len(x) for x in groups])
    grand = y.mean()
    msb = sum(len(x) * (x.mean() - grand) ** 2 for x in groups) / (k - 1)
    msw = sum(((x - x.mean()) ** 2).sum() for x in groups) / (N - k)
    m0 = (N - (sizes ** 2).sum() / N) / (k - 1)
    icc = (msb - msw) / (msb + (m0 - 1) * msw) if (msb + (m0 - 1) * msw) > 0 else 0.0
    return float(icc), float(sizes.mean())


def load_prep():
    with (OUT / "prep_assignment_rev1.tsv").open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["status"] == "ok"]
    for r in rows:
        for k in ("gidx", "bifolio", "rank", "n_page", "para_start", "filled", "tailed", "locus"):
            r[k] = int(r[k])
        for k in ("cy", "H"):
            r[k] = float(r[k])
    rows.sort(key=lambda r: (r["folio"], r["rank"]))
    return rows


# ----------------------------------------------------------------------------------------------- features & model
def leaf_num(pid):
    return int(re.match(r"f(\d+)", pid).group(1))


def baseline_matrix(stars, lab_key):
    """stars: all kept stars (page order). Returns features per star (np array) using labels lab_key."""
    pages = defaultdict(list)
    for i, s in enumerate(stars):
        pages[s["folio"]].append(i)
    X = np.zeros((len(stars), 12))
    for pid, idx in pages.items():
        for j, i in enumerate(idx):
            s = stars[i]
            prev = stars[idx[j - 1]][lab_key] if j > 0 else -1
            prev_enc = 0.0 if prev < 0 else (1.0 if prev == 1 else -1.0)
            others = [stars[k][lab_key] for k in idx if k != i and stars[k][lab_key] >= 0]
            page_loo = float(np.mean(others)) if others else 0.5
            X[i] = [leaf_num(pid), 1.0 if pid.endswith("r") else 0.0, s["rank"], s["rank"] / max(s["n_page"] - 1, 1),
                    s["rank"] % 2, 1.0 if s["rank"] == 0 else 0.0, prev_enc, s["cy"] / s["H"], s["para_start"],
                    s["n_page"], page_loo, 0.0]
    return X


BASE_COLS_FILLED = list(range(10))          # page_loo excluded for the primary class
BASE_COLS_TAILED = list(range(11))          # page term included (f-amend item 4)


def text_matrix(items_list, train_idx):
    df = Counter()
    for i in train_idx:
        df.update(items_list[i])
    vocab = {w: k for k, w in enumerate(sorted(w for w, c in df.items() if c >= MIN_DF))}
    rows, cols = [], []
    for r, its in enumerate(items_list):
        for w in its:
            k = vocab.get(w)
            if k is not None:
                rows.append(r)
                cols.append(k)
    return sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(items_list), max(len(vocab), 1)))


def cv_scores(Xb, y, folds, items=None):
    """Leave-one-bifolio-out pooled OOF probabilities."""
    oof = np.zeros(len(y))
    for f in np.unique(folds):
        tr, te = np.where(folds != f)[0], np.where(folds == f)[0]
        mu, sd = Xb[tr].mean(0), Xb[tr].std(0)
        sd[sd == 0] = 1.0
        Z = (Xb - mu) / sd
        Z[:, Xb[tr].std(0) == 0] = 0.0
        if items is not None:
            T = text_matrix(items, tr)
            M = sparse.hstack([sparse.csr_matrix(Z), T]).tocsr()
        else:
            M = Z
        if len(np.unique(y[tr])) < 2:
            oof[te] = y[tr].mean()
            continue
        clf = LogisticRegression(C=C_REG, solver="liblinear", max_iter=2000)
        clf.fit(M[tr], y[tr])
        oof[te] = clf.predict_proba(M[te])[:, 1]
    return oof


def auc(y, p):
    return float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else float("nan")


def perm_test(Xb, y, folds, pages, items, rng, n_perm=N_PERM):
    base = auc(y, cv_scores(Xb, y, folds))
    obs = auc(y, cv_scores(Xb, y, folds, items))
    delta = obs - base
    groups = defaultdict(list)
    for i, p in enumerate(pages):
        groups[p].append(i)
    ge = 0
    deltas = np.zeros(n_perm)
    for b in range(n_perm):
        perm = list(range(len(items)))
        for idx in groups.values():
            sh = rng.permutation(idx)
            for a, c in zip(idx, sh):
                perm[a] = c
        it2 = [items[perm[i]] for i in range(len(items))]
        d = auc(y, cv_scores(Xb, y, folds, it2)) - base
        deltas[b] = d
        ge += d >= delta
    p = (1 + ge) / (1 + n_perm)
    return dict(base=base, text=obs, delta=delta, p=p, null_mean=float(deltas.mean()),
                null_q95=float(np.quantile(deltas, 0.95)), passed=bool(delta > 0 and p < ALPHA))


def reps_from_lines(lines, seg):
    A = [frozenset(seg.segment(w)[1] for w in ln) for ln in lines]
    B = []
    for ln in lines:
        s = "#" + ".".join(ln) + "#"
        B.append(frozenset(s[i:i + 3] for i in range(len(s) - 2)))
    return A, B


def analysis(stars, lines, seg, lab_key, subset, rng, cols, n_perm=N_PERM, tag=""):
    X_all = baseline_matrix(stars, lab_key)[:, cols]
    sel = [i for i, s in enumerate(stars) if s[lab_key] >= 0 and (subset == "a" or s["para_start"])]
    Xb = X_all[sel]
    y = np.array([stars[i][lab_key] for i in sel])
    folds = np.array([stars[i]["bifolio"] for i in sel])
    pages = [stars[i]["folio"] for i in sel]
    A, B = reps_from_lines([lines[i] for i in sel], seg)
    out = {}
    for name, items in (("A_cores", A), ("B_3grams", B)):
        t0 = time.time()
        r = perm_test(Xb, y, folds, pages, items, rng, n_perm)
        r["n"], r["n1"], r["secs"] = len(y), int(y.sum()), time.time() - t0
        out[name] = r
        emit(f"  {tag} [{name}] n={r['n']} (class1 {r['n1']}): base AUC {r['base']:.4f}, text AUC {r['text']:.4f}, "
             f"delta {r['delta']:+.4f}, perm p {r['p']:.4f} (null mean {r['null_mean']:+.4f}, q95 {r['null_q95']:+.4f}), "
             f"pass={r['passed']}  [{r['secs']:.0f}s]")
    return out


def plant_labels(stars, lines_core_sets, core, rng, mode, dev_rate=0.1):
    """Alternation rule with content override (mode='plant') or random deviations (mode='null')."""
    pages = defaultdict(list)
    for i, s in enumerate(stars):
        pages[s["folio"]].append(i)
    lab = [0] * len(stars)
    for idx in pages.values():
        for j, i in enumerate(idx):
            alt = 1 if j == 0 else 1 - lab[idx[j - 1]]
            if mode == "plant":
                lab[i] = 1 if core in lines_core_sets[i] else alt
            else:
                lab[i] = (1 - alt) if rng.random() < dev_rate else alt
    out = []
    for s, l in zip(stars, lab):
        s2 = dict(s)
        s2["planted"] = l
        out.append(s2)
    return out


# ----------------------------------------------------------------------------------------------- fixture
def synth_lines(stars, rng):
    from scoreboard.metrics_new import SlotSegmenter
    pre = ["", "", "q", "o", "y", "d"]
    suf = ["", "y", "n", "l", "r", "dy"]
    alph = list("aceikhst")
    cores = sorted({"".join(rng.choice(alph, size=rng.integers(2, 5))) for _ in range(400)})
    words = [p + c + s for p in pre for c in cores[:120] for s in suf]
    zipf = 1.0 / np.arange(1, len(words) + 1)
    zipf /= zipf.sum()
    rng.shuffle(words)
    lines = []
    for _ in stars:
        lines.append([str(w) for w in rng.choice(words, size=rng.integers(6, 12), p=zipf)])
    filler = [[str(w) for w in rng.choice(words, size=9, p=zipf)] for _ in range(3000)]
    # planted core 'zvz' carried by ~15% of first lines, wrapped in random prefix/suffix
    for i in range(len(lines)):
        if rng.random() < PLANT_DF:
            lines[i].insert(int(rng.integers(0, len(lines[i]))), str(rng.choice(pre[2:])) + "zvz" + str(rng.choice(suf[1:])))
    seg = SlotSegmenter([w for ln in lines + filler for w in ln])
    return lines, seg


def fixture():
    free = guard_compute()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    emit(f"s106 FIXTURE (synthetic, no manuscript text)  {now()}  free RAM {free:.2f} GB")
    stars = load_prep()
    rng = np.random.default_rng(SEED)
    lines, seg = synth_lines(stars, rng)
    cs = [frozenset(seg.segment(w)[1] for w in ln) for ln in lines]
    emit(f"  segmenter core of planted word e.g. {seg.segment('qzvzy')}, first-line df of 'zvz' core "
         f"{sum('zvz' in c for c in cs) / len(cs):.3f}")
    res = {}
    for mode in ("plant", "null"):
        st = plant_labels(stars, cs, "zvz", rng, mode)
        emit(f" fixture {mode}: deviations from alternation would be scored as in real data")
        res[mode] = analysis(st, lines, seg, "planted", "a", rng, BASE_COLS_FILLED, N_PERM, tag=f"fixture-{mode}")
    ok = all(r["passed"] for r in res["plant"].values()) and not any(r["passed"] for r in res["null"].values())
    emit(f"CALL fixture_ok = {ok}")
    write_new(OUT / f"fixture_{stamp}.txt", "\n".join(LOG) + "\n")


# ----------------------------------------------------------------------------------------------- real
def load_text(name, stars):
    d = json.loads(META[name].read_text(encoding="utf-8"))
    pages = {p["id"]: p["lines"] for p in d["pages"]}
    return pages


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def real():
    if RESULTS.exists():
        sys.exit("ABORT: results_s106.txt exists")
    free = guard_compute()
    t_start = time.time()
    emit("=" * 100)
    emit("RUN s106: X2 -- DOES A RECIPE PARAGRAPH'S FIRST LINE PREDICT ITS STAR CLASS (D-066 f, f-amend)")
    emit("=" * 100)
    emit(f"start {now()}  free RAM {free:.2f} GB  script sha256 {sha(Path(__file__))}")
    emit(f"stub: s106_x2_star_first_line.prereg.sha256 (verify: grep -v '^#' STUB | tr -d '\\r' | sha256sum -c -)")
    emit("prep report (text-free, frozen before scoring):")
    for ln in (OUT / "prep_report_rev1.txt").read_text(encoding="utf-8").splitlines():
        emit("  | " + ln)
    rep = (OUT / "prep_report_rev1.txt").read_text(encoding="utf-8")
    chosen = re.search(r"SUBSET CHOICE: \((\w)\)", rep).group(1)
    hold = "CALL hold = True" in rep
    stars = load_prep()
    if hold:
        emit("CALL hold = True -> text models NOT run (D-066 f stopping rule, f-amend item 3)")
        emit("VERDICT: HOLD")
        write_new(RESULTS, "\n".join(LOG) + "\n")
        return
    from scoreboard.metrics_new import SlotSegmenter
    rng = np.random.default_rng(SEED)
    results = {}
    for tname in ("ZL3b_eva", "RF1b", "IT2a"):
        pages = load_text(tname, stars)
        seg = SlotSegmenter([w for ls in pages.values() for ln in ls for w in ln])
        keep = [s for s in stars if s["folio"] in pages and s["locus"] < len(pages[s["folio"]])]
        if tname == "IT2a":  # line counts differ on f106r: drop that page (index alignment not guaranteed)
            keep = [s for s in keep if s["folio"] != "f106r"]
        lines = [list(pages[s["folio"]][s["locus"]]) for s in keep]
        emit(f"\n--- {tname}: stars with a line {len(keep)}; empty first lines {sum(not l for l in lines)}")
        if tname == "ZL3b_eva":
            cs = [frozenset(seg.segment(w)[1] for w in ln) for ln in lines]
            scored = [i for i, s in enumerate(keep) if s["filled"] >= 0 and (chosen == "a" or s["para_start"])]
            df = Counter(c for i in scored for c in cs[i])
            target = PLANT_DF * len(scored)
            core = sorted(df, key=lambda c: (abs(df[c] - target), c))[0]
            emit(f"CONTROLS on real first lines (subset {chosen}); planted core c*='{core}' df {df[core]}/{len(scored)}")
            ctrl = {}
            for mode in ("plant", "null"):
                st = plant_labels(keep, cs, core, rng, mode)
                for s in st:
                    if s["filled"] < 0:
                        s["planted"] = -1
                ctrl[mode] = analysis(st, lines, seg, "planted", chosen, rng, BASE_COLS_FILLED, N_PERM,
                                      tag=f"control-{mode}")
            controls_ok = all(r["passed"] for r in ctrl["plant"].values()) and \
                not any(r["passed"] for r in ctrl["null"].values())
            emit(f"CALL controls_ok = {controls_ok}")
            emit(f"\nPRIMARY filled/hollow, subset ({chosen}) [acceptance]")
            prim = analysis(keep, lines, seg, "filled", chosen, rng, BASE_COLS_FILLED, N_PERM, tag="ZL3b-primary")
            other = "b" if chosen == "a" else "a"
            emit(f"\nDESCRIPTIVE filled/hollow, subset ({other})")
            analysis(keep, lines, seg, "filled", other, rng, BASE_COLS_FILLED, N_PERM, tag=f"ZL3b-subset-{other}")
            emit("\nDESCRIPTIVE tailed/plain (secondary class, page term in baseline), subset (a)")
            analysis(keep, lines, seg, "tailed", "a", rng, BASE_COLS_TAILED, N_PERM, tag="ZL3b-tailed")
            results["ZL3b"] = prim
        else:
            emit(f"DESCRIPTIVE filled/hollow on {tname}, subset ({chosen})")
            results[tname] = analysis(keep, lines, seg, "filled", chosen, rng, BASE_COLS_FILLED, N_PERM, tag=tname)
    a_pass = results["ZL3b"]["A_cores"]["passed"]
    b_pass = results["ZL3b"]["B_3grams"]["passed"]
    emit(f"\nCALL A_cores_pass = {a_pass}")
    emit(f"CALL B_3grams_pass = {b_pass}")
    emit(f"CALL controls_ok = {controls_ok}")
    if not controls_ok:
        verdict = "INCONCLUSIVE (controls failed)"
    elif a_pass and b_pass:
        verdict = "POSITIVE (both representations; next step is the key route, not attempted here)"
    else:
        verdict = "NEGATIVE at adequate power (stop the marker-prediction line; no variants)"
    emit(f"VERDICT: {verdict}")
    emit(f"end {now()}  elapsed {time.time() - t_start:.0f}s  free RAM {psutil.virtual_memory().available / 1e9:.2f} GB")
    write_new(RESULTS, "\n".join(LOG) + "\n")
    (OUT / "summary.json").write_bytes(json.dumps(results, indent=1, default=str).encode("utf-8")) \
        if not (OUT / "summary.json").exists() else None


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    {"prep": prep, "fixture": fixture, "real": real}.get(stage, lambda: sys.exit("usage: prep|fixture|real"))()
