"""Load Voynich (in several glyph tokenizations) and control texts as word lists."""
import re
import unicodedata
from pathlib import Path

import vparse

CTRL = Path(__file__).parent / "data" / "controls"

# EVA multi-letter glyphs commonly read as single characters
GLYPHS = ["cth", "ckh", "cph", "cfh", "ch", "sh"]
GLYPHS_PLUS = GLYPHS + ["iiin", "iin", "in", "iir", "ir", "ee"]
SYMS = {g: chr(0x100 + i) for i, g in enumerate(GLYPHS_PLUS)}


def to_glyphs(word, units):
    for g in sorted(units, key=len, reverse=True):
        word = word.replace(g, SYMS[g])
    return word


def voynich(subset=None, tokenization="eva", drop_unclear=True, strict_spaces=False):
    recs = vparse.load(strict_spaces=strict_spaces)
    recs = vparse.paragraph_text(recs)
    if subset:
        recs = [r for r in recs if subset(r)]
    words = [w for r in recs for w in r["words"]]
    if drop_unclear:
        words = [w for w in words if "?" not in w]
    if tokenization == "glyph":
        words = [to_glyphs(w, GLYPHS) for w in words]
    elif tokenization == "glyph+":
        words = [to_glyphs(w, GLYPHS_PLUS) for w in words]
    return words


def voynich_lines(subset=None, drop_unclear=True):
    recs = vparse.paragraph_text(vparse.load())
    if subset:
        recs = [r for r in recs if subset(r)]
    out = []
    for r in recs:
        ws = [w for w in r["words"] if not (drop_unclear and "?" in w)]
        if ws:
            out.append(dict(r, words=ws))
    return out


def strip_gutenberg(text):
    s = re.search(r"\*\*\* ?START OF.*?\*\*\*", text)
    e = re.search(r"\*\*\* ?END OF", text)
    return text[s.end() if s else 0: e.start() if e else len(text)]


def control(name, n_tokens=None, strip_accents=True):
    text = strip_gutenberg((CTRL / f"{name}.txt").read_text(encoding="utf-8", errors="replace"))
    text = text.lower()
    if strip_accents:
        text = "".join(c for c in unicodedata.normalize("NFD", text)
                       if unicodedata.category(c) != "Mn")
    words = re.findall(r"[a-zß]+", text)
    # skip front matter so the sample is running text
    words = words[len(words) // 20:]
    return words[:n_tokens] if n_tokens else words


CONTROLS = ["latin_caesar", "latin_augustine", "italian_dante",
            "german_faust", "german_kafka", "english_alice"]
