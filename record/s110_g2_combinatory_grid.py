"""S110 (Phase 7 grid G2; D-066 (o), approved by Jon 2026-10-18 14:42 'Freeze G2, run after s108 (Recommended)'):
can a full-size combinatory-table procedure reproduce the manuscript's JOINT profile, and does content input add
anything over random input?

RIVALS (D-066 (o)): H-19/H-05 procedure from a combinatory table without content (random input passes as well as
 content input); H-19 with content (content input passes and beats its random twin); neither (no cell passes).

PRE-FREEZE AUDIT CHECK (L-227; <team-comms> grepped for 's110', 'G2', 'grid G2', 'combinatory' at 16:08-16:12 PDT, file
 mtimes used for order):
 - No audit addresses lead s110 / Phase 7 grid G2.  <team-comms>,json,prereg.sha256},
   <team-comms> and DAYBREAK_* 'S110' lines are Daybreak db-s110
   (label anchor), a different run (alias map, TEAM-HANDOFF.md).
 - VOYNICH-CURRENT-STATE-2026-10-18.md (mtime 15:58) item 7: 'the successor must first recover its own planted
   mechanism at target scale, then jointly predict rhythm, entropy, frame transition, recurrence, and locality'.
   Consistent with D-066 (o) (fixture gate at target scale, then the joint criteria); not blocking.
 - codex_lab/reviews/s107_lull_cadence_physical_unit_correction_2026-10-18.md (mtime 15:25): manuscript Lullian cells
   are fixed four-character units; OCR token-length cadence of the 1515 rows is withdrawn.  Consistent with G2a's
   4-letter cells (Llull); a fixed cell has no length variance, so any G2a rhythm comes only from the glyph groups.
   Not blocking; recorded as an interpretation limit.
 - codex_lab/reviews/s101_loqo_power_terminal_audit_2026-10-18.md (mtime 15:19): 'future comparisons must demonstrate
   target-scale planted recovery before scoring' = the D-066 (o) fixture gate.  Not blocking.
 - <team-comms>: s107 interpretation limit (Llull rows only); not blocking.
 No audit conflicts with D-066 (o).

JOINT CRITERIA PER CELL (D-066 (o) = G1, D-066 (j), implemented by s104 incl. its (j-amend) A1 target calibration;
 s104's code imported unchanged and hash-checked against its stub, da6c33be...):
 SIG  four-part core signature (S87.c1; ORDER_BAND; R_within(1) > 1 p < 0.05; R_cross < R_within; locality band from
      VOY ZL3b/RF1b/IT2a) on every applicable segmenter (identity, slot, affix2; applicable iff core share >= 0.5).
 BAT  s67 slot battery >= 4/6 on >= 8/15 folds on each of ZL3b, RF1b, IT2a.
 RHY  within-line length rhythm excess > 0 with p < 0.05 (S102.rhythm).
 H2   h2 in [2.023, 2.234].
 LAG2 lag-2 prefix residue <= 0.5 x the s81 table's (s104 lag2 jobs, S98.measure).
 LOQO held-out match >= 8/15 folds on each of ZL3b, RF1b, IT2a (s104 survivor fold rule: fold holds iff S87.c1 on the
      replicate text with SlotSegmenter cores AND its s67 battery row >= 4/6 against the real held-out quire).
 A1 (s104, j-amend): every criterion the manuscript itself fails becomes target-relative with s104's exact rules
      (S104.sig_rel, min VOY battery folds, min VOY rhythm excess, widened h2 band, VOY 90th-percentile lag-2 bar,
      LOQO bar = min VOY fold count).
 PASS(cell) = SIG and BAT and RHY and H2 and LAG2 and LOQO.
 KILLING PROPERTY of a cell = every criterion it fails (printed per cell).
GATES (as s104): S (s97 gate: PC1 planted LP91 on >= 2/3 seeds, PC2 IT2a-as-control full, NC Augustine not full) and
 L (lag-2 validity: manuscript <= bar, s81 table > bar).  GATE = S and L and the fixture gate (below) passed.
PRE-REGISTERED BATTERY FIX (D-066 (o)): a Measured job that raises (the zero-denominator case seen on short s107 texts)
 makes THAT block NOT ASSESSABLE (row n = NA, not counted as holding) instead of failing the whole battery; the
 battery is then scored on the remaining blocks with the unchanged thresholds (>= 4/6 per block, >= 8 blocks of 15).
 For LOQO a fold whose Measured job raises is NOT ASSESSABLE (does not hold).  Shown descriptively on the s107 texts
 (T1, T2, T3 with s107's loaders, layout and battery seeds); s107 is NOT refiled.

CONSTRUCTIONS (all parameters a priori or fitted on training quires; never tuned on any score):
 Inputs (D-066 (o)): content = the s102 Latin medical recipe vocabulary (S102.load_p1: CREMMA Medic MSS + Macer
   Floridus) in text order; content-shuffled = the same words shuffled within each source line
   (default_rng([SEED, 77])); random = i.i.d. uniform codebook indices of the same length.
   FIXED CODEBOOK: word types ranked by frequency in the full content text (ties by string), index k in [0, V);
   position u_k = (perm[k] + 0.5) / V with perm = default_rng([SEED, 11]).permutation(V).  An input unit is a codebook
   index; random input draws k uniformly from [0, V).  The construction reads the unit through u.
 G2a Lullian figure.  Llull's alphabet B C D E F G H I K (9 letters) plus his separator T (Ars brevis / 1515 Tabula
   generalis: every 4-letter cell contains T).  Figure = the Tabula generalis: 84 columns (the 3-letter combinations
   of B..K in lexicographic order) x 20 cells of 4 letters, cell order per column xyz: xyzt, xytx, xyty, xytz, xztx,
   xzty, xztz, xtxy, xtxz, xtyz, yztx, yzty, yztz, ytxy, ytxz, ytyz, ztxy, ztxz, ztyz, txyz (= the 1515 rows, e.g.
   bctb bctc btbc).  A printed row = one cell position j across consecutive columns, so neighbouring cells share
   letters.  1,680 rows (j, start column c0); one input unit per manuscript line selects row floor(u x 1680) =
   (j = r mod 20, c0 = r div 20); the line of n tokens writes cells (c0 + i mod 84, j), i < n.  Letters (10 symbols
   incl. T) are mapped ONCE to glyph groups: symbols ranked by frequency in the whole figure (ties by letter) ->
   SlotSegmenter cores of the training quires ranked by token count (the s104 survivor fill rule); token = the four
   groups concatenated.
 G2b prefix x core x suffix table (fitted only on training quires; SlotSegmenter fitted on the training words;
   affix alphabets = the 24 most frequent values per slot, the rest pooled into one bucket drawn by frequency):
   CORE: inverse-CDF lookup of u in a table with weights (1 - phi) g + phi l_q: g = training core distribution;
     l_q = a quire-local pool of m types drawn (without replacement, by count) from the training core tail (ranks >=
     50), weights by count; a new pool per quire (and per held-out replicate).  (phi, m) fitted DIRECTLY from block
     coverage on the training quires (blocks = quires): the S87 coverage statistic (share of a block's types seen in
     another block) and the types-per-block statistic, each as observed / token-permutation mean (20 permutations),
     matched by a grid phi in {0, .05, .1, .15, .2, .3, .4, .5, .6} x m in {25, 50, 100, 200, 400} (min squared
     relative error of the two coverage ratios; simulated with uniform u).  Never a joint descent over other
     properties (L-221).
   PREFIX: line-initial prefix from the training line-initial distribution; then a first-order step: P(p_t) prop. to
     T[p_{t-1}, p_t] x theta_line(p_t) / pbar(p_t) (T add-0.5 from training via R9.fit_basic, F-46), theta_line = r9's
     drifting state theta_n = (1 - lam) theta_{n-1} + lam Dir(beta pbar), reset per quire (drift scale = 1/lam lines).
     (lam, beta) on r9's grid (R9.LAMS x R9.BETAS) fitted DIRECTLY to the training between-line share decay S(D),
     D = 1..4 (r9's R9a statistic: R9.profile per quire, mean over quires; min squared relative error of the mean of 3 simulations),
     simulating the full affix process on the training layout.  [Pre-fixture design note, 16:3x PDT, before any fixture run:
     r9.fit_drift (rw, rx, rx3 on a chain-free drift generator) read a planted scale 5 as 1.4 when the first-order
     chain is present, in a smoke test of the code (no fixture verdict computed); the decay fit is r9's own
     drift-scale statistic.]
   SUFFIX: line-initial from the training line-initial distribution; then with probability kappa copy the suffix d
     back in the line, d in 1..min(6, t-1) with weight exp(-(d-1)/tau) (short-range order decaying over ~6 words, r6),
     else draw from the drifting theta_line ((lam, beta) fitted on the suffix S(D) as for prefixes).  (kappa, tau) fitted on the training suffix recurrence profile
     R(d), d = 1..6 (within-line same-suffix rate at distance d / within-line shuffle expectation) on a grid kappa in
     {0, .05, .1, .15, .2, .3, .4} x tau in {0.5, 1, 2, 4}.
   Token = prefix + core + suffix.
 CELLS: {G2a, G2b} x {content, content_shuf, random} = 6 cells.  In-sample text of a cell: the ZL3b 22,500-token
   real-page layout (S87.layout, as VOY_ZL3b); every quire's pages generated by the model fitted WITHOUT that quire
   (cross-fitted), input stream in reading order.  LOQO (15 quires, each of ZL3b, RF1b, IT2a): fit on the training
   quires of T; generate the training layout (battery train text) and the held-out quire layout in replicates (s104 /
   s91 rule, pages 'r<j>:<id>', new local pool per replicate) cut to 22,500; content input cyclic from offset 0 over
   the training layout, continuing into the held-out replicates (s104 rule); random input drawn per fold.
CALLS (printed True/False):
 G2_ANY_PASS = GATE and PASS(any of the 6 cells).
 CONTENT_ADDS(construction) = PASS(content cell) AND its LOQO held folds (sum over ZL3b, RF1b, IT2a) exceed both the
   content-shuffled and the random twin's (strictly).  CONTENT_ADDS = any construction.
STOPPING RULE / VERDICT (D-066 (o)), exactly one reading:
 GATE False -> 'uninformative: gate failed (<which>)'.
 no cell passes -> 'combinatory-table procedures closed within G2' with the killing property per cell.
 cells pass, CONTENT_ADDS False -> 'procedure without content (H-05/H-19 procedure): no decipherment attempted'.
 CONTENT_ADDS -> 'candidate encoding: predict held-out quires and the Phase 7.2 cribs before anything is read'.
FIXTURE GATE (--fx110; synthetic only, reads no Voynich data; writes runs/s110/fixture_<stamp>.txt):
 FX1 planted G2b world at target scale (15 quires x 10 pages x 18 lines, lengths 1 + Poisson(7); synthetic core /
     prefix / suffix strings; planted phi 0.3, m 100, prefix chain T Dirichlet(0.5) rows, drift lam 0.2 beta 10
     (scale 5 lines) on both affix streams, suffix kappa 0.2 tau 2; random input).  Per fold: fit on the 14 training
     quires, regenerate the held-out quire (replicates to 22,500).  Fold RECOVERED iff locality inside its band
     (the replicate's S87 locality ratio inside the planted text's S87 locality band, S87.loc_band_from) AND the
     profile matched (S104.sig_rel of the replicate against the planted profile: all four parts, AND battery row
     >= 4/6 against the planted held-out quire).  Pass iff >= 10/15 folds; also median fitted drift scale (prefix and
     suffix) within [2.5, 10] and median prefix-chain total variation <= 0.15 (planted drift scale and prefix chain
     recovered).  The fitted (phi, m) is printed per fold (descriptive): in a pre-fixture smoke test phi and m traded
     off (planted 0.3/100 read as 0.6/200 at equal coverage), so the parameter is not used as the band; the band is
     the locality statistic itself (the property s94 failed, L-221).  Locality grid points average 2 simulations.
 FX2 planted G2a text (same layout; planted glyph map of 10 prefix-free groups; random input): decoding with the known
     map recovers the planted row on >= 0.80 of the held-out quire's lines on >= 10/15 folds, AND the fold rule
     (S104.sig_rel against the planted profile + battery row >= 4/6, map refitted from the training quires) holds on
     >= 10/15 folds.
 FX3 prose fails: Latin prose (Augustine, S87.load_control; a control text) on the same layout: the G2b fold rule
     (target = the prose) holds on < 10/15 folds, and known-map G2a decoding recovers < 0.80 of lines.
 FX4 battery fix: a control text with an empty block gives that block NA and the battery is still scored.
 FIXTURE_PASS = FX1 and FX2 and FX3 and FX4.  At most two revisions (recorded below).  The real run stops unless the
 latest runs/s110/fixture_*.txt prints FIXTURE_PASS = True.
DESIGN REVISIONS (at most two):
 REVISION 1 (after fixture run 1, runs/s110/fixture_20261018-162859.txt, FIXTURE_PASS = False: FX1 4/15, FX2 fold rule
   0/15; FX3, FX4 True).  Diagnostic on the synthetic worlds only (runs/s110/diag_oracle_after_fixture1.{py,txt}):
   the run-1 fold rule fails the TRUE planted generator itself: FX1 oracle sig_rel 8/15 (R_cross < R_within is a coin
   flip when the planted world has no in-line core reuse; Rc1 ranged 0.75-1.31 against the 1.25 band) with battery
   >= 4/6 on 12/15; FX2 known-map oracle sig_rel 12/15, battery >= 4/6 on 2/15.  Changes (fixture only; the real-data
   path and the D-066 (o) criteria are unchanged):
   (a) FX1 'profile matched' = the replicate's o100, o200, R_within(1), R_cross(1) and locality ratio each inside the
       planted generator's own envelope (mean +- 3 SD over 15 oracle replicates, one per fold, fresh seeds) AND
       battery row >= 4/6, AND locality inside the planted S87 band (as before).  FX1 also requires the oracle's
       battery >= 4/6 on >= 10/15 folds (power of the battery part).
   (b) planted G2b world: prefix and suffix glyphs made disjoint from the core glyphs (run 1 had 'o' and 'd' in both;
       SlotSegmenter then split prefixes into core letters, e.g. 'qod').
   (c) FX2 uses the KNOWN planted map: a G2a glyph map is a fixed assignment of figure letters to glyph groups and is
       not a statistic recoverable from G2a output (run 1 refitted it from SlotSegmenter cores of the 4-group tokens,
       which are not the groups).  FX2 = decoding >= 0.80 on >= 10/15 AND S104.sig_rel of the known-map replicate on
       >= 10/15; its battery count is printed (oracle power 2/15 in the diagnostic: a G2a exclusion resting on BAT or
       LOQO is UNINFORMATIVE under D-068 unless the real run shows otherwise).
   FX3 (prose) keeps the run-1 rule.
FIXTURE OUTCOME (no stub frozen; no Voynich statistic computed; results_s110.txt not created):
 run 1 16:28:59-16:55:34 FAIL (FX1 4/15, FX2 0/15, FX3 True, FX4 True) -> REVISION 1.
 run 2 17:06:17-17:26:32 FAIL (FX1 3/15: locality band 12/15, oracle envelope 11/15, battery >= 4/6 5/15, oracle 13/15;
   drift scale median 3.3/3.3 vs planted 5, prefix TV 0.060; FX2 decoding 15/15, sig_rel 9/15; FX3 True; FX4 True).
 Diagnostic (runs/s110/diag_battery_after_fixture2.{py,txt}, synthetic only): per-prediction holds over 15 folds,
   fitted vs oracle: P1 8 vs 11, P2 10 vs 10, P3 7 vs 8, P4 0 vs 0, P5 15 vs 15, P7 15 vs 15; fitted battery >= 4/6 on
   8/15, oracle 12/15.  The fitted G2b loses within-line length rhythm (P1): SlotSegmenter's slot boundaries absorb core
   letters into prefixes and the construction draws prefix and core independently.
 STOPPED at the fixture gate (17:38 PDT): REVISION 2 not used.  Dropping the battery from FX1 would give 10/15 on run
   2's numbers already seen (post hoc weakening); drawing the core conditional on the prefix would change the frozen
   G2b construction (D-066 (o)).  Either needs a lead decision recorded in D-066 before a re-freeze.
COMPUTE: profiles on the GPU (torch cuda); fits, battery and lag-2 in 2 spawn workers at BelowNormal, OMP threads 1;
 free RAM >= 4 GB checked before each pool (else wait up to 10 min, then stop).  Limit 4 CPU-hours.
OUTPUT: results_s110.txt (never overwritten) and runs/s110/ sidecars.
Run: python -I s110_g2_combinatory_grid.py   Fixture: --fx110   Stub list: --list-files
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from collections import Counter, OrderedDict  # noqa: E402
from datetime import datetime  # noqa: E402
from itertools import combinations  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import torch  # noqa: E402

import s97_language_rescue_controls as S97  # noqa: E402

_S97_EMIT, _S97_FLUSH, _S97_MEASURE = S97.emit, S97.flush, S97.measure_job
import s107_tabular_medical_reference as S107  # noqa: E402  (patches S97.emit/flush/measure_job on import: restored next)

S97.emit, S97.flush, S97.measure_job = _S97_EMIT, _S97_FLUSH, _S97_MEASURE
import s104_g1_encoding_grid as S104  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

_spec = importlib.util.spec_from_file_location("r9", ROOT / "runs" / "roach-r9" / "r9.py")
R9 = importlib.util.module_from_spec(_spec)
sys.modules["r9"] = R9
_spec.loader.exec_module(R9)

S87, S67, S80, S91, S98, S102, S81 = S97.S87, S97.S67, S97.S80, S104.S91, S104.S98, S104.S102, S104.S81

SELF = ROOT / "s110_g2_combinatory_grid.py"
STUB = ROOT / "s110_g2_combinatory_grid.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s110"
FIXTURE = "--fx110" in sys.argv
LIST_FILES = "--list-files" in sys.argv
WELLFORMED = "--wellformed" in sys.argv
S104_HASH = "da6c33be8f4143bd0f681bc8da211031331cdc6f90cf786185362a3254e93e70"  # s104 stub entry
SEED = 20261110
N_TOT, NB, N_MATCH = S87.N_TOT, S87.NB, S97.N_MATCH
MIN_CORE_SHARE = S97.MIN_CORE_SHARE
BAT_FOLD_MIN, BAT_MIN_FOLDS = S97.BAT_MIN_HOLD, S97.BAT_MIN_FOLDS
LOQO_MIN = 8
FX_MIN = 10
N_WORKERS = 2
MIN_FREE_GB = 4.0
TRANSLITS = S97.TRANSLITS
SEGS = S97.SEGS
# G2a
LULL9 = "bcdefghik"
CELL_PAT = ["xyzt", "xytx", "xyty", "xytz", "xztx", "xzty", "xztz", "xtxy", "xtxz", "xtyz",
            "yztx", "yzty", "yztz", "ytxy", "ytxz", "ytyz", "ztxy", "ztxz", "ztyz", "txyz"]
# G2b
A_MAX = 24
HEAD = 50
PHI_GRID = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6]
M_GRID = [25, 50, 100, 200, 400]
KAPPA_GRID = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4]
TAU_GRID = [0.5, 1.0, 2.0, 4.0]
D_COPY = 6
N_PERM_FIT = 20
N_SIM_DRIFT = 3
N_SIM_LOC = 2
CONSTR = ["G2a", "G2b"]
INPUTS = ["content", "content_shuf", "random"]
# fixture plant
FX_PHI, FX_M, FX_LAM, FX_BETA, FX_KAPPA, FX_TAU = 0.3, 100, 0.2, 10.0, 0.2, 2.0
FX_PHI_BAND = (0.2, 0.4)
FX_SCALE_BAND = (2.5, 10.0)
FX_TV_MAX = 0.15
FX_LAYOUT = (15, 10, 18)
FX_GROUPS = ["a", "e", "o", "y", "ch", "sh", "d", "k", "t", "l"]
log: list[str] = []
T0 = time.time()
OUT = None
FINAL = None   # results_s110.txt: created (exclusive) only when the run completes; progress goes to OUT (runs/s110)


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    if OUT is None:
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def write_final():
    with open(FINAL, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(log) + "\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def local_modules():
    out = []
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix == ".py" and p.exists():
            out.append(rel.as_posix())
    return sorted(set(out) | {SELF.name})


def data_files():
    out = list(S104.data_files()) + list(S107.DATA_FILES)
    return sorted(set(out), key=out.index)


def stub_files():
    return local_modules() + data_files()


def stub_match():
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
    missing = [m for m in stub_files() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"


def wait_ram(tag):
    for _ in range(20):
        fg = S91.free_gb()
        if fg >= MIN_FREE_GB:
            return fg
        print(f"  [{tag}] free RAM {fg:.1f} GB < {MIN_FREE_GB}; waiting 30 s", flush=True)
        time.sleep(30)
    emit(f"STOP: free RAM {S91.free_gb():.1f} GB < {MIN_FREE_GB} GB after 10 min")
    flush()
    raise SystemExit(2)


def pool_map(fn, jobs, tag):
    import multiprocessing as mp
    fg = wait_ram(tag)
    emit(f"  [{tag}] free RAM {fg:.1f} GB (need >= {MIN_FREE_GB}); {len(jobs)} jobs on {N_WORKERS} workers")
    out = {}
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(N_WORKERS, initializer=S97.worker_init) as pool:
        for i, res in enumerate(pool.imap_unordered(fn, jobs)):
            out[res[0]] = res[1]
            if (i + 1) % 20 == 0 or i + 1 == len(jobs):
                print(f"  [{tag} {time.time() - t0:.0f}s] {i + 1}/{len(jobs)} done", flush=True)
    return out


# ======================================================================= battery with the NOT ASSESSABLE fix
def measure_safe(job):
    try:
        k, m, dr, _ = _S97_MEASURE(job)
        return k, (m, dr)
    except Exception as e:  # noqa: BLE001
        return job["key"], (None, repr(e)[:160])


def battery_pool(jobs, tag):
    return pool_map(measure_safe, jobs, tag)


def battery_score_na(name, Ts, M, ref, folds, ctl_pages):
    """S97.battery_score with the pre-registered fix: a block whose Measured job (control or reference) raised, or whose
    scoring raises, is NOT ASSESSABLE (n = None) instead of failing the whole battery."""
    splits = S97.block_split(ctl_pages)
    res = OrderedDict()
    for T in Ts:
        rows = []
        pages = ref[T]
        for b, Q in enumerate(folds):
            rm, rdr = M[("REF", T, b)]
            cm, cdr = M[("CTL", name, b)]
            n, err = None, None
            if rm is None or cm is None:
                err = (rdr if rm is None else cdr)
            else:
                try:
                    real_te = [ls for p, q, ls in pages if q == Q]
                    cells, _, _, _ = S67.score_model(rm, rm.point(), rdr, [cm], cdr, rm.n_test,
                                                     [[ls for _, ls in splits[b][1]]], real_te)
                    n = sum(bool(cells[k][0]) for k in S67.PREDS)
                except Exception as e:  # noqa: BLE001
                    err = repr(e)[:160]
            rows.append(dict(Q=Q, n=n, err=err))
        nf = sum(1 for r in rows if r["n"] is not None and r["n"] >= BAT_FOLD_MIN)
        na = sum(1 for r in rows if r["n"] is None)
        res[T] = dict(rows=rows, folds_ok=nf, n_na=na, holds=nf >= BAT_MIN_FOLDS)
    return res


def bat_txt(T, r):
    return (f"{T}: folds >=4/6 {r['folds_ok']:2d}/15 (NOT ASSESSABLE {r['n_na']}) {'HOLDS' if r['holds'] else 'fails'} | per fold "
            + " ".join("NA" if x["n"] is None else str(x["n"]) for x in r["rows"]))


# ======================================================================= codebook and inputs
class Codebook:
    def __init__(self, words):
        cnt = Counter(words)
        self.types = [w for w, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
        self.k = {w: i for i, w in enumerate(self.types)}
        self.V = len(self.types)
        perm = np.random.default_rng([SEED, 11]).permutation(self.V)
        self.u = (perm + 0.5) / self.V

    def u_of_words(self, words):
        return self.u[np.array([self.k[w] for w in words], dtype=np.int64)]

    def u_random(self, n, rng):
        return self.u[rng.integers(self.V, size=n)]


def input_streams(lines):
    """-> dict input -> (kind, data): content / content_shuf = word lists (text order), random = None (drawn per use)."""
    content = [w for ln in lines for w in ln]
    rng = np.random.default_rng([SEED, 77])
    sh = []
    for ln in lines:
        x = list(ln)
        rng.shuffle(x)
        sh.extend(x)
    return OrderedDict([("content", content), ("content_shuf", sh), ("random", None)])


def unit_stream(cb, inp_words, n, off, rng):
    """n codebook positions u: cyclic word stream from offset off (content inputs) or i.i.d. uniform (random)."""
    if inp_words is None:
        return cb.u_random(n, rng), off
    L = len(inp_words)
    idx = (off + np.arange(n)) % L
    return cb.u_of_words([inp_words[i] for i in idx]), off + n


# ======================================================================= G2a figure
def build_figure():
    cols = list(combinations(LULL9, 3))
    fig = []
    for x, y, z in cols:
        mp_ = {"x": x, "y": y, "z": z, "t": "t"}
        fig.append(["".join(mp_[ch] for ch in pat) for pat in CELL_PAT])
    return fig


FIG = build_figure()
N_COL, N_POS = len(FIG), len(CELL_PAT)
N_ROWS = N_COL * N_POS
SYM_RANK = [s for s, _ in sorted(Counter(ch for col in FIG for cell in col for ch in cell).items(), key=lambda kv: (-kv[1], kv[0]))]
CELL_POS = {}
for _c, _col in enumerate(FIG):
    for _j, _cell in enumerate(_col):
        CELL_POS.setdefault(_cell, []).append((_c, _j))


def g2a_fit(train_words):
    sg = SlotSegmenter(train_words)
    C = Counter()
    for w in train_words:
        c = sg.segment(w)[1]
        if c:
            C[c] += 1
    cores = [x for x, _ in sorted(C.items(), key=lambda kv: (-kv[1], kv[0]))][:len(SYM_RANK)]
    cores = [cores[i % len(cores)] for i in range(len(SYM_RANK))]
    return {s: g for s, g in zip(SYM_RANK, cores)}


def g2a_line(gmap, row, n):
    j, c0 = row % N_POS, row // N_POS
    return ["".join(gmap[ch] for ch in FIG[(c0 + i) % N_COL][j]) for i in range(n)]


def g2a_gen(gmap, layout, u):
    """layout: list of (pid, qkey, [line lengths]); u: one position per line.  -> pages, rows."""
    pages, rows, li = [], [], 0
    for pid, _, lens in layout:
        ls = []
        for n in lens:
            r = min(N_ROWS - 1, int(u[li] * N_ROWS)); li += 1
            rows.append(r)
            ls.append(g2a_line(gmap, r, n))
        pages.append((pid, ls))
    return pages, rows


def g2a_decode_line(gmap, toks):
    """first row (smallest index) consistent with every token under the known map; None if none."""
    groups = list(gmap.items())

    def parses(w, k):
        if k == 0:
            return [""] if w == "" else []
        out = []
        for s, g in groups:
            if w.startswith(g):
                out += [s + rest for rest in parses(w[len(g):], k - 1)]
        return out
    cand = None
    for i, w in enumerate(toks):
        ps = set(parses(w, 4))
        here = set()
        for cell in ps:
            for c, j in CELL_POS.get(cell, []):
                here.add(((c - i) % N_COL, j))
        cand = here if cand is None else cand & here
        if not cand:
            return None
    if not cand:
        return None
    return min(j + N_POS * c0 for c0, j in cand)


def g2a_recovery(gmap, pages, rows):
    ok = n = 0
    li = 0
    for _, ls in pages:
        for ln in ls:
            d = g2a_decode_line(gmap, ln)
            ok += int(d == rows[li]); n += 1; li += 1
    return ok / max(1, n)


# ======================================================================= G2b model
def _affix_alpha(cnt):
    rk = [x for x, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
    top = rk[:A_MAX - 1] if len(rk) > A_MAX else rk
    rest = rk[len(top):]
    vals = [[(v, 1.0)] for v in top]
    if rest:
        tot = sum(cnt[v] for v in rest)
        vals.append([(v, cnt[v] / tot) for v in rest])
    ix = {v: i for i, v in enumerate(top)}
    for v in rest:
        ix[v] = len(top)
    return vals, ix


def suffix_R(lines, A):
    """R(d), d = 1..6: within-line same-value pairs at distance d / within-line shuffle expectation (all positions)."""
    num = np.zeros(D_COPY + 1); den = np.zeros(D_COPY + 1)
    for ids in lines:
        m = len(ids)
        if m < 2:
            continue
        a = np.asarray(ids)
        c = np.bincount(a, minlength=A)
        e = (c * (c - 1)).sum() / (m * (m - 1))
        for d in range(1, min(D_COPY, m - 1) + 1):
            num[d] += (a[:-d] == a[d:]).sum(); den[d] += (m - d) * e
    return np.array([num[d] / den[d] if den[d] > 0 else np.nan for d in range(1, D_COPY + 1)])


def share_decay(lines, A):
    """S(D), D = 1..4: between-line affix share for same-page lines D apart / quire level (r9 R9a; R9.profile per
    quire on positions >= 2), mean over quires.  lines: (quire, page, ids) in reading order."""
    byq = OrderedDict()
    for q, pg, ids in lines:
        byq.setdefault(q, []).append((pg, list(ids)))
    S = []
    for q, ls in byq.items():
        if len(ls) < 5:
            continue
        S.append(R9.profile(ls, A)["S"][1:5])
    S = np.array(S, dtype=float)
    return np.nanmean(S, axis=0) if len(S) else np.full(4, np.nan)


def decay_err(a, b):
    ok = np.isfinite(a) & np.isfinite(b) & (b != 0)
    return float(np.sum(((a[ok] - b[ok]) / b[ok]) ** 2)) if ok.any() else float("inf")


def cov_stats(cores, blocks, n_perm, rng):
    """S87 coverage statistic (share of a block's types present in another block) and types per block, each as
    observed / token-permutation mean.  cores, blocks: int arrays."""
    c = np.asarray(cores); b = np.asarray(blocks)
    _, c = np.unique(c, return_inverse=True)
    _, b = np.unique(b, return_inverse=True)
    V, B = int(c.max()) + 1, int(b.max()) + 1

    def stats(cc):
        pres = np.bincount(b * V + cc, minlength=B * V).reshape(B, V) > 0
        cnt = pres.sum(0)
        typ = pres.sum(1)
        cov = (pres & ((cnt[None, :] - pres) > 0)).sum(1) / np.maximum(typ, 1)
        return cov.mean(), typ.mean()
    co, to = stats(c)
    nc, nt = [], []
    for _ in range(n_perm):
        x, y = stats(c[rng.permutation(c.size)])
        nc.append(x); nt.append(y)
    return co / np.mean(nc), to / np.mean(nt)


class G2BModel:
    """G2b generator (fitted or planted).  Fields: cores (list), g (np probs), tail (indices), pre/suf (vals, init, T or
    None, p, lam, beta), kappa, tau, phi, m."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def new_quire(self, rng):
        tail = self.tail
        m = min(self.m, len(tail))
        w = self.g[tail]
        pool = rng.choice(tail, size=m, replace=False, p=w / w.sum()) if m > 0 else np.array([], dtype=int)
        mix = (1 - self.phi) * self.g.copy()
        if m > 0:
            lw = self.g[pool] / self.g[pool].sum()
            mix[pool] += self.phi * lw
        else:
            mix = self.g.copy()
        cdf = np.cumsum(mix)
        cdf /= cdf[-1]
        return cdf

    @staticmethod
    def _draw(p, rng):
        x = int(np.searchsorted(np.cumsum(p), rng.random() * p.sum(), side="right"))
        return min(x, len(p) - 1)

    def _affix_str(self, vals, i, rng):
        v = vals[i]
        if len(v) == 1:
            return v[0][0]
        pr = np.array([x[1] for x in v])
        return v[self._draw(pr, rng)][0]

    def gen_ids(self, layout, u, rng, want_strings=True):
        """layout: list of (pid, qkey, [lens]); u: one position per token in reading order.
        -> pages (pid, lines of tokens) and per-line id streams (core idx, prefix id, suffix id)."""
        pages, streams = [], []
        ti, curq = 0, None
        P, S = self.pre, self.suf
        for pid, qk, lens in layout:
            ls = []
            for n in lens:
                if qk != curq:
                    cdf = self.new_quire(rng)
                    thp = rng.dirichlet(P["beta"] * P["p"] + 1e-9)
                    ths = rng.dirichlet(S["beta"] * S["p"] + 1e-9)
                    curq = qk
                else:
                    thp = (1 - P["lam"]) * thp + P["lam"] * rng.dirichlet(P["beta"] * P["p"] + 1e-9)
                    ths = (1 - S["lam"]) * ths + S["lam"] * rng.dirichlet(S["beta"] * S["p"] + 1e-9)
                cs = np.minimum(np.searchsorted(cdf, u[ti:ti + n], side="right"), len(cdf) - 1); ti += n
                pr = [self._draw(P["init"], rng)]
                wq = thp / np.maximum(P["p"], 1e-12)
                for t in range(1, n):
                    pr.append(self._draw(P["T"][pr[-1]] * wq, rng))
                sf = [self._draw(S["init"], rng)]
                for t in range(1, n):
                    if self.kappa > 0 and rng.random() < self.kappa:
                        dm = min(D_COPY, t)
                        kw = np.exp(-(np.arange(1, dm + 1) - 1) / self.tau)
                        d = 1 + self._draw(kw, rng)
                        sf.append(sf[t - d])
                    else:
                        sf.append(self._draw(ths, rng))
                streams.append((qk, pid, cs, pr, sf))
                if want_strings:
                    ls.append([self._affix_str(P["vals"], a, rng) + self.cores[c] + self._affix_str(S["vals"], s, rng)
                               for a, c, s in zip(pr, cs, sf)])
            pages.append((pid, ls))
        return pages, streams


def _stream_lines(seg_lines, ix, slot):
    return [(q, pg, [ix[t[slot]] for t in l]) for q, pg, l in seg_lines]


def g2b_fit(train_pages, seed):
    """train_pages: list of (pid, quire, lines).  Each component fitted directly on the training quires."""
    words = [w for _, _, ls in train_pages for l in ls for w in l]
    sg = SlotSegmenter(words)
    seg_lines = [(q, pid, [sg.segment(w) for w in l]) for pid, q, ls in train_pages for l in ls if l]
    Cc, Pc, Sc = Counter(), Counter(), Counter()
    for _, _, l in seg_lines:
        for p, c, s in l:
            Pc[p] += 1; Cc[c] += 1; Sc[s] += 1
    cores = [x for x, _ in sorted(Cc.items(), key=lambda kv: (-kv[1], kv[0]))]
    cix = {c: i for i, c in enumerate(cores)}
    g = np.array([Cc[c] for c in cores], dtype=float); g /= g.sum()
    tail = np.arange(HEAD, len(cores))
    pvals, pix = _affix_alpha(Pc)
    svals, six = _affix_alpha(Sc)
    pre_lines = _stream_lines(seg_lines, pix, 0)
    suf_lines = _stream_lines(seg_lines, six, 2)
    lay = [(q, pg, len(ids)) for q, pg, ids in pre_lines]
    pm = R9.fit_basic(pre_lines, len(pvals))
    sm = R9.fit_basic(suf_lines, len(svals))
    pre = dict(vals=pvals, init=pm["init"], T=pm["T"], p=pm["p"], lam=1.0, beta=1.0)
    suf = dict(vals=svals, init=sm["init"], T=None, p=sm["p"], lam=1.0, beta=1.0)
    lay_pages = []
    for q, pg, n in lay:
        if lay_pages and lay_pages[-1][0] == pg and lay_pages[-1][1] == q:
            lay_pages[-1][2].append(n)
        else:
            lay_pages.append([pg, q, [n]])
    layout = [(pg, q, lens) for pg, q, lens in lay_pages]
    ntok = sum(n for _, _, n in lay)
    base = G2BModel(cores=cores, g=g, tail=tail, pre=pre, suf=suf, kappa=0.0, tau=1.0, phi=0.0, m=0)
    # drift (lam, beta) per affix stream, directly from the between-line share decay S(D), D = 1..4 (r9 R9a statistic,
    # R9.profile per quire, mean over quires), simulating the full affix process (prefix chain included) on r9's grid
    Sp_r = share_decay(pre_lines, len(pvals))
    Ss_r = share_decay(suf_lines, len(svals))
    bp = bs_ = None
    for lam in R9.LAMS:
        for beta in R9.BETAS:
            base.pre.update(lam=lam, beta=beta); base.suf.update(lam=lam, beta=beta)
            sp_, ss_ = [], []
            for rep in range(N_SIM_DRIFT):
                rng = np.random.default_rng([seed, 5, rep])
                _, st = base.gen_ids(layout, np.zeros(ntok), rng, want_strings=False)
                sp_.append(share_decay([(x[0], x[1], x[3]) for x in st], len(pvals)))
                ss_.append(share_decay([(x[0], x[1], x[4]) for x in st], len(svals)))
            ep = decay_err(np.nanmean(sp_, axis=0), Sp_r)
            es = decay_err(np.nanmean(ss_, axis=0), Ss_r)
            if bp is None or ep < bp[0]:
                bp = (ep, lam, beta)
            if bs_ is None or es < bs_[0]:
                bs_ = (es, lam, beta)
    plam, pbeta, slam, sbeta = bp[1], bp[2], bs_[1], bs_[2]
    base.pre.update(lam=plam, beta=pbeta); base.suf.update(lam=slam, beta=sbeta)
    # (kappa, tau) on the training suffix recurrence profile
    Rr = suffix_R([ids for _, _, ids in suf_lines], len(svals))
    best = None
    for ka in KAPPA_GRID:
        for ta in (TAU_GRID if ka > 0 else [1.0]):
            base.kappa, base.tau = ka, ta
            rng = np.random.default_rng([seed, 1])
            _, st = base.gen_ids(layout, np.zeros(ntok), rng, want_strings=False)
            Rs = suffix_R([x[4] for x in st], len(svals))
            ok = np.isfinite(Rr) & np.isfinite(Rs)
            err = float(np.sum(((Rs[ok] - Rr[ok]) / Rr[ok]) ** 2))
            if best is None or err < best[0]:
                best = (err, ka, ta)
    base.kappa, base.tau = best[1], best[2]
    # (phi, m) directly from block coverage on the training quires (blocks = quires)
    real_c = np.array([cix[t[1]] for _, _, l in seg_lines for t in l])
    qs = {q: i for i, q in enumerate(dict.fromkeys(q for q, _, _ in seg_lines))}
    real_b = np.array([qs[q] for q, _, l in seg_lines for _ in l])
    rc, rt = cov_stats(real_c, real_b, N_PERM_FIT, np.random.default_rng([seed, 2]))
    best = None
    for phi in PHI_GRID:
        for m in (M_GRID if phi > 0 else [0]):
            base.phi, base.m = phi, m
            scs, sts = [], []
            for rep in range(N_SIM_LOC):
                rng = np.random.default_rng([seed, 3, rep])
                cs, bs = [], []
                curq, cdf = None, None
                for pg, q, lens in layout:
                    if q != curq:
                        cdf = base.new_quire(rng); curq = q
                    n = sum(lens)
                    cs.append(np.minimum(np.searchsorted(cdf, rng.random(n), side="right"), len(cdf) - 1)); bs.append(np.full(n, qs[q]))
                a_, b_ = cov_stats(np.concatenate(cs), np.concatenate(bs), N_PERM_FIT, np.random.default_rng([seed, 4, rep]))
                scs.append(a_); sts.append(b_)
            sc, st_ = float(np.mean(scs)), float(np.mean(sts))
            err = ((sc - rc) / rc) ** 2 + ((st_ - rt) / rt) ** 2
            if best is None or err < best[0]:
                best = (err, phi, m, sc, st_)
    base.phi, base.m = best[1], best[2]
    base.fit_info = dict(phi=best[1], m=best[2], cov_real=rc, typ_real=rt, cov_fit=best[3], typ_fit=best[4],
                         pre_lam=plam, pre_beta=pbeta, suf_lam=slam, suf_beta=sbeta, kappa=base.kappa, tau=base.tau,
                         R_real=[float(x) for x in Rr], n_cores=len(cores), n_pre=len(pvals), n_suf=len(svals))
    base.pre_strings = [v[0][0] if len(v) == 1 else None for v in pvals]
    return base


def fits_pool(jobs, tag):
    F = pool_map(fit_job, jobs, tag)
    for v in F.values():
        if "g2b" in v:
            v["g2b"] = G2BModel(**v["g2b"])
    return F


def fit_job(job):
    S87.below_normal()
    t = time.time()
    try:
        m = g2b_fit(job["train"], job["seed"])
        gm = g2a_fit([w for _, _, ls in job["train"] for l in ls for w in l])
        return job["key"], dict(g2b=dict(m.__dict__), g2a=gm, secs=time.time() - t)
    except Exception:  # noqa: BLE001
        return job["key"], dict(error=traceback.format_exc(), secs=time.time() - t)


# ======================================================================= text builders
def layout_of(pages_q):
    """pages_q: list of (pid, quire, lines) -> layout (pid, qkey, lens)."""
    return [(pid, q, [len(l) for l in ls if l]) for pid, q, ls in pages_q]


def gen_text(constr, fit, layout, inp_words, cb, off, rng):
    """-> pages, new offset, rows (G2a) or None."""
    if constr == "G2a":
        n = sum(len(lens) for _, _, lens in layout)
        u, off = unit_stream(cb, inp_words, n, off, rng)
        pages, rows = g2a_gen(fit["g2a"], layout, u)
        return pages, off, rows
    n = sum(sum(lens) for _, _, lens in layout)
    u, off = unit_stream(cb, inp_words, n, off, rng)
    pages, _ = fit["g2b"].gen_ids(layout, u, rng)
    return pages, off, None


def loqo_texts(constr, fit, pages_T, Q, inp_words, cb, rng):
    """-> (train generated pages, first held-out replicate, H = replicates cut to N_TOT)."""
    tr_lay = layout_of([x for x in pages_T if x[1] != Q])
    te_lay = layout_of([x for x in pages_T if x[1] == Q])
    tr, off, _ = gen_text(constr, fit, tr_lay, inp_words, cb, 0, rng)
    H, j, first, tot = [], 0, None, 0
    while tot < N_TOT and j <= 400:
        lay = [(f"r{j}:{pid}", (Q, j), lens) for pid, _, lens in te_lay]
        he, off, _ = gen_text(constr, fit, lay, inp_words, cb, off, rng)
        if first is None:
            first = he
        H.extend(he)
        tot += sum(len(ln) for _, ls in he for ln in ls)
        j += 1
    return tr, first, S91.cut(H)


def fold_holds(p, lb, rel_sig, vprofs, nb):
    """s104 survivor fold rule (slot SIG absolute, or target-relative under A1) and battery row >= 4/6."""
    if rel_sig:
        sig, fl = S104.sig_rel(p, vprofs)
    else:
        sig, _, fl = S97.flags(p, lb)
    return bool(sig and nb is not None and nb >= BAT_FOLD_MIN), fl


# ======================================================================= fixture
def fx_layout(seed):
    nq, npg, nl = FX_LAYOUT
    rng = np.random.default_rng([seed, 5])
    qs = [chr(ord("A") + i) for i in range(nq)]
    return [(f"{q}{p:02d}", q, [1 + int(rng.poisson(7)) for _ in range(nl)]) for q in qs for p in range(npg)], qs


def fx_world_model(seed):
    rng = np.random.default_rng([seed, 6])
    alph = "abcdefghiklmnoprst"
    cores, seen = [], set()
    while len(cores) < 400:
        w = "".join(rng.choice(list(alph), size=int(rng.integers(2, 5))))
        if w not in seen:
            seen.add(w); cores.append(w)
    g = 1.0 / np.arange(1, 401) ** 1.0; g /= g.sum()
    pre_s = ["", "q", "qv", "x", "xz", "z", "qz", "zv", "xv", "qx"]   # [REVISION 1] glyphs disjoint from the cores
    suf_s = ["", "y", "uy", "w", "jy", "j", "wy", "yj", "jw", "ww", "yy", "uj"]
    Tm = rng.dirichlet(np.full(len(pre_s), 0.5), size=len(pre_s))
    pp = np.full(len(pre_s), 1.0 / len(pre_s)); sp = np.full(len(suf_s), 1.0 / len(suf_s))
    pre = dict(vals=[[(s, 1.0)] for s in pre_s], init=pp.copy(), T=Tm, p=pp, lam=FX_LAM, beta=FX_BETA)
    suf = dict(vals=[[(s, 1.0)] for s in suf_s], init=sp.copy(), T=None, p=sp, lam=FX_LAM, beta=FX_BETA)
    return G2BModel(cores=cores, g=g, tail=np.arange(HEAD, 400), pre=pre, suf=suf, kappa=FX_KAPPA, tau=FX_TAU,
                    phi=FX_PHI, m=FX_M), pre_s, Tm


def prefix_tv(fit, pre_s, Tm):
    """mean total variation between the fitted and planted prefix transition rows, over planted prefixes that the
    fitted segmenter recovered as their own value."""
    fs = fit.pre_strings
    idx = {s: i for i, s in enumerate(fs) if s is not None}
    common = [s for s in pre_s if s in idx]
    if len(common) < 2:
        return float("nan"), len(common)
    tvs = []
    for a in common:
        row_f = np.array([fit.pre["T"][idx[a]][idx[b]] for b in common]); row_f /= row_f.sum()
        row_p = np.array([Tm[pre_s.index(a)][pre_s.index(b)] for b in common]); row_p /= row_p.sum()
        tvs.append(0.5 * np.abs(row_f - row_p).sum())
    return float(np.mean(tvs)), len(common)


def run_fixture():
    emit("S110 FIXTURE (synthetic only; reads no Voynich data)")
    emit(f"date: {S87.clock()}")
    emit(f"s110_g2_combinatory_grid.py sha256={sha256(SELF)}; s104 sha256={sha256(ROOT / 's104_g1_encoding_grid.py')} "
         f"(stub {S104_HASH}) -> {sha256(ROOT / 's104_g1_encoding_grid.py') == S104_HASH}")
    emit(f"figure: {N_COL} columns x {N_POS} cells = {N_ROWS} rows; symbol ranks {''.join(SYM_RANK)}; first column {' '.join(FIG[0])}")
    layout, qs = fx_layout(SEED)
    ntok = sum(sum(l) for _, _, l in layout)
    emit(f"layout: {len(qs)} quires, {len(layout)} pages, {sum(len(l) for _, _, l in layout)} lines, {ntok} tokens")
    rng = np.random.default_rng([SEED, 7])
    # FX1 planted G2b
    pm, pre_s, Tm = fx_world_model(SEED)
    pg1, _ = pm.gen_ids(layout, rng.random(ntok), rng)
    planted = [(pid, q, ls) for (pid, q, _), (_, ls) in zip(layout, pg1)]
    # FX2 planted G2a
    gmap = {s: g for s, g in zip(SYM_RANK, FX_GROUPS)}
    nlines = sum(len(l) for _, _, l in layout)
    u2 = rng.random(nlines)
    pg2, rows2 = g2a_gen(gmap, layout, u2)
    planted_a = [(pid, q, ls) for (pid, q, _), (_, ls) in zip(layout, pg2)]
    rec_all = g2a_recovery(gmap, pg2, rows2)
    emit(f"FX2 known-map decoding on the whole planted G2a text: {rec_all:.4f}")
    # FX3 prose on the same layout
    aug = S87.load_control("latin_augustine.txt")
    prose, i = [], 0
    for pid, q, lens in layout:
        ls = []
        for n in lens:
            ls.append(aug[i:i + n]); i += n
        prose.append((pid, q, ls))
    targets = OrderedDict([("FX1_planted_G2b", (planted, "G2b")), ("FX2_planted_G2a", (planted_a, "G2a")),
                           ("FX3_prose_G2b", (prose, "G2b"))])
    # fits (pool)
    jobs = []
    for ti, (tn, (tp, _)) in enumerate(targets.items()):
        if tn == "FX2_planted_G2a":
            continue   # [REVISION 1] FX2 uses the known map (a G2a glyph map is a fixed assignment, not recoverable from G2a output)
        for fi, Q in enumerate(qs):
            jobs.append(dict(key=(tn, fi), train=[x for x in tp if x[1] != Q], seed=SEED + 100 * ti + fi))
    FITS = fits_pool(jobs, "fixture fits")
    for fi in range(len(qs)):
        FITS[("FX2_planted_G2a", fi)] = dict(g2b=pm, g2a=gmap, secs=0.0)
    ORACLE = dict(g2b=pm, g2a=gmap)
    errs = [k for k, v in FITS.items() if "error" in v]
    if errs:
        emit(f"  FIT ERRORS {errs}: {FITS[errs[0]]['error'][-800:]}")
    emit(f"  fit seconds: median {np.median([v['secs'] for v in FITS.values()]):.1f}, max {max(v['secs'] for v in FITS.values()):.1f}")
    flush()
    PROF, LB, MJ, TX = {}, {}, [], {}
    for ti, (tn, (tp, constr)) in enumerate(targets.items()):
        tpages = S91.cut([(pid, ls) for pid, _, ls in tp])
        PROF[tn] = S97.profile_g(f"FX110/{tn}/target", tpages, SlotSegmenter, N_MATCH, SEED + 500 + ti)
        LB[tn] = S87.loc_band_from([PROF[tn]])
        emit("  target " + S97.fmt(PROF[tn], LB[tn]))
        for fi, Q in enumerate(qs):
            MJ.append(dict(key=("REF", tn, fi), name=f"{tn} {Q} target", train=[(p, ls) for p, q, ls in tp if q != Q],
                           test=[(p, ls) for p, q, ls in tp if q == Q], seed=SEED + 30000 + 1000 * ti + fi))
            fit = FITS[(tn, fi)]
            if "error" in fit:
                continue
            frng = np.random.default_rng([SEED, 8, ti, fi])
            cbx = FxCodebook()
            tr, te, H = loqo_texts(constr, fit, tp, Q, None, cbx, frng)
            TX[(tn, fi)] = (tr, te)
            p = S97.profile_g(f"FX110/{tn}/{Q}", H, SlotSegmenter, N_MATCH, SEED + 600 + 100 * ti + fi)
            PROF[(tn, fi)] = p
            MJ.append(dict(key=("SV", tn, fi), name=f"{tn} {Q} gen", train=tr, test=te, seed=SEED + 40000 + 1000 * ti + fi))
            if tn == "FX1_planted_G2b":   # [REVISION 1] oracle replicate from the true planted generator
                orng = np.random.default_rng([SEED, 9, ti, fi])
                otr, ote, OH = loqo_texts(constr, ORACLE, tp, Q, None, cbx, orng)
                TX[("OR", fi)] = (otr, ote)
                PROF[("OR", fi)] = S97.profile_g(f"FX110/oracle/{Q}", OH, SlotSegmenter, N_MATCH, SEED + 800 + fi)
                MJ.append(dict(key=("SV", "OR", fi), name=f"oracle {Q}", train=otr, test=ote, seed=SEED + 45000 + fi))
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        flush()
    # FX4 battery fix: a control with an empty block
    na_pages = [(f"na{i:02d}", [aug[200 * i + 10 * k:200 * i + 10 * k + 10] for k in range(20)]) for i in range(14)]  # block 14 empty
    M = battery_pool(MJ + [dict(key=("CTL", "FX4_na", b), name=f"fx4 b{b}", train=tr_, test=te_, seed=SEED + 50000 + b)
                           for b, (tr_, te_) in enumerate(S97.block_split(na_pages))]
                     + [dict(key=("REF", "FXT", b), name=f"fx4 ref b{b}", train=[(p, ls) for p, q, ls in planted if q != Q],
                             test=[(p, ls) for p, q, ls in planted if q == Q], seed=SEED + 60000 + b) for b, Q in enumerate(qs)],
                     "fixture battery")
    def comps(p):
        return [p["order"][100]["mm"], p["order"][200]["mm"], p["rep"][1]["Rw"], p["rep"][1]["Rc"], p["loc"]["ratio"]]
    OV = np.array([comps(PROF[("OR", fi)]) for fi in range(len(qs))])
    ENV = (OV.mean(0) - 3 * OV.std(0, ddof=1), OV.mean(0) + 3 * OV.std(0, ddof=1))
    emit("  [REVISION 1] oracle envelope (mean +- 3 SD over the 15 oracle replicates) for o100, o200, Rw1, Rc1, loc: "
         + ", ".join(f"[{a:.4f}, {b:.4f}]" for a, b in zip(*ENV)))

    def env_in(p):
        v = comps(p)
        return all(ENV[0][i] <= v[i] <= ENV[1][i] for i in range(len(v))), "".join(
            "Y" if ENV[0][i] <= v[i] <= ENV[1][i] else "n" for i in range(len(v)))
    tp1 = targets["FX1_planted_G2b"][0]
    or_rows = []
    for fi, Q in enumerate(qs):
        rm, rdr = M[("REF", "FX1_planted_G2b", fi)]
        gm, gdr = M[("SV", "OR", fi)]
        nb = None
        if rm is not None and gm is not None:
            try:
                cells, _, _, _ = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test, [[ls for _, ls in TX[("OR", fi)][1]]],
                                                 [ls for p, q, ls in tp1 if q == Q])
                nb = sum(bool(cells[k][0]) for k in S67.PREDS)
            except Exception:  # noqa: BLE001
                nb = None
        ein, efl = env_in(PROF[("OR", fi)])
        lin = LB["FX1_planted_G2b"][0] <= PROF[("OR", fi)]["loc"]["ratio"] <= LB["FX1_planted_G2b"][1]
        or_rows.append(dict(Q=Q, env=efl, bat=nb, ok=bool(ein and lin and nb is not None and nb >= BAT_FOLD_MIN)))
    n_or_bat = sum(1 for r in or_rows if r["bat"] is not None and r["bat"] >= BAT_FOLD_MIN)
    emit("  oracle folds (envelope flags | battery | holds): " + " ".join(f"{r['Q']}:{r['env']}/{r['bat']}{'*' if r['ok'] else ''}" for r in or_rows)
         + f" -> oracle holds {sum(r['ok'] for r in or_rows)}/15, battery >= 4/6 on {n_or_bat}/15")
    RES = OrderedDict()
    for ti, (tn, (tp, constr)) in enumerate(targets.items()):
        rows = []
        for fi, Q in enumerate(qs):
            fit = FITS[(tn, fi)]
            if "error" in fit:
                rows.append(dict(Q=Q, ok=False, note="fit error")); continue
            rm, rdr = M[("REF", tn, fi)]
            gm, gdr = M[("SV", tn, fi)]
            nb = None
            if rm is not None and gm is not None:
                try:
                    real_te = [ls for p, q, ls in tp if q == Q]
                    cells, _, _, _ = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test, [[ls for _, ls in TX[(tn, fi)][1]]], real_te)
                    nb = sum(bool(cells[k][0]) for k in S67.PREDS)
                except Exception as e:  # noqa: BLE001
                    nb = None
            p = PROF[(tn, fi)]
            sig, fl = S104.sig_rel(p, [PROF[tn]])
            loc_in = LB[tn][0] <= p["loc"]["ratio"] <= LB[tn][1]
            f2 = getattr(fit["g2b"], "fit_info", None) or dict(phi=float("nan"), m=0, pre_lam=float("nan"), suf_lam=float("nan"),
                                                                 kappa=float("nan"), tau=float("nan"))
            phi_in = FX_PHI_BAND[0] <= f2["phi"] <= FX_PHI_BAND[1]
            r = dict(Q=Q, sig=sig, flags=fl, bat=nb, loc_in=loc_in, phi=f2["phi"], m=f2["m"], phi_in=phi_in,
                     ps=1 / f2["pre_lam"], ss=1 / f2["suf_lam"], kappa=f2["kappa"], tau=f2["tau"])
            if tn == "FX1_planted_G2b":
                r["tv"], r["n_common"] = prefix_tv(fit["g2b"], pre_s, Tm)
                ein, r["flags"] = env_in(p)
                r["ok"] = bool(loc_in and ein and nb is not None and nb >= BAT_FOLD_MIN)   # [REVISION 1] oracle envelope
            elif tn == "FX2_planted_G2a":
                te_pages = [(pid, ls) for pid, q, ls in tp if q == Q]
                li, te_rows = 0, []
                for pid, q, lens in layout:
                    for _ in lens:
                        if q == Q:
                            te_rows.append(rows2[li])
                        li += 1
                r["dec"] = g2a_recovery(gmap, te_pages, te_rows)
                r["ok_dec"] = r["dec"] >= 0.80
                r["ok_prof"] = bool(sig)   # [REVISION 1] sig_rel of the known-map replicate; battery printed only
                r["ok"] = r["ok_dec"] and r["ok_prof"]
            else:
                r["ok"] = bool(loc_in and sig and nb is not None and nb >= BAT_FOLD_MIN)
                r["ok_prof"] = bool(sig and nb is not None and nb >= BAT_FOLD_MIN)
            rows.append(r)
        RES[tn] = rows
        emit(f"\n  {tn}: per fold Q | sig flags | battery | replicate loc in band | fitted phi, m | drift scale pre/suf | kappa, tau | extra | RECOVERED")
        for r in rows:
            if "flags" not in r:
                emit(f"   {r['Q']} {r.get('note')}"); continue
            extra = ""
            if "tv" in r:
                extra = f"prefix TV {r['tv']:.3f} (n {r['n_common']})"
            if "dec" in r:
                extra = f"decode {r['dec']:.3f} prof {r['ok_prof']}"
            emit(f"   {r['Q']} | {r['flags']} | {r['bat']} | {r['loc_in']} | {r['phi']:.2f}, {r['m']} | {r['ps']:.1f}/{r['ss']:.1f} | "
                 f"{r['kappa']:.2f}, {r['tau']:.1f} | {extra} | {r['ok']}")
        flush()
    n1 = sum(r["ok"] for r in RES["FX1_planted_G2b"])
    med_ps = float(np.median([r["ps"] for r in RES["FX1_planted_G2b"] if "ps" in r]))
    med_ss = float(np.median([r["ss"] for r in RES["FX1_planted_G2b"] if "ss" in r]))
    med_tv = float(np.nanmedian([r["tv"] for r in RES["FX1_planted_G2b"] if "tv" in r]))
    FX1 = n1 >= FX_MIN and FX_SCALE_BAND[0] <= med_ps <= FX_SCALE_BAND[1] and FX_SCALE_BAND[0] <= med_ss <= FX_SCALE_BAND[1] \
        and med_tv <= FX_TV_MAX and n_or_bat >= FX_MIN
    emit(f"\nFX1 planted G2b recovered on {n1}/15 folds (need >= {FX_MIN}); median drift scale prefix {med_ps:.2f} suffix {med_ss:.2f} "
         f"(planted {1 / FX_LAM:.1f}; band {FX_SCALE_BAND}); median prefix TV {med_tv:.3f} (<= {FX_TV_MAX}); oracle battery power {n_or_bat}/15 "
         f"(need >= {FX_MIN}) -> FX1 = {FX1}")
    nd = sum(r.get("ok_dec", False) for r in RES["FX2_planted_G2a"])
    npf = sum(r.get("ok_prof", False) for r in RES["FX2_planted_G2a"])
    FX2 = nd >= FX_MIN and npf >= FX_MIN
    emit(f"FX2 planted G2a: decoding >= 0.80 on {nd}/15 folds; fold rule on {npf}/15 (need >= {FX_MIN} each) -> FX2 = {FX2}")
    n3 = sum(r["ok"] for r in RES["FX3_prose_G2b"])
    n3p = sum(r.get("ok_prof", False) for r in RES["FX3_prose_G2b"])
    dec_prose = g2a_recovery(gmap, [(pid, ls) for pid, _, ls in prose], rows2)
    FX3 = n3 < FX_MIN and dec_prose < 0.80
    emit(f"FX3 prose: G2b fold rule (recovered) on {n3}/15 (profile-only {n3p}/15; need < {FX_MIN}); G2a known-map decoding "
         f"{dec_prose:.3f} (< 0.80) -> FX3 = {FX3}")
    fx4_ref = OrderedDict([("FXREF", [(p, q, ls) for p, q, ls in planted])])
    MM = {("REF", "FXREF", b): M[("REF", "FXT", b)] for b in range(NB)}
    MM.update({k: v for k, v in M.items() if k[0] == "CTL"})
    try:
        b4 = battery_score_na("FX4_na", ["FXREF"], MM, fx4_ref, qs, na_pages)["FXREF"]
        FX4 = b4["n_na"] >= 1 and b4["n_na"] < 15
        emit(f"FX4 battery fix on a control with an empty block: {bat_txt('FXREF', b4)} -> FX4 = {FX4}")
    except Exception:  # noqa: BLE001
        FX4 = False
        emit(f"FX4 raised: {traceback.format_exc()[-600:]}")
    PASS = FX1 and FX2 and FX3 and FX4
    emit(f"\nFIXTURE_PASS = {PASS}")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


