"""s112 -- quire drift of choices vs constant production mechanism. Frozen design: DECISIONS.md D-066 (q).

Modes (run from the project root):
  --fixture       two synthetic books (planted-batch, planted-constant); no real data is read.
  --write-split   seeded discovery/held-out split of real folios, stratified by quire x hand, written to
                  runs/s112/split_s112.tsv (reads only folio metadata and the n_tokens count; no statistic).
  --run           real data, ZL3b primary, RF1b and IT2a replication; reads the split file written above;
                  writes results_s112_<YYYYmmdd_HHMMSS>.txt (never overwrites).

Operationalisation (the design leaves these open; fixed here before any real statistic):
  * statistic: eta^2 of quire on the feature's within-half ranks after removing hand x section cell means
    (the "beyond hand and section" effect; same rank form as the basis scan). Null: quire labels permuted
    within hand x section cells, one permutation set shared by all features of a half ("jointly"), B=10,000.
  * analysis set per transliteration: folio_features n_tokens >= 100 (P tokens, the basis scan's count).
  * Test A features: every folio_features feature except the Test B pair (Rw1_line, rhythm_excess) and
    n_stars (zero outside quire T). A sensitivity count restricted to affix / word-length families is printed.
  * "same sign of effect" on held-out: Pearson r between the per-quire mean residual ranks of the discovery
    half and the held-out half (quires present in both, >= 3 needed) is > 0.
  * Test B planted size: median over replicated Test-A features of the held-out effect in SD units,
    f = sqrt(max(0, eta2 - E0) / (1 - eta2)), E0 = mean permutation-null eta2 (null-bias corrected, held-out
    to avoid the discovery winner's curse). Each simulation: the real values of the half shuffled within
    hand x section cells (removes any quire effect, keeps real per-folio noise), plus per-quire offsets
    (standardised normal draws) x f x pooled within-cell SD. Power = share of 200 sims with p < 0.05; binding
    power is the minimum over the two halves and both features. Planted eta2 = median simulated eta2.
    95% CI: percentile bootstrap (2,000) resampling folios within quire.
  * CONSTANT_SUPPORTED: powered (>= 0.80) and, for both features on both halves, p >= 0.05 and the CI upper
    bound < the planted eta2. If no Test-A feature replicates there is no planted size: Test B UNINFORMATIVE.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import sys, sqlite3, hashlib, subprocess, time, math
from collections import defaultdict
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "vkb", "vkb.sqlite")
RUNDIR = os.path.join(ROOT, "runs", "s112")
SPLIT = os.path.join(RUNDIR, "split_s112.tsv")
SEED = 20261018
B = 10000
NSIM = 200
NBOOT = 2000
MIN_TOK = 100
ALPHA = 0.05
MIN_REP = 5
POWER_MIN = 0.80
TB = ["Rw1_line", "rhythm_excess"]
EXCLUDE_A = set(TB) | {"n_stars"}
TRANSLITS = ["ZL3b", "RF1b", "IT2a"]


def now():
    try:
        return subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S %Z"]).decode().strip()
    except Exception:
        return time.strftime("%Y-%m-%d %H:%M:%S")


def lower_priority():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 10)
        if hasattr(p, "cpu_affinity"):
            p.cpu_affinity([p.cpu_affinity()[-1]])
    except Exception as e:
        print("priority not lowered:", e)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


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


def resid(r, cells):
    r = r.astype(float).copy()
    for g in np.unique(cells):
        m = cells == g
        r[m] -= r[m].mean()
    return r


def perm_index(cells, rng, b):
    n = len(cells)
    idx = np.tile(np.arange(n), (b, 1))
    for g in np.unique(cells):
        pos = np.flatnonzero(cells == g)
        if len(pos) > 1:
            idx[:, pos] = pos[np.argsort(rng.random((b, len(pos))), axis=1)]
    return idx


def onehot(labels):
    lv = sorted(set(labels))
    M = np.zeros((len(labels), len(lv)))
    for i, l in enumerate(labels):
        M[i, lv.index(l)] = 1
    return M, M.sum(axis=0)


def eta2(rc, oh, nk, idx=None):
    sst = float((rc ** 2).sum())
    if sst == 0:
        return None if idx is None else np.zeros(len(idx))
    X = rc[None, :] if idx is None else rc[idx]
    s = X @ oh
    v = ((s ** 2) / nk).sum(axis=1) / sst
    return float(v[0]) if idx is None else v


def stat_rc(x, cells):
    return resid(stats.rankdata(x), cells)


# ---------------------------------------------------------------- split
def make_split(meta, folios, seed=SEED):
    """meta: folio -> (quire, hand, section). Stratified by quire x hand; returns folio -> 'D'/'H'."""
    rng = np.random.default_rng(seed)
    strata = defaultdict(list)
    for f in sorted(folios):
        strata[(meta[f][0], meta[f][1])].append(f)
    out = {}
    for k in sorted(strata):
        fs = list(strata[k])
        order = rng.permutation(len(fs))
        start = int(rng.integers(2))
        for j, i in enumerate(order):
            out[fs[i]] = "D" if (j + start) % 2 == 0 else "H"
    return out


def write_split(path, split, meta, header):
    if os.path.exists(path):
        raise SystemExit(f"refusing to overwrite {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as fh:
        for h in header:
            fh.write("# " + h + "\n")
        fh.write("folio\tquire\thand\tsection\thalf\n")
        for f in sorted(split):
            q, h, s = meta[f]
            fh.write(f"{f}\t{q}\t{h}\t{s}\t{split[f]}\n")


def read_split(path):
    split, meta = {}, {}
    for line in open(path):
        if line.startswith("#") or line.startswith("folio\t"):
            continue
        f, q, h, s, half = line.rstrip("\n").split("\t")
        split[f] = half
        meta[f] = (q, h, s)
    return split, meta


# ---------------------------------------------------------------- analysis
class Half:
    def __init__(self, folios, meta, rng):
        self.folios = folios
        self.meta = meta
        self.rng = rng
        self.cache = {}

    def frame(self, fs):
        key = tuple(fs)
        if key not in self.cache:
            cells = np.array([f"{self.meta[f][1]}|{self.meta[f][2]}" for f in fs])
            quires = [self.meta[f][0] for f in fs]
            oh, nk = onehot(quires)
            idx = perm_index(cells, self.rng, B)
            self.cache[key] = dict(cells=cells, quires=np.array(quires), oh=oh, nk=nk, idx=idx)
        return self.cache[key]

    def test(self, fs, x):
        fr = self.frame(fs)
        rc = stat_rc(x, fr["cells"])
        obs = eta2(rc, fr["oh"], fr["nk"])
        if obs is None:
            return None
        null = eta2(rc, fr["oh"], fr["nk"], fr["idx"])
        p = (1 + int((null >= obs - 1e-12).sum())) / (B + 1)
        qm = {q: float(rc[fr["quires"] == q].mean()) for q in set(fr["quires"])}
        return dict(eta2=obs, p=p, e0=float(null.mean()), qmeans=qm, n=len(fs), rc=rc)


def get_values(ff, feat, folios):
    fs = [f for f in folios if ff[feat].get(f) is not None and not math.isnan(ff[feat][f])]
    return fs, np.array([ff[feat][f] for f in fs], float)


def analyse(ff, meta, split, label, P, seed=SEED):
    """ff: feature -> folio -> value (already restricted to the analysis set). Returns summary dict."""
    rng = np.random.default_rng(seed)
    folios = sorted(f for f in ff["n_tokens"] if f in split and f in meta)
    halves = {h: Half([f for f in folios if split[f] == h], meta, rng) for h in "DH"}
    featsA = sorted(f for f in ff if f not in EXCLUDE_A)
    P(f"-- {label}: {len(folios)} folios (discovery {len(halves['D'].folios)}, held-out {len(halves['H'].folios)}); "
      f"Test A features {len(featsA)}")
    rows = []
    for feat in featsA:
        r = {"feat": feat}
        for h in "DH":
            fs, x = get_values(ff, feat, halves[h].folios)
            r[h] = halves[h].test(fs, x) if len(fs) >= 8 else None
        rows.append(r)
    pD = [r["D"]["p"] if r["D"] else 1.0 for r in rows]
    qD = bh(pD)
    nrep = 0
    P(f"{'feature':15s} {'eta2_D':>7s} {'p_D':>7s} {'q_D':>7s} {'eta2_H':>7s} {'p_H':>7s} {'dir_r':>6s} {'f_H':>6s} rep")
    for r, q in zip(rows, qD):
        r["q"] = q
        d, hh = r["D"], r["H"]
        r["dir"] = None
        if d and hh:
            common = sorted(set(d["qmeans"]) & set(hh["qmeans"]))
            if len(common) >= 3:
                a = np.array([d["qmeans"][c] for c in common]); b_ = np.array([hh["qmeans"][c] for c in common])
                if a.std() > 0 and b_.std() > 0:
                    r["dir"] = float(np.corrcoef(a, b_)[0, 1])
        r["rep"] = bool(d and hh and q < ALPHA and hh["p"] < ALPHA and r["dir"] is not None and r["dir"] > 0)
        r["fH"] = (math.sqrt(max(0.0, hh["eta2"] - hh["e0"]) / (1 - hh["eta2"])) if hh and hh["eta2"] < 1 else None)
        nrep += r["rep"]
        fm = lambda v, nd=4: "n/a" if v is None else f"{v:.{nd}f}"
        P(f"{r['feat']:15s} {fm(d and d['eta2'],3):>7s} {fm(d and d['p']):>7s} {fm(q):>7s} "
          f"{fm(hh and hh['eta2'],3):>7s} {fm(hh and hh['p']):>7s} {fm(r['dir'],2):>6s} {fm(r['fH'],3):>6s} "
          f"{'YES' if r['rep'] else '-'}")
    fam = [r for r in rows if r["feat"].split(":")[0] in ("pfx", "sfx", "init", "final") or "wlen" in r["feat"]]
    nfam = sum(r["rep"] for r in fam)
    drift = nrep >= MIN_REP
    reps = [r["feat"] for r in rows if r["rep"]]
    P(f"Test A {label}: replicated {nrep}/{len(rows)} ({', '.join(reps) or 'none'}); "
      f"affix/word-length families {nfam}/{len(fam)}; call {'DRIFT_REAL' if drift else 'NO_DRIFT'} (rule >= {MIN_REP})")

    # ---- Test B
    fvals = [r["fH"] for r in rows if r["rep"] and r["fH"] is not None]
    tb = dict(status="UNINFORMATIVE", power=None, f=None, detail={})
    if not fvals:
        P(f"Test B {label}: no replicated Test-A feature -> no planted size -> UNINFORMATIVE")
        return dict(label=label, nrep=nrep, n=len(rows), nfam=nfam, nfamn=len(fam), drift=drift, reps=reps, tb=tb)
    fmed = float(np.median(fvals))
    tb["f"] = fmed
    P(f"Test B {label}: planted size f = median held-out SD-unit effect of {len(fvals)} replicated features = {fmed:.3f}")
    srng = np.random.default_rng(seed + 1)
    powers, ok = [], True
    for feat in TB:
        for h in "DH":
            half = halves[h]
            fs, x = get_values(ff, feat, half.folios)
            fr = half.frame(fs)
            obs = half.test(fs, x)
            # power
            cr = resid(x, fr["cells"])
            sd = float(np.sqrt((cr ** 2).sum() / max(1, len(x) - len(np.unique(fr["cells"])))))
            ql = sorted(set(fr["quires"]))
            det, sim_e = 0, []
            for _ in range(NSIM):
                y = x.copy()
                for g in np.unique(fr["cells"]):
                    pos = np.flatnonzero(fr["cells"] == g)
                    y[pos] = y[srng.permutation(pos)]
                z = srng.standard_normal(len(ql))
                z = (z - z.mean()) / (z.std() if z.std() > 0 else 1)
                off = dict(zip(ql, z * fmed * sd))
                y = y + np.array([off[q] for q in fr["quires"]])
                rc = stat_rc(y, fr["cells"])
                e = eta2(rc, fr["oh"], fr["nk"])
                null = eta2(rc, fr["oh"], fr["nk"], fr["idx"])
                p = (1 + int((null >= e - 1e-12).sum())) / (B + 1)
                det += p < ALPHA
                sim_e.append(e)
            pw = det / NSIM
            planted = float(np.median(sim_e))
            # bootstrap CI within quire
            boots = []
            byq = {q: np.flatnonzero(fr["quires"] == q) for q in ql}
            for _ in range(NBOOT):
                sel = np.concatenate([srng.choice(ix, len(ix), replace=True) for ix in byq.values()])
                xb = x[sel]; cb = fr["cells"][sel]
                ohb, nkb = onehot(list(fr["quires"][sel]))
                eb = eta2(stat_rc(xb, cb), ohb, nkb)
                boots.append(0.0 if eb is None else eb)
            lo, hi = np.percentile(boots, [2.5, 97.5])
            powers.append(pw)
            excl = hi < planted
            cond = obs["p"] >= ALPHA and excl
            ok &= cond
            tb["detail"][(feat, h)] = dict(p=obs["p"], eta2=obs["eta2"], power=pw, planted=planted, lo=lo, hi=hi)
            P(f"  {feat:13s} half {h}: n={len(x)} eta2={obs['eta2']:.3f} p={obs['p']:.4f} power={pw:.3f} "
              f"planted_eta2={planted:.3f} CI95=[{lo:.3f},{hi:.3f}] CI_excludes_planted={'yes' if excl else 'no'}")
    tb["power"] = min(powers)
    if tb["power"] < POWER_MIN:
        tb["status"] = "UNINFORMATIVE"
    else:
        tb["status"] = "CONSTANT_SUPPORTED" if ok else "NOT_SUPPORTED"
    P(f"Test B {label}: power(min) {tb['power']:.3f} (rule >= {POWER_MIN}); call {tb['status']}")
    return dict(label=label, nrep=nrep, n=len(rows), nfam=nfam, nfamn=len(fam), drift=drift, reps=reps, tb=tb)


def outcome(res):
    if res["drift"] and res["tb"]["status"] == "CONSTANT_SUPPORTED":
        return "CONSTANT_MECHANISM_DRIFTING_CHOICES"
    if res["drift"]:
        return "DRIFT_ONLY"
    return "NOT_CONFIRMED"


def short(res):
    pw = res["tb"]["power"]
    return (f"TEST_A={'DRIFT_REAL' if res['drift'] else 'NO_DRIFT'} n_rep={res['nrep']}/{res['n']} "
            f"TEST_B={res['tb']['status']} power={'na' if pw is None else f'{pw:.3f}'}")


# ---------------------------------------------------------------- fixture
LAYOUT = [  # (hand, section, {quire: n_folios}) -- synthetic layout loosely shaped like the book
    ("1", "H", {"A": 3, "C": 3, "F": 3, "G": 3, "O": 3, "Q": 4}), ("1", "P", {"S": 7, "O": 7}), ("1", "T", {"A": 1}),
    ("2", "B", {"M": 19}), ("2", "C", {"N": 2}), ("2", "H", {"D": 4, "E": 4, "F": 4, "G": 4}),
    ("2", "T", {"M": 2, "N": 2}), ("3", "H", {"Q": 2}), ("3", "S", {"T": 13, "H": 12}), ("4", "A", {"I": 1}),
    ("4", "C", {"J": 1}), ("5", "H", {"F": 1, "H": 1}), ("5", "T", {"H": 1})]


def synth_book(planted, seed):
    rng = np.random.default_rng(seed)
    meta = {}
    k = 0
    for h, s, qs in LAYOUT:
        for q, n in qs.items():
            for _ in range(n):
                meta[f"x{k:03d}"] = (q, h, s); k += 1
    feats = [f"fa{i:02d}" for i in range(43)] + TB + ["n_tokens"]
    hands = sorted({m[1] for m in meta.values()}); secs = sorted({m[2] for m in meta.values()})
    quires = sorted({m[0] for m in meta.values()})
    ff = defaultdict(dict)
    for feat in feats:
        he = dict(zip(hands, rng.normal(0, 1, len(hands))))
        se = dict(zip(secs, rng.normal(0, 1, len(secs))))
        shift = planted and feat in [f"fa{i:02d}" for i in range(12)]
        qe = dict(zip(quires, rng.normal(0, 0.8, len(quires)) if shift else np.zeros(len(quires))))
        for f, (q, h, s) in meta.items():
            ff[feat][f] = 200.0 if feat == "n_tokens" else he[h] + se[s] + qe[q] + rng.normal()
    return ff, meta


def run_fixture():
    os.makedirs(RUNDIR, exist_ok=True)
    out = os.path.join(RUNDIR, f"fixture_{time.strftime('%Y%m%d_%H%M%S')}.txt")
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
    P(f"s112 FIXTURE started {now()}; script sha256 {sha(os.path.abspath(__file__))}")
    P("Synthetic books (no real data): 107 folios, 13 hand x section cells; 43 Test-A features + Rw1_line + "
      "rhythm_excess = hand + section effects + N(0,1) noise. planted-batch: fa00-fa11 get quire offsets N(0,0.8); "
      "Test B features never shifted. planted-constant: no quire offsets.")
    calls = {}
    for name, planted, sd in (("planted-batch", True, SEED + 11), ("planted-constant", False, SEED + 12)):
        ff, meta = synth_book(planted, sd)
        split = make_split(meta, list(meta))
        sp = os.path.join(RUNDIR, f"fixture_split_{name}_{time.strftime('%Y%m%d_%H%M%S')}.tsv")
        write_split(sp, split, meta, [f"s112 fixture split {name}; seed {SEED}; stratified quire x hand"])
        P(f"== {name}: split written before any statistic -> {os.path.relpath(sp, ROOT)} sha256 {sha(sp)}")
        res = analyse(ff, meta, split, name, P)
        calls[name] = res
        P(f"FIXTURE {name}: {short(res)} OUTCOME={outcome(res)}")
    pb = calls["planted-batch"]["drift"]; pc = not calls["planted-constant"]["drift"]
    P(f"FIXTURE CONTROLS: planted-batch DRIFT_REAL={'PASS' if pb else 'FAIL'}; "
      f"planted-constant no DRIFT={'PASS' if pc else 'FAIL'}; overall {'PASS' if pb and pc else 'FAIL'}")
    P(f"finished {now()}")
    with open(out, "w", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(out, ROOT))
    return 0 if pb and pc else 1


# ---------------------------------------------------------------- real
def load_real():
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    meta = {r[0]: (r[1], r[2], r[3]) for r in c.execute("SELECT folio, quire, hand_davis, section FROM folios")}
    trs = [r[0] for r in c.execute("SELECT DISTINCT translit FROM folio_features")]
    return c, meta, trs


def run_write_split():
    c, meta, trs = load_real()
    keep = set()
    for tr in TRANSLITS:
        if tr in trs:
            keep |= {r[0] for r in c.execute("SELECT folio FROM folio_features WHERE translit=? AND feature='n_tokens' "
                                              "AND value>=?", (tr, MIN_TOK))}
    keep = sorted(f for f in keep if f in meta and meta[f][0] and meta[f][1])
    split = make_split(meta, keep)
    write_split(SPLIT, split, meta, [
        f"s112 real split written {now()}; seed {SEED}; stratified by quire x hand_davis",
        f"set: folios with folio_features n_tokens >= {MIN_TOK} in any of {','.join(TRANSLITS)}; {len(keep)} folios",
        "half D = discovery, H = held-out. No statistic computed before this file was written."])
    nd = sum(v == "D" for v in split.values())
    print(f"wrote {os.path.relpath(SPLIT, ROOT)}: {len(split)} folios, D={nd}, H={len(split)-nd}; sha256 {sha(SPLIT)}")


def run_real():
    lower_priority()
    if not os.path.exists(SPLIT):
        raise SystemExit("split file missing; run --write-split first")
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ROOT, f"results_s112_{ts}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
    t0 = time.time()
    split, smeta = read_split(SPLIT)
    c, meta, trs = load_real()
    built = c.execute("SELECT MAX(built_at) FROM build_log").fetchone()[0]
    P(f"s112 quire drift vs constant mechanism -- REAL RUN. Design DECISIONS.md D-066 (q). started {now()}")
    P(f"script tools/s112_quire_drift.py sha256 {sha(os.path.abspath(__file__))}; split {os.path.relpath(SPLIT, ROOT)} "
      f"sha256 {sha(SPLIT)}; VKB build {built}; B={B}, sims={NSIM}, boots={NBOOT}, seed {SEED}, min tokens {MIN_TOK}")
    missing = [t for t in TRANSLITS if t not in trs]
    if missing:
        P(f"NOTE: transliterations not in folio_features: {missing}")
    results = {}
    for tr in TRANSLITS:
        if tr in missing:
            continue
        ff = defaultdict(dict)
        for f, feat, val in c.execute("SELECT folio, feature, value FROM folio_features WHERE translit=?", (tr,)):
            ff[feat][f] = val
        keep = {f for f, v in ff["n_tokens"].items() if v is not None and v >= MIN_TOK}
        ff = {k: {f: v for f, v in d.items() if f in keep} for k, d in ff.items()}
        P(""); P(f"==== {tr} {'(primary)' if tr == 'ZL3b' else '(replication)'}")
        results[tr] = analyse(ff, smeta, split, tr, P)
        P(f"RESULT {tr}: {short(results[tr])} OUTCOME={outcome(results[tr])}")
    prim = results["ZL3b"]
    reps = {}
    for tr, r in results.items():
        for f in r["reps"]:
            reps.setdefault(f, []).append(tr)
    P(""); P("== per-feature replication across transliterations (Test A replicated in):")
    for f in sorted(reps, key=lambda k: (-len(reps[k]), k)):
        P(f"  {f:15s} {len(reps[f])}/{len(results)} {','.join(reps[f])}")
    P(f"elapsed {time.time() - t0:.0f}s; finished {now()}")
    tail = " | ".join(f"{tr} {short(r)} OUTCOME={outcome(r)}" for tr, r in results.items() if tr != "ZL3b")
    P(f"CALL: s112 primary=ZL3b {short(prim)} OUTCOME={outcome(prim)} | {tail}")
    with open(out, "x", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--fixture" in a:
        lower_priority(); sys.exit(run_fixture())
    elif "--write-split" in a:
        run_write_split()
    elif "--run" in a:
        run_real()
    else:
        print(__doc__)
