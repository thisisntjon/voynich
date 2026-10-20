"""B1: test the .docx synthesis claims on local ZL EVA data (stdlib only).

Claims under test (from 'Analyzing the Voynich Manuscript.docx'):
  T1 Section/hand/quire signatures: -edy ~0% in early Herbal-A and ~0.2% in
     Pharmaceutical, o->e drift across Herbal-A quires, qo- scarce in
     zodiac/astro labels, qok-+-edy dense in Biological.
  T2 Self-citation is POSITIONAL: scribes copied the word at the same
     horizontal position on an earlier line (Timm), not just recent words.
  T3 Key-like sequences: f57v ring repeats a ~17-unit sequence ~4x.
Run: uv run python b1_docx_tests.py  -> results_b1.txt + console
"""
import random
from collections import Counter, defaultdict
from pathlib import Path

import vparse

OUT = Path(__file__).parent / "results_b1.txt"
SEED = 20261017
lines_out = []


def emit(s=""):
    print(s)
    lines_out.append(s)


def clean(words):
    return [w for w in words if w and "?" not in w]


def rates(words):
    n = max(len(words), 1)
    chars = "".join(words)
    oe = chars.count("o") + chars.count("e")
    return {
        "n": len(words),
        "edy%": 100 * sum(w.endswith("edy") for w in words) / n,
        "ed%": 100 * sum("ed" in w for w in words) / n,
        "qo%": 100 * sum(w.startswith("qo") for w in words) / n,
        "qok%": 100 * sum(w.startswith("qok") for w in words) / n,
        "aiin%": 100 * sum(w.endswith("aiin") for w in words) / n,
        "o/(o+e)": chars.count("o") / oe if oe else float("nan"),
    }


def t1_sections(para):
    emit("=== T1: section signatures (paragraph text, grouped by $I illustration code) ===")
    by = defaultdict(list)
    folios = defaultdict(set)
    for r in para:
        by[r["illus"]].extend(clean(r["words"]))
        folios[r["illus"]].add(r["page"])
    hdr = f"{'I':>2} {'folios':>7} {'tokens':>7} {'edy%':>6} {'ed%':>6} {'qo%':>6} {'qok%':>6} {'aiin%':>6} {'o/(o+e)':>8}  top words"
    emit(hdr)
    for code in sorted(by, key=lambda c: -len(by[c])):
        w = by[code]
        r = rates(w)
        top = ",".join(f"{x}:{c}" for x, c in Counter(w).most_common(4))
        fs = sorted(folios[code])
        emit(f"{code:>2} {len(fs):>7} {r['n']:>7} {r['edy%']:>6.2f} {r['ed%']:>6.2f} "
             f"{r['qo%']:>6.2f} {r['qok%']:>6.2f} {r['aiin%']:>6.2f} {r['o/(o+e)']:>8.3f}  {top}  [{fs[0]}..{fs[-1]}]")
    emit("\n--- Herbal-A quire drift (illus=H, lang=A, by quire $Q) ---")
    byq = defaultdict(list)
    for r in para:
        if r["illus"] == "H" and r["lang"] == "A":
            byq[r["quire"]].extend(clean(r["words"]))
    for q in sorted(byq):
        r = rates(byq[q])
        emit(f"Q={q}: n={r['n']:>6} edy%={r['edy%']:.2f} ed%={r['ed%']:.2f} qo%={r['qo%']:.2f} o/(o+e)={r['o/(o+e)']:.3f}")
    emit("\n--- Labels only (unit L*), qo- scarcity check by $I ---")
    recs = vparse.load()
    lab = defaultdict(list)
    for r in recs:
        if r["unit"].startswith("L"):
            lab[r["illus"]].extend(clean(r["words"]))
    for code in sorted(lab, key=lambda c: -len(lab[c])):
        r = rates(lab[code])
        if r["n"] >= 30:
            emit(f"I={code}: label tokens={r['n']:>5} qo%={r['qo%']:.2f} edy%={r['edy%']:.2f} o/(o+e)={r['o/(o+e)']:.3f}")


