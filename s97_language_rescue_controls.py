"""S97 (Phase 6.1; decides H-01 vs H-16/H-17): can a natural language written 'the hard way' reproduce what plainly
written European controls cannot -- the F-40 four-part core signature plus the s67 slot battery?

WHY: H-01's exclusion (F-40, s87 amendment 1) used only plain alphabetic European texts.  H-17 (verbose orthography /
heavy abbreviation / misleading word boundaries) and H-16 (practitioner notation / shorthand) are live and untested
(FINDINGS-GRAPH P-29; red-team RT-1/RT-2).  s18 found abbreviated Latin moves CHARWIN to about -0.15.

TARGET (s87 amendment 1, c-432; S87.c1 rule, imported):
 (a) MM order excess at K=100 AND K=200 inside the frozen ORDER bands K100 [+0.012321,+0.092252],
     K200 [-0.003465,+0.086474] (S87.ORDER_BAND);
 (b) R_within(1) > 1 with permutation p < 0.05;  (c) R_cross(1) < R_within(1);
 (d) quire-locality ratio inside the LOCALITY band (s87 rule: union over the three Voynich transliterations of
     ratio +- 2 half-widths of the 15-block bootstrap; recomputed here from VOY_ZL3b/RF1b/IT2a SlotSegmenter cores
     on the N_TOT cut with s87's seeds; s87 amendment 1 gave [0.9074, 1.0499]).
 Pipeline = s87's, imported (S87.layout, S87.flatten, S87.repetition, S87.locality, S87.order_excess,
 S80.prepare / matched_set / fit_freq): N_TOT = 22,500 tokens, 15 blocks of 1,500, order N_match = 4,731 (s87
 amendment 1, frozen as in s91), 1,000 order shuffles, 1,000 R shuffles, 500 locality permutations, 2,000 bootstraps.
 If a text's G1 held-out set is < 4,731 tokens the order statistic uses all of it and the row is flagged (still
 gating).

SEGMENTERS ("all applicable segmenters"): identity (word = core; s87 primary for natural texts), SlotSegmenter
 (s87 secondary / Voynich convention), Seg_Affix2 (s77, independent onset/coda stripper; s88/s96 segmenter family).
 Zattera (s76) is NOT applicable to non-EVA texts (its glyph-slot grammar parses no Latin/Hebrew/Arabic word, so it
 returns the whole word = identity) and is not run.  A segmenter is applicable to a text iff it yields a non-empty
 core for >= 50 % of the text's tokens (MIN_CORE_SHARE).  Voynich target profiles: SlotSegmenter only (s87).
SLOT BATTERY (s67's six predictions P1 P2 P3 P4 P5 P7, s67/s57 code imported: S57.Measured, S57.draws_for with
 N_DRAW = S67.N_DRAW = 300, S67.score_model; SlotSegmenter inside Measured, as in s67/s91 -- the battery is
 SlotSegmenter-defined and is computed once per text).  Pairing: the control text's N_TOT cut, laid out as above, is
 split by s87 block b (b = 0..14); block b is the held-out "quire", the other 14 blocks the training pages.  It is
 scored as the "generated" text against the REAL Voynich fold folds[b] (S67.folds_of(ZL3b): the 15 quires with >= 4
 ZL3b pages, in that order) of transliteration T (training = the other quires of T, S67.load_pages).  Real draws
 seed S67.SEED + 1000 ti + 10 fi (s91's); control draws seed SEED + 1000 xi + 10 b (xi = text index), once per block
 and reused for every T.  Fold holds iff >= 4 of the 6 predictions hold (BAT_MIN_HOLD).  Battery holds on T iff
 >= 8/15 folds hold (BAT_MIN_FOLDS; s91's bar).  Battery holds iff it holds on each of ZL3b, RF1b, IT2a.

CONTROLS (each through the identical pipeline; real lines where the source has them):
 C1_cremma_marks_la  CREMMA Latin prose manuscripts (s87's 12 prose MSS), REAL manuscript lines, `_marks` family:
                     abbreviation signs and letters kept as written (data/controls_realline/cremma_all_marks.meta.json).
                     Each glyph unit (base code point + following combining marks, the manifest's rule) is mapped to one
                     code point (unit with marks -> a plane-15 private-use code point, bijective, assigned in order of
                     first appearance) so segmenters and CHARWIN count glyph units, not detached marks.
 C2a_hebrew_abjad    Hebrew Torah, unpointed consonantal text (data/controls/hebrew_torah.txt), verse lines as lines
                     ('##' book headers dropped), S87.tokens_norm.  Abjad text is ON DISK, so no derived abjad is made.
 C2b_arabic_abjad    Qur'an, Arabic script without vowel signs (data/controls/arabic_quran.txt), verse lines as lines,
                     S87.tokens_norm (NFD + strip Mn also strips hamza/madda marks: a consonant-skeleton reading).
 C3a_verbose_la      VERBOSE SYLLABIC RE-SPELLING of the CREMMA prose base family (real manuscript lines; the same
                     source lines as s87's P_cremma_prose_la): each word -> syllables (nucleus = maximal run of
                     a e i o u y; between nuclei 0-1 consonants go to the next syllable, >= 2: the first is a coda);
                     syllable types ranked by token frequency (ties by string) get a fixed glyph group from the
                     14-glyph inventory "abcdefghiklmno": ranks 0-153 two glyphs (leader from "abcdefghikl"),
                     ranks 154-741 three glyphs (leader from "mno"), rarer syllables -> a three-glyph group chosen by
                     crc32 (lossy homophony).  Line-held spelling variants: per line one prefix marker from
                     ["", "x", "z", "xz"] and one suffix marker from ["", "w", "j", "wj"] (independent uniform draws,
                     rng default_rng([SEED, 31, line index]) for the prefix and [SEED, 37, line index] for the suffix);
                     word = prefix marker + syllable groups + suffix marker.
 C3b_verbose_it      the same re-spelling (syllable ranks from its own text) of Dante (s17 real verse lines,
                     data/controls_realline/italian_dante.meta.json).
 C4_sigla_disp_la    SHORTHAND / SIGLA, CONSTRUCTED (no sigla-written pharmacy transcription is on disk): the
                     Dispensarium Nicolai antidotary (s87's L_dispensarium_la, OCR, S87.load_dispensarium; no line
                     structure -> ZL3b line lengths as in s87) with (i) fixed pharmacy sigla by stem (recip->rx,
                     drachm->dr, unci->oz, scrupul->sc, libr->lb, manipul->mp, pugill->pg, misce->mi, fiat->ft,
                     pulver/pulvis->pv; each stem also with s->f for the OCR long s; 'ana'->aa) and (ii) every other
                     word among the 400 most frequent types of length >= 4 that is not a Latin function word
                     (LAT_FUNC) -> siglum = first two letters + last letter (lossy, collisions kept).  Which words
                     are 'ingredient and operation' words is approximated by 'frequent content word'.
 Comparators (descriptive, not in the call): REF_cremma_prose_base (plain-written CREMMA prose, real lines; = s87's
 P_cremma_prose_la source).
GATE (must behave before the controls are read; all three required):
 PC1 planted producer: s91's LP91 at its fixture parameters S91.PLANTED (conc 300, alpha 8, rho 0.03, lam 0.45,
     pen 0.8), lexicon = all ZL3b SlotSegmenter core counts, bigram table = ZL3b within-line core pairs, layout =
     ZL3b pages/quires/line lengths, seeds SEED+1..3; its emitted cores scored with identity (it emits cores; no
     affix layer, so the battery is not applicable: s91 C2 showed LP91 words reach 0-2/6).  PASS iff S87.c1 holds
     on >= 2 of 3 seeds.
 PC2 the Voynich text as a control: IT2a words, real pages, through the control path (layout, blocks, battery).
     PASS iff S87.c1 on SlotSegmenter cores AND battery vs IT2a's own real folds holds (>= 4/6 on >= 8/15 folds).
 NC  plain Latin prose: Augustine (S87.load_control('latin_augustine.txt'); ZL3b line lengths).  PASS iff its
     full call (below) is False.
PRE-REGISTERED CALLS
 FULL(X) = [for EVERY applicable segmenter: S87.c1 all four parts True] AND [battery holds on ZL3b, RF1b and IT2a].
 GATE = PC1 and PC2 and NC.
 CALL_REOPEN_H17_H16 = GATE and (FULL(X) for ANY X in {C1, C2a, C2b, C3a, C3b, C4}).  Printed "= True/False".
 READING: CALL True -> "H-17/H-16 reopened: <controls>"; GATE True and CALL False -> "no hard-way control reaches
   the signature + battery: F-40 gains an external-genre line"; GATE False -> "uninformative: gate failed (<which>)"
   (CALL printed False).
 Descriptive per control: which signature parts fail per segmenter, D (s87 distance), battery per T (folds >= 4/6,
   per-prediction hold counts, median holds).
FIXTURE (--fx97; synthetic; reads no real data; writes runs/s97/fixture_<stamp>.txt only):
 world = S91.fx_world (1,500 cores, Zipf lexicon, planted bigrams, 15 quires x 12 pages x 20 lines).
 FX_A, FX_B = LP91 at PLANTED (seeds 1, 2); FX_prose = Markov chain over the same names (p 0.5 fixed successor,
 else Zipf).  Words = core wrapped by a line-held prefix ["", "q", "qo", "o"] and a core-keyed suffix
 ["", "y", "dy", "n"] (crc32).  Bands from FX_A (S87.order_band_from on an s80-style interval; S87.loc_band_from).
 [REVISION 1: bands = union over FX_A1..A3 (LP91 PLANTED seeds 1, 3, 5), as the real bands are a union over three
 transliterations; FX_B = seed 2.]
 FX1 FX_B Voynich-like (identity cores, S87.c1).  FX2 FX_prose not Voynich-like.  FX3 transforms: verbose
 re-spelling of a pseudo-Latin text is injective on word types for >= 99 % of types (variant fixed), markers are
 constant within every line, sigla replace > 0 tokens, glyph-unit map is a bijection on a mark-bearing sample.
 FX4 battery path: FX_B words (control path: layout, blocks) scored against FX_A words (reference quires) hold
 [REVISION 1] >= 3 of the 4 reference-relative predictions (P1 P2 P3 P7) on >= 8/15 folds (P4 and P5 use absolute
 Voynich thresholds -- s15 jsd width, CHARWIN > 0 -- that a synthetic world cannot be expected to meet; the real
 PC2 gate keeps the full >= 4/6 bar).  FX5 (not gating) FX_prose words' battery count; segmenter profiles of FX_B words.
DESIGN REVISIONS (at most two, pre-freeze):
 REVISION 1 (after fixture run 1, 12:26 PDT: FAIL; FX1 FX_B o200 +0.003 below a band built from the single target
   FX_A [+0.0067,+0.0823] -- a one-text 80 %-subsample band omits realisation noise (L-171); FX4 FX_B 1/15 folds
   >= 4/6 because P4 0/15 and P5 0/15 (absolute Voynich thresholds) while P1 11, P2 10, P3 6, P7 13; FX2, FX3
   PASS; prose battery 0/15).  Changes: fixture bands from three planted targets; FX4 on the four reference-relative
   predictions.  Nothing in the real-data path changed.
FIXTURE OUTCOME BEFORE THE FREEZE (runs/s97/fixture_*.txt, run 2, 12:28:20 PDT): PASS.  FX1 FX_B C1 YYYY (o100 +0.016,
 o200 +0.003 in [-0.0039,+0.0950]); FX2 prose nnnn; FX3 PASS; FX4 10/15 (prose 0/15).  Descriptive: FX_B words with a
 line-held prefix are Voynich-like under slot and affix2 cores; under identity locality fails (0.933).
Disclosed pre-freeze looks at real data: CREMMA prose marks-family token count (42,647); first lines of hebrew_torah.txt
 and arabic_quran.txt (format: '##' headers, unpointed, one verse per line); free RAM.  No statistic on any real text.
COMPUTE: profiles on the GPU (torch cuda) in the main process; battery Measured objects in 2 worker processes
 (spawn), BelowNormal priority, OMP threads 1; free RAM >= 4 GB checked before each pool (else stop).
Writes ONLY results_s97.txt and runs/s97/ (fixture: runs/s97/fixture_<stamp>.txt).
Run: python -I s97_language_rescue_controls.py    Fixture: --fx97    Stub helper: --list-locals
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import unicodedata  # noqa: E402
import zlib  # noqa: E402
from collections import Counter, OrderedDict  # noqa: E402
from datetime import datetime  # noqa: E402
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
import s91_line_pool_producer_loqo as S91  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s77_deconfounded_scribe_and_comma_ablation_loqo as S77  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

S80 = S87.S80
S57 = S67.S57

SELF = ROOT / "s97_language_rescue_controls.py"
STUB = ROOT / "s97_language_rescue_controls.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s97"
FIXTURE = "--fx97" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
OUT = (RUN_DIR / f"fixture_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt") if FIXTURE else ROOT / "results_s97.txt"
SEED = 20261097
N_TOT, NB = S87.N_TOT, S87.NB
N_MATCH = 4731
MIN_CORE_SHARE = 0.5
BAT_MIN_HOLD = 4
BAT_MIN_FOLDS = 8
PC1_MIN = 2
N_WORKERS = 2
MIN_FREE_GB = 4.0
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
S87_EXPECT = {"ZL3b": (0.034, 1.180, 0.977), "RF1b": (0.020, 1.193, 0.977), "IT2a": (0.030, 1.217, 0.979)}
CREMMA_PROSE = list(S87.CREMMA_PROSE)
DATA_FILES = ([f"data/translit/{f}.meta.json" for f in TRANSLITS.values()]
              + ["data/controls_realline/cremma_all.meta.json", "data/controls_realline/cremma_all_marks.meta.json",
                 "data/controls_realline/italian_dante.meta.json", "data/controls/hebrew_torah.txt",
                 "data/controls/arabic_quran.txt", "data/controls/latin_augustine.txt",
                 "data/external/genre-s87/BIUSante_pharma_res012103_djvu.txt"])
CODE_ALPH = "abcdefghiklmno"
SHORT_LEAD = "abcdefghikl"
LONG_LEAD = "mno"
PFX_MARK = ["", "x", "z", "xz"]
SFX_MARK = ["", "w", "j", "wj"]
VOWELS = set("aeiouy")
SIGLA_STEMS = [("recip", "rx"), ("drachm", "dr"), ("unci", "oz"), ("scrupul", "sc"), ("libr", "lb"), ("manipul", "mp"),
               ("pugill", "pg"), ("misce", "mi"), ("fiat", "ft"), ("pulver", "pv"), ("pulvis", "pv")]
N_SIGLA_TOP = 400
LAT_FUNC = set("""a ab ac ad atque aut autem cum de e et etiam ex hic haec hoc huius eius ea eo eam eorum earum eis id in
inter is non nec neque per post pro quae qui quod quam quo quia sed si sic sub super tamen tum ut vel vero est sunt sit
esse erit fit ita item enim nam nisi ubi unde ille illa illud ipse ipsa ipsum quoque quibus quorum cuius sive seu ergo
igitur iam nunc tunc semper omnis omnia omnibus quando quidem""".split())
SEGS = OrderedDict([("identity", S80.identity_seg_factory), ("slot", SlotSegmenter), ("affix2", S77.SegAffix2)])
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


# ======================================================================= transforms
def glyph_units(w):
    units, cur = [], ""
    for ch in w:
        if unicodedata.category(ch) == "Mn" and cur:
            cur += ch
        else:
            if cur:
                units.append(cur)
            cur = ch
    if cur:
        units.append(cur)
    return units


class UnitMap:
    """glyph unit with marks -> one plane-15 private-use code point (bijective, first-appearance order)."""

    def __init__(self):
        self.fwd, self.inv = {}, {}

    def word(self, w):
        out = []
        for u in glyph_units(w):
            if len(u) == 1:
                out.append(u)
                continue
            c = self.fwd.get(u)
            if c is None:
                c = chr(0xF0000 + len(self.fwd))
                self.fwd[u] = c; self.inv[c] = u
            out.append(c)
        return "".join(out)


def syllables(w):
    idx = [i for i, ch in enumerate(w) if ch in VOWELS]
    if not idx:
        return [w]
    runs, s, e = [], idx[0], idx[0]
    for i in idx[1:]:
        if i == e + 1:
            e = i
        else:
            runs.append((s, e)); s = e = i
    runs.append((s, e))
    cuts = []
    for (s1, e1), (s2, e2) in zip(runs, runs[1:]):
        nc = s2 - e1 - 1
        cuts.append(e1 + 1 if nc <= 1 else e1 + 2)
    out, prev = [], 0
    for c in cuts:
        out.append(w[prev:c]); prev = c
    out.append(w[prev:])
    return out


def syllable_codes(lines):
    cnt = Counter(s for ln in lines for w in ln for s in syllables(w))
    ranked = sorted(cnt, key=lambda s: (-cnt[s], s))
    n_short = len(SHORT_LEAD) * len(CODE_ALPH)
    n_long = len(LONG_LEAD) * len(CODE_ALPH) ** 2
    A = len(CODE_ALPH)

    def long_code(r):
        return LONG_LEAD[r // (A * A)] + CODE_ALPH[(r // A) % A] + CODE_ALPH[r % A]
    code = {}
    for r, s in enumerate(ranked):
        if r < n_short:
            code[s] = SHORT_LEAD[r // A] + CODE_ALPH[r % A]
        elif r < n_short + n_long:
            code[s] = long_code(r - n_short)
        else:
            code[s] = long_code(zlib.crc32(s.encode("utf-8")) % n_long)
    return code, len(ranked)


def verbose_lines(lines, seed):
    code, n_types = syllable_codes(lines)
    out = []
    for li, ln in enumerate(lines):
        pv = int(np.random.default_rng([seed, 31, li]).integers(len(PFX_MARK)))
        sv = int(np.random.default_rng([seed, 37, li]).integers(len(SFX_MARK)))
        out.append([PFX_MARK[pv] + "".join(code[s] for s in syllables(w)) + SFX_MARK[sv] for w in ln])
    return out, n_types


def sigla_map(tokens):
    fixed = {}
    stems = []
    for st, sg in SIGLA_STEMS:
        stems.append((st, sg))
        if "s" in st:
            stems.append((st.replace("s", "f"), sg))
    cnt = Counter(tokens)
    mp = {}
    for w in cnt:
        if w == "ana":
            mp[w] = "aa"; continue
        for st, sg in stems:
            if w.startswith(st):
                mp[w] = sg; fixed[w] = sg
                break
    top = [w for w, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])) if len(w) >= 4 and w not in LAT_FUNC
           and w not in mp][:N_SIGLA_TOP]
    for w in top:
        mp[w] = w[:2] + w[-1]
    return mp, len(fixed)


# ======================================================================= profile with any segmenter factory
def profile_g(name, pages, segf, n_match, seed):
    """S87.profile generalised to a segmenter factory (identical statistics and calls)."""
    t = time.time()
    toks = [w for _, ls in pages for ln in ls for w in ln]
    seg = segf(toks)
    cache = {}

    def core_of(w):
        c = cache.get(w)
        if c is None:
            c = cache[w] = seg.segment(w)[1]
        return c
    cores, pg, lid, blk, ids = S87.flatten(pages, core_of)
    share = float((cores >= 0).mean())
    rep = S87.repetition(cores, pg, lid, S87.N_SHUF_R, seed)
    loc = S87.locality(cores, blk, S87.N_PERM_LOC, S87.N_BOOT, seed + 2)
    T = S80.prepare(name, "S97", pages, segf)
    mset = S80.matched_set(T, n_match)
    oc, olid, opg = S80.arrays(mset)
    labs = [S80.apply_map(oc, S80.fit_freq(T["tr_counts"], K)) for K in S87.KS]
    ordr = S87.order_excess(labs, olid, S87.N_SHUF_ORDER, seed + 3)
    return dict(name=name, tokens=len(toks), pages=len(pages), lines=int(lid.max()) + 1, types=len(ids),
                empty=int((cores < 0).sum()), core_share=share, te_tok=T["te_tok"], matched_tokens=len(oc),
                order={K: dict(mm=o[0], p=o[1], plug=o[2]) for K, o in zip(S87.KS, ordr)}, rep=rep, loc=loc,
                blocks=int(blk.max()) + 1, secs=time.time() - t)


def flags(p, lb):
    ok, comp = S87.c1(p, lb)
    return ok, comp, "".join("Y" if v else "n" for v in comp.values())


def fmt(p, lb, extra=""):
    o, r, l = p["order"], p["rep"], p["loc"]
    ok, comp, fl = flags(p, lb)
    um = "" if p["te_tok"] >= N_MATCH else f" [order n={p['matched_tokens']}<{N_MATCH}]"
    return (f"{p['name']:34s} tok {p['tokens']:6d} ty {p['types']:5d} core% {100 * p['core_share']:5.1f} | o100 {o[100]['mm']:+.3f}"
            f"(p{o[100]['p']:.3f}) o200 {o[200]['mm']:+.3f} | Rw1 {r[1]['Rw']:.3f}(p{r[1]['pw']:.3f}) Rc1 {r[1]['Rc']:.3f} | "
            f"loc {l['ratio']:.3f}[{l['lo']:.3f},{l['hi']:.3f}] | C1 {fl} {'VOYNICH-LIKE' if ok else '-'}{um}{extra}")


# ======================================================================= battery
def worker_init():
    S87.below_normal()
    try:
        torch.set_num_threads(1)
    except Exception:  # noqa: BLE001
        pass


def measure_job(job):
    t = time.time()
    S57.N_DRAW = S67.N_DRAW
    m = S57.Measured(job["name"], job["train"], job["test"])
    dr = S57.draws_for([m], job["seed"])
    return job["key"], m, dr, time.time() - t


def run_pool(jobs, tag):
    import multiprocessing as mp
    fg = S91.free_gb()
    emit(f"  [{tag}] free RAM {fg:.1f} GB (need >= {MIN_FREE_GB}); {len(jobs)} Measured jobs on {N_WORKERS} workers")
    if not (fg >= MIN_FREE_GB):
        emit(f"STOP: free RAM {fg:.1f} GB < {MIN_FREE_GB} GB")
        flush()
        raise SystemExit(2)
    out = {}
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        for i, (k, m, dr, s) in enumerate(pool.imap_unordered(measure_job, jobs)):
            out[k] = (m, dr)
            if (i + 1) % 10 == 0 or i + 1 == len(jobs):
                print(f"  [{tag} {time.time() - t0:.0f}s] {i + 1}/{len(jobs)} done (last {k} {s:.0f}s)", flush=True)
    return out


def block_split(pages):
    """control pages (s87 layout) -> list over blocks b of (train pages, test pages), s87 block rule."""
    ntot = sum(len(ln) for _, ls in pages for ln in ls)
    tok, blk = 0, []
    for _, ls in pages:
        blk.append(min(NB - 1, tok * NB // ntot))
        tok += sum(len(ln) for ln in ls)
    out = []
    for b in range(NB):
        tr = [(p, ls) for (p, ls), bb in zip(pages, blk) if bb != b]
        te = [(p, ls) for (p, ls), bb in zip(pages, blk) if bb == b]
        out.append((tr, te))
    return out


def ref_jobs(ref_pages_by_T, folds):
    jobs = []
    for ti, (T, pages) in enumerate(ref_pages_by_T.items()):
        for fi, Q in enumerate(folds):
            tr = [(p, ls) for p, q, ls in pages if q != Q]
            te = [(p, ls) for p, q, ls in pages if q == Q]
            jobs.append(dict(key=("REF", T, fi), name=f"{T} {Q} real", train=tr, test=te, seed=S67.SEED + 1000 * ti + 10 * fi))
    return jobs


def ctl_jobs(name, xi, pages):
    jobs = []
    for b, (tr, te) in enumerate(block_split(pages)):
        jobs.append(dict(key=("CTL", name, b), name=f"{name} b{b}", train=tr, test=te, seed=SEED + 1000 * xi + 10 * b))
    return jobs


def battery_score(name, Ts, M, ref_pages_by_T, folds, ctl_pages):
    splits = block_split(ctl_pages)
    res = OrderedDict()
    for T in Ts:
        rows = []
        pages = ref_pages_by_T[T]
        for b, Q in enumerate(folds):
            rm, rdr = M[("REF", T, b)]
            cm, cdr = M[("CTL", name, b)]
            real_te = [ls for p, q, ls in pages if q == Q]
            cells, gen_pt, rt, small = S67.score_model(rm, rm.point(), rdr, [cm], cdr, rm.n_test,
                                                       [[ls for _, ls in splits[b][1]]], real_te)
            holds = {k: bool(cells[k][0]) for k in S67.PREDS}
            rows.append(dict(Q=Q, n=sum(holds.values()), holds=holds, small=small, type_ratio=rt,
                             gen=dict(P1=gen_pt["P1"], P2=gen_pt["P2"], P3=gen_pt["P3"], P4=gen_pt["P4"], P5=gen_pt["P5"])))
        nf = sum(1 for r in rows if r["n"] >= BAT_MIN_HOLD)
        res[T] = dict(rows=rows, folds_ok=nf, holds=nf >= BAT_MIN_FOLDS,
                      per_pred={k: sum(r["holds"][k] for r in rows) for k in S67.PREDS},
                      median_n=float(np.median([r["n"] for r in rows])))
    return res


def bat_line(T, r):
    return (f"{T}: folds >=4/6 {r['folds_ok']:2d}/15 {'HOLDS' if r['holds'] else 'fails'}; median {r['median_n']:.1f}/6; per prediction "
            + " ".join(f"{k} {r['per_pred'][k]:2d}" for k in S67.PREDS)
            + " | per fold " + " ".join(f"{x['n']}" for x in r["rows"]))


# ======================================================================= fixture
FX_PRE = ["", "q", "qo", "o"]
FX_SUF = ["", "y", "dy", "n"]


def fx_wrap(core_pages, seed):
    out = []
    li = 0
    for pid, ls in core_pages:
        L = []
        for ln in ls:
            pv = int(np.random.default_rng([seed, li]).integers(len(FX_PRE))); li += 1
            L.append([FX_PRE[pv] + c + FX_SUF[zlib.crc32(c.encode()) % len(FX_SUF)] for c in ln])
        out.append((pid, L))
    return out


def fx_prose(names, spec, seed):
    r = np.random.default_rng(seed)
    V = len(names)
    z = 1.0 / np.arange(1, V + 1); z /= z.sum()
    succ = np.random.default_rng(seed + 1).permutation(V)
    cur, pages = 0, []
    for pid, q, lens in spec:
        L = []
        for n in lens:
            ln = []
            for _ in range(n):
                cur = int(succ[cur]) if r.random() < 0.5 else int(r.choice(V, p=z))
                ln.append(names[cur])
            L.append(ln)
        pages.append((pid, L))
    return pages


def pseudo_latin(seed, n_lines=400):
    r = np.random.default_rng(seed)
    on = ["", "b", "c", "d", "f", "l", "m", "n", "p", "r", "s", "t", "qu", "st", "pr"]
    nu = ["a", "e", "i", "o", "u", "ae"]
    co = ["", "", "", "s", "m", "n", "r", "t"]
    lex = sorted({"".join(on[r.integers(len(on))] + nu[r.integers(len(nu))] + co[r.integers(len(co))]
                          for _ in range(int(r.integers(1, 5)))) for _ in range(3000)})
    z = 1.0 / np.arange(1, len(lex) + 1); z /= z.sum()
    return [[lex[i] for i in r.choice(len(lex), size=int(1 + r.poisson(7)), p=z)] for _ in range(n_lines)], lex


def run_fixture():
    emit("S97 FIXTURE (synthetic only; no real data read)")
    emit(f"date: {S87.clock()}  device: {S87.DEV}; below_normal={S87.below_normal()}")
    emit(f"s97 sha256={sha256(SELF)}  stub_match={stub_match()}")
    names, glob, B, spec = S91.fx_world()
    prod = S91.LP91(glob, B)
    prod.set_params(S91.PLANTED)
    cA = prod.text(spec, 1); cB = prod.text(spec, 2)
    pr = fx_prose(names, spec, 4)
    cutA, cutB, cutP = S91.cut(cA), S91.cut(cB), S91.cut(pr)
    tgts = [S87.profile(f"FX_A{j + 1}", S91.cut(prod.text(spec, s)), "id", N_MATCH, SEED + 50 * j, interval=True)
            for j, s in enumerate((1, 3, 5))]   # REVISION 1
    tgt = tgts[0]
    saved = S87.ORDER_BAND
    S87.ORDER_BAND = S87.order_band_from(tgts)
    lb = S87.loc_band_from(tgts)
    emit(f"fixture bands from FX_A: K100 [{S87.ORDER_BAND[100][0]:+.4f},{S87.ORDER_BAND[100][1]:+.4f}] K200 "
         f"[{S87.ORDER_BAND[200][0]:+.4f},{S87.ORDER_BAND[200][1]:+.4f}] loc [{lb[0]:.3f},{lb[1]:.3f}]")
    pB = profile_g("FX_B cores/identity", cutB, S80.identity_seg_factory, N_MATCH, SEED + 1)
    pP = profile_g("FX_prose/identity", cutP, S80.identity_seg_factory, N_MATCH, SEED + 2)
    for p in tgts + [pB, pP]:
        p.setdefault("core_share", 1.0)
        emit("  " + fmt(p, lb))
    fx1 = flags(pB, lb)[0]
    fx2 = not flags(pP, lb)[0]
    emit(f"FX1 planted FX_B Voynich-like: {'PASS' if fx1 else 'FAIL'}")
    emit(f"FX2 Markov prose not Voynich-like: {'PASS' if fx2 else 'FAIL'}")
    wA, wB, wP = fx_wrap(cA, 11), fx_wrap(cB, 12), fx_wrap(pr, 13)
    for sn, sf in SEGS.items():
        p = profile_g(f"FX_B words/{sn}", S91.cut(wB), sf, N_MATCH, SEED + 3)
        emit("  [FX5 descriptive] " + fmt(p, lb))
    flush()
    # FX3 transforms
    pl, lex = pseudo_latin(5)
    enc, ntyp = verbose_lines(pl, SEED)
    code, _ = syllable_codes(pl)
    plain_enc = {w: "".join(code[s] for s in syllables(w)) for ln in pl for w in ln}
    inv = Counter(plain_enc.values())
    inj = sum(1 for w, e in plain_enc.items() if inv[e] == 1) / len(plain_enc)
    const = True
    for ln in enc:
        pre = {next((m for m in sorted(PFX_MARK, key=len, reverse=True) if m and e.startswith(m)), "") for e in ln}
        suf = {next((m for m in sorted(SFX_MARK, key=len, reverse=True) if m and e.endswith(m)), "") for e in ln}
        const &= len(pre) <= 1 and len(suf) <= 1
    toks = [w for ln in pl for w in ln] + ["recipe", "drachmas", "ana", "fcrupulum"]
    mp, nfix = sigla_map(toks)
    nrep = sum(1 for w in toks if w in mp)
    um = UnitMap()
    sample = ["q̃", "p̄er", "dñs", "abc", "éè"]
    mapped = [um.word(w) for w in sample]
    back = ["".join(um.inv.get(ch, ch) for ch in m) for m in mapped]
    bij = back == sample and len(set(um.fwd.values())) == len(um.fwd)
    fx3 = inj >= 0.99 and const and nrep > 0 and nfix >= 3 and bij
    emit(f"FX3 transforms: verbose injective share {inj:.4f} ({len(plain_enc)} types, {ntyp} syllable types); markers line-constant {const}; "
         f"sigla replaced {nrep} tokens ({nfix} fixed-stem types); unit map bijective {bij} -> {'PASS' if fx3 else 'FAIL'}")
    flush()
    # FX4 battery path
    ref = OrderedDict([("FXA", [(pid, q, ls) for (pid, q, _), (_, ls) in zip(spec, wA)])])
    folds = sorted({q for _, q, _ in spec})
    cB_pages = S91.cut(wB); cP_pages = S91.cut(wP)
    jobs = ref_jobs(ref, folds) + ctl_jobs("FX_B", 1, cB_pages) + ctl_jobs("FX_prose", 2, cP_pages)
    M = run_pool(jobs, "fixture battery")
    bB = battery_score("FX_B", ["FXA"], M, ref, folds, cB_pages)["FXA"]
    bP = battery_score("FX_prose", ["FXA"], M, ref, folds, cP_pages)["FXA"]
    emit("  FX_B     " + bat_line("FXA", bB))
    emit("  FX_prose " + bat_line("FXA", bP))
    rel = ("P1", "P2", "P3", "P7")   # REVISION 1
    nrelB = sum(1 for x in bB["rows"] if sum(x["holds"][k] for k in rel) >= 3)
    nrelP = sum(1 for x in bP["rows"] if sum(x["holds"][k] for k in rel) >= 3)
    fx4 = nrelB >= BAT_MIN_FOLDS
    emit(f"FX4 FX_B >= 3/4 reference-relative (P1 P2 P3 P7) on {nrelB}/15 folds (need >= {BAT_MIN_FOLDS}); prose {nrelP}/15: {'PASS' if fx4 else 'FAIL'}; "
         f"FX5 prose (descriptive) {bP['folds_ok']}/15")
    S87.ORDER_BAND = saved
    emit(f"FIXTURE {'PASS' if (fx1 and fx2 and fx3 and fx4) else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


# ======================================================================= real texts
def lines_txt(path):
    out = []
    for ln in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.strip() or ln.startswith("##"):
            continue
        t = S87.tokens_norm(ln)
        if t:
            out.append(t)
    return out


def meta_lines_marks():
    um = UnitMap()
    lines = S87.meta_lines(ROOT / "data" / "controls_realline" / "cremma_all_marks.meta.json", set(CREMMA_PROSE))
    return [[um.word(w) for w in ln] for ln in lines], um


def main():
    if LIST_LOCALS:
        for m in stub_files():
            print(m)
        return
    if FIXTURE:
        run_fixture()
        return
    emit("S97: natural language written the hard way vs the F-40 core signature + s67 slot battery (pre-registered in the docstring)")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; BelowNormal set={S87.below_normal()}; battery workers {N_WORKERS}")
    emit(f"s97_language_rescue_controls.py sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH}; order/R shuffles {S87.N_SHUF_ORDER}/{S87.N_SHUF_R}; locality perms {S87.N_PERM_LOC}, "
         f"boot {S87.N_BOOT}; battery N_DRAW {S67.N_DRAW}, fold >= {BAT_MIN_HOLD}/6, >= {BAT_MIN_FOLDS}/15 folds per T; "
         f"MIN_CORE_SHARE {MIN_CORE_SHARE}; seed {SEED}")
    flush()

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    def lay_lines(lines):
        return S87.layout(lines, True, None, line_lens, page_nl)

    def lay_tokens(toks):
        return S87.layout(toks, False, None, line_lens, page_nl)

    # ---- Voynich target
    emit("\n=== Voynich target (SlotSegmenter cores, s87 seeds) ===")
    VOY = OrderedDict()
    for i, T in enumerate(TRANSLITS):
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        pages = S87.layout(None, True, P, line_lens, page_nl)
        VOY[T] = (pages, profile_g(f"VOY_{T}", pages, SlotSegmenter, N_MATCH, S87.SEED + 100 * i))
    lb = S87.loc_band_from([v[1] for v in VOY.values()])
    emit(f"LOCALITY band: [{lb[0]:.4f}, {lb[1]:.4f}] (s87 amendment 1: [0.9074, 1.0499])")
    rw_v = float(np.mean([v[1]["rep"][1]["Rw"] for v in VOY.values()])); rc_v = float(np.mean([v[1]["rep"][1]["Rc"] for v in VOY.values()]))
    for T, (_, p) in VOY.items():
        e = S87_EXPECT[T]
        same = (round(p["order"][100]["mm"], 3) == e[0] and round(p["rep"][1]["Rw"], 3) == e[1] and round(p["loc"]["ratio"], 3) == e[2])
        emit("  " + fmt(p, lb, f" | V2 reproduces s87 amend1 {e}: {same}"))
    flush()

    # ---- texts
    emit("\n=== building texts ===")
    cremma_base = S87.meta_lines(ROOT / "data" / "controls_realline" / "cremma_all.meta.json", set(CREMMA_PROSE))
    marks, um = meta_lines_marks()
    heb = lines_txt(ROOT / "data" / "controls" / "hebrew_torah.txt")
    ara = lines_txt(ROOT / "data" / "controls" / "arabic_quran.txt")
    dante = S87.meta_lines(ROOT / "data" / "controls_realline" / "italian_dante.meta.json")
    # verbose re-spelling: syllable ranks from the N_TOT-cut source lines (the lines that are scored)
    cb_cut = [ln for _, ls in lay_lines(cremma_base) for ln in ls]
    dn_cut = [ln for _, ls in lay_lines(dante) for ln in ls]
    v_la, nsy_la = verbose_lines(cb_cut, SEED + 1)
    v_it, nsy_it = verbose_lines(dn_cut, SEED + 2)
    disp = S87.load_dispensarium()
    smap, nfix = sigla_map(disp[:N_TOT])
    sig = [smap.get(w, w) for w in disp]
    aug = S87.load_control("latin_augustine.txt")
    nrep = sum(1 for w in disp[:N_TOT] if w in smap)
    emit(f"  C1 marks: {len(um.fwd)} mark-bearing glyph units mapped to single code points")
    emit(f"  C3a syllable types {nsy_la}; C3b syllable types {nsy_it}")
    emit(f"  C4 sigla: {len(smap)} types mapped ({nfix} by fixed pharmacy stems); {nrep}/{N_TOT} tokens replaced")
    TEXTS = OrderedDict()   # name -> (role, pages, segs, Ts, label)
    allT = list(TRANSLITS)
    TEXTS["PC2_VOY_IT2a_as_control"] = ("gate", VOY["IT2a"][0], ["slot"], ["IT2a"], "IT2a words, real pages, through the control path")
    TEXTS["NC_augustine_la"] = ("gate", lay_tokens(aug), list(SEGS), allT, "plain Latin prose (Augustine), ZL3b line lengths")
    TEXTS["REF_cremma_prose_base"] = ("descriptive", lay_lines(cremma_base), list(SEGS), allT, "CREMMA prose, plain (base) family, real lines")
    TEXTS["C1_cremma_marks_la"] = ("control", lay_lines(marks), list(SEGS), allT, "CREMMA prose, abbreviations kept (marks family), real lines")
    TEXTS["C2a_hebrew_abjad"] = ("control", lay_lines(heb), list(SEGS), allT, "Hebrew Torah unpointed, verse lines")
    TEXTS["C2b_arabic_abjad"] = ("control", lay_lines(ara), list(SEGS), allT, "Qur'an Arabic, no vowel signs, verse lines")
    TEXTS["C3a_verbose_la"] = ("control", lay_lines(v_la), list(SEGS), allT, "verbose syllabic re-spelling of CREMMA prose, line-held variants, real lines")
    TEXTS["C3b_verbose_it"] = ("control", lay_lines(v_it), list(SEGS), allT, "verbose syllabic re-spelling of Dante, line-held variants, real verse lines")
    TEXTS["C4_sigla_disp_la"] = ("control", lay_tokens(sig), list(SEGS), allT, "Dispensarium antidotary with pharmacy sigla (constructed), ZL3b line lengths")
    for n, (role, pages, segs, Ts, lab) in TEXTS.items():
        nt = sum(len(ln) for _, ls in pages for ln in ls)
        emit(f"  {n:26s} {role:11s} tokens {nt:6d} pages {len(pages):4d} lines {sum(len(ls) for _, ls in pages):5d}  {lab}")
        assert nt == N_TOT, f"{n} has {nt} tokens < N_TOT"
    flush()

    # ---- PC1 planted producer
    emit("\n=== GATE PC1: s91 LP91 at PLANTED " + str(S91.PLANTED) + " on ZL3b lexicon/layout (identity on emitted cores) ===")
    zp = S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS['ZL3b']}.meta.json")
    segz = SlotSegmenter([w for _, _, ls in zp for l in ls for w in l])
    cz = {}

    def zcore(w):
        c = cz.get(w)
        if c is None:
            c = cz[w] = segz.segment(w)[1]
        return c
    zcp = [(p, q, [[zcore(w) for w in l] for l in ls]) for p, q, ls in zp]
    glob = Counter(c for _, _, ls in zcp for l in ls for c in l if c != "")
    prod = S91.LP91(glob, S91.bigram_of([(p, [[c for c in l if c != ""] for l in ls]) for p, q, ls in zcp]))
    prod.set_params(S91.PLANTED)
    spec = [(p, q, [len(l) for l in ls]) for p, q, ls in zp]
    pc1 = []
    for s in (1, 2, 3):
        pages = S91.cut(prod.text(spec, SEED + s))
        p = profile_g(f"PC1_LP91_planted_s{s}", pages, S80.identity_seg_factory, N_MATCH, SEED + 10 + s)
        pc1.append(flags(p, lb)[0])
        emit("  " + fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}"))
    PC1 = sum(pc1) >= PC1_MIN
    emit(f"  PC1 Voynich-like on {sum(pc1)}/3 seeds (need >= {PC1_MIN}) -> {'PASS' if PC1 else 'FAIL'}")
    flush()

    # ---- signature profiles
    emit("\n=== signature profiles (C1 flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PR = OrderedDict()
    for xi, (n, (role, pages, segs, Ts, lab)) in enumerate(TEXTS.items()):
        PR[n] = OrderedDict()
        for si, sn in enumerate(segs):
            p = profile_g(f"{n}/{sn}", pages, SEGS[sn], N_MATCH, SEED + 1000 * xi + 100 * si)
            PR[n][sn] = p
            app = p["core_share"] >= MIN_CORE_SHARE
            emit("  " + fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}{'' if app else ' [NOT APPLICABLE: core share < 0.5]'}"))
            flush()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---- battery
    emit("\n=== s67 slot battery (control block b vs real Voynich fold folds[b]) ===")
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    emit(f"  folds ({len(folds)}): {' '.join(folds)}")
    assert len(folds) == NB
    jobs = ref_jobs(ref, folds)
    for xi, (n, (role, pages, segs, Ts, lab)) in enumerate(TEXTS.items()):
        jobs += ctl_jobs(n, xi + 1, pages)
    M = run_pool(jobs, "battery")
    BAT = OrderedDict()
    for n, (role, pages, segs, Ts, lab) in TEXTS.items():
        BAT[n] = battery_score(n, Ts, M, ref, folds, pages)
        for T, r in BAT[n].items():
            emit(f"  {n:26s} " + bat_line(T, r))
    flush()

    # ---- calls
    emit("\n=== calls ===")
    FULL, DESC = OrderedDict(), OrderedDict()
    for n, (role, pages, segs, Ts, lab) in TEXTS.items():
        app = [sn for sn in segs if PR[n][sn]["core_share"] >= MIN_CORE_SHARE]
        sig = {sn: flags(PR[n][sn], lb) for sn in segs}
        sig_ok = bool(app) and all(sig[sn][0] for sn in app)
        bat_ok = all(BAT[n][T]["holds"] for T in Ts)
        FULL[n] = sig_ok and bat_ok
        fails = {sn: [k for k, v in sig[sn][1].items() if not v] for sn in segs}
        DESC[n] = dict(role=role, applicable=app, sig={sn: sig[sn][2] for sn in segs}, sig_ok=sig_ok, battery_ok=bat_ok,
                       battery={T: BAT[n][T]["folds_ok"] for T in Ts}, fails=fails)
        emit(f"  {n:26s} {role:11s} signature " + " ".join(f"{sn}:{sig[sn][2]}" for sn in segs) +
             f" (applicable {','.join(app)}) -> {sig_ok}; battery " + " ".join(f"{T} {BAT[n][T]['folds_ok']}/15" for T in Ts) +
             f" -> {bat_ok}; FULL = {FULL[n]}")
        emit(f"      failing parts: " + "; ".join(f"{sn}: {', '.join(fails[sn]) or '-'}" for sn in segs))
    PC2 = FULL["PC2_VOY_IT2a_as_control"]
    NC = not FULL["NC_augustine_la"]
    GATE = PC1 and PC2 and NC
    emit(f"  GATE: PC1 {PC1}; PC2 {PC2}; NC (plain Latin not Voynich-like) {NC} -> GATE = {GATE}")
    hits = [n for n, (role, *_r) in TEXTS.items() if role == "control" and FULL[n]]
    CALL = GATE and bool(hits)
    emit(f"  CALL_REOPEN_H17_H16 = {CALL}")
    if not GATE:
        why = [k for k, v in (("PC1", PC1), ("PC2", PC2), ("NC", NC)) if not v]
        reading = f"uninformative: gate failed ({', '.join(why)})"
    elif CALL:
        reading = "H-17/H-16 reopened: " + ", ".join(hits)
    else:
        reading = "no hard-way control reaches the signature + battery: F-40 gains an external-genre line"
    emit(f"\nVERDICT: CALL_REOPEN_H17_H16 = {CALL}: {reading}")

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "profiles.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "segmenter", "tokens", "types", "core_share", "te_tok", "o100", "p100", "o200", "Rw1", "pRw1", "Rc1",
                    "loc", "loc_lo", "loc_hi", "C1", "flags", "D"])
        rows = [(f"VOY_{T}", "slot", v[1]) for T, v in VOY.items()] + [(n, sn, p) for n in PR for sn, p in PR[n].items()]
        for n, sn, p in rows:
            o, r, l = p["order"], p["rep"], p["loc"]
            ok, _, fl = flags(p, lb)
            w.writerow([n, sn, p["tokens"], p["types"], f"{p['core_share']:.4f}", p["te_tok"], f"{o[100]['mm']:.6f}", f"{o[100]['p']:.4f}",
                        f"{o[200]['mm']:.6f}", f"{r[1]['Rw']:.4f}", f"{r[1]['pw']:.4f}", f"{r[1]['Rc']:.4f}", f"{l['ratio']:.4f}",
                        f"{l['lo']:.4f}", f"{l['hi']:.4f}", ok, fl, f"{S87.distance(p, lb, rw_v, rc_v)[0]:.3f}"])
    with (RUN_DIR / "battery.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "T", "fold", "n"] + S67.PREDS + ["small", "type_ratio", "P1", "P2", "P3", "P4", "P5"])
        for n in BAT:
            for T, r in BAT[n].items():
                for x in r["rows"]:
                    w.writerow([n, T, x["Q"], x["n"]] + [x["holds"][k] for k in S67.PREDS] + [x["small"], f"{x['type_ratio']:.4f}"] +
                               [f"{x['gen'][k]:.5f}" for k in ("P1", "P2", "P3", "P4", "P5")])
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(loc_band=lb, order_band=S87.ORDER_BAND, PC1=PC1, PC1_seeds=pc1, PC2=PC2, NC=NC,
                                                        GATE=GATE, CALL_REOPEN_H17_H16=CALL, FULL=FULL, desc=DESC, verdict=reading),
                                                   indent=1, default=str), encoding="utf-8", newline="\n")
    emit(f"\nsidecars: runs/s97/profiles.csv, runs/s97/battery.csv, runs/s97/calls.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


if __name__ == "__main__":
    main()
