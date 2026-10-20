"""S113 (G2 redesign; D-066 (r), chosen by Jon 2026-10-18 19:44): are full-size combinatory-table procedures (G2a
Lullian figure, G2b prefix x core x suffix table, both exactly as built in s110) excluded as producers of the Voynich
text when each is judged against its OWN replicate envelope?

WHY (L-323, L-321): s110's battery/LOQO criteria were uninformative for G2a and marginal for G2b even for the true
 planted generator, so an exclusion on them would mean nothing.  Roach r10/r13 judge a producer by whether the real
 text lies inside the [0.5, 99.5] percentile envelope of replicate texts from the fitted producer; this run does
 the same, led by the manuscript's two signature anomalies (in-line core reuse, low h2) plus within-line rhythm.

STATISTICS (book level; the project's implementations in tools/vkb/features.py, imported unchanged, D-071):
 Rw1_line  features.rw1(lines of SlotSegmenter cores)[1] on ALL lines of the book at once (the within-line-shuffle
           expectation is a sum over lines, so pooling is exact).  SlotSegmenter (scoreboard/metrics_new.py) is fitted
           on the words of the book being measured (the manuscript or the replicate), as tools/vkb/manuscript.py fits
           it on the ZL3b P tokens.
 h2        features.h1_h2(words in glyphs)[1] on all words of the book; glyphs = corpora.to_glyphs(w, corpora.GLYPHS).
 rhythm    features.rhythm(lines of glyph lengths, rng) per page (the VKB folio unit; lengths centred on the page),
           combined as the pair-weighted mean of rhythm_excess over pages with an excess (>= 10 pairs); rng seeded by
           features.seed(tag, page id, 'rhythm'), 200 within-line shuffles (features.R_SHUF).

CANDIDATES (constructions and fitting code imported unchanged from s110_g2_combinatory_grid.py):
 G2b = S110.g2b_fit on the WHOLE book (all quires; no fold held out), generated with S110.G2BModel.gen_ids.
 G2a = S110.g2a_fit (figure letters -> SlotSegmenter cores of the book, s110 fill rule), generated with S110.g2a_gen.
 Inputs (real run, as D-066 (o)): content, content_shuf (S102.load_p1 via S110.input_streams, S110.Codebook) and
 random.  Content inputs start at a uniformly drawn offset per replicate (a fixed offset would make every G2a
 replicate identical); random input = i.i.d. uniform codebook positions.  Cells = {G2a, G2b} x 3 inputs.
 Every replicate book reuses the target book's page / quire / line-length layout exactly.

ENVELOPE AND CALLS:
 N_REP = 100 replicate books per cell; envelope per statistic = [P0.5, P99.5] of the replicate values (numpy
 percentile, linear interpolation).  A cell is EXCLUDED iff the target lies outside its envelope on ANY of Rw1_line,
 h2, rhythm (the killing statistics are printed).  A construction is EXCLUDED iff all three of its input cells are
 EXCLUDED; G2_EXCLUDED (full-size combinatory-table procedures excluded) iff G2a and G2b are both EXCLUDED.
 Primary transliteration ZL3b; RF1b and IT2a are replications (same calls printed; the primary call is ZL3b's).
 s67 battery: DIAGNOSTIC ONLY, never a gate: first replicate of each cell vs the target, 15 quire folds (s110 rule:
 S97.measure_job, S67.score_model, fold holds iff >= 4/6), folds holding printed.

FIXTURE (--fx113; synthetic only, reads no Voynich data; writes runs/s113/fixture_<stamp>.txt):
 10 planted G2b books, book b: S110.fx_world_model(SEED + 1000 b) (s110 revision-1 planted world: phi 0.3, m 100,
 prefix chain Dirichlet(0.5), drift lam 0.2 beta 10, suffix kappa 0.2 tau 2) on S110.fx_layout(SEED + 1000 b)
 (15 quires x 10 pages x 18 lines, lengths 1 + Poisson(7), ~21,700 tokens = Voynich size), random input.
 Each planted book plays the manuscript.  Per book, 100 replicates of each of:
  POS     G2b refitted on the planted book (random input)         -> must be NOT EXCLUDED on >= 9/10 books
  ORACLE  the true planted G2BModel                               -> must CONTAIN the planted book on >= 9/10
  NEG     G2a fitted on the planted book (random input)           -> must be EXCLUDED on >= 9/10 books
  UNI     unigram word baseline (tokens of the planted book shuffled over the whole layout): DIAGNOSTIC only
          (power of the three statistics against a structureless producer; not part of FIXTURE_PASS).
 FIXTURE_PASS = POS and ORACLE and NEG.  Battery diagnostic on book 0 only (first replicate of each candidate).
 Criteria fixed before the first fixture run; no revision is allowed after seeing a failure (the run stops).

STOPPING RULE (real run): G2_EXCLUDED -> full-size combinatory-table procedures (G2a, G2b) closed as producers,
 killing statistic recorded per cell; one construction EXCLUDED -> that one closed, the other survives this test
 (not a confirmation: survival under three statistics is not a match); neither -> not excluded by its own
 envelope; record and go to D-066 for the next question.  Not run unless the stub matches and the latest
 runs/s113/fixture_*.txt prints FIXTURE_PASS = True.

COMPUTE: CPU only (GPU not needed: ~2 s per replicate book).  Workers = min(4, floor((free RAM - 4 GB) / 0.7 GB))
 spawn processes at BelowNormal (0 -> run in this process); free RAM >= 4 GB checked before every job batch (wait up
 to 10 min, then stop).  OMP threads 1.
OUTPUT: results_s113.txt (exclusive create, never overwritten); progress and fixture logs in runs/s113/.
Run: python -I tools/s113_g2_envelope.py   Fixture: --fx113   Stub list: --list-files
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from collections import OrderedDict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT, ROOT / "tools" / "vkb"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import s110_g2_combinatory_grid as S110  # noqa: E402  (constructions; imported unchanged)
import features as F  # noqa: E402  (tools/vkb/features.py: rw1, h1_h2, rhythm, seed)
import corpora  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

S87, S97, S67, S102 = S110.S87, S110.S97, S110.S67, S110.S102

SELF = Path(__file__).resolve()
STUB = ROOT / "s113_g2_envelope.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s113"
FIXTURE = "--fx113" in sys.argv
LIST_FILES = "--list-files" in sys.argv

SEED = 20261113
N_REP = 100
Q_LO, Q_HI = 0.5, 99.5
STATS = ["Rw1_line", "h2", "rhythm"]
N_BOOKS = 10
POS_MIN, ORACLE_MIN, NEG_MIN = 9, 9, 9
MAX_WORKERS = 4
WORKER_GB = 0.7          # measured: a process importing s110 holds ~0.65 GB
MIN_FREE_GB = 4.0
TRANSLITS = S97.TRANSLITS          # ZL3b (primary), RF1b, IT2a
PRIMARY = "ZL3b"
INPUTS = ["content", "content_shuf", "random"]
CONSTR = ["G2a", "G2b"]

log: list[str] = []
OUT = None


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    if OUT is not None:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ======================================================================= statistics (tools/vkb/features.py)
def glyphs(w):
    return corpora.to_glyphs(w, corpora.GLYPHS)


def book_stats(pages, tag):
    """pages: list of (pid, quire, lines of word strings) -> dict Rw1_line, h2, rhythm (book level)."""
    words = [w for _, _, ls in pages for l in ls for w in l]
    sg = SlotSegmenter(words)
    seg = {w: sg.segment(w)[1] for w in set(words)}
    core_lines = [[seg[w] for w in l] for _, _, ls in pages for l in ls if l]
    _, r_line, _ = F.rw1(core_lines)
    gl = {w: glyphs(w) for w in set(words)}
    _, h2 = F.h1_h2([gl[w] for w in words])
    num = den = 0.0
    for pid, _, ls in pages:
        L = [[len(gl[w]) for w in l] for l in ls if l]
        _, exc, n = F.rhythm(L, np.random.default_rng(F.seed(tag, pid, "rhythm")))
        if exc is not None:
            num += exc * n
            den += n
    return dict(Rw1_line=r_line, h2=h2, rhythm=(num / den) if den else None)


def envelope(rows):
    out = {}
    for s in STATS:
        v = np.array([r[s] for r in rows if r[s] is not None], dtype=float)
        out[s] = (float(np.percentile(v, Q_LO)), float(np.percentile(v, Q_HI)), len(v)) if len(v) else (np.nan, np.nan, 0)
    return out


def judge(target, env):
    """-> (excluded, flags string 'YYn' per STATS, killing stats list)."""
    kill, fl = [], ""
    for s in STATS:
        lo, hi, _ = env[s]
        v = target[s]
        inside = v is not None and np.isfinite(lo) and lo <= v <= hi
        fl += "Y" if inside else "n"
        if not inside:
            kill.append(s)
    return bool(kill), fl, kill


# ======================================================================= replicate generation
def gen_book(job, rng):
    """one replicate book on the job's layout -> list of (pid, quire, lines)."""
    lay = job["layout"]
    kind = job["kind"]
    if kind == "UNI":
        toks = list(job["tokens"])
        rng.shuffle(toks)
        out, i = [], 0
        for pid, q, lens in lay:
            ls = []
            for n in lens:
                ls.append(toks[i:i + n]); i += n
            out.append((pid, q, ls))
        return out
    inp = job.get("inp_words")
    off = int(rng.integers(len(inp))) if inp is not None else 0
    pages, _, _ = S110.gen_text(kind, job["fit"], lay, inp, job["cb"], off, rng)
    return [(pid, q, ls) for (pid, q, _), (_, ls) in zip(lay, pages)]


