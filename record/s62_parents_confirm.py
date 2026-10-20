"""s62 -- confirmation of s59's within-page-shuffle (N1) reading on pages s59 never scored.

PRE-REGISTERED (frozen in s62_parents_confirm.prereg.sha256 BEFORE any real-data run; before the freeze this script
ran only on its synthetic fixture, `--fixture`, which reads no real data).

Background: results_s59.txt scored only the 41 held-out pages.  Its decision null N3 called Latin and Dante
"mutation" too (verdict "inconclusive: controls failed").  Beside it, the within-page shuffle null N1 gave real Voynich
W u V ratios 1.02 / 1.01 / 0.99 (no local edit-1 parent excess) while the known mutator C+ gave 1.12-1.15.
s62 tests that N1 reading as a hypothesis on fresh pages.

UNITS (reversed split relative to s59)
  Split: g1_edge_joint.split_names(by) (random.Random(20261017), 80 / 20 of pages).  SCORED = the 166 (IT2a 165)
    "training" pages; FIT = the 41 "held-out" pages.  SlotSegmenter and the top-20 core list are fitted on the FIT
    pages only; every scored token is segmented with that segmenter.  Scored pages in manuscript order.
  Event, parent (W: preceding 15 tokens of the page stream, crossing line ends; V: line above, index j-1..j+1), glyph
    Levenshtein distance 1, end-glyph share, nulls N1 / N2 / N3 / N3t (500 draws each), ratio and interval (80 % page
    subsampling without replacement, 500 draws, [2.5, 97.5] percentiles): EXACTLY s59's functions, imported from the
    frozen s59_rare_core_parents.py (Page, prepare, finish, analyse, summarize, ratios, build_cminus, load_meta;
    s59 is not modified).  "Rare" / N3 pools = FIT-page core types not in the top-20.

DECISION STATISTIC
  W u V ratio real / N1 (within-page shuffle), with its 95 % page-subsample interval.
  "above 1" = interval lower bound > 1; "includes 1 or below" = lower bound <= 1.

CONTROLS
  C+ (known local mutator): s57's local-memory producer (class Producer copied verbatim from s57_local_memory_model.py,
     not imported), built exactly as in s57 on the real s59-training pages (= s62 scored pages) with their
     SlotSegmenter, parameters from runs/s57/fit_<T>.json.  Seeds 1 and 2.  Per seed one text:
     prod.text(seed, fit_line_counts + scored_line_counts), i.e. 41 FIT-like pages (line counts of the real FIT pages,
     manuscript order) FIRST, then 166 scored-like pages (line counts of the real scored pages, manuscript order).
     (Order reversed relative to s57, so the output is fresh and not s57's sidecar text; identical pages vs the s57
     sidecar of the same seed are counted and printed.)  Each seed is scored like a real text (segmenter / top-20 on its
     41 FIT-like pages; score its scored-like pages); the two seeds' scored rows are pooled for the control interval.
  C- (outside list): s59's build_cminus applied to the real scored pages of each transliteration (rare list = rare
     FIT core types, random.Random(20261017 + 7) permutation, refills appended and counted).
  References (not in the gate or verdict): Latin prose (data/controls_realline/cremma_prose15) and Dante
     (data/controls_realline/italian_dante), same reversed split.

GATE: C+ W u V / N1 interval lower bound > 1 on ZL3b, RF1b and IT2a, AND C- W u V / N1 interval lower bound <= 1 on
  all three.  If the gate fails: VERDICT "inconclusive: controls failed".

VERDICT (fixed)
  "no local edit-chain": gate passes and the real W u V / N1 interval includes 1 or lies below it on ZL3b, RF1b, IT2a.
  "local edit-chain":    gate passes and the real interval lies above 1 on all three.
  Otherwise "mixed".

DESCRIPTIVE (not in the verdict): V / N1, W u V / N2, all N3 / N3t ratios, parent-rate levels, end-glyph share,
  per-section W u V / N1 on the real scored pages: herbal A (section H, lang A), herbal B (H, B), bio (B), stars (S),
  pharma (P), others (everything else).

Run:    python -I s62_parents_confirm.py [--fixture]
Writes: results_s62.txt; runs/s62/ (cells.json, cminus_<T>_cores.json, cplus_<T>_s<seed>.meta.json, run.log via the
        caller, fixture.txt).
"""
from __future__ import annotations

