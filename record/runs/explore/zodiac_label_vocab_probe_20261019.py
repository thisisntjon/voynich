"""EXPLORATORY (D-085): are zodiac nymph labels a separate vocabulary (names) or main-text words (filler)?
Compares, per transliteration: zodiac labels vs other labels vs paragraph words, length-matched by resampling.
Measures: share starting 'ot'/'ok'; share of types also found in paragraph vocabulary; mean length."""
import random, sqlite3
from collections import Counter

VKB = "./data/vkb/vkb.sqlite"
Z = {"f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v"}


def words(rows):
    out = []
    for f, txt in rows:
        for w in txt.replace(",", ".").split("."):
            w = w.strip("!*?- ")
            if w and w.isalpha():
                out.append((f, w))
    return out


for t in ("ZL3b", "RF1b", "IT2a"):
    c = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
    lab = c.execute("select folio, text from loci where translit=? and locus_type='L'", (t,)).fetchall()
    zl = [r[0].split(".")[0].strip("!*?,") for f, r in [(f, (x,)) for f, x in lab] if f in Z]
    zl = [w for w in zl if w.isalpha()]
    ol = [w for f, w in words([r for r in lab if r[0] not in Z])]
    para = [w for f, w in words(c.execute("select folio, text from loci where translit=? and locus_type='P'", (t,)).fetchall())]
    pv = set(para)
    rng = random.Random(1)
    bylen = {}
    for w in para:
        bylen.setdefault(len(w), []).append(w)

    def stats(ws):
        n = len(ws)
        return (sum(w.startswith(("ot", "ok")) for w in ws) / n, sum(w in pv for w in set(ws)) / len(set(ws)), sum(map(len, ws)) / n)

    def matched(ws, reps=200):
        acc = [0, 0, 0]
        for _ in range(reps):
            s = [rng.choice(bylen.get(len(w)) or para) for w in ws]
            for k, v in enumerate(stats(s)):
                acc[k] += v / reps
        return acc

    for name, ws in (("zodiac labels", zl), ("other labels", ol)):
        a = stats(ws)
        m = matched(ws)
        print(f"{t} {name:14s} n {len(ws):4d}: ot/ok-initial {a[0]:.2f} (len-matched paragraph {m[0]:.2f}); "
              f"types also in paragraph text {a[1]:.2f} (matched {m[1]:.2f}); mean len {a[2]:.1f}", flush=True)
