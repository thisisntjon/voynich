"""EXPLORATORY all-pairs relationship scan over folio_features (VKB). Nothing here is filed; it finds leads.

1. Feature x folio variable. Variables: quire, Davis hand, Currier language, section, folio side (r/v), bifolio
   position (outer / inner half of the quire's nest; quires with one bifolio -> NULL), n_stars (quire T only).
   Effect: categorical -> eta^2 of the feature's ranks (Kruskal-style); n_stars -> Spearman rho.
   Partial effects: the same after removing hand means (eta2|hand) and section means (eta2|sect) from the ranks.
   p: permutation of feature values over folios, B permutations, three schemes: free, within hand, within section
   (values only move between folios of the same hand / same section, so hand or section cannot carry the effect).
   p = (1 + #{stat_perm >= stat_obs}) / (B + 1). A scheme is n/a when no stratum holds two levels of the variable.
   q: Benjamini-Hochberg over all defined tests of one scheme and one transliteration.
   Flag BOTH: q_hand < 0.05 and q_section < 0.05. Replication: the same test on RF1b and IT2a (p_hand and
   p_section < 0.05 on each).
2. Feature x feature: Spearman rho over folios; partial on n_tokens (ranks residualised on rank n_tokens), and
   partial on n_tokens + hand + section dummies. Pairs whose definitions overlap (same family, a prefix starting
   with a line-initial glyph, a suffix ending with a line-final glyph) are listed apart.
Analysis set: folios with >= MIN_TOK paragraph tokens in that transliteration.
Usage: python -I tools/vkb/queries/folio_relationship_scan.py [out.txt] [--db other.sqlite]
Default output: .inventory/runs/2026-10-18/vkb-relationship-scan.txt (never overwritten: a new name is chosen).
"""
import math, os, sqlite3, subprocess, sys, time
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import DB, ROOT  # noqa: E402

B = 10000
MIN_TOK = 50
SEED = 20261018
ALPHA = 0.05
TRANSLITS = ["ZL3b", "RF1b", "IT2a"]
VARS = ["quire", "hand", "lang", "section", "side", "bifpos", "n_stars"]
FAMILY = {"h1": "h1", "h1_50": "h1", "h2": "h2", "h2_50": "h2", "Rw1": "rw", "Rw1_line": "rw",
          "lag1_wlen": "rh", "rhythm_excess": "rh", "n_tokens": "n", "n_lines": "n"}


def now():
    return subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S %Z"]).decode().strip()


def ranks(x):
    return stats.rankdata(x)


