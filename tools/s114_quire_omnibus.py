"""s114 -- whole-book omnibus test of quire drift beyond hand x section. Frozen design: DECISIONS.md D-066 (s).

Retests the s112 question (D-066 (q)) without the discovery/held-out split (s112 failed its fixture, L-326).
Code for the residual-rank eta^2, the within-cell permutation and the synthetic-book builder is copied from
tools/s112_quire_drift.py (that script is not edited).

Modes (run from the project root):
  --fixture   10 planted-batch + 10 planted-constant synthetic books; no real data is read.
              Writes runs/s114/fixture_<YYYYmmdd_HHMMSS>.txt.
  --run       real VKB folio_features (read-only), ZL3b primary, RF1b and IT2a replication. Refuses to run unless
              the stub s114_quire_omnibus.prereg.sha256 verifies. Writes results_s114_<YYYYmmdd_HHMMSS>.txt
              at the project root (never overwrites).

Frozen design (D-066 (s)):
  * Analysis set per transliteration: folios with folio_features n_tokens >= 100.
  * Test A omnibus T_A = sum over the s112 Test-A set (every folio_features feature except Rw1_line,
    rhythm_excess and n_stars) of eta^2 of quire on hand x section residual ranks.
    Null: 10,000 permutations of quire labels within hand x section cells; one shared permutation set for all
    features of a transliteration. DRIFT_REAL iff p < 0.01 on ZL3b and p < 0.05 on both RF1b and IT2a.
  * Test B: the same omnibus over {Rw1_line, rhythm_excess}, reported with its minimum detectable effect (MDE:
    80% power at alpha 0.05, 200 simulations at real noise). The MDE is computed BEFORE the Test B p-values.
    CONSTANT_SUPPORTED only if MDE <= 0.8 SD and p >= 0.05 on all three transliterations.
  * Fixture controls (not tuned): planted-batch books, quire offsets N(0, 0.8 SD) on 12 features, must give
    DRIFT_REAL on >= 8/10; planted-constant books on <= 1/10. If either fails, stop.

Choices the design leaves open, fixed here before any real statistic:
  * Residual ranks: ranks of the feature over the folios where it is present, minus the hand x section cell mean
    (s112 stat_rc). eta^2 = between-quire SS / total SS of those residual ranks.
  * Missing values: a feature is scored on the folios where it is non-null (>= 8 needed, as in s112). The shared
    permutation acts on quire LABELS over the whole analysis set (within cells); each feature then uses the
    permuted labels of its present folios. With no missing values this equals permuting values (s112).
  * The Test-A set is the literal parenthetical of D-066 (s) (it includes n_tokens, n_lines, Rw1, h1, h2,
    label_share, ttr_50 besides the affix and word-length features). A descriptive sub-omnibus over the strict
    affix/word-length families (pfx:, sfx:, init:, final:, *wlen*) is printed; it is NOT a call.
  * Permutation p = (1 + #{null >= obs}) / (B + 1). One permutation set per transliteration (folio sets differ by
    transliteration), all from the same seed.
  * MDE simulation (per transliteration): the real Test-B values are shuffled within hand x section cells
    (removes any quire effect, keeps the real per-folio noise), then per-quire offsets z * f * SD are added
    independently to each of the two features, z standardised normal draws (mean 0, sd 1 over quires; s112's
    plant), SD = pooled within-cell SD of the raw feature. Grid f = 0.1, 0.2, ..., 2.0 SD; MDE = the smallest
    grid f whose power (share of 200 sims with omnibus p < 0.05, same shared permutation set) is >= 0.80; the
    scan stops there. If no grid point reaches 0.80, MDE is reported as > 2.0.
  * Test B call: CONSTANT_SUPPORTED if every transliteration has MDE <= 0.8 and p >= 0.05; else NOT_SUPPORTED if
    any transliteration has p < 0.05 (mechanism varies by quire at the observed power); else UNINFORMATIVE.
  * Outcome: DRIFT_REAL + CONSTANT_SUPPORTED -> CONSTANT_MECHANISM_DRIFTING_CHOICES; DRIFT_REAL only ->
    DRIFT_ONLY; no drift + CONSTANT_SUPPORTED -> NO_DRIFT_CONSTANT_SUPPORTED; neither -> NOT_CONFIRMED.
  * Top contributing features: per-feature excess eta^2 (observed minus permutation-null mean) and per-feature
    permutation p from the same shared set. DESCRIPTIVE ONLY, no per-feature call.
  * Fixture replication condition: the RF1b / IT2a analogues are independent noisy re-measurements of the same
    synthetic book: identical hand, section and planted quire offsets, fresh N(0, 1) per-folio noise (the same
    per-folio noise level as s112's fixture). This treats the three transliterations as independent given the
    book; real transliterations share most of their per-folio idiosyncrasy, so the real replication condition
    is less independent than in the fixture.
  * Fixture layout: s112's LAYOUT table (107 folios, 13 hand x section cells), copied unchanged.
  * Fixture Test B: run on the first planted-batch book's ZL3b analogue as a code smoke test, not a control.
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
RUNDIR = os.path.join(ROOT, "runs", "s114")
STUB = os.path.join(ROOT, "s114_quire_omnibus.prereg.sha256")
SEED = 20261018
B = 10000
NSIM = 200
MIN_TOK = 100
MIN_PRESENT = 8
ALPHA_B = 0.05
ALPHA_PRIMARY = 0.01
ALPHA_REPL = 0.05
POWER_MIN = 0.80
MDE_MAX = 0.8
GRID = [round(0.1 * i, 1) for i in range(1, 21)]
TB = ["Rw1_line", "rhythm_excess"]
EXCLUDE_A = set(TB) | {"n_stars"}
TRANSLITS = ["ZL3b", "RF1b", "IT2a"]
N_BOOKS = 10
CTRL_BATCH_MIN = 8
CTRL_CONST_MAX = 1


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
        return "BelowNormal, 1 core"
    except Exception as e:
        return f"priority not lowered: {e}"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


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


def is_affix_wlen(feat):
    return feat.split(":")[0] in ("pfx", "sfx", "init", "final") or "wlen" in feat


# ---------------------------------------------------------------- omnibus machinery
class Frame:
    """One analysis set (folios with quire, cells) and its shared permutation set of quire labels."""

    def __init__(self, folios, meta, seed):
        self.folios = list(folios)
        self.n = len(self.folios)
        self.cells = np.array([f"{meta[f][1]}|{meta[f][2]}" for f in self.folios])
        self.quires = np.array([meta[f][0] for f in self.folios])
        self.qlev = sorted(set(self.quires))
        self.K = len(self.qlev)
        code = np.array([self.qlev.index(q) for q in self.quires])
        rng = np.random.default_rng(seed)
        idx = perm_index(self.cells, rng, B)        # permuted positions within cells
        lab = np.vstack([code[None, :], code[idx]])  # row 0 = observed labels, rows 1..B = permuted
        self.flat = (lab + self.K * np.arange(B + 1)[:, None]).ravel()
        self.ncell = len(np.unique(self.cells))

    def prep(self, x):
        """x: values aligned with self.folios (nan = missing). Returns a feature object or None."""
        m = ~np.isnan(x)
        if m.sum() < MIN_PRESENT:
            return None
        rc = np.zeros(self.n)
        rc[m] = resid(stats.rankdata(x[m]), self.cells[m])
        sst = float((rc ** 2).sum())
        if sst <= 1e-12:
            return None
        nk = np.bincount(self.flat, weights=np.tile(m.astype(float), B + 1), minlength=(B + 1) * self.K)
        return dict(m=m, rc=rc, sst=sst, nk=nk.reshape(B + 1, self.K))

    def eta2_all(self, ft, rc=None):
        """eta^2 for observed (index 0) and all B permutations (1..B)."""
        rc = ft["rc"] if rc is None else rc
        sst = ft["sst"] if rc is ft["rc"] else float((rc ** 2).sum())
        s = np.bincount(self.flat, weights=np.tile(rc, B + 1), minlength=(B + 1) * self.K).reshape(B + 1, self.K)
        nk = ft["nk"]
        with np.errstate(divide="ignore", invalid="ignore"):
            q = np.where(nk > 0, s ** 2 / nk, 0.0)
        return q.sum(axis=1) / sst


def pval(v):
    return (1 + int((v[1:] >= v[0] - 1e-12).sum())) / (B + 1)


def omnibus(frame, X, feats):
    """X: feature -> values aligned with frame.folios. Returns T vector (obs + null), per-feature info."""
    T = np.zeros(B + 1)
    per = {}
    for f in feats:
        ft = frame.prep(X[f])
        if ft is None:
            per[f] = None
            continue
        e = frame.eta2_all(ft)
        T += e
        per[f] = dict(eta2=float(e[0]), e0=float(e[1:].mean()), p=pval(e), n=int(ft["m"].sum()))
    return T, per


def mde_scan(frame, X, feats, seed, P, tag):
    """Minimum detectable effect for the omnibus over `feats` at real noise (see docstring)."""
    rng = np.random.default_rng(seed)
    base = {}
    for f in feats:
        x = X[f]
        m = ~np.isnan(x)
        cr = resid(x[m], frame.cells[m])
        sd = float(np.sqrt((cr ** 2).sum() / max(1, m.sum() - len(np.unique(frame.cells[m])))))
        ft = frame.prep(x)
        base[f] = (x, m, sd, ft)
    qi = {q: i for i, q in enumerate(frame.qlev)}
    qcode = np.array([qi[q] for q in frame.quires])
    curve = []
    mde = None
    for fsz in GRID:
        det = 0
        for _ in range(NSIM):
            T = np.zeros(B + 1)
            for f in feats:
                x, m, sd, ft = base[f]
                y = x.copy()
                cm = frame.cells
                for g in np.unique(cm[m]):
                    pos = np.flatnonzero((cm == g) & m)
                    y[pos] = y[rng.permutation(pos)]
                z = rng.standard_normal(frame.K)
                z = (z - z.mean()) / (z.std() if z.std() > 0 else 1)
                y = y + z[qcode] * fsz * sd
                rc = np.zeros(frame.n)
                rc[m] = resid(stats.rankdata(y[m]), cm[m])
                T += frame.eta2_all(ft, rc=rc)
            det += pval(T) < ALPHA_B
        pw = det / NSIM
        curve.append((fsz, pw))
        P(f"  MDE scan {tag}: f={fsz:.1f} SD power={pw:.3f}")
        if pw >= POWER_MIN:
            mde = fsz
            break
    return mde, curve


def analyse(X, frame, featsA, label, P, do_tb=True, seed=SEED):
    """X: feature -> values aligned with frame.folios (nan missing)."""
    TA, perA = omnibus(frame, X, featsA)
    pA = pval(TA)
    used = [f for f in featsA if perA[f] is not None]
    P(f"-- {label}: {frame.n} folios, {frame.ncell} hand x section cells, {frame.K} quires; "
      f"Test A features scored {len(used)}/{len(featsA)}")
    P(f"Test A {label}: omnibus T={TA[0]:.4f} null mean={TA[1:].mean():.4f} null 99th={np.percentile(TA[1:], 99):.4f} "
      f"p={pA:.5f}")
    fam = [f for f in used if is_affix_wlen(f)]
    if fam:
        Tf = np.zeros(B + 1)
        for f in fam:
            Tf += frame.eta2_all(frame.prep(X[f]))
        P(f"  descriptive sub-omnibus (affix/word-length families only, {len(fam)} features, not a call): "
          f"p={pval(Tf):.5f}")
    top = sorted(used, key=lambda f: -(perA[f]["eta2"] - perA[f]["e0"]))
    P(f"  per-feature contributions (DESCRIPTIVE ONLY; excess = eta2 - null mean), top 12 of {len(used)}:")
    P(f"  {'feature':15s} {'n':>4s} {'eta2':>7s} {'null':>7s} {'excess':>7s} {'p_feat':>8s}")
    for f in top[:12]:
        r = perA[f]
        P(f"  {f:15s} {r['n']:4d} {r['eta2']:7.3f} {r['e0']:7.3f} {r['eta2'] - r['e0']:7.3f} {r['p']:8.4f}")
    res = dict(label=label, pA=pA, TA=float(TA[0]), top=[(f, perA[f]["eta2"] - perA[f]["e0"], perA[f]["p"])
                                                          for f in top[:12]])
    if do_tb:
        mde, curve = mde_scan(frame, X, TB, seed + 7, P, label)
        P(f"Test B {label}: MDE = {'> 2.0' if mde is None else f'{mde:.1f}'} SD (80% power, alpha {ALPHA_B}, "
          f"{NSIM} sims; computed before the Test B p-value)")
        TBv, perB = omnibus(frame, X, TB)
        pB = pval(TBv)
        P(f"Test B {label}: omnibus T={TBv[0]:.4f} null mean={TBv[1:].mean():.4f} p={pB:.5f}; " +
          "; ".join(f"{f} eta2={perB[f]['eta2']:.3f} p={perB[f]['p']:.4f} (descriptive)" for f in TB if perB[f]))
        res.update(mde=mde, curve=curve, pB=pB)
    return res


def call_A(res):
    return (res["ZL3b"]["pA"] < ALPHA_PRIMARY and res["RF1b"]["pA"] < ALPHA_REPL and res["IT2a"]["pA"] < ALPHA_REPL)


def call_B(res):
    mdes = [res[t]["mde"] for t in TRANSLITS]
    pbs = [res[t]["pB"] for t in TRANSLITS]
    if all(m is not None and m <= MDE_MAX for m in mdes) and all(p >= ALPHA_B for p in pbs):
        return "CONSTANT_SUPPORTED"
    if any(p < ALPHA_B for p in pbs):
        return "NOT_SUPPORTED"
    return "UNINFORMATIVE"


def outcome(drift, tb):
    if drift and tb == "CONSTANT_SUPPORTED":
        return "CONSTANT_MECHANISM_DRIFTING_CHOICES"
    if drift:
        return "DRIFT_ONLY"
    if tb == "CONSTANT_SUPPORTED":
        return "NO_DRIFT_CONSTANT_SUPPORTED"
    return "NOT_CONFIRMED"


# ---------------------------------------------------------------- fixture (builder copied from s112)
LAYOUT = [  # (hand, section, {quire: n_folios}) -- s112's synthetic layout, copied unchanged
    ("1", "H", {"A": 3, "C": 3, "F": 3, "G": 3, "O": 3, "Q": 4}), ("1", "P", {"S": 7, "O": 7}), ("1", "T", {"A": 1}),
    ("2", "B", {"M": 19}), ("2", "C", {"N": 2}), ("2", "H", {"D": 4, "E": 4, "F": 4, "G": 4}),
    ("2", "T", {"M": 2, "N": 2}), ("3", "H", {"Q": 2}), ("3", "S", {"T": 13, "H": 12}), ("4", "A", {"I": 1}),
    ("4", "C", {"J": 1}), ("5", "H", {"F": 1, "H": 1}), ("5", "T", {"H": 1})]
FIX_FEATS = [f"fa{i:02d}" for i in range(43)] + TB + ["n_tokens"]
PLANTED = [f"fa{i:02d}" for i in range(12)]


def synth_book(planted, seed):
    """Book-level structure: hand, section and (if planted) quire offsets N(0, 0.8) on fa00-fa11."""
    rng = np.random.default_rng(seed)
    meta = {}
    k = 0
    for h, s, qs in LAYOUT:
        for q, n in qs.items():
            for _ in range(n):
                meta[f"x{k:03d}"] = (q, h, s); k += 1
    hands = sorted({m[1] for m in meta.values()}); secs = sorted({m[2] for m in meta.values()})
    quires = sorted({m[0] for m in meta.values()})
    truth = {}
    for feat in FIX_FEATS:
        he = dict(zip(hands, rng.normal(0, 1, len(hands))))
        se = dict(zip(secs, rng.normal(0, 1, len(secs))))
        shift = planted and feat in PLANTED
        qe = dict(zip(quires, rng.normal(0, 0.8, len(quires)) if shift else np.zeros(len(quires))))
        truth[feat] = {f: he[h] + se[s] + qe[q] for f, (q, h, s) in meta.items()}
    return truth, meta


def measure(truth, meta, seed):
    """One transliteration analogue: the book's structure plus fresh N(0, 1) per-folio noise."""
    rng = np.random.default_rng(seed)
    X = {}
    fol = sorted(meta)
    for feat in FIX_FEATS:
        if feat == "n_tokens":
            X[feat] = np.full(len(fol), 200.0)
        else:
            X[feat] = np.array([truth[feat][f] + rng.normal() for f in fol])
    return fol, X


