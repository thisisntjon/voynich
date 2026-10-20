"""S102 (D-066 (h); Jon's hypothesis: medical recipes concealed by a period cipher): does a cipher documented in early
15th-century Italian chancery practice, applied to a period-appropriate recipe / remedy text, reproduce the
manuscript's JOINT profile (F-40 four-part signature + s67 slot battery + F-04 within-line rhythm + h2)?

RIVALS (D-066 (h)): H-14 + H-06 (a codebook / nomenclator with a line-held variant reproduces the joint profile) vs
 H-02/H-03 (substitution or homophonic over letters: predicted to fail) vs H-05/H-07 (no encoding of a real text
 reproduces in-line core reuse with weak order).

PLAINTEXTS (provenance, URLs, licences, sha256: data/controls_period/README.md; original spelling kept):
 P1_la  Latin medical: the five CREMMA 'Medic' manuscripts (CLM13027, Egerton821, H318, Latin16195, Phi_10a135;
        data/controls_realline/cremma_all_marks.meta.json, `_marks` family: abbreviation signs and letters kept as
        written; REAL MANUSCRIPT LINES), followed by Macer Floridus 'De viribus herbarum'
        (data/controls/latin_macer_floridus.txt; REAL VERSE LINES; '##' headers and the Wikisource artefact line
        'recensere' dropped) until N_TOT tokens.
 P2_it  northern-Italian vernacular recipe text (see PERIOD_SRC['P2_it'] and the README); printed-edition lines are
        not source lines, so the tokens are RE-LINED to ZL3b line lengths (s87 layout rule, ZL3b page sizes).
 P3_de  southern German remedy / cookery text (PERIOD_SRC['P3_de']); RE-LINED to ZL3b line lengths likewise.
 Each plaintext is cut to N_TOT = 22,500 tokens (s87 size) by S87.layout; a text shorter than N_TOT is flagged and the
 cell is not scored (the s87 pipeline needs 15 blocks of 1,500).

PLAINTEXT SYMBOLS (what is enciphered; one rule for all texts): NFD; a base letter is lower-cased and reduced to the
 23-letter period alphabet of s50 ("abcdefghiklmnopqrstuxyz": j->i, v->u, w->uu, sharp s->ss, ae/oe ligatures split,
 long s->s, thorn->th, eth->d, yogh->g); abbreviation-letters (p/q with stroke or flourish, con-sign, r rotunda with
 stroke, etc., table ABBR_LETTERS) -> base letter + '~'; Tironian et -> '&'; private-use glyphs (CREMMA's MUFI
 code points) -> '~'.  Combining marks: in P1's CREMMA part (diplomatic transcription) every mark-bearing glyph unit
 gets one '~' after its base letter (the scribe's abbreviation); in edited texts (Macer, P2, P3) only abbreviation
 marks are kept as '~' (combining tilde U+0303, macron U+0304, combining Latin small letters U+0363-U+036F); other
 marks (editorial accents, circumflexes of normalised MHG) are dropped.  Digits, punctuation, pilcrows dropped;
 a token with no symbol left is dropped.  Plaintext alphabet = 23 letters + '~' + '&' = 25 symbols.

ENCODINGS (one key per plaintext x encoding, rng = default_rng([SEED, plaintext index, encoding index])):
 Glyph inventory GLYPHS = 25 EVA lower-case letters "oehyacdiklrstnqpmfgxvzjbu" + 26 upper-case letters (single code
 points; segmenters, h2 and word length count code points).
 E1 monoalphabetic + nulls: the first 27 glyphs, shuffled; 25 -> one per plaintext symbol, 2 nulls (27 glyphs: a
    Voynich-like inventory).  Before each plaintext symbol a null is inserted with probability P_NULL = 0.05 (null
    chosen uniformly).
 E2 homophonic + nulls (Milanese chancery style): plaintext symbols ranked by frequency in that plaintext: ranks 1-3
    get 4 homophones, ranks 4-6 get 3, ranks 7-10 get 2, the rest 1 (25 + 9 + 6 + 4 = 44 cipher glyphs) plus 2
    nulls = the first 46 glyphs, shuffled; each occurrence picks a homophone uniformly; nulls as E1 (P_NULL 0.05).
 E3 nomenclator: the N_CODE = 200 most frequent word types of the 22,500-token plaintext cut that are not function
    words (FUNC_LA / FUNC_IT / FUNC_DE, reduced by the same symbol rule) and have >= 2 symbols get a code group:
    ranks 1-50 two glyphs, 51-200 three glyphs, drawn uniformly from E2's 44 letter glyphs, unique.  Every other word
    is spelled with E2 (same key).  If a spelled form equals a code group, the homophones are redrawn (<= 50 tries;
    remaining collisions counted).  Code groups carry no nulls.
 E4 line-held nomenclator: as E3, but every code word has V_CODE = 3 variant code groups (all unique); per line one
    variant index v ~ U{0,1,2} (rng [SEED, 400 + plaintext index, line index]) is used for every code word on that
    line.  Spelled words as E2.
 Word spaces are kept as word boundaries (one plaintext token -> one cipher token); lines as stated per plaintext.

GATES (before any cell is read; GATE = G1 and G2):
 G1 recovery: the planted decoder (known key: codebook lookup, else glyph -> symbol with nulls dropped) recovers
    >= REC_MIN = 0.80 of the tokens (exact match to the reduced plaintext token) for EVERY encoding on EVERY
    plaintext.  Descriptive (not gating): the s86 solver (S86.fast_solve_stream, s50 5-gram Witten-Bell LM of the
    matching language: latin / italian / german per S50.LANGS; Half A = first half of the glyph stream, Half B =
    second) on E1 and E2: Half-B letter accuracy (nulls and '~' '&' positions count as misses).
 G2 the s97 gate reproduces with s97's code and constants (imported): PC1 s91 LP91 at PLANTED on ZL3b Voynich-like on
    >= 2/3 seeds; PC2 IT2a-as-control full s97 call True; NC plain Latin (Augustine) full s97 call False.

SCORING PER CELL (12 = P1..P3 x E1..E4; plus descriptive REF rows = each unencoded plaintext):
 SIG  F-40 four-part signature (S87.c1 with the s87 amendment-1 ORDER_BAND and the LOCALITY band recomputed from
      VOY ZL3b/RF1b/IT2a SlotSegmenter cores as in s97) on EVERY APPLICABLE segmenter of s97 (identity, SlotSegmenter,
      Seg_Affix2; applicable iff core share >= 0.5).  SIG holds iff all four parts hold on every applicable segmenter.
 BAT  s67 slot battery exactly as s97 (S97.ctl_jobs / S97.battery_score; fold holds iff >= 4/6 predictions;
      battery holds iff >= 8/15 folds on each of ZL3b, RF1b, IT2a).
 RHY  F-04 within-line lag-1 word-length Moran I (S21.analyze: 999 within-line shuffles, seed per row):
      excess = I - median(null); holds iff excess > 0 AND permutation p < 0.05.
 H2   conditional character entropy h2 (a1_profile.char_entropies on the 22,500 tokens joined by spaces);
      Voynich band = [min h2(VOY ZL3b, RF1b, IT2a) - 0.10, max + 0.10] on the same 22,500-token cuts; holds iff inside.
 VOYNICH-LIKE(cell) = SIG and BAT and RHY and H2   (the D-066 (h) rule; thresholds not to be changed).
 PRE-REGISTERED CALL: CALL_S102_PERIOD_CIPHER = GATE and (VOYNICH-LIKE for ANY of the 12 cells).  Printed "= True/False".
 READING: GATE False -> "uninformative: gate failed (<which>)" (CALL printed False); GATE True and CALL False ->
   "no cell is Voynich-like: 'period cipher over vernacular recipes' is closed within the tested constructions
   (D-066 (h) stopping rule; no parameter sweeps)"; CALL True -> "Voynich-like cells: <cells>; next step per D-066 (h):
   constrained decipherment of the manuscript with that encoding family and language as the prior".
 Descriptive: failing parts per segmenter, s87 distance D, battery per T, rhythm I / null median / p, h2, Voynich
   rows for rhythm and h2, the full D-066 rule on PC2 (IT2a as control).
FIXTURE (--fx102; synthetic only, reads no real data; writes runs/s102/fixture_<stamp>.txt):
 FXa encodings on a pseudo-Latin plaintext (S97.pseudo_latin, 3,000 lines, symbols '~' '&' injected at 3 %):
     planted-decoder recovery >= 0.99 for E1..E4; observed null rate in [0.04, 0.06] for E1/E2; E2 homophone counts
     4,4,4,3,3,3,2,2,2,2,1...; E4 every line uses one variant index for all its code tokens; E3/E4 code-token share > 0.
 FXb rhythm: IID word lengths -> |excess| < 0.02; lines with ascending lengths -> excess > 0 and p < 0.05.
 FXc h2 on a deterministic two-symbol alternation ("ab ab ...") < 0.5 bit.
 FXd the 2-worker pool returns both smoke jobs (S97.measure_job on S91.fx_world words).
 FXe (descriptive) S97.profile_g on the fixture E1 and E4 texts (identity).
DESIGN REVISIONS (at most two, pre-freeze): none.  (Pre-run code fixes, not design: a fixture-only list-comprehension
 bug and a mangled hyphen-join regex were fixed before the first fixture result.)
FIXTURE OUTCOME BEFORE THE FREEZE (runs/s102/fixture_*.txt, 12:53:33 PDT): PASS.  FXa: recovery 1.0000 for E1..E4, null
 rate 0.050, homophones 4,4,4,3,3,3,2,2,2,2, E3/E4 code-token share 0.485, line-held True; FXb IID excess +0.0156
 (p 0.015) and ascending +0.704 (p 0.001); a scratch calibration over 20 further IID seeds gave 2/20 p < 0.05 (null
 calibrated; the fixture seed's low p is chance).  FXc, FXd PASS.  FXe (descriptive): fixture E1 identity C1 YnYY,
 E4 identity nYYY (R_within 1.81: the line-held variant manufactures in-line code-group reuse).
Disclosed pre-freeze looks at real data: plaintext token counts and a few sample tokens of P1 (CREMMA Medic 18,096
 tokens + Macer), P2 (24,531 tokens), P3 (58,675 tokens incl. the Megenberg fill); short OCR samples of the
 downloads; free RAM.  No statistic was computed on any real or encoded text.
COMPUTE: profiles on the GPU (torch cuda) in the main process; battery in N_WORKERS = 2 spawn workers at BelowNormal,
 OMP threads 1; free RAM >= 4 GB checked before each pool.  Limit 4 CPU-hours.
OUTPUT: results_s102.txt (never overwritten: if it exists the run stops unless --amend1, which writes
 results_s102_amend1.txt and stops if that exists) and runs/s102/ sidecars.
Run: python -I s102_period_ciphers_recipes.py     Fixture: --fx102     Stub helper: --list-locals
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import unicodedata  # noqa: E402
from collections import Counter, OrderedDict  # noqa: E402
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

import a1_profile as A1  # noqa: E402
import s21_moran_realline as S21  # noqa: E402
import s50_solver_ladder as S50  # noqa: E402
import s86_sticky_table_solver_and_triangulation as S86  # noqa: E402
import s97_language_rescue_controls as S97  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

S87, S91, S67, S80 = S97.S87, S97.S91, S97.S67, S97.S80
SOLV = S86.S   # s50_solver

SELF = ROOT / "s102_period_ciphers_recipes.py"
STUB = ROOT / "s102_period_ciphers_recipes.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s102"
FIXTURE = "--fx102" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
AMEND = "--amend1" in sys.argv
SEED = 20261102
N_TOT, NB = S87.N_TOT, S87.NB
N_MATCH = S97.N_MATCH
MIN_CORE_SHARE = S97.MIN_CORE_SHARE
REC_MIN = 0.80
H2_PAD = 0.10
RHY_P = 0.05
P_NULL = 0.05
N_CODE = 200
N_CODE_SHORT = 50
V_CODE = 3
HOMO_PLAN = [4, 4, 4, 3, 3, 3, 2, 2, 2, 2]
N_WORKERS = 2
MIN_FREE_GB = 4.0
TRANSLITS = S97.TRANSLITS
GLYPHS = list("oehyacdiklrstnqpmfgxvzjbu") + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
PLAIN_ALPHA = list(SOLV.ALPHA) + ["~", "&"]
MEDIC = ["CLM13027", "Egerton821", "H318", "Latin16195", "Phi_10a135"]
SOLVER_LANG = {"P1_la": "latin", "P2_it": "italian", "P3_de": "german"}
# P2 / P3 sources: file (under data/controls_period/raw_*), 1-based inclusive body line ranges, line-drop regex,
# token-drop regex.  Filled from the download report BEFORE the freeze (see README).
PERIOD_SRC = OrderedDict([
    ("P2_it", dict(files=["data/controls_period/raw_it/librodicucinade00fratgoog_djvu.txt",
                          "data/controls_period/raw_it/b21525213_djvu.txt"],
                   ranges=[[(520, 2972)], [(1704, 4334)]],
                   drop_line=r"^\s*\(\d+\)|Digitized by|LIBRO DI CUCINA|^[^a-z]*$",
                   drop_tok=r"^\s*[IVXLCm]+\s*\.|\[\d+\]",
                   label="Anonimo Veneziano 'Libro di cucina del sec. XIV' (Venetian, Frati 1899), then Tuscan 'Il libro "
                         "della cucina del sec. XIV' (Zambrini 1863) to fill")),
    ("P3_de", dict(files=["data/controls_period/raw_de/bub_gb_I0QSAAAAYAAJ_djvu.txt",
                          "data/controls_period/raw_de/Buoch_von_guoter_Spise_rendered.txt",
                          "data/controls_period/raw_de/b24880681_djvu.txt"],
                   ranges=[[(528, 3152)], [(98, 601)], [(21844, 27770)]],
                   drop_line=r"^\s*\d+\.\s|^\s*[*»]?\d*\)|Digitized by|\(Pfeiffer\)|^[^a-zäöüâêîôû]*$",
                   drop_tok=r"\[(WS )?[0-9IVX]+\]|^\s*\(?\d+\.\)",
                   label="Pfeiffer 'Zwei deutsche Arzneibuecher' (Zuercher Arzneibuch, Alemannic 12th c.; Bavarian-Austrian 13th c.; "
                         "1863), then 'Daz buoch von guoter spise' (Wuerzburg c.1350; Wikisource), then Megenberg 'Buch der Natur' "
                         "IV-V (Bavarian c.1350; Pfeiffer 1861) to fill")),
])
ABBR_LETTERS = {"ꝑ": "p~", "ꝓ": "p~", "ꝕ": "p~", "ꝗ": "q~", "ꝙ": "q~", "ꝯ": "c~", "ꝝ": "r~", "ẜ": "s~", "ꝟ": "u~",
                "ꝫ": "~", "ꝭ": "~", "ꝰ": "~", "ꝸ": "~", "ꝵ": "r~", "ꝶ": "r~", "ꝱ": "d~", "ꝲ": "l~", "ꝳ": "m~",
                "ꝴ": "n~", "ꞇ": "t~", "ꝏ": "oo", "ꝛ": "r", "ſ": "s", "ß": "ss", "æ": "ae", "œ": "oe", "þ": "th",
                "ð": "d", "ȝ": "g", "ı": "i", "ȷ": "i", "ƒ": "f", "ꝺ": "d", "ꞃ": "r", "ꞅ": "s", "ꝼ": "f", "ᵹ": "g"}
ABBR_MARKS = {0x0303, 0x0304} | set(range(0x0363, 0x0370))
FUNC_LA = S97.LAT_FUNC
FUNC_IT = set("""e et ed o od a ad al alla alle allo agli ai al la le lo li gli i il el de del della delle dello dei
degli di da dal dalla dalle dai in im con co cum per pe che chi ch se si ne non no un uno una ogni come chome como cosi
cossi così poi poy piu più ma mo anche ancho ancora sono son è e era essere sia fia fa fi su sopra sotto fra tra ço zo
quando quanto tanto questo questa questi queste quello quella quelli quelle quel cio ciò lui lei loro esso essa
dela dele delo deli dal dali ala ale alo ali nel nela nella nelle cho chol chon cola colla qual quale quali sí sì
ben bene tuto tutto tutta tutti tutte et""".split())
FUNC_DE = set("""und unde unt vnd vnde vnt der die diu daz das dem den des ein eine einen einem einer eines er ez es si
sie in im ir mit von vone zu ze zuo zů uf uff vf auf an ane ab als alz also so sô wenne wenn wan wann dann denne dar
da ist sint sind wirt wird werde nit nicht niht ouch auch oder ob man sein sin vil wol wie wi waz was nu noch daz
dez dir dich mich mir uns her hin dô do e ê bi bî by vor uber über unter under durch nach naeh nâch mag mac sol sal
wil müg mug ane ân ain ainen ainem ains aines dz vnz unz biz bis iz""".split())
SEGS = S97.SEGS
log: list[str] = []
T0 = time.time()
OUT = None


def pick_out():
    if FIXTURE:
        return RUN_DIR / f"fixture_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    base = ROOT / ("results_s102_amend1.txt" if AMEND else "results_s102.txt")
    if base.exists():
        print(f"STOP: {base.name} exists; results are never overwritten")
        raise SystemExit(3)
    return base


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    if OUT is None:
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def data_files():
    out = [f"data/translit/{f}.meta.json" for f in TRANSLITS.values()]
    out += ["data/controls_realline/cremma_all_marks.meta.json", "data/controls/latin_macer_floridus.txt",
            "data/controls/latin_augustine.txt"]
    for spec in PERIOD_SRC.values():
        out += list(spec["files"])
    for lang in sorted(set(SOLVER_LANG.values())):
        pn, lms = S50.LANGS[lang]
        for n in [pn] + list(lms or []):
            out.append(f"data/controls/{n}.txt")
    return sorted(set(out), key=out.index)


def local_modules():
    out = []
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix == ".py" and p.exists():
            out.append(rel.as_posix())
    return sorted(set(out) | {SELF.name})


def stub_files():
    return local_modules() + data_files()


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


# ======================================================================= plaintext symbols
def reduce_letter(ch):
    if ch in ABBR_LETTERS:
        return ABBR_LETTERS[ch]
    c = ch.lower()
    if c in ABBR_LETTERS:
        return ABBR_LETTERS[c]
    if "a" <= c <= "z":
        return {"j": "i", "v": "u", "w": "uu"}.get(c, c)
    d = unicodedata.normalize("NFD", c)
    b = d[0] if d else ""
    if "a" <= b <= "z" and b != c:
        return {"j": "i", "v": "u", "w": "uu"}.get(b, b)
    return "~"   # any other letter (unknown abbreviation letter)


def reduce_token(tok, diplomatic):
    """-> plaintext symbol string over PLAIN_ALPHA ('' if nothing left)."""
    out = []
    s = unicodedata.normalize("NFD", tok)
    i = 0
    while i < len(s):
        ch = s[i]
        cat = unicodedata.category(ch)
        marks = []
        j = i + 1
        while j < len(s) and unicodedata.category(s[j]) == "Mn":
            marks.append(ord(s[j])); j += 1
        if cat == "Mn":   # stray mark with no base
            if diplomatic or ord(ch) in ABBR_MARKS:
                out.append("~")
            i = j if j > i + 1 else i + 1
            continue
        if ch == "⁊":
            out.append("&")
        elif cat == "Co":
            out.append("~")
        elif cat.startswith("L"):
            out.append(reduce_letter(ch))
        else:
            i = j
            continue   # digits, punctuation, symbols dropped (their marks with them)
        if marks and (diplomatic or any(m in ABBR_MARKS for m in marks)):
            out.append("~")
        i = j
    return "".join(out)


def tok_line(line, diplomatic=False):
    s = unicodedata.normalize("NFC", line)
    raw = re.findall(r"[^\s.,;:!?()\[\]{}<>\"'«»/\\|=+*0-9]+", s)
    return [t for t in (reduce_token(w, diplomatic) for w in raw) if t]


def load_p1():
    med = S87.meta_lines(ROOT / "data" / "controls_realline" / "cremma_all_marks.meta.json", set(MEDIC))
    lines = [[t for t in (reduce_token(w, True) for w in ln) if t] for ln in med]
    n_med = sum(len(ln) for ln in lines if ln)
    for ln in (ROOT / "data" / "controls" / "latin_macer_floridus.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.strip() or ln.startswith("##") or ln.strip().lower() == "recensere":
            continue
        lines.append(tok_line(ln, False))
    lines = [ln for ln in lines if ln]
    return lines, n_med


def load_period(key):
    """body ranges -> filtered lines -> end-of-line hyphenation joined -> tokens (per file, in order)."""
    spec = PERIOD_SRC[key]
    toks = []
    for f, rngs in zip(spec["files"], spec["ranges"]):
        L = (ROOT / f).read_text(encoding="utf-8", errors="replace").splitlines()
        keep = []
        for a, b in rngs:
            for ln in L[a - 1:b]:
                if not ln.strip() or (spec["drop_line"] and re.search(spec["drop_line"], ln)):
                    continue
                if spec["drop_tok"]:
                    ln = re.sub(spec["drop_tok"], " ", ln)
                keep.append(ln.rstrip())
        text = re.sub(r"[-¬]\s*\n\s*", "", "\n".join(keep))
        for ln in text.split("\n"):
            toks.extend(tok_line(ln, False))
    return toks


# ======================================================================= encodings
class Cipher:
    """key + encoder + planted decoder for E1..E4 (see docstring)."""

    def __init__(self, enc, plain_tokens, func, pi):
        self.enc, self.pi = enc, pi
        rng = np.random.default_rng([SEED, pi, enc])
        self.rng = np.random.default_rng([SEED, pi, enc, 1])
        freq = Counter(ch for w in plain_tokens for ch in w)
        ranked = sorted(PLAIN_ALPHA, key=lambda c: (-freq[c], PLAIN_ALPHA.index(c)))
        if enc == 1:
            g = list(rng.permutation(GLYPHS[:27]))
            self.homo = {c: [g[i]] for i, c in enumerate(PLAIN_ALPHA)}
            self.nulls = g[25:27]
        else:
            g = list(rng.permutation(GLYPHS[:46]))
            self.homo, k = {}, 0
            for r, c in enumerate(ranked):
                n = HOMO_PLAN[r] if r < len(HOMO_PLAN) else 1
                self.homo[c] = g[k:k + n]; k += n
            assert k == 44
            self.nulls = g[44:46]
        self.inv = {gl: c for c, gs in self.homo.items() for gl in gs}
        self.letter_glyphs = sorted(self.inv)
        self.code, self.codebook = {}, {}
        if enc in (3, 4):
            cnt = Counter(plain_tokens)
            cand = [w for w, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])) if w not in func and len(w) >= 2][:N_CODE]
            used = set()
            nv = V_CODE if enc == 4 else 1
            for r, w in enumerate(cand):
                L = 2 if r < N_CODE_SHORT else 3
                vs = []
                for _ in range(nv):
                    while True:
                        cg = "".join(self.letter_glyphs[int(i)] for i in rng.integers(len(self.letter_glyphs), size=L))
                        if cg not in used:
                            used.add(cg); vs.append(cg); break
                self.code[w] = vs
                for cg in vs:
                    self.codebook[cg] = w
        self.collisions = 0
        self.n_null = self.n_sym = 0

    def spell(self, w):
        for _ in range(50):
            out = []
            for ch in w:
                if self.rng.random() < P_NULL:
                    out.append(self.nulls[int(self.rng.integers(2))]); self.n_null += 1
                gs = self.homo[ch]
                out.append(gs[int(self.rng.integers(len(gs)))] if len(gs) > 1 else gs[0]); self.n_sym += 1
            s = "".join(out)
            if s not in self.codebook:
                return s
        self.collisions += 1
        return s

    def encode_lines(self, lines, line_offset=0):
        out, variants = [], []
        for li, ln in enumerate(lines):
            v = int(np.random.default_rng([SEED, 400 + self.pi, line_offset + li]).integers(V_CODE)) if self.enc == 4 else 0
            variants.append(v)
            out.append([self.code[w][v] if w in self.code else self.spell(w) for w in ln])
        return out, variants

    def decode(self, tok):
        if tok in self.codebook:
            return self.codebook[tok]
        return "".join(self.inv[g] for g in tok if g in self.inv)


def encode_pages(pages, cipher):
    out, li = [], 0
    allv = []
    for pid, ls in pages:
        enc, v = cipher.encode_lines(ls, li)
        li += len(ls)
        out.append((pid, enc)); allv.extend(v)
    return out, allv


def recovery(plain_pages, enc_pages, cipher):
    P = [w for _, ls in plain_pages for ln in ls for w in ln]
    C = [w for _, ls in enc_pages for ln in ls for w in ln]
    assert len(P) == len(C)
    return sum(1 for p, c in zip(P, C) if cipher.decode(c) == p) / len(P)


def glyph_stream(plain_pages, enc_pages, cipher):
    """cipher glyph ids and aligned truth letter ids (-1 for nulls, '~', '&', code groups)."""
    gid = {g: i for i, g in enumerate(GLYPHS)}
    s, t = [], []
    for (_, pl), (_, el) in zip(plain_pages, enc_pages):
        for pln, eln in zip(pl, el):
            for pw, ew in zip(pln, eln):
                for g in ew:
                    s.append(gid[g])
                    c = cipher.inv.get(g)
                    t.append(SOLV.A_IDX.get(c, -1) if c is not None else -1)
    return np.asarray(s, dtype=np.int64), np.asarray(t, dtype=np.int64)


def solver_desc(plain_pages, enc_pages, cipher, lang, seed):
    lm, q, plain, _n = S50.get_lm(lang)
    h1 = float(-np.sum(q * np.log2(q)))
    h5 = float(SOLV.lm_bits_per_letter(lm, plain[:50000]))
    s, t = glyph_stream(plain_pages, enc_pages, cipher)
    h = len(s) // 2
    # glyph ids compacted to 0..U-1 on Half A
    ua = {g: i for i, g in enumerate(sorted(set(s[:h].tolist())))}
    sA = np.asarray([ua[g] for g in s[:h]], dtype=np.int64)
    sB = np.asarray([ua.get(g, -1) for g in s[h:]], dtype=np.int64)
    r = S86.fast_solve_stream(sA, sB, lm, q, h1 - h5, restarts=3, sweeps=22, seed=seed, truth_B=t[h:])
    letters_share = float((t[h:] >= 0).mean())
    return r["acc_B"], letters_share


# ======================================================================= rhythm / h2
def rhythm(pages, seed):
    r = S21.analyze([{"lines": ls} for _, ls in pages], seed)
    r["excess"] = r["I"] - r["median"]
    r["holds"] = bool(r["excess"] > 0 and r["p"] < RHY_P)
    return r


def h2_of(pages):
    return float(A1.char_entropies([w for _, ls in pages for ln in ls for w in ln])["h2"])


# ======================================================================= battery pool (own copy: never S97.flush)
def run_pool(jobs, tag):
    import multiprocessing as mp
    fg = S91.free_gb()
    emit(f"  [{tag}] free RAM {fg:.1f} GB (need >= {MIN_FREE_GB}); {len(jobs)} Measured jobs on {N_WORKERS} workers")
    if not (fg >= MIN_FREE_GB):
        emit(f"STOP: free RAM {fg:.1f} GB < {MIN_FREE_GB} GB")
        flush()
        raise SystemExit(2)
    out = {}
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(N_WORKERS, initializer=S97.worker_init) as pool:
        for i, (k, m, dr, s) in enumerate(pool.imap_unordered(S97.measure_job, jobs)):
            out[k] = (m, dr)
            if (i + 1) % 20 == 0 or i + 1 == len(jobs):
                print(f"  [{tag} {time.time() - t0:.0f}s] {i + 1}/{len(jobs)} done (last {k} {s:.0f}s)", flush=True)
    return out


# ======================================================================= fixture
def run_fixture():
    emit("S102 FIXTURE (synthetic only; no real data read)")
    emit(f"date: {S87.clock()}  device: {S87.DEV}; below_normal={S87.below_normal()}")
    emit(f"s102 sha256={sha256(SELF)}  stub_match={stub_match()}")
    pl, _lex = S97.pseudo_latin(7, n_lines=3000)
    r = np.random.default_rng(3)
    pl = [["".join(ch if r.random() > 0.03 else ("~" if r.random() < 0.7 else "&") for ch in w) for w in ln] for ln in pl]
    red = {"j": "i", "v": "u", "w": "uu"}
    pl = [["".join(red.get(ch, ch) for ch in w) for w in ln] for ln in pl]
    pages = S87.layout(pl, True, None, None, [20])
    toks = [w for _, ls in pages for ln in ls for w in ln]
    emit(f"fixture plaintext tokens {len(toks)} types {len(set(toks))}")
    ok_a = True
    encs = {}
    for e in (1, 2, 3, 4):
        c = Cipher(e, toks, FUNC_LA, 9)
        ep, vv = encode_pages(pages, c)
        encs[e] = (c, ep)
        rec = recovery(pages, ep, c)
        nr = c.n_null / max(1, c.n_sym)
        hc = sorted((len(v) for v in c.homo.values()), reverse=True)
        code_share = sum(1 for _, ls in ep for ln in ls for w in ln if w in c.codebook) / len(toks)
        held = True
        if e == 4:
            inv_v = {cg: i for w, vs in c.code.items() for i, cg in enumerate(vs)}
            for _, ls in ep:
                for ln in ls:
                    vs = {inv_v[w] for w in ln if w in inv_v}
                    held &= len(vs) <= 1
        good = rec >= 0.99 and (e > 2 or 0.04 <= nr <= 0.06) and (e == 1 or hc[:10] == HOMO_PLAN) and held and (e < 3 or code_share > 0)
        ok_a &= good
        emit(f"  E{e}: recovery {rec:.4f}; null rate {nr:.4f}; homophones {hc[:12]}; glyphs {len(c.inv) + 2}; code groups {len(c.codebook)}; "
             f"code-token share {code_share:.3f}; collisions {c.collisions}; line-held {held} -> {'ok' if good else 'BAD'}")
    emit(f"FXa encodings/decoder: {'PASS' if ok_a else 'FAIL'}")
    rr = np.random.default_rng(5)
    iid = [("p", [["x" * int(rr.integers(1, 9)) for _ in range(int(rr.integers(4, 11)))] for _ in range(40)]) for _ in range(60)]
    asc = [("p", [["x" * k for k in sorted(int(rr.integers(1, 9)) for _ in range(int(rr.integers(4, 11))))] for _ in range(40)]) for _ in range(60)]
    ri, ra = rhythm(iid, SEED + 1), rhythm(asc, SEED + 2)
    fxb = abs(ri["excess"]) < 0.02 and ra["excess"] > 0 and ra["p"] < 0.05
    emit(f"FXb rhythm: IID excess {ri['excess']:+.4f} (p {ri['p']:.3f}); ascending excess {ra['excess']:+.4f} (p {ra['p']:.3f}) -> {'PASS' if fxb else 'FAIL'}")
    h2a = h2_of([("p", [["ab"] * 500])])
    fxc = h2a < 0.5
    emit(f"FXc h2 alternation {h2a:.4f} -> {'PASS' if fxc else 'FAIL'}")
    flush()
    names, glob, B, spec = S91.fx_world()
    prod = S91.LP91(glob, B); prod.set_params(S91.PLANTED)
    cA = S91.cut(prod.text(spec, 1))
    jobs = [dict(key=("SMOKE", i), name=f"smoke{i}", train=cA[:100], test=cA[100:112 + i], seed=SEED + i) for i in range(2)]
    M = run_pool(jobs, "fixture smoke")
    fxd = set(M) == {("SMOKE", 0), ("SMOKE", 1)}
    emit(f"FXd pool returned {sorted(M)} -> {'PASS' if fxd else 'FAIL'}")
    lb = (0.9074, 1.0499)
    for e in (1, 4):
        p = S97.profile_g(f"FX_E{e}/identity", encs[e][1], S80.identity_seg_factory, 4000, SEED + 20 + e)
        emit("  [FXe descriptive] " + S97.fmt(p, lb))
    emit(f"FIXTURE {'PASS' if (ok_a and fxb and fxc and fxd) else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


# ======================================================================= main
def main():
    global OUT
    if LIST_LOCALS:
        for m in stub_files():
            print(m)
        return
    OUT = pick_out()
    if FIXTURE:
        run_fixture()
        return
    emit("S102: period ciphers (E1 substitution, E2 homophonic, E3 nomenclator, E4 line-held nomenclator) over period "
         "recipe texts vs the joint profile (pre-registered in the docstring; D-066 (h))")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; BelowNormal set={S87.below_normal()}; battery workers {N_WORKERS}")
    emit(f"s102_period_ciphers_recipes.py sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH}; P_NULL {P_NULL}; N_CODE {N_CODE} (short {N_CODE_SHORT}); V_CODE {V_CODE}; "
         f"homophones {HOMO_PLAN}; REC_MIN {REC_MIN}; h2 pad {H2_PAD}; rhythm p < {RHY_P}; seed {SEED}")
    flush()

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    def lay_lines(lines):
        return S87.layout(lines, True, None, line_lens, page_nl)

    def lay_tokens(toks):
        return S87.layout(toks, False, None, line_lens, page_nl)

    # ---- Voynich target
    emit("\n=== Voynich target (SlotSegmenter cores, s87 seeds; rhythm; h2 at the same 22,500-token cut) ===")
    VOY = OrderedDict()
    for i, T in enumerate(TRANSLITS):
        P = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        pages = S87.layout(None, True, P, line_lens, page_nl)
        VOY[T] = (pages, S97.profile_g(f"VOY_{T}", pages, SlotSegmenter, N_MATCH, S87.SEED + 100 * i))
    lb = S87.loc_band_from([v[1] for v in VOY.values()])
    rw_v = float(np.mean([v[1]["rep"][1]["Rw"] for v in VOY.values()])); rc_v = float(np.mean([v[1]["rep"][1]["Rc"] for v in VOY.values()]))
    vh2 = {T: h2_of(v[0]) for T, v in VOY.items()}
    hb = (min(vh2.values()) - H2_PAD, max(vh2.values()) + H2_PAD)
    emit(f"LOCALITY band: [{lb[0]:.4f}, {lb[1]:.4f}]; h2 band [{hb[0]:.4f}, {hb[1]:.4f}] from " + ", ".join(f"{T} {h:.4f}" for T, h in vh2.items()))
    VRH = {}
    for i, (T, (pages, p)) in enumerate(VOY.items()):
        VRH[T] = rhythm(pages, SEED + 7 + i)
        emit("  " + S97.fmt(p, lb) + f" | rhythm I {VRH[T]['I']:.4f} null med {VRH[T]['median']:.4f} exc {VRH[T]['excess']:+.4f} "
             f"p {VRH[T]['p']:.3f} | h2 {vh2[T]:.4f}")
    flush()

    # ---- plaintexts
    emit("\n=== plaintexts (reduced to the 25-symbol plaintext alphabet) ===")
    p1_lines, n_med = load_p1()
    PL = OrderedDict()
    PL["P1_la"] = (lay_lines(p1_lines), FUNC_LA, f"CREMMA Medic MSS ({n_med} tokens, real lines) + Macer Floridus (real verse lines)")
    for key, func in (("P2_it", FUNC_IT), ("P3_de", FUNC_DE)):
        toks = load_period(key)
        PL[key] = (lay_tokens(toks), func, f"{PERIOD_SRC[key]['label']} ({len(toks)} tokens available; relined to ZL3b line lengths)")
    short = []
    for key, (pages, func, lab) in PL.items():
        nt = sum(len(ln) for _, ls in pages for ln in ls)
        sym = Counter(ch for _, ls in pages for ln in ls for w in ln for ch in w)
        emit(f"  {key}: tokens {nt} pages {len(pages)} lines {sum(len(ls) for _, ls in pages)} types "
             f"{len({w for _, ls in pages for ln in ls for w in ln})}; '~' {sym['~']} '&' {sym['&']}; {lab}")
        emit(f"     first line: {' '.join(pages[0][1][0])}")
        if nt < N_TOT:
            short.append(key)
            emit(f"     FLAG: {key} has {nt} < {N_TOT} tokens: its cells are not scored")
    flush()

    # ---- encode + recovery gate
    emit("\n=== encodings and G1 recovery (planted decoder, known key) ===")
    TEXTS = OrderedDict()   # name -> (role, pages, Ts)
    REC = OrderedDict()
    CIPH = {}
    allT = list(TRANSLITS)
    for pi, (key, (pages, func, lab)) in enumerate(PL.items()):
        if key in short:
            continue
        toks = [w for _, ls in pages for ln in ls for w in ln]
        TEXTS[f"REF_{key}_plain"] = ("descriptive", pages, allT)
        for e in (1, 2, 3, 4):
            c = Cipher(e, toks, func, pi + 1)
            ep, vv = encode_pages(pages, c)
            rec = recovery(pages, ep, c)
            name = f"{key}_E{e}"
            REC[name] = rec
            CIPH[name] = (c, pages, ep)
            TEXTS[name] = ("cell", ep, allT)
            code_share = sum(1 for _, ls in ep for ln in ls for w in ln if w in c.codebook) / len(toks)
            emit(f"  {name}: recovery {rec:.4f}; glyphs {len(c.inv) + 2}; null rate {c.n_null / max(1, c.n_sym):.4f}; "
                 f"code groups {len(c.codebook)} (code-token share {code_share:.3f}); collisions {c.collisions}; "
                 f"first line: {' '.join(ep[0][1][0])}")
    G1 = bool(REC) and all(v >= REC_MIN for v in REC.values()) and not short
    emit(f"  G1 recovery >= {REC_MIN} on every cell: {G1} (min {min(REC.values()) if REC else float('nan'):.4f})")
    emit("  descriptive: s86 solver (fast_solve_stream, 5-gram LM of the matching language) on E1/E2, Half-B letter accuracy")
    SOLVE = OrderedDict()
    for name, (c, pages, ep) in CIPH.items():
        if c.enc not in (1, 2):
            continue
        key = name.rsplit("_E", 1)[0]
        acc, ls = solver_desc(pages, ep, c, SOLVER_LANG[key], SEED + 31)
        SOLVE[name] = acc
        emit(f"    {name}: solver Half-B accuracy {acc:.4f} (letter positions {ls:.3f} of glyphs; LM {SOLVER_LANG[key]})")
        flush()
    flush()

    # ---- G2: s97 gate
    emit("\n=== G2: s97 gate (PC1 planted LP91, PC2 IT2a as control, NC plain Latin), s97 code and constants ===")
    aug = S87.load_control("latin_augustine.txt")
    TEXTS["PC2_VOY_IT2a_as_control"] = ("gate", VOY["IT2a"][0], ["IT2a"])
    TEXTS["NC_augustine_la"] = ("gate", lay_tokens(aug), allT)
    zp = S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS['ZL3b']}.meta.json")
    segz = SlotSegmenter([w for _, _, ls in zp for l in ls for w in l])
    zcp = [(p, q, [[segz.segment(w)[1] for w in l] for l in ls]) for p, q, ls in zp]
    glob = Counter(c for _, _, ls in zcp for l in ls for c in l if c != "")
    prod = S91.LP91(glob, S91.bigram_of([(p, [[c for c in l if c != ""] for l in ls]) for p, q, ls in zcp]))
    prod.set_params(S91.PLANTED)
    spec = [(p, q, [len(l) for l in ls]) for p, q, ls in zp]
    pc1 = []
    for s in (1, 2, 3):
        pages = S91.cut(prod.text(spec, S97.SEED + s))
        p = S97.profile_g(f"PC1_LP91_planted_s{s}", pages, S80.identity_seg_factory, N_MATCH, S97.SEED + 10 + s)
        pc1.append(S97.flags(p, lb)[0])
        emit("  " + S97.fmt(p, lb))
    PC1 = sum(pc1) >= S97.PC1_MIN
    emit(f"  PC1 Voynich-like on {sum(pc1)}/3 seeds (need >= {S97.PC1_MIN}) -> {PC1}")
    flush()

    # ---- signature profiles
    emit("\n=== signature profiles (flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PR = OrderedDict()
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        PR[n] = OrderedDict()
        segs = ["slot"] if n.startswith("PC2") else list(SEGS)
        for si, sn in enumerate(segs):
            p = S97.profile_g(f"{n}/{sn}", pages, SEGS[sn], N_MATCH, SEED + 1000 * xi + 100 * si)
            PR[n][sn] = p
            app = p["core_share"] >= MIN_CORE_SHARE
            emit("  " + S97.fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}{'' if app else ' [NOT APPLICABLE: core share < 0.5]'}"))
            flush()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---- rhythm and h2
    emit("\n=== F-04 rhythm (within-line lag-1 length Moran I vs 999 within-line shuffles) and h2 ===")
    RH, H2 = OrderedDict(), OrderedDict()
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        RH[n] = rhythm(pages, SEED + 5000 + xi)
        H2[n] = h2_of(pages)
        emit(f"  {n:28s} I {RH[n]['I']:+.4f} null median {RH[n]['median']:+.4f} q99 {RH[n]['q99']:+.4f} excess {RH[n]['excess']:+.4f} "
             f"p {RH[n]['p']:.3f} -> {RH[n]['holds']} | h2 {H2[n]:.4f} in [{hb[0]:.3f},{hb[1]:.3f}] -> {hb[0] <= H2[n] <= hb[1]}")
    flush()

    # ---- battery
    emit("\n=== s67 slot battery (text block b vs real Voynich fold folds[b]) ===")
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    emit(f"  folds ({len(folds)}): {' '.join(folds)}")
    assert len(folds) == NB
    jobs = S97.ref_jobs(ref, folds)
    for xi, (n, (role, pages, Ts)) in enumerate(TEXTS.items()):
        jobs += S97.ctl_jobs(n, xi + 1, pages)
    M = run_pool(jobs, "battery")
    BAT = OrderedDict()
    for n, (role, pages, Ts) in TEXTS.items():
        BAT[n] = S97.battery_score(n, Ts, M, ref, folds, pages)
        for T, r in BAT[n].items():
            emit(f"  {n:28s} " + S97.bat_line(T, r))
    flush()

    # ---- calls
    emit("\n=== calls ===")
    DESC, LIKE = OrderedDict(), OrderedDict()
    for n, (role, pages, Ts) in TEXTS.items():
        segs = list(PR[n])
        app = [sn for sn in segs if PR[n][sn]["core_share"] >= MIN_CORE_SHARE]
        sig = {sn: S97.flags(PR[n][sn], lb) for sn in segs}
        sig_ok = bool(app) and all(sig[sn][0] for sn in app)
        bat_ok = all(BAT[n][T]["holds"] for T in Ts)
        rhy_ok = RH[n]["holds"]
        h2_ok = hb[0] <= H2[n] <= hb[1]
        s97_full = sig_ok and bat_ok
        LIKE[n] = sig_ok and bat_ok and rhy_ok and h2_ok
        DESC[n] = dict(role=role, applicable=app, sig={sn: sig[sn][2] for sn in segs}, sig_ok=sig_ok, battery_ok=bat_ok,
                       battery={T: BAT[n][T]["folds_ok"] for T in Ts}, rhythm=dict(I=RH[n]["I"], median=RH[n]["median"],
                       excess=RH[n]["excess"], p=RH[n]["p"], holds=rhy_ok), h2=H2[n], h2_ok=h2_ok, s97_full=s97_full,
                       voynich_like=LIKE[n], recovery=REC.get(n), solver_accB=SOLVE.get(n))
        emit(f"  {n:28s} {role:11s} SIG " + " ".join(f"{sn}:{sig[sn][2]}" for sn in segs) + f" (applicable {','.join(app)}) -> {sig_ok}; "
             f"BAT " + " ".join(f"{T} {BAT[n][T]['folds_ok']}/15" for T in Ts) + f" -> {bat_ok}; RHY {RH[n]['excess']:+.4f} p {RH[n]['p']:.3f} -> {rhy_ok}; "
             f"H2 {H2[n]:.3f} -> {h2_ok}; VOYNICH-LIKE = {LIKE[n]}")
    PC2 = DESC["PC2_VOY_IT2a_as_control"]["s97_full"]
    NC = not DESC["NC_augustine_la"]["s97_full"]
    G2 = PC1 and PC2 and NC
    GATE = G1 and G2
    emit(f"  descriptive: PC2 (IT2a as control) under the full D-066 rule: VOYNICH-LIKE = {LIKE['PC2_VOY_IT2a_as_control']}")
    emit(f"  GATE: G1 recovery {G1}; G2 s97 gate (PC1 {PC1}, PC2 {PC2}, NC {NC}) {G2} -> GATE = {GATE}")
    cells = [n for n, d in DESC.items() if d["role"] == "cell"]
    hits = [n for n in cells if LIKE[n]]
    CALL = GATE and bool(hits)
    emit("\n  12-cell table (SIG flags per segmenter id/slot/affix2 | BAT folds ZL3b/RF1b/IT2a | RHY excess,p | h2 | recovery | solver)")
    for n in cells:
        d = DESC[n]
        emit(f"   {n:9s} SIG {'/'.join(d['sig'].values())} {'Y' if d['sig_ok'] else 'n'} | BAT {'/'.join(str(v) for v in d['battery'].values())} "
             f"{'Y' if d['battery_ok'] else 'n'} | RHY {d['rhythm']['excess']:+.4f},{d['rhythm']['p']:.3f} {'Y' if d['rhythm']['holds'] else 'n'} | "
             f"h2 {d['h2']:.3f} {'Y' if d['h2_ok'] else 'n'} | rec {d['recovery']:.3f} | solver {('%.3f' % d['solver_accB']) if d['solver_accB'] is not None else '-'} "
             f"| {'VOYNICH-LIKE' if d['voynich_like'] else '-'}")
    emit(f"  CALL_S102_PERIOD_CIPHER = {CALL}")
    if not GATE:
        why = [k for k, v in (("G1 recovery", G1), ("PC1", PC1), ("PC2", PC2), ("NC", NC)) if not v]
        reading = f"uninformative: gate failed ({', '.join(why)})"
    elif CALL:
        reading = ("Voynich-like cells: " + ", ".join(hits) + "; next step per D-066 (h): constrained decipherment of the "
                   "manuscript with that encoding family and language as the prior")
    else:
        reading = ("no cell is Voynich-like: 'period cipher over vernacular recipes' is closed within the tested constructions "
                   "(D-066 (h) stopping rule; no parameter sweeps)")
    emit(f"\nVERDICT: CALL_S102_PERIOD_CIPHER = {CALL}: {reading}")
    flush()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "profiles.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "segmenter", "tokens", "types", "core_share", "te_tok", "o100", "p100", "o200", "Rw1", "pRw1", "Rc1",
                    "loc", "loc_lo", "loc_hi", "C1", "flags", "D"])
        rows = [(f"VOY_{T}", "slot", v[1]) for T, v in VOY.items()] + [(n, sn, p) for n in PR for sn, p in PR[n].items()]
        for n, sn, p in rows:
            o, r, l = p["order"], p["rep"], p["loc"]
            ok, _, fl = S97.flags(p, lb)
            w.writerow([n, sn, p["tokens"], p["types"], f"{p['core_share']:.4f}", p["te_tok"], f"{o[100]['mm']:.6f}", f"{o[100]['p']:.4f}",
                        f"{o[200]['mm']:.6f}", f"{r[1]['Rw']:.4f}", f"{r[1]['pw']:.4f}", f"{r[1]['Rc']:.4f}", f"{l['ratio']:.4f}",
                        f"{l['lo']:.4f}", f"{l['hi']:.4f}", ok, fl, f"{S87.distance(p, lb, rw_v, rc_v)[0]:.3f}"])
    with (RUN_DIR / "battery.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "T", "fold", "n"] + S67.PREDS + ["small", "type_ratio"])
        for n in BAT:
            for T, r in BAT[n].items():
                for x in r["rows"]:
                    w.writerow([n, T, x["Q"], x["n"]] + [x["holds"][k] for k in S67.PREDS] + [x["small"], f"{x['type_ratio']:.4f}"])
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(loc_band=lb, order_band=S87.ORDER_BAND, h2_band=hb, voy_h2=vh2,
                                                        voy_rhythm={T: {k: v for k, v in r.items()} for T, r in VRH.items()},
                                                        G1=G1, recovery=REC, solver=SOLVE, PC1=PC1, PC1_seeds=pc1, PC2=PC2, NC=NC,
                                                        GATE=GATE, CALL_S102_PERIOD_CIPHER=CALL, desc=DESC, verdict=reading),
                                                   indent=1, default=str), encoding="utf-8", newline="\n")
    for name, (c, pages, ep) in CIPH.items():
        (RUN_DIR / f"key_{name}.json").write_text(json.dumps(dict(homophones=c.homo, nulls=c.nulls, code=c.code), ensure_ascii=False,
                                                              indent=0), encoding="utf-8", newline="\n")
    emit(f"\nsidecars: runs/s102/profiles.csv, runs/s102/battery.csv, runs/s102/calls.json, runs/s102/key_<cell>.json")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


if __name__ == "__main__":
    main()
