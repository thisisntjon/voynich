"""S104 (Phase 7.1, grid G1; D-066 (j), frozen by Jon's approval 2026-10-18 13:07): do table-driven verbose
encodings of real period recipe text reproduce the manuscript's JOINT profile, and does a reproducing construction
then predict held-out quires better than the same construction fed shuffled plaintext?

RIVALS (D-066 (j)): H-14/H-06 table-driven verbose encoding of real recipe text (a construction meeting the spec
 reproduces the joint profile and then predicts held-out quires) vs H-05/H-07 meaningless procedure (spec constructions
 reproduce the profile only with plaintext replaced by random input, i.e. the plaintext adds nothing).

D-066 (j) CRITERIA, REQUIRED JOINTLY PER CELL (copied into the prereg stub header; thresholds never changed):
 SIG  four-part core signature (F-40; S87.c1 with s87 amendment-1 ORDER_BAND K100 [+0.012321,+0.092252],
      K200 [-0.003465,+0.086474]; R_within(1) > 1 with p < 0.05; R_cross(1) < R_within(1); locality ratio inside the
      LOCALITY band recomputed from VOY ZL3b/RF1b/IT2a SlotSegmenter cores as in s97/s102) on EVERY APPLICABLE
      segmenter of s97 (identity, SlotSegmenter, Seg_Affix2; applicable iff core share >= 0.5).
 BAT  s67 slot battery >= 4/6 predictions on >= 8/15 folds, on each of ZL3b, RF1b, IT2a (S97.ctl_jobs /
      S97.battery_score, unchanged).
 RHY  within-line word-length rhythm (F-04): lag-1 Moran I excess over 999 within-line shuffles > 0 with p < 0.05
      (S102.rhythm = S21.analyze).
 H2   conditional character entropy h2 (S102.h2_of = a1_profile.char_entropies) in [2.023, 2.234] (D-066 (j) band,
      = s102's VOY band [2.0234, 2.2336] rounded as written in D-066 (j); the constant H2_BAND below).
 LAG2 lag-2 prefix residue <= 0.5 x the s81 table's (F-46; s98 statistic).  Statistic: s98's cross-fitted
      CMI2 = I(P_t; P_{t-2} | P_{t-1}) (XCMI, K_MAIN = 8, same-length head-swap null, M_NULL = 200; S98.measure
      imported unchanged, prefix slot, SlotSegmenter fitted on the training part), excess = obs - mean(null), scored
      leave-one-block-out on the s87/s97 15 blocks of 1,500 tokens (block b = pseudo-quire b; s97's block rule
      S97.block_split), residue = median over the 15 blocks.  Reference = the s81 line-sticky table's median prefix
      XCMI excess as filed in results_s98.txt ("EXCESS SIZE" block: pre ZL3b / RF1b / IT2a S81 medians), averaged
      over the three transliterations (one number: "the s81 table's"); LAG2 holds iff residue <= 0.5 x reference.
      (results_s98.txt is hashed in the stub; with the filed values 17.874, 12.491, 17.418 x 1e-3 bits the bar is
      0.5 x 15.928e-3 = 7.964e-3 bits.)
 PASS(cell) = SIG and BAT and RHY and H2 and LAG2.
GATES (read before any cell; GATE = R and S and L):
 R  recovery gate: the planted decoder with the known table decodes >= 0.80 of the cipher tokens back to the planted
    plaintext unit (G1a: syllable; G1b: word; G1c: abbreviated word) on EVERY one of the 18 encoded texts.
 S  the s97 gate reproduces with s97's code and constants (as in s102): PC1 s91 LP91 at PLANTED on ZL3b Voynich-like
    on >= 2/3 seeds; PC2 IT2a-as-control s97 full call True (SIG on SlotSegmenter + BAT); NC plain Latin (Augustine)
    s97 full call False.
 L  lag-2 validity on the block pipeline: each of VOY ZL3b, RF1b, IT2a (22,500-token cut, s87 layout) satisfies the
    LAG2 bar, AND the s81 line-sticky table text (S81.encipher, Greshko Naibbe tables, p = 0.75 per line, CREMMA Latin,
    s81's seed for line_sticky75 seed 1, on the ZL3b cut's skeleton) does NOT (residue > bar).  A bar that the
    manuscript fails, or that its own reference passes, cannot separate anything.

CONSTRUCTIONS.  Parameters were set a priori, from the D-066 (j) spec and period practice, BEFORE any scoring; they
were never tuned on any score.  Reasons:
 Common.  Plaintexts = the three s102 texts, loaded with s102's own loaders and symbol rule (S102.load_p1,
   S102.load_period: 23-letter period alphabet + '~' abbreviation + '&' Tironian et): P1_la (CREMMA Medic MSS + Macer
   Floridus), P2_it (Anonimo Veneziano + Tuscan fill), P3_de (Pfeiffer Arzneibuecher + Buoch von guoter Spise +
   Megenberg fill).  The plaintext SEGMENT of a cell = the first words of the text that give N_TOT = 22,500 cipher
   tokens (G1b/G1c: 22,500 words; G1a: the fewest words whose syllables reach 22,500).  All cipher streams are laid
   out on ZL3b line lengths and page sizes (S87.layout, the s87/s102 rule): a syllable stream has no source line
   breaks, and one layout rule keeps the 18 texts comparable.  Row draws (a die throw per line) come from
   default_rng([SEED, tag, global line index]) and are identical for a cell and its twin.
 SHUFFLED TWIN (H-05/H-07 control): the same segment of words permuted uniformly at random (default_rng([SEED, 77,
   plaintext index, construction index])) before the construction runs; same key (keys are built from unit counts,
   which a permutation keeps), same layout, same per-line rows.  It keeps every unigram and destroys word order, hence
   any content-bearing sequence.
 G1a verbose syllabary.  Syllables by s97's rule (S97.syllables: nucleus = maximal run of a e i o u y, 0-1 consonants
   to the next syllable, >= 2: first is coda).  Each plaintext SYLLABLE becomes ONE cipher token (the Naibbe
   convention, s81: each plaintext chunk is one word; it also keeps word lengths near the manuscript's without fitting).
   Syllable core = s97's verbose syllable groups (S97.syllable_codes on the segment, imported unchanged: 14-glyph
   alphabet "abcdefghiklmno", frequency ranks 0-153 two glyphs, 154-741 three glyphs, rarer syllables a crc32-chosen
   three-glyph group (lossy homophony)), so G1a differs from s97's C3a only in syllable = token and the row table.
   Table: K_ROWS = 6 rows (one throw of a six-sided die per line selects the row; dice or cards as the row selector
   is the period-feasible mechanism of the Naibbe reconstruction, Greshko 2025, used in s81); row r writes every
   syllable s as ROW_PFX[r] + core(s) + ROW_SFX[r] with ROW_PFX = ["", "x", "z", "xz", "zx", "zz"], ROW_SFX =
   ["", "w", "j", "wj", "jw", "jj"] (s97's marker glyphs x z / w j): k = 6 glyph groups per syllable, the row held
   for the whole line.  Decoder: strip row marks, core -> highest-ranked syllable with that group.
 G1b line-table nomenclator.  Word types ranked by frequency in the segment (ties by string).  Code book of
   NC = 100 code cores x D = 6 tiers = 600 code words (rank n -> core n mod 100, tier n div 100): a small core
   inventory (100) that covers the frequent words; period nomenclators were short lists of frequent words and names
   beside a cipher alphabet (order of tens to a few hundred entries: general history of cryptography, unverified in
   this run).  Code cores: ranks 0-49 two glyphs, 50-99 three glyphs, drawn uniformly without repeats from s102's
   E2 letter glyphs (s102's E3 rule).  Words outside the book are spelled with s102's E2 homophonic alphabet (S102
   Cipher enc 2: homophones 4,4,4,3,3,3,2,2,2,2,1..., nulls with P_NULL = 0.05; a spelling equal to a code core is
   redrawn), the alphabet every nomenclator carried; spelled words have tier 0.
   PREFIX from the previous word's state (first-order, F-46): a six-position prefix wheel; p_t = (p_{t-1} + tier_t)
   mod 6, p = 0 at every line start (F-14 reset), prefix string PFX_B[p_t], PFX_B = ["", "V", "W", "X", "VW", "WX"].
   The prefix therefore depends on the previous prefix and the current word only.
   SUFFIX from a line-held table: per line a die selects row r of a fixed 6 x 4 table SUF_T (entries drawn once,
   default_rng([SEED, 23]), uniformly from 0..5); column = core class crc32(core) mod 4; suffix string
   SFX_B[SUF_T[r][class]], SFX_B = ["", "Y", "Z", "YZ", "ZY", "YY"].  The suffix carries no plaintext (a null
   decoration that marks the line's row).  Prefix glyphs {V W X} and suffix glyphs {Y Z} are disjoint from the core
   glyphs (s102 GLYPHS[:46]), so the table decodes unambiguously: tier = (p_t - p_{t-1}) mod 6.
 G1c abbreviate, then G1b.  Medieval abbreviation by general signs common to Latin and vernacular hands (Cappelli),
   applied to every reduced plaintext word in this order: (1) whole word et / e / ed / und / unde / unt -> '&'
   (Tironian et); (2) a word of >= 4 symbols beginning per / par / pro / pre -> 'p~' + rest, beginning con / com / cum
   -> 'c~' + rest; (3) a word of >= 5 symbols ending -que -> stem + 'q~', else a word of >= 4 ending -us -> stem + '~';
   (4) in a word of > 2 symbols, m or n after a vowel and before a consonant or at word end -> '~' (nasal macron).
   G1b (its own key: ranks over the abbreviated forms) then runs on the abbreviated words; recovery is to the
   abbreviated word (expansion is a reading step; its majority-expansion accuracy is printed, descriptive).

CELLS: 3 constructions x 3 plaintexts = 9 plaintext cells, each with its shuffled twin (18 encoded texts).
PRE-REGISTERED CALLS (printed "= True/False"):
 CALL_S104_GATE = R and S and L.
 CALL_S104_ANY_PASS = GATE and PASS(any of the 9 plaintext cells).
 TWIN_PASS(cell) = PASS(shuffled twin) (printed for all 9).
SURVIVOR TEST (run only for plaintext cells with PASS; also on that cell's twin):
 Folds = s67's 15 quires (S67.folds_of(ZL3b)), on each of ZL3b, RF1b, IT2a.  FIT on the training quires only: the
 construction's glyph tables are filled from the training quires' SlotSegmenter inventories ranked by token count
 (cores, prefixes, suffixes; empty prefix/suffix allowed as a value; empty cores excluded): G1a syllable rank i ->
 core rank i (beyond the inventory: crc32 into it), row r -> (prefix rank r, suffix rank r); G1b/G1c code core c ->
 core rank c, spelled word -> core rank 100 + crc32(word) mod (inventory - 100), wheel position p -> prefix rank p,
 suffix string k -> suffix rank k; structure (rows, wheel, SUF_T, key ranks, a priori counts) unchanged.  PREDICT the
 held-out quire: the plaintext unit stream (the cell's own segment, cyclic; the twin uses its shuffled segment) is
 written on the training pages' layout, then on the held-out quire's layout in replicates (s91 rule: page ids
 "r<j>:<id>", continuing the stream) until >= N_TOT tokens, cut to N_TOT (S91.cut).  Fold holds iff (i) S87.c1 on the
 replicate text with SlotSegmenter cores (S97.profile_g, s87 bands, this run's LOCALITY band) AND (ii) the s67
 battery fold holds (>= 4/6; generated Measured = training-layout text vs held-out-layout text, scored against the
 real fold's Measured by S67.score_model exactly as S97.battery_score).
 LOQO(cell) iff holds on >= 8/15 folds on each of ZL3b, RF1b, IT2a.  BEAT(cell) iff the plaintext cell's held folds
 summed over the three transliterations exceed its twin's (strictly).  SURVIVOR(cell) = LOQO and BEAT.
STOPPING RULE / VERDICT (D-066 (j)); exactly one reading:
 GATE False -> "uninformative: gate failed (<which>)".
 no plaintext cell passes -> "table-driven verbose encodings of real recipe text are closed within G1; the grid moves
   to the H-05/H-07 side (procedure without plaintext)" (twins that pass are named, as an H-05/H-07 pointer).
 a cell passes and SURVIVOR -> "survivor <cells>: predicts held-out quires and beats its shuffled twin (H-14/H-06);
   a decipherment candidate must first predict the Phase 7.2 cribs".
 a cell passes, LOQO holds but not BEAT, or its twin passes equally -> "structure without content: do not attempt
   decipherment".
 a cell passes and its twin does not, but LOQO fails -> "passes in-sample but does not predict held-out quires:
   closed within G1 (failed property: held-out prediction)".
 Precedence when several cells pass: SURVIVOR in any cell > structure without content > held-out failure.
FIXTURE (--fx104; synthetic only, reads no real data; writes runs/s104/fixture_<stamp>.txt):
 FXa encoders on a pseudo-Latin plaintext (S97.pseudo_latin, 3,500 lines): recovery >= 0.99 for G1b, G1c (G1c to
     the abbreviated form); [REVISION 1] G1a recovery equals the injective share (tokens whose syllable owns its s97
     group; s97's crc32 grouping of rare syllables is lossy by design); G1a every line one row; G1b suffix row consistent within a line and the decoded
     tiers reproduce the wheel; prefix/suffix/core glyph sets disjoint; twin = permutation (same multiset); G1b
     code-token share > 0; abbreviation unit tests (8 words).
 FXb lag-2 on the block pipeline: [REVISION 1] the s81 line-sticky table text (S81.encipher, p 0.75 per line,
     CREMMA Latin from offset S81.FIX_PLAIN_START, seed S81.FIX_SEED: s98's fixture Part B manuscript; Naibbe key and
     CREMMA Latin are not Voynich data) on a synthetic skeleton (12 x 15 pages x 20 lines, lengths 1 + Poisson(7)) has
     residue > the LAG2 bar, and a planted first-order prefix chain (6 prefixes, rows Dirichlet(0.5), reset per line)
     on the same kind of skeleton has residue <= the bar.
 FXc survivor path end to end on a synthetic world (S91.fx_world cores wrapped with prefixes/suffixes): one fold of
     the survivor scoring runs and returns sig/battery fields (crash test, not gating on its value).
 FXd the 2-worker pools return their smoke jobs (battery Measured and lag-2).
LEAD PRE-FREEZE AMENDMENT D-066 (j-amend) (received 13:23 PDT, before any freeze or real score; = REVISION 2).
 Independent roach results r6-r8 arrived BEFORE this freeze: r6 rejects a fixed line-held affix table (0/15; affixes
 cluster within lines C 1.065/1.119, adjacent lines share above page level X 1.050/1.069, suffixes show decaying
 within-line order 1.128 at d=1 to 0.856 at d=6); r7 the four-part signature is heterogeneous by quire and segmenter
 under independent code; r8 the robust cipher mismatch is LOW immediate core recurrence.  Nothing in G1 was fitted to
 r6-r8: constructions and a priori parameters are unchanged.  Changes:
 (A1) TARGET CALIBRATION.  VOY_ZL3b, VOY_RF1b, VOY_IT2a (the 22,500-token cuts) are scored first through the exact
   same cell criteria code (SIG on identity/slot/affix2, BAT vs ZL3b/RF1b/IT2a, RHY, H2, LAG2) and through the
   survivor fold rule.  Any criterion that ANY of the three manuscript texts fails becomes TARGET-RELATIVE for every
   cell (rules fixed here, before scoring):
     SIG on segmenter s: each component inside the manuscript's own range: o100 in [min - 0.039966, max + 0.039966],
       o200 in [min - 0.044970, max + 0.044970], locality in [min - 0.071250, max + 0.071250] (s87/s91 band
       half-widths), R_within(1) and R_cross(1) in [min / 1.25, max x 1.25] (s87 D scaling), min/max over the three
       VOY values on s; R_cross < R_within still required.
     BAT on T: cell folds_ok >= min over the three VOY texts' folds_ok on T.
     RHY: cell excess >= min VOY excess (p not required).
     H2: band = [min(2.023, min VOY h2), max(2.234, max VOY h2)].
     LAG2: bar = the 90th percentile of the 45 pooled VOY per-block excesses (the manuscript's own fold
       distribution); gate L then requires only that the s81 table exceeds that bar.
     Survivor LOQO on T: if the manuscript's own fold count (fold b holds iff VOY's slot SIG holds and its battery
       row b holds >= 4/6, VOY text as control vs T) is < 8 for any of the three VOY texts, the LOQO bar on T = the
       minimum of those counts.
 (A2) TWO UNUSED SURVIVOR PREDICTIONS, scored only for plaintext cells passing the main criteria (and their twins),
   plus the three VOY texts as calibration; never used to choose anything; printed as PRED_A / PRED_B (not part of
   SURVIVOR, which stays LOQO and BEAT per D-066 (j)):
     PRED_A (r6 affix-state profile; SlotSegmenter fitted on the text; prefix and suffix separately):
       C = within-line same-value pair rate / different-line same-page pair rate, p from N_SHUF_AFF = 999 within-page
       token shuffles; X = adjacent-line pair rate / non-adjacent different-line same-page pair rate, p from 999
       within-page line-order shuffles; suffix recurrence R(d) = within-line same-suffix rate at distance d / its
       within-line-shuffle mean, decay = R(1) - R(6), p from 999 within-line shuffles.  Holds iff C > 1 and X > 1
       with p < 0.05 for both prefix and suffix, and decay > 0 with p < 0.05.
     PRED_B (Voynich-scale immediate core recurrence): R_within(1) under SlotSegmenter AND Seg_Affix2 each inside
       [min VOY / 1.25, max VOY x 1.25] on that segmenter with p < 0.05.
 FXe (fixture, added with the amendment): affix_profile on a text with a line-held suffix (suffix kept for the line
   with p 0.8, prefixes IID) gives suffix C > 1 with p < 0.05; on an IID affix text suffix C is within [0.95, 1.05].
DESIGN REVISIONS (at most two, pre-freeze; REVISION 2 = the lead amendment above):
 REVISION 1 (after fixture run 1, 13:20:54 PDT: FAIL).  FXa: G1a recovery 0.9655 < 0.99 because s97's syllable groups
   are lossy for rare syllables (ranks > 741 share crc32 groups; the fixture's injected '~' '&' create more syllable
   types) -> FXa's G1a check becomes "recovery equals the injective share"; two abbreviation test expectations were
   mine and contradicted the documented rules (aquamque -> aqua~q~ by rules 3 and 4; dominus -> domin~ since rule 4
   skips n before '~') -> expectations corrected to the rules (the rules are unchanged).  FXb: a planted 4-table
   hidden line state over 6 prefixes gave residue +1.29e-3 (1/15 positive): too weak a plant to be a positive control;
   the first-order plant gave +4.40e-3 (2/15) -> the positive plant is replaced by s98's own positive manuscript (the
   s81 line-sticky table on a synthetic skeleton).  Nothing in the real-data path changed.
FIXTURE OUTCOME BEFORE THE FREEZE (runs/s104/fixture_*.txt): run 1 13:20:54 FAIL (REVISION 1); run 2 13:22:39 PASS;
 run 3 13:27:43 PASS after REVISION 2 (FXa PASS: G1a recovery = injective share 0.9655, G1b/G1c 1.0000; FXb s81
 line-sticky residue +11.38e-3 > bar 7.964e-3, first-order +4.40e-3; FXc, FXd PASS; FXe held-suffix C 3.94 p 0.001,
 IID suffix C 1.019).  Well-formedness 13:27:55 (runs/s104/wellformed_*.txt): all 18 texts 22,500 tokens, 2,888
 lines, 173 pages; alphabets G1a 18 glyphs, G1b/G1c 51 glyphs; segments: G1a 13,267 / 13,014 / 14,687 words.
Pre-freeze looks at real data (--wellformed; writes runs/s104/wellformed_<stamp>.txt): ONLY glyph alphabets and
 token / line / page counts of the 18 encoded texts and the plaintext segment sizes; no statistic, no recovery.
COMPUTE: profiles on the GPU (torch cuda) in the main process; battery and lag-2 in N_WORKERS = 2 spawn workers at
 BelowNormal, OMP threads 1; free RAM >= 4 GB checked before each pool (else stop).  Limit 4 CPU-hours.
OUTPUT: results_s104.txt (never overwritten: if it exists the run stops unless --amend1, which writes
 results_s104_amend1.txt and stops if that exists) and runs/s104/ sidecars.
Run: python -I s104_g1_encoding_grid.py   Fixture: --fx104   Well-formedness: --wellformed   Stub list: --list-locals
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
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

import s102_period_ciphers_recipes as S102  # noqa: E402
import s97_language_rescue_controls as S97  # noqa: E402
import s98_lag2_prefix_dependence as S98  # noqa: E402
import s81_sticky_table_loqo as S81  # noqa: E402
import s91_line_pool_producer_loqo as S91  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

S87, S67, S80, S57 = S97.S87, S97.S67, S97.S80, S97.S57

SELF = ROOT / "s104_g1_encoding_grid.py"
STUB = ROOT / "s104_g1_encoding_grid.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s104"
S98_RESULTS = ROOT / "results_s98.txt"
FIXTURE = "--fx104" in sys.argv
WELLFORMED = "--wellformed" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
AMEND = "--amend1" in sys.argv
SEED = 20261104
N_TOT, NB = S87.N_TOT, S87.NB
N_MATCH = S97.N_MATCH
MIN_CORE_SHARE = S97.MIN_CORE_SHARE
REC_MIN = 0.80
H2_BAND = (2.023, 2.234)
RHY_P = 0.05
LAG2_FACTOR = 0.5
LOQO_MIN = 8
N_SHUF_AFF = 999
HW_SIG = dict(o100=0.039966, o200=0.044970, loc=0.071250)
R_SCALE = 1.25
LAG2_REL_Q = 90
BAT_FOLD_MIN = S97.BAT_MIN_HOLD
N_WORKERS = 2
MIN_FREE_GB = 4.0
TRANSLITS = S97.TRANSLITS
SEGS = S97.SEGS
# G1a
K_ROWS = 6
ROW_PFX = ["", "x", "z", "xz", "zx", "zz"]
ROW_SFX = ["", "w", "j", "wj", "jw", "jj"]
# G1b
NC = 100
NC_SHORT = 50
D_TIERS = 6
PFX_B = ["", "V", "W", "X", "VW", "WX"]
SFX_B = ["", "Y", "Z", "YZ", "ZY", "YY"]
N_CLASS = 4
PFX_GLYPHS = set("VWX")
SFX_GLYPHS = set("YZ")
# G1c
ET_WORDS = {"et", "e", "ed", "und", "unde", "unt"}
VOW = set("aeiouy")
CONSTR = ["G1a", "G1b", "G1c"]
FUNC = {"P1_la": S102.FUNC_LA, "P2_it": S102.FUNC_IT, "P3_de": S102.FUNC_DE}
log: list[str] = []
T0 = time.time()
OUT = None


def pick_out():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if FIXTURE:
        return RUN_DIR / f"fixture_{stamp}.txt"
    if WELLFORMED:
        return RUN_DIR / f"wellformed_{stamp}.txt"
    base = ROOT / ("results_s104_amend1.txt" if AMEND else "results_s104.txt")
    if base.exists():
        print(f"STOP: {base.name} exists; results are never overwritten")
        raise SystemExit(3)
    return base


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    if OUT is None:
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def data_files():
    out = [f"data/translit/{f}.meta.json" for f in TRANSLITS.values()]
    out += ["data/controls_realline/cremma_all_marks.meta.json", "data/controls/latin_macer_floridus.txt",
            "data/controls/latin_augustine.txt", "results_s98.txt", "runs/s49/lang_latin_cremma.meta.json",
            "data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx"]
    for spec in S102.PERIOD_SRC.values():
        out += list(spec["files"])
    return sorted(set(out), key=out.index)


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


def s81_reference():
    """median prefix XCMI excess of the s81 table per transliteration, parsed from results_s98.txt."""
    txt = S98_RESULTS.read_text(encoding="utf-8")
    blk = txt.split("=== EXCESS SIZE", 1)[1].split("===")[1] if "=== EXCESS SIZE" in txt else ""
    ref = OrderedDict()
    for T in TRANSLITS:
        m = re.search(rf"pre {T}:.*?S81 ([+-][0-9.]+)", blk)
        ref[T] = float(m.group(1)) / 1000.0 if m else float("nan")
    return ref


# ======================================================================= constructions
def abbreviate(w):
    if w in ET_WORDS:
        return "&"
    if len(w) >= 4 and w[:3] in ("per", "par", "pro", "pre"):
        w = "p~" + w[3:]
    elif len(w) >= 4 and w[:3] in ("con", "com", "cum"):
        w = "c~" + w[3:]
    if len(w) >= 5 and w.endswith("que"):
        w = w[:-3] + "q~"
    elif len(w) >= 4 and w.endswith("us"):
        w = w[:-2] + "~"
    if len(w) > 2:
        out = []
        for i, ch in enumerate(w):
            if ch in "mn" and i > 0 and w[i - 1] in VOW and (i == len(w) - 1 or (w[i + 1] not in VOW and w[i + 1] not in "~&")):
                out.append("~")
            else:
                out.append(ch)
        w = "".join(out)
    return w or "~"


def die(tag, li):
    return int(np.random.default_rng([SEED, tag, li]).integers(K_ROWS))


def ranked_types(units):
    cnt = Counter(units)
    return [w for w, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]


class G1A:
    """verbose syllabary: syllable -> row prefix + s97 syllable group + row suffix; row held per line."""

    def __init__(self, seg_words, tables=None):
        self.code, self.n_types = S97.syllable_codes([list(seg_words)])
        syl = [s for w in seg_words for s in S97.syllables(w)]
        self.rank = {s: i for i, s in enumerate(ranked_types(syl))}
        self.inv = {}
        for s, r in sorted(self.rank.items(), key=lambda kv: kv[1]):
            self.inv.setdefault(self.code[s], s)
        self.rows = [(ROW_PFX[r], ROW_SFX[r]) for r in range(K_ROWS)]
        self.core_of = lambda s: self.code[s]  # noqa: E731
        if tables is not None:   # survivor fit: tables from training inventories
            cores, pres, sufs = tables
            nc = len(cores)
            self.core_of = lambda s: cores[self.rank[s]] if self.rank.get(s, nc) < nc else cores[zlib.crc32(s.encode("utf-8")) % nc]  # noqa: E731
            self.rows = [(pres[r % len(pres)], sufs[r % len(sufs)]) for r in range(K_ROWS)]

    @staticmethod
    def units(seg_words):
        return [s for w in seg_words for s in S97.syllables(w)]

    def encode_pages(self, pages, line0=0):
        out, rows, li = [], [], line0
        for pid, ls in pages:
            el = []
            for ln in ls:
                r = die(11, li); li += 1
                rows.append(r)
                p, s = self.rows[r]
                el.append([p + self.core_of(u) + s for u in ln])
            out.append((pid, el))
        return out, rows

    def decode_line(self, toks):
        res = []
        for t in toks:
            core = t.lstrip("xz").rstrip("wj")
            res.append(self.inv.get(core, ""))
        return res


class G1B:
    """line-table nomenclator: code core (mod NC) + tier on a prefix wheel (first-order) + line-held suffix table."""

    def __init__(self, units, func, pi, tables=None):
        self.ranked = ranked_types(units)
        self.rank = {w: i for i, w in enumerate(self.ranked)}
        self.ciph = S102.Cipher(2, list(units), func, 104 + pi)
        rng = np.random.default_rng([SEED, 13, pi])
        lg = self.ciph.letter_glyphs
        self.cores, used = [], set()
        for c in range(NC):
            L = 2 if c < NC_SHORT else 3
            while True:
                cg = "".join(lg[int(i)] for i in rng.integers(len(lg), size=L))
                if cg not in used:
                    used.add(cg); self.cores.append(cg); break
        self.core_idx = {cg: i for i, cg in enumerate(self.cores)}
        self.ciph.codebook = {cg: None for cg in self.cores}   # spelled forms avoid code cores (S102 Cipher.spell)
        self.suf_t = np.random.default_rng([SEED, 23]).integers(len(SFX_B), size=(K_ROWS, N_CLASS))
        self.pfx = list(PFX_B)
        self.sfx = list(SFX_B)
        self.fitted = None
        if tables is not None:
            cores, pres, sufs = tables
            self.fitted = cores
            self.pfx = [pres[p % len(pres)] for p in range(D_TIERS)]
            self.sfx = [sufs[k % len(sufs)] for k in range(len(SFX_B))]

    def core_tier(self, w):
        n = self.rank.get(w, 10 ** 9)
        if n < NC * D_TIERS:
            c, d = n % NC, n // NC
            if self.fitted is not None:
                return self.fitted[c % len(self.fitted)], d
            return self.cores[c], d
        if self.fitted is not None:
            nf = len(self.fitted)
            extra = max(1, nf - NC)
            return self.fitted[min(nf - 1, NC + zlib.crc32(w.encode("utf-8")) % extra)], 0
        return self.ciph.spell(w), 0

    def encode_pages(self, pages, line0=0):
        out, rows, li = [], [], line0
        for pid, ls in pages:
            el = []
            for ln in ls:
                r = die(21, li); li += 1
                rows.append(r)
                p = 0
                toks = []
                for w in ln:
                    core, d = self.core_tier(w)
                    p = (p + d) % D_TIERS
                    k = int(self.suf_t[r][zlib.crc32(core.encode("utf-8")) % N_CLASS])
                    toks.append(self.pfx[p] + core + self.sfx[k])
                el.append(toks)
            out.append((pid, el))
        return out, rows

    def parse(self, t):
        i = 0
        while i < len(t) and t[i] in PFX_GLYPHS:
            i += 1
        j = len(t)
        while j > i and t[j - 1] in SFX_GLYPHS:
            j -= 1
        return t[:i], t[i:j], t[j:]

    def decode_line(self, toks):
        res, prev = [], 0
        for t in toks:
            pre, core, suf = self.parse(t)
            pidx = PFX_B.index(pre) if pre in PFX_B else -1
            if core in self.core_idx and pidx >= 0:
                d = (pidx - prev) % D_TIERS
                n = d * NC + self.core_idx[core]
                res.append(self.ranked[n] if n < len(self.ranked) else "")
            else:
                res.append("".join(self.ciph.inv[g] for g in core if g in self.ciph.inv))
            if pidx >= 0:
                prev = pidx
        return res


def segment_words(words, constr):
    if constr == "G1a":
        n, k = 0, 0
        while k < len(words) and n < N_TOT:
            n += len(S97.syllables(words[k])); k += 1
        return list(words[:k]), n >= N_TOT
    return list(words[:N_TOT]), len(words) >= N_TOT


def build_cell(words, constr, func, pi, xi, twin, line_lens, page_nl):
    """-> dict(units_pages, enc_pages, enc, rows, seg, units)"""
    seg, enough = segment_words(words, constr)
    if twin:
        perm = np.random.default_rng([SEED, 77, pi, xi]).permutation(len(seg))
        seg = [seg[i] for i in perm]
    if constr == "G1a":
        units = G1A.units(seg)
        enc = G1A(seg)
    elif constr == "G1b":
        units = list(seg)
        enc = G1B(units, func, pi)
    else:
        units = [abbreviate(w) for w in seg]
        enc = G1B(units, func, pi)
    up = S87.layout(units, False, None, line_lens, page_nl)
    ep, rows = enc.encode_pages(up)
    return dict(units_pages=up, enc_pages=ep, enc=enc, rows=rows, seg=seg, units=units, enough=enough)


def recovery(cell):
    ok = n = 0
    for (_, ul), (_, el) in zip(cell["units_pages"], cell["enc_pages"]):
        for u, e in zip(ul, el):
            d = cell["enc"].decode_line(e)
            ok += sum(1 for a, b in zip(u, d) if a == b)
            n += len(u)
    return ok / max(1, n)


def expansion_accuracy(seg):
    ab = [abbreviate(w) for w in seg]
    src = {}
    for a, w in zip(ab, seg):
        src.setdefault(a, Counter())[w] += 1
    best = {a: c.most_common(1)[0][0] for a, c in src.items()}
    return sum(1 for a, w in zip(ab, seg) if best[a] == w) / max(1, len(seg))


def alphabet(pages):
    return "".join(sorted({ch for _, ls in pages for ln in ls for w in ln for ch in w}))


def counts(pages):
    return (sum(len(ln) for _, ls in pages for ln in ls), sum(len(ls) for _, ls in pages), len(pages))


# ======================================================================= lag-2 (s98 statistic on 15 blocks)
def with_blocks(pages):
    ntot = sum(len(ln) for _, ls in pages for ln in ls)
    tok, out = 0, []
    for pid, ls in pages:
        out.append((pid, f"B{min(NB - 1, tok * NB // ntot):02d}", ls))
        tok += sum(len(ln) for ln in ls)
    return out


def lag2_job(job):
    S98.lower_priority()
    t = time.time()
    try:
        r = S98.measure(job["pages"], job["Q"], seed=job["seed"], slots=("pre",))
        x = r["pre"]["len"][0]
        return job["key"], dict(excess=x["excess"], p=x["p"], obs=x["obs"], n_tok=r["n_tok"], n_triples=r["n_triples"]), time.time() - t
    except Exception:  # noqa: BLE001
        return job["key"], dict(error=traceback.format_exc()), time.time() - t


def lag2_jobs(name, xi, pages):
    bp = with_blocks(pages)
    qs = sorted({q for _, q, _ in bp})
    return [dict(key=(name, q), pages=bp, Q=q, seed=SEED + 7000 + 100 * xi + b) for b, q in enumerate(qs)]


def lag2_summary(name, R):
    ex = [v["excess"] for (n, q), v in R.items() if n == name and "excess" in v]
    errs = [q for (n, q), v in R.items() if n == name and "error" in v]
    return dict(residue=float(np.median(ex)) if ex else float("nan"), n=len(ex), errors=errs,
                pos=sum(1 for (n, q), v in R.items() if n == name and "excess" in v and v["excess"] > 0 and v["p"] < 0.05))


# ======================================================================= pools
def pool_run(fn, jobs, tag, init):
    import multiprocessing as mp
    fg = S91.free_gb()
    emit(f"  [{tag}] free RAM {fg:.1f} GB (need >= {MIN_FREE_GB}); {len(jobs)} jobs on {N_WORKERS} workers")
    if not (fg >= MIN_FREE_GB):
        emit(f"STOP: free RAM {fg:.1f} GB < {MIN_FREE_GB} GB")
        flush()
        raise SystemExit(2)
    out = {}
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(N_WORKERS, initializer=init) as pool:
        for i, res in enumerate(pool.imap_unordered(fn, jobs)):
            k = res[0]
            out[k] = res[1:-1] if len(res) > 3 else res[1]
            if (i + 1) % 20 == 0 or i + 1 == len(jobs):
                print(f"  [{tag} {time.time() - t0:.0f}s] {i + 1}/{len(jobs)} done (last {k} {res[-1]:.0f}s)", flush=True)
    return out


def battery_pool(jobs, tag):
    return pool_run(S97.measure_job, jobs, tag, S97.worker_init)


def lag2_pool(jobs, tag):
    return pool_run(lag2_job, jobs, tag, S98.lower_priority)


# ======================================================================= survivor test
def inventories(train_words):
    sg = SlotSegmenter(train_words)
    C, P, S = Counter(), Counter(), Counter()
    for w in train_words:
        p, c, s = sg.segment(w)
        P[p] += 1; S[s] += 1
        if c:
            C[c] += 1
    rk = lambda cnt: [x for x, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]  # noqa: E731
    return rk(C), rk(P), rk(S)


def fill_layout(layout, stream, off, pid_fmt="{}"):
    """layout: list of (pid, [line lengths]) -> pages of units, continuing the cyclic stream from off."""
    pages, L = [], len(stream)
    for pid, lens in layout:
        ls = []
        for n in lens:
            ls.append([stream[(off + i) % L] for i in range(n)]); off += n
        pages.append((pid_fmt.format(pid), ls))
    return pages, off


def survivor_texts(cell_meta, pages_T, Q, tag):
    """-> (train_enc_pages, heldout_enc_pages (one replicate), H (replicates cut to N_TOT))."""
    constr, func, pi, seg, units = cell_meta["constr"], cell_meta["func"], cell_meta["pi"], cell_meta["seg"], cell_meta["units"]
    tr_words = [w for _, q, ls in pages_T if q != Q for l in ls for w in l]
    tables = inventories(tr_words)
    enc = G1A(seg, tables) if constr == "G1a" else G1B(units, func, pi, tables)
    tr_lay = [(pid, [len(l) for l in ls]) for pid, q, ls in pages_T if q != Q]
    te_lay = [(pid, [len(l) for l in ls]) for pid, q, ls in pages_T if q == Q]
    up, off = fill_layout(tr_lay, units, 0)
    line0 = 100000 * (1 + tag)
    tr_enc, _ = enc.encode_pages(up, line0)
    H, j, first = [], 0, None
    tot = 0
    while tot < N_TOT and j <= 400:
        hp, off = fill_layout(te_lay, units, off, f"r{j}:" + "{}")
        he, _ = enc.encode_pages(hp, line0 + 50000 + 1000 * j)
        if first is None:
            first = he
        H.extend(he)
        tot += sum(len(ln) for _, ls in he for ln in ls)
        j += 1
    return tr_enc, first, S91.cut(H)


def survivor_run(cells_meta, lb, ref, folds, label):
    """cells_meta: list of dicts (name, twin name, construction data).  -> per cell results."""
    jobs, prof = [], {}
    texts = OrderedDict()
    for ci, cm in enumerate(cells_meta):
        for T in TRANSLITS:
            pages_T = ref[T]
            for fi, Q in enumerate(folds):
                tr, te, H = survivor_texts(cm, pages_T, Q, 1000 * ci + 10 * list(TRANSLITS).index(T) + fi)
                k = (cm["name"], T, fi)
                texts[k] = (tr, te)
                p = S97.profile_g(f"SV/{cm['name']}/{T}/{Q}", H, SlotSegmenter, N_MATCH, SEED + 9000 + 100 * ci + fi)
                prof[k] = p
                jobs.append(dict(key=("SV",) + k, name=f"SV {cm['name']} {T} {Q}", train=tr, test=te,
                                 seed=SEED + 20000 + 1000 * ci + 10 * fi))
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            flush()
    jobs += S97.ref_jobs(ref, folds)
    M = battery_pool(jobs, label)
    res = OrderedDict()
    for cm in cells_meta:
        per_T = OrderedDict()
        for T in TRANSLITS:
            rows = []
            for fi, Q in enumerate(folds):
                k = (cm["name"], T, fi)
                rm, rdr = M[("REF", T, fi)]
                gm, gdr = M[("SV",) + k]
                real_te = [ls for p, q, ls in ref[T] if q == Q]
                cells, _, rt, small = S67.score_model(rm, rm.point(), rdr, [gm], gdr, rm.n_test, [[ls for _, ls in texts[k][1]]], real_te)
                nb = sum(bool(cells[x][0]) for x in S67.PREDS)
                sig, _, fl = S97.flags(prof[k], lb)
                rows.append(dict(Q=Q, sig=sig, flags=fl, bat=nb, holds=bool(sig and nb >= BAT_FOLD_MIN)))
            per_T[T] = dict(rows=rows, held=sum(r["holds"] for r in rows))
        res[cm["name"]] = per_T
    return res


# ======================================================================= amendment: target-relative rules, PRED_A/B
def sig_rel(p, vprofs):
    """target-relative SIG on one segmenter: components inside the manuscript's own range (A1)."""
    def rng(f):
        v = [f(q) for q in vprofs]
        return min(v), max(v)
    o1, o2 = rng(lambda q: q["order"][100]["mm"]), rng(lambda q: q["order"][200]["mm"])
    rw, rc = rng(lambda q: q["rep"][1]["Rw"]), rng(lambda q: q["rep"][1]["Rc"])
    lc = rng(lambda q: q["loc"]["ratio"])
    comp = OrderedDict()
    comp["a"] = (o1[0] - HW_SIG["o100"] <= p["order"][100]["mm"] <= o1[1] + HW_SIG["o100"]
                 and o2[0] - HW_SIG["o200"] <= p["order"][200]["mm"] <= o2[1] + HW_SIG["o200"])
    comp["b"] = rw[0] / R_SCALE <= p["rep"][1]["Rw"] <= rw[1] * R_SCALE
    comp["c"] = rc[0] / R_SCALE <= p["rep"][1]["Rc"] <= rc[1] * R_SCALE and p["rep"][1]["Rc"] < p["rep"][1]["Rw"]
    comp["d"] = lc[0] - HW_SIG["loc"] <= p["loc"]["ratio"] <= lc[1] + HW_SIG["loc"]
    return all(comp.values()), "".join("Y" if v else "n" for v in comp.values())


