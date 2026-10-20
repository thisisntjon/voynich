"""P4-D1: can a cipher whose cores carry plaintext in reading order reproduce A14?

A14 (CONSTRAINTS-MAP; results_s34_morphology_syntax_geography.txt): under the
SlotSegmenter prefix/core/suffix split, adjacent cores within a line carry
LESS mutual information than under a within-line word shuffle (ZL3b ALL
C1->C2 excess -0.0315). Phase 4 investigation (workflow/research/phase-4.md)
found, exploratorily and with a different statistic, that planted ciphers
whose cores carry letters in order sit at +0.30..+0.52. P4-D1 asks the same
question with A14's own statistic and segmenter.

PRE-REGISTRATION (written 2026-10-17 22:28 PDT before any run of this file;
gate approved by Jon 22:26; nothing below is changed after results are seen)

Statistic (A14's, re-implemented line for line from s34 run_part1 1B, using
s34.fast_mi_1d and scoreboard.metrics_new.SlotSegmenter imported unchanged):
  SlotSegmenter fitted on all paragraph tokens of the text; plug-in MI between
  the core ids of adjacent words within lines of >= 2 words; null = 200
  within-line word-order shuffles, random.Random(20261017); excess = obs - null
  mean; sd = null sd.

Texts:
  Voynich  ZL3b, RF1b, IT2a paragraph text (vparse.paragraph_text), ALL /
           Currier A / Currier B (segmenter fitted on ALL, as in s34).
  Planted  for each plaintext in corpora.CONTROLS (latin_caesar,
           latin_augustine, italian_dante, german_faust, german_kafka,
           english_alice) and generator seeds 1, 2, 3, laid into the ZL3b
           paragraph line-length sequence (same lines, same words per line,
           truncated where the plaintext runs out):
    K1 letter-in-core: one cipher word per plaintext letter (a-z, spaces
       dropped). Core = homophone of the letter. Prefix and suffix are drawn
       iid from ZL3b's empirical (prefix, suffix) joint and are independent
       of the plaintext.
    K2 word-in-core: one cipher word per plaintext word; core = code of the
       word (many-to-one when word types outnumber cores); affixes as K1.
    K3 chunk-in-core (Naibbe-like units): plaintext letters cut into 1- or
       2-letter chunks (P(single) = 17/36); core = homophone of the chunk.
    K0 null cores (control): cores iid from ZL3b core frequencies, no
       plaintext. Reported, no verdict weight beyond the instrument check.
    K4 transposed K1 (control): K1 with word order permuted within each line.
       Reported, no verdict weight.
  Core assignment: ZL3b cores (SlotSegmenter on ZL3b) with their token
  frequencies. If units <= cores, each core is given to the unit with the
  largest remaining frequency deficit (cores taken in descending frequency);
  if units > cores, each unit (descending) goes to the core with the largest
  remaining capacity. A homophone is drawn within its unit in proportion to
  the core's ZL3b frequency. Word = prefix + core + suffix, then the planted
  text is RE-SEGMENTED by its own SlotSegmenter (the honest instrument). The
  oracle excess on the generator's true cores is printed as a diagnostic only.

Checks and decision:
  Instrument  ZL3b ALL excess must equal s34's -0.0315 within +-0.0005, else
              INSTRUMENT MISMATCH and no verdict.
  V_max       the largest Voynich excess over the 9 (transliteration x subset)
              rows.
  Per cell (family K1/K2/K3 x plaintext, 18 cells), E = seed-mean excess,
  sd = seed-mean null sd.
    the cell REACHES Voynich if E <= V_max + 0.02;
    the cell is CLEAR if E >= V_max + max(0.02, 3*sd).
  Verdict:  CONFIRMED if all 18 cells are CLEAR;
            REFUTED if >= 6 cells REACH Voynich;
            otherwise MIXED (cells listed).
Interpretation fixed in advance:
  CONFIRMED: through A14's instrument, a cipher whose cores carry plaintext
  letters, letter chunks or words in reading order, with plaintext-independent
  affixes, does not produce Voynich's core-order statistic. The solver target
  moves off letter-order-in-cores (to the affix stream, null cores,
  transposition or a core-avoidance rule). It does NOT rule those out, and it
  does not test affixes that carry plaintext.
  REFUTED: A14 is not a constraint on letter-carrying cores, and the Phase 4
  solver ladder keeps the letter-in-core target.

AMENDMENT 1 (2026-10-17 22:31 PDT, after run 1 crashed at K3/latin_caesar with an empty
homophone list; run 1's partial output is kept as results_p4d1_core_order.run1-crashed.txt and
had printed the Voynich rows plus K1 and K2 for latin_caesar). In assign(), a unit that the
greedy rule leaves with no core takes the least-frequent core of the unit holding the most cores.
This rule fires only where run 1 crashed, so the rows already printed are unchanged. Nothing
else is changed.

Run:  python -I p4d1_core_order.py  -> results_p4d1_core_order.txt only.
Stub: p4d1_core_order.prereg.sha256 hashes this file and the local modules it imports.
"""
from __future__ import annotations

