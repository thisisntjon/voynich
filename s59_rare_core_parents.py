"""s59 -- rare-core parents: when a rare core first appears on a page, is it a 1-glyph mutation of a nearby core on the
same page (procedural self-citation), or drawn from an outside list?

PRE-REGISTERED (frozen in s59_rare_core_parents.prereg.sha256 BEFORE any real-data run; before the freeze this script
ran only on its synthetic fixture, `--fixture`, which reads no real data).

Background: results_s56.txt (rare cores recur at short range, decaying over ~20 tokens); results_s57.txt (a fitted
local-memory copy-and-vary producer fits repetition but fails held-out structure).

UNITS
  Split: g1_edge_joint.split_names(by) (random.Random(20261017), 80 / 20 of pages): ZL3b 166 / 41, RF1b 166 / 41,
    IT2a 165 / 41.  Core = scoreboard/metrics_new.SlotSegmenter fitted on the TRAINING pages' tokens, applied to
    every token.  Top-20 core list = the 20 most frequent cores (token count) on the training pages.  Scoring is on
    the HELD-OUT pages only.  Page stream = the page's lines concatenated in reading order (crossing line ends).
  Event: a held-out token whose core is not in the training top-20 and has not occurred earlier on the same page
    ("first-on-page rare core").
  Parent: an earlier core on the same page at glyph-level (character; EVA character for Voynich) Levenshtein distance
    exactly 1 from the event core, located
      (W) within the preceding 15 tokens of the page stream (crossing line ends), or
      (V) on the line immediately above, token index j-1, j or j+1 (j = the event's token index on its line).
    Counts: events with >= 1 W parent, >= 1 V parent, >= 1 parent in W u V.
  End-glyph share: among events with a W u V parent, the share for which at least one parent differs only at the
    first or last glyph (substitution at index 0 or L-1; insertion / deletion of the first or last glyph).

NULLS (each 500 draws; expected parent counts per page = mean over draws)
  N1 within-page token-order shuffle: the page's cores permuted (multiset kept, line lengths kept), events and
     parents recomputed from scratch.
  N2 cross-page window: each real event keeps its core; the window is taken from a random OTHER held-out page of the
     same section (any other held-out page if the section has no other one): W = the 15 tokens before stream index
     k = min(t, N_other) of that page; V = line min(li-1, n_lines_other-1) of that page at indices j-1..j+1 (only for
     events with li >= 1).  One other page drawn per event per draw.
  N3 frequency-matched (length-matched): the event core is replaced by a random rare core (training core type not in
     the top-20) of the same length (uniform over types; nearest available length if none; resampled up to 20 times
     if the candidate occurred earlier on the page) and its parents are measured in the REAL window.
     Beside (not in the verdict): N3t, the same with candidates weighted by training token count.
  Statistic: ratio = (sum over pages of real events with a parent) / (sum over pages of null expected count), for W,
     V and W u V.  Interval: page subsampling, 80 % of the scored pages without replacement, 500 draws,
     [2.5 %, 97.5 %] percentiles (np.random.default_rng(20261017 + offset)).  "Above 1" = interval lower bound > 1.

CONTROLS (scored identically: own training-page segmenter / top-20 / lexicon, held-out pages only)
  C+ (positive, known on-page mutation): the s57 fitted local-memory producer per transliteration, its sidecars
     runs/s57/gen_<T>_s{1,2,3}.meta.json (166 'train' + 41 'heldout' pages each, role field); each seed scored as its
     own text, the three seeds' held-out page rows pooled (123 pages) for the control call; per seed printed beside.
  C- (negative, outside list): the real held-out core stream of each transliteration, each first-on-page rare core
     replaced, in page order (manuscript order of the held-out pages) and token order, by the next entry of a fixed
     list = all rare training core types in a random.Random(20261017 + 7) permutation (sampled without replacement;
     a fresh permutation is appended if exhausted, counted); every later occurrence of that core on the same page gets
     the same replacement (on-page repetition kept, derivation destroyed); entries already emitted on the page are
     skipped.  Done at the core level (no re-segmentation).
  References (not in the verdict): data/controls_realline/cremma_prose15 (Latin prose; 13 pages -> 3 held-out) and
     data/controls_realline/italian_dante (Dante; 101 pages -> 20 held-out), as in s56, same pipeline.

VERDICT (fixed)
  call(text) = "mutation" iff the W u V ratio vs N3 has interval lower bound > 1.
  Controls pass iff C+ (pooled seeds) is called mutation AND C- is not, on each of ZL3b, RF1b, IT2a.
  If controls fail: "inconclusive: controls failed".
  Else if ZL3b, RF1b and IT2a are all called mutation: "on-page mutation".
  Else if none is: "outside list".
  Else: "split across transliterations: no call".
  Printed beside: the V-only ratio vs every null (line-above echo), W and W u V vs N1 / N2, N3t, end-glyph shares.

Run:    python -I s59_rare_core_parents.py [--fixture]
Writes: results_s59.txt; runs/s59/ (cells.json per-page rows, cminus_<T>_cores.json C- core streams, fixture.txt).
"""
from __future__ import annotations

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

