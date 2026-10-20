"""N4: do the last content discriminators survive a habit generator with a
MANUSCRIPT-SIZED vocabulary? (closes OPEN O-039 and O-041)

Why. N2 (results_n2.txt) killed F1's transferable word order with n1.gen_habit
at p=0.04, and N3 (results_n3.txt) killed page MI with the same generator. That
generator has only ~1.6-1.8k types (manuscript ~7.0-7.3k, hapax share 0.68) and
h2 ~1.78. Red-team objection (O-039): a habit table over a 7k lexicon has far
fewer pair observations per type and may not transfer. Hand-1 within-hand
section NMI held in N3 by only 0.005-0.013 and was never tested against the
7k generator or a bifolio null on generated text (O-041).

PRE-REGISTRATION (written 2026-10-17 19:18 PDT before any run of this file;
nothing below is changed after results are seen)

Texts, per transliteration T in {ZL3b, RF1b, IT2a} (n1.load, unchanged):
  MS       the manuscript.
  HT7k     n1.gen_habit (copied here as gen_habit_k; the ONLY change is that the
           lexicon builder is told the (hand, section) key; the check mode
           asserts token-identical output to n1.gen_habit with c2's lexicon),
           habit p in {0, 0.04} (0.04 = N2's matching point; p=0 only for the
           power and h2-gap checks), seeds 1, 2, 3. Flow beta=1.5, M_CAND=8,
           p_seed=0.6, p_mut=0.6 (g.nb, MS single-glyph neighbours), all inherited.
     V1 circular      lexicon(key) = the manuscript's own tokens of that
                      (hand, section), every type, real counts (c2 'circular').
                      No calibration: whatever type count results is reported.
     V2 non-circular  lexicon(key) = c2's seed lexicon for that key (g.lexicon(rng),
                      300 types, as N2) PLUS a fixed list of synthetic forms for
                      that key, weight 1 each. Synthetic forms (built once per T,
                      seed 20261017): for key i (first-appearance order) take a
                      base = g.lexicon(Random(20261017 + i)); repeatedly pick a
                      parent uniformly from base + forms-so-far and apply ONE
                      c2-style glyph edit (substitute / insert / delete, chosen
                      uniformly; glyph drawn from T's character unigram); keep it
                      only if it is non-empty, not a manuscript type, and not
                      already made. Key i gets E_i = round(lam * N_i) forms, N_i =
                      the manuscript's token count of that key.
                      lam is fixed by ONE calibration, on seed 0 (never used for
                      measurement), p=0: bisection on lam in [0, 3], 14 steps,
                      target = the manuscript's type count for T; the evaluated lam
                      whose output types are closest to the target is used.
  Habit table (both variants): N1's rule (K=4 followers, sqrt-weight draws from
  the same type list, Dirichlet 0.5, seed 20261017), built once per T over the
  new lexicon's type list: V1 = every manuscript type (sqrt count weights);
  V2 = c2's type list (count >= 2, as N1) plus every synthetic form (weight 1).
  Check mode asserts the table builder reproduces n1.habit_table on c2's list.

Bifolio map. Folio -> sheet from the ZL3b IVTFF page headers in
data/ZL3b-n.txt ($Q quire, $B bifolio number within the quire; f1 and f8 share
Q=A B=1), the same source p1_bifolio_null.py used. Nothing downloaded; the
voynich.nu quire tables were not consulted. RF1b/IT2a use the same folio ids.
All 207 pages map; hand 1 H/P spans 27 sheets.

Measures, for MS and every HT7k text:
  N2 checks: n1.residual (quire split, page bootstrap B=1000; pages split no
    bootstrap), n1.profile (edge, h2, types, hapax, repeat).
  types check: |types - MS types| <= 0.15 x MS types (seed mean).
  NMI (p=0.04 texts and MS only), hand 1 (H, P) and hand 2 (B, H, T):
    quire-block null = n3.nmi_tests (c1.chunks -> b5.topics -> c1.block_test,
      blk = quire+section).
    bifolio null = the same chunks and NMF clusters, c1.block_test with
      blk = Q|B|section of the chunk's majority page (section labels permuted
      among bifolio-section blocks within hand), rng default_rng(20261017).
Code check (manuscript only, before the run): ZL3b MS must reprint N3's
NMI h1 0.275 p 0.018 and N2's residual +0.0461; the run aborts otherwise.

Decision rule.
 F1 (word order), per T and variant V:
   power      MS quire CI lower > seed-mean residual of V at p=0, else NO POWER
   resid      seed-mean residual(V, 0.04) >= MS CI lower
   edge       seed-mean edge >= 0.75 x MS edge
   h2         |h2(V,0.04) - h2(MS)| <= |h2(V,0) - h2(MS)| + 0.05
   repeat     repeat % <= 2 x MS
   types      seed-mean types within 15% of MS types
   (T, V) MATCH if power and all six pass; NOT 7K if the types check fails;
   else NO MATCH (failed checks listed).
   V overall: MATCH if MATCH on >= 2 of 3 T; NO MATCH if NO MATCH on >= 2; else MIXED.
   F1 CLOSED FOR GOOD if either variant is MATCH overall. REOPENED (for
   manuscript-sized producers only) if no variant is MATCH and some variant is
   NO MATCH overall. Otherwise INCONCLUSIVE.
 Section NMI, per signal S in {hand 1, hand 2} and T:
   MS bifolio p > 0.05  -> KILLED BY BIFOLIO (the bifolio null alone kills
                            the manuscript's own signal on T)
   else MS quire p > 0.05 -> NOT EVIDENCE
   else V matches if: V passes the types check on T, seed-mean NMI >= 0.75 x
     MS NMI, and null p <= 0.05 in >= 2 of 3 seeds under the quire null AND in
     >= 2 of 3 seeds under the bifolio null.  FALLS if V1 or V2 matches
     (variant named), else HOLDS.
   Per signal: KILLED BY BIFOLIO if KILLED on >= 2 of 3 T; else FALLS if FALLS
   on >= 2; HOLDS if HOLDS on >= 2; NOT EVIDENCE if NOT EVIDENCE or KILLED on
   >= 2; else MIXED.
 Interpretation fixed in advance:
   F1 CLOSED: the small-lexicon objection fails; transferable word order is
   retired as content evidence for good. REOPENED: it separates the manuscript
   from manuscript-sized habit producers only.
   Hand-1 FALLS: no content-specific discriminator remains among the tests run
   so far (this does not show the text is meaningless). HOLDS: hand-1 section
   vocabulary is the one content-side signal that a 7k habit producer with
   section-keyed vocabulary does not reach under either null. KILLED BY
   BIFOLIO: the signal is sheet-level and not content evidence.

Run: python n4_habit7k.py --check  (manuscript only) ; python n4_habit7k.py -> results_n4.txt
"""
import random
import sys
from collections import Counter, OrderedDict
from itertools import accumulate
from pathlib import Path

