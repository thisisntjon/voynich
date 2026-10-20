"""s41 — Currier-B edge coupling decomposed by the suffix class of the left word (and the prefix class of the right
word), with leave-one-class-out.

PRE-REGISTERED QUESTION (verbatim; frozen in s41_b_coupling_by_suffix.prereg.sha256 before the run):
"Is the Currier-B cross-space coupling (last glyph -> next first glyph edge MI excess, cross_excess_eva, B 0.232 in
results_s20.txt / s30) carried by one suffix class of the left word, so that dropping that class moves B into the
real-line language range while Currier A is unchanged?"

Method (fixed before the run)
  Data: N.load (n1_habit_table.load, by path) for ZL3b_eva, RF1b, IT2a; Currier B = pages with lang "B", A = lang "A".
  Segmenter: scoreboard/metrics_new.SlotSegmenter fitted on ALL tokens of that transliteration (no held-out claim is
    made here, so the full-token fit is used; inventory printed).  Suffix class of a token = seg.segment(w)[2]
    ("" = empty suffix, printed as "∅"); prefix class = seg.segment(w)[0]; raw last glyph = w[-1].
  Statistic: c3_edge_coupling.score(lines, c3.EVA) (loaded by path): obs MI of within-line adjacent pairs
    (a[-1], b[0]) minus the mean MI of NREP=20 within-line shuffles (random.Random(0)) = cross_excess_eva.
    Check: ZL3b B full excess reproduces results_s20.txt B 0.2321 (|diff| <= 0.01) and A 0.1203.
  Decomposition (ZL3b, B and A): the observed MI is a sum over pairs of (1/n) log2(p(a,b)/(p(a)p(b))); that pointwise
    sum is grouped by (i) suffix class of the left word, (ii) raw last glyph of the left word, (iii) prefix class of the
    right word; each group's share of the total MI, its pair count, and its mean pointwise MI are printed.  The same
    grouping on the shuffle-null pairs (mean over the 20 shuffles) gives the group's null contribution; group excess =
    observed - null contribution.
  Leave-one-class-out (every transliteration, B and A): for each suffix class s, (a) TOKEN-DROP: every token whose
    suffix class is s is removed from its line (its neighbours become adjacent) and cross_excess_eva is recomputed;
    (b) PAIR-DROP: only the pairs whose left word has suffix class s are removed from the pair list (obs and null
    alike).  The reading rule uses (a); (b) is printed beside.
  Prediction (fixed): if one class carries the coupling, dropping it (token-drop) moves B's cross_excess from 0.232
    into the real-line language range (<= 0.13, the bound named in the plan from the results_s20.txt range) while A
    stays unchanged (|A excess after drop - A excess before| <= 0.02).
  Rule: "one class carries B" if some suffix class satisfies B_after <= 0.13 AND |A_after - A_before| <= 0.02 on ZL3b
    (RF1b / IT2a printed beside: UNSTABLE if the ZL3b call flips there); otherwise "no single class carries B" and the
    class with the largest B drop is named with its margin (B_after - 0.13) and A shift.
  Margins printed for every class: B_after - 0.13 and A_after - A_before.

Run:    python -I s41_b_coupling_by_suffix.py
Writes: results_s41.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

OUT = ROOT / "results_s41.txt"
STUB = ROOT / "s41_b_coupling_by_suffix.prereg.sha256"
SELF = ROOT / "s41_b_coupling_by_suffix.py"
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
LANG_BOUND = 0.13
A_TOL = 0.02
S20 = {"ZL3b": (0.1203, 0.2321), "RF1b": (0.1071, 0.2259), "IT2a": (0.0968, 0.2181)}
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


def load_by_path(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


def lab(c):
    return c if c else "∅"


def pointwise(pairs):
    """pair -> pointwise MI term (1/n) log2(p(a,b)/(p(a)p(b)))."""
    n = len(pairs)
    pj = Counter(pairs); pa = Counter(a for a, _ in pairs); pb = Counter(b for _, b in pairs)
    return {ab: c / n * math.log2(c * n / (pa[ab[0]] * pb[ab[1]])) for ab, c in pj.items()}, n


def grouped_mi(lines, keyfn, nrep=20):
    """Observed MI split by a key of the (left word, right word) pair; null = mean over nrep within-line shuffles."""
    def one(ls):
        pairs, keys = [], []
        for ws in ls:
            for a, b in zip(ws, ws[1:]):
                pairs.append((a[-1], b[0])); keys.append(keyfn(a, b))
        pw, n = pointwise(pairs)
        # exact per-pair attribution: each pair occurrence gets pw[ab] / count(ab)
        pj = Counter(pairs)
        g = defaultdict(float); cnt = Counter()
        for ab, k in zip(pairs, keys):
            g[k] += pw[ab] / pj[ab]
            cnt[k] += 1
        return g, cnt, sum(pw.values())
    obs, cnt, tot = one(lines)
    rng = random.Random(0)
    nul = defaultdict(float); ntot = 0.0
    for _ in range(nrep):
        sh = []
        for ws in lines:
            ws = ws[:]; rng.shuffle(ws); sh.append(ws)
        g, _, t = one(sh)
        for k, v in g.items():
            nul[k] += v / nrep
        ntot += t / nrep
    return obs, cnt, tot, nul, ntot


def drop_tokens(lines, seg, cls):
    out = []
    for ws in lines:
        kept = [w for w in ws if seg.segment(w)[2] != cls]
        if kept:
            out.append(kept)
    return out


def pair_drop_excess(lines, seg, cls, c3, nrep=20):
    def mi_filtered(ls):
        pairs = [(a[-1], b[0]) for ws in ls for a, b in zip(ws, ws[1:]) if seg.segment(a)[2] != cls]
        return c3.mi(pairs) if pairs else 0.0
    obs = mi_filtered(lines)
    rng = random.Random(0)
    nul = []
    for _ in range(nrep):
        sh = []
        for ws in lines:
            ws = ws[:]; rng.shuffle(ws); sh.append(ws)
        nul.append(mi_filtered(sh))
    return obs - sum(nul) / nrep


def main() -> int:
    t0 = time.time()
    emit("S41: Currier-B edge coupling (cross_excess_eva) by suffix class of the left word; leave-one-class-out")
    emit(f"run started {clock()}")
    emit(f"s41_b_coupling_by_suffix.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"statistic: c3_edge_coupling.score (within-line pairs (a[-1], b[0]); null = mean MI of 20 within-line shuffles); "
         f"segmenter: metrics_new.SlotSegmenter on all tokens of each transliteration; rule: B_after <= {LANG_BOUND} and |A shift| <= {A_TOL}")
    emit()
    N = load_by_path("n1_habit_table_s41", ROOT / "n1_habit_table.py")
    c3 = load_by_path("c3_edge_coupling_s41", ROOT / "c3_edge_coupling.py")
    M = load_by_path("metrics_new_s41", ROOT / "scoreboard" / "metrics_new.py")
    verdict = {}
    for T, meta in TRANSLITS.items():
        by = N.load(meta)
        toks = [w for recs in by.values() for r in recs for w in r["words"]]
        seg = M.SlotSegmenter(toks)
        lines = {L: [r["words"] for recs in by.values() for r in recs if r["lang"] == L] for L in ("A", "B")}
        sufs = Counter(seg.segment(w)[2] for w in toks)
        emit(f"=== {T}: {len(toks)} tokens; SlotSegmenter {len(seg.prefixes)} prefixes {sorted(seg.prefixes)}; "
             f"{len(seg.suffixes)} suffixes {sorted(seg.suffixes)}; suffix classes in use {len(sufs)} ===")
        base = {}
        for L in ("A", "B"):
            obs, nm, exc, z = c3.score(lines[L], c3.EVA)
            base[L] = exc
            ref = S20[T][0 if L == "A" else 1]
            emit(f"  {L}: {len(lines[L])} lines {sum(map(len, lines[L]))} tokens; MI {obs:.4f} null {nm:.4f} excess {exc:+.4f} (z {z:.1f}); "
                 f"results_s20.txt {ref:.4f} diff {exc - ref:+.4f} {'OK' if abs(exc - ref) <= 0.01 else 'MISMATCH'}")
        if T == "ZL3b":
            for L in ("B", "A"):
                for title, keyfn in (("suffix class of LEFT word", lambda a, b: seg.segment(a)[2]),
                                     ("raw LAST glyph of left word", lambda a, b: a[-1]),
                                     ("prefix class of RIGHT word", lambda a, b: seg.segment(b)[0])):
                    obs, cnt, tot, nul, ntot = grouped_mi(lines[L], keyfn)
                    emit(f"  --- {T} {L}: MI decomposition by {title}: total MI {tot:.4f}, null {ntot:.4f}, excess {tot - ntot:+.4f} ---")
                    emit(f"  {'class':8} | {'pairs':>6} {'share':>6} | {'obs MI':>8} {'null MI':>8} {'excess':>8} {'% of exc':>8} | {'mean pw obs':>11}")
                    for k, v in sorted(obs.items(), key=lambda kv: -(kv[1] - nul.get(kv[0], 0.0)))[:25]:
                        ex = v - nul.get(k, 0.0)
                        emit(f"  {lab(k):8} | {cnt[k]:6d} {cnt[k] / sum(cnt.values()):6.3f} | {v:8.4f} {nul.get(k, 0.0):8.4f} {ex:+8.4f} {100 * ex / (tot - ntot):8.1f} | {v / cnt[k]:11.6f}")
        emit(f"  --- {T} leave-one-suffix-class-out: TOKEN-DROP (rule) and PAIR-DROP (beside); margins B_after - {LANG_BOUND}, A_after - A_before ---")
        emit(f"  {'class':8} | {'tok share':>9} | {'B tok-drop':>10} {'margin':>8} | {'A tok-drop':>10} {'A shift':>8} | {'B pair-drop':>11} {'A pair-drop':>11} | rule")
        hits = []
        best = None
        for cls, c in sorted(sufs.items(), key=lambda kv: -kv[1]):
            bt = c3.score(drop_tokens(lines["B"], seg, cls), c3.EVA)[2]
            at = c3.score(drop_tokens(lines["A"], seg, cls), c3.EVA)[2]
            bp = pair_drop_excess(lines["B"], seg, cls, c3)
            ap = pair_drop_excess(lines["A"], seg, cls, c3)
            ok = bt <= LANG_BOUND and abs(at - base["A"]) <= A_TOL
            if ok:
                hits.append(cls)
            if best is None or bt < best[1]:
                best = (cls, bt, at)
            emit(f"  {lab(cls):8} | {c / len(toks):9.3f} | {bt:10.4f} {bt - LANG_BOUND:+8.4f} | {at:10.4f} {at - base['A']:+8.4f} | {bp:11.4f} {ap:11.4f} | {'HIT' if ok else '-'}")
        verdict[T] = (hits, best, base)
        emit(f"  {T}: {'one class carries B: ' + ', '.join(lab(h) for h in hits) if hits else 'no single class carries B'}; "
             f"largest B drop by removing {lab(best[0])}: B {base['B']:+.4f} -> {best[1]:+.4f} (margin to {LANG_BOUND}: {best[1] - LANG_BOUND:+.4f}), "
             f"A {base['A']:+.4f} -> {best[2]:+.4f} (shift {best[2] - base['A']:+.4f})")
        emit(f"  elapsed {time.time() - t0:.0f}s")
        emit()
    emit("=== READING (pre-registered rule, ZL3b decides; RF1b / IT2a beside) ===")
    z = verdict["ZL3b"]
    reading = "one class carries B" if z[0] else "no single class carries B"
    flips = [T for T in ("RF1b", "IT2a") if bool(verdict[T][0]) != bool(z[0])]
    emit(f"ZL3b: {reading}{' (' + ', '.join(lab(h) for h in z[0]) + ')' if z[0] else ''}; "
         f"prediction 'one suffix class carries the B coupling' -> {'CONFIRMED' if z[0] else 'FAILED'}; "
         f"{'UNSTABLE on ' + ', '.join(flips) if flips else 'same call on RF1b, IT2a'}")
    for T, (hits, best, base) in verdict.items():
        emit(f"  {T}: B {base['B']:+.4f} A {base['A']:+.4f}; best single drop {lab(best[0])} -> B {best[1]:+.4f} (margin {best[1] - LANG_BOUND:+.4f}), A shift {best[2] - base['A']:+.4f}")
    emit()
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