def _arrays(pages, slot_idx):
    toks = [w for _, ls in pages for ln in ls for w in ln]
    sg = SlotSegmenter(toks)
    vals, line, page, lp = [], [], [], []
    ix = {}
    li = 0
    for pi, (_, ls) in enumerate(pages):
        for ln in ls:
            for w in ln:
                v = sg.segment(w)[slot_idx]
                vals.append(ix.setdefault(v, len(ix)))
                line.append(li); page.append(pi)
            lp.append(pi); li += 1
    return np.asarray(vals), np.asarray(line), np.asarray(page), np.asarray(lp), len(ix)


def _cx(vals, line, page, lp, V, line_perm=None):
    nl = np.bincount(line * V + vals, minlength=len(lp) * V).reshape(len(lp), V).astype(np.float64)
    L = nl.sum(1)
    within = float((nl * (nl - 1)).sum()); wpairs = float((L * (L - 1)).sum())
    npg = np.zeros((int(lp.max()) + 1, V)); np.add.at(npg, lp, nl)
    Np = npg.sum(1)
    diff = float((npg ** 2).sum() - (nl ** 2).sum()); dpairs = float((Np ** 2).sum() - (L ** 2).sum())
    order = np.arange(len(lp)) if line_perm is None else line_perm
    a, b = order[:-1], order[1:]
    same = lp[a] == lp[b]
    adj = float((nl[a][same] * nl[b][same]).sum()); apairs = float((L[a][same] * L[b][same]).sum())
    non = diff / 2 - adj; npairs = dpairs / 2 - apairs
    C = (within / wpairs) / (diff / dpairs) if wpairs and diff and dpairs else float("nan")
    X = (adj / apairs) / (non / npairs) if apairs and non > 0 and npairs > 0 else float("nan")
    return C, X