def rep_job(job):
    S87.below_normal()
    t = time.time()
    try:
        rows, first = [], None
        for r in range(job["n_rep"]):
            rng = np.random.default_rng([SEED, job["seed"], r])
            bk = gen_book(job, rng)
            if r == 0:
                first = bk
            rows.append(book_stats(bk, f"{job['tag']}/rep{r}"))
        return job["key"], dict(rows=rows, first=first, secs=time.time() - t)
    except Exception:  # noqa: BLE001
        return job["key"], dict(error=traceback.format_exc(), secs=time.time() - t)


def fit_job(job):
    S87.below_normal()
    t = time.time()
    try:
        m = S110.g2b_fit(job["pages"], job["seed"])
        gm = S110.g2a_fit([w for _, _, ls in job["pages"] for l in ls for w in l])
        return job["key"], dict(g2b=m, g2a=gm, secs=time.time() - t)
    except Exception:  # noqa: BLE001
        return job["key"], dict(error=traceback.format_exc(), secs=time.time() - t)


# ======================================================================= compute
def free_gb():
    return S110.S91.free_gb()


def wait_ram(tag):
    for _ in range(20):
        fg = free_gb()
        if fg >= MIN_FREE_GB:
            return fg
        print(f"  [{tag}] free RAM {fg:.1f} GB < {MIN_FREE_GB}; waiting 30 s", flush=True)
        time.sleep(30)
    emit(f"STOP: free RAM {free_gb():.1f} GB < {MIN_FREE_GB} GB after 10 min")
    flush()
    raise SystemExit(2)


