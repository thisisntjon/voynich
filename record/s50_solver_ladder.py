"""s50 (P4-D2): solver positive-control ladder L1 -> L4 for the verbose-homophonic family (decision D-052).

Question: with the best simulated-annealing / MCMC solver we can build in this step, can a verbose homophonic cipher
matched to the manuscript's statistics be broken at 38k tokens? Read with workflow/research/phase-4-decipherability.md
Q1 / Q3 (ladder L1-L4, close rule) and workflow/research/phase-4.md (P4-D1 effect on the plan).

PRE-REGISTRATION (written 2026-10-17 23:40 - 2026-10-18 00:40 PDT before any solver run on a ladder rung; frozen in s50_solver_ladder.prereg.sha256,
which hashes this file and s50_solver.py; nothing below changes after a rung result is seen; a crash is reported as
FAILED in results_s50.txt and repaired only by a dated AMENDMENT appended here).

Development record (declared, not a rung; English (english_alice) and Tagalog (tagalog_florante_1838 plaintext,
tagalog_urbana_feliza_1864 LM), neither a ladder language; scratchpad scripts and --dev runs; no ladder language and
no ladder rung was run before the freeze):
  - plain homophonic, 138 units: 100 %. With 15 % nulls (20 null types): first version nulled every unit at once;
    after a null cap (40 % of the stream) it solved a uniform-weight test at 100 % with w_kl = 1 and 4.6 % with
    w_kl = 0 -> w_kl = 1 fixed.
  - on the ladder's own L2 construction (Dirichlet homophone weights) the one-phase schedule hit the null cap on every
    restart (found score -299,582 vs true key -213,952: a search failure, not an objective failure). Hotter starts
    (T0 200, 1000), a 3-gram curriculum and later null moves did not fix it. Diagnosis: with >= 75 % of the true null
    types flagged, letter-only search reaches 100 %; the frequency-rank start is trapped while random starts often
    succeed. Fix (frozen below): two phases per restart (letters only, then letters + nulls at low T), 8 restarts,
    random starts, and a key-free "transparency" null pre-flag. Result: L2 dev keys 1-3 all 100 % (one seed; a later
    check with other seeds solved 2 of 3, so this was superseded by the stepwise phase 2 below).
  - L3 dev: SlotSegmenter's default sets parse 21 % of tokens as planted; the MDL slot search (below) 98.7 %. The
    short candidate solves (1-2 restarts) were too weak to pick the right reading -> more restarts.
  - Still on L2 dev (English key 1; Tagalog florante/urbana, also not a ladder language, keys 2-3): phase 1 succeeds
    on few restarts; a phase-1 null penalty, a robust mixture LM log2(0.8 P + 0.2/23) and 3-gram curriculum did not
    help; stepwise forward null selection (phase 2 above) reached the true-key score on 1 of 3 restarts on English
    key 1 and near it on Tagalog key 3 -> adopted, with 16 restarts. Tagalog L1 (full settings): 3/3 keys ~98 %.
  Unused switches left in s50_solver.py at their off values: P1_ROBUST = None, P1_NULL_PEN = None.

Languages (six on disk, data/controls; no download). Letters: corpora.control (lower-case, accents stripped),
23-letter period alphabet (j->i, v->u, w->uu, sharp s->ss), spaces dropped.
  latin    plaintext latin_caesar            LM latin_augustine + latin_pliny_herbal   (different works)
  italian  plaintext italian_dante [0,100k)  LM italian_dante [120k, end)             (same work, disjoint, 20k gap)
  german   plaintext mhg_nibelungenlied      LM mhg_parzival                           (Middle High German; different works)
  occitan  plaintext occitan_croisade [0,100k) LM same text [120k, end)
  czech    plaintext czech_bible_kralicka_1613 [0,100k) LM same text [120k, end)
  catalan  plaintext catalan_tirant [0,100k) LM same text [120k, end)
  (plaintext = the first 100k letters of the plaintext text; the LM never sees them.)
The solver is GIVEN the true language's LM (language identification is not attempted; this favours the solver, so a
fail is conservative and a pass is weaker than the Q3 rule "true language ranked first", which is not tested here).

Ciphertext size and lines: 38,000 tokens laid on the ZL3b paragraph line-length sequence (p4d1.voynich_lines, 34,857
tokens), cycled from the first line until 38,000 tokens. Held-out split: half A = the lines whose cumulative token count
is <= 19,000, half B = the rest. The solver sees ONLY half A; the learned key (and, for L3/L4, the learned segmentation
sets) is applied unchanged to half B, where accuracy is scored.

Solver (s50_solver.py), one job = (rung, language, key):
  5-gram character LM: interpolated Witten-Bell over the 23 letters, dense table, trained on the language's LM text.
  State: letter[u] for every cipher unit type u of the stream, plus null[u] (rungs L2-L4).
  Score (bits) = LM + HOMO + NULL - w_kl * M * KL(decoded letter unigram || LM unigram), w_kl = 1.0, where LM is the
    5-gram log-likelihood of the decoded non-null letter stream, HOMO the ML homophone-choice log-likelihood
    sum_x[sum_{u in x} n_u log n_u - N_x log N_x], NULL the ML null-emission log-likelihood (Solver docstring).
  Moves: Gibbs sweeps over unit types in random order; each unit's options = 23 letters (+ null in phase 2),
    sampled with p ~ 2^(delta/T) (null options at T <= 1). Per restart: phase 1 = SWEEPS letter-only sweeps, T
    geometric 20 -> 0.5 (last two greedy); phase 2 (rungs with nulls) = stepwise forward null selection
    (s50_solver.Solver.stepwise_nulls: flag the one unit whose nulling raises the score most, re-anneal letters 3 sweeps
    at T = 1, repeat; at most STEPWISE = 60 rounds, stop when no unit gains), then 4 sweeps at T = 0.5 (last two
    greedy) with letter and null options for every unit (null flags may also be removed). Null share capped at 40 % of the stream. Restart 0 starts from the
    frequency-deficit key, restarts 1.. from letters drawn from the LM unigram; initial null flags = the top-k units by
    the key-free transparency score (s50_solver.transparency), k alternating 0, 8.
  Final solve: RESTARTS = 16, SWEEPS = 40; the best-scoring restart on half A is the key. L1 runs with null
    moves off (L1 has no nulls by definition); L2-L4 with null moves on.
  EM homophone cross-check: optional per the step; NOT run (stated, not claimed).
  Segmentation family for L3/L4 (declared): the slot grammar of scoreboard.metrics_new.SlotSegmenter: token =
    prefix + core + suffix, prefix = longest member of a prefix set (length <= 3) leaving >= 1 glyph, suffix = longest
    member of a suffix set (length <= 3) of the remainder leaving >= 1 glyph, core = rest. The solver chooses the
    (prefix set, suffix set) from two candidates: SlotSegmenter fitted on half A with its defaults, and the greedy MDL
    slot search started from it (mdl_sets docstring), and a READING from
    {sep: prefix, core and suffix are separate units; pair: the (prefix, suffix) pair is one unit and the core is
    ignored as null material; core: the core is the unit and the affix pair is ignored}. Unit types seen < 3 times in
    half A are forced null. Each (candidate, reading) gets a short solve (6 restarts, 30 sweeps); the choice maximises
    score + log-likelihood of the ignored layer (ML unigram) - 0.5 * log2(N_tokens_A) * (stream unit types + ignored
    types). The final solve (above) runs on the chosen (candidate, reading).

Scoring: per token of half B, true = the plaintext letters the token carries (nulls carry none), decoded = the
  letters the learned key gives the token's units under the learned segmentation (null units give nothing; a unit type
  never seen in half A gives '?'). Letter accuracy = sum_tokens max(0, len(true) - Levenshtein(true, decoded)) /
  sum_tokens len(true). Success for a key = accuracy >= 0.80 (step rule; the Q3 table's 90 % is reported beside).
  A (rung, language) cell PASSES if >= 2 of its 3 keys succeed. A rung PASSES IN A LANGUAGE if that cell passes.

Rungs (keys = seeds 1, 2, 3 per language; the same plaintext per language, different keys):
  L1 verbose homophonic, 138 letter units, segmentation given. Construction (per key seed): letter shares f_x of the
    plaintext; k_x = max(3, round(138 f_x)) adjusted by largest remainder to sum 138; each letter's k_x units are
    dealt round-robin to the slots core, suffix, prefix (so every letter has >= 1 unit per slot). Unit spellings are
    Voynich glyph strings: prefix units = ZL3b token-initial 2-3-grams then 1-grams by token frequency, taken greedily
    while the set stays prefix-free; suffix units likewise from token-final strings (suffix-free); core units = ZL3b
    SlotSegmenter cores by frequency, accepted only if every prefix x core x suffix combination (with empty affixes)
    parses back exactly under the slot grammar with the true sets (so the true segmentation is a member of the
    declared family). Tokens: core always, prefix with p 0.35, suffix with p 0.60; each present slot takes the next
    plaintext letter in reading order (prefix, core, suffix) and writes one of that letter's homophones in that slot,
    chosen with fixed per-unit weights ~ Dirichlet(1) (key seed). The solver gets the unit-id stream of half A.
  L2 = L1 + nulls: 20 null unit types (7 prefix, 6 core, 7 suffix, same spelling rules); each present slot is a null
    with p 0.15 (does not consume plaintext). Null status unknown to the solver.
  L3 = the L2 cipher with segmentation unknown: the solver sees only the glyph strings and must choose the segmentation
    from the declared family (above).
  L4 = L3's family with key parameters set so the ciphertext matches the manuscript. P4-D1 (results_p4d1_core_order.txt)
    showed letter-carrying cores with free affixes cannot reach A14 (12/12 cells CLEAR), so L4 carries the letters in
    the affix pair and fills the core slot with null material: slot sets = ZL3b's own SlotSegmenter prefix and suffix
    sets; 138 letter pairs + 20 null pairs drawn without replacement from ZL3b's attested (prefix, suffix) pairs,
    weighted by pair token frequency, frequent letters first (k_x = max(1, round(138 f_x)), largest remainder); a token
    is a null pair with p 0.15 else the next letter's homophone pair (weight ~ pair frequency); the core comes from a
    per-line palette: each line draws a length register r from ZL3b's token-weighted core-length distribution and a
    palette of K cores without replacement with weights f_c^alpha * exp(-beta |len(c) - r|) (K = 0: no palette, each
    token draws from the full weighted distribution); each token takes a palette core avoiding the previous token's
    core, restricted to cores that parse back exactly with its pair (else the global compatible list, same weights),
    with extra weight (n_ZL3b(prefix, core, suffix) + 0.5)^gamma (gamma = 0: core independent of the pair; gamma = 1:
    core follows ZL3b's real affix-core co-occurrence, which lowers h2 but lets the core echo the letter-bearing pair).
    Calibration (seed 0, latin plaintext; construction only, no solver): grid K in {0, 4, 12}, beta in {0, 1, 2},
    alpha in {0.7, 1.0, 1.3}, gamma in {0, 0.5, 1} (81 points); the grid point hitting all targets with the smallest max normalised
    distance is used for all languages and keys (else the smallest max distance, with the missed targets recorded).
    Targets (step text; Voynich ZL3b values printed beside):
      types   7,025 +-15 %  -> [5,971, 8,079]                 (distinct tokens of the 38,000)
      hapax   0.68 +- 0.04 (share of types seen once)
      h2      2.10 +- 0.05 (a1_profile.char_entropies, EVA characters with spaces)
      A14     core->core excess <= 0 (p4d1_core_order.core_excess, SlotSegmenter refit on the cipher, 200 shuffles)
      A5      within-line Moran I of token length (s21 estimator) inside s15_ranges within_manuscript x_moran_I
              [lo95, hi95] = [0.1086, 0.1700]
    Each L4 cipher's own five statistics are printed and every miss is listed. If a target cannot be hit at any grid
    point, that is recorded as evidence against the family (Q3), not repaired. The L4 solver jobs still run on the
    closest grid point. Reading: an L4 cell counts as a MATCHED-L4 pass only if it passes AND >= 2 of its 3 ciphers hit
    all five targets. A pass on ciphers that miss targets is reported as "solved the closest constructible L4, not a
    matched L4": the close rule's "fails L4" half is then not met, and its "cannot be constructed" half is.

Gate (step rule): L1 runs first; the next rung runs only while the previous rung passes in >= 1 language; the first
rung that passes in no language is recorded as the first failing rung and the ladder stops there.

Close rule (verbatim, phase-4-decipherability.md Q3): "If the best SA/MCMC solver, with EM as a cross-check, fails L4
in all six languages at 38k tokens within a stated budget (proposed: 50 CPU-hours), the computational Tier-1 route
closes for the verbose-homophonic family. That does not show that Voynich is not a cipher; it shows that a computer
will not read one built this way. If no cipher meeting L4's targets can be constructed at all, that is itself evidence
against the family. Record it as such."
Stated budget for this step: 6 h wall on <= WORKERS CPU processes (about 48 CPU-hours at most); a rung that exceeds
2 h wall is stopped and reported. EM was not run, so a close is reported as "closes under the close rule without the
EM cross-check". If the gate stops the ladder before L4, no L4 solver job runs; the L4 CONSTRUCTION (calibration grid
and the 18 L4 ciphers' statistics, no solver) is still run and reported, so the "cannot be constructed" half of the
close rule is answered; the "L4 fails" half is then reported as NOT TESTED (the L4 construction is not strictly L3 plus
tuning, so failure of an earlier rung is not read as an L4 failure), with the first failing rung named. The Voynich text is NOT run in this step, even if L4 passes.

Dev smoke test (declared): python -I s50_solver_ladder.py --dev OUTDIR [--tagalog] [--quick] runs every rung on one
non-ladder language (default english_alice letters 0-50k plaintext, LM from 55k on; --tagalog as above), 3 L4 grid
points, ignoring the gate (--quick: 4 restarts x 30 sweeps, short solves 2 x 10), and writes only under OUTDIR. It checks the code paths; it is not a rung and its numbers are not results.

Run: python -I s50_solver_ladder.py   Writes: results_s50.txt, runs/s50/ (ciphers, keys, traces) only.
"""
from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import a1_profile  # noqa: E402
import corpora  # noqa: E402
import p4d1_core_order as P4  # noqa: E402
import s50_solver as S  # noqa: E402
import scoreboard.metrics_new as mn  # noqa: E402
import vparse  # noqa: E402

