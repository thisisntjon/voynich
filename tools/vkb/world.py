"""VKB world module: corpora, corpus_stats, sources, external_items (see tools/vkb/README.md).

build(conn) drops and refills the four tables. Every row carries src (path or path:line).

Canonical inputs (parsed at build time, so a rebuild follows the files):
  corpora       data/CONTROLS_MANIFEST.md; data/controls_*/README.md, data/controls_realline/CREMMA_MANIFEST.md;
                data/herbals_*/README.md; data/external/README.md and genre-s87/s89 MANIFEST.md;
                runs/roach-r7, r11, r12 README.md; s97/s102/s104/s107/s108 script headers; corpora.py.
  corpus_stats  results_s87(_amend1), s89(_amend1), s90, s97, s102, s104, s107, s108 (lead profile lines);
                runs/roach-r7, r11 (fold/block rows; corpus value = median over folds/blocks, computed here);
                runs/roach-r12 (whole-text rows); runs/explore/wordlen_perline_bias_20261018.txt;
                data/CONTROLS_MANIFEST.md h2 column (a1_profile definition).
Snapshots (the scratchpad files are not canonical and may vanish; their rows are embedded below with the
scratchpad path:line as src): completeness_gap.md (sources), sprawl_external.md (external_items).
intake.md, if present in the scratchpad at build time, overrides external_items.intake_class.

Schema extensions beyond the README (flagged for the README owner): corpora.kind, corpora.note;
corpus_stats.p, ci_lo, ci_hi, n_tokens, segmenter, pipeline, label, scope, note. The extra corpus_stats columns
are what makes "rank Voynich among texts on statistic X" answerable only within one definition: compare rows
with the same (statistic, pipeline, segmenter, scope).
"""
import os, re, sys, glob, statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, create, insert  # noqa: E402

SCRATCH = os.path.join(ROOT, ".inventory", "runs", "2026-10-18")  # audit reports copied from the 2026-10-18 scratchpad, byte-identical
GAP_MD = os.path.join(SCRATCH, "audit-completeness_gap.md")
SPRAWL_MD = os.path.join(SCRATCH, "audit-sprawl_external.md")
INTAKE_MD = os.path.join(SCRATCH, "audit-intake.md")


# ----------------------------------------------------------------------------------------------- helpers
def P(rel_path):
    return os.path.join(ROOT, rel_path)


_cache = {}


def lines_of(rel_path):
    if rel_path not in _cache:
        try:
            with open(P(rel_path), encoding="utf-8", errors="replace") as f:
                _cache[rel_path] = f.read().split("\n")
        except FileNotFoundError:
            _cache[rel_path] = None
    return _cache[rel_path]


def find_line(rel_path, needle, start=1):
    """path:line of the first line (>= start) containing needle; path alone if not found."""
    ls = lines_of(rel_path)
    if ls:
        for i in range(start - 1, len(ls)):
            if needle in ls[i]:
                return f"{rel_path}:{i + 1}"
    return rel_path


def md_rows(rel_path):
    """Yield (lineno, header_cells, cells, heading) for every markdown table body row."""
    ls = lines_of(rel_path) or []
    header, heading = None, None
    for i, l in enumerate(ls):
        if l.startswith("#"):
            heading = l.lstrip("#").strip()
        if not l.startswith("|"):
            header = None if not l.strip() else header
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if i + 1 < len(ls) and re.match(r"^\|\s*:?-{3,}", ls[i + 1]):
            header = [c.lower() for c in cells]
            continue
        if re.match(r"^\|\s*:?-{3,}", l) or header is None:
            continue
        yield i + 1, header, cells, heading


def col(header, cells, *names):
    for n in names:
        for j, h in enumerate(header):
            if h.startswith(n) and j < len(cells):
                return cells[j]
    return None


URL_RE = re.compile(r"https?://[^\s`)>\]|,;]+")


def first_url(*texts):
    for t in texts:
        if t:
            m = URL_RE.search(t)
            if m:
                return m.group(0).rstrip(".")
    return None


def to_int(s):
    if s is None:
        return None
    m = re.search(r"\d[\d,]*", s.replace("*", ""))
    return int(m.group(0).replace(",", "")) if m else None


def clean(s):
    return s.replace("`", "").replace("**", "").strip() if s else s


PERIOD_RE = re.compile(r"(c\.\s*\d{3,4}(?:-\d{2,4})?|\d{1,2}(?:th|st|nd|rd)(?:-\d{1,2}th)? c\.|\b1[0-9]{3}(?:[-–]\d{2,4})?\b)")


def period_of(*texts):
    for t in texts:
        if t:
            m = PERIOD_RE.search(t)
            if m:
                return m.group(0)
    return None


# ----------------------------------------------------------------------------------------------- corpora
CORPORA = {}  # corpus_id -> row dict


def add_corpus(cid, src, **kw):
    """First documented source wins for each field; later sources only fill gaps."""
    row = CORPORA.get(cid)
    if row is None:
        row = dict(corpus_id=cid, name=None, kind=None, language=None, genre=None, period=None, tokens=None,
                   path=None, licence=None, url=None, used_in=set(), note=None, src=src)
        CORPORA[cid] = row
    else:
        if src not in row["src"]:
            row["src"] += "; " + src
    for k, v in kw.items():
        if k == "used_in":
            row["used_in"].update(v if isinstance(v, (list, set, tuple)) else [v])
        elif v not in (None, "") and row.get(k) in (None, ""):
            row[k] = v
        elif k == "note" and v and v not in (row["note"] or ""):
            row["note"] = (row["note"] + " | " + v) if row["note"] else v
    return row


def corpora_manifest():
    f = "data/CONTROLS_MANIFEST.md"
    kinds = {"A.": ("natural", "natural-language control", "data/controls/"),
             "B.": ("constructed", "constructed / asemic text", "data/controls/"),
             "C.": ("synthetic", "synthetic nomenclator (ctl_nomenclator.py)", "data/controls_synthetic/"),
             "D.": ("synthetic", "generator output (ctl_generators.py / ctl_naibbe.py)", "data/controls_synthetic/")}
    for ln, h, c, heading in md_rows(f):
        sec = (heading or "")[:2]
        if sec not in kinds or not c:
            continue
        fn = clean(c[0])
        kind, genre, base = kinds[sec]
        if fn.startswith("plaintext"):
            cid, path = "nomen_plaintext_macer_pliny", None
        elif fn.startswith("Voynich"):
            continue
        else:
            m = re.match(r"([\w/.-]+)\.txt", fn)
            if not m:
                continue
            cid = os.path.basename(m.group(1))
            path = fn if "/" in fn else base + fn
            if "/" in fn and not fn.startswith("data/"):
                path = "data/" + fn
        src_cell = col(h, c, "source", "script")
        lang = col(h, c, "language")
        add_corpus(cid, f"{f}:{ln}", name=clean(col(h, c, "content", "scheme", "notes") or lang or fn),
                   kind=kind, language=clean(lang), genre=genre, period=period_of(lang),
                   tokens=to_int(col(h, c, "tokens")), path=path, licence=clean(col(h, c, "license")),
                   url=first_url(src_cell), note=clean(col(h, c, "caveats", "notes")))


GENRE_MAP = {  # file in data/external/genre-s8x -> corpus_id
    "pg8102_forme_of_cury.txt": "forme_of_cury", "pg49513_culpeper_complete_herbal.txt": "culpeper_complete_herbal",
    "pg782_mandeville_travels.txt": "mandeville_travels", "twofifteenthcent00austuoft_djvu.txt": "two_15c_cookery_books",
    "alphitaamedicob00mowagoog_djvu.txt": "alphita_mowat1887",
    "BIUSante_pharma_res012103_djvu.txt": "dispensarium_nicolai_1582", "pg7000_kalevala.txt": "kalevala",
    "horaeeboracenses00surtuoft_djvu.txt": "horae_eboracenses", "4617_djvu.txt": "atharva_veda_griffith",
    "carminagadelicah01carm_0_djvu.txt": "carmina_gadelica", "sinonomabartholo01mirfuoft_djvu.txt": "sinonoma_bartholomei",
    "promptoriumparvu00galfuoft_djvu.txt": "promptorium_parvulorum"}


def corpora_genre():
    for run, d in (("s87", "data/external/genre-s87"), ("s89", "data/external/genre-s89")):
        f = d + "/MANIFEST.md"
        for ln, h, c, _ in md_rows(f):
            fn = clean(c[0])
            cid = GENRE_MAP.get(fn)
            if not cid:
                continue
            gl = col(h, c, "genre")
            genre, inner = (gl.split("(", 1) + [""])[:2] if gl else (None, "")
            inner = inner.rstrip(")")
            lang = re.split(r"[,;]", inner)[0].strip() if inner else None
            add_corpus(cid, f"{f}:{ln}", name=fn, kind="natural", genre=genre.strip() if genre else None,
                       language=lang, period=period_of(inner), path=f"{d}/{fn}", licence=clean(col(h, c, "licence")),
                       url=first_url(col(h, c, "source")), used_in=[run], note=clean(gl))


def corpora_original_controls():
    """corpora.CONTROLS: the six original Gutenberg controls (title and eBook number from each file's header)."""
    langs = {"latin": "Latin", "italian": "Italian", "german": "German", "english": "English"}
    src0 = find_line("corpora.py", "CONTROLS = [")
    for cid in ("latin_caesar", "latin_augustine", "italian_dante", "german_faust", "german_kafka", "english_alice"):
        f = f"data/controls/{cid}.txt"
        ls = lines_of(f) or []
        title = next((l.split(":", 1)[1].strip() for l in ls[:40] if l.startswith("Title:")), None)
        eb = next((re.search(r"eBook #(\d+)", l).group(1) for l in ls[:40] if re.search(r"eBook #(\d+)", l)), None)
        add_corpus(cid, src0 + "; " + find_line(f, "eBook #"), name=title, kind="natural",
                   language=langs[cid.split("_")[0]] + " (from file name)",
                   path=f, url=f"https://www.gutenberg.org/ebooks/{eb}" if eb else None,
                   licence="Project Gutenberg (licence text in file header)" if eb else None,
                   note="original corpora.CONTROLS set; token count not documented")


def corpora_realline():
    f = "data/controls_realline/CREMMA_MANIFEST.md"
    lic = "CC-BY 4.0 per htr-united.yml; data paper says CC0 (conflict unresolved, data/external/README.md cremma section)"
    lic_src = find_line("data/external/README.md", "htr-united.yml` states")
    for ln, h, c, _ in md_rows(f):
        if h[0] == "id":
            ms = clean(c[0])
            add_corpus(f"cremma_{ms}", f"{f}:{ln}; {lic_src}", name=f"CREMMA {ms}: {c[3]}", kind="natural",
                       language="Latin (medieval manuscript, diplomatic HTR ground truth)",
                       genre=clean(c[4]) + "; " + clean(c[3]), period=clean(c[1]), tokens=to_int(c[9]),
                       path=f"data/controls_realline/cremma_{ms}.meta.json (base) / _marks.meta.json",
                       licence=lic, url="https://github.com/HTR-United/CREMMA-Medieval-LAT",
                       note=f"script {clean(c[2])}; lines {clean(c[8])}")
        elif h[0] == "file":
            nm = clean(c[0])
            add_corpus(nm, f"{f}:{ln}", name=f"CREMMA pool {nm}: {clean(c[1])}", kind="natural",
                       language="Latin (medieval manuscripts)", tokens=to_int(c[4]),
                       path=f"data/controls_realline/{nm}.meta.json", licence=lic,
                       url="https://github.com/HTR-United/CREMMA-Medieval-LAT")
    f2 = "data/controls_realline/README.md"
    add_corpus("gib_realline_pooled", find_line(f2, "| gib_realline_pooled |"),
               name="Gaskell & Bowern 38 gibberish writers, volunteers' own lines", kind="gibberish",
               language="none (meaningless human text)", tokens=10023,
               path="data/controls_realline/gib_realline_pooled.meta.json",
               licence="modified MIT (code + gibberish data)", url="https://github.com/danielgaskell/voynich")
    s97 = "s97_language_rescue_controls.py"
    add_corpus("cremma_prose", find_line(s97, "Comparators (descriptive"), name="CREMMA prose manuscripts, plain (base) family, real lines (s87's 12 prose MSS)",
               kind="natural", language="Latin (medieval manuscripts)", url="https://github.com/HTR-United/CREMMA-Medieval-LAT",
               licence=lic, used_in=["s87", "s97"])
    add_corpus("cremma_prose_marks", find_line(s97, "C1_cremma_marks_la"), name="CREMMA prose manuscripts, abbreviations kept (marks family), real lines",
               kind="natural", language="Latin (medieval manuscripts, abbreviated)", path="data/controls_realline/cremma_all_marks.meta.json (prose subset)",
               url="https://github.com/HTR-United/CREMMA-Medieval-LAT", licence=lic, used_in=["s97"])


def corpora_gibberish():
    lic_src = find_line("data/external/README.md", "danielgaskell-voynich-main.zip")
    for fp in sorted(glob.glob(P("data/controls_gibberish/gib_*.meta.json"))):
        nm = os.path.basename(fp).replace(".meta.json", "")
        add_corpus(nm, f"data/controls_gibberish/{os.path.basename(fp)}; {lic_src}",
                   name=f"Gaskell & Bowern volunteer gibberish {nm[4:]}", kind="gibberish",
                   language="none (meaningless human text)", genre="volunteer gibberish (2022 study)",
                   path=f"data/controls_gibberish/{os.path.basename(fp)}",
                   licence="modified MIT (code + gibberish data)", url="https://github.com/danielgaskell/voynich")


def corpora_synthetic_dir():
    for fp in sorted(glob.glob(P("data/controls_synthetic/*.meta.json"))):
        nm = os.path.basename(fp).replace(".meta.json", "")
        add_corpus(nm, f"data/controls_synthetic/{os.path.basename(fp)}", kind="synthetic",
                   genre="synthetic control (sidecar in data/controls_synthetic)",
                   path=f"data/controls_synthetic/{os.path.basename(fp)}")


