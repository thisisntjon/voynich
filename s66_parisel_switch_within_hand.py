#!/usr/bin/env python
"""
S66: Parisel's per-folio cho/che "boolean switch", tested WITHIN Davis hand.

PRE-REGISTRATION (frozen in s66_parisel_switch_within_hand.prereg.sha256 before the real run;
the stub covers this file and its one local import, tools/ivtff_to_meta.py).

Source of the question: workflow/research/literature-2026-10-18.md, section 1a and follow-up 1.
Parisel (arXiv 2604.25979v2, sec. 2.9 / 5) reports a per-folio switch f = cho/(cho+che) that is
bimodal (binomial-mixture dAIC 2,549; p1 0.68, p0 0.16).  c-374 (results_s51_*.txt Part 3B):
Davis hand 1 is all Currier A, hands 2 and 3 are Currier B, so the switch may be scribe identity.

STATISTIC (Parisel sec. 2.9, word level, verbatim rule): a word is cho-type if it contains "cho" or
"sho" but not "che" or "she"; che-type if it contains "che" or "she" but not "cho" or "sho"; words with
both or neither are excluded.  Per unit: n = n_cho + n_che, f = n_cho / n.  Secondary (reported, no
verdict): glyph-event count, every [cs]h followed by o (cho event) or e (che event).
d/l (Parisel sec. 3.1 / 7): r_dl = count(d) / (count(d) + count(l)) per unit, >= 20 combined.

DATA: IVTFF files parsed with tools/ivtff_to_meta.convert (P* loci, the scoreboard meta rules):
ZL3b = data/ZL3b-n.txt, RF1b = data/external/voynich-nu-ivtff/RF1b-er.txt,
IT2a = data/external/voynich-nu-ivtff/IT2a-n.txt.  Hands/languages/sections are the IVTFF page
variables $H/$L/$I (the source of the c-374 hand mapping, via the meta.json files).
UNIT = folio side: multi-panel pages (f67r1, f67r2 ...) are merged into f67r (Parisel sec. 9.4 merged
multi-panel folios).  A merged unit whose panels disagree on $H gets hand "mix" (pooled only).
Units with n >= 20 classified words enter.

GROUPS: hand 1 (all its units, Currier A), hand 2 restricted to $L=B, hand 3 restricted to $L=B,
and POOLED = all units of every hand.

TESTS per group:
  (1) beta-binomial mixtures, k=1 (2 params) vs k=2 (5 params), ML via multi-start EM + direct
      polish; dAIC = AIC(k=1) - AIC(k=2) (positive favours two states).  Parisel's own binomial
      mixture (1 vs 3 params) is also reported as a replication, not used for the verdict.
  (2) overdispersion phi = Pearson X^2 / (K-1) against binomial; null = 2000 permutations of the
      group's classified word tokens across its units (unit sizes kept); p = (1+#null>=obs)/2001.
VERDICT (pre-registered):
  "switch within hand"  if dAIC_BB >= 10 in hand 1 AND in at least one of hand 2/hand 3 on ZL3b, and
                        the same holds on RF1b and IT2a;
  "switch is scribe"    if on all three files no within-hand group reaches 10 and POOLED does;
  otherwise "mixed".
CONTROLS (ZL3b unit sizes per group, 20 replicates per group per control, SEED fixed):
  positive = planted two states, state 1 with prob 0.521 (Parisel theta1), per-unit p ~ Beta with
             mean 0.68 / 0.16 and intraclass rho 0.02, k ~ Bin(n, p); correct call dAIC_BB >= 10.
  negative = one state, mean = the group's pooled cho rate, rho = the group's fitted k=1 BB rho
             (clipped to [0.005, 0.30]); correct call dAIC_BB < 10.
  Controls pass if >= 18/20 replicates are called correctly in every group for both controls;
  otherwise the verdict is "inconclusive: controls failed".
ALSO: eta^2 of unit f on hand, Currier language, section (one-way, unweighted, units with n >= 20);
text histograms per hand; bimodality coefficient; r(f, d/l).

Usage: python s66_parisel_switch_within_hand.py --make-fixture   (writes runs/s66/fixture.txt)
       python s66_parisel_switch_within_hand.py --fixture runs/s66/fixture.txt
       python s66_parisel_switch_within_hand.py                  (real data -> results_s66.txt)
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import ivtff_to_meta  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SELF = ROOT / "s66_parisel_switch_within_hand.py"
STUB = ROOT / "s66_parisel_switch_within_hand.prereg.sha256"
OUT_REAL = ROOT / "results_s66.txt"
RUNDIR = ROOT / "runs" / "s66"
SEED = 20261018
MIN_N = 20
N_PERM = 2000
N_CTRL = 20
DAIC_T = 10.0
SOURCES = [("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
           ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"),
           ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt")]

LOG: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return time.strftime("%Y-%m-%d %H:%M:%S") + " (time.strftime)"


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


# ------------------------------------------------------------------ units
def unit_key(pid: str) -> str:
    m = re.match(r"^(f\d+[rv])\d*$", pid)
    return m.group(1) if m else pid


def classify(w: str) -> int:
    o = ("cho" in w) or ("sho" in w)
    e = ("che" in w) or ("she" in w)
    if o and not e:
        return 1
    if e and not o:
        return 0
    return -1


def build_units(path: Path) -> list[dict]:
    d = ivtff_to_meta.convert(path)
    units: dict[str, dict] = {}
    order = []
    for p in d["pages"]:
        k = unit_key(p["id"])
        if k not in units:
            units[k] = dict(id=k, hands=set(), langs=set(), secs=set(), words=[])
            order.append(k)
        u = units[k]
        u["hands"].add(p["hand"]); u["langs"].add(p["lang"]); u["secs"].add(p["section"])
        u["words"].extend(w for ln in p["lines"] for w in ln)
    out = []
    for k in order:
        u = units[k]
        cls = [classify(w) for w in u["words"]]
        n_cho = sum(1 for c in cls if c == 1)
        n_che = sum(1 for c in cls if c == 0)
        ev_o = sum(len(re.findall(r"[cs]ho", w)) for w in u["words"])
        ev_e = sum(len(re.findall(r"[cs]he", w)) for w in u["words"])
        nd = sum(w.count("d") for w in u["words"]); nl = sum(w.count("l") for w in u["words"])
        out.append(dict(
            id=k, hand=(next(iter(u["hands"])) if len(u["hands"]) == 1 else "mix"),
            lang=(next(iter(u["langs"])) if len(u["langs"]) == 1 else "mix"),
            sec=(next(iter(u["secs"])) if len(u["secs"]) == 1 else "mix"),
            n_tok=len(u["words"]), k=n_cho, n=n_cho + n_che, ev_k=ev_o, ev_n=ev_o + ev_e,
            dl=(nd / (nd + nl) if nd + nl >= 20 else None)))
    return out


# ------------------------------------------------------------------ models
def lchoose(n, k):
    return gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)


LB, UB = -4.0, 12.0


def bb_ll_vec(k, n, la, lb):
    a, b = math.exp(la), math.exp(lb)
    return lchoose(n, k) + betaln(k + a, n - k + b) - betaln(a, b)


def bb_fit_weighted(k, n, wts, x0):
    def nll(t):
        return -float(np.sum(wts * bb_ll_vec(k, n, t[0], t[1])))
    best = None
    for st in (x0, (0.0, 0.0)):
        r = minimize(nll, np.clip(st, LB, UB), method="L-BFGS-B", bounds=[(LB, UB)] * 2)
        if best is None or r.fun < best.fun:
            best = r
    return best.x


def mom_start(k, n, wts):
    p = float(np.sum(wts * k) / max(np.sum(wts * n), 1e-9))
    p = min(max(p, 0.02), 0.98)
    s = 20.0
    return (math.log(p * s), math.log((1 - p) * s))


def fit_bb1(k, n):
    w = np.ones(len(k))
    t = bb_fit_weighted(k, n, w, mom_start(k, n, w))
    ll = float(np.sum(bb_ll_vec(k, n, t[0], t[1])))
    return dict(ll=ll, la=t[0], lb=t[1], aic=2 * 2 - 2 * ll)


def mix2_ll(k, n, th):
    la1, lb1, la2, lb2, lw = th
    w = 1 / (1 + math.exp(-lw))
    l1 = bb_ll_vec(k, n, la1, lb1) + math.log(max(w, 1e-300))
    l2 = bb_ll_vec(k, n, la2, lb2) + math.log(max(1 - w, 1e-300))
    m = np.maximum(l1, l2)
    return m + np.log(np.exp(l1 - m) + np.exp(l2 - m)), l1, l2


def fit_bb2(k, n, one, rng):
    f = k / n
    starts = []
    for thr in (0.3, 0.5, 0.7, float(np.median(f))):
        g = (f > thr).astype(float)
        if 0 < g.sum() < len(g):
            starts.append(g)
    for _ in range(4):
        starts.append((rng.random(len(k)) < 0.5).astype(float))
    best = None
    for g in starts:
        r1 = g.copy()
        th = None
        for _it in range(60):
            r1 = np.clip(r1, 1e-6, 1 - 1e-6)
            t1 = bb_fit_weighted(k, n, r1, mom_start(k, n, r1))
            t2 = bb_fit_weighted(k, n, 1 - r1, mom_start(k, n, 1 - r1))
            wm = float(np.clip(r1.mean(), 1e-4, 1 - 1e-4))
            th = np.array([t1[0], t1[1], t2[0], t2[1], math.log(wm / (1 - wm))])
            tot, l1, l2 = mix2_ll(k, n, th)
            new = np.exp(l1 - tot)
            if np.max(np.abs(new - r1)) < 1e-5:
                r1 = new
                break
            r1 = new
        cand = th
        res = minimize(lambda t: -float(np.sum(mix2_ll(k, n, t)[0])), cand, method="L-BFGS-B",
                       bounds=[(LB, UB)] * 4 + [(-12, 12)])
        if best is None or res.fun < best[0]:
            best = (res.fun, res.x)
    # nested start: both components = the one-component fit
    th0 = np.array([one["la"], one["lb"], one["la"], one["lb"], 0.0])
    ll0 = float(np.sum(mix2_ll(k, n, th0)[0]))
    if -ll0 < best[0]:
        best = (-ll0, th0)
    ll = -best[0]
    th = best[1]
    a1, b1, a2, b2 = (math.exp(v) for v in th[:4])
    w = 1 / (1 + math.exp(-th[4]))
    comps = sorted([(a1 / (a1 + b1), w, 1 / (a1 + b1 + 1)), (a2 / (a2 + b2), 1 - w, 1 / (a2 + b2 + 1))],
                   reverse=True)
    return dict(ll=ll, aic=2 * 5 - 2 * ll, comps=comps)


def binom_mix(k, n):
    lc = lchoose(n, k)
    p = float(k.sum() / n.sum())
    ll1 = float(np.sum(lc + k * math.log(p) + (n - k) * math.log(1 - p)))
    best = -np.inf
    f = k / n
    for p1, p2 in ((0.7, 0.15), (0.6, 0.3), (float(np.quantile(f, 0.75)) + 1e-3, float(np.quantile(f, 0.25)) + 1e-3)):
        w = 0.5
        p1 = min(max(p1, 1e-3), 1 - 1e-3); p2 = min(max(p2, 1e-3), 1 - 1e-3)
        for _ in range(500):
            l1 = lc + k * math.log(p1) + (n - k) * math.log(1 - p1) + math.log(w)
            l2 = lc + k * math.log(p2) + (n - k) * math.log(1 - p2) + math.log(1 - w)
            m = np.maximum(l1, l2)
            tot = m + np.log(np.exp(l1 - m) + np.exp(l2 - m))
            r = np.exp(l1 - tot)
            w = float(np.clip(r.mean(), 1e-6, 1 - 1e-6))
            p1 = float(np.clip((r * k).sum() / max((r * n).sum(), 1e-9), 1e-6, 1 - 1e-6))
            p2 = float(np.clip(((1 - r) * k).sum() / max(((1 - r) * n).sum(), 1e-9), 1e-6, 1 - 1e-6))
        best = max(best, float(tot.sum()))
    return (2 * 1 - 2 * ll1) - (2 * 3 - 2 * best)


def daic_bb(k, n, rng):
    one = fit_bb1(k, n)
    two = fit_bb2(k, n, one, rng)
    a, b = math.exp(one["la"]), math.exp(one["lb"])
    return one["aic"] - two["aic"], one, two, 1 / (a + b + 1)


def phi_perm(k, n, rng):
    N = int(n.sum()); K = len(n)
    p = k.sum() / N
    def phi(kk):
        e = n * p
        return float(np.sum((kk - e) ** 2 / (e * (1 - p))) / (K - 1))
    obs = phi(k)
    toks = np.zeros(N, dtype=np.int64); toks[: int(k.sum())] = 1
    starts = np.concatenate([[0], np.cumsum(n)[:-1]]).astype(np.int64)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        pt = rng.permutation(toks)
        null[i] = phi(np.add.reduceat(pt, starts))
    return obs, float(np.median(null)), float(np.quantile(null, 0.99)), (1 + int(np.sum(null >= obs))) / (N_PERM + 1)


def bimod_coef(x):
    x = np.asarray(x, float); m = len(x)
    if m < 4:
        return float("nan")
    s = x.std(ddof=0)
    if s == 0:
        return float("nan")
    g = float(np.mean(((x - x.mean()) / s) ** 3)); ku = float(np.mean(((x - x.mean()) / s) ** 4)) - 3
    g = g * math.sqrt(m * (m - 1)) / (m - 2)
    ku = ((m + 1) * ku + 6) * (m - 1) / ((m - 2) * (m - 3))
    return (g * g + 1) / (ku + 3 * (m - 1) ** 2 / ((m - 2) * (m - 3)))


def eta2(y, groups):
    y = np.asarray(y, float)
    gm = y.mean(); sst = float(np.sum((y - gm) ** 2))
    ssb = 0.0
    for g in set(groups):
        idx = [i for i, v in enumerate(groups) if v == g]
        ssb += len(idx) * (y[idx].mean() - gm) ** 2
    return ssb / sst if sst > 0 else float("nan")


def hist_text(f):
    rows = []
    c = Counter(min(int(v * 10), 9) for v in f)
    for b in range(10):
        rows.append(f"      [{b/10:.1f},{(b+1)/10:.1f}{']' if b == 9 else ')'} {c[b]:3d} {'#' * c[b]}")
    return rows


# ------------------------------------------------------------------ groups
def groups_of(units, key="n"):
    ok = [u for u in units if u[key] >= MIN_N]
    return {
        "hand1": [u for u in ok if u["hand"] == "1"],
        "hand2B": [u for u in ok if u["hand"] == "2" and u["lang"] == "B"],
        "hand3B": [u for u in ok if u["hand"] == "3" and u["lang"] == "B"],
        "pooled": ok,
    }


def arr(us, kk="k", nn="n"):
    return np.array([u[kk] for u in us], float), np.array([u[nn] for u in us], float)


def analyse_file(label, units, rng):
    emit(f"\n=== {label}: {len(units)} units (folio sides, panels merged), "
         f"{sum(u['n_tok'] for u in units)} P-tokens, classified words {sum(u['n'] for u in units)} "
         f"(cho {sum(u['k'] for u in units)}), units with n>={MIN_N}: {sum(u['n'] >= MIN_N for u in units)}")
    emit(f"  hand x lang of entering units: "
         f"{dict(sorted(Counter((u['hand'], u['lang']) for u in units if u['n'] >= MIN_N).items()))}")
    G = groups_of(units)
    res = {}
    emit(f"  {'group':7s} {'K':>3s} {'N':>6s} {'mean f':>7s} {'BC':>6s} | {'dAIC_BB':>8s} {'rho1':>6s} "
         f"{'2-state means (w, rho)':34s} | {'dAIC_bin':>8s} | {'phi':>7s} {'null_med':>8s} {'q99':>6s} {'p':>7s}")
    for g, us in G.items():
        if len(us) < 5:
            emit(f"  {g:7s} K={len(us)} too few units")
            res[g] = float("nan")
            continue
        k, n = arr(us)
        d, one, two, rho1 = daic_bb(k, n, rng)
        db = binom_mix(k, n)
        ph, med, q99, pp = phi_perm(k, n, rng)
        bc = bimod_coef(k / n)
        cs = "; ".join(f"{m:.3f} ({w:.2f},{r:.3f})" for m, w, r in two["comps"])
        emit(f"  {g:7s} {len(us):3d} {int(n.sum()):6d} {float((k/n).mean()):7.3f} {bc:6.3f} | {d:+8.2f} {rho1:6.3f} "
             f"{cs:34s} | {db:+8.1f} | {ph:7.2f} {med:8.3f} {q99:6.3f} {pp:7.4f}")
        res[g] = d
    # secondary: glyph events
    Ge = groups_of(units, key="ev_n")
    emit("  secondary (glyph events [cs]h+o vs [cs]h+e, units with >=20 events):")
    for g, us in Ge.items():
        if len(us) < 5:
            continue
        k, n = arr(us, "ev_k", "ev_n")
        d, _, two, _ = daic_bb(k, n, rng)
        emit(f"    {g:7s} K={len(us):3d} N={int(n.sum()):6d} mean f_ev={float((k/n).mean()):.3f} dAIC_BB={d:+8.2f} "
             f"means {', '.join(f'{m:.3f}' for m, _, _ in two['comps'])}")
    # eta^2
    ok = [u for u in units if u["n"] >= MIN_N]
    fv = [u["k"] / u["n"] for u in ok]
    emit(f"  eta^2 of unit f (K={len(ok)}): hand {eta2(fv, [u['hand'] for u in ok]):.3f}  "
         f"Currier A/B {eta2(fv, [u['lang'] for u in ok]):.3f}  section {eta2(fv, [u['sec'] for u in ok]):.3f}")
    okab = [u for u in ok if u["lang"] in ("A", "B")]
    emit(f"    (units with $L in A/B only, K={len(okab)}: hand {eta2([u['k']/u['n'] for u in okab], [u['hand'] for u in okab]):.3f} "
         f"A/B {eta2([u['k']/u['n'] for u in okab], [u['lang'] for u in okab]):.3f} "
         f"section {eta2([u['k']/u['n'] for u in okab], [u['sec'] for u in okab]):.3f})")
    # d/l
    emit("  d/l ratio (units with n>=20 and d+l>=20):")
    for g, us in G.items():
        pr = [(u["k"] / u["n"], u["dl"]) for u in us if u["dl"] is not None]
        if len(pr) < 5:
            continue
        a = np.array(pr)
        r = float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]) if a[:, 1].std() > 0 and a[:, 0].std() > 0 else float("nan")
        emit(f"    {g:7s} K={len(pr):3d} mean d/l={a[:,1].mean():.3f} sd={a[:,1].std(ddof=1):.3f}  r(f, d/l)={r:+.3f}")
    # histograms
    emit("  per-hand histograms of unit f:")
    for h in sorted({u["hand"] for u in ok}):
        us = [u for u in ok if u["hand"] == h]
        emit(f"    hand {h} (K={len(us)}, langs {dict(Counter(u['lang'] for u in us))}):")
        for row in hist_text([u["k"] / u["n"] for u in us]):
            emit(row)
    return res, G


def run_controls(G, rng):
    emit("\n=== CONTROLS (ZL3b unit sizes per group, 20 replicates each) ===")
    all_ok = True
    for g, us in G.items():
        if len(us) < 5:
            continue
        k, n = arr(us)
        _, one, _, rho1 = daic_bb(k, n, rng)
        rho_neg = float(np.clip(rho1, 0.005, 0.30))
        mean_neg = float(k.sum() / n.sum())
        pos_ok = neg_ok = 0
        dp, dn = [], []
        for _ in range(N_CTRL):
            z = rng.random(len(n)) < 0.521
            mu = np.where(z, 0.68, 0.16)
            s = 1 / 0.02 - 1
            p = rng.beta(mu * s, (1 - mu) * s)
            kk = rng.binomial(n.astype(int), p).astype(float)
            d = daic_bb(kk, n, rng)[0]; dp.append(d); pos_ok += d >= DAIC_T
            s2 = 1 / rho_neg - 1
            p = rng.beta(np.full(len(n), mean_neg * s2), np.full(len(n), (1 - mean_neg) * s2))
            kk = rng.binomial(n.astype(int), p).astype(float)
            d = daic_bb(kk, n, rng)[0]; dn.append(d); neg_ok += d < DAIC_T
        ok = pos_ok >= 18 and neg_ok >= 18
        all_ok &= ok
        emit(f"  {g:7s} K={len(n):3d}: positive {pos_ok}/{N_CTRL} called (dAIC median {np.median(dp):+.1f}, min {min(dp):+.1f}); "
             f"negative (mean {mean_neg:.3f}, rho {rho_neg:.3f}) {neg_ok}/{N_CTRL} correct (dAIC median {np.median(dn):+.2f}, "
             f"max {max(dn):+.2f}) -> {'PASS' if ok else 'FAIL'}")
    emit(f"  controls: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


# ------------------------------------------------------------------ fixture
def make_fixture(path: Path) -> None:
    rng = np.random.default_rng(7)
    lines = ["#=IVTFF Eva- 2.0 M 3", "# s66 synthetic fixture: hand 1 (A) has a planted 2-state switch,"
             " hands 2 and 3 (B) are one state each"]
    stems_o = ["cho", "sho", "chol", "chor", "shody", "chody"]
    stems_e = ["chey", "shey", "chedy", "shedy", "cheol", "chekey"]
    other = ["daiin", "qokaiin", "ol", "ar", "okal", "dal", "lkam", "otedy"]
    fol = 1
    for hand, lang, nunits in (("1", "A", 30), ("2", "B", 20), ("3", "B", 14)):
        for u in range(nunits):
            if hand == "1":
                p = 0.70 if u % 2 == 0 else 0.15
            else:
                p = 0.45 if hand == "2" else 0.30
            side = "r" if u % 2 == 0 else "v"
            pid = f"f{fol}{side}"
            if side == "v":
                fol += 1
            lines.append(f"<{pid}>      <! $Q=A $P=A $F=a $B=1 $I=H $L={lang} $H={hand}>")
            for li in range(1, 9):
                ws = []
                for _ in range(8):
                    r = rng.random()
                    if r < 0.5:
                        ws.append(rng.choice(stems_o) if rng.random() < p else rng.choice(stems_e))
                    else:
                        ws.append(rng.choice(other))
                sep = "@" if li == 1 else "+"
                lines.append(f"<{pid}.{li},{sep}P0>      " + ".".join(ws))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {path}")


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=None)
    ap.add_argument("--make-fixture", action="store_true")
    a = ap.parse_args()
    if a.make_fixture:
        make_fixture(RUNDIR / "fixture.txt")
        return
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    emit("S66: Parisel's per-folio cho/che switch, within Davis hand")
    emit(f"start: {clock()}")
    emit(f"stub_match: {stub_match()}")
    emit(f"script sha256: {sha256(SELF)}  tools/ivtff_to_meta.py sha256: {sha256(ROOT / 'tools' / 'ivtff_to_meta.py')}")
    if a.fixture:
        srcs = [("FIXTURE", Path(a.fixture))]
        out = RUNDIR / "fixture_results.txt"
    else:
        srcs = SOURCES
        out = OUT_REAL
    for lab, p in srcs:
        emit(f"  source {lab}: {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p} sha256 {sha256(p)}")
    results = {}
    G_primary = None
    for lab, p in srcs:
        units = build_units(p)
        res, G = analyse_file(lab, units, rng)
        results[lab] = res
        if G_primary is None:
            G_primary = G
    ctrl = run_controls(G_primary, rng)

    def within(r):
        return r["hand1"] >= DAIC_T and (r["hand2B"] >= DAIC_T or r["hand3B"] >= DAIC_T)

    def scribe(r):
        return all(not (r[g] >= DAIC_T) for g in ("hand1", "hand2B", "hand3B")) and r["pooled"] >= DAIC_T

    emit("\n=== VERDICT ===")
    for lab, r in results.items():
        emit(f"  {lab}: dAIC_BB hand1 {r['hand1']:+.2f}  hand2B {r['hand2B']:+.2f}  hand3B {r['hand3B']:+.2f}  "
             f"pooled {r['pooled']:+.2f}  -> within={within(r)} scribe={scribe(r)}")
    if not ctrl:
        v = "inconclusive: controls failed"
    elif all(within(r) for r in results.values()):
        v = "switch within hand"
    elif all(scribe(r) for r in results.values()):
        v = "switch is scribe"
    else:
        v = "mixed"
    emit(f"VERDICT s66: {v}")
    emit(f"end: {clock()}  (elapsed {time.time() - t0:.0f} s)")
    out.write_text("\n".join(LOG) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
