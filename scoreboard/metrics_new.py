"""New Phase-1 metric families (PLAN.md, Phase 1): lexicon growth, slot structure,
information profile, held-out bake-off.

Input to every metric is a plain list of pages:
    pages = [dict(id=str, section=str, hand=str, quire=str|None, lines=[[tok, ...], ...]), ...]
Loaders: voynich_pages(), wordlist_pages(), meta_json_pages().  No dependency on
scoreboard/score.py or scoreboard/corpus.py.

Hypothesis families used in every docstring:
    L = natural language in an invented script
    C = codebook / nomenclator / non-syntactic notation
    G = copy-and-mutate (self-citation) generation with line rules
Seed convention: 20261017.  Only stdlib + numpy.
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import corpora  # noqa: E402
import vparse  # noqa: E402

SEED = 20261017
LOG2 = math.log(2)


# ----------------------------------------------------------------------------
# loaders
# ----------------------------------------------------------------------------
def voynich_pages(tokenization="eva", drop_unclear=True, strict_spaces=False):
    """Paragraph units (P*) only, grouped by page in manuscript order.
    Tokens containing '?' are dropped; empty lines are dropped."""
    recs = vparse.paragraph_text(vparse.load(strict_spaces=strict_spaces))
    pages, cur = [], None
    for r in recs:
        ws = [w for w in r["words"] if not (drop_unclear and "?" in w)]
        if tokenization == "glyph":
            ws = [corpora.to_glyphs(w, corpora.GLYPHS) for w in ws]
        elif tokenization == "glyph+":
            ws = [corpora.to_glyphs(w, corpora.GLYPHS_PLUS) for w in ws]
        if cur is None or cur["id"] != r["page"]:
            cur = dict(id=r["page"], section=r["illus"], hand=r["hand"],
                       quire=r["quire"], lang=r["lang"], lines=[])
            pages.append(cur)
        if ws:
            cur["lines"].append(ws)
    return [p for p in pages if p["lines"]]


def wordlist_pages(words, line_len=8, page_len=20, section_labels=None, hand="ctrl"):
    """Wrap a flat token list into pages of `page_len` lines of `line_len` tokens.
    section_labels: None -> one section 'ctrl'; a list -> pages split into that many
    contiguous equal blocks, one label per block (gives the profile an
    'other section' relation)."""
    lines = [words[i:i + line_len] for i in range(0, len(words), line_len)]
    chunks = [lines[i:i + page_len] for i in range(0, len(lines), page_len)]
    n = len(chunks)
    pages = []
    for k, ch in enumerate(chunks):
        if section_labels:
            sec = section_labels[min(len(section_labels) - 1, k * len(section_labels) // n)]
        else:
            sec = "ctrl"
        pages.append(dict(id=f"p{k:04d}", section=sec, hand=hand, quire=None, lines=ch))
    return pages


def meta_json_pages(path):
    """Read {"pages":[{"id","section","lines":[[tok,...]]}, ...]} (hand/quire optional)."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for p in d["pages"]:
        out.append(dict(id=str(p["id"]), section=str(p.get("section", "?")),
                        hand=str(p.get("hand", "?")), quire=p.get("quire"),
                        lines=[[str(t) for t in ln] for ln in p["lines"] if ln]))
    return out


def flat_tokens(pages):
    return [t for p in pages for ln in p["lines"] for t in ln]


# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------
def entropy_counts(counter):
    n = sum(counter.values())
    if n == 0:
        return float("nan")
    return -sum(v / n * math.log2(v / n) for v in counter.values() if v)


def edit1_neighbours(w, alph):
    """All strings at Levenshtein distance exactly 1 from w (dup-free)."""
    out = set()
    for i in range(len(w) + 1):
        for a in alph:
            out.add(w[:i] + a + w[i:])
        if i < len(w):
            out.add(w[:i] + w[i + 1:])
            for a in alph:
                if a != w[i]:
                    out.add(w[:i] + a + w[i + 1:])
    out.discard(w)
    return out


def is_edit1(a, b):
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or a == b:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


# ----------------------------------------------------------------------------
# 1. lexicon growth
# ----------------------------------------------------------------------------
def _heaps(tokens, n_grid=40, n_min=100):
    """Types-seen curve, Heaps beta by log-log OLS, early/late slopes, rate ratio."""
    seen, V = set(), np.zeros(len(tokens) + 1, dtype=np.int32)
    for i, t in enumerate(tokens):
        seen.add(t)
        V[i + 1] = len(seen)
    N = len(tokens)
    if N < 4 * n_min:
        return dict(beta=float("nan"), K=float("nan"), beta_early=float("nan"),
                    beta_late=float("nan"), rate_ratio_last20_first20=float("nan"),
                    n_tokens=N, n_types=len(seen))
    grid = np.unique(np.geomspace(n_min, N, n_grid).astype(int))
    x, y = np.log(grid), np.log(V[grid])
    beta, logK = np.polyfit(x, y, 1)
    h = len(grid) // 2
    beta_early = np.polyfit(x[:h + 1], y[:h + 1], 1)[0]
    beta_late = np.polyfit(x[h:], y[h:], 1)[0]
    k = N // 5
    first = V[k] / k
    last = (V[N] - V[N - k]) / k
    return dict(beta=float(beta), K=float(math.exp(logK)), beta_early=float(beta_early),
                beta_late=float(beta_late), rate_ratio_last20_first20=float(last / first),
                n_tokens=N, n_types=len(seen),
                curve=[(int(g), int(V[g])) for g in grid])


