"""P4-U1: are EVA uncertain spaces (',') word-internal junctures or squeezed real spaces?

Phase 4 investigation (workflow/research/phase-4-units.md section 3) found that
spacing is the only unit choice that moves word-level metrics. This test
separates the two readings of ',' with two predictions.

PRE-REGISTRATION (written 2026-10-17 22:30 PDT before any run of this file;
Phase 4 gate approved by Jon 22:26; nothing below is changed after results are seen)

Data: paragraph lines (unit P*) of ZL3b (decision), RF1b and IT2a (reported).
Line text is cleaned exactly as vparse.clean does, except that ',' is kept
and drawing interruptions '<->' become a third separator that is excluded.
Words containing '?' are kept as tokens, but no boundary touching one is
scored. Only lines with >= 3 words are used.

P1 justification (squeezed spaces predict positive):
  Boundary k of n-1 in a line of n words has position q = (k - 0.5)/(n - 1).
  D = comma rate at q > 0.75  minus  comma rate at q <= 0.75.
  Null: 1999 within-line shuffles of the separator labels (this keeps each
  line's comma count), random.Random(20261017). One-sided p = (1 + #null >= D)/2000.
  P1 POSITIVE if D > 0 and p <= 0.01.
  Reported, no verdict weight: D within strata of the left word's final glyph
  (Mantel-Haenszel-style weighted difference).

P2 lexical (junctures predict high):
  Reference vocabulary: comma-free dot tokens, i.e. tokens bounded only by '.',
  line ends or interruptions, containing no ','.
  For a scored boundary between A and B:
    joined = the string A+B occurs in the reference vocabulary.
  Rates for comma boundaries vs dot boundaries, with the dot rate directly
  standardised to the comma boundaries' len(A)+len(B) distribution (lengths
  are capped at 14).
  R = rate_comma / rate_dot_std, and dR = rate_comma - rate_dot_std; 95% CI
  of dR from 1000 page bootstraps (numpy default_rng(20261017)).
  P2 HIGH if R >= 1.5 and the CI of dR excludes 0 on the positive side.
  Reported, no verdict weight: the 'both parts standalone' rate (A and B each
  in the reference vocabulary), standardised the same way.

Verdict (ZL3b):
  JUNCTURES (commas should be merged)  if P2 HIGH and P1 not POSITIVE
  REAL SPACES (commas should split)    if P1 POSITIVE and P2 not HIGH
  BOTH                                 if both hold (the two classes are mixed)
  UNDECIDED                            if neither holds (keep the current split)
Interpretation fixed in advance: this decides the convention for later
Phase 4 work. It moves no board metric by itself, and re-scoring under the
winning convention is a separate, later step. RF1b and IT2a are reported
for agreement only.

Run:  python -I p4u1_space_regimes.py  -> results_p4u1_space_regimes.txt only.
Stub: p4u1_space_regimes.prereg.sha256 hashes this file and vparse.py.
"""
from __future__ import annotations

import hashlib
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import vparse  # noqa: E402

