"""s63 -- Rare-Core Boundary-Bleed, Comma-Juncture & Density-Matched Parent Investigation.

PRE-REGISTERED (frozen in s63_rare_core_boundary_and_subglyph.prereg.sha256 BEFORE running on real data).

SCIENTIFIC OBJECTIVE (s63):
Following results_s59.txt (where Voynich showed no local 15-token or line-above edit-1 parent excess over within-page
shuffle N1: WV vs N1 = 1.02 / 1.01 / 0.99, while 91.1%-91.7% of all edit-1 core parents were end-glyph-only edits,
and the negative control C- failed on RF1b under N3 at 1.08 [1.03, 1.12] due to unmatched core shape-neighborhood
density), this script investigates across ZL3b, RF1b, and IT2a (166 -> 41 page split, g1_edge_joint.split_names,
SlotSegmenter fitted strictly on the 166 training pages):

1. Part 1 -- Exact Anatomical Taxonomy of Held-Out Rare & Unseen Cores (166 -> 41 Split):
   Classifies (a) first-on-page rare cores (~1,893 events, excluding top-20 training cores, matching s59) and
   (b) strictly unseen held-out cores (training count 0) into 5 structural categories (both mutually exclusive
   waterfall B1->B2->B3->B4->B5 and marginal overlapping shares), compared against a random character-shuffled
   core baseline, s59 C-, and s57 C+:
     - B1 (Affix-Core Boundary Shift / Greedy Segmentation Bleed): full word w = P + C + S re-parses as P' + C' + S'
       where C' is a higher-frequency attested training core and P', S' are training prefix/suffix candidates, OR
       1 boundary unit (o, y, d, l, r, s, k, t, e, ch, sh, a, i, n) shifts across P|C or C|S to yield C'.
     - B2 (Compound Core = Core_A + Core_B): C = C1 + C2 is the exact concatenation of two attested training cores
       (|C1| >= 2, |C2| >= 2; with |C1| >= 1, |C2| >= 1 also reported beside).
     - B3 (Internal Sub-Glyph Allomorphy: Gallows/Bench/Minim Swap): C differs from a higher-frequency attested
       training core by a single paleographic/allomorphic alternation (k<->t, p<->f, ch<->sh, ckh<->cth, cph<->cfh,
       e<->ee, i<->ii<->iii, a<->o, l<->r).
     - B4 (Other Edit-1 from Training Core): any other 1-char edit from a higher-frequency training core (broken
       down into end-glyph-only vs internal edit-1).
     - B5 (Edit >= 2 Distal / Novel Root): at edit distance >= 2 from every training core and not B1-B3.

2. Part 2 -- Repair of s59's N3 Control: Neighborhood-Density-Matched Null (N3_dense) + Page-Level (N1 vs N2)
   Decomposition:
   Measures training edit-1 neighborhood degree deg_all(c), deg_top20(c), deg_rare(c), and token-weighted degree
   wdeg(c) for real, C-, C+, and uniform rare training types (N3). Constructs N3_dense matching BOTH length |c| AND
   training edit-1 neighborhood density (deg_top20, wdeg, deg_all). Scores real, C-, and C+ across ZL3b, RF1b, IT2a
   on WV vs N3_dense, WV vs N1, N1 vs N2, and the 4-factor multiplicative decomposition of real/N3.

3. Part 3 -- Held-Out Cross-Entropy Bake-Off on Unseen Cores (166 -> 41):
   Compares held-out cross-entropy (bits/core and bits/char, properly normalized over unseen cores c not in TrainCores)
   of 4 generative core-birth models fitted strictly on the 166 training pages (via leave-singleton-out on training):
     - M_char2: Stationary core character Witten-Bell model fitted on training core types (renormalized over unseen),
     - M_bleed_compound: Mixture of M_char2 + boundary-bleed + compound (C1+C2) + sub-glyph allomorphy model,
     - M_page_mut: Local within-page 15-token + line-above edit-1 mutation model (s57 kernel),
     - M_shuf_null: Position-shuffled within-page edit-1 model (N1).

Run:    python -I s63_rare_core_boundary_and_subglyph.py
Writes: results_s63.txt (only).
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import subprocess
import sys
import time
from collections import Counter, OrderedDict, defaultdict
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
from scoreboard.metrics_new import CharMarkov, SlotSegmenter  # noqa: E402

SELF = ROOT / "s63_rare_core_boundary_and_subglyph.py"
STUB = ROOT / "s63_rare_core_boundary_and_subglyph.prereg.sha256"
OUT = ROOT / "results_s63.txt"

SEED = 20261017
TOPK = 20
WIN = 15
VPOS = 1
N_NULL = 250
N_BOOT = 500
SUB_FRAC = 0.8
DENSE_K = 15
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
KEYS = ("W", "V", "WV")
NULLS = ("N1", "N2", "N3", "N3_dense")
BOUND_UNITS = ("ch", "sh", "o", "y", "d", "l", "r", "s", "k", "t", "e", "a", "i", "n")
SUBGLYPH_PAIRS = (
    ("k", "t"), ("t", "k"),
    ("p", "f"), ("f", "p"),
    ("ch", "sh"), ("sh", "ch"),
    ("ckh", "cth"), ("cth", "ckh"),
    ("cph", "cfh"), ("cfh", "cph"),
    ("e", "ee"), ("ee", "e"),
    ("i", "ii"), ("ii", "i"),
    ("ii", "iii"), ("iii", "ii"),
    ("i", "iii"), ("iii", "i"),
    ("a", "o"), ("o", "a"),
    ("l", "r"), ("r", "l"),
)

log: list[str] = []
T_START = time.time()


def emit(s: str = "") -> None:
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


def local_modules() -> list[str]:
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
        lines = [[w for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if lines:
            by[str(p["id"])] = (str(p.get("section", "?")), lines)
            if "role" in p:
                role[str(p["id"])] = p["role"]
    return by, role


# ======================================================================= edit-distance & subglyph helpers
def variants(c: str, alph: list[str]) -> set[str]:
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


def subglyph_variants(c: str) -> set[str]:
    """All strings differing from c by a single Voynich paleographic/allomorphic alternation."""
    out = set()
    for a, b in SUBGLYPH_PAIRS:
        la = len(a)
        start = 0
        while True:
            idx = c.find(a, start)
            if idx == -1:
                break
            # For e<->ee or i<->ii<->iii, avoid redundant overlapping matches that change >len(b)-len(a)
            cand = c[:idx] + b + c[idx + la:]
            if cand and cand != c:
                out.add(cand)
            start = idx + 1
    return out


def end_only(a: str, b: str) -> bool:
    """a, b at Levenshtein distance 1: True if the edit can be placed at the first or last glyph."""
    if len(a) == len(b):
        d = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return len(d) == 1 and d[0] in (0, len(a) - 1)
    lo, sh = (a, b) if len(a) > len(b) else (b, a)
    return lo[1:] == sh or lo[:-1] == sh


# ======================================================================= Part 1: Anatomical Taxonomy
class CoreTaxonomy:
    """Classifies (word, prefix, core, suffix) into B1..B5 relative to training cores & segmenter."""

    def __init__(self, seg: SlotSegmenter, tr_cores: Counter, top20: set[str]):
        self.seg = seg
        self.tr_cores = tr_cores
        self.top20 = top20
        self.tr_set = set(tr_cores.keys())
        self.alph = sorted(set(ch for c in self.tr_set for ch in c))
        self.pre_strict = set(seg.prefixes) | {""}
        self.suf_strict = set(seg.suffixes) | {""}
        self.pre_cand = set(seg.prefix_stats.keys()) | self.pre_strict
        self.suf_cand = set(seg.suffix_stats.keys()) | self.suf_strict

    def valid_parent(self, c: str, cp: str, strict_freq: bool = True) -> bool:
        if cp == c or not cp or cp not in self.tr_set:
            return False
        if not strict_freq:
            return True
        tc = self.tr_cores.get(c, 0)
        return self.tr_cores[cp] > tc or tc == 0

    def classify_one(self, w: str, p: str, c: str, s: str) -> dict[str, bool]:
        # B1a: Full-word re-parse w = P' + C' + S' with (P', S') != (P, S)
        b1_reparse_strict = False
        b1_reparse_cand = False
        Lw = len(w)
        for lp in range(0, min(4, Lw)):
            pp = w[:lp]
            if pp not in self.pre_cand:
                continue
            for ls in range(0, min(4, Lw - lp)):
                ss = w[Lw - ls:] if ls > 0 else ""
                if ss not in self.suf_cand:
                    continue
                if pp == p and ss == s:
                    continue
                cp = w[lp:Lw - ls]
                if self.valid_parent(c, cp):
                    b1_reparse_cand = True
                    if pp in self.pre_strict and ss in self.suf_strict:
                        b1_reparse_strict = True

        # B1b: 1-unit boundary shift across P|C or C|S (greedy over-strip or under-strip)
        b1_shift = False
        # Over-stripped into P or S:
        for u in BOUND_UNITS:
            lu = len(u)
            if p.endswith(u) and self.valid_parent(c, u + c):
                b1_shift = True
                break
            if s.startswith(u) and self.valid_parent(c, c + u):
                b1_shift = True
                break
            if len(c) > lu and c.startswith(u) and self.valid_parent(c, c[lu:]):
                b1_shift = True
                break
            if len(c) > lu and c.endswith(u) and self.valid_parent(c, c[:-lu]):
                b1_shift = True
                break

        b1 = b1_reparse_cand or b1_shift

        # B2: Compound Core C = C1 + C2
        b2_len2 = False
        b2_any = False
        Lc = len(c)
        tc = self.tr_cores.get(c, 0)
        for k in range(1, Lc):
            c1, c2 = c[:k], c[k:]
            if c1 in self.tr_set and c2 in self.tr_set:
                if self.tr_cores[c1] > tc and self.tr_cores[c2] > tc:
                    b2_any = True
                    if k >= 2 and (Lc - k) >= 2:
                        b2_len2 = True

        # B3: Sub-glyph allomorphy
        sg_cands = subglyph_variants(c)
        b3 = any(self.valid_parent(c, cp) for cp in sg_cands)

        # Edit-1 from training core
        ed1_cands = [cp for cp in variants(c, self.alph) if self.valid_parent(c, cp)]
        any_ed1 = len(ed1_cands) > 0
        ed1_end = any(end_only(c, cp) for cp in ed1_cands)
        ed1_int = any(not end_only(c, cp) for cp in ed1_cands)

        # Waterfall (mutually exclusive: B1 -> B2 -> B3 -> B4 -> B5)
        w_b1 = b1
        w_b2 = (not w_b1) and b2_len2
        w_b3 = (not w_b1) and (not w_b2) and b3
        w_b4 = (not w_b1) and (not w_b2) and (not w_b3) and any_ed1
        w_b5 = not (w_b1 or w_b2 or w_b3 or w_b4)

        return dict(
            w_b1=w_b1, w_b2=w_b2, w_b3=w_b3, w_b4=w_b4, w_b5=w_b5,
            b1=b1, b1_reparse_strict=b1_reparse_strict, b1_reparse_cand=b1_reparse_cand,
            b1_shift=b1_shift, b2_len2=b2_len2, b2_any=b2_any, b3=b3,
            any_ed1=any_ed1, ed1_end=ed1_end, ed1_int=ed1_int,
        )

    def summarize_cohort(self, items: list[tuple[str, str, str, str]]) -> dict:
        """items: list of (w, p, c, s)."""
        n = len(items)
        if n == 0:
            return dict(n=0)
        cache: dict[tuple[str, str, str, str], dict[str, bool]] = {}
        counts = Counter()
        for it in items:
            res = cache.get(it)
            if res is None:
                res = cache[it] = self.classify_one(*it)
            for k, v in res.items():
                if v:
                    counts[k] += 1
        return {k: counts[k] / n for k in (
            "w_b1", "w_b2", "w_b3", "w_b4", "w_b5",
            "b1", "b1_reparse_strict", "b1_reparse_cand", "b1_shift",
            "b2_len2", "b2_any", "b3", "any_ed1", "ed1_end", "ed1_int"
        )} | {"n": n, "counts": dict(counts)}


def make_shuffled_core_items(
    items: list[tuple[str, str, str, str]],
    tr_cores: Counter,
    top20: set[str],
    seed: int,
) -> list[tuple[str, str, str, str]]:
    """Random character-shuffled baseline: for each (w, p, c, s), generate a random core c_shuf of the same
    length |c| by permuting characters (or drawing from training core character unigram when permutation == c
    or lies in top20) and re-wrapping p + c_shuf + s."""
    rng = random.Random(seed)
    gl_cnt = Counter()
    for core, cnt in tr_cores.items():
        for ch in core:
            gl_cnt[ch] += cnt
    alph_w = sorted(gl_cnt.keys())
    cum_w = np.cumsum([gl_cnt[ch] for ch in alph_w]).tolist()

    out = []
    for _w, p, c, s in items:
        L = len(c)
        chars = list(c)
        c_new = c
        for _ in range(15):
            if L >= 3 and len(set(chars)) > 1:
                rng.shuffle(chars)
                cand = "".join(chars)
            else:
                cand = "".join(rng.choices(alph_w, cum_weights=cum_w, k=L))
            if cand != c and cand not in top20:
                c_new = cand
                break
        if c_new == c or c_new in top20:
            for _ in range(15):
                cand = "".join(rng.choices(alph_w, cum_weights=cum_w, k=L))
                if cand not in top20:
                    c_new = cand
                    break
        out.append((p + c_new + s, p, c_new, s))
    return out


# ======================================================================= Part 2: Fast Integer-ID Scorer & N3_dense
class PageObj:
    def __init__(self, pid: str, section: str, lines: list[list[str]], word_lines: list[list[str]] | None = None):
        self.id = pid
        self.section = section
        self.lines = lines
        self.word_lines = word_lines
        self.stream = [c for ln in lines for c in ln]
        self.word_stream = [w for ln in word_lines for w in ln] if word_lines else None
        self.pos = [(li, j) for li, ln in enumerate(lines) for j in range(len(ln))]
        self.lens = [len(ln) for ln in lines]
        self.first: dict[str, int] = {}
        for t, c in enumerate(self.stream):
            self.first.setdefault(c, t)


def build_cminus(X: dict, seed: int) -> tuple[dict, dict]:
    """Exact s59 build_cminus implementation on X."""
    rare_types = sorted(X["rare"])
    rng = random.Random(seed)
    lst = list(rare_types)
    rng.shuffle(lst)
    ptr, refills = 0, 0
    new_pages = []
    for p in X["pages"]:
        mapping, seen_o, seen_n = {}, set(), set()
        lines = []
        for ln in p.lines:
            nl = []
            for c in ln:
                if c in mapping:
                    x = mapping[c]
                elif c not in X["top"] and c not in seen_o:
                    while True:
                        if ptr >= len(lst):
                            nxt = list(rare_types)
                            rng.shuffle(nxt)
                            lst += nxt
                            refills += 1
                        x = lst[ptr]
                        ptr += 1
                        if x not in seen_n and x not in X["top"]:
                            break
                    mapping[c] = x
                else:
                    x = c
                seen_o.add(c)
                seen_n.add(x)
                nl.append(x)
            lines.append(nl)
        new_pages.append(PageObj(p.id, p.section, lines, p.word_lines))
    Y = prepare_from_cores(X["name"] + " C-", X["tr_cores"], X["top"], new_pages)
    return Y, dict(list_used=ptr, refills=refills, list_len=len(rare_types))


def prepare_from_cores(name: str, tr_cores: Counter, top: set[str], pages: list[PageObj]) -> dict:
    rare = {c: n for c, n in tr_cores.items() if c not in top}
    tr_vocab = set(tr_cores.keys())
    te_vocab = set(c for p in pages for c in p.stream)
    all_vocab = sorted(tr_vocab | te_vocab)
    c2i = {c: idx for idx, c in enumerate(all_vocab)}
    alph = sorted(set(ch for c in all_vocab for ch in c))

    # Precompute edit-1 neighbors on all_vocab and training degree metrics for every core
    neigh_str: dict[str, set[str]] = {}
    neigh_id: list[frozenset[int]] = [frozenset()] * len(all_vocab)
    deg_all: dict[str, int] = {}
    deg_top: dict[str, int] = {}
    deg_rare: dict[str, int] = {}
    wdeg_all: dict[str, int] = {}
    wdeg_top: dict[str, int] = {}

    all_set = set(all_vocab)
    for idx, c in enumerate(all_vocab):
        vs = variants(c, alph) & all_set
        neigh_str[c] = vs
        neigh_id[idx] = frozenset(c2i[x] for x in vs)
        tr_nb = vs & tr_vocab
        top_nb = vs & top
        rare_nb = tr_nb - top
        deg_all[c] = len(tr_nb)
        deg_top[c] = len(top_nb)
        deg_rare[c] = len(rare_nb)
        wdeg_all[c] = sum(tr_cores[x] for x in tr_nb)
        wdeg_top[c] = sum(tr_cores[x] for x in top_nb)

    # Length pools for N3
    pool_len: dict[int, list[str]] = defaultdict(list)
    for c in sorted(rare.keys()):
        pool_len[len(c)].append(c)

    # Balanced expected window-hit density score strictly from training counts:
    # rho(c) = wdeg_top(c) / N_tr + 0.5 * deg_rare(c) / max(1, len(rare))
    n_tr_tok = max(1, sum(tr_cores.values()))
    n_rare_typ = max(1, len(rare))
    rho_score: dict[str, float] = {
        c: (wdeg_top[c] / n_tr_tok) + 0.5 * (deg_rare[c] / n_rare_typ)
        for c in all_vocab
    }

    pool_dense_sorted: dict[int, list[str]] = {}
    for L, cands in pool_len.items():
        pool_dense_sorted[L] = sorted(cands, key=lambda c: (deg_top[c], rho_score[c], deg_all[c], c))

    dense_cand_cache: dict[str, list[int]] = {}

    def get_dense_cands(c: str) -> list[int]:
        res = dense_cand_cache.get(c)
        if res is not None:
            return res
        L = len(c)
        if L not in pool_len:
            L = min(pool_len.keys(), key=lambda k: (abs(k - L), k))
        cands = [x for x in pool_dense_sorted[L] if x != c]
        if not cands:
            cands = pool_dense_sorted[L]
        if len(cands) <= DENSE_K:
            res = [c2i[x] for x in cands]
            dense_cand_cache[c] = res
            return res
        dt = deg_top.get(c, 0)
        rc = rho_score.get(c, 0.0)
        da = deg_all.get(c, 0)
        same_dt = [x for x in cands if deg_top[x] == dt]
        pool_use = same_dt if len(same_dt) >= DENSE_K else cands
        ranked = sorted(
            pool_use,
            key=lambda x: (
                abs(deg_top[x] - dt) * 10.0,
                abs(rho_score[x] - rc) + 0.002 * abs(deg_all[x] - da),
                abs(deg_all[x] - da),
                x,
            ),
        )[:DENSE_K]
        res = [c2i[x] for x in ranked]
        dense_cand_cache[c] = res
        return res

    return dict(
        name=name,
        tr_cores=tr_cores,
        top=top,
        top_ids=frozenset(c2i[x] for x in top if x in c2i),
        rare=rare,
        pages=pages,
        all_vocab=all_vocab,
        c2i=c2i,
        neigh_id=neigh_id,
        deg_all=deg_all,
        deg_top=deg_top,
        deg_rare=deg_rare,
        wdeg_all=wdeg_all,
        wdeg_top=wdeg_top,
        pool_len=dict(pool_len),
        pool_len_ids={L: [c2i[x] for x in cs] for L, cs in pool_len.items()},
        get_dense_cands=get_dense_cands,
    )


def pick_len(pool: dict[int, list], L: int) -> int:
    if L in pool:
        return L
    return min(pool.keys(), key=lambda k: (abs(k - L), k))


def score_id_lines(
    id_lines: list[list[int]],
    top_ids: frozenset[int],
    neigh_id: list[frozenset[int]],
    all_vocab: list[str] | None = None,
    want_end: bool = False,
) -> tuple[dict[str, int], list[tuple[int, int, int, int]]]:
    stream = [cid for ln in id_lines for cid in ln]
    pos = [(li, j) for li, ln in enumerate(id_lines) for j in range(len(ln))]
    seen: set[int] = set()
    ev: list[tuple[int, int, int, int]] = []
    for t, cid in enumerate(stream):
        if cid not in top_ids and cid not in seen:
            ev.append((t, pos[t][0], pos[t][1], cid))
        seen.add(cid)
    W_cnt = 0
    V_cnt = 0
    WV_cnt = 0
    END_cnt = 0
    for t, li, j, cid in ev:
        nb = neigh_id[cid]
        Wc = stream[max(0, t - WIN):t]
        Vc = id_lines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else ()
        w = any(x in nb for x in Wc)
        v = any(x in nb for x in Vc)
        wv = w or v
        W_cnt += w
        V_cnt += v
        WV_cnt += wv
        if want_end and wv and all_vocab is not None:
            cs = all_vocab[cid]
            if any(end_only(cs, all_vocab[x]) for x in list(Wc) + list(Vc) if x in nb):
                END_cnt += 1
    return dict(E=len(ev), W=W_cnt, V=V_cnt, WV=WV_cnt, END=END_cnt), ev


def analyse_fast(X: dict, seed: int) -> dict:
    top_ids = X["top_ids"]
    neigh_id = X["neigh_id"]
    c2i = X["c2i"]
    all_vocab = X["all_vocab"]
    pages: list[PageObj] = X["pages"]
    rng = random.Random(seed)

    by_sec: dict[str, list[int]] = defaultdict(list)
    id_pages: list[list[list[int]]] = []
    id_streams: list[list[int]] = []
    id_firsts: list[dict[int, int]] = []
    for i, p in enumerate(pages):
        by_sec[p.section].append(i)
        ilines = [[c2i[c] for c in ln] for ln in p.lines]
        istream = [c2i[c] for c in p.stream]
        ifirst: dict[int, int] = {}
        for t, cid in enumerate(istream):
            ifirst.setdefault(cid, t)
        id_pages.append(ilines)
        id_streams.append(istream)
        id_firsts.append(ifirst)

    rows = []
    real_end = 0
    real_wv = 0
    deg_stats_events = []
    deg_stats_n3 = []
    deg_stats_n3d = []

    for i, p in enumerate(pages):
        ilines = id_pages[i]
        istream = id_streams[i]
        ifirst = id_firsts[i]
        r, ev = score_id_lines(ilines, top_ids, neigh_id, all_vocab, want_end=True)
        real_end += r["END"]
        real_wv += r["WV"]
        row = dict(
            id=p.id,
            section=p.section,
            E=r["E"],
            real={k: r[k] for k in KEYS},
            null={m: {k: 0.0 for k in KEYS} for m in NULLS},
        )

        # Track degree of event cores
        for _t, _li, _j, cid in ev:
            cs = all_vocab[cid]
            deg_stats_events.append((
                len(cs),
                X["deg_all"][cs],
                X["deg_top"][cs],
                X["deg_rare"][cs],
                X["wdeg_all"][cs],
            ))

        # N1: within-page shuffle
        acc = {k: 0 for k in KEYS}
        shuf_stream = list(istream)
        for _ in range(N_NULL):
            rng.shuffle(shuf_stream)
            slines, a = [], 0
            for L in p.lens:
                slines.append(shuf_stream[a:a + L])
                a += L
            rr, _ = score_id_lines(slines, top_ids, neigh_id)
            for k in KEYS:
                acc[k] += rr[k]
        row["null"]["N1"] = {k: acc[k] / N_NULL for k in KEYS}

        # N2: cross-page window in same section
        others = [k for k in by_sec[p.section] if k != i]
        if not others:
            others = [k for k in range(len(pages)) if k != i]
        acc = {k: 0 for k in KEYS}
        for _ in range(N_NULL):
            for t, li, j, cid in ev:
                nb = neigh_id[cid]
                oi = rng.choice(others)
                ostream = id_streams[oi]
                olines = id_pages[oi]
                k_idx = min(t, len(ostream))
                Wc = ostream[max(0, k_idx - WIN):k_idx]
                if li >= 1:
                    ol = olines[min(li - 1, len(olines) - 1)]
                    Vc = ol[max(0, j - VPOS):j + VPOS + 1]
                else:
                    Vc = ()
                w = any(x in nb for x in Wc)
                v = any(x in nb for x in Vc)
                acc["W"] += w
                acc["V"] += v
                acc["WV"] += (w or v)
        row["null"]["N2"] = {k: acc[k] / N_NULL for k in KEYS}

        # Precompute window neighbor union sets for N3 and N3_dense
        acc_n3 = {k: 0.0 for k in KEYS}
        acc_n3d = {k: 0.0 for k in KEYS}
        for t, li, j, cid in ev:
            cs = all_vocab[cid]
            Wc = istream[max(0, t - WIN):t]
            Vc = ilines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else ()
            hit_W: set[int] = set()
            for x in Wc:
                hit_W.update(neigh_id[x])
            hit_V: set[int] = set()
            for x in Vc:
                hit_V.update(neigh_id[x])
            hit_WV = hit_W | hit_V

            # N3: length-matched rare training core
            L = pick_len(X["pool_len_ids"], len(cs))
            cands_n3 = [x for x in X["pool_len_ids"][L] if ifirst.get(x, 10**9) >= t]
            if not cands_n3:
                cands_n3 = X["pool_len_ids"][L]
            n_c3 = len(cands_n3)
            acc_n3["W"] += sum(1 for x in cands_n3 if x in hit_W) / n_c3
            acc_n3["V"] += sum(1 for x in cands_n3 if x in hit_V) / n_c3
            acc_n3["WV"] += sum(1 for x in cands_n3 if x in hit_WV) / n_c3

            # Record mean N3 degree for this event
            sample_n3 = all_vocab[rng.choice(cands_n3)]
            deg_stats_n3.append((
                len(sample_n3),
                X["deg_all"][sample_n3],
                X["deg_top"][sample_n3],
                X["deg_rare"][sample_n3],
                X["wdeg_all"][sample_n3],
            ))

            # N3_dense: length + neighborhood-density matched rare training core
            raw_dense = X["get_dense_cands"](cs)
            cands_d = [x for x in raw_dense if ifirst.get(x, 10**9) >= t]
            if not cands_d:
                cands_d = raw_dense
            n_cd = len(cands_d)
            acc_n3d["W"] += sum(1 for x in cands_d if x in hit_W) / n_cd
            acc_n3d["V"] += sum(1 for x in cands_d if x in hit_V) / n_cd
            acc_n3d["WV"] += sum(1 for x in cands_d if x in hit_WV) / n_cd

            sample_n3d = all_vocab[rng.choice(cands_d)]
            deg_stats_n3d.append((
                len(sample_n3d),
                X["deg_all"][sample_n3d],
                X["deg_top"][sample_n3d],
                X["deg_rare"][sample_n3d],
                X["wdeg_all"][sample_n3d],
            ))

        row["null"]["N3"] = acc_n3
        row["null"]["N3_dense"] = acc_n3d
        rows.append(row)

    def avg_deg(lst):
        if not lst:
            return dict(len=0.0, deg_all=0.0, deg_top=0.0, deg_rare=0.0, wdeg_all=0.0)
        arr = np.array(lst, dtype=float)
        return dict(
            len=float(arr[:, 0].mean()),
            deg_all=float(arr[:, 1].mean()),
            deg_top=float(arr[:, 2].mean()),
            deg_rare=float(arr[:, 3].mean()),
            wdeg_all=float(arr[:, 4].mean()),
        )

    return dict(
        name=X["name"],
        rows=rows,
        real_end=real_end,
        real_wv=real_wv,
        tokens=sum(len(p.stream) for p in pages),
        deg_events=avg_deg(deg_stats_events),
        deg_n3=avg_deg(deg_stats_n3),
        deg_n3d=avg_deg(deg_stats_n3d),
    )


def summarize_part2(label: str, res_list: list[dict], seed: int) -> dict:
    rows = [r for res in res_list for r in res["rows"]]
    n = len(rows)
    real = {k: np.array([r["real"][k] for r in rows], float) for k in KEYS}
    nul = {(m, k): np.array([r["null"][m][k] for r in rows], float) for m in NULLS for k in KEYS}

    rng = np.random.default_rng(seed)
    kk = max(1, int(round(SUB_FRAC * n)))
    idxs = [rng.choice(n, size=kk, replace=False) for _ in range(N_BOOT)]

    rt = {}
    for (m, k), a in nul.items():
        pt = float(real[k].sum() / a.sum()) if a.sum() > 0 else float("nan")
        dr = np.array([real[k][ix].sum() / a[ix].sum() if a[ix].sum() > 0 else np.nan for ix in idxs])
        rt[(m, k)] = (pt, float(np.nanpercentile(dr, 2.5)), float(np.nanpercentile(dr, 97.5)))

    # Also compute N1/N2, N2/N3_dense, and N3_dense/N3 decomposition ratios for WV and W
    decomp = {}
    for k in KEYS:
        for num_m, den_m, dname in (
            ("N1", "N2", "N1/N2"),
            ("N2", "N3_dense", "N2/N3_dense"),
            ("N3_dense", "N3", "N3_dense/N3"),
        ):
            a_num = nul[(num_m, k)]
            a_den = nul[(den_m, k)]
            pt = float(a_num.sum() / a_den.sum()) if a_den.sum() > 0 else float("nan")
            dr = np.array([a_num[ix].sum() / a_den[ix].sum() if a_den[ix].sum() > 0 else np.nan for ix in idxs])
            decomp[(dname, k)] = (pt, float(np.nanpercentile(dr, 2.5)), float(np.nanpercentile(dr, 97.5)))

    E = sum(r["E"] for r in rows)
    rates = {"real": {k: float(real[k].sum() / E) if E else float("nan") for k in KEYS}}
    for m in NULLS:
        rates[m] = {k: float(nul[(m, k)].sum() / E) if E else float("nan") for k in KEYS}

    rend = sum(res["real_end"] for res in res_list)
    rwv = sum(res["real_wv"] for res in res_list)

    def pool_deg(key):
        vals = [res[key] for res in res_list]
        return {k: float(np.mean([v[k] for v in vals])) for k in vals[0]}

    return dict(
        label=label,
        rt=rt,
        decomp=decomp,
        rates=rates,
        E=E,
        pages=n,
        tokens=sum(res["tokens"] for res in res_list),
        end_share=rend / rwv if rwv else float("nan"),
        end_n=(rend, rwv),
        deg_events=pool_deg("deg_events"),
        deg_n3=pool_deg("deg_n3"),
        deg_n3d=pool_deg("deg_n3d"),
    )


# ======================================================================= Part 3: Unseen-Core Generative Bake-Off
def build_structural_unseen_dists(
    base_cores: Counter,
    forbidden_cores: set[str],
    alph: list[str],
    seg: SlotSegmenter,
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """Builds three proper probability distributions over unseen cores c not in forbidden_cores,
    using only base_cores and SlotSegmenter boundary statistics from the training pages:
      1. P_bleed(c): 1-unit boundary shift (attach/strip SlotSegmenter prefix/suffix candidates or BOUND_UNITS)
      2. P_compound(c): concatenation v1 + v2 of top-300 base_cores (both >=2+>=2 and 1+>=2 stem compounds)
      3. P_subglyph(c): single sub-glyph allomorphic swap from v in base_cores
    Each dictionary sums to 1.0 over its support (strictly disjoint from forbidden_cores)."""
    bleed_w: Counter = Counter()
    sub_w: Counter = Counter()

    pre_weights = {u: sh for u, (sh, _h) in seg.prefix_stats.items()}
    suf_weights = {u: sh for u, (sh, _h) in seg.suffix_stats.items()}
    for u in BOUND_UNITS:
        pre_weights.setdefault(u, 0.005)
        suf_weights.setdefault(u, 0.005)

    for v, cnt in base_cores.items():
        w = float(cnt)
        # Under-strip / over-strip at prefix boundary
        for u, pu in pre_weights.items():
            lu = len(u)
            c_add = u + v
            if c_add not in forbidden_cores:
                bleed_w[c_add] += w * pu
            if len(v) > lu and v.startswith(u):
                c_rem = v[lu:]
                if c_rem and c_rem not in forbidden_cores:
                    bleed_w[c_rem] += w * pu * 2.0
        # Under-strip / over-strip at suffix boundary
        for u, su in suf_weights.items():
            lu = len(u)
            c_add = v + u
            if c_add not in forbidden_cores:
                bleed_w[c_add] += w * su
            if len(v) > lu and v.endswith(u):
                c_rem = v[:-lu]
                if c_rem and c_rem not in forbidden_cores:
                    bleed_w[c_rem] += w * su * 2.0

        # Sub-glyph allomorphy candidates from v
        for c_sg in subglyph_variants(v):
            if c_sg not in forbidden_cores:
                sub_w[c_sg] += w

    # Compound candidates C1 + C2 from top-350 base_cores
    comp_w: Counter = Counter()
    top_base = base_cores.most_common(350)
    for v1, n1 in top_base:
        for v2, n2 in top_base:
            cc = v1 + v2
            if 3 <= len(cc) <= 12 and cc not in forbidden_cores:
                bonus = 2.0 if (len(v1) >= 2 and len(v2) >= 2) else 0.5
                comp_w[cc] += bonus * math.sqrt(n1 * n2)

    def norm_dict(cnt: Counter) -> dict[str, float]:
        tot = float(sum(cnt.values()))
        if tot <= 0:
            return {}
        return {k: v / tot for k, v in cnt.items()}

    return norm_dict(bleed_w), norm_dict(comp_w), norm_dict(sub_w)


class RenormCharMarkov:
    """CharMarkov over core types, explicitly renormalized over unseen strings c not in forbidden_cores."""

    def __init__(self, core_types: list[str], forbidden_cores: set[str], order: int = 2):
        self.cm = CharMarkov(core_types, order)
        self.forbidden = forbidden_cores
        seen_mass = sum(2.0 ** self.cm.logp_word(v) for v in forbidden_cores)
        self.rem_mass = max(1e-6, 1.0 - seen_mass)

    def prob_unseen(self, c: str) -> float:
        return (2.0 ** self.cm.logp_word(c)) / self.rem_mass


def window_edit1_unseen_dist(
    Wc: list[str],
    Vc: list[str],
    forbidden_cores: set[str],
    alph: list[str],
    gl_prob: dict[str, float],
    tau: float = 7.0,
    a_line: float = 0.20,
    var_cache: dict[str, dict[str, float]] | None = None,
) -> dict[str, float]:
    """Local within-page edit-1 mutation distribution over unseen cores c not in forbidden_cores,
    following s57's recency kernel over Wc (last 15 tokens) and Vc (line above)."""
    if not Wc and not Vc:
        return {}

    def get_core_muts(u: str) -> dict[str, float]:
        if var_cache is not None and u in var_cache:
            return var_cache[u]
        d: dict[str, float] = {}
        L = len(u)
        # Substitutions
        for i in range(L):
            for g in alph:
                if g != u[i]:
                    cand = u[:i] + g + u[i + 1:]
                    if cand not in forbidden_cores:
                        d[cand] = d.get(cand, 0.0) + gl_prob.get(g, 1e-4) / max(1, L)
        # Insertions
        for i in range(L + 1):
            for g in alph:
                cand = u[:i] + g + u[i:]
                if cand not in forbidden_cores:
                    d[cand] = d.get(cand, 0.0) + gl_prob.get(g, 1e-4) / (L + 1)
        # Deletions
        if L >= 2:
            for i in range(L):
                cand = u[:i] + u[i + 1:]
                if cand and cand not in forbidden_cores:
                    d[cand] = d.get(cand, 0.0) + 1.0 / L
        tot = sum(d.values())
        if tot > 0:
            d = {k: v / tot for k, v in d.items()}
        if var_cache is not None:
            var_cache[u] = d
        return d

    win_weights: Counter = Counter()
    if Wc:
        raw_w = [math.exp(-d / tau) for d in range(len(Wc))]
        tot_w = sum(raw_w)
        scale_w = (1.0 - a_line) if Vc else 1.0
        for d, u in enumerate(reversed(Wc)):
            win_weights[u] += scale_w * (raw_w[d] / tot_w)
    if Vc:
        scale_v = a_line if Wc else 1.0
        for u in Vc:
            win_weights[u] += scale_v / len(Vc)

    out: dict[str, float] = {}
    for u, wu in win_weights.items():
        muts = get_core_muts(u)
        for cand, p_cand in muts.items():
            out[cand] = out.get(cand, 0.0) + wu * p_cand
    tot = sum(out.values())
    if tot <= 0:
        return {}
    return {k: v / tot for k, v in out.items()}