SELF = ROOT / "s50_solver_ladder.py"
STUB = ROOT / "s50_solver_ladder.prereg.sha256"
OUT = ROOT / "results_s50.txt"
RUN = ROOT / "runs" / "s50"
N_TOK, HALF = 38000, 19000
PLAIN_N, GAP = 100_000, 20_000
N_LET_UNITS, N_NULL_UNITS = 138, 20
P_PRE, P_SUF, P_NULL = 0.35, 0.60, 0.15
KEYS = (1, 2, 3)
W_KL, T0, T1 = 1.0, 20.0, 0.5
RESTARTS, SWEEPS = 16, 40
SHORT_RESTARTS, SHORT_SWEEPS = 6, 30
S.STEPWISE = 60
SEG_GRID = [(0.01, 0.5)]
READINGS = ("sep", "pair", "core")
MIN_COUNT = 3
ACC_PASS, ACC_Q3 = 0.80, 0.90
WORKERS = 8
RUNG_LIMIT_S = 2 * 3600
TOTAL_LIMIT_S = 6 * 3600
L4_GRID = [(K, b, a, g) for K in (0, 4, 12) for b in (0.0, 1.0, 2.0) for a in (0.7, 1.0, 1.3) for g in (0.0, 0.5, 1.0)]
TARGET = dict(types=(7025 * 0.85, 7025 * 1.15), hapax=(0.64, 0.72), h2=(2.05, 2.15), a14=(-1e9, 0.0),
              moran=(0.10862106754681204, 0.1700111843378619))