def _rd(vals, line, dmax=6):
    out = []
    for d in range(1, dmax + 1):
        m = line[:-d] == line[d:]
        out.append(float((vals[:-d][m] == vals[d:][m]).mean()) if m.any() else float("nan"))
    return np.asarray(out)


def affix_profile(pages, seed):
    rng = np.random.default_rng(seed)
    res = OrderedDict()
    for si, slot in ((0, "pre"), (2, "suf")):
        vals, line, page, lp, V = _arrays(pages, si)
        C, X = _cx(vals, line, page, lp, V)
        cn, xn = [], []
        for _ in range(N_SHUF_AFF):
            o = np.lexsort((rng.random(len(vals)), page))
            cn.append(_cx(vals[o], line, page, lp, V)[0])
            lo = np.lexsort((rng.random(len(lp)), lp))
            xn.append(_cx(vals, line, page, lp, V, lo)[1])
        r = dict(C=C, pC=(1 + sum(c >= C for c in cn)) / (N_SHUF_AFF + 1), X=X, pX=(1 + sum(x >= X for x in xn)) / (N_SHUF_AFF + 1))
        if slot == "suf":
            obs = _rd(vals, line)
            nul = []
            for _ in range(N_SHUF_AFF):
                o = np.lexsort((rng.random(len(vals)), line))
                nul.append(_rd(vals[o], line))
            nul = np.asarray(nul)
            mu = nul.mean(0)
            R = obs / mu
            dec = float(R[0] - R[-1])
            dn = nul[:, 0] / mu[0] - nul[:, -1] / mu[-1]
            r.update(R=R.tolist(), decay=dec, pdecay=(1 + int((dn >= dec).sum())) / (N_SHUF_AFF + 1))
        res[slot] = r
    res["holds"] = bool(all(res[s]["C"] > 1 and res[s]["pC"] < 0.05 and res[s]["X"] > 1 and res[s]["pX"] < 0.05 for s in ("pre", "suf"))
                        and res["suf"]["decay"] > 0 and res["suf"]["pdecay"] < 0.05)
    return res


