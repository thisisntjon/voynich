"""Parse the ZL IVTFF EVA transliteration into structured lines.

Each record: dict(page, locus, unit, lang, hand, illus, quire, words)
Readings: [a:b] -> first alternative; {xy} ligature -> xy; @nnn; -> '?';
',' (uncertain space) -> word break unless STRICT_SPACES.
"""
import re
from pathlib import Path

DATA = Path(__file__).parent / "data" / "ZL3b-n.txt"

PAGE_RE = re.compile(r"^<(f\w+)>\s+<!(.*)>")
LINE_RE = re.compile(r"^<(f\w+)\.(\d+),(.)(\w+)>\s+(.*)$")
VAR_RE = re.compile(r"\$(\w)=(\w+)")


def clean(text, strict_spaces=False):
    text = re.sub(r"<![^>]*>", "", text)          # inline comments
    text = re.sub(r"<->", ".", text)               # drawing interruption = break
    text = re.sub(r"<[^>]*>", "", text)            # <%> <$> etc
    text = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", text)  # alternatives
    text = re.sub(r"@\d+;", "?", text)            # rare glyphs
    text = text.replace("{", "").replace("}", "").replace("'", "")
    if not strict_spaces:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    return [w for w in text.split(".") if w]


def load(strict_spaces=False, path=DATA):
    meta = {}
    recs = []
    for raw in path.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = PAGE_RE.match(raw)
        if m:
            meta = dict(VAR_RE.findall(m.group(2)))
            meta["page"] = m.group(1)
            continue
        m = LINE_RE.match(raw)
        if not m:
            continue
        page, n, _, unit, text = m.groups()
        recs.append(dict(
            page=page, line=int(n), unit=unit,
            lang=meta.get("L", "?"), hand=meta.get("H", "?"),
            illus=meta.get("I", "?"), quire=meta.get("Q", "?"),
            words=clean(text, strict_spaces),
        ))
    return recs


def paragraph_text(recs):
    """Records from running-text units (P*), excluding labels/circles/radii."""
    return [r for r in recs if r["unit"].startswith("P")]


if __name__ == "__main__":
    recs = load()
    words = [w for r in recs for w in r["words"]]
    print(len(recs), "lines", len(words), "tokens", len(set(words)), "types")
    from collections import Counter
    print(Counter(r["lang"] for r in recs))
    print(Counter(r["illus"] for r in recs))
    print(Counter(r["unit"][0] for r in recs))
