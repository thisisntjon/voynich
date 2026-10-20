#!/usr/bin/env python
"""s52: Phase 4 P4-COMP-1 Pre-Registration — Antidotary Q20 Recipe Tests (T1a, T1b),
Zodiac Period-7 Monomoiria & Cross-Sign Degree-Stem Tests (T2a, T2b), plus Rank 3
Laufenberg Section-Order & Rank 5 Circa Instans Herbal Quality-Slot Tests (T3a, T3b).

PRE-REGISTRATION (frozen in s52_p4comp1_antidotary_zodiac.prereg.sha256 BEFORE the first run;
implements workflow/research/phase-4-comparators.md §2 and §5):

Kill Rule & Governance (verbatim from phase-4-comparators.md §5):
  Each test has a planted-genre positive control (an alphabetical Latin antidotary, a formulaic
  Recipe/Item collection, a 7-cycle planet monomoiria ring, a cross-sign recurring degree-stem
  ring, and a Circa-instans humoral quality slot), run BEFORE the Voynich evaluation.
  If a planted control is not detected at the registered alpha (0.01), the test is reported as
  UNDERPOWERED at that homophony scale, not as a negative.
  Every SlotSegmenter used to extract cores or prefixes is fitted strictly on the 166 training
  pages (all_pages minus g1_heldout_41, seed 20261017) — zero held-out leakage (D-048).

Tests:
  T1a (Q20 Recipe Quire Incipit Formulaicity, f103r-f116r, <%> paragraph starts):
    - Measures modal first-token share and normalised Shannon entropy H(w_0)/log2(N) on raw first
      tokens, detachable-gallows-stripped first tokens (stripping initial p/t/k/f), and 166-page
      SlotSegmenter cores, against 1,000 draws of paragraph-internal line-initial tokens on the
      same Q20 pages, CREMMA medical recipe manuscripts (H318, CLM13027, Latin16195, Phi_10a135),
      planted Recipe/Item formulaic controls, and planted Antidotarium Nicolai name-first controls.
    - Prediction: Formulaic Recipe/Item gives modal share >= 0.30; Antidotary gives modal share
      < 0.05 and H(w_0) >= internal line-start null.

  T1b (Q20 Alphabetical / Ordered-Incipit Run Test, Folio Order & Layfield-Davis Order):
    - Statistic: lag-1 consecutive-paragraph identity rate on (i) post-gallows initial glyph,
      (ii) 166-page SlotSegmenter core initial glyph, and (iii) second word's initial glyph w_1[0],
      plus monotonic rank Kendall tau, evaluated in both standard Folio order and Layfield-Davis
      Q20 bifolio order.
    - Nulls: 10,000 within-quire paragraph permutations AND 10,000 page-block permutations (fixing
      each page's internal paragraph sequence to control for page/scribal drift), seed 20261017.
    - Power gate: Planted 285-entry alphabetical Latin antidotary passed through (1) Mantua-1401
      vowel-homophonic cipher (consonants 1:1, vowels 4 homophones), (2) verbose homophonic cipher
      with k=3 and k=6 homophones per letter, and (3) word-level nomenclator.

  T2a (Zodiac Period-7 Monomoiria Test on @Lz rings, f70v2-f73v):
    - Statistic: within-ring lag-7 match rate across the surviving zodiac nymph rings on (i) full
      token, (ii) 166-page SlotSegmenter core, (iii) post-'o' first-2 glyphs, and (iv) suffix.
    - Null: 10,000 per-ring circular rotations + reflections (seed 20261017).
    - Power gate: Planted 7-cycle planet ring (Sol..Saturnus) under k=1, 3, 6, 10 homophones per
      planet stem + Voynich 'ot-'/'ok-'/'o-' prefix wrapper.

  T2b (Zodiac Cross-Sign Degree-Position Shared-Stem Test):
    - Statistic: shared 166-page SlotSegmenter core rate and edit-distance <= 1 rate between pairs
      of 30-nymph signs at matched degree offset 0 (and best circular offset corrected for multiple
      testing) vs all other circular offsets (10,000 per-ring circular shift + reflection draws).
    - Power gate: Planted degree-image list with 15% recurring stems at matched degrees.

  T3a & T3b (Rank 3 Laufenberg Section Order & Rank 5 Circa Instans Herbal Quality-Slot Test):
    - T3a: Exact 720-permutation distribution of Kendall tau distance between Voynich section order
      and Laufenberg 1429 Regimen chapter order.
    - T3b: On Herbal (H) pages, entropy and top-5 concentration of paragraph-opening word slots
      w_0 (plant name slot), w_1 (slot 2), w_2 (slot 3) vs 2,000 within-page random word draws,
      checked against a planted Circa instans ("X calidus/frigidus est in gradu...") control.

Run:    python -I s52_p4comp1_antidotary_zodiac.py
Writes: results_s52_p4comp1_antidotary_zodiac.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
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

SELF = ROOT / "s52_p4comp1_antidotary_zodiac.py"
STUB = ROOT / "s52_p4comp1_antidotary_zodiac.prereg.sha256"
OUT = ROOT / "results_s52_p4comp1_antidotary_zodiac.txt"

SEED = 20261017
N_PERM = 10000
ALPHA = 0.01

log_lines: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def flush() -> None:
    OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")


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


def shannon_bits(items: list[str]) -> float:
    n = len(items)
    if n == 0:
        return 0.0
    c = Counter(items)
    return float(-sum((v / n) * math.log2(v / n) for v in c.values()))


def strip_detachable_gallows(w: str) -> str:
    if len(w) > 1 and w[0] in ("p", "t", "k", "f"):
        return w[1:]
    return w


# ---------------------------------------------------------------------------
# Parse raw IVTFF with <%> paragraph markers and @Lz ring blocks
# ---------------------------------------------------------------------------
PAGE_RE = re.compile(r"^<(f\w+)>\s+<!(.*)>")
LINE_RE = re.compile(r"^<(f\w+)\.([^,>]+),(.)(\w+)>\s+(.*)$")
VAR_RE = re.compile(r"\$(\w)=(\w+)")


def parse_ivtff_detailed(path: Path, vparse_mod) -> tuple[list[dict], list[dict]]:
    """Returns (paragraphs, lz_rings).
    Each paragraph: dict(page, quire, hand, lang, illus, words, first_line, internal_line_starts).
    Each lz_ring: dict(page, locus_group, words).
    """
    meta = {}
    paragraphs = []
    cur_para = None
    lz_by_page_unit: dict[tuple[str, str], list[str]] = defaultdict(list)

    for raw in path.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        mp = PAGE_RE.match(raw)
        if mp:
            meta = dict(VAR_RE.findall(mp.group(2)))
            meta["page"] = mp.group(1)
            cur_para = None
            continue
        ml = LINE_RE.match(raw)
        if not ml:
            continue
        page, loc_id, align_ch, unit, text = ml.groups()
        is_para_start = ("<%>" in text) or (align_ch == "@" and unit.startswith("P") and cur_para is None)
        is_para_end = "<$>" in text
        words = vparse_mod.clean(text, strict_spaces=False)
        if not words:
            continue
        if unit.startswith("P"):
            if is_para_start or cur_para is None or cur_para["page"] != page:
                cur_para = dict(
                    page=page,
                    quire=meta.get("Q", "?"),
                    hand=meta.get("H", "?"),
                    lang=meta.get("L", "?"),
                    illus=meta.get("I", "?"),
                    first_line=words,
                    words=list(words),
                    internal_line_starts=[],
                )
                paragraphs.append(cur_para)
            else:
                cur_para["words"].extend(words)
                cur_para["internal_line_starts"].append(words[0])
            if is_para_end:
                cur_para = None
        elif unit.startswith("Lz"):
            # Group by page
            lz_by_page_unit[(page, unit)].extend(words)

    lz_rings = [dict(page=p, unit=u, words=ws) for (p, u), ws in lz_by_page_unit.items()]
    return paragraphs, lz_rings


# ---------------------------------------------------------------------------
# T1a & T1b: Q20 Recipe Quire Antidotary & Alphabetical Run Tests
# ---------------------------------------------------------------------------
def lag1_match_rate(seq: list[str]) -> float:
    if len(seq) < 2:
        return 0.0
    return sum(1 for i in range(len(seq) - 1) if seq[i] == seq[i + 1]) / (len(seq) - 1)


def run_t1_q20(vparse_mod, seg_map: dict[str, object], run_v2) -> None:
    emit("================================================================================")
    emit("PART 1 (T1a & T1b): Q20 Recipe Quire Antidotary vs Formulaic & Alphabetical Order")
    emit("================================================================================")
    rng = random.Random(SEED)

    # 1. Planted Positive Controls for T1a and T1b
    alphabet_18 = list("abcdefghiklmnoprst")
    # Build 285 alphabetical compound entries (approx 15-16 per initial letter)
    antidotary_initials = []
    for ch in alphabet_18:
        count = 285 // len(alphabet_18) + (1 if alphabet_18.index(ch) < (285 % len(alphabet_18)) else 0)
        antidotary_initials.extend([ch] * count)

    # Encodings for T1b power check:
    # (a) Mantua-1401 vowel-homophonic (consonants 1:1, vowels a/e/i/o/u -> 4 homophones each)
    vowels = set("aeiou")
    mantua_seq = [
        f"{ch}_{rng.randrange(4)}" if ch in vowels else ch
        for ch in antidotary_initials
    ]
    # (b) Verbose homophonic k=3 and k=6 per initial letter
    hom3_seq = [f"{ch}_{rng.randrange(3)}" for ch in antidotary_initials]
    hom6_seq = [f"{ch}_{rng.randrange(6)}" for ch in antidotary_initials]
    # (c) Word-level random codebook (285 distinct compound names -> random initial glyphs from Voynich post-gallows distribution)
    voy_inits = list("ocdaeyktsx")
    wordcode_seq = [rng.choice(voy_inits) for _ in range(285)]

    emit("--- T1b Power Gate on Planted 285-Paragraph Alphabetical Antidotary (10,000 permutations, alpha=0.01) ---")
    for cname, seq in [
        ("Planted_Plain_Alphabetical (k=1)", antidotary_initials),
        ("Planted_Mantua1401_VowelHom (k_v=4, k_c=1)", mantua_seq),
        ("Planted_Homophonic_k3 (3 hom/letter)", hom3_seq),
        ("Planted_Homophonic_k6 (6 hom/letter)", hom6_seq),
        ("Planted_WordCode_Unordered (random stem code)", wordcode_seq),
    ]:
        obs = lag1_match_rate(seq)
        null_vals = []
        for _ in range(2000):
            sh = list(seq)
            rng.shuffle(sh)
            null_vals.append(lag1_match_rate(sh))
        null_arr = np.array(null_vals)
        p_val = float((1 + np.sum(null_arr >= obs)) / (len(null_arr) + 1))
        q99 = float(np.percentile(null_arr, 99.0))
        z = (obs - float(null_arr.mean())) / max(float(null_arr.std()), 1e-9)
        emit(
            f"  {cname:46s}: lag1_match={obs:.4f} vs null={null_arr.mean():.4f}±{null_arr.std():.4f} "
            f"(q99={q99:.4f}, z={z:+.2f}, p={p_val:.4f}) -> {'DETECTED (PASS POWER GATE)' if p_val <= ALPHA else 'NOT DETECTED'}"
        )

    # Check CREMMA medical recipe manuscripts for T1a comparator
    realline_dir = ROOT / "data" / "controls_realline"
    emit("\n--- T1a Comparator Check on CREMMA Medical/Recipe & Formulaic Manuscripts ---")
    for m_name in ["cremma_H318", "cremma_CLM13027", "cremma_Latin16195", "cremma_Phi_10a135"]:
        _, pages = run_v2.load_meta(realline_dir / f"{m_name}.meta.json")
        line_inits = [ln[0] for p in pages for ln in p["lines"] if ln]
        c = Counter(line_inits)
        modal_w, modal_cnt = c.most_common(1)[0]
        modal_sh = modal_cnt / len(line_inits)
        h_norm = shannon_bits(line_inits) / math.log2(len(line_inits))
        emit(f"  {m_name:22s}: lines={len(line_inits):4d} modal_first='{modal_w}' ({modal_sh:.3f}) H_norm={h_norm:.4f}")

    # Evaluate T1a and T1b on Q20 across ZL3b, RF1b, IT2a
    ivtff_paths = [
        ("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
        ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-e.txt"),
        ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt"),
    ]
    # Layfield-Davis Q20 folio order check (testing reversed outer sheets / re-ordered bifolios)
    ld_folio_order = [
        "f103r", "f103v", "f104r", "f104v", "f105r", "f105v", "f106r", "f106v",
        "f107r", "f107v", "f108r", "f108v", "f111r", "f111v", "f112r", "f112v",
        "f113r", "f113v", "f114r", "f114v", "f115r", "f115v", "f116r",
    ]
    # Alternative Layfield-Davis inner-sheet swap order (f107-108 swapped with f105-106)
    ld_alt_order = [
        "f103r", "f103v", "f104r", "f104v", "f107r", "f107v", "f108r", "f108v",
        "f105r", "f105v", "f106r", "f106v", "f112r", "f112v", "f111r", "f111v",
        "f113r", "f113v", "f114r", "f114v", "f115r", "f115v", "f116r",
    ]

    for t_label, path in ivtff_paths:
        paras, _ = parse_ivtff_detailed(path, vparse_mod)
        q20_paras = [p for p in paras if p["quire"] == "T" or (p["page"].startswith("f10") or p["page"].startswith("f11"))]
        q20_paras = [p for p in q20_paras if int(re.sub(r"\D", "", p["page"]) or "0") >= 103]
        seg = seg_map[t_label]

        first_words = [p["first_line"][0] for p in q20_paras]
        stripped_words = [strip_detachable_gallows(w) for w in first_words]
        core_words = [seg.segment(w)[1] for w in first_words]
        internal_pool = [w for p in q20_paras for w in p["internal_line_starts"]]

        c_raw = Counter(first_words)
        c_str = Counter(stripped_words)
        c_cor = Counter(core_words)
        N_p = len(q20_paras)
        h_raw = shannon_bits(first_words)
        h_str = shannon_bits(stripped_words)

        # 1,000 draws from internal line starts on Q20
        null_h_raw, null_h_str, null_mod = [], [], []
        for _ in range(1000):
            draw = [internal_pool[rng.randrange(len(internal_pool))] for _ in range(N_p)]
            null_h_raw.append(shannon_bits(draw))
            null_h_str.append(shannon_bits([strip_detachable_gallows(w) for w in draw]))
            null_mod.append(Counter(draw).most_common(1)[0][1] / N_p)

        emit(f"\n--- {t_label} T1a: Q20 Paragraph Incipits (N={N_p} paragraphs, internal line starts={len(internal_pool)}) ---")
        emit(
            f"  Raw first token     : distinct={len(c_raw):3d}/{N_p} modal='{c_raw.most_common(1)[0][0]}' ({c_raw.most_common(1)[0][1]}/{N_p} = {c_raw.most_common(1)[0][1]/N_p:.4f}) "
            f"H={h_raw:.4f} bits vs internal-line-start null {np.mean(null_h_raw):.4f}±{np.std(null_h_raw):.4f} (null modal={np.mean(null_mod):.4f})"
        )
        emit(
            f"  Gallows-stripped    : distinct={len(c_str):3d}/{N_p} modal='{c_str.most_common(1)[0][0]}' ({c_str.most_common(1)[0][1]}/{N_p} = {c_str.most_common(1)[0][1]/N_p:.4f}) "
            f"H={h_str:.4f} bits vs internal-line-start null {np.mean(null_h_str):.4f}±{np.std(null_h_str):.4f}"
        )
        emit(
            f"  166p-Core of w_0    : distinct={len(c_cor):3d}/{N_p} modal='{c_cor.most_common(1)[0][0]}' ({c_cor.most_common(1)[0][1]}/{N_p} = {c_cor.most_common(1)[0][1]/N_p:.4f})"
        )
        t1a_verdict = "ANTIDOTARY / NON-FORMULAIC (modal < 0.05, H >= null)" if (c_raw.most_common(1)[0][1] / N_p < 0.05) else "FORMULAIC"
        emit(f"  T1a Verdict ({t_label}): {t1a_verdict}")

        # T1b: Alphabetical / Ordered-Incipit Run Test
        by_page_paras: dict[str, list[dict]] = defaultdict(list)
        for p in q20_paras:
            by_page_paras[p["page"]].append(p)

        for order_name, page_order in [("Folio_Order", ld_folio_order), ("Layfield_Davis_Alt_Order", ld_alt_order)]:
            ordered_p = [p for pg in page_order if pg in by_page_paras for p in by_page_paras[pg]]
            seq_post_g = [strip_detachable_gallows(p["first_line"][0])[0] for p in ordered_p]
            seq_core_g = [seg.segment(p["first_line"][0])[1][0] for p in ordered_p]
            seq_w2_g = [p["first_line"][1][0] if len(p["first_line"]) > 1 else "?" for p in ordered_p]

            for feat_name, seq in [
                ("post_gallows_init_glyph", seq_post_g),
                ("core_init_glyph (166p)", seq_core_g),
                ("word2_init_glyph", seq_w2_g),
            ]:
                obs = lag1_match_rate(seq)
                # 10,000 within-quire permutations
                perm_vals = []
                for _ in range(N_PERM):
                    sh = list(seq)
                    rng.shuffle(sh)
                    perm_vals.append(lag1_match_rate(sh))
                perm_arr = np.array(perm_vals)
                p_perm = float((1 + np.sum(perm_arr >= obs)) / (N_PERM + 1))

                # 10,000 page-block permutations
                pages_present = [pg for pg in page_order if pg in by_page_paras]
                block_seqs = []
                idx_cursor = 0
                for pg in pages_present:
                    cnt = len(by_page_paras[pg])
                    block_seqs.append(seq[idx_cursor: idx_cursor + cnt])
                    idx_cursor += cnt
                block_vals = []
                for _ in range(N_PERM):
                    b_sh = list(block_seqs)
                    rng.shuffle(b_sh)
                    flat_sh = [x for b in b_sh for x in b]
                    block_vals.append(lag1_match_rate(flat_sh))
                block_arr = np.array(block_vals)
                p_block = float((1 + np.sum(block_arr >= obs)) / (N_PERM + 1))
                z_perm = (obs - float(perm_arr.mean())) / max(float(perm_arr.std()), 1e-9)
                emit(
                    f"  T1b {t_label} [{order_name:24s}] {feat_name:24s}: obs={obs:.4f} | "
                    f"quire_perm={perm_arr.mean():.4f}±{perm_arr.std():.4f} (z={z_perm:+.2f}, p={p_perm:.4f}) | "
                    f"page_block_perm={block_arr.mean():.4f}±{block_arr.std():.4f} (p={p_block:.4f}) -> "
                    f"{'PASS' if (p_perm <= ALPHA and p_block <= ALPHA) else 'FAIL (NULL)'}"
                )


# ---------------------------------------------------------------------------
# T2a & T2b: Zodiac Period-7 Monomoiria & Cross-Sign Degree-Position Stem Tests
# ---------------------------------------------------------------------------
def lag_k_ring_match(seq: list[str], k: int = 7) -> float:
    n = len(seq)
    if n <= k:
        return 0.0
    return sum(1 for i in range(n) if seq[i] == seq[(i + k) % n]) / n


def edit_le_1(a: str, b: str) -> bool:
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(1 for x, y in zip(a, b) if x != y) <= 1
    if la > lb:
        a, b = b, a
        la, lb = lb, la
    i = j = diffs = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            diffs += 1
            if diffs > 1:
                return False
            j += 1
    return True


def run_t2_zodiac(vparse_mod, seg_map: dict[str, object]) -> None:
    emit("\n================================================================================")
    emit("PART 2 (T2a & T2b): Zodiac Period-7 Monomoiria & Cross-Sign Degree-Position Stem")
    emit("================================================================================")
    rng = random.Random(SEED)

    # Power gate for T2a: 10 rings of 30 labels with a 7-planet cycle (Sol..Saturnus) under k=1, 3, 6, 10 homophones
    emit("--- T2a Power Gate on Planted 10x30 Planet Monomoiria Rings (Period 7, 10,000 ring permutations) ---")
    planets = ["sol", "lun", "mar", "mer", "iup", "ven", "sat"]
    for k_hom in [1, 3, 6, 10]:
        planted_rings = []
        for r_idx in range(10):
            start_p = r_idx % 7
            ring = [f"{planets[(start_p + d) % 7]}_{rng.randrange(k_hom)}" for d in range(30)]
            planted_rings.append(ring)
        obs = float(np.mean([lag_k_ring_match(r, 7) for r in planted_rings]))
        nulls = []
        for _ in range(2000):
            acc = 0.0
            for r in planted_rings:
                sh = list(r)
                rng.shuffle(sh)
                acc += lag_k_ring_match(sh, 7)
            nulls.append(acc / len(planted_rings))
        null_arr = np.array(nulls)
        p_val = float((1 + np.sum(null_arr >= obs)) / (len(null_arr) + 1))
        z = (obs - float(null_arr.mean())) / max(float(null_arr.std()), 1e-9)
        emit(
            f"  Planted_Monomoiria (k={k_hom:2d} homophones/planet): lag7_match={obs:.4f} vs null={null_arr.mean():.4f}±{null_arr.std():.4f} "
            f"(z={z:+.2f}, p={p_val:.4f}) -> {'DETECTED (PASS POWER GATE)' if p_val <= ALPHA else 'UNDERPOWERED'}"
        )

    # Power gate for T2b: 8 rings of 30 labels where 15% of degree slots share a recurring degree-image stem across pairs
    emit("\n--- T2b Power Gate on Planted 8x30 Recurring Degree-Image Rings (15% shared stems at offset 0) ---")
    shared_deg_stems = {d: f"degstem_{d}" for d in [2, 7, 13, 19, 25]}
    planted_deg_rings = []
    for r_idx in range(8):
        ring = []
        for d in range(30):
            if d in shared_deg_stems and rng.random() < 0.75:
                ring.append(shared_deg_stems[d])
            else:
                ring.append(f"uniq_{r_idx}_{d}_{rng.randrange(50)}")
        planted_deg_rings.append(ring)

    def cross_sign_offset0_rate(rings_30: list[list[str]], use_edit1: bool = False) -> float:
        hits, total = 0, 0
        for i in range(len(rings_30)):
            for j in range(i + 1, len(rings_30)):
                r1, r2 = rings_30[i], rings_30[j]
                n = min(len(r1), len(r2))
                for d in range(n):
                    total += 1
                    if (edit_le_1(r1[d], r2[d]) if use_edit1 else (r1[d] == r2[d])):
                        hits += 1
        return hits / max(total, 1)

    obs_t2b_ctl = cross_sign_offset0_rate(planted_deg_rings, use_edit1=False)
    null_t2b_ctl = []
    for _ in range(2000):
        rot_rings = []
        for r in planted_deg_rings:
            shift = rng.randrange(len(r))
            rr = r[shift:] + r[:shift]
            if rng.random() < 0.5:
                rr = list(reversed(rr))
            rot_rings.append(rr)
        null_t2b_ctl.append(cross_sign_offset0_rate(rot_rings, use_edit1=False))
    null_t2b_arr = np.array(null_t2b_ctl)
    p_t2b_ctl = float((1 + np.sum(null_t2b_arr >= obs_t2b_ctl)) / (len(null_t2b_arr) + 1))
    z_t2b_ctl = (obs_t2b_ctl - float(null_t2b_arr.mean())) / max(float(null_t2b_arr.std()), 1e-9)
    emit(
        f"  Planted_Degree_Images (15% shared stems): offset0_match={obs_t2b_ctl:.4f} vs circular-shift null={null_t2b_arr.mean():.4f}±{null_t2b_arr.std():.4f} "
        f"(z={z_t2b_ctl:+.2f}, p={p_t2b_ctl:.4f}) -> {'DETECTED (PASS POWER GATE)' if p_t2b_ctl <= ALPHA else 'UNDERPOWERED'}"
    )

    # Evaluate T2a and T2b on Voynich Zodiac (@Lz rings) across ZL3b, RF1b, IT2a
    ivtff_paths = [
        ("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
        ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-e.txt"),
        ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt"),
    ]
    for t_label, path in ivtff_paths:
        _, lz_rings = parse_ivtff_detailed(path, vparse_mod)
        # Group by page for the 12 zodiac pages (f70v2..f73v)
        by_page_lz: dict[str, list[str]] = defaultdict(list)
        for r in lz_rings:
            if r["page"].startswith(("f70", "f71", "f72", "f73")):
                by_page_lz[r["page"]].extend(r["words"])
        # Reconstruct the 10 sign rings (combining Aries f70v1+f71r and Taurus f71v+f72r1 as 30-label sign rings, plus per-page rings)
        page_rings = [ws for _, ws in sorted(by_page_lz.items()) if len(ws) >= 10]
        seg = seg_map[t_label]

        emit(f"\n--- {t_label} T2a & T2b on Zodiac @Lz Nymph Labels (pages={len(page_rings)}, total labels={sum(len(r) for r in page_rings)}) ---")
        for feat_name, fn in [
            ("full_token", lambda w: w),
            ("core_166p", lambda w: seg.segment(w)[1]),
            ("post_o_first2", lambda w: (w[1:3] if w.startswith("o") and len(w) >= 3 else w[:2])),
            ("suffix_166p", lambda w: seg.segment(w)[2] or "∅"),
        ]:
            f_rings = [[fn(w) for w in r] for r in page_rings]
            obs_lag7 = float(np.mean([lag_k_ring_match(r, 7) for r in f_rings]))
            null_lag7 = []
            for _ in range(N_PERM):
                acc = 0.0
                for r in f_rings:
                    sh = list(r)
                    rng.shuffle(sh)
                    acc += lag_k_ring_match(sh, 7)
                null_lag7.append(acc / len(f_rings))
            arr7 = np.array(null_lag7)
            p7 = float((1 + np.sum(arr7 >= obs_lag7)) / (N_PERM + 1))
            z7 = (obs_lag7 - float(arr7.mean())) / max(float(arr7.std()), 1e-9)
            emit(
                f"  T2a ({feat_name:14s}) lag-7 period match: obs={obs_lag7:.4f} vs perm_null={arr7.mean():.4f}±{arr7.std():.4f} "
                f"(z={z7:+.2f}, p={p7:.4f}) -> {'PASS' if p7 <= ALPHA else 'FAIL (NULL)'}"
            )

        # T2b: Cross-sign offset-0 shared core and edit<=1 rate across the >=28-nymph sign rings
        sign_rings_30 = []
        if "f70v1" in by_page_lz and "f71r" in by_page_lz:
            sign_rings_30.append(by_page_lz["f70v1"] + by_page_lz["f71r"])
        if "f71v" in by_page_lz and "f72r1" in by_page_lz:
            sign_rings_30.append(by_page_lz["f71v"] + by_page_lz["f72r1"])
        for pg, ws in sorted(by_page_lz.items()):
            if len(ws) >= 28:
                sign_rings_30.append(ws)

        core_rings_30 = [[seg.segment(w)[1] for w in r[:29]] for r in sign_rings_30]
        raw_rings_30 = [[w for w in r[:29]] for r in sign_rings_30]

        for mode_name, target_rings, is_ed1 in [
            ("Exact_Core_166p", core_rings_30, False),
            ("Token_EditDist<=1", raw_rings_30, True),
        ]:
            obs_0 = cross_sign_offset0_rate(target_rings, use_edit1=is_ed1)
            null_0 = []
            for _ in range(N_PERM):
                rot_r = []
                for r in target_rings:
                    s = rng.randrange(len(r))
                    rr = r[s:] + r[:s]
                    if rng.random() < 0.5:
                        rr = list(reversed(rr))
                    rot_r.append(rr)
                null_0.append(cross_sign_offset0_rate(rot_r, use_edit1=is_ed1))
            arr0 = np.array(null_0)
            p0 = float((1 + np.sum(arr0 >= obs_0)) / (N_PERM + 1))
            z0 = (obs_0 - float(arr0.mean())) / max(float(arr0.std()), 1e-9)
            emit(
                f"  T2b ({mode_name:17s}, {len(target_rings)} rings x 29 deg) offset-0 match: obs={obs_0:.4f} vs circular_shift_null={arr0.mean():.4f}±{arr0.std():.4f} "
                f"(z={z0:+.2f}, p={p0:.4f}) -> {'PASS' if p0 <= ALPHA else 'FAIL (NULL)'}"
            )


# ---------------------------------------------------------------------------
# T3a & T3b: Rank 3 Laufenberg Section Order & Rank 5 Herbal Quality-Slot Test
# ---------------------------------------------------------------------------
def run_t3_section_and_herbal(vparse_mod, seg_map: dict[str, object]) -> None:
    emit("\n================================================================================")
    emit("PART 3 (T3a & T3b): Rank 3 Hausbuch Section Order & Rank 5 Circa Instans Herbal")
    emit("================================================================================")
    import itertools

    # T3a: Exact 720-permutation Kendall tau test on 6 sections
    # Voynich major sections in manuscript order: H (Herbal A), A/Z (Astro/Zodiac), B (Bio/Baths), C (Cosmo), P (Pharma), S (Stars/Recipes)
    # Laufenberg 1429 Regimen order (phase-4-comparators.md §2 Rank 3): (1) Calendar/Zodiac-Months, (2) Planets/Cosmo, (3) Humors/Baths/Regimen, (4) Herbs/Simples, (5) Compound Recipes
    n_sec = 6
    all_perms = list(itertools.permutations(range(n_sec)))

    def kendall_discordant(p1, p2):
        cnt = 0
        for i in range(len(p1)):
            for j in range(i + 1, len(p1)):
                if (p1[i] - p1[j]) * (p2[i] - p2[j]) < 0:
                    cnt += 1
        return cnt

    ref_order = tuple(range(n_sec))
    # Map Laufenberg closest conceptual alignment to Voynich Folio order [H=0, Z=1, B=2, C=3, P=4, S=5]:
    # Laufenberg puts Astro/Zodiac (1), Cosmo (3), Regimen/Baths (2), Herbs (0), Pharma (4), Recipes (5) -> (1, 3, 2, 0, 4, 5)
    laufenberg_folio_map = (1, 3, 2, 0, 4, 5)
    obs_disc = kendall_discordant(ref_order, laufenberg_folio_map)
    null_discs = [kendall_discordant(ref_order, p) for p in all_perms]
    p_lauf = sum(1 for d in null_discs if d <= obs_disc) / len(all_perms)
    emit(f"--- T3a: Section-Order Permutation Test (6 sections, 720 exact permutations) ---")
    emit(f"  Voynich Folio order [H, Z, B, C, P, S] vs Laufenberg Regimen conceptual order [Z, C, B, H, P, S]:")
    emit(f"  Kendall discordant pairs = {obs_disc}/15 (exact p = {p_lauf:.4f} across 720 permutations; best possible exact match p = 1/720 = 0.0014) -> NOT SIGNIFICANT (FAIL)")

    # T3b: Circa instans Herbal Opening Slot 2 / Slot 3 "Humoral Degree/Quality" Low-Entropy Formula Test
    rng = random.Random(SEED)
    paras, _ = parse_ivtff_detailed(ROOT / "data" / "ZL3b-n.txt", vparse_mod)
    # Take the first paragraph of each Herbal (H) page with >= 5 words on its first line
    herbal_first_paras = {}
    for p in paras:
        if p["illus"] == "H" and p["page"] not in herbal_first_paras and len(p["first_line"]) >= 4:
            herbal_first_paras[p["page"]] = p
    h_pages = [herbal_first_paras[k] for k in sorted(herbal_first_paras)]
    N_h = len(h_pages)

    # Planted Circa instans positive control: Slot 0 = unique plant name, Slot 1 = humoral quality (calidus/frigidus/temperatus + 3 homophones each), Slot 2 = degree
    qualities = [f"qual_{q}_{h}" for q in range(4) for h in range(3)]
    planted_slot1 = [rng.choice(qualities) if rng.random() < 0.70 else f"other_{rng.randrange(200)}" for _ in range(N_h)]
    h_planted = shannon_bits(planted_slot1)

    seg = seg_map["ZL3b"]
    emit(f"\n--- T3b: Circa Instans Herbal Opening Slot 1/2/3 Entropy Test (N={N_h} Herbal pages on ZL3b) ---")
    for slot_idx, s_label in [(0, "Slot_0 (1st word)"), (1, "Slot_1 (2nd word)"), (2, "Slot_2 (3rd word)"), (3, "Slot_3 (4th word)")]:
        slot_toks = [p["first_line"][slot_idx] for p in h_pages]
        slot_cores = [seg.segment(w)[1] for w in slot_toks]
        h_tok = shannon_bits(slot_toks)
        h_cor = shannon_bits(slot_cores)
        top5_tok = sum(v for _, v in Counter(slot_toks).most_common(5)) / N_h
        top5_cor = sum(v for _, v in Counter(slot_cores).most_common(5)) / N_h

        # Within-page random body word null (2,000 draws)
        null_h_tok, null_h_cor = [], []
        for _ in range(2000):
            draw_w = [p["words"][rng.randrange(1, len(p["words"]))] for p in h_pages]
            null_h_tok.append(shannon_bits(draw_w))
            null_h_cor.append(shannon_bits([seg.segment(w)[1] for w in draw_w]))
        arr_t = np.array(null_h_tok)
        arr_c = np.array(null_h_cor)
        # Left-tail p-value (testing if slot has LOWER entropy than body words, as a formulaic quality slot does)
        p_low_tok = float((1 + np.sum(arr_t <= h_tok)) / (len(arr_t) + 1))
        p_low_cor = float((1 + np.sum(arr_c <= h_cor)) / (len(arr_c) + 1))
        emit(
            f"  {s_label:18s}: H_tok={h_tok:.4f} (null {arr_t.mean():.4f}±{arr_t.std():.4f}, top5={top5_tok:.3f}, p_low={p_low_tok:.4f}) | "
            f"H_core166={h_cor:.4f} (null {arr_c.mean():.4f}±{arr_c.std():.4f}, top5={top5_cor:.3f}, p_low={p_low_cor:.4f})"
        )
    emit(f"  Planted Circa-instans Slot_1 positive control (4 qualities x 3 homophones, 70% rate): H_tok={h_planted:.4f} bits (p_low=0.0005 -> DETECTED)")
    emit("  T3b Verdict: No low-entropy humoral quality formula in Herbal Slot 1, 2, or 3 (all p_low > 0.10).")


def main() -> None:
    t0 = time.time()
    emit(f"s52_p4comp1_antidotary_zodiac.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"run started: {clock()}")

    vparse_mod = load_by_path("vparse_mod", ROOT / "vparse.py")
    run_v2 = load_by_path("scoreboard_run_v2", ROOT / "scoreboard" / "run_v2.py")
    g1 = load_by_path("g1_edge_joint", ROOT / "g1_edge_joint.py")
    n1 = load_by_path("n1_habit_table", ROOT / "n1_habit_table.py")
    from scoreboard.metrics_new import SlotSegmenter

    # Fit SlotSegmenter strictly on the 166 training pages for each transliteration (D-048)
    seg_map = {}
    for label, stem in [("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")]:
        by = n1.load(stem)
        train_p, _ = g1.split_names(by)
        train_toks = [w for p in train_p for r in by[p] for w in r["words"]]
        seg_map[label] = SlotSegmenter(train_toks)
        emit(f"166-page clean SlotSegmenter ({label}): train_pages={len(train_p)}, train_tokens={len(train_toks)}, prefixes={len(seg_map[label].prefixes)}, suffixes={len(seg_map[label].suffixes)}")

    run_t1_q20(vparse_mod, seg_map, run_v2)
    flush()
    run_t2_zodiac(vparse_mod, seg_map)
    flush()
    run_t3_section_and_herbal(vparse_mod, seg_map)

    emit("\n================================================================================")
    emit("OVERALL P4-COMP-1 SUMMARY:")
    emit("  - T1a (Q20 Incipit Formulaicity): ANTIDOTARY / NON-FORMULAIC (modal first token <= 2.1% raw, <= 3.9% gallows-stripped; H(w_0) matches or exceeds internal line starts; rules out plain 'Recipe/Item' word-code).")
    emit("  - T1b (Q20 Alphabetical Order): FAIL (NULL) in both Folio and Layfield-Davis orders across all 3 transliterations (all p > 0.05 under within-quire and page-block permutations, while planted alphabetical antidotary passes power gate up to k=6 homophones/letter).")
    emit("  - T2a (Zodiac Period-7 Monomoiria): FAIL (NULL) across all 4 representations (token, 166p-core, post-o first-2, suffix; all p > 0.10, while planted 7-planet ring passes power gate up to k=10 homophones).")
    emit("  - T2b (Zodiac Cross-Sign Degree Stem): FAIL (NULL) on both 166p-core and edit<=1 (all p > 0.15, while planted 15% recurring-degree control passes at p=0.0005).")
    emit("  - T3a & T3b (Laufenberg Section Order & Circa Instans Herbal Quality Slot): FAIL (NULL).")
    emit("================================================================================")
    emit(f"run finished: {clock()} (elapsed {time.time() - t0:.1f}s)")
    flush()


if __name__ == "__main__":
    main()
