"""Synthetic nomenclator control: a Latin herbal encoded with a 15th-century-style three-slot
code (prefix class + core + suffix class) into a Voynich-like 20-symbol alphabet.

Plaintext: data/controls/latin_macer_floridus.txt (Odo of Meung, 11th c.) followed by
data/controls/latin_pliny_herbal.txt (Pliny NH XX-XXVII, the plant-remedy books), cut to
N_TOKENS tokens; section labels follow the plaintext chapter / book boundaries.

Variants (data/controls_synthetic/):
  nomen_word   word-level code: each distinct plaintext word -> fixed codeword prefix+core+suffix
  nomen_syll   syllable-level code: each distinct syllable -> fixed 2-3 symbol unit; concatenated per word
  nomen_lines  nomen_word plus Voynich-like layout: lines of 6-10 words, pages of 10-25 lines,
               line-initial marker glyph 'p' (prob 0.20), line-final suffix 'm' (prob 0.15)
Each has a sidecar <name>.meta.json: {"pages": [{"page", "section", "lines": [[tok,...],...]}]}.

Run:  python ctl_nomenclator.py   (writes results_ctl_nomenclator.txt)
"""
import json
import math
import random
import re
from collections import Counter
from itertools import product
from pathlib import Path

import numpy as np

import corpora
import corpora_ext
from a1_profile import char_entropies

SEED = 20261017
N_TOKENS = 35000
ROOT = Path(__file__).parent
OUT = ROOT / "data" / "controls_synthetic"
OUT.mkdir(parents=True, exist_ok=True)

# 20-symbol made-up alphabet written as ASCII letters; 'p' and 'm' are reserved for the
# line-edge markers of nomen_lines and never occur inside ordinary codewords.
ALPHABET = list("acdefghiklnoqrstxy") + ["p", "m"]
CORE_SYMS = list("acdefghiklnoqrstxy")
VOW = "aeioy"
CON = "cdfghklnqrstx"

# ------------------------------------------------------------------ plaintext
def plaintext():
    """List of (section, line_tokens) from the Latin herbal, up to N_TOKENS tokens."""
    out, n = [], 0
    for name in ["latin_macer_floridus", "latin_pliny_herbal"]:
        lines, secs = corpora_ext.control_ext_lines(name, with_sections=True)
        for toks, sec in zip(lines, secs):
            label = f"{name.split('_')[1]}:{sec}"
            # Pliny paragraphs are long; chop to verse-like lines of <=12 words
            for i in range(0, len(toks), 12):
                chunk = toks[i:i + 12]
                out.append((label, chunk))
                n += len(chunk)
                if n >= N_TOKENS:
                    return out
    return out


# ------------------------------------------------------------------ word classes
def word_class(w, rank):
    """Prefix class: frequency class for the top words, otherwise a crude Latin ending class
    (stands in for the grammatical classes a period nomenclator would group by)."""
    if rank < 50:
        return 0
    if rank < 300:
        return 1
    if re.search(r"(us|um|os|o)$", w):
        return 2       # 2nd declension nouns / adjectives
    if re.search(r"(a|ae|am|as)$", w):
        return 3       # 1st declension
    if re.search(r"(is|es|em|ibus|ium|e)$", w):
        return 4       # 3rd declension
    if re.search(r"(tur|ntur|ri|re)$", w):
        return 5       # passive / infinitive verb forms
    if re.search(r"(nt|unt|ant|ent)$", w):
        return 6       # 3rd plural verbs
    if re.search(r"(t|at|et|it)$", w):
        return 7       # 3rd singular verbs
    if re.search(r"(i|is|orum|arum)$", w):
        return 8       # genitives / plurals
    if re.search(r"(que|ve|ne)$", w):
        return 9       # enclitics
    if len(w) <= 3:
        return 10      # short particles
    return 11


PREFIXES = ["", "o", "qo", "d", "s", "ch", "y", "ol", "ok", "ot", "ko", "da"]   # one per class
SUFFIXES = ["", "y", "n", "dy", "in", "ar", "ey", "al", "r", "ain"]              # 10 suffix classes


def make_cores(rng, n=150):
    """~150 cores of 2-3 symbols, CV / CVC / VC / VCV shapes over the 18 core symbols."""
    shapes = [(CON, VOW), (CON, VOW, CON), (VOW, CON), (VOW, CON, VOW), (CON, CON, VOW)]
    pool = set()
    for sh in shapes:
        for combo in product(*sh):
            pool.add("".join(combo))
    pool = sorted(pool)
    rng.shuffle(pool)
    return pool[:n]