def _edit1_new_type_share(tokens, window=200, far_offset=None, rng=None):
    """Share of first-occurrence types within edit distance 1 of a type seen in the
    previous `window` tokens (far_offset: compare against a window ending that many
    tokens earlier, as a non-local baseline)."""
    alph = sorted(set("".join(tokens)))
    seen, hits, new = set(), 0, 0
    recent = Counter()
    for i, t in enumerate(tokens):
        if far_offset:
            lo, hi = i - far_offset - window, i - far_offset
            if hi <= 0:
                lo, hi = i + far_offset, i + far_offset + window
            ctx = set(tokens[max(lo, 0):max(hi, 0)])
        else:
            ctx = recent
        if t not in seen:
            new += 1
            if len(t) <= 12:
                nb = edit1_neighbours(t, alph)
                if any(u in ctx for u in nb):
                    hits += 1
        seen.add(t)
        if not far_offset:
            recent[t] += 1
            if i - window >= 0:
                old = tokens[i - window]
                recent[old] -= 1
                if recent[old] == 0:
                    del recent[old]
    return hits / new if new else float("nan")


def lexicon_growth(pages, n_shuffles=20, seed=SEED, min_tokens=2000):
    """New-type introduction curve in manuscript order.
    Returns Heaps beta (log-log OLS, V = K N^beta), early/late segment slopes,
    the new-type rate in the last 20% of tokens over the first 20%, the share of
    new types within edit distance 1 of a type seen in the previous 200 tokens
    (plus a far-window baseline), per section and per hand, and the same for
    n_shuffles random page orderings (null for 'order matters').
    Predictions:
      L: beta ~0.5-0.7, no saturation (beta_late ~ beta_early), rate ratio like
         controls; edit-1 share near the far baseline.
      C: bounded inventory saturates: falling new-type rate, beta_late < beta_early,
         rate ratio well below language controls; order matters little.
      G: steady beta but new types dominated by single-edit variants of recent
         words: edit-1 share far above the far-window baseline and above controls;
         shuffling pages lowers the edit-1 share (locality) more than beta.
    """
    rng = random.Random(seed)
    toks = flat_tokens(pages)
    out = dict(n_tokens=len(toks), n_types=len(set(toks)))
    out["all"] = _heaps(toks)
    out["all"]["edit1_share_recent200"] = _edit1_new_type_share(toks, 200)
    out["all"]["edit1_share_far"] = _edit1_new_type_share(toks, 200, far_offset=5000)
    for key in ("section", "hand"):
        out[f"by_{key}"] = {}
        for lab in sorted({p[key] for p in pages}):
            sub = flat_tokens([p for p in pages if p[key] == lab])
            if len(sub) < min_tokens:
                continue
            r = _heaps(sub)
            r.pop("curve", None)
            r["edit1_share_recent200"] = _edit1_new_type_share(sub, 200)
            out[f"by_{key}"][lab] = r
    null = defaultdict(list)
    for _ in range(n_shuffles):
        order = pages[:]
        rng.shuffle(order)
        st = flat_tokens(order)
        r = _heaps(st)
        for k in ("beta", "beta_early", "beta_late", "rate_ratio_last20_first20"):
            null[k].append(r[k])
        null["edit1_share_recent200"].append(_edit1_new_type_share(st, 200))
    out["shuffled_pages_null"] = {k: dict(mean=float(np.mean(v)), sd=float(np.std(v)))
                                  for k, v in null.items()}
    return out