def fmt_aff(a):
    return (f"pre C {a['pre']['C']:.3f}(p{a['pre']['pC']:.3f}) X {a['pre']['X']:.3f}(p{a['pre']['pX']:.3f}) | suf C {a['suf']['C']:.3f}"
            f"(p{a['suf']['pC']:.3f}) X {a['suf']['X']:.3f}(p{a['suf']['pX']:.3f}) R(1..6) " + " ".join(f"{x:.3f}" for x in a['suf']['R'])
            + f" decay {a['suf']['decay']:+.3f}(p{a['suf']['pdecay']:.3f}) -> PRED_A {a['holds']}")


def pred_b(prs, vprs):
    out = {}
    for sn in ("slot", "affix2"):
        v = [q[sn]["rep"][1]["Rw"] for q in vprs]
        r = prs[sn]["rep"][1]
        out[sn] = bool(min(v) / R_SCALE <= r["Rw"] <= max(v) * R_SCALE and r["pw"] < 0.05)
    return all(out.values()), out


def fx_aff_pages(held, seed):
    rng = np.random.default_rng(seed)
    pres, sufs = ["", "q", "o", "qo"], ["", "y", "n", "dy", "l", "r"]
    cores = ["".join("acehikt"[int(i)] for i in rng.integers(7, size=int(rng.integers(2, 5)))) for _ in range(200)]
    pages = []
    for pg in range(60):
        ls = []
        for _ in range(20):
            cur = int(rng.integers(len(sufs)))
            ln = []
            for _ in range(1 + int(rng.poisson(7))):
                si = cur if (held and rng.random() < 0.8) else int(rng.integers(len(sufs)))
                ln.append(pres[int(rng.integers(4))] + cores[int(rng.integers(200))] + sufs[si])
            ls.append(ln)
        pages.append((f"p{pg:03d}", ls))
    return pages