def run_part3_bakeoff(
    label: str,
    tr_pages_cores: list[list[list[str]]],
    te_pages: list[PageObj],
    tr_cores: Counter,
    seg: SlotSegmenter,
    seed: int,
) -> dict:
    """Fits the 4 core-birth models strictly on the 166 training pages (via leave-singleton-out on training)
    and evaluates held-out cross-entropy (bits/core and bits/char) on strictly unseen held-out core tokens."""
    tr_set = set(tr_cores.keys())
    gl_cnt = Counter()
    for c, cnt in tr_cores.items():
        for ch in c:
            gl_cnt[ch] += cnt
    tot_gl = float(sum(gl_cnt.values()))
    alph = sorted(gl_cnt.keys())
    gl_prob = {ch: gl_cnt[ch] / tot_gl for ch in alph}

    # Step 1: Fit mixture weights strictly on training singletons (count == 1 in tr_cores) vs base_cores (count >= 2)
    base_cores = Counter({c: n for c, n in tr_cores.items() if n >= 2})
    base_set = set(base_cores.keys())
    singletons = [c for c, n in tr_cores.items() if n == 1]

    cm_fit = RenormCharMarkov(sorted(base_set), base_set, order=2)
    p_bleed_fit, p_comp_fit, p_sub_fit = build_structural_unseen_dists(base_cores, base_set, alph, seg)

    # Precompute component probabilities on training singletons
    s_p0 = np.array([cm_fit.prob_unseen(c) for c in singletons], dtype=float)
    s_pb = np.array([p_bleed_fit.get(c, 0.0) for c in singletons], dtype=float)
    s_pc = np.array([p_comp_fit.get(c, 0.0) for c in singletons], dtype=float)
    s_ps = np.array([p_sub_fit.get(c, 0.0) for c in singletons], dtype=float)

    best_lam = (0.25, 0.10, 0.02)
    best_bits = float("inf")
    for lb in (0.10, 0.20, 0.30, 0.40, 0.50):
        for lc in (0.05, 0.10, 0.20, 0.30):
            for ls in (0.01, 0.03, 0.06):
                l0 = 1.0 - lb - lc - ls
                if l0 <= 0.15:
                    continue
                pmix = l0 * s_p0 + lb * s_pb + lc * s_pc + ls * s_ps
                bits = float(-np.log2(np.maximum(pmix, 1e-15)).mean())
                if bits < best_bits:
                    best_bits = bits
                    best_lam = (lb, lc, ls)

    # Fit alpha_mut for M_page_mut on training pages' singleton occurrences
    var_cache_fit: dict[str, dict[str, float]] = {}
    sing_set = set(singletons)
    sing_p0_list = []
    sing_pwin_list = []
    for lines in tr_pages_cores[:60]:
        stream = [c for ln in lines for c in ln]
        pos = [(li, j) for li, ln in enumerate(lines) for j in range(len(ln))]
        for t, c in enumerate(stream):
            if c in sing_set:
                li, j = pos[t]
                Wc = stream[max(0, t - WIN):t]
                Vc = lines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else []
                d_win = window_edit1_unseen_dist(Wc, Vc, base_set, alph, gl_prob, var_cache=var_cache_fit)
                sing_p0_list.append(cm_fit.prob_unseen(c))
                sing_pwin_list.append(d_win.get(c, 0.0))

    arr_p0 = np.array(sing_p0_list, dtype=float)
    arr_pw = np.array(sing_pwin_list, dtype=float)
    best_alpha = 0.10
    best_abits = float("inf")
    for a_cand in (0.01, 0.03, 0.05, 0.10, 0.15, 0.25, 0.35):
        pm = (1.0 - a_cand) * arr_p0 + a_cand * arr_pw
        b = float(-np.log2(np.maximum(pm, 1e-15)).mean())
        if b < best_abits:
            best_abits = b
            best_alpha = a_cand

    # Step 2: Build full training models on all 166 training pages (tr_cores, tr_set)
    cm2_full = RenormCharMarkov(sorted(tr_set), tr_set, order=2)
    cm3_full = RenormCharMarkov(sorted(tr_set), tr_set, order=3)
    p_bleed_full, p_comp_full, p_sub_full = build_structural_unseen_dists(tr_cores, tr_set, alph, seg)
    var_cache_full: dict[str, dict[str, float]] = {}

    lb, lc, ls = best_lam
    l0 = 1.0 - lb - lc - ls

    # Step 3: Score strictly unseen core occurrences on the 41 held-out pages
    rng = random.Random(seed)
    n_unseen_tok = 0
    unseen_types: set[str] = set()
    tot_chars = 0
    bits_acc = {
        "M_char2": 0.0,
        "M_char3": 0.0,
        "M_bleed_compound": 0.0,
        "M_page_mut": 0.0,
        "M_shuf_null": 0.0,
    }
    page_bits: list[dict[str, float]] = []

    for p in te_pages:
        p_acc = {k: 0.0 for k in bits_acc}
        p_n = 0
        # Prepare 5 shuffled streams of this page for M_shuf_null (N1)
        shuf_streams = []
        shuf_lines_list = []
        for _ in range(5):
            ss = list(p.stream)
            rng.shuffle(ss)
            slines, a = [], 0
            for L in p.lens:
                slines.append(ss[a:a + L])
                a += L
            shuf_streams.append(ss)
            shuf_lines_list.append(slines)

        for t, c in enumerate(p.stream):
            if c in tr_set:
                continue
            li, j = p.pos[t]
            n_unseen_tok += 1
            p_n += 1
            unseen_types.add(c)
            tot_chars += len(c) + 1  # +1 for '$' end-of-core symbol

            p0 = cm2_full.prob_unseen(c)
            p3 = cm3_full.prob_unseen(c)
            p_bc = (
                l0 * p0
                + lb * p_bleed_full.get(c, 0.0)
                + lc * p_comp_full.get(c, 0.0)
                + ls * p_sub_full.get(c, 0.0)
            )

            Wc = p.stream[max(0, t - WIN):t]
            Vc = p.lines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else []
            d_win = window_edit1_unseen_dist(Wc, Vc, tr_set, alph, gl_prob, var_cache=var_cache_full)
            p_mut = (1.0 - best_alpha) * p0 + best_alpha * d_win.get(c, 0.0)

            # Position-shuffled within-page window (N1)
            pw_shuf = 0.0
            for ss, slines in zip(shuf_streams, shuf_lines_list):
                W_s = ss[max(0, t - WIN):t]
                V_s = slines[li - 1][max(0, j - VPOS):j + VPOS + 1] if li >= 1 else []
                d_s = window_edit1_unseen_dist(W_s, V_s, tr_set, alph, gl_prob, var_cache=var_cache_full)
                pw_shuf += d_s.get(c, 0.0)
            pw_shuf /= len(shuf_streams)
            p_shuf = (1.0 - best_alpha) * p0 + best_alpha * pw_shuf

            b_c2 = -math.log2(max(p0, 1e-15))
            b_c3 = -math.log2(max(p3, 1e-15))
            b_bc = -math.log2(max(p_bc, 1e-15))
            b_pm = -math.log2(max(p_mut, 1e-15))
            b_sn = -math.log2(max(p_shuf, 1e-15))

            bits_acc["M_char2"] += b_c2
            bits_acc["M_char3"] += b_c3
            bits_acc["M_bleed_compound"] += b_bc
            bits_acc["M_page_mut"] += b_pm
            bits_acc["M_shuf_null"] += b_sn

            p_acc["M_char2"] += b_c2
            p_acc["M_char3"] += b_c3
            p_acc["M_bleed_compound"] += b_bc
            p_acc["M_page_mut"] += b_pm
            p_acc["M_shuf_null"] += b_sn

        if p_n > 0:
            page_bits.append(p_acc | {"n": p_n})

    # Page-subsample 95% interval on (M_bleed_compound - M_char2) and (M_page_mut - M_shuf_null)
    n_pg = len(page_bits)
    kk = max(1, int(round(SUB_FRAC * n_pg)))
    brng = np.random.default_rng(seed + 99)
    idxs = [brng.choice(n_pg, size=kk, replace=False) for _ in range(N_BOOT)]

    def boot_diff(m_a: str, m_b: str) -> tuple[float, float, float]:
        pt = (bits_acc[m_a] - bits_acc[m_b]) / max(1, n_unseen_tok)
        vals = []
        for ix in idxs:
            num = sum(page_bits[i][m_a] - page_bits[i][m_b] for i in ix)
            den = sum(page_bits[i]["n"] for i in ix)
            vals.append(num / max(1, den))
        return pt, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))

    return dict(
        label=label,
        n_tok=n_unseen_tok,
        n_types=len(unseen_types),
        tot_chars=tot_chars,
        lam=best_lam,
        alpha_mut=best_alpha,
        bits_per_core={k: v / max(1, n_unseen_tok) for k, v in bits_acc.items()},
        bits_per_char={k: v / max(1, tot_chars) for k, v in bits_acc.items()},
        diff_bc_vs_c2=boot_diff("M_bleed_compound", "M_char2"),
        diff_mut_vs_shuf=boot_diff("M_page_mut", "M_shuf_null"),
    )


