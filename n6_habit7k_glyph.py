"""N6: F1 word order and within-hand section NMI against a 7k-type habit
generator with a WORD-INTERNAL GLYPH-MODEL lexicon (closes OPEN O-042).

Why. N4 (results_n4.txt) tested O-039 and O-041 with two variants:
  - V1 circular (real section vocabulary) reached only ~4.0k types (NOT 7K).
  - V2 synthetic generated rare forms via recursive uniform random character
    edits without neighbour links in g.nb, which drove character entropy to
    h2 = 3.27 (vs MS 2.11), immediate repeats to 10-12% (vs 0.94%), and
    p=0 quire residual to +0.037..+0.067 (NO POWER).
OPEN O-042 specifies the clean resolution:
  "Pre-register a V2 whose new forms come from a glyph model of the
   manuscript's word-internal transitions (no word pairs), requiring types
   within 15% AND h2 within 0.1 of MS before measurement; rerun N4's F1 and
   NMI rules unchanged by importing n4_habit7k.py."

PRE-REGISTRATION (written 2026-10-17 19:35 PDT before any run of this file;
SHA-256 recorded in n6_habit7k_glyph.prereg.sha256; nothing below is changed
after results are seen)

Texts, per transliteration T in {ZL3b, RF1b, IT2a} (n1.load, unchanged):
  MS          the manuscript.
  V2_glyph    n4.gen_habit_k with p in {0, 0.04}, seeds 1, 2, 3, flow beta=1.5,
              M_CAND=8, p_seed=0.6, p_mut=0.6 (all inherited from N1/N2/N4):
              1. Word-internal order-2 character Markov model M2(T):
                 Fitted strictly on T's word-internal character transitions
                 weighted by token count (start state '^^', end state '$';
                 zero cross-word or word-pair inputs).
              2. Synthetic forms per (hand, section) key i (seed 20261017):
                 Base lexicon = g.lexicon(Random(20261017 + i))[0] (300 types).
                 Each synthetic form v is sampled from M2(T) (length 2..10,
                 accepted if v not in g.freq and v not in made) and linked in
                 g.nb to a parent u drawn uniformly from base (so page-copied
                 synthetic words mutate at p_mut=0.6 to single-edit neighbours
                 of u rather than repeating identically).
              3. Calibration (seed 0, p=0 ONLY, never used for measurement):
                 Key i receives E_i = round(lam * N_i) synthetic forms (weight 1
                 each), where lam in [0, 3.0] is fixed by 14-step bisection on
                 seed 0, p=0 to match T's manuscript type count.
                 Pre-measurement gate (O-042): on seed 0 at p=0, the calibrated
                 generator must satisfy BOTH:
                   - |types(seed 0, p=0) - MS types| <= 0.15 * MS types
                   - |h2(seed 0, p=0) - MS h2| <= 0.10
              4. Habit table: n4.habit_table_over(g.types + extra,
                 g.tw + [1.0]*len(extra)), built once per T with seed 20261017
                 (K=4 followers, Dirichlet 0.5, never from MS word pairs).

Measures & Decision Rules (imported unchanged from n4_habit7k.py):
  F1 (word order), per T:
    power      MS quire CI lower > seed-mean residual(p=0), else NO POWER
    resid      seed-mean residual(p=0.04) >= MS quire CI lower
    edge       seed-mean edge >= 0.75 * MS edge
    h2         |h2(p=0.04) - MS h2| <= |h2(p=0) - MS h2| + 0.05
               AND |h2(p=0) - MS h2| <= 0.10 (O-042 precondition)
    repeat     repeat % <= 2 * MS repeat %
    types      |types(p=0.04) - MS types| <= 0.15 * MS types
    T verdict: NOT 7K if types fails; BAD H2 if |h2(p=0) - MS h2| > 0.10;
    NO POWER if power fails; MATCH if all pass; else NO MATCH.
    Overall F1: CLOSED FOR GOOD if MATCH on >= 2 of 3 T; REOPENED (for 7k
    producers) if NO MATCH on >= 2 of 3 T; else INCONCLUSIVE.
  Section NMI, per signal S in {hand 1, hand 2} and T (same as N4):
    MS bifolio p > 0.05 -> KILLED BY BIFOLIO; else MS quire p > 0.05 ->
    NOT EVIDENCE; else FALLS if V2_glyph passes types & h2 checks, seed-mean
    NMI >= 0.75 * MS NMI, quire null p <= 0.05 in >= 2/3 seeds AND bifolio
    null p <= 0.05 in >= 2/3 seeds; else HOLDS.

Run: python n6_habit7k_glyph.py --check ; python n6_habit7k_glyph.py -> results_n6.txt
"""
import hashlib
import random
import sys
from collections import Counter, defaultdict
from itertools import accumulate
from pathlib import Path

