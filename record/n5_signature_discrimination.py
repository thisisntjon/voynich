"""N5: do the three "generation signatures" discriminate generation from encoded text?
(OPEN O-003.)

PRE-REGISTRATION (written 2026-10-17 19:18 PDT, from `date`, before any run of this
file; nothing below is changed after results are seen)

Signatures, computed with UNCHANGED code (scoreboard/metrics_new.py, m3_bakeoff_reconcile.py):
  (a) CHARWIN  = bits/token(unigram-GT-renorm) - bits/token(char3-WB), m3's proper-
                 distribution pair, m3's page split (pages shuffled with
                 random.Random(20261017), 80/20, one fold; m3.page_split + m3.score_folds).
                 Positive = the character model beats the word list.  Stronger = larger.
                 Manuscript reference (results_m3, page split): 11.245 - 11.151 = +0.094.
  (b) POSLOCK  = metrics_new.extra_signatures()['position_entropy_bits'].
                 Stronger = LOWER.  Manuscript reference 1.661 (m0).
  (c) MORAN    = metrics_new.extra_signatures()['moran_I_wordlen_lag1'].
                 Stronger = HIGHER.  Manuscript reference +0.141 (m0/m2).

Manuscript: ZL3b EVA paragraphs, whole (metrics_new.voynich_pages('eva'), as m0/m4) = primary.
  Robustness: RF1b, IT2a (data/translit/*.meta.json, as m2), and ZL3b cut to its first
  25,000 tokens (the size every other corpus is scored at).

Every non-manuscript corpus is cut to its first 25,000 tokens, whole lines, corpus order
(m4_phase1_board.subsample, as the board does).

ENCODED-text producers (E), membership fixed here:
  E1 flow_cipher_layer        data/controls_synthetic (K5 export of K1 cipher + M5 layer)
  E2 nomen_k2_x2              K5 export
  E3 nomen_k2_x8              K5 export
  E4 f3_flow_cipher           f3.cipher_stream(beta=1.5) seeds 1,2,3, poured into the
                              b4.pages() skeleton by c4.skeleton (the plain F3 flow cipher)
  E5 naibbe_reencrypt         f3.cipher_stream(beta=0) seeds 1,2,3 + c4 skeleton
  E6 naibbe_workbook          c4.naibbe_tokens() (Greshko's own encryption) + c4 skeleton
  E7 h1_ruled_flow            H1: f3 cipher beta=1.5 seeds 1,2,3 + c4 skeleton +
                              h1.apply_rules (RULE_P/RULE_M/RULE_SEED as filed)
  E8 k4_lossy_nomen           K4's four filed configs (pool 7025; k/w/beta = 4/120/1.5,
                              6/180/1.8, 8/260/2.0, 12/400/2.2), encrypt seed 1, book seed
                              20261017 (as k4.main)
MEANINGLESS producers (G), membership fixed here:
  G1 flow_gen_layer           K5 file (= k1.gen_pages seed 1) + k1.gen_pages seeds 2,3
  G2 timm_schinner            file
  G3 timm_schinner_ownlines   file
  G4 schwartz_reuse           file
  G5 c2_best                  file
  G6 n2_habit_p0.04           n1.gen_habit(p=0.04) seeds 1,2,3 on ZL3b_eva (table as n1/n2)
NATURAL-language controls (L): the board's 21 (corpora.CONTROLS + corpora_ext.NATURAL),
  built by m4_phase1_board.natural_from_control / natural_from_ext.  Context only.
CONTEXT rows (scored, in no range): every other data/controls_synthetic/*.meta.json.

Ranges: min..max over every run (producer x seed/config) of the family.
Decision rule per signature, per manuscript transliteration:
  inG = value in G range; inE = value in E range.
  strongE = the median of E producer means (seeds averaged) is at least as strong as
            the median of G producer means (direction as above).
  inG and inE                    -> NON-DIAGNOSTIC
  inG and not inE and strongE    -> NON-DIAGNOSTIC
  inG and not inE and not strongE-> DISCRIMINATES (points to generation)
  inE and not inG                -> POINTS TO ENCODING
  neither                        -> OUTSIDE BOTH (range rule gives no verdict; side reported)
The signature's verdict is the ZL3b-whole verdict; if RF1b, IT2a or ZL3b-25k gives a
different verdict it is reported as UNSTABLE alongside.
Natural-language range is reported for context; it does not enter the verdict.

Run checks: `python n5_signature_discrimination.py --check` scores only the manuscript
and must reproduce 1.661, +0.141 (m0) and +0.094 (m3 page split) before the full run.
Full run: `python n5_signature_discrimination.py` -> results_n5.txt.  Run once.
"""
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import b4_selfcite_sim as b4  # noqa: E402
import c2_section_generator as c2  # noqa: E402
import c4_naibbe_lines as c4  # noqa: E402
import corpora  # noqa: E402
import corpora_ext  # noqa: E402
import f3_flow_choice as f3  # noqa: E402
import h1_flow_lines as h1  # noqa: E402
import k1_joint_producer as k1  # noqa: E402
import k2_nomenclator as k2  # noqa: E402
import k4_lossy_nomenclator as k4  # noqa: E402
import m3_bakeoff_reconcile as m3  # noqa: E402
import m4_phase1_board as m4  # noqa: E402
import n1_habit_table as n1  # noqa: E402
from scoreboard import metrics_new as M  # noqa: E402

