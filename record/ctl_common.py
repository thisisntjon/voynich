"""Shared helpers for the generated-text (G) controls of PLAN Phase 0 item 4:
ctl_timm_schinner.py, ctl_schwartz.py, ctl_c2_best.py, ctl_report.py.

Page/line shape: every synthetic text is poured into the real Voynich ZL3b
paragraph-text shape (vparse.load() + vparse.paragraph_text(), tokens containing
'?' dropped and empty lines dropped, exactly as corpora.voynich_lines() does for
a1/b4/c2), so each synthetic page has the same number of lines and each line the
same number of tokens as the real page, with the real section (illustration
code), hand, Currier language and quire copied into the sidecar.

Sidecar format (read by scoreboard.corpus.Corpus.from_meta_json):
    {"name": ..., "pages": [{"id": "f1r", "section": "H", "hand": "1",
                             "lang": "A", "quire": "A", "lines": [[tok, ...], ...]}, ...]}
The .txt beside it has one text line per line and a "## <section>" marker
whenever the section changes (corpora_ext convention).

Statistics (ctl_stats): tokens, types, h2 = a1_profile.char_entropies (space is a
symbol: " ".join(words) + " "), word-length mean/SD over all tokens, immediate
repeat rate over the whole token stream, and p-initial / m-final line-edge
enrichment via b4_selfcite_sim.enrich on lines 2+ of every page (the b4/c2
convention that gives Voynich x15.97 / x16.55) and, for reference, on all lines.
"""
import json
import math
from collections import Counter
from pathlib import Path

import corpora
from a1_profile import char_entropies
from b4_selfcite_sim import enrich

ROOT = Path(__file__).parent
OUT = ROOT / "data" / "controls_synthetic"
OUT.mkdir(parents=True, exist_ok=True)

VOYNICH_TARGETS = dict(h2=2.13, sd_len=1.76, repeat_pct=0.90, p_init=16.0, m_final=16.6)


def voynich_pages():
    """Real ZL3b paragraph pages, in manuscript order: list of dicts
    id, section, hand, lang, quire, lines (list of token lists)."""
    pages, order = {}, []
    for r in corpora.voynich_lines():
        p = r["page"]
        if p not in pages:
            pages[p] = dict(id=p, section=r["illus"], hand=r["hand"], lang=r["lang"],
                            quire=r["quire"], lines=[])
            order.append(p)
        pages[p]["lines"].append(list(r["words"]))
    return [pages[p] for p in order]


def shape_of(pages):
    return [[len(l) for l in p["lines"]] for p in pages]


def pour(tokens, template=None):
    """Fill the Voynich page/line shape with a flat token stream, in order.
    Raises if the stream is too short."""
    template = template or voynich_pages()
    it = iter(tokens)
    out = []
    for p in template:
        lines = []
        for l in p["lines"]:
            try:
                lines.append([next(it) for _ in l])
            except StopIteration:
                raise ValueError("token stream shorter than the Voynich shape")
        out.append(dict(p, lines=lines))
    return out


def write_control(name, pages, **meta):
    """Write data/controls_synthetic/<name>.txt and <name>.meta.json."""
    txt, last = [], None
    for p in pages:
        if p.get("section") != last:
            txt.append(f"## {p.get('section', '?')}")
            last = p.get("section")
        txt.extend(" ".join(l) for l in p["lines"])
    (OUT / f"{name}.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
    (OUT / f"{name}.meta.json").write_text(
        json.dumps(dict(name=name, **meta, pages=pages), ensure_ascii=False), encoding="utf-8")
    return OUT / f"{name}.txt"


def ctl_stats(pages):
    words = [w for p in pages for l in p["lines"] for w in l]
    lens = [len(w) for w in words]
    mean = sum(lens) / len(lens)
    sd = math.sqrt(sum((x - mean) ** 2 for x in lens) / len(lens))
    rep = sum(a == b for a, b in zip(words, words[1:])) / len(words)
    ce = char_entropies(words)
    lines2 = [l for p in pages for l in p["lines"][1:]]
    lines_all = [l for p in pages for l in p["lines"]]
    return dict(tokens=len(words), types=len(set(words)), hapax=sum(1 for v in Counter(words).values() if v == 1),
                h1=ce["h1"], h2=ce["h2"], mean_len=mean, sd_len=sd, repeat_pct=100 * rep,
                p_init=enrich(lines2, "p", "first"), m_final=enrich(lines2, "m", "last"),
                p_init_all=enrich(lines_all, "p", "first"), m_final_all=enrich(lines_all, "m", "last"))


def stats_row(name, st):
    return (f"{name:22} tokens={st['tokens']:6d} types={st['types']:5d} hapax={st['hapax']:5d} "
            f"h2={st['h2']:.3f} len={st['mean_len']:.2f}+-{st['sd_len']:.2f} repeat={st['repeat_pct']:.2f}% "
            f"p-init x{st['p_init']:5.2f} m-final x{st['m_final']:5.2f} "
            f"(all lines x{st['p_init_all']:5.2f}/x{st['m_final_all']:5.2f})")


def load_control(name):
    return json.loads((OUT / f"{name}.meta.json").read_text(encoding="utf-8"))["pages"]
