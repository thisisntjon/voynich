"""E3: align the f57v.3 circular text as four chunks of 17 words.

results_d6.txt already found that this one line is 68 EVA words = 17 x 4,
while the glyph period is 18. This script prints the alignment and the
positions that vary. It does not assign a reading.

A position is STABLE when all four chunks agree, else VARIANT.
Also reports how many of the 68 tokens match ^qo.*edy$.
"""
from pathlib import Path

import vparse

OUT = Path(__file__).parent / "results_e3.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def main():
    recs = [r for r in vparse.load() if r["page"] == "f57v"]
    emit("E3 f57v lines")
    target = None
    for r in recs:
        emit(f"  line {r['line']:2d} unit={r['unit']:4} n={len(r['words']):3d} "
             f"{' '.join(r['words'][:8])}")
        if r["unit"].startswith("C") and len(r["words"]) == 68:
            target = r
    if target is None:
        emit("NO 68-word circular line. Stop.")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
        return
    words = target["words"]
    chunks = [words[i:i + 17] for i in range(0, 68, 17)]
    emit()
    emit(f"aligned line {target['line']} unit={target['unit']}")
    emit("pos " + " ".join(f"{c:14}" for c in ("c1", "c2", "c3", "c4")) + "  flag")
    n_stable = 0
    variants = []
    for i in range(17):
        col = [chunks[k][i] for k in range(4)]
        flag = "STABLE" if len(set(col)) == 1 else "VARIANT"
        if flag == "STABLE":
            n_stable += 1
        else:
            variants.append((i, col))
        emit(f"{i:3d} " + " ".join(f"{w:14}" for w in col) + f"  {flag}")
    emit()
    emit(f"stable positions={n_stable}/17  variant positions={17 - n_stable}")
    for i, col in variants:
        emit(f"  pos {i:02d}: {' | '.join(col)}")
    qo = [w for w in words if w.startswith("qo") and w.endswith("edy")]
    emit(f"qo*edy tokens in the 68: {len(qo)}/{len(words)}")
    # agreement of each later chunk with the first, word for word
    for k in range(4):
        agree = sum(chunks[k][i] == chunks[0][i] for i in range(17))
        emit(f"chunk {k + 1} agrees with chunk 1 at {agree}/17")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
