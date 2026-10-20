"""s42 — line n-1 recency hits classified by layer (same-core/changed-affix vs same-affix/changed-core).

PRE-REGISTERED QUESTION (verbatim; frozen in s42_recency_by_layer.prereg.sha256 before the run):
"When a word on line n has an exact or edit<=1 match at the same x-position on line n-1 (the m1 / s35 recency
signal), is the copied unit the core (same core, changed affix) or the operator frame (same affixes, changed core)?"

Recency definition — copied from s35_physical_codicology_quire_network.py (sha256
c86b92c82ae8a14b5da3b74325cdea51a4367f7cc0b51d80b237510b0d8a1c51), section 1D, tier "1_prev_line", "same_x"; the
helpers are m1_coordinates.py (sha256 0ddc1eaafd22eb852b46f0fe2023b6cefaae3c3cbc9d59c47efc57a74e01626b), loaded here
by path (s35 itself is NOT imported).  Verbatim from s35:

        by_no = {no: toks for no, toks in pg["lines"]}
        nos = sorted(by_no)
        for no in nos:
            cur = [t for t in by_no[no] if m1.ok_word(t["word"])]
            if not cur:
                continue
            prev = by_no.get(no - 1)
            ...
            cand_lines = {"1_prev_line": prev, ...}
            for tname, cline in cand_lines.items():
                if not cline:
                    continue
                cands = [t for t in cline if m1.ok_word(t["word"])]
                if not cands:
                    continue
                for tok in cur:
                    w = tok["word"]
                    d, c = m1.nearest(tok, cands)
                    if d <= 0.5 * W:
                        ex, e1 = m1.score(w, c["word"])
                        tier_hits[tname]["same_x"].append((f, pg["bifolio"], int(ex or e1), int(ex)))

  with (m1_coordinates.py) pages_m1 = m1.build_pages() (pages[folio] -> dict(meta, W = mean token box width,
  lines = [(line_no, [tok(word, cx, cy, w)])]), paragraph lines whose boxes aligned); m1.nearest(tok, cands) = the
  candidate with the smallest |cx - tok.cx| (returns (d, cand)); m1.score(w, c) = (w == c, (not exact) and
  lev_le1(w, c)); m1.lev_le1 = Levenshtein distance <= 1 (substitution, insertion or deletion); m1.ok_word(w) =
  non-empty and no "?".  A "same_x edit<=1 hit" = a token of line n whose nearest same-x token on line n-1 (d <=
  0.5 W) is exact or within one edit.  s35 reports the hit rate as 100 * hits / probes ("obs=…%").

Method (fixed before the run)
  Probes: every (token on line n, nearest token on line n-1 with d <= 0.5 W) pair as above, on all aligned pages
    (ZL3b, the only transliteration with box coordinates).  Hit = exact or lev_le1.
  Layers: scoreboard/metrics_new.SlotSegmenter fitted on all ZL3b paragraph tokens (M.voynich_pages("eva"); no
    held-out claim; inventory printed).  seg.segment(w) -> (prefix, core, suffix).
  Classes of a hit (w = line-n word, c = its line n-1 match):
    both-same              : w == c (exact hit);
    same-core/changed-affix: core(w) == core(c) and (prefix(w), suffix(w)) != (prefix(c), suffix(c));
    same-affix/changed-core: (prefix(w), suffix(w)) == (prefix(c), suffix(c)) and core(w) != core(c);
    other                  : everything else (core and at least one affix differ).
  Null: within-page line permutation, 200 draws, random.Random(20261017): for each page and each line n, the
    comparison line is a random OTHER line of the same page (not line n itself; pages with < 2 lines are skipped);
    probes and hits computed identically; per draw the hit count of each class.  Null mean, sd, z = (obs - mean)/sd
    and one-sided Monte-Carlo p = (1 + #draws >= obs) / 201 per class; excess = obs - null mean.
  Prediction (Timm-Schinner self-citation, fixed): hits above null are dominated by same-core/changed-affix, i.e. the
    excess (obs - null mean) of same-core/changed-affix exceeds the excess of same-affix/changed-core.  If instead
    same-affix/changed-core has the larger excess, the copied unit is the operator frame.
  Rule: "core copied" if excess(same-core/changed-affix) > excess(same-affix/changed-core) and the former's p <= 0.05;
    "frame copied" if the reverse ordering with p <= 0.05; "neither" otherwise.  Margin printed = difference of the
    two excesses and each class's z.  Exact hits (both-same) are reported separately and are not in the rule.
  Checks: total same_x edit<=1 rate printed against the s35 line (results_s35_... "Line n-1 same_x edit<=1 : obs=…%").

Run:    python -I s42_recency_by_layer.py
Writes: results_s42.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

OUT = ROOT / "results_s42.txt"
STUB = ROOT / "s42_recency_by_layer.prereg.sha256"
SELF = ROOT / "s42_recency_by_layer.py"
SEED = 20261017
DRAWS = 200
CLASSES = ["both-same", "same-core/changed-affix", "same-affix/changed-core", "other"]
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


def classify(w, c, seg):
    if w == c:
        return "both-same"
    pw, kw, sw = seg.segment(w)
    pc, kc, sc = seg.segment(c)
    if kw == kc and (pw, sw) != (pc, sc):
        return "same-core/changed-affix"
    if (pw, sw) == (pc, sc) and kw != kc:
        return "same-affix/changed-core"
    return "other"


def count_hits(pages, m1, seg, prev_of):
    """prev_of(by_no, nos, no) -> comparison line tokens or None.  Returns (probes, Counter of hit classes, examples)."""
    probes = 0
    hits = Counter()
    for f, pg in pages.items():
        W = pg["W"]
        by_no = {no: toks for no, toks in pg["lines"]}
        nos = sorted(by_no)
        for no in nos:
            cur = [t for t in by_no[no] if m1.ok_word(t["word"])]
            if not cur:
                continue
            cline = prev_of(by_no, nos, no)
            if not cline:
                continue
            cands = [t for t in cline if m1.ok_word(t["word"])]
            if not cands:
                continue
            for tok in cur:
                w = tok["word"]
                d, c = m1.nearest(tok, cands)
                if d <= 0.5 * W:
                    probes += 1
                    ex, e1 = m1.score(w, c["word"])
                    if ex or e1:
                        hits[classify(w, c["word"], seg)] += 1
    return probes, hits


def main() -> int:
    t0 = time.time()
    emit("S42: line n-1 same-x edit<=1 recency hits classified by layer (core vs operator frame); within-page line-permutation null")
    emit(f"run started {clock()}")
    emit(f"s42_recency_by_layer.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"recency definition: s35_physical_codicology_quire_network.py sha256={sha256(ROOT / 's35_physical_codicology_quire_network.py')} (copied, not imported); "
         f"m1_coordinates.py sha256={sha256(ROOT / 'm1_coordinates.py')} (loaded by path)")
    emit(f"null: within-page line permutation, {DRAWS} draws, random.Random({SEED}); prediction: same-core/changed-affix excess > same-affix/changed-core excess")
    emit()
    m1 = load_by_path("m1_coordinates_s42", ROOT / "m1_coordinates.py")
    M = load_by_path("metrics_new_s42", ROOT / "scoreboard" / "metrics_new.py")
    toks = M.flat_tokens(M.voynich_pages("eva"))
    seg = M.SlotSegmenter(toks)
    emit(f"SlotSegmenter on {len(toks)} ZL3b tokens: {len(seg.prefixes)} prefixes {sorted(seg.prefixes)}; {len(seg.suffixes)} suffixes {sorted(seg.suffixes)}; "
         f"{len(set(seg.segment(w)[1] for w in set(toks)))} cores")
    pages, stats = m1.build_pages()
    n_lines = sum(len(pg["lines"]) for pg in pages.values())
    emit(f"m1.build_pages: {len(pages)} aligned pages, {n_lines} aligned paragraph lines, {sum(len(t) for pg in pages.values() for _, t in pg['lines'])} tokens")
    emit()

    probes, obs = count_hits(pages, m1, seg, lambda by_no, nos, no: by_no.get(no - 1))
    tot = sum(obs.values())
    emit(f"observed: {probes} same-x probes (line n vs line n-1, d <= 0.5 W); {tot} edit<=1 hits = {100 * tot / probes:.2f} % "
         f"(check vs results_s35 'Line n-1 same_x edit<=1 : obs=…%'); exact {obs['both-same']} = {100 * obs['both-same'] / probes:.2f} %")
    for k in CLASSES:
        emit(f"  {k:26}: {obs[k]:5d} hits  {100 * obs[k] / probes:6.2f} % of probes  {100 * obs[k] / max(tot, 1):6.1f} % of hits")
    emit()

    rng = random.Random(SEED)
    null = {k: [] for k in CLASSES}
    null_probes = []
    for d in range(DRAWS):
        def prev_of(by_no, nos, no, rng=rng):
            others = [m for m in nos if m != no]
            return by_no[rng.choice(others)] if others else None
        p, h = count_hits(pages, m1, seg, prev_of)
        null_probes.append(p)
        for k in CLASSES:
            null[k].append(h[k])
    emit(f"null ({DRAWS} draws): comparison line = random other line of the same page; probes per draw mean {np.mean(null_probes):.0f}")
    emit(f"  {'class':26} | {'obs':>5} | {'null mean':>9} {'sd':>7} | {'excess':>7} {'z':>7} {'p':>7} | {'obs %':>7} {'null %':>7}")
    res = {}
    for k in CLASSES:
        arr = np.array(null[k], dtype=float)
        mu, sd = arr.mean(), arr.std()
        z = (obs[k] - mu) / sd if sd > 0 else float("inf")
        p = (1 + int((arr >= obs[k]).sum())) / (DRAWS + 1)
        res[k] = dict(obs=obs[k], mu=mu, sd=sd, exc=obs[k] - mu, z=z, p=p)
        emit(f"  {k:26} | {obs[k]:5d} | {mu:9.1f} {sd:7.1f} | {obs[k] - mu:+7.1f} {z:+7.2f} {p:7.3f} | {100 * obs[k] / probes:7.2f} {100 * mu / np.mean(null_probes):7.2f}")
    emit()
    emit("=== READING (pre-registered rule) ===")
    a, b = res["same-core/changed-affix"], res["same-affix/changed-core"]
    margin = a["exc"] - b["exc"]
    if margin > 0 and a["p"] <= 0.05:
        reading = "core copied"
    elif margin < 0 and b["p"] <= 0.05:
        reading = "frame copied"
    else:
        reading = "neither"
    emit(f"excess same-core/changed-affix {a['exc']:+.1f} (z {a['z']:+.2f}, p {a['p']:.3f}) vs same-affix/changed-core {b['exc']:+.1f} (z {b['z']:+.2f}, p {b['p']:.3f}); "
         f"margin {margin:+.1f} hits -> {reading}")
    emit(f"prediction (same-core/changed-affix dominates above null): {'CONFIRMED' if reading == 'core copied' else 'FAILED'}")
    emit(f"exact hits (both-same, not in the rule): excess {res['both-same']['exc']:+.1f} (z {res['both-same']['z']:+.2f}); other: excess {res['other']['exc']:+.1f} (z {res['other']['z']:+.2f})")
    emit()
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