def build_word_code(types_by_freq, rng):
    """Deterministic one-to-one mapping plaintext word -> prefix+core+suffix."""
    cores = make_cores(rng)
    # per class, a fixed (seeded) order over the core x suffix inventory
    # if a class needs more than 150 x 10 entries, a one-symbol tag series (like a codebook's
    # supplementary table) is opened; untagged cells are always used first
    inv = {}
    for c in range(len(PREFIXES)):
        cells = []
        for tag in ["", "s", "l", "d", "k"]:
            block = list(product(range(len(cores)), range(len(SUFFIXES)), [tag]))
            rng.shuffle(block)
            cells.extend(block)
        inv[c] = cells
    # the top-50 words get the shortest codes: 2-symbol cores and empty suffix, like a
    # nomenclator's one-sign entries for common words
    short_cores = [c for c in cores if len(c) == 2]
    used = set()
    code = {}
    ptr = {c: 0 for c in inv}
    for rank, w in enumerate(types_by_freq):
        cls = word_class(w, rank)
        if rank < 50 and rank < len(short_cores):
            cw = PREFIXES[cls] + short_cores[rank]
        else:
            while True:
                ci, si, tag = inv[cls][ptr[cls]]
                ptr[cls] += 1
                cw = PREFIXES[cls] + cores[ci] + SUFFIXES[si] + tag
                if cw not in used:
                    break
        used.add(cw)
        code[w] = cw
    return code, cores


# ------------------------------------------------------------------ syllables
def syllabify(w):
    """Simple Latin syllabifier: a syllable is onset consonants + vowel group + (coda if the
    following cluster has 2+ consonants or it is word-final)."""
    v = set("aeiouy")
    syls, i, n = [], 0, len(w)
    while i < n:
        j = i
        while j < n and w[j] not in v:
            j += 1
        while j < n and w[j] in v:
            j += 1
        # j is at the first consonant after the vowel group
        k = j
        while k < n and w[k] not in v:
            k += 1
        if k == n:            # word-final cluster belongs to this syllable
            j = n
        elif k - j >= 2:      # split a cluster: first consonant stays
            j = j + 1
        syls.append(w[i:j])
        i = j
    return [s for s in syls if s]


def make_units(rng):
    shapes = [(CON, VOW), (VOW, CON), (CON, VOW, CON), (CON, CON, VOW), (VOW, CON, VOW), (CON, VOW, VOW)]
    pool = set()
    for sh in shapes:
        for combo in product(*sh):
            pool.add("".join(combo))
    pool = sorted(pool)
    rng.shuffle(pool)
    pool.sort(key=len)        # short units first -> frequent syllables get short units
    return pool


# ------------------------------------------------------------------ layout helpers
def pages_from_lines(lines, secs, per_page=20):
    pages = []
    for i in range(0, len(lines), per_page):
        pages.append(dict(page=len(pages) + 1, section=secs[i], lines=lines[i:i + per_page]))
    return pages