SELF = ROOT / "s59_rare_core_parents.py"
STUB = ROOT / "s59_rare_core_parents.prereg.sha256"
OUT = ROOT / "results_s59.txt"
RUNS = ROOT / "runs" / "s59"
SEED = 20261017
TOPK = 20
WIN = 15
VPOS = 1
N_NULL = 500
N_BOOT = 500
SUB_FRAC = 0.8
TIME_LIMIT = 45 * 60
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
REFS = {"latin_cremma_prose15": "cremma_prose15", "italian_dante": "italian_dante"}
KEYS = ("W", "V", "WV")
NULLS = ("N1", "N2", "N3", "N3t")
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
    return sorted(set(out))


def load_meta(path: Path):
    """-> OrderedDict id -> (section, lines), plus role dict if present."""
    d = json.loads(path.read_text(encoding="utf-8"))
    by, role = OrderedDict(), {}
    for p in d["pages"]:
        lines = [[w for w in l if w] for l in p["lines"]]
        lines = [l for l in lines if l]
        if lines:
            by[str(p["id"])] = (str(p.get("section", "?")), lines)
            if "role" in p:
                role[str(p["id"])] = p["role"]
    return by, role


# ======================================================================= edit-distance helpers
def variants(c: str, alph):
    out = set()
    L = len(c)
    for i in range(L):
        out.add(c[:i] + c[i + 1:])
        for g in alph:
            if g != c[i]:
                out.add(c[:i] + g + c[i + 1:])
    for i in range(L + 1):
        for g in alph:
            out.add(c[:i] + g + c[i:])
    out.discard(c)
    out.discard("")
    return out


def end_only(a: str, b: str) -> bool:
    """a, b at Levenshtein distance 1: True if the edit can be placed at the first or last glyph."""
    if len(a) == len(b):
        d = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return len(d) == 1 and d[0] in (0, len(a) - 1)
    lo, sh = (a, b) if len(a) > len(b) else (b, a)
    return lo[1:] == sh or lo[:-1] == sh


class Scorer:
    """Neighbour sets restricted to the cores present on the scored pages (all windows come from those pages)."""

    def __init__(self, vocab, alph):
        self.vocab = set(vocab)
        self.alph = sorted(alph)
        self.nb = {}

    def neigh(self, c):
        s = self.nb.get(c)
        if s is None:
            s = self.nb[c] = frozenset(variants(c, self.alph) & self.vocab)
        return s

    def flags(self, c, Wc, Vc, want_end=False):
        nb = self.neigh(c)
        w = not nb.isdisjoint(Wc)
        v = bool(Vc) and not nb.isdisjoint(Vc)
        e = False
        if want_end and (w or v):
            e = any(end_only(c, x) for x in list(Wc) + list(Vc) if x in nb)
        return w, v, e