def corpora_period():
    f = "data/controls_period/README.md"
    ids = {"librodicucinade00fratgoog": "frati_libro_cucina_1899", "b21525213": "zambrini_libro_cucina_1863",
           "bub_gb_I0QSAAAAYAAJ": "pfeiffer_arzneibuecher_1863", "Buoch_von_guoter_Spise": "buoch_von_guoter_spise",
           "b24880681": "megenberg_buch_der_natur_1861"}
    for ln, h, c, heading in md_rows(f):
        fcell = col(h, c, "file") or ""
        cid = next((v for k, v in ids.items() if k in fcell), None)
        if not cid:
            continue
        ld = col(h, c, "language")
        add_corpus(cid, f"{f}:{ln}", name=clean(col(h, c, "edition")), kind="natural", language=clean(ld),
                   genre="period recipe / remedy text", period=period_of(ld), path="data/controls_period/" + clean(fcell).split(" ")[0],
                   licence=clean(col(h, c, "licence")), url=first_url(col(h, c, "source")), used_in=["s102", "s104"],
                   note=f"s102 part {clean(c[0])}; body lines {clean(col(h, c, 'body'))}")
    s102 = "s102_period_ciphers_recipes.py"
    for cid, lab, lang in (("period_p1_la", "P1_la  Latin medical", "Latin"),
                           ("period_p2_it", "P2_it  northern-Italian", "Italian (Venetian + Tuscan)"),
                           ("period_p3_de", "P3_de  southern German", "German (Alemannic / Bavarian / East Franconian)")):
        add_corpus(cid, find_line(s102, lab) + "; " + f, name=f"s102 plaintext {cid[-5:].upper()} (composite, 22,500 tokens)",
                   kind="natural", language=lang, genre="period recipe / remedy plaintext (composite)",
                   tokens=22500, used_in=["s102", "s104"],
                   note="composite of the parts listed in data/controls_period/README.md; reduced to the 25-symbol plaintext alphabet")


def corpora_tabular():
    f = "data/controls_tabular/README.md"
    ids = {"raw_tacuinum_medimanus": "tacuinum_bnf_lat9333", "raw_degradibus/BIUSante": "degradibus_constantinus_1536",
           "raw_lull_1515": "lull_tabula_generalis_1515"}
    for ln, h, c, heading in md_rows(f):
        if not heading or not heading.startswith("Used"):
            continue
        cid = next((v for k, v in ids.items() if k in c[0]), None)
        if cid:
            add_corpus(cid, f"{f}:{ln}", name=clean(c[1])[:200], kind="natural", language="Latin",
                       genre="tabular medical / combinatory text", period=period_of(c[3]),
                       path="data/controls_tabular/" + clean(c[0]), licence=clean(c[4])[:300], url=first_url(c[2]),
                       used_in=["s107"], note=clean(c[3]))
    f = "data/controls_tabular_ruled/README.md"
    s108 = "s108_ruled_medical_tables.py"
    for cid, needle, lab, url_needle in (
            ("alkindi_degradibus_1531", "BIUSante_00188x01_djvu.xml |", "T1_alkindi_1531", "BIUSante_00188x01_djvu.xml"),
            ("tacuinum_sanitatis_1531", "BIUSante_00188x01_djvu.xml |", "T2_tacuinum_1531", "BIUSante_00188x01_djvu.xml"),
            ("ibnjazlah_tacuini_aegritudinum_1532", "b14562455_0002_djvu.xml |", "T3_ibnjazlah_1532", "b14562455_0002_djvu.xml")):
        src = find_line(f, needle)
        ln = int(src.rsplit(":", 1)[1]) if ":" in src else None
        row = (lines_of(f) or [""])[ln - 1] if ln else ""
        cells = [x.strip() for x in row.strip().strip("|").split("|")] if row else []
        add_corpus(cid, src + "; " + find_line(s108, lab), name=lab + ": " + (clean(cells[1])[:160] if len(cells) > 1 else ""),
                   kind="natural", language="Latin", genre="ruled period medical table (page images + OCR word boxes)",
                   period=period_of(cells[1] if len(cells) > 1 else None), path="data/controls_tabular_ruled/" + (clean(cells[0]) if cells else ""),
                   licence=clean(cells[3]) if len(cells) > 3 else None, url=first_url(cells[2] if len(cells) > 2 else None),
                   used_in=["s108"], note="s108 legibility gate: no text admitted (NOT ASSESSABLE)")


def corpora_herbals():
    f = "data/herbals_period/README.md"
    for ln, h, c, heading in md_rows(f):
        if h[0] == "ms" and len(h) == 5:
            ms = clean(c[0])
            add_corpus(f"herbal_{ms}", f"{f}:{ln}", name=clean(c[1])[:200], kind="image-corpus",
                       genre="period illustrated herbal (page images; captions agent-transcribed, unverified)",
                       period=period_of(c[1]), tokens=None, path=f"data/herbals_period/{ms}/", licence=clean(c[3])[:200],
                       url=first_url(c[1]), used_in=["s103"], note=f"page images: {clean(c[4])}")
    f = "data/herbals_alchemical/README.md"
    for ln, h, c, heading in md_rows(f):
        if h[0] == "folder":
            ms = clean(c[0])
            add_corpus(f"herbal_{ms}", f"{f}:{ln}", name=ms, kind="image-corpus",
                       genre="alchemical-herbal family candidate (page images)", path=f"data/herbals_alchemical/{ms}/",
                       licence=clean(c[3]), used_in=["s105"],
                       note=f"obtained: {clean(c[1])}; images {clean(c[2])}; identities: {clean(c[5])}")


def corpora_voynich():
    f = "data/external/README.md"
    ids = {"GC2a-n.txt": "GC2a", "FG2a-n.txt": "FG2a", "CD2a-n.txt": "CD2a", "IT2a-n.txt": "IT2a", "VT0e-n.txt": "VT0e",
           "LSI_ivtff_0d.txt": "LSI", "RF1b-e.txt": "RF1b", "RF1b-er.txt": "RF1b-er"}
    for ln, h, c, heading in md_rows(f):
        fn = clean(c[0])
        if fn in ids:
            add_corpus(f"voynich-{ids[fn]}", f"{f}:{ln}", name=f"Voynich transliteration {clean(c[1])} ({clean(c[2])})",
                       kind="voynich", language="Voynichese", genre=f"transliteration, alphabet {clean(c[3])}",
                       period="1404-1438 (C14, vellum)", tokens=to_int(c[6]), path=f"data/external/voynich-nu-ivtff/{fn}",
                       licence="voynich.nu: no formal licence; citation requested (research use)",
                       url="https://www.voynich.nu/data/", note=f"coverage {clean(c[8])}")
    add_corpus("voynich-ZL3b", find_line(f, "Our own data/ZL3b-n.txt gives"), name="Voynich ZL3b (Zandbergen-Landini, EVA, IVTFF 2.0)",
               kind="voynich", language="Voynichese", genre="transliteration, alphabet EVA", period="1404-1438 (C14, vellum)",
               tokens=38255, path="data/ZL3b-n.txt", licence="voynich.nu: no formal licence; citation requested (research use)",
               url="https://www.voynich.nu/data/ZL3b-n.txt", note="tokens by tools/ivtff_tokens.py; frozen project reference")


def corpora_roach():
    f = "runs/roach-r7/README.md"
    r7 = {"Latin (negative control)": ("caesar_bg_v_viii", "Latin", "prose (negative control)"),
          "Recipe reference": ("forme_of_cury", "Middle English", "recipe collection"),
          "Repetition reference": ("bcp_litany_psalter", "English", "litany and psalter (Book of Common Prayer)"),
          "Prose reference": ("manzoni_promessi_sposi", "Italian", "novel prose")}
    for ln, h, c, _ in md_rows(f):
        k = clean(c[0])
        if k in r7:
            cid, lang, genre = r7[k]
            add_corpus(cid, f"{f}:{ln}", name=clean(c[1])[:200], kind="natural", language=lang, genre=genre,
                       tokens=to_int(re.search(r"([\d,]{5,}) words", c[1]).group(1)) if re.search(r"([\d,]{5,}) words", c[1]) else None,
                       url=first_url(c[2]), licence="Project Gutenberg" if "gutenberg" in c[2] else None,
                       used_in=["r7", "r11", "r12"] if cid == "caesar_bg_v_viii" else ["r7"])
    f = "runs/roach-r11/README.md"
    r11 = {"Apicius": ("apicius_de_re_coquinaria", "Latin"), "Digby": ("digby_closet_opened_1669", "English"),
           "Roget": ("roget_thesaurus", "English"), "Culpeper": ("culpeper_complete_herbal", "English"),
           "Kalevala": ("kalevala", "Finnish"), "English and Scottish": ("child_ballads_vol1", "English / Scots"),
           "Complete Manual of Catholic": ("catholic_piety_manual", "English"), "Prayers of the Middle Ages": ("prayers_middle_ages", "English"),
           "CREMMA Medii Aevi, raw ALTO": ("cremma_raw_alto_r11", "Latin (abbreviations kept)"),
           "WLC Genesis": ("hebrew_wlc_genesis_exodus", "Hebrew (unvowelled)"), "Dante, Commedia": ("italian_dante", "Italian")}
    for ln, h, c, _ in md_rows(f):
        cid = next((v for k, v in r11.items() if c[0].startswith(k)), None)
        if not cid or h[0] != "text":
            continue
        add_corpus(cid[0], f"{f}:{ln}", name=clean(c[0]), kind="natural", language=cid[1], genre=clean(c[1]),
                   tokens=None if cid[0] in CORPORA else to_int(c[2]), url=first_url(c[3]),
                   licence="Project Gutenberg" if "gutenberg" in c[3] else None, used_in=["r11", "r12"],
                   note=f"r11 words used: {clean(c[2])}")
    f12 = "runs/roach-r12/README.md"
    for cid in ("caesar_bg_v_viii",):
        add_corpus(cid, find_line(f12, "| Texts |"), used_in=["r12"])
    for cid, name, kind, src in (
            ("roach_planted", "roach planted positive control (Voynich layout, planted core reuse)", "synthetic", "runs/roach-r7/README.md"),
            ("roach_word_markov", "roach word-Markov negative control", "synthetic", "runs/roach-r7/README.md"),
            ("roach_planted_ar", "roach planted AR(0.3) word-length positive control", "synthetic", f12),
            ("roach_shuffled_voynich", "roach within-line-shuffled Voynich negative control", "synthetic", f12)):
        needle = {"roach_planted": "Planted (positive)", "roach_word_markov": "Word-Markov (negative)",
                  "roach_planted_ar": "Planted AR(0.3)", "roach_shuffled_voynich": "within-line-shuffled copy"}[cid]
        add_corpus(cid, find_line(src, needle),
                   name=name, kind=kind, genre="roach control")


def corpora_scripts():
    """Corpora defined in the s97 / s102 / s104 / s107 / s108 script headers (derived and constructed texts)."""
    s97 = "s97_language_rescue_controls.py"
    rows = [
        ("hebrew_torah", s97, "C2a_hebrew_abjad", {}, ["s97"]),
        ("arabic_quran", s97, "C2b_arabic_abjad", {}, ["s97"]),
        ("verbose_la_cremma", s97, "C3a_verbose_la", dict(name="verbose syllabic re-spelling of CREMMA prose, line-held variants", kind="encoded", language="Latin (encoded)", genre="constructed encoding of a natural text"), ["s97"]),
        ("verbose_it_dante", s97, "C3b_verbose_it", dict(name="verbose syllabic re-spelling of Dante, line-held variants", kind="encoded", language="Italian (encoded)", genre="constructed encoding of a natural text"), ["s97"]),
        ("sigla_dispensarium", s97, "C4_sigla_disp_la", dict(name="Dispensarium antidotary with pharmacy sigla (constructed)", kind="encoded", language="Latin (sigla)", genre="constructed shorthand of a natural text"), ["s97"]),
        ("latin_augustine", s97, "NC  plain Latin prose", {}, ["s97", "s102", "s104", "s107", "s108"]),
        ("lp91_planted", s97, "PC1 planted producer", dict(name="s91 LP91 planted producer at S91.PLANTED (3 seeds)", kind="synthetic", genre="planted positive control"), ["s97", "s102", "s104", "s107", "s108"]),
        ("tacuinum_bnf_lat9333", "s107_tabular_medical_reference.py", "T1_tacuinum", {}, ["s107"]),
        ("degradibus_constantinus_1536", "s107_tabular_medical_reference.py", "T2_degradibus", {}, ["s107"]),
        ("lull_tabula_generalis_1515", "s107_tabular_medical_reference.py", "T3_lull_tabula_1515", {}, ["s107"]),
    ]
    for cid, f, needle, kw, runs in rows:
        add_corpus(cid, find_line(f, needle), used_in=runs, **kw)
    s102 = "s102_period_ciphers_recipes.py"
    enc = {"E1": "monoalphabetic + nulls", "E2": "homophonic + nulls (Milanese chancery style)", "E3": "nomenclator (200 code groups)",
           "E4": "line-held nomenclator (3 variants)"}
    for p, lang in (("P1_la", "Latin"), ("P2_it", "Italian"), ("P3_de", "German")):
        for e, d in enc.items():
            add_corpus(f"{p}_{e}".lower(), find_line(s102, f" {e} ") , name=f"s102 {p} enciphered {e}: {d}", kind="encoded",
                       language=f"{lang} (enciphered)", genre="period cipher over period recipe plaintext", tokens=22500, used_in=["s102"])
    s104 = "s104_g1_encoding_grid.py"
    g = {"G1a": "verbose syllabary", "G1b": "line-table nomenclator", "G1c": "abbreviate-then-G1b"}
    for p, lang in (("P1_la", "Latin"), ("P2_it", "Italian"), ("P3_de", "German")):
        for e, d in g.items():
            for shuf in ("", "_shuf"):
                add_corpus(f"{p}_{e}{shuf}".lower(), find_line(s104, f"{e} ") if e != "G1a" else find_line(s104, "G1a"),
                           name=f"s104 {p} {e} {d}" + (" (shuffled-plaintext twin)" if shuf else ""), kind="encoded",
                           language=f"{lang} (encoded)", genre="table-driven verbose encoding of period recipe plaintext",
                           tokens=22500, used_in=["s104"])


