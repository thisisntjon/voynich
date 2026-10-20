"""Build real-line control sidecars for Phase 1 step s17 (workflow/phases/phase-1.md).

Every sidecar keeps the source's own line breaks (the "native" line) and groups lines into
pages by the source's own structural unit.  Dialect = the one `scoreboard/run_v2.py:load_meta`
reads (page key "id"; section/hand/lang/quire strings; "lines" = list of token lists):

    {"name": ..., "tokenization": "latin", "source": ..., "pages": [
      {"id": "<folio-style id>", "section": "...", "hand": "...", "lang": "?", "quire": "?",
       "lines": [["tok", ...], ...]}, ...]}

Outputs (data/controls_realline/, created if absent):
  gib_realline_pooled      Gaskell-Bowern volunteer gibberish, 38 source files, one page per
                           writer (id = writer code, hand = writer code), the volunteers' own
                           lines; `_____` page-rule lines and empty lines dropped; a token
                           ending in `-` at line end is joined to the first token of the next
                           non-empty line (the joined token sits on the NEXT line, exactly as
                           tools/gibberish_to_meta.py:tokens_of does it); token rule identical
                           to tools/gibberish_to_meta.py:clean_token (NFKD, strip Mn marks,
                           lowercase, delete non a-z).  Token count therefore reconciles with
                           n7's gib_pooled (10,023) exactly; the only structural difference
                           is the lines/pages.
  mhg_nibelungenlied       data/controls/mhg_nibelungenlied.txt; the edited long-lines are the
                           lines; each `## N. Aventiure` block is a page (id = "avNN", section
                           = the header text); tokens = corpora_ext.tokenize (the loader
                           m4_phase1_board.natural_from_ext uses for this file: lowercase, _FOLD
                           ligature map, NFKD, strip Mn, maximal runs of Unicode letters).
  oldfrench_roland         data/controls/oldfrench_roland.txt; verse lines; `## laisse N`
                           blocks as pages (id = "lNNN"); corpora_ext.tokenize.
  occitan_croisade         data/controls/occitan_croisade_albigeoise.txt; same layout
                           (`## laisse N` blocks); corpora_ext.tokenize.
  italian_dante            data/controls/italian_dante.txt (Gutenberg); verse lines, the
                           a2_position.verse_lines rule (strip_gutenberg, lower, NFD, strip Mn,
                           tokens = [a-zß]+, keep lines with >=3 tokens; here WITHOUT the
                           first-5000-lines cap, which run_v2's 25k-token subsample makes moot);
                           cantos as pages (id = "<canticle>_NN", section = canticle).
  <name>_relined8          one twin per sidecar: the same tokens in the same order re-cut into
                           lines of exactly 8 tokens, same page ids in the same order.  A line
                           belongs to the page in which its 8th token falls (remainders carry
                           into the next page), so only the final line of the corpus can be
                           shorter than 8; a page whose tokens never complete a line is kept
                           with an empty "lines" list (load_meta drops it).
  README.md                counts, the line-preservation check and the gibberish reconciliation,
                           written by this script.

Checks performed after writing (results go to README.md and stdout):
  * flattened token stream of each control sidecar == the project's own loader stream
    (corpora_ext.control_ext_lines for the three medieval texts; a2_position.verse_lines for
    Dante, compared on its 5,000-line prefix);
  * gib_realline_pooled token stream == tools/gibberish_to_meta.py:tokens_of over the same files;
  * line preservation: run_v2.load_meta + run_v2.subsample(25000) returns per-line token counts
    equal to the sidecar's own non-empty lines (prefix), for every sidecar.

Run from the project root with the isolated interpreter:
    python -I tools/realline_to_meta.py [--dst DIR]
Writes only data/controls_realline/*.meta.json and data/controls_realline/README.md.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import corpora  # noqa: E402  (CTRL, strip_gutenberg)
import corpora_ext  # noqa: E402  (tokenize, control_ext_lines)

GIB_SRC = (ROOT / "data" / "external" / "gaskell-bowern-gibberish" / "danielgaskell-voynich-main"
           / "voynich-main" / "data" / "gibberish_transcriptions")
CTRL = ROOT / "data" / "controls"
DST = ROOT / "data" / "controls_realline"
N_SAMPLE = 25000
RELINE = 8
GIB_NAME_RE = re.compile(r"^Gibberish - (.+)\.txt$")


def _load_by_path(modname: str, path: Path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------- gibberish
def gib_clean_token(tok: str) -> str:
    """Identical to tools/gibberish_to_meta.py:clean_token."""
    s = unicodedata.normalize("NFKD", tok)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z]", "", s)


def gib_lines_of(text: str) -> list[list[str]]:
    """The volunteer's own lines, hyphen-joined like gibberish_to_meta.tokens_of (carry goes to
    the next non-empty line; carry survives `_____` rules and blank lines)."""
    out: list[list[str]] = []
    carry = ""
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or set(ln) <= {"_"}:
            continue
        parts = ln.split()
        if carry:
            parts[0] = carry + parts[0]
            carry = ""
        if parts[-1].endswith("-") and len(parts[-1]) > 1:
            carry = parts.pop().rstrip("-")
        toks = [t for t in (gib_clean_token(p) for p in parts) if t]
        if toks:
            out.append(toks)
    if carry:
        t = gib_clean_token(carry)
        if t:
            out.append([t])
    return out


def build_gibberish() -> dict:
    pages = []
    for f in sorted(GIB_SRC.glob("*.txt")):
        m = GIB_NAME_RE.match(f.name)
        if not m:
            print(f"skip (name pattern): {f.name}", file=sys.stderr)
            continue
        writer = m.group(1).strip().replace(" ", "_")
        lines = gib_lines_of(f.read_text(encoding="utf-8", errors="strict"))
        pages.append(dict(id=writer, section="gib", hand=writer, lang="?", quire="?", lines=lines))
    return dict(name="gib_realline_pooled", tokenization="latin",
                source="Gaskell & Bowern 2022 volunteer gibberish, 38 source files "
                       f"({GIB_SRC.relative_to(ROOT).as_posix()}), one page per writer (id = hand = "
                       "writer code), the volunteers' own lines; `_` page rules and empty lines "
                       "dropped; line-end `-` joined to the next line's first token; token rule = "
                       "tools/gibberish_to_meta.py:clean_token (NFKD, strip marks, lowercase, a-z only); "
                       "tools/realline_to_meta.py",
                pages=pages)


# ----------------------------------------------------------------------------- `## ` block texts
def build_blocks(name: str, fname: str, header_re: str, id_fmt, section_fn, hand: str,
                 source_note: str) -> dict:
    """Pages = `## ` header blocks; lines = source lines; tokens = corpora_ext.tokenize."""
    hre = re.compile(header_re)
    pages, cur = [], None
    for raw in (CTRL / f"{fname}.txt").read_text(encoding="utf-8").split("\n"):
        if raw.startswith("## "):
            head = raw[3:].strip()
            m = hre.match(head)
            if not m:
                raise SystemExit(f"{fname}: header {head!r} does not match {header_re!r}")
            cur = dict(id=id_fmt(m), section=section_fn(head, m), hand=hand, lang="?", quire="?",
                       lines=[])
            pages.append(cur)
            continue
        toks = corpora_ext.tokenize(raw)
        if toks:
            if cur is None:
                raise SystemExit(f"{fname}: text before the first `## ` header")
            cur["lines"].append(toks)
    return dict(name=name, tokenization="latin",
                source=f"data/controls/{fname}.txt; {source_note}; lines = the file's own lines; "
                       "tokens = corpora_ext.tokenize (lowercase, ligature fold, NFKD, strip marks, "
                       "runs of Unicode letters); tools/realline_to_meta.py",
                pages=pages)


# ----------------------------------------------------------------------------- Dante
DANTE_TOK = re.compile(r"[a-zß]+")
CANTICLES = ("inferno", "purgatorio", "paradiso")
CANTO_RE = re.compile(r"^canto\s+([ivxl]+)$")
ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50}


def roman_to_int(s: str) -> int:
    n, prev = 0, 0
    for c in reversed(s):
        v = ROMAN[c]
        n = n - v if v < prev else n + v
        prev = max(prev, v)
    return n


def dante_norm(text: str) -> str:
    """a2_position.verse_lines normalisation: lower, NFD, strip combining marks."""
    return "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if unicodedata.category(c) != "Mn")


def build_dante() -> dict:
    t = dante_norm(corpora.strip_gutenberg(
        (CTRL / "italian_dante.txt").read_text(encoding="utf-8", errors="replace")))
    pages, cur, canticle, pending = [], None, None, None
    for raw in t.splitlines():
        s = raw.strip()
        if s in CANTICLES:
            pending = s          # body form: "<canticle>" line, then "canto N" line
            continue
        m = CANTO_RE.match(s)
        if m and pending:
            canticle = pending
            n = roman_to_int(m.group(1))
            cur = dict(id=f"{canticle[:3]}_{n:02d}", section=canticle, hand="Gutenberg", lang="?",
                       quire="?", lines=[])
            pages.append(cur)
            pending = None
            continue
        pending = None
        toks = DANTE_TOK.findall(raw)
        if len(toks) >= 3:
            if cur is None:
                # Gutenberg title lines ("la divina commedia", "di dante alighieri") are >=3 tokens
                # and verse_lines keeps them; a "front" page keeps the stream identical.
                cur = dict(id="front", section="front", hand="Gutenberg", lang="?", quire="?", lines=[])
                pages.append(cur)
            cur["lines"].append(toks)
    return dict(name="italian_dante", tokenization="latin",
                source="data/controls/italian_dante.txt (Gutenberg); verse lines by the "
                       "a2_position.verse_lines rule (strip_gutenberg, lower, NFD, strip marks, "
                       "tokens [a-zß]+, lines with >=3 tokens, no 5000-line cap); cantos as pages "
                       "(id <canticle3>_NN, section = canticle); tools/realline_to_meta.py",
                pages=pages)


# ----------------------------------------------------------------------------- re-lining
def relined8(doc: dict) -> dict:
    pages, buf = [], []
    for p in doc["pages"]:
        q = dict(p, lines=[])
        for ln in p["lines"]:
            buf.extend(ln)
            while len(buf) >= RELINE:
                q["lines"].append(buf[:RELINE])
                buf = buf[RELINE:]
        pages.append(q)
    if buf:
        pages[-1]["lines"].append(buf)
    return dict(name=f"{doc['name']}_relined{RELINE}", tokenization=doc["tokenization"],
                source=f"{doc['name']} re-cut into lines of exactly {RELINE} tokens (same tokens, "
                       "same order, same page ids; remainders carry into the next page; only the "
                       f"corpus's final line may be short); tools/realline_to_meta.py",
                pages=pages)


# ----------------------------------------------------------------------------- checks
def flat(doc: dict) -> list[str]:
    return [t for p in doc["pages"] for ln in p["lines"] for t in ln]


def counts(doc: dict) -> dict:
    lines = [ln for p in doc["pages"] for ln in p["lines"]]
    lens = [len(ln) for ln in lines]
    return dict(pages=len(doc["pages"]), nonempty_pages=sum(1 for p in doc["pages"] if p["lines"]),
                lines=len(lines), tokens=sum(lens), min_len=min(lens), max_len=max(lens),
                mode_len=max(set(lens), key=lens.count),
                types=len(set(flat(doc))))


def preservation_check(path: Path, R2) -> tuple[bool, str]:
    _, pg = R2.load_meta(path)
    pg = R2.subsample(pg, N_SAMPLE)
    a = [len(l) for q in pg for l in q["lines"]]
    d = json.loads(path.read_text(encoding="utf-8"))
    b = [len(l) for q in d["pages"] for l in q["lines"] if l][:len(a)]
    ok = a == b and len(a) > 0
    return ok, (f"lines kept={ok} subsampled_lines={len(a)} subsampled_tokens={sum(a)} "
                f"(sidecar prefix lines={len(b)} tokens={sum(b)})")


def stream_checks(docs: dict) -> list[str]:
    out = []
    gtm = _load_by_path("gibberish_to_meta", ROOT / "tools" / "gibberish_to_meta.py")
    ref = []
    for f in sorted(GIB_SRC.glob("*.txt")):
        if GIB_NAME_RE.match(f.name):
            ref.extend(gtm.tokens_of(f.read_text(encoding="utf-8", errors="strict")))
    mine = flat(docs["gib_realline_pooled"])
    out.append(f"gib_realline_pooled token stream == tools/gibberish_to_meta.tokens_of over the 38 files: "
               f"{mine == ref} ({len(mine)} vs {len(ref)} tokens)")
    for name, fname in (("mhg_nibelungenlied", "mhg_nibelungenlied"),
                        ("oldfrench_roland", "oldfrench_roland"),
                        ("occitan_croisade", "occitan_croisade_albigeoise")):
        ref_lines = corpora_ext.control_ext_lines(fname)
        mine_lines = [ln for p in docs[name]["pages"] for ln in p["lines"]]
        out.append(f"{name} lines == corpora_ext.control_ext_lines('{fname}'): {mine_lines == ref_lines} "
                   f"({len(mine_lines)} vs {len(ref_lines)} lines)")
    a2 = _load_by_path("a2_position", ROOT / "a2_position.py")
    ref_lines = a2.verse_lines("italian_dante")
    mine_lines = [ln for p in docs["italian_dante"]["pages"] for ln in p["lines"]]
    out.append(f"italian_dante lines[:5000] == a2_position.verse_lines('italian_dante'): "
               f"{mine_lines[:5000] == ref_lines} ({len(mine_lines)} lines total vs {len(ref_lines)} capped)")
    return out


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dst", type=Path, default=DST)
    a = ap.parse_args(argv)
    dst = a.dst
    dst.mkdir(parents=True, exist_ok=True)

    docs = {}
    docs["gib_realline_pooled"] = build_gibberish()
    docs["mhg_nibelungenlied"] = build_blocks(
        "mhg_nibelungenlied", "mhg_nibelungenlied", r"^(\d+)\. Aventiure$",
        lambda m: f"av{int(m.group(1)):02d}", lambda head, m: head, "HsA",
        "each `## N. Aventiure` block is a page (id avNN); the edited long-lines are the lines")
    docs["oldfrench_roland"] = build_blocks(
        "oldfrench_roland", "oldfrench_roland", r"^laisse (\d+)$",
        lambda m: f"l{int(m.group(1)):03d}", lambda head, m: head, "?",
        "each `## laisse N` block is a page (id lNNN); verse lines")
    docs["occitan_croisade"] = build_blocks(
        "occitan_croisade", "occitan_croisade_albigeoise", r"^laisse (\d+)$",
        lambda m: f"l{int(m.group(1)):03d}", lambda head, m: head, "?",
        "each `## laisse N` block is a page (id lNNN); verse lines")
    docs["italian_dante"] = build_dante()
    for name in list(docs):
        docs[f"{name}_relined{RELINE}"] = relined8(docs[name])

    written = []
    for name, doc in docs.items():
        p = dst / f"{name}.meta.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        written.append(p)

    # checks
    from scoreboard import run_v2 as R2  # import after ROOT is on sys.path (n7 idiom)
    rows, pres = [], []
    for name, doc in docs.items():
        c = counts(doc)
        ok, msg = preservation_check(dst / f"{name}.meta.json", R2)
        rows.append((name, c))
        pres.append((name, ok, msg))
    streams = stream_checks(docs)
    relined_ok = []
    for name in docs:
        if name.endswith(f"_relined{RELINE}"):
            base = name[: -len(f"_relined{RELINE}")]
            same_tokens = flat(docs[name]) == flat(docs[base])
            same_ids = [p["id"] for p in docs[name]["pages"]] == [p["id"] for p in docs[base]["pages"]]
            lens = [len(ln) for p in docs[name]["pages"] for ln in p["lines"]]
            all8 = all(x == RELINE for x in lens[:-1])
            relined_ok.append(f"{name}: same tokens in order={same_tokens} same page ids={same_ids} "
                              f"all lines but the last exactly {RELINE}={all8} last line={lens[-1]}")

    gib_n = counts(docs["gib_realline_pooled"])["tokens"]
    recon = (f"gib_realline_pooled tokens = {gib_n}; n7's gib_pooled (tools/gibberish_to_meta.py, 8x20 wrap) = "
             f"10,023; difference = {gib_n - 10023}. Same token rule and the same hyphen-join rule, so the "
             f"streams are identical token for token (checked above); only the line/page structure differs "
             f"(volunteers' lines, one page per writer, vs 8 tokens x 20 lines). s2 Part 1's "
             f"'Gibberish_38 (native)' counted 9,974 tokens because it stripped line-end '-' without joining "
             f"and dropped 1-token lines (s2_u1_u2_u3_controls.py:116-129).")

    stamp = subprocess.run(["date"], capture_output=True, text=True).stdout.strip() or \
        datetime.now().strftime("%Y-%m-%d %H:%M %Z (datetime.now)")
    sha = hashlib.sha256((ROOT / "tools" / "realline_to_meta.py").read_bytes()).hexdigest()
    md = [
        "# data/controls_realline — real-line control sidecars for Phase 1 s17",
        "",
        f"Built {stamp} by `python -I tools/realline_to_meta.py` (sha256 {sha}).",
        "Sidecar dialect: `run_v2.load_meta` (`id` page key; section/hand/lang/quire; `lines` = token lists).",
        "Every `<name>` keeps the source's own line breaks; `<name>_relined8` is the same token stream re-cut",
        "into 8-token lines with the same page ids (remainders carry to the next page; only the corpus's final",
        "line may be short). Score with `python -I scoreboard/run_v2.py --meta <file> --family L ...` (no `--lang`:",
        "every page has `lang=\"?\"`). Not globbed by n7/m4/n5 (those read data/controls_gibberish and",
        "data/controls_synthetic only). This folder is shared with s18: `cremma_*.meta.json` and",
        "`CREMMA_MANIFEST.md` are s18's (tools/cremma_to_meta.py), not covered by this README or by s17.",
        "",
        "## Sources and rules",
        "",
        "| sidecar | source | page unit (id) | line unit | token rule |",
        "|---|---|---|---|---|",
        "| gib_realline_pooled | 38 files `data/external/gaskell-bowern-gibberish/.../gibberish_transcriptions/Gibberish - <W>.txt` | writer (`<W>`) | volunteer's own line; `_` rules and blanks dropped; line-end `-` joined to next line's first token | `tools/gibberish_to_meta.py:clean_token` (NFKD, strip Mn, lower, a-z only) |",
        "| mhg_nibelungenlied | `data/controls/mhg_nibelungenlied.txt` | `## N. Aventiure` block (`avNN`) | edited long-line | `corpora_ext.tokenize` |",
        "| oldfrench_roland | `data/controls/oldfrench_roland.txt` | `## laisse N` block (`lNNN`) | verse line | `corpora_ext.tokenize` |",
        "| occitan_croisade | `data/controls/occitan_croisade_albigeoise.txt` | `## laisse N` block (`lNNN`) | verse line | `corpora_ext.tokenize` |",
        "| italian_dante | `data/controls/italian_dante.txt` (Gutenberg) | canto (`inf_NN`/`pur_NN`/`par_NN`; plus a 2-line `front` page holding the Gutenberg title lines verse_lines keeps) | verse line, >=3 tokens (a2_position.verse_lines rule, no 5000-line cap) | lower, NFD, strip Mn, `[a-zß]+` |",
        "",
        "`corpora_ext.tokenize` splits on apostrophes and brackets (`l’estoria` -> `l`, `estoria`; `emper[er]e` ->",
        "`emper`, `er`, `e`), as the m4 board's loader does for these files; s2 Part 1 instead deleted non a-z",
        "characters inside a token, so its token counts for Roland/Croisade/Nibelungenlied differ slightly.",
        "Gibberish lines of 77 and 82 tokens (writers DC_32, DC_40) are run-on lines in the source files, kept as is.",
        "",
        "## Counts",
        "",
        "| sidecar | pages | non-empty pages | lines | tokens | types | line length min/mode/max |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, c in rows:
        md.append(f"| {name} | {c['pages']} | {c['nonempty_pages']} | {c['lines']} | {c['tokens']} | {c['types']} | "
                  f"{c['min_len']}/{c['mode_len']}/{c['max_len']} |")
    md += ["", "## Line-preservation check (run_v2.load_meta + subsample(25000), per-line token counts vs sidecar)", ""]
    for name, ok, msg in pres:
        md.append(f"- {name}: {'PASS' if ok else 'FAIL'} — {msg}")
    md += ["", "## Stream checks against the project's own loaders", ""]
    md += [f"- {s}" for s in streams]
    md += ["", "## Re-lined twins", ""]
    md += [f"- {s}" for s in relined_ok]
    md += ["", "## Gibberish token reconciliation", "", recon, ""]
    (dst / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")

    print("\n".join(md))
    print("\nwrote:")
    for p in written + [dst / "README.md"]:
        print(f"  {p}")
    bad = [n for n, ok, _ in pres if not ok] + [s for s in streams if "False" in s] + \
          [s for s in relined_ok if "False" in s]
    if bad:
        print("\nCHECK FAILURES:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