SEED = 20261017
N_SAMPLE = 25000
OUT = ROOT / "results_n5.txt"
SYNTH = ROOT / "data" / "controls_synthetic"
SIGS = ("CHARWIN", "POSLOCK", "MORAN")
STRONGER_HIGH = {"CHARWIN": True, "POSLOCK": False, "MORAN": True}
REF = {"POSLOCK": 1.661, "MORAN": 0.141, "CHARWIN": 0.094}
E_FILES = ["flow_cipher_layer", "nomen_k2_x2", "nomen_k2_x8"]
G_FILES = ["timm_schinner", "timm_schinner_ownlines", "schwartz_reuse", "c2_best"]
K4_CONFIGS = [(7025, 4, 120, 1.5), (7025, 6, 180, 1.8), (7025, 8, 260, 2.0), (7025, 12, 400, 2.2)]
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def by_to_pages(by):
    out = []
    for pg, recs in by.items():
        lines = [list(r["words"]) for r in recs if r["words"]]
        if lines:
            r0 = recs[0]
            out.append(dict(id=str(pg), section=str(r0.get("illus", "?")), hand=str(r0.get("hand", "?")),
                            quire=r0.get("quire"), lines=lines))
    return out


def score(pages):
    ex = M.extra_signatures(pages)
    acc = m3.score_folds(pages, m3.page_split(pages, SEED))
    rn = acc["unigram-GT-renorm"]; wb = acc["char3-WB"]
    return dict(CHARWIN=rn["bits"] / rn["tok"] - wb["bits"] / wb["tok"],
                POSLOCK=ex["position_entropy_bits"], MORAN=ex["moran_I_wordlen_lag1"],
                tokens=len(M.flat_tokens(pages)))


def manuscripts():
    zl = M.voynich_pages("eva")
    return [("ZL3b", zl),
            ("RF1b", m4.load_meta(ROOT / "data" / "translit" / "RF1b.meta.json")),
            ("IT2a", m4.load_meta(ROOT / "data" / "translit" / "IT2a.meta.json")),
            ("ZL3b-25k", m4.subsample(zl, N_SAMPLE))]


def cut(pages):
    return m4.subsample(pages, N_SAMPLE)


def file_pages(name):
    return m4.load_meta(SYNTH / f"{name}.meta.json")