SELF = ROOT / "p4u1_space_regimes.py"
STUB = ROOT / "p4u1_space_regimes.prereg.sha256"
OUT = ROOT / "results_p4u1_space_regimes.txt"
DEPS = [ROOT / "vparse.py"]
TRANSLITS = [("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
             ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-e.txt"),
             ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt")]
SEED = 20261017
N_SHUF = 1999
N_BOOT = 1000
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stub_check():
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        parts = ln.split()
        if len(parts) >= 2 and not ln.startswith("#"):
            want[parts[1].lstrip("*")] = parts[0]
    return " ".join(f"{p.name}={'MATCH' if want.get(p.name) == sha(p) else 'MISMATCH'}" for p in [SELF] + DEPS)


def tokenize(text):
    """vparse.clean, keeping ',' and marking interruptions as '|'. Returns (words, seps)."""
    text = re.sub(r"<![^>]*>", "", text)
    text = re.sub(r"<->", "|", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", text)
    text = re.sub(r"@\d+;", "?", text)
    text = text.replace("{", "").replace("}", "").replace("'", "")
    parts = re.split(r"([.,|])", text)
    words, seps, pending = [], [], None
    for p in parts:
        if p in (".", ",", "|"):
            if words:
                pending = p if pending in (None, ".") or p == "|" else pending
                if p == "," and pending != "|":
                    pending = ","
            continue
        if not p:
            continue
        if words:
            seps.append(pending or ".")
        words.append(p)
        pending = None
    return words, seps


def load_lines(path):
    lines = []
    page = None
    for raw in path.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = vparse.PAGE_RE.match(raw)
        if m:
            page = m.group(1)
            continue
        m = vparse.LINE_RE.match(raw)
        if not m or not m.group(4).startswith("P"):
            continue
        words, seps = tokenize(m.group(5))
        if len(words) >= 3:
            lines.append((page, words, seps))
    return lines


def scored(words, seps):
    """Indices k (0-based boundary after word k) usable for scoring."""
    return [k for k, s in enumerate(seps) if s in (".", ",") and "?" not in words[k] and "?" not in words[k + 1]]


def p1(lines, rng):
    rows = []  # (line_id, q, is_comma, left_final)
    for li, (_, w, s) in enumerate(lines):
        n = len(w)
        for k in scored(w, s):
            rows.append((li, (k + 0.5) / (n - 1), s[k] == ",", w[k][-1]))
    late = np.array([q > 0.75 for _, q, _, _ in rows])
    comma = np.array([c for _, _, c, _ in rows])
    lid = np.array([li for li, _, _, _ in rows])

    def D(c):
        return c[late].mean() - c[~late].mean()

    obs = D(comma)
    groups = defaultdict(list)
    for i, li in enumerate(lid):
        groups[li].append(i)
    idx = [np.array(g) for g in groups.values()]
    null = []
    c = comma.copy()
    for _ in range(N_SHUF):
        for g in idx:
            c[g] = comma[g][rng.permutation(len(g))]
        null.append(D(c))
    p = (1 + sum(x >= obs for x in null)) / (N_SHUF + 1)
    num = den = 0.0
    for g in set(r[3] for r in rows):
        m = np.array([r[3] == g for r in rows])
        nl, ne = (m & late).sum(), (m & ~late).sum()
        if nl and ne:
            wgt = nl * ne / (nl + ne)
            num += wgt * (comma[m & late].mean() - comma[m & ~late].mean())
            den += wgt
    return obs, p, float(np.mean(null)), float(np.quantile(null, 0.99)), num / den if den else float("nan"), comma.mean(), len(rows)


def p2(lines, boot_rng):
    ref = Counter()
    for _, w, s in lines:
        # comma-free dot tokens: merge across ',' then keep only pieces that had no ','
        cur, had = w[0], False
        for k, sep in enumerate(s):
            if sep == ",":
                cur, had = cur + w[k + 1], True
            else:
                if not had:
                    ref[cur] += 1
                cur, had = w[k + 1], False
        if not had:
            ref[cur] += 1
    recs = []  # (page, is_comma, lenbin, joined, both)
    for page, w, s in lines:
        for k in scored(w, s):
            a, b = w[k], w[k + 1]
            recs.append((page, s[k] == ",", min(len(a) + len(b), 14), (a + b) in ref, a in ref and b in ref))

    def rates(rs):
        com = [r for r in rs if r[1]]
        dot = [r for r in rs if not r[1]]
        if not com:
            return float("nan"), float("nan"), float("nan"), float("nan")
        bins = Counter(r[2] for r in com)
        by = defaultdict(list)
        for r in dot:
            by[r[2]].append(r)
        tot = sum(bins[b] for b in bins if by[b])
        rc_j = np.mean([r[3] for r in com if by[r[2]]])
        rc_b = np.mean([r[4] for r in com if by[r[2]]])
        rd_j = sum(bins[b] * np.mean([r[3] for r in by[b]]) for b in bins if by[b]) / tot
        rd_b = sum(bins[b] * np.mean([r[4] for r in by[b]]) for b in bins if by[b]) / tot
        return rc_j, rd_j, rc_b, rd_b

    rc_j, rd_j, rc_b, rd_b = rates(recs)
    pages = sorted({r[0] for r in recs})
    bypage = defaultdict(list)
    for r in recs:
        bypage[r[0]].append(r)
    d = []
    for _ in range(N_BOOT):
        pick = boot_rng.integers(0, len(pages), len(pages))
        rs = [r for i in pick for r in bypage[pages[i]]]
        a, b, _, _ = rates(rs)
        d.append(a - b)
    lo, hi = np.quantile(d, [0.025, 0.975])
    n_com = sum(r[1] for r in recs)
    return rc_j, rd_j, (lo, hi), rc_b, rd_b, n_com, len(recs) - n_com


def main():
    emit("P4-U1: uncertain spaces as junctures vs squeezed spaces (pre-registered in the docstring)")
    try:
        clk = subprocess.run(["date"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        clk = "unavailable"
    emit(f"Clock: {clk}")
    emit(f"Stub: {stub_check()}")
    emit()
    verdicts = {}
    for T, path in TRANSLITS:
        lines = load_lines(path)
        rng = np.random.default_rng(SEED)
        rng_py = random.Random(SEED)  # noqa: F841  (seed fixed in the pre-registration; numpy rng drives the shuffle)
        D, p, nmean, nq99, mh, crate, nb = p1(lines, rng)
        rc_j, rd_j, ci, rc_b, rd_b, n_com, n_dot = p2(lines, np.random.default_rng(SEED))
        R = rc_j / rd_j if rd_j else float("inf")
        p1_pos = D > 0 and p <= 0.01
        p2_high = R >= 1.5 and ci[0] > 0
        v = ("BOTH" if p1_pos and p2_high else "JUNCTURES" if p2_high else
             "REAL SPACES" if p1_pos else "UNDECIDED")
        verdicts[T] = v
        emit(f"=== {T}: {len(lines)} lines, {nb} scored boundaries, comma share {crate:.3f} ({n_com} comma, {n_dot} dot) ===")
        emit(f"P1  D(last quarter - rest) = {D:+.4f}   null mean {nmean:+.4f}  q99 {nq99:+.4f}  p = {p:.4f}"
             f"   [left-final-glyph stratified D {mh:+.4f}, reported]  -> {'POSITIVE' if p1_pos else 'not positive'}")
        emit(f"P2  joined-form rate: comma {rc_j:.4f} vs dot (length-standardised) {rd_j:.4f}  R = {R:.2f}"
             f"  dR 95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}]  -> {'HIGH' if p2_high else 'not high'}")
        emit(f"    both-parts-standalone rate: comma {rc_b:.4f} vs dot {rd_b:.4f}  (reported)")
        emit(f"VERDICT {T}: {v}{'  (decision row)' if T == 'ZL3b' else '  (agreement only)'}")
        emit()
    emit(f"VERDICT P4-U1: {verdicts['ZL3b']}   agreement: " + "  ".join(f"{k}={v}" for k, v in verdicts.items()))


if __name__ == "__main__":
    main()
