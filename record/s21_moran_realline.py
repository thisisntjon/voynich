#!/usr/bin/env python
"""
S21: Daybreak's within-line lag-1 word-length Moran I on real-line gibberish and CREMMA
(workflow/phases/phase-2.md step s21; prefix reassigned from "Timm bound", done as c-309).

PRE-REGISTRATION (frozen in s21_moran_realline.prereg.sha256 before the first run).

Question. Daybreak's Codex-lab ablation (external tree, below) found the Voynich ZL3b within-line
lag-1 word-length Moran I = 0.157244, above every registered N5 encoded (E max 0.041133),
meaningless-producer (G max 0.128961, schwartz_reuse) and natural-language (L max 0.042799)
control, all of which were scored on synthetic or relined text.  Step s21 asks whether a
*human*-written, *real-line* meaningless corpus (the Gaskell & Bowern volunteer gibberish on the
volunteers' own lines, data/controls_realline/gib_realline_pooled.meta.json) and real-line Latin
(CREMMA Medii Aevi, native lines) reach that value when scored with the identical statistic.

EXTERNAL DEFINITION (treated as data; NOT imported, NOT executed)
  path   : C:\\Users\\thisi\\Desktop\\yonichmanuscript\\codex_lab\\experiments\\moran-ablation-v1\\moran_ablation.py
  sha256 : 086cff8c993b5f157e6d5bdda7f932ed01a4e76d05fd96b7506957c9c7b38a41
  PREREG.md  sha256 e27fa209e282eae1465236cd4dfa862de4acf652175afcc463bda6bfe52e19b6
  REPORT.md  sha256 6d9704bd18b6c584a063072dde6e7c78ac875ea4a769306137aea1370ad706bb
  result.json sha256 359b3819c8424005833af9942d6eccc98022969534144e9898d0c9692f42dc47

Verbatim from moran_ablation.py (the statistic):

    def materialize(pages: list[dict]) -> dict:
        lengths: list[int] = []
        ...
        for page in pages:
            for line in page["lines"]:
                if not line:
                    continue
                start = len(lengths)
                line_lengths = [len(token) for token in line]
                lengths.extend(line_lengths)
                tokens.extend(line)
                idx = np.arange(start, start + len(line), dtype=np.int64)
                lines.append(idx)
        ...
        x = np.asarray(lengths, dtype=np.float64)
        left = np.concatenate([line[:-1] for line in lines if len(line) > 1])
        right = np.concatenate([line[1:] for line in lines if len(line) > 1])

    def moran_for_pairs(x: np.ndarray, left: np.ndarray, right: np.ndarray) -> float:
        mean = float(x.mean())
        z = x - mean
        denom = float(np.dot(z, z))
        return float(len(x) / len(left) * np.dot(z[left], z[right]) / denom)

    observed = moran_for_pairs(x, left, right)        # "within_line"

  i.e. word length = Python string length of the token; x = every token of every non-empty line
  (global mean and global sum of squares); the lag-1 pairs are the adjacent pairs INSIDE a line
  (lines of >= 2 tokens contribute pairs; 1-token lines contribute only to the mean/denominator);
  I = (N / n_pairs) * sum(z_left * z_right) / sum(z^2).

Verbatim from moran_ablation.py (the line-shuffle null and its summary):

    rng_line = np.random.default_rng(SEED + seed_offset)
    line_null = np.empty(N_DRAWS, dtype=np.float64)
    shuffled = x.copy()
    for draw in range(N_DRAWS):
        for idx in data["lines"]:
            shuffled[idx] = rng_line.permutation(x[idx])
        line_null[draw] = moran_for_pairs(shuffled, left, right)

    def summarize(values: np.ndarray, observed: float) -> dict:
        return {
            "draws": int(len(values)),
            "median": float(np.median(values)),
            "p_one_sided": float((1 + int(np.count_nonzero(values >= observed))) / (len(values) + 1)),
            "q99": float(np.quantile(values, 0.99)),
        }

  PREREG.md: "Within-line shuffle: independently permute lengths inside every line. This preserves
  each line's word-length multiset and token count." ... "Use one-sided Monte Carlo
  p=(1 + count(null >= observed))/(999 + 1) and report null median and 99th percentile."
  External constants: SEED = 20261018 (ZL3b seed_offset 0), N_DRAWS = 999.  This step
  pre-registers seed 20261017 and 999 draws (phase-2.md s21); the null is distribution-identical,
  draws are not byte-identical, so q99 is checked as "near 0.081", not to three decimals.

Implementation here: the same statistic, re-implemented from the definition above in numpy.  The
within-line permutation is done in one vectorised step per draw (random keys, lexsort by
(line_id, key)), which is an independent uniform permutation inside every line, as specified.

Daybreak's reported values (REPORT.md / result.json, ZL3b = metrics_new.voynich_pages("eva"),
all paragraph lines, 34,857 tokens, 30,727 within-line pairs):
  within_line 0.157244, line-shuffle null median 0.069368, q99 0.080927, p 0.001,
  whole_sequence 0.140670; 25,007-token ZL3b size diagnostic within-line I 0.135569.
  Control maxima (25,000-token cut, synthetic / relined): E 0.041133, G 0.128961 (schwartz_reuse),
  L 0.042799.

PROCEDURE
 1. Sidecars loaded with scoreboard/run_v2.load_meta imported by path (n7/s18 pattern); lines as in
    the sidecar; NO 25k subsample (Daybreak scored the full transcriptions and reported the 25k row
    only as a size diagnostic, so the controls here are full corpora and ZL3b is reported both full
    and run_v2.subsample(…, 25000)).
 2. Reproduction gate first: ZL3b as run_v2 --voynich loads it (metrics_new.voynich_pages("eva"))
    must give within-line I = 0.157 to three decimals (|I - 0.157244| <= 0.003) and a line-shuffle
    q99 near 0.081.  If the I check fails, STOP: the discrepancy is written to results_s21.txt and
    no control row is computed.
 3. Rows (within-line I, line-shuffle null median / q99 / Monte Carlo p, 999 draws, seed 20261017,
    pairs from lines >= 2 tokens): gib_realline_pooled, cremma_prose15, cremma_c15, cremma_all,
    mhg_nibelungenlied, oldfrench_roland, occitan_croisade, italian_dante (native sidecars in
    data/controls_realline/), the 8-word relined twins of gib_realline_pooled and cremma_all for
    the layout contrast, ZL3b full and ZL3b-25k.
 4. Pre-registered reading (verbatim): "if real-line gibberish within-line I >= 0.129 (Daybreak's
    control maximum, schwartz_reuse), the clause 'no tested meaningless model reproduces it' is
    withdrawn and O-043 narrows to human meaningless production; if < 0.129 it joins the control set
    and the clause stands. CREMMA and verse rows are reported as the real-line language reference;
    sign and magnitude relative to Voynich 0.157 printed."
    Threshold constant: GIB_THRESHOLD = 0.129, applied to the gib_realline_pooled (native lines) row.

Writes ONLY results_s21.txt.  No register, PLAN, data, scoreboard or other results file is touched.
Run: python -I s21_moran_realline.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):  # -I ignores PYTHONIOENCODING; the console may be cp1252
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SELF = ROOT / "s21_moran_realline.py"
STUB = ROOT / "s21_moran_realline.prereg.sha256"
OUT = ROOT / "results_s21.txt"
SIDECARS = ROOT / "data" / "controls_realline"
EXT_DIR = Path(r"C:\Users\thisi\Desktop\yonichmanuscript\codex_lab\experiments\moran-ablation-v1")
EXT_SCRIPT = EXT_DIR / "moran_ablation.py"
EXT_SHA_EXPECTED = "086cff8c993b5f157e6d5bdda7f932ed01a4e76d05fd96b7506957c9c7b38a41"

SEED = 20261017
N_DRAWS = 999
N_SAMPLE = 25000
GIB_THRESHOLD = 0.129
VOY_REF_I = 0.157244
VOY_REF_Q99 = 0.080927
VOY_REF_MEDIAN = 0.069368
VOY_REF_25K = 0.135569
REPRO_TOL = 0.003
CONTROL_MAX = {"E": 0.041133, "G": 0.128961, "L": 0.042799}

ROWS = [  # (label, sidecar stem or None for Voynich, note)
    ("gib_realline_pooled", "gib_realline_pooled", "human gibberish, writers' own lines (G&B 2022)"),
    ("cremma_prose15", "cremma_prose15", "CREMMA Latin prose, 15th c., native lines"),
    ("cremma_c15", "cremma_c15", "CREMMA Latin, 15th c., native lines"),
    ("cremma_all", "cremma_all", "CREMMA Latin, all, native lines"),
    ("mhg_nibelungenlied", "mhg_nibelungenlied", "MHG verse, native lines"),
    ("oldfrench_roland", "oldfrench_roland", "Old French epic, native lines"),
    ("occitan_croisade", "occitan_croisade", "Occitan epic, native lines"),
    ("italian_dante", "italian_dante", "Italian verse, native lines"),
    ("gib_realline_pooled_relined8", "gib_realline_pooled_relined8", "layout contrast: gibberish relined 8 words"),
    ("cremma_all_relined8", "cremma_all_relined8", "layout contrast: CREMMA all relined 8 words"),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def load_by_path(modname: str, path: Path):
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


# ---------------------------------------------------------------- the statistic (per the docstring)
def materialize(pages):
    """x = lengths of every token of every non-empty line (contiguous per line); left/right = adjacent
    pairs inside lines of >= 2 tokens; line_id per token for the vectorised within-line shuffle."""
    lengths, line_id, left, right = [], [], [], []
    n_lines = n_lines_ge2 = 0
    for p in pages:
        for ln in p["lines"]:
            if not ln:
                continue
            start = len(lengths)
            lengths.extend(len(t) for t in ln)
            line_id.extend([n_lines] * len(ln))
            if len(ln) > 1:
                idx = np.arange(start, start + len(ln), dtype=np.int64)
                left.append(idx[:-1])
                right.append(idx[1:])
                n_lines_ge2 += 1
            n_lines += 1
    x = np.asarray(lengths, dtype=np.float64)
    return dict(x=x, line_id=np.asarray(line_id, dtype=np.int64),
                left=np.concatenate(left), right=np.concatenate(right),
                n_lines=n_lines, n_lines_ge2=n_lines_ge2)


def moran_for_pairs(x, left, right):
    mean = float(x.mean())
    z = x - mean
    denom = float(np.dot(z, z))
    return float(len(x) / len(left) * np.dot(z[left], z[right]) / denom)


def whole_sequence(x):
    z = x - float(x.mean())
    return float(len(z) / (len(z) - 1) * np.dot(z[:-1], z[1:]) / np.dot(z, z))


def line_shuffle_null(data, seed):
    """Independently permute the lengths inside every line, N_DRAWS times (vectorised: random keys,
    stable lexsort by (line_id, key); lines are contiguous so x[perm] keeps every value in its line)."""
    x, lid, left, right = data["x"], data["line_id"], data["left"], data["right"]
    rng = np.random.default_rng(seed)
    out = np.empty(N_DRAWS, dtype=np.float64)
    for d in range(N_DRAWS):
        keys = rng.random(len(x))
        perm = np.lexsort((keys, lid))
        out[d] = moran_for_pairs(x[perm], left, right)
    return out


def summarize(values, observed):
    return dict(draws=int(len(values)), median=float(np.median(values)),
                p=float((1 + int(np.count_nonzero(values >= observed))) / (len(values) + 1)),
                q99=float(np.quantile(values, 0.99)))


def analyze(pages, seed):
    data = materialize(pages)
    obs = moran_for_pairs(data["x"], data["left"], data["right"])
    null = summarize(line_shuffle_null(data, seed), obs)
    return dict(I=obs, whole=whole_sequence(data["x"]), tokens=int(len(data["x"])),
                lines=data["n_lines"], lines_ge2=data["n_lines_ge2"], pairs=int(len(data["left"])), **null)


# ---------------------------------------------------------------- main
def main() -> None:
    lines_out: list[str] = []

    def emit(s: str = "") -> None:
        print(s, flush=True)
        lines_out.append(s)

    def flush() -> None:
        OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")

    ext_sha = sha256(EXT_SCRIPT) if EXT_SCRIPT.exists() else "absent"
    emit("S21: Daybreak's within-line lag-1 word-length Moran I on real-line gibberish and CREMMA (phase-2.md s21)")
    emit(f"run started {clock()}")
    emit(f"s21_moran_realline.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"external definition: {EXT_SCRIPT}  sha256={ext_sha}  "
         f"(matches docstring: {ext_sha == EXT_SHA_EXPECTED}); NOT imported, NOT executed")
    for n in ("PREREG.md", "REPORT.md", "result.json"):
        q = EXT_DIR / n
        emit(f"  external {n} sha256={sha256(q) if q.exists() else 'absent'}")
    emit(f"null: within-line shuffle, {N_DRAWS} draws, seed {SEED} (one np.random.default_rng per row); "
         f"p = (1 + #(null >= obs)) / {N_DRAWS + 1}; pairs from lines >= 2 tokens; full corpora (no 25k cap "
         f"except the ZL3b-25k diagnostic row)")
    emit(f"loader: scoreboard/run_v2.py load_meta / subsample by path (sha256 {sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}…); "
         f"ZL3b = metrics_new.voynich_pages('eva') as run_v2 --voynich")
    emit()

    R2 = load_by_path("run_v2_s21", ROOT / "scoreboard" / "run_v2.py")

    # 1. reproduction gate
    emit("=== reproduction check: ZL3b (all paragraph lines) vs Daybreak result.json ===")
    zl = R2.M.voynich_pages("eva")
    rz = analyze(zl, SEED)
    d_i = rz["I"] - VOY_REF_I
    ok = abs(d_i) <= REPRO_TOL
    emit(f"ZL3b  tokens={rz['tokens']} lines={rz['lines']} (>=2 tokens: {rz['lines_ge2']}) pairs={rz['pairs']}  "
         f"within-line I={rz['I']:.6f}  (Daybreak 0.157244; delta {d_i:+.6f}; tol {REPRO_TOL})  "
         f"whole-sequence I={rz['whole']:.6f} (Daybreak 0.140670)")
    emit(f"      line-shuffle null median={rz['median']:.6f} q99={rz['q99']:.6f} p={rz['p']:.3f}  "
         f"(Daybreak median 0.069368, q99 0.080927, p 0.001; seed differs, distribution-identical)")
    emit(f"      Daybreak token_count 34857 / pair_count_within_line 30727 -> here {rz['tokens']} / {rz['pairs']}")
    emit(f"REPRODUCTION: {'PASS' if ok else 'FAIL'}  (|delta I| = {abs(d_i):.6f} {'<=' if ok else '>'} {REPRO_TOL}; "
         f"q99 {'near' if abs(rz['q99'] - VOY_REF_Q99) <= 0.005 else 'NOT near'} 0.081)")
    if not ok:
        emit()
        emit("STOP: the reproduction failed by more than 0.003; no control row computed (pre-registered stop rule).")
        emit(f"discrepancy: within-line I here {rz['I']:.6f} vs Daybreak 0.157244 on tokens {rz['tokens']} vs 34857, "
             f"pairs {rz['pairs']} vs 30727. Possible causes to check: voynich_pages('eva') version/line set, "
             f"tokenisation ('?' drop, strict_spaces), or the statistic's pair/mean convention.")
        emit(f"run ended {clock()}")
        flush()
        return
    emit()

    # 3. rows
    emit("=== rows: within-line lag-1 word-length Moran I, line-shuffle null (999 draws, seed 20261017) ===")
    hdr = (f"{'row':30s} {'tokens':>7s} {'lines':>6s} {'ln>=2':>6s} {'pairs':>7s} {'I_within':>9s} {'I_whole':>9s} "
           f"{'null_med':>9s} {'null_q99':>9s} {'p':>6s} {'I-0.157':>8s}  note")
    emit(hdr)
    results = {}

    def row(label, res, note):
        results[label] = res
        emit(f"{label:30s} {res['tokens']:7d} {res['lines']:6d} {res['lines_ge2']:6d} {res['pairs']:7d} "
             f"{res['I']:9.6f} {res['whole']:9.6f} {res['median']:9.6f} {res['q99']:9.6f} {res['p']:6.3f} "
             f"{res['I'] - VOY_REF_I:+8.4f}  {note}")

    for label, stem, note in ROWS:
        p = SIDECARS / f"{stem}.meta.json"
        if not p.exists():
            emit(f"{label:30s} MISSING sidecar {p}")
            continue
        _, pages = R2.load_meta(p)
        row(label, analyze(pages, SEED), note)
    row("ZL3b", rz, "Voynich, all paragraph lines (reproduction row)")
    z25 = R2.subsample(zl, N_SAMPLE)
    row("ZL3b-25k", analyze(z25, SEED), f"Voynich first {N_SAMPLE}-token cut (Daybreak diagnostic 0.135569)")
    emit()
    emit(f"Daybreak control maxima (25k cut, synthetic/relined): E {CONTROL_MAX['E']:.6f}  "
         f"G {CONTROL_MAX['G']:.6f} (schwartz_reuse)  L {CONTROL_MAX['L']:.6f}")
    emit()

    # 4. reading
    emit("=== READING (pre-registered, verbatim in the docstring, threshold 0.129 on gib_realline_pooled) ===")
    g = results.get("gib_realline_pooled")
    if g is None:
        emit("gib_realline_pooled row missing: no reading.")
    else:
        emit(f"real-line gibberish within-line I = {g['I']:.6f}  (p = {g['p']:.3f} vs its own line-shuffle null, "
             f"q99 {g['q99']:.6f}); threshold {GIB_THRESHOLD}; Voynich ZL3b {rz['I']:.6f}")
        if g["I"] >= GIB_THRESHOLD:
            emit(f"-> {g['I']:.6f} >= {GIB_THRESHOLD}: the clause 'no tested meaningless model reproduces it' is "
                 f"WITHDRAWN; O-043 narrows to human meaningless production.")
        else:
            emit(f"-> {g['I']:.6f} < {GIB_THRESHOLD}: real-line gibberish joins the control set (new G maximum "
                 f"{max(g['I'], CONTROL_MAX['G']):.6f}); the clause 'no tested meaningless model reproduces it' STANDS.")
        emit(f"   gibberish vs Voynich: delta {g['I'] - rz['I']:+.6f} ({g['I'] / rz['I']:.2f}x); "
             f"sign of gibberish I: {'positive' if g['I'] > 0 else 'non-positive'}; "
             f"above its own line-shuffle q99: {g['I'] > g['q99']}")
        g8 = results.get("gib_realline_pooled_relined8")
        if g8:
            emit(f"   layout contrast: gibberish relined8 I = {g8['I']:.6f} (delta vs native lines {g8['I'] - g['I']:+.6f})")
    emit()
    emit("real-line language reference (sign and magnitude relative to Voynich 0.157):")
    for label in ("cremma_prose15", "cremma_c15", "cremma_all", "cremma_all_relined8",
                  "mhg_nibelungenlied", "oldfrench_roland", "occitan_croisade", "italian_dante"):
        r = results.get(label)
        if r is None:
            continue
        emit(f"  {label:22s} I={r['I']:+.6f}  {'positive' if r['I'] > 0 else 'non-positive':12s} "
             f"delta vs Voynich {r['I'] - rz['I']:+.6f}  ({r['I'] / rz['I']:+.2f}x)  "
             f"above own q99: {r['I'] > r['q99']}  p={r['p']:.3f}")
    lang = [results[k]["I"] for k in ("cremma_prose15", "cremma_c15", "cremma_all", "mhg_nibelungenlied",
                                       "oldfrench_roland", "occitan_croisade", "italian_dante") if k in results]
    if lang:
        emit(f"  real-line language range: [{min(lang):+.6f}, {max(lang):+.6f}]  "
             f"(Daybreak's relined L max {CONTROL_MAX['L']:.6f}); Voynich {rz['I']:.6f} "
             f"{'outside' if rz['I'] > max(lang) or rz['I'] < min(lang) else 'inside'} that range")
    emit()
    nrows = len(results)
    emit(f"done-when: results_s21.txt exists with the ZL3b reproduction line and the control rows "
         f"({nrows} rows written: 8 native real-line, 2 relined8 contrasts, ZL3b, ZL3b-25k) -> "
         f"{'met' if nrows == 12 else 'NOT met'}")
    emit(f"run ended {clock()}")
    flush()


if __name__ == "__main__":
    main()