# ======================================================================= fixture
def fx_lag2_pages(kind, seed):
    rng = np.random.default_rng(seed)
    pres = ["", "q", "o", "qo", "d", "s"]
    cores = ["".join("acehiklrty"[int(i)] for i in rng.integers(10, size=int(rng.integers(2, 5)))) for _ in range(300)]
    z = 1.0 / np.arange(1, 301); z /= z.sum()
    sufs = ["", "y", "n", "dy"]
    if kind == "state":
        tabs = [0.05 / 6 + 0.95 * rng.dirichlet(np.full(6, 0.3)) for _ in range(4)]
    else:
        trans = rng.dirichlet(np.full(6, 0.5), size=6)
        init = rng.dirichlet(np.full(6, 0.5))
    pages = []
    for pg in range(12 * NB):
        ls = []
        for _ in range(20):
            L = 1 + int(rng.poisson(7))
            ln, st, prev = [], int(rng.integers(4)), None
            for j in range(L):
                if kind == "state":
                    if j > 0 and rng.random() >= 0.75:
                        st = int(rng.integers(4))
                    pidx = int(rng.choice(6, p=tabs[st] / tabs[st].sum()))
                else:
                    pidx = int(rng.choice(6, p=init if prev is None else trans[prev]))
                prev = pidx
                ln.append(pres[pidx] + cores[int(rng.choice(300, p=z))] + sufs[int(rng.integers(4))])
            ls.append(ln)
        pages.append((f"p{pg:04d}", ls))
    return S87.layout(None, True, pages, None, None)