import numpy as np

import b5_nmf_topics as b5
import c1_quire_null as c1
import c2_section_generator as c2
import f3_flow_choice as f3
import n1_habit_table as N
import n3_content_signals as n3
import vparse

OUT = Path(__file__).parent / "results_n4.txt"
SEEDS = (1, 2, 3)
P_HAB = 0.04
SEED = 20261017
LAM_HI, LAM_STEPS = 3.0, 14
TYPES_TOL = 0.15
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    if "--check" not in sys.argv:
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- bifolio map
def bifolio_map():
    """page id -> 'Q|B|' from the ZL3b IVTFF page headers ($Q quire, $B sheet in quire)."""
    out = {}
    for raw in vparse.DATA.read_text(encoding="ascii", errors="replace").splitlines():
        m = vparse.PAGE_RE.match(raw)
        if m:
            meta = dict(vparse.VAR_RE.findall(m.group(2)))
            out[m.group(1)] = f"{meta.get('Q', '?')}|{meta.get('B', '?')}|"
    return out


BMAP = bifolio_map()


def nmi_bifolio(by):
    rng = np.random.default_rng(SEED)
    ch = c1.chunks(by)
    out = {}
    for hand, secs in n3.WITHIN:
        sub = [dict(c, blk=BMAP[c["page"]] + c["sec"]) for c in ch if c["hand"] == hand and c["sec"] in secs]
        cl = b5.topics([c["text"] for c in sub], k=len(secs) + 2)
        r = c1.block_test(sub, cl, rng)
        out[f"h{hand}"] = (r["obs"], r["p"], r["nb"], r["na"])
    return out