# ----------------------------------------------------------------------------
# 2. slot structure
# ----------------------------------------------------------------------------
class SlotSegmenter:
    """Data-driven prefix/core/suffix segmentation.
    Candidate prefixes: strings (len 1..max_len) that begin >= min_share of tokens and
    whose next-symbol (glyph or end-of-word) entropy >= ent_frac * H(glyph).
    Suffixes likewise from the end.  prefix = longest candidate leaving >= 1 glyph,
    suffix = longest candidate of the remainder leaving >= 1 glyph, core = rest."""

    def __init__(self, tokens, min_share=0.01, max_len=3, ent_frac=0.5):
        freq = Counter(tokens)
        N = sum(freq.values())
        gl = Counter()
        for w, c in freq.items():
            for ch in w:
                gl[ch] += c
        self.alph = sorted(gl)
        self.h_glyph = entropy_counts(gl)
        self.thresh = ent_frac * self.h_glyph
        self.prefixes, self.prefix_stats = self._candidates(freq, N, max_len, min_share, False)
        self.suffixes, self.suffix_stats = self._candidates(freq, N, max_len, min_share, True)
        self._cache = {}

    def _candidates(self, freq, N, max_len, min_share, reverse):
        cnt, nxt = Counter(), defaultdict(Counter)
        for w, c in freq.items():
            s = w[::-1] if reverse else w
            for L in range(1, min(max_len, len(s)) + 1):
                a = s[:L]
                cnt[a] += c
                nxt[a][s[L] if len(s) > L else "#"] += c
        cands, stats = set(), {}
        for a, c in cnt.items():
            if c / N < min_share:
                continue
            h = entropy_counts(nxt[a])
            stats[a[::-1] if reverse else a] = (c / N, h)
            if h >= self.thresh:
                cands.add(a[::-1] if reverse else a)
        return cands, stats

    def segment(self, w):
        r = self._cache.get(w)
        if r is not None:
            return r
        pre = ""
        for L in range(min(3, len(w) - 1), 0, -1):
            if w[:L] in self.prefixes:
                pre = w[:L]
                break
        rest = w[len(pre):]
        suf = ""
        for L in range(min(3, len(rest) - 1), 0, -1):
            if rest[-L:] in self.suffixes:
                suf = rest[-L:]
                break
        core = rest[:len(rest) - len(suf)]
        r = (pre, core, suf)
        self._cache[w] = r
        return r


def _slot_metrics(tokens, seg):
    freq = Counter(tokens)
    trip = {w: seg.segment(w) for w in freq}
    P = Counter(); PC = Counter(); C = Counter(); CS = Counter(); S = Counter()
    for w, c in freq.items():
        p, k, s = trip[w]
        P[p] += c; C[k] += c; S[s] += c; PC[(p, k)] += c; CS[(k, s)] += c
    nP, nC, nS = len(P), len(C), len(S)
    n_types = len(freq)
    # H(core|prefix) token-weighted
    N = sum(freq.values())
    h_c_given_p = sum(P[p] / N * entropy_counts(Counter({k: v for (pp, k), v in PC.items() if pp == p}))
                      for p in P)
    # table-likeness: mean normalised entropy of cores within prefix
    rows = []
    for p in P:
        d = Counter({k: v for (pp, k), v in PC.items() if pp == p})
        if len(d) >= 2:
            rows.append((P[p], entropy_counts(d) / math.log2(len(d)), len(d)))
    wsum = sum(r[0] for r in rows) or 1
    # core edit-1 neighbourhood density (types)
    cores = set(C)
    alph = seg.alph
    nb = sum(1 for k in cores if len(k) <= 10 and any(u in cores for u in edit1_neighbours(k, alph)))
    return dict(
        n_tokens=N, n_types=n_types, n_prefixes=nP, n_cores=nC, n_suffixes=nS,
        occupancy_3d=n_types / (nP * nC * nS),
        occupancy_prefix_core=len(PC) / (nP * nC),
        occupancy_core_suffix=len(CS) / (nC * nS),
        H_core=entropy_counts(C), H_core_given_prefix=h_c_given_p,
        H_prefix=entropy_counts(P), H_suffix=entropy_counts(S),
        table_likeness_weighted=sum(r[0] * r[1] for r in rows) / wsum,
        table_likeness_unweighted=float(np.mean([r[1] for r in rows])) if rows else float("nan"),
        mean_row_fill=float(np.mean([r[2] / nC for r in rows])) if rows else float("nan"),
        core_edit1_share=nb / len(cores),
        empty_prefix_token_share=P[""] / N, empty_suffix_token_share=S[""] / N,
        top_prefixes=[(p, round(P[p] / N, 3)) for p, _ in P.most_common(12)],
        top_suffixes=[(s, round(S[s] / N, 3)) for s, _ in S.most_common(12)],
        top_cores=[(k, round(C[k] / N, 3)) for k, _ in C.most_common(12)],
    )


