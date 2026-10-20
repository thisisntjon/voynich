#!/usr/bin/env python3
"""s77_deconfounded_scribe_and_comma_ablation_loqo.py — Section/Quire-Matched Herbal-B Scribe Test
& Direct Comma/Ink-Gap Alignment + LOQO Rare-Core Component Ablation (s77).

PRE-REGISTERED SPECIFICATION (frozen in s77_deconfounded_scribe_and_comma_ablation_loqo.prereg.sha256
BEFORE running on data):
Directly addresses the two methodological open items in workflow/CONSTRAINTS-MAP.md §C lines 197-198
(L-303 and L-304) across ZL3b, RF1b, and IT2a with ZERO reuse of the 166->41 page split or any
globally fitted segmenter:

  Part 1 (CONSTRAINTS-MAP.md §C line 198 & L-303: Section/Quire-Matched Herbal-B Hand 2 vs Hand 3
          Test with Clean Nested Training-Only Segmentation on LOBO & LOQO Folds):
    - On every fold of Leave-One-Bifolio-Out (LOBO, both physical sheet $Q|$B and folio leaf $Q|$F)
      and Leave-One-Quire-Out (LOQO), fits BOTH:
        (a) SlotSegmenter(train_fold_tokens) [greedy entropy-thresholded prefix/core/suffix], and
        (b) Seg_Affix2(train_fold_tokens) [independent boundary-free frequent 1-2 char onset/coda
            segmenter fitted strictly on training fold tokens]
      strictly on the training fold tokens, never touching the held-out fold.
    - Test 1A (Strictly Section-Matched Herbal-B: Hand 2 vs Hand 3 inside Section = H):
      * Evaluates three explicit Herbal-B / Quire-H cohort definitions side-by-side:
        - Cohort C1 (Strict Herbal-B: Sec=H, Lang=B, Davis Hand 2 [f26r..f55v in Quires D,E,F,G,
          20p; plus E,F,G subset f33r..f55v, 16p] vs Hand 3 [f94r..f95v in Quire Q, 6p; + f65v in
          Quire H, 7p]).
        - Cohort C2 (Extended Herbal-B + Quire H: Hand 2 [f26r..f55v] vs Hand 3+Quire-H
          [f58r..f66v in Quire H + f94r..f95v in Quire Q]).
        - Cohort C3 (Direct Intra-Quire-H & Intra-Quire-F Same-Quire Same-Section Contrasts:
          Quire H [f55r/v, f57r vs f65v, f58r/v, f66r/v] and Quire F [Hand 2 f43r/v, f46r/v vs
          Hand 5 f41r/v, f48r/v]).
      * Measures cross-scribe slot transfer penalty Delta_H(H2_HerbB <-> H3_HerbB) and symmetric
        divergence D_sym(H2_HerbB, H3_HerbB) on:
          (i)   All Herbal-B tokens (core-conditioned frame P(P_t, S_t | C_t, pos_t, S_{t-1})),
          (ii)  Shared Top-50 training cores (C_top50, zero topical core stem difference),
          (iii) Core-blind frame transitions P(P_t, S_t | pos_t, S_{t-1}, state).
      * Evaluates against three stratified permutation nulls (500 permutations + exact enumeration):
          - Null P1 (Within-Herbal-B Page Permutation): permuting Hand 2 / Hand 3 labels strictly
            among Herbal-B pages (completely eliminating Section B vs S confounding).
          - Null P2 (Within-Herbal-B Bifolio-Block Permutation): permuting Hand 2 / Hand 3 labels
            at the physical bifolio sheet level ($Q|$B) and folio-leaf level ($Q|$F) inside Herbal-B.
          - Null P3 (Within-Herbal-B Quire-Block Permutation + Direct Intra-Quire Contrasts).
      * Decomposes s60's unstratified Currier-B divergence (D_sym = +0.41) across the 2x2 factorial
        {Hand 2, Hand 3} x {Section H, Section B/S} and tests Out-of-Section Cross-Projection
        (training purely on Quire M [H2 Bio] vs Quire T [H3 Stars] and predicting untouched
        Herbal-B H2 vs H3 pages inside Section H).

  Part 2 (CONSTRAINTS-MAP.md §C line 197 & L-304: Direct Comma & Physical Ink-Gap Alignment of B2
          Two-Core Splits + Clean Nested LOQO Component Ablation):
    - Test 2A (Direct Inspection of Actual Comma ',' Locations in Raw IVTFF & Physical Ink Gaps):
      * Parses raw IVTFF files (data/ZL3b-n.txt, data/external/voynich-nu-ivtff/RF1b-er.txt,
        data/external/voynich-nu-ivtff/IT2a-n.txt) keeping exact character offsets of uncertain
        spaces (',' commas) inside U1 comma-joined words, AND cross-transliteration comma/space
        splits (where one transliteration writes w1.w2 or w1,w2 while another writes w1w2).
      * Aligns s47 physical intra-word ink-gap measurements (runs/s47/positions.tsv & runs/s45/pages/)
        to exact internal character offsets of words on the 127 clean Yale scan pages.
      * Across all 15 Leave-One-Quire-Out (LOQO) folds (with SlotSegmenter and Seg_Affix2 fitted
        strictly on the 14 training quires):
          1. Separates Strict 1-Glyph Boundary Shifts (B1_1char) from Multi-Glyph Reparses (B1_multi)
             and tests cross-segmenter stability (SlotSegmenter vs Seg_Affix2).
          2. For every held-out rare/unseen core that admits a B2 two-core split C = C1 + C2:
             measures how often an actual raw IVTFF comma ',' (in U1 before joining, OR in either
             of the other two transliterations at that exact token) or an s47 physical ink-space
             call (r = w_px / thr) sits at the exact C1 | C2 boundary vs internal non-split
             character positions and a length-matched character-shuffled string null.
    - Test 2B (Pre-Registered 6-Model Individual Component Ablation on 15 LOQO Folds):
      * On strictly unseen cores of each held-out quire across all 15 LOQO folds (ZL3b, RF1b, IT2a),
        under both SlotSegmenter and Seg_Affix2 fitted strictly on the 14 training quires, evaluates
        held-out cross-entropy (bits/core and bits/char) and 15-quire paired bootstrap 95% CIs of:
          1. M0_char2      : Stationary character Markov baseline (order 2; order 3 also reported).
          2. M1_bleed1_only: M0_char2 + Strict 1-Glyph Boundary Shift (B1_1char) ONLY.
          3. M2_reparse_only: M0_char2 + Alternative Multi-Glyph Training Affix Reparse (B1_reparse) ONLY.
          4. M3_comp_only  : M0_char2 + Two-Core Concatenation (B2_comp: C1 + C2) ONLY.
          5. M4_subglyph_only: M0_char2 + Sub-Glyph Allomorphy (B3: e/i run & gallows/vowel swap) ONLY.
          6. M5_joint_all  : Full joint mixture (M0_char2 + B1_1char + B1_reparse + B2_comp + B3_subglyph).

Run:    C:\\Users\\thisi\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -I s77_deconfounded_scribe_and_comma_ablation_loqo.py
Writes: results_s77.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import random
import re
import subprocess
import sys
import time
from collections import Counter, OrderedDict, defaultdict
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

import vparse  # noqa: E402
from scoreboard.metrics_new import CharMarkov, SlotSegmenter  # noqa: E402

SELF = ROOT / "s77_deconfounded_scribe_and_comma_ablation_loqo.py"
STUB = ROOT / "s77_deconfounded_scribe_and_comma_ablation_loqo.prereg.sha256"
OUT = ROOT / "results_s77.txt"

SEED = 20261017
N_PERM = 500
N_BOOT = 1000
TOPK_RARE = 20
EMPTY = "∅"

TRANSLITS = [
    ("ZL3b", "ZL3b_eva.meta.json", ROOT / "data" / "ZL3b-n.txt"),
    ("RF1b", "RF1b.meta.json", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"),
    ("IT2a", "IT2a.meta.json", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt"),
]

BOUND_UNITS_1CHAR = ("o", "y", "d", "l", "r", "s", "k", "t", "e", "a", "i", "n", "p", "f", "g", "m")
BOUND_UNITS_ALL = ("ch", "sh", "o", "y", "d", "l", "r", "s", "k", "t", "e", "a", "i", "n", "p", "f")
SUBGLYPH_PAIRS = (
    ("k", "t"), ("t", "k"),
    ("p", "f"), ("f", "p"),
    ("ch", "sh"), ("sh", "ch"),
    ("ckh", "cth"), ("cth", "ckh"),
    ("cph", "cfh"), ("cfh", "cph"),
    ("e", "ee"), ("ee", "e"),
    ("i", "ii"), ("ii", "i"),
    ("ii", "iii"), ("iii", "ii"),
    ("i", "iii"), ("iii", "i"),
    ("a", "o"), ("o", "a"),
    ("l", "r"), ("r", "l"),
)

log_lines: list[str] = []
T_START = time.time()


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


# ===========================================================================
# 1. Independent Boundary-Free Character Onset/Coda Segmenter (Seg_Affix2)
# ===========================================================================
class SegAffix2:
    """Independent non-SlotSegmenter segmentation model fitted strictly on training tokens.
    Selects frequent 1-2 character onsets and 1-2 character codas by raw token frequency
    (>= min_share of training tokens of length >= 4, without SlotSegmenter's branching-entropy
    threshold), and strips at most one onset (longest match 2 then 1) and one coda (longest
    match 2 then 1) provided at least 1 core character remains."""

    def __init__(self, tokens: list[str], min_share: float = 0.025):
        freq = Counter(tokens)
        n_elig = max(1, sum(c for w, c in freq.items() if len(w) >= 4))
        onset_cnt: Counter = Counter()
        coda_cnt: Counter = Counter()
        for w, c in freq.items():
            if len(w) >= 4:
                onset_cnt[w[:1]] += c
                onset_cnt[w[:2]] += c
                coda_cnt[w[-1:]] += c
                coda_cnt[w[-2:]] += c
        self.prefix_stats = {
            u: (cnt / n_elig, 1.0) for u, cnt in onset_cnt.items() if cnt / n_elig >= min_share
        }
        self.suffix_stats = {
            u: (cnt / n_elig, 1.0) for u, cnt in coda_cnt.items() if cnt / n_elig >= min_share
        }
        self.prefixes = sorted(self.prefix_stats.keys(), key=lambda x: (-len(x), x))
        self.suffixes = sorted(self.suffix_stats.keys(), key=lambda x: (-len(x), x))
        self._p2 = {u for u in self.prefixes if len(u) == 2}
        self._p1 = {u for u in self.prefixes if len(u) == 1}
        self._s2 = {u for u in self.suffixes if len(u) == 2}
        self._s1 = {u for u in self.suffixes if len(u) == 1}
        self._cache: dict[str, tuple[str, str, str]] = {}

    def segment(self, w: str) -> tuple[str, str, str]:
        res = self._cache.get(w)
        if res is not None:
            return res
        p = ""
        rem = w
        if len(rem) >= 4 and rem[:2] in self._p2:
            p = rem[:2]
            rem = rem[2:]
        elif len(rem) >= 3 and rem[:1] in self._p1:
            p = rem[:1]
            rem = rem[1:]
        s = ""
        if len(rem) >= 3 and rem[-2:] in self._s2:
            s = rem[-2:]
            rem = rem[:-2]
        elif len(rem) >= 2 and rem[-1:] in self._s1:
            s = rem[-1:]
            rem = rem[:-1]
        res = (p, rem, s)
        self._cache[w] = res
        return res


# ===========================================================================
# 2. Metadata, Codicological Bifolios ($Q|$B and $Q|$F), & Raw IVTFF Commas
# ===========================================================================
def folio_leaf_key(pid: str) -> str:
    m = re.match(r"^f(\d+)[rv](\d*)$", pid)
    if not m:
        return pid
    return f"f{int(m.group(1))}"


def load_codicology_and_inventory() -> dict[str, dict[str, str]]:
    inv_path = ROOT / "data" / "folio_evidence_inventory.tsv"
    inv: dict[str, dict[str, str]] = {}
    if inv_path.exists():
        lines = inv_path.read_text(encoding="utf-8").splitlines()
        if lines:
            headers = lines[0].split("\t")
            for ln in lines[1:]:
                if not ln.strip():
                    continue
                row = dict(zip(headers, ln.split("\t")))
                f = row["folio"]
                h_raw = row.get("hand", "?")
                q_raw = row.get("quire", "?")
                f_slot = row.get("bifolio", "?")
                davis_h = h_raw if h_raw in {"1", "2", "3", "4", "5"} else (
                    "3" if q_raw == "T" or f == "f115r" else h_raw
                )
                inv[f] = dict(
                    header_hand=h_raw,
                    davis_hand=davis_h,
                    lang=row.get("lang", "?"),
                    section=row.get("section", "?"),
                    quire=q_raw,
                    f_slot=f_slot,
                    b_sheet="?",
                    leaf=folio_leaf_key(f),
                )
    # Extract exact $B (physical bifolio sheet within quire) and $F from ZL3b-n.txt headers
    zl_path = ROOT / "data" / "ZL3b-n.txt"
    if zl_path.exists():
        for raw in zl_path.read_text(encoding="ascii", errors="replace").splitlines():
            m = vparse.PAGE_RE.match(raw)
            if not m:
                continue
            pid = m.group(1)
            meta = dict(vparse.VAR_RE.findall(m.group(2)))
            if pid not in inv:
                q_raw = meta.get("Q", "?")
                h_raw = meta.get("H", "?")
                inv[pid] = dict(
                    header_hand=h_raw,
                    davis_hand=h_raw if h_raw in {"1", "2", "3", "4", "5"} else ("3" if q_raw == "T" else h_raw),
                    lang=meta.get("L", "?"),
                    section=meta.get("I", "?"),
                    quire=q_raw,
                    f_slot=meta.get("F", "?"),
                    b_sheet=meta.get("B", "?"),
                    leaf=folio_leaf_key(pid),
                )
            else:
                inv[pid]["b_sheet"] = meta.get("B", inv[pid].get("b_sheet", "?"))
                if inv[pid]["f_slot"] == "?":
                    inv[pid]["f_slot"] = meta.get("F", "?")
    return inv


def load_meta_pages(meta_name: str, inv: dict[str, dict[str, str]]) -> list[dict]:
    d = json.loads((ROOT / "data" / "translit" / meta_name).read_text(encoding="utf-8"))
    pages = []
    for p in d["pages"]:
        pid = str(p["id"])
        lines = [[str(w) for w in ln if w] for ln in p["lines"]]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue
        info = inv.get(pid, {})
        h_hdr = str(p.get("hand", info.get("header_hand", "?")))
        q_str = str(p.get("quire", info.get("quire", "?")))
        davis_h = h_hdr if h_hdr in {"1", "2", "3", "4", "5"} else (
            info.get("davis_hand", "3") if (q_str == "T" or pid == "f115r") else h_hdr
        )
        b_sh = info.get("b_sheet", "?")
        f_sl = info.get("f_slot", "?")
        leaf = info.get("leaf", folio_leaf_key(pid))
        pages.append(dict(
            id=pid,
            header_hand=h_hdr,
            hand=davis_h,
            lang=str(p.get("lang", info.get("lang", "?"))),
            section=str(p.get("section", info.get("section", "?"))),
            quire=q_str,
            bifolio=f"{q_str}|{b_sh}",
            folio_slot=f"{q_str}|{f_sl}",
            leaf=f"{q_str}|{leaf}",
            lines=lines,
        ))
    return pages


def parse_raw_ivtff_with_commas(ivtff_path: Path, inv: dict[str, dict[str, str]]) -> dict:
    """Parses a raw IVTFF file (P* paragraph lines), returning:
      - split_pages: list of page dicts where ',' and '.' both split words (standard tokenization)
      - u1_pages   : list of page dicts where '.' splits words and ',' is joined (U1 tokenization),
                     plus u1_comma_offsets_lines parallel to lines giving frozenset of internal
                     character offsets where raw ',' stood inside each U1 token!
      - line_map   : dict (pid, line_no) -> dict(split_words, u1_words, u1_comma_offs)
                     for exact cross-transliteration alignment."""
    meta: dict[str, str] = {}
    by_page_split: OrderedDict[str, list[list[str]]] = OrderedDict()
    by_page_u1: OrderedDict[str, list[list[str]]] = OrderedDict()
    by_page_u1_offs: OrderedDict[str, list[list[frozenset[int]]]] = OrderedDict()
    by_page_lno: OrderedDict[str, list[int]] = OrderedDict()
    page_meta_map: dict[str, dict[str, str]] = {}
    line_map: dict[tuple[str, int], dict] = {}

    for raw in ivtff_path.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        mp = vparse.PAGE_RE.match(raw)
        if mp:
            meta = dict(vparse.VAR_RE.findall(mp.group(2)))
            meta["page"] = mp.group(1)
            page_meta_map[mp.group(1)] = dict(meta)
            continue
        ml = vparse.LINE_RE.match(raw)
        if not ml:
            continue
        page, lno_s, _, unit, text = ml.groups()
        if not unit.startswith("P"):
            continue
        lno = int(lno_s)

        # Clean inline tags matching vparse.clean, preserving '.' and ','
        t = re.sub(r"<![^>]*>", "", text)
        t = re.sub(r"<->", ".", t)
        t = re.sub(r"<[^>]*>", "", t)
        t = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", t)
        t = re.sub(r"@\d+;", "?", t)
        t = t.replace("{", "").replace("}", "").replace("'", "")

        # Standard split words (both '.' and ',' break words; drop tokens with '?' or non-[a-z])
        raw_split = [w for w in t.replace(",", ".").split(".") if w]
        clean_split = [w for w in raw_split if "?" not in w and w.isalpha()]

        # U1 comma-joined words: split on '.', keep ',' offsets inside each piece
        u1_words: list[str] = []
        u1_offs: list[frozenset[int]] = []
        for chunk in t.split("."):
            if not chunk:
                continue
            subparts = [sp for sp in chunk.split(",") if sp]
            if not subparts:
                continue
            joined = "".join(subparts)
            if "?" in joined or not joined.isalpha():
                continue
            offs: set[int] = set()
            acc = 0
            for sp in subparts[:-1]:
                acc += len(sp)
                offs.add(acc)
            u1_words.append(joined)
            u1_offs.append(frozenset(offs))

        if clean_split:
            by_page_split.setdefault(page, []).append(clean_split)
            by_page_lno.setdefault(page, []).append(lno)
        if u1_words:
            by_page_u1.setdefault(page, []).append(u1_words)
            by_page_u1_offs.setdefault(page, []).append(u1_offs)
        line_map[(page, lno)] = dict(
            split_words=clean_split,
            u1_words=u1_words,
            u1_offs=u1_offs,
        )

    def make_page_list(by_lines: OrderedDict, by_offs: OrderedDict | None = None) -> list[dict]:
        out = []
        for pid, lines in by_lines.items():
            info = inv.get(pid, {})
            pm = page_meta_map.get(pid, {})
            q_str = info.get("quire", pm.get("Q", "?"))
            h_hdr = info.get("header_hand", pm.get("H", "?"))
            davis_h = info.get("davis_hand", h_hdr if h_hdr in {"1", "2", "3", "4", "5"} else ("3" if q_str == "T" else h_hdr))
            b_sh = info.get("b_sheet", pm.get("B", "?"))
            f_sl = info.get("f_slot", pm.get("F", "?"))
            leaf = info.get("leaf", folio_leaf_key(pid))
            rec = dict(
                id=pid,
                header_hand=h_hdr,
                hand=davis_h,
                lang=info.get("lang", pm.get("L", "?")),
                section=info.get("section", pm.get("I", "?")),
                quire=q_str,
                bifolio=f"{q_str}|{b_sh}",
                folio_slot=f"{q_str}|{f_sl}",
                leaf=f"{q_str}|{leaf}",
                lines=lines,
                line_nos=by_page_lno.get(pid, list(range(1, len(lines) + 1))),
            )
            if by_offs is not None:
                rec["comma_offs"] = by_offs[pid]
            out.append(rec)
        return out

    return dict(
        split_pages=make_page_list(by_page_split),
        u1_pages=make_page_list(by_page_u1, by_page_u1_offs),
        line_map=line_map,
    )


# ===========================================================================
# 3. Load s47 Physical Intra-Word Ink-Gap Measurements Mapped to Char Offsets
# ===========================================================================
def load_s47_char_gap_map() -> dict[tuple[str, int, int, int], tuple[int, float | None]]:
    """Maps (page, line_no, word_idx_in_split_line, char_offset_in_word) -> (ink_call, r_norm)
    and also (page, line_no, -1, inter_word_idx) -> (ink_call, r_norm) for comma/space positions,
    using runs/s47/positions.tsv + runs/s45/pages/<id>.json + data/ZL3b-n.txt (zero image loading)."""
    pos_tsv = ROOT / "runs" / "s47" / "positions.tsv"
    s45_dir = ROOT / "runs" / "s45"
    zl_path = ROOT / "data" / "ZL3b-n.txt"
    seg_py = ROOT / "tools" / "segment_scans.py"
    if not (pos_tsv.exists() and s45_dir.exists() and zl_path.exists() and seg_py.exists()):
        return {}

    spec = importlib.util.spec_from_file_location("seg_scans_s77", seg_py)
    seg_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seg_mod)
    az_re = re.compile(r"[a-z]+")

    # Group positions.tsv rows by (page, line_no)
    pos_by_line: dict[tuple[str, int], list[tuple[str, int, float | None]]] = defaultdict(list)
    for ln in pos_tsv.read_text(encoding="utf-8").splitlines()[1:]:
        if not ln.strip():
            continue
        parts = ln.split("\t")
        pid = parts[0]
        lno = int(parts[1])
        cls = parts[2]
        ink_c = int(parts[3])
        w_px = float(parts[4]) if parts[4] != "" else None
        thr = float(parts[5])
        r_val = (w_px / thr) if (w_px is not None and thr > 0) else None
        pos_by_line[(pid, lno)].append((cls, ink_c, r_val))

    # Parse ZL3b-n.txt with separators exactly as s47_ink_space_agreement.py
    def clean_seps(text: str):
        text = re.sub(r"<![^>]*>", "", text)
        text = re.sub(r"<->", "|", text)
        text = re.sub(r"<[^>]*>", "", text)
        text = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", text)
        text = re.sub(r"@\d+;", "?", text)
        text = text.replace("{", "").replace("}", "").replace("'", "")
        parts = re.split(r"([.,|])", text)
        words, seps, pend = [], [], ""
        for p in parts:
            if p in (".", ",", "|"):
                pend += p
            elif p:
                if words:
                    seps.append("I" if "|" in pend else ("D" if "." in pend else "C"))
                words.append(p)
                pend = ""
        return words, seps

    seps_of: dict[tuple[str, int], tuple[list[str], list[str]]] = {}
    for raw in zl_path.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip() or vparse.PAGE_RE.match(raw):
            continue
        m = vparse.LINE_RE.match(raw)
        if not m:
            continue
        pg, n_s, _, unit, text = m.groups()
        if not unit.startswith("P"):
            continue
        w, s = clean_seps(text)
        seps_of[(pg, int(n_s))] = (w, s)

    zmap = {p["id"]: p for p in seg_mod.zl_pages()}
    summ = json.loads((s45_dir / "segment_summary.json").read_text(encoding="utf-8"))
    clean_ids = summ["clean_ids"]

    out_map: dict[tuple[str, int, int, int], tuple[int, float | None]] = {}

    for pid in clean_ids:
        pj_path = s45_dir / "pages" / f"{pid}.json"
        if not pj_path.exists() or pid not in zmap:
            continue
        pj = json.loads(pj_path.read_text(encoding="utf-8"))
        loci = zmap[pid]["loci"]
        ri = 0
        for ar in pj["alignment"]:
            nent = len(ar["loci"]) if ar["op"] == "miss" else len(ar["det"])
            ents = pj["reseg_lines"][ri:ri + nent]
            ri += nent
            if ar["op"] != "1:1" or len(ar["det"]) != 1 or len(ar["loci"]) != 1:
                continue
            line = pj["lines"][ar["det"][0]]
            loc = loci[ar["loci"][0]]
            lno = int(loc["line"])
            if (pid, lno) not in pos_by_line or (pid, lno) not in seps_of:
                continue
            words, seps = seps_of[(pid, lno)]
            ink = line["tokens"]
            if len(ink) == len(words):
                groups = [((k, k + 1), (k, k + 1)) for k in range(len(words))]
            else:
                widths = [float(t["w"]) for t in ink]
                chars = [float(len(seg_mod.glyphs(w))) for w in words]
                ppc = sum(widths) / max(sum(chars), 1.0)
                a = [w / ppc for w in widths]
                P = seg_mod.PARAMS["dp_word"]
                groups, _ = seg_mod.align(a, chars, P["skip"], P["merge_pen"], P["max_group"])
            new = seg_mod.resegment_line(ink, words)[0]
            if [e["tokens"] for e in ents] != [new]:
                continue

            # Trace emitted positions in exact lockstep with s47 line_positions
            gl = [seg_mod.glyphs(w) for w in words]
            # Map from clean_split word index (which drops '?' tokens) to raw words index j
            raw_to_clean_idx: dict[int, int] = {}
            c_idx = 0
            all_clean = True
            for j_raw, w_raw in enumerate(words):
                if "?" not in w_raw and w_raw.isalpha():
                    raw_to_clean_idx[j_raw] = c_idx
                    c_idx += 1
                else:
                    all_clean = False
            word_start_char = [0] * (len(words) + 1)
            for j_raw, w_raw in enumerate(words):
                word_start_char[j_raw + 1] = word_start_char[j_raw] + len(w_raw)

            emitted_keys: list[tuple[int, int, str, int]] = []  # (clean_word_idx or -1, char_off or raw_j, cls, line_char_off)

            def record_emit(lg: str, rg: str, cls_s: str, w_j: int, char_off: int, l_off: int) -> None:
                if cls_s == "I":
                    return
                if not (az_re.fullmatch(lg) and az_re.fullmatch(rg)):
                    return
                emitted_keys.append((w_j, char_off, cls_s, l_off))

            mapped = [(gi, g) for gi, g in enumerate(groups) if g[0][1] > g[0][0] and g[1][1] > g[1][0]]
            for gi, ((i0, i1), (j0, j1)) in mapped:
                ni, nj = i1 - i0, j1 - j0
                if ni == 1:
                    for j in range(j0, j1):
                        if j > j0:
                            record_emit(gl[j - 1][-1], gl[j][0], seps[j - 1], -1, j - 1, word_start_char[j])
                        acc_ch = 0
                        for k, g_str in enumerate(gl[j]):
                            if k > 0:
                                record_emit(gl[j][k - 1], g_str, "N", raw_to_clean_idx.get(j, -2), acc_ch, word_start_char[j] + acc_ch)
                            acc_ch += len(g_str)
                else:
                    g = gl[j0]
                    toks = ink[i0:i1]
                    ws = [t["w"] for t in toks]
                    tot = sum(ws)
                    fr = (np.cumsum(ws)[:-1] / tot).tolist()
                    pieces = seg_mod.split_token(words[j0], fr)
                    if pieces is None:
                        continue
                    s_g = 0
                    acc_ch = 0
                    c_j = raw_to_clean_idx.get(j0, -2)
                    for k_p, pc in enumerate(pieces):
                        pg = seg_mod.glyphs(pc)
                        for k_in, g_str in enumerate(pg):
                            if k_in > 0:
                                record_emit(pg[k_in - 1], g_str, "N", c_j, acc_ch, word_start_char[j0] + acc_ch)
                            acc_ch += len(g_str)
                        s_g += len(pg)
                        if k_p < len(pieces) - 1:
                            record_emit(g[s_g - 1], g[s_g], "N", c_j, acc_ch, word_start_char[j0] + acc_ch)
                if gi + 1 < len(groups):
                    (ni0, ni1), (nj0, nj1) = groups[gi + 1]
                    if ni1 > ni0 and nj1 > nj0:
                        record_emit(gl[j1 - 1][-1], gl[nj0][0], seps[j1 - 1], -1, j1 - 1, word_start_char[nj0])

            stored_rows = pos_by_line[(pid, lno)]
            if len(emitted_keys) == len(stored_rows):
                for (w_j, char_off, cls_s, l_off), (cls_r, ink_c, r_val) in zip(emitted_keys, stored_rows):
                    if cls_s == cls_r and w_j >= -1:
                        out_map[(pid, lno, w_j, char_off)] = (ink_c, r_val)
                        if all_clean and l_off > 0:
                            out_map[(pid, lno, -10, l_off)] = (ink_c, r_val)

    return out_map


# ===========================================================================
# 4. Part 1: Slot Annotation & Fast Counted Witten-Bell Slot Models
# ===========================================================================
def line_pos_label(idx: int, line_len: int, is_para_start: bool = False) -> str:
    if idx == 0:
        return "para_0" if is_para_start else "line_0"
    if idx == line_len - 1:
        return "line_final"
    return "interior"


def annotate_pages_with_seg(pages: list[dict], seg) -> list[dict]:
    out = []
    for p in pages:
        ann_lines = []
        for l_idx, ln in enumerate(p["lines"]):
            L = len(ln)
            pcs = [seg.segment(w) for w in ln]
            dom_p = "<NONE>"
            recs = []
            for i, (w, (pre, core, suf)) in enumerate(zip(ln, pcs)):
                pos = line_pos_label(i, L, is_para_start=(l_idx == 0))
                p_sym = pre if pre else EMPTY
                s_sym = suf if suf else EMPTY
                c_sym = core if core else EMPTY
                s_prev = (pcs[i - 1][2] or EMPTY) if i > 0 else "<BOS>"
                p_prev = (pcs[i - 1][0] or EMPTY) if i > 0 else "<BOS>"
                state = (p_prev, dom_p)
                recs.append(dict(
                    w=w, pre=pre, core=core, suf=suf,
                    P=p_sym, C=c_sym, S=s_sym, F=(p_sym, s_sym),
                    pos=pos, s_prev=s_prev, p_prev=p_prev, state=state,
                ))
                if pre:
                    dom_p = pre
            ann_lines.append(recs)
        out.append(dict(p, ann_lines=ann_lines))
    return out


class FastSlotScorer:
    """Counted Witten-Bell slot model fitted strictly on a training page subset.
    Supports both core-conditioned P(P_t, S_t | C_t, pos_t, S_{t-1}, state) and
    core-blind P(P_t, S_t | pos_t, S_{t-1}, state) frame cross-entropy."""

    def __init__(self, train_ann_pages: list[dict], vocab_P: list[str], vocab_S: list[str]):
        self.p2i = {v: i for i, v in enumerate(vocab_P)}
        self.s2i = {v: i for i, v in enumerate(vocab_S)}
        self.V_P = max(len(vocab_P), 1)
        self.V_S = max(len(vocab_S), 1)

        self.uni_P = Counter()
        self.uni_S = Counter()
        self.N = 0

        self.p_pos = defaultdict(Counter)
        self.p_pos_s = defaultdict(Counter)
        self.p_pos_s_p = defaultdict(Counter)
        self.p_c = defaultdict(Counter)
        self.p_c_pos = defaultdict(Counter)

        self.s_pos = defaultdict(Counter)
        self.s_pos_p = defaultdict(Counter)
        self.s_pos_p_s = defaultdict(Counter)
        self.s_c = defaultdict(Counter)
        self.s_c_pos_p = defaultdict(Counter)

        for p in train_ann_pages:
            for ln in p["ann_lines"]:
                for r in ln:
                    P, C, S = r["P"], r["C"], r["S"]
                    pos, s_prev, p_prev = r["pos"], r["s_prev"], r["p_prev"]
                    self.uni_P[P] += 1
                    self.uni_S[S] += 1
                    self.N += 1

                    self.p_pos[pos][P] += 1
                    self.p_pos_s[(pos, s_prev)][P] += 1
                    self.p_pos_s_p[(pos, s_prev, p_prev)][P] += 1
                    self.p_c[C][P] += 1
                    self.p_c_pos[(C, pos)][P] += 1

                    self.s_pos[pos][S] += 1
                    self.s_pos_p[(pos, P)][S] += 1
                    self.s_pos_p_s[(pos, P, s_prev)][S] += 1
                    self.s_c[C][S] += 1
                    self.s_c_pos_p[(C, pos, P)][S] += 1

        self.st_p_pos = {k: (sum(c.values()), len(c), c) for k, c in self.p_pos.items()}
        self.st_p_pos_s = {k: (sum(c.values()), len(c), c) for k, c in self.p_pos_s.items()}
        self.st_p_pos_s_p = {k: (sum(c.values()), len(c), c) for k, c in self.p_pos_s_p.items()}
        self.st_p_c = {k: (sum(c.values()), len(c), c) for k, c in self.p_c.items()}
        self.st_p_c_pos = {k: (sum(c.values()), len(c), c) for k, c in self.p_c_pos.items()}

        self.st_s_pos = {k: (sum(c.values()), len(c), c) for k, c in self.s_pos.items()}
        self.st_s_pos_p = {k: (sum(c.values()), len(c), c) for k, c in self.s_pos_p.items()}
        self.st_s_pos_p_s = {k: (sum(c.values()), len(c), c) for k, c in self.s_pos_p_s.items()}
        self.st_s_c = {k: (sum(c.values()), len(c), c) for k, c in self.s_c.items()}
        self.st_s_c_pos_p = {k: (sum(c.values()), len(c), c) for k, c in self.s_c_pos_p.items()}

        self.denom_P = max(self.N, 1) + 0.5 * (self.V_P + 1)
        self.denom_S = max(self.N, 1) + 0.5 * (self.V_S + 1)

    @staticmethod
    def _wb(st_dict: dict, key, outcome: str, back_p: float) -> float:
        st = st_dict.get(key)
        if st is None:
            return back_p
        n, T, cnt = st
        return (cnt.get(outcome, 0) + T * back_p) / (n + T)

    def prob_token(self, r: dict, blind: bool = False) -> float:
        P, C, S = r["P"], r["C"], r["S"]
        pos, s_prev, p_prev = r["pos"], r["s_prev"], r["p_prev"]

        p = (self.uni_P.get(P, 0) + 0.5) / self.denom_P
        p = self._wb(self.st_p_pos, pos, P, p)
        p = self._wb(self.st_p_pos_s, (pos, s_prev), P, p)
        p = self._wb(self.st_p_pos_s_p, (pos, s_prev, p_prev), P, p)
        if not blind:
            p = self._wb(self.st_p_c, C, P, p)
            p = self._wb(self.st_p_c_pos, (C, pos), P, p)

        q = (self.uni_S.get(S, 0) + 0.5) / self.denom_S
        q = self._wb(self.st_s_pos, pos, S, q)
        q = self._wb(self.st_s_pos_p, (pos, P), S, q)
        q = self._wb(self.st_s_pos_p_s, (pos, P, s_prev), S, q)
        if not blind:
            q = self._wb(self.st_s_c, C, S, q)
            q = self._wb(self.st_s_c_pos_p, (C, pos, P), S, q)

        return max(p * q, 1e-15)

    def score_pages(self, pages: list[dict], core_filter: set[str] | None = None, blind: bool = False) -> tuple[float, int]:
        bits = 0.0
        n = 0
        for p in pages:
            for ln in p["ann_lines"]:
                for r in ln:
                    if core_filter is not None and r["C"] not in core_filter:
                        continue
                    bits -= math.log2(self.prob_token(r, blind=blind))
                    n += 1
        return bits, n


def get_shared_top50_cores(pages_a: list[dict], pages_b: list[dict]) -> set[str]:
    ca = Counter(r["C"] for p in pages_a for ln in p["ann_lines"] for r in ln)
    cb = Counter(r["C"] for p in pages_b for ln in p["ann_lines"] for r in ln)
    shared = set(ca.keys()) & set(cb.keys())
    if len(shared) < 50:
        combined = ca + cb
        return {c for c, _ in combined.most_common(50)}
    ranked = sorted(shared, key=lambda c: (-min(ca[c], cb[c]), -(ca[c] + cb[c]), c))
    return set(ranked[:50])


def evaluate_nested_folds(
    cohort_pages: list[dict],
    group_key: str,
    hand_a_pred,
    hand_b_pred,
    seg_cls,
) -> dict:
    """Runs clean nested cross-validation holding out one group_key (e.g. 'leaf', 'bifolio', 'quire')
    at a time. On EVERY fold:
      1. Fits seg_cls strictly on the training fold tokens.
      2. Annotates training and held-out pages using ONLY that fold's fitted segmenter.
      3. Identifies top-50 shared cores strictly on the training fold.
      4. Fits FastSlotScorer for Hand A and Hand B strictly on the training fold.
      5. Accumulates held-out cross-entropy bits on held-out Hand A and Hand B pages across:
         - all tokens (core-conditioned)
         - top-50 shared training cores (C_top50)
         - core-blind slot transitions (blind=True)."""
    groups = sorted({p[group_key] for p in cohort_pages})
    # accumulators: [bits_own, bits_other, n_tok] for Hand A and Hand B across 3 modes
    acc = {
        mode: {"A_own": 0.0, "A_oth": 0.0, "A_n": 0, "B_own": 0.0, "B_oth": 0.0, "B_n": 0}
        for mode in ("all", "top50", "blind")
    }
    per_page_diffs = {mode: [] for mode in ("all", "top50", "blind")}  # (pid, hand_ab, diff_bits, n_tok)

    for g_val in groups:
        tr_raw = [p for p in cohort_pages if p[group_key] != g_val]
        te_raw = [p for p in cohort_pages if p[group_key] == g_val]
        if not tr_raw or not te_raw:
            continue
        tr_a_raw = [p for p in tr_raw if hand_a_pred(p)]
        tr_b_raw = [p for p in tr_raw if hand_b_pred(p)]
        if not tr_a_raw or not tr_b_raw:
            continue

        tr_words = [w for p in tr_raw for ln in p["lines"] for w in ln]
        seg_fold = seg_cls(tr_words)
        tr_ann = annotate_pages_with_seg(tr_raw, seg_fold)
        te_ann = annotate_pages_with_seg(te_raw, seg_fold)

        vocab_P = sorted({r["P"] for p in tr_ann for ln in p["ann_lines"] for r in ln} | {EMPTY})
        vocab_S = sorted({r["S"] for p in tr_ann for ln in p["ann_lines"] for r in ln} | {EMPTY})

        tr_a = [p for p in tr_ann if hand_a_pred(p)]
        tr_b = [p for p in tr_ann if hand_b_pred(p)]
        top50 = get_shared_top50_cores(tr_a, tr_b)

        mod_a = FastSlotScorer(tr_a, vocab_P, vocab_S)
        mod_b = FastSlotScorer(tr_b, vocab_P, vocab_S)

        for p_te in te_ann:
            is_a = hand_a_pred(p_te)
            is_b = hand_b_pred(p_te)
            if not (is_a or is_b):
                continue
            for mode, c_flt, is_blind in (
                ("all", None, False),
                ("top50", top50, False),
                ("blind", None, True),
            ):
                ba, na = mod_a.score_pages([p_te], core_filter=c_flt, blind=is_blind)
                bb, _ = mod_b.score_pages([p_te], core_filter=c_flt, blind=is_blind)
                if is_a:
                    acc[mode]["A_own"] += ba
                    acc[mode]["A_oth"] += bb
                    acc[mode]["A_n"] += na
                    per_page_diffs[mode].append((p_te["id"], "A", bb - ba, na))
                elif is_b:
                    acc[mode]["B_own"] += bb
                    acc[mode]["B_oth"] += ba
                    acc[mode]["B_n"] += na
                    per_page_diffs[mode].append((p_te["id"], "B", ba - bb, na))

    out = {}
    for mode in ("all", "top50", "blind"):
        d = acc[mode]
        na = max(d["A_n"], 1)
        nb = max(d["B_n"], 1)
        dh_b_to_a = (d["A_oth"] - d["A_own"]) / na
        dh_a_to_b = (d["B_oth"] - d["B_own"]) / nb
        dsym = 0.5 * (dh_b_to_a + dh_a_to_b)
        p_correct = sum(1 for _, _, diff_b, nt in per_page_diffs[mode] if nt > 0 and diff_b > 0)
        p_total = sum(1 for _, _, _, nt in per_page_diffs[mode] if nt > 0)
        out[mode] = dict(
            dh_b_to_a=dh_b_to_a,
            dh_a_to_b=dh_a_to_b,
            dsym=dsym,
            n_tok_a=d["A_n"],
            n_tok_b=d["B_n"],
            page_acc=p_correct / max(p_total, 1),
            page_correct=p_correct,
            page_total=p_total,
            per_page_diffs=per_page_diffs[mode],
        )
    return out


def fast_lobo_permutation_nulls(
    cohort_pages: list[dict],
    hand_a_ids: set[str],
    hand_b_ids: set[str],
    seg_cls,
    n_perm: int = N_PERM,
) -> dict:
    """Evaluates Leave-One-Leaf-Out (LOLO / LOBO) D_sym(A, B) on cohort_pages and computes
    three stratified permutation nulls:
      - Null P1: Page-level label permutation within cohort_pages
      - Null P2_leaf: Folio-leaf ($Q|$F) block permutation within cohort_pages
      - Null P2_bif : Physical bifolio-sheet ($Q|$B) block permutation within cohort_pages
      - Null P3_quire: Quire-level ($Q) block permutation within cohort_pages."""
    # Precompute per-leaf nested segmentation & per-page encoded token lists for speed:
    # Note that segmenter fitting depends ONLY on the unlabeled training fold tokens!
    leaves = sorted({p["leaf"] for p in cohort_pages})
    fold_encoded: list[tuple[list[dict], list[dict]]] = []

    for lf in leaves:
        tr_raw = [p for p in cohort_pages if p["leaf"] != lf]
        te_raw = [p for p in cohort_pages if p["leaf"] == lf]
        if not tr_raw or not te_raw:
            continue
        seg_f = seg_cls([w for p in tr_raw for ln in p["lines"] for w in ln])
        tr_ann = annotate_pages_with_seg(tr_raw, seg_f)
        te_ann = annotate_pages_with_seg(te_raw, seg_f)
        vocab_P = sorted({r["P"] for p in tr_ann + te_ann for ln in p["ann_lines"] for r in ln} | {EMPTY})
        vocab_S = sorted({r["S"] for p in tr_ann + te_ann for ln in p["ann_lines"] for r in ln} | {EMPTY})
        p2i = {v: i for i, v in enumerate(vocab_P)}
        s2i = {v: i for i, v in enumerate(vocab_S)}
        V_P, V_S = len(vocab_P), len(vocab_S)
        c_cnt = Counter(r["C"] for p in tr_ann for ln in p["ann_lines"] for r in ln)
        top50 = {c for c, _ in c_cnt.most_common(50)}

        def enc_page(p: dict) -> dict:
            uP = np.zeros(V_P, dtype=np.int64)
            uS = np.zeros(V_S, dtype=np.int64)
            pos_s_P = defaultdict(Counter)
            c_P = defaultdict(Counter)
            pos_P_S = defaultdict(Counter)
            c_P_S = defaultdict(Counter)
            toks_all = []
            toks_t50 = []
            for ln in p["ann_lines"]:
                for r in ln:
                    pi = p2i[r["P"]]
                    si = s2i[r["S"]]
                    C, pos, s_prev = r["C"], r["pos"], r["s_prev"]
                    uP[pi] += 1
                    uS[si] += 1
                    pos_s_P[(pos, s_prev)][pi] += 1
                    c_P[C][pi] += 1
                    pos_P_S[(pos, pi)][si] += 1
                    c_P_S[(C, pi)][si] += 1
                    it = (pi, si, C, pos, s_prev)
                    toks_all.append(it)
                    if C in top50:
                        toks_t50.append(it)
            return dict(
                id=p["id"], uP=uP, uS=uS, n=len(toks_all),
                pos_s_P=pos_s_P, c_P=c_P, pos_P_S=pos_P_S, c_P_S=c_P_S,
                toks_all=toks_all, toks_t50=toks_t50, V_P=V_P, V_S=V_S,
            )

        fold_encoded.append(([enc_page(p) for p in tr_ann], [enc_page(p) for p in te_ann]))

    def score_assignment(a_set: set[str], b_set: set[str]) -> tuple[float, float, float]:
        ba_own_a, ba_oth_a, na_a = 0.0, 0.0, 0
        bb_own_a, bb_oth_a, nb_a = 0.0, 0.0, 0
        ba_own_t, ba_oth_t, na_t = 0.0, 0.0, 0
        bb_own_t, bb_oth_t, nb_t = 0.0, 0.0, 0
        ba_own_bl, ba_oth_bl = 0.0, 0.0
        bb_own_bl, bb_oth_bl = 0.0, 0.0

        for tr_enc, te_enc in fold_encoded:
            tr_a = [ep for ep in tr_enc if ep["id"] in a_set]
            tr_b = [ep for ep in tr_enc if ep["id"] in b_set]
            if not tr_a or not tr_b:
                continue

            def fit_fast(plist):
                V_P, V_S = plist[0]["V_P"], plist[0]["V_S"]
                uP = np.zeros(V_P, dtype=np.float64)
                uS = np.zeros(V_S, dtype=np.float64)
                N = 0
                pos_s_P = defaultdict(Counter)
                c_P = defaultdict(Counter)
                pos_P_S = defaultdict(Counter)
                c_P_S = defaultdict(Counter)
                for ep in plist:
                    uP += ep["uP"]
                    uS += ep["uS"]
                    N += ep["n"]
                    for k, cnt in ep["pos_s_P"].items():
                        pos_s_P[k].update(cnt)
                    for k, cnt in ep["c_P"].items():
                        c_P[k].update(cnt)
                    for k, cnt in ep["pos_P_S"].items():
                        pos_P_S[k].update(cnt)
                    for k, cnt in ep["c_P_S"].items():
                        c_P_S[k].update(cnt)
                pu_P = (uP + 0.5) / (max(N, 1) + 0.5 * (V_P + 1))
                pu_S = (uS + 0.5) / (max(N, 1) + 0.5 * (V_S + 1))
                st_psP = {k: (sum(c.values()), len(c), c) for k, c in pos_s_P.items()}
                st_cP = {k: (sum(c.values()), len(c), c) for k, c in c_P.items()}
                st_pPS = {k: (sum(c.values()), len(c), c) for k, c in pos_P_S.items()}
                st_cPS = {k: (sum(c.values()), len(c), c) for k, c in c_P_S.items()}

                def eval_toks(tlist, t50_list):
                    bits_all, bits_bl = 0.0, 0.0
                    for pi, si, C, pos, s_prev in tlist:
                        p = pu_P[pi]
                        s1 = st_psP.get((pos, s_prev))
                        if s1 is not None:
                            p = (s1[2].get(pi, 0) + s1[1] * p) / (s1[0] + s1[1])
                        p_bl = p
                        s2 = st_cP.get(C)
                        if s2 is not None:
                            p = (s2[2].get(pi, 0) + s2[1] * p) / (s2[0] + s2[1])

                        q = pu_S[si]
                        t1 = st_pPS.get((pos, pi))
                        if t1 is not None:
                            q = (t1[2].get(si, 0) + t1[1] * q) / (t1[0] + t1[1])
                        q_bl = q
                        t2 = st_cPS.get((C, pi))
                        if t2 is not None:
                            q = (t2[2].get(si, 0) + t2[1] * q) / (t2[0] + t2[1])

                        bits_all -= math.log2(max(p * q, 1e-15))
                        bits_bl -= math.log2(max(p_bl * q_bl, 1e-15))

                    bits_t50 = 0.0
                    for pi, si, C, pos, s_prev in t50_list:
                        p = pu_P[pi]
                        s1 = st_psP.get((pos, s_prev))
                        if s1 is not None:
                            p = (s1[2].get(pi, 0) + s1[1] * p) / (s1[0] + s1[1])
                        s2 = st_cP.get(C)
                        if s2 is not None:
                            p = (s2[2].get(pi, 0) + s2[1] * p) / (s2[0] + s2[1])
                        q = pu_S[si]
                        t1 = st_pPS.get((pos, pi))
                        if t1 is not None:
                            q = (t1[2].get(si, 0) + t1[1] * q) / (t1[0] + t1[1])
                        t2 = st_cPS.get((C, pi))
                        if t2 is not None:
                            q = (t2[2].get(si, 0) + t2[1] * q) / (t2[0] + t2[1])
                        bits_t50 -= math.log2(max(p * q, 1e-15))
                    return bits_all, len(tlist), bits_t50, len(t50_list), bits_bl

                return eval_toks

            ma = fit_fast(tr_a)
            mb = fit_fast(tr_b)
            for ep in te_enc:
                pid = ep["id"]
                if pid in a_set:
                    b_aa, n_a, b_at, n_t, b_abl = ma(ep["toks_all"], ep["toks_t50"])
                    b_ba, _, b_bt, _, b_bbl = mb(ep["toks_all"], ep["toks_t50"])
                    ba_own_a += b_aa; ba_oth_a += b_ba; na_a += n_a
                    ba_own_t += b_at; ba_oth_t += b_bt; na_t += n_t
                    ba_own_bl += b_abl; ba_oth_bl += b_bbl
                elif pid in b_set:
                    b_bb, n_b, b_bt, n_t, b_bbl = mb(ep["toks_all"], ep["toks_t50"])
                    b_ab, _, b_at, _, b_abl = ma(ep["toks_all"], ep["toks_t50"])
                    bb_own_a += b_bb; bb_oth_a += b_ab; nb_a += n_b
                    bb_own_t += b_bt; bb_oth_t += b_at; nb_t += n_t
                    bb_own_bl += b_bbl; bb_oth_bl += b_abl

        if na_a == 0 or nb_a == 0:
            return 0.0, 0.0, 0.0
        ds_all = 0.5 * ((ba_oth_a - ba_own_a) / na_a + (bb_oth_a - bb_own_a) / nb_a)
        ds_t50 = 0.5 * ((ba_oth_t - ba_own_t) / max(na_t, 1) + (bb_oth_t - bb_own_t) / max(nb_t, 1))
        ds_bl = 0.5 * ((ba_oth_bl - ba_own_bl) / na_a + (bb_oth_bl - bb_own_bl) / nb_a)
        return ds_all, ds_t50, ds_bl

    obs_all, obs_t50, obs_bl = score_assignment(hand_a_ids, hand_b_ids)

    # Null P1: Page permutation inside cohort
    all_ids = [p["id"] for p in cohort_pages if p["id"] in (hand_a_ids | hand_b_ids)]
    n_a_pages = sum(1 for pid in all_ids if pid in hand_a_ids)
    rng = random.Random(SEED)
    p1_draws = []
    for _ in range(n_perm):
        sh = list(all_ids)
        rng.shuffle(sh)
        p1_draws.append(score_assignment(set(sh[:n_a_pages]), set(sh[n_a_pages:])))

    # Helper for block permutations (exact enumeration if C(N_blocks, K_b) <= n_perm, else n_perm random draws)
    def run_block_null(block_key: str) -> tuple[list[tuple[float, float, float]], int]:
        blocks: dict[str, list[str]] = defaultdict(list)
        block_b_cnt: Counter = Counter()
        for p in cohort_pages:
            pid = p["id"]
            if pid in (hand_a_ids | hand_b_ids):
                bk = p[block_key]
                blocks[bk].append(pid)
                if pid in hand_b_ids:
                    block_b_cnt[bk] += 1
        bk_names = sorted(blocks.keys())
        k_b = sum(1 for bk in bk_names if block_b_cnt[bk] > len(blocks[bk]) / 2)
        k_b = max(1, min(len(bk_names) - 1, k_b))
        n_comb = math.comb(len(bk_names), k_b)
        draws = []
        if n_comb <= n_perm:
            for chosen_b in itertools.combinations(bk_names, k_b):
                b_set_b = set(chosen_b)
                b_ids = {pid for bk in b_set_b for pid in blocks[bk]}
                a_ids = set(all_ids) - b_ids
                draws.append(score_assignment(a_ids, b_ids))
        else:
            for _ in range(n_perm):
                sh_b = list(bk_names)
                rng.shuffle(sh_b)
                b_set_b = set(sh_b[:k_b])
                b_ids = {pid for bk in b_set_b for pid in blocks[bk]}
                a_ids = set(all_ids) - b_ids
                draws.append(score_assignment(a_ids, b_ids))
        return draws, n_comb

    p2_leaf_draws, n_comb_leaf = run_block_null("leaf")
    p2_bif_draws, n_comb_bif = run_block_null("bifolio")
    p3_quire_draws, n_comb_quire = run_block_null("quire")

    def summarize_draws(obs_val: float, vals: list[float]) -> dict:
        if not vals:
            return dict(mean=0.0, sd=0.0, z=0.0, p=1.0, n=0)
        m = float(np.mean(vals))
        s = float(np.std(vals))
        z = (obs_val - m) / max(s, 1e-9)
        p = (1 + sum(1 for x in vals if x >= obs_val - 1e-12)) / (len(vals) + 1)
        return dict(mean=m, sd=s, z=z, p=p, n=len(vals))

    out = dict(obs_all=obs_all, obs_t50=obs_t50, obs_bl=obs_bl)
    for null_name, draws, n_c in (
        ("P1_page", p1_draws, math.comb(len(all_ids), n_a_pages)),
        ("P2_leaf", p2_leaf_draws, n_comb_leaf),
        ("P2_bif", p2_bif_draws, n_comb_bif),
        ("P3_quire", p3_quire_draws, n_comb_quire),
    ):
        out[null_name] = dict(
            n_comb=n_c,
            all=summarize_draws(obs_all, [x[0] for x in draws]),
            top50=summarize_draws(obs_t50, [x[1] for x in draws]),
            blind=summarize_draws(obs_bl, [x[2] for x in draws]),
        )
    return out


def run_part1_deconfounded_scribe(tr_name: str, pages: list[dict]) -> dict:
    emit("\n================================================================================")
    emit(f"PART 1 [{tr_name}]: SECTION/QUIRE-MATCHED HERBAL-B HAND 2 vs HAND 3 TEST (L-303)")
    emit("================================================================================")

    # Define explicit Herbal-B and Quire-H page subsets
    h2_herbb_all = [p for p in pages if p["section"] == "H" and p["lang"] == "B" and p["hand"] == "2"]
    h2_herbb_efg = [p for p in h2_herbb_all if p["quire"] in {"E", "F", "G"}]
    h3_herbb_q = [p for p in pages if p["section"] == "H" and p["lang"] == "B" and p["hand"] == "3"]
    h3_herbb_qh = [p for p in pages if (p["id"] in {x["id"] for x in h3_herbb_q}) or (p["quire"] == "H" and p["hand"] == "3" and p["section"] == "H")]
    h3_ext_qh = [p for p in pages if (p["id"] in {x["id"] for x in h3_herbb_q}) or (p["quire"] == "H" and p["hand"] in {"3", "5"} and p["id"] != "f57r")]
    h5_herbb = [p for p in pages if p["section"] == "H" and p["lang"] == "B" and p["hand"] == "5"]

    emit(
        f"  Codicological Breakdown inside Section = H (Herbal) & Quire H [{tr_name}]:\n"
        f"    Hand 2 Herbal-B (Quires D,E,F,G): {len(h2_herbb_all)} pages {[p['id'] for p in h2_herbb_all]} "
        f"(bifolios={sorted({p['bifolio'] for p in h2_herbb_all})}, leaves={len({p['leaf'] for p in h2_herbb_all})})\n"
        f"    Hand 2 Herbal-B (Quires E,F,G)  : {len(h2_herbb_efg)} pages {[p['id'] for p in h2_herbb_efg]}\n"
        f"    Hand 3 Herbal-B (Quire Q strict): {len(h3_herbb_q)} pages {[p['id'] for p in h3_herbb_q]} "
        f"(bifolio={sorted({p['bifolio'] for p in h3_herbb_q})}, leaves={sorted({p['leaf'] for p in h3_herbb_q})})\n"
        f"    Hand 3 Herbal   (Quire Q + f65v): {len(h3_herbb_qh)} pages {[p['id'] for p in h3_herbb_qh]}\n"
        f"    Quire H + Quire Q Extended      : {len(h3_ext_qh)} pages {[p['id'] for p in h3_ext_qh]}\n"
        f"    Hand 5 Herbal-B (Quires F, H)   : {len(h5_herbb)} pages {[p['id'] for p in h5_herbb]}"
    )

    cohorts = [
        ("C1_Strict_HerbB (Sec=H,Lang=B: H2[20p] vs H3_Q+f65v[7p])", h2_herbb_all + h3_herbb_qh,
         {p["id"] for p in h2_herbb_all}, {p["id"] for p in h3_herbb_qh}),
        ("C1b_Strict_EFG_vs_Q (Sec=H,Lang=B: H2_EFG[16p] vs H3_Q[6p])", h2_herbb_efg + h3_herbb_q,
         {p["id"] for p in h2_herbb_efg}, {p["id"] for p in h3_herbb_q}),
        ("C2_Extended_HerbB_QuireH (H2_EFG+f55[16p] vs H3_QuireH+Q[11p])", h2_herbb_efg + h3_ext_qh,
         {p["id"] for p in h2_herbb_efg}, {p["id"] for p in h3_ext_qh}),
    ]

    part1_out = {}

    for c_label, c_pages, a_ids, b_ids in cohorts:
        emit(f"\n--- {c_label} [{tr_name}] ---")
        for seg_name, seg_cls in (("SlotSegmenter", SlotSegmenter), ("Seg_Affix2", SegAffix2)):
            lobo_leaf = evaluate_nested_folds(
                c_pages, "leaf", lambda p: p["id"] in a_ids, lambda p: p["id"] in b_ids, seg_cls
            )
            lobo_bif = evaluate_nested_folds(
                c_pages, "bifolio", lambda p: p["id"] in a_ids, lambda p: p["id"] in b_ids, seg_cls
            )
            loqo_res = evaluate_nested_folds(
                c_pages, "quire", lambda p: p["id"] in a_ids, lambda p: p["id"] in b_ids, seg_cls
            )
            emit(
                f"  [{seg_name:13s}] Nested LOLO/Leaf-Out  : "
                f"D_sym(all)={lobo_leaf['all']['dsym']:+.4f} (H3->H2={lobo_leaf['all']['dh_b_to_a']:+.4f}, H2->H3={lobo_leaf['all']['dh_a_to_b']:+.4f}, acc={lobo_leaf['all']['page_correct']}/{lobo_leaf['all']['page_total']}) | "
                f"D_sym(C_top50)={lobo_leaf['top50']['dsym']:+.4f} | D_sym(blind)={lobo_leaf['blind']['dsym']:+.4f}"
            )
            emit(
                f"  [{seg_name:13s}] Nested LOBO ($Q|$B)   : "
                f"D_sym(all)={lobo_bif['all']['dsym']:+.4f} (acc={lobo_bif['all']['page_correct']}/{lobo_bif['all']['page_total']}) | "
                f"D_sym(C_top50)={lobo_bif['top50']['dsym']:+.4f} | D_sym(blind)={lobo_bif['blind']['dsym']:+.4f}"
            )
            if loqo_res["all"]["n_tok_a"] > 0 and loqo_res["all"]["n_tok_b"] > 0:
                emit(
                    f"  [{seg_name:13s}] Nested LOQO ($Q)      : "
                    f"D_sym(all)={loqo_res['all']['dsym']:+.4f} (H3->H2={loqo_res['all']['dh_b_to_a']:+.4f}, H2->H3={loqo_res['all']['dh_a_to_b']:+.4f}, acc={loqo_res['all']['page_correct']}/{loqo_res['all']['page_total']}) | "
                    f"D_sym(C_top50)={loqo_res['top50']['dsym']:+.4f} | D_sym(blind)={loqo_res['blind']['dsym']:+.4f}"
                )

            if seg_name == "SlotSegmenter":
                pnulls = fast_lobo_permutation_nulls(c_pages, a_ids, b_ids, seg_cls, n_perm=N_PERM)
                part1_out[c_label] = dict(lobo_leaf=lobo_leaf, lobo_bif=lobo_bif, loqo=loqo_res, pnulls=pnulls)
                for n_key, n_title in (
                    ("P1_page", "Null P1 (Within-Herbal-B Page Perm)"),
                    ("P2_leaf", "Null P2a (Within-Herbal-B Leaf $Q|$F Block)"),
                    ("P2_bif", "Null P2b (Within-Herbal-B Bifolio $Q|$B Block)"),
                    ("P3_quire", "Null P3 (Within-Herbal-B Quire $Q Block)"),
                ):
                    nr = pnulls[n_key]
                    emit(
                        f"    {n_title:44s} [n_comb={nr['n_comb']:6d}, draws={nr['all']['n']:3d}]: "
                        f"all null={nr['all']['mean']:+.4f}+/-{nr['all']['sd']:.4f} (z={nr['all']['z']:+.2f}, p={nr['all']['p']:.4f}) | "
                        f"C_top50 p={nr['top50']['p']:.4f} (z={nr['top50']['z']:+.2f}) | "
                        f"blind p={nr['blind']['p']:.4f} (z={nr['blind']['z']:+.2f})"
                    )

    # 1B. Direct Intra-Quire Contrasts (Quire H & Quire F) + Out-of-Section Cross-Projection Test
    emit(f"\n--- 1B. Direct Intra-Quire Contrasts (Quire H & Quire F) & Out-of-Section Cross-Projection [{tr_name}] ---")
    # Out-of-Section Cross-Projection: Fit SlotSegmenter + H2 model on Quire M (Bio, Sec=B, Hand=2)
    # and H3 model on Quire T (Stars, Sec=S, Hand=3) — ZERO Herbal-B pages in training!
    # Then evaluate on untouched Herbal-B Hand 2 (Quires D,E,F,G) vs Hand 3 (Quire Q + f65v) AND inside Quire H!
    qm_h2 = [p for p in pages if p["quire"] == "M" and p["hand"] == "2"]
    qt_h3 = [p for p in pages if p["quire"] == "T" and p["hand"] == "3"]
    seg_mt = SlotSegmenter([w for p in qm_h2 + qt_h3 for ln in p["lines"] for w in ln])
    ann_qm = annotate_pages_with_seg(qm_h2, seg_mt)
    ann_qt = annotate_pages_with_seg(qt_h3, seg_mt)
    ann_all_mt = annotate_pages_with_seg(pages, seg_mt)
    vP_mt = sorted({r["P"] for p in ann_qm + ann_qt for ln in p["ann_lines"] for r in ln} | {EMPTY})
    vS_mt = sorted({r["S"] for p in ann_qm + ann_qt for ln in p["ann_lines"] for r in ln} | {EMPTY})
    top50_mt = get_shared_top50_cores(ann_qm, ann_qt)
    mod_qm_h2 = FastSlotScorer(ann_qm, vP_mt, vS_mt)
    mod_qt_h3 = FastSlotScorer(ann_qt, vP_mt, vS_mt)

    ann_h2_hb = [p for p in ann_all_mt if p["section"] == "H" and p["lang"] == "B" and p["hand"] == "2"]
    ann_h3_hb = [p for p in ann_all_mt if (p["section"] == "H" and p["lang"] == "B" and p["hand"] == "3") or p["id"] == "f65v"]

    for mode_lbl, c_flt, is_bl in (
        ("All Tokens (Core-Cond)", None, False),
        ("Shared Top-50 Cores   ", top50_mt, False),
        ("Core-Blind Transitions", None, True),
    ):
        b2_m2, n2 = mod_qm_h2.score_pages(ann_h2_hb, core_filter=c_flt, blind=is_bl)
        b2_m3, _ = mod_qt_h3.score_pages(ann_h2_hb, core_filter=c_flt, blind=is_bl)
        b3_m3, n3 = mod_qt_h3.score_pages(ann_h3_hb, core_filter=c_flt, blind=is_bl)
        b3_m2, _ = mod_qm_h2.score_pages(ann_h3_hb, core_filter=c_flt, blind=is_bl)
        dh_on_h2 = (b2_m3 - b2_m2) / max(n2, 1)
        dh_on_h3 = (b3_m2 - b3_m3) / max(n3, 1)
        dsym_proj = 0.5 * (dh_on_h2 + dh_on_h3)

        # Page-level blind accuracy on untouched Herbal-B pages
        c_h2 = sum(1 for p in ann_h2_hb if mod_qm_h2.score_pages([p], c_flt, is_bl)[0] < mod_qt_h3.score_pages([p], c_flt, is_bl)[0])
        c_h3 = sum(1 for p in ann_h3_hb if mod_qt_h3.score_pages([p], c_flt, is_bl)[0] < mod_qm_h2.score_pages([p], c_flt, is_bl)[0])
        emit(
            f"  Out-of-Quire Cross-Projection (Train: Q_M[H2,Bio] vs Q_T[H3,Stars] -> Test: Untouched Herbal-B Sec=H):\n"
            f"    [{mode_lbl}] Delta_H on H2_HerbB(20p)={dh_on_h2:+.4f}, Delta_H on H3_HerbB(7p)={dh_on_h3:+.4f}, "
            f"D_sym={dsym_proj:+.4f} | Blind Page ID: H2={c_h2}/{len(ann_h2_hb)}, H3={c_h3}/{len(ann_h3_hb)}"
        )

    # Direct per-page scores inside Quire G/H (f55r/v, f57r, f58r/v, f65v, f66r/v) and Quire Q (f94r..f95v1)
    emit(f"  Direct Per-Page Cross-Entropy (H(page|H3_Q_T) - H(page|H2_Q_M)) on Quire G/H/Q Transition Folios:")
    focus_ids = ["f50r", "f50v", "f55r", "f55v", "f57r", "f58r", "f58v", "f65v", "f66r", "f66v",
                 "f94r", "f94v", "f95r1", "f95r2", "f95v2", "f95v1"]
    id2ann = {p["id"]: p for p in ann_all_mt}
    row_strs = []
    for fid in focus_ids:
        if fid not in id2ann:
            continue
        p = id2ann[fid]
        bm2, nt = mod_qm_h2.score_pages([p])
        bm3, _ = mod_qt_h3.score_pages([p])
        diff = (bm3 - bm2) / max(nt, 1)  # >0 favors H2, <0 favors H3
        row_strs.append(f"{fid}(Q={p['quire']},S={p['section']},L={p['lang']},H={p['hand']}):{diff:+.3f}")
    emit("    " + " | ".join(row_strs[:8]))
    emit("    " + " | ".join(row_strs[8:]))

    # 1C. 2x2 Variance Decomposition: Section (Bio B vs Stars S vs Herbal H) vs Hand (H2 vs H3) under Clean Nested LOQO
    emit(f"\n--- 1C. 2x2 Factorial Decomposition: How Much of s60's Currier-B Divergence (D_sym=+0.41) is Section vs Hand? [{tr_name}] ---")
    b_pages = [p for p in pages if p["lang"] == "B" or p["id"] == "f65v"]
    seg_b = SlotSegmenter([w for p in b_pages for ln in p["lines"] for w in ln])
    ann_b = annotate_pages_with_seg(b_pages, seg_b)

    sub_h2_bio = [p for p in ann_b if p["hand"] == "2" and p["section"] == "B"]
    sub_h2_hb = [p for p in ann_b if p["hand"] == "2" and p["section"] == "H"]
    sub_h3_st = [p for p in ann_b if p["hand"] == "3" and p["section"] == "S"]
    sub_h3_hb = [p for p in ann_b if p["hand"] == "3" and p["section"] == "H"]

    def pair_loqo_dsym(pa: list[dict], pb: list[dict]) -> tuple[float, float, float]:
        a_set = {p["id"] for p in pa}
        b_set = {p["id"] for p in pb}
        res_f = evaluate_nested_folds(pa + pb, "leaf", lambda p: p["id"] in a_set, lambda p: p["id"] in b_set, SlotSegmenter)
        return res_f["all"]["dsym"], res_f["top50"]["dsym"], res_f["blind"]["dsym"]

    d_unstrat = evaluate_nested_folds(
        [p for p in pages if p["lang"] == "B" and p["hand"] in {"2", "3"}],
        "leaf", lambda p: p["hand"] == "2", lambda p: p["hand"] == "3", SlotSegmenter
    )
    d_cross_both = pair_loqo_dsym(sub_h2_bio, sub_h3_st)
    d_within_h2_sec = pair_loqo_dsym(sub_h2_bio, sub_h2_hb)
    d_within_h3_sec = pair_loqo_dsym(sub_h3_st, sub_h3_hb)
    d_within_sec_hand = pair_loqo_dsym(sub_h2_hb, sub_h3_hb)

    emit(
        f"  1. Unstratified Currier-B (All H2_CurB vs All H3_CurB, s60 baseline): "
        f"D_sym(all)={d_unstrat['all']['dsym']:+.4f} | D_sym(C_top50)={d_unstrat['top50']['dsym']:+.4f} | D_sym(blind)={d_unstrat['blind']['dsym']:+.4f}\n"
        f"  2. Cross-Hand + Cross-Section (H2_Bio[Sec=B] vs H3_Stars[Sec=S])     : "
        f"D_sym(all)={d_cross_both[0]:+.4f} | D_sym(C_top50)={d_cross_both[1]:+.4f} | D_sym(blind)={d_cross_both[2]:+.4f}\n"
        f"  3. Same-Hand-2 Cross-Section  (H2_Bio[Sec=B] vs H2_HerbB[Sec=H])     : "
        f"D_sym(all)={d_within_h2_sec[0]:+.4f} | D_sym(C_top50)={d_within_h2_sec[1]:+.4f} | D_sym(blind)={d_within_h2_sec[2]:+.4f}\n"
        f"  4. Same-Hand-3 Cross-Section  (H3_Stars[Sec=S] vs H3_HerbB[Sec=H])   : "
        f"D_sym(all)={d_within_h3_sec[0]:+.4f} | D_sym(C_top50)={d_within_h3_sec[1]:+.4f} | D_sym(blind)={d_within_h3_sec[2]:+.4f}\n"
        f"  5. Same-Section-H Cross-Hand  (H2_HerbB[Sec=H] vs H3_HerbB[Sec=H])   : "
        f"D_sym(all)={d_within_sec_hand[0]:+.4f} | D_sym(C_top50)={d_within_sec_hand[1]:+.4f} | D_sym(blind)={d_within_sec_hand[2]:+.4f}\n"
        f"  -> Pure Within-Section Hand Retention Share (Row 5 / Row 1)          : "
        f"all={d_within_sec_hand[0]/max(d_unstrat['all']['dsym'],1e-9)*100:.1f}%, "
        f"C_top50={d_within_sec_hand[1]/max(d_unstrat['top50']['dsym'],1e-9)*100:.1f}%, "
        f"blind={d_within_sec_hand[2]/max(d_unstrat['blind']['dsym'],1e-9)*100:.1f}%"
    )

    part1_out["decomp"] = dict(
        unstrat=d_unstrat,
        cross_both=d_cross_both,
        within_h2_sec=d_within_h2_sec,
        within_h3_sec=d_within_h3_sec,
        within_sec_hand=d_within_sec_hand,
    )
    return part1_out


# ===========================================================================
# 5. Part 2A: Direct Comma ',', Cross-Transcriber & s47 Ink-Gap Alignment of B2
# ===========================================================================
def subglyph_variants(c: str) -> set[str]:
    out = set()
    for a, b in SUBGLYPH_PAIRS:
        la = len(a)
        start = 0
        while True:
            idx = c.find(a, start)
            if idx == -1:
                break
            cand = c[:idx] + b + c[idx + la:]
            if cand and cand != c:
                out.add(cand)
            start = idx + 1
    return out


def edit1_variants(c: str, alph: list[str]) -> set[str]:
    out = set()
    L = len(c)
    for i in range(L):
        out.add(c[:i] + c[i + 1:])
        for g in alph:
            if g != c[i]:
                out.add(c[:i] + g + c[i + 1:])
    for i in range(L + 1):
        for g in alph:
            out.add(c[:i] + g + c[i:])
    out.discard(c)
    out.discard("")
    return out


def cross_translit_break_offsets(
    w: str,
    pid: str,
    lno: int,
    other_line_maps: list[dict[tuple[str, int], dict]],
) -> tuple[set[int], set[int]]:
    """For a word w on (pid, lno), checks the other two transliterations at (pid, lno).
    Returns:
      - comma_offs: internal character offsets k in 1..len(w)-1 where another transliteration
                    had a comma ',' inside a matching joined token
      - break_offs: internal character offsets k in 1..len(w)-1 where another transliteration
                    had ANY word break ('.' or ',') splitting w into u_a + u_{a+1}."""
    comma_offs: set[int] = set()
    break_offs: set[int] = set()
    Lw = len(w)
    if Lw < 2:
        return comma_offs, break_offs

    for lm in other_line_maps:
        rec = lm.get((pid, lno))
        if not rec:
            continue
        # 1. Check U1 words in other transliteration for exact match with internal comma
        for uw, uoffs in zip(rec["u1_words"], rec["u1_offs"]):
            if uw == w and uoffs:
                comma_offs.update(uoffs)
                break_offs.update(uoffs)
        # 2. Check split_words in other transliteration for contiguous sequence concatenating to w
        sw = rec["split_words"]
        n_s = len(sw)
        for i in range(n_s):
            if not w.startswith(sw[i]) or len(sw[i]) >= Lw:
                continue
            acc_s = sw[i]
            offs_here = [len(acc_s)]
            for j in range(i + 1, min(i + 5, n_s)):
                acc_s += sw[j]
                if len(acc_s) < Lw and w.startswith(acc_s):
                    offs_here.append(len(acc_s))
                elif acc_s == w:
                    break_offs.update(offs_here)
                    break
                else:
                    break
    return comma_offs, break_offs


def run_part2a_comma_and_ink_alignment(
    tr_name: str,
    raw_data_by_tr: dict[str, dict],
    s47_map: dict[tuple[str, int, int, int], tuple[int, float | None]],
) -> dict:
    emit("\n================================================================================")
    emit(f"PART 2A [{tr_name}]: DIRECT COMMA ',' & s47 INK-GAP ALIGNMENT OF B2 SPLITS + B1_1CHAR vs B1_MULTI (L-304)")
    emit("================================================================================")

    cur_raw = raw_data_by_tr[tr_name]
    other_lms = [raw_data_by_tr[k]["line_map"] for k in raw_data_by_tr if k != tr_name]

    split_pages = cur_raw["split_pages"]
    u1_pages = cur_raw["u1_pages"]
    quires = sorted({p["quire"] for p in split_pages})

    # Counters on Standard (',' split) LOQO folds under SlotSegmenter and Seg_Affix2
    stats = {}
    for stream_tag, page_list, is_u1 in (
        ("Standard_Split", split_pages, False),
        ("U1_CommaJoined", u1_pages, True),
    ):
        for seg_tag, seg_cls in (("SlotSegmenter", SlotSegmenter), ("Seg_Affix2", SegAffix2)):
            if is_u1 and seg_tag == "Seg_Affix2":
                continue
            key = f"{stream_tag}__{seg_tag}"
            n_rare = 0
            n_unseen = 0
            # B1 breakdown on unseen cores: B1_1char vs B1_multi
            u_b1_1char = 0
            u_b1_multi_only = 0
            u_b1_any = 0
            u_b2_len2 = 0
            u_b2_any = 0
            u_b3_sub = 0
            u_b4_ed1 = 0
            u_b5_dist = 0
            u_disappears_other_seg = 0

            # B2 split alignment counters (on unseen cores with B2_len2, and on rare event cores with B2_len2)
            for_cohorts = {
                "unseen": dict(
                    n_cores=0, n_b2_len2=0, n_b2_any=0,
                    b2_same_tr_comma_exact=0, b2_same_tr_comma_any=0,
                    b2_cross_tr_break_exact=0, b2_cross_tr_comma_exact=0,
                    b2_either_break_exact=0, b2_pure_unbroken=0,
                    shuf_n_b2_len2=0, shuf_either_break_exact=0,
                    s47_b2_r=[], s47_b2_ink=[], s47_nonb2_r=[], s47_nonb2_ink=[],
                ),
                "rare_ev": dict(
                    n_cores=0, n_b2_len2=0, n_b2_any=0,
                    b2_same_tr_comma_exact=0, b2_same_tr_comma_any=0,
                    b2_cross_tr_break_exact=0, b2_cross_tr_comma_exact=0,
                    b2_either_break_exact=0, b2_pure_unbroken=0,
                    shuf_n_b2_len2=0, shuf_either_break_exact=0,
                    s47_b2_r=[], s47_b2_ink=[], s47_nonb2_r=[], s47_nonb2_ink=[],
                ),
            }

            rng = random.Random(SEED + (100 if is_u1 else 0))

            for q_hold in quires:
                tr_p = [p for p in page_list if p["quire"] != q_hold]
                te_p = [p for p in page_list if p["quire"] == q_hold]
                if not tr_p or not te_p:
                    continue
                tr_words = [w for p in tr_p for ln in p["lines"] for w in ln]
                seg = seg_cls(tr_words)
                other_seg = SegAffix2(tr_words) if seg_cls is SlotSegmenter else SlotSegmenter(tr_words)

                tr_cores = Counter(seg.segment(w)[1] for w in tr_words)
                other_tr_cores = set(other_seg.segment(w)[1] for w in tr_words)
                tr_set = set(tr_cores.keys())
                top20 = {c for c, _ in tr_cores.most_common(TOPK_RARE)}
                alph = sorted({ch for c in tr_set for ch in c})
                pre_cand = set(seg.prefix_stats.keys()) | set(seg.prefixes) | {""}
                suf_cand = set(seg.suffix_stats.keys()) | set(seg.suffixes) | {""}

                # Character unigram weights for shuffled core null
                gl_cnt = Counter()
                for c_k, cnt_v in tr_cores.items():
                    for ch in c_k:
                        gl_cnt[ch] += cnt_v
                alph_w = sorted(gl_cnt.keys())
                cum_w = np.cumsum([gl_cnt[ch] for ch in alph_w]).tolist()

                def valid_p(c_cur: str, cp: str) -> bool:
                    if cp == c_cur or not cp or cp not in tr_set:
                        return False
                    tc = tr_cores.get(c_cur, 0)
                    return tr_cores[cp] > tc or tc == 0

                def find_b2_splits(c_str: str, tc_val: int) -> tuple[list[int], list[int]]:
                    """Returns (len2_split_offsets, any_split_offsets) inside c_str (1..len(c_str)-1)."""
                    Lc = len(c_str)
                    s_len2, s_any = [], []
                    for k_sp in range(1, Lc):
                        c1, c2 = c_str[:k_sp], c_str[k_sp:]
                        if c1 in tr_set and c2 in tr_set:
                            if tr_cores[c1] > tc_val and tr_cores[c2] > tc_val:
                                s_any.append(k_sp)
                                if k_sp >= 2 and (Lc - k_sp) >= 2:
                                    s_len2.append(k_sp)
                    return s_len2, s_any

                for pg in te_p:
                    pid = pg["id"]
                    seen_on_page: set[str] = set()
                    comma_lines = pg.get("comma_offs", [[frozenset()] * len(ln) for ln in pg["lines"]])
                    line_nos = pg.get("line_nos", list(range(1, len(pg["lines"]) + 1)))

                    for l_idx, (ln, c_offs_ln, lno) in enumerate(zip(pg["lines"], comma_lines, line_nos)):
                        line_char_pos = 0
                        for w_idx, (w, w_comma_offs) in enumerate(zip(ln, c_offs_ln)):
                            cur_w_start = line_char_pos
                            line_char_pos += len(w)
                            p_s, c_s, s_s = seg.segment(w)
                            len_p = len(p_s)
                            tc = tr_cores.get(c_s, 0)
                            is_rare_ev = (c_s not in top20) and (c_s not in seen_on_page)
                            seen_on_page.add(c_s)
                            is_unseen = (tc == 0)

                            if not (is_rare_ev or is_unseen):
                                continue

                            # Cross-transliteration break offsets in w
                            xt_comma_offs, xt_break_offs = cross_translit_break_offsets(w, pid, lno, other_lms)
                            all_break_offs_in_w = set(w_comma_offs) | xt_break_offs

                            # B2 splits on real core c_s
                            b2_l2_offs, b2_any_offs = find_b2_splits(c_s, tc)
                            # Convert core-internal split offset k_sp to word-internal offset len_p + k_sp
                            b2_w_offs = {len_p + k_sp for k_sp in b2_l2_offs}

                            # Shuffled core of same length |c_s|
                            Lc = len(c_s)
                            chars = list(c_s)
                            c_shuf = c_s
                            for _ in range(10):
                                if Lc >= 3 and len(set(chars)) > 1:
                                    rng.shuffle(chars)
                                    cand = "".join(chars)
                                else:
                                    cand = "".join(rng.choices(alph_w, cum_weights=cum_w, k=Lc))
                                if cand != c_s and cand not in top20:
                                    c_shuf = cand
                                    break
                            shuf_l2_offs, _ = find_b2_splits(c_shuf, 0 if is_unseen else tc)
                            shuf_w_offs = {len_p + k_sp for k_sp in shuf_l2_offs}

                            for coh_key, flag in (("unseen", is_unseen), ("rare_ev", is_rare_ev)):
                                if not flag:
                                    continue
                                cd = for_cohorts[coh_key]
                                cd["n_cores"] += 1
                                if b2_any_offs:
                                    cd["n_b2_any"] += 1
                                if b2_l2_offs:
                                    cd["n_b2_len2"] += 1
                                    has_same_exact = bool(b2_w_offs & set(w_comma_offs))
                                    has_same_any = bool(w_comma_offs)
                                    has_xt_comma = bool(b2_w_offs & xt_comma_offs)
                                    has_xt_break = bool(b2_w_offs & xt_break_offs)
                                    has_either = bool(b2_w_offs & all_break_offs_in_w)
                                    if has_same_exact:
                                        cd["b2_same_tr_comma_exact"] += 1
                                    if has_same_any:
                                        cd["b2_same_tr_comma_any"] += 1
                                    if has_xt_comma:
                                        cd["b2_cross_tr_comma_exact"] += 1
                                    if has_xt_break:
                                        cd["b2_cross_tr_break_exact"] += 1
                                    if has_either:
                                        cd["b2_either_break_exact"] += 1
                                    else:
                                        cd["b2_pure_unbroken"] += 1

                                    # Check s47 physical ink gaps at B2 split offset vs other internal offsets of w
                                    if tr_name == "ZL3b":
                                        for k_in_c in range(1, Lc):
                                            w_off = len_p + k_in_c
                                            s47_key = (pid, lno, -10, cur_w_start + w_off) if is_u1 else (pid, lno, w_idx, w_off)
                                            s47_hit = s47_map.get(s47_key)
                                            if s47_hit is not None:
                                                ink_c, r_val = s47_hit
                                                if k_in_c in b2_l2_offs:
                                                    cd["s47_b2_ink"].append(ink_c)
                                                    if r_val is not None:
                                                        cd["s47_b2_r"].append(r_val)
                                                else:
                                                    cd["s47_nonb2_ink"].append(ink_c)
                                                    if r_val is not None:
                                                        cd["s47_nonb2_r"].append(r_val)

                                if shuf_l2_offs:
                                    cd["shuf_n_b2_len2"] += 1
                                    if shuf_w_offs & all_break_offs_in_w:
                                        cd["shuf_either_break_exact"] += 1

                            if is_unseen:
                                n_unseen += 1
                                # Check if other segmenter maps w to an already-attested training core
                                _, c_other, _ = other_seg.segment(w)
                                if c_other in other_tr_cores:
                                    u_disappears_other_seg += 1

                                # Separate B1_1char (strict 1-char boundary shift) vs B1_multi (multi-char reparse)
                                b1_1c = False
                                for u in BOUND_UNITS_1CHAR:
                                    if (p_s.endswith(u) and valid_p(c_s, u + c_s)) or (
                                        s_s.startswith(u) and valid_p(c_s, c_s + u)
                                    ) or (
                                        len(c_s) > 1 and c_s.startswith(u) and valid_p(c_s, c_s[1:])
                                    ) or (
                                        len(c_s) > 1 and c_s.endswith(u) and valid_p(c_s, c_s[:-1])
                                    ):
                                        b1_1c = True
                                        break

                                b1_rep = False
                                Lw = len(w)
                                for lp in range(0, min(4, Lw)):
                                    pp = w[:lp]
                                    if pp not in pre_cand:
                                        continue
                                    for ls in range(0, min(4, Lw - lp)):
                                        ss = w[Lw - ls:] if ls > 0 else ""
                                        if ss not in suf_cand or (pp == p_s and ss == s_s):
                                            continue
                                        cp = w[lp:Lw - ls]
                                        if valid_p(c_s, cp):
                                            b1_rep = True
                                            break
                                    if b1_rep:
                                        break

                                b1_shf_all = b1_1c
                                if not b1_shf_all:
                                    for u in ("ch", "sh"):
                                        if (p_s.endswith(u) and valid_p(c_s, u + c_s)) or (
                                            s_s.startswith(u) and valid_p(c_s, c_s + u)
                                        ) or (
                                            len(c_s) > 2 and c_s.startswith(u) and valid_p(c_s, c_s[2:])
                                        ) or (
                                            len(c_s) > 2 and c_s.endswith(u) and valid_p(c_s, c_s[:-2])
                                        ):
                                            b1_shf_all = True
                                            break

                                b1_any = b1_1c or b1_rep or b1_shf_all
                                if b1_1c:
                                    u_b1_1char += 1
                                elif b1_any:
                                    u_b1_multi_only += 1
                                if b1_any:
                                    u_b1_any += 1

                                b2_l2 = len(b2_l2_offs) > 0
                                b3_sg = any(valid_p(c_s, cp) for cp in subglyph_variants(c_s))
                                b4_e1 = any(valid_p(c_s, cp) for cp in edit1_variants(c_s, alph))

                                if not b1_any and b2_l2:
                                    u_b2_len2 += 1
                                elif not b1_any and not b2_l2 and b3_sg:
                                    u_b3_sub += 1
                                elif not b1_any and not b2_l2 and not b3_sg and b4_e1:
                                    u_b4_ed1 += 1
                                elif not (b1_any or b2_l2 or b3_sg or b4_e1):
                                    u_b5_dist += 1
                            if is_rare_ev:
                                n_rare += 1

            stats[key] = dict(
                n_unseen=n_unseen,
                n_rare=n_rare,
                u_b1_1char=u_b1_1char,
                u_b1_multi_only=u_b1_multi_only,
                u_b1_any=u_b1_any,
                u_b2_len2=u_b2_len2,
                u_b3_sub=u_b3_sub,
                u_b4_ed1=u_b4_ed1,
                u_b5_dist=u_b5_dist,
                u_disappears_other_seg=u_disappears_other_seg,
                cohorts=for_cohorts,
            )

            emit(
                f"\n  [{key}] 15-Quire LOQO Unseen Core Breakdown (N_unseen={n_unseen}, N_rare_events={n_rare}):\n"
                f"    B1 Total Boundary Bleed/Reparse = {u_b1_any:4d}/{n_unseen} ({u_b1_any/max(n_unseen,1)*100:5.2f}%): "
                f"Strict 1-Char Shift (B1_1char) = {u_b1_1char:4d} ({u_b1_1char/max(n_unseen,1)*100:5.2f}%) vs "
                f"Multi-Char Reparse Only (B1_multi) = {u_b1_multi_only:4d} ({u_b1_multi_only/max(n_unseen,1)*100:5.2f}%)\n"
                f"    Waterfall Remainder: B2_comp(>=2+>=2)={u_b2_len2/max(n_unseen,1)*100:5.2f}%, "
                f"B3_subglyph={u_b3_sub/max(n_unseen,1)*100:5.2f}%, B4_edit1={u_b4_ed1/max(n_unseen,1)*100:5.2f}%, "
                f"B5_distal={u_b5_dist/max(n_unseen,1)*100:5.2f}%\n"
                f"    Cross-Segmenter Sensitivity: {u_disappears_other_seg:4d}/{n_unseen} ({u_disappears_other_seg/max(n_unseen,1)*100:5.2f}%) "
                f"of unseen cores disappear (become attested training cores) under the alternate segmenter!"
            )

            for coh_name, coh_label in (("unseen", "Strictly Unseen Held-Out Cores"), ("rare_ev", "First-on-Page Rare Cores (s59/s63)")):
                cd = for_cohorts[coh_name]
                nb2 = max(cd["n_b2_len2"], 1)
                n_all = max(cd["n_cores"], 1)
                emit(
                    f"    {coh_label} (N={cd['n_cores']}, marginal B2_len2={cd['n_b2_len2']} [{cd['n_b2_len2']/n_all*100:5.2f}%] "
                    f"vs char-shuffled null B2_len2={cd['shuf_n_b2_len2']} [{cd['shuf_n_b2_len2']/n_all*100:5.2f}%]):\n"
                    f"      - Exact C1|C2 Raw IVTFF Comma (same translit before U1 join): "
                    f"{cd['b2_same_tr_comma_exact']:4d}/{cd['n_b2_len2']} ({cd['b2_same_tr_comma_exact']/nb2*100:5.2f}%) "
                    f"[any comma in word: {cd['b2_same_tr_comma_any']}/{cd['n_b2_len2']} ({cd['b2_same_tr_comma_any']/nb2*100:5.2f}%)]\n"
                    f"      - Exact C1|C2 Cross-Transcriber Break (other 2 translits '.' or ','): "
                    f"{cd['b2_cross_tr_break_exact']:4d}/{cd['n_b2_len2']} ({cd['b2_cross_tr_break_exact']/nb2*100:5.2f}%) "
                    f"[comma only: {cd['b2_cross_tr_comma_exact']}/{cd['n_b2_len2']} ({cd['b2_cross_tr_comma_exact']/nb2*100:5.2f}%)]\n"
                    f"      - Total True Comma/Break Split (Same-OR-Cross Translit at C1|C2): "
                    f"{cd['b2_either_break_exact']:4d}/{cd['n_b2_len2']} ({cd['b2_either_break_exact']/nb2*100:5.2f}%) vs "
                    f"Pure Unbroken String Split: {cd['b2_pure_unbroken']:4d}/{cd['n_b2_len2']} ({cd['b2_pure_unbroken']/nb2*100:5.2f}%) "
                    f"[shuffled null break align: {cd['shuf_either_break_exact']}/{max(cd['shuf_n_b2_len2'],1)} ({cd['shuf_either_break_exact']/max(cd['shuf_n_b2_len2'],1)*100:5.2f}%)]"
                )
                if cd["s47_b2_ink"]:
                    b2_ink_rate = float(np.mean(cd["s47_b2_ink"]))
                    nb2_ink_rate = float(np.mean(cd["s47_nonb2_ink"])) if cd["s47_nonb2_ink"] else 0.0
                    b2_med_r = float(np.median(cd["s47_b2_r"])) if cd["s47_b2_r"] else 0.0
                    nb2_med_r = float(np.median(cd["s47_nonb2_r"])) if cd["s47_nonb2_r"] else 0.0
                    emit(
                        f"      - s47 Physical Ink-Gap Alignment at C1|C2 (n={len(cd['s47_b2_ink'])} aligned B2 boundaries vs {len(cd['s47_nonb2_ink'])} non-B2 internal boundaries):\n"
                        f"        C1|C2 median r = {b2_med_r:.4f} (ink-space call rate = {sum(cd['s47_b2_ink'])}/{len(cd['s47_b2_ink'])} = {b2_ink_rate*100:5.2f}%) vs "
                        f"non-B2 internal median r = {nb2_med_r:.4f} (ink-space call rate = {nb2_ink_rate*100:5.2f}%) "
                        f"[ref s47: N=0.3737 (3.37%), Comma C=0.9400 (44.83%), Dot D=1.8601 (91.37%)]"
                    )

    return stats


# ===========================================================================
# 6. Part 2B: Pre-Registered 6-Model Individual Component Ablation on 15 LOQO Folds
# ===========================================================================
class RenormCharMarkov:
    """CharMarkov over core types, explicitly renormalized over unseen strings c not in forbidden_cores."""

    def __init__(self, core_types: list[str], forbidden_cores: set[str], order: int = 2):
        self.cm = CharMarkov(core_types, order)
        self.forbidden = forbidden_cores
        seen_mass = sum(2.0 ** self.cm.logp_word(v) for v in forbidden_cores)
        self.rem_mass = max(1e-6, 1.0 - seen_mass)

    def prob_unseen(self, c: str) -> float:
        return (2.0 ** self.cm.logp_word(c)) / self.rem_mass


def build_four_ablated_unseen_dists(
    base_cores: Counter,
    forbidden_cores: set[str],
    seg,
) -> tuple[dict[str, float], dict[str, float], dict[str, float], dict[str, float]]:
    """Constructs four separate, proper probability distributions over unseen cores c not in forbidden_cores,
    fitted strictly on base_cores and seg from the 14 training quires:
      1. P_bleed1(c)  : Strict 1-Glyph Boundary Shift (B1_1char) ONLY (attaching/stripping 1 char at core edge).
      2. P_reparse(c) : Multi-Glyph Alternative Training Affix Reparse (B1_reparse, len>=2 or P+C+S shift) ONLY.
      3. P_comp(c)    : Two-Core Concatenation (B2_comp: C1 + C2) ONLY.
      4. P_subglyph(c): Sub-Glyph Allomorphy (B3: e/i run & gallows/vowel/liquid swap) ONLY."""
    bleed1_w: Counter = Counter()
    reparse_w: Counter = Counter()
    sub_w: Counter = Counter()

    pre_weights = {u: sh for u, (sh, _h) in seg.prefix_stats.items()}
    suf_weights = {u: sh for u, (sh, _h) in seg.suffix_stats.items()}
    for u in BOUND_UNITS_ALL:
        pre_weights.setdefault(u, 0.005)
        suf_weights.setdefault(u, 0.005)

    p1_weights = {u: w for u, w in pre_weights.items() if len(u) == 1}
    s1_weights = {u: w for u, w in suf_weights.items() if len(u) == 1}
    p_multi_weights = {u: w for u, w in pre_weights.items() if len(u) >= 2}
    s_multi_weights = {u: w for u, w in suf_weights.items() if len(u) >= 2}

    for v, cnt in base_cores.items():
        w = float(cnt)
        # 1. Strict 1-char boundary shift (B1_1char)
        for u, pu in p1_weights.items():
            c_add = u + v
            if c_add not in forbidden_cores:
                bleed1_w[c_add] += w * pu
            if len(v) > 1 and v[0] == u:
                c_rem = v[1:]
                if c_rem and c_rem not in forbidden_cores:
                    bleed1_w[c_rem] += w * pu * 2.0
        for u, su in s1_weights.items():
            c_add = v + u
            if c_add not in forbidden_cores:
                bleed1_w[c_add] += w * su
            if len(v) > 1 and v[-1] == u:
                c_rem = v[:-1]
                if c_rem and c_rem not in forbidden_cores:
                    bleed1_w[c_rem] += w * su * 2.0

        # 2. Multi-char affix reparse (B1_reparse: len>=2 affixes + simultaneous P & S shifts)
        for u, pu in p_multi_weights.items():
            lu = len(u)
            c_add = u + v
            if c_add not in forbidden_cores:
                reparse_w[c_add] += w * pu
            if len(v) > lu and v.startswith(u):
                c_rem = v[lu:]
                if c_rem and c_rem not in forbidden_cores:
                    reparse_w[c_rem] += w * pu * 2.0
        for u, su in s_multi_weights.items():
            lu = len(u)
            c_add = v + u
            if c_add not in forbidden_cores:
                reparse_w[c_add] += w * su
            if len(v) > lu and v.endswith(u):
                c_rem = v[:-lu]
                if c_rem and c_rem not in forbidden_cores:
                    reparse_w[c_rem] += w * su * 2.0

        # 4. Sub-glyph allomorphy (B3)
        for c_sg in subglyph_variants(v):
            if c_sg not in forbidden_cores:
                sub_w[c_sg] += w

    # Also include simultaneous P+S reparse on top-250 base_cores in P_reparse
    top_p = sorted(pre_weights.items(), key=lambda x: -x[1])[:8]
    top_s = sorted(suf_weights.items(), key=lambda x: -x[1])[:8]
    for v, cnt in base_cores.most_common(250):
        w = float(cnt)
        for u_p, pu in top_p:
            for u_s, su in top_s:
                c_both = u_p + v + u_s
                if len(c_both) <= 12 and c_both not in forbidden_cores:
                    reparse_w[c_both] += w * pu * su

    # 3. Two-Core Concatenation (B2_comp: C1 + C2) from top-280 base_cores
    comp_w: Counter = Counter()
    top_base = base_cores.most_common(280)
    for v1, n1 in top_base:
        for v2, n2 in top_base:
            cc = v1 + v2
            if 3 <= len(cc) <= 12 and cc not in forbidden_cores:
                bonus = 2.0 if (len(v1) >= 2 and len(v2) >= 2) else 0.5
                comp_w[cc] += bonus * math.sqrt(n1 * n2)

    def norm_d(cnt: Counter) -> dict[str, float]:
        tot = float(sum(cnt.values()))
        if tot <= 0:
            return {}
        return {k: v / tot for k, v in cnt.items()}

    return norm_d(bleed1_w), norm_d(reparse_w), norm_d(comp_w), norm_d(sub_w)


def fit_singleton_weights(
    tr_cores: Counter,
    seg,
) -> dict[str, float | tuple[float, float, float, float]]:
    """Fits the 1D mixture weight lambda_k for each individual ablated model (M1..M4) and the 4D
    mixture weights for M5_joint_all strictly on the 14 training quires via leave-singleton-out."""
    base_cores = Counter({c: n for c, n in tr_cores.items() if n >= 2})
    base_set = set(base_cores.keys())
    singletons = [c for c, n in tr_cores.items() if n == 1]
    if not singletons or not base_set:
        return dict(lam1=0.15, lam2=0.10, lam3=0.10, lam4=0.03, lam5=(0.15, 0.10, 0.10, 0.03))

    cm_fit = RenormCharMarkov(sorted(base_set), base_set, order=2)
    p_b1, p_rep, p_comp, p_sub = build_four_ablated_unseen_dists(base_cores, base_set, seg)

    s_p0 = np.array([cm_fit.prob_unseen(c) for c in singletons], dtype=np.float64)
    s_b1 = np.array([p_b1.get(c, 0.0) for c in singletons], dtype=np.float64)
    s_rep = np.array([p_rep.get(c, 0.0) for c in singletons], dtype=np.float64)
    s_comp = np.array([p_comp.get(c, 0.0) for c in singletons], dtype=np.float64)
    s_sub = np.array([p_sub.get(c, 0.0) for c in singletons], dtype=np.float64)

    def fit_1d(s_comp_arr: np.ndarray) -> float:
        best_l = 0.05
        best_b = float("inf")
        for l_cand in (0.01, 0.02, 0.04, 0.07, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
            pm = (1.0 - l_cand) * s_p0 + l_cand * s_comp_arr
            b = float(-np.log2(np.maximum(pm, 1e-15)).mean())
            if b < best_b:
                best_b = b
                best_l = l_cand
        return best_l

    lam1 = fit_1d(s_b1)
    lam2 = fit_1d(s_rep)
    lam3 = fit_1d(s_comp)
    lam4 = fit_1d(s_sub)

    best_lam5 = (0.15, 0.10, 0.10, 0.02)
    best_b5 = float("inf")
    for l1 in (0.05, 0.12, 0.20, 0.28):
        for l2 in (0.03, 0.08, 0.15):
            for l3 in (0.04, 0.10, 0.18):
                for l4 in (0.01, 0.03, 0.06):
                    l0 = 1.0 - l1 - l2 - l3 - l4
                    if l0 <= 0.20:
                        continue
                    pm = l0 * s_p0 + l1 * s_b1 + l2 * s_rep + l3 * s_comp + l4 * s_sub
                    b = float(-np.log2(np.maximum(pm, 1e-15)).mean())
                    if b < best_b5:
                        best_b5 = b
                        best_lam5 = (l1, l2, l3, l4)

    return dict(lam1=lam1, lam2=lam2, lam3=lam3, lam4=lam4, lam5=best_lam5)


def run_part2b_loqo_component_ablation(tr_name: str, split_pages: list[dict]) -> dict:
    emit("\n================================================================================")
    emit(f"PART 2B [{tr_name}]: PRE-REGISTERED 6-MODEL COMPONENT ABLATION ON 15 LOQO FOLDS (L-304)")
    emit("================================================================================")

    quires = sorted({p["quire"] for p in split_pages})
    models_order = [
        "M0_char2",
        "M0_char3",
        "M1_bleed1_only",
        "M2_reparse_only",
        "M3_comp_only",
        "M4_subglyph_only",
        "M5_joint_all",
    ]

    out_by_seg = {}
    for seg_tag, seg_cls in (("SlotSegmenter", SlotSegmenter), ("Seg_Affix2", SegAffix2)):
        # Fit mixture weights once on full corpus singletons as reference, and re-fit per LOQO fold
        quire_records = []
        tot_tok = 0
        tot_chars = 0
        unseen_types: set[str] = set()
        bits_sum = {m: 0.0 for m in models_order}

        for q_hold in quires:
            tr_p = [p for p in split_pages if p["quire"] != q_hold]
            te_p = [p for p in split_pages if p["quire"] == q_hold]
            if not tr_p or not te_p:
                continue

            tr_words = [w for p in tr_p for ln in p["lines"] for w in ln]
            seg = seg_cls(tr_words)
            tr_cores = Counter(seg.segment(w)[1] for w in tr_words)
            tr_set = set(tr_cores.keys())

            # Fit mixture weights strictly on the 14 training quires (leave-singleton-out)
            w_fit = fit_singleton_weights(tr_cores, seg)
            lam1 = float(w_fit["lam1"])
            lam2 = float(w_fit["lam2"])
            lam3 = float(w_fit["lam3"])
            lam4 = float(w_fit["lam4"])
            l5_1, l5_2, l5_3, l5_4 = w_fit["lam5"]  # type: ignore[misc]
            l5_0 = 1.0 - l5_1 - l5_2 - l5_3 - l5_4

            # Build full 14-quire models over unseen cores c not in tr_set
            cm2 = RenormCharMarkov(sorted(tr_set), tr_set, order=2)
            cm3 = RenormCharMarkov(sorted(tr_set), tr_set, order=3)
            p_b1, p_rep, p_comp, p_sub = build_four_ablated_unseen_dists(tr_cores, tr_set, seg)

            q_bits = {m: 0.0 for m in models_order}
            q_n = 0
            q_ch = 0

            for p in te_p:
                for ln in p["lines"]:
                    for w in ln:
                        _, c, _ = seg.segment(w)
                        if c in tr_set:
                            continue
                        q_n += 1
                        q_ch += len(c) + 1
                        unseen_types.add(c)

                        p0 = cm2.prob_unseen(c)
                        p3 = cm3.prob_unseen(c)
                        pb1 = p_b1.get(c, 0.0)
                        prep = p_rep.get(c, 0.0)
                        pcp = p_comp.get(c, 0.0)
                        psb = p_sub.get(c, 0.0)

                        probs = {
                            "M0_char2": p0,
                            "M0_char3": p3,
                            "M1_bleed1_only": (1.0 - lam1) * p0 + lam1 * pb1,
                            "M2_reparse_only": (1.0 - lam2) * p0 + lam2 * prep,
                            "M3_comp_only": (1.0 - lam3) * p0 + lam3 * pcp,
                            "M4_subglyph_only": (1.0 - lam4) * p0 + lam4 * psb,
                            "M5_joint_all": l5_0 * p0 + l5_1 * pb1 + l5_2 * prep + l5_3 * pcp + l5_4 * psb,
                        }
                        for m_name, pr in probs.items():
                            b_val = -math.log2(max(pr, 1e-15))
                            q_bits[m_name] += b_val
                            bits_sum[m_name] += b_val

            tot_tok += q_n
            tot_chars += q_ch
            if q_n > 0:
                quire_records.append(dict(quire=q_hold, n=q_n, ch=q_ch, bits=q_bits))

        # Paired quire-level bootstrap (B=1000 resamples of the held-out quires with replacement)
        n_q = len(quire_records)
        rng_b = np.random.default_rng(SEED + 77)
        boot_idx = rng_b.integers(0, n_q, size=(N_BOOT, n_q))

        def quire_boot_delta(m_name: str) -> tuple[float, float, float, int]:
            pt = (bits_sum[m_name] - bits_sum["M0_char2"]) / max(tot_tok, 1)
            diffs = np.array([qr["bits"][m_name] - qr["bits"]["M0_char2"] for qr in quire_records], dtype=np.float64)
            ns = np.array([qr["n"] for qr in quire_records], dtype=np.float64)
            b_vals = diffs[boot_idx].sum(axis=1) / np.maximum(ns[boot_idx].sum(axis=1), 1.0)
            q_wins = int(sum(1 for d in diffs if d < 0))
            return pt, float(np.percentile(b_vals, 2.5)), float(np.percentile(b_vals, 97.5)), q_wins

        emit(f"\n  --- [{seg_tag}] 15-Quire LOQO Held-Out Cross-Entropy on Strictly Unseen Cores ({tr_name}: {tot_tok} tok, {len(unseen_types)} types across {n_q} quires) ---")
        emit(f"  {'Model':18s} | {'bits/core':>9s} | {'bits/char':>9s} | {'Delta vs M0_char2 (95% Quire-Boot CI)':>38s} | {'Quires Won':>10s} | {'Share of M5 Gain':>16s}")
        emit("  " + "-" * 112)

        m5_gain = (bits_sum["M5_joint_all"] - bits_sum["M0_char2"]) / max(tot_tok, 1)
        seg_res = dict(tot_tok=tot_tok, n_types=len(unseen_types), n_quires=n_q, models={})
        for m_name in models_order:
            b_core = bits_sum[m_name] / max(tot_tok, 1)
            b_char = bits_sum[m_name] / max(tot_chars, 1)
            pt, lo, hi, q_wins = quire_boot_delta(m_name)
            share_m5 = (pt / m5_gain * 100.0) if (m5_gain < -1e-9 and m_name != "M0_char2") else 0.0
            seg_res["models"][m_name] = dict(
                b_core=b_core, b_char=b_char, delta=pt, ci_lo=lo, ci_hi=hi, q_wins=q_wins, share_m5=share_m5
            )
            emit(
                f"  {m_name:18s} | {b_core:9.4f} | {b_char:9.4f} | "
                f"{pt:+8.4f} [{lo:+8.4f}, {hi:+8.4f}]         | "
                f"{q_wins:4d}/{n_q:<5d} | {share_m5:14.1f}%"
            )
        out_by_seg[seg_tag] = seg_res

    return out_by_seg


# ===========================================================================
# Main Entrypoint
# ===========================================================================
def main() -> None:
    emit("s77 -- Section/Quire-Matched Herbal-B Scribe Test & Direct Comma/Ink-Gap Alignment + LOQO Rare-Core Component Ablation")
    emit(f"date: {clock()}")
    emit(f"sha256 s77_deconfounded_scribe_and_comma_ablation_loqo.py: {sha256(SELF)}")
    emit(f"sha256 s77_deconfounded_scribe_and_comma_ablation_loqo.prereg.sha256: {sha256(STUB) if STUB.exists() else 'MISSING'}")
    emit(f"stub_match: {stub_match()}")

    inv = load_codicology_and_inventory()
    s47_map = load_s47_char_gap_map()
    emit(f"Loaded folio_evidence_inventory.tsv ({len(inv)} folios with $Q, $B, $F, Davis hand) and s47 ink-gap map ({len(s47_map)} glyph boundaries).")

    raw_data_by_tr: dict[str, dict] = {}
    meta_pages_by_tr: dict[str, list[dict]] = {}
    for tr_name, meta_name, ivtff_path in TRANSLITS:
        meta_pages_by_tr[tr_name] = load_meta_pages(meta_name, inv)
        raw_data_by_tr[tr_name] = parse_raw_ivtff_with_commas(ivtff_path, inv)

    p1_all = {}
    p2a_all = {}
    p2b_all = {}

    for tr_name, _meta_name, _ivtff_path in TRANSLITS:
        t_tr = time.time()
        emit(
            f"\n################################################################################\n"
            f"TRANSLITERATION {tr_name}: {len(meta_pages_by_tr[tr_name])} P* pages "
            f"(U1 comma-joined pages={len(raw_data_by_tr[tr_name]['u1_pages'])})\n"
            f"################################################################################"
        )
        p1_all[tr_name] = run_part1_deconfounded_scribe(tr_name, meta_pages_by_tr[tr_name])
        flush()
        p2a_all[tr_name] = run_part2a_comma_and_ink_alignment(tr_name, raw_data_by_tr, s47_map)
        flush()
        p2b_all[tr_name] = run_part2b_loqo_component_ablation(tr_name, raw_data_by_tr[tr_name]["split_pages"])
        emit(f"\n[{tr_name} completed in {time.time() - t_tr:.1f}s]")
        flush()

    emit("\n================================================================================")
    emit("CONSOLIDATED SUMMARY OF s77 FINDINGS (CLOSING L-303 & L-304 IN CONSTRAINTS-MAP.md §C):")
    emit("================================================================================")
    for tr_name in ("ZL3b", "RF1b", "IT2a"):
        p1 = p1_all[tr_name]
        c1 = p1["C1_Strict_HerbB (Sec=H,Lang=B: H2[20p] vs H3_Q+f65v[7p])"]
        dec = p1["decomp"]
        p2b_s = p2b_all[tr_name]["SlotSegmenter"]["models"]
        p2b_a = p2b_all[tr_name]["Seg_Affix2"]["models"]
        emit(
            f"  [{tr_name}] PART 1 (L-303 — Herbal-B Section-Matched Hand 2 vs Hand 3):\n"
            f"    - Unstratified Currier-B D_sym(all/top50/blind) = "
            f"{dec['unstrat']['all']['dsym']:+.4f} / {dec['unstrat']['top50']['dsym']:+.4f} / {dec['unstrat']['blind']['dsym']:+.4f}\n"
            f"    - Strict Herbal-B (Sec=H) Nested LOLO D_sym     = "
            f"{c1['lobo_leaf']['all']['dsym']:+.4f} / {c1['lobo_leaf']['top50']['dsym']:+.4f} / {c1['lobo_leaf']['blind']['dsym']:+.4f} "
            f"(Null P1 page p={c1['pnulls']['P1_page']['all']['p']:.4f}, Null P2a leaf p={c1['pnulls']['P2_leaf']['all']['p']:.4f}, "
            f"Null P2b bifolio p={c1['pnulls']['P2_bif']['all']['p']:.4f}, Null P3 quire p={c1['pnulls']['P3_quire']['all']['p']:.4f})\n"
            f"  [{tr_name}] PART 2 (L-304 — 15-Quire LOQO Individual Component Ablation Delta vs M0_char2 [bits/core]):\n"
            f"    - SlotSegmenter: M1_bleed1={p2b_s['M1_bleed1_only']['delta']:+.4f}, "
            f"M2_reparse={p2b_s['M2_reparse_only']['delta']:+.4f}, M3_comp={p2b_s['M3_comp_only']['delta']:+.4f}, "
            f"M4_subglyph={p2b_s['M4_subglyph_only']['delta']:+.4f}, M5_joint={p2b_s['M5_joint_all']['delta']:+.4f}\n"
            f"    - Seg_Affix2   : M1_bleed1={p2b_a['M1_bleed1_only']['delta']:+.4f}, "
            f"M2_reparse={p2b_a['M2_reparse_only']['delta']:+.4f}, M3_comp={p2b_a['M3_comp_only']['delta']:+.4f}, "
            f"M4_subglyph={p2b_a['M4_subglyph_only']['delta']:+.4f}, M5_joint={p2b_a['M5_joint_all']['delta']:+.4f}"
        )
    emit(f"\nrun finished: {clock()} (total elapsed {time.time() - T_START:.1f}s)")
    flush()


if __name__ == "__main__":
    main()
