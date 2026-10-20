"""Experiment 6b: calibrate the solver score.

For a given LM language and BPE level k, report solver scores for:
  * VMS (real)
  * pseudo-VMS sampled from a unit-TRIGRAM model (keeps more word-internal shape)
  * real texts in OTHER languages, homophonically enciphered with VMS's unit
    count (what a genuine but wrong-language plaintext scores)
  * the same-language positive control (ceiling the solver actually attains)
"""
import random
import sys

import numpy as np

import corpora
import a6_solver as S


def pseudo3(seqs, n_words, seed):
    rng = random.Random(seed)
    trans = {}
    for s in seqs:
        q = ["^", "_"] + list(s) + ["_"]
        for x, y, z in zip(q, q[1:], q[2:]):
            trans.setdefault((x, y), []).append(z)
    out = []
    while len(out) < n_words:
        w, ctx = [], ("^", "_")
        while True:
            z = rng.choice(trans[ctx])
            if z == "_" or len(w) > 12:
                break
            w.append(z)
            ctx = (ctx[1], z)
        if w:
            out.append(tuple(w))
    return out


def run(seqs, lm, seed=0):
    seq, inv = S.encode_units(seqs)
    return S.solve(seq, len(inv), lm, seed=seed)[0]


def main():
    k = int(sys.argv[1]); lang = sys.argv[2]
    trains = {"latin": ["latin_augustine"], "italian": ["italian_dante"],
              "german": ["german_faust", "german_kafka"]}
    tests = {"latin": "latin_caesar", "italian": "italian_dante", "german": "german_kafka",
             "english": "english_alice"}
    lm = S.train_lm(sum((corpora.control(t) for t in trains[lang]), []))
    allv = S.voynich_units(k)
    vseq = allv[:S.SAMPLE_WORDS]
    nu = len({u for s in vseq for u in s})
    out = [f"k={k} LM={lang} units={nu} units/word={np.mean([len(s) for s in vseq]):.2f}"]
    out.append(f"  VMS real            {run(vseq, lm):.3f}")
    out.append(f"  pseudo-VMS trigram  {np.mean([run(pseudo3(allv, S.SAMPLE_WORDS, s), lm, s) for s in range(2)]):.3f}")
    for tl, name in tests.items():
        words = corpora.control(name)
        words = words[len(words) // 2: len(words) // 2 + S.SAMPLE_WORDS]  # held-out-ish half
        enc, _ = S.homophonic(words, max(nu, 22), seed=5)
        tag = "same-lang ceiling" if tl == lang else f"real {tl}"
        out.append(f"  {tag:19} {run(enc, lm):.3f}")
    print("\n".join(out), flush=True)


if __name__ == "__main__":
    main()