def run_fixture():
    emit("S104 FIXTURE (synthetic only; no real data read)")
    emit(f"date: {S87.clock()}  device: {S87.DEV}; below_normal={S87.below_normal()}")
    emit(f"s104 sha256={sha256(SELF)}  stub_match={stub_match()}")
    pl, _lex = S97.pseudo_latin(7, n_lines=3500)
    r = np.random.default_rng(3)
    pl = [["".join(ch if r.random() > 0.03 else ("~" if r.random() < 0.7 else "&") for ch in w) for w in ln] for ln in pl]
    red = {"j": "i", "v": "u", "w": "uu"}
    words = [w for ln in pl for w in ("".join(red.get(ch, ch) for ch in w) for w in ln) if w]
    emit(f"fixture plaintext words {len(words)} types {len(set(words))}")
    zl_like = [int(x) for x in np.random.default_rng(4).integers(4, 12, size=400)]
    page_nl = [int(x) for x in np.random.default_rng(5).integers(8, 30, size=200)]
    ok_a = True
    for xi, constr in enumerate(CONSTR):
        cells = {}
        for twin in (False, True):
            c = build_cell(words, constr, S102.FUNC_LA, 1, xi, twin, zl_like, page_nl)
            cells[twin] = c
            rec = recovery(c)
            n, nl, npg = counts(c["enc_pages"])
            good = rec >= 0.99 and n == N_TOT
            held = True
            disj = True
            if constr == "G1a":
                for _, el in c["enc_pages"]:
                    for ln in el:
                        held &= len({(t[:len(t) - len(t.lstrip('xz'))], t[len(t.rstrip('wj')):]) for t in ln}) == 1
                disj = not (set(alphabet(c["enc_pages"])) - set(S97.CODE_ALPH) - set("xzwj"))
                us = [u for _, ls in c["units_pages"] for ln in ls for u in ln]
                inj = sum(1 for u in us if c["enc"].inv.get(c["enc"].code[u]) == u) / len(us)
                good = abs(rec - inj) < 1e-12 and n == N_TOT
                emit(f"  {constr}{' twin' if twin else ''}: injective share {inj:.4f} (recovery must equal it)")
            else:
                enc = c["enc"]
                li = 0
                for _, el in c["enc_pages"]:
                    for ln in el:
                        rrow = c["rows"][li]; li += 1
                        for t in ln:
                            pre, core, suf = enc.parse(t)
                            k = int(enc.suf_t[rrow][zlib.crc32(core.encode("utf-8")) % N_CLASS])
                            held &= suf == SFX_B[k] and pre in PFX_B
                            disj &= set(core) <= set(S102.GLYPHS[:46])
                code_share = sum(1 for _, ls in c["enc_pages"] for ln in ls for t in ln if enc_code(c, t)) / n if constr != "G1a" else float("nan")
                good &= code_share > 0
            alph = alphabet(c["enc_pages"])
            good &= held and disj
            ok_a &= good
            emit(f"  {constr}{' twin' if twin else ''}: recovery {rec:.4f}; tokens {n} lines {nl} pages {npg}; alphabet {len(alph)} '{alph}'; "
                 f"line-held/wheel ok {held}; disjoint {disj}" + (f"; code share {code_share:.3f}" if constr != "G1a" else "")
                 + f" -> {'ok' if good else 'BAD'}")
        same = Counter(cells[False]["seg"]) == Counter(cells[True]["seg"]) and cells[False]["seg"] != cells[True]["seg"]
        ok_a &= same
        emit(f"  {constr}: twin is a permutation of the plaintext segment: {same}")
    tests = [("et", "&"), ("perfundere", "p~fu~dere"), ("confectio", "c~fectio"), ("herbam", "herba~"), ("aquamque", "aqua~q~"),
             ("dominus", "domin~"), ("und", "&"), ("in", "in")]
    tres = [(w, abbreviate(w), e) for w, e in tests]
    ok_ab = all(a == e for _, a, e in tres)
    ok_a &= ok_ab
    emit(f"  abbreviation tests: " + "; ".join(f"{w}->{a} (want {e})" for w, a, e in tres) + f" -> {'ok' if ok_ab else 'BAD'}")
    emit(f"FXa encoders/decoders: {'PASS' if ok_a else 'FAIL'}")
    flush()
    # FXb lag-2 on the block pipeline
    thr = LAG2_FACTOR * float(np.mean(list(s81_reference().values())))
    skp = fx_lag2_pages("fo", 11)
    skel = [[len(l) for l in ls] for _, ls in skp]
    s81p = S81.encipher(S81.plain_letters("latin_cremma"), S81.key_tables(), skel, "line", S91.STICKY_P, seed=S81.FIX_SEED,
                        start=S81.FIX_PLAIN_START)
    jobs = lag2_jobs("FX_state", 1, [(pid, s81p[i]) for i, (pid, _) in enumerate(skp)]) + lag2_jobs("FX_fo", 2, fx_lag2_pages("fo", 12))
    R = lag2_pool(jobs, "fixture lag-2")
    s1, s2 = lag2_summary("FX_state", R), lag2_summary("FX_fo", R)
    fxb = s1["residue"] > thr and s2["residue"] <= thr and not s1["errors"] and not s2["errors"]
    emit(f"FXb lag-2 bar {thr * 1000:.3f} e-3 bits: s81 line-sticky residue {s1['residue'] * 1000:+.3f} (pos {s1['pos']}/{s1['n']}); "
         f"first-order residue {s2['residue'] * 1000:+.3f} (pos {s2['pos']}/{s2['n']}) -> {'PASS' if fxb else 'FAIL'}")
    flush()
    # FXc survivor path on a synthetic world; FXd pools
    names, glob, B, spec = S91.fx_world()
    prod = S91.LP91(glob, B); prod.set_params(S91.PLANTED)
    cp = prod.text(spec, 1)
    rr = np.random.default_rng(9)
    wp = [(pid, q, [[["", "q", "o", "qo"][int(rr.integers(4))] + c + ["", "y", "dy", "n"][int(rr.integers(4))] for c in l] for l in ls])
          for (pid, ls), (_, q, _) in zip(cp, spec)]
    if True:
        fake_ref = OrderedDict((T, wp) for T in TRANSLITS)
        folds = S67.folds_of(wp)[:1]
        cm = dict(name="FXc_G1b", constr="G1b", func=S102.FUNC_LA, pi=1, seg=words[:N_TOT], units=words[:N_TOT])
        cma = dict(name="FXc_G1a", constr="G1a", func=S102.FUNC_LA, pi=1, seg=words[:12000], units=G1A.units(words[:12000]))
        lb = (0.9074, 1.0499)
        try:
            sv = survivor_run_fx([cm, cma], lb, fake_ref, folds)
            fxc = all(len(sv[c]["ZL3b"]["rows"]) == 1 for c in sv)
            for c, per in sv.items():
                emit(f"  [FXc] {c}: " + "; ".join(f"{T} " + " ".join(f"{r['Q']} sig {r['flags']} bat {r['bat']}/6" for r in v["rows"]) for T, v in per.items()))
        except Exception:  # noqa: BLE001
            emit("FXc ERROR " + traceback.format_exc())
            fxc = False
    emit(f"FXc survivor path end to end: {'PASS' if fxc else 'FAIL'}")
    fxd = bool(R) and all("excess" in v for v in R.values())
    emit(f"FXd pools returned (lag-2 {len(R)} jobs ok {fxd}; battery via FXc) -> {'PASS' if fxd and fxc else 'FAIL'}")
    ah, ai = affix_profile(fx_aff_pages(True, 31), SEED + 31), affix_profile(fx_aff_pages(False, 32), SEED + 32)
    fxe = ah["suf"]["C"] > 1 and ah["suf"]["pC"] < 0.05 and 0.95 <= ai["suf"]["C"] <= 1.05
    emit(f"FXe affix profile: held-suffix {fmt_aff(ah)}")
    emit(f"    IID {fmt_aff(ai)} -> {'PASS' if fxe else 'FAIL'}")
    emit(f"FIXTURE {'PASS' if (ok_a and fxb and fxc and fxd and fxe) else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


def survivor_run_fx(cells_meta, lb, ref, folds):
    """fixture wrapper: the survivor scoring on a synthetic reference (one translit key per entry)."""
    return survivor_run(cells_meta, lb, ref, folds, "fixture survivor")


def enc_code(c, t):
    enc = c["enc"]
    _, core, _ = enc.parse(t)
    return core in enc.core_idx


# ======================================================================= main
def load_plaintexts():
    p1_lines, n_med = S102.load_p1()
    W = OrderedDict()
    W["P1_la"] = [w for ln in p1_lines for w in ln]
    for key in ("P2_it", "P3_de"):
        W[key] = S102.load_period(key)
    return W


def build_all(W, line_lens, page_nl):
    CELLS = OrderedDict()
    for pi, (key, words) in enumerate(W.items()):
        for xi, constr in enumerate(CONSTR):
            for twin in (False, True):
                name = f"{key}_{constr}{'_shuf' if twin else ''}"
                c = build_cell(words, constr, FUNC[key], pi + 1, xi, twin, line_lens, page_nl)
                c.update(name=name, key=key, constr=constr, twin=twin, pi=pi + 1, func=FUNC[key])
                CELLS[name] = c
    return CELLS


def run_wellformed():
    emit("S104 WELL-FORMEDNESS CHECK (pre-freeze; only alphabets and counts; no statistic, no recovery)")
    emit(f"date: {S87.clock()}")
    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]
    W = load_plaintexts()
    for k, w in W.items():
        emit(f"  plaintext {k}: {len(w)} words available")
    CELLS = build_all(W, line_lens, page_nl)
    for n, c in CELLS.items():
        t, nl, npg = counts(c["enc_pages"])
        alph = alphabet(c["enc_pages"])
        emit(f"  {n:18s} segment words {len(c['seg'])} (enough {c['enough']}); units {len(c['units'])}; cipher tokens {t} lines {nl} "
             f"pages {npg}; alphabet {len(alph)} '{alph}'")
    emit(f"finished {S87.clock()}")
    flush()