# ---------------------------------------------------------------- generator
def habit_table_over(types, weights):
    """n1.habit_table's rule over an arbitrary type list (cum_weights: same draws, faster)."""
    rng = random.Random(N.TABLE_SEED)
    nrng = np.random.default_rng(N.TABLE_SEED)
    cum = list(accumulate(weights))
    table = {}
    for w in types:
        fol = rng.choices(types, cum_weights=cum, k=N.K_FOLLOW)
        table[w] = (fol, list(nrng.dirichlet([N.DIR_ALPHA] * N.K_FOLLOW)))
    return table


def gen_habit_k(g, R, seed, p_hab, table, lexicon, p_seed=0.6, p_mut=0.6):
    """n1.gen_habit, except lexicon(key, rng) builds the lexicon of a (hand, section) key."""
    rng = random.Random(seed)
    lex = {}

    def draw(r):
        key = (r["hand"], r["illus"])
        if key not in lex:
            ws, wt = lexicon(key, rng)
            lex[key] = (ws, list(accumulate(wt)))
        return rng.choices(lex[key][0], cum_weights=lex[key][1])[0]

    def mutate(w):
        if rng.random() < p_mut and w in g.nb:
            c, wt = g.nb[w]
            return rng.choices(c, wt)[0]
        return w

    out = {}
    for page, recs in g.by.items():
        lines = []
        for li, r in enumerate(recs):
            line = []
            for _ in range(len(r["words"])):
                cands = []
                for _ in range(f3.M_CAND):
                    if line and p_hab and line[-1] in table and rng.random() < p_hab:
                        cands.append(rng.choices(*table[line[-1]])[0])
                        continue
                    if li == 0 or rng.random() < p_seed:
                        w = draw(r)
                    else:
                        w = rng.choice([x for l in lines for x in l] + line)
                    cands.append(mutate(w))
                if line:
                    w = rng.choices(cands, [R(line[-1][-1], c[0]) ** N.BETA for c in cands])[0]
                else:
                    w = cands[0]
                line.append(w)
            lines.append(line)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


def keys_in_order(by):
    return list(OrderedDict.fromkeys((r["hand"], r["illus"]) for recs in by.values() for r in recs))


def synth_forms(g, by):
    """Per key, LAM_HI * N_key synthetic forms in growth order (prefixes are used)."""
    rng = random.Random(SEED)
    chars = Counter(ch for w in g.freq.elements() for ch in w)
    alph, aw = list(chars), list(accumulate(chars.values()))
    ntok = Counter((r["hand"], r["illus"]) for recs in by.values() for r in recs for _ in r["words"])
    made, out = set(), {}
    for i, key in enumerate(keys_in_order(by)):
        base = g.lexicon(random.Random(SEED + i))[0]
        forms, want = [], round(LAM_HI * ntok[key])
        while len(forms) < want:
            w = rng.choice(base) if rng.random() < len(base) / (len(base) + len(forms)) else rng.choice(forms)
            j = rng.randrange(len(w) + 1)
            op = rng.randrange(3)
            c = rng.choices(alph, cum_weights=aw)[0]
            if op == 0 and j < len(w):
                v = w[:j] + c + w[j + 1:]
            elif op == 1:
                v = w[:j] + c + w[j:]
            elif j < len(w):
                v = w[:j] + w[j + 1:]
            else:
                continue
            if v and v not in g.freq and v not in made:
                made.add(v)
                forms.append(v)
        out[key] = forms
    return out, ntok


class V1:
    name = "V1 circular"

    def __init__(self, g, by):
        self.g = g
        types = list(g.freq)
        self.table = habit_table_over(types, [g.freq[w] ** 0.5 for w in types])

    def lexicon(self, key, rng):
        c = self.g.real[key]
        ws = list(c)
        return ws, [c[w] for w in ws]


class V2:
    name = "V2 synthetic"

    def __init__(self, g, by, R, target):
        self.g = g
        self.forms, self.ntok = synth_forms(g, by)
        self.table = {}
        lo, hi, tried = 0.0, LAM_HI, []
        for _ in range(LAM_STEPS):
            lam = (lo + hi) / 2
            self.lam = lam
            t = N.profile(gen_habit_k(g, R, 0, 0, {}, self.lexicon))["types"]
            tried.append((abs(t - target), lam, t))
            lo, hi = (lam, hi) if t < target else (lo, lam)
        _, self.lam, self.cal_types = min(tried)
        self.cal = tried
        extra = [f for k in self.forms for f in self.forms[k][:self.n(k)]]
        types = g.types + extra
        self.table = habit_table_over(types, g.tw + [1.0] * len(extra))
        self.n_extra = len(extra)

    def n(self, key):
        return round(self.lam * self.ntok[key])

    def lexicon(self, key, rng):
        ws, wt = self.g.lexicon(rng)
        ex = self.forms[key][:self.n(key)]
        return ws + ex, wt + [1] * len(ex)