# label in a results file -> corpus_id (natural texts that recur across runs); everything else defaults to label.lower()
ALIAS = {
    "VOY_ZL3b": "voynich-ZL3b", "VOY_RF1b": "voynich-RF1b", "VOY_IT2a": "voynich-IT2a", "PC2_VOY_IT2a_as_control": "voynich-IT2a",
    "VOYNICH_ZL": "voynich-ZL3b", "VOYNICH_IT": "voynich-IT2a", "Voynich ZL3b": "voynich-ZL3b",
    "L_alphita_la": "alphita_mowat1887", "T_alphita_la": "alphita_mowat1887", "L_dispensarium_la": "dispensarium_nicolai_1582",
    "L_cookery15_enm": "two_15c_cookery_books", "L_culpeper_en": "culpeper_complete_herbal", "CULPEPER_HERBAL": "culpeper_complete_herbal",
    "L_cury_enm": "forme_of_cury", "REF_FORME_OF_CURY": "forme_of_cury",
    "P_cremma_prose_la": "cremma_prose", "REF_cremma_prose_base": "cremma_prose", "C1_cremma_marks_la": "cremma_prose_marks",
    "CREMMA Latin (real lines)": "cremma_all", "P_caesar_la": "latin_caesar", "P_augustine_la": "latin_augustine",
    "NC_augustine_la": "latin_augustine", "P_pliny_herbal_la": "latin_pliny_herbal", "P_mandeville_en": "mandeville_travels",
    "P_alice_en": "english_alice", "V_dante_it": "italian_dante", "DANTE_VERSE": "italian_dante", "Dante Italian": "italian_dante",
    "V_nibelungenlied_gmh": "mhg_nibelungenlied", "V_croisade_oc": "occitan_croisade_albigeoise", "V_roland_fro": "oldfrench_roland",
    "R_kalevala_fi": "kalevala", "KALEVALA_VERSE": "kalevala", "R_horae_ebor_la": "horae_eboracenses",
    "R_atharva_en": "atharva_veda_griffith", "R_carmina_gd_en": "carmina_gadelica",
    "R_steganographia_la": "trithemius_steganographia_1608", "C_steganographia_la": "trithemius_steganographia_1608",
    "C_steg_heidel_la": "trithemius_polygraphia", "R_enochian": "enochian_keys_dee", "C_enochian_keys": "enochian_keys_dee",
    "C_enochian_clauses": "enochian_keys_dee", "C_ignota": "ignota_hildegard_glossary", "C_lull_rows5": "lull_ars_brevis_table",
    "R_egerton821_la": "cremma_Egerton821", "R_hours_sbb_la": "cremma_SBB_PK_Hdschr25",
    "T_promptorium_enm_la": "promptorium_parvulorum", "T_sinonoma_la_en": "sinonoma_bartholomei",
    "C2a_hebrew_abjad": "hebrew_torah", "C2b_arabic_abjad": "arabic_quran", "C3a_verbose_la": "verbose_la_cremma",
    "C3b_verbose_it": "verbose_it_dante", "C4_sigla_disp_la": "sigla_dispensarium",
    "CTRL_NEG_CAESAR": "caesar_bg_v_viii", "CAESAR_LATIN": "caesar_bg_v_viii", "LATIN": "caesar_bg_v_viii",
    "REF_BCP_LITANY": "bcp_litany_psalter", "REF_MANZONI": "manzoni_promessi_sposi", "APICIUS_LATIN_RECIPES": "apicius_de_re_coquinaria",
    "DIGBY_RECIPES": "digby_closet_opened_1669", "ROGET_SYNONYMS": "roget_thesaurus", "BALLADS_REFRAINS": "child_ballads_vol1",
    "CATHOLIC_LITANIES": "catholic_piety_manual", "MEDIEVAL_PRAYERS": "prayers_middle_ages", "CREMMA_ABBREV_LATIN": "cremma_raw_alto_r11",
    "HEBREW_UNVOWELLED": "hebrew_wlc_genesis_exodus", "PLANTED": "roach_planted", "CTRL_POS_PLANTED": "roach_planted",
    "WORD_MARKOV": "roach_word_markov", "CTRL_POS_PLANTED_AR": "roach_planted_ar", "CTRL_NEG_SHUFFLED": "roach_shuffled_voynich",
    "T1_tacuinum_bnf9333": "tacuinum_bnf_lat9333", "T2_degradibus_const": "degradibus_constantinus_1536",
    "T3_lull_tabula_1515": "lull_tabula_generalis_1515", "REF_P1_la_plain": "period_p1_la", "REF_P2_it_plain": "period_p2_it",
    "REF_P3_de_plain": "period_p3_de", "PC1_LP91_planted_s1": "lp91_planted", "PC1_LP91_planted_s2": "lp91_planted",
    "PC1_LP91_planted_s3": "lp91_planted",
}


def corpus_id(label):
    if label in ALIAS:
        return ALIAS[label]
    if label.startswith("N_cremma_"):
        return "cremma_" + label[len("N_cremma_"):]
    if label.startswith("H_gib_"):
        return label.lower() if label == "H_gib_pool" else "gib_" + label[len("H_gib_"):]
    return label.lower()


# ----------------------------------------------------------------------------------------------- corpus_stats
STATS = []
KIND_HINT = {}  # corpus_id -> (label, description, tokens, src) from results corpus lists (fallback for corpora rows)

LEAD_FILES = [("s87", "results_s87.txt"), ("s87-amend1", "results_s87_amend1.txt"), ("s89", "results_s89.txt"),
              ("s89-amend1", "results_s89_amend1.txt"), ("s90", "results_s90.txt"), ("s97", "results_s97.txt"),
              ("s102", "results_s102.txt"), ("s104", "results_s104.txt"), ("s107", "results_s107.txt"),
              ("s108", "results_s108.txt")]
LEAD_NOTE = {"s87": "s87 original: order arm measured on ~1,129 held-out tokens (page-id defect, POST-RUN AUDIT NOTE); "
                    "use s87-amend1 for order values"}

NUM = r"([+-]?(?:\d+\.\d+|\d+|nan))"


def fnum(s):
    try:
        v = float(s)
        return None if v != v else v
    except (TypeError, ValueError):
        return None


def stat(cid, statistic, value, run, src, **kw):
    if value is None:
        return
    r = dict(corpus_id=cid, statistic=statistic, value=value, run_id=run, claim_id=None, p=None, ci_lo=None, ci_hi=None,
             n_tokens=None, segmenter=None, pipeline=None, label=None, scope=None, note=None, src=src)
    r.update(kw)
    STATS.append(r)


def seg_of(label, run):
    if "/" in label:
        s = label.split("/", 1)[1]
        return {"stem": "slot", "slot": "slot", "identity": "word", "affix2": "affix2"}.get(s, s)
    base = label
    if base.startswith(("VOY_", "PC2_")):
        return "slot"
    if base.startswith("G_"):
        return "generated-core"
    return "word"


def parse_lead():
    prof = re.compile(r"^\s{2}(?P<label>\S+)\s+tok\s+(?P<tok>\d+)\s+ty\s+(?P<ty>\d+)(?P<rest>.*)$")
    rhy = re.compile(r"^\s{2}(?P<label>\S+)\s+I " + NUM + r" null median " + NUM + r"(?: q99 \S+)? excess " + NUM +
                     r" p ([\d.]+) -> \w+ \| h2 ([\d.]+)")
    clist = re.compile(r"^\s{2}(?P<label>\S+)\s+(?:[A-Z]+\s+)?(?:gating|descriptive|UNMATCHED|gate|control|tabular|target)\s+tokens\s+(\d+)\s+(.*)$")
    for run, f in LEAD_FILES:
        ls = lines_of(f)
        if ls is None:
            continue
        seen = set()
        for i, l in enumerate(ls, 1):
            src = f"{f}:{i}"
            m = clist.match(l)
            if m:
                cid = corpus_id(m.group("label"))
                desc = re.sub(r"\s+", " ", m.group(3)).strip()
                desc = re.sub(r"^(?:pages\s+\d+\s+held-out\s+\S+|lines\s+\d+\s+mean line\s+[\d.]+|pages\s+\d+\s+lines\s+\d+(?:\s+mean line\s+[\d.]+)?)\s*", "", desc)
                KIND_HINT.setdefault(cid, (m.group("label"), desc, int(m.group(2)), src, run))
            m = prof.match(l)
            if m and ("| order" in l or "| o100" in l):
                label = m.group("label")
                if label.startswith("PWR_"):
                    continue  # power rows: subsampled cuts, not texts
                base = label.split("/")[0]
                cid, seg, rest = corpus_id(base), seg_of(label, run), m.group("rest")
                n = int(m.group("tok"))
                note = []
                if "UNMATCHED" in rest:
                    note.append("UNMATCHED size (" + re.search(r"\[([^\]]*)\]", rest).group(1) + ")" if re.search(r"\[([^\]]*)\]", rest) else "UNMATCHED")
                if base == "PC2_VOY_IT2a_as_control":
                    note.append("IT2a through the control path (gate row)")
                if run in LEAD_NOTE:
                    note.append(LEAD_NOTE[run])
                common = dict(n_tokens=n, segmenter=seg, pipeline="lead-S87.c1", label=label,
                              scope="22,500-token cut (or full text if smaller), real or ZL3b-length lines",
                              note="; ".join(note) or None)

                def put(statistic, value, **kw):
                    key = (cid, statistic, seg, base == "PC2_VOY_IT2a_as_control")
                    if key in seen or value is None:
                        return
                    seen.add(key)
                    stat(cid, statistic, value, run, src, **{**common, **kw})

                mo = re.search(r"(?:K100|o100) " + NUM + r"(?:\(p([\d.]+)\))?", rest)
                if mo:
                    put("core_order_K100", fnum(mo.group(1)), p=fnum(mo.group(2)))
                mo = re.search(r"(?:K200|o200) " + NUM + r"(?:\(p([\d.]+)\))?", rest)
                if mo:
                    put("core_order_K200", fnum(mo.group(1)), p=fnum(mo.group(2)))
                mo = re.search(r"Rw1 " + NUM + r"\(p([\d.]+)\)", rest)
                if mo:
                    put("Rw1", fnum(mo.group(1)), p=fnum(mo.group(2)))
                mo = re.search(r"Rc1 " + NUM, rest)
                if mo:
                    put("Rc1", fnum(mo.group(1)))
                mo = re.search(r"loc " + NUM + r"\[" + NUM + "," + NUM + r"\]", rest)
                if mo:
                    put("quire_locality", fnum(mo.group(1)), ci_lo=fnum(mo.group(2)), ci_hi=fnum(mo.group(3)))
                mo = re.search(r"rhythm (?:I \S+ null med \S+ )?exc " + NUM + r" p ([\d.]+)", rest)
                if mo:
                    put("rhythm_excess", fnum(mo.group(1)), p=fnum(mo.group(2)), segmenter="word-length",
                        scope="within-line lag-1 word-length Moran I minus within-line-shuffle median (999 shuffles)")
                mo = re.search(r"\| h2 ([\d.]+)", rest)
                if mo:
                    put("h2", fnum(mo.group(1)), segmenter="char", scope="character conditional entropy at the 22,500-token cut")
                continue
            m = rhy.match(l)
            if m:
                label = m.group("label")
                cid = corpus_id(label)
                for statistic, value, kw in (
                        ("rhythm_excess", fnum(m.group(4)), dict(p=fnum(m.group(5)), segmenter="word-length",
                                                                  scope="within-line lag-1 word-length Moran I minus within-line-shuffle median (999 shuffles)",
                                                                  note=f"I {m.group(2)}, null median {m.group(3)}")),
                        ("h2", fnum(m.group(6)), dict(segmenter="char", scope="character conditional entropy at the 22,500-token cut"))):
                    key = (cid, statistic, kw["segmenter"], label == "PC2_VOY_IT2a_as_control")
                    if key in seen:
                        continue
                    seen.add(key)
                    nt = ["IT2a through the control path (gate row)"] if label.startswith("PC2_") else []
                    if kw.get("note"):
                        nt.append(kw.pop("note"))
                    stat(cid, statistic, value, run, src, n_tokens=22500, pipeline="lead-S87.c1", label=label,
                         note="; ".join(nt) or None, **kw)


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


SEGNAME = {"S0": "word", "S1": "roach-S1 (r3 affix lists / frequency affixes)", "S2": "roach-S2 (MDL affix inducer)"}


def parse_r7():
    f = "runs/roach-r7/results_r7.txt"
    ls = lines_of(f) or []
    head = re.compile(r"^\s{2}(\w+) (S\d): (\d+) folds")
    row = re.compile(r"^\s{3}(\w+)\s+\| " + NUM + r" ([\d.]+) (?:True|False)\s*\| " + NUM + r" ([\d.]+) (?:True|False)\s*\| " + NUM +
                     r" \(" + NUM + "/" + NUM + r"\) ([\d.]+) (?:True|False)\s*\| " + NUM + r" \[")
    cur, start, acc = None, None, []
    for i, l in enumerate(ls, 1):
        m = head.match(l)
        if m:
            cur, start, acc = (m.group(1), m.group(2)), i, []
            continue
        m = row.match(l)
        if m and cur:
            acc.append([fnum(m.group(k)) for k in (2, 4, 7, 8, 10)])
            continue
        m = re.search(r"folds passing:.*ALL FOUR (\d+) of (\d+)", l)
        if m and cur:
            label, s = cur
            cid, src = corpus_id(label), f"{f}:{start}-{i}"
            n = len(acc)
            kw = dict(segmenter=SEGNAME[s], pipeline="roach-r7", label=f"{label} {s}",
                      scope=f"median over {n} LOQO quire folds (computed by world.py from the fold rows)",
                      note="roach block estimator; not the lead whole-cut value")
            stat(cid, "core_order_K100", med([a[0] for a in acc]), "r7", src, **{**kw, "note": kw["note"] + "; Miller-Madow MI excess at K=100"})
            stat(cid, "Rw1", med([a[1] for a in acc]), "r7", src, **kw)
            stat(cid, "Rc1", med([a[3] for a in acc]), "r7", src, **{**kw, "note": kw["note"] + "; Rx' (within-page shuffle term of (c))"})
            stat(cid, "quire_locality", med([a[4] for a in acc]), "r7", src, **kw)
            stat(cid, "loqo_folds", int(m.group(1)), "r7", f"{f}:{i}", **{**kw, "scope": f"folds passing all four of {m.group(2)}",
                                                                          "note": "threshold 8"})
            cur = None


def parse_r11():
    f = "runs/roach-r11/results_r11.txt"
    ls = lines_of(f) or []
    head = re.compile(r"^\s{2}(\w+) (S\d): \(b\) (\d+), \(c\) (\d+), \(b\)&\(c\) (\d+) of (\d+) blocks")
    row = re.compile(r"^\s{6}(\w+)\s+\(b\) R " + NUM + r" p ([\d.]+) \w+\s*\| \(c\) D " + NUM + r" \(Rw' " + NUM + r" / Rx' " + NUM + r"\)")
    cur = None

    def flush(end):
        if not cur:
            return
        label, s, start, acc, nb = cur
        cid, src = corpus_id(label), f"{f}:{start}-{end}"
        kw = dict(segmenter=SEGNAME[s], pipeline="roach-r11", label=f"{label} {s}",
                  scope=f"median over {len(acc)} blocks (computed by world.py from the block rows)",
                  note="roach block estimator; 2,000 shuffles per test")
        stat(cid, "Rw1", med([a[0] for a in acc]), "r11", src, **kw)
        stat(cid, "Rc1", med([a[2] for a in acc]), "r11", src, **{**kw, "note": kw["note"] + "; Rx'"})

    for i, l in enumerate(ls, 1):
        m = head.match(l)
        if m:
            flush(i - 1)
            cur = (m.group(1), m.group(2), i, [], int(m.group(6)))
            continue
        m = row.match(l)
        if m and cur:
            cur[3].append([fnum(m.group(2)), fnum(m.group(5)), fnum(m.group(6))])
            continue
        if l.startswith("CALLS") and cur:
            flush(i - 1)
            cur = None
    flush(len(ls))