import hashlib
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import corpora  # noqa: E402
import s34_morphology_syntax_geography as s34  # noqa: E402
import scoreboard.metrics_new as mn  # noqa: E402
import vparse  # noqa: E402

SELF = ROOT / "p4d1_core_order.py"
STUB = ROOT / "p4d1_core_order.prereg.sha256"
OUT = ROOT / "results_p4d1_core_order.txt"
DEPS = [ROOT / "corpora.py", ROOT / "s34_morphology_syntax_geography.py",
        ROOT / "scoreboard" / "metrics_new.py", ROOT / "vparse.py"]
SEED = 20261017
N_SHUF = 200
GEN_SEEDS = (1, 2, 3)
S34_ZL_ALL = -0.0315
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
    out = []
    for p in [SELF] + DEPS:
        key = str(p.relative_to(ROOT)).replace("\\", "/")
        got = sha(p)
        out.append(f"{key}={'MATCH' if want.get(key) == got else 'MISMATCH'}")
    return " ".join(out)


def core_excess(seg_tokens, lines):
    """A14's C1->C2 statistic, as in s34 run_part1 section 1B."""
    seg = mn.SlotSegmenter(seg_tokens)
    vocab = sorted(set(seg_tokens))
    w2i = {w: i for i, w in enumerate(vocab)}
    cs = sorted({seg.segment(w)[1] for w in vocab})
    c2i = {x: i for i, x in enumerate(cs)}
    C_W = np.array([c2i[seg.segment(w)[1]] for w in vocab], dtype=np.int64)
    lines_2 = [[w2i[w] for w in ln] for ln in lines if len(ln) >= 2]
    n_pairs = sum(len(ln) - 1 for ln in lines_2)
    w1 = np.fromiter((w for ln in lines_2 for w in ln[:-1]), dtype=np.int64, count=n_pairs)
    w2 = np.fromiter((w for ln in lines_2 for w in ln[1:]), dtype=np.int64, count=n_pairs)
    obs = s34.fast_mi_1d(C_W[w1], C_W[w2], len(cs), len(cs))[0]
    rng = random.Random(SEED)
    null = []
    for _ in range(N_SHUF):
        sh = [rng.sample(ln, len(ln)) for ln in lines_2]
        a = np.fromiter((w for ln in sh for w in ln[:-1]), dtype=np.int64, count=n_pairs)
        b = np.fromiter((w for ln in sh for w in ln[1:]), dtype=np.int64, count=n_pairs)
        null.append(s34.fast_mi_1d(C_W[a], C_W[b], len(cs), len(cs))[0])
    m, sd = float(np.mean(null)), float(np.std(null))
    return obs - m, sd, len(cs), n_pairs


def voynich_lines(path):
    para = vparse.paragraph_text(vparse.load(path=path))
    return [(r["lang"], [w for w in r["words"] if "?" not in w]) for r in para]