import numpy as np

import c2_section_generator as c2
import f3_flow_choice as f3
import n1_habit_table as N
import n3_content_signals as n3
import n4_habit7k as n4

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_n6.txt"
STUB = HERE / "n6_habit7k_glyph.prereg.sha256"
SEEDS = n4.SEEDS
P_HAB = n4.P_HAB
SEED = n4.SEED
LAM_HI, LAM_STEPS = 3.0, 14
TYPES_TOL = 0.15
H2_TOL = 0.10
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    if "--check" not in sys.argv:
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def fit_char_markov2(freq):
    """Order-2 character Markov model fitted strictly on word-internal transitions."""
    trans = defaultdict(Counter)
    for w, c in freq.items():
        s = "^^" + w + "$"
        for i in range(2, len(s)):
            trans[s[i - 2:i]][s[i]] += c
    table = {}
    for ctx, cnt in trans.items():
        chars = sorted(cnt)
        cum = list(accumulate(cnt[ch] for ch in chars))
        table[ctx] = (chars, cum)
    return table


def sample_word_m2(table, rng, min_len=2, max_len=10):
    """Sample one word from the word-internal order-2 character Markov model."""
    for _ in range(100):
        ctx = "^^"
        out = []
        while len(out) <= max_len:
            if ctx not in table:
                break
            chars, cum = table[ctx]
            ch = rng.choices(chars, cum_weights=cum)[0]
            if ch == "$":
                if len(out) >= min_len:
                    return "".join(out)
                break
            out.append(ch)
            ctx = ctx[1] + ch
    return None


def synth_glyph_forms(g, by):
    """Per (hand, section) key, LAM_HI * N_key synthetic forms from word-internal M2."""
    rng = random.Random(SEED)
    m2 = fit_char_markov2(g.freq)
    ntok = Counter((r["hand"], r["illus"]) for recs in by.values() for r in recs for _ in r["words"])
    made, out, nb_links = set(), {}, {}
    for i, key in enumerate(n4.keys_in_order(by)):
        base = [w for w in g.lexicon(random.Random(SEED + i))[0] if w in g.nb]
        forms, want = [], round(LAM_HI * ntok[key])
        while len(forms) < want:
            v = sample_word_m2(m2, rng)
            if v and v not in g.freq and v not in made:
                made.add(v)
                forms.append(v)
                parent = rng.choice(base)
                nb_links[v] = g.nb[parent]
        out[key] = forms
    return out, ntok, nb_links


class V2Glyph:
    name = "V2_glyph"

    def __init__(self, g, by, R, target_types):
        self.g = g
        self.forms, self.ntok, nb_links = synth_glyph_forms(g, by)
        g.nb.update(nb_links)
        self.table = {}
        lo, hi, tried = 0.0, LAM_HI, []
        for _ in range(LAM_STEPS):
            lam = (lo + hi) / 2
            self.lam = lam
            pr = N.profile(n4.gen_habit_k(g, R, 0, 0, {}, self.lexicon))
            t = pr["types"]
            tried.append((abs(t - target_types), lam, t, pr["h2"], pr["hapax"], pr["redup"]))
            lo, hi = (lam, hi) if t < target_types else (lo, lam)
        _, self.lam, self.cal_types, self.cal_h2, self.cal_hapax, self.cal_redup = min(tried)
        self.cal = tried
        extra = [f for k in self.forms for f in self.forms[k][:self.n(k)]]
        types = g.types + extra
        self.table = n4.habit_table_over(types, g.tw + [1.0] * len(extra))
        self.n_extra = len(extra)

    def n(self, key):
        return round(self.lam * self.ntok[key])

    def lexicon(self, key, rng):
        ws, wt = self.g.lexicon(rng)
        ex = self.forms[key][:self.n(key)]
        return ws + ex, wt + [1] * len(ex)


