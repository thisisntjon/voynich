"""E2: how much of the cross-space MI is the single y -> q rule?

Plug-in MI(last character of token i; first character of token i+1),
paragraph lines, '?' tokens dropped, within-line pairs only.

Counterfactual: replace H(first | last='y') with H(first), which deletes
only the information the y-rule carries, and recompute MI. Same deletion
for each of the other frequent left-edge characters.

No decision threshold. The script reports the residual.
"""
import math
from collections import Counter, defaultdict
from pathlib import Path

import vparse

OUT = Path(__file__).parent / "results_e2.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def H(counter, n):
    if n <= 0:
        return 0.0
    return -sum(v / n * math.log2(v / n) for v in counter.values() if v)


def main():
    recs = vparse.paragraph_text(vparse.load())
    lines = []
    for r in recs:
        ws = [w for w in r["words"] if "?" not in w and w.isalpha()]
        if len(ws) >= 2:
            lines.append(ws)
    pairs = [(a[-1], b[0]) for ws in lines for a, b in zip(ws, ws[1:]) if a and b]
    n = len(pairs)
    by_left = defaultdict(Counter)
    first = Counter()
    left = Counter()
    joint = Counter(pairs)
    for a, b in pairs:
        by_left[a][b] += 1
        first[b] += 1
        left[a] += 1
    hf = H(first, n)
    h_cond = sum(left[a] / n * H(by_left[a], left[a]) for a in left)
    mi = hf - h_cond

    emit("E2 edge ablation  paragraph P*  '?' dropped")
    emit(f"pairs={n}  H(first)={hf:.4f}  H(first|last)={h_cond:.4f}  MI={mi:.4f}")
    emit()
    emit(f"{'delete rule':12} {'P(left)':8} {'H(F|left)':10} {'MI if deleted':14} {'share of MI':12}")
    rows = []
    for a in sorted(left, key=lambda g: -left[g]):
        if left[a] < 100:
            continue
        h_a = H(by_left[a], left[a])
        # replace this left-context's conditional with the marginal
        h_cf = h_cond - (left[a] / n) * h_a + (left[a] / n) * hf
        mi_cf = hf - h_cf
        share = (mi - mi_cf) / mi if mi else 0.0
        rows.append((a, left[a] / n, h_a, mi_cf, share))
        emit(f"{a:12} {left[a] / n:8.3f} {h_a:10.4f} {mi_cf:14.4f} {share:12.3f}")
    emit()
    emit("P(first | last) for the left edges that carry the most MI")
    for a, *_ in sorted(rows, key=lambda r: -r[4])[:6]:
        tot = left[a]
        top = by_left[a].most_common(5)
        bits = ", ".join(f"{b}:{c / tot:.3f}" for b, c in top)
        emit(f"  {a} n={tot:5d}  {bits}")
    emit()
    yq = joint[("y", "q")]
    emit(f"y->q count={yq}  rate among y-left={yq / left['y']:.3f}  "
         f"rate among all pairs={yq / n:.3f}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