def parse_r12():
    f = "runs/roach-r12/results_r12.txt"
    ls = lines_of(f) or []
    label = None
    defs = {"L1_POOLED": "Pearson lag-1 word-length r over in-line pairs (primary)",
            "L1_LINE": "mean per-line lag-1 autocorrelation, lines >= 4 words",
            "PARA": "lag-1 inside paragraphs incl. pairs across line breaks (within-paragraph shuffles)",
            "XLINE": "last word of a line vs first word of the next"}
    for i, l in enumerate(ls, 1):
        m = re.match(r"^\s{2}(\w+): (\d+) blocks ; positive blocks: (.*)\(threshold", l)
        if m:
            label = m.group(1)
            pos = dict(re.findall(r"(\w+) (\d+)", m.group(3)))
            continue
        if label and l.strip().startswith("whole text:"):
            for name, obs, null, exc, p in re.findall(r"(\w+) obs " + NUM + " null " + NUM + " excess " + NUM + r" p_up ([\d.]+)", l):
                stat(corpus_id(label), "rhythm_excess", fnum(exc), "r12", f"{f}:{i}", p=fnum(p), segmenter="word-length",
                     pipeline="roach-r12", label=f"{label} {name}", scope=f"{name}: {defs.get(name, name)}; obs - within-line-shuffle mean (2,000 shuffles), whole text",
                     note=f"obs {obs}, null {null}; positive blocks {pos.get(name)}/15")
            label = None


def parse_explore():
    f = "runs/explore/wordlen_perline_bias_20261018.txt"
    ls = lines_of(f) or []
    for i, l in enumerate(ls, 1):
        m = re.match(r"^(?P<name>\S.*?)\s{2,}" + NUM + r"\s+" + NUM + r"\s+" + NUM + r" \|\s+" + NUM + r"\s+" + NUM + r"\s*$", l)
        if not m:
            continue
        cid = corpus_id(m.group("name").strip())
        kw = dict(segmenter="word-length", pipeline="explore-wordlen", label=m.group("name").strip())
        stat(cid, "rhythm_excess", fnum(m.group(4)), "explore-wordlen-20261018", f"{f}:{i}",
             scope="per-line mean Pearson lag-1 r minus 20 within-line shuffles, lines >= 3 words", note="exploratory, not pre-registered", **kw)
        pooled = fnum(m.group(5)) - fnum(m.group(6))
        stat(cid, "rhythm_excess", round(pooled, 4), "explore-wordlen-20261018", f"{f}:{i}",
             scope="pooled within-line Pearson lag-1 r minus shuffled (difference computed by world.py)",
             note=f"exploratory; pooled {m.group(5)} vs shuffled {m.group(6)}", **{**kw, "label": kw["label"] + " pooled"})


def parse_manifest_h2():
    f = "data/CONTROLS_MANIFEST.md"
    for ln, h, c, heading in md_rows(f):
        sec = (heading or "")[:2]
        if sec not in ("A.", "B.", "C.", "D.") or "h2" not in h:
            continue
        fn = clean(c[0])
        v = fnum(clean(c[h.index("h2")]))
        if v is None:
            continue
        if fn.startswith("Voynich"):
            cid = "voynich-ZL3b"
            note = "row 'Voynich EVA first 35k'; corpora.voynich() reads data/ZL3b-n.txt (vparse.DATA)"
        elif fn.startswith("plaintext"):
            cid, note = "nomen_plaintext_macer_pliny", None
        else:
            m = re.match(r"([\w/.-]+)\.txt", fn)
            if not m:
                continue
            cid, note = os.path.basename(m.group(1)), None
        scope = "first 25k tokens (35k for sections C/D rows)" if sec in ("A.", "B.") else "full synthetic file (~35k tokens)"
        stat(cid, "h2", v, "controls-manifest", f"{f}:{ln}", segmenter="char", pipeline="a1_profile",
             scope="character conditional entropy, space as a symbol (a1_profile.py); " + scope, label=fn, note=note)
    ln = find_line(f, "Reference: Voynich EVA h2")
    stat("voynich-ZL3b", "h2", 2.13, "controls-manifest", ln, segmenter="char", pipeline="a1_profile", label="Voynich EVA (reference line)",
         scope="character conditional entropy, space as a symbol (a1_profile.py); first 25k tokens",
         note="corpora.voynich() reads data/ZL3b-n.txt (vparse.DATA)")


# ----------------------------------------------------------------------------------------------- sources
# Snapshot of the scratchpad completeness_gap.md tables (kind, line, cells), written 2026-10-18 15:55 PDT by that file.
# Regenerate: python -I <scratchpad>/vkbw/gen_gap.py <scratchpad>/completeness_gap.md out.py
QUESTIONS = {  # completeness_gap.md "Top 15 gaps" (line) -> item title prefix
    138: "Water stains and offsets", 139: "Glyph-level segmentation", 140: "Multispectral imaging",
    141: "Period ciphers", 142: "Davis's 5-scribe", 143: "HistoCrypt and the VOY 2022", 144: "Alchemical-herbal family",
    145: "Tabular medical texts", 146: "Quire collation", 147: "Stolfi / Landini interlinear", 148: "Foldouts",
    149: "McCrone ink", 150: "Montemurro & Zanette", 151: "Shorthand systems", 152: "Reddy & Knight 2011"}
QUESTIONS_EXTRA = {150: "Bowern & Lindemann 2021", 152: "Currier 1976", 146: "Original foliation and quire marks"}
LIC_RE = re.compile(r"(CC[ -]BY(?:-SA)?[ -]?\d\.\d|CC BY(?:-SA)?|CC0|public domain|Public Domain(?: Mark)?(?: 1\.0)?|\bPD\b|MIT|Etalab|"
                    r"no formal licence|no licence(?: stated)?|ACL CC BY|Yale terms|attribution, no licence|paywalled|open access)", re.I)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def sources_rows(gap_text_lines):
    out = []
    qtext = {}
    if gap_text_lines:
        for ln in list(QUESTIONS) + list(QUESTIONS_EXTRA):
            qtext[ln] = gap_text_lines[ln - 1].strip() if ln - 1 < len(gap_text_lines) else None
    for kind, ln, c in _GAP:
        title = c[0]
        if kind == "literature":
            on_disk, claims = c[1], c[2]
            st = (re.match(r"(HAVE|PARTIAL|MISSING)", claims) or [None])[0]
            if title.startswith("Reddy") or title.startswith("HistoCrypt") or title.startswith("Voynich Ninja"):
                st = "MISSING"  # completeness_gap.md line 120 names these three rows MISSING
            path_cell, note = on_disk, claims
        else:
            st = re.match(r"(HAVE|PARTIAL|MISSING)", c[1]).group(1)
            path_cell, note = c[2], c[3]
            if c[1] != st:
                note = c[1] + "; " + note
        paths = re.findall(r"`([^`]+)`", path_cell)
        qs = [qtext.get(q) for q, pre in list(QUESTIONS.items()) + list(QUESTIONS_EXTRA.items()) if title.startswith(pre)]
        qsrc = [f"{GAP_MD}:{q}" for q, pre in list(QUESTIONS.items()) + list(QUESTIONS_EXTRA.items()) if title.startswith(pre)]
        lic = sorted(set(m.group(0) for m in LIC_RE.finditer(path_cell + " " + note)))
        out.append(dict(source_id=f"{kind[:5]}-{slug(title)}", kind=kind, title=title,
                        url=first_url(path_cell, note), licence="; ".join(lic) or None,
                        local_path="; ".join(paths) or None, have=st, gap_note=(path_cell + " | " + note) if kind != "literature" else f"on disk: {on_disk} | {claims}",
                        questions=" || ".join(q for q in qs if q) or None,
                        src=f"{GAP_MD}:{ln}" + ("; " + "; ".join(qsrc) if qsrc else "")))
    # Phase 8.5 sources refresh (2026-10-19): the gap map predates these pulls; disk wins when the file exists
    for r in out:
        if r["source_id"] in DISK_REFRESH:
            have, path, why = DISK_REFRESH[r["source_id"]]
            if os.path.exists(P(path)):
                r.update(have=have, local_path=path, gap_note=f"{r['gap_note']} | disk refresh: {why}")
    return out


DISK_REFRESH = {
    "physi-water-stains-and-offsets-layfield-davis-2026": ("HAVE", "data/external/intake-phase1/layfield-davis-2026-pdf.pdf",
                                                         "PDF 1.7, 866,048 B, plus layfield-davis-2026.html"),
    "compa-shorthand-systems-tironian": ("PARTIAL", "data/external/wave5-cnt-tironian",
                                         "CNT image corpus zip (Transcribo); images only, no text"),
}


def sources_fake_and_data():
    f = "data/external/README.md"
    rows = [
        ("fake-ivtff-format-pdf", "literature", "IVTFF format spec (saved copy is an HTML 404 page)", None, "data/external/voynich-nu-ivtff/ivtff_format.pdf",
         "FAKE", "355-byte HTML 404 saved under the PDF name; real spec now at voynich-nu-ivtff/ivtff_format.real.pdf", find_line(f, "| `voynich-nu-ivtff/ivtff_format.pdf`")),
        ("fake-meister-1902-zip", "comparandum", "Meister 1902 page scans (Pelling zip; saved copy is an HTML 404 page)", "http://www.nickpelling.com/voynich/Meister1902.zip",
         "data/external/lit-20261018/meister-1902-pelling-zip/Meister1902.zip", "FAKE", "355-byte HTML 404; real zip fetched from the Wayback Machine as Meister1902.real.zip",
         find_line(f, "Meister1902.zip` | HTML 404")),
        ("fake-greshko-2025-pdf", "literature", "Greshko 2025, Cryptologia (Naibbe cipher) paper PDF (saved copy is a Cloudflare challenge page)",
         "https://doi.org/10.1080/01611194.2025.2566408", "data/external/lit-20261018/greshko-tandf-pdf/greshko.pdf", "FAKE",
         "5,865-byte HTML challenge page; NOT OBTAINED (tandfonline 403, no Wayback); O-018 open", find_line(f, "greshko.pdf` | HTML Cloudflare")),
        ("lit-ivtff-format-spec-real", "literature", "IVTFF format specification (Zandbergen)", "https://www.voynich.nu/software/ivtt/IVTFF_format.pdf",
         "data/external/voynich-nu-ivtff/ivtff_format.real.pdf", "HAVE", "fetched 2026-10-18 16:07 PDT, PDF 1.7, 1,171,234 B", find_line(f, "ivtff_format.real.pdf")),
        ("comp-meister-1902-real", "comparandum", "Meister 1902, Die Anfaenge der modernen diplomatischen Geheimschrift (page scans)",
         "http://www.nickpelling.com/voynich/Meister1902.zip", "data/external/lit-20261018/meister-1902-pelling-zip/Meister1902.real.zip", "HAVE",
         "zip 11,273,577 B, integrity test passed, not extracted; closes the 'Meister 1902 not online' gap", find_line(f, "Meister1902.real.zip")),
    ]
    out = [dict(source_id=a, kind=b, title=c, url=d, licence=None, local_path=e, have=g, gap_note=h, questions=None, src=s)
           for a, b, c, d, e, g, h, s in rows]
    # data folders (HAVE unless stated), one row per data/external entry in its README and per other data/ dataset
    ext = [("voynich-nu-ivtff", "transliteration", "voynich.nu IVTFF transliterations (GC, FSG, CD, IT, VT, LSI, RF)", "https://www.voynich.nu/data/",
            "voynich.nu: no formal licence; citation requested", "| 1 | voynich.nu IVTFF"),
           ("schwartz-2026-preprint", "literature", "Schwartz 2026 preprint 'How the Voynich Manuscript was written' + text", "https://bootloops.ai/voynich.pdf", "no licence stated (author preprint)", "| 2 | Schwartz"),
           ("timm-schinner-generator", "comparandum", "Timm & Schinner self-citation generator + arXiv 1407.6639", "https://github.com/TorstenTimm/SelfCitationTextgenerator", "MIT (Java generator)", "| 3 | Timm"),
           ("bowern-lindemann-entropy", "dataset", "Lindemann & Bowern entropy corpora statistics CSVs + code (slimmed)", "https://github.com/chirila/Voynich-public", None, "| 4 | Lindemann"),
           ("gaskell-bowern-gibberish", "comparandum", "Gaskell & Bowern gibberish corpus (38 writers, 72 meaningful texts) + CEUR papers", "https://github.com/danielgaskell/voynich", "modified MIT for code + gibberish data", "| 5 | Gaskell"),
           ("word-coordinates", "layout", "Rozanova-Temerev voynich-units word boxes (223 folios) + Yale IIIF manifest", "https://github.com/lrozanova/voynich-units", "MIT (repo); third-party data keep their terms", "| 6 | Word bounding"),
           ("cribs", "literature", "Cribs: f68r star labels, zodiac labels, Sherwood plant list, f116v readings", None, None, "| 7 | Cribs"),
           ("nomenclators", "comparandum", "Period nomenclators: Meister 1906, Tranchedino notes, blog notes", "https://archive.org/details/diegeheimschrift00meis", "public domain (Meister 1906)", "| 8 | Period nomenclators"),
           ("naibbe-greshko", "comparandum", "Naibbe cipher (Greshko 2025) Zenodo supplement (Voynichesque.xlsm) + forum thread", "https://zenodo.org/records/17219445", "CC-BY-4.0 (Zenodo record)", "| + | Naibbe"),
           ("papers", "literature", "Papers: Rozanova-Temerev, Parisel, Zattera, Bowern-Gaskell, Montemurro-Zanette, pastiche LLM", None, "open access (per README)", "| + | Papers"),
           ("cremma", "comparandum", "CREMMA Medii Aevi v0.1.2 ALTO XML (121 files)", "https://github.com/HTR-United/CREMMA-Medieval-LAT", "CC-BY 4.0 vs CC0 conflict", "## cremma/"),
           ("yale_scans", "image", "Yale Beinecke MS 408 full-resolution IIIF JPEGs (204 canvases)", "https://collections.library.yale.edu/manifests/2002046", "public domain (Yale catalog)", "## 9. yale_scans/"),
           ("models", "dataset", "s48 frozen vision weights (dinov2-base, siglip-base-patch16-224)", "https://huggingface.co/facebook/dinov2-base", None, "## models/"),
           ("genre-s87", "comparandum", "s87 reference texts (Forme of Cury, Culpeper, Mandeville, Austin cookery, Alphita, Dispensarium)", None, "PD / Gutenberg / archive.org", None),
           ("genre-s89", "comparandum", "s89 reference texts (Kalevala, Horae Eboracenses, Atharva-Veda, Carmina Gadelica, Sinonoma, Promptorium)", None, "PD / Gutenberg / archive.org", None),
           ("lit-20261018", "literature", "literature downloads 2026-10-18 (Parisel 2604.25979, Steckley 2404.13069, Greshko, Meister 1902)", None, None, "## lit-20261018/"),
           ("quid-pro-quo", "comparandum", "quid pro quo pairs CSV + School of Salernum OCR", None, None, None),
           ("thevoynich-register", "dataset", "thevoynich register research snapshot JSON", None, None, None),
           ("cremma-medieval-lat-mlc1", "comparandum", "earlier CREMMA partial copy (83 files, unlogged; superseded by cremma/)", None, None, "cremma-medieval-lat-mlc1/")]
    for d, kind, title, url, lic, needle in ext:
        src = find_line(f, needle) if needle else f"data/external/{d}/" + ("MANIFEST.md" if d.startswith("genre") else "")
        if not needle and not d.startswith("genre"):
            src = f"data/external/{d}/"
        out.append(dict(source_id=f"data-ext-{d}", kind=kind, title=title, url=url, licence=lic, local_path=f"data/external/{d}/",
                        have="HAVE" if os.path.isdir(P(f"data/external/{d}")) else "MISSING", gap_note=None, questions=None, src=src))
    other = [("translit-sidecars", "transliteration", "transliteration sidecars (ZL3b_eva, RF1b, IT2a, GC2a meta.json)", "data/translit/"),
             ("facsimile", "image", "older facsimile cutouts (6 folios)", "data/facsimile/"),
             ("naibbe-zenodo", "comparandum", "Naibbe Zenodo 17219445 files (Naibbe_Cipher.xlsx, supplement PDF)", "data/naibbe_zenodo_17219445/"),
             ("folio-evidence-inventory", "physical", "folio evidence inventory (quire, page_in_quire, bifolio)", "data/folio_evidence_inventory.tsv"),
             ("controls", "comparandum", "natural-language and constructed controls (CONTROLS_MANIFEST.md)", "data/controls/"),
             ("controls_raw", "comparandum", "raw control downloads (untrusted)", "data/controls_raw/"),
             ("controls_synthetic", "comparandum", "synthetic controls (nomenclators, generators)", "data/controls_synthetic/"),
             ("controls_gibberish", "comparandum", "Gaskell & Bowern gibberish sidecars", "data/controls_gibberish/"),
             ("controls_realline", "comparandum", "real-line control sidecars (CREMMA, Dante, MHG, Old French, Occitan, gibberish)", "data/controls_realline/"),
             ("controls_period", "comparandum", "period recipe / remedy plaintexts for s102", "data/controls_period/"),
             ("controls_tabular", "comparandum", "tabular medical / combinatory texts for s107", "data/controls_tabular/"),
             ("controls_tabular_ruled", "comparandum", "ruled period medical table page images + OCR for s108", "data/controls_tabular_ruled/"),
             ("herbals_period", "comparandum", "period illustrated herbals LJS 419, Sloane 4016 (s103)", "data/herbals_period/"),
             ("herbals_alchemical", "comparandum", "alchemical-herbal family scans BSB Clm 5905, BL Add 41623 (s105)", "data/herbals_alchemical/")]
    for d, kind, title, path in other:
        readme = next((p for p in (path + "README.md", path.rstrip("/") + "/README.md") if os.path.exists(P(p))), None)
        src = readme or ("data/CONTROLS_MANIFEST.md" if d in ("controls", "controls_raw", "controls_synthetic") else path)
        out.append(dict(source_id=f"data-{d}", kind=kind, title=title, url=None, licence=None, local_path=path,
                        have="HAVE" if os.path.exists(P(path)) else "MISSING", gap_note=None, questions=None, src=src))
    return out