def slot_structure(pages, top_types=2000, min_share=0.01, ent_frac=0.5):
    """Induce prefix/core/suffix slots (SlotSegmenter) and measure the product space.
    Reports inventory sizes, occupancy of prefix x core x suffix (occupied cells /
    possible cells, plus 2-D occupancies), H(core|prefix), a table-likeness score
    (token-weighted mean normalised entropy of the core distribution within each
    prefix; 1 = uniform), row fill, and core edit-1 neighbour share; computed on
    all types and on the top `top_types` types.  Also the positional glyph profile
    (mean relative position per glyph) used to sanity-check the affix lists.
    Predictions:
      L: sparse product space (occupancy << controls? no: like controls), Zipfian
         cores within prefix (table-likeness like Latin/Italian), large core
         inventory relative to affixes.
      C: designed table: high occupancy, near-uniform core usage within prefix
         (table-likeness near 1), small closed core inventory, low edit-1 crowding.
      G: in between: occupancy above language, table-likeness like language,
         but cores crowded with single-edit neighbours (core_edit1_share high).
    """
    toks = flat_tokens(pages)
    seg = SlotSegmenter(toks, min_share=min_share, ent_frac=ent_frac)
    freq = Counter(toks)
    top = {w for w, _ in freq.most_common(top_types)}
    out = dict(
        h_glyph=seg.h_glyph, entropy_threshold=seg.thresh,
        prefix_candidates=sorted(seg.prefixes, key=lambda a: -seg.prefix_stats[a][0]),
        suffix_candidates=sorted(seg.suffixes, key=lambda a: -seg.suffix_stats[a][0]),
        prefix_rejected=[(a, round(sh, 3), round(h, 2)) for a, (sh, h) in
                         sorted(seg.prefix_stats.items(), key=lambda x: -x[1][0]) if a not in seg.prefixes],
        suffix_rejected=[(a, round(sh, 3), round(h, 2)) for a, (sh, h) in
                         sorted(seg.suffix_stats.items(), key=lambda x: -x[1][0]) if a not in seg.suffixes],
        all_types=_slot_metrics(toks, seg),
        top_types=_slot_metrics([t for t in toks if t in top], seg),
    )
    # positional glyph profile: mean relative position, share initial, share final
    pos = defaultdict(list); ini = Counter(); fin = Counter(); tot = Counter()
    for w in toks:
        L = len(w)
        for i, ch in enumerate(w):
            tot[ch] += 1
            if L > 1:
                pos[ch].append(i / (L - 1))
            ini[ch] += i == 0
            fin[ch] += i == L - 1
    out["glyph_position"] = {ch: dict(n=tot[ch], mean_relpos=float(np.mean(pos[ch])) if pos[ch] else 0.5,
                                      p_initial=ini[ch] / tot[ch], p_final=fin[ch] / tot[ch])
                             for ch in tot if tot[ch] >= 100}
    out["example_segmentations"] = [(w, seg.segment(w)) for w, _ in freq.most_common(15)]
    return out, seg


# ----------------------------------------------------------------------------
# 3. information profile
# ----------------------------------------------------------------------------
RELATIONS = ["adjacent", "same_line_2_5", "prev_line_same_col", "prev_line_other_col",
             "same_page_far", "same_section_other_page", "other_section"]


def _mi_from_pairs(a, b, V):
    joint = np.bincount(a * V + b, minlength=V * V).astype(float)
    n = joint.sum()
    pa = np.bincount(a, minlength=V).astype(float) / n
    pb = np.bincount(b, minlength=V).astype(float) / n
    pj = joint / n
    nz = pj > 0
    pj2 = pj.reshape(V, V)
    outer = np.outer(pa, pb).ravel()
    return float((pj[nz] * np.log2(pj[nz] / outer[nz])).sum()), float(-(pa[pa > 0] * np.log2(pa[pa > 0])).sum())


def _collect_pairs(id_pages, rng):
    """id_pages: list of (section, [[ids]]).  Returns dict relation -> list of (w, c)."""
    pairs = {r: [] for r in RELATIONS}
    by_sec = defaultdict(list)
    for pi, (sec, lines) in enumerate(id_pages):
        by_sec[sec].append(pi)
    flat = [[t for ln in lines for t in ln] for _, lines in id_pages]
    secs = sorted(by_sec)
    for pi, (sec, lines) in enumerate(id_pages):
        same_sec = [q for q in by_sec[sec] if q != pi and flat[q]]
        other_sec = [q for s in secs if s != sec for q in by_sec[s] if flat[q]]
        for i, line in enumerate(lines):
            far_lines = [k for k in range(len(lines)) if abs(k - i) >= 3]
            prev = lines[i - 1] if i > 0 else None
            for j, w in enumerate(line):
                if j + 1 < len(line):
                    pairs["adjacent"].append((w, line[j + 1]))
                for d in range(2, 6):
                    if j + d < len(line):
                        pairs["same_line_2_5"].append((w, line[j + d]))
                if prev:
                    if j < len(prev):
                        pairs["prev_line_same_col"].append((w, prev[j]))
                    others = [prev[k] for k in range(len(prev)) if k != j]
                    if others:
                        pairs["prev_line_other_col"].append((w, rng.choice(others)))
                if far_lines:
                    k = rng.choice(far_lines)
                    pairs["same_page_far"].append((w, rng.choice(lines[k])))
                if same_sec:
                    pairs["same_section_other_page"].append((w, rng.choice(flat[rng.choice(same_sec)])))
                if other_sec:
                    pairs["other_section"].append((w, rng.choice(flat[rng.choice(other_sec)])))
    return pairs