# ======================================================================= page structures
class Page:
    def __init__(self, pid, section, lines):
        self.id, self.section, self.lines = pid, section, lines
        self.stream = [c for l in lines for c in l]
        self.pos = [(li, j) for li, l in enumerate(lines) for j in range(len(l))]
        self.lens = [len(l) for l in lines]
        self.first = {}
        for t, c in enumerate(self.stream):
            self.first.setdefault(c, t)


def events_of(stream, pos, top):
    seen, ev = set(), []
    for t, c in enumerate(stream):
        if c not in top and c not in seen:
            ev.append((t,) + pos[t] + (c,))
        seen.add(c)
    return ev


def window(stream, lines, t, li, j):
    Wc = stream[max(0, t - WIN):t]
    Vc = lines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else []
    return Wc, Vc


def score_lines(lines, top, sc, want_end=True):
    stream = [c for l in lines for c in l]
    pos = [(li, j) for li, l in enumerate(lines) for j in range(len(l))]
    ev = events_of(stream, pos, top)
    r = dict(E=len(ev), W=0, V=0, WV=0, END=0)
    for t, li, j, c in ev:
        Wc, Vc = window(stream, lines, t, li, j)
        w, v, e = sc.flags(c, Wc, Vc, want_end)
        r["W"] += w; r["V"] += v; r["WV"] += (w or v); r["END"] += e
    return r, ev


# ======================================================================= one text
def prepare(name, train_lines_list, test_pages, segment):
    """train_lines_list: list of pages (lines of words); test_pages: list of (id, section, lines of words).
    segment: word -> core.  Returns dict with cores, top-20, rare pools, scorer."""
    tr_cores = Counter(segment(w) for ls in train_lines_list for l in ls for w in l)
    top = set(c for c, _ in tr_cores.most_common(TOPK))
    pages = [Page(pid, sec, [[segment(w) for w in l] for l in ls]) for pid, sec, ls in test_pages]
    return finish(name, tr_cores, top, pages)


def finish(name, tr_cores, top, pages):
    rare = {c: n for c, n in tr_cores.items() if c not in top}
    pool, poolw = {}, {}
    for c, n in sorted(rare.items()):
        pool.setdefault(len(c), []).append(c)
        poolw.setdefault(len(c), []).append(n)
    poolcum = {L: np.cumsum(v).tolist() for L, v in poolw.items()}
    vocab = set(c for p in pages for c in p.stream)
    alph = set(ch for c in list(vocab) + list(tr_cores) for ch in c)
    return dict(name=name, top=top, tr_cores=tr_cores, rare=rare, pool=pool, poolcum=poolcum, pages=pages,
                sc=Scorer(vocab, alph))


def pick_len(pool, L):
    if L in pool:
        return L
    ks = sorted(pool, key=lambda k: (abs(k - L), k))
    return ks[0]


