"""vx01_seg_mdl.py - MDL prefix/core/suffix segmenter for the X-01 plan (script 1).

Plan: PLAN-X01-v5.1 (SHA256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393), sections 4 (A1 rows), 6.
Frozen BEFORE any A1 book exists (plan 4, freeze order step 1). Never tuned on A1 books.
All results from this file are UNVERIFIED until the Independent Verifier signs.
Deterministic. No random numbers, no seeds. No import of SlotSegmenter or any other project segmenter.

What it is (own, simple, written from the textbook two-part MDL idea; not copied from project code)
  Word = prefix + core + suffix, prefix in P or "", suffix in S or "", core non-empty.
  Cost of a model and data, in bits:
    L = L_lex + L_data
    L_lex  = sum over distinct units u of each stream (prefix, core, suffix; non-empty only)
             of (len(u) + 1) * log2(A + 1)          (spell the unit once; A = glyphs seen in training)
    L_data = 3 * N * log2(N) - sum over units c_u * log2(c_u)   (all three streams, empty units included;
             this is N * (H_prefix + H_core + H_suffix) with maximum-likelihood unit rates)
  Candidate affixes: glyph strings of length 1..MAX_AFFIX_LEN that start (prefixes) or end (suffixes)
  at least MIN_SHARE of the training tokens, token-weighted.
  Fit: start with every word type whole (no affix). (1) Greedy affix additions: at each step, for every
  candidate affix not yet in the inventory, compute the exact change of L if ALL word types that can use
  it switch to it at once (a type switches only from a shorter prefix of it, or a shorter suffix of it);
  accept the candidate with the largest drop of L; stop when no candidate lowers L (at most MAX_STEPS
  steps). (2) One removal pass over the inventory (an affix is dropped if its removal lowers L).
  (3) PASSES passes of coordinate descent over single word types in a fixed order (count desc, then
  string): each type takes the (prefix, suffix) option that lowers L the most. Final P and S = affixes
  still used. Segment(w) for any word: choose, by final unit costs, the
  (prefix, suffix) that minimises -log2 P(prefix) - log2 P(core) - log2 P(suffix); an unseen core
  costs its spelling cost. Ties: fewer affix glyphs first, then longer prefix, then longer suffix, then
  the order of strings. Words shorter than 2 glyphs are never split.
Fixed constants (arbitrary, chosen now, never tuned): MAX_AFFIX_LEN=3, MIN_SHARE=0.002, PASSES=4, MAX_STEPS=300.
Interface: SegMDL(tokens).segment(w) -> (prefix, core, suffix); prefix and suffix may be "".
Library only: never started directly, no dev log of its own.
"""
from __future__ import annotations

import math
from collections import Counter

MAX_AFFIX_LEN = 3
MIN_SHARE = 0.002
PASSES = 4
MAX_STEPS = 300


def _clogc(c: int) -> float:
    return c * math.log2(c) if c > 0 else 0.0


