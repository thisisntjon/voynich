#!/usr/bin/env python3
"""
Experimental Investigation for Candidates 4, 5, 6, and 7 on Voynich (ZL3b):
  - Test 4 (Candidate 4): Combinatorial Codebook Matrix & Independent Attribute Link
  - Test 5 (Candidate 5): Highly Abbreviated Specialist Writing — Expansion & Edge-Restriction Test
  - Test 6 (Candidate 6): Syllabic Writing with Strict Sound-Combination Rules / Stolfi Grammar
  - Test 7 (Candidate 7): Formulaic Records / Procedural Notation — Cross-Entry Template Prediction

READ-ONLY Rule: Reads from . without modifying any file there.
Writes output strictly to scratch/results_c4_c5_c6_c7.txt (and copies script + results to parent scratch).
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import random
import re
import shutil
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

VOY_ROOT = Path(r".")
PARENT_SCRATCH = Path(r"<home>/.gemini/antigravity/brain/<session>/scratch")
OUR_SCRATCH = Path(r"<home>/.gemini/antigravity/brain/<session>/scratch")
OUT_PATH_PARENT = PARENT_SCRATCH / "results_c4_c5_c6_c7.txt"
OUT_PATH_OUR = OUR_SCRATCH / "results_c4_c5_c6_c7.txt"

if str(VOY_ROOT) not in sys.path:
    sys.path.insert(0, str(VOY_ROOT))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import a1_profile  # noqa: E402
import a2_position as a2_mod  # noqa: E402
import s37_affix_cadence_and_genres as s37  # noqa: E402
import scoreboard.metrics_new as mn  # noqa: E402
import scoreboard.run_v2 as R2  # noqa: E402
import vparse  # noqa: E402

SEED = 20261017
log_lines: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def entropy_from_counts(counts: Counter | dict | list | np.ndarray) -> float:
    if isinstance(counts, (Counter, dict)):
        arr = np.array([v for v in counts.values() if v > 0], dtype=np.float64)
    else:
        arr = np.asarray(counts, dtype=np.float64)
        arr = arr[arr > 0]
    n = float(arr.sum())
    if n <= 0:
        return 0.0
    p = arr / n
    return float(-(p * np.log2(p)).sum())


def mi_discrete(x: list | np.ndarray, y: list | np.ndarray) -> tuple[float, float, float, float]:
    """Return (MI(X;Y), H(X), H(Y), NMI_sym) in bits."""
    n = len(x)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0
    cx = Counter(x)
    cy = Counter(y)
    cxy = Counter(zip(x, y))
    hx = entropy_from_counts(cx)
    hy = entropy_from_counts(cy)
    hxy = entropy_from_counts(cxy)
    mi = max(0.0, hx + hy - hxy)
    nmi = (2.0 * mi / (hx + hy)) if (hx + hy) > 0 else 0.0
    return mi, hx, hy, nmi


def z_p_emp(obs: float, nulls: list[float] | np.ndarray) -> tuple[float, float, float, float, float]:
    arr = np.asarray(nulls, dtype=np.float64)
    mu = float(arr.mean())
    sd = float(arr.std())
    q99 = float(np.quantile(arr, 0.99))
    z = (obs - mu) / (sd if sd > 1e-12 else 1e-12)
    p = float((1 + np.sum(arr >= obs - 1e-12)) / (len(arr) + 1))
    return mu, sd, q99, z, p


# ==============================================================================
# TEST 4: COMBINATORIAL CODEBOOK MATRIX & INDEPENDENT ATTRIBUTE LINK
# ==============================================================================
def run_test_4(zl_pages: list[dict], zl_recs: list[dict]) -> None:
    emit("=" * 105)
    emit("TEST 4 (CANDIDATE 4): COMBINATORIAL CODEBOOK MATRIX FILL & INDEPENDENT ATTRIBUTE LINK")
    emit("=" * 105)

    para_recs = vparse.paragraph_text(zl_recs)
    all_toks = [w for r in para_recs for w in r["words"] if "?" not in w]
    seg = mn.SlotSegmenter(all_toks)

    # 4A: Combinatorial Cube Fill Rate, 2-way & 3-way MI / Interaction Information
    emit("\n--- 4A. Combinatorial Cube Fill Rate, 2-Way MI & 3-Way Interaction Information (P x C x S) ---")
    emit("Compares Voynich (ZL3b ALL, Currier A, Currier B) against 100 frequency-matched independent")
    emit("product-null draws (permuting P, C, S independently) and against combinatorial/taxonomic controls.")

    _, prose15_pages = R2.load_meta(VOY_ROOT / "data" / "controls_realline" / "cremma_prose15.meta.json")
    conlang_specs = dict((name, pgs) for name, pgs, _ in s37.build_conlang_and_combinatorial_controls(prose15_pages, seed=SEED))

    corpora_4a = [
        ("ZL3b_ALL", all_toks, seg),
        ("ZL3b_Currier_A", [w for r in para_recs if r["lang"] == "A" for w in r["words"] if "?" not in w], seg),
        ("ZL3b_Currier_B", [w for r in para_recs if r["lang"] == "B" for w in r["words"] if "?" not in w], seg),
    ]
    for cname in ("lull_ars_combinatoria_lines8", "taxonomic_conlang_syntax", "taxonomic_conlang_cadence"):
        ctoks = mn.flat_tokens(conlang_specs[cname])
        corpora_4a.append((cname, ctoks, mn.SlotSegmenter(ctoks)))
    corpora_4a.append(("cremma_prose15", mn.flat_tokens(prose15_pages), mn.SlotSegmenter(mn.flat_tokens(prose15_pages))))

    hdr_4a = (
        f"{'corpus':28s} | {'N_tok':>6s} {'P':>3s} {'C':>5s} {'S':>3s} | "
        f"{'Top50%':>6s} {'Cube50_Obs':>10s} {'Cube50_Null':>11s} {'O/N_50':>6s} | "
        f"{'MI(P;C)':>7s} {'MI(C;S)':>7s} {'MI(P;S)':>7s} {'TC_3way':>7s} {'II_3way':>8s}"
    )
    emit(hdr_4a)
    emit("-" * len(hdr_4a))

    rng = np.random.default_rng(SEED)
    detail_4a = {}
    for cname, toks, cseg in corpora_4a:
        triples = [cseg.segment(w) for w in toks]
        P_list = [t[0] for t in triples]
        C_list = [t[1] for t in triples]
        S_list = [t[2] for t in triples]

        uP = sorted(set(P_list))
        uC = sorted(set(C_list))
        uS = sorted(set(S_list))
        nP, nC, nS = len(uP), len(uC), len(uS)

        c_counts = Counter(C_list)
        top50_cores = {c for c, _ in c_counts.most_common(50)}
        n_top_actual = min(50, nC)
        top50_idx = [i for i, c in enumerate(C_list) if c in top50_cores]
        top50_share = len(top50_idx) / len(toks)

        P_50 = [P_list[i] for i in top50_idx]
        C_50 = [C_list[i] for i in top50_idx]
        S_50 = [S_list[i] for i in top50_idx]

        max_cube50 = nP * n_top_actual * nS
        obs_cells50 = len(set(zip(P_50, C_50, S_50)))
        obs_fill50 = obs_cells50 / max_cube50 if max_cube50 else 0.0

        obs_pc50 = len(set(zip(P_50, C_50)))
        obs_cs50 = len(set(zip(C_50, S_50)))
        obs_ps50 = len(set(zip(P_50, S_50)))

        p50_arr = np.array([uP.index(p) for p in P_50], dtype=np.int64)
        c50_arr = np.array([sorted(top50_cores).index(c) for c in C_50], dtype=np.int64)
        s50_arr = np.array([uS.index(s) for s in S_50], dtype=np.int64)

        null_cells50 = []
        null_pc50 = []
        null_cs50 = []
        for _ in range(100):
            cp = rng.permutation(c50_arr)
            sp = rng.permutation(s50_arr)
            code3 = p50_arr * (n_top_actual * nS) + cp * nS + sp
            null_cells50.append(len(np.unique(code3)))
            null_pc50.append(len(np.unique(p50_arr * n_top_actual + cp)))
            null_cs50.append(len(np.unique(cp * nS + sp)))

        mu_cells50 = float(np.mean(null_cells50))
        sd_cells50 = float(np.std(null_cells50))
        ratio_50 = obs_cells50 / mu_cells50 if mu_cells50 > 0 else 0.0

        hp = entropy_from_counts(Counter(P_list))
        hc = entropy_from_counts(Counter(C_list))
        hs = entropy_from_counts(Counter(S_list))
        hpc = entropy_from_counts(Counter(zip(P_list, C_list)))
        hcs = entropy_from_counts(Counter(zip(C_list, S_list)))
        hps = entropy_from_counts(Counter(zip(P_list, S_list)))
        hpcs = entropy_from_counts(Counter(zip(P_list, C_list, S_list)))

        mi_pc = hp + hc - hpc
        mi_cs = hc + hs - hcs
        mi_ps = hp + hs - hps
        tc_3way = hp + hc + hs - hpcs
        ii_3way = tc_3way - (mi_pc + mi_cs + mi_ps)
        mi_ps_given_c = hpc + hcs - hc - hpcs

        p_all_arr = np.array([uP.index(p) for p in P_list], dtype=np.int64)
        c_all_arr = np.array([uC.index(c) for c in C_list], dtype=np.int64)
        s_all_arr = np.array([uS.index(s) for s in S_list], dtype=np.int64)
        null_tc = []
        for _ in range(100):
            cp = rng.permutation(c_all_arr)
            sp = rng.permutation(s_all_arr)
            code3 = p_all_arr * (nC * nS) + cp * nS + sp
            _, cnts = np.unique(code3, return_counts=True)
            h_null = entropy_from_counts(cnts)
            null_tc.append(hp + hc + hs - h_null)
        mu_tc = float(np.mean(null_tc))

        detail_4a[cname] = dict(
            n_tok=len(toks), nP=nP, nC=nC, nS=nS, top50_share=top50_share,
            max_cube50=max_cube50, obs_cells50=obs_cells50, obs_fill50=obs_fill50,
            mu_cells50=mu_cells50, sd_cells50=sd_cells50, ratio_50=ratio_50,
            obs_pc50=obs_pc50, mu_pc50=float(np.mean(null_pc50)), max_pc50=nP * n_top_actual,
            obs_cs50=obs_cs50, mu_cs50=float(np.mean(null_cs50)), max_cs50=n_top_actual * nS,
            obs_ps50=obs_ps50, max_ps50=nP * nS,
            hp=hp, hc=hc, hs=hs, mi_pc=mi_pc, mi_cs=mi_cs, mi_ps=mi_ps,
            tc_3way=tc_3way, mu_tc=mu_tc, ii_3way=ii_3way, mi_ps_given_c=mi_ps_given_c,
        )

        emit(
            f"{cname:28s} | {len(toks):6d} {nP:3d} {nC:5d} {nS:3d} | "
            f"{100*top50_share:5.1f}% {obs_cells50:4d} ({100*obs_fill50:4.1f}%) "
            f"{mu_cells50:6.1f}±{sd_cells50:4.1f} {ratio_50:5.2f}x | "
            f"{mi_pc:7.4f} {mi_cs:7.4f} {mi_ps:7.4f} {tc_3way:7.4f} {ii_3way:+8.4f}"
        )

    d_zl = detail_4a["ZL3b_ALL"]
    emit(f"\n  [ZL3b_ALL 2D & 3D Cube Anatomy on Top-50 Cores ({100*d_zl['top50_share']:.2f}% of all tokens)]:")
    emit(f"    - P x C_top50 face (29 x 50 = {d_zl['max_pc50']} cells): obs={d_zl['obs_pc50']} ({100*d_zl['obs_pc50']/d_zl['max_pc50']:.1f}%) vs indep_null={d_zl['mu_pc50']:.1f} ({100*d_zl['mu_pc50']/d_zl['max_pc50']:.1f}%), ratio={d_zl['obs_pc50']/d_zl['mu_pc50']:.2f}x")
    emit(f"    - C_top50 x S face (50 x 19 = {d_zl['max_cs50']} cells): obs={d_zl['obs_cs50']} ({100*d_zl['obs_cs50']/d_zl['max_cs50']:.1f}%) vs indep_null={d_zl['mu_cs50']:.1f} ({100*d_zl['mu_cs50']/d_zl['max_cs50']:.1f}%), ratio={d_zl['obs_cs50']/d_zl['mu_cs50']:.2f}x")
    emit(f"    - P x C_top50 x S cube (29 x 50 x 19 = {d_zl['max_cube50']} cells): obs={d_zl['obs_cells50']} ({100*d_zl['obs_fill50']:.2f}%) vs indep_null={d_zl['mu_cells50']:.1f} ({100*d_zl['mu_cells50']/d_zl['max_cube50']:.2f}%), ratio={d_zl['ratio_50']:.2f}x (z={(d_zl['obs_cells50']-d_zl['mu_cells50'])/d_zl['sd_cells50']:+.1f})")
    emit(f"    - Conditional MI(P; S | C) = {d_zl['mi_ps_given_c']:.4f} bits vs unconditional MI(P; S) = {d_zl['mi_ps']:.4f} bits (3-way Interaction II = {d_zl['ii_3way']:+.4f} bits)")
    emit(f"    - Total Correlation TC(P;C;S) = {d_zl['tc_3way']:.4f} bits vs indep_null = {d_zl['mu_tc']:.4f} bits (excess = {d_zl['tc_3way']-d_zl['mu_tc']:+.4f} bits)")

    # --------------------------------------------------------------------------
    # 4B: Independently Identifiable Page / Label Attribute Link Beyond Section & Hand
    # --------------------------------------------------------------------------
    emit("\n--- 4B.1: Q1 Label Locus/Unit Classes (Lz, Lf, Ls, Ln, Lt, Lc, Lp, L0) — Slot Link vs Hierarchy of Nulls ---")
    emit("Tests whether WholeWord (W), Prefix (P), Core (C), or Suffix (S) of the 1,164 label tokens links to")
    emit("label locus type (Lp=plant, Lz=zodiac, Ls=star, Lf=figure, Ln=nymph, Lt=tube, Lc=circle, L0=other)")
    emit("under (1) Free Shuffle, (2) Within-(Section, Hand) Token Shuffle, (3) Within-(Section, Hand) Folio-Block")
    emit("Permutation, and (4) Strictly Within-Page Shuffle on the 23 multi-unit pages (500 draws each).")

    lab_recs = [r for r in zl_recs if r["unit"].startswith("L")]
    lab_toks = [
        dict(w=w, unit=r["unit"], illus=r["illus"], hand=r["hand"], page=r["page"], line=r["line"],
             p=seg.segment(w)[0], c=seg.segment(w)[1], s=seg.segment(w)[2])
        for r in lab_recs for w in r["words"] if "?" not in w
    ]

    by_sh = defaultdict(list)
    by_page = defaultdict(list)
    for i, t in enumerate(lab_toks):
        by_sh[(t["illus"], t["hand"])].append(i)
        by_page[t["page"]].append(i)

    multi_unit_pages = {pg: idxs for pg, idxs in by_page.items() if len({lab_toks[i]["unit"] for i in idxs}) >= 2}
    multi_page_idxs = [i for idxs in multi_unit_pages.values() for i in idxs]
    emit(f"  Label inventory: {len(lab_toks)} tokens across {len(by_page)} pages; {len(multi_unit_pages)} pages have >=2 distinct L* unit types ({len(multi_page_idxs)} tokens).")
    for sh, idxs in sorted(by_sh.items(), key=lambda x: -len(x[1])):
        u_cnt = Counter(lab_toks[i]["unit"] for i in idxs)
        if len(u_cnt) >= 2:
            emit(f"    Multi-unit stratum (illus={sh[0]}, hand={sh[1]}): n={len(idxs)} tokens, units={dict(u_cnt.most_common())}")

    hdr_4b1 = (
        f"{'Component':12s} | {'V_typ':>5s} {'obs_MI':>7s} | "
        f"{'Free_mu':>7s} {'Free_z':>7s} | {'WinSH_mu':>8s} {'WinSH_z':>7s} {'p_SH':>6s} | "
        f"{'FolSH_mu':>8s} {'FolSH_z':>7s} {'p_Fol':>6s} | {'WinPg_obs':>9s} {'WinPg_mu':>8s} {'WinPg_z':>7s} {'p_Pg':>6s}"
    )
    emit("\n" + hdr_4b1)
    emit("-" * len(hdr_4b1))

    units_all = [t["unit"] for t in lab_toks]
    units_mp = [lab_toks[i]["unit"] for i in multi_page_idxs]

    n_perm = 500
    py_rng = random.Random(SEED)
    perm_free = []
    perm_win_sh = []
    perm_fol_sh = []
    perm_win_pg = []

    sh_pages = defaultdict(list)
    for pg, idxs in by_page.items():
        sh = (lab_toks[idxs[0]]["illus"], lab_toks[idxs[0]]["hand"])
        sh_pages[sh].append(pg)

    for _ in range(n_perm):
        u_f = units_all[:]
        py_rng.shuffle(u_f)
        perm_free.append(u_f)

        u_sh = units_all[:]
        for idxs in by_sh.values():
            vals = [u_sh[i] for i in idxs]
            py_rng.shuffle(vals)
            for i, v in zip(idxs, vals):
                u_sh[i] = v
        perm_win_sh.append(u_sh)

        u_fol = units_all[:]
        for sh, pgs in sh_pages.items():
            if len(pgs) <= 1:
                continue
            shuf_pgs = pgs[:]
            py_rng.shuffle(shuf_pgs)
            for pg_dst, pg_src in zip(pgs, shuf_pgs):
                src_units = [units_all[i] for i in by_page[pg_src]]
                for idx_k, i_dst in enumerate(by_page[pg_dst]):
                    u_fol[i_dst] = src_units[idx_k % len(src_units)]
        perm_fol_sh.append(u_fol)

        u_pg = [lab_toks[i]["unit"] for i in multi_page_idxs]
        offset = 0
        for pg, idxs in multi_unit_pages.items():
            L = len(idxs)
            sub = u_pg[offset : offset + L]
            py_rng.shuffle(sub)
            u_pg[offset : offset + L] = sub
            offset += L
        perm_win_pg.append(u_pg)

    for comp_key, comp_label in [("w", "WholeWord"), ("p", "Prefix"), ("c", "Core"), ("s", "Suffix")]:
        vals_all = [t[comp_key] for t in lab_toks]
        vals_mp = [lab_toks[i][comp_key] for i in multi_page_idxs]
        v_typ = len(set(vals_all))

        obs_mi, _, _, _ = mi_discrete(vals_all, units_all)
        null_f = [mi_discrete(vals_all, u)[0] for u in perm_free]
        null_sh = [mi_discrete(vals_all, u)[0] for u in perm_win_sh]
        null_fol = [mi_discrete(vals_all, u)[0] for u in perm_fol_sh]

        obs_mp, _, _, _ = mi_discrete(vals_mp, units_mp)
        null_pg = [mi_discrete(vals_mp, u)[0] for u in perm_win_pg]

        mu_f, _, _, z_f, _ = z_p_emp(obs_mi, null_f)
        mu_sh, _, _, z_sh, p_sh = z_p_emp(obs_mi, null_sh)
        mu_fol, _, _, z_fol, p_fol = z_p_emp(obs_mi, null_fol)
        mu_pg, _, _, z_pg, p_pg = z_p_emp(obs_mp, null_pg)

        emit(
            f"{comp_label:12s} | {v_typ:5d} {obs_mi:7.4f} | "
            f"{mu_f:7.4f} {z_f:+7.2f} | {mu_sh:8.4f} {z_sh:+7.2f} {p_sh:6.3f} | "
            f"{mu_fol:8.4f} {z_fol:+7.2f} {p_fol:6.3f} | {obs_mp:9.4f} {mu_pg:8.4f} {z_pg:+7.2f} {p_pg:6.3f}"
        )

    # 4B.2: Independent Page-Level Attributes in Herbal (H), Pharmaceutical (P), and Zodiac (Z)
    emit("\n--- 4B.2: Independent Page & Botanical/Astrological Attribute Link Beyond (Section, Hand, Quire) ---")

    raw_zl = (VOY_ROOT / "data" / "ZL3b-n.txt").read_text(encoding="ascii", errors="replace").splitlines()
    page_meta = {}
    cur_pg = None
    for ln in raw_zl:
        m = vparse.PAGE_RE.match(ln)
        if m:
            cur_pg = m.group(1)
            vars_d = dict(vparse.VAR_RE.findall(m.group(2)))
            page_meta[cur_pg] = dict(vars=vars_d, comments=[], same_plant=[], plant_id="")
        elif ln.startswith("#") and cur_pg is not None:
            page_meta[cur_pg]["comments"].append(ln)
            if "same plant" in ln.lower():
                refs = re.findall(r"f\d+[rv]\d*", ln)
                page_meta[cur_pg]["same_plant"].extend([r for r in refs if r != cur_pg])
            if "plant id:" in ln.lower():
                page_meta[cur_pg]["plant_id"] += " " + ln.split(":", 1)[1].strip()

    sherman_path = VOY_ROOT / "data" / "external" / "cribs" / "julianbunn_GA_Sherman_spreadsheet.htm.txt"
    sherman_lines = [ln.strip() for ln in sherman_path.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    folio_re = re.compile(r"^f\d+[rv]\d*$")
    botanical_genus = {}
    i_ln = 0
    while i_ln < len(sherman_lines):
        if folio_re.match(sherman_lines[i_ln]):
            pg = sherman_lines[i_ln]
            block = []
            i_ln += 1
            while i_ln < len(sherman_lines) and not folio_re.match(sherman_lines[i_ln]):
                block.append(sherman_lines[i_ln])
                i_ln += 1
            genera = set()
            for b in block:
                for m_lat in re.finditer(r"\b([A-Z][a-z]{3,})\s+[a-z]{3,}\b", b):
                    w1 = m_lat.group(1)
                    if w1 not in ("Deadly", "Diffuse", "Water", "Feathery", "Alpine", "Wolfs", "Tennis",
                                  "Bear", "Green", "Sweet", "Wild", "Common", "marsh", "Yellow", "White",
                                  "Black", "Great", "Small", "Prickly", "Purple", "Dwarf", "Field"):
                        genera.add(w1)
            if genera:
                botanical_genus[pg] = sorted(genera)
        else:
            i_ln += 1

    cross_pairs = set()
    for pg, md in page_meta.items():
        for ref_pg in md["same_plant"]:
            if pg in page_meta and ref_pg in page_meta:
                cross_pairs.add(tuple(sorted((pg, ref_pg))))
    cross_pairs = sorted(cross_pairs)

    pg_to_words = defaultdict(list)
    for r in para_recs:
        ws = [w for w in r["words"] if "?" not in w]
        if ws:
            pg_to_words[r["page"]].extend(ws)

    para0_by_page = defaultdict(list)
    for ln in raw_zl:
        m = vparse.LINE_RE.match(ln)
        if m:
            pg, _, loc_type, unit, text = m.groups()
            if unit.startswith("P") and loc_type in ("@", "*"):
                ws = [w for w in vparse.clean(text) if "?" not in w]
                if ws:
                    para0_by_page[pg].append(ws[0])

    valid_cross = [(p1, p2) for p1, p2 in cross_pairs if pg_to_words[p1] and pg_to_words[p2]]
    emit(f"  [Test 4B.2a] Petersen/Stolfi Cross-Referenced Plant Pairs in ZL3b-n.txt: {len(valid_cross)} valid folio pairs: {valid_cross}")

    def jaccard(s1: set, s2: set) -> float:
        return len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0.0

    def cosine_cnt(c1: Counter, c2: Counter) -> float:
        keys = set(c1) | set(c2)
        num = sum(c1[k] * c2[k] for k in keys)
        d1 = math.sqrt(sum(v * v for v in c1.values()))
        d2 = math.sqrt(sum(v * v for v in c2.values()))
        return num / (d1 * d2) if (d1 > 0 and d2 > 0) else 0.0

    if valid_cross:
        all_h_p_pages = [pg for pg in pg_to_words if page_meta[pg]["vars"].get("I") in ("H", "P")]
        for comp_name, fn_extract in [
            ("WholeWord_Jaccard", lambda ws: set(ws)),
            ("Core_Jaccard", lambda ws: {seg.segment(w)[1] for w in ws}),
            ("Prefix_Cosine", lambda ws: Counter(seg.segment(w)[0] for w in ws)),
            ("Suffix_Cosine", lambda ws: Counter(seg.segment(w)[2] for w in ws)),
            ("Para0_Core_Match", lambda ws, pg=None: {seg.segment(w)[1] for w in para0_by_page.get(pg, [])}),
        ]:
            if comp_name == "Para0_Core_Match":
                obs_val = float(np.mean([jaccard(fn_extract(None, p1), fn_extract(None, p2)) for p1, p2 in valid_cross]))
                null_vals = []
                for _ in range(1000):
                    rp = [(p1, py_rng.choice(all_h_p_pages)) for p1, _ in valid_cross]
                    null_vals.append(float(np.mean([jaccard(fn_extract(None, a), fn_extract(None, b)) for a, b in rp])))
            elif "Cosine" in comp_name:
                obs_val = float(np.mean([cosine_cnt(fn_extract(pg_to_words[p1]), fn_extract(pg_to_words[p2])) for p1, p2 in valid_cross]))
                null_vals = []
                for _ in range(1000):
                    rp = [(p1, py_rng.choice(all_h_p_pages)) for p1, _ in valid_cross]
                    null_vals.append(float(np.mean([cosine_cnt(fn_extract(pg_to_words[a]), fn_extract(pg_to_words[b])) for a, b in rp])))
            else:
                obs_val = float(np.mean([jaccard(fn_extract(pg_to_words[p1]), fn_extract(pg_to_words[p2])) for p1, p2 in valid_cross]))
                null_vals = []
                for _ in range(1000):
                    rp = [(p1, py_rng.choice(all_h_p_pages)) for p1, _ in valid_cross]
                    null_vals.append(float(np.mean([jaccard(fn_extract(pg_to_words[a]), fn_extract(pg_to_words[b])) for a, b in rp])))
            mu, sd, _, z, p = z_p_emp(obs_val, null_vals)
            emit(f"    {comp_name:20s}: obs={obs_val:.4f} vs random (H,P) pair null={mu:.4f}±{sd:.4f} (z={z:+.2f}, p={p:.3f})")

    h1_pages = [pg for pg in pg_to_words if page_meta[pg]["vars"].get("I") == "H" and page_meta[pg]["vars"].get("H") == "1"]
    emit(f"\n  [Test 4B.2b] Herbal Hand-1 Pages (n={len(h1_pages)} pages) — Link to Independent Page Attributes vs Page-Perm Null:")

    # Attribute 1: Paragraph layout (1 paragraph vs 2+ paragraphs on Herbal Hand-1 pages)
    h1_para_cnt = {pg: ("1_para" if len(para0_by_page.get(pg, [])) <= 1 else "2plus_para") for pg in h1_pages}
    emit(f"    (i) Herbal Hand-1 Page Layout (1_para vs 2plus_para: {dict(Counter(h1_para_cnt.values()))}):")
    tok_h1 = [(pg, h1_para_cnt[pg], w, *seg.segment(w)) for pg in h1_pages for w in pg_to_words[pg]]
    pg_list_h1 = sorted(h1_pages)
    lay_list_pg = [h1_para_cnt[pg] for pg in pg_list_h1]
    for idx_f, fname in [(3, "Prefix"), (4, "Core"), (5, "Suffix")]:
        f_vals = [t[idx_f] for t in tok_h1]
        y_vals = [t[1] for t in tok_h1]
        obs_mi, _, _, _ = mi_discrete(f_vals, y_vals)
        null_pg_mi = []
        for _ in range(300):
            shuf_y = lay_list_pg[:]
            py_rng.shuffle(shuf_y)
            m_shuf = dict(zip(pg_list_h1, shuf_y))
            null_pg_mi.append(mi_discrete(f_vals, [m_shuf[t[0]] for t in tok_h1])[0])
        mu, sd, _, z, p = z_p_emp(obs_mi, null_pg_mi)
        emit(f"        MI({fname:6s}; ParaCount_Layout): obs={obs_mi:.4f} vs page-perm null={mu:.4f}±{sd:.4f} (excess={obs_mi-mu:+.4f}, z={z:+.2f}, p={p:.3f})")

    genus_to_pages = defaultdict(list)
    for pg in h1_pages:
        for g in botanical_genus.get(pg, []):
            genus_to_pages[g].append(pg)
    same_genus_pairs = set()
    for g, pgs in genus_to_pages.items():
        if len(pgs) >= 2:
            for a_i in range(len(pgs)):
                for b_i in range(a_i + 1, len(pgs)):
                    same_genus_pairs.add(tuple(sorted((pgs[a_i], pgs[b_i]))))
    same_genus_pairs = sorted(same_genus_pairs)
    emit(f"    (ii) Sherwood/Scott Same-Genus Herbal Hand-1 Folio Pairs (n={len(same_genus_pairs)} pairs across {len([g for g,ps in genus_to_pages.items() if len(ps)>=2])} shared genera):")
    if same_genus_pairs:
        for comp_name, fn_extract in [
            ("Core_Jaccard", lambda ws: {seg.segment(w)[1] for w in ws}),
            ("Prefix_Cosine", lambda ws: Counter(seg.segment(w)[0] for w in ws)),
            ("Suffix_Cosine", lambda ws: Counter(seg.segment(w)[2] for w in ws)),
            ("Para0_Prefix_Match", lambda pg: {seg.segment(w)[0] for w in para0_by_page.get(pg, [])}),
        ]:
            if comp_name == "Para0_Prefix_Match":
                obs_v = float(np.mean([jaccard(fn_extract(p1), fn_extract(p2)) for p1, p2 in same_genus_pairs]))
                null_v = [float(np.mean([jaccard(fn_extract(p1), fn_extract(py_rng.choice(h1_pages))) for p1, _ in same_genus_pairs])) for _ in range(500)]
            elif "Cosine" in comp_name:
                obs_v = float(np.mean([cosine_cnt(fn_extract(pg_to_words[p1]), fn_extract(pg_to_words[p2])) for p1, p2 in same_genus_pairs]))
                null_v = [float(np.mean([cosine_cnt(fn_extract(pg_to_words[p1]), fn_extract(pg_to_words[py_rng.choice(h1_pages)])) for p1, _ in same_genus_pairs])) for _ in range(500)]
            else:
                obs_v = float(np.mean([jaccard(fn_extract(pg_to_words[p1]), fn_extract(pg_to_words[p2])) for p1, p2 in same_genus_pairs]))
                null_v = [float(np.mean([jaccard(fn_extract(pg_to_words[p1]), fn_extract(pg_to_words[py_rng.choice(h1_pages)])) for p1, _ in same_genus_pairs])) for _ in range(500)]
            mu, sd, _, z, p = z_p_emp(obs_v, null_v)
            emit(f"        {comp_name:20s}: obs={obs_v:.4f} vs random H1 pair null={mu:.4f}±{sd:.4f} (z={z:+.2f}, p={p:.3f})")

    ZODIAC_MAP = {
        "f70v2": ("Pisces", "Water", "Winter"),
        "f70v1": ("Aries", "Fire", "Spring"),
        "f71r":  ("Taurus", "Earth", "Spring"),
        "f71v":  ("Taurus", "Earth", "Spring"),
        "f72r1": ("Gemini", "Air", "Spring"),
        "f72r2": ("Cancer", "Water", "Summer"),
        "f72r3": ("Leo", "Fire", "Summer"),
        "f72v3": ("Virgo", "Earth", "Autumn"),
        "f72v2": ("Libra", "Air", "Autumn"),
        "f72v1": ("Scorpio", "Water", "Autumn"),
        "f73r":  ("Sagittarius", "Fire", "Winter"),
        "f73v":  ("Capricorn", "Earth", "Winter"),
    }
    lz_toks = [t for t in lab_toks if t["unit"] == "Lz" and t["page"] in ZODIAC_MAP]
    z_pages = sorted(ZODIAC_MAP.keys())
    emit(f"    (iii) Zodiac Lz Labels ({len(lz_toks)} tokens across {len(z_pages)} pages) — Link to Classical Element & Season vs Page-Block Null:")
    for attr_idx, attr_name in [(1, "Element_4"), (2, "Season_4")]:
        attr_vals = [ZODIAC_MAP[t["page"]][attr_idx] for t in lz_toks]
        for comp_key, comp_label in [("p", "Prefix"), ("c", "Core"), ("s", "Suffix")]:
            c_vals = [t[comp_key] for t in lz_toks]
            obs_mi, _, _, _ = mi_discrete(c_vals, attr_vals)
            pg_attr_list = [ZODIAC_MAP[pg][attr_idx] for pg in z_pages]
            null_z_mi = []
            for _ in range(500):
                shuf_a = pg_attr_list[:]
                py_rng.shuffle(shuf_a)
                m_a = dict(zip(z_pages, shuf_a))
                null_z_mi.append(mi_discrete(c_vals, [m_a[t["page"]] for t in lz_toks])[0])
            mu, sd, _, z, p = z_p_emp(obs_mi, null_z_mi)
            emit(f"        MI({comp_label:6s}; {attr_name:9s}): obs={obs_mi:.4f} vs page-block null={mu:.4f}±{sd:.4f} (excess={obs_mi-mu:+.4f}, z={z:+.2f}, p={p:.3f})")


# ==============================================================================
# TEST 5: HIGHLY ABBREVIATED SPECIALIST WRITING — EXPANSION & EDGE-RESTRICTION
# ==============================================================================
def compute_word_internal_rigidity(tokens: list[str], min_char_count: int = 50) -> dict:
    char_bins = defaultdict(lambda: np.zeros(5, dtype=np.float64))
    char_tot = Counter()
    bigrams = Counter()
    inits = Counter()
    finals = Counter()

    for w in tokens:
        L = len(w)
        if L == 0:
            continue
        inits[w[0]] += 1
        finals[w[-1]] += 1
        for i, ch in enumerate(w):
            char_tot[ch] += 1
            if L == 1:
                b = 0
            elif i == 0:
                b = 0
            elif i == L - 1:
                b = 4
            else:
                rel = i / (L - 1)
                b = 1 if rel < 0.38 else (2 if rel <= 0.62 else 3)
            char_bins[ch][b] += 1.0
        for a, b_ch in zip(w[:-1], w[1:]):
            if a != b_ch:
                bigrams[(a, b_ch)] += 1

    log2_5 = math.log2(5.0)
    weighted_h = 0.0
    tot_w = 0.0
    for ch, cnt in char_tot.items():
        if cnt < min_char_count:
            continue
        h = entropy_from_counts(char_bins[ch]) / log2_5
        weighted_h += cnt * h
        tot_w += cnt
    h_pos_norm = weighted_h / tot_w if tot_w > 0 else float("nan")

    chars_all = sorted(char_tot.keys())
    num_asym = 0
    den_asym = 0
    for i_a, a in enumerate(chars_all):
        for b in chars_all[i_a + 1 :]:
            cab = bigrams[(a, b)]
            cba = bigrams[(b, a)]
            num_asym += abs(cab - cba)
            den_asym += cab + cba
    a_ord = num_asym / den_asym if den_asym > 0 else float("nan")

    n_tok = len(tokens) or 1
    top3_fin = sum(v for _, v in finals.most_common(3)) / n_tok
    top3_ini = sum(v for _, v in inits.most_common(3)) / n_tok
    ce = a1_profile.char_entropies(tokens)
    return dict(
        h_pos_norm=h_pos_norm,
        a_ord=a_ord,
        top3_fin=top3_fin,
        top3_ini=top3_ini,
        h2=ce["h2"],
    )


def build_latin_abbreviation_simulations(med_pages: list[dict], seed: int = SEED) -> list[tuple[str, list[dict], str]]:
    def abbrev_tachy(w: str) -> str:
        s = w
        for pfx, rep in [("con", "9"), ("com", "9"), ("per", "p~"), ("pro", "p;"), ("prae", "p^"), ("pre", "p^"), ("quod", "qd"), ("quia", "qa")]:
            if s.startswith(pfx) and len(s) > len(pfx):
                s = rep + s[len(pfx):]
                break
        for sfx, rep in [("orum", "4"), ("arum", "4"), ("ibus", "b;"), ("tur", "t~"), ("mur", "m~"),
                         ("us", "9"), ("um", "m~"), ("is", ";"), ("em", "e~"), ("am", "a~"), ("er", "~"), ("ri", "^")]:
            if s.endswith(sfx) and len(s) > len(sfx) + 1:
                s = s[:-len(sfx)] + rep
                break
        s = s.replace("ae", "e").replace("oe", "e").replace("ct", "t")
        return s

    def abbrev_radical(w: str) -> str:
        if len(w) <= 3:
            return w
        ending = ""
        for sfx, rep in [("us", "y"), ("um", "m"), ("is", "s"), ("em", "n"), ("am", "n"),
                         ("ur", "r"), ("er", "r"), ("or", "r"), ("ae", "y"), ("ia", "y"), ("io", "o")]:
            if w.endswith(sfx):
                ending = rep
                break
        if not ending:
            ending = w[-1]
        stem = w[:3]
        return stem + ending

    pages_5a, pages_5b, pages_5c, pages_5d = [], [], [], []
    for p in med_pages:
        lns_a, lns_b, lns_c, lns_d = [], [], [], []
        for li, ln in enumerate(p["lines"]):
            if not ln:
                continue
            L = len(ln)
            lns_a.append([abbrev_tachy(w) for w in ln])
            lns_b.append([abbrev_radical(w) for w in ln])

            row_c = []
            for k, w in enumerate(ln):
                if k == 0:
                    row_c.append(w)
                elif k == L - 1:
                    row_c.append(w[:min(3, len(w))] + ("m" if len(w) >= 4 else ""))
                elif k == L - 2 and L >= 5:
                    row_c.append(abbrev_radical(w))
                else:
                    row_c.append(abbrev_tachy(w))
            lns_c.append(row_c)

            row_d = []
            for k, w in enumerate(ln):
                if k == 0:
                    hdr = "recipe" if li == 0 else ("item" if li % 2 == 0 else "accipe")
                    row_d.append(hdr + w[:2])
                elif k == L - 1:
                    dose = "ana" if (li + k) % 3 == 0 else ("dr" if (li + k) % 3 == 1 else "qs")
                    row_d.append(dose)
                else:
                    row_d.append(abbrev_radical(w))
            lns_d.append(row_d)

        pages_5a.append(dict(p, lines=lns_a))
        pages_5b.append(dict(p, lines=lns_b))
        pages_5c.append(dict(p, lines=lns_c))
        pages_5d.append(dict(p, lines=lns_d))

    return [
        ("Sim5A_Heavy_Tachygraphic", pages_5a, "Medieval Latin medical recipes with heavy tachygraphic brevigraphs"),
        ("Sim5B_Radical_3ch_Susp", pages_5b, "Specialist 3-char stem truncation + standardized 1-char case ending"),
        ("Sim5C_RightMargin_Susp", pages_5c, "Right-margin space-saving suspension (full slot 0, suspended line-final)"),
        ("Sim5D_Formulaic_Rec_Abbrev", pages_5d, "Formulaic recipe header at slot 0 + radical abbrev mid + dose at line end"),
    ]


def run_test_5(zl_pages: list[dict]) -> None:
    emit("\n" + "=" * 105)
    emit("TEST 5 (CANDIDATE 5): HIGHLY ABBREVIATED SPECIALIST WRITING — EXPANSION & EDGE-RESTRICTION TEST")
    emit("=" * 105)
    emit("Compares Voynich (ZL3b ALL, A, B) directly against CREMMA medieval medical/specialist manuscripts")
    emit("WITH tachygraphic abbreviation marks preserved (_marks) and 4 explicit abbreviation/suspension models.")
    emit("Metrics:")
    emit("  - H_pos : Within-word 5-bin normalized positional entropy (lower = stricter internal glyph order)")
    emit("  - A_ord : Within-word character-bigram unidirectional asymmetry (higher = stricter one-way glyph order)")
    emit("  - Fin3% : Share of word tokens ending in the top-3 word-final characters")
    emit("  - h2    : Conditional character entropy H(c_i | c_{i-1})")
    emit("  - A1_jsd, A3_edge, A5_I_within (vs q99), I_core, S1->P2, C1->C2, A6_CHARWIN")

    realline_dir = VOY_ROOT / "data" / "controls_realline"
    med_ms = ["H318", "CLM13027", "Latin16195", "Phi_10a135"]
    med_base_pages, med_marks_pages = [], []
    indiv_corpora = []
    for ms in med_ms:
        _, pb = R2.load_meta(realline_dir / f"cremma_{ms}.meta.json")
        _, pm = R2.load_meta(realline_dir / f"cremma_{ms}_marks.meta.json")
        med_base_pages.extend(pb)
        med_marks_pages.extend(pm)
        indiv_corpora.append((f"{ms}_base", pb))
        indiv_corpora.append((f"{ms}_marks", pm))

    _, eg_marks = R2.load_meta(realline_dir / "cremma_Egerton821_marks.meta.json")
    sims_5 = build_latin_abbreviation_simulations(med_base_pages, seed=SEED)

    test5_list = [
        ("ZL3b_ALL", zl_pages),
        ("ZL3b_Currier_A", [p for p in zl_pages if p.get("lang") == "A"]),
        ("ZL3b_Currier_B", [p for p in zl_pages if p.get("lang") == "B"]),
        ("CREMMA_Med_Recipes_base", med_base_pages),
        ("CREMMA_Med_Recipes_marks", med_marks_pages),
    ] + indiv_corpora + [("Egerton821_marks (Charms)", eg_marks)] + [(n, pg) for n, pg, _ in sims_5]

    hdr5 = (
        f"{'corpus_name':26s} | {'toks':>6s} | {'H_pos':>6s} {'A_ord':>6s} {'Fin3%':>6s} {'h2':>5s} | "
        f"{'A1_jsd':>7s} {'A3_edg':>7s} {'I_win':>7s} {'I_q99':>6s} {'I_core':>7s} | "
        f"{'S1->P2':>7s} {'C1->C2':>7s} {'CHARWIN':>8s}"
    )
    emit("\n" + hdr5)
    emit("-" * len(hdr5))

    for cname, pgs in test5_list:
        toks = mn.flat_tokens(pgs)
        rig = compute_word_internal_rigidity(toks, min_char_count=max(20, len(toks) // 500))
        bat = s37.evaluate_two_layer_battery(cname, pgs, "Test5", R2, mn, a2_mod)
        emit(
            f"{cname[:26]:26s} | {len(toks):6d} | "
            f"{rig['h_pos_norm']:6.4f} {rig['a_ord']:6.4f} {100*rig['top3_fin']:5.1f}% {rig['h2']:5.2f} | "
            f"{bat['jsd_first_exc']:+7.4f} {bat['cross_excess']:+7.4f} {bat['I_within']:+7.4f} "
            f"{bat['I_null_q99']:+6.4f} {bat['I_core']:+7.4f} | "
            f"{bat['sp_mi_exc']:+7.4f} {bat['cc_mi_exc']:+7.4f} {bat['charwin']:+8.4f}"
        )


# ==============================================================================
# TEST 6: SYLLABIC WRITING WITH SOUND-COMBINATION RULES / STOLFI GRAMMAR
# ==============================================================================
# Strict CV/CVC syllabic parser where:
#   - Onset: compound bench-gallows (cth, ckh, cph, cfh) or ch/sh or single consonant (q, k, t, p, f, d, l, r, s, y, m, n, g)
#   - Nucleus: vowel cluster ([oaei]+, or syllabic 'y' when following a consonant as in dy, ky, ty, chy, shy)
#   - Coda: optional resonant/sibilant/glide (n, r, l, m, s, y) when at word end or before next consonant onset
STRICT_SYL_RE = re.compile(
    r"(cth|ckh|cph|cfh|ch|sh|[qktpfdlrsymng])?"
    r"([oaei]+|(?<=[hktpfdlrsymng])y)"
    r"([nrlmsy](?=$|cth|ckh|cph|cfh|ch|sh|[qktpfdlrsymng]))?"
)


def parse_voynich_syllables(w: str) -> list[str]:
    """Decompose a Voynich word into strict CV/CVC syllable blocks (e.g. qokedy -> ['qo', 'ke', 'dy'],
    chodaiin -> ['cho', 'daiin'], shedy -> ['she', 'dy'])."""
    if not w:
        return []
    syls = []
    pos = 0
    for m in STRICT_SYL_RE.finditer(w):
        start, end = m.span()
        if start == end:
            continue
        prefix_rem = w[pos:start]
        blk = prefix_rem + m.group(0)
        if blk:
            syls.append(blk)
        pos = end
    if pos < len(w):
        if syls:
            syls[-1] += w[pos:]
        else:
            syls.append(w[pos:])
    return syls if syls else [w]


def build_syllabary_transducer_controls(
    pages: list[dict],
    v_syl_rank: list[str],
    v_init_rank: list[str],
    v_mid_rank: list[str],
    v_fin_rank: list[str],
) -> tuple[list[dict], list[dict]]:
    """Build two Syllabary Transducer Controls on real-line medieval Latin (cremma_prose15):
      1. Free_CV_Syllabary: each Latin syllable maps 1-to-1 by global frequency rank to a Voynich CV/CVC syllable.
      2. Stolfi_PosLocked_Syllabary: each Latin word of k syllables maps its initial syllable to Voynich's
         Syl_initial rank table, medial syllables to Syl_medial, and final syllable to Syl_final (enforcing
         Stolfi's Crust-Mantle-Core positional syllable grammar within every word!)."""
    lat_syl_re = re.compile(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy]+(?=$|[^aeiouy][aeiouy]))?")

    def split_lat_syls(w: str) -> list[str]:
        ms = [m.group(0) for m in lat_syl_re.finditer(w) if m.group(0)]
        return ms if ms else [w]

    all_lat_syls = [s for p in pages for ln in p["lines"] for w in ln for s in split_lat_syls(w)]
    lat_ranks = [s for s, _ in Counter(all_lat_syls).most_common()]
    syl_map_free = {s: v_syl_rank[i % len(v_syl_rank)] for i, s in enumerate(lat_ranks)}
    syl_map_init = {s: v_init_rank[i % len(v_init_rank)] for i, s in enumerate(lat_ranks)}
    syl_map_mid = {s: v_mid_rank[i % len(v_mid_rank)] for i, s in enumerate(lat_ranks)}
    syl_map_fin = {s: v_fin_rank[i % len(v_fin_rank)] for i, s in enumerate(lat_ranks)}

    out_free, out_pos = [], []
    for p in pages:
        lns_f, lns_p = [], []
        for ln in p["lines"]:
            row_f, row_p = [], []
            for w in ln:
                if not w:
                    continue
                ss = split_lat_syls(w)
                row_f.append("".join(syl_map_free[s] for s in ss))
                if len(ss) == 1:
                    row_p.append(syl_map_fin[ss[0]])
                elif len(ss) == 2:
                    row_p.append(syl_map_init[ss[0]] + syl_map_fin[ss[1]])
                else:
                    # Cap at 3 syllables like Voynich (Crust + Mantle + Core)
                    row_p.append(syl_map_init[ss[0]] + syl_map_mid[ss[1]] + syl_map_fin[ss[-1]])
            if row_f:
                lns_f.append(row_f)
                lns_p.append(row_p)
        if lns_f:
            out_free.append(dict(p, lines=lns_f))
            out_pos.append(dict(p, lines=lns_p))
    return out_free, out_pos


