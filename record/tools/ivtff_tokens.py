"""Minimal IVTFF tokeniser. Usage: python -I ivtff_tokens.py FILE [FILE...]
Rules: '#' lines are comments; text lines start with <fNN.loc,@Tn> locus tag;
page header lines '<fNN>' carry no text. In the text: '<...>' inline tags are
removed (e.g. <->, <%>, <$>); '{...}' ligature/comment braces are removed but their
contents kept unless the content starts with '@' or '!' (IVTFF 2.0 comments);
'[a:b]' alternatives take the first option; '.' ',' are word breaks; '-' '=' line
breaks; '?' '!' '*' uncertain-glyph markers are dropped; '@nnn;' codes are kept as
one glyph '@'.  Emits per file: pages, loci, tokens, types, and top-10 types."""
import sys, re, collections

TAG = re.compile(r"<[^>]*>")
ALT = re.compile(r"\[([^\]:]*):[^\]]*\]")
BRACE = re.compile(r"\{([^}]*)\}")
NUMCODE = re.compile(r"@\d+;")

def clean(text):
    text = ALT.sub(r"\1", text)
    text = BRACE.sub(lambda m: "" if m.group(1)[:1] in "@!" else m.group(1), text)
    text = TAG.sub("", text)
    text = NUMCODE.sub("@", text)
    text = text.replace("!", "").replace("*", "").replace("%", "")
    text = re.sub(r"[-=]", ".", text)
    return [w for w in re.split(r"[.,\s]+", text) if w and w != "?" and not set(w) <= set("?")]

def parse(path):
    pages, loci, toks = set(), 0, []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            m = re.match(r"<(f[^.>,]+)(?:\.([^,>]+))?(?:,([^>]*))?>\s*(.*)", line)
            if not m:
                continue
            page, loc, body = m.group(1), m.group(2), m.group(4)
            pages.add(page)
            if loc is None:
                continue  # page header
            loci += 1
            toks.extend(clean(body))
    return pages, loci, toks

if __name__ == "__main__":
    for p in sys.argv[1:]:
        pages, loci, toks = parse(p)
        c = collections.Counter(toks)
        print(f"{p}: pages={len(pages)} loci={loci} tokens={len(toks)} types={len(c)} "
              f"top10={c.most_common(10)}")