class SegMDL:
    def __init__(self, tokens):
        freq = Counter(tokens)
        self.N = sum(freq.values())
        glyphs = set("".join(freq))
        self.spell_bit = math.log2(len(glyphs) + 1)
        n = max(1, self.N)
        pc, sc = Counter(), Counter()
        for w, c in freq.items():
            for k in range(1, MAX_AFFIX_LEN + 1):
                if len(w) > k:
                    pc[w[:k]] += c
                    sc[w[-k:]] += c
        self.cand_p = frozenset(a for a, c in pc.items() if c / n >= MIN_SHARE)
        self.cand_s = frozenset(a for a, c in sc.items() if c / n >= MIN_SHARE)
        types = sorted(freq, key=lambda w: (-freq[w], w))
        cnt = {0: Counter(), 1: Counter(), 2: Counter()}
        assign = {}
        for w in types:
            assign[w] = ("", "")
            cnt[0][""] += freq[w]
            cnt[1][w] += freq[w]
            cnt[2][""] += freq[w]
        self._cnt = cnt
        self.freq = freq
        by_p = {a: [] for a in self.cand_p}
        by_s = {a: [] for a in self.cand_s}
        for w in types:
            for k in range(1, MAX_AFFIX_LEN + 1):
                if len(w) > k:
                    if w[:k] in by_p:
                        by_p[w[:k]].append(w)
                    if w[len(w) - k:] in by_s:
                        by_s[w[len(w) - k:]].append(w)
        cands = [(0, a) for a in sorted(by_p, key=lambda x: (len(x), x))] + \
                [(2, a) for a in sorted(by_s, key=lambda x: (len(x), x))]
        inv = {0: set(), 2: set()}
        lists = {0: by_p, 2: by_s}
        for _ in range(MAX_STEPS):
            best, best_d, best_moves = None, -1e-9, None
            for st, a in cands:
                if a in inv[st]:
                    continue
                moves = self._moves_add(st, a, lists[st][a], assign)
                if not moves:
                    continue
                d = self._batch_delta(moves, cnt)
                if d < best_d:
                    best, best_d, best_moves = (st, a), d, moves
            if best is None:
                break
            self._apply(best_moves, assign, cnt)
            inv[best[0]].add(best[1])
        for st in (0, 2):
            for a in sorted(inv[st], key=lambda x: (len(x), x)):
                moves = self._moves_remove(st, a, lists[st][a], assign, inv)
                if moves and self._batch_delta(moves, cnt) < -1e-9:
                    self._apply(moves, assign, cnt)
                    inv[st].discard(a)
        for _ in range(PASSES):
            changed = False
            for w in types:
                best = self._best_option(w, freq[w], assign[w], cnt)
                if best != assign[w]:
                    self._move(w, freq[w], assign[w], best, cnt)
                    assign[w] = best
                    changed = True
            if not changed:
                break
        self.prefixes = frozenset(p for p in cnt[0] if p and cnt[0][p] > 0)
        self.suffixes = frozenset(s for s in cnt[2] if s and cnt[2][s] > 0)
        self.core_count = cnt[1]
        self.cnt = cnt
        self._cache = {}

    # --- helpers ---------------------------------------------------------------------------------
    def _greedy_cut(self, w):
        p = ""
        for k in range(MAX_AFFIX_LEN, 0, -1):
            if len(w) - k >= 1 and w[:k] in self.cand_p:
                p = w[:k]
                break
        s = ""
        for k in range(MAX_AFFIX_LEN, 0, -1):
            if len(w) - len(p) - k >= 1 and w[len(w) - k:] in self.cand_s:
                s = w[len(w) - k:]
                break
        return p, s

    def _options(self, w):
        ps = [""] + [w[:k] for k in range(1, MAX_AFFIX_LEN + 1) if len(w) > k and w[:k] in self.cand_p]
        ss = [""] + [w[len(w) - k:] for k in range(1, MAX_AFFIX_LEN + 1) if len(w) > k and w[len(w) - k:] in self.cand_s]
        out = []
        for p in ps:
            for s in ss:
                if len(w) - len(p) - len(s) >= 1:
                    out.append((p, s))
        return out

    def _units(self, w, ps):
        p, s = ps
        return (p, w[len(p):len(w) - len(s)], s)

    def _lex(self, stream, u, present):
        if stream == 1 or u:
            return (len(u) + 1) * self.spell_bit
        return 0.0

    def _delta_cost(self, w, n, old, new, cnt):
        """Exact change of L when type w (n tokens) moves from option old to option new."""
        uo, un = self._units(w, old), self._units(w, new)
        delta = 0.0
        # net count change per (stream, unit)
        net = {}
        for st in range(3):
            net[(st, uo[st])] = net.get((st, uo[st]), 0) - n
            net[(st, un[st])] = net.get((st, un[st]), 0) + n
        for (st, u), d in net.items():
            if d == 0:
                continue
            c0 = cnt[st].get(u, 0)
            c1 = c0 + d
            delta -= _clogc(c1) - _clogc(c0)              # L_data = const - sum c log c
            if st == 1 or u:
                if c0 == 0 and c1 > 0:
                    delta += (len(u) + 1) * self.spell_bit
                elif c0 > 0 and c1 == 0:
                    delta -= (len(u) + 1) * self.spell_bit
        return delta

    def _best_option(self, w, n, cur, cnt):
        best, best_d = cur, 0.0
        for opt in self._options(w):
            if opt == cur:
                continue
            d = self._delta_cost(w, n, cur, opt, cnt)
            if d < best_d - 1e-12:
                best, best_d = opt, d
        return best

    def _move(self, w, n, old, new, cnt):
        uo, un = self._units(w, old), self._units(w, new)
        for st in range(3):
            cnt[st][uo[st]] -= n
            if cnt[st][uo[st]] == 0:
                del cnt[st][uo[st]]
            cnt[st][un[st]] += n

    def _moves_add(self, st, a, tlist, assign):
        out = []
        for w in tlist:
            p0, s0 = assign[w]
            if st == 0:
                if p0 == a or not a.startswith(p0) or len(w) - len(a) - len(s0) < 1:
                    continue
                out.append((w, (p0, s0), (a, s0)))
            else:
                if s0 == a or not a.endswith(s0) or len(w) - len(p0) - len(a) < 1:
                    continue
                out.append((w, (p0, s0), (p0, a)))
        return out

    def _moves_remove(self, st, a, tlist, assign, inv):
        out = []
        for w in tlist:
            p0, s0 = assign[w]
            if st == 0 and p0 == a:
                alts = [""] + [w[:k] for k in range(1, len(a)) if w[:k] in inv[0]]
                p1 = max(alts, key=len)
                out.append((w, (p0, s0), (p1, s0)))
            elif st == 2 and s0 == a:
                alts = [""] + [w[len(w) - k:] for k in range(1, len(a)) if w[len(w) - k:] in inv[2]]
                s1 = max(alts, key=len)
                out.append((w, (p0, s0), (p0, s1)))
        return out

    def _batch_delta(self, moves, cnt):
        net = {}
        for w, old, new in moves:
            n = self.freq[w]
            uo, un = self._units(w, old), self._units(w, new)
            for st in range(3):
                net[(st, uo[st])] = net.get((st, uo[st]), 0) - n
                net[(st, un[st])] = net.get((st, un[st]), 0) + n
        delta = 0.0
        for (st, u), d in net.items():
            if d == 0:
                continue
            c0 = cnt[st].get(u, 0)
            c1 = c0 + d
            delta -= _clogc(c1) - _clogc(c0)
            if st == 1 or u:
                if c0 == 0 and c1 > 0:
                    delta += (len(u) + 1) * self.spell_bit
                elif c0 > 0 and c1 == 0:
                    delta -= (len(u) + 1) * self.spell_bit
        return delta

    def _apply(self, moves, assign, cnt):
        for w, old, new in moves:
            self._move(w, self.freq[w], old, new, cnt)
            assign[w] = new

    # --- public ----------------------------------------------------------------------------------
    def _unit_bits(self, st, u):
        c = self.cnt[st].get(u, 0)
        if c > 0:
            return -math.log2(c / self.N)
        # unseen unit: spelling cost plus one-count escape
        return (len(u) + 1) * self.spell_bit + math.log2(self.N + 1)

    def segment(self, w: str):
        r = self._cache.get(w)
        if r is not None:
            return r
        if len(w) < 2:
            r = ("", w, "")
        else:
            best, best_key = None, None
            for p, s in self._options_final(w):
                c = w[len(p):len(w) - len(s)]
                bits = (self._unit_bits(0, p) + self._unit_bits(1, c) + self._unit_bits(2, s))
                key = (round(bits, 9), len(p) + len(s), -len(p), -len(s), p, s)
                if best_key is None or key < best_key:
                    best, best_key = (p, c, s), key
            r = best
        self._cache[w] = r
        return r

    def _options_final(self, w):
        ps = [""] + [w[:k] for k in range(1, MAX_AFFIX_LEN + 1) if len(w) > k and w[:k] in self.prefixes]
        ss = [""] + [w[len(w) - k:] for k in range(1, MAX_AFFIX_LEN + 1) if len(w) > k and w[len(w) - k:] in self.suffixes]
        return [(p, s) for p in ps for s in ss if len(w) - len(p) - len(s) >= 1]