def run_test_6(zl_pages: list[dict], zl_recs: list[dict]) -> None:
    emit("\n" + "=" * 105)
    emit("TEST 6 (CANDIDATE 6): SYLLABIC WRITING WITH SOUND-COMBINATION RULES / STOLFI GRAMMAR")
    emit("=" * 105)

    para_recs = vparse.paragraph_text(zl_recs)
    all_toks = [w for r in para_recs for w in r["words"] if "?" not in w]

    syl_seqs = [parse_voynich_syllables(w) for w in all_toks]
    flat_syls = [s for seq in syl_seqs for s in seq]
    syl_counts = Counter(flat_syls)
    total_syl_toks = len(flat_syls)
    total_syl_types = len(syl_counts)

    sorted_counts = [c for _, c in syl_counts.most_common()]
    cum = np.cumsum(sorted_counts) / total_syl_toks

    def types_for_cov(target: float) -> int:
        return int(np.searchsorted(cum, target) + 1)

    ranked_syls = [s for s, _ in syl_counts.most_common()]
    syl_to_rank = {s: i + 1 for i, s in enumerate(ranked_syls)}
    word_max_syl_rank = np.sort([max(syl_to_rank[s] for s in seq) for seq in syl_seqs])

    def k_syls_for_word_cov(target: float) -> int:
        idx = min(len(word_max_syl_rank) - 1, int(math.ceil(target * len(word_max_syl_rank))) - 1)
        return int(word_max_syl_rank[idx])

    syl_len_dist = Counter(len(seq) for seq in syl_seqs)
    emit("\n--- 6A. Strict CV/CVC Syllable Decomposition & Coverage on ZL3b (34,857 word tokens) ---")
    emit(f"  Total CV/CVC syllable tokens : {total_syl_toks} (mean {total_syl_toks/len(all_toks):.3f} syllables/word, {len(''.join(all_toks))/total_syl_toks:.3f} chars/syllable)")
    emit(f"  Distinct CV/CVC syllable types: {total_syl_types}")
    emit(f"  Word syllable-count distribution: 1-syl={100*syl_len_dist[1]/len(all_toks):.2f}%, 2-syl={100*syl_len_dist[2]/len(all_toks):.2f}%, 3-syl={100*syl_len_dist[3]/len(all_toks):.2f}%, 4+syl={100*sum(v for k,v in syl_len_dist.items() if k>=4)/len(all_toks):.2f}%")
    emit(f"  Syllable-token coverage thresholds: 50%={types_for_cov(0.50)} types, 80%={types_for_cov(0.80)} types, 90%={types_for_cov(0.90)} types, 95%={types_for_cov(0.95)} types, 99%={types_for_cov(0.99)} types")
    emit(f"  Whole-word token coverage (all syllables in word <= rank K): 50%={k_syls_for_word_cov(0.50)} syl types, 80%={k_syls_for_word_cov(0.80)} syl types, 90%={k_syls_for_word_cov(0.90)} syl types, 95%={k_syls_for_word_cov(0.95)} syl types, 99%={k_syls_for_word_cov(0.99)} syl types")
    emit(f"  Top-20 CV/CVC syllables: {[(s, c, f'{100*c/total_syl_toks:.2f}%') for s, c in syl_counts.most_common(20)]}")

    emit("\n--- 6B. Within-Word Syllable Slot Locking (Syl_1 vs Syl_mid vs Syl_final on 2+ Syllable Words) ---")
    words_ge2 = [seq for seq in syl_seqs if len(seq) >= 2]
    s1_cnt = Counter(seq[0] for seq in words_ge2)
    smid_cnt = Counter(s for seq in words_ge2 if len(seq) >= 3 for s in seq[1:-1])
    sfin_cnt = Counter(seq[-1] for seq in words_ge2)
    all_s_vocab = sorted(set(s1_cnt) | set(sfin_cnt))
    p1 = np.array([s1_cnt[s] for s in all_s_vocab], dtype=np.float64); p1 /= p1.sum()
    pfin = np.array([sfin_cnt[s] for s in all_s_vocab], dtype=np.float64); pfin /= pfin.sum()
    m_dist = 0.5 * (p1 + pfin)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl1 = np.where(p1 > 0, p1 * np.log2(p1 / m_dist), 0.0).sum()
        kl2 = np.where(pfin > 0, pfin * np.log2(pfin / m_dist), 0.0).sum()
    jsd_syl_init_fin = float(0.5 * (kl1 + kl2))
    mi_s1_s2, _, _, nmi_s1_s2 = mi_discrete([seq[0] for seq in words_ge2], [seq[-1] for seq in words_ge2])
    emit(f"  2+ syllable words: n={len(words_ge2)} ({100*len(words_ge2)/len(all_toks):.1f}% of corpus)")
    emit(f"  JSD(Syl_initial || Syl_final) within words = {jsd_syl_init_fin:.4f} bits (1.000 = completely disjoint syllable alphabets!)")
    emit(f"  Top-8 Initial Syllables (Syl_1)   : {[(s, f'{100*c/len(words_ge2):.1f}%') for s, c in s1_cnt.most_common(8)]}")
    emit(f"  Top-8 Medial Syllables  (Syl_mid) : {[(s, f'{100*c/sum(smid_cnt.values()):.1f}%') for s, c in smid_cnt.most_common(8)]}")
    emit(f"  Top-8 Final Syllables   (Syl_last): {[(s, f'{100*c/len(words_ge2):.1f}%') for s, c in sfin_cnt.most_common(8)]}")
    emit(f"  Within-word MI(Syl_1; Syl_last)   = {mi_s1_s2:.4f} bits (NMI={nmi_s1_s2:.4f})")

    emit("\n--- 6C. Syllable Count & Syllable Type Dependence on Line Position (Lines >= 4 tokens) ---")
    para_starts = s37.load_ivtff_para_starts(VOY_ROOT / "data" / "ZL3b-n.txt", vparse)
    slot_buckets = defaultdict(list)
    adj_syl_pairs = []
    for p in zl_pages:
        pid = p["id"]
        for li, ln in enumerate(p["lines"]):
            if len(ln) >= 2:
                for w1, w2 in zip(ln[:-1], ln[1:]):
                    adj_syl_pairs.append((parse_voynich_syllables(w1)[-1], parse_voynich_syllables(w2)[0]))
            if len(ln) < 4:
                continue
            is_p0 = (pid, li) in para_starts
            slot_buckets["0_para_init" if is_p0 else "0_ord_init"].append(ln[0])
            slot_buckets["1_second"].append(ln[1])
            for w in ln[2:-2]:
                slot_buckets["2_mid"].append(w)
            slot_buckets["3_penult"].append(ln[-2])
            slot_buckets["4_line_final"].append(ln[-1])

    hdr6c = f"{'line_slot':15s} | {'n_tok':>6s} | {'mean_chr':>8s} {'mean_syl':>8s} {'chr/syl':>7s} | {'1-syl%':>6s} {'2-syl%':>6s} {'3+syl%':>6s} | {'pf_onset%':>9s} {'m_coda%':>7s}"
    emit(hdr6c)
    emit("-" * len(hdr6c))
    for sb in ("0_para_init", "0_ord_init", "1_second", "2_mid", "3_penult", "4_line_final"):
        ws = slot_buckets[sb]
        seqs = [parse_voynich_syllables(w) for w in ws]
        m_chr = float(np.mean([len(w) for w in ws]))
        m_syl = float(np.mean([len(s) for s in seqs]))
        c_per_s = m_chr / m_syl if m_syl > 0 else 0.0
        p1s = 100.0 * sum(len(s) == 1 for s in seqs) / len(seqs)
        p2s = 100.0 * sum(len(s) == 2 for s in seqs) / len(seqs)
        p3s = 100.0 * sum(len(s) >= 3 for s in seqs) / len(seqs)
        pf_on = 100.0 * sum(w.startswith(("p", "f", "cph", "cfh")) or ("p" in w[:2]) or ("f" in w[:2]) for w in ws) / len(ws)
        m_cod = 100.0 * sum(w.endswith("m") for w in ws) / len(ws)
        emit(f"{sb:15s} | {len(ws):6d} | {m_chr:8.4f} {m_syl:8.4f} {c_per_s:7.4f} | {p1s:5.1f}% {p2s:5.1f}% {p3s:5.1f}% | {pf_on:8.2f}% {m_cod:6.2f}%")

    s_last_list = [a for a, _ in adj_syl_pairs]
    s_next_list = [b for _, b in adj_syl_pairs]
    cross_syl_mi = s37.mi_shuffle_corrected_pairs(s_last_list, s_next_list, seed=SEED, n_null=100)
    emit(f"\n  Cross-Word Syllable Boundary MI(Syl_last(w_t); Syl_first(w_{{t+1}})):")
    emit(f"    obs={cross_syl_mi['raw']:.4f} bits vs shuf_null={cross_syl_mi['null_mean']:.4f}±{cross_syl_mi['null_sd']:.4f} -> excess={cross_syl_mi['excess']:+.4f} bits (z={cross_syl_mi['z']:+.2f})")

    emit("\n--- 6D. Syllabary Transducer Controls (Natural Language Mapped into Voynich Free & Position-Locked Syllabaries) ---")
    realline_dir = VOY_ROOT / "data" / "controls_realline"
    _, prose15_pages = R2.load_meta(realline_dir / "cremma_prose15.meta.json")

    v_init_rank = [s for s, _ in s1_cnt.most_common(100)]
    v_mid_rank = [s for s, _ in smid_cnt.most_common(100)]
    v_fin_rank = [s for s, _ in sfin_cnt.most_common(100)]
    syl_free_pg, syl_pos_pg = build_syllabary_transducer_controls(prose15_pages, ranked_syls[:200], v_init_rank, v_mid_rank, v_fin_rank)

    for s_label, s_pgs in [
        ("Voynich_ZL3b_ALL", zl_pages),
        ("Sim6A_Free_CV_Syllabary", syl_free_pg),
        ("Sim6B_Stolfi_PosLocked_Syl", syl_pos_pg),
    ]:
        bat = s37.evaluate_two_layer_battery(s_label, s_pgs, "Syl_Control", R2, mn, a2_mod)
        rig = compute_word_internal_rigidity(mn.flat_tokens(s_pgs))
        emit(
            f"  {s_label:26s} | h2={rig['h2']:.2f} H_pos={rig['h_pos_norm']:.4f} A_ord={rig['a_ord']:.4f} CHARWIN={bat['charwin']:+.4f} | "
            f"A1_jsd={bat['jsd_first_exc']:+.4f} A3_edg={bat['cross_excess']:+.4f} I_win={bat['I_within']:+.4f} (q99={bat['I_null_q99']:+.4f}) "
            f"I_core={bat['I_core']:+.4f} S1->P2={bat['sp_mi_exc']:+.4f} C1->C2={bat['cc_mi_exc']:+.4f}"
        )


