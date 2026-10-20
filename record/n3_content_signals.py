"""N3: do the last content-specific signals survive against N2's habit generator?

After N2, transferable word order no longer separates meaning from meaningless
generation. Two signals remain that have been read as evidence of content:
  section vocabulary  within-hand NMI(NMF topic cluster, section), tested
                      against C1's quire-block null (results_b5.txt, results_c1.txt)
  page clustering     MI between a word and a word >= 3 lines away on the same
                      page, above a permuted-context null (m0 same_page_far)
N3 asks whether N2's matching generator reproduces them too.

PRE-REGISTRATION (written 2026-10-17 18:50 PDT before any run of this file;
nothing below is changed after results are seen)

Texts, per transliteration T in {ZL3b, RF1b, IT2a} (n1.load, unchanged):
  MS       the manuscript.
  HT 0.04  N2's matching setting: n1.gen_habit, p=0.04, seeds 1, 2, 3, with the same
           habit table and generator (c2 section lexicons, flow beta=1.5).
  HT 0     the same generator without habits, seeds 1, 2, 3 (reported, no
           effect on the verdict).
Caveat fixed in advance: the generator draws from c2's per-(hand, section)
lexicons, so some section vocabulary is built in. N3 therefore tests whether
a meaningless producer with section-keyed vocabulary and pair habits
reproduces each signal at the manuscript's strength, under the same nulls.
It does not test whether a generator without section vocabulary could.

Measures (existing code, unchanged):
  NMI, hand 1 (sections H, P) and hand 2 (B, H, T): c1.chunks (40-token chunks)
    -> b5.topics (NMF, k = sections + 2) -> c1.block_test. Reports NMI and the
    quire-block p, rng = numpy default_rng(20261017).
  Page MI: scoreboard.metrics_new.information_profile (seed 20261017, top
    500, n_boot 30). Reports same_page_far mi and se, word boundaries as given.

Decision rule, per signal S (NMI-h1, NMI-h2, pageMI) and transliteration T:
  S is evidence on T only if the manuscript passes its own null:
     NMI: quire-block p <= 0.05.   pageMI: mi - 2*se > 0.
  If it fails, S is NOT EVIDENCE on T.
  HT 0.04 matches S if:
     NMI: seed-mean NMI >= 0.75 x the manuscript's, AND quire-block p <= 0.05
          in at least 2 of 3 seeds.
     pageMI: seed-mean mi >= the manuscript's mi - 2 x its se.
  Per T: FALLS (evidence and matched), HOLDS (evidence, not matched), or NOT
  EVIDENCE.
  Per signal: FALLS if FALLS on >= 2 of 3 T; HOLDS if HOLDS on >= 2 of 3 T;
  NOT EVIDENCE if NOT EVIDENCE on >= 2 of 3 T; otherwise MIXED.
Interpretation fixed in advance:
  A signal that HOLDS is the sharpest remaining discriminator for content.
  If no signal HOLDS, no content-specific evidence remains among the tests
  run so far. That does not show the text is meaningless.

Run: python n3_content_signals.py  -> results_n3.txt
"""
from collections import Counter
from pathlib import Path

import numpy as np

import b5_nmf_topics as b5
import c1_quire_null as c1
import c2_section_generator as c2
import f3_flow_choice as f3
import n1_habit_table as N
from scoreboard import metrics_new as mn

OUT = Path(__file__).parent / "results_n3.txt"
SEEDS = (1, 2, 3)
WITHIN = (("1", ("H", "P")), ("2", ("B", "H", "T")))
SEED = 20261017
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def nmi_tests(by):
    rng = np.random.default_rng(SEED)
    ch = c1.chunks(by)
    out = {}
    for hand, secs in WITHIN:
        sub = [dict(c, blk=c["quire"] + c["sec"]) for c in ch if c["hand"] == hand and c["sec"] in secs]
        cl = b5.topics([c["text"] for c in sub], k=len(secs) + 2)
        r = c1.block_test(sub, cl, rng)
        out[f"h{hand}"] = (r["obs"], r["p"], r["nb"], r["na"])
    return out


