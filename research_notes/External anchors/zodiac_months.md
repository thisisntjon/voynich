# Zodiac month names (f70v–f73v) as an external anchor

Stamped: `Sat Oct 17 20:02:38 PDT 2026` (output of `date`).
Scope: O-012, O-029. Read-only: web pages were read, nothing was downloaded, and no project files were changed except this note.
Quotes are a few words each. **Unverified** marks a claim I saw only second-hand, through a search summary or a forum relay, and not on the primary page.

## 1. What is written, the language, and the hand

**Readings.** These follow Zandbergen, https://www.voynich.nu/writing.html, section "Extraneous writing" (page read):

| page | sign | reading |
|---|---|---|
| f70v2 | Pisces | mars |
| f70v1, f71r | Aries (2 pages) | aberil |
| f71v, f72r1 | Taurus (2 pages) | may |
| f72r2 | Gemini | jong |
| f72r3 | Cancer | iollet |
| f72v3 | Leo | augst |
| f72v2 | Virgo | septe(m)b(r) |
| f72v1 | Libra | octe(m)bre |
| f73r | Scorpio | nove(m)bre |
| f73v | Sagittarius | decebre (his overview table says "decembre") |

Capricorn and Aquarius are lost, with the missing folio(s) after f73.

**Older readings in the local Stolfi crib files** (`data/external/cribs/voynich_nu_f07*_tr.txt`, opened):
- f70v1 is "ab**il".
- f70v2 is "mars", glossed as French.
- f72r2 is "Jony", after Robert Firth.
- f72v1 is "oct~ebre" with a tilde.
- f72v3 is "augst".
- f73v is "possibly oct", which conflicts with Zandbergen's "decebre". **Unverified**: I did not check it on the image.

Schwerdtfeger's list (mars, aberil, may, yony, jolliz?, augst … octembre, novembre, decebre) is reported by Bax at https://stephenbax.net/?p=1226. That page returned 403 to WebFetch, so I saw it only through a search summary: **unverified**.