# ==============================================================================
# TEST 7: FORMULAIC RECORDS / PROCEDURAL NOTATION — CROSS-ENTRY TEMPLATE PREDICTION
# ==============================================================================
def extract_paragraphs_by_section(zl_recs: list[dict], raw_zl_lines: list[str]) -> dict[str, list[list[list[str]]]]:
    sec_paras: dict[str, list[list[list[str]]]] = defaultdict(list)
    cur_sec = "?"
    cur_para: list[list[str]] = []

    for raw in raw_zl_lines:
        if raw.startswith("#") or not raw.strip():
            continue
        mp = vparse.PAGE_RE.match(raw)
        if mp:
            if cur_para and cur_sec != "?":
                sec_paras[cur_sec].append(cur_para)
                cur_para = []
            vars_d = dict(vparse.VAR_RE.findall(mp.group(2)))
            cur_sec = vars_d.get("I", "?")
            continue
        ml = vparse.LINE_RE.match(raw)
        if not ml:
            continue
        pg, _, loc_type, unit, text = ml.groups()
        if not unit.startswith("P"):
            continue
        ws = [w for w in vparse.clean(text) if "?" not in w]
        if not ws:
            continue
        if loc_type in ("@", "*") or not cur_para:
            if cur_para:
                sec_paras[cur_sec].append(cur_para)
            cur_para = [ws]
        else:
            cur_para.append(ws)
            if loc_type == "=":
                sec_paras[cur_sec].append(cur_para)
                cur_para = []
    if cur_para and cur_sec != "?":
        sec_paras[cur_sec].append(cur_para)
    return sec_paras


