"""Per-locus disagreement among the local transliterations.

Rules, fixed in this file before the first run:
  A locus id is page + locator. The locator is the text after the first dot and
  before a comma, semicolon, or '>'. The LSI transcriber is the letter after ';'.
  Second-choice codes D, G, I, Q, M are excluded. They are alternate readings of
  another transcriber's line, not a further witness.
  Tokens use the same cleaner as tools/ivtff_tokens.py. '!' '?' '*' are dropped,
  so an uncertain glyph does not by itself make two lines disagree.
  A (locus, reader) with two lines is dropped from every rate.
  LSI readers are the witnesses. IT2a is compared with LSI H as a conversion
  check, because its header says it was extracted from LSI. RF1b-er (basic EVA)
  is compared with LSI H. GC2a is v101, so only word counts are compared.
  Agreement is whole-locus token identity. It is not a word-aligned rate.
  Nothing here is the frozen profile (c-002 h2 2.109; c-126 2.11 / 7,025 / 0.68).

Usage (project root): python -I tools/locus_disagreement.py
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IV = ROOT / "data" / "external" / "voynich-nu-ivtff"
OUT = ROOT / "data" / "translit" / "locus-disagreement"
SECOND = set("DGIMQ")  # D G I Q M: second choice of another transcriber's line

LINE = re.compile(
    r"^<(f[^.\s>]+)\.([^,>;]+)(?:,([^>;]*))?(?:;([A-Z]))?>\s*(.*)$"
)
ALT = re.compile(r"\[([^\]:]*):[^\]]*\]")
BRACE = re.compile(r"\{([^}]*)\}")
TAG = re.compile(r"<[^>]*>")
NUMCODE = re.compile(r"@\d+;")


def clean(text):
    text = ALT.sub(r"\1", text)
    text = BRACE.sub(lambda m: "" if m.group(1)[:1] in "@!" else m.group(1), text)
    text = TAG.sub("", text)
    text = NUMCODE.sub("@", text)
    text = text.replace("!", "").replace("*", "").replace("%", "")
    text = re.sub(r"[-=]", ".", text)
    return tuple(w for w in re.split(r"[.,\s]+", text) if w and w != "?" and not set(w) <= set("?"))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse(path):
    """locus -> list of (transcriber or '', tokens)."""
    out = defaultdict(list)
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("<"):
                continue
            m = LINE.match(line.rstrip("\n"))
            if not m:
                continue
            page, loc, _props, trans, body = m.groups()
            out[page + "." + loc].append((trans or "", clean(body or "")))
    return out


def singles(rows, allowed=None):
    """Return {reader: tokens} when that reader has exactly one line. Count dupes."""
    by = defaultdict(list)
    for trans, toks in rows:
        if allowed is not None and trans not in allowed:
            continue
        by[trans].append(toks)
    good, dup = {}, []
    for trans, group in by.items():
        if len(group) == 1:
            good[trans] = group[0]
        else:
            dup.append(trans)
    return good, dup


def rate(pairs):
    n = len(pairs)
    if n == 0:
        return 0, 0, 0.0, 0.0
    tok = sum(a == b for a, b in pairs)
    wc = sum(len(a) == len(b) for a, b in pairs)
    return n, tok, tok / n, wc / n


def main():
    lsi_path = IV / "LSI_ivtff_0d.txt"
    it_path = IV / "IT2a-n.txt"
    rf_path = IV / "RF1b-er.txt"
    gc_path = IV / "GC2a-n.txt"
    lsi = parse(lsi_path)
    it = parse(it_path)
    rf = parse(rf_path)
    gc = parse(gc_path)

    readers = Counter()
    dup_loci = 0
    comparable = 0
    all_tok = 0
    wc_differ = 0
    pair_bucket = defaultdict(list)
    it_vs_h = []
    rf_vs_h = []
    gc_vs_it = []  # (gc_n, it_n) word counts
    locus_rows = []

    for locus, rows in lsi.items():
        good, dup = singles(rows, allowed=None)
        primary = {t: toks for t, toks in good.items() if t and t not in SECOND}
        if dup:
            dup_loci += 1
        for t in primary:
            readers[t] += 1
        if len(primary) >= 2:
            comparable += 1
            vals = list(primary.values())
            same = all(v == vals[0] for v in vals[1:])
            counts = {len(v) for v in vals}
            if same:
                all_tok += 1
            if len(counts) > 1:
                wc_differ += 1
            names = sorted(primary)
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    pair_bucket[(a, b)].append((primary[a], primary[b]))
        it_g, _ = singles(it.get(locus, []))
        rf_g, _ = singles(rf.get(locus, []))
        gc_g, _ = singles(gc.get(locus, []))
        it_tok = it_g.get("")
        rf_tok = rf_g.get("")
        gc_tok = gc_g.get("")
        h = primary.get("H")
        if h is not None and it_tok is not None:
            it_vs_h.append((h, it_tok))
        if h is not None and rf_tok is not None:
            rf_vs_h.append((h, rf_tok))
        if it_tok is not None and gc_tok is not None:
            gc_vs_it.append((len(gc_tok), len(it_tok)))
        if primary or it_tok is not None:
            locus_rows.append((
                locus,
                "".join(sorted(primary)),
                len(primary),
                len({len(v) for v in primary.values()}) if primary else 0,
                int(len(primary) >= 2 and all(v == next(iter(primary.values())) for v in primary.values())),
                len(h) if h is not None else "",
                len(it_tok) if it_tok is not None else "",
                len(rf_tok) if rf_tok is not None else "",
                len(gc_tok) if gc_tok is not None else "",
            ))

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "loci.tsv").open("w", encoding="utf-8", newline="\n") as f:
        f.write("locus\tlsi_readers\tn_lsi\tn_distinct_wordcounts\tall_lsi_tokens_agree\tn_H\tn_IT2a\tn_RF1b\tn_GC2a\n")
        for row in locus_rows:
            f.write("\t".join(str(x) for x in row) + "\n")

    pair_lines = []
    for (a, b), pairs in sorted(pair_bucket.items(), key=lambda kv: -len(kv[1])):
        n, tok, tr, wr = rate(pairs)
        pair_lines.append(f"{a}-{b}\t{n}\t{tok}\t{tr:.4f}\t{wr:.4f}")
    (OUT / "pairs.tsv").write_text(
        "pair\tn\ttoken_agree\ttoken_agree_rate\twordcount_agree_rate\n" + "\n".join(pair_lines) + "\n",
        encoding="utf-8",
    )

    def block(title, pairs, wordcount_only=False):
        n, tok, tr, wr = rate(pairs)
        if wordcount_only:
            same_n = sum(a == b for a, b in pairs)
            return f"{title}: n={n} wordcount_agree={same_n} rate={same_n / n if n else 0:.4f}"
        return f"{title}: n={n} token_agree={tok} rate={tr:.4f} wordcount_agree_rate={wr:.4f}"

    lines = [
        "per-locus disagreement. Whole-locus token identity after ivtff_tokens.clean.",
        "Not a word-aligned rate. Not h2, not the 7,025-type count, not hapax 0.68.",
        "Second-choice LSI codes excluded: D G I Q M.",
        f"LSI loci={len(lsi)} IT2a={len(it)} RF1b-er={len(rf)} GC2a={len(gc)}",
        f"loci with a duplicated reader line (that reader dropped)={dup_loci}",
        "LSI reader locus counts: " + " ".join(f"{k}:{readers[k]}" for k in sorted(readers)),
        f"comparable (>=2 primary LSI readers): {comparable}",
        f"all those readers identical tokens: {all_tok} rate={all_tok / comparable if comparable else 0:.4f}",
        f"word counts differ among them: {wc_differ} rate={wc_differ / comparable if comparable else 0:.4f}",
        block("IT2a vs LSI H", it_vs_h),
        block("RF1b-er vs LSI H", rf_vs_h),
        "GC2a vs IT2a word count: n={n} agree={k} rate={r:.4f}".format(
            n=len(gc_vs_it),
            k=sum(a == b for a, b in gc_vs_it),
            r=(sum(a == b for a, b in gc_vs_it) / len(gc_vs_it)) if gc_vs_it else 0),
        "H-F and H-C are in pairs.tsv. Whole-locus identity is stricter than a word-aligned rate.",
        "pair table: data/translit/locus-disagreement/pairs.tsv",
        "per locus: data/translit/locus-disagreement/loci.tsv",
        "sha256 LSI " + sha256(lsi_path),
        "sha256 IT2a " + sha256(it_path),
        "sha256 RF1b-er " + sha256(rf_path),
        "sha256 GC2a " + sha256(gc_path),
    ]
    text = "\n".join(lines) + "\n"
    (OUT / "SUMMARY.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