def assign(units_freq, cores_freq):
    """Return {unit: [(core, weight), ...]} by the pre-registered greedy rule."""
    U = sorted(units_freq, key=lambda u: -units_freq[u])
    C = sorted(cores_freq, key=lambda c: -cores_freq[c])
    tu, tc = sum(units_freq.values()), sum(cores_freq.values())
    out = {u: [] for u in U}
    if len(U) <= len(C):
        deficit = {u: units_freq[u] / tu for u in U}
        for c in C:
            u = max(U, key=lambda x: deficit[x])
            out[u].append((c, cores_freq[c]))
            deficit[u] -= cores_freq[c] / tc
        for u in U:  # AMENDMENT 1 (22:31): a unit left with no core takes the least-frequent core of the unit holding the most cores
            if not out[u]:
                donor = max(U, key=lambda x: len(out[x]))
                out[donor].sort(key=lambda cw: -cw[1])
                out[u].append(out[donor].pop())
    else:
        cap = {c: cores_freq[c] / tc for c in C}
        for u in U:
            c = max(C, key=lambda x: cap[x])
            out[u].append((c, cores_freq[c]))
            cap[c] -= units_freq[u] / tu
    return out


def plant(units, table, affix_pairs, affix_w, line_lens, rng):
    toks, cores = [], []
    for u in units:
        cand = table[u]
        c = rng.choices([x for x, _ in cand], weights=[w for _, w in cand])[0]
        p, s = rng.choices(affix_pairs, weights=affix_w)[0]
        toks.append(p + c + s)
        cores.append(c)
    lines, oracle, i = [], [], 0
    for n in line_lens:
        if i >= len(toks):
            break
        lines.append(toks[i:i + n])
        oracle.append(cores[i:i + n])
        i += n
    return lines, oracle


def oracle_excess(oracle_lines):
    """Diagnostic: same statistic on the generator's true cores (no re-segmentation)."""
    vocab = sorted({c for ln in oracle_lines for c in ln})
    c2i = {c: i for i, c in enumerate(vocab)}
    lines_2 = [[c2i[c] for c in ln] for ln in oracle_lines if len(ln) >= 2]
    n = sum(len(ln) - 1 for ln in lines_2)
    a = np.fromiter((w for ln in lines_2 for w in ln[:-1]), dtype=np.int64, count=n)
    b = np.fromiter((w for ln in lines_2 for w in ln[1:]), dtype=np.int64, count=n)
    obs = s34.fast_mi_1d(a, b, len(vocab), len(vocab))[0]
    rng = random.Random(SEED)
    null = []
    for _ in range(N_SHUF):
        sh = [rng.sample(ln, len(ln)) for ln in lines_2]
        x = np.fromiter((w for ln in sh for w in ln[:-1]), dtype=np.int64, count=n)
        y = np.fromiter((w for ln in sh for w in ln[1:]), dtype=np.int64, count=n)
        null.append(s34.fast_mi_1d(x, y, len(vocab), len(vocab))[0])
    return obs - float(np.mean(null))


def chunks(letters, rng):
    out, i = [], 0
    while i < len(letters):
        k = 1 if (rng.random() < 17 / 36 or i == len(letters) - 1) else 2
        out.append("".join(letters[i:i + k]))
        i += k
    return out