def build_procedural_recipe_control(seed: int = SEED) -> list[list[list[str]]]:
    rng = random.Random(seed)
    TAKE_VERBS = ["recipe", "accipe", "toma", "cape", "pone", "adde"]
    HERBS = [f"herba{i:02d}" for i in range(40)]
    PARTS = ["radicis", "foliorum", "seminis", "floris", "corticis", "succi", "pulveris", "olei"]
    MEASURES = ["dragmas", "uncias", "manipulos", "libellam", "scrupulos", "partes"]
    NUMS = ["duas", "tres", "quatuor", "quinque", "sex", "dimidiam", "aequales", "quantum"]
    ACTIONS = ["coque", "tere", "misce", "distilla", "bulliat", "infunde", "cola", "solve"]
    VESSELS = ["in_aqua", "in_vino", "in_aceto", "in_melle", "in_oleo", "in_vase", "in_igne", "in_balneo"]
    ADMIN = ["detur", "bibat", "ungatur", "ponatur", "sumat", "fiat_emplastrum", "fiat_potio", "fiat_pulvis"]
    CONDITIONS = ["mane", "sero", "ieiuno", "calidum", "frigidum", "cotidie", "post_cibum", "pro_febre"]
    CLOSERS = ["probatur", "expertum_est", "sanabitur", "optime_valet", "deo_volente", "amen"]

    paras = []
    for _ in range(200):
        n_lns = rng.choice([3, 4, 4, 5, 6])
        para = []
        for li in range(n_lns):
            if li == 0:
                ln = [rng.choice(TAKE_VERBS), rng.choice(HERBS), rng.choice(PARTS), rng.choice(MEASURES), rng.choice(NUMS)]
                if rng.random() < 0.5:
                    ln.extend(["et", rng.choice(HERBS), rng.choice(PARTS), rng.choice(NUMS)])
            elif li == n_lns - 1:
                ln = [rng.choice(ADMIN), rng.choice(CONDITIONS), rng.choice(MEASURES), rng.choice(NUMS), rng.choice(CLOSERS)]
            else:
                ln = [rng.choice(ACTIONS), rng.choice(VESSELS), rng.choice(HERBS), rng.choice(PARTS), rng.choice(MEASURES), rng.choice(NUMS)]
                if rng.random() < 0.3:
                    ln.insert(2, rng.choice(CONDITIONS))
            para.append(ln)
        paras.append(para)
    return paras