def verify_prereg_hash():
    my_bytes = Path(__file__).resolve().read_bytes()
    my_hash = hashlib.sha256(my_bytes).hexdigest()
    if STUB.exists():
        first = STUB.read_text(encoding="utf-8").strip().splitlines()[0].split()[0]
        return my_hash, first == my_hash
    return my_hash, False


def check():
    ok_n4 = n4.check()
    by = N.load(N.TRANSLITS["ZL3b"])
    ms = N.profile(by)
    g = c2.Gen(by)
    R = f3.ratio_table(by)
    v2 = V2Glyph(g, by, R, ms["types"])
    t_ok = abs(v2.cal_types - ms["types"]) <= TYPES_TOL * ms["types"]
    h2_ok = abs(v2.cal_h2 - ms["h2"]) <= H2_TOL
    my_hash, hash_ok = verify_prereg_hash()
    print(f"ZL3b seed-0 p=0 calibration: lam={v2.lam:.4f} types={v2.cal_types} (target {ms['types']}, ok={t_ok})"
          f" h2={v2.cal_h2:.3f} (MS {ms['h2']:.3f}, gap={abs(v2.cal_h2 - ms['h2']):.3f}, ok={h2_ok})"
          f" hapax={v2.cal_hapax:.3f} repeat={v2.cal_redup:.2f}%  prereg_hash={my_hash[:16]} (match={hash_ok})")
    return ok_n4 and t_ok and h2_ok


