"""s56 -- core repetition as a function of distance (refractory zone vs burstiness vs copy-from-line-above).

PRE-REGISTERED QUESTION (frozen in s56_core_repetition_lag.prereg.sha256 before any real-text scoring):
"How does core repetition depend on distance?  Do Voynich word cores avoid recently used cores at short range
(d = 1, 2) and return at medium range (d in 3..20) -- a refractory zone -- and is that pattern absent from every
class of built text?"

Method (fixed before the run)
  Texts: Voynich ZL3b_eva (all pages; A-only and B-only pages beside), RF1b, IT2a (data/translit/*.meta.json);
    the 30 s49 class texts (runs/s49/labels.json classes LANG, CIPH, CODE, GEN, GIB); the s36 two-layer producers
    in runs/s49 (all *G2layer* files -> class 2LAYER_G, all *L2layer* files -> 2LAYER_L; the seed-1 ZL3b pair is
    also a GEN / CIPH member); real-line controls data/controls_realline/cremma_prose15 (Latin prose pool) and
    italian_dante (full Dante).  runs/s49 is read only.
  Units: (a) core = scoreboard/metrics_new.SlotSegmenter fitted on the tokens of the text's own training pages
    (g1_edge_joint.split_names(by)[0], random.Random(20261017), 80 % of pages) and applied to every token;
    for Voynich A-only / B-only the full-text 166-page ZL3b fit is used; (b) whole word type.
  Stream: per page, the lines concatenated in reading order (crossing line ends); pages never joined.
  Statistic: for lag d = 1..50, obs(d) = number of positions t with u[t] == u[t+d] within a page, summed over
    pages; exp(d) = the same count averaged over 200 within-page token shuffles (each page's tokens permuted,
    line lengths kept; np.random.default_rng(20261017 + text index)); ratio R(d) = obs(d) / exp(d).
    Within-line variant (d = 1..6): only pairs with both tokens on the same line, same shuffle null.
    Same-x on line n-1 (s35 definition, token-index proxy): s35 compares a token with the nearest token on line
    n-1 within 0.5 mean token width (pixel cx, Voynich only); built texts have no coordinates, so x is the token
    index on its line (one token = one width) and the same-x partner is the token with the same index on line
    n-1 (if that line is long enough); off-x = partners at index distance 3..5 (s35 off_column 3W-5W).
    Ratio = obs / shuffle expectation, pooled over all such pairs.
    Frequency-conditioned variant: only pairs whose first member's unit is NOT among the 20 most frequent units
    of the text (positions kept, so d keeps its meaning), same shuffle null.
  Interval: page subsampling, 80 % of pages without replacement, 500 draws (np.random.default_rng(20261017));
    ratio = sum obs / sum exp over the drawn pages; [2.5 %, 97.5 %] percentiles.
  Predictions (fixed), decided on ZL3b, unit = core, crossing-line profile; RF1b / IT2a / word unit /
    top-20-excluded printed beside:
    P1 refractory: R(1) < 1 and R(2) < 1 with both interval upper bounds < 1, AND max R(d) over d = 3..20 >= 1
       (point value).  PASS / FAIL.
    P2 uniqueness: for each class (LANG, CIPH, CODE, GEN, GIB, 2LAYER_G, 2LAYER_L) take the medians over the
       class's texts of R(1), of the R(1) interval upper bound, and of max R(3..20); the class "shows the
       pattern" if median R(1) < 1 AND median upper bound < 1 AND median max R(3..20) >= 1.  P2 PASS if no class
       shows it.  The per-text pattern flag (same rule on the single text) and counts per class are printed.
    The two real-line controls are printed as references (not a class).
  Fixture: `--fixture` runs the same code on synthetic texts (iid, refractory, bursty, copy-from-line-above)
    and checks the profile reacts as built; run before the stub is frozen.

Run:    python -I s56_core_repetition_lag.py [--fixture]
Writes: results_s56.txt, runs/s56/profiles.json (real run); runs/s56/fixture.txt (fixture).  Nothing else.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import time
from collections import Counter, OrderedDict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

OUT = ROOT / "results_s56.txt"
RUNS = ROOT / "runs" / "s56"
STUB = ROOT / "s56_core_repetition_lag.prereg.sha256"
SELF = ROOT / "s56_core_repetition_lag.py"
SEED = 20261017
N_SHUF = 200
N_BOOT = 500
SUB_FRAC = 0.8
DMAX = 50
DLINE = 6
TOPK = 20
SHOW_D = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 50]
CLASSES = ["LANG", "CIPH", "CODE", "GEN", "GIB", "2LAYER_G", "2LAYER_L"]
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


def load_by_path(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


def load_meta(path: Path):
    """-> OrderedDict page -> list of lines (token lists), plus page -> lang."""
    d = json.loads(path.read_text(encoding="utf-8"))
    by, lang = OrderedDict(), {}
    for p in d["pages"]:
        lines = [[w for w in l if w] for l in p["lines"]]
        lines = [l for l in lines if l]
        if lines:
            by[p["id"]] = lines
            lang[p["id"]] = p.get("lang", "?")
    return by, lang


# ---------------------------------------------------------------- core statistic
def page_counts(units, rng, topset):
    """units: list of lines (unit ids, ints).  Returns dict of obs/exp arrays for this page.
    Keys: lag (DMAX), lagx (DMAX, top-k excluded), line (DLINE), linex (DLINE), samex, offx (scalars as len-1)."""
    lens = [len(l) for l in units]
    s = np.array([u for l in units for u in l], dtype=np.int64)
    N = len(s)
    line_id = np.repeat(np.arange(len(lens)), lens)
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    # same-x / off-x pairs (index proxy) between line k-1 and line k
    sx_a, sx_b, ox_a, ox_b = [], [], [], []
    for k in range(1, len(lens)):
        a0, b0 = starts[k - 1], starts[k]
        for i in range(lens[k]):
            if i < lens[k - 1]:
                sx_a.append(a0 + i); sx_b.append(b0 + i)
            for j in range(lens[k - 1]):
                if 3 <= abs(i - j) <= 5:
                    ox_a.append(a0 + j); ox_b.append(b0 + i)
    sx_a, sx_b, ox_a, ox_b = map(lambda v: np.array(v, dtype=np.int64), (sx_a, sx_b, ox_a, ox_b))
    # shuffles: matrix (N_SHUF+1) x N, row 0 = observed
    perms = np.argsort(rng.random((N_SHUF, N)), axis=1)
    M = np.vstack([s[None, :], s[perms]])
    notop = ~np.isin(M, topset) if len(topset) else np.ones_like(M, dtype=bool)
    res = {k: np.zeros((2, n)) for k, n in (("lag", DMAX), ("lagx", DMAX), ("line", DLINE), ("linex", DLINE),
                                            ("samex", 1), ("offx", 1), ("samexx", 1))}
    for d in range(1, min(DMAX, N - 1) + 1):
        eq = M[:, :-d] == M[:, d:]
        eqx = eq & notop[:, :-d]
        c = eq.sum(1); cx = eqx.sum(1)
        res["lag"][0, d - 1] = c[0]; res["lag"][1, d - 1] = c[1:].mean()
        res["lagx"][0, d - 1] = cx[0]; res["lagx"][1, d - 1] = cx[1:].mean()
        if d <= DLINE:
            same = line_id[:-d] == line_id[d:]
            if same.any():
                cl = eq[:, same].sum(1); clx = eqx[:, same].sum(1)
                res["line"][0, d - 1] = cl[0]; res["line"][1, d - 1] = cl[1:].mean()
                res["linex"][0, d - 1] = clx[0]; res["linex"][1, d - 1] = clx[1:].mean()
    if len(sx_a):
        e = M[:, sx_a] == M[:, sx_b]
        c = e.sum(1); res["samex"][:, 0] = (c[0], c[1:].mean())
        ex = e & notop[:, sx_b]
        c = ex.sum(1); res["samexx"][:, 0] = (c[0], c[1:].mean())
    if len(ox_a):
        c = (M[:, ox_a] == M[:, ox_b]).sum(1); res["offx"][:, 0] = (c[0], c[1:].mean())
    return res


def profile(by_units, seed):
    """by_units: OrderedDict page -> lines of unit ids.  Returns per-page stacked arrays."""
    rng = np.random.default_rng(seed)
    freq = Counter(u for lines in by_units.values() for l in lines for u in l)
    topset = np.array([u for u, _ in freq.most_common(TOPK)], dtype=np.int64)
    per = [page_counts(lines, rng, topset) for lines in by_units.values()]
    stacked = {k: np.stack([p[k] for p in per]) for k in per[0]}   # pages x 2 x n
    return stacked, len(freq)


def ratios(st, idx=None):
    out = {}
    for k, a in st.items():
        b = a if idx is None else a[idx]
        o, e = b[:, 0].sum(0), b[:, 1].sum(0)
        out[k] = np.where(e > 0, o / np.where(e > 0, e, 1), np.nan)
    return out


def boot(st, seed):
    n = next(iter(st.values())).shape[0]
    k = max(1, int(round(SUB_FRAC * n)))
    rng = np.random.default_rng(seed)
    draws = {key: [] for key in st}
    for _ in range(N_BOOT):
        idx = rng.choice(n, size=k, replace=False)
        r = ratios(st, idx)
        for key in st:
            draws[key].append(r[key])
    return {key: (np.nanpercentile(np.array(v), 2.5, axis=0), np.nanpercentile(np.array(v), 97.5, axis=0)) for key, v in draws.items()}


def to_units(by, mode, seg):
    vocab = {}
    out = OrderedDict()
    for p, lines in by.items():
        ul = []
        for l in lines:
            ul.append([vocab.setdefault(seg.segment(w)[1] if mode == "core" else w, len(vocab)) for w in l])
        out[p] = ul
    return out


def analyse(name, by, seg, mode, seed):
    bu = to_units(by, mode, seg)
    st, ntypes = profile(bu, seed)
    r = ratios(st)
    ci = boot(st, seed + 1)
    ntok = sum(len(l) for ls in by.values() for l in ls)
    lag, lo, hi = r["lag"], ci["lag"][0], ci["lag"][1]
    mx = float(np.nanmax(lag[2:20]))
    flag = bool(lag[0] < 1 and hi[0] < 1 and mx >= 1)
    p1 = bool(lag[0] < 1 and lag[1] < 1 and hi[0] < 1 and hi[1] < 1 and mx >= 1)
    return dict(name=name, mode=mode, pages=len(by), tokens=ntok, types=ntypes, r=r, ci=ci, max3_20=mx,
                argmax3_20=int(np.nanargmax(lag[2:20]) + 3), flag=flag, p1=p1,
                raw=st)


# ---------------------------------------------------------------- printing
def fpc(res, i, key="lag"):
    """Beside-only: the 80 %-without-replacement subsample spread is about sqrt((1-f)/f) = 0.5 of a sampling
    interval; this rescales the percentile distances from the full-text value by sqrt(f/(1-f)) = 2."""
    c = res["r"][key][i]; lo, hi = res["ci"][key][0][i], res["ci"][key][1][i]
    k = np.sqrt(SUB_FRAC / (1 - SUB_FRAC))
    return f"[{c - k * (c - lo):.3f},{c + k * (hi - c):.3f}]"


def fmt(x):
    return "   nan" if x is None or not np.isfinite(x) else f"{x:6.3f}"


def head_row(label_w=34):
    return f"{'text':{label_w}} {'unit':4} | " + " ".join(f"{'d' + str(d):>6}" for d in SHOW_D) + " | max3-20 @d"


def prof_row(res, key="lag", label_w=34):
    r = res["r"][key]
    return (f"{res['name'][:label_w]:{label_w}} {res['mode']:4} | " + " ".join(fmt(r[d - 1]) for d in SHOW_D)
            + f" | {fmt(float(np.nanmax(r[2:20])))} @{int(np.nanargmax(r[2:20]) + 3)}")


def ci_lines(res, key="lag"):
    lo, hi = res["ci"][key]
    return "    interval: " + "  ".join(f"d{d}:[{lo[d - 1]:.3f},{hi[d - 1]:.3f}]" for d in SHOW_D)


def line_row(res, label_w=34):
    r, rx = res["r"]["line"], res["r"]["linex"]
    lo, hi = res["ci"]["line"]
    sx, ox, sxx = res["r"]["samex"][0], res["r"]["offx"][0], res["r"]["samexx"][0]
    slo, shi = res["ci"]["samex"][0][0], res["ci"]["samex"][1][0]
    return (f"{res['name'][:label_w]:{label_w}} {res['mode']:4} | " + " ".join(fmt(r[d]) for d in range(DLINE))
            + f" | {fmt(r[0])} [{lo[0]:.3f},{hi[0]:.3f}] | ex-top20 " + " ".join(fmt(rx[d]) for d in range(3))
            + f" | same-x {fmt(sx)} [{slo:.3f},{shi:.3f}] off-x {fmt(ox)} same-x ex-top20 {fmt(sxx)}")


# ---------------------------------------------------------------- fixture
def fixture():
    lines_out = []

    def say(s):
        print(s, flush=True)
        lines_out.append(s)

    rng = random.Random(1)
    V = [f"w{i}" for i in range(60)]
    wts = [1 / (i + 1) for i in range(60)]

    def make(kind):
        by = OrderedDict()
        for p in range(120):
            lines, hist = [], []
            for li in range(12):
                L = []
                for i in range(8):
                    if kind == "refractory":
                        while True:
                            w = rng.choices(V, wts)[0]
                            if w not in hist[-2:]:
                                break
                    elif kind == "bursty":
                        w = hist[-1] if hist and rng.random() < 0.15 else rng.choices(V, wts)[0]
                    elif kind == "copy":
                        w = lines[-1][i] if lines and rng.random() < 0.2 else rng.choices(V, wts)[0]
                    else:
                        w = rng.choices(V, wts)[0]
                    L.append(w); hist.append(w)
                lines.append(L)
            by[f"p{p}"] = lines
        return by

    class Ident:
        def segment(self, w):
            return ("", w, "")

    ok = True
    for kind in ("iid", "refractory", "bursty", "copy"):
        res = analyse(kind, make(kind), Ident(), "word", SEED)
        say(prof_row(res)); say(ci_lines(res)); say(line_row(res))
        r = res["r"]["lag"]; sx = res["r"]["samex"][0]
        if kind == "iid":
            c = abs(r[0] - 1) < 0.05 and abs(r[1] - 1) < 0.05 and abs(sx - 1) < 0.08 and not res["p1"]
        elif kind == "refractory":
            c = r[0] < 0.2 and r[1] < 0.2 and res["max3_20"] >= 1 and res["p1"]
        elif kind == "bursty":
            c = r[0] > 1.5 and not res["p1"]
        else:
            # the within-page shuffle null is zero-sum over lags (sum_d obs = sum_d exp per page), so a same-x copy
            # excess at d ~ line length forces R < 1 at every other lag, d = 1, 2 included: the P1 rule can be met
            # without any refractory mechanism.  Expected here: same-x > 1.5 and a flat deficit (R1 ~ R(21..50)).
            c = sx > 1.5 and abs(r[0] - np.nanmedian(r[20:50])) < 0.05
        say(f"  fixture {kind}: {'OK' if c else 'FAIL'} (P1 flag {res['p1']}, R1 {r[0]:.3f}, R2 {r[1]:.3f}, max3-20 {res['max3_20']:.3f}, "
            f"same-x {sx:.3f}, R1/med R(21..50) {r[0] / np.nanmedian(r[20:50]):.3f}, fpc-rescaled R1 interval {fpc(res, 0)})")
        ok &= c
    say(f"FIXTURE {'PASS' if ok else 'FAIL'}")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture.txt").write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")
    return ok


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    emit("s56 -- core repetition by distance (refractory zone test)")
    emit(f"date: {clock()}")
    emit(f"sha256 s56_core_repetition_lag.py: {sha256(SELF)}")
    emit(f"stub_match: {stub_match()}")
    emit(f"settings: lags 1..{DMAX} crossing line ends within page; within-line d=1..{DLINE}; same-x = same token index on line n-1 "
         f"(off-x = index distance 3..5); null = {N_SHUF} within-page token shuffles; interval = {N_BOOT} draws of {int(SUB_FRAC * 100)} % "
         f"of pages without replacement; frequency-conditioned = pairs whose first member is not in the text's top {TOPK} units")
    g1 = load_by_path("g1_edge_joint_s56", ROOT / "g1_edge_joint.py")
    M = load_by_path("metrics_new_s56", ROOT / "scoreboard" / "metrics_new.py")

    def fit(by):
        train, _ = g1.split_names(by)
        return M.SlotSegmenter([w for p in train for l in by[p] for w in l]), len(train)

    texts = []   # (name, cls, path)
    for T, f in (("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")):
        texts.append((T, "VOYNICH", ROOT / "data" / "translit" / f"{f}.meta.json"))
    labels = json.loads((ROOT / "runs" / "s49" / "labels.json").read_text(encoding="utf-8"))["labels"]
    for n, c in labels.items():
        if "G2layer" in n:
            cls = "2LAYER_G"
        elif "L2layer" in n:
            cls = "2LAYER_L"
        else:
            cls = c
        texts.append((n, cls, ROOT / "runs" / "s49" / f"{n}.meta.json"))
    texts.append(("realline_cremma_prose15", "REAL", ROOT / "data" / "controls_realline" / "cremma_prose15.meta.json"))
    texts.append(("realline_italian_dante", "REAL", ROOT / "data" / "controls_realline" / "italian_dante.meta.json"))
    # s49 class texts in GEN/CIPH that are also 2-layer seed-1 members
    extra_member = {"gen_G2layer_ZL3b_s1": "GEN", "ciph_L2layer_ZL3b_s1": "CIPH"}

    results = []
    for ti, (name, cls, path) in enumerate(texts):
        tt = time.time()
        by, lang = load_meta(path)
        seg, ntr = fit(by)
        for mode in ("core", "word"):
            res = analyse(name, by, seg, mode, SEED + 1000 * ti + (0 if mode == "core" else 500))
            res["cls"] = cls; res["train_pages"] = ntr; res["n_prefix"] = len(seg.prefixes); res["n_suffix"] = len(seg.suffixes)
            results.append(res)
        if name == "ZL3b":
            for sub in ("A", "B"):
                bys = OrderedDict((p, l) for p, l in by.items() if lang[p] == sub)
                for mode in ("core", "word"):
                    res = analyse(f"ZL3b-{sub}only", bys, seg, mode, SEED + 1000 * ti + (100 if sub == "A" else 200) + (0 if mode == "core" else 50))
                    res["cls"] = "VOYNICH"; res["train_pages"] = ntr; res["n_prefix"] = len(seg.prefixes); res["n_suffix"] = len(seg.suffixes)
                    results.append(res)
        print(f"  [{ti + 1}/{len(texts)}] {name} {time.time() - tt:.1f}s", flush=True)

    R = {(r["name"], r["mode"]): r for r in results}
    emit("")
    emit("=== Texts (core inventory from each text's own training-page SlotSegmenter fit) ===")
    for r in results:
        if r["mode"] == "core":
            emit(f"  {r['name']:34} {r['cls']:9} pages {r['pages']:4} tokens {r['tokens']:6} cores {r['types']:5} words {R[(r['name'], 'word')]['types']:5} "
                 f"(train pages {r['train_pages']}, {r['n_prefix']} prefix / {r['n_suffix']} suffix candidates)")

    for key, title in (("lag", "R(d) = obs/shuffle-expected repetition, reading order within page, crossing line ends"),
                       ("lagx", "R(d) excluding pairs whose first member is a top-20 unit")):
        emit("")
        emit(f"=== {title} ===")
        emit(head_row())
        for r in results:
            if r["cls"] in ("VOYNICH", "REAL"):
                emit(prof_row(r, key))
                emit(ci_lines(r, key))
        emit("  -- built texts --")
        for c in CLASSES:
            for r in results:
                if r["cls"] == c:
                    emit(prof_row(r, key) + f"  [{c}] R1 int [{r['ci'][key][0][0]:.3f},{r['ci'][key][1][0]:.3f}]")

    emit("")
    emit("=== Within-line R(d) d=1..6 | d1 interval | within-line ex-top20 d1..3 | same-x on line n-1 (index proxy) ===")
    for r in results:
        emit(line_row(r))

    emit("")
    emit("=== Per-class medians (unit core / word), crossing-line profile ===")
    emit(f"{'class':10} {'unit':4} {'n':>2} | " + " ".join(f"{'d' + str(d):>6}" for d in SHOW_D)
         + " | medR1hi medMax3-20 | line-d1 same-x | ex-top20 d1 d2 | pattern  texts-flagged")
    shows = {}
    for mode in ("core", "word"):
        for c in CLASSES:
            members = [r for r in results if r["mode"] == mode and (r["cls"] == c or extra_member.get(r["name"]) == c)]
            if not members:
                continue
            med = np.nanmedian(np.array([m["r"]["lag"] for m in members]), axis=0)
            medx = np.nanmedian(np.array([m["r"]["lagx"] for m in members]), axis=0)
            mhi = float(np.median([m["ci"]["lag"][1][0] for m in members]))
            mmx = float(np.median([m["max3_20"] for m in members]))
            mline = float(np.nanmedian([m["r"]["line"][0] for m in members]))
            msx = float(np.nanmedian([m["r"]["samex"][0] for m in members]))
            mloc = float(np.median([m["r"]["lag"][0] / np.nanmedian(m["r"]["lag"][20:50]) for m in members]))
            pat = bool(med[0] < 1 and mhi < 1 and mmx >= 1)
            shows[(c, mode)] = pat
            nfl = sum(m["flag"] for m in members)
            emit(f"{c:10} {mode:4} {len(members):2} | " + " ".join(fmt(med[d - 1]) for d in SHOW_D)
                 + f" | {mhi:7.3f} {mmx:10.3f} | {fmt(mline)} {fmt(msx)} | {fmt(medx[0])} {fmt(medx[1])} | {'YES' if pat else 'no ':3}      {nfl}/{len(members)} | R1/medR(21..50) {mloc:.3f}")

    emit("")
    emit("=== Readings ===")
    for mode in ("core", "word"):
        for nm in ("ZL3b", "RF1b", "IT2a", "ZL3b-Aonly", "ZL3b-Bonly"):
            r = R[(nm, mode)]
            lag, (lo, hi) = r["r"]["lag"], r["ci"]["lag"]
            emit(f"  {nm:11} {mode:4}: R1 {lag[0]:.3f} [{lo[0]:.3f},{hi[0]:.3f}]  R2 {lag[1]:.3f} [{lo[1]:.3f},{hi[1]:.3f}]  "
                 f"max R(3..20) {r['max3_20']:.3f} @d{r['argmax3_20']}  -> P1 rule {'met' if r['p1'] else 'not met'}"
                 f"  | fpc-rescaled R1 {fpc(r, 0)} R2 {fpc(r, 1)}  | R1/med R(21..50) {lag[0] / np.nanmedian(lag[20:50]):.3f} R2/med {lag[1] / np.nanmedian(lag[20:50]):.3f}"
                 f"  | ex-top20 R1 {r['r']['lagx'][0]:.3f} [{r['ci']['lagx'][0][0]:.3f},{r['ci']['lagx'][1][0]:.3f}] R2 {r['r']['lagx'][1]:.3f}")
    z = R[("ZL3b", "core")]
    lag, (lo, hi) = z["r"]["lag"], z["ci"]["lag"]
    emit(f"P1 (refractory; ZL3b, core, crossing line): {'PASS' if z['p1'] else 'FAIL'}  "
         f"margins: 1 - R1hi = {1 - hi[0]:+.3f}, 1 - R2hi = {1 - hi[1]:+.3f}, max R(3..20) - 1 = {z['max3_20'] - 1:+.3f} (d={z['argmax3_20']})")
    sc = [c for c in CLASSES if shows.get((c, "core"))]
    emit(f"P2 (uniqueness; core unit, class medians): {'PASS' if not sc else 'FAIL'}  classes showing the pattern: {sc or 'none'}  "
         f"(word unit, beside: {[c for c in CLASSES if shows.get((c, 'word'))] or 'none'})")
    for nm in ("realline_cremma_prose15", "realline_italian_dante"):
        for mode in ("core", "word"):
            r = R[(nm, mode)]
            emit(f"  reference {nm} {mode}: R1 {r['r']['lag'][0]:.3f} [{r['ci']['lag'][0][0]:.3f},{r['ci']['lag'][1][0]:.3f}] "
                 f"max R(3..20) {r['max3_20']:.3f}; pattern flag {r['flag']}; R1/med R(21..50) {r['r']['lag'][0] / np.nanmedian(r['r']['lag'][20:50]):.3f}")
    emit("  caveat (fixture, fixed before the run): the within-page shuffle null is zero-sum over lags, so R(1), R(2) < 1 can be forced by an")
    emit("  excess elsewhere (e.g. same-x copying at d ~ line length); R1/med R(21..50) near 1 means a flat deficit, well below 1 a local one.")
    emit("  The 80 % subsample interval is ~half a sampling interval; fpc-rescaled intervals (x2 distances) are printed beside, not used by P1/P2.")
    if not z["p1"]:
        emit("  (P1 FAIL makes P2 moot as a uniqueness claim for a pattern Voynich does not show; P2 is printed as measured.)")

    RUNS.mkdir(parents=True, exist_ok=True)
    dump = []
    for r in results:
        dump.append(dict(name=r["name"], cls=r["cls"], mode=r["mode"], pages=r["pages"], tokens=r["tokens"], types=r["types"],
                         ratios={k: [None if not np.isfinite(x) else float(x) for x in v] for k, v in r["r"].items()},
                         ci={k: [[float(x) for x in v[0]], [float(x) for x in v[1]]] for k, v in r["ci"].items()},
                         obs={k: v[:, 0].sum(0).tolist() for k, v in r["raw"].items()},
                         exp={k: v[:, 1].sum(0).tolist() for k, v in r["raw"].items()},
                         flag=r["flag"], p1=r["p1"]))
    (RUNS / "profiles.json").write_text(json.dumps(dump, indent=1), encoding="utf-8", newline="\n")
    emit("")
    emit(f"elapsed: {time.time() - t0:.1f} s")
    emit(f"paths: {OUT}, {RUNS / 'profiles.json'}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--fixture" in sys.argv:
        sys.exit(0 if fixture() else 1)
    main()