LANGS = {
    "latin": ("latin_caesar", ["latin_augustine", "latin_pliny_herbal"]),
    "italian": ("italian_dante", None),
    "german": ("mhg_nibelungenlied", ["mhg_parzival"]),
    "occitan": ("occitan_croisade_albigeoise", None),
    "czech": ("czech_bible_kralicka_1613", None),
    "catalan": ("catalan_tirant", None),
}
DEV = "--dev" in sys.argv
if DEV:   # English-only smoke test of the code paths (declared in the docstring); never a rung, never a result
    _o = Path(sys.argv[sys.argv.index("--dev") + 1])
    OUT, RUN = _o / "dev_results.txt", _o / "runs"
    if "--tagalog" in sys.argv:
        LANGS = {"tagalog": ("tagalog_florante_1838", ["tagalog_urbana_feliza_1864"])}
    else:
        LANGS = {"english": ("english_alice", None)}
        PLAIN_N, GAP = 50_000, 5_000
    KEYS = (1, 2, 3)
    if "--quick" in sys.argv:
        RESTARTS, SWEEPS, SHORT_RESTARTS, SHORT_SWEEPS = 4, 30, 2, 10
    L4_GRID = [(0, 0.0, 1.0, 1.0), (4, 1.0, 1.0, 0.5), (12, 2.0, 1.3, 0.0)]
log: list[str] = []
L4_HIT: dict = {}
L4_MATCHED_PASS: list = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stub_match():
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty'})"