def bh(ps):
    ps = np.asarray(ps, float)
    n = len(ps)
    if n == 0:
        return ps
    o = np.argsort(ps)
    q = ps[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.minimum(q, 1)
    return out


def resid(r, labels):
    """ranks minus their group mean."""
    r = r.astype(float).copy()
    for g in set(labels):
        m = labels == g
        r[m] -= r[m].mean()
    return r


def perm_index(strata, rng, n):

    idx = np.tile(np.arange(n), (B, 1))
    if strata is None:
        return np.argsort(rng.random((B, n)), axis=1)
    for g in sorted(set(strata)):
        pos = np.flatnonzero(strata == g)
        if len(pos) > 1:
            idx[:, pos] = pos[np.argsort(rng.random((B, len(pos))), axis=1)]
    return idx


def eta2_batch(rc, idx, onehot, nk):
    """rc: centred ranks (n,), idx: (B, n) or None. eta^2 = SS_between / SS_total."""
    sst = float((rc ** 2).sum())
    if sst == 0:
        return None
    X = rc[None, :] if idx is None else rc[idx]
    s = X @ onehot
    return ((s ** 2) / nk).sum(axis=1) / sst


def main():
    args = sys.argv[1:]
    db = DB
    if "--db" in args:  # testing against a non-default build
        i = args.index("--db"); db = args[i + 1]; del args[i:i + 2]
    out = args[0] if args else os.path.join(ROOT, ".inventory", "runs", "2026-10-18",
                                                              "vkb-relationship-scan.txt")
    if os.path.exists(out):  # never overwrite
        stem, ext = os.path.splitext(out)
        out = f"{stem}.{time.strftime('%Y%m%d-%H%M%S')}{ext}"
    t0 = time.time()
    start = now()
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    built = c.execute("SELECT MAX(built_at) FROM build_log").fetchone()[0]
    fol = {r[0]: r[1:] for r in c.execute("SELECT folio, quire, bifolio, leaf_side, section, hand_davis, currier_lang, "
                                          "n_stars FROM folios")}
    nb = defaultdict(set)
    for f, (q, bif, *_rest) in fol.items():
        if bif:
            nb[q].add(int(bif.split("-")[1]))

    def var_value(f, v):
        q, bif, side, sec, hand, lang, ns = fol[f]
        if v == "quire": return q
        if v == "hand": return hand
        if v == "lang": return lang or None
        if v == "section": return sec
        if v == "side": return side
        if v == "n_stars": return ns
        if v == "bifpos":
            if not bif or len(nb[q]) < 2: return None
            k, K = int(bif.split("-")[1]), max(nb[q])
            return "outer" if (k - 1) / (K - 1) < 0.5 else "inner"

    L = []
    P = L.append
    P("EXPLORATORY -- VKB folio relationship scan. Not pre-registered, not filed, moves no scoreboard entry.")
    P(f"started {start}; VKB build {built}; db {os.path.relpath(db, ROOT)}")
    P(f"script tools/vkb/queries/folio_relationship_scan.py; B={B} permutations; seed {SEED}; analysis set: "
      f">= {MIN_TOK} P tokens; BH-FDR per scheme and transliteration; flag BOTH = q_hand < {ALPHA} and q_sect < {ALPHA}")
    P("Effect: eta2 = eta^2 of feature ranks across the variable's levels (n_stars: Spearman rho); eta2|hand, "
      "eta2|sect = same after removing hand / section rank means. replicates: RF1b / IT2a p < 0.05 under every applicable control. p_free, p_hand, p_sect: permutation p (free, "
      "within hand, within section); q_*: BH. n/a = no stratum holds two levels of the variable.")
    P("")

    results = {}
    data = {}
    for tr in TRANSLITS:
        ff = defaultdict(dict)
        for f, feat, val in c.execute("SELECT folio, feature, value FROM folio_features WHERE translit=?", (tr,)):
            ff[feat][f] = val
        folios = sorted(f for f, v in ff["n_tokens"].items() if v is not None and v >= MIN_TOK and f in fol)
        feats = sorted(ff)
        data[tr] = (ff, folios, feats)
        rng = np.random.default_rng(SEED)
        cache = {}
        rows = []
        for feat in feats:
            for v in VARS:
                if feat == "n_stars" and v == "n_stars":
                    continue
                fs = [f for f in folios if ff[feat].get(f) is not None and var_value(f, v) is not None]
                if len(fs) < 8:
                    continue
                g = np.array([var_value(f, v) for f in fs], dtype=object)
                hand = np.array([fol[f][4] for f in fs]); sect = np.array([fol[f][3] for f in fs])
                x = np.array([ff[feat][f] for f in fs], float)
                key = tuple(fs)
                if key not in cache:
                    cache[key] = {"free": perm_index(None, rng, len(fs)), "hand": perm_index(hand, rng, len(fs)),
                                  "sect": perm_index(sect, rng, len(fs))}
                idxs = cache[key]
                r = ranks(x)
                rc = r - r.mean()
                row = dict(feat=feat, var=v, n=len(fs), levels=None)
                if v == "n_stars":
                    gr = ranks(g.astype(float)); gc = gr - gr.mean()
                    den = math.sqrt((rc ** 2).sum() * (gc ** 2).sum())
                    if den == 0:
                        continue
                    obs = float(rc @ gc) / den
                    row.update(effect=obs, kind="rho", eh=None, es=None)
                    for s, idx in idxs.items():
                        if s != "free":
                            strata = hand if s == "hand" else sect
                            gv = g.astype(float)
                            if not any(len(set(gv[strata == st])) > 1 for st in set(strata)):
                                row["p_" + s] = None; continue
                        pr = (rc[idx] @ gc) / den
                        row["p_" + s] = (1 + int((np.abs(pr) >= abs(obs) - 1e-12).sum())) / (B + 1)
                else:
                    levels = sorted(set(g))
                    if len(levels) < 2:
                        continue
                    onehot = np.array([[gi == lv for lv in levels] for gi in g], float)
                    nk = onehot.sum(0)
                    obs = float(eta2_batch(rc, None, onehot, nk)[0])
                    eh = eta2_batch(resid(r, hand), None, onehot, nk)
                    es = eta2_batch(resid(r, sect), None, onehot, nk)
                    row.update(effect=obs, kind="eta2", eh=None if eh is None else float(eh[0]),
                               es=None if es is None else float(es[0]), levels=len(levels))
                    for s, idx in idxs.items():
                        if s != "free":
                            strata = hand if s == "hand" else sect
                            if not any(len(set(g[strata == st])) > 1 for st in set(strata)):
                                row["p_" + s] = None; continue
                        pr = eta2_batch(rc, idx, onehot, nk)
                        row["p_" + s] = (1 + int((pr >= obs - 1e-12).sum())) / (B + 1)
                rows.append(row)
        for s in ("free", "hand", "sect"):
            d = [r for r in rows if r.get("p_" + s) is not None]
            for r, q in zip(d, bh([r["p_" + s] for r in d])):
                r["q_" + s] = float(q)
        results[tr] = {(r["feat"], r["var"]): r for r in rows}
        P(f"{tr}: {len(folios)} folios, {len(feats)} features, {len(rows)} feature x variable tests "
          f"({time.time() - t0:.0f}s)")
    P("")

    def fmt(x, nd=3):
        if x is None:
            return "n/a"
        if abs(x) < 1e-10:
            return "0"
        return f"{x:.2g}" if abs(x) < 10 ** -(nd - 1) else f"{x:.{nd}f}"

    zl = results["ZL3b"]

    def rep(key):
        out = []
        for tr in ("RF1b", "IT2a"):
            r = results[tr].get(key)
            ps = [r.get(k) for k in ("p_hand", "p_sect")] if r else []
            ps = [p for p in ps if p is not None]  # hand / section rows: only the other control applies
            ok = bool(ps) and all(p < ALPHA for p in ps)
            out.append(f"{tr}:{'yes' if ok else 'no'}")
        return " ".join(out)

    both = [r for r in zl.values() if r.get("q_hand") is not None and r.get("q_sect") is not None
            and r["q_hand"] < ALPHA and r["q_sect"] < ALPHA]
    both.sort(key=lambda r: (max(r["q_hand"], r["q_sect"]), -abs(r["effect"])))
    hdr = (f"{'feature':16s} {'variable':8s} {'n':>4s} {'stat':>4s} {'effect':>7s} {'eta2|hand':>9s} {'eta2|sect':>9s} "
           f"{'p_free':>8s} {'p_hand':>8s} {'p_sect':>8s} {'q_free':>7s} {'q_hand':>7s} {'q_sect':>7s}  replicates")

    def line(r):
        return (f"{r['feat']:16s} {r['var']:8s} {r['n']:4d} {r['kind']:>4s} {r['effect']:+7.3f} {fmt(r['eh']):>9s} "
                f"{fmt(r['es']):>9s} {fmt(r['p_free'], 4):>8s} {fmt(r.get('p_hand'), 4):>8s} {fmt(r.get('p_sect'), 4):>8s} "
                f"{fmt(r.get('q_free'), 4):>7s} {fmt(r.get('q_hand'), 4):>7s} {fmt(r.get('q_sect'), 4):>7s}  {rep((r['feat'], r['var']))}")
    P(f"== 1a. ZL3b associations surviving BOTH within-hand and within-section permutation (BH q < {ALPHA}): {len(both)}")
    P(hdr)
    for r in both:
        P(line(r))
    P("")
    for v, other in (("hand", "sect"), ("section", "hand")):
        d = [r for r in zl.values() if r["var"] == v and r.get("q_" + other) is not None and r["q_" + other] < ALPHA]
        d.sort(key=lambda r: (r["q_" + other], -r["effect"]))
        P(f"== 1b. ZL3b {v}: only the {'within-section' if other == 'sect' else 'within-hand'} control applies; "
          f"q < {ALPHA}: {len(d)}")
        P(hdr)
        for r in d:
            P(line(r))
        P("")
    P("== 1c. Per variable: tests, significant free (q<0.05), surviving within hand, within section, both (ZL3b)")
    for v in VARS:
        d = [r for r in zl.values() if r["var"] == v]
        k = lambda s: sum(1 for r in d if r.get("q_" + s) is not None and r["q_" + s] < ALPHA)  # noqa: E731
        na = lambda s: sum(1 for r in d if r.get("p_" + s) is None)  # noqa: E731
        P(f"  {v:8s} tests {len(d):3d}  free {k('free'):3d}  hand {k('hand'):3d} (n/a {na('hand')})  "
          f"sect {k('sect'):3d} (n/a {na('sect')})  both {sum(1 for r in both if r['var'] == v):3d}")
    P("")
    P("== 1d. Strongest free associations that do NOT survive both controls (top 15 by effect, q_free < 0.05)")
    P(hdr)
    lost = [r for r in zl.values() if r.get("q_free") is not None and r["q_free"] < ALPHA and r not in both
            and r["var"] not in ("hand", "section")]
    for r in sorted(lost, key=lambda r: -abs(r["effect"]))[:15]:
        P(line(r))
    P("")

    # 2. feature x feature
    ff, folios, feats = data["ZL3b"]
    feats2 = [f for f in feats if f != "n_stars" and sum(ff[f].get(x) is not None for x in folios) >= 0.9 * len(folios)]
    fs = [x for x in folios if all(ff[f].get(x) is not None for f in feats2)]
    M = np.array([[ff[f][x] for f in feats2] for x in fs], float)
    R = np.apply_along_axis(ranks, 0, M)
    ntok = ranks(np.array([ff["n_tokens"][x] for x in fs], float))
    hand = np.array([fol[x][4] for x in fs]); sect = np.array([fol[x][3] for x in fs])
    D1 = np.column_stack([np.ones(len(fs)), ntok])
    dums = [(hand == h).astype(float) for h in sorted(set(hand))[1:]] + [(sect == s).astype(float) for s in sorted(set(sect))[1:]]
    D2 = np.column_stack([D1] + dums)

    def res(D):
        beta, *_ = np.linalg.lstsq(D, R, rcond=None)
        E = R - D @ beta
        E /= np.linalg.norm(E, axis=0)
        return E
    C0 = np.corrcoef(R, rowvar=False)
    E1, E2 = res(D1), res(D2)
    C1, C2 = E1.T @ E1, E2.T @ E2
    n = len(fs)
    pairs = []
    for i in range(len(feats2)):
        for j in range(i + 1, len(feats2)):
            a, b = feats2[i], feats2[j]
            if "n_tokens" in (a, b) or "n_lines" in (a, b):
                continue
            r1 = float(C1[i, j]); df = n - 3
            t = r1 * math.sqrt(df / max(1e-12, 1 - r1 * r1))
            p1 = 2 * stats.t.sf(abs(t), df)
            ov = FAMILY.get(a, a) == FAMILY.get(b, b)
            for x, y in ((a, b), (b, a)):
                if x.startswith("pfx:") and y.startswith("init:") and x[4:].startswith(y[5:]):
                    ov = True
                if x.startswith("sfx:") and y.startswith("final:") and x[4:].endswith(y[6:]):
                    ov = True
            pairs.append(dict(a=a, b=b, r0=float(C0[i, j]), r1=r1, r2=float(C2[i, j]), p1=p1, ov=ov))
    for p, q in zip(pairs, bh([p["p1"] for p in pairs])):
        p["q1"] = float(q)
    P(f"== 2. ZL3b feature x feature over {n} folios, {len(feats2)} features, {len(pairs)} pairs (n_tokens/n_lines "
      "excluded as partners). rho = Spearman; rho|n = partial on rank n_tokens; rho|n,h,s = partial on n_tokens + "
      "hand + section dummies; p, q for rho|n (t approximation, BH over all pairs).")
    ph = f"{'feature a':16s} {'feature b':16s} {'rho':>7s} {'rho|n':>7s} {'rho|n,h,s':>9s} {'p':>9s} {'q':>9s}"
    pl = lambda p: (f"{p['a']:16s} {p['b']:16s} {p['r0']:+7.3f} {p['r1']:+7.3f} {p['r2']:+9.3f} "  # noqa: E731
                    f"{p['p1']:9.2e} {p['q1']:9.2e}")
    P("-- 2a. strongest pairs not explained by n_tokens, no definitional overlap (top 25 by |rho|n|)")
    P(ph)
    for p in sorted([p for p in pairs if not p["ov"]], key=lambda p: -abs(p["r1"]))[:25]:
        P(pl(p))
    P("-- 2b. same ranking, also surviving hand + section (top 15 by |rho|n,h,s|, no overlap)")
    P(ph)
    for p in sorted([p for p in pairs if not p["ov"]], key=lambda p: -abs(p["r2"]))[:15]:
        P(pl(p))
    P("-- 2c. pairs with definitional overlap (top 10 by |rho|n|; expected, listed for completeness)")
    P(ph)
    for p in sorted([p for p in pairs if p["ov"]], key=lambda p: -abs(p["r1"]))[:10]:
        P(pl(p))
    P("-- 2d. correlation with n_tokens (Spearman), the size confound, all features")
    k = feats2.index("n_tokens")
    P("  " + "; ".join(f"{f} {C0[k, i]:+.2f}" for i, f in sorted(enumerate(feats2), key=lambda t: -abs(C0[k, t[0]]))
                        if f != "n_tokens"))
    P("")
    P(f"finished {now()}; {time.time() - t0:.0f}s. EXPLORATORY: leads only; any lead needs a pre-registered run.")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))
    print("wrote", out)


if __name__ == "__main__":
    main()
