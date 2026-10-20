"""S107 (D-066 (k), approved by Jon 2026-10-18 13:33): do period TABULAR medical / combinatory texts show the F-40 core
behaviour -- the same core repeated inside a line with less repetition across line breaks?

FROZEN QUESTION, RIVALS, ACCEPTANCE, STOPPING RULE: D-066 (k) in .inventory/registers/DECISIONS.md, copied verbatim into
the stub header (s107_tabular_medical_reference.prereg.sha256).  Nothing here changes a threshold.
 Rivals: tabular-content reading (H-01 in tabular form, H-06: a table written row by row repeats terms within a row and
 changes them across rows, so it passes (b) and (c)) vs F-40 as stated (no natural text, tabular included, shows it).

MACHINERY (imported from s97, unchanged; nothing reimplemented): S97.profile_g (s87 signature parts (a) order excess at
 K=100/200 in S87.ORDER_BAND, (b) R_within(1) > 1 with permutation p < 0.05, (c) R_cross(1) < R_within(1), (d) quire-
 locality ratio in the band recomputed from the three Voynich transliterations, S87.c1), S97.flags / S97.fmt, the s67
 slot battery via S97.ref_jobs / S97.ctl_jobs / S97.run_pool / S97.battery_score (fold holds iff >= 4/6 predictions,
 battery holds on T iff >= 8/15 folds, battery holds iff on each of ZL3b, RF1b, IT2a), segmenters S97.SEGS (identity,
 slot = SlotSegmenter, affix2 = s77 SegAffix2), applicability S97.MIN_CORE_SHARE (non-empty core for >= 50 % of tokens),
 layout S87.layout with ZL3b page line counts (real source lines kept as lines), N_MATCH 4,731, S87 shuffle counts.
 Glue only: the s97 main() block is not a function, so its gate is re-composed from the same imported functions with the
 SAME seeds and indices as s97 (VOY profiles S87.SEED + 100 i; PC1 texts S97.SEED + s, profiles S97.SEED + 10 + s;
 PC2 profile xi = 0, NC profiles xi = 1 with S97.SEED + 1000 xi + 100 si; battery control xi + 1 = 1 (PC2), 2 (NC)).
 S97.emit / S97.flush / S97.measure_job are redirected to this script (log to results_s107.txt; a Measured job that
 raises returns None instead of killing the pool) -- s97's results file is never written.

GATE (s97 definition, must hold before the tabular texts are read as evidence; all three required):
 PC1 s91 LP91 at S91.PLANTED on the ZL3b lexicon/layout, identity on emitted cores: S87.c1 on >= 2 of 3 seeds.
 PC2 IT2a through the control path: S87.c1 on SlotSegmenter cores AND battery vs IT2a holds.
 NC  plain Latin prose (Augustine, ZL3b line lengths): s97 FULL = False.
 GATE = PC1 and PC2 and NC.  REPRO (descriptive, not gating): gate rows equal runs/s97/profiles.csv to 3 decimals.

TABULAR TEXTS (public domain sources; data/controls_tabular/README.md has URL, edition, licence, sha256; read as text):
 T1_tacuinum_bnf9333  Tacuinum sanitatis (Latin, Ibn Butlan's Taqwim), MS Paris BnF latin 9333 (1445-1450),
                      transcription published by MediManus (CHS Harvard).  One line = one table entry as transcribed (each
                      <p style="text-align:justify..."> paragraph: item name + Complexio/Natura, Electio, Iuuamentum,
                      Nocumentum, Remotio nocumenti, Quid generat, Conuenit; field labels kept as written).  The index
                      (Latin name -> folio) is a finding aid and is not used; the preface paragraph(s) are kept (they are
                      paragraphs of the same source).  The ordinal signs º/ª are removed before tokenising (their digits
                      are dropped by S87.tokens_norm).  The site's separate heading line is not used (it duplicates the
                      name that opens each paragraph).
 T2_degradibus_const  Constantinus Africanus, Liber de gradibus, in Constantini Africani ... opera (Basel: Henricus Petrus,
                      1536), BIU Sante copy, archive.org OCR.  The source is running entries (one simple after another),
                      not a ruled table, so it is laid out by the source's own entry boundaries: OCR lines from the line
                      after the 'DE GRADIBVS' title (first after OCR line 19800) to before 'Liber graduum finit'; running
                      heads dropped (line whose letters contain GRADIB/RADIBV/LIBER/DIBER, <= 12 tokens, >= 60 % capitals);
                      a line with <= 2 tokens that stands alone between blank lines is dropped (catchwords, margins)
                      [REVISION 1; was: every line with <= 2 tokens]; a new entry starts at a line that begins with
                      a capital AND (follows a blank line OR has a degree formula in its first 10 tokens: a token
                      containing 'grad' or equal to 'gra', or 'in' + primo/fecundo/secundo/tertio/quarto/fine/initio/
                      medio); a line ending in - / ^ = or the not-sign is joined to the next without a space.
 T3_lull_tabula_1515  Ramon Llull, Tabula generalis (Ars inventiva veritatis; Tabula generalis; ..., Valencia 1515),
                      archive.org ARes54311 OCR.  The combinatory table (letter cells such as bctb) printed in rows; one
                      OCR line = one printed table row.  Rows = OCR lines 18100-18599 whose letters (A-Z only, lowercased)
                      are >= 4 long and >= 90 % from the Lull alphabet b c d e f g h i k t; one-letter OCR fragments
                      dropped; if the remaining letters number a multiple of 4 the row is re-cut into 4-letter cells
                      (every Lull cell has 4 letters; OCR splits cells as 'bc tc'), otherwise the OCR tokens are kept.
 RECIPE LIST (optional in the brief): NOT RUN.  No Antidotarium Nicolai text with machine-readable entry boundaries was
 found (the on-disk Dispensarium OCR, s87/s97, has no recoverable recipe boundaries: 'recipe'/'rec' occur 4 times in its 59k OCR lines).
 TACUINUM 1531 Strasbourg print (Schott; three archive.org OCRs inspected): its tables are printed as rotated grids and
 the OCR of the grid pages is illegible, so it is not used.  Lull 1565/1596/1617 OCRs inspected: Cyrillic OCR, or
 < 200 cells.  Disclosed pre-freeze looks: token counts, entry counts, the first entries of each text, top word counts of
 T1; no signature statistic on any tabular text.
 SIZE: every text is used at its full size (S87.layout n_tot = 22,500 cuts nothing smaller); a text below 22,500 tokens is
 FLAGGED 'below 22,500'.  A text with fewer than 15 pages under the ZL3b page layout is FLAGGED 'pages < 15': locality (d)
 and the battery need 15 blocks; empty blocks make (d) and the battery not assessable (battery jobs that raise -> battery
 False); (b) and (c) need only lines within pages.

PRE-REGISTERED CALLS (D-066 (k)):
 SHOWS_F40_CORE(X) = for at least one APPLICABLE segmenter of {identity, slot, affix2}: (b) R_within(1) > 1 with p < 0.05
   AND (c) R_cross(1) < R_within(1)  (S87.c1 components b_Rwithin and c_Rcross<Rwithin).
 FULL_VOYNICH_LIKE(X) = s97 FULL rule: every applicable segmenter has all four parts (S87.c1) AND battery holds on ZL3b,
   RF1b and IT2a (>= 4/6 on >= 8/15 folds each).
 CALL_RESTATE_F40 = GATE and SHOWS_F40_CORE(X) for ANY X in {T1, T2, T3}.  Printed '= True/False'.
 READING (stopping rule, D-066 (k)): CALL True -> "F-40 restated: in-line reuse is not unique to the manuscript (tabular
   writing produces it): <texts>; H-01-tabular opened as a new hypothesis"; GATE True and CALL False -> "no tabular text
   shows (b)+(c): F-40 gains a tabular-genre line"; GATE False -> "uninformative: gate failed (<which>)" (CALL False).
DESCRIPTIVE (not in any call): per text and segmenter all parts, D (s87 distance), battery per T; POWER rows: the same
 profile on (i) LP91 PLANTED seed 1 emitted cores (identity) and (ii) IT2a words (slot), each cut to the token count of
 each tabular text with the ZL3b layout: does the machinery detect (b)+(c) at that size?
FIXTURE (--fx107; synthetic, reads no real data): loader rules on synthetic strings (entry splitting, head removal,
 hyphen join, Lull re-cut, º removal) and (b)+(c) detection on S91.fx_world LP91 PLANTED cores cut to 1,300 / 10,000
 tokens vs Markov prose (S97.fx_prose).  Writes runs/s107/fixture_<stamp>.txt only.
DESIGN REVISIONS (at most two, pre-freeze):
 REVISION 1 (after fixture run 1, 13:48:31 PDT: FAIL, FXb only; FXa, FXc, FXd PASS): the T2 rule dropped every line with
   <= 2 tokens, which also dropped short continuation lines ('macho & epati.' after 'Valet do/').  Now only a line that
   stands alone between blank lines (catchword, margin) is dropped, and never one that a join mark continues.  The FXb
   synthetic catchword is placed alone between blank lines, as catchwords stand in the OCR.  Nothing else changed.
FIXTURE OUTCOME BEFORE THE FREEZE (runs/s107/fixture_*.txt, run 2, 13:49:00 PDT): PASS (FXa-FXc loaders; FXd planted
 (b)+(c) detected at 1,300 and 10,000 tokens, Markov prose not).
COMPUTE: profiles on the GPU (torch cuda) in the main process; battery in 2 spawn workers, BelowNormal, OMP threads 1;
 free RAM >= 4 GB checked at start and before the pool (else STOP, exit 2).  Budget 2 CPU-hours.
Writes ONLY results_s107.txt (fixture: runs/s107/fixture_<stamp>.txt) and runs/s107/ sidecars.  Never overwrites a results
 file: if results_s107.txt exists the run stops (an amendment is results_s107_amend1.txt via --amend1).
Run: python -I s107_tabular_medical_reference.py    Fixture: --fx107    Stub helper: --list-files
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import html  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import OrderedDict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import torch  # noqa: E402

import s97_language_rescue_controls as S97  # noqa: E402

S87, S91, S67, S80, S57 = S97.S87, S97.S91, S97.S67, S97.S80, S97.S57
SlotSegmenter = S97.SlotSegmenter

SELF = ROOT / "s107_tabular_medical_reference.py"
STUB = ROOT / "s107_tabular_medical_reference.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s107"
TAB = ROOT / "data" / "controls_tabular"
FIXTURE = "--fx107" in sys.argv
LIST_FILES = "--list-files" in sys.argv
AMEND1 = "--amend1" in sys.argv
OUT = ((RUN_DIR / f"fixture_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt") if FIXTURE
       else ROOT / ("results_s107_amend1.txt" if AMEND1 else "results_s107.txt"))
SEED = 20261107
N_TOT, NB, N_MATCH = S97.N_TOT, S97.NB, S97.N_MATCH
MIN_FREE_GB = S97.MIN_FREE_GB
TRANSLITS = S97.TRANSLITS
SRC_T1 = TAB / "raw_tacuinum_medimanus" / "tacuinum_sanitatis.html"
SRC_T2 = TAB / "raw_degradibus" / "BIUSante_00128x01_djvu.txt"
SRC_T3 = TAB / "raw_lull_1515" / "ARes54311_djvu.txt"
DATA_FILES = ([f"data/translit/{f}.meta.json" for f in TRANSLITS.values()]
              + ["data/controls/latin_augustine.txt", "runs/s97/profiles.csv", "results_s97.txt",
                 "data/controls_tabular/README.md"]
              + [p.relative_to(ROOT).as_posix() for p in (SRC_T1, SRC_T2, SRC_T3)])
S97_PC2_ROW = ("PC2_VOY_IT2a_as_control", "slot")
LULL_ALPH = set("bcdefghikt")
ORD = {"primo", "fecundo", "secundo", "tertio", "quarto", "fine", "initio", "medio"}
log: list[str] = []
T0 = time.time()


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


_ORIG_MEASURE = S97.measure_job


def measure_job_safe(job):
    try:
        return _ORIG_MEASURE(job)
    except Exception as e:  # noqa: BLE001
        return job["key"], None, repr(e)[:200], 0.0


S97.emit, S97.flush, S97.measure_job = emit, flush, measure_job_safe


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stub_files():
    mods = set(S97.local_modules()) | {SELF.name}
    return sorted(mods) + list(DATA_FILES)


def stub_match():
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
    missing = [m for m in stub_files() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"


# ======================================================================= loaders (rules in the docstring)
def tok(s):
    return S87.tokens_norm(s.replace("º", " ").replace("ª", " "))


def t1_lines(text):
    paras = re.findall(r'<p style="text-align:justify[^"]*">(.*?)</p>', text, flags=re.S)
    out = []
    for p in paras:
        t = tok(html.unescape(re.sub(r"<[^>]+>", " ", p)))
        if t:
            out.append(t)
    return out


def is_head(raw):
    letters = [c for c in raw if c.isalpha()]
    comp = re.sub(r"[^A-Za-z]", "", raw).upper()
    return (any(k in comp for k in ("GRADIB", "RADIBV", "LIBER", "DIBER")) and len(tok(raw)) <= 12
            and bool(letters) and sum(c.isupper() for c in letters) >= 0.6 * len(letters))


def starts_upper(raw):
    t = raw.lstrip(" .,'\"*-|")
    return bool(t) and t[0].isupper()


def degree_start(raw):
    f = tok(raw)[:10]
    return any(("grad" in w) or w == "gra" for w in f) or any(f[i] == "in" and f[i + 1] in ORD for i in range(len(f) - 1))


def t2_lines(raw_lines, a, b):
    lines, prev_blank = [], True
    seg = raw_lines[a:b]
    for i, ln in enumerate(seg):
        if not ln.strip():
            prev_blank = True
            continue
        alone = (i == 0 or not seg[i - 1].strip()) and (i + 1 >= len(seg) or not seg[i + 1].strip())   # REVISION 1
        joined = bool(lines) and lines[-1][0][-1] in "-/^=¬"
        if is_head(ln) or (len(tok(ln)) <= 2 and alone and not joined):
            continue
        lines.append((ln.rstrip(), prev_blank))
        prev_blank = False
    entries, cur = [], None
    for ln, pb in lines:
        if cur is None or (starts_upper(ln) and (pb or degree_start(ln))):
            if cur is not None:
                entries.append(cur)
            cur = ""
        cur += ln[:-1] if ln[-1] in "-/^=¬" else ln + " "
    if cur is not None:
        entries.append(cur)
    return [t for t in (tok(e) for e in entries) if t]


def t2_load():
    L = SRC_T2.read_text(encoding="utf-8", errors="replace").splitlines()
    a = next(i for i, ln in enumerate(L) if i > 19800 and "GRADIBVS" in ln) + 1
    b = next(i for i, ln in enumerate(L) if "Liber graduum finit" in ln)
    return t2_lines(L, a, b), (a, b)


def t3_row(ln):
    letters = re.sub(r"[^A-Za-z ]", " ", ln).lower()
    lt = letters.replace(" ", "")
    if len(lt) < 4 or sum(c in LULL_ALPH for c in lt) / len(lt) < 0.9:
        return None
    toks = [w for w in letters.split() if len(w) > 1]
    j = "".join(toks)
    if j and len(j) % 4 == 0:
        toks = [j[i:i + 4] for i in range(0, len(j), 4)]
    return toks or None


def t3_load():
    L = SRC_T3.read_text(encoding="utf-8", errors="replace").splitlines()
    return [r for r in (t3_row(ln) for ln in L[18100:18600]) if r]


# ======================================================================= profile wrapper
def profile_safe(name, pages, segf, seed):
    """S97.profile_g; if the order or locality step raises on a small text, (b)/(c) come from S87.repetition alone and
    (a)/(d) are NaN (so S87.c1 marks them False)."""
    try:
        return S97.profile_g(name, pages, segf, N_MATCH, seed), None
    except Exception as e:  # noqa: BLE001
        toks = [w for _, ls in pages for ln in ls for w in ln]
        seg = segf(toks)
        cache = {}

        def core_of(w):
            c = cache.get(w)
            if c is None:
                c = cache[w] = seg.segment(w)[1]
            return c
        cores, pg, lid, blk, ids = S87.flatten(pages, core_of)
        rep = S87.repetition(cores, pg, lid, S87.N_SHUF_R, seed)
        nan = float("nan")
        return dict(name=name, tokens=len(toks), pages=len(pages), lines=int(lid.max()) + 1, types=len(ids),
                    empty=int((cores < 0).sum()), core_share=float((cores >= 0).mean()), te_tok=0, matched_tokens=0,
                    order={K: dict(mm=nan, p=nan, plug=nan) for K in S87.KS}, rep=rep,
                    loc=dict(ratio=nan, lo=nan, hi=nan), blocks=int(blk.max()) + 1, secs=0.0), repr(e)[:160]


def bc(p, lb):
    _, comp, _ = S97.flags(p, lb)
    return comp["b_Rwithin"] and comp["c_Rcross<Rwithin"]


def ntok(pages):
    return sum(len(ln) for _, ls in pages for ln in ls)


# ======================================================================= fixture
def run_fixture():
    emit("S107 FIXTURE (synthetic only; no real data read)")
    emit(f"date: {S87.clock()}  device: {S87.DEV}; below_normal={S87.below_normal()}")
    emit(f"s107 sha256={sha256(SELF)}  stub_match={stub_match()}")
    ok = True
    h = ('<p class="mb-6"><strong>Ficus</strong></p><p style="text-align:justify;width:640px">Ficus. <strong>Complexio:</strong> '
         'calida et humida in 1º gradum.</p><p style="text-align:justify">Uue. <strong>Electio:</strong> albe.</p>')
    l1 = t1_lines(h)
    f1 = l1 == [["ficus", "complexio", "calida", "et", "humida", "in", "gradum"], ["uue", "electio", "albe"]]
    emit(f"FXa T1 paragraphs -> lines, heading not used, º removed: {l1} -> {'PASS' if f1 else 'FAIL'}"); ok &= f1
    raw = ["", "Rofa frigida in primo gradu, ficca in fine fecundi. Valet do/", "macho & epati.", "",
           "ta cum polline hordei valet contra calorem.", "DE GRADIBVS LIBER. 545", "Viola frigida in fine primi gradus, humi^",
           "da in initio fecundi.", "", "Kebuli funt qui nafcuntur in India, frigidi in primo gradu.", "", "fenfus", "",
           "Qui frigidi funt in primo gradu purgant."]
    l2 = t2_lines(raw, 0, len(raw))
    want2 = [["rofa", "frigida", "in", "primo", "gradu", "ficca", "in", "fine", "fecundi", "valet", "domacho", "epati", "ta", "cum",
              "polline", "hordei", "valet", "contra", "calorem"],
             ["viola", "frigida", "in", "fine", "primi", "gradus", "humida", "in", "initio", "fecundi"],
             ["kebuli", "funt", "qui", "nafcuntur", "in", "india", "frigidi", "in", "primo", "gradu"],
             ["qui", "frigidi", "funt", "in", "primo", "gradu", "purgant"]]
    f2 = l2 == want2
    emit(f"FXb T2 entry rule (blank+capital, degree formula, continuation, head, catchword, hyphen join): {len(l2)} entries "
         f"-> {'PASS' if f2 else 'FAIL ' + str(l2)}"); ok &= f2
    r3 = [t3_row(x) for x in [": bc tc bctc bctcbctc", "bctb bctb bctb bctb", "Ars magna tabula", "i bftb bgtb bbtbbitb", "bcft bcg bcb bef"]]
    want3 = [["bctc", "bctc", "bctc", "bctc"], ["bctb", "bctb", "bctb", "bctb"], None, ["bftb", "bgtb", "bbtb", "bitb"],
             ["bcft", "bcg", "bcb", "bef"]]
    f3 = r3 == want3
    emit(f"FXc T3 row filter and 4-letter re-cut: {r3} -> {'PASS' if f3 else 'FAIL'}"); ok &= f3
    flush()
    names, glob, B, spec = S91.fx_world()
    prod = S91.LP91(glob, B)
    prod.set_params(S91.PLANTED)
    cB = S91.cut(prod.text(spec, 2))
    pr = S91.cut(S97.fx_prose(names, spec, 4))
    lens = [len(ln) for _, ls in cB for ln in ls]
    pnl = [len(ls) for _, ls in cB]
    lb = (0.0, 2.0)
    for n in (1300, 10000):
        pp = S87.layout(None, True, cB, lens, pnl, n_tot=n)
        qq = S87.layout(None, True, pr, lens, pnl, n_tot=n)
        p, e1 = profile_safe(f"FX_LP91_n{n}", pp, S80.identity_seg_factory, SEED + n)
        q, e2 = profile_safe(f"FX_prose_n{n}", qq, S80.identity_seg_factory, SEED + n + 1)
        fp, fq = bc(p, lb), bc(q, lb)
        emit("  " + S97.fmt(p, lb) + (f" [{e1}]" if e1 else ""))
        emit("  " + S97.fmt(q, lb) + (f" [{e2}]" if e2 else ""))
        emit(f"FXd n={n}: planted (b)+(c) {fp} (want True); Markov prose (b)+(c) {fq} (want False) -> "
             f"{'PASS' if (fp and not fq) else 'FAIL'}")
        ok &= fp and not fq
        flush()
    emit(f"FIXTURE {'PASS' if ok else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


# ======================================================================= main
def main():
    if LIST_FILES:
        for m in stub_files():
            print(m)
        return
    if FIXTURE:
        run_fixture()
        return
    if OUT.exists():
        print(f"STOP: {OUT.name} exists; never overwrite (use --amend1 for an amendment run)")
        raise SystemExit(3)
    emit("S107: tabular medical / combinatory texts vs the F-40 core behaviour (D-066 (k); pre-registered in the docstring)")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; BelowNormal set={S87.below_normal()}; battery workers {S97.N_WORKERS}")
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    fg = S91.free_gb()
    emit(f"free RAM {fg:.1f} GB (need >= {MIN_FREE_GB})")
    if not (fg >= MIN_FREE_GB):
        emit(f"STOP: free RAM {fg:.1f} GB < {MIN_FREE_GB} GB")
        flush()
        raise SystemExit(2)
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH}; order/R shuffles {S87.N_SHUF_ORDER}/{S87.N_SHUF_R}; locality perms {S87.N_PERM_LOC}, "
         f"boot {S87.N_BOOT}; battery N_DRAW {S67.N_DRAW}, fold >= {S97.BAT_MIN_HOLD}/6, >= {S97.BAT_MIN_FOLDS}/15 folds per T; "
         f"MIN_CORE_SHARE {S97.MIN_CORE_SHARE}; s97 seed {S97.SEED}; s107 seed {SEED}")
    flush()

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    def lay_lines(lines, n_tot=N_TOT):
        return S87.layout(lines, True, None, line_lens, page_nl, n_tot)

    # ---- Voynich target (s97 seeds)
    emit("\n=== Voynich target (SlotSegmenter cores, s87 seeds; as s97) ===")
    VOY = OrderedDict()
    for i, T in enumerate(TRANSLITS):
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        pages = S87.layout(None, True, P, line_lens, page_nl)
        VOY[T] = (pages, S97.profile_g(f"VOY_{T}", pages, SlotSegmenter, N_MATCH, S87.SEED + 100 * i))
    lb = S87.loc_band_from([v[1] for v in VOY.values()])
    emit(f"LOCALITY band: [{lb[0]:.4f}, {lb[1]:.4f}] (s97: [0.9074, 1.0499])")
    rw_v = float(np.mean([v[1]["rep"][1]["Rw"] for v in VOY.values()])); rc_v = float(np.mean([v[1]["rep"][1]["Rc"] for v in VOY.values()]))
    for T, (_, p) in VOY.items():
        emit("  " + S97.fmt(p, lb))
    flush()

    # ---- texts
    emit("\n=== building texts ===")
    aug = S87.load_control("latin_augustine.txt")
    t1 = t1_lines(SRC_T1.read_text(encoding="utf-8", errors="replace"))
    t2, (a2, b2) = t2_load()
    t3 = t3_load()
    emit(f"  T1 Tacuinum BnF lat. 9333 (MediManus): {len(t1)} entry lines, {sum(map(len, t1))} tokens")
    emit(f"  T2 Constantinus De gradibus (Basel 1536 OCR lines {a2 + 1}-{b2}): {len(t2)} entry lines, {sum(map(len, t2))} tokens")
    emit(f"  T3 Lull Tabula generalis (1515 OCR): {len(t3)} table rows, {sum(map(len, t3))} tokens")
    allT = list(TRANSLITS)
    TEXTS = OrderedDict()
    TEXTS["PC2_VOY_IT2a_as_control"] = ("gate", VOY["IT2a"][0], ["slot"], ["IT2a"], 0, S97.SEED, "IT2a words, real pages, control path")
    TEXTS["NC_augustine_la"] = ("gate", S87.layout(aug, False, None, line_lens, page_nl), list(S97.SEGS), allT, 1, S97.SEED,
                                "plain Latin prose (Augustine), ZL3b line lengths")
    TEXTS["T1_tacuinum_bnf9333"] = ("tabular", lay_lines(t1), list(S97.SEGS), allT, 11, SEED, "Tacuinum sanitatis, one table entry per line")
    TEXTS["T2_degradibus_const"] = ("tabular", lay_lines(t2), list(S97.SEGS), allT, 12, SEED, "De gradibus, one entry (simple) per line, by source entry boundaries")
    TEXTS["T3_lull_tabula_1515"] = ("tabular", lay_lines(t3), list(S97.SEGS), allT, 13, SEED, "Lull Tabula generalis, one printed table row per line")
    FLAGS = {}
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        nt = ntok(pages)
        fl = []
        if nt < N_TOT:
            fl.append("below 22,500")
        if len(pages) < NB:
            fl.append("pages < 15")
        FLAGS[n] = fl
        emit(f"  {n:26s} {role:8s} tokens {nt:6d} pages {len(pages):4d} lines {sum(len(ls) for _, ls in pages):5d} "
             f"mean line {nt / max(1, sum(len(ls) for _, ls in pages)):5.1f}  {lab}{'  FLAG: ' + '; '.join(fl) if fl else ''}")
    flush()

    # ---- PC1 (as s97)
    emit("\n=== GATE PC1: s91 LP91 at PLANTED " + str(S91.PLANTED) + " on ZL3b lexicon/layout (identity on emitted cores; as s97) ===")
    zp = S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS['ZL3b']}.meta.json")
    segz = SlotSegmenter([w for _, _, ls in zp for l in ls for w in l])
    cz = {}

    def zcore(w):
        c = cz.get(w)
        if c is None:
            c = cz[w] = segz.segment(w)[1]
        return c
    zcp = [(p, q, [[zcore(w) for w in l] for l in ls]) for p, q, ls in zp]
    from collections import Counter
    glob = Counter(c for _, _, ls in zcp for l in ls for c in l if c != "")
    prod = S91.LP91(glob, S91.bigram_of([(p, [[c for c in l if c != ""] for l in ls]) for p, q, ls in zcp]))
    prod.set_params(S91.PLANTED)
    spec = [(p, q, [len(l) for l in ls]) for p, q, ls in zp]
    pc1, lp_pages = [], None
    for s in (1, 2, 3):
        pages = S91.cut(prod.text(spec, S97.SEED + s))
        if s == 1:
            lp_pages = pages
        p = S97.profile_g(f"PC1_LP91_planted_s{s}", pages, S80.identity_seg_factory, N_MATCH, S97.SEED + 10 + s)
        pc1.append(S97.flags(p, lb)[0])
        emit("  " + S97.fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}"))
    PC1 = sum(pc1) >= S97.PC1_MIN
    emit(f"  PC1 Voynich-like on {sum(pc1)}/3 seeds (need >= {S97.PC1_MIN}) -> {'PASS' if PC1 else 'FAIL'}")
    flush()

    # ---- signature profiles
    emit("\n=== signature profiles (C1 flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PR, ERR = OrderedDict(), {}
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        PR[n] = OrderedDict()
        for si, sn in enumerate(segs):
            p, err = profile_safe(f"{n}/{sn}", pages, S97.SEGS[sn], sd + 1000 * xi + 100 * si)
            PR[n][sn] = p
            if err:
                ERR[(n, sn)] = err
            app = p["core_share"] >= S97.MIN_CORE_SHARE
            emit("  " + S97.fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f} | b+c {bc(p, lb)}"
                              f"{'' if app else ' [NOT APPLICABLE: core share < 0.5]'}{' [order/locality not computable: ' + err + ']' if err else ''}"))
            flush()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---- REPRO vs s97 (descriptive)
    emit("\n=== REPRO: gate rows vs runs/s97/profiles.csv (descriptive, 3 decimals: o100 Rw1 Rc1 loc) ===")
    s97rows = {}
    with (ROOT / "runs" / "s97" / "profiles.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            s97rows[(r["text"], r["segmenter"])] = r
    repro_all = True
    for n in ("PC2_VOY_IT2a_as_control", "NC_augustine_la"):
        for sn, p in PR[n].items():
            r = s97rows.get((n, sn))
            mine = (round(p["order"][100]["mm"], 3), round(p["rep"][1]["Rw"], 3), round(p["rep"][1]["Rc"], 3), round(p["loc"]["ratio"], 3))
            theirs = tuple(round(float(r[k]), 3) for k in ("o100", "Rw1", "Rc1", "loc")) if r else None
            same = mine == theirs
            repro_all &= same
            emit(f"  {n}/{sn}: s107 {mine} s97 {theirs} -> {same}")
    emit(f"  REPRO all gate rows = {repro_all}")
    flush()

    # ---- power rows (descriptive)
    emit("\n=== POWER (descriptive): planted LP91 seed 1 (identity) and IT2a (slot) cut to each tabular text's size ===")
    POW = OrderedDict()
    for n, (role, pages, *_r) in TEXTS.items():
        if role != "tabular":
            continue
        nt = ntok(pages)
        for lab2, src, segf, sd in (("LP91", lp_pages, S80.identity_seg_factory, SEED + 7), ("IT2a", VOY["IT2a"][0], SlotSegmenter, SEED + 8)):
            pp = S87.layout(None, True, src, line_lens, page_nl, n_tot=nt)
            p, err = profile_safe(f"PWR_{lab2}_n{nt}", pp, segf, sd + nt)
            POW[(n, lab2)] = bc(p, lb)
            emit("  " + S97.fmt(p, lb, f" | b+c {bc(p, lb)} (size of {n}){' [' + err + ']' if err else ''}"))
            flush()

    # ---- battery
    emit("\n=== s67 slot battery (text block b vs real Voynich fold folds[b]) ===")
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    emit(f"  folds ({len(folds)}): {' '.join(folds)}")
    assert len(folds) == NB
    jobs = S97.ref_jobs(ref, folds)
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        jobs += S97.ctl_jobs(n, xi + 1, pages)
    M = S97.run_pool(jobs, "battery")
    bad = {k: v[1] for k, v in M.items() if v[0] is None}
    if bad:
        emit(f"  {len(bad)} Measured jobs raised: " + "; ".join(f"{k}: {e}" for k, e in list(bad.items())[:6]))
    BAT = OrderedDict()
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        keys = [("CTL", n, b) for b in range(NB)] + [("REF", T, b) for T in Ts for b in range(NB)]
        if any(M[k][0] is None for k in keys):
            BAT[n] = None
            emit(f"  {n:26s} battery NOT ASSESSABLE (a Measured job raised; battery = False)")
            continue
        try:
            BAT[n] = S97.battery_score(n, Ts, M, ref, folds, pages)
        except Exception as e:  # noqa: BLE001
            BAT[n] = None
            emit(f"  {n:26s} battery NOT ASSESSABLE ({repr(e)[:120]}; battery = False)")
            continue
        for T, r in BAT[n].items():
            emit(f"  {n:26s} " + S97.bat_line(T, r))
    flush()

    # ---- calls
    emit("\n=== calls ===")
    FULL, SHOWS, DESC = OrderedDict(), OrderedDict(), OrderedDict()
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        app = [sn for sn in segs if PR[n][sn]["core_share"] >= S97.MIN_CORE_SHARE]
        sig = {sn: S97.flags(PR[n][sn], lb) for sn in segs}
        sig_ok = bool(app) and all(sig[sn][0] for sn in app)
        bat_ok = BAT[n] is not None and all(BAT[n][T]["holds"] for T in Ts)
        FULL[n] = sig_ok and bat_ok
        bcs = {sn: bc(PR[n][sn], lb) for sn in segs}
        SHOWS[n] = any(bcs[sn] for sn in app)
        DESC[n] = dict(role=role, flags=FLAGS[n], tokens=ntok(pages), applicable=app, sig={sn: sig[sn][2] for sn in segs},
                       bc=bcs, sig_ok=sig_ok, battery_ok=bat_ok,
                       battery=(None if BAT[n] is None else {T: BAT[n][T]["folds_ok"] for T in Ts}))
        btxt = "NOT ASSESSABLE" if BAT[n] is None else " ".join(f"{T} {BAT[n][T]['folds_ok']}/15" for T in Ts)
        emit(f"  {n:26s} {role:8s} signature " + " ".join(f"{sn}:{sig[sn][2]}" for sn in segs) +
             f" (applicable {','.join(app)}) -> {sig_ok}; battery {btxt} -> {bat_ok}; FULL_VOYNICH_LIKE = {FULL[n]}; "
             f"SHOWS_F40_CORE (b+c) = {SHOWS[n]} [" + " ".join(f"{sn}:{bcs[sn]}" for sn in segs) + "]"
             + (f"  FLAG: {'; '.join(FLAGS[n])}" if FLAGS[n] else ""))
    PC2 = FULL["PC2_VOY_IT2a_as_control"]
    NC = not FULL["NC_augustine_la"]
    GATE = PC1 and PC2 and NC
    emit(f"  GATE: PC1 {PC1}; PC2 {PC2}; NC (plain Latin not Voynich-like) {NC} -> GATE = {GATE}  (REPRO descriptive = {repro_all})")
    hits = [n for n, d in DESC.items() if d["role"] == "tabular" and SHOWS[n]]
    CALL = GATE and bool(hits)
    emit(f"  CALL_RESTATE_F40 = {CALL}")
    if not GATE:
        why = [k for k, v in (("PC1", PC1), ("PC2", PC2), ("NC", NC)) if not v]
        reading = f"uninformative: gate failed ({', '.join(why)})"
    elif CALL:
        reading = ("F-40 restated: in-line reuse is not unique to the manuscript (tabular writing produces it): "
                   + ", ".join(hits) + "; H-01-tabular opened as a new hypothesis")
    else:
        reading = "no tabular text shows (b)+(c): F-40 gains a tabular-genre line"
    emit(f"\nVERDICT: CALL_RESTATE_F40 = {CALL}: {reading}")

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    sfx = "_amend1" if AMEND1 else ""
    with (RUN_DIR / f"profiles{sfx}.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "segmenter", "tokens", "types", "core_share", "te_tok", "o100", "p100", "o200", "Rw1", "pRw1", "Rc1",
                    "loc", "loc_lo", "loc_hi", "C1", "flags", "bc", "D"])
        rows = [(f"VOY_{T}", "slot", v[1]) for T, v in VOY.items()] + [(n, sn, p) for n in PR for sn, p in PR[n].items()]
        for n, sn, p in rows:
            o, r, l = p["order"], p["rep"], p["loc"]
            ok, _, fl = S97.flags(p, lb)
            w.writerow([n, sn, p["tokens"], p["types"], f"{p['core_share']:.4f}", p["te_tok"], f"{o[100]['mm']:.6f}", f"{o[100]['p']:.4f}",
                        f"{o[200]['mm']:.6f}", f"{r[1]['Rw']:.4f}", f"{r[1]['pw']:.4f}", f"{r[1]['Rc']:.4f}", f"{l['ratio']:.4f}",
                        f"{l['lo']:.4f}", f"{l['hi']:.4f}", ok, fl, bc(p, lb), f"{S87.distance(p, lb, rw_v, rc_v)[0]:.3f}"])
    with (RUN_DIR / f"battery{sfx}.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "T", "fold", "n"] + S67.PREDS + ["small", "type_ratio"])
        for n in BAT:
            if BAT[n] is None:
                continue
            for T, r in BAT[n].items():
                for x in r["rows"]:
                    w.writerow([n, T, x["Q"], x["n"]] + [x["holds"][k] for k in S67.PREDS] + [x["small"], f"{x['type_ratio']:.4f}"])
    with (RUN_DIR / f"texts{sfx}.txt").open("w", encoding="utf-8", newline="\n") as fh:
        for n, (role, pages, *_r) in TEXTS.items():
            if role == "tabular":
                for pid, ls in pages:
                    for ln in ls:
                        fh.write(f"{n}\t{pid}\t{' '.join(ln)}\n")
    (RUN_DIR / f"calls{sfx}.json").write_text(json.dumps(dict(loc_band=lb, order_band=S87.ORDER_BAND, PC1=PC1, PC1_seeds=pc1, PC2=PC2,
                                                              NC=NC, GATE=GATE, REPRO=repro_all, CALL_RESTATE_F40=CALL, SHOWS=SHOWS,
                                                              FULL=FULL, desc=DESC, power={f"{a}|{b}": v for (a, b), v in POW.items()},
                                                              errors={f"{a}|{b}": v for (a, b), v in ERR.items()}, verdict=reading),
                                                         indent=1, default=str), encoding="utf-8", newline="\n")
    emit(f"\nsidecars: runs/s107/profiles{sfx}.csv, runs/s107/battery{sfx}.csv, runs/s107/texts{sfx}.txt, runs/s107/calls{sfx}.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


if __name__ == "__main__":
    main()