def encoded_runs():
    by = b4.pages()
    R = f3.ratio_table(by)
    seq, tab = f3.naibbe_chunks()
    runs = [(n, n, file_pages(n)) for n in E_FILES]
    for s in (1, 2, 3):
        runs.append(("f3_flow_cipher", f"f3_flow_cipher s{s}",
                     by_to_pages(c4.skeleton(f3.cipher_stream(seq, tab, R, 1.5, s), by))))
    for s in (1, 2, 3):
        runs.append(("naibbe_reencrypt", f"naibbe_reencrypt s{s}",
                     by_to_pages(c4.skeleton(f3.cipher_stream(seq, tab, R, 0, s), by))))
    runs.append(("naibbe_workbook", "naibbe_workbook", by_to_pages(c4.skeleton(c4.naibbe_tokens(), by))))
    for s in (1, 2, 3):
        sk = c4.skeleton(f3.cipher_stream(seq, tab, R, h1.BETA, s), by)
        ruled = iter(h1.apply_rules([r["words"] for recs in sk.values() for r in recs]))
        sk2 = {pg: [dict(r, words=next(ruled)) for r in recs] for pg, recs in sk.items()}
        runs.append(("h1_ruled_flow", f"h1_ruled_flow s{s}", by_to_pages(sk2)))
    lby = k1.layout()
    Qi, Qe, para = k1.line_tables(lby)
    R1 = f3.ratio_table(lby)
    g = c2.Gen(lby)
    streams = k2.plaintext_streams(lby, shuffle=False)
    allw = [w for v in streams.values() for w in v]
    for pool_cap, k_ch, win, beta in K4_CONFIGS:
        book = k4.build_shared_codebook(allw, g.freq, pool_cap=pool_cap, k_choices=k_ch,
                                        rank_window=win, seed=20261017)[0]
        enc = k4.encrypt_shared(lby, streams, book, R1, Qi, Qe, para, beta=beta, seed=1)
        runs.append(("k4_lossy_nomen", f"k4 k={k_ch} w={win} b={beta}", by_to_pages(enc)))
    return runs


def meaningless_runs():
    runs = [("flow_gen_layer", "flow_gen_layer s1 (file)", file_pages("flow_gen_layer"))]
    lby = k1.layout()
    Qi, Qe, para = k1.line_tables(lby)
    R1 = f3.ratio_table(lby)
    g = c2.Gen(lby)
    for s in (2, 3):
        runs.append(("flow_gen_layer", f"flow_gen_layer s{s}", by_to_pages(k1.gen_pages(g, R1, Qi, Qe, para, True, s))))
    runs += [(n, n, file_pages(n)) for n in G_FILES]
    nby = n1.load("ZL3b_eva")
    ng = c2.Gen(nby)
    nR = f3.ratio_table(nby)
    table = n1.habit_table(ng)
    for s in (1, 2, 3):
        runs.append(("n2_habit_p0.04", f"n2_habit_p0.04 s{s}", by_to_pages(n1.gen_habit(ng, nR, s, 0.04, table))))
    return runs


def natural_runs():
    runs = [(n, n, m4.natural_from_control(n)[0]) for n in corpora.CONTROLS]
    for n in corpora_ext.NATURAL:
        try:
            runs.append((n, n, m4.natural_from_ext(n)[0]))
        except FileNotFoundError:
            emit(f"natural control missing: {n}")
    return runs


def context_runs():
    used = set(E_FILES) | set(G_FILES) | {"flow_gen_layer"}
    return [(p.name[:-10], p.name[:-10], m4.load_meta(p)) for p in sorted(SYNTH.glob("*.meta.json"))
            if p.name[:-10] not in used]


def stronger_or_equal(sig, a, b):
    return a >= b if STRONGER_HIGH[sig] else a <= b


def verdict(sig, v, fam):
    E, G = fam["E"], fam["G"]
    lo_e, hi_e = min(r[sig] for r in E["runs"]), max(r[sig] for r in E["runs"])
    lo_g, hi_g = min(r[sig] for r in G["runs"]), max(r[sig] for r in G["runs"])
    inE, inG = lo_e <= v <= hi_e, lo_g <= v <= hi_g
    medE = statistics.median(E["means"][sig].values())
    medG = statistics.median(G["means"][sig].values())
    strongE = stronger_or_equal(sig, medE, medG)
    if inG and inE:
        v_ = "NON-DIAGNOSTIC"
    elif inG and strongE:
        v_ = "NON-DIAGNOSTIC"
    elif inG:
        v_ = "DISCRIMINATES (points to generation)"
    elif inE:
        v_ = "POINTS TO ENCODING"
    else:
        allv = [r[sig] for r in E["runs"] + G["runs"]]
        if min(allv) <= v <= max(allv):
            side = "in a gap between the ranges"
        elif (v > max(allv)) == STRONGER_HIGH[sig]:
            side = "stronger than every producer run"
        else:
            side = "weaker than every producer run"
        v_ = f"OUTSIDE BOTH ({side})"
    return v_, dict(inE=inE, inG=inG, medE=medE, medG=medG, strongE=strongE)