# ======================================================================= main
def main() -> None:
    emit("s63 -- Rare-Core Boundary-Bleed, Comma-Juncture & Density-Matched Parent Investigation")
    emit(f"date: {clock()}")
    emit(f"sha256 s63_rare_core_boundary_and_subglyph.py: {sha256(SELF)}")
    if STUB.exists():
        emit(f"sha256 s63_rare_core_boundary_and_subglyph.prereg.sha256: {sha256(STUB)}")
    emit(f"stub_match: {stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    emit(
        f"numpy {np.__version__}; python {sys.version.split()[0]} {'-I' if sys.flags.isolated else ''}; "
        f"top-{TOPK} from training cores; W = preceding {WIN} tokens; V = line above j-{VPOS}..j+{VPOS}; "
        f"N1/N2 {N_NULL} draws; N3/N3_dense exact pool expectation (K={DENSE_K} nearest density neighbors); "
        f"interval {N_BOOT} draws of {int(SUB_FRAC * 100)}% held-out pages without replacement"
    )
    emit("")

    part1_results = {}
    part2_summaries = {}
    part3_results = {}

    off = 0
    for T, fname in TRANSLITS.items():
        off += 100
        t0 = time.time()
        path = ROOT / "data" / "translit" / f"{fname}.meta.json"
        by, _ = load_meta(path)
        names = list(by)
        tr, te = G1.split_names(OrderedDict((k, v[1]) for k, v in by.items()))
        te_set = set(te)
        tr_set_pages = set(tr)
        tr_ordered = [k for k in names if k in tr_set_pages]
        te_ordered = [k for k in names if k in te_set]

        tr_words = [w for p in tr_ordered for ln in by[p][1] for w in ln]
        seg = SlotSegmenter(tr_words)
        tr_pages_cores = [[[seg.segment(w)[1] for w in ln] for ln in by[p][1]] for p in tr_ordered]
        tr_cores = Counter(c for lines in tr_pages_cores for ln in lines for c in ln)
        top20 = set(c for c, _ in tr_cores.most_common(TOPK))

        te_pages = [
            PageObj(p, by[p][0], [[seg.segment(w)[1] for w in ln] for ln in by[p][1]], by[p][1])
            for p in te_ordered
        ]

        emit(
            f"=== {T} ({path.relative_to(ROOT).as_posix()}, sha256={sha256(path)[:16]}) ===\n"
            f"  pages {len(by)} -> train {len(tr_ordered)} / held-out {len(te_ordered)}; "
            f"SlotSegmenter {len(seg.prefixes)} prefixes / {len(seg.suffixes)} suffixes "
            f"({len(seg.prefix_stats)} / {len(seg.suffix_stats)} >=1% candidates); "
            f"train core types {len(tr_cores)} (rare {len(tr_cores) - len(top20)})"
        )

        # ---------------- PART 1: Anatomical Taxonomy ----------------
        tax = CoreTaxonomy(seg, tr_cores, top20)
        # (a) First-on-page rare cores on held-out pages (matching s59 events)
        rare_event_items: list[tuple[str, str, str, str]] = []
        # (b) Strictly unseen held-out core tokens & unique types
        unseen_tok_items: list[tuple[str, str, str, str]] = []
        unseen_type_map: OrderedDict[str, tuple[str, str, str, str]] = OrderedDict()

        for pg in te_pages:
            seen_c: set[str] = set()
            for c, w in zip(pg.stream, pg.word_stream):
                p_slot, c_slot, s_slot = seg.segment(w)
                item = (w, p_slot, c_slot, s_slot)
                if c not in top20 and c not in seen_c:
                    rare_event_items.append(item)
                seen_c.add(c)
                if tr_cores.get(c, 0) == 0:
                    unseen_tok_items.append(item)
                    if c not in unseen_type_map:
                        unseen_type_map[c] = item

        shuf_rare_items = make_shuffled_core_items(rare_event_items, tr_cores, top20, SEED + off + 1)
        shuf_unseen_items = make_shuffled_core_items(unseen_tok_items, tr_cores, top20, SEED + off + 2)

        # Prepare real X and C- Y for both Part 1 and Part 2
        X = prepare_from_cores(T, tr_cores, top20, te_pages)
        Y_cminus, cminus_info = build_cminus(X, SEED + 7)

        # C- rare event items (wrapping replaced C- core with the original token's P and S)
        cminus_rare_items: list[tuple[str, str, str, str]] = []
        for pg in Y_cminus["pages"]:
            seen_c = set()
            for c, w_orig in zip(pg.stream, pg.word_stream):
                if c not in top20 and c not in seen_c:
                    p_orig, _, s_orig = seg.segment(w_orig)
                    cminus_rare_items.append((p_orig + c + s_orig, p_orig, c, s_orig))
                seen_c.add(c)

        # C+ (s57 seed 1) rare event items for Part 1 comparison
        cplus_s1_path = ROOT / "runs" / "s57" / f"gen_{T}_s1.meta.json"
        by_s1, role_s1 = load_meta(cplus_s1_path)
        tr_s1 = [k for k in by_s1 if role_s1.get(k) == "train"]
        te_s1 = [k for k in by_s1 if role_s1.get(k) == "heldout"]
        seg_s1 = SlotSegmenter([w for p in tr_s1 for ln in by_s1[p][1] for w in ln])
        tr_cores_s1 = Counter(seg_s1.segment(w)[1] for p in tr_s1 for ln in by_s1[p][1] for w in ln)
        top20_s1 = set(c for c, _ in tr_cores_s1.most_common(TOPK))
        tax_s1 = CoreTaxonomy(seg_s1, tr_cores_s1, top20_s1)
        cplus_rare_items: list[tuple[str, str, str, str]] = []
        for p in te_s1:
            seen_c = set()
            for ln in by_s1[p][1]:
                for w in ln:
                    p_s, c_s, s_s = seg_s1.segment(w)
                    if c_s not in top20_s1 and c_s not in seen_c:
                        cplus_rare_items.append((w, p_s, c_s, s_s))
                    seen_c.add(c_s)

        p1 = dict(
            rare_real=tax.summarize_cohort(rare_event_items),
            rare_cminus=tax.summarize_cohort(cminus_rare_items),
            rare_cplus=tax_s1.summarize_cohort(cplus_rare_items),
            rare_shuf=tax.summarize_cohort(shuf_rare_items),
            unseen_tok=tax.summarize_cohort(unseen_tok_items),
            unseen_type=tax.summarize_cohort(list(unseen_type_map.values())),
            unseen_shuf=tax.summarize_cohort(shuf_unseen_items),
        )
        part1_results[T] = p1

        emit(f"  [Part 1: Taxonomy on {T} 41 held-out pages]")
        emit(
            "    Cohort                       N | Waterfall (mutually exclusive): B1_bleed  B2_comp  B3_subgl  B4_ed1  B5_distal | "
            "Marginal: B1_rep  B1_shf  B2_any  AnyEd1  EndEd1"
        )
        for cname, cdict in (
            (f"{T} (a) rare events (real)", p1["rare_real"]),
            (f"{T} (a) rare events (C-)", p1["rare_cminus"]),
            (f"{T} (a) rare events (C+ s1)", p1["rare_cplus"]),
            (f"{T} (a) rare events (shuf)", p1["rare_shuf"]),
            (f"{T} (b) unseen tokens (real)", p1["unseen_tok"]),
            (f"{T} (b) unseen types  (real)", p1["unseen_type"]),
            (f"{T} (b) unseen tokens (shuf)", p1["unseen_shuf"]),
        ):
            emit(
                f"    {cname:28} {cdict['n']:5d} | "
                f"                            {100*cdict['w_b1']:6.2f}%  {100*cdict['w_b2']:6.2f}%   {100*cdict['w_b3']:6.2f}%  "
                f"{100*cdict['w_b4']:6.2f}%    {100*cdict['w_b5']:6.2f}% | "
                f"         {100*cdict['b1_reparse_cand']:6.2f}% {100*cdict['b1_shift']:6.2f}% "
                f"{100*cdict['b2_any']:6.2f}% {100*cdict['any_ed1']:6.2f}% {100*cdict['ed1_end']:6.2f}%"
            )

        # ---------------- PART 2: N3_dense & Page-Level Decomposition ----------------
        A_real = analyse_fast(X, SEED + off + 10)
        S_real = summarize_part2(T, [A_real], SEED + off + 11)
        part2_summaries[T] = S_real

        A_cm = analyse_fast(Y_cminus, SEED + off + 20)
        S_cm = summarize_part2(f"{T} C-", [A_cm], SEED + off + 21)
        part2_summaries[f"{T} C-"] = S_cm

        # Also score C- across 3 independent list-permutation seeds (s1-3 pooled, symmetric with C+ s1-3 pooled)
        res_cm_pool = [A_cm]
        for cm_s in (2, 3):
            Y_cm_s, _ = build_cminus(X, SEED + 7 + cm_s)
            res_cm_pool.append(analyse_fast(Y_cm_s, SEED + off + 20 + cm_s))
        S_cm_pool = summarize_part2(f"{T} C- (s1-3)", res_cm_pool, SEED + off + 25)
        part2_summaries[f"{T} C- (s1-3)"] = S_cm_pool

        res_cplus = []
        for s_idx in (1, 2, 3):
            cp_path = ROOT / "runs" / "s57" / f"gen_{T}_s{s_idx}.meta.json"
            by_g, role_g = load_meta(cp_path)
            tr_g = [k for k in by_g if role_g.get(k) == "train"]
            te_g = [k for k in by_g if role_g.get(k) == "heldout"]
            seg_g = SlotSegmenter([w for p in tr_g for ln in by_g[p][1] for w in ln])
            tr_cores_g = Counter(seg_g.segment(w)[1] for p in tr_g for ln in by_g[p][1] for w in ln)
            top20_g = set(c for c, _ in tr_cores_g.most_common(TOPK))
            te_pages_g = [
                PageObj(p, by_g[p][0], [[seg_g.segment(w)[1] for w in ln] for ln in by_g[p][1]], by_g[p][1])
                for p in te_g
            ]
            Xg = prepare_from_cores(f"{T} C+ s{s_idx}", tr_cores_g, top20_g, te_pages_g)
            Ag = analyse_fast(Xg, SEED + off + 30 + s_idx)
            res_cplus.append(Ag)
            if s_idx == 1:
                Xg_s1 = (tr_g, by_g, seg_g, tr_cores_g, te_pages_g)
        S_cp = summarize_part2(f"{T} C+", res_cplus, SEED + off + 40)
        part2_summaries[f"{T} C+"] = S_cp

        emit(f"\n  [Part 2: Neighborhood-Degree Diagnostics & Parent Ratios on {T}]")
        for lab in (T, f"{T} C-", f"{T} C- (s1-3)", f"{T} C+"):
            S = part2_summaries[lab]
            de = S["deg_events"]
            dn3 = S["deg_n3"]
            dn3d = S["deg_n3d"]
            emit(
                f"    {lab:13} (E={S['E']:4d}): event deg_all={de['deg_all']:.2f} (top20={de['deg_top']:.2f}, wdeg={de['wdeg_all']:.1f}) | "
                f"N3 deg_all={dn3['deg_all']:.2f} (top20={dn3['deg_top']:.2f}, wdeg={dn3['wdeg_all']:.1f}) | "
                f"N3_dense deg_all={dn3d['deg_all']:.2f} (top20={dn3d['deg_top']:.2f}, wdeg={dn3d['wdeg_all']:.1f})"
            )
            emit(
                f"      rates WuV: real={S['rates']['real']['WV']:.4f}  N1={S['rates']['N1']['WV']:.4f}  "
                f"N2={S['rates']['N2']['WV']:.4f}  N3_dense={S['rates']['N3_dense']['WV']:.4f}  N3={S['rates']['N3']['WV']:.4f}"
            )
            emit(
                f"      WV vs N1      : {S['rt'][('N1', 'WV')][0]:.3f} [{S['rt'][('N1', 'WV')][1]:.3f},{S['rt'][('N1', 'WV')][2]:.3f}] | "
                f"W vs N1: {S['rt'][('N1', 'W')][0]:.3f} [{S['rt'][('N1', 'W')][1]:.3f},{S['rt'][('N1', 'W')][2]:.3f}] | "
                f"V vs N1: {S['rt'][('N1', 'V')][0]:.3f} [{S['rt'][('N1', 'V')][1]:.3f},{S['rt'][('N1', 'V')][2]:.3f}]"
            )
            emit(
                f"      WV vs N2      : {S['rt'][('N2', 'WV')][0]:.3f} [{S['rt'][('N2', 'WV')][1]:.3f},{S['rt'][('N2', 'WV')][2]:.3f}] | "
                f"N1/N2 (WV): {S['decomp'][('N1/N2', 'WV')][0]:.3f} [{S['decomp'][('N1/N2', 'WV')][1]:.3f},{S['decomp'][('N1/N2', 'WV')][2]:.3f}] | "
                f"V vs N2: {S['rt'][('N2', 'V')][0]:.3f} [{S['rt'][('N2', 'V')][1]:.3f},{S['rt'][('N2', 'V')][2]:.3f}]"
            )
            emit(
                f"      WV vs N3_dense: {S['rt'][('N3_dense', 'WV')][0]:.3f} [{S['rt'][('N3_dense', 'WV')][1]:.3f},{S['rt'][('N3_dense', 'WV')][2]:.3f}] | "
                f"WV vs N3: {S['rt'][('N3', 'WV')][0]:.3f} [{S['rt'][('N3', 'WV')][1]:.3f},{S['rt'][('N3', 'WV')][2]:.3f}] | "
                f"N3_dense/N3: {S['decomp'][('N3_dense/N3', 'WV')][0]:.3f} [{S['decomp'][('N3_dense/N3', 'WV')][1]:.3f},{S['decomp'][('N3_dense/N3', 'WV')][2]:.3f}]"
            )

        # ---------------- PART 3: Unseen-Core Cross-Entropy Bake-Off ----------------
        p3_real = run_part3_bakeoff(T, tr_pages_cores, te_pages, tr_cores, seg, SEED + off + 50)
        part3_results[T] = p3_real

        # Also score s57 C+ seed 1 unseen cores as positive control for M_page_mut vs M_shuf_null
        tr_g, by_g, seg_g, tr_cores_g, te_pages_g = Xg_s1
        tr_pages_cores_g = [[[seg_g.segment(w)[1] for w in ln] for ln in by_g[p][1]] for p in tr_g]
        p3_cp = run_part3_bakeoff(f"{T} C+ s1", tr_pages_cores_g, te_pages_g, tr_cores_g, seg_g, SEED + off + 60)
        part3_results[f"{T} C+ s1"] = p3_cp

        emit(f"\n  [Part 3: Unseen-Core Cross-Entropy Bake-Off on {T} (166 -> 41)]")
        for p3 in (p3_real, p3_cp):
            b_core = p3["bits_per_core"]
            b_char = p3["bits_per_char"]
            d_bc = p3["diff_bc_vs_c2"]
            d_ms = p3["diff_mut_vs_shuf"]
            emit(
                f"    {p3['label']:10} (unseen tok={p3['n_tok']:4d}, types={p3['n_types']:4d}; "
                f"fitted lam_bleed/comp/sub={p3['lam'][0]:.2f}/{p3['lam'][1]:.2f}/{p3['lam'][2]:.2f}, alpha_mut={p3['alpha_mut']:.2f}):"
            )
            emit(
                f"      bits/core: M_char2={b_core['M_char2']:.3f} (M_char3={b_core['M_char3']:.3f}) | "
                f"M_bleed_compound={b_core['M_bleed_compound']:.3f} | "
                f"M_page_mut={b_core['M_page_mut']:.3f} | M_shuf_null(N1)={b_core['M_shuf_null']:.3f}"
            )
            emit(
                f"      bits/char: M_char2={b_char['M_char2']:.3f} (M_char3={b_char['M_char3']:.3f}) | "
                f"M_bleed_compound={b_char['M_bleed_compound']:.3f} | "
                f"M_page_mut={b_char['M_page_mut']:.3f} | M_shuf_null(N1)={b_char['M_shuf_null']:.3f}"
            )
            emit(
                f"      Delta(M_bleed_compound - M_char2): {d_bc[0]:+.3f} [{d_bc[1]:+.3f},{d_bc[2]:+.3f}] bits/core | "
                f"Delta(M_page_mut - M_shuf_null): {d_ms[0]:+.4f} [{d_ms[1]:+.4f},{d_ms[2]:+.4f}] bits/core"
            )
        emit(f"  [{T} completed in {time.time() - t0:.1f}s]\n")

    # ======================================================================= Consolidated Summary Tables
    emit("=== CONSOLIDATED TABLE 1: Anatomical Taxonomy of Held-Out Rare & Unseen Cores (166 -> 41) ===")
    emit(
        f"{'Cohort':30} {'N':>5} | {'B1_bleed':>8} {'B2_comp':>8} {'B3_subgl':>8} {'B4_ed1':>8} {'B5_dist':>8} | "
        f"{'B1_rep':>7} {'B1_shf':>7} {'B2_any':>7} {'AnyEd1':>7} {'EndEd1':>7}"
    )
    for T in TRANSLITS:
        p1 = part1_results[T]
        for label_s, key_s in (
            (f"{T} rare events (real)", "rare_real"),
            (f"{T} rare events (C-)", "rare_cminus"),
            (f"{T} rare events (C+ s1)", "rare_cplus"),
            (f"{T} rare events (char-shuf)", "rare_shuf"),
            (f"{T} unseen tokens (real)", "unseen_tok"),
            (f"{T} unseen types  (real)", "unseen_type"),
            (f"{T} unseen tokens (char-shuf)", "unseen_shuf"),
        ):
            c = p1[key_s]
            emit(
                f"{label_s:30} {c['n']:5d} | "
                f"{100*c['w_b1']:7.2f}% {100*c['w_b2']:7.2f}% {100*c['w_b3']:7.2f}% {100*c['w_b4']:7.2f}% {100*c['w_b5']:7.2f}% | "
                f"{100*c['b1_reparse_cand']:6.2f}% {100*c['b1_shift']:6.2f}% {100*c['b2_any']:6.2f}% "
                f"{100*c['any_ed1']:6.2f}% {100*c['ed1_end']:6.2f}%"
            )
    emit("")

    emit("=== CONSOLIDATED TABLE 2: Repair of N3 -> N3_dense & 4-Factor Decomposition of WV Parent Ratio ===")
    emit(
        f"{'Text':14} {'Events':>6} | {'deg(ev/N3/N3d)':>18} | {'WV vs N1 (local)':^21} | "
        f"{'N1/N2 (page)':^19} | {'WV vs N3_dense':^21} | {'WV vs N3 (s59)':^21} | {'N3_dense/N3':^19}"
    )
    for T in TRANSLITS:
        for lab in (T, f"{T} C-", f"{T} C- (s1-3)", f"{T} C+"):
            S = part2_summaries[lab]
            d_str = f"{S['deg_events']['deg_all']:.1f}/{S['deg_n3']['deg_all']:.1f}/{S['deg_n3d']['deg_all']:.1f}"
            r_n1 = S["rt"][("N1", "WV")]
            r_n1n2 = S["decomp"][("N1/N2", "WV")]
            r_n3d = S["rt"][("N3_dense", "WV")]
            r_n3 = S["rt"][("N3", "WV")]
            r_dn3 = S["decomp"][("N3_dense/N3", "WV")]
            emit(
                f"{lab:14} {S['E']:6d} | {d_str:>18} | "
                f"{r_n1[0]:5.3f} [{r_n1[1]:.3f},{r_n1[2]:.3f}] | "
                f"{r_n1n2[0]:5.3f} [{r_n1n2[1]:.3f},{r_n1n2[2]:.3f}] | "
                f"{r_n3d[0]:5.3f} [{r_n3d[1]:.3f},{r_n3d[2]:.3f}] | "
                f"{r_n3[0]:5.3f} [{r_n3[1]:.3f},{r_n3[2]:.3f}] | "
                f"{r_dn3[0]:5.3f} [{r_dn3[1]:.3f},{r_dn3[2]:.3f}]"
            )
    emit("")

    emit("=== CONSOLIDATED TABLE 3: Held-Out Cross-Entropy Bake-Off on Strictly Unseen Cores (166 -> 41) ===")
    emit(
        f"{'Text':10} {'Tok':>5} {'Typ':>5} | {'M_char2 (b/c, b/ch)':>20} | {'M_bleed_comp (b/c, b/ch)':>24} | "
        f"{'M_page_mut (b/c)':>16} | {'M_shuf_null (b/c)':>17} | {'Delta(BC-C2)':^21} | {'Delta(Mut-Shuf)':^21}"
    )
    for T in TRANSLITS:
        for lab in (T, f"{T} C+ s1"):
            p3 = part3_results[lab]
            bc = p3["bits_per_core"]
            bch = p3["bits_per_char"]
            d_bc = p3["diff_bc_vs_c2"]
            d_ms = p3["diff_mut_vs_shuf"]
            emit(
                f"{lab:10} {p3['n_tok']:5d} {p3['n_types']:5d} | "
                f"{bc['M_char2']:8.3f}, {bch['M_char2']:8.3f}   | "
                f"{bc['M_bleed_compound']:10.3f}, {bch['M_bleed_compound']:8.3f}   | "
                f"{bc['M_page_mut']:16.3f} | "
                f"{bc['M_shuf_null']:17.3f} | "
                f"{d_bc[0]:+5.3f} [{d_bc[1]:+.3f},{d_bc[2]:+.3f}] | "
                f"{d_ms[0]:+6.4f} [{d_ms[1]:+.4f},{d_ms[2]:+.4f}]"
            )
    emit("")
    emit(f"date end: {clock()}")
    emit(f"elapsed: {time.time() - T_START:.1f} s")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
