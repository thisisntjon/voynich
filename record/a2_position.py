"""Experiment 2: does position in the LINE change word form?

In a natural-language text written in lines, the first/last word of a line is
just whatever word falls there; its letter statistics should match mid-line
words. We measure, for Voynich and for line-structured controls (Dante verse,
Faust verse), the Jensen-Shannon divergence between the distribution of
first/last glyphs of line-initial / line-final words and of mid-line words,
against a permutation null (shuffle positions within lines).
"""
import random
import re
from collections import Counter

import numpy as np

import corpora


def jsd(p, q):
    keys = set(p) | set(q)
    P = np.array([p.get(k, 0) for k in keys], float); P /= P.sum()
    Q = np.array([q.get(k, 0) for k in keys], float); Q /= Q.sum()
    M = (P + Q) / 2
    def kl(a, b):
        m = a > 0
        return np.sum(a[m] * np.log2(a[m] / b[m]))
    return (kl(P, M) + kl(Q, M)) / 2


def stats(lines, feat):
    first = Counter(); mid = Counter(); last = Counter()
    for ws in lines:
        if len(ws) < 3:
            continue
        first[feat(ws[0])] += 1
        last[feat(ws[-1])] += 1
        for w in ws[1:-1]:
            mid[feat(w)] += 1
    return jsd(first, mid), jsd(last, mid)


def null(lines, feat, n=30):
    out = []
    for i in range(n):
        rng = random.Random(i)
        sh = []
        for ws in lines:
            ws = ws[:]; rng.shuffle(ws); sh.append(ws)
        out.append(stats(sh, feat))
    return np.array(out)


def verse_lines(name):
    from corpora import CTRL, strip_gutenberg
    import unicodedata
    t = strip_gutenberg((CTRL / f"{name}.txt").read_text(encoding="utf-8", errors="replace"))
    t = "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")
    lines = [re.findall(r"[a-zß]+", l) for l in t.splitlines()]
    return [l for l in lines if len(l) >= 3][:5000]


def report(name, lines):
    for label, feat in [("first glyph", lambda w: w[0]), ("last glyph", lambda w: w[-1]),
                        ("length", lambda w: min(len(w), 9))]:
        f, l = stats(lines, feat)
        nl = null(lines, feat)
        print(f"{name:16} {label:12} JSD(first,mid)={f:.4f} null={nl[:,0].mean():.4f}±{nl[:,0].std():.4f}"
              f"   JSD(last,mid)={l:.4f} null={nl[:,1].mean():.4f}±{nl[:,1].std():.4f}")


def main():
    vl = [r["words"] for r in corpora.voynich_lines()]
    report("VMS", vl)
    for n in ["italian_dante", "german_faust"]:
        report(n, verse_lines(n))

    # Concrete glyph preferences in Voynich
    recs = corpora.voynich_lines()
    first, mid, last = Counter(), Counter(), Counter()
    for r in recs:
        ws = r["words"]
        if len(ws) < 3:
            continue
        first[ws[0][0]] += 1; last[ws[-1][-1]] += 1
        for w in ws[1:-1]:
            mid[w[0] + ">"] += 1; mid["<" + w[-1]] += 1
    nm = sum(v for k, v in mid.items() if k.endswith(">"))
    nf = sum(first.values())
    print("\nLine-initial word first glyph: ratio vs mid-line (>1 = over-represented)")
    for g, v in first.most_common(10):
        print(f"  {g}: {v/nf:.3f} vs {mid[g+'>']/nm:.3f}  x{(v/nf)/max(mid[g+'>']/nm,1e-9):.2f}")
    nl_ = sum(last.values())
    print("Line-final word last glyph:")
    for g, v in last.most_common(10):
        print(f"  {g}: {v/nl_:.3f} vs {mid['<'+g]/nm:.3f}  x{(v/nl_)/max(mid['<'+g]/nm,1e-9):.2f}")

    # Page-initial gallows
    import vparse
    raw = vparse.paragraph_text(vparse.load())
    starts = Counter(); other = Counter()
    prev_page = None
    for r in raw:
        if not r["words"]:
            continue
        g = r["words"][0][0]
        # IVTFF '*' marker isn't kept; approximate paragraph start = first line on page
        if r["page"] != prev_page:
            starts[g] += 1
        else:
            other[g] += 1
        prev_page = r["page"]
    ns, no = sum(starts.values()), sum(other.values())
    gal = set("ktpf")
    print(f"\nPage-first-line initial glyph is a gallows (k,t,p,f): "
          f"{sum(starts[g] for g in gal)/ns:.2%} vs other lines {sum(other[g] for g in gal)/no:.2%}")
    print("  p/f only:", f"{(starts['p']+starts['f'])/ns:.2%} vs {(other['p']+other['f'])/no:.2%}")


if __name__ == "__main__":
    main()