def _init():
    S87.below_normal()


def run_jobs(fn, jobs, tag):
    fg = wait_ram(tag)
    nw = max(0, min(MAX_WORKERS, int((fg - MIN_FREE_GB) / WORKER_GB)))
    emit(f"  [{tag}] free RAM {fg:.1f} GB (keep >= {MIN_FREE_GB}); {len(jobs)} jobs on "
         f"{nw if nw else 'no'} workers{'' if nw else ' (in-process, BelowNormal)'}")
    out, t0 = {}, time.time()
    if nw == 0:
        S87.below_normal()
        for i, j in enumerate(jobs):
            wait_ram(tag)
            k, v = fn(j)
            out[k] = v
            print(f"  [{tag} {time.time() - t0:.0f}s] {i + 1}/{len(jobs)} done ({k})", flush=True)
        return out
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(nw, initializer=_init) as pool:
        for i, (k, v) in enumerate(pool.imap_unordered(fn, jobs)):
            out[k] = v
            print(f"  [{tag} {time.time() - t0:.0f}s] {i + 1}/{len(jobs)} done ({k})", flush=True)
    return out


# ======================================================================= s67 battery (diagnostic only)
def battery_diag(target, folds, reps, seed0, tag):
    """target: (pid, q, lines); reps: name -> replicate pages.  -> name -> (folds >= 4/6, per-fold counts)."""
    MJ = []
    for b, Q in enumerate(folds):
        MJ.append(dict(key=("REF", b), name=f"{tag} ref {Q}", train=[(p, ls) for p, q, ls in target if q != Q],
                       test=[(p, ls) for p, q, ls in target if q == Q], seed=seed0 + b))
        for ni, (nm, rp) in enumerate(reps.items()):
            MJ.append(dict(key=("SV", nm, b), name=f"{tag} {nm} {Q}", train=[(p, ls) for p, q, ls in rp if q != Q],
                           test=[(p, ls) for p, q, ls in rp if q == Q], seed=seed0 + 1000 * (ni + 1) + b))
    M = run_jobs(S110.measure_safe, MJ, f"{tag} battery")
    res = OrderedDict()
    for nm, rp in reps.items():
        counts = []
        for b, Q in enumerate(folds):
            rm, rdr = M[("REF", b)]
            gm, gdr = M[("SV", nm, b)]
            nb = None
            if rm is not None and gm is not None:
                try:
                    cells, _, _, _ = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test,
                                                     [[ls for p, q, ls in rp if q == Q]],
                                                     [ls for p, q, ls in target if q == Q])
                    nb = sum(bool(cells[k][0]) for k in S67.PREDS)
                except Exception:  # noqa: BLE001
                    nb = None
            counts.append(nb)
        res[nm] = (sum(1 for c in counts if c is not None and c >= S97.BAT_MIN_HOLD), counts)
    return res