def evaluate_paragraph_template_prediction(
    name: str,
    paras: list[list[list[str]]],
    seg: mn.SlotSegmenter,
    target_mode: str = "prefix_P",
) -> dict:
    n_paras = len(paras)
    split = max(1, int(0.80 * n_paras))
    train_paras = paras[:split]
    test_paras = paras[split:]

    train_toks = [w for p in train_paras for ln in p for w in ln]
    top50_c = {c for c, _ in Counter(seg.segment(w)[1] for w in train_toks).most_common(50)}

    def tok_to_sym(w: str) -> str:
        p, c, s = seg.segment(w)
        if target_mode == "prefix_P":
            return p or "<EMPTY_P>"
        elif target_mode == "frame_PS":
            return f"{p or '0'}_{s or '0'}"
        else:
            return c if c in top50_c else "<OTHER_C>"

    def line_role(li: int, n_lns: int) -> str:
        if li == 0:
            return "L_first"
        elif li == n_lns - 1:
            return "L_last"
        return "L_mid"

    def slot_bucket(k: int, L: int) -> str:
        if k == 0:
            return "S0_init"
        elif k == L - 1:
            return "S4_final"
        elif k == 1:
            return "S1_sec"
        elif k == L - 2 and L >= 4:
            return "S3_pen"
        return "S2_mid"

    def annotate(p_list):
        records = []
        exact_lines = []
        for para in p_list:
            n_lns = len(para)
            prev_syms = None
            for li, ln in enumerate(para):
                L = len(ln)
                l_role = line_role(li, n_lns)
                syms = [tok_to_sym(w) for w in ln]
                exact_lines.append(tuple(syms))
                for k, sym in enumerate(syms):
                    s_buck = slot_bucket(k, L)
                    pos_key = (l_role, s_buck)
                    vert_sym = prev_syms[min(k, len(prev_syms) - 1)] if prev_syms else "<NO_PREV_LINE>"
                    prev1_sym = syms[k - 1] if k >= 1 else "<BOL>"
                    prev2_sym = syms[k - 2] if k >= 2 else "<BOL2>"
                    records.append((sym, pos_key, vert_sym, prev1_sym, prev2_sym, (l_role, min(k, 8))))
                prev_syms = syms
        return records, exact_lines

    train_recs, train_lines = annotate(train_paras)
    test_recs, test_lines = annotate(test_paras)

    train_l4 = set(ln for ln in train_lines if len(ln) >= 4)
    test_l4 = [ln for ln in test_lines if len(ln) >= 4]
    exact_line_hit = sum(1 for ln in test_l4 if ln in train_l4) / len(test_l4) if test_l4 else 0.0

    vocab = sorted({r[0] for r in train_recs} | {r[0] for r in test_recs})
    V = len(vocab)
    alpha = 0.5

    c_uni = Counter()
    c_pos = defaultdict(Counter)
    c_vert = defaultdict(Counter)
    c_tmpl = defaultdict(Counter)
    c_big = defaultdict(Counter)
    c_lag2 = defaultdict(Counter)

    for sym, pos_key, vert_sym, prev1_sym, prev2_sym, k_exact in train_recs:
        c_uni[sym] += 1
        c_pos[pos_key][sym] += 1
        c_vert[(pos_key, vert_sym)][sym] += 1
        c_tmpl[k_exact][sym] += 1
        c_big[(pos_key, prev1_sym)][sym] += 1
        c_lag2[(pos_key, prev2_sym)][sym] += 1

    n_train = len(train_recs)

    def prob_uni(sym: str) -> float:
        return (c_uni[sym] + alpha) / (n_train + alpha * V)

    def prob_pos(sym: str, pos_key) -> float:
        cnts = c_pos[pos_key]
        tot = sum(cnts.values())
        if tot == 0:
            return prob_uni(sym)
        return (cnts[sym] + alpha) / (tot + alpha * V)

    def prob_cond(sym: str, pos_key, table: dict, ctx_key, lam: float = 0.75) -> float:
        p_base = prob_pos(sym, pos_key)
        cnts = table.get((pos_key, ctx_key))
        if not cnts:
            return p_base
        tot = sum(cnts.values())
        p_ctx = (cnts[sym] + alpha * p_base * V) / (tot + alpha * V)
        return lam * p_ctx + (1.0 - lam) * p_base

    models = ["B0_Marginal", "B1_Pos_Unigram", "M1_Vert_Col", "M2_ExactSlot_Tmpl", "M3_Local_Bigram", "M4_Lag2_Phrase"]
    bits = {m: 0.0 for m in models}
    hits = {m: 0 for m in models}

    arg_uni = c_uni.most_common(1)[0][0]
    arg_pos = {k: v.most_common(1)[0][0] for k, v in c_pos.items() if v}
    arg_vert = {k: v.most_common(1)[0][0] for k, v in c_vert.items() if v}
    arg_tmpl = {k: v.most_common(1)[0][0] for k, v in c_tmpl.items() if v}
    arg_big = {k: v.most_common(1)[0][0] for k, v in c_big.items() if v}
    arg_lag2 = {k: v.most_common(1)[0][0] for k, v in c_lag2.items() if v}

    for sym, pos_key, vert_sym, prev1_sym, prev2_sym, k_exact in test_recs:
        p0 = prob_uni(sym)
        p1 = prob_pos(sym, pos_key)
        p_v = prob_cond(sym, pos_key, c_vert, vert_sym)
        cnt_t = c_tmpl.get(k_exact)
        p_t = ((cnt_t[sym] + alpha) / (sum(cnt_t.values()) + alpha * V)) if cnt_t else p1
        p_b = prob_cond(sym, pos_key, c_big, prev1_sym)
        p_l2 = prob_cond(sym, pos_key, c_lag2, prev2_sym)

        bits["B0_Marginal"] += -math.log2(p0)
        bits["B1_Pos_Unigram"] += -math.log2(p1)
        bits["M1_Vert_Col"] += -math.log2(p_v)
        bits["M2_ExactSlot_Tmpl"] += -math.log2(p_t)
        bits["M3_Local_Bigram"] += -math.log2(p_b)
        bits["M4_Lag2_Phrase"] += -math.log2(p_l2)

        b1_pred = arg_pos.get(pos_key, arg_uni)
        hits["B0_Marginal"] += int(arg_uni == sym)
        hits["B1_Pos_Unigram"] += int(b1_pred == sym)
        hits["M1_Vert_Col"] += int(arg_vert.get((pos_key, vert_sym), b1_pred) == sym)
        hits["M2_ExactSlot_Tmpl"] += int(arg_tmpl.get(k_exact, b1_pred) == sym)
        hits["M3_Local_Bigram"] += int(arg_big.get((pos_key, prev1_sym), b1_pred) == sym)
        hits["M4_Lag2_Phrase"] += int(arg_lag2.get((pos_key, prev2_sym), b1_pred) == sym)

    n_test = len(test_recs) or 1
    return dict(
        name=name,
        target_mode=target_mode,
        n_paras=n_paras,
        n_train_tok=n_train,
        n_test_tok=len(test_recs),
        vocab_size=V,
        exact_line_hit=exact_line_hit,
        ce={m: bits[m] / n_test for m in models},
        acc={m: 100.0 * hits[m] / n_test for m in models},
    )


