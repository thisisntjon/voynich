"""EXPLORATORY (D-085; O-086 follow-up): does in-line adjacent reuse R_within(1) survive a position-preserving null?
Observed: identical unit for adjacent tokens (p, p+1) in the same line.
Null A (s87-like): page shuffle (300). Null B: for each pair, the rate at which unit(p) equals the token at position p+1
of OTHER lines on the same page (same absolute position; keeps position-specific vocabularies)."""
import random, sqlite3
from collections import defaultdict

VKB = "./data/vkb/vkb.sqlite"


def run(t, col):
    c = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
    rows = c.execute(f"select folio, line_id, {col} from tokens where translit=? order by folio, line_id, pos", (t,)).fetchall()
    lines = defaultdict(list)
    for f, lid, u in rows:
        lines[(f, lid)].append(u or "")
    pages = defaultdict(list)
    for (f, lid), us in lines.items():
        if len(us) >= 2:
            pages[f].append(us)
    obs = 0
    expB = 0.0
    for f, L in pages.items():
        for i, us in enumerate(L):
            for p in range(len(us) - 1):
                a, b = us[p], us[p + 1]
                if not a or not b:
                    continue
                obs += a == b
                others = [v[p + 1] for j, v in enumerate(L) if j != i and len(v) > p + 1 and v[p + 1]]
                if others:
                    expB += sum(a == s for s in others) / len(others)
    rng = random.Random(87)
    expA = 0.0
    S = 200
    for _ in range(S):
        hit = 0
        for f, L in pages.items():
            flat = [u for v in L for u in v]
            rng.shuffle(flat)
            k = 0
            for v in L:
                w = flat[k:k + len(v)]
                k += len(v)
                hit += sum(1 for p in range(len(w) - 1) if w[p] and w[p + 1] and w[p] == w[p + 1])
        expA += hit / S
    print(f"{t} {col:9s}: observed adjacent identical {obs}; null A page-shuffle {expA:.1f} (O/E {obs/expA:.2f}); "
          f"null B position-preserving {expB:.1f} (O/E {obs/expB:.2f})", flush=True)


for t in ("ZL3b", "RF1b", "IT2a"):
    for col in ("slot_core", "a2_core", "word"):
        run(t, col)
