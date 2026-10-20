"""Strip tags from saved HTML files -> sibling .txt. Usage: python -I html2text.py FILE..."""
import re, sys, html
for fn in sys.argv[1:]:
    t = open(fn, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</tr>|</h\d>|</li>", "\n", t, flags=re.I)
    t = re.sub(r"</t[dh]>", "\t", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
    open(fn + ".txt", "w", encoding="utf-8").write(t)
    print(fn, len(t))