def main():
    global OUT
    if LIST_LOCALS:
        for m in stub_files():
            print(m)
        return
    OUT = pick_out()
    if FIXTURE:
        run_fixture()
        return
    if WELLFORMED:
        run_wellformed()
        return
    emit("S104: grid G1 (G1a verbose syllabary, G1b line-table nomenclator, G1c abbreviate-then-G1b) x 3 period recipe "
         "plaintexts, each with a shuffled-plaintext twin, vs the D-066 (j) joint profile (pre-registered in the docstring)")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; BelowNormal set={S87.below_normal()}; workers {N_WORKERS}")
    emit(f"s104_g1_encoding_grid.py sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    REF81 = s81_reference()
    THR = LAG2_FACTOR * float(np.mean(list(REF81.values())))
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH}; K_ROWS {K_ROWS}; NC {NC} x D {D_TIERS}; REC_MIN {REC_MIN}; H2 band {H2_BAND}; "
         f"rhythm p < {RHY_P}; LAG2: s81 reference (results_s98.txt) " + ", ".join(f"{T} {v * 1000:+.3f}" for T, v in REF81.items())
         + f" e-3 bits, mean {np.mean(list(REF81.values())) * 1000:.3f}, bar = {LAG2_FACTOR} x mean = {THR * 1000:.3f} e-3 bits; seed {SEED}")
    flush()

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    def lay_tokens(toks):
        return S87.layout(toks, False, None, line_lens, page_nl)

    # ---- Voynich target
    emit("\n=== Voynich target (SlotSegmenter cores, s87 seeds; rhythm; h2 at the same 22,500-token cut) ===")
    VOY = OrderedDict()
    for i, T in enumerate(TRANSLITS):
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        pages = S87.layout(None, True, P, line_lens, page_nl)
        VOY[T] = (pages, S97.profile_g(f"VOY_{T}", pages, SlotSegmenter, N_MATCH, S87.SEED + 100 * i))
    lb = S87.loc_band_from([v[1] for v in VOY.values()])
    rw_v = float(np.mean([v[1]["rep"][1]["Rw"] for v in VOY.values()])); rc_v = float(np.mean([v[1]["rep"][1]["Rc"] for v in VOY.values()]))
    emit(f"LOCALITY band: [{lb[0]:.4f}, {lb[1]:.4f}]")
    for i, (T, (pages, p)) in enumerate(VOY.items()):
        rh = S102.rhythm(pages, SEED + 7 + i)
        emit("  " + S97.fmt(p, lb) + f" | rhythm exc {rh['excess']:+.4f} p {rh['p']:.3f} | h2 {S102.h2_of(pages):.4f}")
    flush()

    # ---- plaintexts and cells
    emit("\n=== plaintexts and the 18 encoded texts ===")
    W = load_plaintexts()
    for k, w in W.items():
        emit(f"  plaintext {k}: {len(w)} words available; first words: {' '.join(w[:12])}")
    CELLS = build_all(W, line_lens, page_nl)
    REC = OrderedDict()
    for n, c in CELLS.items():
        REC[n] = recovery(c)
        t, nl, npg = counts(c["enc_pages"])
        extra = ""
        if c["constr"] != "G1a":
            cs = sum(1 for _, ls in c["enc_pages"] for ln in ls for tk in ln if enc_code(c, tk)) / t
            extra = f"; code-token share {cs:.3f}; spelled collisions {c['enc'].ciph.collisions}"
        if c["constr"] == "G1a":
            extra = f"; syllable types {c['enc'].n_types}"
        if c["constr"] == "G1c":
            extra += f"; majority-expansion accuracy {expansion_accuracy(c['seg']):.3f}"
        emit(f"  {n:18s} words {len(c['seg'])} (enough {c['enough']}) units {len(c['units'])} | tokens {t} lines {nl} pages {npg} | "
             f"alphabet {len(alphabet(c['enc_pages']))} | recovery {REC[n]:.4f}{extra}")
        emit(f"       first line: {' '.join(c['enc_pages'][0][1][0])}   <- {' '.join(c['units_pages'][0][1][0])}")
    G_R = all(v >= REC_MIN for v in REC.values()) and all(c["enough"] for c in CELLS.values())
    emit(f"  R recovery >= {REC_MIN} on all 18 (and every segment long enough): {G_R} (min {min(REC.values()):.4f})")
    flush()

    TEXTS = OrderedDict((n, ("cell" if not c["twin"] else "twin", c["enc_pages"], list(TRANSLITS))) for n, c in CELLS.items())

    # ---- S: s97 gate
    emit("\n=== S: s97 gate (PC1 planted LP91, PC2 IT2a as control, NC plain Latin), s97 code and constants ===")
    aug = S87.load_control("latin_augustine.txt")
    for T in TRANSLITS:   # A1 target calibration through the same cell criteria code
        TEXTS[f"VOY_{T}"] = ("target", VOY[T][0], list(TRANSLITS))
    TEXTS["PC2_VOY_IT2a_as_control"] = ("gate", VOY["IT2a"][0], ["IT2a"])
    TEXTS["NC_augustine_la"] = ("gate", lay_tokens(aug), list(TRANSLITS))
    zp = S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS['ZL3b']}.meta.json")
    segz = SlotSegmenter([w for _, _, ls in zp for l in ls for w in l])
    zcp = [(p, q, [[segz.segment(w)[1] for w in l] for l in ls]) for p, q, ls in zp]
    glob = Counter(c for _, _, ls in zcp for l in ls for c in l if c != "")
    prod = S91.LP91(glob, S91.bigram_of([(p, [[c for c in l if c != ""] for l in ls]) for p, q, ls in zcp]))
    prod.set_params(S91.PLANTED)
    spec = [(p, q, [len(l) for l in ls]) for p, q, ls in zp]
    pc1 = []
    for s in (1, 2, 3):
        pages = S91.cut(prod.text(spec, S97.SEED + s))
        p = S97.profile_g(f"PC1_LP91_planted_s{s}", pages, S80.identity_seg_factory, N_MATCH, S97.SEED + 10 + s)
        pc1.append(S97.flags(p, lb)[0])
        emit("  " + S97.fmt(p, lb))
    PC1 = sum(pc1) >= S97.PC1_MIN
    emit(f"  PC1 Voynich-like on {sum(pc1)}/3 seeds (need >= {S97.PC1_MIN}) -> {PC1}")
    flush()

    # ---- signature profiles
    emit("\n=== SIG profiles (flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PR = OrderedDict()
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        PR[n] = OrderedDict()
        segs = ["slot"] if n.startswith("PC2") else list(SEGS)
        for si, sn in enumerate(segs):
            p = S97.profile_g(f"{n}/{sn}", pages, SEGS[sn], N_MATCH, SEED + 1000 * xi + 100 * si)
            PR[n][sn] = p
            app = p["core_share"] >= MIN_CORE_SHARE
            emit("  " + S97.fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}{'' if app else ' [NOT APPLICABLE: core share < 0.5]'}"))
            flush()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---- rhythm and h2
    emit("\n=== RHY (within-line lag-1 length Moran I vs 999 within-line shuffles) and H2 ===")
    RH, H2 = OrderedDict(), OrderedDict()
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        RH[n] = S102.rhythm(pages, SEED + 5000 + xi)
        H2[n] = S102.h2_of(pages)
        emit(f"  {n:26s} I {RH[n]['I']:+.4f} null median {RH[n]['median']:+.4f} excess {RH[n]['excess']:+.4f} p {RH[n]['p']:.3f} -> "
             f"{RH[n]['holds']} | h2 {H2[n]:.4f} in [{H2_BAND[0]}, {H2_BAND[1]}] -> {H2_BAND[0] <= H2[n] <= H2_BAND[1]}")
    flush()

    # ---- LAG2 (cells + L gate texts)
    emit(f"\n=== LAG2: s98 prefix XCMI (K {S98.K_MAIN}, same-length null, M {S98.M_NULL}) leave-one-block-out, residue = median "
         f"excess over 15 blocks; bar {THR * 1000:.3f} e-3 bits ===")
    skel_pages = VOY["ZL3b"][0]
    skel = [[len(l) for l in ls] for _, ls in skel_pages]
    s81 = S81.encipher(S81.plain_letters("latin_cremma"), S81.key_tables(), skel, "line", S91.STICKY_P,
                       seed=S81.gen_seed("line_sticky75", "latin_cremma", 1))
    L_TEXTS = OrderedDict()
    for n, c in CELLS.items():
        L_TEXTS[n] = c["enc_pages"]
    for T, (pages, _) in VOY.items():
        L_TEXTS[f"VOY_{T}"] = pages
    L_TEXTS["S81_line_sticky75"] = [(pid, s81[i]) for i, (pid, _) in enumerate(skel_pages)]
    jobs = []
    for xi, (n, pages) in enumerate(L_TEXTS.items()):
        jobs += lag2_jobs(n, xi, pages)
    LR = lag2_pool(jobs, "lag-2")
    LAG = OrderedDict()
    for n in L_TEXTS:
        LAG[n] = lag2_summary(n, LR)
        LAG[n]["holds"] = bool(np.isfinite(LAG[n]["residue"]) and LAG[n]["residue"] <= THR and not LAG[n]["errors"])
        emit(f"  {n:26s} residue {LAG[n]['residue'] * 1000:+.3f} e-3 bits (blocks {LAG[n]['n']}, positive {LAG[n]['pos']}/15"
             f"{', ERRORS ' + str(LAG[n]['errors']) if LAG[n]['errors'] else ''}) -> <= bar {LAG[n]['holds']}")
    G_L = all(LAG[f"VOY_{T}"]["holds"] for T in TRANSLITS) and (not LAG["S81_line_sticky75"]["holds"]) \
        and not LAG["S81_line_sticky75"]["errors"]
    emit(f"  (preliminary, absolute bar; final L after A1 calibration) L lag-2 validity: VOY all <= bar {all(LAG[f'VOY_{T}']['holds'] for T in TRANSLITS)}; s81 table > bar "
         f"{not LAG['S81_line_sticky75']['holds']} -> {G_L}")
    flush()

    # ---- battery
    emit("\n=== BAT: s67 slot battery (text block b vs real Voynich fold folds[b]) ===")
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    emit(f"  folds ({len(folds)}): {' '.join(folds)}")
    assert len(folds) == NB
    jobs = S97.ref_jobs(ref, folds)
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        jobs += S97.ctl_jobs(n, xi + 1, pages)
    M = battery_pool(jobs, "battery")
    BAT = OrderedDict()
    for n, (role, pages, Ts) in TEXTS.items():
        BAT[n] = S97.battery_score(n, Ts, M, ref, folds, pages)
        for T, r in BAT[n].items():
            emit(f"  {n:26s} " + S97.bat_line(T, r))
    flush()

    # ---- calls
    emit("\n=== A1 target calibration: the manuscript through the same criteria (absolute rules) ===")
    VOYN = [f"VOY_{T}" for T in TRANSLITS]
    REL_SIG = {sn: any(not S97.flags(PR[v][sn], lb)[0] for v in VOYN) for sn in SEGS}
    REL_BAT = {T: any(not BAT[v][T]["holds"] for v in VOYN) for T in TRANSLITS}
    REL_RHY = any(not RH[v]["holds"] for v in VOYN)
    REL_H2 = any(not (H2_BAND[0] <= H2[v] <= H2_BAND[1]) for v in VOYN)
    REL_LAG = any(not LAG[v]["holds"] for v in VOYN)
    h2b = (min([H2_BAND[0]] + [H2[v] for v in VOYN]), max([H2_BAND[1]] + [H2[v] for v in VOYN])) if REL_H2 else H2_BAND
    bat_min = {T: min(BAT[v][T]["folds_ok"] for v in VOYN) for T in TRANSLITS}
    rhy_min = min(RH[v]["excess"] for v in VOYN)
    pooled = [x["excess"] for (nm, q), x in LR.items() if nm in VOYN and "excess" in x]
    THR_USED = float(np.percentile(pooled, LAG2_REL_Q)) if REL_LAG else THR
    for v in VOYN:
        emit(f"  {v}: SIG " + " ".join(f"{sn}:{S97.flags(PR[v][sn], lb)[2]}" for sn in SEGS) + " | BAT "
             + " ".join(f"{T} {BAT[v][T]['folds_ok']}/15" for T in TRANSLITS) + f" | RHY {RH[v]['excess']:+.4f} p {RH[v]['p']:.3f} | h2 {H2[v]:.4f}"
             f" | LAG2 {LAG[v]['residue'] * 1000:+.3f}")
    emit(f"  TARGET-RELATIVE criteria (manuscript fails the absolute rule): SIG {[sn for sn, v in REL_SIG.items() if v] or 'none'}; "
         f"BAT {[T for T, v in REL_BAT.items() if v] or 'none'} (min VOY folds {bat_min}); RHY {REL_RHY} (min excess {rhy_min:+.4f}); "
         f"H2 {REL_H2} (band {h2b[0]:.4f}, {h2b[1]:.4f}); LAG2 {REL_LAG} (bar used {THR_USED * 1000:.3f} e-3 bits)")
    vfold = {}
    for v in VOYN:
        sigv = S97.flags(PR[v]["slot"], lb)[0]
        for T in TRANSLITS:
            vfold[(v, T)] = sum(1 for r in BAT[v][T]["rows"] if sigv and r["n"] >= BAT_FOLD_MIN)
    LOQO_BAR = {T: (min(vfold[(v, T)] for v in VOYN) if any(vfold[(v, T)] < LOQO_MIN for v in VOYN) else LOQO_MIN) for T in TRANSLITS}
    emit(f"  survivor fold rule on the manuscript (slot SIG and battery row >= 4/6): " + "; ".join(f"{v} vs {T} {vfold[(v, T)]}/15" for v in VOYN for T in TRANSLITS))
    emit(f"  survivor LOQO bar per T: {LOQO_BAR}")
    for n in list(LAG):
        LAG[n]["holds"] = bool(np.isfinite(LAG[n]["residue"]) and LAG[n]["residue"] <= THR_USED and not LAG[n]["errors"])
    G_L = (all(LAG[v]["holds"] for v in VOYN) or REL_LAG) and LAG["S81_line_sticky75"]["residue"] > THR_USED \
        and not LAG["S81_line_sticky75"]["errors"]
    emit(f"  L lag-2 validity with the bar used ({THR_USED * 1000:.3f}): VOY <= bar {[LAG[v]['holds'] for v in VOYN]}; "
         f"s81 table {LAG['S81_line_sticky75']['residue'] * 1000:+.3f} > bar -> {G_L}")
    VPR = [PR[v] for v in VOYN]
    emit("\n=== calls ===")
    DESC, PASS = OrderedDict(), OrderedDict()
    for n, (role, pages, Ts) in TEXTS.items():
        segs = list(PR[n])
        app = [sn for sn in segs if PR[n][sn]["core_share"] >= MIN_CORE_SHARE]
        sig = {}
        for sn in segs:
            if REL_SIG.get(sn) and role in ("cell", "twin"):
                ok, fl = sig_rel(PR[n][sn], [q[sn] for q in VPR])
                sig[sn] = (ok, None, fl + "*")
            else:
                sig[sn] = S97.flags(PR[n][sn], lb)
        sig_ok = bool(app) and all(sig[sn][0] for sn in app)
        bat_ok = all((BAT[n][T]["folds_ok"] >= bat_min[T]) if (REL_BAT[T] and role in ("cell", "twin")) else BAT[n][T]["holds"] for T in Ts)
        rhy_ok = (RH[n]["excess"] >= rhy_min) if (REL_RHY and role in ("cell", "twin")) else RH[n]["holds"]
        h2_ok = h2b[0] <= H2[n] <= h2b[1]
        lag_ok = LAG[n]["holds"] if n in LAG else None
        PASS[n] = bool(sig_ok and bat_ok and rhy_ok and h2_ok and lag_ok) if role in ("cell", "twin", "target") else None
        DESC[n] = dict(role=role, applicable=app, sig={sn: sig[sn][2] for sn in segs}, sig_ok=sig_ok, battery={T: BAT[n][T]["folds_ok"] for T in Ts},
                       battery_ok=bat_ok, rhythm=dict(excess=RH[n]["excess"], p=RH[n]["p"], holds=rhy_ok), h2=H2[n], h2_ok=h2_ok,
                       lag2=(LAG[n]["residue"] if n in LAG else None), lag2_ok=lag_ok, s97_full=sig_ok and bat_ok, PASS=PASS[n],
                       recovery=REC.get(n))
    PC2 = DESC["PC2_VOY_IT2a_as_control"]["s97_full"]
    NC_ok = not DESC["NC_augustine_la"]["s97_full"]
    G_S = PC1 and PC2 and NC_ok
    GATE = G_R and G_S and G_L
    emit(f"  R recovery {G_R}; S s97 gate (PC1 {PC1}, PC2 {PC2}, NC {NC_ok}) {G_S}; L lag-2 validity {G_L}")
    emit(f"  CALL_S104_GATE = {GATE}")
    emit("\n  CELL TABLE (plaintext row, then its shuffled twin): SIG flags id/slot/affix2 | BAT folds ZL3b/RF1b/IT2a | RHY excess,p | "
         "h2 | LAG2 residue e-3 | rec | PASS")
    plain = [n for n, c in CELLS.items() if not c["twin"]]
    for n in plain + []:
        for m in (n, n + "_shuf"):
            d = DESC[m]
            emit(f"   {m:18s} SIG {'/'.join(d['sig'].values())} {'Y' if d['sig_ok'] else 'n'} | BAT {'/'.join(str(v) for v in d['battery'].values())} "
                 f"{'Y' if d['battery_ok'] else 'n'} | RHY {d['rhythm']['excess']:+.4f},{d['rhythm']['p']:.3f} {'Y' if d['rhythm']['holds'] else 'n'} | "
                 f"h2 {d['h2']:.3f} {'Y' if d['h2_ok'] else 'n'} | LAG2 {d['lag2'] * 1000:+.2f} {'Y' if d['lag2_ok'] else 'n'} | rec {d['recovery']:.3f} | "
                 f"{'PASS' if d['PASS'] else '-'}")
    hits = [n for n in plain if PASS[n]]
    twin_hits = [n + "_shuf" for n in plain if PASS[n + "_shuf"]]
    ANY = GATE and bool(hits)
    emit(f"  CALL_S104_ANY_PASS = {ANY}")
    for n in plain:
        emit(f"  TWIN_PASS({n}) = {PASS[n + '_shuf']}")
    flush()

    # ---- survivor test
    SV = OrderedDict()
    if ANY:
        emit("\n=== SURVIVOR TEST (LOQO, fitted tables, plaintext vs shuffled twin) ===")
        emit("  A2 unused predictions (calibration on the manuscript first):")
        AFF = OrderedDict()
        for i, v in enumerate(VOYN):
            AFF[v] = affix_profile(TEXTS[v][1], SEED + 600 + i)
            emit(f"   {v:18s} {fmt_aff(AFF[v])} | PRED_B {pred_b(PR[v], VPR)}")
        for i, n in enumerate(hits):
            for m in (n, n + "_shuf"):
                AFF[m] = affix_profile(TEXTS[m][1], SEED + 700 + i)
                emit(f"   PRED_A({m}) = {AFF[m]['holds']}: {fmt_aff(AFF[m])}")
                emit(f"   PRED_B({m}) = {pred_b(PR[m], VPR)[0]}: {pred_b(PR[m], VPR)[1]}")
        flush()
        metas = []
        for n in hits:
            for m in (n, n + "_shuf"):
                c = CELLS[m]
                metas.append(dict(name=m, constr=c["constr"], func=c["func"], pi=c["pi"], seg=c["seg"], units=c["units"]))
        SV = survivor_run(metas, lb, ref, folds, "survivor battery")
        for m, per in SV.items():
            for T, v in per.items():
                emit(f"  {m:18s} {T}: held {v['held']}/15 | " + " ".join(f"{r['Q']}:{r['flags']}/{r['bat']}{'*' if r['holds'] else ''}" for r in v["rows"]))
        flush()
    SURV, STRUCT, HELDFAIL = [], [], []
    for n in hits:
        if not SV:
            break
        loqo = all(SV[n][T]["held"] >= LOQO_BAR[T] for T in TRANSLITS)
        beat = sum(SV[n][T]["held"] for T in TRANSLITS) > sum(SV[n + "_shuf"][T]["held"] for T in TRANSLITS)
        emit(f"  {n}: LOQO = {loqo}; BEAT = {beat}; SURVIVOR = {loqo and beat}; twin passes criteria = {PASS[n + '_shuf']}")
        if loqo and beat:
            SURV.append(n)
        elif (loqo and not beat) or PASS[n + "_shuf"]:
            STRUCT.append(n)
        else:
            HELDFAIL.append(n)
    if ANY:
        emit(f"  CALL_S104_SURVIVOR = {bool(SURV)}")

    if not GATE:
        why = [k for k, v in (("R recovery", G_R), ("S PC1", PC1), ("S PC2", PC2), ("S NC", NC_ok), ("L lag-2 validity", G_L)) if not v]
        reading = f"uninformative: gate failed ({', '.join(why)})"
    elif not hits:
        reading = ("no plaintext cell passes: table-driven verbose encodings of real recipe text are closed within G1; the grid moves "
                   "to the H-05/H-07 side (procedure without plaintext) (D-066 (j) stopping rule)")
        if twin_hits:
            reading += f"; shuffled twins passing: {', '.join(twin_hits)} (H-05/H-07 pointer)"
    elif SURV:
        reading = (f"survivor {', '.join(SURV)}: predicts held-out quires and beats its shuffled twin (H-14/H-06); a decipherment "
                   "candidate must first predict the Phase 7.2 cribs")
    elif STRUCT:
        reading = f"structure without content ({', '.join(STRUCT)}): do not attempt decipherment (D-066 (j) stopping rule)"
    else:
        reading = (f"passes in-sample but does not predict held-out quires ({', '.join(HELDFAIL)}): closed within G1 (failed property: "
                   "held-out prediction)")
    emit(f"\nVERDICT: CALL_S104_GATE = {GATE}; CALL_S104_ANY_PASS = {ANY}: {reading}")
    flush()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "profiles.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "segmenter", "tokens", "types", "core_share", "o100", "p100", "o200", "Rw1", "pRw1", "Rc1", "loc", "C1", "flags"])
        rows = [(f"VOY_{T}", "slot", v[1]) for T, v in VOY.items()] + [(n, sn, p) for n in PR for sn, p in PR[n].items()]
        for n, sn, p in rows:
            o, r, l = p["order"], p["rep"], p["loc"]
            ok, _, fl = S97.flags(p, lb)
            w.writerow([n, sn, p["tokens"], p["types"], f"{p['core_share']:.4f}", f"{o[100]['mm']:.6f}", f"{o[100]['p']:.4f}",
                        f"{o[200]['mm']:.6f}", f"{r[1]['Rw']:.4f}", f"{r[1]['pw']:.4f}", f"{r[1]['Rc']:.4f}", f"{l['ratio']:.4f}", ok, fl])
    with (RUN_DIR / "lag2.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "block", "excess", "p", "obs", "n_tok", "n_triples", "error"])
        for (n, q), v in sorted(LR.items()):
            w.writerow([n, q, v.get("excess"), v.get("p"), v.get("obs"), v.get("n_tok"), v.get("n_triples"), "error" in v])
    with (RUN_DIR / "battery.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "T", "fold", "n"] + S67.PREDS)
        for n in BAT:
            for T, r in BAT[n].items():
                for x in r["rows"]:
                    w.writerow([n, T, x["Q"], x["n"]] + [x["holds"][k] for k in S67.PREDS])
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(loc_band=lb, order_band=S87.ORDER_BAND, h2_band=H2_BAND, lag2_ref=REF81, lag2_bar=THR,
                                                        G_R=G_R, recovery=REC, PC1=PC1, PC1_seeds=pc1, PC2=PC2, NC=NC_ok, G_S=G_S, G_L=G_L,
                                                        lag2={n: v for n, v in LAG.items()}, GATE=GATE, CALL_S104_ANY_PASS=ANY, desc=DESC,
                                                        survivor=SV, survivors=SURV, structure_only=STRUCT, heldout_fail=HELDFAIL, verdict=reading),
                                                   indent=1, default=str), encoding="utf-8", newline="\n")
    for n, c in CELLS.items():
        if c["twin"]:
            continue
        enc = c["enc"]
        key = dict(rows=list(zip(ROW_PFX, ROW_SFX)), code=enc.code) if c["constr"] == "G1a" else \
            dict(cores=enc.cores, ranked=enc.ranked[:NC * D_TIERS], pfx=PFX_B, sfx=SFX_B, suf_t=enc.suf_t.tolist(),
                 homophones=enc.ciph.homo, nulls=enc.ciph.nulls)
        (RUN_DIR / f"key_{n}.json").write_text(json.dumps(key, ensure_ascii=False, indent=0), encoding="utf-8", newline="\n")
    emit("\nsidecars: runs/s104/profiles.csv, runs/s104/lag2.csv, runs/s104/battery.csv, runs/s104/calls.json, runs/s104/key_<cell>.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


if __name__ == "__main__":
    main()