def lev_le1(a, b):
    """True if Levenshtein distance <= 1 (fast path)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b = b, a
        la, lb = lb, la
    i = j = diff = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1; j += 1
        else:
            diff += 1; j += 1
            if diff > 1:
                return False
    return True


def t2_same_column(para):
    emit("\n=== T2: same-column previous-line copying (positional self-citation) ===")
    pages = defaultdict(list)
    for r in para:
        ws = clean(r["words"])
        if len(ws) >= 3:
            pages[r["page"]].append(ws)
    rng = random.Random(SEED)
    all_lines = [ws for ls in pages.values() for ws in ls]
    stats = Counter()
    def hit(w, cands):
        ex = any(w == c for c in cands)
        near = ex or any(lev_le1(w, c) for c in cands)
        return ex, near
    for ls in pages.values():
        for i in range(1, len(ls)):
            prev, cur = ls[i - 1], ls[i]
            far_line = ls[i - 4] if i >= 4 else rng.choice(all_lines)
            for j, w in enumerate(cur):
                near_c = [prev[k] for k in (j - 1, j, j + 1) if 0 <= k < len(prev)]
                off_c = [prev[k] for k in (j + 4, j + 5, j + 6) if 0 <= k < len(prev)]
                far_c = [far_line[k] for k in (j - 1, j, j + 1) if 0 <= k < len(far_line)]
                if not near_c:
                    continue
                stats["n"] += 1
                e, n_ = hit(w, near_c); stats["col_exact"] += e; stats["col_near"] += n_
                if off_c:
                    stats["n_off"] += 1
                    e, n_ = hit(w, off_c); stats["off_exact"] += e; stats["off_near"] += n_
                if far_c:
                    stats["n_far"] += 1
                    e, n_ = hit(w, far_c); stats["far_exact"] += e; stats["far_near"] += n_
    def pct(a, b):
        return 100 * stats[a] / max(stats[b], 1)
    emit(f"tokens evaluated: {stats['n']} (same-col), {stats['n_off']} (off-col), {stats['n_far']} (far-line)")
    emit(f"exact match  same-column prev line : {pct('col_exact','n'):.2f}%")
    emit(f"exact match  off-column prev line  : {pct('off_exact','n_off'):.2f}%")
    emit(f"exact match  same-column far line  : {pct('far_exact','n_far'):.2f}%")
    emit(f"edit<=1 hit  same-column prev line : {pct('col_near','n'):.2f}%")
    emit(f"edit<=1 hit  off-column prev line  : {pct('off_near','n_off'):.2f}%")
    emit(f"edit<=1 hit  same-column far line  : {pct('far_near','n_far'):.2f}%")
    if stats["far_near"] and stats["off_near"]:
        emit(f"ratios (edit<=1): col/far = {pct('col_near','n')/pct('far_near','n_far'):.2f}, "
             f"col/off = {pct('col_near','n')/pct('off_near','n_off'):.2f}")


def t3_key_sequences():
    emit("\n=== T3: key-like folios f49v / f57v / f66r / f116v (all units) ===")
    recs = vparse.load()
    for page in ("f49v", "f57v", "f66r", "f116v"):
        rs = [r for r in recs if r["page"] == page]
        words = [w for r in rs for w in r["words"]]
        units = Counter(r["unit"] for r in rs)
        emit(f"{page}: lines={len(rs)} tokens={len(words)} units={dict(units)}")
        emit(f"  text: {' '.join(words[:80])}")
    # Periodicity scan on f57v circular/diagram text (EVA chars, words joined)
    s = "".join(w for r in recs if r["page"] == "f57v" for w in r["words"] if "?" not in w)
    emit(f"\nf57v char stream length (EVA chars): {len(s)}")
    emit(f"f57v stream head: {s[:160]}")
    best = []
    for p in range(5, 61):
        if len(s) - p < 20:
            break
        m = sum(1 for i in range(p, len(s)) if s[i] == s[i - p]) / (len(s) - p)
        best.append((m, p))
    best.sort(reverse=True)
    emit("top periods by char-match rate (period, rate): "
         + ", ".join(f"{p}:{m:.3f}" for m, p in best[:8]))
    # Longest repeated substring (bounded brute force on suffix pairs via dict of 12-mers)
    seen, best_rep = {}, ""
    for k in (24, 20, 16, 12):
        seen = {}
        found = None
        for i in range(len(s) - k + 1):
            sub = s[i:i + k]
            if sub in seen:
                found = sub
                break
            seen[sub] = i
        if found:
            best_rep = found
            emit(f"repeated {k}-char block exists in f57v stream: {found!r}")
            break
    if not best_rep:
        emit("no repeated 12-char block in f57v EVA char stream")


def main():
    para = vparse.paragraph_text(vparse.load())
    t1_sections(para)
    t2_same_column(para)
    t3_key_sequences()
    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