# ---------------------------------------------------------------- measures
def fmt_nmi(q, b):
    return "  ".join(f"NMI {h} {q[h][0]:.3f} (quire p {q[h][1]:.3f}/{q[h][2]}bl, bifolio p {b[h][1]:.3f}/{b[h][2]}bl)"
                     for h in ("h1", "h2"))


def check():
    """Manuscript-only code check plus generator/table equivalence (no HT7k output)."""
    by = N.load(N.TRANSLITS["ZL3b"])
    q = n3.nmi_tests(by)
    b = nmi_bifolio(by)
    res, ci = N.residual(by, "quires")
    print(f"ZL3b MS residual quires {res:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]  {fmt_nmi(q, b)}")
    ok = round(q["h1"][0], 3) == 0.275 and round(q["h1"][1], 3) == 0.018 and round(res, 4) == 0.0461
    g = c2.Gen(by)
    R = f3.ratio_table(by)
    t1 = N.habit_table(g)
    t2 = habit_table_over(g.types, g.tw)
    same_t = t1 == t2
    a = N.gen_habit(g, R, 1, P_HAB, t1)
    bb = gen_habit_k(g, R, 1, P_HAB, t2, lambda k, rng: g.lexicon(rng))
    same_g = all([r["words"] for r in a[p]] == [r["words"] for r in bb[p]] for p in a)
    print(f"reprints N3/N2: {ok}   habit table identical: {same_t}   gen_habit_k == n1.gen_habit: {same_g}")
    print(f"pages mapped to bifolios: {sum(p in BMAP for p in by)}/{len(by)}")
    return ok and same_t and same_g