def run_test_7(zl_recs: list[dict]) -> None:
    emit("\n" + "=" * 105)
    emit("TEST 7 (CANDIDATE 7): FORMULAIC RECORDS / PROCEDURAL NOTATION — CROSS-ENTRY TEMPLATE PREDICTION")
    emit("=" * 105)
    emit("Trains on the first 80% of paragraphs and evaluates on the held-out last 20% of paragraphs across")
    emit("Voynich Sections S (Stars/Recipes), H (Herbal), P (Pharmaceutical), B (Biological) vs medieval")
    emit("medical recipes (CREMMA_Medical_Recipes), liturgical litanies, and a procedural recipe ledger.")

    raw_zl_lines = (VOY_ROOT / "data" / "ZL3b-n.txt").read_text(encoding="ascii", errors="replace").splitlines()
    sec_paras = extract_paragraphs_by_section(zl_recs, raw_zl_lines)

    para_recs = vparse.paragraph_text(zl_recs)
    all_toks = [w for r in para_recs for w in r["words"] if "?" not in w]
    seg_zl = mn.SlotSegmenter(all_toks)

    emit("\n--- 7A. Paragraph Census Across Voynich Sections (ZL3b @P/*P Paragraph Blocks) ---")
    for sec in ("S", "H", "B", "P", "T", "C", "A"):
        ps = sec_paras.get(sec, [])
        if not ps:
            continue
        n_lns = [len(p) for p in ps]
        n_toks = [sum(len(ln) for ln in p) for p in ps]
        emit(f"  Section {sec}: {len(ps):4d} paragraphs | lines/para={np.mean(n_lns):.2f}±{np.std(n_lns):.2f} (median {np.median(n_lns):.0f}) | tokens/para={np.mean(n_toks):.1f}±{np.std(n_toks):.1f} (total {sum(n_toks)} toks)")

    realline_dir = VOY_ROOT / "data" / "controls_realline"
    med_pages = []
    for ms in ("H318", "CLM13027", "Latin16195", "Phi_10a135"):
        _, pb = R2.load_meta(realline_dir / f"cremma_{ms}.meta.json")
        med_pages.extend(pb)
    med_all_lines = [ln for p in med_pages for ln in p["lines"] if ln]
    med_paras = [med_all_lines[i : i + 5] for i in range(0, len(med_all_lines), 5) if len(med_all_lines[i : i + 5]) >= 2]
    seg_med = mn.SlotSegmenter([w for p in med_paras for ln in p for w in ln])

    _, cremma_all_pages = R2.load_meta(realline_dir / "cremma_all.meta.json")
    synth_lit = dict((n, pg) for n, pg, _ in s37.build_synthetic_liturgical_controls(cremma_all_pages, seed=SEED))
    lit_lines = [ln for p in synth_lit["litany_sanctorum_synth"] for ln in p["lines"] if ln]
    lit_paras = [lit_lines[i : i + 5] for i in range(0, len(lit_lines), 5) if len(lit_lines[i : i + 5]) >= 2]
    seg_lit = mn.SlotSegmenter([w for p in lit_paras for ln in p for w in ln])

    proc_paras = build_procedural_recipe_control(seed=SEED)
    seg_proc = mn.SlotSegmenter([w for p in proc_paras for ln in p for w in ln])

    datasets_7 = [
        ("Voynich_Sec_S (Recipes)", sec_paras["S"], seg_zl),
        ("Voynich_Sec_H (Herbal)", sec_paras["H"], seg_zl),
        ("Voynich_Sec_B (Biol)", sec_paras["B"], seg_zl),
        ("Voynich_Sec_P (Pharma)", sec_paras["P"], seg_zl),
        ("CREMMA_Med_Recipes", med_paras, seg_med),
        ("Litany_Sanctorum_Synth", lit_paras, seg_lit),
        ("Procedural_Recipe_Ledger", proc_paras, seg_proc),
    ]

    for mode, mode_title in [
        ("prefix_P", "7B.1 Held-Out Prefix Slot (P, V=29) Sequence Prediction (80% Train -> 20% Test Paragraphs)"),
        ("frame_PS", "7B.2 Held-Out Morphological Frame (Prefix, Suffix) Prediction (80% Train -> 20% Test Paragraphs)"),
        ("core_top50", "7C. Held-Out Top-50 Core Stem Sequence Prediction (80% Train -> 20% Test Paragraphs)"),
    ]:
        emit(f"\n--- {mode_title} ---")
        emit("Cross-Entropy (bits/token, lower = better) and Top-1 Accuracy (%) on held-out 20% paragraphs:")
        emit("  - d_Pos  = B0_Marginal - B1_Pos_Unigram   (gain from line/paragraph boundary position alone)")
        emit("  - d_Vert = B1_Pos_Unigram - M1_Vert_Col   (gain from cross-line vertical column template)")
        emit("  - d_Tmpl = B1_Pos_Unigram - M2_ExactSlot  (gain from exact column index k template)")
        emit("  - d_Big  = B1_Pos_Unigram - M3_Local_Big  (gain from local horizontal lag-1 transition)")
        emit("  - d_Lag2 = B1_Pos_Unigram - M4_Lag2_Phr   (gain from non-adjacent lag-2 template memory)")
        hdr7 = (
            f"{'dataset':25s} | {'P_cnt':>5s} {'N_tst':>5s} {'V':>4s} {'RepL%':>6s} | "
            f"{'B0_Uni':>6s} {'B1_Pos':>6s} | {'d_Pos':>6s} {'d_Vert':>6s} {'d_Tmpl':>6s} {'d_Big':>6s} {'d_Lag2':>6s} | "
            f"{'Acc_B1':>6s} {'Acc_Tm':>6s} {'Acc_Bg':>6s}"
        )
        emit(hdr7)
        emit("-" * len(hdr7))
        for dname, plist, dseg in datasets_7:
            r = evaluate_paragraph_template_prediction(dname, plist, dseg, target_mode=mode)
            ce = r["ce"]
            ac = r["acc"]
            d_pos = ce["B0_Marginal"] - ce["B1_Pos_Unigram"]
            d_vert = ce["B1_Pos_Unigram"] - ce["M1_Vert_Col"]
            d_tmpl = ce["B1_Pos_Unigram"] - ce["M2_ExactSlot_Tmpl"]
            d_big = ce["B1_Pos_Unigram"] - ce["M3_Local_Bigram"]
            d_lag2 = ce["B1_Pos_Unigram"] - ce["M4_Lag2_Phrase"]
            emit(
                f"{dname:25s} | {r['n_paras']:5d} {r['n_test_tok']:5d} {r['vocab_size']:4d} {100*r['exact_line_hit']:5.1f}% | "
                f"{ce['B0_Marginal']:6.3f} {ce['B1_Pos_Unigram']:6.3f} | "
                f"{d_pos:+6.3f} {d_vert:+6.3f} {d_tmpl:+6.3f} {d_big:+6.3f} {d_lag2:+6.3f} | "
                f"{ac['B1_Pos_Unigram']:5.1f}% {ac['M2_ExactSlot_Tmpl']:5.1f}% {ac['M3_Local_Bigram']:5.1f}%"
            )


def main() -> int:
    t0 = time.time()
    OUR_SCRATCH.mkdir(parents=True, exist_ok=True)
    PARENT_SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(Path(__file__), PARENT_SCRATCH / "exp_c4_c5_c6_c7.py")
    except Exception:
        pass

    zl_pages = mn.voynich_pages("eva")
    zl_recs = vparse.load()

    run_test_4(zl_pages, zl_recs)
    run_test_5(zl_pages)
    run_test_6(zl_pages, zl_recs)
    run_test_7(zl_recs)

    elapsed = time.time() - t0
    emit(f"\nCompleted all 4 candidate experiments (C4, C5, C6, C7) in {elapsed:.2f}s.")
    text_out = "\n".join(log_lines) + "\n"
    OUT_PATH_OUR.write_text(text_out, encoding="utf-8")
    OUT_PATH_PARENT.write_text(text_out, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
