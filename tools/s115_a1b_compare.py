"""s115-A1b: cross-model Cohen's kappa, Claude consensus (data/anchor_A1/labels.tsv) vs the
independent local-model labels (data/anchor_A1b/labels_gemma.tsv).

Uses cohen_kappa, read_labels and CATS imported unchanged from s115_a1_kappa.py (never edited).
Rules (CODEBOOK.md agreement rules): PT over all images; other categories over images where both
sides gave a level other than NA. Consensus cells DISAGREE:<p1>|<p2> are skipped and counted.
Invalid model levels count as written (i.e. as disagreement). A2-eligible: kappa >= 0.6 and n >= 10.
Usage: python -I tools/s115_a1b_compare.py   (writes data/anchor_A1b/kappa_cross_model.txt, never overwrites)
"""
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from s115_a1_kappa import cohen_kappa, read_labels, write_new, CATS  # noqa: E402

CONS = os.path.join(ROOT, "data", "anchor_A1", "labels.tsv")
MINE = os.path.join(ROOT, "data", "anchor_A1b", "labels_gemma.tsv")
OUT = os.path.join(ROOT, "data", "anchor_A1b", "kappa_cross_model.txt")
# allowed levels transcribed from CODEBOOK.md (sha256 8b72197f...); NA allowed everywhere except PT
ALLOWED = {"PT": "CIRCLE BATH PHARMA PLANT MARGINAL NONE OTHER", "P_plants": "1 2 3+",
           "P_root": "BULB TUBER TAPROOT BRANCHING NONE", "P_leafshape": "DIVIDED ROUND ELLIPTIC LINEAR NONE",
           "P_leafcount": "0 1-4 5-10 11-20 21+", "P_flower": "0 1 2-4 5+", "P_habit": "ROSETTE SINGLE MULTI",
           "J_shape": "CYLINDER VASE OTHER NONE", "J_count": "0 1-2 3-4 5+", "J_fragcount": "0 1-5 6-15 16+",
           "J_fragtype": "ROOTS LEAVES MIXED NONE", "C_centre": "ANIMAL HUMAN FACE GEOMETRIC EMPTY",
           "C_animal": "FISH HORNED HORNLESS CRAWLER BIRD OTHER", "C_figures": "0 1-9 10-19 20+",
           "C_rings": "0-1 2 3 4+", "C_diagrams": "1 2-3 4+", "C_rays": "PRESENT ABSENT",
           "B_pools": "1 2 3+", "B_figures": "1-5 6-10 11+", "B_tubes": "PRESENT ABSENT"}
ALLOWED = {k: set(v.split()) | ({"NA"} if k != "PT" else set()) for k, v in ALLOWED.items()}


def read_consensus(path):
    lines = [l.rstrip("\r\n") for l in open(path, encoding="utf-8") if l.strip()]
    head = lines[0].split("\t")
    return {r[0]: dict(zip(head, r)) for r in (l.split("\t") for l in lines[1:])}


def main(model_tag):
    c, m = read_consensus(CONS), read_labels(MINE)
    stems = sorted(set(c) & set(m))
    out = [f"s115-A1b cross-model kappa: Claude consensus labels.tsv vs {os.path.basename(MINE)} ({model_tag})",
           f"images in both: {len(stems)} (only consensus {len(set(c) - set(m))}, only model {len(set(m) - set(c))})",
           "rule: PT over all images; others where both non-NA; consensus DISAGREE cells skipped; "
           "A2-eligible = kappa >= 0.6 and n >= 10",
           "category\tn\tpercent_agree\tkappa\tdisagree_skipped\tinvalid_model_levels_all_images\tA2\tlevels_consensus\tlevels_model"]
    eligible, tot_skip = [], 0
    for cat in CATS:
        pr, skip, inval = [], 0, 0
        for s in stems:
            x, y = c[s].get(cat, "MISSING"), m[s][cat]
            if x.startswith("DISAGREE"):
                skip += 1
                continue
            if cat != "PT" and (x == "NA" or y == "NA"):
                continue
            pr.append((x, y))
        inval = sum(1 for s in stems if m[s][cat] not in ALLOWED[cat])
        k, n, po = cohen_kappa([x for x, _ in pr], [y for _, y in pr])
        ok = k is not None and k >= 0.6 and n >= 10
        if ok:
            eligible.append(cat)
        tot_skip += skip
        ks = "undefined" if k is None else f"{k:.3f}"
        pos = "-" if po is None else f"{po:.3f}"
        l1 = ",".join(f"{a}:{b}" for a, b in sorted(Counter(x for x, _ in pr).items()))
        l2 = ",".join(f"{a}:{b}" for a, b in sorted(Counter(y for _, y in pr).items()))
        out.append(f"{cat}\t{n}\t{pos}\t{ks}\t{skip}\t{inval}\t{'ELIGIBLE' if ok else 'no'}\t{l1}\t{l2}")
    out.append(f"total DISAGREE cells skipped: {tot_skip}")
    out.append("A2-eligible: " + (" ".join(eligible) if eligible else "(none)"))
    write_new(OUT, "\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "qwen2.5vl:7b")
