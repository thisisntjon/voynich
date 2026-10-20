"""Run the new Phase-1 metric families (scoreboard/metrics_new.py) on Voynich EVA,
two language controls (Caesar, Dante; 25k tokens wrapped as 8-token lines, 20-line
pages, 4 contiguous section blocks) and a char-bigram pseudo-Voynich null with
Voynich's page/line shape and labels.  Seed 20261017.

Run from the project root:  python -m scoreboard.run_new --voynich
Writes results_m0_newmetrics.txt (+ results_m0_newmetrics.json sidecar).
"""
import argparse
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import corpora  # noqa: E402
from scoreboard import metrics_new as M  # noqa: E402

OUT = ROOT / "results_m0_newmetrics.txt"
OUTJ = ROOT / "results_m0_newmetrics.json"
N_CTRL = 25000
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def f(x, d=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "nan"
    return f"{x:.{d}f}"


def build_corpora():
    voy = M.voynich_pages("eva")
    secs = ["s1", "s2", "s3", "s4"]
    return [
        ("voynich_eva", voy),
        ("latin_caesar", M.wordlist_pages(corpora.control("latin_caesar", N_CTRL), 8, 20, secs)),
        ("italian_dante", M.wordlist_pages(corpora.control("italian_dante", N_CTRL), 8, 20, secs)),
        ("NULL_bigram_pseudo", M.bigram_pseudo_pages(voy, M.SEED)),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voynich", action="store_true", help="run the full set (default)")
    ap.add_argument("--quick", action="store_true", help="fewer shuffles")
    args = ap.parse_args()
    n_shuf = 5 if args.quick else 20
    sets = build_corpora()
    names = [n for n, _ in sets]
    R = {n: {} for n in names}
    emit(f"# results_m0_newmetrics: new Phase-1 metric families, seed {M.SEED}")
    emit(f"# run {datetime.now().strftime('%Y-%m-%d %H:%M')} (system clock)")
    for n, pg in sets:
        toks = M.flat_tokens(pg)
        emit(f"# {n:20} pages={len(pg):4}  lines={sum(len(p['lines']) for p in pg):5}  "
             f"tokens={len(toks):6}  types={len(set(toks)):5}  sections={sorted({p['section'] for p in pg})}")
    emit()
    timing = {}
    for n, pg in sets:
        t = time.time(); R[n]["lex"] = M.lexicon_growth(pg, n_shuffles=n_shuf); timing[(n, "lex")] = time.time() - t
        t = time.time(); R[n]["slot"], _ = M.slot_structure(pg); timing[(n, "slot")] = time.time() - t
        t = time.time(); R[n]["info"] = M.information_profile(pg); timing[(n, "info")] = time.time() - t
        t = time.time(); R[n]["bake"] = M.heldout_bakeoff(pg); timing[(n, "bake")] = time.time() - t
        t = time.time(); R[n]["extra"] = M.extra_signatures(pg); timing[(n, "extra")] = time.time() - t
        print(f"[{n}] done", {k[1]: round(v, 1) for k, v in timing.items() if k[0] == n}, flush=True)

    hdr = f"{'metric':40}" + "".join(f"{n:>20}" for n in names)

    def row(label, get, d=3):
        emit(f"{label:40}" + "".join(f"{f(get(R[n]), d):>20}" for n in names))

    emit("=== 1. LEXICON GROWTH (Heaps V=K N^beta; log-log OLS on 40 log-spaced points from N=100) ===")
    emit("L: beta ~0.5-0.7 steady; C: beta_late < beta_early, low rate ratio; G: steady beta, high edit-1 share")
    emit(hdr)
    row("beta (all)", lambda r: r["lex"]["all"]["beta"])
    row("beta early half", lambda r: r["lex"]["all"]["beta_early"])
    row("beta late half", lambda r: r["lex"]["all"]["beta_late"])
    row("new-type rate last20%/first20%", lambda r: r["lex"]["all"]["rate_ratio_last20_first20"])
    row("new types edit1 of prev-200 tokens", lambda r: r["lex"]["all"]["edit1_share_recent200"])
    row("  same, far window (baseline)", lambda r: r["lex"]["all"]["edit1_share_far"])
    row("null(shuffled pages) beta mean", lambda r: r["lex"]["shuffled_pages_null"]["beta"]["mean"])
    row("null beta_late mean", lambda r: r["lex"]["shuffled_pages_null"]["beta_late"]["mean"])
    row("null rate ratio mean", lambda r: r["lex"]["shuffled_pages_null"]["rate_ratio_last20_first20"]["mean"])
    row("null rate ratio sd", lambda r: r["lex"]["shuffled_pages_null"]["rate_ratio_last20_first20"]["sd"])
    row("null edit1 share mean", lambda r: r["lex"]["shuffled_pages_null"]["edit1_share_recent200"]["mean"])
    row("null edit1 share sd", lambda r: r["lex"]["shuffled_pages_null"]["edit1_share_recent200"]["sd"], 4)
    emit("Per section / hand (Voynich; >=2000 tokens):")
    for key in ("by_section", "by_hand"):
        for lab, r in R["voynich_eva"]["lex"][key].items():
            emit(f"  {key[3:]}={lab:2} N={r['n_tokens']:6} V={r['n_types']:5} beta={f(r['beta'])} "
                 f"early={f(r['beta_early'])} late={f(r['beta_late'])} rate_ratio={f(r['rate_ratio_last20_first20'])} "
                 f"edit1={f(r['edit1_share_recent200'])}")
    emit("Voynich types-seen curve (N:V): " + " ".join(f"{a}:{b}" for a, b in R["voynich_eva"]["lex"]["all"]["curve"][::4]))
    emit()

    emit("=== 2. SLOT STRUCTURE (prefix/core/suffix induced by >=1% share + successor entropy >= 0.5 H(glyph)) ===")
    emit("L: sparse, Zipfian cores within prefix; C: high occupancy, table-likeness ~1; G: between, crowded cores")
    for which in ("all_types", "top_types"):
        emit(f"[{which}]")
        emit(hdr)

        def g(k, w=which):
            return lambda r: r["slot"][w][k]
        row("n prefixes", g("n_prefixes"), 0)
        row("n cores", g("n_cores"), 0)
        row("n suffixes", g("n_suffixes"), 0)
        row("n types (occupied cells)", g("n_types"), 0)
        row("occupancy P x C x S", g("occupancy_3d"), 4)
        row("occupancy P x C", g("occupancy_prefix_core"), 4)
        row("occupancy C x S", g("occupancy_core_suffix"), 4)
        row("H(core) bits", g("H_core"))
        row("H(core | prefix) bits", g("H_core_given_prefix"))
        row("table-likeness (tok-weighted)", g("table_likeness_weighted"))
        row("table-likeness (unweighted)", g("table_likeness_unweighted"))
        row("mean row fill (cores/prefix / nC)", g("mean_row_fill"), 4)
        row("core edit-1 neighbour share", g("core_edit1_share"))
        row("empty-prefix token share", g("empty_prefix_token_share"))
        row("empty-suffix token share", g("empty_suffix_token_share"))
    for n in names:
        s = R[n]["slot"]
        emit(f"[{n}] H(glyph)={f(s['h_glyph'])} thresh={f(s['entropy_threshold'])}")
        emit(f"   prefixes: {' '.join(s['prefix_candidates'])}")
        emit(f"   suffixes: {' '.join(s['suffix_candidates'])}")
        emit(f"   rejected prefixes (share, H_next): {s['prefix_rejected'][:8]}")
        emit(f"   top prefixes: {s['all_types']['top_prefixes'][:8]}")
        emit(f"   top cores: {s['all_types']['top_cores'][:8]}")
        emit(f"   top suffixes: {s['all_types']['top_suffixes'][:8]}")
        emit(f"   examples: {' '.join(w + '=' + '|'.join(t) for w, t in s['example_segmentations'][:10])}")
    emit()

    emit("=== 3. INFORMATION PROFILE (MI(w; context) bits, top-500 types + OTHER, plug-in minus permutation null, +- bootstrap SE) ===")
    emit("L: steep decay from adjacent; C: flat page/section level; G: adjacent + previous-line spikes")
    for lab in ("word_boundaries_given", "bpe_resegmented"):
        emit(f"[{lab}]  tokens: " + "  ".join(f"{n}={R[n]['info'][lab]['n_tokens']}" for n in names)
             + "  OTHER share: " + "  ".join(f"{n}={f(R[n]['info'][lab]['other_share'])}" for n in names))
        emit(hdr)
        for rel in M.RELATIONS:
            emit(f"{rel:40}" + "".join(
                f"{f(R[n]['info'][lab][rel]['mi']) + '+-' + f(R[n]['info'][lab][rel]['se']):>20}" for n in names))
        row("  adjacent / same_page_far ratio",
            lambda r, l=lab: r["info"][l]["adjacent"]["mi"] / max(r["info"][l]["same_page_far"]["mi"], 1e-6), 1)
        row("  H(w) (adjacent pair set)", lambda r, l=lab: r["info"][l]["adjacent"]["H_w"])
        row("  raw MI adjacent (uncorrected)", lambda r, l=lab: r["info"][l]["adjacent"]["mi_raw"])
        row("  permutation null adjacent", lambda r, l=lab: r["info"][l]["adjacent"]["mi_null"])
    for n in names:
        emit(f"[{n}] BPE merges: {' '.join(R[n]['info']['bpe_merges'])}")
    emit()

    emit("=== 4. HELD-OUT BAKE-OFF (leave-one-quire-out for Voynich/null, blocks of 10 pages for controls; bits/token, bits/char) ===")
    emit("L: markov3/unigram win, copy adds nothing; C: slot beats markov3; G: copy beats markov3")
    emit(hdr)
    models = list(R[names[0]]["bake"]["overall"].keys())
    for m in models:
        row(f"{m} bits/token", lambda r, m=m: r["bake"]["overall"][m]["bits_per_token"])
    for m in models:
        row(f"{m} bits/char", lambda r, m=m: r["bake"]["overall"][m]["bits_per_char"])
    for nm in R[names[0]]["bake"]["copy_gain_bits"]:
        row(f"gain over markov3: {nm}", lambda r, nm=nm: r["bake"]["copy_gain_bits"][nm])
    row("slot - markov3 bits/token", lambda r: r["bake"]["overall"]["slot"]["bits_per_token"] - r["bake"]["overall"]["markov3"]["bits_per_token"])
    row("folds", lambda r: r["bake"]["n_folds"], 0)
    for n in names:
        emit(f"[{n}] per-section winner (bits/token): " + "; ".join(
            f"{sec}:{d['winner']}({f(d[d['winner']], 2)}, n={d['n_tokens']})" for sec, d in R[n]["bake"]["by_section"].items()))
    emit()

    emit("=== 5. EXTRA PUBLISHED SIGNATURES ===")
    emit("(a) edge MI: R&T ~0.2 Voynich > prose; (b) hapax ~70% vs 41-60%; (c) Moran I wordlen >0 Voynich/gibberish, <0 text;")
    emit("(d) position entropy low = position-locked glyphs; (e) ltr-rtl bits/char asymmetry (Parisel)")
    emit(hdr)
    row("(a) edge MI word->next word", lambda r: r["extra"]["edge_mi_word"])
    row("    edge MI line-end->next line", lambda r: r["extra"]["edge_mi_line"])
    row("(b) hapax share @10k", lambda r: r["extra"]["hapax_share_10k"])
    row("    hapax share @20k", lambda r: r["extra"]["hapax_share_20k"])
    row("    hapax share all tokens", lambda r: r["extra"]["hapax_share_all"])
    row("(c) Moran I wordlen lag1", lambda r: r["extra"]["moran_I_wordlen_lag1"])
    row("    Moran I within-line pairs", lambda r: r["extra"]["moran_I_wordlen_lag1_within_line"])
    row("(d) glyph position entropy (max 2.32)", lambda r: r["extra"]["position_entropy_bits"])
    row("(e) bits/char ltr", lambda r: r["extra"]["bits_per_char_ltr"])
    row("    bits/char rtl", lambda r: r["extra"]["bits_per_char_rtl"])
    row("    asymmetry ltr - rtl", lambda r: r["extra"]["directional_asymmetry_ltr_minus_rtl"], 4)
    emit()
    emit("timing (s): " + ", ".join(f"{k[0]}/{k[1]}={v:.1f}" for k, v in timing.items()))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, float) and math.isnan(o):
            return None
        return o
    for n in names:
        R[n]["lex"]["all"].pop("curve", None)
        R[n]["slot"].pop("glyph_position", None)
    OUTJ.write_text(json.dumps(clean(R), indent=1), encoding="utf-8")
    print("wrote", OUT, OUTJ)


if __name__ == "__main__":
    main()
