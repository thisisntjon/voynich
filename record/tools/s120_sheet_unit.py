"""s120 -- is the sheet (bifolio) the production batch? Frozen design: DECISIONS.md D-066 (y) = s119's design
(D-066 (x), tools/s119_sheet_unit.py, copied unchanged) with ONLY one change: matched strata are (quire, bound
distance, same-hand-x-section-cell flag), so conjugate pairs are compared only with non-conjugate pairs whose two
pages share (or do not share) a hand x section cell exactly as the conjugates do (L-338). Lead 1 of
.inventory/runs/2026-10-18/bigpicture-physical.md and bigpicture-historical.md.

Question: are the two leaves of one sheet (conjugate leaves, far apart in bound order) more alike in folio
features than non-conjugate same-quire pairs at matched bound distance? F-32's within-quire drift predicts the
opposite (conjugates less alike because they are far apart).

Modes (run from the project root):
  --fixture   power check + fixture controls on synthetic books with the REAL layout (VKB folios table and the
              per-transliteration n_tokens >= 50 page sets). No real feature values other than n_tokens are read.
              Writes runs/s120/fixture_<YYYYmmdd_HHMMSS>.txt.
  --run       real VKB folio_features (read-only). Refuses to run unless s120_sheet_unit.prereg.sha256 verifies.
              Writes results_s120_<YYYYmmdd_HHMMSS>.txt at the project root (never overwrites).

Frozen design:
  * Units: VKB folio_features rows (pages, e.g. f1r, f89r1) with n_tokens >= 50, per transliteration. ZL3b
    primary, RF1b and IT2a replication.
  * Feature set: the s114 Test-A set = every folio_features feature except Rw1_line, rhythm_excess and n_stars
    (tools/s114_quire_omnibus.py EXCLUDE_A; 43 features in s114).
  * Standardisation: each feature z-scored within hand_davis x section cells of the analysis set (ddof 1; a
    zero-SD cell gives z = 0); |z| clipped at 4. Pages in cells with < 3 analysis pages are dropped.
  * Leaf = folio number parsed from the page name (f89r1 -> f89); pages without one (fRos) are dropped.
    Conjugate leaf from the VKB folios.conjugate column. Bound position of a page = 2 * (leaf index within its
    quire, VKB folios rowid order over ALL pages of the quire) + (1 if leaf_side == 'v' else 0). Bound
    distance = |position difference|.
  * Pairs: all page pairs in the same quire on different leaves. Conjugate pair: leaf(b) == conjugate(leaf a).
    Pair distance = sqrt(mean over features present on both pages of (z_a - z_b)^2); a pair needs >= 20 shared
    features. Strata = (quire, bound distance, same-cell flag), same-cell flag = both pages in the same
    hand x section cell; only strata holding >= 1 conjugate and >= 1 non-conjugate pair
    are informative and used.
  * Statistic T = mean over conjugate pairs of (d - mean d of non-conjugate pairs in the same stratum).
    T < 0: conjugates more alike. Computed as a linear statistic: T = sum_i L_i * w_s * (d_i - mean_s d) / K,
    w_s = n_s / (n_s - k_s), which is exactly the matched difference above.
  * Null: B = 10,000 permutations of the conjugate labels among the pairs of each stratum (within quire, at
    matched distance), k_s fixed. p_more = (1 + #{T_null <= T}) / (B + 1); p_less = (1 + #{T_null >= T}) / (B + 1).
  * Decision rule (fixed before data):
      SHEET_BATCH iff p_more < 0.05 on ZL3b and p_more < 0.05 on RF1b and IT2a;
      DRIFT_ONLY  iff p_less < 0.05 on ZL3b and p_less < 0.05 on RF1b and IT2a (conjugates significantly LESS
                  alike; same thresholds, mirrored);
      NULL otherwise.
      The run reports UNDERPOWERED (no real statistic computed) if any real-run gate below fails.
  * Power check (pre-freeze, in --fixture): synthetic books on the ZL3b real layout, 43 features = hand + section
    effects + N(0, 1) page noise; a sheet effect of 0.8 SD (per-bifolio offsets N(0, 0.8), shared by every page
    of the sheet) planted on 12 of the 43 features (the s114 fixture convention). Must reach p_more < 0.05 on
    >= 80% of 200 sims, else UNDERPOWERED and no stub / no real data.
  * Fixture controls (pre-freeze, not tuned):
      (a) 20 planted-sheet books, each measured three times (ZL3b, RF1b, IT2a layouts, fresh noise): the full rule
          must call SHEET_BATCH on >= 16/20;
      (b) no-sheet books: 200 single-analogue sims on the ZL3b layout must give p_more < 0.05 on <= 10% and
          p_less < 0.05 on <= 10%; 20 three-analogue no-sheet books must give a non-NULL call on <= 2/20;
      (c) drift-only books (within-quire linear drift, per-quire slopes N(0, 0.8) SD across the quire span on 12
          features, no sheet effect): 200 sims, p_more < 0.05 on <= 10% (matching on bound distance must absorb
          positional drift). p_less rate is reported, not gated.
    If any control fails, stop.
  * Real-run gates, per transliteration, computed BEFORE the real statistic (real per-page noise): rows of the
    real standardised-input matrix are shuffled jointly within hand x section cells (keeps the real per-page
    noise and the correlation between features, removes sheet and quire structure). (i) real-noise power: plant
    per-sheet offsets z * 0.8 * SD_f (z ~ N(0, 1) per sheet, SD_f = pooled within-cell SD of the raw feature) on
    12 features drawn at random per sim; 200 sims; p_more < 0.05 on >= 80%. (ii) real-noise calibration: same
    shuffle, no plant, 200 sims; p_more < 0.05 and p_less < 0.05 each on <= 10%. If any gate fails on any
    transliteration the CALL is UNDERPOWERED (power) or MISCALIBRATED (calibration) and no real p is computed.
  * Descriptive only (no call): raw mean d of conjugate vs matched non-conjugate pairs, per-quire matched
    differences, Spearman rho of d vs bound distance among non-conjugate same-quire pairs (the F-32 drift
    direction), number of conjugate page pairs and leaf pairs.
  * Seed 20261018. 1 worker, BelowNormal.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import sys, re, sqlite3, hashlib, subprocess, time
from collections import defaultdict
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "vkb", "vkb.sqlite")
RUNDIR = os.path.join(ROOT, "runs", "s120")
STUB = os.path.join(ROOT, "s120_sheet_unit.prereg.sha256")
SEED = 20261018
B = 10000
NSIM = 200
MIN_TOK = 50
MIN_CELL = 3
MIN_SHARED = 20
ZCLIP = 4.0
PLANT_SD = 0.8
N_PLANT = 12
N_FIX_FEAT = 43
ALPHA_PRIMARY = 0.05
ALPHA_REPL = 0.05
ALPHA_POWER = 0.05
POWER_MIN = 0.80
FP_MAX = 0.10
N_BOOKS = 20
BOOK_PASS = 16
BOOK_NULL_MAX = 2
EXCLUDE = {"Rw1_line", "rhythm_excess", "n_stars"}
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
        return "BelowNormal, 1 core"
    except Exception as e:
        return f"priority not lowered: {e}"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- layout
def read_meta(c):
    """Page metadata from the VKB folios table (rowid = bound order)."""
    rows = list(c.execute("SELECT folio, quire, bifolio, conjugate, leaf_side, section, hand_davis "
                          "FROM folios ORDER BY rowid"))
    leafpos = {}
    order = defaultdict(list)
    meta = {}
    for folio, quire, bif, conj, side, sec, hand in rows:
        m = re.match(r"f(\d+)", folio)
        if not m or not quire:
            continue
        leaf = "f" + m.group(1)
        if leaf not in order[quire]:
            order[quire].append(leaf)
        meta[folio] = dict(quire=quire, bif=bif, conj=conj, side=side, sec=sec, hand=hand, leaf=leaf)
    for q, leaves in order.items():
        for i, lf in enumerate(leaves):
            leafpos[(q, lf)] = i
    for f, d in meta.items():
        d["pos"] = 2 * leafpos[(d["quire"], d["leaf"])] + (1 if d["side"] == "v" else 0)
    return meta


class Layout:
    """Analysis pages of one transliteration, their pairs, strata and the shared permutation label set."""

    def __init__(self, pages, meta, seed):
        cells = defaultdict(list)
        for f in pages:
            d = meta[f]
            if d["hand"] and d["sec"]:
                cells[f"{d['hand']}|{d['sec']}"].append(f)
        keep = sorted(f for g, fs in cells.items() if len(fs) >= MIN_CELL for f in fs)
        self.dropped = sorted(set(pages) - set(keep))
        self.pages = keep
        self.n = len(keep)
        self.meta = meta
        self.cell = np.array([f"{meta[f]['hand']}|{meta[f]['sec']}" for f in keep])
        self.ncell = len(set(self.cell))
        self.sheet = [f"{meta[f]['quire']}:{meta[f]['bif']}" for f in keep]
        self.pos = np.array([meta[f]["pos"] for f in keep], float)
        self.quire = [meta[f]["quire"] for f in keep]
        allp = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                a, b = meta[keep[i]], meta[keep[j]]
                if a["quire"] != b["quire"] or a["leaf"] == b["leaf"]:
                    continue
                conj = (a["conj"] == b["leaf"]) or (b["conj"] == a["leaf"])
                dist = abs(a["pos"] - b["pos"])
                allp.append((i, j, conj, a["quire"], int(dist)))
        self.allpairs = allp
        st = defaultdict(list)
        for k, (i, j, cj, q, dist) in enumerate(allp):
            st[(q, dist, bool(self.cell[i] == self.cell[j]))].append(k)
        use = []
        for key, ks in st.items():
            nc = sum(allp[k][2] for k in ks)
            if 0 < nc < len(ks):
                use.append(key)
        use.sort()
        self.strata = use
        I, J, L, S = [], [], [], []
        for si, key in enumerate(use):
            for k in st[key]:
                i, j, cj, q, dist = allp[k]
                I.append(i); J.append(j); L.append(cj); S.append(si)
        self.I = np.array(I); self.J = np.array(J)
        self.L = np.array(L, bool); self.S = np.array(S)
        self.np_ = len(I)
        self.K = int(self.L.sum())
        ns = np.bincount(self.S, minlength=len(use)).astype(float)
        ks = np.bincount(self.S, weights=self.L.astype(float), minlength=len(use))
        self.w = (ns / (ns - ks))[self.S]
        self.ns = ns
        self.n_conj_all = sum(p[2] for p in allp)
        self.leafpairs = sorted({tuple(sorted((meta[keep[i]]["leaf"], meta[keep[j]]["leaf"])))
                                 for i, j, cj in zip(self.I, self.J, self.L) if cj})
        self.leafpairs_all = sorted({tuple(sorted((meta[keep[p[0]]]["leaf"], meta[keep[p[1]]]["leaf"])))
                                     for p in allp if p[2]})
        # shared permutation set: row 0 = observed labels
        rng = np.random.default_rng(seed)
        lab = np.zeros((B + 1, self.np_), np.float32)
        lab[0] = self.L
        for si in range(len(use)):
            pos = np.flatnonzero(self.S == si)
            k = int(self.L[pos].sum())
            order = np.argsort(rng.random((B, len(pos))), axis=1)[:, :k]
            rows = np.repeat(np.arange(1, B + 1), k)
            lab[rows, pos[order].ravel()] = 1.0
        self.lab = lab

    def stat(self, Z):
        """Z: n x F standardised matrix (nan = missing). Returns T vector (obs + B null) and pair distances."""
        D = Z[self.I] - Z[self.J]
        ok = ~np.isnan(D)
        cnt = ok.sum(axis=1)
        sq = np.where(ok, D ** 2, 0.0).sum(axis=1)
        d = np.sqrt(sq / np.maximum(cnt, 1))
        valid = cnt >= MIN_SHARED
        if not valid.all():
            # drop pairs without enough shared features from their stratum (recompute centring on valid pairs)
            d = np.where(valid, d, np.nan)
        mean_s = np.array([np.nanmean(d[self.S == s]) for s in range(len(self.strata))])
        c = np.nan_to_num(d - mean_s[self.S])
        T = self.lab @ (self.w * c).astype(np.float32) / self.K
        return T.astype(float), d


def standardise(X, cell):
    """X: n x F raw (nan missing). z within cells, ddof 1, zero-SD -> 0, clip |z| at ZCLIP."""
    Z = np.full_like(X, np.nan, dtype=float)
    for g in np.unique(cell):
        m = cell == g
        x = X[m]
        mu = np.nanmean(x, axis=0)
        cnt = (~np.isnan(x)).sum(axis=0)
        sd = np.nanstd(x, axis=0, ddof=1) if m.sum() > 1 else np.zeros(x.shape[1])
        sd = np.where((cnt > 1) & (sd > 1e-12), sd, np.inf)
        Z[m] = (x - mu) / sd
    Z = np.where(np.isnan(X), np.nan, np.nan_to_num(Z, nan=0.0))
    return np.clip(Z, -ZCLIP, ZCLIP)


def pvals(T):
    return ((1 + int((T[1:] <= T[0] + 1e-12).sum())) / (B + 1),
            (1 + int((T[1:] >= T[0] - 1e-12).sum())) / (B + 1))


def call(p):
    """p: translit -> (p_more, p_less)."""
    if p["ZL3b"][0] < ALPHA_PRIMARY and p["RF1b"][0] < ALPHA_REPL and p["IT2a"][0] < ALPHA_REPL:
        return "SHEET_BATCH"
    if p["ZL3b"][1] < ALPHA_PRIMARY and p["RF1b"][1] < ALPHA_REPL and p["IT2a"][1] < ALPHA_REPL:
        return "DRIFT_ONLY"
    return "NULL"


def pooled_sd(X, cell):
    out = np.zeros(X.shape[1])
    for f in range(X.shape[1]):
        x = X[:, f]
        m = ~np.isnan(x)
        r = x[m].copy()
        cm = cell[m]
        for g in np.unique(cm):
            r[cm == g] -= r[cm == g].mean()
        dfree = max(1, m.sum() - len(np.unique(cm)))
        out[f] = np.sqrt((r ** 2).sum() / dfree)
    return out


def sheet_codes(lay):
    lev = sorted(set(lay.sheet))
    return np.array([lev.index(s) for s in lay.sheet]), len(lev)


def describe(lay, P, tag):
    qs = sorted(set(lay.quire))
    P(f"-- {tag}: {lay.n} pages (dropped for cell < {MIN_CELL}: {len(lay.dropped)} {lay.dropped}), {lay.ncell} hand x "
      f"section cells, {len(qs)} quires; same-quire different-leaf pairs {len(lay.allpairs)}, of which conjugate "
      f"{lay.n_conj_all} ({len(lay.leafpairs_all)} leaf pairs)")
    P(f"   informative strata (quire, bound distance, same-cell flag) {len(lay.strata)}; pairs used {lay.np_}; conjugate page pairs used "
      f"{lay.K} covering {len(lay.leafpairs)} conjugate leaf pairs: {' '.join(a + '/' + b for a, b in lay.leafpairs)}")


# ---------------------------------------------------------------- synthetic books (real layout)
def synth(lay, rng, sheet=0.0, drift=0.0, nfeat=N_FIX_FEAT, nplant=N_PLANT):
    """hand + section effects + N(0,1) noise; optional per-sheet N(0, sheet) offsets and within-quire drift on
    the first nplant features."""
    cells = sorted(set(lay.cell))
    ci = np.array([cells.index(c) for c in lay.cell])
    X = rng.normal(0, 1, (len(cells), nfeat))[ci] + rng.normal(0, 1, (lay.n, nfeat))
    if sheet > 0:
        sc, ns = sheet_codes(lay)
        X[:, :nplant] += rng.normal(0, sheet, (ns, nplant))[sc]
    if drift > 0:
        for q in set(lay.quire):
            m = np.array([x == q for x in lay.quire])
            p = lay.pos[m]
            span = (p - p.min()) / max(1.0, p.max() - p.min()) * 2 - 1
            X[np.ix_(m, np.arange(nplant))] += np.outer(span, rng.normal(0, drift, nplant))
    return X


def layout_pages(c, tr, meta):
    pages = []
    for f, v in c.execute("SELECT folio, value FROM folio_features WHERE translit=? AND feature='n_tokens'", (tr,)):
        if v is not None and v >= MIN_TOK and f in meta:
            pages.append(f)
    return sorted(pages)


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
    P(f"s120 FIXTURE + POWER CHECK started {now()}; script sha256 {sha(os.path.abspath(__file__))}; {pr}")
    P(f"Synthetic books on the REAL layout (VKB folios table; per-transliteration n_tokens >= {MIN_TOK} page sets; "
      f"no other real feature value read). {N_FIX_FEAT} features = hand x section effects + N(0,1) noise; sheet plant "
      f"N(0, {PLANT_SD}) per bifolio on {N_PLANT} features. B={B}, sims={NSIM}, seed {SEED}.")
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    meta = read_meta(c)
    lays = {}
    for j, tr in enumerate(TRANSLITS):
        lays[tr] = Layout(layout_pages(c, tr, meta), meta, SEED + j)
        describe(lays[tr], P, f"layout {tr}")
    c.close()
    lz = lays["ZL3b"]
    rng = np.random.default_rng(SEED + 1)

    def rate(sheet, drift, n=NSIM):
        pm, pl = [], []
        for _ in range(n):
            X = synth(lz, rng, sheet=sheet, drift=drift)
            T, _ = lz.stat(standardise(X, lz.cell))
            a, b = pvals(T)
            pm.append(a < ALPHA_POWER); pl.append(b < ALPHA_POWER)
        return float(np.mean(pm)), float(np.mean(pl))

    P("")
    pw, _ = rate(PLANT_SD, 0.0)
    pw_ok = pw >= POWER_MIN
    P(f"POWER CHECK (ZL3b layout, sheet {PLANT_SD} SD on {N_PLANT}/{N_FIX_FEAT} features): p_more < {ALPHA_POWER} on "
      f"{pw:.3f} of {NSIM} sims (need >= {POWER_MIN}) -> {'PASS' if pw_ok else 'UNDERPOWERED'}")
    fm, fl = rate(0.0, 0.0)
    nb_ok = fm <= FP_MAX and fl <= FP_MAX
    P(f"CONTROL (b) no-sheet single-analogue: p_more < 0.05 rate {fm:.3f}, p_less < 0.05 rate {fl:.3f} "
      f"(need each <= {FP_MAX}) -> {'PASS' if nb_ok else 'FAIL'}")
    dm, dl = rate(0.0, PLANT_SD)
    dr_ok = dm <= FP_MAX
    P(f"CONTROL (c) drift-only (within-quire slopes N(0, {PLANT_SD}) on {N_PLANT} features): p_more < 0.05 rate "
      f"{dm:.3f} (need <= {FP_MAX}) -> {'PASS' if dr_ok else 'FAIL'}; p_less < 0.05 rate {dl:.3f} (reported)")
    counts = {}
    for kind, sh in (("planted-sheet", PLANT_SD), ("no-sheet", 0.0)):
        calls = []
        for bk in range(N_BOOKS):
            brng = np.random.default_rng(SEED + (1000 if sh else 2000) + bk)
            # one book: the same hand/section effects and sheet offsets per page, re-measured on each layout
            cells = sorted(set(meta[f]["hand"] + "|" + meta[f]["sec"] for f in meta if meta[f]["hand"] and meta[f]["sec"]))
            ceff = {g: brng.normal(0, 1, N_FIX_FEAT) for g in cells}
            sheets = sorted({f"{m['quire']}:{m['bif']}" for m in meta.values()})
            seff = {s: brng.normal(0, sh, N_PLANT) if sh else np.zeros(N_PLANT) for s in sheets}
            p = {}
            for tr in TRANSLITS:
                lay = lays[tr]
                X = np.array([ceff[g] for g in lay.cell]) + brng.normal(0, 1, (lay.n, N_FIX_FEAT))
                X[:, :N_PLANT] += np.array([seff[s] for s in lay.sheet])
                T, _ = lay.stat(standardise(X, lay.cell))
                p[tr] = pvals(T)
            cl = call(p)
            calls.append(cl)
            P(f"BOOK {kind}#{bk}: " + " ".join(f"{t} p_more={p[t][0]:.4f} p_less={p[t][1]:.4f}" for t in TRANSLITS)
              + f" -> {cl}")
        counts[kind] = calls
    na = sum(c == "SHEET_BATCH" for c in counts["planted-sheet"])
    nn = sum(c != "NULL" for c in counts["no-sheet"])
    a_ok = na >= BOOK_PASS
    n_ok = nn <= BOOK_NULL_MAX
    P(f"CONTROL (a) planted-sheet books: SHEET_BATCH {na}/{N_BOOKS} (need >= {BOOK_PASS}) -> {'PASS' if a_ok else 'FAIL'}")
    P(f"CONTROL (b2) no-sheet books: non-NULL {nn}/{N_BOOKS} (need <= {BOOK_NULL_MAX}) -> {'PASS' if n_ok else 'FAIL'}")
    ok = pw_ok and nb_ok and dr_ok and a_ok and n_ok
    P("")
    P(f"FIXTURE OVERALL: {'PASS' if ok else 'FAIL'}; power {pw:.3f}; elapsed {time.time() - t0:.0f}s; finished {now()}")
    with open(out, "x", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(out, ROOT))
    return 0 if ok else 1


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
    out = os.path.join(ROOT, f"results_s120_{ts}.txt")
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
    t0 = time.time()
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    meta = read_meta(c)
    built = c.execute("SELECT MAX(built_at) FROM build_log").fetchone()[0]
    P(f"s120 sheet as unit -- REAL RUN. Design DECISIONS.md D-066 (y). started {now()}; {pr}")
    P(f"script tools/s120_sheet_unit.py sha256 {sha(os.path.abspath(__file__))}; stub {os.path.basename(STUB)} verified "
      f"({nver} files) sha256 {sha(STUB)}; VKB {os.path.relpath(DB, ROOT)} sha256 {sha(DB)} build {built}; B={B}, "
      f"sims={NSIM}, seed {SEED}, min tokens {MIN_TOK}")
    data = {}
    for j, tr in enumerate(TRANSLITS):
        ff = defaultdict(dict)
        for f, feat, val in c.execute("SELECT folio, feature, value FROM folio_features WHERE translit=?", (tr,)):
            ff[feat][f] = val
        feats = sorted(f for f in ff if f not in EXCLUDE)
        lay = Layout(layout_pages(c, tr, meta), meta, SEED + j)
        X = np.array([[np.nan if ff[ft].get(f) is None else float(ff[ft][f]) for ft in feats] for f in lay.pages])
        data[tr] = (lay, X, feats)
    c.close()
    # gates first (real noise), no real statistic yet
    gate = {}
    for j, tr in enumerate(TRANSLITS):
        lay, X, feats = data[tr]
        P(""); P(f"==== {tr} {'(primary)' if tr == 'ZL3b' else '(replication)'}; features ({len(feats)}): {', '.join(feats)}")
        describe(lay, P, tr)
        rng = np.random.default_rng(SEED + 100 + j)
        sd = pooled_sd(X, lay.cell)
        sc, ns = sheet_codes(lay)
        pm, fm, fl = [], [], []
        for plant in (True, False):
            for _ in range(NSIM):
                Y = X.copy()
                for g in np.unique(lay.cell):
                    pos = np.flatnonzero(lay.cell == g)
                    Y[pos] = Y[rng.permutation(pos)]
                if plant:
                    fs = rng.choice(len(feats), N_PLANT, replace=False)
                    Y[:, fs] += rng.standard_normal((ns, N_PLANT))[sc] * PLANT_SD * sd[fs]
                T, _ = lay.stat(standardise(Y, lay.cell))
                a, b = pvals(T)
                if plant:
                    pm.append(a < ALPHA_POWER)
                else:
                    fm.append(a < ALPHA_POWER); fl.append(b < ALPHA_POWER)
        gate[tr] = (float(np.mean(pm)), float(np.mean(fm)), float(np.mean(fl)))
        P(f"GATE {tr} (computed before the real statistic): real-noise power at {PLANT_SD} SD on {N_PLANT} random "
          f"features = {gate[tr][0]:.3f} (need >= {POWER_MIN}); real-noise calibration p_more<0.05 rate "
          f"{gate[tr][1]:.3f}, p_less<0.05 rate {gate[tr][2]:.3f} (need each <= {FP_MAX})")
    under = [t for t in TRANSLITS if gate[t][0] < POWER_MIN]
    miscal = [t for t in TRANSLITS if gate[t][1] > FP_MAX or gate[t][2] > FP_MAX]
    gstr = " ".join(f"power_{t}={gate[t][0]:.3f}" for t in TRANSLITS) + " " + \
        " ".join(f"fp_{t}={gate[t][1]:.3f}/{gate[t][2]:.3f}" for t in TRANSLITS)
    sz = {t: data[t][0] for t in TRANSLITS}
    nstr = " ".join(f"nconj_{t}={sz[t].K}({len(sz[t].leafpairs)}leaf)" for t in TRANSLITS)
    if under or miscal:
        oc = "UNDERPOWERED" if under else "MISCALIBRATED"
        P(""); P(f"Gates failed: underpowered {under}, miscalibrated {miscal}; no real statistic computed.")
        P(f"elapsed {time.time() - t0:.0f}s; finished {now()}")
        P(f"CALL: s120 OUTCOME={oc} {nstr} {gstr}")
    else:
        p = {}
        for tr in TRANSLITS:
            lay, X, feats = data[tr]
            T, d = lay.stat(standardise(X, lay.cell))
            p[tr] = pvals(T)
            cm = np.nanmean(d[lay.L]); ncm = np.nanmean(d[~lay.L])
            P(""); P(f"REAL {tr}: T (conjugate minus matched non-conjugate mean distance) = {T[0]:+.4f}; null mean "
                     f"{T[1:].mean():+.4f}, null sd {T[1:].std():.4f}; p_more={p[tr][0]:.5f} p_less={p[tr][1]:.5f}")
            P(f"  descriptive: raw mean d conjugate {cm:.4f} vs non-conjugate in informative strata {ncm:.4f}")
            for q in sorted(set(lay.quire)):
                sel = np.array([lay.quire[i] == q for i in lay.I]) if lay.np_ else np.array([], bool)
                if not sel.any() or not lay.L[sel].any():
                    continue
                mean_s = np.array([np.nanmean(d[lay.S == s]) for s in range(len(lay.strata))])
                cc = (d - mean_s[lay.S]) * lay.w
                P(f"  descriptive quire {q}: conjugate pairs {int(lay.L[sel].sum())}, matched diff "
                  f"{np.nansum(cc[sel & lay.L]) / lay.L[sel].sum():+.4f}")
            # F-32 direction (descriptive): all non-conjugate same-quire pairs, d vs bound distance
            Z = standardise(X, lay.cell)
            dd, bd = [], []
            for i, j, cj, q, dist in lay.allpairs:
                if cj:
                    continue
                D = Z[i] - Z[j]; ok = ~np.isnan(D)
                if ok.sum() >= MIN_SHARED:
                    dd.append(np.sqrt((D[ok] ** 2).mean())); bd.append(dist)
            rho, pr_ = stats.spearmanr(bd, dd)
            P(f"  descriptive F-32 direction: Spearman rho(d, bound distance) over {len(dd)} non-conjugate same-quire "
              f"pairs = {rho:+.3f} (asymptotic p {pr_:.4f}, pairs not independent)")
        oc = call(p)
        P("")
        P(f"Rule: SHEET_BATCH iff p_more ZL3b < {ALPHA_PRIMARY} and RF1b, IT2a < {ALPHA_REPL}; DRIFT_ONLY mirrored on "
          f"p_less; else NULL. p_more " + ", ".join(f"{t}={p[t][0]:.5f}" for t in TRANSLITS) + "; p_less " +
          ", ".join(f"{t}={p[t][1]:.5f}" for t in TRANSLITS) + f" -> {oc}")
        P(f"elapsed {time.time() - t0:.0f}s; finished {now()}")
        P(f"CALL: s120 OUTCOME={oc} " + " ".join(f"pmore_{t}={p[t][0]:.5f} pless_{t}={p[t][1]:.5f}" for t in TRANSLITS)
          + f" {nstr} {gstr}")
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