import hashlib
import json
import math
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

import s59_rare_core_parents as S59  # noqa: E402  (frozen; functions used verbatim)

SELF = ROOT / "s62_parents_confirm.py"
STUB = ROOT / "s62_parents_confirm.prereg.sha256"
OUT = ROOT / "results_s62.txt"
RUNS = ROOT / "runs" / "s62"
SEED = 20261017
CPLUS_SEEDS = (1, 2)
W = 20   # s57 producer window (used by the copied Producer)
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
REFS = {"latin_cremma_prose15": "cremma_prose15", "italian_dante": "italian_dante"}
SECTIONS = ("herbal A", "herbal B", "bio", "stars", "pharma", "others")
KEYS = S59.KEYS
log: list[str] = []
T_START = time.time()


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


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


def section_group(sec: str, lang: str) -> str:
    if sec == "H":
        return "herbal A" if lang == "A" else ("herbal B" if lang == "B" else "others")
    return {"B": "bio", "S": "stars", "P": "pharma"}.get(sec, "others")


def load_langs(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return {str(p["id"]): str(p.get("lang", "?")) for p in d["pages"]}


# ======================================================================= s57 producer (copied verbatim from
# s57_local_memory_model.py, class Producer; W = 20 as in s57)
class Producer:
    def __init__(self, train_pages, seg):
        self.seg = seg
        start = Counter(l[0] for lines in train_pages for l in lines)
        lex = Counter(w for lines in train_pages for l in lines for w in l)
        self.start_w, self.start_c = self._cum(start)
        self.lex_w, self.lex_c = self._cum(lex)
        self.lens = [len(l) for lines in train_pages for l in lines]
        self.page_lines = [len(lines) for lines in train_pages]
        pre, suf, gl = Counter(), Counter(), Counter()
        for w, c in lex.items():
            p, co, s = seg.segment(w)
            pre[p] += c; suf[s] += c
            for ch in co:
                gl[ch] += c
        self.pre_w, self.pre_c = self._cum(pre)
        self.suf_w, self.suf_c = self._cum(suf)
        self.gl_w, self.gl_c = self._cum(gl)
        self.set_params(dict(p_copy=0.0, tau=1.0, a=0.0, q_pre=0.25, q_suf=0.25, q_core=0.25))

    @staticmethod
    def _cum(counter):
        items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
        ws = [k for k, _ in items]
        cum, t = [], 0
        for _, c in items:
            t += c; cum.append(t)
        return ws, cum

    def set_params(self, prm):
        self.prm = dict(prm)
        wts = [math.exp(-(d - 1) / prm["tau"]) for d in range(1, W + 1)]
        self.kcum = []
        t = 0.0
        for x in wts:
            t += x; self.kcum.append(t)

    def _swap(self, rng, cur, ws, cum):
        for _ in range(30):
            x = rng.choices(ws, cum_weights=cum)[0]
            if x != cur:
                return x
        return cur

    def edit(self, rng, w):
        p = self.prm
        u = rng.random()
        if u >= p["q_pre"] + p["q_suf"] + p["q_core"]:
            return w
        pre, core, suf = self.seg.segment(w)
        if u < p["q_pre"]:
            pre = self._swap(rng, pre, self.pre_w, self.pre_c)
        elif u < p["q_pre"] + p["q_suf"]:
            suf = self._swap(rng, suf, self.suf_w, self.suf_c)
        else:
            op = rng.randrange(3)
            if op == 2 and len(core) < 2:
                op = 0
            i = rng.randrange(len(core) + (1 if op == 1 else 0))
            if op == 0:
                g = self._swap(rng, core[i], self.gl_w, self.gl_c)
                core = core[:i] + g + core[i + 1:]
            elif op == 1:
                g = rng.choices(self.gl_w, cum_weights=self.gl_c)[0]
                core = core[:i] + g + core[i:]
            else:
                core = core[:i] + core[i + 1:]
        return pre + core + suf

    def page(self, rng, n_lines):
        p = self.prm
        hist, lines = [], []
        for _ in range(n_lines):
            L = rng.choice(self.lens)
            line = [rng.choices(self.start_w, cum_weights=self.start_c)[0]]
            hist.append(line[0])
            for i in range(1, L):
                if p["p_copy"] > 0 and rng.random() < p["p_copy"]:
                    if lines and len(lines[-1]) > i and rng.random() < p["a"]:
                        src = lines[-1][i]
                    else:
                        h = min(W, len(hist))
                        d = rng.choices(range(1, h + 1), cum_weights=self.kcum[:h])[0]
                        src = hist[-d]
                    w = self.edit(rng, src)
                else:
                    w = rng.choices(self.lex_w, cum_weights=self.lex_c)[0]
                line.append(w); hist.append(w)
            lines.append(line)
        return lines

    def text(self, seed, page_line_counts):
        rng = random.Random(seed)
        return [self.page(rng, n) for n in page_line_counts]


# ======================================================================= pipeline pieces
def reversed_prepare(label, by, SlotSegmenter, split_names, segment_override=None):
    """by: OrderedDict id -> (section, lines).  Fit on split_names' held-out (FIT) pages, score its training pages."""
    names = list(by)
    tr, te = split_names(OrderedDict((k, v[1]) for k, v in by.items()))
    fit_set, sc_set = set(te), set(tr)
    fit_names = [k for k in names if k in fit_set]
    sc_names = [k for k in names if k in sc_set]
    if segment_override is None:
        seg = SlotSegmenter([w for p in fit_names for l in by[p][1] for w in l])
        segf = lambda w: seg.segment(w)[1]  # noqa: E731
        seginfo = f"SlotSegmenter {len(seg.prefixes)} prefix / {len(seg.suffixes)} suffix candidates (fit pages)"
    else:
        segf, seginfo = segment_override, "identity segmentation"
    X = S59.prepare(label, [by[p][1] for p in fit_names], [(p, by[p][0], by[p][1]) for p in sc_names], segf)
    return X, fit_names, sc_names, tr, seginfo


def gate_and_verdict(real_lo, cplus_lo, cminus_lo):
    """dicts T -> W u V / N1 interval lower bound.  -> (gate ok, per-T flags, verdict)."""
    cp = {T: v > 1 for T, v in cplus_lo.items()}
    cm = {T: v <= 1 for T, v in cminus_lo.items()}
    gate = all(cp.values()) and all(cm.values())
    above = {T: v > 1 for T, v in real_lo.items()}
    if not gate:
        verdict = "inconclusive: controls failed"
    elif not any(above.values()):
        verdict = "no local edit-chain"
    elif all(above.values()):
        verdict = "local edit-chain"
    else:
        verdict = "mixed"
    return gate, cp, cm, above, verdict


def fmt(rt, m, k):
    pt, lo, hi = rt[(m, k)]
    return f"{pt:.3f} [{lo:.3f},{hi:.3f}]"


def print_block(S, emit_fn):
    emit_fn(f"--- {S['label']}: {S['pages']} scored pages, {S['tokens']} tokens, {S['E']} events (first-on-page rare cores); "
            f"N2 section fallback pages {S['n2_fallback']}, N3 length fallback events {S['len_fallback']}")
    r = S["rates"]
    emit_fn("    parent rates  real  W {W:.4f}  V {V:.4f}  WuV {WV:.4f}".format(**r["real"]))
    for m in S59.NULLS:
        emit_fn(f"                  {m:4}  W {r[m]['W']:.4f}  V {r[m]['V']:.4f}  WuV {r[m]['WV']:.4f}")
    for m in S59.NULLS:
        emit_fn(f"    ratio vs {m:4}: " + "  ".join(f"{k:2} {fmt(S['rt'], m, k)}" for k in KEYS))
    emit_fn(f"    end-glyph-only parent share: real {S['end_share']:.4f} ({S['end_n'][0]}/{S['end_n'][1]}); "
            + ", ".join(f"{m} {S['null_end_share'][m]:.4f}" for m in S59.NULLS))
    pt, lo, hi = S["rt"][("N1", "WV")]
    emit_fn(f"    DECISION STAT WuV/N1 {pt:.3f} [{lo:.3f},{hi:.3f}] -> {'above 1' if lo > 1 else 'includes 1 or below'}")


def per_section(rows, groups, seed):
    out = {}
    for i, g in enumerate(SECTIONS):
        sub = [r for r in rows if groups.get(r["id"]) == g]
        if not sub:
            out[g] = None
            continue
        rt, rates, E = S59.ratios(sub, seed + i)
        out[g] = dict(pages=len(sub), E=E, wv_n1=rt[("N1", "WV")], v_n1=rt[("N1", "V")])
    return out


# ======================================================================= fixture (synthetic only)
def fixture():
    out = []

    def say(s=""):
        print(s, flush=True)
        out.append(s)

    import g1_edge_joint as G1  # noqa: E402  (split helper only; reads no data)
    from scoreboard.metrics_new import SlotSegmenter  # noqa: E402
    rng = random.Random(5)
    alph = "abcdefghik"
    common = sorted(set("".join(rng.choice(alph) for _ in range(rng.randint(2, 4))) for _ in range(60)))[:40]
    cw = [1 / (i + 1) for i in range(len(common))]
    # dense rare pool (short words over 5 glyphs) so that list texts still have enough chance edit-1 parents
    rarepool = sorted(set("".join(rng.choice("abcde") for _ in range(rng.randint(3, 5))) for _ in range(6000)) - set(common))

    def mutate(w):
        op = rng.randrange(3)
        if op == 2 and len(w) < 2:
            op = 0
        i = rng.randrange(len(w) + (1 if op == 1 else 0))
        g = rng.choice(alph)
        if op == 0:
            return w[:i] + g + w[i + 1:]
        if op == 1:
            return w[:i] + g + w[i:]
        return w[:i] + w[i + 1:]

    def make(kind, n_pages=100):
        pages = []
        for _ in range(n_pages):
            lines, hist = [], []
            for li in range(10):
                L = []
                for j in range(8):
                    u = rng.random()
                    if kind == "mutation" and u < 0.15 and hist:
                        w = mutate(hist[-rng.randint(1, min(S59.WIN, len(hist)))])
                    elif u < 0.30:
                        w = rng.choice(rarepool)
                    else:
                        w = rng.choices(common, cw)[0]
                    L.append(w); hist.append(w)
                lines.append(L)
            pages.append(lines)
        return pages

    keep = (S59.N_NULL, S59.N_BOOT)
    S59.N_NULL, S59.N_BOOT = 100, 200   # fixture only: fewer draws for speed
    res = {}
    for kind in ("mutation", "list"):
        pages = make(kind, 300)
        by = OrderedDict((f"p{i}", ("SEC" + str(i % 3), ls)) for i, ls in enumerate(pages))
        X, fit_names, sc_names, _, info = reversed_prepare(kind, by, SlotSegmenter, G1.split_names, lambda w: w)
        say(f"fixture {kind}: fit {len(fit_names)} / scored {len(sc_names)} pages; {info}")
        S = S59.summarize(f"fixture {kind}", [S59.analyse(X, SEED + 11)], SEED + 12)
        print_block(S, say)
        res[kind] = S
        Y, inf = S59.build_cminus(X, SEED + 7)
        say(f"    C- built: list entries used {inf['list_used']} of {inf['list_len']}, refills {inf['refills']}")
        S2 = S59.summarize(f"fixture C- from {kind} text", [S59.analyse(Y, SEED + 13)], SEED + 14)
        print_block(S2, say)
        res["cminus " + kind] = S2
    # C+ path: copied s57 producer on synthetic wrapped words, fresh-order generation, SlotSegmenter cores
    pre = ["", "q", "o", "d"]; suf = ["", "y", "n", "l"]
    base = [[[rng.choice(pre) + w + rng.choice(suf) for w in l] for l in ls] for ls in make("list", 80)]
    gseg = SlotSegmenter([w for ls in base for l in ls for w in l])
    prod = Producer(base, gseg)
    prod.set_params(dict(p_copy=0.3, tau=4.0, a=0.15, q_pre=0.1, q_suf=0.1, q_core=0.6))
    fitc, scc = [len(ls) for ls in base[:20]], [len(ls) for ls in base[20:]]
    rows = []
    for s in CPLUS_SEEDS:
        pages = prod.text(s, fitc + scc)
        gfit, gsc = pages[:len(fitc)], pages[len(fitc):]
        assert [len(p) for p in gsc] == scc
        seg = SlotSegmenter([w for ls in gfit for l in ls for w in l])
        Xg = S59.prepare(f"fixture C+ s{s}", gfit, [(f"g{i}", "S57", ls) for i, ls in enumerate(gsc)], lambda w, seg=seg: seg.segment(w)[1])
        rows.append(S59.analyse(Xg, SEED + 20 + s))
    Sp = S59.summarize("fixture C+ (copied s57 producer, seeds 1-2 pooled)", rows, SEED + 30)
    print_block(Sp, say)
    S59.N_NULL, S59.N_BOOT = keep
    # verdict logic on toy inputs
    g1 = gate_and_verdict({"a": 0.98, "b": 0.99}, {"a": 1.1, "b": 1.05}, {"a": 0.9, "b": 1.0})[4]
    g2 = gate_and_verdict({"a": 1.02, "b": 1.03}, {"a": 1.1, "b": 1.05}, {"a": 0.9, "b": 0.95})[4]
    g3 = gate_and_verdict({"a": 1.02, "b": 0.97}, {"a": 1.1, "b": 1.05}, {"a": 0.9, "b": 0.95})[4]
    g4 = gate_and_verdict({"a": 0.9, "b": 0.9}, {"a": 1.1, "b": 0.99}, {"a": 0.9, "b": 0.95})[4]
    g5 = gate_and_verdict({"a": 0.9, "b": 0.9}, {"a": 1.1, "b": 1.1}, {"a": 1.01, "b": 0.95})[4]
    say(f"  verdict logic: {g1} / {g2} / {g3} / {g4} / {g5}")
    sec = per_section([dict(id="x", real={k: 1 for k in KEYS}, null={m: {k: 1.0 for k in KEYS} for m in S59.NULLS}, E=1)],
                      {"x": section_group("H", "A")}, SEED)
    checks = [
        ("mutation WuV/N1 lower bound > 1", res["mutation"]["rt"][("N1", "WV")][1] > 1),
        ("list WuV/N1 lower bound <= 1", res["list"]["rt"][("N1", "WV")][1] <= 1),
        ("C- from list text WuV/N1 lower bound <= 1", res["cminus list"]["rt"][("N1", "WV")][1] <= 1),
        # not a check (printed only): pre-freeze fixture run gave C- from the 15 %-mutation text WuV/N1 1.049
        # [1.031,1.072]; C- keeps the real windows, which in a mutation text are enriched in the words the rare list
        # (itself fit-page mutants) neighbours, so C- under N1 is not guaranteed <= 1 when the source text mutates.
        ("C+ (copied s57 producer) WuV/N1 lower bound > 1", Sp["rt"][("N1", "WV")][1] > 1),
        ("verdict logic", (g1, g2, g3, g4, g5) == ("no local edit-chain", "local edit-chain", "mixed",
                                                  "inconclusive: controls failed", "inconclusive: controls failed")),
        ("section grouping", sec["herbal A"] is not None and section_group("H", "B") == "herbal B"
         and section_group("T", "B") == "others" and section_group("H", "?") == "others"),
        ("s59 constants as s59", (S59.WIN, S59.VPOS, S59.TOPK, S59.N_NULL, S59.N_BOOT, S59.SUB_FRAC) == (15, 1, 20, 500, 500, 0.8)),
    ]
    ok = True
    for nm, c in checks:
        say(f"  check {nm}: {'OK' if c else 'FAIL'}")
        ok &= bool(c)
    say(f"FIXTURE {'PASS' if ok else 'FAIL'}")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return ok


# ======================================================================= main
def main():
    import g1_edge_joint as G1  # noqa: E402
    from scoreboard.metrics_new import SlotSegmenter  # noqa: E402
    emit("s62 -- confirmation of s59's N1 reading: rare-core edit-1 parents on the 166 s59-training pages (fit on the 41 held-out)")
    emit(f"date: {clock()}")
    emit(f"sha256 s62_parents_confirm.py: {sha256(SELF)}")
    if STUB.exists():
        emit(f"sha256 s62_parents_confirm.prereg.sha256: {sha256(STUB)}")
    emit(f"stub_match: {stub_match()}")
    for m in S59.local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    assert (S59.WIN, S59.VPOS, S59.TOPK, S59.N_NULL, S59.N_BOOT, S59.SUB_FRAC) == (15, 1, 20, 500, 500, 0.8)
    emit(f"numpy {np.__version__}; python {sys.version.split()[0]} {'-I' if sys.flags.isolated else ''}; s59 functions imported; "
         f"top-{S59.TOPK} from FIT-page cores; W = preceding {S59.WIN} tokens; V = line above j-{S59.VPOS}..j+{S59.VPOS}; "
         f"nulls {S59.N_NULL} draws; interval {S59.N_BOOT} draws of {int(S59.SUB_FRAC * 100)} % of scored pages without replacement")
    emit("")
    RUNS.mkdir(parents=True, exist_ok=True)
    summaries, allrows, info, sections = {}, {}, {}, {}

    def run(label, X, seedoff):
        t = time.time()
        A = S59.analyse(X, SEED + seedoff)
        S = S59.summarize(label, [A], SEED + seedoff + 1)
        allrows[label] = A["rows"]
        emit(f"  [{label}] analysed in {time.time() - t:.0f}s (top-20: {' '.join(sorted(X['top']))}; rare FIT core types {len(X['rare'])})")
        return A, S

    off = 0
    for T, f in TRANSLITS.items():
        off += 100
        path = ROOT / "data" / "translit" / f"{f}.meta.json"
        by, _ = S59.load_meta(path)
        langs = load_langs(path)
        X, fit_names, sc_names, tr_names, seginfo = reversed_prepare(T, by, SlotSegmenter, G1.split_names)
        emit(f"text {T}: {path.relative_to(ROOT).as_posix()} sha256={sha256(path)[:16]}; pages {len(by)} -> scored {len(sc_names)} / fit {len(fit_names)}; {seginfo}")
        A, S = run(T, X, off)
        summaries[T] = S
        print_block(S, emit)
        groups = {p: section_group(by[p][0], langs.get(p, "?")) for p in sc_names}
        sections[T] = per_section(A["rows"], groups, SEED + off + 50)
        # C-
        Y, inf = S59.build_cminus(X, SEED + 7)
        info[f"{T} C-"] = inf
        (RUNS / f"cminus_{T}_cores.json").write_text(json.dumps(dict(
            source=f"s62 C- list-reading control (s59 build_cminus) on {T} scored pages (core level)", **inf,
            pages=[dict(id=p.id, section=p.section, lines=p.lines) for p in Y["pages"]])), encoding="utf-8", newline="\n")
        emit(f"  C- {T}: list entries used {inf['list_used']} (rare FIT core types {inf['list_len']}), refills {inf['refills']}")
        A2, S2 = run(f"{T} C-", Y, off + 10)
        summaries[f"{T} C-"] = S2
        print_block(S2, emit)
        # C+: s57 producer, fresh order
        fitj = json.loads((ROOT / "runs" / "s57" / f"fit_{T}.json").read_text(encoding="utf-8"))
        prm = fitj["params"]
        tr_ordered = list(tr_names)   # s57 built its producer from G1.split_names training pages in split order
        gseg = SlotSegmenter([w for p in tr_ordered for l in by[p][1] for w in l])
        prod = Producer([by[p][1] for p in tr_ordered], gseg)
        prod.set_params(prm)
        fitc = [len(by[p][1]) for p in fit_names]
        scc = [len(by[p][1]) for p in sc_names]
        res_list = []
        for s in CPLUS_SEEDS:
            pages = prod.text(s, fitc + scc)
            gfit, gsc = pages[:len(fitc)], pages[len(fitc):]
            side = dict(source=f"s62 C+: s57 producer (params runs/s57/fit_{T}.json) on {T} s59-training pages, seed {s}, "
                               f"41 fit-like pages first then {len(gsc)} scored-like pages", params=prm,
                        pages=[dict(id=f"f{i}", section="S57", lines=ls, role="fit") for i, ls in enumerate(gfit)]
                        + [dict(id=f"g{i}", section="S57", lines=ls, role="scored") for i, ls in enumerate(gsc)])
            (RUNS / f"cplus_{T}_s{s}.meta.json").write_text(json.dumps(side), encoding="utf-8", newline="\n")
            s57p = ROOT / "runs" / "s57" / f"gen_{T}_s{s}.meta.json"
            ident = "n/a"
            if s57p.exists():
                old = set(json.dumps(p["lines"]) for p in json.loads(s57p.read_text(encoding="utf-8"))["pages"])
                ident = sum(json.dumps(ls) in old for ls in pages)
            seg = SlotSegmenter([w for ls in gfit for l in ls for w in l])
            Xg = S59.prepare(f"{T} C+ s{s}", gfit, [(f"g{i}", "S57", ls) for i, ls in enumerate(gsc)], lambda w, seg=seg: seg.segment(w)[1])
            emit(f"text {T} C+ s{s}: params {prm}; fit-like {len(gfit)} / scored-like {len(gsc)} pages, "
                 f"{sum(len(l) for ls in gsc for l in ls)} scored tokens; pages identical to s57 sidecar seed {s}: {ident}")
            Ag, Sg = run(f"{T} C+ s{s}", Xg, off + 20 + s)
            res_list.append(Ag)
            emit(f"    seed {s} beside: WuV/N1 {fmt(Sg['rt'], 'N1', 'WV')}, events {Sg['E']}")
        Sp = S59.summarize(f"{T} C+ (s57 producer, seeds 1-2 pooled)", res_list, SEED + off + 30)
        summaries[f"{T} C+"] = Sp
        print_block(Sp, emit)
        emit(f"  elapsed so far {time.time() - T_START:.0f}s")
        emit("")
    for R, f in REFS.items():
        off += 100
        path = ROOT / "data" / "controls_realline" / f"{f}.meta.json"
        by, _ = S59.load_meta(path)
        X, fit_names, sc_names, _, seginfo = reversed_prepare(R, by, SlotSegmenter, G1.split_names)
        emit(f"text {R}: {path.relative_to(ROOT).as_posix()} sha256={sha256(path)[:16]}; pages {len(by)} -> scored {len(sc_names)} / fit {len(fit_names)}; {seginfo}")
        A, S = run(R, X, off)
        summaries[R] = S
        print_block(S, emit)
        emit("")

    emit("=== Summary: ratio real/null [95 % page-subsample interval] ===")
    cols = [("N1", "WV"), ("N1", "V"), ("N1", "W"), ("N2", "WV"), ("N3", "WV"), ("N3", "V"), ("N3t", "WV")]
    emit(f"{'text':38} {'pages':>5} {'events':>6} | " + " | ".join(f"{k + '/' + m:^19}" for m, k in cols))
    for lab, S in summaries.items():
        emit(f"{lab[:38]:38} {S['pages']:5d} {S['E']:6d} | " + " | ".join(
            f"{S['rt'][(m, k)][0]:5.3f} [{S['rt'][(m, k)][1]:.2f},{S['rt'][(m, k)][2]:.2f}]".center(19) for m, k in cols))
    emit("")
    emit("=== Parent-rate levels (share of events with a WuV parent) and end-glyph share ===")
    for lab, S in summaries.items():
        r = S["rates"]
        emit(f"  {lab[:38]:38} real {r['real']['WV']:.4f}  N1 {r['N1']['WV']:.4f}  N2 {r['N2']['WV']:.4f}  N3 {r['N3']['WV']:.4f}  "
             f"N3t {r['N3t']['WV']:.4f} | end-glyph real {S['end_share']:.3f} / N1 {S['null_end_share']['N1']:.3f} / N3 {S['null_end_share']['N3']:.3f}")
    emit("")
    emit("=== Per-section WuV/N1 and V/N1 on real scored pages (descriptive) ===")
    for T in TRANSLITS:
        for g in SECTIONS:
            d = sections[T][g]
            if d is None:
                emit(f"  {T:5} {g:9} (no scored pages)")
                continue
            emit(f"  {T:5} {g:9} pages {d['pages']:3d} events {d['E']:5d}  WuV/N1 {d['wv_n1'][0]:.3f} [{d['wv_n1'][1]:.3f},{d['wv_n1'][2]:.3f}]  "
                 f"V/N1 {d['v_n1'][0]:.3f} [{d['v_n1'][1]:.3f},{d['v_n1'][2]:.3f}]")
    emit("")
    lo = lambda lab: summaries[lab]["rt"][("N1", "WV")][1]  # noqa: E731
    gate, cp, cm, above, verdict = gate_and_verdict({T: lo(T) for T in TRANSLITS}, {T: lo(f"{T} C+") for T in TRANSLITS},
                                                    {T: lo(f"{T} C-") for T in TRANSLITS})
    emit("=== Pre-registered verdict (decision statistic WuV/N1, interval lower bound) ===")
    for T in TRANSLITS:
        emit(f"  {T}: real {fmt(summaries[T]['rt'], 'N1', 'WV')} -> {'above 1' if above[T] else 'includes 1 or below'}; "
             f"C+ {fmt(summaries[T + ' C+']['rt'], 'N1', 'WV')} {'PASS' if cp[T] else 'FAIL'} (needs lo > 1); "
             f"C- {fmt(summaries[T + ' C-']['rt'], 'N1', 'WV')} {'PASS' if cm[T] else 'FAIL'} (needs lo <= 1)")
    emit(f"  control gate: {'PASS' if gate else 'FAIL'}")
    emit(f"VERDICT: {verdict}")
    emit("  caveats fixed before the run: the top-20 list and segmenter come from only 41 pages, so the 'rare' event set and the")
    emit("  C- list differ from s59's; C+ is the s57 producer with s57's parameters (fitted on these same pages' text, which is")
    emit("  the generator's lexicon, not the scored output); the Latin reference has only 10 scored pages.  Fixture note: C- built")
    emit("  from a strongly mutating synthetic text sat above 1 under N1 (1.049 [1.031,1.072]): C- keeps the real windows, so a")
    emit("  C- gate failure would point at the source text's local composition, not at a bug.  The 80 % subsample interval is")
    emit("  narrower than a full bootstrap, and with ~4x s59's pages it is about half as wide as s59's.")
    (RUNS / "cells.json").write_text(json.dumps(dict(
        summaries={lab: dict(E=S["E"], pages=S["pages"], tokens=S["tokens"], end_share=S["end_share"],
                             null_end_share=S["null_end_share"], rates=S["rates"],
                             ratios={f"{k} vs {m}": list(v) for (m, k), v in S["rt"].items()}) for lab, S in summaries.items()},
        sections=sections, rows=allrows, cminus=info, gate=gate, verdict=verdict), indent=1, default=float),
        encoding="utf-8", newline="\n")
    emit("")
    emit(f"date end: {clock()}")
    emit(f"elapsed: {time.time() - T_START:.1f} s")
    emit(f"paths: {OUT}, {RUNS / 'cells.json'}, {RUNS}/cminus_<T>_cores.json, {RUNS}/cplus_<T>_s<seed>.meta.json")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--fixture" in sys.argv:
        sys.exit(0 if fixture() else 1)
    main()