def fmt_stats(d):
    return " ".join(f"{s} {d[s]:.4f}" if d[s] is not None else f"{s} NA" for s in STATS)


def fmt_env(env):
    return " ".join(f"{s} [{env[s][0]:.4f}, {env[s][1]:.4f}]" for s in STATS)


# ======================================================================= fixture
def run_fixture():
    emit("S113 FIXTURE (synthetic only; reads no Voynich data)")
    emit(f"date: {S87.clock()}")
    emit(f"tools/s113_g2_envelope.py sha256={sha256(SELF)}")
    emit(f"s110_g2_combinatory_grid.py sha256={sha256(ROOT / 's110_g2_combinatory_grid.py')}; "
         f"tools/vkb/features.py sha256={sha256(ROOT / 'tools' / 'vkb' / 'features.py')} (R_SHUF {F.R_SHUF})")
    emit(f"N_REP {N_REP}; envelope [P{Q_LO}, P{Q_HI}]; stats {', '.join(STATS)}; books {N_BOOKS}; "
         f"POS >= {POS_MIN}/10 not excluded, ORACLE >= {ORACLE_MIN}/10 contained, NEG (G2a) >= {NEG_MIN}/10 excluded; "
         f"UNI diagnostic; seed {SEED}")
    flush()
    BOOKS, fjobs = [], []
    for b in range(N_BOOKS):
        ws = SEED + 1000 * b
        layout, qs = S110.fx_layout(ws)
        pm, _, _ = S110.fx_world_model(ws)
        rng = np.random.default_rng([SEED, 7, b])
        ntok = sum(sum(l) for _, _, l in layout)
        pg, _ = pm.gen_ids(layout, rng.random(ntok), rng)
        planted = [(pid, q, ls) for (pid, q, _), (_, ls) in zip(layout, pg)]
        BOOKS.append(dict(layout=layout, qs=qs, pm=pm, planted=planted, ntok=ntok))
        fjobs.append(dict(key=b, pages=planted, seed=SEED + 100 + b))
    emit(f"planted books: {N_BOOKS}; tokens per book {min(x['ntok'] for x in BOOKS)}-{max(x['ntok'] for x in BOOKS)}; "
         f"lines {sum(len(l) for _, _, l in BOOKS[0]['layout'])}")
    FITS = run_jobs(fit_job, fjobs, "fits")
    errs = [k for k, v in FITS.items() if "error" in v]
    if errs:
        emit(f"STOP: fit errors {errs}: {FITS[errs[0]]['error'][-800:]}")
        flush()
        raise SystemExit(5)
    for b in range(N_BOOKS):
        fi = FITS[b]["g2b"].fit_info
        emit(f"  book {b} G2b fit ({FITS[b]['secs']:.0f}s): phi {fi['phi']} m {fi['m']} drift pre 1/{fi['pre_lam']} beta "
             f"{fi['pre_beta']} suf 1/{fi['suf_lam']} beta {fi['suf_beta']} kappa {fi['kappa']} tau {fi['tau']} "
             f"(planted phi 0.3 m 100 lam 0.2 beta 10 kappa 0.2 tau 2)")
    flush()
    cb = S110.FxCodebook()
    rjobs = []
    for b, B in enumerate(BOOKS):
        base = dict(layout=[(pid, q, [len(l) for l in ls]) for pid, q, ls in B["planted"]], n_rep=N_REP, cb=cb,
                    inp_words=None)
        rjobs.append(dict(base, key=("POS", b), kind="G2b", fit=dict(g2b=FITS[b]["g2b"]), seed=10 * b + 1, tag=f"fx/POS/{b}"))
        rjobs.append(dict(base, key=("ORACLE", b), kind="G2b", fit=dict(g2b=B["pm"]), seed=10 * b + 2, tag=f"fx/OR/{b}"))
        rjobs.append(dict(base, key=("NEG", b), kind="G2a", fit=dict(g2a=FITS[b]["g2a"]), seed=10 * b + 3, tag=f"fx/NEG/{b}"))
        rjobs.append(dict(base, key=("UNI", b), kind="UNI", fit=None, seed=10 * b + 4, tag=f"fx/UNI/{b}",
                          tokens=[w for _, _, ls in B["planted"] for l in ls for w in l]))
    R = run_jobs(rep_job, rjobs, "replicates")
    errs = [k for k, v in R.items() if "error" in v]
    if errs:
        emit(f"STOP: replicate errors {errs}: {R[errs[0]]['error'][-800:]}")
        flush()
        raise SystemExit(6)
    emit("\n=== per book: target statistics; per candidate envelope and flags (Y = inside, order Rw1_line h2 rhythm) ===")
    CNT = dict(POS=0, ORACLE=0, NEG=0, UNI=0)
    KILL = {k: {s: 0 for s in STATS} for k in CNT}
    for b, B in enumerate(BOOKS):
        tgt = book_stats(B["planted"], f"fx/TARGET/{b}")
        emit(f"book {b}: target {fmt_stats(tgt)}")
        for cand in ("POS", "ORACLE", "NEG", "UNI"):
            env = envelope(R[(cand, b)]["rows"])
            ex, fl, kill = judge(tgt, env)
            for s in kill:
                KILL[cand][s] += 1
            CNT[cand] += int(ex)
            emit(f"  {cand:6s} {fmt_env(env)} flags {fl} -> {'EXCLUDED' if ex else 'not excluded'}"
                 f"{' (' + ', '.join(kill) + ')' if kill else ''}")
        flush()
    pos_ok = (N_BOOKS - CNT["POS"]) >= POS_MIN
    or_ok = (N_BOOKS - CNT["ORACLE"]) >= ORACLE_MIN
    neg_ok = CNT["NEG"] >= NEG_MIN
    # battery diagnostic, book 0
    emit("\n=== s67 battery DIAGNOSTIC (book 0; first replicate of each candidate vs the planted book; not a gate) ===")
    B = BOOKS[0]
    reps = OrderedDict((c, R[(c, 0)]["first"]) for c in ("POS", "ORACLE", "NEG", "UNI"))
    bd = battery_diag(B["planted"], B["qs"], reps, SEED + 70000, "fx")
    for nm, (nf, counts) in bd.items():
        emit(f"  {nm:6s} folds >= 4/6: {nf}/15 | per fold " + " ".join("NA" if c is None else str(c) for c in counts))
    emit("\n=== FIXTURE CALLS ===")
    emit(f"POS (G2b refitted) not excluded on {N_BOOKS - CNT['POS']}/{N_BOOKS} (need >= {POS_MIN}): {pos_ok}; "
         f"killing stats {KILL['POS']}")
    emit(f"ORACLE (true planted G2b) contains the planted book on {N_BOOKS - CNT['ORACLE']}/{N_BOOKS} (need >= {ORACLE_MIN}): "
         f"{or_ok}; killing stats {KILL['ORACLE']}")
    emit(f"NEG (G2a fitted) excluded on {CNT['NEG']}/{N_BOOKS} (need >= {NEG_MIN}): {neg_ok}; killing stats {KILL['NEG']}")
    emit(f"UNI (unigram word baseline, diagnostic) excluded on {CNT['UNI']}/{N_BOOKS}; killing stats {KILL['UNI']}")
    emit(f"FIXTURE_PASS = {pos_ok and or_ok and neg_ok}")
    emit(f"finished: {S87.clock()}")
    flush()


