"""s61 -- does a joint-word producer (whole words chosen jointly, copy-and-vary + counted context with line state) predict untouched pages?

PRE-REGISTERED QUESTION (frozen in s61_joint_word_producer.prereg.sha256 BEFORE any fitting on real pages; before the
freeze this script ran only on its synthetic fixture, `--fixture`, which reads no real data):
"A producer JW that emits WHOLE words (prefix + core + suffix chosen as one unit) -- copying a recent word of the same
page with probability p_copy (optionally with one core edit), inventing a novel frame+core combination with probability
p_new, and otherwise drawing a training word from a counted context model P(word | line-position class, previous
word's suffix, line prefix state) -- fitted ONLY on the 166 training pages, is asked to predict s57's six properties of
the 41 held-out pages it never sees.  Does it predict >= 5 of 6, with the same calls on all three transliterations?"

CONTEXT: s57 (results_s57.txt) local-memory copy-and-vary: 0/6 on ZL3b, RF1b, IT2a (null 1/6).  s58 (results_s58.txt)
two-layer TL (lag-1 counted affix wrapper chosen independently of the core): ZL3b 1/6, RF1b 2/6, IT2a 2/6; it recovered
CHARWIN but missed Moran, prefix gain and jsd_first, and inflated types by ~65 %, which drove p_copy to 0.02.  s54:
MI(frame; core) = +1.79 bits -- prefix, core and suffix are chosen jointly, with state longer than one word.

SPLIT: g1_edge_joint.split_names (random.Random(20261017)), 166 / 41 (IT2a 165 / 41).  Everything below is estimated
on the training pages only; held-out pages are touched only by the scoring code (s57's Measured, imported verbatim).

PRODUCER JW (fixed before hashing)
  Segmenter: scoreboard/metrics_new.SlotSegmenter fitted on the training tokens; word -> (pre, core, suf).
  Line-position class: P = first token of a paragraph-initial line, I = first token of any other line, F = last token
    of a line of length >= 2, M = otherwise.  PARAGRAPH PROXY (stated before the run): the meta.json transliterations
    keep no paragraph markers, so -- as a2_position.py does -- the paragraph-initial line is approximated by the first
    line of each page.
  Context of token t in a line: pos class, previous word's suffix within the line ("^" at line start, "" = empty
    suffix), line prefix state = the most recent NON-EMPTY prefix among the earlier tokens of the current line
    ("none" if there is none).  The state is updated from whatever word is emitted (copied, edited, novel or drawn).
  Context model (counted from the training pages; 0 free parameters): P(word | pos, prev_suf, line_prefix_state),
    Witten-Bell back-off by sampling (stay at a context with probability N / (N + T), N = tokens, T = distinct words
    seen there, else back off): (pos, prev_suf, state) -> (pos, prev_suf) -> (pos) -> unigram of all training words.
  Line length: drawn from the empirical training line-length distribution; page line counts as s57.
  Each token (every position, including line-initial, once the page has history):
    1. with probability p_copy: copy a recent whole word of the same page: with probability a (if the line above is
       long enough) the same-position word on the line above, else the word d back in the page stream (crossing line
       ends), d in 1..min(W, history), W = 20, P(d) ~ exp(-(d-1)/tau); then with probability q_edit apply ONE core
       edit (s57's core 1-glyph substitution / insertion / deletion, 1/3 each, deletion only if the core has >= 2
       glyphs, else substitution; glyph from the training core-glyph distribution), prefix and suffix kept;
    2. else with probability p_new: a novel word: frame (pre, suf) = the slots of a word drawn from the context model
       at the current context; core drawn from the training core lexicon by token frequency.  This is the ONLY
       source of new prefix/core/suffix combinations (apart from copy edits);
    3. else: a whole training word drawn from the context model.
  Free parameters: p_copy, tau, a, q_edit, p_new = 5 (<= 6).
COMPARATORS (scored identically, seeds as JW):
  (a) JW0 = JW with p_copy = 0; p_new refit to the type count alone (stage A0 below, types part of the loss);
  (b) JW-lag1 = JW without the line prefix state (back-off starts at (pos, prev_suf)); fitted by the SAME staged grid
      on its own (refit, not JW's parameters), so it is JW's best lag-1 counterpart;
  (c) s57 and s58 as filed (not rerun): s57 local-memory 0/6 x3 (null 1/6 x3); s58 TL ZL3b 1/6, RF1b 2/6, IT2a 2/6
      (TL0 2/6 x3).

FITTING (training pages only): s57's targets and loss (S57.fit_stats / S57.loss imported): R(d), d = 1..20; edit-type
  shares (identical / prefix-only / suffix-only / core 1-edit); type count; line lengths by construction.  Common random
  numbers: every candidate generated with seed 0 as 166 pages with the training pages' line counts.  Staged grid:
    A0: p_copy = 0, p_new in GRID_PN, chosen by the TYPES part of the loss only (this is also JW0's p_new);
    A : q_edit = 0.25, p_new = A0's, grid p_copy x tau x a (s57's grids);
    B : at A's best (p_copy, tau, a): q_edit in {0, .1, ..., 1} x p_new in GRID_PN;
    C : at B's best (q_edit, p_new): p_copy x tau x a within +-2 / +-1 / +-1 grid steps of A's best;
    D : at C's best: p_new in GRID_PN again.
  Per transliteration and per model (JW, JW-lag1).  Fitted parameters -> runs/s61/fit_<T>.json.

PREDICTIONS: exactly s57's P1-P6, pass rules, intervals (80 % page subsampling without replacement, 500 draws,
  np.random.default_rng(20261017 + offset), s57's offsets; real side = s57's seed, so the real intervals are s57's),
  s15 width [0.1447, 0.2156] for P4 and the s39 rule for P6, computed by s57's own scoring code (S57.Measured,
  S57.draws_for, S57.score_cells imported).  Generated texts seeds 1-3: 166 training-like pages + 41 held-out-like
  pages (line counts = random.Random(seed).sample of the training counts, as s57), each scored like the real text.
  Fallback stated before the run: if the run would exceed 45 minutes it is rerun with `--two-seeds` (seeds 1-2) and
  the result file says so.
VERDICT RULE: "joint word producer predicts untouched pages" iff >= 5 of 6 hold on ZL3b AND on RF1b and IT2a the SAME
  set of predictions holds as on ZL3b; if ZL3b >= 5 but RF1b / IT2a differ: "holds on ZL3b only, not stable across
  transliterations"; else "joint word producer does NOT predict untouched pages".  Also reported, per transliteration:
  predictions JW holds that JW0 does not, and that JW-lag1 does not (and the reverse).
MEMORISATION CHECK: on each generated text's 41 held-out-like pages, the share of lines that occur verbatim among the
  REAL training lines (all lines, and lines of >= 3 words), and the share of within-line word bigrams that occur among
  the real training bigrams; compared with the real held-out pages' shares against the real training pages.
IN-SAMPLE SANITY: fitted R(d), edit shares and type count (seed 0) against the training targets for JW, JW-lag1, JW0.
  If a fit's type count is off by more than 15 % it is flagged '!!! TYPE COUNT OFF BY > 15 %' (the s58 failure mode).
CAVEATS stated before the run: P6 is weak (s57: the s39 rule gives 'affix layer' on ZL3b, 'core layer' on RF1b,
  'both / neither' on IT2a for the real text of this split); P4 and P3 are close to built-in (line-initial words and the
  prefix of each word come from a context model counted on the training pages); a context model over whole training
  words can memorise -- the memorisation check measures how much; the paragraph proxy (first line of page) is coarse.

Run:    python -I s61_joint_word_producer.py [--fixture] [--two-seeds]
Writes: results_s61.txt, runs/s61/ (fit_<T>.json, sidecars JW_<T>_s<seed>.meta.json, JW0_..., JWlag1_..., cells.json;
        fixture.txt and fixture/ for --fixture).  Nothing else.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import time
from collections import Counter, OrderedDict, defaultdict
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
import s57_local_memory_model as S57  # noqa: E402  (scoring, fit statistics, loss: verbatim)
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s61_joint_word_producer.py"
STUB = ROOT / "s61_joint_word_producer.prereg.sha256"
OUT = ROOT / "results_s61.txt"
RUNS = ROOT / "runs" / "s61"
W = S57.W
STEP_LIMIT = 30 * 60
RUN_LIMIT = 45 * 60
TRANSLITS = S57.TRANSLITS
GRID_P, GRID_TAU, GRID_A = S57.GRID_P, S57.GRID_TAU, S57.GRID_A
GRID_QE = [i / 10 for i in range(11)]
GRID_PN = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.13, 0.16, 0.20, 0.25, 0.30, 0.40]
EDIT_KINDS = S57.EDIT_KINDS
LABELS = ("JW", "JW0", "JW-lag1")
SEEDS = (1, 2) if "--two-seeds" in sys.argv else (1, 2, 3)
TYPE_FLAG = 0.15
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


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


def _cum(counter):
    items = sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))
    ws = [k for k, _ in items]
    cum, t = [], 0
    for _, c in items:
        t += c; cum.append(t)
    return ws, cum


def pos_class(li, i, L):
    if i == 0:
        return "P" if li == 0 else "I"
    return "F" if i == L - 1 else "M"


# ======================================================================= context model (counted)
class ContextModel:
    """P(word | pos, prev_suf, line_prefix_state), Witten-Bell back-off -> (pos, prev_suf) -> (pos) -> unigram.
    use_state=False (JW-lag1): back-off starts at (pos, prev_suf)."""

    def __init__(self, train_pages, seg, use_state=True):
        self.use_state = use_state
        c2, c1, c0, call = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), Counter()
        for lines in train_pages:
            for li, l in enumerate(lines):
                L = len(l)
                psuf, lps = "^", "none"
                for i, w in enumerate(l):
                    pos = pos_class(li, i, L)
                    call[w] += 1
                    c0[pos][w] += 1
                    c1[(pos, psuf)][w] += 1
                    c2[(pos, psuf, lps)][w] += 1
                    p, _, s = seg.segment(w)
                    psuf = s
                    if p:
                        lps = p
        tabs = (c2, c1, c0) if use_state else (c1, c0)
        self.levels = [{k: (*_cum(v), sum(v.values()) / (sum(v.values()) + len(v))) for k, v in tab.items()} for tab in tabs]
        self.all = _cum(call)
        self.sizes = dict(ctx_state=len(c2) if use_state else 0, ctx_suf=len(c1), ctx_pos=len(c0), words=len(call))

    def draw(self, rng, pos, psuf, lps):
        keys = [(pos, psuf, lps), (pos, psuf), pos] if self.use_state else [(pos, psuf), pos]
        for lev, k in zip(self.levels, keys):
            e = lev.get(k)
            if e is None:
                continue
            ws, cum, lam = e
            if rng.random() < lam:
                return rng.choices(ws, cum_weights=cum)[0]
        return rng.choices(self.all[0], cum_weights=self.all[1])[0]


# ======================================================================= joint-word producer
class JWProducer:
    def __init__(self, train_pages, seg, use_state=True):
        self.seg = seg
        self.ctx = ContextModel(train_pages, seg, use_state)
        corec, gl = Counter(), Counter()
        for lines in train_pages:
            for l in lines:
                for w in l:
                    c = seg.segment(w)[1]
                    corec[c] += 1
                    for ch in c:
                        gl[ch] += 1
        self.core_w, self.core_c = _cum(corec)
        self.gl_w, self.gl_c = _cum(gl)
        self.lens = [len(l) for lines in train_pages for l in lines]
        self.set_params(dict(p_copy=0.0, tau=1.0, a=0.0, q_edit=0.25, p_new=0.0))

    def set_params(self, prm):
        self.prm = dict(prm)
        self.kcum, t = [], 0.0
        for d in range(1, W + 1):
            t += math.exp(-(d - 1) / prm["tau"]); self.kcum.append(t)

    def _swap(self, rng, cur, ws, cum):
        for _ in range(30):
            x = rng.choices(ws, cum_weights=cum)[0]
            if x != cur:
                return x
        return cur

    def core_edit(self, rng, core):
        """s57 Producer.edit, core branch (verbatim logic; an empty core can only be inserted into)."""
        op = rng.randrange(3)
        if op == 2 and len(core) < 2:
            op = 0
        if op == 0 and len(core) == 0:
            op = 1
        i = rng.randrange(len(core) + (1 if op == 1 else 0))
        if op == 0:
            g = self._swap(rng, core[i], self.gl_w, self.gl_c)
            return core[:i] + g + core[i + 1:]
        if op == 1:
            g = rng.choices(self.gl_w, cum_weights=self.gl_c)[0]
            return core[:i] + g + core[i:]
        return core[:i] + core[i + 1:]

    def page(self, rng, n_lines):
        p = self.prm
        seg = self.seg.segment
        hist, lines = [], []
        for li in range(n_lines):
            L = rng.choice(self.lens)
            line, psuf, lps = [], "^", "none"
            for i in range(L):
                pos = pos_class(li, i, L)
                if hist and p["p_copy"] > 0 and rng.random() < p["p_copy"]:
                    if lines and len(lines[-1]) > i and rng.random() < p["a"]:
                        src = lines[-1][i]
                    else:
                        h = min(W, len(hist))
                        d = rng.choices(range(1, h + 1), cum_weights=self.kcum[:h])[0]
                        src = hist[-d]
                    if rng.random() < p["q_edit"]:
                        pr, co, su = seg(src)
                        w = pr + self.core_edit(rng, co) + su
                    else:
                        w = src
                elif p["p_new"] > 0 and rng.random() < p["p_new"]:
                    pr, _, su = seg(self.ctx.draw(rng, pos, psuf, lps))
                    w = pr + rng.choices(self.core_w, cum_weights=self.core_c)[0] + su
                else:
                    w = self.ctx.draw(rng, pos, psuf, lps)
                line.append(w); hist.append(w)
                pr, _, su = seg(w)
                psuf = su
                if pr:
                    lps = pr
            lines.append(line)
        return lines

    def text(self, seed, page_line_counts):
        rng = random.Random(seed)
        return [self.page(rng, n) for n in page_line_counts]


KEYS = ("p_copy", "tau", "a", "q_edit", "p_new")


def fit(train_pages, seg, emit_fn, budget_t0, use_state=True):
    enc = S57.Encoder(seg)
    real = S57.fit_stats(train_pages, enc)
    prod = JWProducer(train_pages, seg, use_state)
    counts = [len(l) for l in train_pages]
    cache = {}

    def evaluate(prm):
        key = tuple(round(prm[k], 6) for k in KEYS)
        if key in cache:
            return cache[key]
        prod.set_params(prm)
        g = S57.fit_stats(prod.text(0, counts), enc)
        L, parts = S57.loss(g, real)
        cache[key] = (L, parts, g)
        if time.time() - budget_t0 > STEP_LIMIT:
            raise TimeoutError("fitting step exceeded 30 minutes")
        return cache[key]

    # A0: p_copy = 0, p_new by the types part of the loss (also JW0's p_new)
    a0 = None
    for pn in GRID_PN:
        prm = dict(p_copy=0.0, tau=1.0, a=0.0, q_edit=0.25, p_new=pn)
        lv = evaluate(prm)[1][2]
        if a0 is None or lv < a0[0]:
            a0 = (lv, prm)
    pn0 = a0[1]["p_new"]
    emit_fn(f"    stage A0 ({len(cache)} evals): p_copy 0, best types loss {a0[0]:.2f} at p_new {pn0}")
    best = None
    for pc in GRID_P:
        for tau in GRID_TAU:
            for a in GRID_A:
                prm = dict(p_copy=pc, tau=tau, a=a, q_edit=0.25, p_new=pn0)
                L = evaluate(prm)[0]
                if best is None or L < best[0]:
                    best = (L, prm)
    emit_fn(f"    stage A ({len(cache)} evals): best loss {best[0]:.2f} at p_copy {best[1]['p_copy']}, tau {best[1]['tau']}, a {best[1]['a']}")
    bA = best[1]
    for qe in GRID_QE:
        for pn in GRID_PN:
            prm = dict(bA, q_edit=qe, p_new=pn)
            L = evaluate(prm)[0]
            if L < best[0]:
                best = (L, prm)
    emit_fn(f"    stage B ({len(cache)} evals): best loss {best[0]:.2f} at q_edit {best[1]['q_edit']}, p_new {best[1]['p_new']}")
    qe, pn = best[1]["q_edit"], best[1]["p_new"]
    ip, it, ia = GRID_P.index(bA["p_copy"]), GRID_TAU.index(bA["tau"]), GRID_A.index(bA["a"])
    for pc in GRID_P[max(0, ip - 2): ip + 3]:
        for tau in GRID_TAU[max(0, it - 1): it + 2]:
            for a in GRID_A[max(0, ia - 1): ia + 2]:
                prm = dict(p_copy=pc, tau=tau, a=a, q_edit=qe, p_new=pn)
                L = evaluate(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    emit_fn(f"    stage C ({len(cache)} evals): best loss {best[0]:.2f} at p_copy {best[1]['p_copy']}, tau {best[1]['tau']}, a {best[1]['a']}")
    bC = best[1]
    for pn in GRID_PN:
        prm = dict(bC, p_new=pn)
        L = evaluate(prm)[0]
        if L < best[0]:
            best = (L, prm)
    emit_fn(f"    stage D ({len(cache)} evals): best loss {best[0]:.2f} at p_new {best[1]['p_new']}")
    L, parts, g = evaluate(best[1])
    L0, parts0, g0 = evaluate(a0[1])
    return dict(params=best[1], loss=L, parts=parts, gen=g, real=real, n_evals=len(cache), ctx=prod.ctx.sizes,
                p0=a0[1], loss0=L0, parts0=parts0, gen0=g0)


# ======================================================================= memorisation
def memo_sets(train):
    lines = set(); bigr = set()
    for _, ls in train:
        for l in ls:
            lines.add(tuple(l))
            bigr.update(zip(l, l[1:]))
    return lines, bigr


def memo_shares(sets, test):
    lines_set, bigr_set = sets
    ls_all = [tuple(l) for _, ls in test for l in ls]
    l3 = [l for l in ls_all if len(l) >= 3]
    bg = [b for l in ls_all for b in zip(l, l[1:])]
    f = lambda xs, S: (sum(1 for x in xs if x in S) / len(xs)) if xs else float("nan")
    return dict(lines=f(ls_all, lines_set), lines3=f(l3, lines_set), bigrams=f(bg, bigr_set),
                n_lines=len(ls_all), n_lines3=len(l3), n_bigrams=len(bg))


# ======================================================================= one transliteration
def sanity(emit_fn, lab, r, g, prm_txt):
    emit_fn(f"  [in-sample {lab}] {prm_txt}")
    emit_fn(f"  [in-sample {lab}] fitted R(d) s0 : " + " ".join(f"{x:.3f}" for x in g["R"]))
    emit_fn(f"  [in-sample {lab}] edit shares s0: " + ", ".join(f"{k} {v:.4f}" for k, v in zip(EDIT_KINDS, g["shares"]))
            + f"  (counts {g['counts'].astype(int).tolist()})")
    dv = (g["types"] - r["types"]) / r["types"]
    flag = "   !!! TYPE COUNT OFF BY > 15 % (s58 failure mode) !!!" if abs(dv) > TYPE_FLAG else ""
    emit_fn(f"  [in-sample {lab}] types {g['types']} at {g['tokens']} tokens vs real {r['types']} at {r['tokens']} ({dv * 100:+.1f} %){flag}")
    return dict(types=g["types"], tokens=g["tokens"], dv=dv, flag=bool(flag), R=g["R"].tolist(), shares=g["shares"].tolist())


def run_translit(T, by, emit_fn, t_start, out_dir: Path, real_name="real"):
    train_names, held_names = G1.split_names(by)
    train = [(p, by[p]) for p in train_names]
    test = [(p, by[p]) for p in held_names]
    tr_pages = [ls for _, ls in train]
    tr_tok = [w for _, ls in train for l in ls for w in l]
    seg = SlotSegmenter(tr_tok)
    emit_fn(f"=== {T}: {len(by)} pages; training {len(train)} pages ({len(tr_tok)} tokens), held-out {len(test)} pages "
            f"({sum(len(l) for _, ls in test for l in ls)} tokens); training SlotSegmenter {len(seg.prefixes)} prefix / {len(seg.suffixes)} suffix candidates ===")
    fits = {}
    for lab, st in (("JW", True), ("JW-lag1", False)):
        t0 = time.time()
        emit_fn(f"  fitting {lab} (line prefix state {'on' if st else 'off'})")
        F = fit(tr_pages, seg, emit_fn, t0, use_state=st)
        fits[lab] = F
        prm = F["params"]
        emit_fn(f"  {lab} context tables (counted): {F['ctx']}")
        emit_fn(f"  {lab} fit ({F['n_evals']} grid evaluations, {time.time() - t0:.0f}s): " + ", ".join(f"{k} {prm[k]}" for k in KEYS)
                + f"; loss {F['loss']:.2f} (R {F['parts'][0]:.2f}, shares {F['parts'][1]:.2f}, types {F['parts'][2]:.2f})")
    F = fits["JW"]
    r = F["real"]
    params = {"JW": F["params"], "JW0": dict(F["p0"]), "JW-lag1": fits["JW-lag1"]["params"]}
    emit_fn(f"  JW0 = JW with p_copy 0, p_new {params['JW0']['p_new']} (stage A0, type count); loss {F['loss0']:.2f} "
            f"(R {F['parts0'][0]:.2f}, shares {F['parts0'][1]:.2f}, types {F['parts0'][2]:.2f})")
    emit_fn("  [in-sample] target R(d) real    : " + " ".join(f"{x:.3f}" for x in r["R"]))
    emit_fn("  [in-sample] target edit shares  : " + ", ".join(f"{k} {v:.4f}" for k, v in zip(EDIT_KINDS, r["shares"])) + f"  (counts {r['counts'].astype(int).tolist()})")
    san = {}
    san["JW"] = sanity(emit_fn, "JW", r, F["gen"], ", ".join(f"{k} {params['JW'][k]}" for k in KEYS))
    san["JW-lag1"] = sanity(emit_fn, "JW-lag1", r, fits["JW-lag1"]["gen"], ", ".join(f"{k} {params['JW-lag1'][k]}" for k in KEYS))
    san["JW0"] = sanity(emit_fn, "JW0", r, F["gen0"], f"p_copy 0, p_new {params['JW0']['p_new']}")
    lr, lg = np.array(r["lens"]), np.array(F["gen"]["lens"])
    emit_fn(f"  [in-sample] line length real mean {lr.mean():.3f} sd {lr.std():.3f}; JW seed 0 mean {lg.mean():.3f} sd {lg.std():.3f} (empirical sampling)")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"fit_{T}.json").write_text(json.dumps(dict(
        translit=T, params=params, W=W, free_parameters=5,
        loss={k: fits[k]["loss"] for k in fits}, loss_parts={k: fits[k]["parts"] for k in fits},
        n_evals={k: fits[k]["n_evals"] for k in fits}, context_tables={k: fits[k]["ctx"] for k in fits},
        target=dict(R=r["R"].tolist(), shares=r["shares"].tolist(), types=r["types"], tokens=r["tokens"]),
        fitted=san, paragraph_proxy="first line of page",
        method="staged grid (A0 p_new by types at p_copy 0; A p_copy x tau x a at q_edit .25; B q_edit x p_new; C local p/tau/a; D p_new), seed 0, common random numbers",
    ), indent=1), encoding="utf-8", newline="\n")
    # ---- generate
    prods = {"JW": JWProducer(tr_pages, seg, True), "JW-lag1": JWProducer(tr_pages, seg, False)}
    prods["JW0"] = prods["JW"]
    tr_counts = [len(ls) for _, ls in train]
    gens = {}
    for lab in LABELS:
        prod = prods[lab]
        prod.set_params(params[lab])
        gens[lab] = []
        for s in SEEDS:
            te_counts = random.Random(s).sample(tr_counts, len(test))
            pages = prod.text(s, tr_counts + te_counts)
            gtr = [(f"g{i}", pages[i]) for i in range(len(train))]
            gte = [(f"h{i}", pages[len(train) + i]) for i in range(len(test))]
            gens[lab].append((gtr, gte))
            side = dict(source=f"s61 {lab} joint-word producer fitted on {T} training pages, seed {s}", params=params[lab],
                        pages=[dict(id=p, section="S61", hand="S61", lang="?", quire="?", lines=ls,
                                    role="train" if i < len(train) else "heldout") for i, (p, ls) in enumerate(gtr + gte)])
            (out_dir / f"{lab.replace('-', '')}_{T}_s{s}.meta.json").write_text(json.dumps(side), encoding="utf-8", newline="\n")
    # ---- memorisation check
    ms_sets = memo_sets(train)
    memo = {"real held-out": memo_shares(ms_sets, test)}
    for lab in LABELS:
        sh = [memo_shares(ms_sets, gte) for _, gte in gens[lab]]
        memo[lab] = {k: float(np.mean([x[k] for x in sh])) for k in sh[0]}
    emit_fn("  memorisation (vs REAL training pages): share of held-out(-like) lines verbatim in training lines (all / >= 3 words), "
            "share of within-line word bigrams seen in training")
    for k, v in memo.items():
        emit_fn(f"    {k:14}: lines {v['lines']:.4f} (n {v['n_lines']:.0f}), lines>=3 {v['lines3']:.4f} (n {v['n_lines3']:.0f}), "
                f"bigrams {v['bigrams']:.4f} (n {v['n_bigrams']:.0f})")
    # ---- measure
    t1 = time.time()
    real_m = S57.Measured(f"{T} {real_name}", train, test)
    ms = {k: [S57.Measured(f"{T} {k} s{SEEDS[i]}", a, b) for i, (a, b) in enumerate(gens[k])] for k in LABELS}
    emit_fn(f"  measured {1 + sum(len(v) for v in ms.values())} texts in {time.time() - t1:.0f}s")
    if time.time() - t_start > RUN_LIMIT:
        raise TimeoutError("run exceeded 45 minutes")
    off = {"ZL3b": 0, "RF1b": 10, "IT2a": 20}.get(T, 30)
    t2 = time.time()
    real_dr = S57.draws_for([real_m], S57.SEED + off)
    drs = {lab: S57.draws_for(ms[lab], S57.SEED + off + 1 + j) for j, lab in enumerate(LABELS)}
    emit_fn(f"  subsample draws {time.time() - t2:.0f}s")
    real_pt = real_m.point()
    pts = {k: S57.mean_point(ms[k]) for k in LABELS}
    real_ci = {k: S57.pct(real_dr[k]) for k in S57.DRAW_KEYS}
    emit_fn(f"  real held-out: Moran {real_pt['P1']:.4f} [{real_ci['P1'][0]:.4f},{real_ci['P1'][1]:.4f}]; core->core {real_pt['P2']:+.4f} "
            f"[{real_ci['P2'][0]:+.4f},{real_ci['P2'][1]:+.4f}]; prefix gain {real_pt['P3']:+.4f} [{real_ci['P3'][0]:+.4f},{real_ci['P3'][1]:+.4f}]; "
            f"jsd_first_fg {real_pt['P4']:.4f} (excess {real_pt['P4_exc']:+.4f}); CHARWIN {real_pt['P5']:+.4f}")
    emit_fn("  real F1 by stream: " + ", ".join(f"{k[3:]} {real_pt[k]:+.4f} [{real_ci[k][0]:+.4f},{real_ci[k][1]:+.4f}]" for k in ("F1_prefix", "F1_core", "F1_suffix"))
            + f" -> s39 rule on the real text (this split): {S57.f1_layer_call(real_ci)}")
    for lab in LABELS:
        for i, p in enumerate(pts[lab][1]):
            emit_fn(f"    {lab} s{SEEDS[i]}: Moran {p['P1']:.4f} core->core {p['P2']:+.4f} prefix gain {p['P3']:+.4f} jsd_first_fg {p['P4']:.4f} "
                    f"CHARWIN {p['P5']:+.4f} F1 prefix/core/suffix {p['F1_prefix']:+.4f}/{p['F1_core']:+.4f}/{p['F1_suffix']:+.4f}")
    res = {}
    for lab in LABELS:
        cells = S57.score_cells(real_pt, real_dr, pts[lab][0], drs[lab])
        n = sum(1 for v in cells.values() if v[0])
        emit_fn(f"  -- {lab}: {n}/6 hold --")
        for k, (ok, txt) in cells.items():
            emit_fn(f"    {k} {'HOLDS' if ok else 'fails'}: {txt}")
        res[lab] = dict(n=n, holds={k: bool(v[0]) for k, v in cells.items()}, text={k: v[1] for k, v in cells.items()},
                        point=pts[lab][0])
    res["fit"] = dict(params=params, loss={k: fits[k]["loss"] for k in fits}, parts={k: fits[k]["parts"] for k in fits})
    res["sanity"] = san
    res["memo"] = memo
    res["real_point"] = real_pt; res["real_ci"] = real_ci
    return res


# ======================================================================= summary / verdict
def summarize(allres, emit_fn):
    Ts = list(allres)
    T0 = Ts[0]
    emit_fn("=== VERDICT (pre-registered rule) ===")
    for lab in LABELS:
        row = []
        for T in Ts:
            h = allres[T][lab]["holds"]
            row.append(f"{T} {allres[T][lab]['n']}/6 [" + " ".join(f"{k}{'+' if v else '-'}" for k, v in h.items()) + "]")
        emit_fn(f"  {lab:7}: " + "; ".join(row))
    emit_fn("  s57 as filed (not rerun): local-memory ZL3b 0/6, RF1b 0/6, IT2a 0/6; null p_copy=0 1/6 each")
    emit_fn("  s58 as filed (not rerun): TL ZL3b 1/6, RF1b 2/6, IT2a 2/6; TL0 2/6 each")
    z = allres[T0]["JW"]
    sets = {T: tuple(sorted(k for k, v in allres[T]["JW"]["holds"].items() if v)) for T in Ts}
    if z["n"] >= 5 and all(sets[T] == sets[T0] for T in Ts):
        verdict = "joint word producer predicts untouched pages"
    elif z["n"] >= 5:
        verdict = "holds on ZL3b only, not stable across transliterations"
    else:
        verdict = "joint word producer does NOT predict untouched pages"
    emit_fn(f"VERDICT: {verdict} ({T0} {z['n']}/6; holding sets {sets})")
    for T in Ts:
        a = allres[T]["JW"]["holds"]
        for cmp_ in ("JW0", "JW-lag1"):
            b = allres[T][cmp_]["holds"]
            emit_fn(f"  {T}: held by JW not {cmp_}: {[k for k in a if a[k] and not b[k]] or 'none'}; "
                    f"held by {cmp_} not JW: {[k for k in a if b[k] and not a[k]] or 'none'}")
    emit_fn("")
    emit_fn("=== TABLE: generated point (mean over seeds) vs real held-out; + = holds ===")
    emit_fn("  translit model     P1 Moran         P2 core->core      P3 prefix gain     P4 jsd_first      P5 CHARWIN        P6 F1 core (call)")
    for T in Ts:
        rp = allres[T]["real_point"]
        emit_fn(f"  {T:8} real     {rp['P1']:+.4f}          {rp['P2']:+.4f}            {rp['P3']:+.4f}            {rp['P4']:.4f}            "
                f"{rp['P5']:+.4f}           {rp['F1_core']:+.4f}")
        for lab in LABELS:
            g, h = allres[T][lab]["point"], allres[T][lab]["holds"]
            mk = lambda k: "+" if h[k] else "-"
            call = allres[T][lab]["text"]["P6"].split("-> ")[-1].split(";")[0]
            emit_fn(f"  {T:8} {lab:8} {g['P1']:+.4f} {mk('P1')}        {g['P2']:+.4f} {mk('P2')}          {g['P3']:+.4f} {mk('P3')}          "
                    f"{g['P4']:.4f} {mk('P4')}          {g['P5']:+.4f} {mk('P5')}         {g['F1_core']:+.4f} {mk('P6')} ({call})")
    emit_fn("")
    emit_fn("=== IN-SAMPLE TYPE COUNT CHECK (flag if off by > 15 %) ===")
    for T in Ts:
        s = allres[T]["sanity"]
        emit_fn(f"  {T}: " + "; ".join(f"{lab} {s[lab]['dv'] * 100:+.1f} %{' !!! FLAGGED' if s[lab]['flag'] else ''}" for lab in LABELS))
    emit_fn("caveats: P6 weak (the s39 rule gives a different call on each transliteration's real text for this split); "
            "P3 / P4 close to built-in via the counted context model; paragraph-initial = first line of page (proxy); "
            "the context model draws whole training words -- see the memorisation check")
    return verdict, sets


# ======================================================================= fixture (synthetic, no real data)
def fixture():
    out_lines = []

    def say(s=""):
        print(s, flush=True)
        out_lines.append(s)

    t0 = time.time()
    say(f"s61 fixture; stub_match: {stub_match()}; date {S57.clock()}")
    rng = random.Random(5)
    alph = "abcdefghij"
    pres = ["", "", "q", "o", "ch", "sh", "d"]
    sufs = ["", "", "y", "dy", "in", "ol", "r"]
    cores = sorted({"".join(rng.choice(alph) for _ in range(rng.randint(1, 4))) for _ in range(600)})
    cw = [1 + 200 / (1 + i) for i in range(len(cores))]
    # pseudo training text with joint frame/core choice and a line-prefix state: prefix of t follows suffix of t-1
    # (70 %), cores tied to the prefix (core index band by prefix), line-final suffix bias
    base = []
    for _ in range(60):
        lines = []
        for _ in range(14):
            L = rng.randint(5, 10)
            line, ps = [], None
            for i in range(L):
                p = pres[(sufs.index(ps) + 1) % len(pres)] if ps is not None and rng.random() < 0.7 else rng.choice(pres)
                s = "r" if i == L - 1 and rng.random() < 0.5 else rng.choice(sufs)
                band = (pres.index(p) * 80) % len(cores)
                c = cores[(band + rng.choices(range(len(cores)), cw)[0]) % len(cores)] if rng.random() < 0.6 else rng.choices(cores, cw)[0]
                line.append(p + c + s); ps = s
            lines.append(line)
        base.append(lines)
    seg0 = SlotSegmenter([w for ls in base for l in ls for w in l])
    truth = dict(p_copy=0.2, tau=4.0, a=0.15, q_edit=0.3, p_new=0.1)
    pr = JWProducer(base, seg0, True)
    pr.set_params(truth)
    pages = pr.text(99, [14] * 120)
    by = OrderedDict((f"f{i}", ls) for i, ls in enumerate(pages))
    say(f"fixture: synthetic text {len(by)} pages, {sum(len(l) for ls in pages for l in ls)} tokens, truth {truth}")
    nd = S57.N_DRAW
    S57.N_DRAW = 40
    try:
        res = run_translit("FIX", by, say, t0, RUNS / "fixture", real_name="synthetic")
    finally:
        S57.N_DRAW = nd
    fp = res["fit"]["params"]["JW"]
    ok1 = abs(fp["p_copy"] - truth["p_copy"]) <= 0.08
    say(f"  fixture check: fitted JW p_copy {fp['p_copy']} vs planted {truth['p_copy']} -> {'OK' if ok1 else 'FAIL'} (tolerance 0.08); "
        f"fitted {fp} (informative)")
    say(f"  fixture JW {res['JW']['n']}/6, JW0 {res['JW0']['n']}/6, JW-lag1 {res['JW-lag1']['n']}/6 (informative only)")
    say("  fixture: exercising summarize() with the fixture result under all three translit names")
    summarize({"ZL3b": res, "RF1b": res, "IT2a": res}, say)
    (RUNS / "fixture").mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture" / "cells.json").write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                                 encoding="utf-8", newline="\n")
    ok = ok1
    say(f"FIXTURE {'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f}s)")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8", newline="\n")
    return ok


# ======================================================================= main
def main():
    t0 = time.time()
    emit("s61 -- joint-word producer JW (whole words: copy-and-vary + novel frame/core + counted context with line prefix "
         "state) fitted on the training pages, predicting s57's 6 properties of the 41 held-out pages")
    emit(f"date: {S57.clock()}")
    emit(f"sha256 s61_joint_word_producer.py: {sha256(SELF)}")
    emit(f"sha256 s61_joint_word_producer.prereg.sha256: {sha256(STUB) if STUB.exists() else 'missing'}")
    emit(f"stub_match: {stub_match()}")
    for m in S57.local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"numpy {np.__version__}; python -I; CPU; W={W}; grid p_copy {GRID_P}, tau {GRID_TAU}, a {GRID_A}, q_edit {GRID_QE}, "
         f"p_new {GRID_PN}; subsample {int(S57.SUB_FRAC * 100)} % of held-out pages without replacement x {S57.N_DRAW}; "
         f"core->core null {S57.N_SHUF_POINT} (point) / {S57.N_SHUF_DRAW} (per draw); seeds {list(SEEDS)}"
         f"{' (TWO-SEED FALLBACK: 45-minute budget)' if len(SEEDS) == 2 else ''}; scoring = s57 code imported")
    emit("")
    allres = {}
    for T, f in TRANSLITS.items():
        path = ROOT / "data" / "translit" / f"{f}.meta.json"
        emit(f"translit {T}: {path.name} sha256={sha256(path)[:16]}")
        by = S57.load_meta(path)
        allres[T] = run_translit(T, by, emit, t0, RUNS)
        emit(f"  elapsed so far {time.time() - t0:.0f}s")
        emit("")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    summarize(allres, emit)
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "cells.json").write_text(json.dumps(allres, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                     encoding="utf-8", newline="\n")
    emit("")
    emit(f"elapsed: {time.time() - t0:.1f} s")
    emit(f"date end: {S57.clock()}")
    emit(f"paths: {OUT}, {RUNS}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--fixture" in sys.argv:
        sys.exit(0 if fixture() else 1)
    main()