class FxCodebook:
    """fixture input: random uniform positions (no codebook needed)."""

    def u_random(self, n, rng):
        return rng.random(n)


# ======================================================================= real run
def latest_fixture():
    fs = sorted(RUN_DIR.glob("fixture_*.txt"))
    if not fs:
        return None, False
    txt = fs[-1].read_text(encoding="utf-8")
    return fs[-1], "FIXTURE_PASS = True" in txt


def main():
    global OUT, FINAL
    if LIST_FILES:
        for m in stub_files():
            print(m)
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if FIXTURE:
        OUT = RUN_DIR / f"fixture_{stamp}.txt"
        run_fixture()
        return
    if WELLFORMED:
        OUT = RUN_DIR / f"wellformed_{stamp}.txt"
        run_wellformed()
        return
    FINAL = ROOT / "results_s110.txt"
    if FINAL.exists():
        print("STOP: results_s110.txt exists; results are never overwritten")
        raise SystemExit(3)
    OUT = RUN_DIR / f"progress_{stamp}.txt"
    emit("S110: Phase 7 grid G2 (G2a Lullian figure, G2b prefix x core x suffix table) x inputs (content, content-shuffled, "
         "random) vs the D-066 (o) joint profile (pre-registered in the docstring)")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; BelowNormal set={S87.below_normal()}; workers {N_WORKERS}")
    emit(f"s110_g2_combinatory_grid.py sha256={sha256(SELF)}")
    sm = stub_match()
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={sm}")
    h104 = sha256(ROOT / "s104_g1_encoding_grid.py")
    emit(f"s104 import check: sha256 {h104} == s104 stub {S104_HASH} -> {h104 == S104_HASH}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    fx, fx_ok = latest_fixture()
    emit(f"fixture gate: latest {fx.name if fx else '-'} FIXTURE_PASS = {fx_ok}")
    if sm != "True" or h104 != S104_HASH or not fx_ok:
        emit("STOP: stub mismatch, s104 hash mismatch or fixture gate not passed; no real statistic computed")
        flush()
        raise SystemExit(4)
    REF81 = S104.s81_reference()
    THR = S104.LAG2_FACTOR * float(np.mean(list(REF81.values())))
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH}; figure {N_COL} x {N_POS}; H2 band {S104.H2_BAND}; LAG2 bar {THR * 1000:.3f} e-3 bits; seed {SEED}")
    flush()

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    # ---- Voynich target
    emit("\n=== Voynich target (SlotSegmenter cores, s87 seeds; rhythm; h2) ===")
    VOY = OrderedDict()
    for i, T in enumerate(TRANSLITS):
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        pages = S87.layout(None, True, P, line_lens, page_nl)
        VOY[T] = (pages, S97.profile_g(f"S110_VOY_{T}", pages, SlotSegmenter, N_MATCH, S87.SEED + 100 * i))
    lb = S87.loc_band_from([v[1] for v in VOY.values()])
    emit(f"LOCALITY band: [{lb[0]:.4f}, {lb[1]:.4f}]")
    for T, (pages, p) in VOY.items():
        emit("  " + S97.fmt(p, lb))
    flush()

    # ---- references, folds, fits
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    assert len(folds) == NB
    emit(f"  folds ({len(folds)}): {' '.join(folds)}")
    zq = {pid: q for pid, q, _ in ref["ZL3b"]}
    cut_pages = VOY["ZL3b"][0]
    cut_quires = list(dict.fromkeys(zq[pid] for pid, _ in cut_pages))
    emit(f"  ZL3b 22,500 cut: {len(cut_pages)} pages in quires {' '.join(cut_quires)}")
    jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            jobs.append(dict(key=(T, Q), train=[x for x in ref[T] if x[1] != Q], seed=SEED + 1000 * ti + fi))
    for Q in cut_quires:
        if Q not in folds:
            jobs.append(dict(key=("ZL3b", Q), train=[x for x in ref["ZL3b"] if x[1] != Q], seed=SEED + 900 + ord(Q)))
    emit("\n=== fits (G2b components and G2a glyph map, each fold fitted on its training quires only) ===")
    FITS = fits_pool(jobs, "fits")
    bad = [k for k, v in FITS.items() if "error" in v]
    if bad:
        emit(f"STOP: fit errors {bad}: {FITS[bad[0]]['error'][-800:]}")
        flush()
        raise SystemExit(5)
    for (T, Q), v in FITS.items():
        f = v["g2b"].fit_info
        emit(f"  {T} -Q{Q}: phi {f['phi']:.2f} m {f['m']} (coverage real {f['cov_real']:.4f}/{f['typ_real']:.4f}, fit {f['cov_fit']:.4f}/"
             f"{f['typ_fit']:.4f}) | drift scale pre {1 / f['pre_lam']:.1f} (beta {f['pre_beta']}) suf {1 / f['suf_lam']:.1f} (beta "
             f"{f['suf_beta']}) | kappa {f['kappa']:.2f} tau {f['tau']:.1f} | cores {f['n_cores']} | G2a map "
             + " ".join(f"{s}={g}" for s, g in v["g2a"].items()) + f" | {v['secs']:.0f}s")
    flush()

    # ---- cells (in-sample text, cross-fitted per quire)
    p1_lines, _ = S102.load_p1()
    cb = Codebook([w for ln in p1_lines for w in ln])
    INP = input_streams(p1_lines)
    emit(f"\n=== cells: content = s102 P1 Latin ({sum(map(len, p1_lines))} words, {len(p1_lines)} lines, codebook V {cb.V}) ===")
    CELLS = OrderedDict()
    for xi, constr in enumerate(CONSTR):
        for ii, inp in enumerate(INP):
            name = f"{constr}_{inp}"
            rng = np.random.default_rng([SEED, 21, xi, ii])
            off, out_pages, rows = 0, [], []
            groups = []
            for pid, ls in cut_pages:
                q = zq[pid]
                if groups and groups[-1][0] == q:
                    groups[-1][1].append((pid, q, [len(l) for l in ls]))
                else:
                    groups.append((q, [(pid, q, [len(l) for l in ls])]))
            for q, lay in groups:
                pg, off, rw = gen_text(constr, FITS[("ZL3b", q)], lay, INP[inp], cb, off, rng)
                out_pages += pg
                if rw is not None:
                    rows += rw
            rec = g2a_recovery(FITS[("ZL3b", cut_quires[0])]["g2a"], out_pages[:20], rows[:sum(len(ls) for _, ls in out_pages[:20])]) \
                if constr == "G2a" else None
            CELLS[name] = dict(constr=constr, inp=inp, pages=out_pages)
            t = sum(len(ln) for _, ls in out_pages for ln in ls)
            emit(f"  {name:18s} tokens {t} lines {sum(len(ls) for _, ls in out_pages)} pages {len(out_pages)} | alphabet "
                 f"{len(S104.alphabet(out_pages))} | first line: {' '.join(out_pages[0][1][0])}"
                 + (f" | G2a known-map decoding (first 20 pages, quire-{cut_quires[0]} map; descriptive) {rec:.3f}" if rec is not None else ""))
    flush()

    TEXTS = OrderedDict((n, ("cell", c["pages"], list(TRANSLITS))) for n, c in CELLS.items())
    aug = S87.load_control("latin_augustine.txt")
    for T in TRANSLITS:
        TEXTS[f"VOY_{T}"] = ("target", VOY[T][0], list(TRANSLITS))
    TEXTS["PC2_VOY_IT2a_as_control"] = ("gate", VOY["IT2a"][0], ["IT2a"])
    TEXTS["NC_augustine_la"] = ("gate", S87.layout(aug, False, None, line_lens, page_nl), list(TRANSLITS))

    # ---- S gate PC1
    emit("\n=== S: s97 gate (PC1 planted LP91, PC2 IT2a as control, NC plain Latin) ===")
    zp = ref["ZL3b"]
    segz = SlotSegmenter([w for _, _, ls in zp for l in ls for w in l])
    zcp = [(p, q, [[segz.segment(w)[1] for w in l] for l in ls]) for p, q, ls in zp]
    glob = Counter(c for _, _, ls in zcp for l in ls for c in l if c != "")
    prod = S91.LP91(glob, S91.bigram_of([(p, [[c for c in l if c != ""] for l in ls]) for p, q, ls in zcp]))
    prod.set_params(S91.PLANTED)
    spec = [(p, q, [len(l) for l in ls]) for p, q, ls in zp]
    pc1 = []
    for s in (1, 2, 3):
        pages = S91.cut(prod.text(spec, S97.SEED + s))
        p = S97.profile_g(f"S110_PC1_LP91_planted_s{s}", pages, S80.identity_seg_factory, N_MATCH, S97.SEED + 10 + s)
        pc1.append(S97.flags(p, lb)[0])
        emit("  " + S97.fmt(p, lb))
    PC1 = sum(pc1) >= S97.PC1_MIN
    emit(f"  PC1 Voynich-like on {sum(pc1)}/3 seeds -> {PC1}")
    flush()

    # ---- SIG
    emit("\n=== SIG profiles (flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PR = OrderedDict()
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        PR[n] = OrderedDict()
        segs = ["slot"] if n.startswith("PC2") else list(SEGS)
        for si, sn in enumerate(segs):
            p = S97.profile_g(f"S110/{n}/{sn}", pages, SEGS[sn], N_MATCH, SEED + 1000 * xi + 100 * si)
            PR[n][sn] = p
            app = p["core_share"] >= MIN_CORE_SHARE
            emit("  " + S97.fmt(p, lb, "" if app else " [NOT APPLICABLE: core share < 0.5]"))
        flush()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---- RHY, H2
    emit("\n=== RHY and H2 ===")
    RH, H2 = OrderedDict(), OrderedDict()
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        try:
            RH[n] = S102.rhythm(pages, SEED + 5000 + xi)
        except Exception as e:  # noqa: BLE001
            RH[n] = dict(I=float("nan"), median=float("nan"), excess=float("nan"), p=1.0, holds=False, err=repr(e)[:100])
        H2[n] = S102.h2_of(pages)
        emit(f"  {n:26s} rhythm excess {RH[n]['excess']:+.4f} p {RH[n]['p']:.3f} -> {RH[n]['holds']}{' ' + RH[n].get('err', '') if RH[n].get('err') else ''}"
             f" | h2 {H2[n]:.4f}")
    flush()

    # ---- LAG2
    emit(f"\n=== LAG2 (s98 prefix XCMI per block, residue = median over 15 blocks; bar {THR * 1000:.3f}) ===")
    skel_pages = VOY["ZL3b"][0]
    skel = [[len(l) for l in ls] for _, ls in skel_pages]
    s81 = S81.encipher(S81.plain_letters("latin_cremma"), S81.key_tables(), skel, "line", S91.STICKY_P,
                       seed=S81.gen_seed("line_sticky75", "latin_cremma", 1))
    L_TEXTS = OrderedDict((n, c["pages"]) for n, c in CELLS.items())
    for T, (pages, _) in VOY.items():
        L_TEXTS[f"VOY_{T}"] = pages
    L_TEXTS["S81_line_sticky75"] = [(pid, s81[i]) for i, (pid, _) in enumerate(skel_pages)]
    jobs = []
    for xi, (n, pages) in enumerate(L_TEXTS.items()):
        jobs += S104.lag2_jobs(n, xi, pages)
    LR = pool_map(lag2_job_kv, jobs, "lag-2")
    LAG = OrderedDict()
    for n in L_TEXTS:
        LAG[n] = S104.lag2_summary(n, LR)
        emit(f"  {n:26s} residue {LAG[n]['residue'] * 1000:+.3f} e-3 bits (blocks {LAG[n]['n']}, positive {LAG[n]['pos']}/15"
             f"{', ERRORS ' + str(LAG[n]['errors']) if LAG[n]['errors'] else ''})")
    flush()

    # ---- BAT (in-sample) + LOQO texts, one battery pool
    emit("\n=== BAT (s67 battery, text block b vs real fold b; NOT ASSESSABLE fix) and LOQO texts ===")
    bjobs = S97.ref_jobs(ref, folds)
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        bjobs += S97.ctl_jobs(n, xi + 1, pages)
    # s107 texts (descriptive, battery fix shown; s107 not refiled)
    t1 = S107.t1_lines(S107.SRC_T1.read_text(encoding="utf-8", errors="replace"))
    t2, _ = S107.t2_load()
    t3 = S107.t3_load()
    S107T = OrderedDict([("T1_tacuinum_bnf9333", (t1, 11)), ("T2_degradibus_const", (t2, 12)), ("T3_lull_tabula_1515", (t3, 13))])
    S107P = OrderedDict()
    for n, (lines, xi) in S107T.items():
        S107P[n] = S87.layout(lines, True, None, line_lens, page_nl, N_TOT)
        bjobs += S97.ctl_jobs(n, xi + 1, S107P[n])
    # LOQO
    LQ_TX, LQ_PR = {}, {}
    for ci, (n, c) in enumerate(CELLS.items()):
        for ti, T in enumerate(TRANSLITS):
            for fi, Q in enumerate(folds):
                rng = np.random.default_rng([SEED, 31, ci, ti, fi])
                tr, te, H = loqo_texts(c["constr"], FITS[(T, Q)], ref[T], Q, INP[c["inp"]], cb, rng)
                LQ_TX[(n, T, fi)] = te
                LQ_PR[(n, T, fi)] = S97.profile_g(f"S110_SV/{n}/{T}/{Q}", H, SlotSegmenter, N_MATCH, SEED + 9000 + 100 * ci + 10 * ti + fi)
                bjobs.append(dict(key=("SV", n, T, fi), name=f"SV {n} {T} {Q}", train=tr, test=te,
                                  seed=SEED + 20000 + 1000 * ci + 100 * ti + fi))
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        emit(f"  LOQO texts and profiles done for {n} ({time.time() - T0:.0f} s)")
        flush()
    M = battery_pool(bjobs, "battery")
    nbad = [k for k, v in M.items() if v[0] is None]
    emit(f"  Measured jobs that raised (block NOT ASSESSABLE): {len(nbad)}" + (": " + "; ".join(f"{k}: {M[k][1]}" for k in nbad[:8]) if nbad else ""))
    BAT = OrderedDict()
    for n, (role, pages, Ts) in TEXTS.items():
        BAT[n] = battery_score_na(n, Ts, M, ref, folds, pages)
        for T, r in BAT[n].items():
            emit(f"  {n:26s} " + bat_txt(T, r))
    flush()

    # ---- A1 calibration (s104 rules)
    emit("\n=== A1 target calibration: the manuscript through the same criteria (absolute rules) ===")
    VOYN = [f"VOY_{T}" for T in TRANSLITS]
    H2B = S104.H2_BAND
    for n in LAG:
        LAG[n]["holds"] = bool(np.isfinite(LAG[n]["residue"]) and LAG[n]["residue"] <= THR and not LAG[n]["errors"])
    REL_SIG = {sn: any(not S97.flags(PR[v][sn], lb)[0] for v in VOYN) for sn in SEGS}
    REL_BAT = {T: any(not BAT[v][T]["holds"] for v in VOYN) for T in TRANSLITS}
    REL_RHY = any(not RH[v]["holds"] for v in VOYN)
    REL_H2 = any(not (H2B[0] <= H2[v] <= H2B[1]) for v in VOYN)
    REL_LAG = any(not LAG[v]["holds"] for v in VOYN)
    h2b = (min([H2B[0]] + [H2[v] for v in VOYN]), max([H2B[1]] + [H2[v] for v in VOYN])) if REL_H2 else H2B
    bat_min = {T: min(BAT[v][T]["folds_ok"] for v in VOYN) for T in TRANSLITS}
    rhy_min = min(RH[v]["excess"] for v in VOYN)
    pooled = [x["excess"] for (nm, q), x in LR.items() if nm in VOYN and "excess" in x]
    THR_USED = float(np.percentile(pooled, S104.LAG2_REL_Q)) if REL_LAG else THR
    for v in VOYN:
        emit(f"  {v}: SIG " + " ".join(f"{sn}:{S97.flags(PR[v][sn], lb)[2]}" for sn in SEGS) + " | BAT "
             + " ".join(f"{T} {BAT[v][T]['folds_ok']}/15" for T in TRANSLITS) + f" | RHY {RH[v]['excess']:+.4f} p {RH[v]['p']:.3f} | h2 {H2[v]:.4f}"
             f" | LAG2 {LAG[v]['residue'] * 1000:+.3f}")
    emit(f"  TARGET-RELATIVE criteria: SIG {[sn for sn, v in REL_SIG.items() if v] or 'none'}; BAT {[T for T, v in REL_BAT.items() if v] or 'none'} "
         f"(min VOY folds {bat_min}); RHY {REL_RHY} (min excess {rhy_min:+.4f}); H2 {REL_H2} (band {h2b[0]:.4f}, {h2b[1]:.4f}); LAG2 {REL_LAG} "
         f"(bar used {THR_USED * 1000:.3f} e-3 bits)")
    vfold = {}
    for v in VOYN:
        sigv = S97.flags(PR[v]["slot"], lb)[0]
        for T in TRANSLITS:
            vfold[(v, T)] = sum(1 for r in BAT[v][T]["rows"] if sigv and r["n"] is not None and r["n"] >= BAT_FOLD_MIN)
    LOQO_BAR = {T: (min(vfold[(v, T)] for v in VOYN) if any(vfold[(v, T)] < LOQO_MIN for v in VOYN) else LOQO_MIN) for T in TRANSLITS}
    emit("  manuscript fold rule (slot SIG and battery row >= 4/6): " + "; ".join(f"{v} vs {T} {vfold[(v, T)]}/15" for v in VOYN for T in TRANSLITS))
    emit(f"  LOQO bar per T: {LOQO_BAR}")
    for n in list(LAG):
        LAG[n]["holds"] = bool(np.isfinite(LAG[n]["residue"]) and LAG[n]["residue"] <= THR_USED and not LAG[n]["errors"])
    G_L = (all(LAG[v]["holds"] for v in VOYN) or REL_LAG) and LAG["S81_line_sticky75"]["residue"] > THR_USED \
        and not LAG["S81_line_sticky75"]["errors"]
    emit(f"  L lag-2 validity (bar {THR_USED * 1000:.3f}): VOY <= bar {[LAG[v]['holds'] for v in VOYN]}; s81 table "
         f"{LAG['S81_line_sticky75']['residue'] * 1000:+.3f} > bar -> {G_L}")
    VPR = [PR[v] for v in VOYN]
    flush()

    # ---- LOQO folds
    emit("\n=== LOQO (fold holds iff slot SIG [A1-relative if the manuscript fails it] and battery row >= 4/6 vs the real held-out quire) ===")
    LQ = OrderedDict()
    for n in CELLS:
        LQ[n] = OrderedDict()
        for T in TRANSLITS:
            rows = []
            for fi, Q in enumerate(folds):
                rm, rdr = M[("REF", T, fi)]
                gm, gdr = M[("SV", n, T, fi)]
                nb = None
                if rm is not None and gm is not None:
                    try:
                        real_te = [ls for p, q, ls in ref[T] if q == Q]
                        cells, _, _, _ = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test, [[ls for _, ls in LQ_TX[(n, T, fi)]]], real_te)
                        nb = sum(bool(cells[k][0]) for k in S67.PREDS)
                    except Exception:  # noqa: BLE001
                        nb = None
                h, fl = fold_holds(LQ_PR[(n, T, fi)], lb, REL_SIG["slot"], [q["slot"] for q in VPR], nb)
                rows.append(dict(Q=Q, flags=fl, bat=nb, holds=h))
            LQ[n][T] = dict(rows=rows, held=sum(r["holds"] for r in rows))
            emit(f"  {n:18s} {T}: held {LQ[n][T]['held']:2d}/15 | " + " ".join(
                f"{r['Q']}:{r['flags']}/{'NA' if r['bat'] is None else r['bat']}{'*' if r['holds'] else ''}" for r in rows))
    flush()

    # ---- calls
    emit("\n=== calls ===")
    PC2 = None
    DESC, PASS, KILL = OrderedDict(), OrderedDict(), OrderedDict()
    for n, (role, pages, Ts) in TEXTS.items():
        segs = list(PR[n])
        app = [sn for sn in segs if PR[n][sn]["core_share"] >= MIN_CORE_SHARE]
        sig = {}
        for sn in segs:
            if REL_SIG.get(sn) and role == "cell":
                ok, fl = S104.sig_rel(PR[n][sn], [q[sn] for q in VPR])
                sig[sn] = (ok, None, fl + "*")
            else:
                sig[sn] = S97.flags(PR[n][sn], lb)
        sig_ok = bool(app) and all(sig[sn][0] for sn in app)
        bat_ok = all((BAT[n][T]["folds_ok"] >= bat_min[T]) if (REL_BAT[T] and role == "cell") else BAT[n][T]["holds"] for T in Ts)
        rhy_ok = (RH[n]["excess"] >= rhy_min) if (REL_RHY and role == "cell") else RH[n]["holds"]
        h2_ok = h2b[0] <= H2[n] <= h2b[1]
        lag_ok = LAG[n]["holds"] if n in LAG else None
        lq_ok = all(LQ[n][T]["held"] >= LOQO_BAR[T] for T in TRANSLITS) if n in LQ else None
        if role == "cell":
            PASS[n] = bool(sig_ok and bat_ok and rhy_ok and h2_ok and lag_ok and lq_ok)
            KILL[n] = [k for k, v in (("SIG", sig_ok), ("BAT", bat_ok), ("RHY", rhy_ok), ("H2", h2_ok), ("LAG2", lag_ok), ("LOQO", lq_ok)) if not v]
        DESC[n] = dict(role=role, applicable=app, sig={sn: sig[sn][2] for sn in segs}, sig_ok=sig_ok,
                       battery={T: BAT[n][T]["folds_ok"] for T in Ts}, battery_na={T: BAT[n][T]["n_na"] for T in Ts}, battery_ok=bat_ok,
                       rhythm=dict(excess=RH[n]["excess"], p=RH[n]["p"], holds=rhy_ok), h2=H2[n], h2_ok=h2_ok,
                       lag2=(LAG[n]["residue"] if n in LAG else None), lag2_ok=lag_ok,
                       loqo=({T: LQ[n][T]["held"] for T in TRANSLITS} if n in LQ else None), loqo_ok=lq_ok,
                       s97_full=sig_ok and bat_ok, PASS=PASS.get(n), kill=KILL.get(n))
    PC2 = DESC["PC2_VOY_IT2a_as_control"]["s97_full"]
    NC_ok = not DESC["NC_augustine_la"]["s97_full"]
    G_S = PC1 and PC2 and NC_ok
    GATE = G_S and G_L and fx_ok
    emit(f"  fixture gate {fx_ok}; S s97 gate (PC1 {PC1}, PC2 {PC2}, NC {NC_ok}) {G_S}; L lag-2 validity {G_L}")
    emit(f"  CALL_S110_GATE = {GATE}")
    emit("\n  CELL TABLE (construction x input): SIG flags id/slot/affix2 | BAT folds ZL3b/RF1b/IT2a | RHY excess,p | h2 | LAG2 e-3 | "
         "LOQO held ZL3b/RF1b/IT2a | PASS | KILLING PROPERTY")
    for n in CELLS:
        d = DESC[n]
        emit(f"   {n:18s} SIG {'/'.join(d['sig'].values())} {'Y' if d['sig_ok'] else 'n'} | BAT {'/'.join(str(v) for v in d['battery'].values())} "
             f"{'Y' if d['battery_ok'] else 'n'} | RHY {d['rhythm']['excess']:+.4f},{d['rhythm']['p']:.3f} {'Y' if d['rhythm']['holds'] else 'n'} | "
             f"h2 {d['h2']:.3f} {'Y' if d['h2_ok'] else 'n'} | LAG2 {d['lag2'] * 1000:+.2f} {'Y' if d['lag2_ok'] else 'n'} | "
             f"LOQO {'/'.join(str(v) for v in d['loqo'].values())} {'Y' if d['loqo_ok'] else 'n'} | {'PASS' if d['PASS'] else '-'} | "
             f"{', '.join(d['kill']) or 'none'}")
    hits = [n for n in CELLS if PASS[n]]
    ANY = GATE and bool(hits)
    CA = OrderedDict()
    for constr in CONSTR:
        c, s, r = f"{constr}_content", f"{constr}_content_shuf", f"{constr}_random"
        tot = {x: sum(LQ[x][T]["held"] for T in TRANSLITS) for x in (c, s, r)}
        CA[constr] = bool(GATE and PASS[c] and tot[c] > tot[s] and tot[c] > tot[r])
        emit(f"  CONTENT_ADDS({constr}) = {CA[constr]} (content PASS {PASS[c]}; LOQO held sums content {tot[c]}, shuffled {tot[s]}, random {tot[r]})")
    CONTENT_ADDS = any(CA.values())
    emit(f"  G2_ANY_PASS = {ANY}")
    emit(f"  CONTENT_ADDS = {CONTENT_ADDS}")
    flush()

    # ---- s107 descriptive battery fix
    emit("\n=== battery fix on the s107 texts (DESCRIPTIVE; s107 is not refiled; s107 battery seeds xi + 1) ===")
    S107B = OrderedDict()
    for n, pages in S107P.items():
        S107B[n] = battery_score_na(n, list(TRANSLITS), M, ref, folds, pages)
        for T, r in S107B[n].items():
            emit(f"  {n:22s} " + bat_txt(T, r))
        full = all(r["holds"] for r in S107B[n].values())
        emit(f"  {n:22s} battery with the fix holds on all three: {full} (descriptive)")
    flush()

    if not GATE:
        why = [k for k, v in (("fixture", fx_ok), ("S PC1", PC1), ("S PC2", PC2), ("S NC", NC_ok), ("L lag-2 validity", G_L)) if not v]
        reading = f"uninformative: gate failed ({', '.join(why)})"
    elif not hits:
        reading = ("no cell passes: combinatory-table procedures are closed within G2 (D-066 (o) stopping rule); killing property per cell: "
                   + "; ".join(f"{n} [{', '.join(KILL[n])}]" for n in CELLS))
    elif CONTENT_ADDS:
        reading = (f"CONTENT_ADDS ({', '.join(k for k, v in CA.items() if v)}): candidate encoding; predict held-out quires and the Phase 7.2 "
                   "cribs before anything is read (D-066 (o) stopping rule)")
    else:
        reading = (f"cells pass ({', '.join(hits)}) but content adds nothing over its twins: procedure without content (H-05/H-19 "
                   "procedure); no decipherment attempted (D-066 (o) stopping rule)")
    emit(f"\nVERDICT: CALL_S110_GATE = {GATE}; G2_ANY_PASS = {ANY}; CONTENT_ADDS = {CONTENT_ADDS}: {reading}")
    flush()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(
        loc_band=lb, lag2_bar=THR, lag2_bar_used=THR_USED, PC1=PC1, PC1_seeds=pc1, PC2=PC2, NC=NC_ok, G_S=G_S, G_L=G_L, fixture=str(fx),
        GATE=GATE, G2_ANY_PASS=ANY, CONTENT_ADDS=CONTENT_ADDS, content_adds=CA, desc=DESC, loqo_bar=LOQO_BAR,
        loqo={n: {T: v["rows"] for T, v in per.items()} for n, per in LQ.items()},
        fits={f"{T}-{Q}": v["g2b"].fit_info | dict(g2a_map=v["g2a"]) for (T, Q), v in FITS.items()},
        s107_battery_fix={n: {T: dict(folds_ok=r["folds_ok"], n_na=r["n_na"], holds=r["holds"]) for T, r in b.items()} for n, b in S107B.items()},
        verdict=reading), indent=1, default=str), encoding="utf-8", newline="\n")
    with (RUN_DIR / "cell_texts_first_pages.txt").open("w", encoding="utf-8", newline="\n") as fh:
        for n, c in CELLS.items():
            fh.write(f"## {n}\n")
            for pid, ls in c["pages"][:3]:
                for ln in ls:
                    fh.write(f"{pid}\t{' '.join(ln)}\n")
    emit("\nsidecars: runs/s110/calls.json, runs/s110/cell_texts_first_pages.txt")
    emit(f"progress log: {OUT.relative_to(ROOT).as_posix()}; results file written at the end (exclusive create)")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()
    write_final()