def analyse(X, seed):
    """Per-page rows: real counts and null expected counts.  Returns dict rows (pages x ...)."""
    top, sc, pages = X["top"], X["sc"], X["pages"]
    rng = random.Random(seed)
    by_sec = {}
    for i, p in enumerate(pages):
        by_sec.setdefault(p.section, []).append(i)
    n2_fallback = 0
    rows = []
    real_end = 0; real_wv = 0
    null_end = {k: [0, 0] for k in NULLS}   # (end count, parent count) summed over draws
    len_fallback = 0
    for i, p in enumerate(pages):
        r, ev = score_lines(p.lines, top, sc, True)
        real_end += r["END"]; real_wv += r["WV"]
        row = dict(id=p.id, section=p.section, E=r["E"], real={k: r[k] for k in KEYS}, real_end=r["END"],
                   null={k: {kk: 0.0 for kk in KEYS} for k in NULLS})
        # N1: within-page shuffle
        acc = {kk: 0 for kk in KEYS}
        stream = list(p.stream)
        for _ in range(N_NULL):
            rng.shuffle(stream)
            lines, a = [], 0
            for L in p.lens:
                lines.append(stream[a:a + L]); a += L
            rr, _ = score_lines(lines, top, sc, True)
            for kk in KEYS:
                acc[kk] += rr[kk]
            null_end["N1"][0] += rr["END"]; null_end["N1"][1] += rr["WV"]
        row["null"]["N1"] = {kk: acc[kk] / N_NULL for kk in KEYS}
        # N2: cross-page window
        others = [k for k in by_sec[p.section] if k != i]
        if not others:
            others = [k for k in range(len(pages)) if k != i]
            n2_fallback += 1
        acc = {kk: 0 for kk in KEYS}
        for _ in range(N_NULL):
            for t, li, j, c in ev:
                o = pages[rng.choice(others)]
                k = min(t, len(o.stream))
                Wc = o.stream[max(0, k - WIN):k]
                if li >= 1:
                    ol = o.lines[min(li - 1, len(o.lines) - 1)]
                    Vc = ol[max(0, j - VPOS):j + VPOS + 1]
                else:
                    Vc = []
                w, v, e = sc.flags(c, Wc, Vc, True)
                acc["W"] += w; acc["V"] += v; acc["WV"] += (w or v)
                null_end["N2"][0] += e; null_end["N2"][1] += (w or v)
        row["null"]["N2"] = {kk: acc[kk] / N_NULL for kk in KEYS}
        # N3 / N3t: length-matched rare training core in the real window
        wins = [window(p.stream, p.lines, t, li, j) for t, li, j, c in ev]
        for nm in ("N3", "N3t"):
            acc = {kk: 0 for kk in KEYS}
            for (t, li, j, c), (Wc, Vc) in zip(ev, wins):
                L = pick_len(X["pool"], len(c))
                if L != len(c):
                    len_fallback += 1
                cands, cum = X["pool"][L], X["poolcum"][L]
                for _ in range(N_NULL):
                    for _try in range(20):
                        x = rng.choice(cands) if nm == "N3" else rng.choices(cands, cum_weights=cum)[0]
                        if p.first.get(x, 10 ** 9) >= t:
                            break
                    w, v, e = sc.flags(x, Wc, Vc, True)
                    acc["W"] += w; acc["V"] += v; acc["WV"] += (w or v)
                    null_end[nm][0] += e; null_end[nm][1] += (w or v)
            row["null"][nm] = {kk: acc[kk] / N_NULL for kk in KEYS}
        rows.append(row)
        if time.time() - T_START > TIME_LIMIT:
            raise TimeoutError("run exceeded 45 minutes")
    return dict(name=X["name"], rows=rows, n2_fallback=n2_fallback, len_fallback=len_fallback // 2,
                real_end=real_end, real_wv=real_wv, null_end=null_end,
                tokens=sum(len(p.stream) for p in pages), n_top=len(top), n_rare_types=len(X["rare"]))


def ratios(rows, seed):
    """-> {(null, key): (point, lo, hi)} and rates."""
    n = len(rows)
    real = {k: np.array([r["real"][k] for r in rows], float) for k in KEYS}
    nul = {(m, k): np.array([r["null"][m][k] for r in rows], float) for m in NULLS for k in KEYS}
    rng = np.random.default_rng(seed)
    kk = max(1, int(round(SUB_FRAC * n)))
    idxs = [rng.choice(n, size=kk, replace=False) for _ in range(N_BOOT)]
    out = {}
    for (m, k), a in nul.items():
        pt = real[k].sum() / a.sum() if a.sum() > 0 else float("nan")
        dr = np.array([real[k][ix].sum() / a[ix].sum() if a[ix].sum() > 0 else np.nan for ix in idxs])
        out[(m, k)] = (pt, float(np.nanpercentile(dr, 2.5)), float(np.nanpercentile(dr, 97.5)))
    E = sum(r["E"] for r in rows)
    rates = {"real": {k: real[k].sum() / E if E else float("nan") for k in KEYS}}
    for m in NULLS:
        rates[m] = {k: nul[(m, k)].sum() / E if E else float("nan") for k in KEYS}
    return out, rates, E