**Language.**
- **Zandbergen**: "certainly a Romance language". Candidates have been Spanish, Occitan and French. He concludes Northern French, and calls "jong" the strongest evidence for that (https://www.voynich.nu/writing.html).
- **Pelling**: "some form of Occitan". He cites Stolfi's 1997 query, which found the closest match in 15th-century Toulon (Jaume Deydier's livre de raison, 1477–1521). The only month name Pelling could find quoted from that text is "Septembre" (https://ciphermysteries.com/2009/08/22/jaume-deydiers-livre-de-raison).
- **Bax**: the names look "a sort of French". He points to a 14th-century Picardy astrolabe that has "may" and "octembre" (https://stephenbax.net/?p=1226, **unverified**, 403).
- **Forum debate** (https://www.voynich.ninja/archive/index.php/thread-4745-6.html and https://www.voynich.ninja/archive/index.php/thread-4751-14.html): langue d'oïl versus langue d'oc; "aberil" and "iollet" are hard to match; Catalan "abril" is raised. All of this is from search summaries: **unverified**.
- **Judeo-Romance**: no source found.

**Davis.** A thread summary says the month names were "added" by early owners. I found no palaeographic statement from her about this hand (https://threadreaderapp.com/thread/1557092705485967360.html, **unverified**). Zandbergen's table puts f67–f73 in Davis's Hand 4, but that is the Voynich scribe, not the hand of the month names.

**Dating and hand.** Zandbergen says "written in a later hand", with no further identification (https://www.voynich.ninja/archive/index.php/thread-5299.html, thread dated 2026-01-26, opened). Views reported in that thread:
- **nablator**: the palaeographer Baptiste Etienne gave "15th c."
- **ReneZ**: Toresella also said 15th century, possibly several decades after the text.
- **Stolfi**: putting June on Gemini fits a calendar of about 1430 poorly, so the names were probably added by a later owner.
- **Stefan Wirtz_2**: the ink resembles the folio numbers, and the date may be nearer 1580.

The Stolfi crib file for f70v2 says the month name is in "slightly darker ink" than the labels.

**Consensus:** a later Romance-language hand, probably 15th century. That makes the names an owner's gloss, not the author's.

## 2. Do the 30 labels per sign track the calendar?

Zandbergen's label study (https://voynich.nu/extra/labels.html, opened) finds:
- 299 zodiac labels where 300 are expected.
- 238 of them (80 %) are hapax.
- The top types, "otaly" and "okal", occur 5 times each.
- 52 % start with ok- or ot-.
- He writes that the labels "may be … numbers or coordinates", but does not test this.

Other attempts:
- **Firth** conjectured star names, with ok-/ot- standing for Arabic al- (https://www.ic.unicamp.br/~stolfi/voynich/mirror/reeds/firth/07.txt, search summary, **unverified**). It was never tested.
- **Stolfi**: the star labels do not match the star-name lists he compared (https://ic.unicamp.br/~stolfi/voynich/Notes/040/data-sections/zod, search summary, **unverified**).
- **Bax's star readings** are on f68r, not on the zodiac pages: "doary" read as "taurn" near the Pleiades (local cribs `bax_stars_*`). They were never extended to the 300 nymph labels, and no follow-up on them was found.
- **"Seasonal prefix clustering"** by UrexEregerRep, 2026-06-14 (https://www.voynich.ninja/archive/index.php/thread-5817.html, opened). It reports ot-/ok- in the winter–spring pages, ol-/or-/oe- in summer–autumn, and y-/yk- on f73v. It has no null model; dashstofsk replied that page-to-page variation is ordinary.
- **ReneZ and Koen G**: the labels do not follow Zipf's law and are almost all unique (thread-5817 search summary, **unverified**).

**Result:** no published day-number or star-name reading has survived.

## 3. Has anyone matched a Voynich word to a month name?

None was found.
- In thread-5299, titled "Why the month names aren't Voynichese?", Zauriek only speculates that an equivalent "may be there somewhere".
- labels.html makes no such claim.
- Self-published "decodings" (e.g. https://zenodo.org/records/17794596) were not examined.

## 4. Local test

Script and output are in the scratchpad: `zodiac_month_test.py` and `zodiac_out.txt` (seed 20261017, 2,000 permutations).

**Data.**
- In ZL3b-n, zodiac pages use only units `Cc` (rings) and `Lz` (labels). There are no R* units, and the Latin month names are not transcribed.
- The 12 pages hold 1,316 tokens and 782 types.
- 630 of the types (81 %) occur in only one month. The two-page months count as one month.
- The full per-page block listing (rings and label bands in file order) is in `zodiac_out.txt`.

**Positions.** 47 structural slots were scored:
- first, second and last token of each ring and each label band, counted in file order from both ends;
- the first and last label;
- the first and last token of the page;
- the label nearest 0, 3, 6 and 9 o'clock, using ZL's `<!hh:mm>` clock comments.

A slot "hits" a month when its token occurs in no other month.

**Results.**
- The best slot was the last label on the page, often the central star label (e.g. f70v2 "otolal"). It hits 9 of 10 months.
- No slot hits 10 of 10.
- **Two-page check.** A real month word should repeat on both Aries pages and on both Taurus pages.
  - Aries (f70v1 + f71r) shares zero month-unique tokens.
  - Taurus (f71v + f72r1) shares "chal" (49 occurrences manuscript-wide) and "okeodaly" (2), and they are not in the same slot on the two pages.
  - No slot agrees within either pair.

**Nulls.**
- Shuffling tokens across pages: the maximum over slots has a median of 8 and a 95th percentile of 9, and P(max ≥ 9) = 0.35.
- Shuffling within each page: median 8, 95th percentile 10, P = 0.42.
- The mean hits per slot is 5.21 against about 4.7 under either null. This is consistent with labels being more hapax-rich than ring text. The dispersion of this mean was not computed, so its significance is **unverified**.

**Verdict: null.**
- No candidate Voynich month word was found. The 9/10 slots reflect hapax-rich labels and are within the shuffle range.
- The two-page months refute a repeated month token at a fixed slot.
- **What would overturn this:** a better transcription of the central labels, or a slot definition not covered here (e.g. text inside the central disc). Neither was checked.
- **O-012**: the expected null holds.
- **O-029**: the month names are usable only as a later owner's gloss. They give dating or provenance, not a crib for the Voynich text.