def write_variant(name, pages, note):
    toks = [w for p in pages for l in p["lines"] for w in l]
    text = "\n".join(" ".join(l) for p in pages for l in p["lines"]) + "\n"
    (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
    (OUT / f"{name}.meta.json").write_text(json.dumps(dict(name=name, seed=SEED, note=note, pages=pages),
                                                      ensure_ascii=False), encoding="utf-8")
    return toks


def stats(words):
    c = Counter(words)
    lens = [len(w) for w in words]
    ce = char_entropies(words)
    redup = sum(a == b for a, b in zip(words, words[1:])) / (len(words) - 1) * 100
    return dict(types=len(c), tokens=len(words), mean_len=float(np.mean(lens)), sd_len=float(np.std(lens)),
                h1=ce["h1"], h2=ce["h2"], alpha=ce["alpha"], redup=redup,
                hapax=sum(v == 1 for v in c.values()) / len(c))


# ------------------------------------------------------------------ main
def main():
    rng = random.Random(SEED)
    pt = plaintext()
    pt_words = [w for _, l in pt for w in l]
    freq = Counter(pt_words)
    types_by_freq = [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    secs = [s for s, _ in pt]
    plain_lines = [l for _, l in pt]

    rows = []
    rows.append(("plaintext (Macer+Pliny)", stats(pt_words)))

    # 1. word-level
    code, cores = build_word_code(types_by_freq, rng)
    assert len(set(code.values())) == len(code), "code not one-to-one"
    enc_lines = [[code[w] for w in l] for l in plain_lines]
    pages = pages_from_lines(enc_lines, secs)
    toks = write_variant("nomen_word", pages,
                         "word-level nomenclator: prefix class (12) + core (150) + suffix class (10); "
                         "one-to-one, top-50 words get 2-symbol cores; lines = plaintext lines, 20 lines/page")
    rows.append(("nomen_word", stats(toks)))
    (OUT / "nomen_word.key.json").write_text(json.dumps(dict(prefixes=PREFIXES, suffixes=SUFFIXES, cores=cores,
                                                             code=code), ensure_ascii=False), encoding="utf-8")

    # 2. syllable-level
    rng2 = random.Random(SEED + 1)
    units = make_units(rng2)
    syl_freq = Counter(s for w in pt_words for s in syllabify(w))
    syl_by_freq = [s for s, _ in sorted(syl_freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    assert len(syl_by_freq) <= len(units), (len(syl_by_freq), len(units))
    syl_code = {s: units[i] for i, s in enumerate(syl_by_freq)}
    enc_lines = [["".join(syl_code[s] for s in syllabify(w)) for w in l] for l in plain_lines]
    pages = pages_from_lines(enc_lines, secs)
    toks = write_variant("nomen_syll", pages,
                         f"syllable-level code: {len(syl_by_freq)} distinct syllables -> fixed 2-3 symbol units, "
                         "concatenated per word; lines = plaintext lines, 20 lines/page")
    rows.append(("nomen_syll", stats(toks)))
    (OUT / "nomen_syll.key.json").write_text(json.dumps(syl_code, ensure_ascii=False), encoding="utf-8")

    # 3. word-level + line layout + edge markers
    rng3 = random.Random(SEED + 2)
    stream = [(s, code[w]) for s, l in pt for w in l]
    pages, i, pno = [], 0, 0
    while i < len(stream):
        n_lines = rng3.randint(10, 25)
        lines, sec = [], stream[i][0]
        for _ in range(n_lines):
            if i >= len(stream):
                break
            n = rng3.randint(6, 10)
            line = [cw for _, cw in stream[i:i + n]]
            i += n
            if rng3.random() < 0.20:
                line[0] = "p" + line[0]
            if rng3.random() < 0.15:
                line[-1] = line[-1] + "m"
            lines.append(line)
        pno += 1
        pages.append(dict(page=pno, section=sec, lines=lines))
    toks = write_variant("nomen_lines", pages,
                         "nomen_word code with layout: 6-10 words/line, 10-25 lines/page, line-initial 'p' "
                         "marker p=0.20, line-final 'm' suffix p=0.15")
    rows.append(("nomen_lines", stats(toks)))

    # reference: Voynich itself, same statistics, same 35k cut
    rows.append(("Voynich EVA (first 35k)", stats(corpora.voynich()[:N_TOKENS])))

    cols = ["tokens", "types", "hapax", "mean_len", "sd_len", "alpha", "h1", "h2", "redup"]
    lines_out = [f"ctl_nomenclator.py  seed={SEED}  N_TOKENS={N_TOKENS}",
                 "h2 = char conditional entropy with space as a symbol (a1_profile.char_entropies); "
                 "redup = immediate word repeats (%)", ""]
    lines_out.append(f"{'variant':26}" + "".join(f"{c:>10}" for c in cols))
    for name, st in rows:
        lines_out.append(f"{name:26}" + "".join(
            f"{st[c]:>10.3f}" if isinstance(st[c], float) else f"{st[c]:>10}" for c in cols))
    lines_out.append("")
    lines_out.append(f"plaintext sections: {len(set(secs))}; code classes: {Counter(word_class(w, r) for r, w in enumerate(types_by_freq))}")
    lines_out.append(f"word code: {len(code)} types -> {len(set(code.values()))} codewords (one-to-one)")
    lines_out.append(f"syllable code: {len(syl_by_freq)} syllables; unit length distribution "
                     f"{Counter(len(u) for u in syl_code.values())}")
    text = "\n".join(lines_out) + "\n"
    (ROOT / "results_ctl_nomenclator.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