def summarize(label, res_list, seed):
    rows = [r for res in res_list for r in res["rows"]]
    rt, rates, E = ratios(rows, seed)
    rend = sum(res["real_end"] for res in res_list); rwv = sum(res["real_wv"] for res in res_list)
    nend = {m: (sum(res["null_end"][m][0] for res in res_list), sum(res["null_end"][m][1] for res in res_list)) for m in NULLS}
    return dict(label=label, rt=rt, rates=rates, E=E, pages=len(rows), tokens=sum(res["tokens"] for res in res_list),
                end_share=rend / rwv if rwv else float("nan"), end_n=(rend, rwv),
                null_end_share={m: (a / b if b else float("nan")) for m, (a, b) in nend.items()},
                n2_fallback=sum(res["n2_fallback"] for res in res_list),
                len_fallback=sum(res["len_fallback"] for res in res_list))


def call(S):
    pt, lo, hi = S["rt"][("N3", "WV")]
    return lo > 1


def print_summary(S, emit_fn):
    emit_fn(f"--- {S['label']}: {S['pages']} held-out pages, {S['tokens']} tokens, {S['E']} events (first-on-page rare cores); "
            f"N2 section fallback pages {S['n2_fallback']}, N3 length fallback events {S['len_fallback']}")
    r = S["rates"]
    emit_fn("    parent rates  real  W {W:.4f}  V {V:.4f}  WuV {WV:.4f}".format(**r["real"]))
    for m in NULLS:
        emit_fn(f"                  {m:4}  W {r[m]['W']:.4f}  V {r[m]['V']:.4f}  WuV {r[m]['WV']:.4f}")
    for m in NULLS:
        emit_fn(f"    ratio vs {m:4}: " + "  ".join(
            f"{k:2} {S['rt'][(m, k)][0]:6.3f} [{S['rt'][(m, k)][1]:.3f},{S['rt'][(m, k)][2]:.3f}]" for k in KEYS))
    emit_fn(f"    end-glyph-only parent share: real {S['end_share']:.4f} ({S['end_n'][0]}/{S['end_n'][1]}); "
            + ", ".join(f"{m} {S['null_end_share'][m]:.4f}" for m in NULLS))
    pt, lo, hi = S["rt"][("N3", "WV")]
    emit_fn(f"    CALL (WuV vs N3 lower bound > 1): {'mutation' if lo > 1 else 'not mutation'}  (margin lo-1 = {lo - 1:+.3f})")


# ======================================================================= C- builder
def build_cminus(X, seed):
    rare_types = sorted(X["rare"])
    rng = random.Random(seed)
    lst = list(rare_types); rng.shuffle(lst)
    ptr, refills = 0, 0
    new_pages = []
    for p in X["pages"]:
        mapping, seen_o, seen_n = {}, set(), set()
        lines = []
        for l in p.lines:
            nl = []
            for c in l:
                if c in mapping:
                    x = mapping[c]
                elif c not in X["top"] and c not in seen_o:
                    while True:
                        if ptr >= len(lst):
                            nxt = list(rare_types); rng.shuffle(nxt); lst += nxt; refills += 1
                        x = lst[ptr]; ptr += 1
                        if x not in seen_n and x not in X["top"]:
                            break
                    mapping[c] = x
                else:
                    x = c
                seen_o.add(c); seen_n.add(x); nl.append(x)
            lines.append(nl)
        new_pages.append(Page(p.id, p.section, lines))
    Y = finish(X["name"] + " C-", X["tr_cores"], X["top"], new_pages)
    return Y, dict(list_used=ptr, refills=refills, list_len=len(rare_types))