# ----------------------------------------------------------------------------------------------- external_items
# Snapshot of the scratchpad sprawl_external.md (stamp 2026-10-18 15:56 PDT). Exact file names for the Daybreak
# codex_lab results were resolved by listing codex_lab\experiments (read-only) while building this module.
SQ = "<team-comms>"
YM = "lab"
CL = YM + "\\codex_lab"
AR = "<home>//.gemini//antigravity//brain//<session>"
AR2 = "<home>//.gemini//antigravity//brain//<session>-..."
AR3 = "<home>//.gemini//antigravity//brain//<session>-..."
FR = "<local-path>"
EXT = [  # (path, location, kind, owner, filed_as, note, sprawl line)
    (SQ, "<team-comms>", "location", "<team-comms> comms (mixed: Daybreak, roach, skynet/codex)", "partly (r5-r11, s101, s100/s106 audits, O-059)", "809 Voynich/Daybreak/Argon-named files; contradicts repo in places", 11),
    (YM, YM, "location", "early battery (Oct-17)", "yes: all 39 results_*.txt byte-identical in repo", "stale, superseded", 12),
    (CL, CL, "location", "Daybreak", "partly: db-s88..99, 101, 104-106, 109, 111, 114, 115, 118, 120 cited", "221 experiment files, 117 reviews, acquisition corpora, 4 status files", 13),
    (AR, AR, "location", "Argon", "partly (s108/s109 designs; Fontana, Bodleian manifest, plant concordance not adopted)", "contradicts repo: s105 '100% unblocked'", 14),
    (AR2, AR2, "location", "Argon", "partly (s108 texts, s109 question)", "multi_agent_deep_investigation_synthesis.md; id truncated in the sprawl file", 15),
    (AR3, AR3, "location", "unstated (.gemini brain dir)", "yes (incoming/ten-theories, L-132 EXPLORATORY)", "voynich_10_theories_investigation.md; id truncated in the sprawl file", 16),
    (FR, FR, "location", "roach", "r1-r11 yes (runs/roach-r*); r12 filed since (runs/roach-r12)", "r1r2-raw, r3-r12, ten-theories; no r13 yet", 17),
    ("<local-path>", "<local-path>", "location", "mirror", "yes", "only incoming\\ten-theories", 18),
    ("<home>//.claude//projects//<agent-project>//memory", "memory dir", "location", "main session (guidance)", "n/a (guidance)", "7 files: goal, roster, comms, CPU, triangulation, order-agnostic", 19),
    ("<local-path>", "<local-path>", "location", "unrelated projects", "n/a", "no Voynich in <local-path>", 20),
    (FR + "<local-path>", FR, "result", "roach", "runs/roach-r12/results_r12.txt", "r12 word-length rhythm: Voynich-specific positive in-line rhythm NOT HOLDS (Kalevala 15/15)", 26),
    (SQ + "<local-path>", SQ, "package", "roach", "runs/roach-r12/", "identical copy of r12", 26),
    (SQ + "\\20261018T215500Z-roach-voynich91-r12-raw-package.zip", SQ, "package", "roach", "runs/roach-r12/", "r12 zip", 26),
    (CL + "<local-path>", CL, "package", "roach", "runs/roach-r12/", "r12 copy in codex_lab", 26),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s100 NO_LARGE_TAIL_PICTURE_LINK_DETECTED", 29),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s102 NO_REPLICATED_GEOMETRY_LINK (only a research-note mention)", 30),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s103 s93 recurrence overshoot: DIAGONAL_CAUSE", 31),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s107 NO_EARLY_HEAD_FRAME_REGISTER_LINK", 32),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s108 f57v Latin consonant key: NO_RING_KEY_SIGNAL", 33),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s110 label anchor: REPRESENTATION_DEPENDENT_LABEL_SIGNAL", 34),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s112 NO_OBJECT_LEVEL_LABEL_VISUAL_LINK", 35),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s113 NO_EXTERNAL_CONTAINER_LABEL_FORM_LINK", 36),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s116 NO_TWO_PART_ANTIDOTARY_ARCHITECTURE", 37),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s117 order-free Antidotarium graph: UNDERPOWERED", 38),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s119 medical recipe family retrieval: UNDERPOWERED", 39),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s121 NO_IDENTIFIED_RECIPE_SOURCE_OR_FAMILY (file name match to db-s121 unverified)", 40),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s122 NO_TRANSFERABLE_EXTERNAL_LABEL_FORM", 41),
    (SQ + "\\VOYNICH-DB-S123-LLULL-HELDOUT-*", SQ, "result", "Daybreak", None, "db-s123 Llull held-out continuation: HOLD at data gate (14 rows / 26 tokens < 30/100); .md/.txt/.json/.py/.sha256", 42),
    (CL + "<local-path>", CL, "result", "Daybreak", None, "db-s123 (codex_lab copy)", 42),
    (SQ + "\\VOYNICH-R12-EXACT-WORD-ABLATION*", SQ, "analysis", "Daybreak", None, "R12 identity ablation: removing identical pairs keeps 84-96% of cadence excess", 44),
    (SQ + "\\VOYNICH-R12-S0-S1-S2-ABLATION*", SQ, "analysis", "Daybreak", None, "R12 S0/S1/S2 ablation", 44),
    (SQ + "\\<team-comms>", SQ, "analysis", "Daybreak", None, "R11-R12 quire coupling (cadence vs exact recurrence r=.601, vs boundary contrast r=.707)", 45),
    (CL + "<local-path>", CL, "analysis", "Daybreak", None, "R11-R12 quire coupling review", 45),
    (SQ + "\\VOYNICH-S107-LLULL-RHYTHM*", SQ, "analysis", "Daybreak", None, "S107 Llull rhythm/stability (.py/.txt/.json)", 46),
    (SQ + "\\VOYNICH-S107-LLULL-JOINT-LEAD-2026-10-18.md", SQ, "analysis", "Daybreak", None, "S107 Llull joint lead", 46),
    ("s107_lull_cadence_physical_unit_correction_2026-10-18.md", "unstated (<team-comms> or codex_lab)", "analysis", "Daybreak", None, "S107 physical-unit correction; location not given in the sprawl file", 46),
    (SQ + "\\VOYNICH-LEAD-S109-PREFREEZE-AUDIT-2026-10-18.md", SQ, "audit", "Daybreak", None, "HOLD_BEFORE_FREEZE, six missing requirements (+ .json); audited a pre-stub state", 47),
    (SQ + "\\<team-comms>", SQ, "comms", "Daybreak", None, "S109 pre-freeze HOLD message", 47),
    (CL + "<local-path>", CL, "analysis", "Daybreak", None, "R14 Vatican Pal. lat. 984 ruled 4-char rows; zero repo hits", 48),
    (CL + "<local-path>", CL, "analysis", "Daybreak", None, "R14 Barcelona BC Ms 3075 f114r-f119r (1457)", 48),
    (CL + "<local-path>", CL, "analysis", "Daybreak", None, "R14 UCM BH MSS 106 negative preflight", 48),
    (CL + "<local-path>", CL, "analysis", "Daybreak", None, "R14 Lullian combinatory reference sources", 48),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "1.9 MB, receipt + manifest", 48),
    (SQ + "\\VOYNICH-ROACH-R13-PROPOSAL-2026-10-18.md", SQ, "proposal", "Daybreak", None, "r13 continuous reference contrast; differs from repo P-50 r13 = s101 replication", 49),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "label catalogue", 51),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "label attributes", 51),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "object-label registration", 51),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "Antidotarium Nicolai Latin recipes; no repo hits", 52),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "Scribonius Latin recipes", 52),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "Liber de coquina Latin recipes", 52),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "CoReMa culinary recipes", 52),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "9.5 MB", 52),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "CoReMa M2 Alemannic", 52),
    (CL + "<local-path>", CL, "dataset", "Daybreak", None, "22 MB", 52),
    (AR + "<local-path>", AR, "dataset", "Argon", "not adopted (PLAN 14:42)", "1-98 plant concordance; s105 HOLD in repo", 54),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "with canon_misc_408/500 parsed manifests", 54),
    (AR + "<local-path>", AR, "literature", "Argon", None, "Beasley 2024 thesis (.pdf/.txt); repo gap map lists it MISSING", 54),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "IIIF manifests", 54),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "witness IIIF status", 54),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "collation / conjoint-leaf table; repo has no collation table", 55),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "bifolio affinity", 55),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "15,666 ink gaps", 55),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "43 Rozanova pages", 55),
    (AR + "<local-path>", AR, "result", "Argon", "not adopted; Argon quarantined (D-065)", "Fontana NAL 635 pegboard simulator; results_h19_fontana_lull.txt SHOWS_F40_CORE=True, FULL_C1=True (unregistered)", 56),
    (AR + "<local-path>", AR, "dataset", "Argon", None, "Alfonso Lapidario degree stones, Astrolabium 1494/1502, De balneis, star_deviations_catalog.tsv", 57),
    (AR2 + "\\multi_agent_deep_investigation_synthesis.md", AR2, "synthesis", "Argon", "partly (s109 uses the label question)", "cross-section label scan, Q1-Q20 collation + 7 missing-leaf gaps + Davis 5-scribe map, tabular corpora URLs", 58),
    (SQ + "\\VOYNICH-DB-S114-GHOST-ROW-CORRECTION-2026-10-18.md", SQ, "analysis", "Daybreak", "O-059 open; FINDINGS-GRAPH line 425 unchanged", "confirms O-059 (15 independent pairs)", 66),
    (SQ + "\\VOYNICH-CURRENT-STATE-2026-10-18.md", SQ, "status-file", "Daybreak", None, "teammate status file; stated times unreliable", 70),
    (SQ + "\\VOYNICH-AGENT-START.md", SQ, "status-file", "Daybreak", None, "teammate start file", 71),
    (SQ + "\\VOYNICH-AGENT-START-2026-10-18.md", SQ, "status-file", "Daybreak", None, "teammate start file", 71),
    (SQ + "\\AGENT-START.md", SQ, "status-file", "Daybreak", None, "says 'Canonical interpretation'; read-first list puts codex_lab before the repo", 71),
    (SQ + "\\VOYNICH-EVIDENCE-INDEX.md", SQ, "status-file", "Daybreak", None, "overstates S101 (repo D-068: F-23/F-30 at-risk)", 72),
    (SQ + "\\VOYNICH-EVIDENCE-INDEX-2026-10-18.md", SQ, "status-file", "Daybreak", None, "evidence index", 72),
    (SQ + "\\VOYNICH-TOP10-EVIDENCE-2026-10-18.md", SQ, "status-file", "Daybreak", None, "109 KB; ~30 other VOYNICH-TOP10-* versions; says producer exclusions withdrawn", 73),
    (SQ + "\\VOYNICH-TOP10-PLAIN-ENGLISH-2026-10-18.md", SQ, "status-file", "Daybreak", None, "top-10 plain English", 73),
    (CL + "\\AGENT-START.md", CL, "status-file", "Daybreak", None, "codex_lab status file", 74),
    (CL + "\\CURRENT_STATE_2026-10-18.md", CL, "status-file", "Daybreak", None, "stronger than repo on S101", 74),
    (CL + "\\EVIDENCE-INDEX.md", CL, "status-file", "Daybreak", None, "codex_lab evidence index", 74),
    (CL + "\\BIG-PICTURE-EVIDENCE-SYNTHESIS-2026-10-18.md", CL, "status-file", "Daybreak", None, "codex_lab synthesis", 74),
    (YM + "\\TEAM-HANDOFF.md", YM, "status-file", "early battery (Oct-17)", None, "Oct-17 stale; says 'Read in this order (canonical)'", 75),
    (YM + "\\PLAN.md", YM, "status-file", "early battery (Oct-17)", None, "Oct-17 stale", 75),
    (YM + "\\FINDINGS.md", YM, "status-file", "early battery (Oct-17)", None, "Oct-17 stale", 75),
    (YM + "\\LEADS-AND-FINDINGS.md", YM, "status-file", "early battery (Oct-17)", None, "Oct-17 stale", 75),
    (AR + "\\VOYNICH_MASTER_FINDINGS_INDEX.md", AR, "status-file", "Argon", None, "'single retrieval hub', 'Current Established Truth'; §8 s105 '100% Unblocked' contradicts repo", 76),
    (AR + "\\voynich_deep_web_and_cross_manuscript_triangulation.md", AR, "synthesis", "Argon", None, "§2 s105 unblocked claim", 62),
    (AR + "\\voynich_concrete_truths_and_relationships.md", AR, "status-file", "Argon", None, "self-marked superseded", 77),
    (AR + "\\voynich_cryptanalysis_report.md", AR, "status-file", "Argon", None, "self-marked superseded", 77),
]
INTAKE_CLASSES = ("admissible", "scope", "not-admissible", "data-only", "unaudited")
# Classes from the scratchpad intake.md (stamp 2026-10-18 16:08 PDT), applied only when that file exists at build
# time. Its wording maps as ADMISSIBLE -> admissible, ADMISSIBLE-WITH-SCOPE -> scope, NOT ADMISSIBLE -> not-admissible,
# DATA-ONLY -> data-only. path -> (class, intake.md line, wording).
_E = CL + "<local-path>"
_A = CL + "<local-path>"
_R = CL + "<local-path>"
_S = AR + "<local-path>"
INTAKE = {
    _E + "results_s100_tail_picture_semantic_link.txt": ("scope", 18, "ADMISSIBLE-WITH-SCOPE"),
    _E + "results_s102_tail_objective_geometry.txt": ("scope", 19, "ADMISSIBLE-WITH-SCOPE"),
    _E + "results_s103_s93_recurrence_overshoot_diagnosis.txt": ("scope", 20, "ADMISSIBLE-WITH-SCOPE (method note)"),
    _E + "results_s107_head_frame_to_tail_register.txt": ("scope", 21, "ADMISSIBLE-WITH-SCOPE"),
    _E + "results_s108_f57v_latin_consonant_key.txt": ("scope", 22, "ADMISSIBLE-WITH-SCOPE"),
    _E + "results_s110_label_anchor_robustness.txt": ("admissible", 23, "ADMISSIBLE"),
    _E + "results_s112_object_level_label_visual_link.txt": ("scope", 24, "ADMISSIBLE-WITH-SCOPE"),
    _E + "results_s113_external_container_label.txt": ("scope", 25, "ADMISSIBLE-WITH-SCOPE (uninformative exclusion)"),
    _E + "results_s116_antidotarium_two_part_architecture.txt": ("not-admissible", 26, "NOT ADMISSIBLE as a negative (D-063); file as UNDERPOWERED"),
    _E + "results_s117_order_free_antidotarium_graph_mapping.txt": ("not-admissible", 27, "NOT ADMISSIBLE beyond UNDERPOWERED"),
    _E + "results_s119_medical_recipe_family_retrieval.txt": ("admissible", 28, "ADMISSIBLE as UNDERPOWERED (no claim)"),
    _E + "results_s121_frozen_role_graph_q20_application.txt": ("scope", 29, "ADMISSIBLE-WITH-SCOPE"),
    _E + "results_s122_expanded_external_label_form.txt": ("scope", 30, "ADMISSIBLE-WITH-SCOPE (not an exclusion; weak trend)"),
    SQ + "\\" + "VOYNICH-DB-S123-LLULL-HELDOUT-*": ("admissible", 63, "ADMISSIBLE as HOLD; no scientific claim"),
    _E + "results_db_s123_lull_heldout_continuation.txt": ("admissible", 63, "ADMISSIBLE as HOLD; no scientific claim"),
    _R + "pal_lat_984_table_visual_triage_2026-10-18.md": ("data-only", 84, "DATA-ONLY (visual preflight, no claim)"),
    _R + "bc_ms_3075_table_visual_triage_2026-10-18.md": ("data-only", 84, "DATA-ONLY (visual preflight, no claim)"),
    _R + "ucm_bh_mss_106_layout_preflight_2026-10-18.md": ("data-only", 84, "DATA-ONLY (visual preflight, no claim)"),
    _R + "lullian_combinatory_reference_sources_2026-10-18.md": ("data-only", 84, "DATA-ONLY"),
    _A + "bc_ms_3075_r14\\": ("data-only", 84, "DATA-ONLY (images and manifests; rights CNE)"),
    SQ + "\\" + "VOYNICH-R12-EXACT-WORD-ABLATION*": ("scope", 94, "ADMISSIBLE-WITH-SCOPE as descriptive lines only (unverified: true)"),
    SQ + "\\" + "VOYNICH-R12-S0-S1-S2-ABLATION*": ("scope", 94, "ADMISSIBLE-WITH-SCOPE as descriptive lines only (unverified: true)"),
    SQ + "\\" + "<team-comms>": ("scope", 94, "ADMISSIBLE-WITH-SCOPE as descriptive lines only"),
    _R + "r11_r12_quire_coupling_2026-10-18.md": ("scope", 94, "ADMISSIBLE-WITH-SCOPE as descriptive lines only"),
    _A + "s114_stolfi_full_label_catalogue.csv": ("data-only", 113, "DATA-ONLY; licence unknown (cite as derived)"),
    _A + "s113_stolfi_label_attributes.csv": ("data-only", 113, "DATA-ONLY; licence unknown"),
    _A + "s112_object_label_registration.csv": ("data-only", 113, "DATA-ONLY"),
    _A + "s115_antidotarium_nicolai_latin_recipes.csv": ("data-only", 113, "DATA-ONLY; DBNL licence to be confirmed"),
    _A + "s119_scribonius_latin_recipes.csv": ("data-only", 113, "DATA-ONLY; do not copy (thesis licence)"),
    _A + "s119_liber_de_coquina_latin_recipes.csv": ("data-only", 113, "DATA-ONLY; licence not stated"),
    _A + "s119_corema_*_culinary_recipes.csv": ("data-only", 113, "DATA-ONLY; CC BY 4.0"),
    _A + "corema_collection\\": ("data-only", 113, "DATA-ONLY; CC BY 4.0"),
    _A + "corema_m2_alemannic\\": ("data-only", 113, "DATA-ONLY; CC BY 4.0"),
    _A + "external\\": ("data-only", 113, "DATA-ONLY; mixed licences"),
    _S + "h19_fontana_lull\\": ("not-admissible", 128, "NOT ADMISSIBLE (unregistered, edited after the run, circular)"),
    _S + "o062_herbal\\alchemical_herbal_98_concordance.tsv": ("data-only", 131, "DATA-ONLY, provenance partly unverifiable"),
    _S + "physical_forensics\\exp3_e3_leaf_collation_all.tsv": ("data-only", 151, "DATA-ONLY (derived from repo folio_evidence_inventory.tsv)"),
    _S + "physical_forensics\\exp3_e3_bifolio_lobo_affinity.tsv": ("data-only", 151, "DATA-ONLY (derived from repo data)"),
    _S + "physical_forensics\\exp1_e5_hesitation_summary.tsv": ("not-admissible", 151, "NOT ADMISSIBLE (ink-gap result; s47 output re-tabulated, unregistered claim)"),
}

