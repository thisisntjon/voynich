"""Corpus: the one input shape every scoreboard metric is computed on.

A Corpus is a list of pages in reading order. Each page is a dict:

    page_id : str   folio / block identifier (unique within the corpus)
    section : str   subject label ("H","S","B","T","P","C","A" for Voynich
                    = the IVTFF $I illustration code; "?" if unknown)
    hand    : str   scribe label ("?" if unknown)
    lang    : str   Currier language label ("?" if unknown)
    quire   : str   quire label ("?" if unknown)
    lines   : list[list[str]]   tokens of each line, in order
    block   : str   (optional) grouping unit for the NMF permutation /
                    rotation nulls; defaults to page_id

All token-stream metrics flatten `pages -> lines -> tokens` in this order,
so the first n_tokens of `corpus.words()` are what a1/a7/b3 saw.

Constructors
------------
from_voynich(tokenization, subset)      ZL3b paragraph text via vparse/corpora
from_control(name, lines=None|"verse"|int) Gutenberg controls via corpora.control
from_wordlist(words, line_len, page_len) any flat list, optionally re-wrapped
from_meta_json(path)                      synthetic corpora with a sidecar

Sidecar format (.meta.json), produced by the synthetic-corpus colleague:

    {"pages": [{"id": "p001", "section": "H",
                "hand": "1", "lang": "A", "quire": "1",   # optional
                "lines": [["tok", "tok", ...], ...]}, ...]}

Only "id" and "lines" are required; "section" defaults to "?". Extra keys
are kept on the page dict untouched. If the path given ends in ".txt" the
loader looks for "<path>.meta.json" next to it and ignores the .txt.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import corpora  # noqa: E402

UNKNOWN = "?"


def _page(page_id, lines, section=UNKNOWN, hand=UNKNOWN, lang=UNKNOWN,
          quire=UNKNOWN, **extra):
    d = dict(page_id=str(page_id), section=str(section), hand=str(hand),
             lang=str(lang), quire=str(quire), lines=[list(l) for l in lines])
    d.update(extra)
    return d


@dataclass
class Corpus:
    name: str
    pages: list = field(default_factory=list)
    # False when the corpus is a flat word list with no real/pseudo lines:
    # line-position and column metrics are then reported as None.
    has_lines: bool = True
    tokenization: str = "eva"
    source: dict = field(default_factory=dict)

    # ---- views -----------------------------------------------------------
    def words(self):
        return [w for p in self.pages for l in p["lines"] for w in l]

    def lines(self):
        return [l for p in self.pages for l in p["lines"]]

    def body_lines(self):
        """Lines 2+ of each page (b4_selfcite_sim.report convention)."""
        return [l for p in self.pages for l in p["lines"][1:]]

    def page_lines(self):
        """[(page_id, [line, ...]), ...] in order."""
        return [(p["page_id"], p["lines"]) for p in self.pages]

    def tokens_meta(self):
        """[(word, (lang, section, hand), page_id), ...] as a4b.tokens()."""
        return [(w, (p["lang"], p["section"], p["hand"]), p["page_id"])
                for p in self.pages for l in p["lines"] for w in l]

    def has_meta(self, key):
        return any(p.get(key, UNKNOWN) != UNKNOWN for p in self.pages)

    def n_tokens(self):
        return sum(len(l) for p in self.pages for l in p["lines"])

    def summary(self):
        return dict(name=self.name, pages=len(self.pages),
                    lines=len(self.lines()), tokens=self.n_tokens(),
                    has_lines=self.has_lines, tokenization=self.tokenization,
                    sections=sorted({p["section"] for p in self.pages}),
                    hands=sorted({p["hand"] for p in self.pages}),
                    langs=sorted({p["lang"] for p in self.pages}))

    # ---- constructors ----------------------------------------------------
    @classmethod
    def from_voynich(cls, tokenization="eva", subset=None, drop_unclear=True):
        """ZL3b-n paragraph text (P* units), '?'-words dropped, grouped by
        folio in file order. Identical token stream to corpora.voynich(
        tokenization=...) and identical lines to corpora.voynich_lines().
        tokenization: "eva" | "glyph" (ch sh cth ckh cph cfh collapsed) |
        "glyph+" (also iiin iin in iir ir ee); see corpora.GLYPHS(_PLUS)."""
        units = {"eva": None, "glyph": corpora.GLYPHS,
                 "glyph+": corpora.GLYPHS_PLUS}[tokenization]
        recs = corpora.voynich_lines(subset=subset, drop_unclear=drop_unclear)
        pages, order = {}, []
        for r in recs:
            ws = r["words"]
            if units:
                ws = [corpora.to_glyphs(w, units) for w in ws]
            if r["page"] not in pages:
                order.append(r["page"])
                pages[r["page"]] = _page(r["page"], [], section=r["illus"],
                                         hand=r["hand"], lang=r["lang"],
                                         quire=r["quire"])
            pages[r["page"]]["lines"].append(ws)
        name = "voynich" if tokenization == "eva" else f"voynich:{tokenization}"
        if subset is not None:
            name += ":subset"
        return cls(name=name, pages=[pages[p] for p in order],
                   tokenization=tokenization,
                   source=dict(kind="voynich", data=str(corpora.vparse.DATA),
                               tokenization=tokenization,
                               drop_unclear=drop_unclear))

    @classmethod
    def from_wordlist(cls, words, line_len=None, page_len=30, name="wordlist",
                      section=UNKNOWN, **meta):
        """Flat control. line_len=None keeps one page with one line and sets
        has_lines=False (position metrics return None). line_len=k wraps the
        stream into pseudo-lines of k tokens and pages of page_len lines, so
        line/column/NMF metrics run on an a-structural baseline."""
        words = list(words)
        if line_len is None:
            return cls(name=name, pages=[_page("p0", [words], section=section, **meta)],
                       has_lines=False,
                       source=dict(kind="wordlist", line_len=None))
        lines = [words[i:i + line_len] for i in range(0, len(words), line_len)]
        pages = [_page(f"p{j:04d}", lines[i:i + page_len], section=section, **meta)
                 for j, i in enumerate(range(0, len(lines), page_len))]
        return cls(name=name, pages=pages,
                   source=dict(kind="wordlist", line_len=line_len, page_len=page_len))

    @classmethod
    def from_control(cls, name, lines=None, n_tokens=None, page_len=30):
        """Gutenberg control from data/controls/<name>.txt.
        lines=None   : corpora.control(name) stream (front 5% skipped), flat.
        lines=int    : same stream wrapped into pseudo-lines of that length.
        lines="verse": the file's own line breaks, lines with >=3 words,
                       first 5000 lines (a2_position.verse_lines convention;
                       note this stream is NOT the corpora.control stream:
                       no 5% skip, all lines kept)."""
        if lines == "verse":
            from a2_position import verse_lines
            vl = verse_lines(name)
            pages = [_page(f"p{j:04d}", vl[i:i + page_len])
                     for j, i in enumerate(range(0, len(vl), page_len))]
            return cls(name=f"{name}:verse", pages=pages,
                       source=dict(kind="control", control=name, lines="verse",
                                   page_len=page_len))
        words = corpora.control(name, n_tokens)
        c = cls.from_wordlist(words, line_len=lines, page_len=page_len, name=name)
        c.source = dict(kind="control", control=name, lines=lines, n_tokens=n_tokens,
                        page_len=page_len)
        if lines is not None:
            c.name = f"{name}:lines{lines}"
        return c

    @classmethod
    def from_control_sections(cls, name, header_re, chunk=40, block_chunks=5):
        """Control with section labels taken from in-text headers, laid out
        exactly as b5_nmf_topics.control_chunks: pages of `chunk` tokens
        (one NMF chunk each) labelled by the majority token label, with
        block = chunk_index // block_chunks for the permutation/rotation
        nulls. Used for the b5 CTRL rows (Dante canticles, Augustine books)."""
        from b5_nmf_topics import control_chunks
        import b5_nmf_topics as b5
        assert b5.CHUNK == chunk
        cc = control_chunks(name, header_re)
        pages = [_page(f"c{i:05d}", [c["text"].split(" ")], section=c["label"],
                       block=str(c["block"]))
                 for i, c in enumerate(cc)]
        return cls(name=f"{name}:sections", pages=pages,
                   source=dict(kind="control_sections", control=name,
                               header_re=header_re, chunk=chunk,
                               block_chunks=block_chunks))

    @classmethod
    def from_meta_json(cls, path, name=None):
        """Synthetic corpus from a .meta.json sidecar (format in the module
        docstring). `path` may be the sidecar itself or the .txt it sits
        beside (then '<path>.meta.json' is read)."""
        path = Path(path)
        if path.suffix != ".json":
            cand = path.with_name(path.name + ".meta.json")
            if not cand.exists():
                cand = path.with_suffix(".meta.json")
            path = cand
        data = json.loads(path.read_text(encoding="utf-8"))
        pages = []
        for i, p in enumerate(data["pages"]):
            extra = {k: v for k, v in p.items()
                     if k not in ("id", "section", "hand", "lang", "quire", "lines")}
            pages.append(_page(p.get("id", f"p{i:04d}"), p["lines"],
                               section=p.get("section", UNKNOWN),
                               hand=p.get("hand", UNKNOWN), lang=p.get("lang", UNKNOWN),
                               quire=p.get("quire", UNKNOWN), **extra))
        return cls(name=name or data.get("name") or path.stem.replace(".meta", ""),
                   pages=pages, tokenization=data.get("tokenization", "eva"),
                   source=dict(kind="meta_json", path=str(path)))


def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


__all__ = ["Corpus", "UNKNOWN", "strip_accents", "re"]