def page_mi(by):
    pages = [dict(section=recs[0]["illus"], lines=[r["words"] for r in recs]) for recs in by.values()]
    r = mn.information_profile(pages, top=500, seed=SEED, n_boot=30)["word_boundaries_given"]["same_page_far"]
    return r["mi"], r["se"]


def measure(by):
    n = nmi_tests(by)
    m, se = page_mi(by)
    return dict(h1=n["h1"], h2=n["h2"], mi=m, se=se)


def fmt(r):
    return (f"NMI h1 {r['h1'][0]:.3f} (p {r['h1'][1]:.3f}, {r['h1'][2]} blocks)  NMI h2 {r['h2'][0]:.3f} (p {r['h2'][1]:.3f}, "
            f"{r['h2'][2]} blocks)  pageMI {r['mi']:+.4f} +- {r['se']:.4f}")


def main():
    emit("N3: section vocabulary and page clustering vs N2's habit generator (pre-registered in the docstring)")
    emit()
    per = {"NMI-h1": {}, "NMI-h2": {}, "pageMI": {}}
    for T, meta in N.TRANSLITS.items():
        by = N.load(meta)
        ms = measure(by)
        emit(f"=== {T} ===")
        emit(f"MS          {fmt(ms)}")
        g = c2.Gen(by)
        R = f3.ratio_table(by)
        table = N.habit_table(g)
        runs = {}
        for p in (0, 0.04):
            runs[p] = []
            for s in SEEDS:
                r = measure(N.gen_habit(g, R, s, p, table))
                runs[p].append(r)
                emit(f"HT p={p:<4} s{s} {fmt(r)}")
        ht = runs[0.04]
        for h in ("h1", "h2"):
            key = f"NMI-{h}"
            ev = ms[h][1] <= 0.05
            mean = float(np.mean([r[h][0] for r in ht]))
            npass = sum(r[h][1] <= 0.05 for r in ht)
            match = mean >= 0.75 * ms[h][0] and npass >= 2
            v = "NOT EVIDENCE" if not ev else "FALLS" if match else "HOLDS"
            per[key][T] = v
            emit(f"  {key}: MS {ms[h][0]:.3f} p {ms[h][1]:.3f} -> {'evidence' if ev else 'MS fails own null'};"
                 f" HT0.04 seed-mean {mean:.3f} (>= {0.75 * ms[h][0]:.3f}?), null passed in {npass}/3 seeds -> {v}")
        ev = ms["mi"] - 2 * ms["se"] > 0
        mean = float(np.mean([r["mi"] for r in ht]))
        match = mean >= ms["mi"] - 2 * ms["se"]
        v = "NOT EVIDENCE" if not ev else "FALLS" if match else "HOLDS"
        per["pageMI"][T] = v
        emit(f"  pageMI: MS {ms['mi']:+.4f} +- {ms['se']:.4f} -> {'evidence' if ev else 'MS fails own null'};"
             f" HT0.04 seed-mean {mean:+.4f} (>= {ms['mi'] - 2 * ms['se']:+.4f}?) -> {v}")
        emit()
    emit("SIGNAL VERDICTS")
    holds = []
    for key, d in per.items():
        c = Counter(d.values())
        v = ("FALLS" if c["FALLS"] >= 2 else "HOLDS" if c["HOLDS"] >= 2 else
             "NOT EVIDENCE" if c["NOT EVIDENCE"] >= 2 else "MIXED")
        if v == "HOLDS":
            holds.append(key)
        emit(f"  {key}: {v}   " + "  ".join(f"{t}={x}" for t, x in d.items()))
    emit(f"OVERALL: {'remaining discriminator(s): ' + ', '.join(holds) if holds else 'no content-specific signal HOLDS against the habit generator'}")


if __name__ == "__main__":
    main()
