"""Extended control corpora (non-Latin scripts, medieval vernaculars, constructed texts, synthetic
controls) as word lists, mirroring corpora.control() but script-aware.

Files live in data/controls/<name>.txt (natural + constructed) or data/controls_synthetic/<name>.txt
(synthetic). Format: one source line per line; lines starting with "## " are section markers.

Tokenisation (control_ext):
  - lowercase; Unicode NFKD, then every combining mark (category Mn) is dropped: this removes
    Hebrew nikkud/cantillation, Arabic harakat, Greek accents/breathings and Latin-script
    diacritics alike, and folds long-s (U+017F) to s;
  - abjads (Hebrew, Arabic) are kept as unpointed consonantal text, final-letter forms kept;
  - a token is a maximal run of Unicode letters (\\w minus digits/underscore), so Hebrew, Arabic,
    Greek, Latin-script letters all survive; apostrophes/okina split words (Hawaiian 'okina is
    treated as a boundary, like the Latin-script controls' apostrophes);
  - no front-matter skip (the builder already removed front matter).
"""
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
DIRS = [HERE / "data" / "controls", HERE / "data" / "controls_synthetic"]

_WORD = re.compile(r"[^\W\d_]+")
_FOLD = str.maketrans({"ƈ": "c", "ſ": "s", "ß": "ss", "æ": "ae", "œ": "oe", "ꝛ": "r"})


def _path(name):
    for d in DIRS:
        p = d / f"{name}.txt"
        if p.exists():
            return p
    raise FileNotFoundError(name)


def tokenize(line, strip_marks=True):
    line = line.lower().translate(_FOLD)
    if strip_marks:
        line = "".join(c for c in unicodedata.normalize("NFKD", line)
                       if unicodedata.category(c) != "Mn")
    return _WORD.findall(line)


def control_ext_lines(name, strip_marks=True, with_sections=False):
    """List of lines, each a list of tokens (empty lines dropped). With with_sections=True,
    returns (lines, sections) where sections[i] is the current '## ' label of line i."""
    lines, secs, cur = [], [], "0"
    for raw in _path(name).read_text(encoding="utf-8").split("\n"):
        if raw.startswith("## "):
            cur = raw[3:].strip()
            continue
        toks = tokenize(raw, strip_marks)
        if toks:
            lines.append(toks)
            secs.append(cur)
    return (lines, secs) if with_sections else lines


def control_ext(name, n_tokens=None, strip_marks=True):
    words = [w for l in control_ext_lines(name, strip_marks) for w in l]
    return words[:n_tokens] if n_tokens else words


def control_ext_pages(name):
    """For synthetic controls with a .meta.json sidecar: list of pages, each a dict with
    'section' and 'lines' (list of token lists)."""
    p = _path(name).with_suffix(".meta.json")
    return json.loads(p.read_text(encoding="utf-8"))["pages"]


NATURAL = ["hebrew_torah", "arabic_quran", "greek_herodotus", "czech_bible_kralicka_1613",
           "occitan_croisade_albigeoise", "oldfrench_roland", "mhg_nibelungenlied", "mhg_parzival",
           "catalan_tirant", "turkish_kanun_medeni_1926", "latin_macer_floridus", "latin_pliny_herbal",
           "hawaiian_fornander", "tagalog_urbana_feliza_1864", "tagalog_florante_1838"]
CONSTRUCTED = ["enochian_keys_dee", "ignota_hildegard_glossary", "trithemius_steganographia_1608",
               "trithemius_polygraphia", "lull_ars_brevis_table"]
SYNTHETIC = ["nomen_word", "nomen_syll", "nomen_lines", "markov1", "rugg_grille", "naibbe_like",
             "latin_merged"]
