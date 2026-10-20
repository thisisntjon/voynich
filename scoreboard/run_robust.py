"""PREREG robustness check 1: repeat the five metric families of scoreboard/metrics_new
on (a) the glyph-collapsed ZL3b tokenization and (b) three other transliterations
(RF1b-er reference = ZL+GC consensus, IT2a Takahashi, GC2a Claston v101 alphabet),
all converted by tools/ivtff_to_meta.py into data/translit/*.meta.json.  Seed 20261017.

Columns: ZL3b-EVA (copied from results_m0_newmetrics.json / results_d1_newmetrics.json,
whichever exists), ZL3b-glyph+, RF1b, IT2a, GC2a.  The final "flips" section compares
each headline number's position relative to the Latin (Caesar) and Italian (Dante)
controls of that baseline run, per transliteration.

Run from the project root:  python -m scoreboard.run_robust
Writes results_m2_robustness.txt (+ results_m2_robustness.json).
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
from scoreboard import metrics_new as M  # noqa: E402

TRANSLIT = ROOT / "data" / "translit"
OUT = ROOT / "results_m2_robustness.txt"
OUTJ = ROOT / "results_m2_robustness.json"
BASELINES = [ROOT / "results_m0_newmetrics.json", ROOT / "results_d1_newmetrics.json"]
EVA = "ZL3b-EVA"
COLS = [(EVA, None), ("ZL3b-glyph+", "ZL3b_glyphplus.meta.json"), ("RF1b", "RF1b.meta.json"),
        ("IT2a", "IT2a.meta.json"), ("GC2a", "GC2a.meta.json")]
LAT, ITA = "latin_caesar", "italian_dante"
SUBSAMPLE = 25000
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def f(x, d=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "nan"
    return f"{x:.{d}f}"


def subsample(pages, n):
    """First n tokens in manuscript order (whole lines), used only if --fast."""
    out, k = [], 0
    for p in pages:
        q = dict(p, lines=[])
        for ln in p["lines"]:
            if k >= n:
                break
            q["lines"].append(ln); k += len(ln)
        if q["lines"]:
            out.append(q)
        if k >= n:
            break
    return out


# ---- row definitions (same accessors as run_new.py) -------------------------------
def rows_lex():
    return [("beta (all)", lambda r: r["lex"]["all"]["beta"], 3),
            ("beta early half", lambda r: r["lex"]["all"]["beta_early"], 3),
            ("beta late half", lambda r: r["lex"]["all"]["beta_late"], 3),
            ("new-type rate last20%/first20%", lambda r: r["lex"]["all"]["rate_ratio_last20_first20"], 3),
            ("new types edit1 of prev-200 tokens", lambda r: r["lex"]["all"]["edit1_share_recent200"], 3),
            ("  same, far window (baseline)", lambda r: r["lex"]["all"]["edit1_share_far"], 3),
            ("  edit-1 locality excess (recent - far)", lambda r: r["lex"]["all"]["edit1_share_recent200"] - r["lex"]["all"]["edit1_share_far"], 3),
            ("null(shuffled pages) beta mean", lambda r: r["lex"]["shuffled_pages_null"]["beta"]["mean"], 3),
            ("null rate ratio mean", lambda r: r["lex"]["shuffled_pages_null"]["rate_ratio_last20_first20"]["mean"], 3),
            ("null edit1 share mean", lambda r: r["lex"]["shuffled_pages_null"]["edit1_share_recent200"]["mean"], 3)]


def rows_slot(which):
    def g(k, d=3):
        return (lambda r: r["slot"][which][k]), d
    return [(f"[{which}] n prefixes",) + g("n_prefixes", 0), (f"[{which}] n cores",) + g("n_cores", 0),
            (f"[{which}] n suffixes",) + g("n_suffixes", 0), (f"[{which}] n types",) + g("n_types", 0),
            (f"[{which}] occupancy P x C x S",) + g("occupancy_3d", 4),
            (f"[{which}] occupancy P x C",) + g("occupancy_prefix_core", 4),
            (f"[{which}] occupancy C x S",) + g("occupancy_core_suffix", 4),
            (f"[{which}] H(core) bits",) + g("H_core"), (f"[{which}] H(core | prefix) bits",) + g("H_core_given_prefix"),
            (f"[{which}] table-likeness (tok-weighted)",) + g("table_likeness_weighted"),
            (f"[{which}] table-likeness (unweighted)",) + g("table_likeness_unweighted"),
            (f"[{which}] core edit-1 neighbour share",) + g("core_edit1_share"),
            (f"[{which}] empty-prefix token share",) + g("empty_prefix_token_share"),
            (f"[{which}] empty-suffix token share",) + g("empty_suffix_token_share")]


def rows_info(lab):
    rows = [(f"[{lab}] {rel}", (lambda r, rel=rel: r["info"][lab][rel]["mi"]), 3) for rel in M.RELATIONS]
    rows += [(f"[{lab}] same_col - other_col (prev line)",
              lambda r: r["info"][lab]["prev_line_same_col"]["mi"] - r["info"][lab]["prev_line_other_col"]["mi"], 3),
             (f"[{lab}] H(w) adjacent pair set", lambda r: r["info"][lab]["adjacent"]["H_w"], 3),
             (f"[{lab}] raw MI adjacent", lambda r: r["info"][lab]["adjacent"]["mi_raw"], 3)]
    return rows


BAKE_MODELS = ["markov2", "markov3", "slot", "unigram_gt", "copy0.3+markov3", "copy0.1+markov3", "copy0.05+markov3"]


def rows_bake():
    rows = [(f"{m} bits/token", (lambda r, m=m: r["bake"]["overall"][m]["bits_per_token"]), 3) for m in BAKE_MODELS]
    rows += [(f"{m} bits/char", (lambda r, m=m: r["bake"]["overall"][m]["bits_per_char"]), 3) for m in BAKE_MODELS]
    rows += [(f"gain over markov3: {m}", (lambda r, m=m: r["bake"]["copy_gain_bits"][m]), 3)
             for m in BAKE_MODELS if m.startswith("copy")]
    rows += [("slot - markov3 bits/token", lambda r: r["bake"]["overall"]["slot"]["bits_per_token"] - r["bake"]["overall"]["markov3"]["bits_per_token"], 3),
             ("markov3 - unigram_gt bits/token", lambda r: r["bake"]["overall"]["markov3"]["bits_per_token"] - r["bake"]["overall"]["unigram_gt"]["bits_per_token"], 3),
             ("folds", lambda r: r["bake"]["n_folds"], 0)]
    return rows


def rows_extra():
    return [("(a) edge MI word->next word", lambda r: r["extra"]["edge_mi_word"], 3),
            ("    edge MI line-end->next line", lambda r: r["extra"]["edge_mi_line"], 3),
            ("(b) hapax share @10k", lambda r: r["extra"]["hapax_share_10k"], 3),
            ("    hapax share @20k", lambda r: r["extra"]["hapax_share_20k"], 3),
            ("    hapax share all tokens", lambda r: r["extra"]["hapax_share_all"], 3),
            ("(c) Moran I wordlen lag1", lambda r: r["extra"]["moran_I_wordlen_lag1"], 3),
            ("    Moran I within-line pairs", lambda r: r["extra"]["moran_I_wordlen_lag1_within_line"], 3),
            ("(d) glyph position entropy (max 2.32)", lambda r: r["extra"]["position_entropy_bits"], 3),
            ("(e) bits/char ltr", lambda r: r["extra"]["bits_per_char_ltr"], 3),
            ("    bits/char rtl", lambda r: r["extra"]["bits_per_char_rtl"], 3),
            ("    asymmetry ltr - rtl", lambda r: r["extra"]["directional_asymmetry_ltr_minus_rtl"], 4)]


def winner(r):
    ov = r["bake"]["overall"]
    return min(ov, key=lambda m: ov[m]["bits_per_token"])


# headline numbers for the flips section: (label, accessor, kind)
HEADLINES = [
    ("Heaps beta", lambda r: r["lex"]["all"]["beta"]),
    ("late/early new-type rate", lambda r: r["lex"]["all"]["rate_ratio_last20_first20"]),
    ("edit-1 locality excess (recent - far)", lambda r: r["lex"]["all"]["edit1_share_recent200"] - r["lex"]["all"]["edit1_share_far"]),
    ("slot occupancy PxCxS (all types)", lambda r: r["slot"]["all_types"]["occupancy_3d"]),
    ("table-likeness tok-weighted (all types)", lambda r: r["slot"]["all_types"]["table_likeness_weighted"]),
    ("core crowding: core edit-1 share (all types)", lambda r: r["slot"]["all_types"]["core_edit1_share"]),
    ("adjacent MI (word boundaries given)", lambda r: r["info"]["word_boundaries_given"]["adjacent"]["mi"]),
    ("page-level MI: same_page_far (wbg)", lambda r: r["info"]["word_boundaries_given"]["same_page_far"]["mi"]),
    ("same-col minus other-col prev-line MI (wbg)", lambda r: r["info"]["word_boundaries_given"]["prev_line_same_col"]["mi"] - r["info"]["word_boundaries_given"]["prev_line_other_col"]["mi"]),
    ("bake-off winner", winner),
    ("markov3 - unigram_gt bits/token", lambda r: r["bake"]["overall"]["markov3"]["bits_per_token"] - r["bake"]["overall"]["unigram_gt"]["bits_per_token"]),
    ("edge MI word->next word", lambda r: r["extra"]["edge_mi_word"]),
    ("hapax share @10k", lambda r: r["extra"]["hapax_share_10k"]),
    ("Moran's I word length lag 1", lambda r: r["extra"]["moran_I_wordlen_lag1"]),
    ("glyph position entropy", lambda r: r["extra"]["position_entropy_bits"]),
    ("ltr - rtl bits/char asymmetry", lambda r: r["extra"]["directional_asymmetry_ltr_minus_rtl"]),
]


def relation(v, lat, ita):
    if v > max(lat, ita):
        return "above both"
    if v < min(lat, ita):
        return "below both"
    return "between (Lat>V>Ita)" if lat > ita else "between (Ita>V>Lat)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="subsample each corpus to 25k tokens, 5 shuffles")
    args = ap.parse_args()
    base_path = next((p for p in BASELINES if p.exists()), None)
    if base_path is None:
        sys.exit("no baseline json (results_m0_newmetrics.json / results_d1_newmetrics.json)")
    base = json.loads(base_path.read_text(encoding="utf-8"))
    R = {EVA: base["voynich_eva"]}
    sets = []
    for name, fn in COLS[1:]:
        pg = M.meta_json_pages(TRANSLIT / fn)
        if args.fast:
            pg = subsample(pg, SUBSAMPLE)
        sets.append((name, pg))
    names = [c[0] for c in COLS]
    emit(f"# results_m2_robustness: PREREG robustness check 1 (second transliterations + glyph-collapsed), seed {M.SEED}")
    emit(f"# run {datetime.now().strftime('%Y-%m-%d %H:%M')} (system clock); baseline column {EVA} copied from {base_path.name}")
    emit(f"# converter: tools/ivtff_to_meta.py (paragraph loci only, unreadable tokens dropped, [a:b]->a, braces removed)")
    emit(f"# {EVA:14} tokens={base['voynich_eva']['lex']['n_tokens']:6}  types={base['voynich_eva']['lex']['n_types']:5}")
    for n, pg in sets:
        toks = M.flat_tokens(pg)
        alph = sorted({c for t in toks for c in t})
        emit(f"# {n:14} pages={len(pg):4}  lines={sum(len(p['lines']) for p in pg):5}  tokens={len(toks):6}  "
             f"types={len(set(toks)):5}  alphabet={len(alph):3} chars  quires={len({p['quire'] for p in pg})}")
    emit()
    timing = {}
    n_shuf = 5 if args.fast else 20
    for n, pg in sets:
        R[n] = {}
        t = time.time(); R[n]["lex"] = M.lexicon_growth(pg, n_shuffles=n_shuf); timing[(n, "lex")] = time.time() - t
        t = time.time(); R[n]["slot"], _ = M.slot_structure(pg); timing[(n, "slot")] = time.time() - t
        t = time.time(); R[n]["info"] = M.information_profile(pg); timing[(n, "info")] = time.time() - t
        t = time.time(); R[n]["bake"] = M.heldout_bakeoff(pg); timing[(n, "bake")] = time.time() - t
        t = time.time(); R[n]["extra"] = M.extra_signatures(pg); timing[(n, "extra")] = time.time() - t
        print(f"[{n}] done", {k[1]: round(v, 1) for k, v in timing.items() if k[0] == n}, flush=True)

    hdr = f"{'metric':44}" + "".join(f"{n:>14}" for n in names)
    moved = []  # (family, label, col, eva, val, rel change)

    def table(title, rows):
        emit(title)
        emit(hdr)
        for label, get, d in rows:
            vals = [get(R[n]) for n in names]
            emit(f"{label:44}" + "".join(f"{f(v, d):>14}" for v in vals))
            e = vals[0]
            if isinstance(e, (int, float)) and e is not None and not math.isnan(e) and abs(e) >= 0.005 and d > 0:
                for n, v in zip(names[1:], vals[1:]):
                    if v is not None and not math.isnan(v) and abs(v - e) / abs(e) > 0.20:
                        moved.append((label, n, e, v, (v - e) / abs(e)))
        emit()

    table("=== 1. LEXICON GROWTH ===", rows_lex())
    table("=== 2. SLOT STRUCTURE ===", rows_slot("all_types") + rows_slot("top_types"))
    for n in names[1:]:
        s = R[n]["slot"]
        emit(f"[{n}] H(glyph)={f(s['h_glyph'])}  prefixes: {' '.join(s['prefix_candidates'])}")
        emit(f"[{n}]   suffixes: {' '.join(s['suffix_candidates'])}")
    emit()
    table("=== 3. INFORMATION PROFILE (MI bits, plug-in minus permutation null) ===",
          rows_info("word_boundaries_given") + rows_info("bpe_resegmented"))
    table("=== 4. HELD-OUT BAKE-OFF (leave-one-quire-out; bits/token, bits/char; 'char' = one alphabet symbol) ===", rows_bake())
    emit(f"{'bake-off winner (overall)':44}" + "".join(f"{winner(R[n]):>18}" for n in names))
    emit()
    table("=== 5. EXTRA PUBLISHED SIGNATURES ===", rows_extra())

    # ---- flips ------------------------------------------------------------------
    emit("=== flips: sign/ordering of the Voynich value relative to the Latin (Caesar) and Italian (Dante) controls of the baseline run ===")
    emit(f"baseline controls from {base_path.name}; 'preserved' = every transliteration keeps the EVA relation")
    emit(f"{'headline':44}{'Latin':>9}{'Italian':>9}{'EVA rel.':>30}" + "".join(f"{n:>18}" for n in names[1:]) + "  preserved")
    flips = {}
    for label, get in HEADLINES:
        lat, ita = get(base[LAT]), get(base[ITA])
        if label == "bake-off winner":
            ev = get(R[EVA])
            vals = [get(R[n]) for n in names[1:]]
            ok = all(v == ev for v in vals)
            emit(f"{label:44}{lat[:9]:>9}{ita[:9]:>9}{ev:>30}" + "".join(f"{v:>18}" for v in vals) + f"  {'YES' if ok else 'NO'}")
            flips[label] = dict(latin=lat, italian=ita, eva=ev, values=dict(zip(names[1:], vals)), preserved=ok)
            continue
        ev = get(R[EVA])
        rel = relation(ev, lat, ita)
        cells, ok = [], True
        vals = {}
        for n in names[1:]:
            v = get(R[n]); r = relation(v, lat, ita)
            same = (r == rel)
            ok &= same
            cells.append(f"{f(v, 4)}{'' if same else '*'}")
            vals[n] = dict(value=v, relation=r)
        emit(f"{label:44}{f(lat, 4):>9}{f(ita, 4):>9}{(f(ev, 4) + ' ' + rel):>30}" + "".join(f"{c:>18}" for c in cells) + f"  {'YES' if ok else 'NO'}")
        flips[label] = dict(latin=lat, italian=ita, eva=ev, eva_relation=rel, values=vals, preserved=ok)
    emit("(* = relation to the controls differs from the EVA baseline)")
    emit()
    emit("=== magnitude moves > 20% vs ZL3b-EVA (any row above with |EVA| >= 0.005; bits/char rows are not comparable for ZL3b-glyph+ or GC2a, whose symbols are multi-letter glyphs / v101 glyphs) ===")
    for label, n, e, v, rc in moved:
        emit(f"  {label:44} {n:12} EVA={f(e, 4)} -> {f(v, 4)}  ({rc:+.0%})")
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
    for n in names[1:]:
        R[n]["lex"]["all"].pop("curve", None)
        R[n]["slot"].pop("glyph_position", None)
    OUTJ.write_text(json.dumps(clean(dict(results=R, flips=flips, moved=moved)), indent=1), encoding="utf-8")
    print("wrote", OUT, OUTJ)


if __name__ == "__main__":
    main()