def clock():
    try:
        return subprocess.run(["date"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return time.strftime("%Y-%m-%d %H:%M:%S") + " (time.strftime; `date` unavailable)"


# ------------------------------------------------------------------ texts
def lang_texts(lang):
    plain_name, lm_names = LANGS[lang]
    t = S.letters_of(corpora.control(plain_name))
    plain = t[:PLAIN_N]
    if lm_names:
        lmt = np.concatenate([S.letters_of(corpora.control(n)) for n in lm_names])
    else:
        lmt = t[PLAIN_N + GAP:]
    return plain, lmt


_LM_CACHE = {}


def get_lm(lang):
    if lang not in _LM_CACHE:
        plain, lmt = lang_texts(lang)
        lm, q, _lm3 = S.train_lm(lmt)
        _LM_CACHE[lang] = (lm, q, plain, len(lmt))
    return _LM_CACHE[lang]


# ------------------------------------------------------------------ Voynich reference
def voynich():
    vl = P4.voynich_lines(vparse.DATA)
    lines = [ln for _, ln in vl if ln]
    toks = [w for ln in lines for w in ln]
    return lines, toks


def line_lengths(vlines):
    out, n, i = [], 0, 0
    while n < N_TOK:
        L = len(vlines[i % len(vlines)])
        L = min(L, N_TOK - n)
        out.append(L)
        n += L
        i += 1
    return out


def slot_parse(w, pre, suf):
    p = ""
    for L in range(min(3, len(w) - 1), 0, -1):
        if w[:L] in pre:
            p = w[:L]
            break
    rest = w[len(p):]
    s = ""
    for L in range(min(3, len(rest) - 1), 0, -1):
        if rest[-L:] in suf:
            s = rest[-L:]
            break
    return p, rest[:len(rest) - len(s)], s


# ------------------------------------------------------------------ statistics
def moran_within(lines):
    x, left, right = [], [], []
    for ln in lines:
        st = len(x)
        x.extend(len(t) for t in ln)
        if len(ln) > 1:
            left.extend(range(st, st + len(ln) - 1))
            right.extend(range(st + 1, st + len(ln)))
    x = np.asarray(x, dtype=np.float64)
    z = x - x.mean()
    return float(len(x) / len(left) * np.dot(z[left], z[right]) / np.dot(z, z))


def stats(lines):
    toks = [w for ln in lines for w in ln]
    c = Counter(toks)
    ex, _sd, _nc, _np = P4.core_excess(toks, lines)
    return dict(types=len(c), hapax=sum(1 for v in c.values() if v == 1) / len(c),
                h2=a1_profile.char_entropies(toks)["h2"], a14=ex, moran=moran_within(lines))


def hits(st):
    return {k: TARGET[k][0] <= st[k] <= TARGET[k][1] for k in TARGET}


def target_dist(st):
    d = [abs(math.log(st["types"] / 7025)) / math.log(1.15), abs(st["hapax"] - 0.68) / 0.04,
         abs(st["h2"] - 2.10) / 0.05, max(0.0, st["a14"]) / 0.01 + (1.0 if st["a14"] > 0 else 0.0)]
    lo, hi = TARGET["moran"]
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    d.append(abs(st["moran"] - mid) / half)
    return max(d)


def fmt_stats(st):
    h = hits(st)
    return (f"types {st['types']}{'' if h['types'] else '*'}  hapax {st['hapax']:.3f}{'' if h['hapax'] else '*'}  "
            f"h2 {st['h2']:.3f}{'' if h['h2'] else '*'}  A14 {st['a14']:+.4f}{'' if h['a14'] else '*'}  "
            f"Moran {st['moran']:+.4f}{'' if h['moran'] else '*'}")


# ------------------------------------------------------------------ L1-L3 construction
def alloc(f, total, kmin):
    raw = f * total
    k = np.maximum(kmin, np.floor(raw)).astype(int)
    while k.sum() < total:
        k[int(np.argmax(raw - k))] += 1
    while k.sum() > total:
        cand = np.where(k > kmin, k - raw, -np.inf)
        k[int(np.argmax(cand))] -= 1
    return k


def build_inventory(vtoks, rng):
    """Prefix-free prefix units, suffix-free suffix units, compatible core units (spellings only)."""
    fc = Counter(vtoks)
    ini, fin = Counter(), Counter()
    for w, c in fc.items():
        for L in (1, 2, 3):
            if len(w) > L:
                ini[w[:L]] += c
                fin[w[-L:]] += c
    need_p = need_s = 0
    # caller decides sizes; build long ranked candidate lists
    def ranked(cnt):
        a = [s for s, _ in cnt.most_common() if len(s) >= 2]
        b = [s for s, _ in cnt.most_common() if len(s) == 1]
        return a + b
    return ranked(ini), ranked(fin), fc


def pick_free(cands, n, rng, suffix):
    out = []
    pool = list(cands[:max(n * 4, 60)])
    rng.shuffle(pool)
    pool.sort(key=lambda s: cands.index(s) // 8)   # keep frequency order in blocks of 8, shuffled within
    for s in pool:
        ok = True
        for t in out:
            if (t.endswith(s) or s.endswith(t)) if suffix else (t.startswith(s) or s.startswith(t)):
                ok = False
                break
        if ok:
            out.append(s)
        if len(out) == n:
            break
    if len(out) < n:
        for s in cands:
            if s in out:
                continue
            if all(not ((t.endswith(s) or s.endswith(t)) if suffix else (t.startswith(s) or s.startswith(t))) for t in out):
                out.append(s)
            if len(out) == n:
                break
    return out


def make_l123_key(plain, vtoks, vcores, seed):
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)
    f = np.bincount(plain, minlength=S.A) / len(plain)
    k = alloc(f, N_LET_UNITS, 3)
    slots = {"C": [], "S": [], "P": []}         # (letter, unit index in slot)
    for x in range(S.A):
        for j in range(k[x]):
            slots["CSP"[j % 3]].append(x)
    n_null = {"P": 7, "C": 6, "S": 7}
    ini, fin, _ = build_inventory(vtoks, rng)
    pre = pick_free(ini, len(slots["P"]) + n_null["P"], rng, False)
    suf = pick_free(fin, len(slots["S"]) + n_null["S"], rng, True)
    preset, sufset = set(pre), set(suf)
    cores = []
    for c in vcores:
        if not c or len(cores) >= len(slots["C"]) + n_null["C"]:
            continue
        ok = all(slot_parse(p + c + s, preset, sufset) == (p, c, s) for p in [""] + pre for s in [""] + suf)
        if ok:
            cores.append(c)
    if len(cores) < len(slots["C"]) + n_null["C"]:
        raise RuntimeError("core inventory exhausted")
    rng.shuffle(pre); rng.shuffle(suf); rng.shuffle(cores)
    spell = {"P": pre, "C": cores, "S": suf}
    units = []   # (slot, spelling, letter or -1)
    hom = {}
    for sl in "PCS":
        letters = slots[sl] + [-1] * n_null[sl]
        for i, x in enumerate(letters):
            uid = len(units)
            units.append((sl, spell[sl][i], int(x)))
            hom.setdefault((sl, int(x)), []).append(uid)
    wts = nrng.dirichlet(np.ones(len(units))) * len(units)
    return dict(units=units, hom={f"{a}|{b}": v for (a, b), v in hom.items()}, weights=wts.tolist(),
                pre=pre, suf=suf, alloc=k.tolist())


def gen_l123(plain, key, nulls, seed, lens):
    rng = random.Random(seed * 1000 + 7)
    units, hom, wts = key["units"], key["hom"], key["weights"]
    it = 0
    toks, truth, unit_seq = [], [], []
    for _ in range(sum(lens)):
        slots = ["P"] if rng.random() < P_PRE else []
        slots.append("C")
        if rng.random() < P_SUF:
            slots.append("S")
        spell, tl, us = "", [], []
        for sl in slots:
            if nulls and rng.random() < P_NULL:
                cand = hom[f"{sl}|-1"]
            else:
                x = int(plain[it % len(plain)])
                it += 1
                cand = hom[f"{sl}|{x}"]
                tl.append(x)
            u = rng.choices(cand, weights=[wts[c] for c in cand])[0]
            spell += units[u][1]
            us.append(u)
        toks.append(spell)
        truth.append(tl)
        unit_seq.append(us)
    return toks, truth, unit_seq


# ------------------------------------------------------------------ L4 construction
class L4Base:
    def __init__(self, vtoks):
        self.seg = mn.SlotSegmenter(vtoks)
        trip = [self.seg.segment(w) for w in vtoks]
        self.pairs = Counter((p, s) for p, _, s in trip)
        self.core_f = Counter(c for _, c, _ in trip)
        self.cores = list(self.core_f)
        self.cf = np.array([self.core_f[c] for c in self.cores], dtype=np.float64)
        self.clen = np.array([len(c) for c in self.cores])
        lens = Counter()
        for _, c, _ in trip:
            lens[len(c)] += 1
        self.len_vals = list(lens)
        self.len_w = [lens[v] for v in self.len_vals]
        self._compat = {}
        self.tri = Counter(trip)
        self._tri = {}

    def tri_w(self, pair, g):
        v = self._tri.get(pair)
        if v is None:
            p, s = pair
            v = np.array([self.tri[(p, c, s)] for c in self.cores], dtype=np.float64) + 0.5
            self._tri[pair] = v
        return v ** g

    def compat(self, pair):
        m = self._compat.get(pair)
        if m is None:
            p, s = pair
            m = np.array([self.seg.segment(p + c + s) == (p, c, s) for c in self.cores])
            self._compat[pair] = m
        return m


def make_l4_key(plain, base, seed):
    rng = random.Random(seed)
    f = np.bincount(plain, minlength=S.A) / len(plain)
    k = alloc(f, N_LET_UNITS, 1)
    pool = dict(base.pairs)
    hom = {}
    order = list(np.argsort(-f, kind="stable")) + [-1]
    for x in order:
        n = N_NULL_UNITS if x == -1 else int(k[x])
        got = []
        for _ in range(n):
            ks = list(pool)
            ch = rng.choices(ks, weights=[pool[q] for q in ks])[0]
            got.append(ch)
            del pool[ch]
        hom[int(x)] = got
    return dict(hom={str(x): [list(p) for p in v] for x, v in hom.items()}, alloc=k.tolist())


def gen_l4(plain, key, base, params, seed, lens):
    K, beta, alpha, gam = params
    rng = np.random.default_rng(seed * 1000 + 11)
    hom = {int(x): [tuple(p) for p in v] for x, v in key["hom"].items()}
    w_core = base.cf ** alpha
    it = 0
    lines, truth = [], []
    for L in lens:
        r = rng.choice(base.len_vals, p=np.array(base.len_w) / sum(base.len_w))
        wl = w_core * np.exp(-beta * np.abs(base.clen - r))
        if K > 0:
            pal = rng.choice(len(base.cores), size=min(K, len(base.cores)), replace=False, p=wl / wl.sum())
        prev = -1
        ln, tl = [], []
        for _ in range(L):
            if rng.random() < P_NULL:
                cand, x = hom[-1], None
            else:
                x = int(plain[it % len(plain)])
                it += 1
                cand = hom[x]
            pw = np.array([base.pairs[c] for c in cand], dtype=np.float64)
            pair = cand[int(rng.choice(len(cand), p=pw / pw.sum()))]
            ok = base.compat(pair)
            tw = base.tri_w(pair, gam)
            ci = -1
            if K > 0:
                opts = [c for c in pal if ok[c] and c != prev]
                if opts:
                    ow = tw[opts]
                    ci = int(opts[int(rng.choice(len(opts), p=ow / ow.sum()))])
            if ci < 0:
                ww = wl * ok * tw
                if prev >= 0:
                    ww[prev] = 0.0
                if ww.sum() <= 0:
                    ww = ok.astype(np.float64)
                ci = int(rng.choice(len(base.cores), p=ww / ww.sum()))
            prev = ci
            ln.append(pair[0] + base.cores[ci] + pair[1])
            tl.append([] if x is None else [x])
        lines.append(ln)
        truth.extend(tl)
    return lines, truth


# ------------------------------------------------------------------ solving
def levenshtein(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def accuracy(truth, dec):
    num = den = 0
    for t, d in zip(truth, dec):
        den += len(t)
        num += max(0, len(t) - levenshtein(t, d))
    return num / den if den else float("nan")


def stream_from(tok_units, names=None):
    """tok_units: list of per-token unit-name lists -> (int stream, name->id)."""
    ids = {} if names is None else names
    s = []
    for us in tok_units:
        for u in us:
            if u not in ids:
                ids[u] = len(ids)
            s.append(ids[u])
    return np.asarray(s, dtype=np.int64), ids


def reading_units(parsed, reading):
    """parsed: list of (p, c, s). Returns per-token unit names and the ignored-layer symbol per token."""
    out, ign = [], []
    for p, c, s in parsed:
        if reading == "sep":
            out.append(([f"P:{p}"] if p else []) + [f"C:{c}"] + ([f"S:{s}"] if s else []))
            ign.append(None)
        elif reading == "pair":
            out.append([f"A:{p}|{s}"])
            ign.append(c)
        else:
            out.append([f"C:{c}"])
            ign.append(f"{p}|{s}")
    return out, ign


def run_solve(s, lm, q, allow_null, restarts, sweeps, seed, deadline, trace, tag):
    n = np.bincount(s)
    forced = n < MIN_COUNT
    return S.solve(s, lm, q, w_kl=W_KL, allow_null=allow_null, restarts=restarts, sweeps=sweeps, T0=T0, T1=T1,
                   seed=seed, forced_null=forced, deadline=deadline, trace=trace, tag=tag)


def mdl_sets(toks, pre0, suf0, trace):
    """Greedy MDL search over (prefix set, suffix set) in the slot grammar. Candidates: token-initial / token-final
    glyph strings of length 1-3 covering >= 0.2 % of tokens (token longer than the string). Cost = sum over slots of
    N * H(slot unigram) + lexicon spelling cost sum_{distinct slot strings} (len + 1) * log2(G + 1), G = glyph types.
    Start from (pre0, suf0); toggle each candidate in turn, keep a toggle if the cost falls; up to 3 passes."""
    fc = Counter(toks)
    N = len(toks)
    G = len({ch for w in fc for ch in w})
    lg = math.log2(G + 1)
    ini, fin = Counter(), Counter()
    for w, c in fc.items():
        for L in (1, 2, 3):
            if len(w) > L:
                ini[w[:L]] += c
                fin[w[-L:]] += c
    cp = sorted(a for a, c in ini.items() if c >= 0.002 * N)
    cs = sorted(a for a, c in fin.items() if c >= 0.002 * N)

    def cost(pre, suf):
        slots = [Counter(), Counter(), Counter()]
        for w, c in fc.items():
            for i, x in enumerate(slot_parse(w, pre, suf)):
                slots[i][x] += c
        tot = 0.0
        for sc in slots:
            tot += N * math.log2(N) - sum(v * math.log2(v) for v in sc.values())
            tot += sum((len(x) + 1) * lg for x in sc)
        return tot

    pre, suf = set(pre0), set(suf0)
    best = cost(pre, suf)
    c0 = best
    for _pass in range(3):
        changed = False
        for side, cands in (("P", cp), ("S", cs)):
            for a in cands:
                st = pre if side == "P" else suf
                st ^= {a}
                c = cost(pre, suf)
                if c < best - 1e-6:
                    best = c
                    changed = True
                else:
                    st ^= {a}
        if not changed:
            break
    trace.append(f"MDL slot search: {len(cp)} prefix / {len(cs)} suffix candidates; cost {c0:.0f} -> {best:.0f}; |P|={len(pre)} |S|={len(suf)}")
    return pre, suf


def decode_tokens(tok_units, ids, letter, null):
    dec = []
    for us in tok_units:
        d = []
        for u in us:
            i = ids.get(u)
            if i is None or i >= len(letter):
                d.append(-9)
            elif not null[i]:
                d.append(int(letter[i]))
        dec.append(d)
    return dec


def job(args):
    rung, lang, kseed, path, deadline = args
    t0 = time.time()
    lm, q, _plain, _nlm = get_lm(lang)
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    truth, nA = d["truth"], d["nA"]
    trace = [f"job {rung} {lang} key {kseed} start {time.strftime('%H:%M:%S')}"]
    seed = 50_000 + kseed * 101 + list(LANGS).index(lang) * 7 + int(rung[1]) * 1009
    info = {}
    if rung in ("L1", "L2"):
        tu = [[str(u) for u in us] for us in d["unit_seq"]]
        sA, ids = stream_from(tu[:nA])
        letter, null, sc = run_solve(sA, lm, q, rung != "L1", RESTARTS, SWEEPS, seed, deadline, trace, rung)
        dec = decode_tokens(tu[nA:], ids, letter, null)
        info["chosen"] = "given"
    else:
        toks = d["tokens"]
        tA, tB = toks[:nA], toks[nA:]
        Ntok = len(tA)
        cands, seen = [], set()
        for ms, ef in SEG_GRID:
            sg = mn.SlotSegmenter(tA, min_share=ms, ent_frac=ef)
            keyset = (frozenset(sg.prefixes), frozenset(sg.suffixes))
            if keyset in seen:
                continue
            seen.add(keyset)
            cands.append(((ms, ef), sg.prefixes, sg.suffixes))
        mp_, ms_ = mdl_sets(tA, cands[0][1], cands[0][2], trace)
        if (frozenset(mp_), frozenset(ms_)) not in seen:
            cands.append((("mdl", "-"), mp_, ms_))
        best = None
        for (ms, ef), pre, suf in cands:
            parsedA = [slot_parse(w, pre, suf) for w in tA]
            for rd in READINGS:
                tu, ign = reading_units(parsedA, rd)
                sA, ids = stream_from(tu)
                _l, _n, sc = run_solve(sA, lm, q, True, SHORT_RESTARTS, SHORT_SWEEPS, seed, deadline, None, "")
                ig = 0.0
                n_ign = 0
                if rd != "sep":
                    cnt = Counter(ign)
                    ig = sum(v * math.log2(v / Ntok) for v in cnt.values())
                    n_ign = len(cnt)
                crit = sc + ig - 0.5 * math.log2(Ntok) * (len(ids) + n_ign)
                trace.append(f"cand ({ms},{ef}) |P|={len(pre)} |S|={len(suf)} reading={rd} units={len(ids)} score={sc:.0f} ignored={ig:.0f} crit={crit:.0f}")
                if best is None or crit > best[0]:
                    best = (crit, (ms, ef), pre, suf, rd)
        _c, msef, pre, suf, rd = best
        info["chosen"] = f"seg{msef} {rd} |P|={len(pre)} |S|={len(suf)}"
        info["true_sets"] = d.get("true_sets_note", "")
        parsedA = [slot_parse(w, pre, suf) for w in tA]
        tu, _ = reading_units(parsedA, rd)
        sA, ids = stream_from(tu)
        letter, null, sc = run_solve(sA, lm, q, True, RESTARTS, SWEEPS, seed + 1, deadline, trace, f"final {rd}")
        parsedB = [slot_parse(w, pre, suf) for w in tB]
        tuB, _ = reading_units(parsedB, rd)
        dec = decode_tokens(tuB, ids, letter, null)
        if "true_pre" in d:
            info["seg_match_true"] = (set(pre) == set(d["true_pre"]) and set(suf) == set(d["true_suf"]))
            info["reading_true"] = d["true_reading"]
    acc = accuracy(truth[nA:], dec)
    accA = None
    info.update(acc=acc, score=sc, nulls=int(null.sum()), units=int(len(letter)), elapsed=time.time() - t0)
    trace.append(f"RESULT acc={acc:.4f} info={info}")
    tp = RUN / "traces" / f"{rung}_{lang}_k{kseed}.txt"
    tp.write_text("\n".join(trace) + "\n", encoding="utf-8", newline="\n")
    (RUN / "keys" / f"{rung}_{lang}_k{kseed}_learned.json").write_text(json.dumps(
        dict(letter=letter.tolist(), null=null.tolist(), ids=list(ids.keys()) if isinstance(ids, dict) else None)),
        encoding="utf-8")
    return rung, lang, kseed, info


def l4_calibrate(vtoks, vseg, plains, cal_lang, lens):
    base = L4Base(vtoks)
    emit(f"L4 base: ZL3b SlotSegmenter |P|={len(vseg.prefixes)} |S|={len(vseg.suffixes)}, {len(base.pairs)} attested pairs, {len(base.cores)} cores")
    calk = make_l4_key(plains[cal_lang], base, 0)
    grid = []
    for prm in L4_GRID:
        ln, _tr = gen_l4(plains[cal_lang], calk, base, prm, 0, lens)
        st = stats(ln)
        grid.append((prm, st))
        emit(f"L4 calibration K={prm[0]:<2} beta={prm[1]:<3} alpha={prm[2]:<3} gamma={prm[3]:<3}: {fmt_stats(st)}  dist {target_dist(st):.2f}")
    allhit = [(target_dist(st), prm, st) for prm, st in grid if all(hits(st).values())]
    if allhit:
        _d, prm, st = min(allhit)
        note = f"L4 calibration: grid point K={prm[0]} beta={prm[1]} alpha={prm[2]} gamma={prm[3]} hits all five targets"
    else:
        _d, prm, st = min((target_dist(st), prm, st) for prm, st in grid)
        missed = [k for k, v in hits(st).items() if not v]
        note = (f"L4 calibration: NO grid point hits all five targets; closest K={prm[0]} beta={prm[1]} "
                f"alpha={prm[2]} gamma={prm[3]} misses {missed} -> recorded as evidence against the family (Q3)")
        per = {k: sum(hits(s)[k] for _p, s in grid) for k in TARGET}
        note += f"; grid points hitting each target: {per}"
    emit(note)
    return base, prm, note


def l4_construction_only(vtoks, vseg, plains, cal_lang, lens):
    emit("=== L4 construction only (gate stopped the ladder; no L4 solver job) ===")
    base, prm, note = l4_calibrate(vtoks, vseg, plains, cal_lang, lens)
    for lang in LANGS:
        for k in KEYS:
            key = make_l4_key(plains[lang], base, k)
            ln, _truth = gen_l4(plains[lang], key, base, prm, k, lens)
            emit(f"L4 cipher {lang} key {k}: {fmt_stats(stats(ln))}")
    return note


# ------------------------------------------------------------------ main
def split_index(lens):
    n, k = 0, 0
    for L in lens:
        if n + L > HALF:
            break
        n += L
        k += 1
    return n


def write_cipher(rung, lang, kseed, payload):
    p = RUN / "ciphers" / f"{rung}_{lang}_k{kseed}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def run_rung(rung, payloads, t_start_total):
    t0 = time.time()
    deadline = min(t0 + RUNG_LIMIT_S, t_start_total + TOTAL_LIMIT_S)
    jobs = [(rung, lang, k, str(p), deadline) for (lang, k), p in payloads.items()]
    res = {}
    stopped = False
    with mp.get_context("spawn").Pool(WORKERS) as pool:
        it = pool.imap_unordered(job, jobs)
        for _ in jobs:
            try:
                r = it.next(timeout=max(1.0, deadline - time.time() + 600))
            except mp.TimeoutError:
                stopped = True
                break
            res[(r[1], r[2])] = r[3]
        pool.terminate()
    el = time.time() - t0
    emit(f"--- {rung} results (elapsed {el / 60:.1f} min{'; STOPPED at time limit' if stopped or el > RUNG_LIMIT_S else ''})")
    langs_pass = []
    for lang in LANGS:
        accs = []
        for k in KEYS:
            info = res.get((lang, k))
            if info is None:
                emit(f"{rung} {lang:<8} key {k}: NOT FINISHED")
                continue
            accs.append(info["acc"])
            extra = f"  chosen={info['chosen']}" + (f" seg_true={info.get('seg_match_true')} true_reading={info.get('reading_true')}" if "seg_match_true" in info else "")
            emit(f"{rung} {lang:<8} key {k}: acc {info['acc']:.4f} {'OK' if info['acc'] >= ACC_PASS else 'fail'}"
                 f" (>=0.90: {'yes' if info['acc'] >= ACC_Q3 else 'no'})  nulls {info['nulls']}/{info['units']} units"
                 f"  {info['elapsed'] / 60:.1f} min{extra}")
        n_ok = sum(a >= ACC_PASS for a in accs)
        cell = n_ok >= 2
        if cell:
            langs_pass.append(lang)
        emit(f"{rung} {lang:<8} CELL {'PASS' if cell else 'FAIL'} ({n_ok}/3 keys >= {ACC_PASS:.2f}; mean acc {np.mean(accs) if accs else float('nan'):.4f})")
    emit(f"{rung} passes in {len(langs_pass)}/6 languages: {', '.join(langs_pass) or 'none'}")
    emit()
    return langs_pass, el, stopped or el > RUNG_LIMIT_S


def main():
    t_start = time.time()
    for sub in ("ciphers", "keys", "traces"):
        (RUN / sub).mkdir(parents=True, exist_ok=True)
    emit("S50 (P4-D2): solver positive-control ladder L1->L4, verbose homophonic family (pre-registered in the docstring)")
    emit(f"date: {clock()}")
    emit(f"hashes: s50_solver_ladder.py={sha(SELF)}  s50_solver.py={sha(ROOT / 's50_solver.py')}")
    emit(f"stub_match: {stub_match()}  (stub {STUB.name})")
    emit(f"deps (imported unchanged): p4d1_core_order.py={sha(ROOT / 'p4d1_core_order.py')[:16]}  "
         f"scoreboard/metrics_new.py={sha(ROOT / 'scoreboard' / 'metrics_new.py')[:16]}  corpora.py={sha(ROOT / 'corpora.py')[:16]}  "
         f"a1_profile.py={sha(ROOT / 'a1_profile.py')[:16]}  s15_ranges.json={sha(ROOT / 's15_ranges.json')[:16]}")
    emit()
    vlines, vtoks = voynich()
    lens = line_lengths(vlines)
    nA = split_index(lens)
    emit(f"Voynich ZL3b paragraph text: {len(vtoks)} tokens, {len(vlines)} lines; cipher layout {sum(lens)} tokens on "
         f"{len(lens)} lines (cycled); half A = {nA} tokens, half B = {sum(lens) - nA}")
    vst = stats(vlines)
    emit(f"Voynich ZL3b statistics (reference, 34,857 tokens): {fmt_stats(vst)}")
    emit(f"Targets: types [{TARGET['types'][0]:.0f}, {TARGET['types'][1]:.0f}]  hapax [0.64, 0.72]  h2 [2.05, 2.15]  "
         f"A14 <= 0  Moran [{TARGET['moran'][0]:.4f}, {TARGET['moran'][1]:.4f}]   (* = outside)")
    emit()
    emit("Languages (plaintext letters / LM letters / LM held-out bits per letter on the plaintext):")
    for lang in LANGS:
        lm, q, plain, nlm = get_lm(lang)
        emit(f"  {lang:<8} plaintext {LANGS[lang][0]} {len(plain)} letters; LM {LANGS[lang][1] or 'same text, letters >= 120k'} "
             f"{nlm} letters; H = {S.lm_bits_per_letter(lm, plain):.3f} bits/letter")
    emit()

    vseg = mn.SlotSegmenter(vtoks)
    vcores = [c for c, _ in Counter(vseg.segment(w)[1] for w in vtoks).most_common()]
    plains = {lang: get_lm(lang)[2] for lang in LANGS}
    keys123 = {}
    for lang in LANGS:
        for k in KEYS:
            keys123[(lang, k)] = make_l123_key(plains[lang], vtoks, vcores, k)
    cal_lang = list(LANGS)[0] if DEV else "latin"

    def l123_payload(rung, lang, k):
        key = keys123[(lang, k)]
        toks, truth, useq = gen_l123(plains[lang], key, rung != "L1", k, lens)
        lines, i = [], 0
        for L in lens:
            lines.append(toks[i:i + L]); i += L
        payload = dict(rung=rung, lang=lang, key_seed=k, nA=nA, tokens=toks, truth=truth, unit_seq=useq,
                       lens=lens, key=key, true_pre=key["pre"], true_suf=key["suf"], true_reading="sep")
        (RUN / "keys" / f"{rung}_{lang}_k{k}_true.json").write_text(json.dumps(key), encoding="utf-8")
        return write_cipher(rung, lang, k, payload), lines

    first_fail = None
    passed = {}
    l4_note = ""
    for rung in ("L1", "L2", "L3", "L4"):
        if time.time() - t_start > TOTAL_LIMIT_S:
            emit(f"{rung}: NOT RUN (total budget exhausted)")
            break
        emit(f"=== {rung} === start {clock()}")
        payloads = {}
        if rung != "L4":
            for lang in LANGS:
                for k in KEYS:
                    p, lines = l123_payload(rung, lang, k)
                    payloads[(lang, k)] = p
                    if k == 1:
                        st = stats(lines)
                        emit(f"{rung} construction {lang} key 1: alloc min/max {min(keys123[(lang, k)]['alloc'])}/{max(keys123[(lang, k)]['alloc'])}; "
                             f"|P|={len(keys123[(lang, k)]['pre'])} |S|={len(keys123[(lang, k)]['suf'])}; ciphertext {fmt_stats(st)}")
        else:
            base, prm, l4_note = l4_calibrate(vtoks, vseg, plains, cal_lang, lens)
            for lang in LANGS:
                for k in KEYS:
                    key = make_l4_key(plains[lang], base, k)
                    ln, truth = gen_l4(plains[lang], key, base, prm, k, lens)
                    toks = [w for l_ in ln for w in l_]
                    st = stats(ln)
                    L4_HIT[(lang, k)] = all(hits(st).values())
                    emit(f"L4 cipher {lang} key {k}: {fmt_stats(st)}")
                    payload = dict(rung="L4", lang=lang, key_seed=k, nA=nA, tokens=toks, truth=truth, lens=lens,
                                   key=key, params=list(prm), true_pre=sorted(vseg.prefixes), true_suf=sorted(vseg.suffixes),
                                   true_reading="pair")
                    (RUN / "keys" / f"L4_{lang}_k{k}_true.json").write_text(json.dumps(key), encoding="utf-8")
                    payloads[(lang, k)] = write_cipher("L4", lang, k, payload)
        emit(f"{rung}: launching {len(payloads)} solver jobs on {WORKERS} processes at {clock()}")
        langs_pass, el, over = run_rung(rung, payloads, t_start)
        passed[rung] = langs_pass
        if rung == "L4":
            for lang in langs_pass:
                if sum(L4_HIT.get((lang, k), False) for k in KEYS) >= 2:
                    L4_MATCHED_PASS.append(lang)
            emit(f"L4 matched-L4 passes (cell passes and >= 2 ciphers hit all targets): {L4_MATCHED_PASS or 'none'}")
        if over:
            emit(f"{rung} exceeded the 2 h rung limit or the total budget: stopped and reported (step rule)")
            if not langs_pass:
                first_fail = first_fail or rung
            break
        if not langs_pass:
            first_fail = first_fail or rung
            emit(f"{rung} passes in no language -> first failing rung = {rung}; the ladder stops here (gate)")
            if not DEV:
                if rung != "L4":
                    l4_note = l4_construction_only(vtoks, vseg, plains, cal_lang, lens)
                break

    emit("=== Summary ===")
    for r, lp in passed.items():
        emit(f"{r}: passes in {len(lp)}/6 ({', '.join(lp) or 'none'})")
    if l4_note:
        emit(l4_note)
    emit(f"First failing rung: {first_fail or 'none (L4 passes in >= 1 language)'}")
    if first_fail is not None and first_fail != "L4":
        emit(f"Close-rule reading: the ladder stopped at {first_fail} (gate), so 'fails L4 in all six languages' is NOT "
             "TESTED and the Q3 close rule is not met as written. Recorded: the best solver built here fails "
             f"{first_fail} in all six languages at 38k tokens; the L4 construction result is the line above. EM not run.")
    elif first_fail is not None:
        emit("Close-rule reading: the best solver built here fails "
             f"{first_fail} in all six languages at 38k tokens (on the L4 ciphers described by the L4 calibration line) within "
             "the stated budget; EM cross-check not run. Under the Q3 close rule the computational Tier-1 route closes "
             "for the verbose-homophonic family (without the EM cross-check). This does not show that Voynich is not a "
             "cipher; it shows that a computer will not read one built this way.")
    elif "L4" in passed and L4_MATCHED_PASS:
        emit(f"Close-rule reading: matched L4 passes in {', '.join(L4_MATCHED_PASS)}, so the route does NOT close. Per the "
             "step, the Voynich run is NOT made here; it is the next step (Currier B first, pseudo-Voynich null, "
             "split-half key consistency).")
    elif "L4" in passed:
        emit("Close-rule reading: L4 passes in >= 1 language, but on ciphers that miss the manuscript targets (no matched "
             "L4 pass). So the solver reads the closest constructible L4; 'fails L4' is not met; 'no cipher meeting L4's "
             "targets can be constructed' holds within this family and grid -> recorded as evidence against the family "
             "(Q3). The route does not close by the solver half of the rule; the family is disfavoured by the "
             "construction half. Voynich not run (step rule).")
    else:
        emit("Close-rule reading: ladder did not reach a verdict (stopped by budget).")
    emit(f"elapsed: {(time.time() - t_start) / 60:.1f} min; end {clock()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        import traceback
        emit("FAILED: " + repr(e))
        emit(traceback.format_exc())
        raise