# ======================================================================= fixture
def fixture():
    out = []

    def say(s=""):
        print(s, flush=True)
        out.append(s)

    rng = random.Random(5)
    alph = "abcdefghik"
    common = sorted(set("".join(rng.choice(alph) for _ in range(rng.randint(2, 4))) for _ in range(60)))[:40]
    cw = [1 / (i + 1) for i in range(len(common))]
    rarepool = sorted(set("".join(rng.choice(alph) for _ in range(rng.randint(4, 7))) for _ in range(6000)) - set(common))

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
                    if kind in ("mutation", "linecopy") and u < 0.15 and hist:
                        if kind == "linecopy" and lines:
                            above = lines[-1]
                            src = above[min(len(above) - 1, max(0, j + rng.randint(-1, 1)))]
                        else:
                            src = hist[-rng.randint(1, min(WIN, len(hist)))]
                        w = mutate(src)
                    elif u < 0.30:
                        w = rng.choice(rarepool)
                    else:
                        w = rng.choices(common, cw)[0]
                    L.append(w); hist.append(w)
                lines.append(L)
            pages.append(lines)
        return pages

    import g1_edge_joint as G1  # noqa: E402  (split helper only; reads no data)
    from scoreboard.metrics_new import SlotSegmenter  # noqa: E402
    ok = True
    global N_NULL, N_BOOT
    keep = (N_NULL, N_BOOT)
    N_NULL, N_BOOT = 100, 200   # fixture only: fewer draws for speed
    res = {}
    for kind in ("mutation", "list", "linecopy"):
        pages = make(kind)
        by = OrderedDict((f"p{i}", ls) for i, ls in enumerate(pages))
        tr, te = G1.split_names(by)
        X = prepare(kind, [by[p] for p in tr], [(p, "SEC" + str(int(p[1:]) % 3), by[p]) for p in te], lambda w: w)
        A = analyse(X, SEED + 11)
        S = summarize(f"fixture {kind} (identity segmentation)", [A], SEED + 12)
        print_summary(S, say)
        res[kind] = S
        if kind == "mutation":
            Y, info = build_cminus(X, SEED + 7)
            say(f"    C- built: list entries used {info['list_used']} of {info['list_len']}, refills {info['refills']}")
            S2 = summarize("fixture C- from mutation text", [analyse(Y, SEED + 13)], SEED + 14)
            print_summary(S2, say)
            res["cminus"] = S2
    # end-to-end with the SlotSegmenter path (wrapped words)
    pre = ["", "q", "o", "d"]; suf = ["", "y", "n", "l"]
    pages = make("mutation", 60)
    pages = [[[rng.choice(pre) + w + rng.choice(suf) for w in l] for l in ls] for ls in pages]
    by = OrderedDict((f"p{i}", ls) for i, ls in enumerate(pages))
    tr, te = G1.split_names(by)
    seg = SlotSegmenter([w for p in tr for l in by[p] for w in l])
    X = prepare("wrapped", [by[p] for p in tr], [(p, "S", by[p]) for p in te], lambda w: seg.segment(w)[1])
    S = summarize("fixture mutation, wrapped words, SlotSegmenter cores", [analyse(X, SEED + 15)], SEED + 16)
    print_summary(S, say)
    N_NULL, N_BOOT = keep
    checks = [
        ("mutation called mutation", call(res["mutation"])),
        ("list not called mutation", not call(res["list"])),
        ("C- from mutation text not called mutation", not call(res["cminus"])),
        ("linecopy V vs N1 ratio > 1.5", res["linecopy"]["rt"][("N1", "V")][0] > 1.5),
        ("mutation W vs N1 lower bound > 1", res["mutation"]["rt"][("N1", "W")][1] > 1),
        ("list WuV vs N3 interval includes 1", res["list"]["rt"][("N3", "WV")][1] <= 1 <= res["list"]["rt"][("N3", "WV")][2]),
    ]
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
    emit("s59 -- rare-core parents: on-page 1-glyph mutation vs outside list (held-out pages)")
    emit(f"date: {clock()}")
    emit(f"sha256 s59_rare_core_parents.py: {sha256(SELF)}")
    if STUB.exists():
        emit(f"sha256 s59_rare_core_parents.prereg.sha256: {sha256(STUB)}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(f"numpy {np.__version__}; python {sys.version.split()[0]} {'-I' if sys.flags.isolated else ''}; "
         f"top-{TOPK} from training cores; W = preceding {WIN} tokens; V = line above, index j-{VPOS}..j+{VPOS}; "
         f"nulls {N_NULL} draws; interval {N_BOOT} draws of {int(SUB_FRAC * 100)} % of pages without replacement")
    emit("")
    summaries, allrows, info = {}, {}, {}

    def real_text(label, path, seedoff):
        by, _ = load_meta(path)
        names = list(by)
        tr, te = G1.split_names(OrderedDict((k, v[1]) for k, v in by.items()))
        te_set = set(te)
        te_ordered = [k for k in names if k in te_set]   # manuscript order
        seg = SlotSegmenter([w for p in tr for l in by[p][1] for w in l])
        emit(f"text {label}: {path.relative_to(ROOT).as_posix()} sha256={sha256(path)[:16]}; pages {len(by)} -> train {len(tr)} / held-out {len(te)}; "
             f"SlotSegmenter {len(seg.prefixes)} prefix / {len(seg.suffixes)} suffix candidates")
        X = prepare(label, [by[p][1] for p in tr], [(p, by[p][0], by[p][1]) for p in te_ordered], lambda w: seg.segment(w)[1])
        return X

    def run(label, X, seedoff):
        t = time.time()
        A = analyse(X, SEED + seedoff)
        S = summarize(label, [A], SEED + seedoff + 1)
        allrows[label] = A["rows"]
        emit(f"  [{label}] analysed in {time.time() - t:.0f}s (top-20: {' '.join(sorted(X['top']))}; rare training core types {len(X['rare'])})")
        return A, S

    RUNS.mkdir(parents=True, exist_ok=True)
    off = 0
    for T, f in TRANSLITS.items():
        off += 100
        X = real_text(T, ROOT / "data" / "translit" / f"{f}.meta.json", off)
        A, S = run(T, X, off)
        summaries[T] = S
        print_summary(S, emit)
        Y, inf = build_cminus(X, SEED + 7)
        info[f"{T} C-"] = inf
        (RUNS / f"cminus_{T}_cores.json").write_text(json.dumps(dict(
            source=f"s59 C- list-reading control on {T} held-out pages (core level)", **inf,
            pages=[dict(id=p.id, section=p.section, lines=p.lines) for p in Y["pages"]])), encoding="utf-8", newline="\n")
        emit(f"  C- {T}: list entries used {inf['list_used']} of {inf['list_len']} rare training core types, refills {inf['refills']}")
        A2, S2 = run(f"{T} C-", Y, off + 10)
        summaries[f"{T} C-"] = S2
        print_summary(S2, emit)
        # C+: s57 sidecars
        res_list = []
        for s in (1, 2, 3):
            path = ROOT / "runs" / "s57" / f"gen_{T}_s{s}.meta.json"
            by, role = load_meta(path)
            tr = [k for k in by if role.get(k) == "train"]
            te = [k for k in by if role.get(k) == "heldout"]
            seg = SlotSegmenter([w for p in tr for l in by[p][1] for w in l])
            emit(f"text {T} C+ s{s}: {path.relative_to(ROOT).as_posix()} sha256={sha256(path)[:16]}; train {len(tr)} / held-out {len(te)}")
            Xg = prepare(f"{T} C+ s{s}", [by[p][1] for p in tr], [(p, by[p][0], by[p][1]) for p in te], lambda w, seg=seg: seg.segment(w)[1])
            Ag, Sg = run(f"{T} C+ s{s}", Xg, off + 20 + s)
            res_list.append(Ag)
            emit(f"    seed {s} beside: WuV vs N3 {Sg['rt'][('N3', 'WV')][0]:.3f} [{Sg['rt'][('N3', 'WV')][1]:.3f},{Sg['rt'][('N3', 'WV')][2]:.3f}], "
                 f"events {Sg['E']}")
        Sp = summarize(f"{T} C+ (s57 producer, seeds 1-3 pooled)", res_list, SEED + off + 30)
        summaries[f"{T} C+"] = Sp
        print_summary(Sp, emit)
        emit("")
    for R, f in REFS.items():
        off += 100
        X = real_text(R, ROOT / "data" / "controls_realline" / f"{f}.meta.json", off)
        A, S = run(R, X, off)
        summaries[R] = S
        print_summary(S, emit)
        emit("")

    # ---------------- summary table
    emit("=== Summary: ratio real/null [95 % page-subsample interval] ===")
    emit(f"{'text':34} {'events':>6} | " + " | ".join(f"{k + ' vs ' + m:^22}" for m in ("N1", "N2", "N3") for k in KEYS))
    for lab, S in summaries.items():
        emit(f"{lab[:34]:34} {S['E']:6d} | " + " | ".join(
            f"{S['rt'][(m, k)][0]:5.2f} [{S['rt'][(m, k)][1]:.2f},{S['rt'][(m, k)][2]:.2f}]".center(22) for m in ("N1", "N2", "N3") for k in KEYS))
    emit("")
    emit("=== V-only (line-above echo) and beside statistics ===")
    for lab, S in summaries.items():
        emit(f"  {lab[:34]:34} V vs N1 {S['rt'][('N1', 'V')][0]:.3f} [{S['rt'][('N1', 'V')][1]:.3f},{S['rt'][('N1', 'V')][2]:.3f}]  "
             f"V vs N2 {S['rt'][('N2', 'V')][0]:.3f}  V vs N3 {S['rt'][('N3', 'V')][0]:.3f} [{S['rt'][('N3', 'V')][1]:.3f},{S['rt'][('N3', 'V')][2]:.3f}]  "
             f"WuV vs N3t {S['rt'][('N3t', 'WV')][0]:.3f} [{S['rt'][('N3t', 'WV')][1]:.3f},{S['rt'][('N3t', 'WV')][2]:.3f}]  "
             f"end-glyph share real {S['end_share']:.3f} / N1 {S['null_end_share']['N1']:.3f} / N3 {S['null_end_share']['N3']:.3f}")
    emit("")
    # ---------------- verdict
    calls = {T: call(summaries[T]) for T in TRANSLITS}
    cplus = {T: call(summaries[f"{T} C+"]) for T in TRANSLITS}
    cminus = {T: not call(summaries[f"{T} C-"]) for T in TRANSLITS}
    controls = all(cplus.values()) and all(cminus.values())
    emit("=== Pre-registered verdict ===")
    for T in TRANSLITS:
        emit(f"  {T}: real WuV vs N3 -> {'mutation' if calls[T] else 'not mutation'}; C+ {'PASS' if cplus[T] else 'FAIL'} (called mutation); "
             f"C- {'PASS' if cminus[T] else 'FAIL'} (not called mutation)")
    if not controls:
        verdict = "inconclusive: controls failed"
    elif all(calls.values()):
        verdict = "on-page mutation"
    elif not any(calls.values()):
        verdict = "outside list"
    else:
        verdict = "split across transliterations: no call"
    emit(f"VERDICT: {verdict}")
    emit("  caveats fixed before the run: N3 controls the window's density but not that the event cores themselves may sit in")
    emit("  denser shape neighbourhoods than random rare training types; N1 (same page, positions destroyed) is the cleaner locality")
    emit("  test and is printed beside.  The Latin reference has only 3 held-out pages (interval coarse).")
    (RUNS / "cells.json").write_text(json.dumps(dict(
        summaries={lab: dict(E=S["E"], pages=S["pages"], tokens=S["tokens"], end_share=S["end_share"],
                             null_end_share=S["null_end_share"], rates=S["rates"],
                             ratios={f"{k} vs {m}": list(v) for (m, k), v in S["rt"].items()}) for lab, S in summaries.items()},
        rows=allrows, cminus=info, verdict=verdict), indent=1, default=float), encoding="utf-8", newline="\n")
    emit("")
    emit(f"date end: {clock()}")
    emit(f"elapsed: {time.time() - T_START:.1f} s")
    emit(f"paths: {OUT}, {RUNS / 'cells.json'}, {RUNS}/cminus_<T>_cores.json")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--fixture" in sys.argv:
        sys.exit(0 if fixture() else 1)
    main()