def _profile(id_pages, V, rng, n_boot=30, n_null=5, cap=30000):
    pairs = _collect_pairs(id_pages, rng)
    sizes = [len(v) for v in pairs.values() if v]
    n = min(min(sizes), cap)
    nrng = np.random.default_rng(rng.randrange(1 << 30))
    res = {}
    for rel, pr in pairs.items():
        if len(pr) < 200:
            res[rel] = dict(n_pairs=len(pr), mi_raw=float("nan"), mi_null=float("nan"),
                            mi=float("nan"), se=float("nan"))
            continue
        arr = np.array(pr, dtype=np.int64)
        arr = arr[nrng.choice(len(arr), n, replace=False)]
        a, b = arr[:, 0], arr[:, 1]
        mi, hw = _mi_from_pairs(a, b, V)
        null = [_mi_from_pairs(a, nrng.permutation(b), V)[0] for _ in range(n_null)]
        boots = []
        for _ in range(n_boot):
            idx = nrng.integers(0, n, n)
            boots.append(_mi_from_pairs(a[idx], b[idx], V)[0])
        res[rel] = dict(n_pairs=len(pr), n_used=n, H_w=hw, mi_raw=mi, mi_null=float(np.mean(null)),
                        mi=mi - float(np.mean(null)), se=float(np.std(boots)))
    return res


def bpe_resegment(pages, n_merges=30):
    """Remove word boundaries within each line, learn n_merges BPE merges on the glyph
    stream (pairs never cross lines), and return pages whose tokens are BPE units."""
    lines = [[list("".join(ln)) for ln in p["lines"]] for p in pages]
    merges = []
    for _ in range(n_merges):
        pc = Counter()
        for pl in lines:
            for s in pl:
                pc.update(zip(s, s[1:]))
        if not pc:
            break
        (x, y), _ = pc.most_common(1)[0]
        merges.append(x + y)
        xy = x + y
        for pl in lines:
            for s in pl:
                i, out = 0, []
                while i < len(s):
                    if i + 1 < len(s) and s[i] == x and s[i + 1] == y:
                        out.append(xy); i += 2
                    else:
                        out.append(s[i]); i += 1
                s[:] = out
    new = []
    for p, pl in zip(pages, lines):
        new.append(dict(p, lines=[s for s in pl if s]))
    return new, merges


def information_profile(pages, top=500, seed=SEED, n_boot=30, bpe_merges=30):
    """Word-token information H(w) - H(w|context) = MI(w; context) at seven context
    relations: adjacent, same line distance 2-5, previous line same column, previous
    line other column, same page >= 3 lines away, same section other page, other
    section.  Types outside the top `top` are mapped to OTHER.  Pair sets are
    subsampled to a common size so the plug-in bias is comparable; the reported
    `mi` is the plug-in MI minus the mean MI of 5 context-permuted copies (same
    marginals); `se` is a bootstrap SE (n_boot resamples) of the raw MI.
    Computed twice: with the given word boundaries, and after re-segmenting the
    space-removed glyph stream with BPE (`bpe_merges` merges), PLAN section 5.
    Predictions:
      L: steep decay from adjacent (adjacent >> distance 2-5 >> page-level), and
         re-segmentation does not remove the adjacent peak.
      C: flat profile: adjacent ~ same line ~ same page, all at a page/section
         (topic) level; little change on re-segmentation.
      G: spikes at adjacent and previous-line (esp. same column), page-level low.
    """
    rng = random.Random(seed)
    out = {}
    for label, pg in (("word_boundaries_given", pages),
                      ("bpe_resegmented", None)):
        if pg is None:
            pg, merges = bpe_resegment(pages, bpe_merges)
            out["bpe_merges"] = merges
        toks = flat_tokens(pg)
        freq = Counter(toks)
        vocab = {w: i for i, (w, _) in enumerate(freq.most_common(top))}
        V = len(vocab) + 1
        other = V - 1
        id_pages = [(p["section"], [[vocab.get(t, other) for t in ln] for ln in p["lines"]]) for p in pg]
        r = _profile(id_pages, V, rng, n_boot=n_boot)
        r["n_tokens"] = len(toks)
        r["other_share"] = sum(1 for t in toks if t not in vocab) / len(toks)
        out[label] = r
    return out