# ======================================================================= real run (not executed before the stub)
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
    return sorted(set(out) | {SELF.relative_to(ROOT).as_posix()})


def data_files():
    return ([f"data/translit/{f}.meta.json" for f in TRANSLITS.values()]
            + ["data/controls_realline/cremma_all_marks.meta.json", "data/controls/latin_macer_floridus.txt"])


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


def latest_fixture():
    fs = sorted(RUN_DIR.glob("fixture_*.txt"))
    if not fs:
        return None, False
    return fs[-1], "FIXTURE_PASS = True" in fs[-1].read_text(encoding="utf-8")


def run_real():
    global OUT
    final = ROOT / "results_s113.txt"
    if final.exists():
        print("STOP: results_s113.txt exists; results are never overwritten")
        raise SystemExit(3)
    OUT = RUN_DIR / f"progress_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    emit("S113: G2a / G2b judged against their own replicate envelopes on Rw1_line, h2, rhythm (D-066 (r))")
    emit(f"date: {S87.clock()}")
    emit(f"tools/s113_g2_envelope.py sha256={sha256(SELF)}")
    sm = stub_match()
    emit(f"prereg stub {STUB.name} stub_match={sm}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m) if (ROOT / m).exists() else 'MISSING'}")
    fx, fx_ok = latest_fixture()
    emit(f"fixture gate: latest {fx.name if fx else '-'} FIXTURE_PASS = {fx_ok}")
    if sm != "True" or not fx_ok:
        emit("STOP: stub mismatch or fixture gate not passed; no real statistic computed")
        flush()
        raise SystemExit(4)
    content_lines, _ = S102.load_p1()
    streams = S110.input_streams(content_lines)
    cb = S110.Codebook(streams["content"])
    emit(f"content input: {len(streams['content'])} words, codebook V = {cb.V}")
    REF = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    FITS = run_jobs(fit_job, [dict(key=T, pages=P, seed=SEED + 100 + i) for i, (T, P) in enumerate(REF.items())], "fits")
    errs = [k for k, v in FITS.items() if "error" in v]
    if errs:
        emit(f"STOP: fit errors {errs}: {FITS[errs[0]]['error'][-800:]}")
        flush()
        raise SystemExit(5)
    rjobs = []
    for ti, (T, P) in enumerate(REF.items()):
        fi = FITS[T]["g2b"].fit_info
        emit(f"  {T}: {len(P)} pages, {sum(len(l) for _, _, ls in P for l in ls)} tokens; G2b phi {fi['phi']} m {fi['m']} "
             f"kappa {fi['kappa']} tau {fi['tau']} drift pre 1/{fi['pre_lam']} suf 1/{fi['suf_lam']}")
        lay = [(pid, q, [len(l) for l in ls]) for pid, q, ls in P]
        for ci, c in enumerate(CONSTR):
            for ii, inp in enumerate(INPUTS):
                rjobs.append(dict(key=(T, c, inp), kind=c, fit=dict(g2a=FITS[T]["g2a"], g2b=FITS[T]["g2b"]), layout=lay,
                                  inp_words=streams[inp], cb=cb, n_rep=N_REP, seed=1000 + 100 * ti + 10 * ci + ii,
                                  tag=f"s113/{T}/{c}/{inp}"))
    flush()
    R = run_jobs(rep_job, rjobs, "replicates")
    errs = [k for k, v in R.items() if "error" in v]
    if errs:
        emit(f"STOP: replicate errors {errs}: {R[errs[0]]['error'][-800:]}")
        flush()
        raise SystemExit(6)
    CALL = {}
    for T, P in REF.items():
        tgt = book_stats(P, f"s113/TARGET/{T}")
        emit(f"\n=== {T}: manuscript {fmt_stats(tgt)} ===")
        for c in CONSTR:
            for inp in INPUTS:
                env = envelope(R[(T, c, inp)]["rows"])
                ex, fl, kill = judge(tgt, env)
                CALL[(T, c, inp)] = ex
                emit(f"  {c} {inp:12s} {fmt_env(env)} flags {fl} -> {'EXCLUDED' if ex else 'not excluded'}"
                     f"{' (killing: ' + ', '.join(kill) + ')' if kill else ''}")
        flush()
    emit("\n=== s67 battery DIAGNOSTIC (ZL3b; first replicate of each cell; not a gate) ===")
    P = REF[PRIMARY]
    reps = OrderedDict((f"{c}/{inp}", R[(PRIMARY, c, inp)]["first"]) for c in CONSTR for inp in INPUTS)
    bd = battery_diag(P, S67.folds_of(P), reps, SEED + 80000, "real")
    for nm, (nf, counts) in bd.items():
        emit(f"  {nm:18s} folds >= 4/6: {nf}/15 | per fold " + " ".join("NA" if x is None else str(x) for x in counts))
    emit("\n=== CALLS ===")
    for T in REF:
        ce = {c: all(CALL[(T, c, i)] for i in INPUTS) for c in CONSTR}
        emit(f"{T}{' (primary)' if T == PRIMARY else ' (replication)'}: G2a_EXCLUDED = {ce['G2a']}; G2b_EXCLUDED = {ce['G2b']}; "
             f"G2_EXCLUDED = {ce['G2a'] and ce['G2b']}")
    ce = {c: all(CALL[(PRIMARY, c, i)] for i in INPUTS) for c in CONSTR}
    if ce["G2a"] and ce["G2b"]:
        v = "full-size combinatory-table procedures (G2a, G2b) closed as producers (killing statistics per cell above)"
    elif ce["G2a"] or ce["G2b"]:
        v = (f"{'G2a' if ce['G2a'] else 'G2b'} closed; {'G2b' if ce['G2a'] else 'G2a'} survives this test "
             "(survival is not a match)")
    else:
        v = "not excluded by their own envelopes; record and return to D-066"
    emit(f"VERDICT: {v}")
    emit(f"finished: {S87.clock()}")
    flush()
    with open(final, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(log) + "\n")


def main():
    global OUT
    if LIST_FILES:
        for m in stub_files():
            print(m)
        return
    if FIXTURE:
        OUT = RUN_DIR / f"fixture_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        run_fixture()
        return
    run_real()


if __name__ == "__main__":
    main()
