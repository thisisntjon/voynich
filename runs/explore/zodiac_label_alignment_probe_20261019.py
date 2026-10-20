"""EXPLORATORY probe (not a scoreboard result): do zodiac nymph labels line up by position across signs
under ANY ring start/direction? Order-agnostic: max over all rotations x 2 directions per page pair.
Match = same first word (exact) or edit distance <= 1 (both reported). Null: shuffle labels within page, 1000 perms."""
import random, sqlite3, sys
from itertools import combinations

VKB = "./data/vkb/vkb.sqlite"
PAGES = ["f70v1", "f70v2", "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v1", "f72v2", "f72v3", "f73r", "f73v"]


def lev1(a, b):
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def labels(c, t, f):
    rows = c.execute("select text from loci where translit=? and locus_type='L' and folio=? order by line_no", (t, f)).fetchall()
    return [r[0].split(".")[0].strip("!*?,") for r in rows if r[0]]


def best(A, B, eq):
    n = min(len(A), len(B))
    A, B = A[:n], B[:n]
    m = 0
    for d in (1, -1):
        for r in range(n):
            m = max(m, sum(eq(A[i], B[(d * i + r) % n]) for i in range(n)))
    return m


def run(t, eq, name, perms=1000, seed=7):
    c = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
    P = {f: labels(c, t, f) for f in PAGES}
    pairs = [(a, b) for a, b in combinations(PAGES, 2) if min(len(P[a]), len(P[b])) >= 15]
    obs = sum(best(P[a], P[b], eq) for a, b in pairs)
    rng = random.Random(seed)
    null = []
    for _ in range(perms):
        Q = {f: rng.sample(v, len(v)) for f, v in P.items()}
        null.append(sum(best(Q[a], Q[b], eq) for a, b in pairs))
    p = (1 + sum(x >= obs for x in null)) / (perms + 1)
    allw = [w for v in P.values() for w in v]
    cross = sum(1 for w in set(allw) if sum(w in P[f] for f in PAGES) > 1)
    print(f"{t} {name}: labels {len(allw)} distinct {len(set(allw))} on>1 page {cross}; "
          f"sum best-alignment matches over {len(pairs)} pairs obs {obs} null mean {sum(null)/len(null):.1f} "
          f"q99 {sorted(null)[int(.99*len(null))]} p {p:.4f}", flush=True)


if __name__ == "__main__":
    for t in ("ZL3b", "RF1b", "IT2a"):
        run(t, lambda a, b: a == b, "exact")
        run(t, lev1, "edit<=1", perms=300)