# ----------------------------------------------------------------------------
# 4. held-out bake-off
# ----------------------------------------------------------------------------
class CharMarkov:
    """Interpolated Witten-Bell character n-gram over words (start pad '^', end '$')."""

    def __init__(self, words, order):
        self.order = order
        self.counts = [defaultdict(Counter) for _ in range(order + 1)]
        alph = set()
        for w in words:
            s = "^" * order + w + "$"
            alph.update(w)
            for i in range(order, len(s)):
                for k in range(order + 1):
                    self.counts[k][s[i - k:i]][s[i]] += 1
        self.alph = alph
        self.uniform = 1.0 / (len(alph) + 2)
        self.stats = [{ctx: (sum(c.values()), len(c)) for ctx, c in lvl.items()} for lvl in self.counts]
        self._cache = {}

    def prob(self, ctx, x):
        key = (ctx, x)
        r = self._cache.get(key)
        if r is not None:
            return r
        p = self.uniform
        for k in range(0, self.order + 1):
            c = ctx[len(ctx) - k:] if k else ""
            st = self.stats[k].get(c)
            if st is None:
                break
            n, T = st
            p = (self.counts[k][c].get(x, 0) + T * p) / (n + T)
        self._cache[key] = p
        return p

    def logp_word(self, w):
        s = "^" * self.order + w + "$"
        lp = 0.0
        for i in range(self.order, len(s)):
            lp += math.log2(self.prob(s[i - self.order:i], s[i]))
        return lp


def _wb_dist(counter_of_counters):
    """Witten-Bell conditional with a backoff callback."""
    stats = {k: (sum(c.values()), len(c)) for k, c in counter_of_counters.items()}

    def prob(ctx, x, backoff):
        st = stats.get(ctx)
        if st is None:
            return backoff
        n, T = st
        return (counter_of_counters[ctx].get(x, 0) + T * backoff) / (n + T)
    return prob


class SlotModel:
    """P(prefix) P(core|prefix) P(suffix|core) with Witten-Bell backoff
    (core|prefix -> core -> order-2 char model over cores; suffix|core -> suffix)."""

    def __init__(self, words, seg):
        self.seg = seg
        P, PC, C, CS, S = Counter(), defaultdict(Counter), Counter(), defaultdict(Counter), Counter()
        cores = []
        for w in words:
            p, k, s = seg.segment(w)
            P[p] += 1; PC[p][k] += 1; C[k] += 1; CS[k][s] += 1; S[s] += 1
            cores.append(k)
        self.N = len(words)
        self.P, self.C, self.S = P, C, S
        self.TP, self.TC, self.TS = len(P), len(C), len(S)
        self.pc = _wb_dist(PC)
        self.cs = _wb_dist(CS)
        self.core_char = CharMarkov(cores, 2)
        self.pref_char = CharMarkov(list(P.elements()), 2)
        self.suf_char = CharMarkov(list(S.elements()), 2)

    def logp_word(self, w):
        p, k, s = self.seg.segment(w)
        # prefix
        pp = (self.P.get(p, 0) + self.TP * 2 ** self.pref_char.logp_word(p)) / (self.N + self.TP)
        # core | prefix, backoff to core unigram, backoff to char model
        pk_char = 2 ** self.core_char.logp_word(k)
        pk_uni = (self.C.get(k, 0) + self.TC * pk_char) / (self.N + self.TC)
        pk = self.pc(p, k, pk_uni)
        ps_uni = (self.S.get(s, 0) + self.TS * 2 ** self.suf_char.logp_word(s)) / (self.N + self.TS)
        ps = self.cs(k, s, ps_uni)
        return math.log2(pp) + math.log2(pk) + math.log2(ps)


class UnigramGT:
    """Word unigram with Good-Turing mass N1/N for unseen words, spread over strings by
    an order-3 char model (deficient: char mass on seen strings is not removed)."""

    def __init__(self, words, char_model):
        self.c = Counter(words)
        self.N = len(words)
        n1 = sum(1 for v in self.c.values() if v == 1)
        self.p0 = max(n1, 1) / self.N
        self.cm = char_model

    def logp_word(self, w):
        c = self.c.get(w, 0)
        if c:
            return math.log2((1 - self.p0) * c / self.N)
        return math.log2(self.p0) + self.cm.logp_word(w)


def _folds(pages, block=10):
    if all(p.get("quire") not in (None, "?") for p in pages):
        labs = sorted({p["quire"] for p in pages})
        return [[i for i, p in enumerate(pages) if p["quire"] == q] for q in labs]
    return [list(range(i, min(i + block, len(pages)))) for i in range(0, len(pages), block)]