def main():
    emit("P4-D1: A14 core->core statistic on planted in-order ciphers (pre-registered in the docstring)")
    try:
        clk = subprocess.run(["date"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        clk = "unavailable"
    emit(f"Clock: {clk}")
    emit(f"Stub: {stub_check()}")
    emit()
    vrows = {}
    zl_lines = None
    for T, path in s34.TRANSLITS:
        vl = voynich_lines(path)
        if T == "ZL3b":
            zl_lines = vl
        seg_tokens = [w for _, ln in vl for w in ln]
        for sub, f in (("ALL", None), ("A", "A"), ("B", "B")):
            lines = [ln for lang, ln in vl if f is None or lang == f]
            ex, sd, nc, npairs = core_excess(seg_tokens, lines)
            vrows[(T, sub)] = ex
            emit(f"Voynich {T:<5} {sub:<3} cores={nc:<5} pairs={npairs:<6} excess={ex:+.4f}  null sd={sd:.4f}")
    inst = abs(vrows[("ZL3b", "ALL")] - S34_ZL_ALL) <= 0.0005
    v_max = max(vrows.values())
    emit(f"Instrument check: ZL3b ALL {vrows[('ZL3b', 'ALL')]:+.4f} vs s34 {S34_ZL_ALL:+.4f} -> {'OK' if inst else 'INSTRUMENT MISMATCH'}")
    emit(f"V_max = {v_max:+.4f}; REACH threshold {v_max + 0.02:+.4f}")
    emit()

    zl_tokens = [w for _, ln in zl_lines for w in ln]
    zseg = mn.SlotSegmenter(zl_tokens)
    trip = [zseg.segment(w) for w in zl_tokens]
    core_freq = Counter(c for _, c, _ in trip)
    aff = Counter((p, s) for p, _, s in trip)
    affix_pairs, affix_w = list(aff), list(aff.values())
    line_lens = [len(ln) for _, ln in zl_lines]
    n_target = sum(line_lens)

    cells = {}
    for name in corpora.CONTROLS:
        words = corpora.control(name)
        letters = [ch for w in words for ch in w]
        for fam in ("K1", "K2", "K3", "K0", "K4"):
            exs, sds, ors, sizes = [], [], [], []
            for gs in GEN_SEEDS:
                rng = random.Random(gs)
                if fam in ("K1", "K4"):
                    units = letters[:n_target]
                elif fam == "K2":
                    units = words[:n_target]
                elif fam == "K3":
                    units = chunks(letters[:2 * n_target], rng)[:n_target]
                else:
                    units = rng.choices(list(core_freq), weights=list(core_freq.values()), k=n_target)
                if fam == "K0":
                    table = {c: [(c, 1)] for c in core_freq}
                else:
                    table = assign(Counter(units), core_freq)
                lines, oracle = plant(units, table, affix_pairs, affix_w, line_lens, rng)
                if fam == "K4":
                    perm = [rng.sample(range(len(ln)), len(ln)) for ln in lines]
                    lines = [[ln[j] for j in p] for ln, p in zip(lines, perm)]
                    oracle = [[ln[j] for j in p] for ln, p in zip(oracle, perm)]
                seg_tokens = [w for ln in lines for w in ln]
                ex, sd, nc, npairs = core_excess(seg_tokens, lines)
                exs.append(ex); sds.append(sd); ors.append(oracle_excess(oracle)); sizes.append((len(seg_tokens), nc, npairs))
            E, SD, OR = float(np.mean(exs)), float(np.mean(sds)), float(np.mean(ors))
            cells[(fam, name)] = (E, SD)
            tag = ""
            if fam in ("K1", "K2", "K3"):
                reach = E <= v_max + 0.02
                clear = E >= v_max + max(0.02, 3 * SD)
                tag = "REACHES Voynich" if reach else "CLEAR" if clear else "between"
            emit(f"{fam} {name:<16} tokens={sizes[0][0]:<6} cores={sizes[0][1]:<5} excess seeds "
                 + " ".join(f"{x:+.4f}" for x in exs)
                 + f"  mean {E:+.4f} sd {SD:.4f}  oracle {OR:+.4f}  {tag}")
        emit()

    main_cells = {k: v for k, v in cells.items() if k[0] in ("K1", "K2", "K3")}
    n_reach = sum(E <= v_max + 0.02 for E, _ in main_cells.values())
    n_clear = sum(E >= v_max + max(0.02, 3 * SD) for E, SD in main_cells.values())
    if not inst:
        verdict = "NO VERDICT (INSTRUMENT MISMATCH)"
    elif n_clear == len(main_cells):
        verdict = "CONFIRMED"
    elif n_reach >= 6:
        verdict = "REFUTED"
    else:
        verdict = "MIXED"
    emit(f"Cells: {len(main_cells)}; CLEAR {n_clear}; REACH {n_reach}")
    if verdict == "MIXED":
        emit("Non-clear cells: " + ", ".join(f"{f}/{n} {E:+.4f}" for (f, n), (E, SD) in main_cells.items()
                                            if E < v_max + max(0.02, 3 * SD)))
    emit(f"VERDICT P4-D1: {verdict}")


if __name__ == "__main__":
    main()
