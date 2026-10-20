"""Experiment 3: are labels referential?

If a label names the drawn object (plant part, star, nymph), the same word
should turn up in that page's running text more often than in other pages of
the same section. Null: permute label-sets among pages of the same section.
Also: do pages share vocabulary with their neighbours more than with distant
pages of the same section (topic locality)?
"""
import random
from collections import defaultdict

import numpy as np

import vparse


def main():
    recs = [r for r in vparse.load() if r["words"]]
    labels = defaultdict(list); text = defaultdict(set); sect = {}
    for r in recs:
        ws = [w for w in r["words"] if "?" not in w]
        sect[r["page"]] = r["illus"]
        if r["unit"].startswith("L"):
            labels[r["page"]] += ws
        elif r["unit"].startswith("P"):
            text[r["page"]].update(ws)
    pages = [p for p in labels if text.get(p)]

    def hit_rate(assign):
        h = n = 0
        for p in pages:
            for w in assign[p]:
                n += 1
                h += w in text[p]
        return h / n

    obs = hit_rate(labels)
    by_sec = defaultdict(list)
    for p in pages:
        by_sec[sect[p]].append(p)
    nulls = []
    for i in range(500):
        rng = random.Random(i)
        perm = {}
        for s, ps in by_sec.items():
            sh = ps[:]; rng.shuffle(sh)
            for a, b in zip(ps, sh):
                perm[a] = labels[b]
        nulls.append(hit_rate(perm))
    nulls = np.array(nulls)
    print(f"Pages with labels+text: {len(pages)}  label tokens: {sum(len(labels[p]) for p in pages)}")
    print(f"Label word found in own page text: {obs:.3f}; section-permuted null {nulls.mean():.3f}±{nulls.std():.3f};"
          f" p={np.mean(nulls >= obs):.3f}")
    for s, ps in sorted(by_sec.items()):
        o = sum(w in text[p] for p in ps for w in labels[p]) / max(1, sum(len(labels[p]) for p in ps))
        print(f"  section {s}: {len(ps)} pages, own-page hit {o:.3f}")

    # Topic locality among herbal pages: Jaccard of rare-word sets vs page distance
    order = [r["page"] for r in recs]
    seen = []
    for p in order:
        if p not in seen:
            seen.append(p)
    from collections import Counter
    freq = Counter(w for p in text for w in text[p])
    for s in ["H", "B", "S", "P"]:
        ps = [p for p in seen if sect.get(p) == s and text.get(p)]
        rare = {p: {w for w in text[p] if 2 <= freq[w] <= 20} for p in ps}
        near, far = [], []
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                a, b = rare[ps[i]], rare[ps[j]]
                if not a or not b:
                    continue
                jac = len(a & b) / len(a | b)
                (near if j - i <= 2 else far).append(jac)
        print(f"Section {s}: rare-word Jaccard adjacent(<=2 pages)={np.mean(near):.4f} vs distant={np.mean(far):.4f}"
              f"  ratio {np.mean(near)/np.mean(far):.2f}")


if __name__ == "__main__":
    main()
