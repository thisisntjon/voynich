"""EXPLORATORY (D-085; O-086): is F-40's cross-line avoidance R_cross(1) an artefact of line-edge vocabulary?
Observed: identical unit (slot core / a2 core / word) for (final token of line i, initial token of line i+1), same page.
Null A (s87-like): shuffle all units within page, recompute adjacent cross-break identity (500 shuffles).
Null B (position-preserving): final unit of line i vs initial units of all OTHER lines j != i, i+1 on the same page
(expected identity rate), i.e. keeps line-edge vocabularies. Lines with >= 2 tokens; empty units skipped."""
import random, sqlite3
from collections import defaultdict

VKB = "./data/vkb/vkb.sqlite"


def run(t, col):
    c = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
    rows = c.execute(f"select folio, line_id, pos, {col} from tokens where translit=? order by folio, line_id, pos", (t,)).fetchall()
    lines = defaultdict(list)
    for f, lid, pos, u in rows:
        lines[(f, lid)].append(u or "")
    pages = defaultdict(list)
    for (f, lid), us in lines.items():
        if len(us) >= 2:
            try:
                n = int(lid.split(".")[-1])
            except ValueError:
                continue
            pages[f].append((n, us))
    obs = opp = 0
    expB = 0.0
    shuf_inputs = []
    for f, L in pages.items():
        L.sort()
        ends = [us[-1] for _, us in L]
        starts = [us[0] for _, us in L]
        for i in range(len(L) - 1):
            if L[i + 1][0] != L[i][0] + 1 or not ends[i] or not starts[i + 1]:
                continue
            opp += 1
            obs += ends[i] == starts[i + 1]
            others = [starts[j] for j in range(len(L)) if j not in (i, i + 1) and starts[j]]
            if others:
                expB += sum(ends[i] == s for s in others) / len(others)
        shuf_inputs.append(L)
    rng = random.Random(86)
    expA = 0.0
    S = 300
    for _ in range(S):
        hit = 0
        for L in shuf_inputs:
            flat = [u for _, us in L for u in us]
            rng.shuffle(flat)
            k = 0
            new = []
            for n, us in L:
                new.append((n, flat[k:k + len(us)]))
                k += len(us)
            for i in range(len(new) - 1):
                if new[i + 1][0] != new[i][0] + 1 or not new[i][1][-1] or not new[i + 1][1][0]:
                    continue
                hit += new[i][1][-1] == new[i + 1][1][0]
        expA += hit / S
    print(f"{t} {col:9s}: cross-break pairs {opp}; observed identical {obs}; "
          f"null A page-shuffle {expA:.1f} (O/E {obs/expA if expA else float('nan'):.2f}); "
          f"null B edge-preserving {expB:.1f} (O/E {obs/expB if expB else float('nan'):.2f})", flush=True)


for t in ("ZL3b", "RF1b", "IT2a"):
    for col in ("slot_core", "a2_core", "word"):
        run(t, col)