def heldout_bakeoff(pages, copy_mass=0.3, seed=SEED):
    """Leave-one-quire-out (or blocks of 10 pages) held-out log-likelihood per token for
      (a) char Markov order 2 and 3 (Witten-Bell), (b) slot model P(pre)P(core|pre)
      P(suf|core) using SlotSegmenter induced on training pages, (c) word unigram
      with Good-Turing unseen mass (+ order-3 char model for unseen strings),
      (d) copy model: `copy_mass` (and 0.1, 0.05) on the previous line's tokens (half
      exact, half spread over their single-edit variants) mixed with (a) order 3.
    bits/char divides by sum(len(w)+1).  Reports overall and per-section means and
    the per-section winner.  (b) and (c) are slightly deficient (mass leaks to
    non-canonical strings), so they are conservative.
    Predictions:
      L: char Markov-3 or unigram+char wins everywhere; slot model close to Markov
         because affixes are real morphology but cores are an open class;
         copy model adds nothing over Markov-3.
      C: slot model beats Markov-3 clearly (closed slot inventories); copy adds
         nothing; unigram strong because entries are drawn from a fixed list.
      G: copy model wins over Markov-3 by a clear margin on the previous-line
         terms; slot model competitive (words are built from slots).
    """
    folds = _folds(pages)
    masses = (copy_mass, 0.1, 0.05)
    copy_names = [f"copy{m}+markov3" for m in masses]
    models = ["markov2", "markov3", "slot", "unigram_gt"] + copy_names
    per_sec = defaultdict(lambda: {m: [0.0, 0, 0] for m in models})  # bits, tokens, chars
    tot = {m: [0.0, 0, 0] for m in models}
    for fold in folds:
        test = set(fold)
        train_words = flat_tokens([p for i, p in enumerate(pages) if i not in test])
        if not train_words:
            continue
        m2, m3 = CharMarkov(train_words, 2), CharMarkov(train_words, 3)
        seg = SlotSegmenter(train_words)
        slot = SlotModel(train_words, seg)
        uni = UnigramGT(train_words, m3)
        A = len(m3.alph)
        for i in fold:
            p = pages[i]
            lines = p["lines"]
            for li, line in enumerate(lines):
                prev = lines[li - 1] if li > 0 else None
                for w in line:
                    nch = len(w) + 1
                    lp = {"markov2": m2.logp_word(w), "markov3": m3.logp_word(w),
                          "slot": slot.logp_word(w), "unigram_gt": uni.logp_word(w)}
                    pm3 = 2 ** lp["markov3"]
                    if prev:
                        pc = 0.0
                        for u in prev:
                            if w == u:
                                pc += 0.5
                            elif is_edit1(w, u):
                                n1 = len(u) * (A - 1) + (len(u) + 1) * A + len(u)
                                pc += 0.5 / n1
                        pc /= len(prev)
                        for m, nm in zip(masses, copy_names):
                            lp[nm] = math.log2(m * pc + (1 - m) * pm3)
                    else:
                        for nm in copy_names:
                            lp[nm] = lp["markov3"]
                    for m in models:
                        for acc in (tot[m], per_sec[p["section"]][m]):
                            acc[0] -= lp[m]; acc[1] += 1; acc[2] += nch
    out = dict(n_folds=len(folds), fold_type="quire" if all(p.get("quire") not in (None, "?") for p in pages) else "block10")
    out["overall"] = {m: dict(bits_per_token=v[0] / v[1], bits_per_char=v[0] / v[2], n_tokens=v[1])
                      for m, v in tot.items() if v[1]}
    out["by_section"] = {}
    for sec, d in per_sec.items():
        row = {m: v[0] / v[1] for m, v in d.items() if v[1]}
        row["winner"] = min(row, key=row.get)
        row["n_tokens"] = d["markov3"][1]
        out["by_section"][sec] = row
    out["copy_gain_bits"] = {nm: out["overall"]["markov3"]["bits_per_token"] - out["overall"][nm]["bits_per_token"]
                             for nm in copy_names}
    return out


# ----------------------------------------------------------------------------
# nulls
# ----------------------------------------------------------------------------
def bigram_pseudo_pages(pages, seed=SEED):
    """Sample a char-bigram pseudo-text (word boundaries as a symbol, same recipe as
    a6_solver.pseudo) with the same page/line shape and section/hand labels."""
    rng = random.Random(seed)
    trans = defaultdict(list)
    for w in flat_tokens(pages):
        q = ["_"] + list(w) + ["_"]
        for x, y in zip(q, q[1:]):
            trans[x].append(y)

    def word():
        while True:
            w, x = [], "_"
            while True:
                x = rng.choice(trans[x])
                if x == "_" or len(w) > 12:
                    break
                w.append(x)
            if w:
                return "".join(w)
    return [dict(p, lines=[[word() for _ in ln] for ln in p["lines"]]) for p in pages]


# ----------------------------------------------------------------------------
# 5. extra published signatures
# ----------------------------------------------------------------------------
def _mi_shuffle_corrected(a, b, rng, n_null=5):
    sa = sorted(set(a) | set(b))
    idx = {s: i for i, s in enumerate(sa)}
    V = len(sa)
    A = np.array([idx[x] for x in a]); B = np.array([idx[x] for x in b])
    mi, _ = _mi_from_pairs(A, B, V)
    null = [_mi_from_pairs(A, rng.permutation(B), V)[0] for _ in range(n_null)]
    return mi, mi - float(np.mean(null))


