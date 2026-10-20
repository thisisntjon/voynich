"""S76: does the slot-layer picture depend on our SlotSegmenter?  (re-measurement under Zattera's 12-slot word model;
pre-registered calls C-a..C-e; no producer)

QUESTION (frozen): Argon's s63 showed many "rare cores" are boundary shifts made by scoreboard/metrics_new.SlotSegmenter
(CONSTRAINTS-MAP A21).  Do the key slot-layer results survive a segmenter of a different design, the hand-built slot
model of Zattera 2022 (CEUR-WS 3313 paper 10; data/external/papers/zattera_2022_ceur3313_paper10.txt, sec. 2.1-2.3)?

PRE-REGISTRATION: s76_segmenter_independence.prereg.sha256 (sha256sum format) = sha256 of this file and of every local
module it imports, frozen BEFORE any real-text run.  Before the freeze the script ran only with --synthetic (synthetic
texts from a planted slot grammar; reads no real data; writes only runs/s76/fixture.txt).  The script re-hashes itself
and its local imports and prints stub_match.

ZATTERA SLOT MODEL (as implemented; fixed before any real run)
  Slots 0-11, each empty or holding ONE glyph of the Slot alphabet (paper sec. 2.1, 2.2, Fig. 2-4):
     0: q s d     1: o y     2: l r     3: t k p f     4: ch sh     5: cth ckh cph cfh     6: e ee eee
     7: s d       8: o a     9: i ii iii   10: d l r m n   11: y
  Source of the table: Fig. 2 itself is an image and is not in the text file.  The table is read off the state
  names of the Fig. 4 grammar, which IS in the text (0_d 0_q 0_s 1_o 1_y 2_l 2_r 3_tpkf 4_C 4_S 5_TPK 6_eEB 7_d 7_s 8_a
  8_o 9_iJ 10_d 10_l 10_m 10_n 10_r 11_y = slot_glyph), plus the text's statements: pedestalled gallows are
  cth ckh cph cfh (sec. 2.2; cfh is absent from Fig. 4 and placed with its class in slot 5); "e and i only appear in
  slots 6 and 9 respectively, in a sequence of 1, 2 or 3" (so eee in 6, iii in 9); "each glyph can appear only in one
  or two slots, with exception of d that can appear in three" (d in 0, 7, 10: checked); "for 9 out of 12 slots ...
  as low as 2-3 possible glyphs" (slots 0,1,2,4,6,7,8,9 have 2-3, slot 11 has 1: checked).  The table agrees with
  the independent transcription of Fig. 2 in data/external/papers/rozanova_2608.17096_src (read, not imported).
  c and h are not glyphs (paper: "c and h do not correspond to Voynich characters"), nor are g x v u j b z.
  DECOMPOSITION ("regular" in the paper): a word decomposes iff it can be cut into Slot-alphabet glyphs whose slots
  can be chosen strictly increasing.  e-runs and i-runs are single glyphs (a run of 4 fails).  Ambiguity (o y l r s d
  sit in two or three slots): among tokenizations, fewest glyphs; then the LATEST-SLOT assignment (from the right,
  each glyph takes the highest slot it may occupy below the next glyph's slot that still leaves a valid assignment
  of the glyphs to its left).  Reason: the paper's left crust (slots 0-2) is only needed before a core glyph; a bare
  "ol", "dy", "or" then reads as right crust, as in the Fig. 4 grammar (10_d -> 11_y; 8_o -> 10_l) where every
  BEGIN path into 0-2 continues into a slot >= 3 or 8_a via 2_r.  Diagnostic, printed: the share of decomposed tokens
  that are complete Fig. 4 grammar paths, and the share of those whose grammar slot assignment equals ours.
  Unit for coverage: tokens / word types of each transliteration's meta.json text (the s69 loader), not Zattera's
  merged "concordance" interlinear (31,317 tokens, 5,105 types; 86.6 % of tokens and 51.3 % of types regular).
  Our undecomposable = his "separable" (10.4 %) + "unstructured" (3.0 %).  The comparison figure is 86.6 % of tokens.

SLOT -> LAYER MAPPING (fixed before any real run)
  prefix = slots 0-2, core = slots 3-7, suffix = slots 8-11.  Justification from the paper text:
  * "gallows in slots 3 and 5, which belong to the core layer, could well enclose pedestals in slots 4" (sec. 2.3.1):
    3-5 (gallows, pedestal, pedestalled gallows) must be one block, and it is the core.
  * slot 6 (e-runs) follows the pedestal; the paper treats e-runs with the pedestal as Stolfi's mantle and says they
    "appear in very definite positions"; it is kept with the core block so that the core is the gallows/bench/e block.
  * "the crust is not homogeneous as it is composed of a left and a right part which are quite different (see e.g.
    position of q or i)": left crust = slots 0-2 (q in slot 0) = prefix, the leading slots before the first
    core-bearing slot (3); right crust = slots 8-11 (i in slot 9) = suffix.
  * slot 7 (s, d) is not placed by the text.  We put it in the core: in Fig. 4, 7_d is entered straight from <BEGIN>
    and from 1_o, like the gallows/pedestal states, and leads into the right-crust vowel slot (7_d -> 8_a, 8_o), so in
    gallows-less words (daiin, dar, dol) it stands where a core glyph would; 7_s follows the e-run (6_eEB -> 7_s).
    Reported-only sensitivity S3 moves slot 7 into the suffix.
  An empty layer is the empty string (prefix/suffix print as "∅" through the s69/s55 code; an empty core is "").

UNDECOMPOSABLE WORDS
  PRIMARY ("drop"): excluded from the slot statistics: removed from their lines before any measurement (they are
    neither targets nor contexts; their neighbours become adjacent; emptied lines/pages are dropped, counts printed).
  S1 ("whole", requested sensitivity): kept in place as whole-word cores, prefix = suffix = "".
  S2 ("empty", reported only): kept in place with prefix = suffix = "" and core = "∅" (the literal "prefix/core/suffix
    of ∅" reading; note it hands M7 a deterministic class and R(1) a frequent repeated unit).
  S3 ("slot7suffix", reported only): as PRIMARY but core = slots 3-6, suffix = slots 7-11.
  Calls and verdict are judged on PRIMARY; S1-S3 calls are printed beside.

TEXTS, SPLIT, MEASURES (each source study's code imported and called verbatim; only the segmenter is swapped)
  Voynich ZL3b (ZL3b_eva), RF1b, IT2a.  Split = random.Random(20261017) page shuffle, first round(0.8 n) training
  (166/41, 166/41, 165/41) as in s55/s56/s69/g1_edge_joint.split_names.  "orig" = scoreboard/metrics_new.SlotSegmenter
  (defaults) fitted on training tokens, exactly as each source did; it is recomputed here and the published value is
  printed beside as a reproduction check.  The Zattera segmenter has no fitted parameters.
  (a) s69 M1 held-out prefix gain (bits/prefix) with its 95 % interval (500 subsamples of round(0.8 x 41) held-out
      pages without replacement, rng 20261017) and its within-line-shuffle excess (200 shuffles, rng 20261018):
      s69_prefix_stream_memory.Text + .measure, with s69's module name SlotSegmenter rebound to the chosen segmenter.
  (b) s69 b_pos (matched line reset), same call.        (c) s69 M7 (current core class -> prefix; K = 12 k-means on
      training, s69/s67 core_classes), same call.
  (d) A14 core->core MI excess on held-out pages: s55_code_vs_generator.TextData (s55 loader voynich_pages, s55 split)
      with s55's SlotSegmenter rebound; point = TextData.core_core over all held-out pages, 200 within-line shuffles,
      np.random.default_rng(20261017) (= s55 f2_core_core).  Interval [DEVIATION from s55, which used a with-
      replacement bootstrap]: 500 subsamples of round(0.8 x held-out pages) without replacement, each scored by
      TextData.core_core with 20 shuffles (s55's N_SHUF_BOOT), one np.random.default_rng(20261017) stream.
      Noted on the fixture before the freeze: the plug-in MI excess on 80 % of the held-out pages runs below the
      full-sample point (small-sample bias), so this interval is not centred on the point; the subsample median is
      printed beside.  The C-d rule (lower bound <= 0) stays as worded; the bias favours C-d holding.
  (e) s56 R(1) for all cores ("lag", d = 1) and for pairs whose first core is not a top-20 core ("lagx"):
      s56_core_repetition_lag.load_meta + .analyse(mode "core", seed 20261017 + 1000 x text index 0/1/2), its 200
      within-page shuffles and 500 80 %-page subsamples.  Orig fit = g1_edge_joint.split_names training pages (s56).

PRE-REGISTERED CALLS (per transliteration; PRIMARY Zattera values; the same calls on orig printed beside)
  C-a: M1 gain > 0 and its interval lower bound > 0.
  C-b: b_pos < 0 and its interval upper bound < 0.
  C-c: M7 > M1 (point values).
  C-d: the A14 excess interval includes 0 or lies below it (lower bound <= 0).
  C-e: R(1) all cores > 1 and its interval lower bound > 1.
  VERDICT: "not testable" if fewer than 70 % of tokens decompose on any transliteration; else "segmenter-independent"
  if all five calls hold under Zattera on all three transliterations; else "partly dependent", naming each failing
  (call, transliteration) and marking it FLIP if the call held under orig there, or "fails under both" if not.

FIXTURE (pre-freeze only, --synthetic): (1) parser: 20,000 words drawn from a planted slot grammar (each slot empty or
  one random glyph of that slot, >= 1 glyph) must all decompose, and every word whose slot assignment is unique must
  recover its planted slots exactly; 2,000 junk words (outside glyphs, slot-order violations, 4-runs) must all fail.
  (2) pipeline: three synthetic "transliterations" whose words are planted prefix (slots 0-2) + core (slots 3-6) +
  suffix (slots 8-11), cores repeating at lag 1 (p 0.25), prefix tied to the core's class (p 0.7), plus 8 % junk
  words; the Zattera PRIMARY layers must equal the planted layers on every decomposable token, and C-a, C-c, C-e must
  hold on all three (C-b, C-d reported).
Constraints: python -I, one CPU process, no new data; writes ONLY results_s76.txt and runs/s76/ (fixture: only
runs/s76/fixture.txt).  Wall limit 30 min.
Run: python -I s76_segmenter_independence.py      Fixture: --synthetic    Stub helper (lists local imports): --list-locals
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
import sys
import time
from collections import Counter, OrderedDict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import g1_edge_joint as G1  # noqa: E402
import s55_code_vs_generator as S55  # noqa: E402
import s56_core_repetition_lag as S56  # noqa: E402
import s69_prefix_stream_memory as S69  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s76_segmenter_independence.py"
STUB = ROOT / "s76_segmenter_independence.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s76"
SEED = 20261017
FIXTURE = "--synthetic" in sys.argv   # own flag: s55/s69 read "--fixture" from argv at import
LIST_LOCALS = "--list-locals" in sys.argv
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s76.txt"
WALL = 30 * 60
COVER_MIN = 0.70
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
# s69 / s56 / s55 resampling settings (source values; smaller on the fixture only)
N69_NULL, N69_SUB = (20, 100) if FIXTURE else (200, 500)
N56_SHUF, N56_BOOT = (40, 100) if FIXTURE else (200, 500)
N55_SHUF, N55_SUB, N55_SUB_SHUF = (40, 100, 10) if FIXTURE else (200, 500, 20)
SUB_FRAC = 0.8
CALL_IDS = ("C-a", "C-b", "C-c", "C-d", "C-e")
CALL_TEXT = OrderedDict([("C-a", "M1 gain > 0, interval above 0"), ("C-b", "b_pos < 0, interval below 0"),
                         ("C-c", "M7 > M1"), ("C-d", "A14 excess interval includes 0 or lies below it"),
                         ("C-e", "R(1) all cores > 1, interval above 1")])
PUBLISHED = {  # source-file values, printed beside the recomputed orig values (reproduction check only)
    "ZL3b": dict(M1=0.0999, M7=0.6881, b_pos=-0.0674, f2=-0.0527919, R1=1.169),
    "RF1b": dict(M1=0.0951, M7=0.6818, b_pos=-0.0922, f2=-0.0499643, R1=1.160),
    "IT2a": dict(M1=0.0961, M7=0.6437, b_pos=-0.0420, f2=-0.0507628, R1=1.220),
}

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


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


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
        if p.suffix == ".py":
            out.append(rel.as_posix())
    return sorted(set(out) | {SELF.name})


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
    missing = [m for m in local_modules() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; loaded but not in stub: {', '.join(missing) or '-'})"


# ======================================================================= Zattera slot model
SLOTS = OrderedDict([(0, ("q", "s", "d")), (1, ("o", "y")), (2, ("l", "r")), (3, ("t", "k", "p", "f")),
                     (4, ("ch", "sh")), (5, ("cth", "ckh", "cph", "cfh")), (6, ("e", "ee", "eee")), (7, ("s", "d")),
                     (8, ("o", "a")), (9, ("i", "ii", "iii")), (10, ("d", "l", "r", "m", "n")), (11, ("y",))])
SLOTS_OF: dict[str, tuple] = {}
for _s, _gs in SLOTS.items():
    for _g in _gs:
        SLOTS_OF[_g] = tuple(sorted(set(SLOTS_OF.get(_g, ())) | {_s}))
GLYPHS = sorted(SLOTS_OF, key=lambda g: (-len(g), g))
LAYER_SLOTS = {"primary": ((0, 1, 2), (3, 4, 5, 6, 7), (8, 9, 10, 11)),
               "slot7suffix": ((0, 1, 2), (3, 4, 5, 6), (7, 8, 9, 10, 11))}
# Fig. 4 grammar (paper text): state -> (glyphs, successors)
GRAMMAR = {"0_d": (["d"], ["4_C", "4_S"]), "0_q": (["q"], ["1_o"]), "0_s": (["s"], ["4_C"]),
           "1_o": (["o"], ["2_r", "3_tpkf", "4_C", "5_TPK", "6_eEB", "7_d", "8_a"]),
           "1_y": (["y"], ["3_tpkf", "4_C", "4_S"]), "2_l": (["l"], ["3_tpkf", "4_C", "4_S"]), "2_r": (["r"], ["8_a"]),
           "3_tpkf": (["t", "p", "k", "f"], ["4_C", "6_eEB", "8_a", "8_o", "11_y"]),
           "4_C": (["ch"], ["6_eEB", "8_a", "8_o", "10_d", "11_y"]), "4_S": (["sh"], ["6_eEB", "8_o"]),
           "5_TPK": (["cth", "cph", "ckh"], ["6_eEB", "8_a", "8_o"]),
           "6_eEB": (["e", "ee", "eee"], ["7_s", "8_o", "10_d", "11_y", "END"]), "7_d": (["d"], ["8_a", "8_o"]),
           "7_s": (["s"], ["END"]), "8_a": (["a"], ["9_iJ", "10_l", "10_m", "10_n", "10_r"]),
           "8_o": (["o"], ["10_d", "10_l", "10_r", "END"]), "9_iJ": (["i", "ii"], ["10_n", "10_r"]),
           "10_d": (["d"], ["11_y", "END"]), "10_l": (["l"], ["11_y", "END"]), "10_m": (["m"], ["END"]),
           "10_n": (["n"], ["END"]), "10_r": (["r"], ["END"]), "11_y": (["y"], ["END"])}
G_BEGIN = ["0_d", "0_q", "0_s", "1_o", "1_y", "2_l", "2_r", "3_tpkf", "4_C", "4_S", "5_TPK", "7_d", "8_a"]


def tokenizations(w):
    out = []

    def rec(i, acc):
        if i == len(w):
            out.append(tuple(acc))
            return
        for L in (3, 2, 1):
            g = w[i:i + L]
            if len(g) == L and g in SLOTS_OF:
                acc.append(g); rec(i + L, acc); acc.pop()
    rec(0, [])
    return out


def latest_assignment(toks):
    """Strictly increasing slots; from the right, each glyph takes its highest feasible slot.  None if impossible."""
    early, prev = [], -1
    for g in toks:
        c = [s for s in SLOTS_OF[g] if s > prev]
        if not c:
            return None
        prev = min(c); early.append(prev)
    out, nxt = [0] * len(toks), 12
    for i in range(len(toks) - 1, -1, -1):
        c = [s for s in SLOTS_OF[toks[i]] if early[i] <= s < nxt]
        if not c:
            return None
        out[i] = nxt = max(c)
    return out


def all_assignments(toks):
    res = []

    def rec(i, prev, acc):
        if i == len(toks):
            res.append(tuple(acc)); return
        for s in SLOTS_OF[toks[i]]:
            if s > prev:
                acc.append(s); rec(i + 1, s, acc); acc.pop()
    rec(0, -1, [])
    return res


_PARSE: dict = {}


def parse(w):
    """-> tuple of (glyph, slot) or None."""
    if w in _PARSE:
        return _PARSE[w]
    best = None
    for toks in sorted(tokenizations(w), key=len):
        a = latest_assignment(toks)
        if a is not None:
            best = tuple(zip(toks, a))
            break
    _PARSE[w] = best
    return best


def why_not(w):
    return "glyph" if not tokenizations(w) else "order"


def grammar_slots(w):
    """set of slot tuples over complete <BEGIN>..<END> paths of the Fig. 4 grammar."""
    res = set()
    for toks in tokenizations(w):
        def rec(i, states, acc):
            if i == len(toks):
                if any("END" in GRAMMAR[s][1] for s in states):
                    res.add(tuple(acc))
                return
            nxt = {}
            for st in (G_BEGIN if i == 0 else [n for s in states for n in GRAMMAR[s][1] if n != "END"]):
                if toks[i] in GRAMMAR[st][0]:
                    nxt.setdefault(int(st.split("_")[0]), []).append(st)
            for slot, sts in nxt.items():
                rec(i + 1, sts, acc + [slot])
        rec(0, None, [])
    return res


def layers(p, mapping="primary"):
    P, C, S = LAYER_SLOTS[mapping]
    return ("".join(g for g, s in p if s in P), "".join(g for g, s in p if s in C), "".join(g for g, s in p if s in S))


class ZatteraSegmenter:
    """Drop-in for SlotSegmenter.segment (prefix, core, suffix); no fitted parameters."""
    def __init__(self, und="drop", mapping="primary", tokens=()):
        self.und, self.mapping = und, mapping
        self.prefixes, self.suffixes = set(), set()
        for w in set(tokens):
            p = parse(w)
            if p is not None:
                a, _c, b = layers(p, mapping)
                self.prefixes.add(a); self.suffixes.add(b)

    def segment(self, w):
        p = parse(w)
        if p is None:
            if self.und == "whole":
                return ("", w, "")
            if self.und == "empty":
                return ("", "∅", "")
            raise ValueError(f"undecomposable word reached the drop-variant segmenter: {w!r}")
        return layers(p, self.mapping)


CONFIGS = OrderedDict([("orig", None), ("Z_primary", ("drop", "primary")), ("Z_S1_whole", ("whole", "primary")),
                       ("Z_S2_empty", ("empty", "primary")), ("Z_S3_slot7suffix", ("drop", "slot7suffix"))])


# ======================================================================= text filtering (drop variant)
def ok_word(w):
    return parse(w) is not None


def filt69(pages):
    out, dropped_pages = [], 0
    for p in pages:
        L, G, P = [], [], []
        for li, ln in enumerate(p["lines"]):
            keep = [j for j, w in enumerate(ln) if ok_word(w)]
            if not keep:
                continue
            L.append([ln[j] for j in keep])
            if p.get("gaps") is not None:
                G.append([p["gaps"][li][j] for j in keep])
            if p.get("para") is not None:
                P.append(p["para"][li])
        if L:
            out.append(dict(p, lines=L, gaps=G if p.get("gaps") is not None else None,
                            para=P if p.get("para") is not None else None))
        else:
            dropped_pages += 1
    return out, dropped_pages


def filt_lines_pages(pages):
    out = []
    for p in pages:
        L = [[w for w in ln if ok_word(w)] for ln in p["lines"]]
        L = [ln for ln in L if ln]
        if L:
            out.append(dict(p, lines=L))
    return out


def filt_by(by):
    out = OrderedDict()
    for k, lines in by.items():
        L = [[w for w in ln if ok_word(w)] for ln in lines]
        L = [ln for ln in L if ln]
        if L:
            out[k] = L
    return out


# ======================================================================= measures
def set_resampling():
    S69.N_NULL, S69.B_SUB = N69_NULL, N69_SUB
    S56.N_SHUF, S56.N_BOOT = N56_SHUF, N56_BOOT


def make_seg_factory(cfg):
    if cfg is None:
        return SlotSegmenter
    und, mapping = cfg
    return lambda tokens: ZatteraSegmenter(und, mapping, tokens)


def measure69(name, pages, cfg):
    S69.SlotSegmenter = make_seg_factory(cfg)
    try:
        t = S69.Text(name, pages)
        r = S69.measure(t)
    finally:
        S69.SlotSegmenter = SlotSegmenter
    p, ci, nul = r["point"], r["ci"], r["null"]
    return dict(M1=p["M1"], M1_ci=ci["M1"], M1_null=nul["M1"], M7=p["M7"], M7_ci=ci["M7"], b_pos=p["b_pos"],
                b_pos_ci=ci["b_pos"], n_M1=r["n"]["M1"], n_b=r["n"]["b_pos"], tr_te=(t.n_tr, t.n_te),
                n_prefix=t.n_pre, cls_sizes=t.cls_sizes, tokens69=t.tokens)


def measure55(name, pages, cfg):
    S55.SlotSegmenter = make_seg_factory(cfg)
    try:
        td = S55.TextData(name, pages)
    finally:
        S55.SlotSegmenter = SlotSegmenter
    cores, _fr, lid, _sec, _pg = td.concat(td.hp)
    f2 = td.core_core(cores, lid, N55_SHUF, np.random.default_rng(SEED))
    rng = np.random.default_rng(SEED)
    n = len(td.hp)
    m = int(round(SUB_FRAC * n))
    draws = []
    for _ in range(N55_SUB):
        idx = rng.choice(n, size=m, replace=False)
        c_, _f, l_, _s, _p = td.concat([td.hp[i] for i in idx])
        draws.append(td.core_core(c_, l_, N55_SUB_SHUF, rng))
    return dict(f2=f2, f2_ci=(float(np.nanpercentile(draws, 2.5)), float(np.nanpercentile(draws, 97.5))),
                f2_med=float(np.nanmedian(draws)),
                core_types55=td.n_core_types, tr_te55=(len(td.tr), len(td.te)))


def measure56(name, by, cfg, ti):
    if cfg is None:
        train, _ = G1.split_names(by)
        seg = SlotSegmenter([w for p in train for l in by[p] for w in l])
    else:
        seg = ZatteraSegmenter(cfg[0], cfg[1], [w for ls in by.values() for l in ls for w in l])
    res = S56.analyse(name, by, seg, "core", SEED + 1000 * ti)
    lag, (lo, hi) = res["r"]["lag"], res["ci"]["lag"]
    lx, (lox, hix) = res["r"]["lagx"], res["ci"]["lagx"]
    return dict(R1=float(lag[0]), R1_ci=(float(lo[0]), float(hi[0])), R1x=float(lx[0]), R1x_ci=(float(lox[0]), float(hix[0])),
                core_types56=res["types"])


def calls_of(v):
    return OrderedDict([
        ("C-a", (v["M1"] > 0 and v["M1_ci"][0] > 0, f"M1 {v['M1']:+.4f} [{v['M1_ci'][0]:+.4f},{v['M1_ci'][1]:+.4f}]")),
        ("C-b", (v["b_pos"] < 0 and v["b_pos_ci"][1] < 0, f"b_pos {v['b_pos']:+.4f} [{v['b_pos_ci'][0]:+.4f},{v['b_pos_ci'][1]:+.4f}]")),
        ("C-c", (v["M7"] > v["M1"], f"M7 {v['M7']:+.4f} vs M1 {v['M1']:+.4f}")),
        ("C-d", (v["f2_ci"][0] <= 0, f"A14 {v['f2']:+.4f} [{v['f2_ci'][0]:+.4f},{v['f2_ci'][1]:+.4f}]")),
        ("C-e", (v["R1"] > 1 and v["R1_ci"][0] > 1, f"R1 {v['R1']:.3f} [{v['R1_ci'][0]:.3f},{v['R1_ci'][1]:.3f}]")),
    ])


def verdict(V, cover, names):
    low = [T for T in names if cover[T]["tok_share"] < COVER_MIN]
    if low:
        return f"not testable (token coverage < {COVER_MIN:.0%} on {', '.join(low)})"
    fails = []
    for T in names:
        cz, co = calls_of(V[(T, "Z_primary")]), calls_of(V[(T, "orig")])
        for C in CALL_IDS:
            if not cz[C][0]:
                fails.append(f"{C} on {T} ({'FLIP: held under orig' if co[C][0] else 'fails under both'})")
    if not fails:
        return "segmenter-independent (all five calls hold under Zattera on all three transliterations)"
    return "partly dependent: " + "; ".join(fails)


# ======================================================================= coverage
def coverage(pages):
    tok = Counter(w for p in pages for ln in p["lines"] for w in ln)
    ntok, ntyp = sum(tok.values()), len(tok)
    reg = {w for w in tok if parse(w) is not None}
    rtok = sum(tok[w] for w in reg)
    why = Counter()
    for w, c in tok.items():
        if w not in reg:
            why[why_not(w)] += c
    g_tok = g_same = 0
    for w in reg:
        gs = grammar_slots(w)
        if gs:
            g_tok += tok[w]
            if tuple(s for _g, s in parse(w)) in gs:
                g_same += tok[w]
    und = Counter({w: c for w, c in tok.items() if w not in reg})
    und_multi = sum(c for c in und.values() if c >= 2)
    lay = Counter()
    for w in reg:
        a, c, b = layers(parse(w))
        lay["pfx_nonempty"] += tok[w] * bool(a); lay["core_nonempty"] += tok[w] * bool(c); lay["sfx_nonempty"] += tok[w] * bool(b)
    return dict(tokens=ntok, types=ntyp, reg_tokens=rtok, reg_types=len(reg), tok_share=rtok / ntok, typ_share=len(reg) / ntyp,
                und_glyph_tok=why["glyph"], und_order_tok=why["order"], und_multi_tok=und_multi,
                grammar_tok=g_tok, grammar_same_tok=g_same, layer_nonempty={k: v / rtok for k, v in lay.items()},
                und_top=und.most_common(40))


# ======================================================================= fixture
P_GLY = {s: list(g) for s, g in SLOTS.items()}


def fixture_parser_check():
    r = random.Random(7)
    n_ok = n_unique = n_unique_ok = n_layer_ok = 0
    N = 20000
    for _ in range(N):
        while True:
            planted = [(r.choice(P_GLY[s]), s) for s in range(12) if r.random() < 0.3]
            if planted:
                break
        w = "".join(g for g, _ in planted)
        p = parse(w)
        if p is None:
            continue
        n_ok += 1
        toks = [g for g, _ in planted]
        uniq = len(tokenizations(w)) == 1 and len(all_assignments(toks)) == 1
        if uniq:
            n_unique += 1
            n_unique_ok += tuple(p) == tuple(planted)
        P, C, S = LAYER_SLOTS["primary"]
        pl = ("".join(g for g, s in planted if s in P), "".join(g for g, s in planted if s in C), "".join(g for g, s in planted if s in S))
        n_layer_ok += layers(p) == pl
    junk = []
    for _ in range(2000):
        k = r.randrange(4)
        if k == 0:
            junk.append(r.choice(["g", "x", "v", "u", "j", "b", "z", "c", "h"]) + r.choice(["ol", "edy", "aiin", "y"]))
        elif k == 1:
            junk.append(r.choice(["y", "o", "l"]) + "q" + r.choice(["okedy", "ol", "ar"]))
        elif k == 2:
            junk.append(r.choice(["qo", "", "o"]) + r.choice(["kt", "kp", "tf", "chsh", "kchk"]) + r.choice(["y", "edy", "ol"]))
        else:
            junk.append(r.choice(["ch", "qok", "sh"]) + "eeee" + r.choice(["y", "dy", ""]))
    junk_fail = sum(parse(w) is None for w in junk)
    return dict(N=N, decomposed=n_ok, unique=n_unique, unique_ok=n_unique_ok, layer_ok=n_layer_ok, junk=len(junk), junk_fail=junk_fail)


def fixture_texts():
    pre = ["", "qo", "o", "y", "d", "s", "l", "ol", "ql", "dy"]
    pre = [x for x in pre if parse(x + "k") is not None and layers(parse(x + "k"))[0] == x]
    cores = sorted({c for c in (g3 + g4 + g5 + g6 for g3 in ["", "t", "k", "p", "f"] for g4 in ["", "ch", "sh"]
                                for g5 in ["", "cth", "ckh"] for g6 in ["", "e", "ee"]) if c})
    sfx = ["", "y", "dy", "ol", "or", "aiin", "ain", "al", "ar", "am", "o", "ody"]
    junk = ["gol", "xar", "ykt", "chkchy", "qeeeey", "yqol", "okchkey", "bdy", "kchk", "teeeey"]
    for x in pre + sfx:
        assert x == "" or parse(x) is not None, x

    def text(seed):
        r = random.Random(seed)
        cls_pre = {c: r.randrange(len(pre)) for c in cores}
        pages, truth = [], {}
        for pi in range(60):
            lines = []
            for _li in range(10):
                L, prev = [], None
                for _j in range(r.randint(7, 11)):
                    if r.random() < 0.08:
                        L.append(r.choice(junk)); continue
                    c = prev if prev is not None and r.random() < 0.25 else r.choice(cores)
                    a = pre[cls_pre[c]] if r.random() < 0.7 else r.choice(pre)
                    b = r.choice(sfx)
                    w = a + c + b
                    truth[w] = (a, c, b)
                    L.append(w); prev = c
                lines.append(L)
            pages.append(dict(id=f"p{pi:03d}", section="S" if pi % 2 else "T", lines=lines,
                              gaps=[[False] * len(l) for l in lines], para=[li % 5 == 0 for li in range(len(lines))]))
        return pages, truth
    return OrderedDict((T, text(s)) for T, s in (("FXa", 31), ("FXb", 32), ("FXc", 33)))


# ======================================================================= main
def fci(v, ci, f="+.4f"):
    return f"{v:{f}} [{ci[0]:{f}},{ci[1]:{f}}]"


def main():
    if LIST_LOCALS:
        for m in local_modules():
            print(m)
        return
    set_resampling()
    emit("S76: segmenter independence of the slot-layer picture (Zattera 2022 12-slot model vs SlotSegmenter)"
         + ("  [SYNTHETIC FIXTURE, not reported]" if FIXTURE else ""))
    emit(f"date: {clock()}")
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name}" + (f" sha256={sha256(STUB)}" if STUB.exists() else " (absent)") + f"  stub_match={stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"python {sys.version.split()[0]}; numpy {np.__version__}; seed {SEED}; s69 nulls {N69_NULL} / subsamples {N69_SUB}; "
         f"s56 shuffles {N56_SHUF} / subsamples {N56_BOOT}; s55 f2 shuffles {N55_SHUF}, interval {N55_SUB} subsamples x {N55_SUB_SHUF} shuffles")
    emit("slot table: " + "  ".join(f"{s}:{'/'.join(g)}" for s, g in SLOTS.items()))
    emit("layers (primary): prefix = slots 0-2, core = 3-7, suffix = 8-11; S3: core 3-6, suffix 7-11.  "
         "Undecomposable: primary drop; S1 whole-word core; S2 core '∅'.")
    emit()
    flush()

    if FIXTURE:
        fc = fixture_parser_check()
        emit("=== FIXTURE part 1: planted slot grammar -> parser ===")
        emit(f"  planted words {fc['N']}: decomposed {fc['decomposed']} (required all) -> {'PASS' if fc['decomposed'] == fc['N'] else 'FAIL'}")
        emit(f"  unique-assignment words {fc['unique']}: planted slots recovered {fc['unique_ok']} (required all) -> "
             f"{'PASS' if fc['unique_ok'] == fc['unique'] and fc['unique'] > 0 else 'FAIL'}")
        emit(f"  layer agreement over all planted words (ambiguous ones included, reported): {fc['layer_ok'] / fc['decomposed']:.4f}")
        emit(f"  junk words {fc['junk']}: undecomposable {fc['junk_fail']} (required all) -> {'PASS' if fc['junk_fail'] == fc['junk'] else 'FAIL'}")
        gs = grammar_slots("qokeedy"); gs2 = grammar_slots("daiin")
        emit(f"  grammar check: qokeedy {sorted(gs)} parse {parse('qokeedy')}; daiin {sorted(gs2)} parse {parse('daiin')}; "
             f"ol grammar {sorted(grammar_slots('ol'))} parse {parse('ol')}")
        emit()
        FX = fixture_texts()
        names = list(FX)
        src69 = {T: S69.norm_pages(FX[T][0]) for T in names}
        src55 = {T: [dict(id=p["id"], section=p["section"], lines=p["lines"]) for p in FX[T][0]] for T in names}
        src56 = {T: OrderedDict((p["id"], p["lines"]) for p in FX[T][0]) for T in names}
        bad = 0; tot = 0
        for T in names:
            for w, lay in FX[T][1].items():
                tot += 1; bad += layers(parse(w)) != lay
        emit(f"=== FIXTURE part 2: pipeline texts; planted layers recovered on {tot - bad}/{tot} planted word types "
             f"-> {'PASS' if bad == 0 else 'FAIL'}")
    else:
        names = list(TRANSLITS)
        src69, src55, src56, notes = {}, {}, {}, {}
        for T in names:
            pages, note = S69.voynich_pages(T)
            src69[T] = pages; notes[T] = note
            src55[T] = S55.voynich_pages(T)
            by, _lang = S56.load_meta(ROOT / "data" / "translit" / f"{TRANSLITS[T]}.meta.json")
            src56[T] = by
        for T in names:
            emit(f"  {T}: {notes[T]}")
    emit()

    # ---- coverage
    cover = OrderedDict()
    emit("=== decomposition coverage (unit: this text's tokens / word types; Zattera's concordance: 86.6 % tokens, 51.3 % types) ===")
    for T in names:
        c = cover[T] = coverage(src69[T])
        emit(f"  {T:5s} tokens {c['tokens']:6d} types {c['types']:5d} | decomposed tokens {c['reg_tokens']:6d} = {c['tok_share']:.1%}  "
             f"types {c['reg_types']:5d} = {c['typ_share']:.1%} | undecomposable tokens: outside glyphs {c['und_glyph_tok']}, "
             f"slot order {c['und_order_tok']}; of types seen >= 2 times {c['und_multi_tok']} tok ({c['und_multi_tok'] / c['tokens']:.1%}; Zattera 1.5 %)")
        emit(f"        Fig. 4 grammar generates {c['grammar_tok']} decomposed tokens ({c['grammar_tok'] / c['reg_tokens']:.1%}); "
             f"our slot assignment = a grammar assignment on {c['grammar_same_tok']} of them "
             f"({(c['grammar_same_tok'] / c['grammar_tok']) if c['grammar_tok'] else float('nan'):.1%}); non-empty layers among decomposed tokens: "
             + ", ".join(f"{k} {v:.1%}" for k, v in c["layer_nonempty"].items()))
        emit("        top undecomposable: " + " ".join(f"{w}:{n}" for w, n in c["und_top"][:15]))
    for T in names:
        d69, dp = filt69(src69[T])
        emit(f"  {T:5s} drop variant: {sum(len(l) for p in d69 for l in p['lines'])} tokens kept on {len(d69)} pages "
             f"({dp} pages emptied), lines {sum(len(p['lines']) for p in src69[T])} -> {sum(len(p['lines']) for p in d69)}")
    emit()
    flush()

    # ---- measures
    V = OrderedDict()
    emit("=== measures per text and configuration ===")
    for ti, T in enumerate(names):
        for cfg_name, cfg in CONFIGS.items():
            if time.time() - T0 > WALL:
                emit(f"STOPPED: wall limit exceeded at {clock()}; partial"); flush(); sys.exit(2)
            drop = cfg is not None and cfg[0] == "drop"
            p69 = filt69(src69[T])[0] if drop else src69[T]
            p55 = filt_lines_pages(src55[T]) if drop else src55[T]
            b56 = filt_by(src56[T]) if drop else src56[T]
            v = {}
            v.update(measure69(f"{T}_{cfg_name}", p69, cfg))
            v.update(measure55(f"{T}_{cfg_name}", p55, cfg))
            v.update(measure56(T, b56, cfg, ti))
            V[(T, cfg_name)] = v
            mu, sd = v["M1_null"]
            emit(f"  {T:5s} {cfg_name:17s} split69 {v['tr_te'][0]}/{v['tr_te'][1]} split55 {v['tr_te55'][0]}/{v['tr_te55'][1]} "
                 f"tok {v['tokens69']} prefixes {v['n_prefix']} cores55 {v['core_types55']} cores56 {v['core_types56']} | "
                 f"M1 {fci(v['M1'], v['M1_ci'])} excess {v['M1'] - mu:+.4f} (z {(v['M1'] - mu) / sd if sd > 0 else float('nan'):+.1f}) | "
                 f"b_pos {fci(v['b_pos'], v['b_pos_ci'])} | M7 {fci(v['M7'], v['M7_ci'])} | A14 {fci(v['f2'], v['f2_ci'])} (subsample median {v['f2_med']:+.4f}) | "
                 f"R1 {fci(v['R1'], v['R1_ci'], '.3f')} R1 non-top20 {fci(v['R1x'], v['R1x_ci'], '.3f')}  [{time.time() - T0:.0f}s]")
            flush()
    emit()
    if not FIXTURE:
        emit("=== reproduction check: recomputed orig vs published source values ===")
        for T in names:
            o, pb = V[(T, "orig")], PUBLISHED[T]
            emit(f"  {T:5s} M1 {o['M1']:+.4f} (s69 {pb['M1']:+.4f})  M7 {o['M7']:+.4f} (s69 {pb['M7']:+.4f})  b_pos {o['b_pos']:+.4f} "
                 f"(s69 {pb['b_pos']:+.4f})  A14 {o['f2']:+.5f} (s55 f2 {pb['f2']:+.5f})  R1 {o['R1']:.3f} (s56 {pb['R1']:.3f})")
        emit()

    # ---- side-by-side table
    emit("=== orig (SlotSegmenter) vs Zattera PRIMARY (values [95 % interval]) ===")
    rows = [("(a) M1 gain", "M1", "+.4f"), ("(b) b_pos", "b_pos", "+.4f"), ("(c) M7", "M7", "+.4f"),
            ("(d) A14 excess", "f2", "+.4f"), ("(e) R(1) all", "R1", ".3f"), ("(e) R(1) non-top20", "R1x", ".3f")]
    for T in names:
        o, z = V[(T, "orig")], V[(T, "Z_primary")]
        for lab, k, f in rows:
            emit(f"  {T:5s} {lab:20s} orig {fci(o[k], o[k + '_ci'], f):>28s}   Zattera {fci(z[k], z[k + '_ci'], f):>28s}")
        mo, mz = o["M1_null"][0], z["M1_null"][0]
        emit(f"  {T:5s} {'(a) M1 excess':20s} orig {o['M1'] - mo:+.4f} (null {mo:+.4f} sd {o['M1_null'][1]:.4f})   "
             f"Zattera {z['M1'] - mz:+.4f} (null {mz:+.4f} sd {z['M1_null'][1]:.4f})")
    emit()

    # ---- calls
    emit("=== PRE-REGISTERED CALLS (judged on Zattera PRIMARY; orig and S1-S3 beside) ===")
    for C in CALL_IDS:
        emit(f"  {C} {CALL_TEXT[C]}")
        for T in names:
            cells = []
            for cfg_name in CONFIGS:
                ok, s = calls_of(V[(T, cfg_name)])[C]
                cells.append(f"{cfg_name}={'holds' if ok else 'FAILS'}")
            emit(f"      {T:5s} Zattera: {'holds' if calls_of(V[(T, 'Z_primary')])[C][0] else 'FAILS'}  ({calls_of(V[(T, 'Z_primary')])[C][1]})   "
                 + " ".join(cells))
    emit()
    emit(f"VERDICT (Zattera PRIMARY): {verdict(V, cover, names)}")
    for cfg_name in ("Z_S1_whole", "Z_S2_empty", "Z_S3_slot7suffix"):
        VV = dict(V)
        for T in names:
            VV[(T, "Z_primary")] = V[(T, cfg_name)]
        emit(f"  same rule on {cfg_name} (reported only): {verdict(VV, cover, names)}")
    emit()

    if FIXTURE:
        emit("=== FIXTURE CHECK ===")
        ok = all(calls_of(V[(T, "Z_primary")])[C][0] for T in names for C in ("C-a", "C-c", "C-e"))
        emit(f"  C-a, C-c, C-e hold under Zattera PRIMARY on all three planted texts (required): {'PASS' if ok else 'FAIL'}")
        emit("  C-b, C-d on the fixture are reported only (planted lag-1 core repetition makes core->core MI positive).")
    else:
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        with (RUN_DIR / "values.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["translit", "config", "stat", "value", "lo95", "hi95"])
            for (T, cfg_name), v in V.items():
                for k in ("M1", "b_pos", "M7", "f2", "R1", "R1x"):
                    w.writerow([T, cfg_name, k, f"{v[k]:.6g}", f"{v[k + '_ci'][0]:.6g}", f"{v[k + '_ci'][1]:.6g}"])
                w.writerow([T, cfg_name, "M1_null_mean", f"{v['M1_null'][0]:.6g}", "", ""])
                w.writerow([T, cfg_name, "M1_null_sd", f"{v['M1_null'][1]:.6g}", "", ""])
        (RUN_DIR / "coverage.json").write_text(json.dumps(cover, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
        (RUN_DIR / "calls.json").write_text(json.dumps(
            {f"{T}|{cfg_name}": {C: [bool(a), b] for C, (a, b) in calls_of(v).items()} for (T, cfg_name), v in V.items()},
            indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
        emit("sidecars: runs/s76/values.csv, runs/s76/coverage.json, runs/s76/calls.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {clock()}")
    flush()


if __name__ == "__main__":
    main()
