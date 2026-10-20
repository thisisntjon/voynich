#!/usr/bin/env python
"""
S34: superimposed-streams check (Phase 3; sibling of s24_music_seriation.py).

PRE-REGISTRATION (frozen in s34_superimposed_streams.prereg.sha256 BEFORE the first run).

Hypothesis (Jon, verbatim): "the music and the words may be superimposed on top of each other",
i.e. two streams interleaved in one glyph string: some glyph classes carry pitch, the rest carry
words, mixed within words.

Cap: `python -I`, one CPU process, no GPU, no paid calls, no new data; expected < 5 min; HARD STOP
15 min wall clock enforced by a watchdog that writes what it has (copied from s24) plus in-loop
checks.  Writes ONLY results_s34.txt.  The script hashes itself against the stub and prints
stub_match in the header.

Corpora (existing sidecars only, loaded with scoreboard/run_v2.load_meta imported by path, as s24):
  Voynich: data/translit/ZL3b_eva, RF1b, IT2a (EVA characters; lines as in the sidecar).
  Negative controls (same search, same rules): gib_realline_pooled, c2_best, schwartz_reuse,
    timm_schinner, flow_gen_layer, mhg_nibelungenlied, italian_dante.
  Positive control (P3): a planted corpus built IN MEMORY from cremma_all real lines (never written).

DESIGN (verbatim from the task; the only scoring rules)

Glyph classes: use the project's slot classes (gallows k/t/p/f and their bench-gallows forms,
benches ch/sh, e-group e/ee/eee, o/a, i-group, finals n/r/l/m/g/s, d, y, q; take the exact class
list from the SlotSegmenter or b3; print it).  Partition search: every 2-partition of the C classes
into stream M (music) and stream W (words), M non-empty and W non-empty (2^C - 2 partitions; if
C > 12, restrict to partitions where M has <= 4 classes and state so).  For each partition, strip M
glyphs from every token (keep line and word boundaries; drop empty tokens) and compute on the W
residual: h2 (same estimator as s24, 25k-token cap), type count at 25k tokens, hapax share; on the
M stream (sequence of M glyphs per line): alphabet size, within-line lag-1 autocorrelation of
M-glyph identity (Cramer's V or mutual information between successive M glyphs) and its
line-shuffle null (200 draws).

Fixed predictions: P1 Residual-is-language: there exists a partition whose W residual has h2 inside
the real-line language range (from s17/s18 rows, print it), types_25k <= 3000 and hapax <= 0.50.
P2 Stream-is-melody: for that same partition (best by P1 score, declared: minimise |h2 - language
midpoint| subject to the type/hapax conditions) the M stream's within-line successive-glyph MI
exceeds its line-shuffle null 99th percentile.  P3 Positive-control recovery: build in memory a
planted corpus from cremma_all real lines: insert one of K=5 synthetic pitch symbols after each
vowel-group (syllable proxy) with a Markov contour (p stay 0.5, step +-1 0.2 each, jump 0.1); run
the same search with the 5 pitch symbols as one extra class; PASS if the search's best partition
puts exactly the pitch class in M and the residual reproduces cremma_all's h2 within 0.05.
Negative controls: the same search on gib_realline_pooled, c2_best, schwartz_reuse, timm_schinner,
flow_gen_layer, mhg_nibelungenlied, italian_dante; report each control's best P1 score and whether
it satisfies P1/P2, so the Voynich result has a margin.  Verdict rule: "superimposed streams
SUPPORTED" only if P3 passes AND P1 and P2 pass for Voynich on all three transliterations (ZL3b,
RF1b, IT2a) AND no negative control satisfies P1+P2; "NOT SUPPORTED" otherwise; "TEST INVALID" if
P3 fails.  Print margins everywhere.

Amendment 1 (pre-run, 21:28 PDT, coordinator; recorded before any run; the original stub hash is
kept as a SUPERSEDED comment line in the .prereg.sha256).  Reason found while reading the sidecars
before the first freeze: at 25k tokens the five language rows have 3478-8626 types and hapax
0.074-0.248 (cremma_all 8626 / 0.248, italian_dante 5249 / 0.133, mhg_nibelungenlied 3478 / 0.074),
so the fixed bound types_25k <= 3000 was stricter than every language control and the P3 pitch-only
residual (= cremma_all) could not meet P1; and the |h2 - midpoint| selector does not favour the
true partition.  Two design changes:
(1) P1 conditions become relative to the language rows: h2 inside the language range as before;
    types_25k inside [min, max] of the five language rows (s17 mhg/dante/roland/croisade + s18
    cremma_all, computed at run time from their sidecars with the same 25k convention and
    printed); hapax_25k <= the maximum of those five rows.  The fixed 3000 / 0.50 constants are
    dropped.
(2) Selector: the superimposition claim is that M and W are independent streams, so among
    partitions satisfying P1 choose argmax S = I_self - I_cross, where I_self = plug-in MI between
    successive M glyphs within a line (across token boundaries, as before) and I_cross = plug-in
    MI between each M glyph and its immediately preceding W glyph in the same line (first-in-line
    M glyphs paired with a boundary symbol).  Ties: fewer M classes, then class order.  Fallback
    if nothing satisfies P1: unconstrained argmax S with P1 FAIL.  P2 becomes: on the selected
    partition, I_self exceeds its 200-draw within-line line-shuffle null 99th percentile AND S > 0
    (I_self > I_cross).  P3 unchanged in form: PASS iff the selected M == {PITCH} exactly and
    |residual h2 - h2(cremma_all)| <= 0.05; also print the rank of the PITCH-only partition under
    S and its S value.  Negative controls and the verdict rule unchanged.  S, I_self, I_cross are
    printed for the selected and PITCH-only partitions everywhere.
Where the verbatim design text above and Amendment 1 disagree (P1 thresholds, selector, P2 rule),
Amendment 1 governs; the operational definitions below are written to the amended rules.

OPERATIONAL DEFINITIONS (declared here, fixed)

Class list.  The project has no stored glyph-class table: metrics_new.SlotSegmenter induces
  prefix/core/suffix strings from the data and carries no class list; the only class constant in the
  project is b3_slot_claims.py GALLOWS = set("tkpf") (read as text at run time and printed).  The
  class list is therefore declared here, following the task's enumeration, and printed:
    GALLOWS      k t p f                     (b3 GALLOWS)
    BENCHGALLOWS ckh cth cph cfh             (bench-gallows forms)
    BENCH        ch sh
    E            e+  (a maximal run of e is ONE glyph: e, ee, eee, ...)
    OA           o a
    I            i+  (a maximal run of i is ONE glyph)
    FINAL        n r l m g s
    D            d
    Y            y
    Q            q
    PITCH        the 5 planted symbols (planted corpus only; absent from every sidecar; checked)
  Every other character (EVA x b j u z v, a stray c or h outside a bench, and any non-EVA character
  of the Latin/MHG/Italian/gibberish controls) is OTHER: it is never a slot class, it always stays
  in W, and its share of characters is printed per corpus.  Tokens are parsed left to right with
  the regex  ckh|cth|cph|cfh|ch|sh|e+|i+|[ktpf]|[oa]|[nrlmgs]|d|y|q|[PITCH]|.  (longest listed
  alternative first).  The same literal parser is applied to every corpus (Voynich, generators,
  language controls, gibberish, planted): the control search is the identical procedure, not a
  re-tuned one.  C = the number of declared classes present in a corpus (C = 10 for Voynich if all
  ten occur; C = 11 for the planted corpus); the partition count 2^C - 2 is printed per corpus.
  C never exceeds 12, so the <= 4-class restriction is never triggered (stated per corpus).

Strip.  For a partition (M, W): every glyph whose class is in M is deleted from its token; the
  remaining glyphs keep their order and concatenate into the residual token; empty residual tokens
  are dropped (count printed); line boundaries and word boundaries are unchanged.

W residual metrics (first 25,000 non-empty residual tokens in reading order, run_v2 DEFAULT_N):
  h2 = s24 h2_of convention (a1_profile.char_entropies): H(char pair) - H(char) on
       " ".join(words) + " " over those tokens, space included as a symbol, plug-in, bits.
       Computed with a numpy bincount implementation of the same formula during the search; the
       s24 string/Counter implementation is re-run on the chosen partition and the difference
       printed (h2_check; must be < 1e-9).
  types_25k = number of distinct residual types among those tokens.
  hapax = share of those tokens whose type occurs exactly once among them.
  Language h2 range = [min, max] of "row"["h2"] over results_s17_mhg_nibelungenlied.json,
       results_s17_italian_dante.json, results_s17_oldfrench_roland.json,
       results_s17_occitan_croisade.json, results_s18_cremma_all.json (as s24 P3).  Printed.
  Language types/hapax range (Amendment 1): types_25k and hapax_25k computed at run time, with
       the conventions above, on the five language sidecars data/controls_realline/
       {mhg_nibelungenlied, italian_dante, oldfrench_roland, occitan_croisade, cremma_all}.meta.json
       (unstripped tokens, first 25,000); types_lo/types_hi = their min/max, hapax_hi = their max.
       All five values printed.
  P1 conditions (Amendment 1): h2_lo <= h2 <= h2_hi AND types_lo <= types_25k <= types_hi AND
       hapax <= hapax_hi.

Selector S and "selected partition" (one per corpus; Amendment 1): S = I_self - I_cross (bits,
  definitions under "M stream metrics").  Among partitions satisfying all three P1 conditions, the
  one with the largest S; ties by fewer M classes, then by the M class names in the order listed
  above.  If NO partition satisfies the conditions, P1 FAILs for that corpus and the selected
  partition is the unconstrained argmax S (same tie-break), on which P2 is still evaluated and
  reported.  The top 10 partitions by the same ordering are printed per corpus (S, I_self,
  I_cross, h2, types, hapax, M alphabet), and the number of partitions meeting the conditions.

M stream metrics (whole corpus, all lines): the M stream of a line is the sequence of M-glyph
  identities (glyph strings, e.g. "k", "ch", "ee") in reading order across the tokens of that line.
  alphabet = number of distinct M glyph strings.  I_self = plug-in mutual information (bits)
  between successive M glyphs inside a line (pairs (g_i, g_{i+1}) with both in the same line;
  lines with < 2 M glyphs contribute no pairs).  I_cross (Amendment 1) = plug-in MI (bits) between
  each M glyph and its immediately preceding W glyph in the same line, i.e. the nearest glyph
  before it in reading order within the line that is not in M (OTHER characters count as W glyphs
  since they stay in W); an M glyph with no W glyph before it in its line is paired with the
  boundary symbol "#".  One pair per M glyph; consecutive M glyphs share the same preceding W
  glyph.  S = I_self - I_cross.  All three are printed for every partition in the top-10 table and
  for the selected and PITCH-only partitions.  The null is drawn for the selected partition only
  (P2 is defined on that partition): 200 draws of I_self, each an independent uniform permutation
  of the M glyphs inside every line (line marginals preserved), numpy default_rng(20261017) per
  corpus.  P2 PASS iff I_self_obs > numpy.percentile(null, 99) AND S > 0.  Printed: I_self_obs,
  I_cross, S, null 99th pct, null max, null median, Monte-Carlo p = (1 + #(null >= obs)) / 201,
  excess over the 99th percentile.

P3 planted corpus.  Source = cremma_all sidecar pages and lines (real lines).  Vowel-group = a
  maximal run of characters whose NFKD base letter is in aeiouy (either case).  After every
  vowel-group inside a token one pitch symbol from the 5 symbols alpha beta gamma delta epsilon
  (U+03B1..U+03B5; asserted absent from cremma_all and from every other corpus loaded) is inserted,
  so the pitch glyphs are interleaved inside words.  Contour: state s in {0..4}; first state
  uniform; each next state: stay (p 0.5), s+1 (0.2), s-1 (0.2), jump (0.1) = uniform over the
  states at distance >= 2; a +-1 step that would leave {0..4} is reflected to the opposite
  direction.  The chain runs continuously through the corpus in reading order (no reset at token
  or line ends).  random.Random(20261017).  The planted corpus is held in memory only.
  The same search runs with PITCH as the 11th class (C = 11, 2046 partitions).  P3 PASS iff the
  planted corpus's selected partition (same P1 conditions, same selector S) has M == {PITCH}
  exactly AND |h2(residual) - h2(cremma_all unplanted, same estimator, first 25,000 tokens)| <=
  0.05.  P3 FAIL otherwise (the selected partition, both h2 values, and the PITCH-only partition's
  rank under S, its S, I_self and I_cross are printed).  P3 FAIL => TEST INVALID.

Margins printed: per corpus selected S, I_self, I_cross, distance of h2 to each range edge,
  types_25k minus each type bound, hapax minus hapax_hi, I_self minus null 99th pct; Voynich vs
  every negative control in one summary table.

Verdict (verbatim rule above): SUPPORTED only if P3 PASS and P1 and P2 PASS for ZL3b, RF1b and
  IT2a and no negative control satisfies P1 AND P2; NOT SUPPORTED otherwise; TEST INVALID if P3
  FAILs (printed before the other verdict lines, which are still printed for the record).

HARD STOP: a watchdog thread at 900 s wall clock writes the lines collected so far plus a STOPPED
  line to results_s34.txt and terminates the process; the search loops also check the clock.

Runtime (author's estimate from operation counts, unverified; the script was NOT run before the
  stub was frozen): ~1022 partitions x 11 corpora + 2046 for the planted corpus, each ~20-80 ms
  (per-type residual join, numpy h2, Counter, M-stream bincount) => roughly 3-8 min; the 200-draw
  nulls add ~10 s.  The task cap says expected < 5 min; the hard stop at 15 min is the binding
  limit.  Calibration read from the sidecars before freezing (not a result): at 25k tokens
  cremma_all has 8626 types / hapax 0.248, italian_dante 5249 / 0.133, mhg_nibelungenlied
  3478 / 0.074, Voynich 5417-5680 / 0.15, gib_realline_pooled 6839 / 0.581.  The original fixed
  type bound (3000) was stricter than every language control, so the P3 pitch-only residual
  (= cremma_all) could not meet it; Amendment 1 (above) replaced the fixed bounds with the
  language-row range and the |h2 - midpoint| selector with S before any run.  I_cross adds one
  bincount per partition (negligible).

Run: python -I s34_superimposed_streams.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import re
import subprocess
import sys
import threading
import time
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):  # -I ignores PYTHONIOENCODING; the console may be cp1252
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SELF = ROOT / "s34_superimposed_streams.py"
STUB = ROOT / "s34_superimposed_streams.prereg.sha256"
OUT = ROOT / "results_s34.txt"
TRANSLIT = ROOT / "data" / "translit"
REALLINE = ROOT / "data" / "controls_realline"
SYNTH = ROOT / "data" / "controls_synthetic"

SEED = 20261017
N_NULL = 200
H2_N = 25000
P3_H2_TOL = 0.05
K_PITCH = 5
PITCH_SYMBOLS = "αβγδε"  # alpha beta gamma delta epsilon
P_STAY, P_UP, P_DOWN, P_JUMP = 0.5, 0.2, 0.2, 0.1
MAX_C_FULL = 12
M_MAX_IF_LARGE = 4
TOP_PRINT = 10
CAP_EXPECTED_S = 300
CAP_HARD_S = 900

VOYNICH = [("ZL3b", TRANSLIT / "ZL3b_eva.meta.json"),
           ("RF1b", TRANSLIT / "RF1b.meta.json"),
           ("IT2a", TRANSLIT / "IT2a.meta.json")]
NEG_CONTROLS = [("gib_realline_pooled", REALLINE / "gib_realline_pooled.meta.json",
                 "human GIBBERISH, writers' own lines"),
                ("c2_best", SYNTH / "c2_best.meta.json", "c2 section generator"),
                ("schwartz_reuse", SYNTH / "schwartz_reuse.meta.json", "Schwartz reuse generator"),
                ("timm_schinner", SYNTH / "timm_schinner.meta.json", "Timm-Schinner self-citation"),
                ("flow_gen_layer", SYNTH / "flow_gen_layer.meta.json", "n2 flow generator layer"),
                ("mhg_nibelungenlied", REALLINE / "mhg_nibelungenlied.meta.json", "MHG verse, native lines"),
                ("italian_dante", REALLINE / "italian_dante.meta.json", "Italian verse, native lines")]
CREMMA = REALLINE / "cremma_all.meta.json"
LANG_SIDECARS = [("mhg_nibelungenlied", REALLINE / "mhg_nibelungenlied.meta.json"),
                 ("italian_dante", REALLINE / "italian_dante.meta.json"),
                 ("oldfrench_roland", REALLINE / "oldfrench_roland.meta.json"),
                 ("occitan_croisade", REALLINE / "occitan_croisade.meta.json"),
                 ("cremma_all", CREMMA)]
H2_ROWS = [ROOT / "results_s17_mhg_nibelungenlied.json", ROOT / "results_s17_italian_dante.json",
           ROOT / "results_s17_oldfrench_roland.json", ROOT / "results_s17_occitan_croisade.json",
           ROOT / "results_s18_cremma_all.json"]

# ---------------------------------------------------------------- declared glyph classes
CLASS_NAMES = ["GALLOWS", "BENCHGALLOWS", "BENCH", "E", "OA", "I", "FINAL", "D", "Y", "Q", "PITCH"]
CLASS_MEMBERS = {"GALLOWS": "k t p f", "BENCHGALLOWS": "ckh cth cph cfh", "BENCH": "ch sh", "E": "e+ (run = one glyph)",
                 "OA": "o a", "I": "i+ (run = one glyph)", "FINAL": "n r l m g s", "D": "d", "Y": "y", "Q": "q",
                 "PITCH": "planted alpha beta gamma delta epsilon (planted corpus only)"}
OTHER = len(CLASS_NAMES)  # class id of every non-class character; always stays in W
GLYPH_RE = re.compile(r"ckh|cth|cph|cfh|ch|sh|e+|i+|[ktpf]|[oa]|[nrlmgs]|d|y|q|[" + PITCH_SYMBOLS + r"]|.", re.DOTALL)


def class_of(g: str) -> int:
    if g in ("k", "t", "p", "f"):
        return 0
    if g in ("ckh", "cth", "cph", "cfh"):
        return 1
    if g in ("ch", "sh"):
        return 2
    if g[0] == "e":
        return 3
    if g in ("o", "a"):
        return 4
    if g[0] == "i":
        return 5
    if g in ("n", "r", "l", "m", "g", "s"):
        return 6
    if g == "d":
        return 7
    if g == "y":
        return 8
    if g == "q":
        return 9
    if g in PITCH_SYMBOLS:
        return 10
    return OTHER


T0 = time.monotonic()
LINES: list[str] = []
_LOCK = threading.Lock()


def elapsed() -> float:
    return time.monotonic() - T0


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def load_by_path(modname: str, path: Path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def emit(s: str = "") -> None:
    print(s, flush=True)
    with _LOCK:
        LINES.append(s)


def flush() -> None:
    with _LOCK:
        OUT.write_text("\n".join(LINES) + "\n", encoding="utf-8", newline="\n")


def hard_stop(where: str) -> None:
    emit()
    emit(f"STOPPED: hard cap {CAP_HARD_S} s reached at {elapsed():.1f} s during {where}; partial results above.")
    emit(f"run ended {clock()}")
    flush()
    os._exit(3)


def check_cap(where: str) -> None:
    if elapsed() >= CAP_HARD_S:
        hard_stop(where)


# ---------------------------------------------------------------- h2 (s24 h2_of convention)
def h2_of(words, n_tokens=H2_N):
    """Verbatim s24 estimator (string / Counter): H(pair) - H(char) on ' '.join(words) + ' '."""
    words = words[:n_tokens]
    s = " ".join(words) + " "
    c1 = Counter(s)
    n = len(s)
    h1 = -sum(v / n * math.log2(v / n) for v in c1.values())
    c2 = Counter(zip(s, s[1:]))
    n2 = sum(c2.values())
    h12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return h12 - h1


def _ent(counts) -> float:
    c = counts[counts > 0].astype(np.float64)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def h2_fast(words, n_tokens=H2_N):
    """Same formula as h2_of on the same string, with numpy bincounts."""
    s = " ".join(words[:n_tokens]) + " "
    codes = np.frombuffer(s.encode("utf-32-le"), dtype=np.uint32)
    _, inv = np.unique(codes, return_inverse=True)
    inv = inv.astype(np.int64)
    k = int(inv.max()) + 1
    h1 = _ent(np.bincount(inv, minlength=k))
    h12 = _ent(np.bincount(inv[:-1] * k + inv[1:], minlength=k * k))
    return h12 - h1


# ---------------------------------------------------------------- corpus preparation
class Corpus:
    """Tokens parsed once into glyph units with class ids; everything per partition is derived."""

    def __init__(self, name, pages, note=""):
        self.name, self.note = name, note
        toks, lid = [], []
        n_lines = 0
        for p in pages:
            for ln in p["lines"]:
                t = [str(x) for x in ln if x]
                if not t:
                    continue
                toks.extend(t)
                lid.extend([n_lines] * len(t))
                n_lines += 1
        self.n_tokens, self.n_lines = len(toks), n_lines
        types = sorted(set(toks))
        tidx = {t: i for i, t in enumerate(types)}
        self.types = types
        self.tok_type = np.asarray([tidx[t] for t in toks], dtype=np.int64)
        self.tok_line = np.asarray(lid, dtype=np.int64)
        # per type: glyph strings and class ids
        self.type_glyphs = [GLYPH_RE.findall(t) for t in types]
        self.type_classes = [[class_of(g) for g in gl] for gl in self.type_glyphs]
        # flat glyph arrays (reading order) for the M stream
        gstr = sorted({g for gl in self.type_glyphs for g in gl})
        gidx = {g: i for i, g in enumerate(gstr)}
        self.glyph_names = gstr
        tg_ids = [np.asarray([gidx[g] for g in gl], dtype=np.int64) for gl in self.type_glyphs]
        tg_cls = [np.asarray(cl, dtype=np.int64) for cl in self.type_classes]
        self.g_id = np.concatenate([tg_ids[t] for t in self.tok_type]) if len(toks) else np.zeros(0, np.int64)
        self.g_cls = np.concatenate([tg_cls[t] for t in self.tok_type]) if len(toks) else np.zeros(0, np.int64)
        lens = np.asarray([len(tg_ids[t]) for t in self.tok_type], dtype=np.int64)
        self.g_line = np.repeat(self.tok_line, lens)
        self.n_glyphs = int(self.g_cls.size)
        n_chars = sum(len(t) for t in toks)
        tcount = np.bincount(self.tok_type, minlength=len(types))
        other_chars = int(sum(tcount[i] * sum(len(g) for g, c in zip(self.type_glyphs[i], self.type_classes[i]) if c == OTHER)
                              for i in range(len(types))))
        self.other_share = other_chars / n_chars if n_chars else float("nan")
        self.n_chars = n_chars
        present = sorted({c for cl in self.type_classes for c in cl if c != OTHER})
        self.classes = present  # class ids present (partition universe)
        self.class_token_share = {c: float(np.mean(self.g_cls == c)) for c in present}

    def residual(self, m_set):
        """Residual token strings (all non-empty, reading order) and the dropped-empty count."""
        res_type = ["".join(itertools.compress(gl, [c not in m_set for c in cl]))
                    for gl, cl in zip(self.type_glyphs, self.type_classes)]
        res_arr = np.asarray(res_type, dtype=object)
        toks = res_arr[self.tok_type]
        nonempty = toks != ""
        dropped = int((~nonempty).sum())
        kept = toks[nonempty]
        return kept, dropped

    def w_metrics(self, m_set):
        kept, dropped = self.residual(m_set)
        head = kept[:H2_N].tolist()
        h2 = h2_fast(head)
        c = Counter(head)
        types = len(c)
        hapax = sum(1 for v in c.values() if v == 1) / len(head) if head else float("nan")
        return dict(h2=h2, types=types, hapax=hapax, n_res=int(kept.size), dropped=dropped, head=head)

    def m_arrays(self, m_set):
        mask = np.isin(self.g_cls, list(m_set))
        return self.g_id[mask], self.g_line[mask]

    def cross_pairs(self, m_set):
        """(preceding W glyph id or BOUNDARY=G, M glyph id) for every M glyph, same line only."""
        G = len(self.glyph_names)
        is_m = np.isin(self.g_cls, list(m_set))
        idx = np.arange(self.n_glyphs)
        last_w = np.maximum.accumulate(np.where(is_m, -1, idx))  # index of the nearest preceding W glyph
        m_idx = idx[is_m]
        lw = last_w[is_m]
        has = (lw >= 0) & (self.g_line[np.maximum(lw, 0)] == self.g_line[m_idx])
        x = np.where(has, self.g_id[np.maximum(lw, 0)], G)
        return x, self.g_id[m_idx]

    def m_metrics(self, m_set):
        G = len(self.glyph_names)
        gid, gl = self.m_arrays(m_set)
        alph = int(np.unique(gid).size) if gid.size else 0
        i_self = mi_pairs(gid, gl, G)
        x, y = self.cross_pairs(m_set)
        i_cross = mi_xy(x, y, G + 1, G)
        return dict(alphabet=alph, n_m=int(gid.size), i_self=i_self, i_cross=i_cross, S=i_self - i_cross)


def mi_xy(a, b, Ga, Gb):
    """Plug-in MI (bits) of paired integer arrays a (< Ga) and b (< Gb)."""
    n = a.size
    if n == 0:
        return float("nan")
    joint = np.bincount(a * Gb + b, minlength=Ga * Gb).reshape(Ga, Gb).astype(np.float64)
    marg = joint.sum(1, keepdims=True) * joint.sum(0, keepdims=True)  # row sum * column sum
    nz = joint > 0
    return float((joint[nz] / n * np.log2(joint[nz] * n / marg[nz])).sum())


def mi_pairs(gid, gl, G):
    """I_self: MI between successive M glyphs inside a line."""
    same = gl[:-1] == gl[1:]
    return mi_xy(gid[:-1][same], gid[1:][same], G, G)


def mi_line_null(gid, gl, G, reps=N_NULL, seed=SEED, where=""):
    rng = np.random.default_rng(seed)
    out = np.empty(reps)
    for k in range(reps):
        keys = rng.random(gid.size)
        perm = np.lexsort((keys, gl))  # gl is non-decreasing in reading order, so gl[perm] == gl
        out[k] = mi_pairs(gid[perm], gl, G)
        if k % 50 == 49:
            check_cap(f"MI null {where}")
    return out


# ---------------------------------------------------------------- planted corpus (P3)
def is_vowel(ch: str) -> bool:
    base = unicodedata.normalize("NFKD", ch)[:1].lower()
    return base in "aeiouy"


def plant(pages, seed=SEED):
    rng = random.Random(seed)
    state = rng.randrange(K_PITCH)
    n_inserted = 0

    def step(s):
        u = rng.random()
        if u < P_STAY:
            return s
        if u < P_STAY + P_UP:
            return s + 1 if s + 1 < K_PITCH else s - 1
        if u < P_STAY + P_UP + P_DOWN:
            return s - 1 if s - 1 >= 0 else s + 1
        far = [t for t in range(K_PITCH) if abs(t - s) >= 2]
        return rng.choice(far)

    out = []
    first = True
    for p in pages:
        q = dict(p, lines=[])
        for ln in p["lines"]:
            new = []
            for tok in ln:
                tok = str(tok)
                if not tok:
                    continue
                buf, in_vowel = [], False
                for ch in tok:
                    v = is_vowel(ch)
                    if in_vowel and not v:
                        if not first:
                            state = step(state)
                        first = False
                        buf.append(PITCH_SYMBOLS[state])
                        n_inserted += 1
                    buf.append(ch)
                    in_vowel = v
                if in_vowel:
                    if not first:
                        state = step(state)
                    first = False
                    buf.append(PITCH_SYMBOLS[state])
                    n_inserted += 1
                new.append("".join(buf))
            if new:
                q["lines"].append(new)
        if q["lines"]:
            out.append(q)
    return out, n_inserted


# ---------------------------------------------------------------- partition search
def partitions(classes):
    C = len(classes)
    restricted = C > MAX_C_FULL
    out = []
    for r in range(1, C):
        if restricted and r > M_MAX_IF_LARGE:
            break
        for m in itertools.combinations(classes, r):
            out.append(frozenset(m))
    return out, restricted


def mname(m_set):
    return "+".join(CLASS_NAMES[c] for c in sorted(m_set))


def row_line(i, r):
    return (f"    {i:4d} {str(r['ok']):>5s} {r['S']:+8.4f} {r['i_self']:7.4f} {r['i_cross']:7.4f} {r['h2']:7.4f} {r['types']:6d} "
            f"{r['hapax']:6.3f} {r['n_res']:7d} {r['dropped']:7d} {r['alphabet']:6d} {r['n_m']:8d}  {mname(r['m'])}")


def search(corpus: Corpus, B):
    """B = dict(h2_lo, h2_hi, types_lo, types_hi, hapax_hi): the language-row bounds (Amendment 1)."""
    parts, restricted = partitions(corpus.classes)
    C = len(corpus.classes)
    emit(f"--- {corpus.name}: {corpus.n_tokens} tokens, {corpus.n_lines} lines, {corpus.n_glyphs} glyphs, "
         f"OTHER char share {100 * corpus.other_share:.2f} %; classes present C={C} "
         f"[{', '.join(CLASS_NAMES[c] for c in corpus.classes)}]; partitions {len(parts)}"
         f"{' (RESTRICTED to |M| <= 4 because C > 12)' if restricted else ' (= 2^C - 2, no restriction)'}  {corpus.note}")
    emit("    class glyph shares: " + ", ".join(f"{CLASS_NAMES[c]} {100 * s:.1f}%" for c, s in corpus.class_token_share.items()))
    rows = []
    for k, m in enumerate(parts):
        w = corpus.w_metrics(m)
        mm = corpus.m_metrics(m)
        ok = (B["h2_lo"] <= w["h2"] <= B["h2_hi"]) and (B["types_lo"] <= w["types"] <= B["types_hi"]) and w["hapax"] <= B["hapax_hi"]
        rows.append(dict(m=m, ok=ok, h2=w["h2"], types=w["types"], hapax=w["hapax"], n_res=w["n_res"], dropped=w["dropped"],
                         alphabet=mm["alphabet"], n_m=mm["n_m"], i_self=mm["i_self"], i_cross=mm["i_cross"], S=mm["S"]))
        if k % 100 == 99:
            check_cap(f"search {corpus.name} partition {k + 1}/{len(parts)}")
    key = lambda r: (0 if r["ok"] else 1, -(r["S"] if r["S"] == r["S"] else -math.inf), len(r["m"]), tuple(sorted(r["m"])))  # noqa: E731
    rows.sort(key=key)
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    n_ok = sum(r["ok"] for r in rows)
    emit(f"    partitions meeting P1 conditions (h2 in [{B['h2_lo']:.4f}, {B['h2_hi']:.4f}], types_25k in "
         f"[{B['types_lo']}, {B['types_hi']}], hapax <= {B['hapax_hi']:.3f}): {n_ok} of {len(parts)}; "
         f"ordering: P1-ok first, then argmax S = I_self - I_cross, then fewer M classes, then class order")
    emit(f"    {'rank':>4s} {'ok':>5s} {'S':>8s} {'I_self':>7s} {'I_cross':>7s} {'h2':>7s} {'types':>6s} {'hapax':>6s} {'res_tok':>7s} "
         f"{'dropped':>7s} {'M_alph':>6s} {'M_glyphs':>8s}  M classes")
    for r in rows[:TOP_PRINT]:
        emit(row_line(r["rank"], r))
    best = rows[0]
    # P2 on the selected partition
    gid, gl = corpus.m_arrays(best["m"])
    null = mi_line_null(gid, gl, len(corpus.glyph_names), where=corpus.name)
    q99 = float(np.percentile(null, 99))
    p_mc = (1 + int(np.sum(null >= best["i_self"]))) / (N_NULL + 1)
    p2 = bool(best["i_self"] > q99) and bool(best["S"] > 0)
    # h2 cross-check with the verbatim s24 estimator on the selected partition
    kept, _ = corpus.residual(best["m"])
    h2_ref = h2_of(kept[:H2_N].tolist())
    emit(f"    SELECTED partition M = {{{mname(best['m'])}}} ({'meets' if best['ok'] else 'does NOT meet'} P1 conditions; "
         f"{'constrained' if best['ok'] else 'unconstrained fallback'} argmax S): S {best['S']:+.4f} = I_self {best['i_self']:.4f} "
         f"- I_cross {best['i_cross']:.4f} bits")
    emit(f"    P1 {corpus.name}: h2 {best['h2']:.4f} (to range edges {best['h2'] - B['h2_lo']:+.4f} / {B['h2_hi'] - best['h2']:+.4f}); "
         f"types_25k {best['types']} ({best['types'] - B['types_lo']:+d} vs lo {B['types_lo']}, {B['types_hi'] - best['types']:+d} vs hi {B['types_hi']}); "
         f"hapax {best['hapax']:.3f} ({best['hapax'] - B['hapax_hi']:+.3f} vs {B['hapax_hi']:.3f}); "
         f"h2_check |fast - s24| = {abs(best['h2'] - h2_ref):.2e} -> {'PASS' if best['ok'] else 'FAIL'}")
    emit(f"    P2 {corpus.name}: M alphabet {best['alphabet']}, M glyphs {best['n_m']}, I_self {best['i_self']:.4f} bits vs line-shuffle null "
         f"({N_NULL} draws) 99th pct {q99:.4f}, max {null.max():.4f}, median {np.median(null):.4f}; excess over 99th pct "
         f"{best['i_self'] - q99:+.4f}; MC p {p_mc:.3f}; S {best['S']:+.4f} ({'> 0' if best['S'] > 0 else 'NOT > 0'}) "
         f"-> {'PASS' if p2 else 'FAIL'}")
    emit()
    flush()
    return dict(best=best, p1=bool(best["ok"]), p2=p2, q99=q99, null=null, n_ok=n_ok, n_parts=len(parts), C=C,
                h2_ref=h2_ref, rows=rows)


# ---------------------------------------------------------------- main
def main() -> None:
    watchdog = threading.Timer(CAP_HARD_S, hard_stop, args=("watchdog",))
    watchdog.daemon = True
    watchdog.start()

    emit("S34: superimposed-streams check (Phase 3; sibling of s24): two interleaved streams, M = pitch classes, W = word classes")
    emit(f"run started {clock()}")
    emit(f"s34_superimposed_streams.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"cap: python -I, one CPU process, no GPU, no paid calls, no new data; expected < {CAP_EXPECTED_S} s; "
         f"HARD STOP {CAP_HARD_S} s (watchdog + in-loop checks); planted corpus held in memory only")
    emit(f"loader: scoreboard/run_v2.py load_meta by path (sha256 {sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}...)")
    emit(f"search: exhaustive 2-partitions of the present classes (2^C - 2); h2 on first {H2_N} residual tokens; "
         f"M-stream MI line-shuffle null {N_NULL} draws on the best partition; seed {SEED}")
    emit()
    R2 = load_by_path("run_v2_s34", ROOT / "scoreboard" / "run_v2.py")

    # class list provenance
    b3 = ROOT / "b3_slot_claims.py"
    b3_gal = "?"
    if b3.exists():
        mm = re.search(r'GALLOWS\s*=\s*set\("(\w+)"\)', b3.read_text(encoding="utf-8"))
        b3_gal = mm.group(1) if mm else "not found"
    emit("=== Glyph classes (declared; metrics_new.SlotSegmenter is data-driven and has no class list; "
         f"b3_slot_claims.py GALLOWS = \"{b3_gal}\" read as text) ===")
    for i, c in enumerate(CLASS_NAMES):
        emit(f"  {i:2d} {c:13s} {CLASS_MEMBERS[c]}")
    emit(f"  -- OTHER: every other character; never a slot class, always in W")
    emit(f"  parser regex: {GLYPH_RE.pattern}")
    emit()

    # language h2 range
    h2_rows = {}
    for p in H2_ROWS:
        if p.exists():
            h2_rows[p.stem] = float(json.loads(p.read_text(encoding="utf-8"))["row"]["h2"])
        else:
            emit(f"h2 row MISSING: {p}")
    h2_lo, h2_hi = min(h2_rows.values()), max(h2_rows.values())
    emit("language h2 rows: " + ", ".join(f"{k.replace('results_', '')}={v:.4f}" for k, v in h2_rows.items()))
    emit(f"language h2 range = [{h2_lo:.4f}, {h2_hi:.4f}]")
    # Amendment 1: types_25k / hapax_25k bounds from the five language sidecars, same 25k convention
    lang_stats = {}
    for lname, lpath in LANG_SIDECARS:
        _, lpages = R2.load_meta(lpath)
        ltoks = [str(t) for p in lpages for ln in p["lines"] for t in ln if t][:H2_N]
        lc = Counter(ltoks)
        lang_stats[lname] = (len(lc), sum(1 for v in lc.values() if v == 1) / len(ltoks), h2_of(ltoks))
    types_lo = min(v[0] for v in lang_stats.values())
    types_hi = max(v[0] for v in lang_stats.values())
    hapax_hi = max(v[1] for v in lang_stats.values())
    emit("language rows at 25k tokens (types_25k / hapax_25k / h2 recomputed): " +
         ", ".join(f"{k} {v[0]} / {v[1]:.3f} / {v[2]:.4f}" for k, v in lang_stats.items()))
    B = dict(h2_lo=h2_lo, h2_hi=h2_hi, types_lo=types_lo, types_hi=types_hi, hapax_hi=hapax_hi)
    emit(f"P1 conditions (Amendment 1): h2 in [{h2_lo:.4f}, {h2_hi:.4f}], types_25k in [{types_lo}, {types_hi}], "
         f"hapax_25k <= {hapax_hi:.3f}; selector: argmax S = I_self - I_cross among P1-ok partitions")
    emit()

    # load corpora
    corpora = {}
    for name, path in VOYNICH:
        _, pages = R2.load_meta(path)
        corpora[name] = Corpus(name, pages, "Voynich")
    negs = []
    for name, path, note in NEG_CONTROLS:
        if path.exists():
            _, pages = R2.load_meta(path)
            corpora[name] = Corpus(name, pages, f"negative control: {note}")
            negs.append(name)
        else:
            emit(f"control sidecar MISSING: {name} {path}")
    _, cremma_pages = R2.load_meta(CREMMA)
    cremma_toks = [str(t) for p in cremma_pages for ln in p["lines"] for t in ln if t]
    for name, c in corpora.items():
        if any(s in "".join(c.types) for s in PITCH_SYMBOLS):
            emit(f"ABORT: pitch symbol present in {name}")
            flush()
            os._exit(2)
    if any(s in "".join(cremma_toks) for s in PITCH_SYMBOLS):
        emit("ABORT: pitch symbol present in cremma_all")
        flush()
        os._exit(2)
    planted_pages, n_ins = plant(cremma_pages)
    planted = Corpus("planted_cremma", planted_pages, f"POSITIVE CONTROL: cremma_all real lines + {n_ins} planted pitch glyphs "
                                                     f"(K={K_PITCH}, Markov contour stay {P_STAY}/step {P_UP}+{P_DOWN}/jump {P_JUMP})")
    cremma_h2 = h2_of(cremma_toks)
    cremma_c = Counter(cremma_toks[:H2_N])
    emit(f"cremma_all unplanted reference: {len(cremma_toks)} tokens, h2 {cremma_h2:.4f}, types_25k {len(cremma_c)}, "
         f"hapax {sum(1 for v in cremma_c.values() if v == 1) / min(len(cremma_toks), H2_N):.3f}")
    for name, _ in VOYNICH:
        c = corpora[name]
        cc = Counter(c.types[i] for i in c.tok_type[:H2_N].tolist())
        emit(f"{name} unstripped reference: {c.n_tokens} tokens, h2 {h2_of([c.types[i] for i in c.tok_type.tolist()]):.4f}, "
             f"types_25k {len(cc)}, hapax {sum(1 for v in cc.values() if v == 1) / min(c.n_tokens, H2_N):.3f}")
    emit()
    check_cap("loading")

    # ================================================================ P3 first (validity gate), then Voynich, then negatives
    emit("=== P3 positive control: planted corpus search (PITCH must be exactly M of the selected partition) ===")
    r3 = search(planted, B)
    pitch_only = r3["best"]["m"] == frozenset({10})
    d_h2 = abs(r3["best"]["h2"] - cremma_h2)
    p3 = pitch_only and d_h2 <= P3_H2_TOL
    emit(f"P3: selected partition M = {{{mname(r3['best']['m'])}}} ({'exactly PITCH' if pitch_only else 'NOT exactly PITCH'}); "
         f"S {r3['best']['S']:+.4f} (I_self {r3['best']['i_self']:.4f}, I_cross {r3['best']['i_cross']:.4f}); "
         f"residual h2 {r3['best']['h2']:.4f} vs cremma_all {cremma_h2:.4f} (|d| {d_h2:.4f} vs tol {P3_H2_TOL}); "
         f"P2 on it {'PASS' if r3['p2'] else 'FAIL'} (reference only) -> {'PASS' if p3 else 'FAIL'}")
    pr = next((r for r in r3["rows"] if r["m"] == frozenset({10})), None)
    if pr is not None:
        emit(f"P3 PITCH-only partition: rank {pr['rank']} of {r3['n_parts']} under S (P1-ok first); meets P1 conditions: {pr['ok']}; "
             f"S {pr['S']:+.4f} = I_self {pr['i_self']:.4f} - I_cross {pr['i_cross']:.4f}; h2 {pr['h2']:.4f} "
             f"(|d| vs cremma_all {abs(pr['h2'] - cremma_h2):.4f}), types_25k {pr['types']}, hapax {pr['hapax']:.3f}, "
             f"M alphabet {pr['alphabet']}, M glyphs {pr['n_m']}; planted pitch glyphs = {n_ins}")
        emit("    " + row_line(pr["rank"], pr).strip())
    emit()
    flush()
    check_cap("after P3")

    emit("=== Voynich: P1 residual-is-language and P2 stream-is-melody ===")
    rv = {}
    for name, _ in VOYNICH:
        rv[name] = search(corpora[name], B)
        check_cap(f"after Voynich {name}")

    emit("=== Negative controls: same search, same rules ===")
    rn = {}
    for name in negs:
        rn[name] = search(corpora[name], B)
        check_cap(f"after control {name}")

    # ================================================================ summary and verdict
    emit("=== SUMMARY (margins) ===")
    emit(f"{'corpus':22s} {'C':>2s} {'parts':>5s} {'n_ok':>5s} {'S':>8s} {'I_self':>7s} {'I_cross':>7s} {'h2':>7s} {'types':>6s} "
         f"{'hapax':>6s} {'null99':>7s} {'excess':>7s}  P1    P2    P1+P2  selected M")
    rows_all = [("planted_cremma", r3)] + [(n, rv[n]) for n, _ in VOYNICH] + [(n, rn[n]) for n in negs]
    for name, r in rows_all:
        b = r["best"]
        emit(f"{name:22s} {r['C']:2d} {r['n_parts']:5d} {r['n_ok']:5d} {b['S']:+8.4f} {b['i_self']:7.4f} {b['i_cross']:7.4f} {b['h2']:7.4f} "
             f"{b['types']:6d} {b['hapax']:6.3f} {r['q99']:7.4f} {b['i_self'] - r['q99']:+7.4f}  {'PASS' if r['p1'] else 'FAIL'}  "
             f"{'PASS' if r['p2'] else 'FAIL'}  {str(r['p1'] and r['p2']):5s}  {mname(b['m'])}")
    if pr is not None:
        emit(f"{'planted PITCH-only':22s} {r3['C']:2d} {r3['n_parts']:5d} {'-':>5s} {pr['S']:+8.4f} {pr['i_self']:7.4f} {pr['i_cross']:7.4f} "
             f"{pr['h2']:7.4f} {pr['types']:6d} {pr['hapax']:6.3f} {'-':>7s} {'-':>7s}  {'ok' if pr['ok'] else 'no':4s}  -     -      "
             f"PITCH (rank {pr['rank']} under S)")
    neg_both = [n for n in negs if rn[n]["p1"] and rn[n]["p2"]]
    voy_ok = all(rv[n]["p1"] and rv[n]["p2"] for n, _ in VOYNICH)
    emit()
    emit("=== VERDICT (pre-registered rule: SUPPORTED only if P3 PASS and P1+P2 PASS on ZL3b, RF1b, IT2a and no negative "
         "control satisfies P1+P2; NOT SUPPORTED otherwise; TEST INVALID if P3 FAILs) ===")
    emit(f"P3 positive control: {'PASS' if p3 else 'FAIL'}")
    for name, _ in VOYNICH:
        emit(f"{name}: P1 {'PASS' if rv[name]['p1'] else 'FAIL'}  P2 {'PASS' if rv[name]['p2'] else 'FAIL'}  best M = {{{mname(rv[name]['best']['m'])}}}")
    emit(f"negative controls satisfying P1+P2: {', '.join(neg_both) if neg_both else 'none'}")
    if not p3:
        verdict = "TEST INVALID (P3 positive control failed)"
    elif voy_ok and not neg_both:
        verdict = "superimposed streams SUPPORTED"
    else:
        verdict = "superimposed streams NOT SUPPORTED"
    emit(f"VERDICT: {verdict}")
    failed = []
    if not p3:
        failed.append("P3")
    if not all(rv[n]["p1"] for n, _ in VOYNICH):
        failed.append("P1")
    if not all(rv[n]["p2"] for n, _ in VOYNICH):
        failed.append("P2")
    if neg_both:
        failed.append("negative-control margin")
    emit(f"failed predictions: {', '.join(failed) if failed else 'none'}")
    emit()
    emit(f"elapsed {elapsed():.1f} s (expected < {CAP_EXPECTED_S} s; hard cap {CAP_HARD_S} s; within cap: {elapsed() < CAP_HARD_S})")
    emit("done-when: results_s34.txt exists with the class list, the P3 planted-search block, the P1/P2 blocks on all three "
         "transliterations, the seven negative-control blocks, the summary table and the verdict line -> met")
    emit(f"run ended {clock()}")
    flush()
    watchdog.cancel()


if __name__ == "__main__":
    main()