def extra_signatures(pages, seed=SEED):
    """Five published family-separating signatures (each shuffle-corrected or
    held-out where the plug-in estimate is biased).
      (a) edge-coupling MI: MI(last glyph of word, first glyph of next word) within a
          line, and MI(last glyph of a line's last word, first glyph of the next line)
          (Rozanova & Temerev, arXiv 2608.17096: ~0.2 bits Voynich, above all prose).
          L: low (word edges are nearly independent); C: can be high if code entries
          are chained by slot; G: high (next word is built from the previous one).
      (b) hapax profile: share of types that are hapax at 10k / 20k / 35k tokens
          (R&T: ~70% Voynich vs 41-60% controls).  L: 41-60%; C: depends on inventory
          but a bounded codebook gives a falling hapax share; G: high and steady.
      (c) Moran's I (lag 1) of word length along the token sequence (Gaskell &
          Bowern, CEUR 3313: positive in Voynich and human gibberish, negative in
          real text).  L: negative (long words alternate with short function words);
          C: ~0; G: positive (copied neighbours share length).
      (d) within-word glyph position bias: token-weighted mean over glyphs of the
          entropy of the glyph's relative-position quintile distribution (bits);
          low = position-locked (Gaskell & Bowern's single separating metric).
          L: high (~2 bits); C/G: low (slot-built words lock glyphs to positions).
      (e) directional asymmetry: leave-one-fold-out bits/char of an order-3 char
          model trained on words vs on reversed words (Parisel, arXiv 2604.19762:
          right-to-left optimisation within words).  L: ~0 asymmetry; a slot
          system (C or G) built from the right would favour reversed training.
    """
    rng = np.random.default_rng(seed)
    toks = flat_tokens(pages)
    out = {}
    # (a) edge coupling
    a, b = [], []
    for p in pages:
        for ln in p["lines"]:
            for u, v in zip(ln, ln[1:]):
                a.append(u[-1]); b.append(v[0])
    la, lb = [], []
    for p in pages:
        for l1, l2 in zip(p["lines"], p["lines"][1:]):
            la.append(l1[-1][-1]); lb.append(l2[0][0])
    out["edge_mi_word_raw"], out["edge_mi_word"] = _mi_shuffle_corrected(a, b, rng)
    out["edge_mi_line_raw"], out["edge_mi_line"] = _mi_shuffle_corrected(la, lb, rng)
    out["edge_n_word"], out["edge_n_line"] = len(a), len(la)
    # (b) hapax profile
    for n in (10000, 20000, 35000):
        if len(toks) >= n:
            c = Counter(toks[:n])
            out[f"hapax_share_{n // 1000}k"] = sum(1 for v in c.values() if v == 1) / len(c)
        else:
            out[f"hapax_share_{n // 1000}k"] = float("nan")
    c = Counter(toks)
    out["hapax_share_all"] = sum(1 for v in c.values() if v == 1) / len(c)
    # (c) Moran's I lag 1 on word length (along the token sequence, lines concatenated)
    x = np.array([len(t) for t in toks], dtype=float)
    z = x - x.mean()
    out["moran_I_wordlen_lag1"] = float(len(z) / (len(z) - 1) * (z[:-1] * z[1:]).sum() / (z * z).sum())
    # within-line only (avoid line-edge effects): pairs that do not cross a line break
    zz = []
    for p in pages:
        for ln in p["lines"]:
            L = np.array([len(t) for t in ln], dtype=float) - x.mean()
            zz.append((L[:-1] * L[1:]).sum() if len(L) > 1 else 0.0)
    npairs = sum(max(len(ln) - 1, 0) for p in pages for ln in p["lines"])
    out["moran_I_wordlen_lag1_within_line"] = float(len(z) / npairs * sum(zz) / (z * z).sum())
    # (d) position bias
    q = defaultdict(Counter)
    tot = Counter()
    for w in toks:
        L = len(w)
        for i, ch in enumerate(w):
            rp = i / (L - 1) if L > 1 else 0.5
            q[ch][min(4, int(rp * 5))] += 1
            tot[ch] += 1
    N = sum(tot.values())
    out["position_entropy_bits"] = sum(tot[ch] / N * entropy_counts(q[ch]) for ch in tot)
    out["position_entropy_max"] = math.log2(5)
    # (e) directional asymmetry
    folds = _folds(pages)
    bits = {"ltr": 0.0, "rtl": 0.0}
    nch = 0
    for fold in folds:
        test = set(fold)
        tr = flat_tokens([p for i, p in enumerate(pages) if i not in test])
        te = flat_tokens([pages[i] for i in fold])
        if not tr or not te:
            continue
        mf = CharMarkov(tr, 3); mr = CharMarkov([w[::-1] for w in tr], 3)
        for w in te:
            bits["ltr"] -= mf.logp_word(w); bits["rtl"] -= mr.logp_word(w[::-1]); nch += len(w) + 1
    out["bits_per_char_ltr"] = bits["ltr"] / nch
    out["bits_per_char_rtl"] = bits["rtl"] / nch
    out["directional_asymmetry_ltr_minus_rtl"] = (bits["ltr"] - bits["rtl"]) / nch
    return out