def main():
    my_hash, hash_ok = verify_prereg_hash()
    if not n4.check():
        print("CODE CHECK FAILED - not running")
        sys.exit(1)
    emit(f"N6: 7k-type glyph-model habit generator (V2_glyph, O-042) vs F1 word order and within-hand section NMI")
    emit(f"prereg_sha256={my_hash} (stub_match={hash_ok}); imports n4_habit7k.py rules unchanged")
    emit()
    f1v = {}
    nv = {"h1": {}, "h2": {}}
    for T, meta in N.TRANSLITS.items():
        by = N.load(meta)
        ms = N.profile(by)
        ms_q, ms_ci = N.residual(by, "quires")
        ms_p, _ = N.residual(by, "pages", boot=False)
        mq, mb = n3.nmi_tests(by), n4.nmi_bifolio(by)
        emit(f"=== {T} ===")
        emit(f"MS       residual quires {ms_q:+.4f} [{ms_ci[0]:+.4f}, {ms_ci[1]:+.4f}]  pages {ms_p:+.4f}  edge {ms['edge']:+.3f}"
             f"  h2 {ms['h2']:.3f}  types {ms['types']}  hapax {ms['hapax']:.3f}  repeat {ms['redup']:.2f}%")
        emit(f"MS       {n4.fmt_nmi(mq, mb)}")
        g = c2.Gen(by)
        R = f3.ratio_table(by)
        V = V2Glyph(g, by, R, ms["types"])
        emit(f"V2_glyph calibration (seed 0, p=0): lam={V.lam:.4f} -> types {V.cal_types} (target {ms['types']}),"
             f" h2 {V.cal_h2:.3f}, hapax {V.cal_hapax:.3f}, repeat {V.cal_redup:.2f}%; {V.n_extra} synthetic forms")
        rows = {}
        for p in (0, P_HAB):
            res = []
            for s in SEEDS:
                gb = n4.gen_habit_k(g, R, s, p, V.table, V.lexicon)
                q, qci = N.residual(gb, "quires")
                pg, _ = N.residual(gb, "pages", boot=False)
                pr = N.profile(gb)
                line = (f"{V.name} p={p:<4} s{s}  residual quires {q:+.4f} [{qci[0]:+.4f}, {qci[1]:+.4f}]  pages {pg:+.4f}"
                        f"  edge {pr['edge']:+.3f}  h2 {pr['h2']:.3f}  types {pr['types']}  hapax {pr['hapax']:.3f}  repeat {pr['redup']:.2f}%")
                d = dict(q=q, **pr)
                if p:
                    d["nq"], d["nb"] = n3.nmi_tests(gb), n4.nmi_bifolio(gb)
                    line += "\n      " + n4.fmt_nmi(d["nq"], d["nb"])
                res.append(d)
                emit(line)
            rows[p] = res
        m = {p: {k: float(np.mean([r[k] for r in rows[p]])) for k in ("q", "edge", "h2", "types", "hapax", "redup")}
             for p in rows}
        r, b0 = m[P_HAB], m[0]
        power = ms_ci[0] > b0["q"]
        h2_pre = abs(b0["h2"] - ms["h2"]) <= H2_TOL
        checks = dict(
            resid=r["q"] >= ms_ci[0],
            edge=r["edge"] >= 0.75 * ms["edge"],
            h2=h2_pre and abs(r["h2"] - ms["h2"]) <= abs(b0["h2"] - ms["h2"]) + 0.05,
            repeat=r["redup"] <= 2 * ms["redup"],
            types=abs(r["types"] - ms["types"]) <= TYPES_TOL * ms["types"],
        )
        v = ("NOT 7K" if not checks["types"] else "BAD H2" if not h2_pre else
             "NO POWER" if not power else "MATCH" if all(checks.values()) else "NO MATCH")
        f1v[T] = (v, checks["types"] and h2_pre)
        emit(f"  F1 {V.name}: p=0 mean {b0['q']:+.4f} (power {'OK' if power else 'NO'}, h2_p0={b0['h2']:.3f} gap={abs(b0['h2'] - ms['h2']):.3f});"
             f" p=0.04 mean residual {r['q']:+.4f} edge {r['edge']:+.3f} h2 {r['h2']:.3f} types {r['types']:.0f}"
             f" hapax {r['hapax']:.3f} repeat {r['redup']:.2f}%  "
             + "  ".join(f"{k}={'ok' if x else 'FAIL'}" for k, x in checks.items()) + f"  -> {v}")
        rs = rows[P_HAB]
        for h in ("h1", "h2"):
            obs, pq, pb = mq[h][0], mq[h][1], mb[h][1]
            mean = float(np.mean([x["nq"][h][0] for x in rs]))
            nq = sum(x["nq"][h][1] <= 0.05 for x in rs)
            nb_ = sum(x["nb"][h][1] <= 0.05 for x in rs)
            ok = f1v[T][1] and mean >= 0.75 * obs and nq >= 2 and nb_ >= 2
            emit(f"  NMI-{h} {V.name}: seed-mean {mean:.3f} (>= {0.75 * obs:.3f}?) quire null passed {nq}/3,"
                 f" bifolio null passed {nb_}/3, types&h2 ok {f1v[T][1]} -> {'match' if ok else 'no match'}")
            nv_t = ("KILLED BY BIFOLIO" if pb > 0.05 else "NOT EVIDENCE" if pq > 0.05 else
                    "FALLS" if ok else "HOLDS")
            nv[h][T] = nv_t
            emit(f"  NMI-{h}: MS {obs:.3f} quire p {pq:.3f} bifolio p {pb:.3f} -> {nv_t}" + (" (matched by V2_glyph)" if ok and nv_t == "FALLS" else ""))
        emit()
    emit("VERDICTS")
    c = Counter(x[0] for x in f1v.values())
    over = "MATCH" if c["MATCH"] >= 2 else "NO MATCH" if c["NO MATCH"] >= 2 else "MIXED"
    emit(f"  F1 V2_glyph: {over}   " + "  ".join(f"{t}={x[0]}" for t, x in f1v.items()))
    f1_final = ("CLOSED FOR GOOD" if over == "MATCH" else
                "REOPENED for manuscript-sized producers" if over == "NO MATCH" else "INCONCLUSIVE")
    sig = {}
    for h, d in nv.items():
        ch = Counter(d.values())
        sig[h] = ("KILLED BY BIFOLIO" if ch["KILLED BY BIFOLIO"] >= 2 else "FALLS" if ch["FALLS"] >= 2 else
                  "HOLDS" if ch["HOLDS"] >= 2 else
                  "NOT EVIDENCE" if ch["NOT EVIDENCE"] + ch["KILLED BY BIFOLIO"] >= 2 else "MIXED")
        emit(f"  NMI-{h}: {sig[h]}   " + "  ".join(f"{t}={x}" for t, x in d.items()))
    emit(f"VERDICT: F1 {f1_final}; hand-1 section NMI {sig['h1']}; hand-2 section NMI {sig['h2']}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    main()