def check():
    emit(f"N5 --check (manuscript only)  run={datetime.now().isoformat(timespec='seconds')}")
    ok = True
    for name, pg in manuscripts():
        r = score(pg)
        emit(f"  {name:<9} tokens={r['tokens']:6d}  CHARWIN {r['CHARWIN']:+.3f}  POSLOCK {r['POSLOCK']:.3f}  MORAN {r['MORAN']:+.3f}")
        if name == "ZL3b":
            for s in SIGS:
                good = abs(r[s] - REF[s]) < 0.0015
                ok &= good
                emit(f"    {s}: {r[s]:.4f} vs reference {REF[s]} -> {'REPRODUCED' if good else 'MISMATCH'}")
    emit("CHECK " + ("PASS" if ok else "FAIL"))
    return ok


def main():
    emit(f"N5 signature discrimination (O-003)  run={datetime.now().isoformat(timespec='seconds')}  seed={SEED}")
    emit("pre-registered in the n5_signature_discrimination.py docstring; prereg hash in n5_signature_discrimination.prereg.sha256")
    emit("CHARWIN = unigram-GT-renorm - char3-WB bits/token (page split, + = char wins, stronger high); "
         "POSLOCK = glyph position entropy (stronger low); MORAN = Moran I word length lag 1 (stronger high)")
    emit()
    ms = [(n, score(p)) for n, p in manuscripts()]
    emit("--- manuscript ---")
    for n, r in ms:
        emit(f"  {n:<9} tokens={r['tokens']:6d}  CHARWIN {r['CHARWIN']:+.3f}  POSLOCK {r['POSLOCK']:.3f}  MORAN {r['MORAN']:+.3f}")
    emit()
    fam = {}
    for key, title, builder in (("E", "ENCODED producers", encoded_runs), ("G", "MEANINGLESS producers", meaningless_runs),
                                ("L", "NATURAL-language controls", natural_runs), ("X", "CONTEXT (no range)", context_runs)):
        emit(f"--- {title} (first {N_SAMPLE} tokens) ---")
        runs, by_prod = [], {}
        for prod, label, pages in builder():
            try:
                r = score(cut(pages))
            except Exception as e:  # AMENDMENT 19:24: context rows only; E/G/L errors still raise
                if key != "X":
                    raise
                emit(f"  {label:<34} NOT SCORED ({type(e).__name__}: {e})")
                continue
            r["prod"] = prod
            runs.append(r)
            by_prod.setdefault(prod, []).append(r)
            emit(f"  {label:<34} tokens={r['tokens']:6d}  CHARWIN {r['CHARWIN']:+.3f}  POSLOCK {r['POSLOCK']:.3f}  MORAN {r['MORAN']:+.3f}")
        means = {s: {p: statistics.mean(x[s] for x in rs) for p, rs in by_prod.items()} for s in SIGS}
        fam[key] = dict(runs=runs, means=means)
        for s in SIGS:
            vals = [x[s] for x in runs]
            emit(f"  range {s:<8} {min(vals):+.3f} .. {max(vals):+.3f}   median of producer means {statistics.median(means[s].values()):+.3f}")
        emit()
    emit("=== VERDICTS (decision rule as pre-registered) ===")
    for s in SIGS:
        main_v, det = verdict(s, ms[0][1][s], fam)
        others = {n: verdict(s, r[s], fam)[0] for n, r in ms[1:]}
        unstable = [n for n, v in others.items() if v != main_v]
        lv = [x[s] for x in fam["L"]["runs"]]
        v0 = ms[0][1][s]
        emit(f"{s}: manuscript ZL3b {v0:+.3f}  inE={det['inE']}  inG={det['inG']}  "
             f"median E {det['medE']:+.3f} vs median G {det['medG']:+.3f} (E as strong: {det['strongE']})  "
             f"natural range {min(lv):+.3f}..{max(lv):+.3f} (ms inside: {min(lv) <= v0 <= max(lv)})")
        emit(f"  VERDICT {s}: {main_v}" + (f"   UNSTABLE: {', '.join(f'{n}={others[n]}' for n in unstable)}" if unstable else
                                          "   (same verdict on RF1b, IT2a, ZL3b-25k)"))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit(f"wrote {OUT}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    main()