# Later intake audits (audit-external-A/B/C/D.md, 2026-10-18): one table row per item, first cell = exact path
# (backticks optional), second cell = class. They extend INTAKE; a path already in INTAKE keeps its earlier class.
EXTERNAL_AUDITS = sorted(glob.glob(os.path.join(SCRATCH, "audit-external-*.md")))


def _external_audit_classes():
    out = {}
    for fp in EXTERNAL_AUDITS:
        with open(fp, encoding="utf-8", errors="replace") as f:
            for ln, row in enumerate(f, 1):
                if not row.startswith("|"):
                    continue
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if len(cells) < 3 or cells[1] not in INTAKE_CLASSES[:4]:
                    continue
                path = cells[0].strip("`").strip()
                if path.startswith("ARG\\"):  # audit-external-A abbreviates the Argon brain directory
                    path = AR + path[3:]
                out.setdefault(path, (cells[1], ln, cells[2][:300], fp))
    return out


EXTERNAL_CLASSES = _external_audit_classes()

INTAKE_DIR = os.path.join(ROOT, "data", "external", "intake")


def _intake_from_files():
    """Phase 8.2 (D-070): intake classes and extra external items live in data files, not code literals.
    intake_classes.tsv overrides the INTAKE literal (kept as fallback); external_items_extra.tsv adds team items."""
    import csv
    f = os.path.join(INTAKE_DIR, "intake_classes.tsv")
    if os.path.exists(f):
        with open(f, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="	", quoting=csv.QUOTE_NONE):
                INTAKE[r["path"]] = (r["intake_class"], int(r["intake_md_line"] or 0), r["wording"])
    extra = []
    f = os.path.join(INTAKE_DIR, "external_items_extra.tsv")
    if os.path.exists(f):
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        with open(f, encoding="utf-8", newline="") as fh:
            for i, r in enumerate(csv.DictReader(fh, delimiter="	", quoting=csv.QUOTE_NONE), start=2):
                extra.append(dict(path=r["path"], location=r.get("location"), kind=r.get("kind"), owner=r.get("owner"),
                                  intake_class=r.get("intake_class") or "unaudited", filed_as=r.get("filed_as") or None,
                                  note=r.get("note"), src=f"{rel}:{i}" + (f"; {r['evidence']}" if r.get("evidence") else "")))
    return extra

