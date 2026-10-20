"""Experiment 1: statistical profile of Voynich vs natural-language controls.

All texts are cut to the same token count so vocabulary measures compare.
"""
import math
import random
from collections import Counter

import numpy as np

import corpora

N = 25000  # common sample size (Kafka is the smallest control)


def char_entropies(words):
    s = " ".join(words) + " "
    c1 = Counter(s)
    n = len(s)
    h1 = -sum(v / n * math.log2(v / n) for v in c1.values())
    c2 = Counter(zip(s, s[1:]))
    n2 = sum(c2.values())
    h12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    c3 = Counter(zip(s, s[1:], s[2:]))
    n3 = sum(c3.values())
    h123 = -sum(v / n3 * math.log2(v / n3) for v in c3.values())
    return dict(alpha=len(c1), h1=h1, h2=h12 - h1, h3=h123 - h12)


def word_entropy_cond(words):
    c1 = Counter(words)
    c2 = Counter(zip(words, words[1:]))
    n1, n2 = len(words), len(words) - 1
    H1 = -sum(v / n1 * math.log2(v / n1) for v in c1.values())
    H12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return H1, H12 - H1


def zipf_slope(words):
    f = np.array(sorted(Counter(words).values(), reverse=True), float)
    r = np.arange(1, len(f) + 1)
    k = slice(0, min(1000, len(f)))
    return np.polyfit(np.log(r[k]), np.log(f[k]), 1)[0]


def mutual_info_gain(words, shuffles=3):
    """Word-bigram conditional entropy drop vs a shuffled copy (syntax signal)."""
    _, hc = word_entropy_cond(words)
    hs = []
    for i in range(shuffles):
        w = words[:]
        random.Random(i).shuffle(w)
        hs.append(word_entropy_cond(w)[1])
    return np.mean(hs) - hc


def profile(name, words):
    words = words[:N]
    c = Counter(words)
    ce = char_entropies(words)
    H1w, _ = word_entropy_cond(words)
    lens = [len(w) for w in words]
    redup = sum(a == b for a, b in zip(words, words[1:])) / (len(words) - 1)
    top10 = sum(v for _, v in c.most_common(10)) / len(words)
    return dict(
        text=name, tokens=len(words), types=len(c),
        hapax=sum(v == 1 for v in c.values()) / len(c),
        mean_len=np.mean(lens), sd_len=np.std(lens),
        alpha=ce["alpha"], h1=ce["h1"], h2=ce["h2"], h3=ce["h3"],
        Hword=H1w, syntax_gain=mutual_info_gain(words),
        zipf=zipf_slope(words), redup=redup * 100, top10=top10 * 100,
    )


def main():
    rows = []
    for tok in ["eva", "glyph", "glyph+"]:
        rows.append(profile(f"VMS {tok}", corpora.voynich(tokenization=tok)))
    rows.append(profile("VMS lang A", corpora.voynich(lambda r: r["lang"] == "A")))
    rows.append(profile("VMS lang B", corpora.voynich(lambda r: r["lang"] == "B")))
    for name in corpora.CONTROLS:
        rows.append(profile(name, corpora.control(name)))
    cols = ["tokens", "types", "hapax", "mean_len", "sd_len", "alpha", "h1", "h2", "h3",
            "Hword", "syntax_gain", "zipf", "redup", "top10"]
    print(f"{'text':18}" + "".join(f"{c:>11}" for c in cols))
    for r in rows:
        print(f"{r['text']:18}" + "".join(
            f"{r[c]:>11.3f}" if isinstance(r[c], float) else f"{r[c]:>11}" for c in cols))


if __name__ == "__main__":
    main()