def run_fixture():
    os.makedirs(RUNDIR, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(RUNDIR, f"fixture_{ts}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
    pr = lower_priority()
    t0 = time.time()
    P(f"s114 FIXTURE started {now()}; script sha256 {sha(os.path.abspath(__file__))}; {pr}")
    P("Synthetic books (no real data): s112 LAYOUT, 107 folios, 13 hand x section cells; 43 Test-A features "
      "fa00-fa42 + n_tokens (constant, unscored) + Rw1_line + rhythm_excess = hand + section effects + N(0,1) noise. "
      "planted-batch: fa00-fa11 get quire offsets N(0, 0.8); Test B features never shifted. planted-constant: none.")
    P("Replication analogues: ZL3b/RF1b/IT2a = the same book (same hand, section, quire offsets) with fresh "
      "independent N(0,1) per-folio noise each.")
    P(f"Rule: DRIFT_REAL iff p(ZL3b) < {ALPHA_PRIMARY} and p(RF1b), p(IT2a) < {ALPHA_REPL}; B={B}; seed {SEED}. "
      f"Controls: planted-batch >= {CTRL_BATCH_MIN}/{N_BOOKS}, planted-constant <= {CTRL_CONST_MAX}/{N_BOOKS}.")
    featsA = [f for f in FIX_FEATS if f not in EXCLUDE_A]
    counts = {}
    for kind, planted, off in (("planted-batch", True, 1000), ("planted-constant", False, 2000)):
        nd = 0
        for b in range(N_BOOKS):
            truth, meta = synth_book(planted, SEED + off + b)
            res = {}
            for j, tr in enumerate(TRANSLITS):
                fol, X = measure(truth, meta, SEED + off + 100 * (b + 1) + j)
                frame = Frame(fol, meta, SEED + j)
                do_tb = (kind == "planted-batch" and b == 0 and tr == "ZL3b")
                P(""); P(f"== {kind} book {b} analogue {tr}" + ("  [Test B smoke test]" if do_tb else ""))
                res[tr] = analyse(X, frame, featsA, f"{kind}#{b}/{tr}", P, do_tb=do_tb, seed=SEED + off + b)
            d = call_A(res)
            nd += d
            P(f"BOOK {kind}#{b}: p ZL3b={res['ZL3b']['pA']:.5f} RF1b={res['RF1b']['pA']:.5f} "
              f"IT2a={res['IT2a']['pA']:.5f} -> {'DRIFT_REAL' if d else 'NO_DRIFT'}")
        counts[kind] = nd
        P(f"FIXTURE {kind}: DRIFT_REAL on {nd}/{N_BOOKS} books")
    pb = counts["planted-batch"] >= CTRL_BATCH_MIN
    pc = counts["planted-constant"] <= CTRL_CONST_MAX
    P("")
    P(f"FIXTURE CONTROLS: planted-batch {counts['planted-batch']}/{N_BOOKS} (need >= {CTRL_BATCH_MIN}) "
      f"{'PASS' if pb else 'FAIL'}; planted-constant {counts['planted-constant']}/{N_BOOKS} (need <= {CTRL_CONST_MAX}) "
      f"{'PASS' if pc else 'FAIL'}; overall {'PASS' if pb and pc else 'FAIL'}")
    P(f"elapsed {time.time() - t0:.0f}s; finished {now()}")
    with open(out, "x", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(out, ROOT))
    return 0 if pb and pc else 1


# ---------------------------------------------------------------- real
def verify_stub():
    if not os.path.exists(STUB):
        raise SystemExit(f"stub missing: {STUB}; freeze before --run")
    raw = open(STUB, "rb").read()
    if b"\r" in raw:
        raise SystemExit("stub contains CR bytes")
    n = 0
    for line in raw.decode().split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        h, p = line.split(" ", 1)
        p = p.lstrip("*")
        got = sha(os.path.join(ROOT, p))
        if got != h:
            raise SystemExit(f"stub mismatch for {p}: {got} != {h}")
        n += 1
    return n


def run_real():
    pr = lower_priority()
    nver = verify_stub()
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ROOT, f"results_s114_{ts}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
    t0 = time.time()
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    meta = {r[0]: (r[1], r[2], r[3]) for r in c.execute("SELECT folio, quire, hand_davis, section FROM folios")}
    trs = [r[0] for r in c.execute("SELECT DISTINCT translit FROM folio_features")]
    built = c.execute("SELECT MAX(built_at) FROM build_log").fetchone()[0]
    P(f"s114 whole-book quire omnibus -- REAL RUN. Design DECISIONS.md D-066 (s). started {now()}; {pr}")
    P(f"script tools/s114_quire_omnibus.py sha256 {sha(os.path.abspath(__file__))}; stub "
      f"{os.path.basename(STUB)} verified ({nver} files) sha256 {sha(STUB)}; VKB {os.path.relpath(DB, ROOT)} "
      f"sha256 {sha(DB)} build {built}; B={B}, sims={NSIM}, seed {SEED}, min tokens {MIN_TOK}")
    missing = [t for t in TRANSLITS if t not in trs]
    if missing:
        raise SystemExit(f"transliterations missing from folio_features: {missing}")
    res = {}
    for j, tr in enumerate(TRANSLITS):
        ff = defaultdict(dict)
        for f, feat, val in c.execute("SELECT folio, feature, value FROM folio_features WHERE translit=?", (tr,)):
            ff[feat][f] = val
        keep = sorted(f for f, v in ff["n_tokens"].items()
                      if v is not None and v >= MIN_TOK and f in meta and meta[f][0] and meta[f][1] and meta[f][2])
        featsA = sorted(f for f in ff if f not in EXCLUDE_A)
        X = {feat: np.array([np.nan if ff[feat].get(f) is None else float(ff[feat][f]) for f in keep])
             for feat in featsA + TB}
        frame = Frame(keep, meta, SEED + j)
        P(""); P(f"==== {tr} {'(primary)' if tr == 'ZL3b' else '(replication)'}; Test-A set ({len(featsA)}): "
                 f"{', '.join(featsA)}")
        res[tr] = analyse(X, frame, featsA, tr, P, do_tb=True, seed=SEED + 10 * j)
    drift = call_A(res)
    tb = call_B(res)
    oc = outcome(drift, tb)
    P("")
    P(f"Test A: p ZL3b={res['ZL3b']['pA']:.5f} (rule < {ALPHA_PRIMARY}), RF1b={res['RF1b']['pA']:.5f}, "
      f"IT2a={res['IT2a']['pA']:.5f} (rule < {ALPHA_REPL}) -> {'DRIFT_REAL' if drift else 'NO_DRIFT'}")
    fm = lambda m: ">2.0" if m is None else f"{m:.1f}"
    P(f"Test B: MDE " + ", ".join(f"{t}={fm(res[t]['mde'])}" for t in TRANSLITS) + f" (rule <= {MDE_MAX}); p " +
      ", ".join(f"{t}={res[t]['pB']:.5f}" for t in TRANSLITS) + f" (rule >= {ALPHA_B}) -> {tb}")
    P(f"elapsed {time.time() - t0:.0f}s; finished {now()}")
    P("CALL: s114 TEST_A=" + ("DRIFT_REAL" if drift else "NO_DRIFT") + " " +
      " ".join(f"pA_{t}={res[t]['pA']:.5f}" for t in TRANSLITS) + f" TEST_B={tb} " +
      " ".join(f"MDE_{t}={fm(res[t]['mde'])}" for t in TRANSLITS) + " " +
      " ".join(f"pB_{t}={res[t]['pB']:.5f}" for t in TRANSLITS) + f" OUTCOME={oc}")
    with open(out, "x", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--fixture" in a:
        sys.exit(run_fixture())
    elif "--run" in a:
        run_real()
    else:
        print(__doc__)
