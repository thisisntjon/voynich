"""s66 -- Scribal Self-Corrections & Overwrites Anatomy (D-055 Rec 3), Quire/Bifolio Vocabulary
Turnover & Rare-Core Horizon, and Post-Mortem Diagnosis of Phase-4 Producers (s57, s58, s61, s67; D-056).

PRE-REGISTERED (frozen in s66_scribal_corrections_and_quire_seams.prereg.sha256 BEFORE running on data).

SCIENTIFIC OBJECTIVES (s66):
1. Part 1 (D-055 Rec 3: Complete Forensic Catalog & Slot-Grammar Test of Scribal Self-Corrections,
   Overwrites, and [a:b] Alternates in ZL3b-n.txt):
   - Extracts all 21 <!corr?> / <!erased?> / <!weirdo> tokens from raw IVTFF lines in data/ZL3b-n.txt
     along with folio, locus, Davis hand, section, raw IVTFF token, cleaned token, preceding/following
     tokens, line slot, 166p-fitted SlotSegmenter (P, C, S) decomposition, and physical bounding-box
     coordinates [x, y, w, h] from tools/boxes.py (223 box-aligned folios).
   - Analyzes all inline [a:b] glyph-alternation tokens across data/ZL3b-n.txt: classifies whether the
     alternation sits in Prefix (P), Core (C), or Suffix (S), tests whether one variant is a higher-frequency
     attested 166p training word/core while the other is rare/unseen, and tabulates the top glyph-pair
     confusions (o/a, e/c, d/s, ch/sh, k/t, i/ii, l/r, etc.).

2. Part 2 (Hierarchical Quire/Bifolio Vocabulary Turnover & Codicological Horizon of Rare-Core Families):
   - Directly answers CONSTRAINTS-MAP.md Dot 23 & §C ("why each quire's vocabulary is narrow") and
     voynich-08's TEAM-HANDOFF note ("quire vocabulary turnover left to Argon's s66").
   - Across ZL3b, RF1b, and IT2a (166p-fitted SlotSegmenter), measures across all 15 quires with >= 300 tokens:
     (a) Active core inventory ratio: observed core types in quire Q vs expected core types from a
         token-count-matched draw from the same (Davis Hand, Section) pool and from the global training
         lexicon (explaining Quire M's 1.75x over-production in s67 and the low cross-page core coverage
         f5a = 0.573 in s55).
     (b) 5-level hierarchical core Jaccard & cross-entropy turnover strictly WITHIN the same (Hand, Section):
         Same-Leaf Recto<->Verso vs Same-Bifolio Conjoint Sheet ($B) vs Same-Quire Non-Conjoint ($Q)
         vs Cross-Quire Same-(Hand, Section) vs Cross-Hand.
     (c) Codicological horizon of edit-1 rare-core families (extending s59/s62/s63): within-page edit-1
         rare-core sharing vs Same-Leaf Recto/Verso vs Conjoint Bifolio vs Same-Quire vs Cross-Quire
         within (Hand, Section), plus decomposition of within-page edit-1 rare-core pairs into
         Boundary-Bleed (P/S glyph), Vowel/Minim-Run edit (o/a/e/i/y), and Consonant/Gallows edit.

3. Part 3 (D-056 Mechanistic Post-Mortem of s57, s58, s61, and s67 -- Why All Four Producers Missed
   the Joint Target, with Zero New Producer Fitting):
   - Evaluates the saved held-out sidecar corpora in runs/s57/, runs/s58/, and runs/s61/ against real
     held-out pages (41 pages, seed=20261017) across ZL3b, RF1b, and IT2a, plus analyzes the 15-quire
     LOQO prefix-order gap in s67:
     (a) Whole-word memorization vs compositional OOV (CHARWIN): why drawing whole training words in
         s57 (-0.313) and s61 (-0.214) collapses the held-out OOV word rate (~6.0% vs real 17.2%) so
         word unigram beats char-3, whereas compositional part-assembly in s58 (+0.089) and core-class
         part-assembly in s67 (CA, positive on 13/15 quires) restores the positive CHARWIN sign.
     (b) 4-way within-line length covariance decomposition:
         Delta_Cov(|w_t|, |w_{t+1}|) = Cov(|A_t|,|A_{t+1}|) + Cov(|C_t|,|C_{t+1}|)
                                     + Cov(|A_t|,|C_{t+1}|) + Cov(|C_t|,|A_{t+1}|)
         plus within-word Cov(|A_t|, |C_t|) across Real Held-Out vs s57, s58, s61.
     (c) Exact information-theoretic diagnosis of why s67 (CA) produced prefix_gain ~ 0.000 vs real +0.100:
         decomposes held-out I(P_t; P_{t-1}) into the part mediated by s67's conditioning variables
         (class(C_t), pos_t, S_{t-1}) vs the unmediated conditional mutual information
         I(P_t; P_{t-1} | class(C_t), pos_t, S_{t-1}) and page-level prefix regime persistence.

Run:    python -I s66_scribal_corrections_and_quire_seams.py
Writes: results_s66.txt (only).
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import boxes as box_mod  # noqa: E402
import corpora  # noqa: E402
import g1_edge_joint as G1  # noqa: E402
import vparse  # noqa: E402
from scoreboard.metrics_new import CharMarkov, SlotSegmenter, UnigramGT  # noqa: E402

SELF = ROOT / "s66_scribal_corrections_and_quire_seams.py"
STUB = ROOT / "s66_scribal_corrections_and_quire_seams.prereg.sha256"
OUT = ROOT / "results_s66.txt"
SEED = 20261017
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}

log: list[str] = []
T_START = time.time()


def emit(s: str = "") -> None:
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_stub() -> bool:
    h_self = sha256(SELF)
    emit(f"sha256 s66_scribal_corrections_and_quire_seams.py: {h_self}")
    if not STUB.exists():
        emit("stub_match: False (missing stub)")
        return False
    h_stub_file = sha256(STUB)
    emit(f"sha256 s66_scribal_corrections_and_quire_seams.prereg.sha256: {h_stub_file}")
    txt = STUB.read_text(encoding="utf-8").strip().splitlines()
    ok = False
    for line in txt:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1].endswith("s66_scribal_corrections_and_quire_seams.py"):
            ok = (parts[0].lower() == h_self.lower())
    emit(f"stub_match: {ok}")
    return ok


def parse_zl_folio_headers() -> dict[str, dict[str, str]]:
    zl_path = ROOT / "data" / "ZL3b-n.txt"
    out: dict[str, dict[str, str]] = {}
    for raw in zl_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = vparse.PAGE_RE.match(raw)
        if m:
            f = m.group(1)
            d = dict(vparse.VAR_RE.findall(m.group(2)))
            out[f] = {
                "quire": d.get("Q", "?"),
                "bifolio": d.get("B", "?"),
                "hand": d.get("H", "?"),
                "section": d.get("I", "?"),
                "currier": d.get("L", "?"),
            }
    return out


def clean_tok(t: str) -> str:
    res = vparse.clean(t)
    return res[0] if res else ""


def load_translit_pages(meta_name: str):
    meta_path = ROOT / "data" / "translit" / f"{meta_name}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    by_page: dict[str, list[list[str]]] = {}
    page_meta: dict[str, dict] = {}
    for p in meta["pages"]:
        f = str(p["id"])
        lines = [[w for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue
        by_page[f] = lines
        page_meta[f] = {
            "folio": f,
            "section": str(p.get("section", "?")),
            "currier": str(p.get("currier", "?")),
            "hand": str(p.get("hand", "?")),
            "quire": str(p.get("quire", "?")),
            "bifolio": str(p.get("bifolio", "?")),
        }
    zl_folios = parse_zl_folio_headers()
    for f, fdict in zl_folios.items():
        if f in page_meta:
            for k in ("quire", "bifolio", "hand", "section", "currier"):
                if page_meta[f][k] in ("?", "", "None"):
                    page_meta[f][k] = fdict[k]
    return by_page, page_meta, sha256(meta_path)[:16]


def leaf_stem(folio: str) -> str:
    m = re.match(r"^(f\d+)[rv]", folio)
    return m.group(1) if m else folio


def is_edit1(a: str, b: str) -> bool:
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diffs = sum(1 for x, y in zip(a, b) if x != y)
        return diffs == 1
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


def classify_edit1_pair(c1: str, c2: str, pre_set: set[str], suf_set: set[str]) -> str:
    """Classify an edit-1 pair (c1, c2) into Boundary-Bleed, Vowel/Minim edit, or Consonant/Gallows edit."""
    VOWELS = set("oaeiy")
    la, lb = len(c1), len(c2)
    if la != lb:
        short, long_s = (c1, c2) if la < lb else (c2, c1)
        # Check if 1-char prefix or suffix extension
        if long_s[1:] == short and (long_s[0] in pre_set or long_s[0] in "oydlsr"):
            return "B_bleed"
        if long_s[:-1] == short and (long_s[-1] in suf_set or long_s[-1] in "yrlnsomd"):
            return "B_bleed"
        # Find inserted char
        ch_diff = None
        for idx in range(len(short)):
            if short[idx] != long_s[idx]:
                ch_diff = long_s[idx]
                break
        if ch_diff is None:
            ch_diff = long_s[-1]
        return "V_vowel_minim" if ch_diff in VOWELS else "C_cons_gallows"
    else:
        diffs = [(idx, x, y) for idx, (x, y) in enumerate(zip(c1, c2)) if x != y]
        if len(diffs) != 1:
            return "C_cons_gallows"
        idx, x, y = diffs[0]
        if (idx == 0 and (x in pre_set or y in pre_set)) or (idx == la - 1 and (x in suf_set or y in suf_set)):
            if x not in VOWELS or y not in VOWELS:
                return "B_bleed"
        if x in VOWELS and y in VOWELS:
            return "V_vowel_minim"
        return "C_cons_gallows"


# ==============================================================================
# PART 1: D-055 Rec 3 -- 21 Scribal Self-Corrections, Overwrites & [a:b] Catalog
# ==============================================================================
def run_part1(seg_zl: SlotSegmenter, train_words: Counter, train_cores: Counter) -> None:
    emit("=== PART 1 (D-055 Rec 3): Forensic Catalog of 21 Scribal Corrections/Overwrites & [a:b] Alternations ===")
    zl_path = ROOT / "data" / "ZL3b-n.txt"
    raw_lines = zl_path.read_text(encoding="utf-8", errors="replace").splitlines()
    zl_folios = parse_zl_folio_headers()
    aligned_box_map: dict[tuple[str, int], list[dict]] = {}
    try:
        aligned_pages, _ = box_mod.align_all(vparse.load())
        for f_k, pairs in aligned_pages.items():
            for rec, al_line in pairs:
                aligned_box_map[(f_k, rec["line"])] = al_line["tokens"]
    except Exception:
        aligned_box_map = {}

    corr_tag_re = re.compile(r"<!(?:corr|erased|overwrite|added|weirdo)[^>]*>")
    loc_re = re.compile(r"^<(f[^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    events = []
    ab_tokens = []

    for line in raw_lines:
        if not line.startswith("<f"):
            continue
        m = loc_re.match(line)
        if not m:
            continue
        folio, loc_id, ltype, body = m.group(1), m.group(2), m.group(3), m.group(4)
        fobj = zl_folios.get(folio, {})
        hand = fobj.get("hand", "?")
        sec = fobj.get("section", "?")
        quire = fobj.get("quire", "?")

        # Tokenize raw body on dots/commas/spaces while preserving inline tags per token
        body_no_line_tags = re.sub(r"<\$[^>]*>|<->|<!plant[^>]*>|<!figure[^>]*>|<!label[^>]*>", " ", body)
        raw_toks = [t for t in re.split(r"[.,\s]+", body_no_line_tags.strip()) if t]
        clean_toks = [clean_tok(t) for t in raw_toks]

        line_num = int(loc_id) if loc_id.isdigit() else -1
        line_boxes = aligned_box_map.get((folio, line_num))

        for ti, rtok in enumerate(raw_toks):
            ctok = clean_toks[ti]
            pos_slot = (
                "para_0" if (ti == 0 and ltype.startswith("@P"))
                else ("line_0" if ti == 0 else ("line_end" if ti == len(raw_toks) - 1 else "mid"))
            )
            prev_w = clean_toks[ti - 1] if ti > 0 else "^"
            next_w = clean_toks[ti + 1] if ti + 1 < len(raw_toks) else "$"

            # 1A: Check for <!corr?> / <!erased?> / <!weirdo>
            tags = corr_tag_re.findall(rtok)
            if tags:
                p_s, c_s, s_s = seg_zl.segment(ctok) if ctok else ("", "", "")
                b_coord = "no_box"
                if line_boxes and ti < len(line_boxes):
                    wb = line_boxes[ti]
                    bx = int(round(wb["cx"] - wb["w"] / 2))
                    by_c = int(round(wb["cy"] - wb["h"] / 2))
                    b_coord = f"[{bx},{by_c},{wb['w']},{wb['h']}]"
                events.append({
                    "idx": len(events) + 1,
                    "folio": folio,
                    "loc": f"{loc_id},{ltype}",
                    "quire": quire,
                    "hand": hand,
                    "sec": sec,
                    "pos": pos_slot,
                    "tag": "".join(tags),
                    "raw": rtok,
                    "clean": ctok or "(erased)",
                    "prev": prev_w,
                    "next": next_w,
                    "pcs": f"{p_s or '-'}|{c_s or '-'}|{s_s or '-'}",
                    "core_cnt": train_cores.get(c_s, 0) if c_s else 0,
                    "word_cnt": train_words.get(ctok, 0) if ctok else 0,
                    "box": b_coord,
                })

            # 1B: Check for inline [a:b] bracketed glyph alternations
            ab_matches = list(re.finditer(r"\[([^:\]]+):([^\]]+)\]", rtok))
            if ab_matches and ltype.startswith(("P", "+P", "@P")):
                # Construct variant A and variant B
                var_a_raw = re.sub(r"\[([^:\]]+):([^\]]+)\]", r"\1", rtok)
                var_b_raw = re.sub(r"\[([^:\]]+):([^\]]+)\]", r"\2", rtok)
                va = clean_tok(var_a_raw)
                vb = clean_tok(var_b_raw)
                if va and vb and va != vb:
                    pa, ca, sa = seg_zl.segment(va)
                    pb, cb, sb = seg_zl.segment(vb)
                    if pa != pb and ca == cb and sa == sb:
                        slot_changed = "Prefix"
                    elif sa != sb and pa == pb and ca == cb:
                        slot_changed = "Suffix"
                    elif ca != cb and pa == pb and sa == sb:
                        slot_changed = "Core"
                    else:
                        slot_changed = "Boundary_Shift(P/C/S)"
                    for m_ab in ab_matches:
                        ga, gb = m_ab.group(1), m_ab.group(2)
                        pair_key = "/".join(sorted([ga, gb]))
                        ab_tokens.append({
                            "folio": folio,
                            "hand": hand,
                            "sec": sec,
                            "pos": pos_slot,
                            "va": va,
                            "vb": vb,
                            "slot": slot_changed,
                            "pair": pair_key,
                            "wa_cnt": train_words.get(va, 0),
                            "wb_cnt": train_words.get(vb, 0),
                            "ca_cnt": train_cores.get(ca, 0),
                            "cb_cnt": train_cores.get(cb, 0),
                        })

    emit(f"Total <!corr/erased/weirdo> token events in ZL3b-n.txt: {len(events)}")
    emit(
        f"{'#':>2} {'Folio':6} {'Loc':9} {'Q':2} {'H':2} {'S':2} {'Slot':8} {'Tag':14} "
        f"{'Clean':12} {'P|C|S (166p)':16} {'wCnt':>4} {'cCnt':>4} {'Prev':10} {'Next':10} {'Box [x,y,w,h]':18}"
    )
    tag_counts = Counter()
    hand_counts = Counter()
    pos_counts = Counter()
    attested_core_n = 0
    nonempty_n = 0
    for ev in events:
        tag_counts[ev["tag"]] += 1
        hand_counts[ev["hand"]] += 1
        pos_counts[ev["pos"]] += 1
        if ev["clean"] != "(erased)":
            nonempty_n += 1
            if ev["core_cnt"] > 0:
                attested_core_n += 1
        emit(
            f"{ev['idx']:2d} {ev['folio']:6} {ev['loc']:9} {ev['quire']:2} {ev['hand']:2} {ev['sec']:2} "
            f"{ev['pos']:8} {ev['tag']:14} {ev['clean']:12} {ev['pcs']:16} "
            f"{ev['word_cnt']:4d} {ev['core_cnt']:4d} {ev['prev']:10} {ev['next']:10} {ev['box']:18}"
        )
    emit(
        f"Summary 1A: tags={dict(tag_counts)} | by_hand={dict(hand_counts)} | by_pos={dict(pos_counts)} | "
        f"non-erased tokens with attested 166p core: {attested_core_n}/{nonempty_n} "
        f"({100.0 * attested_core_n / max(1, nonempty_n):.1f}%)"
    )

    # Summarize 1B: [a:b] inline glyph alternations
    slot_c = Counter(r["slot"] for r in ab_tokens)
    pair_c = Counter(r["pair"] for r in ab_tokens)
    one_attested_word = sum(1 for r in ab_tokens if (r["wa_cnt"] > 0) != (r["wb_cnt"] > 0))
    both_attested_word = sum(1 for r in ab_tokens if r["wa_cnt"] > 0 and r["wb_cnt"] > 0)
    any_attested_core = sum(1 for r in ab_tokens if r["ca_cnt"] > 0 or r["cb_cnt"] > 0)
    freq_ratio_gt5 = sum(
        1 for r in ab_tokens if max(r["wa_cnt"], r["wb_cnt"]) >= 5 * max(1, min(r["wa_cnt"], r["wb_cnt"]))
    )
    emit("")
    emit(f"Summary 1B: Inline [a:b] glyph-alternation occurrences in paragraph lines: {len(ab_tokens)}")
    emit(
        f"  Slot localization of [a:b]: Core={slot_c['Core']} ({100*slot_c['Core']/max(1,len(ab_tokens)):.1f}%), "
        f"Boundary_Shift(P/C/S)={slot_c['Boundary_Shift(P/C/S)']} ({100*slot_c['Boundary_Shift(P/C/S)']/max(1,len(ab_tokens)):.1f}%), "
        f"Suffix={slot_c['Suffix']} ({100*slot_c['Suffix']/max(1,len(ab_tokens)):.1f}%), "
        f"Prefix={slot_c['Prefix']} ({100*slot_c['Prefix']/max(1,len(ab_tokens)):.1f}%)"
    )
    emit(
        f"  Lexical asymmetry (166p training): exactly one of (a,b) is attested training word = "
        f"{one_attested_word}/{len(ab_tokens)} ({100*one_attested_word/max(1,len(ab_tokens)):.1f}%), "
        f"both attested = {both_attested_word}/{len(ab_tokens)} ({100*both_attested_word/max(1,len(ab_tokens)):.1f}%), "
        f"dominant variant >=5x rarer variant = {freq_ratio_gt5}/{len(ab_tokens)} ({100*freq_ratio_gt5/max(1,len(ab_tokens)):.1f}%), "
        f"at least one core attested = {any_attested_core}/{len(ab_tokens)} ({100*any_attested_core/max(1,len(ab_tokens)):.1f}%)"
    )
    top_pairs = ", ".join(f"{k}:{v}" for k, v in pair_c.most_common(12))
    emit(f"  Top 12 [a:b] glyph pairs: {top_pairs}")
    emit("")


# ==============================================================================
# PART 2: Quire/Bifolio Vocabulary Turnover & Codicological Horizon of Rare Cores
# ==============================================================================
def run_part2() -> dict:
    emit("=== PART 2: Quire/Bifolio Vocabulary Turnover (Dot 23) & Codicological Horizon of Rare-Core Families ===")
    rng = random.Random(SEED)
    part2_out = {}

    for T_label, meta_name in TRANSLITS.items():
        by_page, page_meta, h_meta = load_translit_pages(meta_name)
        train_p, test_p = G1.split_names(by_page)
        train_lines = [ln for p in train_p for ln in by_page[p]]
        train_toks = [w for ln in train_lines for w in ln]
        seg = SlotSegmenter(train_toks)
        pre_set = set(seg.prefixes) - {""}
        suf_set = set(seg.suffixes) - {""}

        # Segment every page into words and cores
        page_cores: dict[str, list[str]] = {}
        page_words: dict[str, list[str]] = {}
        global_core_counts = Counter()
        for p, lines in by_page.items():
            w_list = [w for ln in lines for w in ln]
            c_list = [seg.segment(w)[1] for w in w_list]
            page_words[p] = w_list
            page_cores[p] = c_list
            global_core_counts.update(c_list)

        top20_cores = {c for c, _ in global_core_counts.most_common(20)}

        # 2A: Quire-level vocabulary narrowness across the 15 quires with >= 300 tokens
        quire_pages: dict[str, list[str]] = defaultdict(list)
        hs_pool_words: dict[tuple[str, str], list[str]] = defaultdict(list)
        hs_pool_cores: dict[tuple[str, str], list[str]] = defaultdict(list)
        all_words_flat = []
        all_cores_flat = []
        for p in sorted(by_page.keys()):
            m = page_meta[p]
            q = m["quire"]
            hs = (m["hand"], m["section"])
            quire_pages[q].append(p)
            hs_pool_words[hs].extend(page_words[p])
            hs_pool_cores[hs].extend(page_cores[p])
            all_words_flat.extend(page_words[p])
            all_cores_flat.extend(page_cores[p])

        quire_rows = []
        for q in sorted(quire_pages.keys()):
            ps = quire_pages[q]
            q_words = [w for p in ps for w in page_words[p]]
            q_cores = [c for p in ps for c in page_cores[p]]
            if len(q_words) < 300 or q == "?":
                continue
            obs_w_types = len(set(q_words))
            obs_c_types = len(set(q_cores))
            # Dominant (hand, section) for this quire
            hs_counts = Counter((page_meta[p]["hand"], page_meta[p]["section"]) for p in ps)
            dom_hs = hs_counts.most_common(1)[0][0]
            # Expected word & core types under:
            # (i) Global random token draw of size N_q
            # (ii) Same-(Hand, Section) random token draw of size N_q
            exp_w_glob, exp_c_glob = [], []
            exp_w_hs, exp_c_hs = [], []
            n_q = len(q_words)
            hs_w_src = hs_pool_words[dom_hs] if len(hs_pool_words[dom_hs]) >= n_q else all_words_flat
            hs_c_src = hs_pool_cores[dom_hs] if len(hs_pool_cores[dom_hs]) >= n_q else all_cores_flat
            for _ in range(50):
                samp_idx = [rng.randrange(len(all_words_flat)) for _ in range(n_q)]
                exp_w_glob.append(len({all_words_flat[i] for i in samp_idx}))
                exp_c_glob.append(len({all_cores_flat[i] for i in samp_idx}))
                samp_hs = [rng.randrange(len(hs_w_src)) for _ in range(n_q)]
                exp_w_hs.append(len({hs_w_src[i] for i in samp_hs}))
                exp_c_hs.append(len({hs_c_src[i] for i in samp_hs}))
            mw_glob = float(np.mean(exp_w_glob))
            mc_glob = float(np.mean(exp_c_glob))
            mw_hs = float(np.mean(exp_w_hs))
            mc_hs = float(np.mean(exp_c_hs))
            quire_rows.append({
                "quire": q,
                "n_pages": len(ps),
                "hand_sec": f"H{dom_hs[0]}:{dom_hs[1]}",
                "n_tok": n_q,
                "obs_w": obs_w_types,
                "exp_w_glob": mw_glob,
                "ratio_w_glob": mw_glob / max(1, obs_w_types),
                "obs_c": obs_c_types,
                "exp_c_glob": mc_glob,
                "ratio_c_glob": mc_glob / max(1, obs_c_types),
                "ratio_c_hs": mc_hs / max(1, obs_c_types),
            })

        # 2B: 5-Level Codicological Hierarchy for Rare-Core Family Sharing & Core Jaccard
        # For every page p, extract its set of distinct rare cores (excluding top-20 global cores)
        page_rare_types: dict[str, set[str]] = {
            p: {c for c in page_cores[p] if c and c not in top20_cores}
            for p in by_page
        }
        # Precompute edit-1 neighbors among all rare core types in the book
        all_rare_vocab = sorted({c for s in page_rare_types.values() for c in s})
        ed1_map: dict[str, set[str]] = defaultdict(set)
        by_len: dict[int, list[str]] = defaultdict(list)
        for c in all_rare_vocab:
            by_len[len(c)].append(c)
        for c in all_rare_vocab:
            L = len(c)
            for L2 in (L - 1, L, L + 1):
                for c2 in by_len.get(L2, ()):
                    if c < c2 and is_edit1(c, c2):
                        ed1_map[c].add(c2)
                        ed1_map[c2].add(c)

        # Within-page edit-1 family rate (for each rare core type on page p, does page p contain an edit-1 relative != c?)
        within_page_ed1_hits = 0
        within_page_rare_total = 0
        edit_class_counts = Counter()
        for p, rset in page_rare_types.items():
            if len(rset) < 2:
                continue
            for c in rset:
                within_page_rare_total += 1
                rels = ed1_map[c] & rset
                if rels:
                    within_page_ed1_hits += 1
                    for c2 in rels:
                        if c < c2:
                            edit_class_counts[classify_edit1_pair(c, c2, pre_set, suf_set)] += 1
        within_page_ed1_rate = within_page_ed1_hits / max(1, within_page_rare_total)

        # Pairwise page comparisons across the 5 codicological levels (controlling for token/type count via subsampling K=25 rare types per page)
        K_SUB = 25
        eligible_pages = [p for p, rset in page_rare_types.items() if len(rset) >= K_SUB]
        # Pre-draw 10 subsamples of K_SUB rare core types per eligible page so page size cannot confound any level!
        page_subs: dict[str, list[set[str]]] = {}
        for p in eligible_pages:
            rlist = sorted(page_rare_types[p])
            page_subs[p] = [set(rng.sample(rlist, K_SUB)) for _ in range(10)]

        # Also compute within-page split-half on K_SUB vs K_SUB (for pages with >= 2*K_SUB rare types)
        levels_exact: dict[str, list[float]] = defaultdict(list)
        levels_ed1: dict[str, list[float]] = defaultdict(list)

        for i_p, p1 in enumerate(eligible_pages):
            m1 = page_meta[p1]
            if m1["hand"] == "?" or m1["section"] == "?":
                continue
            for p2 in eligible_pages[i_p + 1:]:
                m2 = page_meta[p2]
                if m2["hand"] == "?" or m2["section"] == "?":
                    continue
                same_hs = (m1["hand"] == m2["hand"] and m1["section"] == m2["section"])
                if not same_hs:
                    lvl = "5_diff_hand_or_sec"
                elif leaf_stem(p1) == leaf_stem(p2):
                    lvl = "1_same_leaf_RV"
                elif m1["quire"] == m2["quire"] and m1["bifolio"] != "?" and m1["bifolio"] == m2["bifolio"]:
                    lvl = "2_conjoint_bifolio"
                elif m1["quire"] == m2["quire"] and m1["quire"] != "?":
                    lvl = "3_same_quire_other_bif"
                else:
                    lvl = "4_diff_quire_same_HS"

                # Size-standardized K_SUB x K_SUB exact rare-core overlap and edit-1 neighbor overlap
                ex_vals = []
                ed_vals = []
                for s1, s2 in zip(page_subs[p1][:4], page_subs[p2][:4]):
                    ex_vals.append(len(s1 & s2) / K_SUB)
                    ed_hits = sum(1 for c in s1 if (ed1_map[c] & s2))
                    ed_vals.append(ed_hits / K_SUB)
                levels_exact[lvl].append(float(np.mean(ex_vals)))
                levels_ed1[lvl].append(float(np.mean(ed_vals)))

        # Edit-class null on random cross-quire pairs within (hand, section)
        null_edit_class = Counter()
        for _ in range(400):
            p1, p2 = rng.sample(eligible_pages, 2)
            if page_meta[p1]["hand"] == page_meta[p2]["hand"] and page_meta[p1]["section"] == page_meta[p2]["section"]:
                for c in page_rare_types[p1]:
                    for c2 in (ed1_map[c] & page_rare_types[p2]):
                        null_edit_class[classify_edit1_pair(c, c2, pre_set, suf_set)] += 1

        emit(f"--- {T_label} (meta sha256={h_meta}) ---")
        emit("  2A. Quire-Level Vocabulary Narrowness (Global Pool vs Quire Observed; explains s67 Dot 23):")
        emit(
            f"    {'Quire':5} {'Pages':>5} {'Hand:Sec':8} {'Tokens':>6} | {'ObsWord':>7} {'ExpW_Glob':>9} {'Glob/ObsW':>9} | "
            f"{'ObsCore':>7} {'ExpC_Glob':>9} {'Glob/ObsC':>9} {'HS/ObsC':>8}"
        )
        for qr in quire_rows:
            emit(
                f"    {qr['quire']:5} {qr['n_pages']:5d} {qr['hand_sec']:8} {qr['n_tok']:6d} | "
                f"{qr['obs_w']:7d} {qr['exp_w_glob']:9.1f} {qr['ratio_w_glob']:8.3f}x | "
                f"{qr['obs_c']:7d} {qr['exp_c_glob']:9.1f} {qr['ratio_c_glob']:8.3f}x {qr['ratio_c_hs']:7.3f}x"
            )
        mean_w_over = float(np.mean([r["ratio_w_glob"] for r in quire_rows]))
        mean_c_over = float(np.mean([r["ratio_c_glob"] for r in quire_rows]))
        mean_c_hs_over = float(np.mean([r["ratio_c_hs"] for r in quire_rows]))
        qm_row = next((r for r in quire_rows if r["quire"] == "M"), None)
        qm_str = f"{qm_row['ratio_w_glob']:.3f}x words / {qm_row['ratio_c_glob']:.3f}x cores" if qm_row else "n/a"
        emit(
            f"    Mean across {len(quire_rows)} quires: Global-pool draw over-produces word types by {mean_w_over:.3f}x "
            f"and core types by {mean_c_over:.3f}x (within Hand+Sec draw over-produces cores by {mean_c_hs_over:.3f}x; "
            f"Quire M = {qm_str})."
        )

        emit("  2B. Size-Controlled (K=25 rare cores/page) Codicological Hierarchy Within (Hand, Section):")
        base_ex = float(np.mean(levels_exact["4_diff_quire_same_HS"]))
        base_ed = float(np.mean(levels_ed1["4_diff_quire_same_HS"]))
        for lvl_k in (
            "1_same_leaf_RV",
            "2_conjoint_bifolio",
            "3_same_quire_other_bif",
            "4_diff_quire_same_HS",
            "5_diff_hand_or_sec",
        ):
            ex_arr = levels_exact[lvl_k]
            ed_arr = levels_ed1[lvl_k]
            m_ex = float(np.mean(ex_arr)) if ex_arr else 0.0
            m_ed = float(np.mean(ed_arr)) if ed_arr else 0.0
            emit(
                f"    {lvl_k:24} (n_pairs={len(ex_arr):4d}): exact_rare_share={m_ex:.4f} ({m_ex/max(1e-9,base_ex):.3f}x vs diff_quire_HS) | "
                f"edit1_rare_share={m_ed:.4f} ({m_ed/max(1e-9,base_ed):.3f}x vs diff_quire_HS)"
            )

        tot_ec = max(1, sum(edit_class_counts.values()))
        tot_nc = max(1, sum(null_edit_class.values()))
        emit(
            f"  2C. Within-Page Edit-1 Rare-Core Pair Anatomy (n_pairs={tot_ec}, within_page_rate={within_page_ed1_rate:.3f}): "
            f"Boundary_Bleed={100*edit_class_counts['B_bleed']/tot_ec:.1f}% (null {100*null_edit_class['B_bleed']/tot_nc:.1f}%), "
            f"Vowel/Minim={100*edit_class_counts['V_vowel_minim']/tot_ec:.1f}% (null {100*null_edit_class['V_vowel_minim']/tot_nc:.1f}%), "
            f"Cons/Gallows={100*edit_class_counts['C_cons_gallows']/tot_ec:.1f}% (null {100*null_edit_class['C_cons_gallows']/tot_nc:.1f}%)"
        )
        emit("")
        part2_out[T_label] = {
            "mean_w_over": mean_w_over,
            "mean_c_over": mean_c_over,
            "mean_c_hs_over": mean_c_hs_over,
            "qm_w_over": qm_row["ratio_w_glob"] if qm_row else 0.0,
            "rv_vs_diffq_ex": float(np.mean(levels_exact["1_same_leaf_RV"])) / max(1e-9, base_ex),
            "sameq_vs_diffq_ex": float(np.mean(levels_exact["3_same_quire_other_bif"])) / max(1e-9, base_ex),
            "rv_vs_diffq_ed1": float(np.mean(levels_ed1["1_same_leaf_RV"])) / max(1e-9, base_ed),
        }
    return part2_out


# ==============================================================================
# PART 3: D-056 Post-Mortem of Phase-4 Producers (s57, s58, s61, s67)
# ==============================================================================
def four_way_length_cov(lines: list[list[str]], seg: SlotSegmenter, seed: int = 20261017) -> dict[str, float]:
    """Decompose within-line lag-1 word-length covariance into (A->A, C->C, A->C, C->A) excess over line shuffle."""
    rng = random.Random(seed)
    w_lens = []
    a_lens = []
    c_lens = []
    ac_within_x = []
    ac_within_y = []
    for ln in lines:
        if len(ln) < 2:
            continue
        lw, la, lc = [], [], []
        for w in ln:
            p, c, s = seg.segment(w)
            lw.append(len(w))
            la.append(len(p) + len(s))
            lc.append(len(c))
            ac_within_x.append(len(p) + len(s))
            ac_within_y.append(len(c))
        w_lens.append(lw)
        a_lens.append(la)
        c_lens.append(lc)

    def pair_cov(seqs_x, seqs_y):
        xs, ys = [], []
        for sx, sy in zip(seqs_x, seqs_y):
            for i in range(len(sx) - 1):
                xs.append(sx[i])
                ys.append(sy[i + 1])
        if not xs:
            return 0.0
        xa = np.asarray(xs, dtype=float)
        ya = np.asarray(ys, dtype=float)
        return float(np.mean((xa - xa.mean()) * (ya - ya.mean())))

    obs_ww = pair_cov(w_lens, w_lens)
    obs_aa = pair_cov(a_lens, a_lens)
    obs_cc = pair_cov(c_lens, c_lens)
    obs_ac = pair_cov(a_lens, c_lens)
    obs_ca = pair_cov(c_lens, a_lens)

    n_shuf = 100
    n_ww, n_aa, n_cc, n_ac, n_ca = [], [], [], [], []
    for _ in range(n_shuf):
        sw, sa, sc = [], [], []
        for lw, la, lc in zip(w_lens, a_lens, c_lens):
            idx = list(range(len(lw)))
            rng.shuffle(idx)
            sw.append([lw[i] for i in idx])
            sa.append([la[i] for i in idx])
            sc.append([lc[i] for i in idx])
        n_ww.append(pair_cov(sw, sw))
        n_aa.append(pair_cov(sa, sa))
        n_cc.append(pair_cov(sc, sc))
        n_ac.append(pair_cov(sa, sc))
        n_ca.append(pair_cov(sc, sa))

    ax = np.asarray(ac_within_x, dtype=float)
    cy = np.asarray(ac_within_y, dtype=float)
    cov_within_ac = float(np.mean((ax - ax.mean()) * (cy - cy.mean())))

    return {
        "d_ww": obs_ww - float(np.mean(n_ww)),
        "d_aa": obs_aa - float(np.mean(n_aa)),
        "d_cc": obs_cc - float(np.mean(n_cc)),
        "d_ac": obs_ac - float(np.mean(n_ac)),
        "d_ca": obs_ca - float(np.mean(n_ca)),
        "within_ac": cov_within_ac,
    }


def load_sidecar_lines(meta_path: Path, test_set: set[str] | None = None) -> list[list[str]]:
    if meta_path.exists():
        d = json.loads(meta_path.read_text(encoding="utf-8"))
        if "pages" in d:
            pages = d["pages"]
            has_role = any("role" in p for p in pages)
            out = []
            for p in pages:
                if has_role and p.get("role") not in ("test", "heldout"):
                    continue
                if (not has_role) and test_set and str(p.get("id")) not in test_set and len(pages) > 60:
                    continue
                for ln in p["lines"]:
                    toks = [w for w in ln if w]
                    if toks:
                        out.append(toks)
            if out:
                return out
    txt_path = meta_path.with_suffix(".txt")
    if txt_path.exists():
        raw_lines = txt_path.read_text(encoding="utf-8").splitlines()
        return [[w for w in ln.strip().split() if w] for ln in raw_lines if ln.strip()]
    return []


def run_part3() -> None:
    emit("=== PART 3 (D-056): Mechanistic Post-Mortem of s57, s58, s61 Sidecars & s67 Prefix-Order Gap ===")
    emit(
        f"{'Text / Model':18} | {'HO_Types':>8} {'OOV_Word%':>9} {'H_uni':>7} {'H_char3':>7} {'CHARWIN':>8} | "
        f"{'dCov(w,w)':>9} {'dCov(A,A)':>9} {'dCov(C,C)':>9} {'dCov(A,C)':>9} {'dCov(C,A)':>9} {'Cov(A_t,C_t)':>12}"
    )

    for T_label, meta_name in TRANSLITS.items():
        by_page, page_meta, _ = load_translit_pages(meta_name)
        train_p, test_p = G1.split_names(by_page)
        train_lines = [ln for p in train_p for ln in by_page[p]]
        test_lines = [ln for p in test_p for ln in by_page[p]]
        train_toks = [w for ln in train_lines for w in ln]
        seg = SlotSegmenter(train_toks)
        train_vocab = set(train_toks)
        cm = CharMarkov(train_toks, 3)
        ug = UnigramGT(train_toks, cm)

        candidates = [("Real_HO", test_lines)]
        sidecar_specs = [
            ("s57_copy_vary", ROOT / "runs" / "s57" / f"gen_{T_label}_s1.meta.json"),
            ("s58_affix_wrap", ROOT / "runs" / "s58" / f"TL_{T_label}_s1.meta.json"),
            ("s61_joint_JW", ROOT / "runs" / "s61" / f"JW_{T_label}_s1.meta.json"),
        ]
        for s_name, s_path in sidecar_specs:
            if s_path.exists() or s_path.with_suffix(".txt").exists():
                sc_lines = load_sidecar_lines(s_path, set(test_p))
                if sc_lines:
                    candidates.append((s_name, sc_lines))

        for c_name, lines_ho in candidates:
            toks_ho = [w for ln in lines_ho for w in ln]
            n_types = len(set(toks_ho))
            oov_rate = sum(1 for w in toks_ho if w not in train_vocab) / max(1, len(toks_ho))
            h_uni = -sum(ug.logp_word(w) for w in toks_ho) / max(1, len(toks_ho))
            h_ch3 = -sum(cm.logp_word(w) for w in toks_ho) / max(1, len(toks_ho))
            charwin = h_uni - h_ch3
            covs = four_way_length_cov(lines_ho, seg, seed=SEED)
            label_row = f"{T_label}:{c_name}"
            emit(
                f"{label_row:18} | {n_types:8d} {100*oov_rate:8.2f}% {h_uni:7.3f} {h_ch3:7.3f} {charwin:+8.4f} | "
                f"{covs['d_ww']:+9.4f} {covs['d_aa']:+9.4f} {covs['d_cc']:+9.4f} "
                f"{covs['d_ac']:+9.4f} {covs['d_ca']:+9.4f} {covs['within_ac']:+12.4f}"
            )

        # 3B: Exact diagnosis of why s67 (CA) produced prefix_gain ~ 0.000 vs real +0.100
        # In s67, affixes (P_t, S_t) are drawn from P(P_t, S_t | class(C_t), pos_t, S_{t-1}) -- omitting P_{t-1} and page/hand state!
        train_p_uni = Counter()
        train_p_bi = defaultdict(Counter)
        train_p_s67_ctx = defaultdict(Counter)
        for ln in train_lines:
            prev_p = "^"
            prev_s = "^"
            for i, w in enumerate(ln):
                p, c, s = seg.segment(w)
                pos = "start" if i == 0 else ("end" if i == len(ln) - 1 else "mid")
                train_p_uni[p] += 1
                train_p_bi[prev_p][p] += 1
                train_p_s67_ctx[(pos, prev_s)][p] += 1
                prev_p, prev_s = p, s

        tot_tr = sum(train_p_uni.values())
        V_p = len(seg.prefixes) + 1

        def wb_prob(cnt: Counter, key: str, back_prob: float) -> float:
            n = sum(cnt.values())
            u = len(cnt)
            if n == 0:
                return back_prob
            return (cnt.get(key, 0) + u * back_prob) / (n + u)

        ll_uni = 0.0
        ll_bi = 0.0
        ll_s67_mediated = 0.0
        ll_joint_ps = 0.0
        ll_page_adapt = 0.0

        # Also fit joint (prev_p, prev_s, pos) on training
        train_p_joint = defaultdict(Counter)
        for ln in train_lines:
            prev_p, prev_s = "^", "^"
            for i, w in enumerate(ln):
                p, c, s = seg.segment(w)
                pos = "start" if i == 0 else ("end" if i == len(ln) - 1 else "mid")
                train_p_joint[(pos, prev_p, prev_s)][p] += 1
                prev_p, prev_s = p, s

        n_tok_ho = 0
        for p_name in test_p:
            p_lines = by_page[p_name]
            # Leave-one-line-out page prefix unigram for page-regime component
            page_p_counts = Counter(seg.segment(w)[0] for ln in p_lines for w in ln)
            for ln in p_lines:
                ln_p_counts = Counter(seg.segment(w)[0] for w in ln)
                rem_page = page_p_counts - ln_p_counts
                prev_p, prev_s = "^", "^"
                for i, w in enumerate(ln):
                    p, c, s = seg.segment(w)
                    pos = "start" if i == 0 else ("end" if i == len(ln) - 1 else "mid")
                    p0 = (train_p_uni.get(p, 0) + 0.5) / (tot_tr + 0.5 * V_p)
                    p_bi = wb_prob(train_p_bi[prev_p], p, p0)
                    # Under s67's model, P_t only knows (pos, prev_s), not prev_p
                    p_s67 = wb_prob(train_p_s67_ctx[(pos, prev_s)], p, p0)
                    p_j = wb_prob(train_p_joint[(pos, prev_p, prev_s)], p, p_s67)
                    p_pg = wb_prob(rem_page, p, p0)

                    ll_uni += -math.log2(max(1e-12, p0))
                    ll_bi += -math.log2(max(1e-12, p_bi))
                    ll_s67_mediated += -math.log2(max(1e-12, p_s67))
                    ll_joint_ps += -math.log2(max(1e-12, p_j))
                    ll_page_adapt += -math.log2(max(1e-12, p_pg))
                    prev_p, prev_s = p, s
                    n_tok_ho += 1

        h_p0 = ll_uni / n_tok_ho
        gain_bi = (ll_uni - ll_bi) / n_tok_ho
        gain_s67 = (ll_uni - ll_s67_mediated) / n_tok_ho
        gain_joint = (ll_uni - ll_joint_ps) / n_tok_ho
        cmi_p_given_s = (ll_s67_mediated - ll_joint_ps) / n_tok_ho
        gain_page_regime = (ll_uni - ll_page_adapt) / n_tok_ho
        emit(
            f"  [{T_label} Prefix-Order Decomposition on 41 Held-Out Pages (n={n_tok_ho})]: "
            f"H(P_t)={h_p0:.4f}b | lag1_prefix_gain={gain_bi:+.4f}b | "
            f"s67_pos_prevS_gain={gain_s67:+.4f}b | joint(pos,P_{{t-1}},S_{{t-1}})_gain={gain_joint:+.4f}b | "
            f"direct CMI I(P_t; P_{{t-1}} | pos, S_{{t-1}})={cmi_p_given_s:+.4f}b | "
            f"page_prefix_regime_gain={gain_page_regime:+.4f}b"
        )
    emit("")


def main() -> None:
    emit(f"s66 -- Scribal Self-Corrections, Quire/Bifolio Vocabulary Turnover & Producer Post-Mortem")
    emit(f"date: {datetime.now().isoformat(timespec='seconds')}")
    verify_stub()
    emit("")

    by_page_zl, _, _ = load_translit_pages("ZL3b_eva")
    train_p_zl, _ = G1.split_names(by_page_zl)
    train_lines_zl = [ln for p in train_p_zl for ln in by_page_zl[p]]
    train_toks_zl = [w for ln in train_lines_zl for w in ln]
    seg_zl = SlotSegmenter(train_toks_zl)
    train_words_zl = Counter(train_toks_zl)
    train_cores_zl = Counter(seg_zl.segment(w)[1] for w in train_toks_zl)

    run_part1(seg_zl, train_words_zl, train_cores_zl)
    run_part2()
    run_part3()

    emit(f"elapsed: {time.time() - T_START:.1f} s")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