# completeness_gap.md table rows: (kind, line, cells). Snapshot; see the note above QUESTIONS.
_GAP = [('transliteration',
  25,
  ['ZL3b (EVA, IVTFF 2.0, 13/05/2025)',
   'HAVE',
   '`data/ZL3b-n.txt`; sidecars `data/translit/ZL3b_eva.meta.json`, `ZL3b_glyphplus.meta.json`',
   '740 `<%>` markers. These do not exhaust the physical entries: on f108v, f111r and f111v the scans show '
   '16/17/19 stars where `<%>` gives 7/6/8 (L-216; 321 stars against about 285 paragraphs). The page '
   'variables carry $Q, $P, $F, $B, $I, $L, $H (Davis) and $C (Currier hands 1-5, X, Y).']),
 ('transliteration',
  26,
  ['RF1b (ZL+GC merged via STA1)',
   'HAVE',
   '`data/external/voynich-nu-ivtff/RF1b-e.txt` (extended EVA), `RF1b-er.txt` (basic); '
   '`data/translit/RF1b.meta.json`',
   '100% coverage. Extended `@nnn;` codes are lost in `-er`.']),
 ('transliteration',
  27,
  ['IT2a (Takahashi, 1999 state)',
   'HAVE',
   '`voynich-nu-ivtff/IT2a-n.txt`, `data/translit/IT2a.meta.json`; also `VT0e-n.txt` (voynichese.com auto '
   'version)',
   '96.8% coverage. VT0e is auto-generated and has fewer types (8,078 against 8,547).']),
 ('transliteration',
  28,
  ['Takahashi original EVT',
   'PARTIAL',
   'only via IT2a and LSI',
   "the original `takahashi.evt` from Stolfi's mirror is not on disk (low value)"]),
 ('transliteration',
  29,
  ["Currier / D'Imperio (CD2a)",
   'HAVE',
   '`voynich-nu-ivtff/CD2a-n.txt`',
   '40.8% coverage (herbal-heavy). Currier alphabet, so it needs an alphabet map; no meta sidecar.']),
 ('transliteration',
  30,
  ['FSG (FG2a)',
   'HAVE',
   '`voynich-nu-ivtff/FG2a-n.txt`',
   '75.4% coverage: no circular or radial text, only 98 labels; no sidecar']),
 ('transliteration',
  31,
  ['v101 (Glen Claston, GC2a + voyn_101)',
   'HAVE',
   '`GC2a-n.txt`, `voyn_101.txt`, `data/translit/GC2a.meta.json`',
   'Not losslessly convertible to EVA. The h2 band is alphabet-specific (O-022: GC2a 2.540).']),
 ('transliteration',
  32,
  ['EVA variants (Eva-T basic, extended EVA, STA1, glyph+)',
   'PARTIAL',
   'basic and extended EVA via RF1b; glyph+ sidecar',
   "No standalone STA-alphabet file. Zattera's SLA alphabet exists only as the paper "
   '(`papers/zattera_2022...`). The IVTFF spec PDF is a 404 page (see Defects). Source: '
   'https://www.voynich.nu/extra/sp_transcr.html (no licence; citation requested).']),
 ('transliteration',
  33,
  ['Stolfi / Landini interlinear',
   'PARTIAL',
   "`voynich-nu-ivtff/LSI_ivtff_0d.txt` (Zandbergen's IVTFF 1.5 beta conversion)",
   "Stolfi's original release 1.6e6 (`tcmt16e6.evt`, per-page comment files, per-unit files) is not on disk. "
   'Source: https://ic.unicamp.br/~stolfi/voynich/98-12-28-interln16e6 (no licence stated; about 2-5 MB). '
   'Ghost duplicates: O-059 reports that 16 of 31 repeated label pairs may be interlinear duplicates in '
   "Stolfi's 1998 HTML (f89r2 under f89v2, f100v under f101v1). This is **unverified**, and db-s114 is "
   'blocked on it. LSI token counts sum over transcribers, so split by the transcriber letter first.']),
 ('transliteration',
  34,
  ['Per-locus transcriber disagreement table',
   'HAVE',
   'data/translit/locus-disagreement/SUMMARY.txt',
   '5282 loci with at least two primary LSI readers: all-token agree 0.2226, word counts differ on 0.4154. '
   'H vs F token agree 0.3272 (n=4074); H vs C 0.3384 (n=2550). Whole-locus identity, not a word-aligned rate. '
   'GC2a is word counts only (0.5656 vs IT2a). Not the frozen profile.']),
 ('image',
  42,
  ['Yale Beinecke full-resolution scans',
   'HAVE',
   '`data/external/yale_scans/pages/` (204 JPEGs, 523 MB, sha256 in MANIFEST.md); manifest '
   '`manifest_2002046.json`',
   'Public domain (Yale catalogue). These are IIIF `full/full` JPEGs at native size (about 2700-3000 x '
   '3700-3800 px). The TIFF masters (`/download/tiff/<id>`) were not fetched. Covers, flyleaves, spine and '
   'edges were skipped (9 canvases).']),
 ('image',
  43,
  ['Foldouts',
   'PARTIAL',
   'composite canvases ("69v and 70r", "85r (part)", ...); `tools/segment_scans.py` lists them as unmatched',
   '11 panels from canvases that already had two or more x-fractions in tools/plant_regions.py '
   'are in data/physical/foldout_panels/. Those fractions were set by eye and are unverified. '
   'f67, f68, f72, f85/86, f90r1 against f90r2, and f95 have no fraction on disk and were not cut.']),
 ('image', 44, ['Older facsimile cutouts', 'HAVE', '`data/facsimile/` (6 folios)', '—']),
 ('image',
  45,
  ['Multispectral imaging (Lazarus Project / RIT 2014, released by Davis 2024; 10 folios: 1r, 8r, 17r, 26r, '
   '47r, 70v1, 71r, 93r, 102v1, 116v)',
   'PARTIAL',
   'Google Drive folder https://drive.google.com/drive/folders/1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig, linked '
   'from '
   'https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/',
   'PARTIAL on disk 2026-10-19: data/msi/f1r (44 files) and <local-path> f17r+f116v '
   '(86 files including MANIFEST.sha256; O-069 records 85 files). The other seven of the ten named '
   'folios are not in those folders. Hashes were not rechecked in this edit. No formal licence; credit '
   'the Lazarus Project / RIT Carlson Center. This replaces the older O-060 deferred wording.']),
 ('image',
  46,
  ['Raking light',
   'MISSING (no public source)',
   'none found; the only public trace is a proposal on ciphermysteries (raking IR of f116v)',
   'It would need a request to the Beinecke. A stand-in is the MSI lab true-colour set on the same 10 '
   'folios.']),
 ('image',
  47,
  ['Covers, spine and binding images',
   'PARTIAL',
   'they are in the Yale manifest but were skipped by the fetch',
   'small; same PD source']),
 ('physical',
  55,
  ['Quire collation and missing leaves',
   'PARTIAL',
   '$Q, $P, $F, $B in `data/ZL3b-n.txt`; `data/folio_evidence_inventory.tsv` (quire, page_in_quire, '
   'bifolio); prose list in `research_notes/.../physical_provenance.md` Q3',
   'There is no structured collation table with missing-leaf slots (f12 stub, ff59-64, f74 stub, ff91-92, '
   'ff97-98, ff109-110; 14 against 16 missing). Sources: https://www.voynich.nu/descr.html and Layfield & '
   'Davis 2026 Table 5.']),
 ('physical',
  56,
  ['Bifolio structure and conjugate pairs',
   'HAVE',
   'ZL $B / $F; used by `s35_physical_codicology_quire_network.py` and `p1_bifolio_null.py`',
   'Not cross-checked against Layfield & Davis Table 5 (CC BY 4.0, '
   'https://journals.openedition.org/digitalmedievalist/2331).']),
 ('physical',
  57,
  ['Original foliation and quire marks',
   'PARTIAL',
   'prose only (physical_provenance.md)',
   'No per-folio table records foliation hand, quire-mark presence, the trailing "9", or paint over numbers '
   '(f42r). Source: https://voynich.nu/extra/sp_origin.html.']),
 ('physical',
  58,
  ["Davis's 5-scribe assignments",
   'HAVE',
   '$H in ZL3b (113/46/33/27/7 pages); article data/external/intake-phase1/davis-2020.pdf',
   'The 2020 article is data/external/intake-phase1/davis-2020.pdf. It names five scribes and says f115r '
   'starts with Scribe 2 and passes to Scribe 3. A folio table was not copied to a TSV. The model is contested (O-020).']),
 ('physical',
  59,
  ['Water stains and offsets (Layfield & Davis 2026)',
   'MISSING',
   'The article has **no catalogue** of stains or offsets (checked by fetch). It names only 10v/15r '
   '(splash), 33v/40r (blue), 58v/65r (green), 76v/83r (arm) and 78v/81r (streams).',
   'No public dataset exists, so one would have to be built from the scans.']),
 ('physical',
  60,
  ['Stitching and binding history',
   'PARTIAL',
   'prose (physical_provenance.md Q3: single late-Gothic sewing, Zyats 2016)',
   'No sewing-station or thread-hole data. Zyats et al. AIC 2011 paper: '
   'https://resources.culturalheritage.org/conservators-converse/?p=3447.']),
 ('physical',
  61,
  ['C14 dating (Arizona 2009)',
   'HAVE',
   'data/external/intake-phase1/hodgins-2009.pdf (10 pp.; sha256 7a84d9582bcf5de7…)',
   'Figure 7: mean n=4, 516±18 BP, 95.4% 1404-1438 AD, 68.2% 1411-1430 AD. Untreated f68 excluded. '
   'Leaf 26 alone is 1404-1438 at 68.2%, a different interval. c-561.']),
 ('physical',
  62,
  ['McCrone ink and pigment report (2009)',
   'HAVE',
   'data/external/intake-phase1/mccrone-2009.pdf (8 pp. image scan, 6,059,189 B, Canon ScanFront 220, created 2009-04-01)',
   'Stored whole. No text layer, so pigment sentences are not filed. Footer on the public copy asks that it not be reproduced in part.']),
 ('physical', 63, ['Vellum (calf; goat cover, York 2014)', 'PARTIAL', 'prose', 'no source document on disk']),
 ('physical',
  64,
  ['f116v marginalia',
   'PARTIAL',
   'images, plus `data/external/cribs/stolfi_f116v.htm`, `stolfi_note016_f116v.txt`, ciphermysteries page',
   'The MSI f116v stack is missing.']),
 ('physical',
  65,
  ['f1r key-like letters and Tepenec signature',
   'PARTIAL',
   'image `002_1r.jpg`; ZL comment (lines 5-20 of ZL3b)',
   'MSI 1r (UV signature, erased text) is missing.']),
 ('physical',
  66,
  ['f17r marginalia', 'PARTIAL', 'image only', 'MSI 17r is missing and no reading is on disk.']),
 ('physical',
  67,
  ['Provenance documents (Marci 1665/66, Baresch 1637/1639, Kircher, Horczicky)',
   'PARTIAL',
   'secondary prose only',
   'Transcriptions and translations: https://www.voynich.nu/letters.html (research use; the Kircher '
   'carteggio scan links died in 2025 per that page). Guzy 2022 on Rudolf II book transactions is CEUR 3313 '
   'paper 16 (CC BY 4.0).']),
 ('layout',
  75,
  ['Word bounding boxes (Rozanova / voynichese.com)',
   'HAVE',
   '`data/external/word-coordinates/lrozanova-voynich-units-main/.../voynichese_boxes/` (223 folios, MIT)',
   'Snapped to a 3-px grid on a page about 600 px wide. Provenance is "incompletely documented" (O-019). Box '
   'gaps disagree with ink gaps at 26% of zero-gap sites.']),
 ('layout',
  76,
  ['Line boxes',
   'PARTIAL',
   '`runs/s47/lines.tsv`, `positions.tsv`; s45 `ink_lines_ZL3b.meta.json`',
   'These come from scan segmentation aligned to ZL. There is no independent line-polygon ground truth '
   '(PAGE-XML).']),
 ('layout',
  77,
  ['Label loci',
   'HAVE',
   '`@L` loci in ZL3b; cribs for f67v2, f68r1-r3 and f70v-f73v (clock positions)',
   'No x,y anchor of each label against its drawn object.']),
 ('layout',
  78,
  ['Ink-derived word gaps (s45, s47)',
   'HAVE',
   '`runs/s45/`, `runs/s47/`, `results_s45.txt`, `results_s47.txt`',
   'κ 0.87 against ZL spaces; scope is agreement only (O-048)']),
 ('layout',
  79,
  ['Paragraph and star positions (s100)',
   'HAVE',
   '`runs/s100/star_classes.tsv` (321 stars: page x,y, nearest line, filled/tailed)',
   'Paragraph starts beyond `<%>` are not re-encoded as loci (O-061).']),
 ('layout',
  80,
  ['Illustration and plant regions',
   'PARTIAL',
   '`runs/s48/` (crops, embeddings) via `tools/plant_regions.py`',
   'No full-manuscript drawing/text mask and no text-over-paint order.']),
 ('layout',
  81,
  ['Glyph-level segmentation',
   'MISSING',
   'none public (README §6: "Not found")',
   'must be built from the scans']),
 ('comparandum',
  89,
  ['Period herbals (images and plant identities)',
   'PARTIAL',
   '`data/herbals_period/ljs419` (205 images, PD), `sloane4016` (235); captions are agent transcriptions and '
   '**unverified**',
   'No edition-sourced identities. Touwaide 2013 (Sloane 4016) is not open. Tucker & Talbert 2013 '
   '(HerbalGram) is not on disk. Sherwood lists are in `cribs/`.']),
 ('comparandum',
  90,
  ['Alchemical-herbal family (Beasley 2024, 38 MSS)',
   'PARTIAL',
   '`data/herbals_alchemical/` (BSB Clm 5905 and BL Add 41623 on disk but **outside** the family); BnF Lat. '
   '17848/17844 were refused by Gallica',
   'The thesis PDF is not on disk: https://shareok.org/items/76577e4f-2332-4974-b6ca-113704873aaf (ShareOK; '
   'licence unverified). Segre Rutz 2000 (identities) is not open. O-062.']),
 ('comparandum',
  91,
  ['Recipe texts',
   'HAVE',
   '`data/controls_period/raw_it`, `raw_de`; `external/genre-s87` (Forme of Cury and others)',
   '—']),
 ('comparandum',
  92,
  ['Tabular medical texts',
   'PARTIAL',
   '`data/controls_tabular/` (MediManus Tacuinum BnF lat. 9333 is the **only machine-readable table** found; '
   'De gradibus; Lull Tabula); `controls_tabular_ruled/` (1531/1532 page images, OCR 39-53% token match, '
   'L-223)',
   'No transcription of a ruled table exists (O-063). It would need HTR (CREMMA models) or manual keying.']),
 ('comparandum',
  93,
  ['Lullian works',
   'HAVE',
   '`controls_tabular/raw_lull*` (1515, 1596, 1617)',
   'only the Tabula generalis is scored']),
 ('comparandum',
  94,
  ['Period ciphers (Florentine, Venetian, Milanese) and nomenclators',
   'PARTIAL',
   '`external/nomenclators/` (Meister 1906 PD; Pelling blogs); Megyesi 2022 and 2021 statistics in '
   '`research_notes/External anchors/period_nomenclators.md`',
   'Missing: (a) the **DECODE database** (https://de-crypt.org; over 1,000 keys, about 41% transcribed; '
   'papers CC BY 4.0, data terms **unverified**); (b) Meister 1902 (HathiTrust `pdus`, hvd.hxub2m and '
   'uc1.b4177709, US IP only); (c) Tranchedino Cod. Vind. 2398 (no ÖNB digitisation found; ADEVA 1970 '
   'facsimile only).']),
 ('comparandum',
  95,
  ['Shorthand systems (Tironian)',
   'MISSING',
   'Schmitz 1893 *Commentarii notarum tironianarum*: https://archive.org/details/commentariinotar00schm (PD, '
   'OCR)',
   'about 13,000 signs; no control file in `data/controls/`']),
 ('comparandum',
  96,
  ['Glossaries',
   'PARTIAL',
   '`genre-s89` (Promptorium parvulorum, Sinonoma Bartholomei, Alphita); Lingua Ignota is a 30-entry sample '
   'only (O-015)',
   '—']),
 ('comparandum',
  97,
  ['Period Latin, Italian and German texts',
   'HAVE',
   'CREMMA (121 XML, CC BY/CC0 conflict), `data/controls/*`, `controls_period`',
   '—']),
 ('comparandum',
  98,
  ['Real period gibberish manuscript (Sloane MS 3188, Boxer 2022)',
   'MISSING',
   'CEUR 3313 paper 1 (CC BY 4.0) https://ceur-ws.org/Vol-3313/',
   'the only real-manuscript meaningless-text comparator named in the literature']),
 ('literature',
  106,
  ['Currier 1976',
   'No (https://voynich.nu/extra/curr_main.html, transcription by Guy and Reeds 1992)',
   'PARTIAL. A/B and hands are used throughout via $L/$C. Parisel 2026b confirms them. His specific '
   'statistics (line-final and line-initial glyph rules, the hand 3/4/X/Y claims) are not tested as '
   'claims.']),
 ('literature',
  107,
  ['Stolfi (word grammar, page notes)',
   'PARTIAL (cribs, LSI)',
   'PARTIAL. Recorded in CONSTRAINTS-MAP; the 2000 grammar is not scored directly.']),
 ('literature',
  108,
  ['Reddy & Knight 2011',
   'No (https://aclanthology.org/W11-1511/, ACL CC BY)',
   'Recorded only as "external, unverified" in FINDINGS-GRAPH line 162. Not tested.']),
 ('literature',
  109,
  ['Montemurro & Zanette 2013',
   'Yes (`papers/montemurro_zanette_2013_plosone.txt`, CC BY)',
   'PARTIAL. Claim c-221 is VERIFIED-LITERATURE, but the information-vs-scale peak (M18) has **no code** '
   '(METHODS.md line 196).']),
 ('literature',
  110,
  ['Timm & Schinner',
   'Yes (generator, arXiv 1407.6639)',
   'HAVE. Scored as a producer (`ctl_timm_schinner.py`, n6/n7). The 2019/2020 Cryptologia paper is '
   'paywalled.']),
 ('literature',
  111,
  ['Rugg 2004 (grille)',
   'No (Cryptologia, paywalled)',
   'HAVE as a producer (`results_n6_rugg_grille`, s71)']),
 ('literature',
  112,
  ['Bowern & Lindemann 2021',
   'Yes (Yale PDF, corpora CSVs)',
   'PARTIAL. The statistics CSVs are on disk, but O-031 says they were never put on the board. No '
   '`results_*` cites them.']),
 ('literature', 113, ['Davis 2020', 'No (MUSE open access)', 'PARTIAL ($H used; criteria not read)']),
 ('literature',
  114,
  ['Zandbergen voynich.nu (history, quire, illustration pages)',
   'No (only IVTFF files and README)',
   'PARTIAL. Prose notes cite descr.html, carbon.html and sp_origin.html. The per-quire pages and '
   'illustration-section pages are not saved or tabulated.']),
 ('literature',
  115,
  ['Ponzi',
   'No',
   'PARTIAL. Ponzi 2019 on line ends was extended by s35 Part 2 (TEAM-HANDOFF line 84). No Ponzi text is on '
   'disk.']),
 ('literature',
  116,
  ['HistoCrypt and the VOY 2022 papers',
   '3 of 16 CEUR 3313 papers on disk (4, 6, 10)',
   'Missing: Farrugia, Layfield & van der Plas (scribes), Caruana et al. (word relations), Lindemann '
   '(MATTR), Painter & Bowern (glyph phylogeny), Feaster (rightward/downward grapheme distributions), '
   'Stafford (paragraph habits), Boxer (Sloane 3188), Katz and Guzy (ownership), Schmeh & Dunin, and the '
   'Zandbergen and Davis keynotes. All CC BY 4.0 at https://ceur-ws.org/Vol-3313/. HistoCrypt Megyesi keys '
   'papers: recorded.']),
 ('literature',
  117,
  ['Voynich Ninja statistics threads',
   '1 thread (5081, Naibbe)',
   'MISSING. Guests cannot see links (O-033, human decision).']),
 ('literature',
  118,
  ['Schwartz 2026, Rozanova-Temerev 2026, Parisel, Steckley, Zattera, Greshko',
   'Yes (the Greshko paper text is not)',
   'HAVE: tested extensively'])]