def run_wellformed():
    """pre-freeze code-path check on the real layouts and plaintext: builds the inputs, a G2a text with a PLACEHOLDER
    map (no fit) and a G2b text from the fixture's planted model (no fit), one LOQO text set per transliteration, the
    s107 layouts, the s81 skeleton and the job lists.  Prints ONLY counts and alphabets: no fit, no statistic."""
    emit("S110 WELL-FORMEDNESS CHECK (pre-freeze; only counts and alphabets; no fit, no statistic)")
    emit(f"date: {S87.clock()}")
    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]
    P = [(p["id"], p["lines"]) for p in zl]
    cut_pages = S87.layout(None, True, P, line_lens, page_nl)
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    zq = {pid: q for pid, q, _ in ref["ZL3b"]}
    cut_quires = list(dict.fromkeys(zq[pid] for pid, _ in cut_pages))
    emit(f"ZL3b cut: {len(cut_pages)} pages, {sum(len(l) for _, ls in cut_pages for l in ls)} tokens, quires {' '.join(cut_quires)}; folds {' '.join(folds)}")
    p1_lines, _ = S102.load_p1()
    cb = Codebook([w for ln in p1_lines for w in ln])
    INP = input_streams(p1_lines)
    emit(f"P1 Latin: {sum(map(len, p1_lines))} words, {len(p1_lines)} lines, V {cb.V}; inputs {[ (k, None if v is None else len(v)) for k, v in INP.items()]}")
    pm, _, _ = fx_world_model(SEED)
    fake = dict(g2b=pm, g2a={s: g for s, g in zip(SYM_RANK, FX_GROUPS)})
    for constr in CONSTR:
        for inp in INP:
            rng = np.random.default_rng([SEED, 99])
            groups = []
            for pid, ls in cut_pages:
                q = zq[pid]
                if groups and groups[-1][0] == q:
                    groups[-1][1].append((pid, q, [len(l) for l in ls]))
                else:
                    groups.append((q, [(pid, q, [len(l) for l in ls])]))
            off, out = 0, []
            for q, lay in groups:
                pg, off, _ = gen_text(constr, fake, lay, INP[inp], cb, off, rng)
                out += pg
            emit(f"  {constr}_{inp}: tokens {sum(len(l) for _, ls in out for l in ls)} lines {sum(len(ls) for _, ls in out)} pages {len(out)} "
                 f"alphabet {len(S104.alphabet(out))} ctl jobs {len(S97.ctl_jobs('x', 1, out))} lag2 jobs {len(S104.lag2_jobs('x', 1, out))}")
            for T in TRANSLITS:
                tr, te, H = loqo_texts(constr, fake, ref[T], folds[0], INP[inp], cb, rng)
                emit(f"     LOQO {T} fold {folds[0]}: train tokens {sum(len(l) for _, ls in tr for l in ls)}, first replicate pages {len(te)}, "
                     f"H tokens {sum(len(l) for _, ls in H for l in ls)} pages {len(H)}")
    t1 = S107.t1_lines(S107.SRC_T1.read_text(encoding="utf-8", errors="replace"))
    t2, _ = S107.t2_load()
    t3 = S107.t3_load()
    for n, lines in (("T1", t1), ("T2", t2), ("T3", t3)):
        pg = S87.layout(lines, True, None, line_lens, page_nl, N_TOT)
        emit(f"  s107 {n}: lines {len(lines)} -> pages {len(pg)} tokens {sum(len(l) for _, ls in pg for l in ls)}; ctl jobs {len(S97.ctl_jobs(n, 2, pg))}")
    skel = [[len(l) for l in ls] for _, ls in cut_pages]
    s81 = S81.encipher(S81.plain_letters("latin_cremma"), S81.key_tables(), skel, "line", S91.STICKY_P,
                       seed=S81.gen_seed("line_sticky75", "latin_cremma", 1))
    emit(f"  s81 skeleton text: pages {len(s81)}; REF battery jobs {len(S97.ref_jobs(ref, folds))}; s81 reference {S104.s81_reference()}")
    emit(f"finished {S87.clock()}")
    flush()


def lag2_job_kv(job):
    k, v, _ = S104.lag2_job(job)
    return k, v


if __name__ == "__main__":
    main()
