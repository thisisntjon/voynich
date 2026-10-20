"""S89: do genres with LINE-LEVEL repetition, or a line-scoped pool producer fitted out of sample, reproduce the
Voynich core-layer signature?

AMENDMENT 1 (06:39 PDT, after the first real run crashed; crash only): the frozen run crashed in S87.profile on
 R_enochian (descriptive, 1,306 tokens; its held-out pages hold no within-line pair, torch max() on an empty tensor)
 after profiling five gating texts.  With --a1-89 a DESCRIPTIVE text whose profile raises is reported as "not
 profilable" and skipped (a gating text that raises still stops the run); outputs go to results_s89_amend1.txt and
 runs/s89/amend1/.  Nothing else changes: texts, seeds, bands, C1, C2 and the reading are as frozen.

FREEZE SCOPE (lead decision received 06:36 PDT; this block governs and overrides the arm-B text and calls below):
 Arm B deferred (producer failed its own planted-instance fixture: FX1 4/15 after one revision; double-sampling
 locality bias).  The arm-B code stays in this file but is disabled (RUN_ARM_B = False) and is never run under this
 stub; arm B is split out to a later experiment.  Fixture history for the record: run 5 (four parameters) FX1 0/15
 (H 11/15, G (d) 0/15); revision 1 (mix) run 7 FX1 4/15 (H 12/15, G 5/15).
 CALLS FOR THIS FREEZE:
   C1: per arm-A text (gating texts, >= N_TOT tokens, single texts and class pools): Voynich-like iff S87.c1 (s87's
       four-part rule, unchanged bands: ORDER = S87.ORDER_BAND, LOCALITY recomputed from VOY as s87).
   C2: count of Voynich-like gating texts per class R, T, N (descriptive texts reported, never counted).
   READING: any gating text Voynich-like -> "a real genre with line-level repetition reproduces the core layer:
       <genre>"; none -> "no line-repetition genre reproduces the core layer" + the closest gating text (smallest
       S87.distance D) and its failing component(s).
 FIXTURE FOR THIS FREEZE (--fx89): FX2 (Markov prose not Voynich-like against the fixture target built from the planted
   line-pool text FX_A) and FXP (S87.profile recovers the independent planted in-line-repetition text FX_B as
   Voynich-like on (b) and (c)).  COMPUTE: arm A runs in the main process (GPU through S87; BelowNormal).

TARGET (s87 amendment 1, c-432; results_s87_amend1.txt): the Voynich core layer (SlotSegmenter cores) has a four-part
signature that no tested class reproduced: (a) weak but real core order at matched K (MM excess K100 +0.020..+0.034,
frozen band [+0.012321, +0.092252]; K200 band [-0.003465, +0.086474]); (b) in-line reuse R_within(1) 1.18-1.22,
p 0.001; (c) cross-line avoidance R_cross(1) 0.56-0.67 (s87's rule: R_cross(1) < R_within(1)); (d) quire-locality
ratio inside [0.9074, 1.0499].  Prose, verse and list genres: too much order, no in-line reuse.  s57/s67/line-pool/
page-pool generators: no order, no cross-line avoidance.

PRE-REGISTRATION: s89_line_repetition_genres.prereg.sha256 (sha256sum format, LF, no BOM) = sha256 of this file, of
every local module it imports and of every data file it reads directly, frozen BEFORE any real-data run.  Before the
freeze the script ran only with --fx89 (synthetic; reads no real data; writes only runs/s89/fixture.txt).
Disclosed pre-freeze looks at real data: the downloaded and local reference files were opened to find body line
ranges, section markers and line widths (to write the load_* rules); Voynich page counts per quire (folds: the 15
quires with >= 4 ZL3b pages, quire J (2 pages) stays in training); the ZL3b SlotSegmenter empty-core share (0.0).
No profile statistic was computed on any arm-A text or on any producer output from real data before the freeze.

PROFILE CODE: s87_core_layer_genre imported and used unchanged: S87.profile (order = s80 machinery, M-freq, MM excess
over 1000 within-line shuffles at N_match; R = roach r5 R5b, 1000 within-page shuffles; locality = 15 blocks, 500
permutations, 2000 bootstraps), S87.c1, S87.distance, S87.layout, S87.loc_band_from, S87.order_band_from,
S87.tokens_norm, S87.meta_lines.  N_match is frozen at 4731 (s87 amendment 1, smallest held-out count there) so
order values are on s87's footing; a text whose held-out pages hold fewer tokens is scored on all of them (flagged).
Amendment-1 page-id handling: every concatenation (replicates, pools) gets unique page ids "<tag>:<id>", so
S80.prepare never merges pages.  Bands: ORDER = S87.ORDER_BAND (frozen); LOCALITY = recomputed here from the three
Voynich profiles exactly as s87 (same layout, seeds 20261018 + 100 i) and checked against s87 amendment 1
[0.9074, 1.0499] (validity V1).

ARM A (reference classes with line-level repetition; word = core (identity), PRIMARY; SlotSegmenter stems SECONDARY,
descriptive).  Lines = the source's own lines (verse lines, printed/OCR lines, manuscript lines): line-level
repetition lives there, so no text is re-cut to ZL3b line lengths (deviation from s87, which re-cut list/prose
texts).  Pages = lines grouped by ZL3b's page line counts (s87 rule).  OCR rule (ocr_lines): whitespace collapsed,
S87.tokens_norm(min_len 2), lines with >= 2 tokens kept; for glossary columns lines wider than MAXC characters are
dropped (footnotes and prefaces run full width).
 R ritual repetition:
   R_kalevala_fi        Kalevala (Finnish runo verse, charm-rich; Gutenberg 7000; verse lines, min_len 1)
   R_horae_ebor_la      Horae Eboracenses, hours/litany/prayers (Latin; lines 5800-18078 of the OCR)
   R_atharva_en         Atharva-Veda hymns and charms books X-XX (English verse tr. Griffith 1896; lines 89-35660)
   R_carmina_gd_en      Carmina Gadelica vol. 1, hymns and incantations (Gaelic + facing English; from line 2168)
   R_steganographia_la  Trithemius Steganographia 1608 (spirit conjurations as cipher; data/controls OCR)
   R_enochian           Enochian Keys / Calls (data/controls; one Key per line)
   R_egerton821_la      CREMMA Egerton 821, sortes and charms (real manuscript lines)
   R_hours_sbb_la       CREMMA SBB-PK Hdschr. 25, Book of Hours (real manuscript lines)
 T tabular texts written as lines:
   T_alphita_la         Alphita glossary, real OCR lines (genre-s87 file, s87's Alphita filter, lines kept)
   T_promptorium_enm_la Promptorium parvulorum, English-Latin glossary columns (lines 4250-64656, MAXC 40)
   T_sinonoma_la_en     Sinonoma Bartholomei glossary (lines 1733-5361, Incipiunt..Expliciunt; MAXC 48)
   T_horae_kalendar_la  Horae Eboracenses kalendar (lines 3628-5800; dominical letters/golden numbers/saints)
   (no ephemeris, astrological, medical or computus table in word form was found free; reported as unavailable)
 N notations / abbreviated texts:
   N_cremma_<ms>        13 CREMMA Latin manuscripts outside verse and liturgy (graphemic transcription,
                        abbreviations NOT expanded): the 12 prose manuscripts of s87's P_cremma_prose_la (which
                        include the medical CLM13027, Latin16195, Phi_10a135) plus H318 (so N overlaps s87's P)
 Class pools: R_pool, T_pool, N_pool = each member's first q_i tokens (whole lines), concatenated in the listed
   order; quotas water-filled to N_TOT (members in ascending size: q_i = min(size_i, ceil(remaining / members left))).  General rule (s87): a text (or pool) with fewer than N_TOT = 22,500 tokens after
   cleaning is UNMATCHED: profiled at its own size, printed, never in a call.  GATING = >= N_TOT tokens.

ARM B (one line-scoped producer, LP; 15-quire leave-one-quire-out on ZL3b, RF1b, IT2a; folds = s67's).
 Per fold (T, Q): training = all pages of T outside quire Q.  SlotSegmenter fitted on training tokens -> cores.
 Inputs: per-quire core vocabulary (token counts of each quire's cores; for the held-out quire its own words
   segmented by the training segmenter: vocabulary is given data, as s87's page pools); bigram table B = within-line
   adjacent core pairs of the TRAINING pages only; real page layout (each page's real line lengths).
 Producer, per page (no state crosses pages): for each line of length n:
   pool: k = min(#vocab, max(1, round(alpha n))) distinct cores drawn without replacement from the quire vocabulary,
     weight = mixed quire weight x (1 - pen if the core occurs in the previous line of the page else 1) (if every weight
     is 0 the penalty is dropped for that line);
   token 1: from the pool, weight = quire count;  token i > 1: with probability rho a uniform copy of an earlier
     token of the same line (in-line reuse), else from the pool with probability (1 - lam) f(c) + lam B(c | prev),
     f = pool-normalised quire counts, B(c | prev) = training bigram counts prev -> c restricted to the pool and
     normalised (if prev has no training successor in the pool: f alone).
 Words (C3 only): word = prefix + core + suffix, (prefix, suffix) from s67's CAProducer affix table (core class,
   line position, previous suffix; Witten-Bell back-off; training pages only; unseen cores -> back-off class 12).
 Free parameters (5): alpha (pool size), lam (transition strength), rho (in-line reuse), pen (previous-line penalty),
   mix (the quire vocabulary is (1 - mix) x quire distribution + mix x training-lexicon distribution; the training
   lexicon = core counts of the fold's training pages, so the held-out quire borrows nothing from itself).
   [REVISION 1 (pre-freeze, the one allowed by the lead; after fixture run 5, 06:28 PDT): run 5 had H (a-c) on 11/15
   folds but G failed (d) on 15/15: G locality 0.84-0.88 vs the fixture band [0.892, 0.960] (target 0.926), because
   regenerating from each quire's OBSERVED vocabulary samples twice and makes text more quire-local than the source.
   mix was added as a fifth fitted parameter (grid below, start 0.1, swept after rho) to let the fit match (d).  The
   brief named four parameters; this is a disclosed deviation.  Run 5 also used 2 workers after a low-memory stop.]
 FIT (training quires only): target = S87.profile of the real training pages (cores by the training segmenter,
   identity profile, whole training text, own size); candidate = S87.profile of LP output on the training pages'
   layout (common random numbers: seed 0).  Loss = mean of z^2 over (order K100, order K200, R_within(1),
   R_cross(1), locality ratio): z = (gen - real) / hw for order and locality (hw = half-widths of the frozen bands:
   0.039966, 0.044970, 0.071250) and z = ln(gen / real) / ln 1.25 for the two R's (s87's D scaling).  During the fit
   the profile runs with reduced counts (order 200 shuffles, R 200, locality 100 permutations, 200 bootstraps; set as
   S87 module attributes, code unchanged); every scored profile uses s87's full counts.
   Search: coordinate descent from (alpha 1.7, lam 0.3, rho 0.06, pen 0.6) over the grids below, sweeping pen, rho,
   alpha, lam; up to 3 sweeps, stopping at a sweep with no improvement.
 SCORING per fold (full counts; s87 bands):
   H (held-out text): the held-out quire Q's pages generated by the fitted LP (Q's vocabulary, training bigrams, Q's
     real line lengths) in independent replicates (seeds 1001, 1002, ...; page ids "r<j>:<id>") until >= N_TOT
     tokens, cut to N_TOT.  [(d) is not defined on H: all blocks share Q's vocabulary; (d) is carried by G.]
   G (global text): every page of T (file order, real line lengths) generated by the fold's fitted LP (each page
     from its own quire's vocabulary; training bigrams), cut to N_TOT as the Voynich texts in s87.
   Fold call: LP is Voynich-like on fold Q iff S87.c1 components (a), (b), (c) hold on H AND all four (a)-(d) hold
     on G.  [Pre-freeze change after fixture run 2: H's locality is not trivially in band (replicate blocks share one
     vocabulary, ratio ~0.99, outside a band that excludes 1), so (d) is judged on G only.]
   Validity (not gating): V2 the REAL held-out quire's cores replicated the same way (ids "r<j>:<id>"): (a), (b), (c)
     flags printed ((d) is meaningless for exact replicates).
 C3 battery (secondary): s67's six predictions (s57 P1-P5 + P7 type count) by s67's own scoring code (S67.score_model,
   S57.Measured, S57.draws_for, N_DRAW 300, real draws with s67's seeds 20261017 + 1000 ti + 10 fi): LP words on the
   training pages' layout + the held-out pages' layout, seeds 1 and 2.

CALLS (pre-registered)
 C1: per arm-A text (gating: >= N_TOT tokens; single texts and class pools), Voynich-like iff S87.c1 (all of a-d).
 C2: arm B: LP is Voynich-like on held-out quires on >= 8/15 folds on each of ZL3b, RF1b, IT2a.
 C3: arm B also holds >= 5/6 of s67's battery on >= 8/15 folds on each transliteration (reported, secondary).
 READING (one): any gating arm-A text Voynich-like -> "a real genre with line-level repetition reproduces the core
   layer: <genre>"; else C2 true -> "a line-scoped pool producer with weak transitions and cross-line avoidance
   reproduces the core layer out of sample"; else -> "core signature still unreproduced" + the closest arm-A text
   (smallest S87.distance D) and the closest arm-B fold text (smallest D over H texts), each with failing components.
 Validity V1: the three Voynich profiles recomputed here are Voynich-like under C1 and give the s87 locality band.

FIXTURE (--fx89; synthetic only): a 15-quire synthetic manuscript (12 pages x 20 lines per quire, line lengths
 1 + Poisson(7)); 1,500 letter-string cores, quire vocabularies = 6,000 draws from 0.7 Zipf + 0.3 quire topic; a
 planted sparse bigram table.  FX_A and FX_B = the LP producer planted at (alpha 2.4, lam 0.35, rho 0.05, pen 0.5),
 seeds 1 and 2.  [Pre-freeze changes after fixture run 2 (FAIL 0/15): that world (2,500 draws, 0.4/0.6 mix, alpha 0.8,
 rho 0.08, pen 0.7) gave R_within(1) ~6, far from Voynich's 1.2, and every fit sat on the grid edge alpha 0.3; the
 alpha grid was widened to 5.0 and the start moved to 1.7; the H locality rule above changed.]  Target
 bands from FX_A by s87's rules (order: s80-style 80 % page subsamples, 200 draws x 20; locality: bootstrap).
 FX1: LP fitted LOQO on FX_B (identity segmentation) is Voynich-like (H and G) on >= 12/15 folds.
 FX2: FX_prose (s87's Markov prose generator, same layout) is not Voynich-like under C1 against the fixture target.
 FX3 (crash test, not gating): the C3 battery runs end to end on one fixture fold.
COMPUTE: 2 worker processes (arm B folds; lead decision received 06:24 PDT after a low-memory stop of fixture run 4; CUDA cache
 emptied after every fold), BelowNormal priority; shuffles, permutations and MI on the GPU (torch
 cuda) through S87; CPU fallback.  Device recorded in the header.
Writes ONLY results_s89.txt and runs/s89/ (fixture: runs/s89/fixture.txt only).
Run: python -I s89_line_repetition_genres.py     Fixture: --fx89     Stub helper: --list-locals
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, OrderedDict, defaultdict  # noqa: E402
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

import s87_core_layer_genre as S87  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

S80 = S87.S80
S57 = S67.S57

SELF = ROOT / "s89_line_repetition_genres.py"
STUB = ROOT / "s89_line_repetition_genres.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s89"
GENRE = ROOT / "data" / "external" / "genre-s89"
GENRE87 = ROOT / "data" / "external" / "genre-s87"
CTRL = ROOT / "data" / "controls"
RL = ROOT / "data" / "controls_realline"
FIXTURE = "--fx89" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
AMEND1 = "--a1-89" in sys.argv   # AMENDMENT 1 (06:39 PDT, crash only): see docstring; outputs to *_amend1
if AMEND1:
    RUN_DIR = RUN_DIR / "amend1"
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / ("results_s89_amend1.txt" if AMEND1 else "results_s89.txt")
SEED = 20261089
SEED87 = S87.SEED
N_TOT, NB = S87.N_TOT, S87.NB
N_MATCH = 4731
LOC_BAND_S87 = (0.9074, 1.0499)
HW = dict(o100=(0.092252 - 0.012321) / 2, o200=(0.086474 + 0.003465) / 2, loc=(1.0499 - 0.9074) / 2)
FIT_COUNTS = dict(N_SHUF_ORDER=200, N_SHUF_R=200, N_PERM_LOC=100, N_BOOT=200)
FULL_COUNTS = dict(N_SHUF_ORDER=S87.N_SHUF_ORDER, N_SHUF_R=S87.N_SHUF_R, N_PERM_LOC=S87.N_PERM_LOC, N_BOOT=S87.N_BOOT)
GRID = OrderedDict(alpha=[0.3, 0.5, 0.8, 1.2, 1.7, 2.4, 3.4, 5.0],
                   lam=[0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0],
                   rho=[0.0, 0.03, 0.06, 0.1, 0.15, 0.2, 0.3],
                   pen=[0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0],
                   mix=[0.0, 0.05, 0.1, 0.2, 0.3, 0.5])
START = dict(alpha=1.7, lam=0.3, rho=0.06, pen=0.6, mix=0.1)
SWEEP = ["pen", "rho", "mix", "alpha", "lam"]
MAX_SWEEPS = 3
KEYS = ("alpha", "lam", "rho", "pen", "mix")
N_WORKERS = 2
RUN_ARM_B = False   # arm B deferred (lead decision 06:36 PDT); never run under the s89 stub
MIN_C2 = 8
MAXC_PROMPT, MAXC_SINON = 40, 48
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
CREMMA_MED = ["H318", "CLM13027", "Latin16195", "Phi_10a135"]
CREMMA_N = CREMMA_MED + [m for m in S87.CREMMA_PROSE if m not in CREMMA_MED]   # 13 unique
DATA_FILES = (["data/external/genre-s89/" + f for f in
               ("pg7000_kalevala.txt", "horaeeboracenses00surtuoft_djvu.txt", "4617_djvu.txt",
                "carminagadelicah01carm_0_djvu.txt", "sinonomabartholo01mirfuoft_djvu.txt",
                "promptoriumparvu00galfuoft_djvu.txt")]
              + ["data/external/genre-s87/alphitaamedicob00mowagoog_djvu.txt",
                 "data/controls/trithemius_steganographia_1608.txt", "data/controls/enochian_keys_dee.txt"]
              + [f"data/controls_realline/cremma_{m}.meta.json" for m in ["Egerton821", "SBB_PK_Hdschr25"] + CREMMA_N]
              + [f"data/translit/{f}.meta.json" for f in TRANSLITS.values()])
log: list[str] = []
T0 = time.time()


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


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


def stub_files():
    return local_modules() + list(DATA_FILES)


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


def set_counts(c):
    for k, v in c.items():
        setattr(S87, k, v)


# ======================================================================= producer
class LinePool:
    """Line-scoped pool producer (arm B).  vocab: {quire: Counter(core -> count)}; bigram: {prev: Counter(next)}."""

    def __init__(self, vocab, bigram, affix=None, glob=None):
        """glob: Counter of training core counts (the global lexicon for the mix parameter; None -> sum of vocab)."""
        if glob is None:
            glob = Counter()
            for cnt in vocab.values():
                glob.update(cnt)
        allc = set(c for cnt in vocab.values() for c in cnt if c != "") | set(c for c in glob if c != "")
        items = sorted(allc)
        idx = {c: i for i, c in enumerate(items)}
        self.items = items
        g = np.array([float(glob.get(c, 0)) for c in items])
        self.g = g / g.sum()
        self.succ = []
        for c in items:
            row = bigram.get(c)
            self.succ.append({idx[d]: float(n) for d, n in row.items() if d in idx} if row else {})
        self.Q = {}
        for q, cnt in vocab.items():
            w = np.array([float(cnt.get(c, 0)) for c in items])
            if w.sum() > 0:
                self.Q[q] = w / w.sum()
        self.affix = affix
        self.set_params(START)

    def set_params(self, p):
        self.p = dict(p)

    def page(self, rng, q, lens, pyrng=None):
        items, succ = self.items, self.succ
        a, lam, rho, pen, mix = self.p["alpha"], self.p["lam"], self.p["rho"], self.p["pen"], self.p["mix"]
        w = (1.0 - mix) * self.Q[q] + mix * self.g
        nI = len(items)
        prev = None
        out_c, out_w = [], []
        for li, n in enumerate(lens):
            if n <= 0:
                continue
            ww = w.copy()
            if prev and pen > 0:
                ww[list(prev)] *= (1.0 - pen)
                if ww.sum() <= 0:
                    ww = w.copy()
            k = min(nI, max(1, int(round(a * n))), int((ww > 0).sum()))
            pool = rng.choice(nI, size=k, replace=False, p=ww / ww.sum())
            f = w[pool] / w[pool].sum()
            line = []
            for i in range(n):
                if i > 0 and rho > 0 and rng.random() < rho:
                    c = line[int(rng.integers(i))]
                else:
                    pr = f
                    if i > 0 and lam > 0:
                        row = succ[line[-1]]
                        if row:
                            t = np.array([row.get(int(j), 0.0) for j in pool])
                            s = t.sum()
                            if s > 0:
                                pr = (1.0 - lam) * f + lam * t / s
                    cs = np.cumsum(pr)
                    c = int(pool[min(k - 1, int(np.searchsorted(cs, rng.random() * cs[-1], side="right")))])
                line.append(c)
            prev = set(line)
            cores = [items[c] for c in line]
            out_c.append(cores)
            if self.affix is not None and pyrng is not None:
                out_w.append(self.words(pyrng, li, cores))
        return out_c, out_w

    def words(self, pyrng, li, cores):
        L = len(cores)
        psuf = "^"
        out = []
        for i, c in enumerate(cores):
            pos = S67.pos_class(li, i, L)
            for _ in range(50):
                pr, su = self.affix.affix(pyrng, c, pos, psuf)
                if pr + c + su:
                    break
            w = pr + c + su or "o"
            out.append(w)
            psuf = su
        return out

    def text(self, spec, seed, words=False, tag=None):
        """spec: list of (pid, quire, [line lengths]) -> core pages [(id, lines)] (and word pages if words)."""
        rng = np.random.default_rng(seed)
        pyrng = random.Random(seed)
        cp, wp = [], []
        for pid, q, lens in spec:
            c, w = self.page(rng, q, lens, pyrng if words else None)
            name = f"{tag}:{pid}" if tag is not None else pid
            cp.append((name, c))
            if words:
                wp.append((name, w))
        return (cp, wp) if words else cp


def bigram_of(core_pages):
    B = defaultdict(Counter)
    for _, lines in core_pages:
        for ln in lines:
            for a, b in zip(ln[:-1], ln[1:]):
                B[a][b] += 1
    return B


def comps(p):
    return dict(o100=p["order"][100]["mm"], o200=p["order"][200]["mm"], Rw1=p["rep"][1]["Rw"], Rc1=p["rep"][1]["Rc"],
                loc=p["loc"]["ratio"])


def fit_loss(g, r):
    z = [(g["o100"] - r["o100"]) / HW["o100"], (g["o200"] - r["o200"]) / HW["o200"], (g["loc"] - r["loc"]) / HW["loc"],
         math.log(max(g["Rw1"], 1e-3) / max(r["Rw1"], 1e-3)) / math.log(1.25),
         math.log(max(g["Rc1"], 1e-3) / max(r["Rc1"], 1e-3)) / math.log(1.25)]
    return float(np.mean(np.square(z)))


def own(pages):
    return S87.layout(None, True, pages, None, None, n_tot=10 ** 9)


def cut(pages):
    return S87.layout(None, True, pages, None, None, n_tot=N_TOT)


def replicate_to_ntot(make, first_seed):
    """make(seed, j) -> pages for replicate j; concatenated until >= N_TOT tokens, cut to N_TOT."""
    pages, tot, j = [], 0, 0
    while tot < N_TOT:
        P = make(first_seed + j, j)
        pages.extend(P)
        tot += sum(len(ln) for _, ls in P for ln in ls)
        j += 1
        if j > 400:
            break
    return cut(pages), j


def fit_lp(prod, spec_tr, target, seed):
    set_counts(FIT_COUNTS)
    cache = {}

    def ev(prm):
        key = tuple(prm[k] for k in KEYS)
        if key not in cache:
            prod.set_params(prm)
            pg = own(prod.text(spec_tr, 0))
            g = comps(S87.profile("fit", pg, "id", N_MATCH, seed))
            cache[key] = (fit_loss(g, target), g, dict(prm))
        return cache[key]
    best = ev(dict(START))
    sweeps = 0
    for _ in range(MAX_SWEEPS):
        sweeps += 1
        improved = False
        for k in SWEEP:
            for v in GRID[k]:
                r = ev(dict(best[2], **{k: v}))
                if r[0] < best[0] - 1e-12:
                    best = r; improved = True
        if not improved:
            break
    set_counts(FULL_COUNTS)
    prod.set_params(best[2])
    return dict(params=best[2], loss=best[0], gen=best[1], n_evals=len(cache), sweeps=sweeps)


# ======================================================================= one LOQO fold (worker)
def worker_init():
    S87.below_normal()
    try:
        torch.set_num_threads(1)
    except Exception:  # noqa: BLE001
        pass


def run_fold(job):
    t0 = time.time()
    set_counts(FULL_COUNTS)
    T, Q, ti, fi = job["T"], job["Q"], job["ti"], job["fi"]
    pages = job["pages"] if job.get("pages") is not None else S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS[T]}.meta.json")
    off = 1000 * ti + 10 * fi
    seed = SEED + off
    train = [(p, q, ls) for p, q, ls in pages if q != Q]
    test = [(p, q, ls) for p, q, ls in pages if q == Q]
    tr_tok = [w for _, _, ls in train for l in ls for w in l]
    seg = SlotSegmenter(tr_tok) if job["seg"] == "slot" else S80.identity_seg_factory(tr_tok)
    cache = {}

    def core(w):
        c = cache.get(w)
        if c is None:
            c = cache[w] = seg.segment(w)[1]
        return c
    cpages = [(p, q, [[core(w) for w in l] for l in ls]) for p, q, ls in pages]
    vocab = defaultdict(Counter)
    for p, q, ls in cpages:
        for l in ls:
            vocab[q].update(l)
    B = bigram_of([(p, ls) for p, q, ls in cpages if q != Q])
    affix = None
    if job.get("c3"):
        affix = S67.CAProducer([ls for _, _, ls in train], seg, True)
        affix.cls = defaultdict(lambda: S67.K, affix.cls)
    glob = Counter()
    for p, q, ls in cpages:
        if q != Q:
            for l in ls:
                glob.update(l)
    prod = LinePool(vocab, B, affix, glob)
    spec_tr = [(p, q, [len(l) for l in ls]) for p, q, ls in train]
    spec_te = [(p, q, [len(l) for l in ls]) for p, q, ls in test]
    spec_all = [(p, q, [len(l) for l in ls]) for p, q, ls in pages]
    real_tr = own([(p, ls) for p, q, ls in cpages if q != Q])
    target = comps(S87.profile("target", real_tr, "id", N_MATCH, seed))
    F = fit_lp(prod, spec_tr, target, seed)
    H, nrep = replicate_to_ntot(lambda s, j: prod.text(spec_te, s, tag=f"r{j}"), 1001)
    G = cut(prod.text(spec_all, 7))
    pH = S87.profile(f"LP_H_{T}_{Q}", H, "id", N_MATCH, seed + 1)
    pG = S87.profile(f"LP_G_{T}_{Q}", G, "id", N_MATCH, seed + 2)
    real_te = [(p, ls) for p, q, ls in cpages if q == Q]
    R, _ = replicate_to_ntot(lambda s, j: [(f"r{j}:{p}", ls) for p, ls in real_te], 0)
    pR = S87.profile(f"REAL_rep_{T}_{Q}", R, "id", N_MATCH, seed + 3)
    res = dict(T=T, Q=Q, n_test=len(test), test_tok=sum(len(l) for _, _, ls in test for l in ls), train_tok=len(tr_tok),
               fit=F, target=target, pH=pH, pG=pG, pR=pR, nrep=nrep, c3=None)
    if job.get("c3"):
        S57.N_DRAW = S67.N_DRAW
        tr2 = [(p, ls) for p, q, ls in train]
        te2 = [(p, ls) for p, q, ls in test]
        real_m = S57.Measured(f"{T} {Q} real", tr2, te2)
        real_dr = S57.draws_for([real_m], S67.SEED + off)
        real_pt = real_m.point()
        gens, ms = [], []
        for s in (1, 2):
            _, wtr = prod.text(spec_tr, 100 + s, words=True, tag="g")
            _, wte = prod.text(spec_te, 200 + s, words=True, tag="h")
            gens.append((wtr, wte))
            ms.append(S57.Measured(f"{T} {Q} LP s{s}", wtr, wte))
        gen_dr = S57.draws_for(ms, S67.SEED + off + 1)
        cells, gen_pt, rt, small = S67.score_model(real_m, real_pt, real_dr, ms, gen_dr, len(test),
                                                   [[ls for _, ls in b] for _, b in gens], [ls for _, ls in te2])
        res["c3"] = dict(n=sum(1 for k in S67.PREDS if cells[k][0]), holds={k: bool(cells[k][0]) for k in S67.PREDS},
                         text={k: cells[k][1] for k in S67.PREDS}, small=small, type_ratio=rt)
    res["secs"] = time.time() - t0
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return res


def run_pool(jobs, tag):
    import multiprocessing as mp
    out = {}
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(min(N_WORKERS, len(jobs)), initializer=worker_init) as pool:
        for r in pool.imap_unordered(run_fold, jobs):
            out[(r["T"], r["Q"])] = r
            print(f"  [{tag} {time.time() - t0:.0f}s] fold {r['T']} {r['Q']} done ({r['secs']:.0f}s; {r['fit']['n_evals']} evals; "
                  f"mix {r['fit']['params']['mix']} loss {r['fit']['loss']:.3f})", flush=True)
    return out


def flags(p, lb):
    ok, comp = S87.c1(p, lb)
    return ok, comp, "".join("Y" if v else "n" for v in comp.values())


def short(p):
    o, r, l = p["order"], p["rep"], p["loc"]
    return (f"o100 {o[100]['mm']:+.3f} o200 {o[200]['mm']:+.3f} Rw1 {r[1]['Rw']:.3f}(p{r[1]['pw']:.3f}) Rc1 {r[1]['Rc']:.3f} "
            f"loc {l['ratio']:.3f}")


def fold_rows(res, folds_by_T, lb, rw_v, rc_v, say):
    calls = {}
    for T, folds in folds_by_T.items():
        say(f"  {T}:")
        for Q in folds:
            r = res[(T, Q)]
            _, cH, fH = flags(r["pH"], lb)
            okH = cH["a_order"] and cH["b_Rwithin"] and cH["c_Rcross<Rwithin"]
            okG, _, fG = flags(r["pG"], lb)
            _, cR, _ = flags(r["pR"], lb)
            fR = "".join("Y" if cR[k] else "n" for k in ("a_order", "b_Rwithin", "c_Rcross<Rwithin"))
            dH = S87.distance(r["pH"], lb, rw_v, rc_v)[0]
            dG = S87.distance(r["pG"], lb, rw_v, rc_v)[0]
            calls[(T, Q)] = dict(H=okH, G=okG, ok=okH and okG, dH=dH, dG=dG, fH=fH, fG=fG, fR=fR)
            pr = r["fit"]["params"]
            c3 = r["c3"]
            c3s = (f" | C3 {c3['n']}/6 " + "".join("+" if c3["holds"][k] else "-" for k in S67.PREDS) + ("*" if c3["small"] else "")) if c3 else ""
            say(f"    {Q:2s} pages {r['n_test']:3d} tok {r['test_tok']:5d} | fit a {pr['alpha']} lam {pr['lam']} rho {pr['rho']} pen {pr['pen']} "
                f"mix {pr['mix']} loss {r['fit']['loss']:.3f} ({r['fit']['n_evals']} ev) | H[{r['nrep']}x] {short(r['pH'])} {fH} D {dH:.2f} | "
                f"G {short(r['pG'])} {fG} D {dG:.2f} | fold {'VOYNICH-LIKE' if okH and okG else '-'} | realQ abc {fR}{c3s}")
            say(f"       fit target (real training) o100 {r['target']['o100']:+.3f} o200 {r['target']['o200']:+.3f} Rw1 {r['target']['Rw1']:.3f} "
                f"Rc1 {r['target']['Rc1']:.3f} loc {r['target']['loc']:.3f}; fitted LP (in-sample, reduced counts) o100 {r['fit']['gen']['o100']:+.3f} "
                f"o200 {r['fit']['gen']['o200']:+.3f} Rw1 {r['fit']['gen']['Rw1']:.3f} Rc1 {r['fit']['gen']['Rc1']:.3f} loc {r['fit']['gen']['loc']:.3f}")
    return calls


# ======================================================================= fixture
FX_ALPH = "acdehiklnoqrsty"


def fx_world():
    rng = np.random.default_rng(89)
    names = set()
    while len(names) < 1500:
        L = int(rng.integers(2, 6))
        names.add("".join(FX_ALPH[int(i)] for i in rng.integers(0, len(FX_ALPH), size=L)))
    names = sorted(names)
    rng.shuffle(names)
    V = len(names)
    z = 1.0 / np.arange(1, V + 1); z /= z.sum()
    vocab = {}
    for qi in range(NB):
        q = f"Q{qi:02d}"
        topic = rng.choice(V, size=200, replace=False)
        boost = np.zeros(V); boost[topic] = rng.dirichlet(np.ones(200) * 0.5)
        d = 0.7 * z + 0.3 * boost
        draws = rng.choice(V, size=6000, p=d / d.sum())
        vocab[q] = Counter(names[i] for i in draws)
    B = defaultdict(Counter)
    for a in names:
        succ = rng.choice(V, size=4, replace=False)
        for s, wv in zip(succ, rng.dirichlet(np.ones(4))):
            B[a][names[s]] = int(1 + 20 * wv)
    lens = [1 + int(x) for x in rng.poisson(7, size=6000)]
    spec, k = [], 0
    for qi in range(NB):
        for pi in range(12):
            ll = lens[k:k + 20]; k += 20
            spec.append((f"q{qi:02d}p{pi:02d}", f"Q{qi:02d}", ll))
    return names, vocab, B, spec


def run_fixture():
    emit("S89 FIXTURE (synthetic only; no real data read)")
    emit(f"date: {S87.clock()}  device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); "
         f"below_normal={S87.below_normal()}")
    emit(f"s89_line_repetition_genres.py sha256={sha256(SELF)}  stub_match={stub_match()}")
    names, vocab, B, spec = fx_world()
    planted = dict(alpha=2.4, lam=0.35, rho=0.05, pen=0.5, mix=0.0)
    prod = LinePool(vocab, B)
    prod.set_params(planted)
    A = prod.text(spec, 1)
    Bt = prod.text(spec, 2)
    emit(f"fixture world: {len(names)} cores, {NB} quires x 12 pages x 20 lines; FX_A {sum(len(l) for _, ls in A for l in ls)} tokens; "
         f"planted {planted}")
    pA = S87.profile("FX_A", cut(A), "id", N_MATCH, SEED, interval=True)
    band = S87.order_band_from([pA])
    lb = S87.loc_band_from([pA])
    saved = S87.ORDER_BAND
    S87.ORDER_BAND = band
    rw_v, rc_v = pA["rep"][1]["Rw"], pA["rep"][1]["Rc"]
    emit(f"fixture target (FX_A): {short(pA)}; order bands K100 [{band[100][0]:+.4f},{band[100][1]:+.4f}] K200 "
         f"[{band[200][0]:+.4f},{band[200][1]:+.4f}]; locality band [{lb[0]:.4f},{lb[1]:.4f}]")
    # FX2: prose
    succ = np.random.default_rng(4).permutation(len(names))
    zz = 1.0 / np.arange(1, len(names) + 1); zz /= zz.sum()
    r = np.random.default_rng(5)
    cur, toks = 0, []
    for _ in range(N_TOT + 2000):
        cur = int(succ[cur]) if r.random() < 0.5 else int(r.choice(len(names), p=zz))
        toks.append(names[cur])
    pros, i = [], 0
    for pid, q, lens in spec:
        L = []
        for n in lens:
            L.append(toks[i:i + n]); i += n
        pros.append((pid, L))
        if i >= len(toks):
            break
    pP = S87.profile("FX_prose", cut(pros), "id", N_MATCH, SEED + 5)
    okP, _, fP = flags(pP, lb)
    emit(f"FX_prose: {short(pP)} C1 {fP} -> {'VOYNICH-LIKE' if okP else 'not Voynich-like'}")
    fx2 = not okP
    flush()
    # FXP (arm A): planted in-line-repetition text FX_B (independent seed) recovered on (b) and (c) by S87.profile
    pB = S87.profile("FX_B", cut(Bt), "id", N_MATCH, SEED + 7)
    okB, cB, fB = flags(pB, lb)
    fxp = cB["b_Rwithin"] and cB["c_Rcross<Rwithin"]
    emit(f"FXP planted in-line-repetition text FX_B: {short(pB)} C1 {fB} -> (b) and (c) recovered: {'PASS' if fxp else 'FAIL'}")
    emit(f"FX2 prose not Voynich-like: {'PASS' if fx2 else 'FAIL'}")
    fx1 = True
    if RUN_ARM_B:   # arm B deferred: the LOQO fixture below is not run under the s89 stub
        # FX1: LOQO on FX_B
        pagesB = [(pid, q, ls) for (pid, q, _), (_, ls) in zip(spec, Bt)]
        folds = sorted({q for _, q, _ in spec})
        jobs = [dict(T="FX_B", Q=Q, ti=9, fi=fi, pages=pagesB, seg="id", c3=(fi == 0)) for fi, Q in enumerate(folds)]
        res = run_pool(jobs, "fixture")
        calls = fold_rows(res, {"FX_B": folds}, lb, rw_v, rc_v, emit)
        n_ok = sum(1 for Q in folds if calls[("FX_B", Q)]["ok"])
        fx1 = n_ok >= 12
        emit(f"FX1 planted LP recovered as Voynich-like (H and G) on {n_ok}/{len(folds)} folds (need >= 12): {'PASS' if fx1 else 'FAIL'}")
        emit(f"   H-only {sum(calls[('FX_B', Q)]['H'] for Q in folds)}/{len(folds)}, G-only {sum(calls[('FX_B', Q)]['G'] for Q in folds)}/{len(folds)}; "
             f"fitted params: " + "; ".join(f"{Q} " + ",".join(str(res[('FX_B', Q)]['fit']['params'][k]) for k in KEYS) for Q in folds))
        emit(f"FX2 prose not Voynich-like: {'PASS' if fx2 else 'FAIL'}")
        c3 = res[("FX_B", folds[0])]["c3"]
        emit(f"FX3 (crash test, not gating) C3 battery ran on fold {folds[0]}: {c3['n']}/6 " +
             "".join("+" if c3["holds"][k] else "-" for k in S67.PREDS) if c3 else "FX3 C3 did not run")
    S87.ORDER_BAND = saved
    emit(f"FIXTURE {'PASS' if (fxp and fx2 and fx1) else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


# ======================================================================= arm A texts
def rdg(path):
    return Path(path).read_text(encoding="utf-8", errors="replace").splitlines()


def ocr_lines(L, min_len=2, min_tok=2, maxc=None):
    out = []
    for ln in L:
        s = " ".join(ln.split())
        if maxc is not None and len(s) > maxc:
            continue
        t = S87.tokens_norm(s, min_len)
        if len(t) >= min_tok:
            out.append(t)
    return out


def load_kalevala():
    L = rdg(GENRE / "pg7000_kalevala.txt")
    a = next(i for i, x in enumerate(L) if x.startswith("*** START OF"))
    b = next(i for i, x in enumerate(L) if x.startswith("*** END OF"))
    return ocr_lines(L[a + 1:b], min_len=1, min_tok=1)


def load_alphita_lines():
    out = []
    for ln in rdg(GENRE87 / "alphitaamedicob00mowagoog_djvu.txt")[300:20440]:
        s = ln.strip()
        if not (10 <= len(s) <= 48) or "GLOSSARY" in s or s[:1].isdigit() and "." in s[:4]:
            continue
        t = S87.tokens_norm(s, 2)
        if sum(w in S87.EN_STOP for w in t) >= 2 or len(t) < 1:
            continue
        out.append(t)
    return out


def arm_a_texts():
    """-> OrderedDict name -> (class, lines, label)."""
    T = OrderedDict()
    T["R_kalevala_fi"] = ("R", load_kalevala(), "Kalevala, Finnish runo verse with charms (verse lines)")
    T["R_horae_ebor_la"] = ("R", ocr_lines(rdg(GENRE / "horaeeboracenses00surtuoft_djvu.txt")[5799:18077]),
                            "Horae Eboracenses hours/litany/prayers, Latin, OCR lines")
    T["R_atharva_en"] = ("R", ocr_lines(rdg(GENRE / "4617_djvu.txt")[88:35659]), "Atharva-Veda hymns and charms X-XX, English (Griffith), OCR lines")
    T["R_carmina_gd_en"] = ("R", ocr_lines(rdg(GENRE / "carminagadelicah01carm_0_djvu.txt")[2167:]),
                            "Carmina Gadelica I hymns and incantations, Gaelic + English, OCR lines")
    T["R_steganographia_la"] = ("R", ocr_lines(rdg(CTRL / "trithemius_steganographia_1608.txt")),
                                "Trithemius Steganographia 1608 conjurations, Latin, OCR lines")
    T["R_enochian"] = ("R", ocr_lines(rdg(CTRL / "enochian_keys_dee.txt"), min_len=1, min_tok=1), "Enochian Keys/Calls (one Key per line)")
    T["R_egerton821_la"] = ("R", S87.meta_lines(RL / "cremma_Egerton821.meta.json"), "CREMMA Egerton 821 sortes and charms, ms lines")
    T["R_hours_sbb_la"] = ("R", S87.meta_lines(RL / "cremma_SBB_PK_Hdschr25.meta.json"), "CREMMA SBB-PK Hdschr. 25 Book of Hours, ms lines")
    T["T_alphita_la"] = ("T", load_alphita_lines(), "Alphita glossary, Latin, real OCR lines")
    T["T_promptorium_enm_la"] = ("T", ocr_lines(rdg(GENRE / "promptoriumparvu00galfuoft_djvu.txt")[4249:64655], maxc=MAXC_PROMPT),
                                 "Promptorium parvulorum English-Latin glossary columns, OCR lines <= 40 chars")
    T["T_sinonoma_la_en"] = ("T", ocr_lines(rdg(GENRE / "sinonomabartholo01mirfuoft_djvu.txt")[1732:5361], maxc=MAXC_SINON),
                             "Sinonoma Bartholomei glossary, OCR lines <= 48 chars")
    T["T_horae_kalendar_la"] = ("T", ocr_lines(rdg(GENRE / "horaeeboracenses00surtuoft_djvu.txt")[3627:5799]),
                                "Horae Eboracenses kalendar, Latin, OCR lines")
    for m in CREMMA_N:
        T[f"N_cremma_{m}"] = ("N", S87.meta_lines(RL / f"cremma_{m}.meta.json"),
                              f"CREMMA {m}, Latin abbreviated graphemic, ms lines" + (" (medical)" if m in CREMMA_MED else " (prose; in s87 P)"))
    for cls, lab in (("R", "ritual"), ("T", "tabular"), ("N", "abbreviated")):
        mem = [n for n, v in T.items() if v[0] == cls]
        size = {n: sum(len(x) for x in T[n][1]) for n in mem}
        quota, need, left = {}, N_TOT, len(mem)
        for n in sorted(mem, key=lambda m: (size[m], m)):   # water-filling: short members give their shortfall away
            quota[n] = min(size[n], math.ceil(need / left))
            need -= quota[n]; left -= 1
        lines = []
        for n in mem:
            tot = 0
            for ln in T[n][1]:
                if tot >= quota[n]:
                    break
                lines.append(ln); tot += len(ln)
        T[f"{cls}_pool"] = (cls, lines, f"{lab} class pool of {len(mem)} members, water-filled quotas (max {max(quota.values())} tokens)")
    return T


# ======================================================================= main
def main():
    if LIST_LOCALS:
        for m in stub_files():
            print(m)
        return
    if FIXTURE:
        run_fixture()
        return
    emit("S89: line-repetition genres (arm A) and a line-scoped pool producer, LOQO (arm B), vs the four-part core signature")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; priority BelowNormal set={S87.below_normal()}; "
         f"arm B on {N_WORKERS} worker processes (BelowNormal, GPU shared)")
    emit(f"s89_line_repetition_genres.py sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH} (frozen from s87 amendment 1); s87 counts {FULL_COUNTS}; fit counts {FIT_COUNTS}; seed {SEED}")
    emit(f"ORDER bands (S87.ORDER_BAND, frozen): K100 [{S87.ORDER_BAND[100][0]:+.6f},{S87.ORDER_BAND[100][1]:+.6f}] "
         f"K200 [{S87.ORDER_BAND[200][0]:+.6f},{S87.ORDER_BAND[200][1]:+.6f}]")
    flush()

    # ---- Voynich reference (s87 settings) -> locality band
    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]
    voy = []
    for i, T in enumerate(TRANSLITS):
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        voy.append(S87.profile(f"VOY_{T}", S87.layout(None, True, P, line_lens, page_nl), "slot", N_MATCH, SEED87 + 100 * i))
    lb = S87.loc_band_from(voy)
    rw_v = float(np.mean([p["rep"][1]["Rw"] for p in voy])); rc_v = float(np.mean([p["rep"][1]["Rc"] for p in voy]))
    same = abs(lb[0] - LOC_BAND_S87[0]) < 5e-4 and abs(lb[1] - LOC_BAND_S87[1]) < 5e-4
    emit(f"\nLOCALITY band (recomputed from VOY, s87 rule): [{lb[0]:.4f}, {lb[1]:.4f}]; s87 amendment 1 [{LOC_BAND_S87[0]}, "
         f"{LOC_BAND_S87[1]}] -> {'MATCH' if same else 'DIFFERS'}")
    emit(f"R_VOY (mean of 3): R_within(1) {rw_v:.3f}, R_cross(1) {rc_v:.3f}")
    v1 = []
    for p in voy:
        ok, comp, f = flags(p, lb)
        emit(f"  V1 {p['name']}: {short(p)} C1 {f} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            v1.append(p["name"])
    flush()

    # ---- ARM A
    texts = arm_a_texts()
    emit("\n=== ARM A corpus list (class, gating, tokens, lines, label) ===")
    laid = OrderedDict()
    for name, (cls, lines, lab) in texts.items():
        lines = [ln for ln in lines if ln]
        ntok = sum(len(x) for x in lines)
        gating = ntok >= N_TOT
        laid[name] = (cls, gating, S87.layout(lines, True, None, line_lens, page_nl, n_tot=min(ntok, N_TOT)), lab, ntok, len(lines))
        emit(f"  {name:24s} {cls}  {'gating' if gating else 'UNMATCHED':9s} tokens {ntok:7d} lines {len(lines):6d} "
             f"mean line {ntok / max(1, len(lines)):5.2f}  {lab}")
    flush()
    emit("\n=== ARM A profiles (primary = whole words; C1 flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PA, PA2 = OrderedDict(), OrderedDict()
    for i, (name, (cls, gating, pages, lab, ntok, nl)) in enumerate(laid.items()):
        try:
            p = S87.profile(name, pages, "id", N_MATCH, SEED + 100 * i)
        except Exception as e:  # noqa: BLE001  AMENDMENT 1: descriptive texts only
            if gating or not AMEND1:
                raise
            emit(f"  {name:24s} NOT PROFILABLE (descriptive, {ntok} tokens): {type(e).__name__}: {str(e)[:90]}")
            continue
        p["cls"], p["gating"] = cls, gating
        PA[name] = p
        D = S87.distance(p, lb, rw_v, rc_v)[0]
        p["D"] = D
        emit("  " + S87.fmt_prof(p, lb) + f" | D {D:.2f} [{cls}{'' if gating else ', UNMATCHED'}; held-out {p['matched_tokens']}"
             f"{' < N_match' if p['matched_tokens'] < N_MATCH else ''}]")
        flush()
    emit("\n=== ARM A secondary: SlotSegmenter stems (descriptive) ===")
    for i, (name, (cls, gating, pages, lab, ntok, nl)) in enumerate(laid.items()):
        if name not in PA:
            continue
        try:
            p = S87.profile(name + "/stem", pages, "slot", N_MATCH, SEED + 100 * i + 50)
        except Exception as e:  # noqa: BLE001  AMENDMENT 1: descriptive texts only
            if gating or not AMEND1:
                raise
            emit(f"  {name + '/stem':24s} NOT PROFILABLE (descriptive): {type(e).__name__}")
            continue
        PA2[name] = p
        emit("  " + S87.fmt_prof(p, lb) + f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}")
    flush()

    # ---- ARM B: DEFERRED (lead decision 06:36 PDT); code kept, flag off
    if RUN_ARM_B:
        # ---- ARM B
        emit("\n=== ARM B: line-scoped pool producer LP, 15-quire LOQO ===")
        pz = S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS['ZL3b']}.meta.json")
        folds = S67.folds_of(pz)
        emit(f"folds: {folds} ({len(folds)}); grids {dict(GRID)}; start {START}; sweep order {SWEEP}, <= {MAX_SWEEPS} sweeps")
        jobs = [dict(T=T, Q=Q, ti=ti, fi=fi, pages=None, seg="slot", c3=True) for ti, T in enumerate(TRANSLITS) for fi, Q in enumerate(folds)]
        flush()
        res = run_pool(jobs, "armB")
        emit("per-fold (H = held-out quire replicated to N_TOT; G = all pages generated with the fold's fit; realQ abc = real "
             "held-out quire replicated, flags a b c; C3 +/- order P1 P2 P3 P4 P5 P7, * small fold):")
        fb = {T: folds for T in TRANSLITS}
        calls = fold_rows(res, fb, lb, rw_v, rc_v, emit)
        flush()
        emit("\n=== C2 / C3 (arm B) ===")
        c2T, c3T = {}, {}
        for T in TRANSLITS:
            n_ok = sum(calls[(T, Q)]["ok"] for Q in folds)
            nH = sum(calls[(T, Q)]["H"] for Q in folds); nG = sum(calls[(T, Q)]["G"] for Q in folds)
            n3 = sum(1 for Q in folds if res[(T, Q)]["c3"]["n"] >= 5)
            c2T[T], c3T[T] = n_ok, n3
            comp_fail = Counter()
            for Q in folds:
                for part, fl in (("H", calls[(T, Q)]["fH"]), ("G", calls[(T, Q)]["fG"])):
                    for k, ch in zip("abcd", fl):
                        if ch == "n":
                            comp_fail[f"{part}.{k}"] += 1
            per = {k: sum(res[(T, Q)]["c3"]["holds"][k] for Q in folds) for k in S67.PREDS}
            emit(f"  {T}: LP Voynich-like {n_ok}/{len(folds)} folds (H {nH}, G {nG}); component failures over folds {dict(sorted(comp_fail.items()))}; "
                 f"C3 >= 5/6 on {n3}/{len(folds)} folds; per prediction " + ", ".join(f"{k} {v}/{len(folds)}" for k, v in per.items()))
            ps = [res[(T, Q)]["fit"]["params"] for Q in folds]
            emit(f"     fitted params (min-max, median): " + "; ".join(
                f"{k} {min(p[k] for p in ps)}-{max(p[k] for p in ps)} ({float(np.median([p[k] for p in ps])):g})" for k in KEYS))
            realabc = Counter(calls[(T, Q)]["fR"] for Q in folds)
            emit(f"     V2 real held-out quire replicated, a/b/c flags: {dict(realabc)}")
        C2 = all(c2T[T] >= MIN_C2 for T in TRANSLITS)
        C3 = all(c3T[T] >= MIN_C2 for T in TRANSLITS)
        emit(f"  C2 (>= {MIN_C2}/15 on all three): {C2}  [" + ", ".join(f"{T} {c2T[T]}/15" for T in TRANSLITS) + "]")
        emit(f"  C3 (>= 5/6 on >= {MIN_C2}/15 on all three; secondary): {C3}  [" + ", ".join(f"{T} {c3T[T]}/15" for T in TRANSLITS) + "]")
    else:
        emit("\n=== ARM B: DEFERRED (not run under this stub): producer failed its own planted-instance fixture "
             "(FX1 4/15 after one revision; double-sampling locality bias) ===")

    # ---- calls
    emit("\n=== C1 (arm A, gating texts) ===")
    c1 = OrderedDict()
    for name, p in PA.items():
        ok, comp, f = flags(p, lb)
        tag = "" if p["gating"] else "  [UNMATCHED: descriptive, not in C1]"
        if p["gating"]:
            c1[name] = ok
        emit(f"  C1 {name:24s} {p['cls']}  {'VOYNICH-LIKE' if ok else 'no':12s} fails: {', '.join(k for k, v in comp.items() if not v) or '-'}{tag}")
    for cls in ("R", "T", "N"):
        n = [x for x in c1 if PA[x]["cls"] == cls]
        emit(f"  class {cls}: {sum(c1[x] for x in n)}/{len(n)} gating texts Voynich-like")
    c2 = OrderedDict((cls, sum(c1[x] for x in c1 if PA[x]["cls"] == cls)) for cls in ("R", "T", "N"))
    emit("  C2 Voynich-like gating texts per class: " + "; ".join(
        f"{cls} {c2[cls]}/{sum(1 for x in c1 if PA[x]['cls'] == cls)}" for cls in c2))

    # ---- reading (arm A only)
    hits = [n for n, ok in c1.items() if ok]
    if hits:
        reading = "a real genre with line-level repetition reproduces the core layer: " + ", ".join(f"{n} ({PA[n]['cls']})" for n in hits)
    else:
        an = min(c1, key=lambda n: PA[n]["D"])
        af = [k for k, v in S87.c1(PA[an], lb)[1].items() if not v]
        reading = f"no line-repetition genre reproduces the core layer; closest text {an} ({PA[an]['cls']}, D {PA[an]['D']:.2f}), failing: {', '.join(af)}"
    if v1:
        reading += f" [target self-check failed: {', '.join(v1)}]"
    emit(f"\nVERDICT: {reading}")

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "armA_profiles.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "cores", "class", "gating", "tokens", "types", "o100", "p100", "o200", "p200", "Rw1", "pRw1", "Rc1",
                    "loc", "loc_lo", "loc_hi", "C1", "D"])
        for tag, PP in (("primary", PA), ("stem", PA2)):
            for name, p in PP.items():
                o, r, l = p["order"], p["rep"], p["loc"]
                w.writerow([name, tag, PA[name]["cls"], PA[name]["gating"], p["tokens"], p["types"], f"{o[100]['mm']:.6f}", f"{o[100]['p']:.4f}",
                            f"{o[200]['mm']:.6f}", f"{o[200]['p']:.4f}", f"{r[1]['Rw']:.4f}", f"{r[1]['pw']:.4f}", f"{r[1]['Rc']:.4f}",
                            f"{l['ratio']:.4f}", f"{l['lo']:.4f}", f"{l['hi']:.4f}", S87.c1(p, lb)[0], f"{S87.distance(p, lb, rw_v, rc_v)[0]:.3f}"])
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(loc_band=lb, order_band=S87.ORDER_BAND, rw_v=rw_v, rc_v=rc_v, C1=c1, C2=c2,
                                                        arm_b="deferred", verdict=reading), indent=1), encoding="utf-8", newline="\n")
    emit(f"\nsidecars: {RUN_DIR.relative_to(ROOT).as_posix()}/armA_profiles.csv, {RUN_DIR.relative_to(ROOT).as_posix()}/calls.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


if __name__ == "__main__":
    main()