# ----------------------------------------------------------------------------------------------- build
def build(conn):
    CORPORA.clear(); STATS.clear(); KIND_HINT.clear(); _cache.clear()
    corpora_manifest(); corpora_genre(); corpora_original_controls(); corpora_realline(); corpora_gibberish()
    corpora_period(); corpora_tabular(); corpora_herbals(); corpora_voynich(); corpora_roach(); corpora_scripts()
    corpora_synthetic_dir()
    parse_lead(); parse_r7(); parse_r11(); parse_r12(); parse_explore(); parse_manifest_h2()
    # every corpus with a statistic gets a corpora row; undocumented ones from the results' own corpus list
    for s in STATS:
        cid = s["corpus_id"]
        if cid not in CORPORA:
            hint = KIND_HINT.get(cid)
            if hint:
                lab, desc, tok, src, run = hint
                k = ("gibberish" if lab.startswith("H_") else "synthetic" if lab.startswith(("G_", "PC1"))
                     else "constructed" if lab.startswith("C_") else "natural" if lab.startswith(("R_", "T_", "N_")) else None)
                add_corpus(cid, src, name=desc, kind=k, tokens=tok if "pool" in lab else None,
                           note=f"described only by the {run} corpus list (tokens there are the run's cut)")
            else:
                add_corpus(cid, s["src"], name=s["label"], note="described only by the results row")
        CORPORA[cid]["used_in"].add(s["run_id"])
    for cid in ("voynich-ZL3b", "voynich-RF1b", "voynich-IT2a"):
        CORPORA[cid]["used_in"].update(r for r, _ in LEAD_FILES)

    create(conn, "corpora", ["corpus_id TEXT PRIMARY KEY", "name TEXT", "kind TEXT", "language TEXT", "genre TEXT", "period TEXT",
                             "tokens INTEGER", "path TEXT", "licence TEXT", "url TEXT", "used_in TEXT", "note TEXT"])
    insert(conn, "corpora", [{**r, "used_in": ",".join(sorted(r["used_in"])) or None} for r in CORPORA.values()])
    create(conn, "corpus_stats", ["corpus_id TEXT", "statistic TEXT", "value REAL", "run_id TEXT", "claim_id TEXT", "p REAL",
                                  "ci_lo REAL", "ci_hi REAL", "n_tokens INTEGER", "segmenter TEXT", "pipeline TEXT", "label TEXT",
                                  "scope TEXT", "note TEXT"])
    insert(conn, "corpus_stats", STATS)

    gap_lines = None
    if os.path.exists(GAP_MD):
        with open(GAP_MD, encoding="utf-8", errors="replace") as f:
            gap_lines = f.read().split("\n")
    src_rows = sources_rows(gap_lines) + sources_fake_and_data()
    seen = set()
    for r in src_rows:
        while r["source_id"] in seen:
            r["source_id"] += "-2"
        seen.add(r["source_id"])
    create(conn, "sources", ["source_id TEXT PRIMARY KEY", "kind TEXT", "title TEXT", "url TEXT", "licence TEXT", "local_path TEXT",
                             "have TEXT", "gap_note TEXT", "questions TEXT"])
    insert(conn, "sources", src_rows)

    global EXTRA_ITEMS
    EXTRA_ITEMS = _intake_from_files()
    have_intake = os.path.exists(INTAKE_MD)
    ext_rows = []
    for path, loc, kind, owner, filed, note, ln in EXT:
        cls, csrc = "unaudited", None
        if have_intake and path in INTAKE:
            cls, iln, wording = INTAKE[path]
            csrc = f"{INTAKE_MD}:{iln}"
            note = f"{note}; intake: {wording}"
        elif path in EXTERNAL_CLASSES:
            cls, iln, wording, afp = EXTERNAL_CLASSES[path]
            csrc = f"{afp}:{iln}"
            note = f"{note}; intake: {wording}"
        ext_rows.append(dict(path=path, location=loc, kind=kind, owner=owner, intake_class=cls, filed_as=filed, note=note,
                             src=f"{SPRAWL_MD}:{ln}" + (f"; {csrc}" if csrc else "")))
    create(conn, "external_items", ["path TEXT PRIMARY KEY", "location TEXT", "kind TEXT", "owner TEXT", "intake_class TEXT",
                                    "filed_as TEXT", "note TEXT"])
    team = team_files()
    create(conn, "team_files", ["location TEXT", "name TEXT", "kind TEXT", "voynich INTEGER", "size INTEGER", "mtime TEXT",
                                "owner TEXT", "status TEXT", "sha256 TEXT", "lead_id TEXT"])
    insert(conn, "team_files", team)
    have_paths = {r["path"] for r in ext_rows}
    ext_rows += [r for r in EXTRA_ITEMS if r["path"] not in have_paths]
    insert(conn, "external_items", ext_rows)
    pf = page_facts()
    create(conn, "page_facts", ["folio TEXT", "attribute TEXT", "value TEXT", "source TEXT", "url TEXT", "quote TEXT",
                                "fetched TEXT", "pull TEXT"])
    insert(conn, "page_facts", pf)
    conn.commit()
    return dict(corpora=len(CORPORA), corpus_stats=len(STATS), sources=len(src_rows), external_items=len(ext_rows),
                page_facts=len(pf))


PAGE_FACTS = os.path.join(ROOT, "data", "external", "page-facts")


def page_facts():
    """Published per-page facts (D-066 dd): data/external/page-facts/<pull>/facts.tsv, one fact per row, quoted."""
    import csv
    rows = []
    for f in sorted(glob.glob(os.path.join(PAGE_FACTS, "*", "facts.tsv"))):
        pull = os.path.basename(os.path.dirname(f))
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        with open(f, encoding="utf-8", newline="") as fh:
            for i, r in enumerate(csv.DictReader(fh, delimiter="	", quoting=csv.QUOTE_NONE), start=2):
                rows.append(dict(folio=r["folio"], attribute=r["attribute"], value=r["value"], source=r["source"],
                                 url=r["url"], quote=r["quote"], fetched=r["fetched"], pull=pull, src=f"{rel}:{i}"))
    return rows


# ----------------------------------------------------------------------------------------------- self-test
def _rank_report(conn):
    q = conn.execute
    print("\n== statistics by corpora covered ==")
    for st, n, k in q("SELECT statistic, COUNT(DISTINCT corpus_id), COUNT(*) FROM corpus_stats GROUP BY statistic ORDER BY 2 DESC"):
        print(f"  {st:16s} corpora {n:4d}  rows {k}")
    print("\n== by (statistic, pipeline, segmenter) ==")
    for row in q("SELECT statistic, pipeline, segmenter, COUNT(DISTINCT corpus_id) FROM corpus_stats GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 14"):
        print("  ", row)

    def rank(statistic, pipeline, segmenter, scope_like="%", natural_only=False, title="", min_tok=0):
        sql = ("SELECT s.corpus_id, AVG(s.value), COUNT(*), c.kind FROM corpus_stats s LEFT JOIN corpora c USING(corpus_id) "
               "WHERE statistic=? AND pipeline=? AND segmenter=? AND scope LIKE ? AND (s.note IS NULL OR s.note NOT LIKE '%control path%') "
               "AND COALESCE(s.n_tokens, 1000000000) >= ? GROUP BY s.corpus_id")
        rows = q(sql, (statistic, pipeline, segmenter, scope_like, min_tok)).fetchall()
        title += f" (n_tokens >= {min_tok})" if min_tok else ""
        if natural_only:
            rows = [r for r in rows if r[3] in ("natural", "voynich")]
        rows.sort(key=lambda r: -r[1])
        print(f"\n-- {title}: {statistic} [{pipeline}, {segmenter}] {len(rows)} corpora{' (natural + Voynich only)' if natural_only else ''}")
        for i, r in enumerate(rows, 1):
            if r[0].startswith("voynich") or i <= 3:
                print(f"   rank {i:3d}/{len(rows)}  {r[0]:34s} {r[1]:+.4f}  (rows {r[2]}, kind {r[3]})")

    rank("Rw1", "lead-S87.c1", "slot", title="Rw1, SlotSegmenter cores on every text")
    rank("Rw1", "lead-S87.c1", "slot", title="Rw1, SlotSegmenter cores on every text", min_tok=22500)
    rank("Rw1", "lead-S87.c1", "slot", natural_only=True, title="Rw1, SlotSegmenter cores on every text", min_tok=22500)
    rank("Rw1", "lead-S87.c1", "word", natural_only=True, title="Rw1, whole words (Voynich word rows: s104 /identity)", min_tok=22500)
    rank("Rw1", "roach-r11", "word", title="Rw1, roach r11 S0 block medians")
    rank("rhythm_excess", "lead-S87.c1", "word-length", title="rhythm, lead Moran I excess (s102/s104)")
    rank("rhythm_excess", "lead-S87.c1", "word-length", natural_only=True, title="rhythm, lead Moran I excess (s102/s104)")
    rank("rhythm_excess", "roach-r12", "word-length", "L1_POOLED%", title="rhythm, roach r12 L1_POOLED")
    rank("rhythm_excess", "roach-r12", "word-length", "L1_POOLED%", natural_only=True, title="rhythm, roach r12 L1_POOLED")
    rank("rhythm_excess", "explore-wordlen", "word-length", "per-line%", title="rhythm, explore per-line")


if __name__ == "__main__":
    import sqlite3
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "vkb", "test_world.sqlite")
    assert not out.endswith("vkb.sqlite"), "self-test never writes vkb.sqlite"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        os.remove(out)
    conn = sqlite3.connect(out)
    print(build(conn))
    for t in ("corpora", "corpus_stats", "sources", "external_items"):
        n_nosrc = conn.execute(f"SELECT COUNT(*) FROM {t} WHERE src IS NULL OR src=''").fetchone()[0]
        print(f"  {t}: {conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows, {n_nosrc} without src")
    print("  sources.have:", conn.execute("SELECT have, COUNT(*) FROM sources GROUP BY have").fetchall())
    print("  corpora.kind:", conn.execute("SELECT kind, COUNT(*) FROM corpora GROUP BY kind").fetchall())
    print("  external intake:", conn.execute("SELECT intake_class, COUNT(*) FROM external_items GROUP BY 1").fetchall())
    _rank_report(conn)
    conn.close()


SQUIRE = os.environ.get("VKB_SQUIRE", "<team-comms>")
_VOY = re.compile(r"voynich|egerton|fontana|ventura|vkb|daybreak|db-s\d|yonich|msi|herbal|zandbergen|stolfi|roach-r\d|s1\d\d", re.I)


_OWNERS = [("voynich-lead", "lead"), ("daybreak", "Daybreak"), ("grok", "Grok Bot"), ("roach-12b", "roach-12B"),
           ("roach", "roach"), ("argon", "Argon"), ("sylvie", "Sylvie"), ("independent-verifier", "Independent Verifier"),
           ("iv-", "Independent Verifier"), ("muse", "Muse"), ("eve", "Eve / Voynich Analyst"), ("codex", "Codex"),
           ("voynich-expert", "Voynich Expert")]


def _squire_owner(low):
    """Best-effort owner from a <team-comms> file name (sender token, else any team token); None when no token matches."""
    m = re.match(r"ssr-comms-([a-z0-9-]+?)-(?:to|request|b379)-", low)
    head = m.group(1) if m else low
    for tok, who in _OWNERS:
        if tok in head:
            return who
    return None


def team_files():
    """Phase 8.2: read-only index of team work outside the repo (<team-comms> top level, scanned at build time;
    codex_lab/yonichmanuscript from data/external/intake/codex_lab_index.tsv when Codex delivers it).
    Never moves or edits anything; the repo only records what exists."""
    import csv, time as _t
    rows = []
    if os.path.isdir(SQUIRE):
        for name in sorted(os.listdir(SQUIRE)):
            fp = os.path.join(SQUIRE, name)
            if not os.path.isfile(fp) or name.startswith("."):
                continue
            low = name.lower()
            kind = ("comms" if low.startswith("ssr-comms") or "-roach-" in low or "-skynet-" in low else
                    "package" if low.endswith(".zip") else "stub" if "prereg" in low else
                    "result" if low.startswith("results") or "result" in low else "doc" if low.endswith(".md") else "file")
            st = os.stat(fp)
            rows.append(dict(location="<team-comms>", name=name, kind=kind, voynich=int(bool(_VOY.search(name))), size=st.st_size,
                             mtime=_t.strftime("%Y-%m-%d %H:%M", _t.localtime(st.st_mtime)), owner=_squire_owner(low), status=None,
                             sha256=None, lead_id=None, src=f"scan of {SQUIRE} at build"))
    f = os.path.join(INTAKE_DIR, "codex_lab_index.tsv")
    if os.path.exists(f):
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        with open(f, encoding="utf-8", newline="") as fh:
            for i, r in enumerate(csv.DictReader(fh, delimiter="	", quoting=csv.QUOTE_NONE), start=2):
                rows.append(dict(location=r.get("location") or "codex_lab", name=r.get("path") or r.get("name"), kind=r.get("kind"),
                                 voynich=1, size=int(r["size"]) if (r.get("size") or "").isdigit() else None, mtime=r.get("mtime"),
                                 owner=r.get("owner"), status=r.get("status"), sha256=r.get("sha256"), lead_id=r.get("lead_id"),
                                 src=f"{rel}:{i}"))
    return rows