def main():
    if not check():
        print("CODE CHECK FAILED - not running")
        sys.exit(1)
    emit("N4: habit generator with a manuscript-sized lexicon (HT7k) vs F1 word order and within-hand section NMI")
    emit("pre-registered in the docstring; code check passed (ZL3b MS reprints N3 NMI h1 0.275 p 0.018, N2 residual +0.0461;"
         " gen_habit_k and the table builder reproduce n1 exactly)")
    emit()
    f1v = {"V1 circular": {}, "V2 synthetic": {}}
    nv = {"h1": {}, "h2": {}}
    for T, meta in N.TRANSLITS.items():
        by = N.load(meta)
        ms = N.profile(by)
        ms_q, ms_ci = N.residual(by, "quires")
        ms_p, ms_pci = N.residual(by, "pages")
        mq, mb = n3.nmi_tests(by), nmi_bifolio(by)
        emit(f"=== {T} ===")
        emit(f"MS   residual quires {ms_q:+.4f} [{ms_ci[0]:+.4f}, {ms_ci[1]:+.4f}]  pages {ms_p:+.4f}  edge {ms['edge']:+.3f}"
             f"  h2 {ms['h2']:.3f}  types {ms['types']}  hapax {ms['hapax']:.3f}  repeat {ms['redup']:.2f}%")
        emit(f"MS   {fmt_nmi(mq, mb)}")
        g = c2.Gen(by)
        R = f3.ratio_table(by)
        variants = [V1(g, by), V2(g, by, R, ms["types"])]
        v2 = variants[1]
        emit(f"V2 calibration (seed 0, p=0): lam={v2.lam:.4f} -> types {v2.cal_types} (target {ms['types']});"
             f" {v2.n_extra} synthetic forms; steps " + " ".join(f"{l:.3f}:{t}" for _, l, t in v2.cal))
        nmi_runs = {}
        for V in variants:
            rows = {}
            for p in (0, P_HAB):
                res = []
                for s in SEEDS:
                    gb = gen_habit_k(g, R, s, p, V.table, V.lexicon)
                    q, qci = N.residual(gb, "quires")
                    pg, _ = N.residual(gb, "pages", boot=False)
                    pr = N.profile(gb)
                    line = (f"{V.name} p={p:<4} s{s}  residual quires {q:+.4f} [{qci[0]:+.4f}, {qci[1]:+.4f}]  pages {pg:+.4f}"
                            f"  edge {pr['edge']:+.3f}  h2 {pr['h2']:.3f}  types {pr['types']}  hapax {pr['hapax']:.3f}  repeat {pr['redup']:.2f}%")
                    d = dict(q=q, **pr)
                    if p:
                        d["nq"], d["nb"] = n3.nmi_tests(gb), nmi_bifolio(gb)
                        line += "\n      " + fmt_nmi(d["nq"], d["nb"])
                    res.append(d)
                    emit(line)
                rows[p] = res
            nmi_runs[V.name] = rows[P_HAB]
            m = {p: {k: float(np.mean([r[k] for r in rows[p]])) for k in ("q", "edge", "h2", "types", "hapax", "redup")}
                 for p in rows}
            r, b0 = m[P_HAB], m[0]
            power = ms_ci[0] > b0["q"]
            checks = dict(resid=r["q"] >= ms_ci[0], edge=r["edge"] >= 0.75 * ms["edge"],
                          h2=abs(r["h2"] - ms["h2"]) <= abs(b0["h2"] - ms["h2"]) + 0.05,
                          repeat=r["redup"] <= 2 * ms["redup"], types=abs(r["types"] - ms["types"]) <= TYPES_TOL * ms["types"])
            v = ("NOT 7K" if not checks["types"] else "NO POWER" if not power else
                 "MATCH" if all(checks.values()) else "NO MATCH")
            f1v[V.name][T] = (v, checks["types"])
            emit(f"  F1 {V.name}: p=0 mean {b0['q']:+.4f} (power {'OK' if power else 'NO'}); p=0.04 mean residual {r['q']:+.4f}"
                 f" edge {r['edge']:+.3f} h2 {r['h2']:.3f} types {r['types']:.0f} hapax {r['hapax']:.3f} repeat {r['redup']:.2f}%  "
                 + "  ".join(f"{k}={'ok' if x else 'FAIL'}" for k, x in checks.items()) + f"  -> {v}")
        for h in ("h1", "h2"):
            obs, pq, pb = mq[h][0], mq[h][1], mb[h][1]
            matched = []
            for V in variants:
                rs = nmi_runs[V.name]
                mean = float(np.mean([x["nq"][h][0] for x in rs]))
                nq = sum(x["nq"][h][1] <= 0.05 for x in rs)
                nb_ = sum(x["nb"][h][1] <= 0.05 for x in rs)
                ok = f1v[V.name][T][1] and mean >= 0.75 * obs and nq >= 2 and nb_ >= 2
                if ok:
                    matched.append(V.name)
                emit(f"  NMI-{h} {V.name}: seed-mean {mean:.3f} (>= {0.75 * obs:.3f}?) quire null passed {nq}/3,"
                     f" bifolio null passed {nb_}/3, types ok {f1v[V.name][T][1]} -> {'match' if ok else 'no match'}")
            v = ("KILLED BY BIFOLIO" if pb > 0.05 else "NOT EVIDENCE" if pq > 0.05 else
                 "FALLS" if matched else "HOLDS")
            nv[h][T] = v
            emit(f"  NMI-{h}: MS {obs:.3f} quire p {pq:.3f} bifolio p {pb:.3f} -> {v}" + (f" (matched by {', '.join(matched)})" if matched and v == "FALLS" else ""))
        emit()
    emit("VERDICTS")
    over = {}
    for V, d in f1v.items():
        c = Counter(x[0] for x in d.values())
        over[V] = "MATCH" if c["MATCH"] >= 2 else "NO MATCH" if c["NO MATCH"] >= 2 else "MIXED"
        emit(f"  F1 {V}: {over[V]}   " + "  ".join(f"{t}={x[0]}" for t, x in d.items()))
    f1 = ("CLOSED FOR GOOD" if "MATCH" in over.values() else
          "REOPENED for manuscript-sized producers" if "NO MATCH" in over.values() else "INCONCLUSIVE")
    sig = {}
    for h, d in nv.items():
        c = Counter(d.values())
        sig[h] = ("KILLED BY BIFOLIO" if c["KILLED BY BIFOLIO"] >= 2 else "FALLS" if c["FALLS"] >= 2 else
                  "HOLDS" if c["HOLDS"] >= 2 else
                  "NOT EVIDENCE" if c["NOT EVIDENCE"] + c["KILLED BY BIFOLIO"] >= 2 else "MIXED")
        emit(f"  NMI-{h}: {sig[h]}   " + "  ".join(f"{t}={x}" for t, x in d.items()))
    emit(f"VERDICT: F1 {f1}; hand-1 section NMI {sig['h1']}; hand-2 section NMI {sig['h2']}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    main()
