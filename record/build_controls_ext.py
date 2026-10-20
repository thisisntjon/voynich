"""Build the extended control corpora from the raw downloads in data/controls_raw/.

Run from the project root:  python build_controls_ext.py
Outputs plain UTF-8 text into data/controls/ (natural languages, constructed texts).
File format: one source line per line (verse line, verse, or paragraph); lines that
start with "## " are section markers (book / chapter / sura) and are not text.
corpora_ext.control_ext() / control_ext_lines() know this format.

Nothing from data/controls_raw/ is executed; it is read as data only.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "controls_raw"
OUT = ROOT / "data" / "controls"
OUT.mkdir(parents=True, exist_ok=True)


def html_text(h):
    h = re.sub(r"<(script|style)\b.*?</\1>", "", h, flags=re.S | re.I)
    h = re.sub(r"<(sup|span)\b[^>]*class=\"[^\"]*(reference|pagenum|mw-editsection)[^\"]*\"[^>]*>.*?</\1>",
               "", h, flags=re.S)
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</(p|div|li|tr|h\d|dd|dt)>", "\n", h, flags=re.I)
    h = re.sub(r"<[^>]+>", "", h)
    return html.unescape(h)


def ws_text(path):
    return html_text(json.loads(Path(path).read_text(encoding="utf-8"))["parse"]["text"]["*"])


def write(name, lines, min_words=0):
    text = "\n".join(lines) + "\n"
    (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
    n = sum(len(l.split()) for l in lines if not l.startswith("## "))
    print(f"{name:32} lines={len(lines):6}  words~{n}")


def clean_lines(text, drop_patterns=()):
    out = []
    for l in text.split("\n"):
        l = l.strip()
        if not l:
            continue
        if any(re.search(p, l) for p in drop_patterns):
            continue
        out.append(l)
    return out


# ---------------------------------------------------------------- Hebrew (Sefaria, Torah)
def hebrew():
    lines = []
    for book, fn in [("Genesis", "genesis.json"), ("Exodus", "Exodus.json"), ("Leviticus", "Leviticus.json"),
                     ("Numbers", "Numbers.json"), ("Deuteronomy", "Deuteronomy.json")]:
        d = json.loads((RAW / "hebrew" / fn).read_text(encoding="utf-8"))
        lines.append(f"## {book}")
        for ch in d["he"]:
            for v in ch:
                v = html_text(v)
                v = re.sub(r"[֑-ׇ]", "", v)      # cantillation + nikkud + sof pasuq etc.
                v = v.replace("־", " ")                # maqaf
                v = re.sub(r"[^א-ת\s]", " ", v)   # keep Hebrew letters only
                v = " ".join(v.split())
                if v:
                    lines.append(v)
    write("hebrew_torah", lines)


# ---------------------------------------------------------------- Arabic (tanzil simple-clean)
def arabic():
    lines, cur = [], None
    for l in (RAW / "arabic" / "quran-simple-clean.txt").read_text(encoding="utf-8").split("\n"):
        m = re.match(r"(\d+)\|(\d+)\|(.*)", l)
        if not m:
            continue
        s, v, t = m.groups()
        if s != cur:
            cur = s
            lines.append(f"## sura {s}")
        t = re.sub(r"[ً-ٰٟۖ-ۭـ]", "", t)  # harakat, superscript alef, tatweel
        t = re.sub(r"[^ء-ي\s]", " ", t)
        t = " ".join(t.split())
        if t:
            lines.append(t)
    write("arabic_quran", lines)


# ---------------------------------------------------------------- Greek (Perseus Herodotus)
def greek():
    x = (RAW / "greek" / "herodotus.xml").read_text(encoding="utf-8")
    x = x[x.find("<body"):]
    x = re.sub(r"<note\b.*?</note>", "", x, flags=re.S)
    x = re.sub(r"<bibl\b.*?</bibl>", "", x, flags=re.S)
    lines = []
    for m in re.finditer(r"<div[^>]*subtype=\"book\"[^>]*n=\"(\d+)\"[^>]*>(.*?)(?=<div[^>]*subtype=\"book\"|</body>)", x, flags=re.S):
        lines.append(f"## book {m.group(1)}")
        for p in re.findall(r"<p\b[^>]*>(.*?)</p>", m.group(2), flags=re.S):
            t = " ".join(html.unescape(re.sub(r"<[^>]+>", "", p)).split())
            if t:
                lines.append(t)
    write("greek_herodotus", lines)


# ---------------------------------------------------------------- Czech (Bible kralicka 1613)
def czech():
    lines = []
    for book in ["Genesis", "Exodus", "Leviticus"]:
        t = ws_text(RAW / "czech" / f"{book}.json")
        # body starts at first verse "1 " after the metadata block; drop the wikisource chrome
        i = t.find("Kapitola")
        if i < 0:
            i = 0
        body = t[i:]
        lines.append(f"## {book}")
        for l in clean_lines(body, drop_patterns=[r"^Kapitola\b", r"^\[", r"^Údaje", r"^Titulek", r"^Autor",
                                                    r"^Zdroj", r"^Licence", r"^Vydáno", r"^Jazyk"]):
            l = re.sub(r"^\d+\s*", "", l)
            if len(l.split()) >= 2:
                lines.append(l)
    write("czech_bible_kralicka_1613", lines)


# ---------------------------------------------------------------- Occitan (Croisade albigeoise)
def occitan():
    t = ws_text(RAW / "occitan" / "croisade_chanson.json")
    i = t.find("EL nom del Payre")
    body = t[i:]
    lines, n = ["## laisse 1"], 1
    for l in clean_lines(body):
        if re.fullmatch(r"[IVXLC]+\.?(\[\d+\])?", l):
            n += 1
            lines.append(f"## laisse {n}")
            continue
        if re.match(r"^\(p\. ?\d+\)$", l) or re.match(r"^\[\d+\]", l) or l.startswith("↑"):
            continue
        l = re.sub(r"^\(p\. ?\d+\)", "", l).strip()
        l = re.sub(r"^\d+", "", l).strip()            # verse numbers glued to the line start
        l = re.sub(r"\[\d+\]", "", l)
        # the page carries Meyer's French apparatus after the poem: stop at its first line
        if n >= 214 and re.search(r"\bms\.|\bcorr\.|Réd\. en pr|\bvoy\.|\bmanque|^— ?\d+\.", l):
            break
        if re.search(r"[a-zA-Z]{2,}", l) and not l.startswith("Note"):
            lines.append(l)
        if "Lor defendra Tholoza" in l:      # last verse of the poem
            break
    write("occitan_croisade_albigeoise", lines)


# ---------------------------------------------------------------- Old French (Roland, Oxford MS)
def oldfrench():
    t = ws_text(RAW / "oldfrench" / "roland_mortier.json")
    i = t.find("Carles li reis")
    body = t[i:]
    lines, n = ["## laisse 1"], 1
    for l in clean_lines(body, drop_patterns=[r"^\[modifier\]", r"^modifier$"]):
        if re.fullmatch(r"[IVXLC]+", l):
            n += 1
            lines.append(f"## laisse {n}")
            continue
        l = re.sub(r"^\d+", "", l).strip()
        l = re.sub(r"\s*AOI\.?$", "", l)
        l = re.sub(r"\[\d+\]", "", l)
        if re.search(r"[a-zA-Z]{2,}", l):
            lines.append(l)
    write("oldfrench_roland", lines)


# ---------------------------------------------------------------- Middle High German (Augustana)
def augustana(files, name, section_pat):
    lines = []
    for f in files:
        t = html_text(f.read_text(encoding="utf-8", errors="replace"))
        for l in clean_lines(t, drop_patterns=[r"Augustana", r"AUGUSTANA", r"<<<", r">>>", r"Übersicht",
                                                r"^Handschrift", r"^\d{4}", r"Wolfram von Eschenbach$",
                                                r"^Das Nibelungenlied$", r"^Parzival$", r"^Buch\s", r"^\(.*\)$"]):
            if re.match(section_pat, l):
                lines.append(f"## {l}")
                continue
            l = re.sub(r"^\d+\s*", "", l)
            l = re.sub(r"\s+\d+$", "", l)
            if re.search(r"[a-zA-Z]{2,}", l):
                lines.append(l)
    write(name, lines)


def mhg():
    nib = sorted((RAW / "mhg").glob("nib_a_*.html"))
    augustana(nib, "mhg_nibelungenlied", r"^\d+\. Aventiure")
    wol = sorted((RAW / "mhg").glob("wol_pa*.html"))
    augustana(wol, "mhg_parzival", r"^[IVX]+\.?\s*$|^\d+\. Buch")


# ---------------------------------------------------------------- Catalan (Tirant 1905)
def catalan():
    files = []
    for f in (RAW / "catalan").glob("*.json"):
        m = re.search(r"\((\d{4})\)_(\d)_Capítol_(\d+)", f.name)
        if m:
            files.append((int(m.group(2)), int(m.group(3)), f))
    files.sort()
    lines = []
    for vol, cap, f in files:
        t = ws_text(f)
        i = re.search(r"\nCAPITOL\s", t)
        body = t[i.start():] if i else t
        lines.append(f"## vol {vol} capitol {cap}")
        for l in clean_lines(body, drop_patterns=[r"^CAPITOL\b", r"^Capítol \d", r"^Baixa com", r"^Sou a",
                                                    r"djvu", r"^\[", r"^Tirant lo Blanch$"]):
            if len(l.split()) >= 3:
                lines.append(l)
    write("catalan_tirant", lines)


# ---------------------------------------------------------------- Turkish (1926 civil code)
def turkish():
    t = ws_text(RAW / "turkish" / "kanun_743.json")
    i = t.find("Kanun Numarası")
    body = t[i:]
    lines, sec = [], 0
    for l in clean_lines(body, drop_patterns=[r"^\{\{", r"^\}\}", r"^\|", r"^Kanun Numarası", r"^Kabul", r"^Yayımlandığı",
                                                r"^\*\*"]):
        if re.match(r"^[A-ZÇĞİÖŞÜ]+ KİTAP\b", l) or re.match(r"^(BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ) KİTAP", l):
            sec += 1
            lines.append(f"## kitap {sec}")
            continue
        if len(l.split()) >= 3:
            lines.append(l)
    write("turkish_kanun_medeni_1926", lines)


# ---------------------------------------------------------------- Latin herbal (Macer; Pliny XX-XXVII)
def latin_herbal():
    t = ws_text(RAW / "latin_herbal" / "macer.json")
    i = t.find("I.  Artemisia")
    if i < 0:
        i = t.find("Artemisia")
    body = t[i:]
    lines = []
    for l in clean_lines(body, drop_patterns=[r"^\[recensere\]", r"^\[", r"^↑", r"EPUB", r"^editio", r"^fons"]):
        l = l.replace("[recensere]", "").strip()
        if re.match(r"^[IVXLC]+\.\s+\S", l):
            lines.append("## " + l.strip("."))
            continue
        l = re.sub(r"\s+\d+$", "", l)
        if re.search(r"[a-zA-Z]{2,}", l):
            lines.append(l)
    write("latin_macer_floridus", lines)

    lines = []
    for n in ["XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII"]:
        t = ws_text(RAW / "latin_herbal" / f"pliny_{n}.json")
        lines.append(f"## liber {n}")
        for l in clean_lines(t, drop_patterns=[r"^Liber\s", r"^Gaius", r"^Naturalis", r"^\d+ - \d+", r"^\[", r"^↑"]):
            l = re.sub(r"\[\d+\]", "", l)
            if len(l.split()) >= 4 and re.search(r"[a-zA-Z]{2,}", l):
                lines.append(l)
    write("latin_pliny_herbal", lines)


# ---------------------------------------------------------------- Tagalog (Gutenberg)
def gutenberg_body(path):
    t = path.read_text(encoding="utf-8", errors="replace")
    s = re.search(r"\*\*\* ?START OF.*?\*\*\*", t)
    e = re.search(r"\*\*\* ?END OF", t)
    return t[s.end() if s else 0: e.start() if e else len(t)]


CREDITS = re.compile(r"Produced by|Project Gutenberg|Distributed Proofread|Transcriber|E-text prepared", re.I)


def paragraphs(text):
    out = []
    for p in re.split(r"\n\s*\n", text):
        p = " ".join(p.split())
        if p and not CREDITS.search(p):
            out.append(p)
    return out


def tagalog():
    body = gutenberg_body(RAW / "tagalog" / "15980.txt").replace("~", "")
    lines = [p for p in paragraphs(body) if len(p.split()) >= 4]
    write("tagalog_urbana_feliza_1864", lines)
    body = gutenberg_body(RAW / "tagalog" / "15845.txt").replace("~", "")
    lines = [l.strip() for l in body.split("\n") if len(l.split()) >= 3 and not CREDITS.search(l)]
    write("tagalog_florante_1838", lines)


# ---------------------------------------------------------------- Hawaiian (Fornander, Hawaiian lines only)
def hawaiian():
    hw = set("aeiouhklmnpw")
    lines = []
    for vol, fn in [(1, "72686.txt"), (2, "73166.txt"), (3, "74570.txt")]:
        body = gutenberg_body(RAW / "hawaiian" / fn)
        lines.append(f"## volume {vol}")
        for l in body.split("\n"):
            ws_ = re.findall(r"[A-Za-zʻ'‘’]+", l)
            if len(ws_) < 4:
                continue
            # genealogy tables mark sex with (w)/(k) and list bare names: skip them
            if any(w.lower() in ("w", "k") for w in ws_) or sum(w[0].isupper() for w in ws_) > len(ws_) // 2:
                continue
            if all(set(re.sub(r"[ʻ'‘’]", "", w).lower()) <= hw for w in ws_):
                lines.append(l.strip())
    write("hawaiian_fornander", lines)


# ---------------------------------------------------------------- constructed texts
def enochian():
    t = html_text((RAW / "constructed" / "liber_chanokh_wayback.html").read_text(encoding="utf-8", errors="replace"))
    paras = [p for p in paragraphs(t)]
    lines, k = [], 0
    for i, p in enumerate(paras):
        if re.fullmatch(r"THE [A-Z\-]+ KEY", p) or p.startswith("THE CALL OR KEY OF THE THIRTY"):
            # the Enochian text is the first substantive paragraph after the header
            j = i + 1
            while j < len(paras) and (len(paras[j].split()) < 5 or paras[j].startswith("THE ")):
                j += 1
            if j < len(paras) and not paras[j].startswith("Liber"):
                k += 1
                lines.append(f"## key {k}")
                lines.append(re.sub(r"\d+\)", "", paras[j]))
    write("enochian_keys_dee", lines)


def lingua_ignota():
    wt = json.loads((RAW / "constructed" / "lingua_ignota_wp.json").read_text(encoding="utf-8"))["parse"]["wikitext"]["*"]
    words = re.findall(r"\{\{lang\|art-DE\|([^}|]+)\}\}", wt)
    seen, out = set(), []
    for w in words:
        w = w.strip()
        if w and w not in seen:
            seen.add(w)
            out.append(w)
    write("ignota_hildegard_glossary", ["## glossary sample (Roth 1895 via Wikipedia)"] + out)


def trithemius():
    for src, name in [("trithemius_steganographia_1608_ocr.txt", "trithemius_steganographia_1608"),
                      ("trithemius_polygraphia_wellcome_ocr.txt", "trithemius_polygraphia")]:
        t = (RAW / "constructed" / src).read_text(encoding="utf-8", errors="replace")
        lines = [l.strip() for l in t.split("\n") if len(re.findall(r"[A-Za-z]{2,}", l)) >= 3]
        write(name, lines)


def main():
    for fn in [hebrew, arabic, greek, czech, occitan, oldfrench, mhg, catalan, turkish, latin_herbal,
               tagalog, hawaiian, enochian, lingua_ignota, trithemius]:
        try:
            fn()
        except Exception as e:  # keep going; report at the end
            print(f"FAILED {fn.__name__}: {e!r}")


if __name__ == "__main__":
    main()
