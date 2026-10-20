# Quire 13 page colour annotations (external, read-only pull)

Fetched: Mon Oct 19 00:39 PDT 2026 (from `date`). Raw text only. Nothing here is joined to bifolio data, and no statistic has been computed.

## File

`q13_page_colours.tsv` is tab-separated with LF line endings and a header row: `folio, water_colours, other_colours, source_url, quote`.
- There are 40 rows: 20 pages (f75r-f84v) x 2 sources. The `source_url` column says which source a row comes from.
- `water_colours` holds only colours the source ties to water-type objects (pool, pond, flow, tube, pipe, liquid, water, channel, funnel, bucket, tub, spout) or to "all_water". Where the source names the object, the object is kept. Colours listed without an object go in `other_colours`, marked "no object".
- NA means the source says nothing on that point.
- `quote` holds the exact source text. Several excerpts are separated by ` | `, and `[...]` marks an elision.

## Sources

1. **Jorge Stolfi, page notes**, `https://www.ic.unicamp.br/~stolfi/voynich/Notes/040/data/<folio>` (the HTML twin is `.../html/<folio>.htm`). All 20 Q13 pages were fetched, each returning HTTP 200.
   - Each page has a `* Colors:` attribute line, credited to "(Reeds)" or "(Rene)". Some trailing entries carry no credit, on f80v and f83r. These are recorded as "unattributed".
   - Reeds' lists are mostly bare colour names with no objects. "b" probably means blue, but that is unverified, so it is kept as given.
   - Rene's entries name objects, such as `green(pools)` and `blue(all_water)`, but appear on only 11 of 20 pages.
   - Long prose colour descriptions exist only for f78r, f83v and f84r, all by Stolfi. The notes date from 1999-2000 and were made from Beinecke images. The f83v note itself warns that the Beinecke image colours are "severly distorted".
   - The notes do not say anything about painting order or bifolio pairing of colours. They do carry a `Bifolio:` field: bM1=f75+f84, bM2=f76+f83, bM3=f77+f82, bM4=f78+f81, bM5=f79+f80.
2. **René Zandbergen, quire 13 page**, `https://voynich.nu/q13/index.html`, one section per folio.
   - The sections are short prose. Water colour is given for 14 pages.
   - It is silent on f76r (text only), f76v, f77r, f77v and f83r. For f83v it mentions green only on globular structures.
   - On f75v it calls the bottom pool blue in one sentence and green in another. Both are recorded as given.
   - It says nothing about painting order or about colour shared by bifolio. It does note tubes that continue across the f78v/f81r bifolio.
3. **Voynich Ninja, thread "Colors"** (tid 1484), page 2, `https://www.voynich.ninja/thread-1484-page-2.html`. This is not in the TSV because it gives no per-page data.
   - Post #11 is by Searcher, 03-02-2017 10:46 PM (`thread-1484-post-11683.html#pid11683`). It claims "most of the plants pairs have the same colors and shades". That claim is about herbal bifolios, not Q13. On Q13 the same post claims the green pools reflect a lack of blue pigment and that blue was added later.
   - Post #12 is by Linda, 03-02-2017 11:20 PM. It claims blue and green in Q13 are intentional and mean fresh and salt water.
4. **Nick Pelling, Cipher Mysteries**, "Green Voynich pools? I really don't think so, sorry", 4 Mar 2011, `https://ciphermysteries.com/2011/03/04/green-voynich-pools-i-really-dont-think-so-sorry`. This is not in the TSV.
   - Pelling claims Q13 was first painted blue, with green added later on top of it and after the quire numbers.
   - He says f78v, f81r and f81v have green over blue, and that f78v and f81r were originally adjacent.
   - Zandbergen disputes this in the comments.
   - These quotes came through a WebFetch summariser and were not checked against the raw HTML, so they are unverified.

Not checked (unverified): Reeds' original colour list in its primary form, the Stolfi pages' HTML versions beyond f75v, and the other Pelling posts (`ciphermysteries.com/2009/06/18/q13-and-voynich-balneology-sources`, `?p=3646`).
