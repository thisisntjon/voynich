# Phase 4: can a known genre or exemplar supply a structural crib?

Stamped 2026-10-17 22:19 PDT from `date`. Investigation only; nothing here is pre-registered and nothing was run as a
test. The local numbers in section 1 are **descriptive counts** from `data/ZL3b-n.txt` (IVTFF locus types, `<%>`
paragraph markers). They were taken to size the tests and are not claims. Web content was read as data; nothing was
downloaded on purpose. (WebFetch auto-saved two PDFs to the session tool-results folder and they were not readable
here.) "Unverified" means I did not open a primary source.

## 0. Bottom line

No candidate comparator is close enough, *and* also available as a transcription, to act as an aligned plaintext
crib today. The practical route is three cheap tests that each fit in one pre-registration. Each one can kill a genre
match. None of them yields a crib unless it passes **and** then predicts something on held-out pages:

1. **Recipe quire as an antidotary rather than a "Recipe…/Item…" collection** (rank 1). It is cheap and local, and it
   comes with a sharp null.
2. **Zodiac labels as a degree-text list** (rank 2). A monomoiria-type list is already contradicted by the counts. A
   test against Abano/Alfonsine degree images needs a transcribed list that nobody has made.
3. **Section order against a German iatromathematical *Hausbuch* or Laufenberg regimen** (rank 3). It is cheap as a
   permutation test, but the only prior art is a single-researcher register.

The comparators the brief named (De balneis, Tacuinum, Circa instans, Bellifortis, Fontana) are useful as
**context and practice priors**, not as section-by-section exemplars. Section 3 gives the reasons.

## 1. Local descriptive facts that size the tests (ZL3b, not pre-registered)

- **Zodiac (f70v2–f73v):** 299 nymph labels and 264 label types. Per sign: Pisces 30; Aries 15+15; Taurus 15+15;
  Gemini 30; Cancer 29; Leo, Virgo, Libra, Scorpio and Sagittarius 30 each. Capricorn and Aquarius are lost. Most
  labels start with `o` (229/299), and 53% start with `ot-`/`ok-`. Only about 20 types repeat, and only `otaly` (5),
  `okal` (4) and `okaly` (4) occur more than three times.
- **Star pages:** f68r1 has 29 labels (29 stars, per Stolfi); f68r2 24; f68r3 12; f67r2 39 (this probably includes
  sector labels); f69r 22.
- **Recipe quire Q20 (f103–f116):** 285 `<%>` paragraphs and 10.6k body tokens. Words per paragraph: mean 38, median
  32, range 13–365. The 365-word maximum is merged paragraphs on pages where stars outnumber paragraphs (f111r has 17
  stars and about 6 paragraphs, per voynich.nu). voynich.nu counts 324 stars. Bifolio ff109–110 is missing, so about
  24–28 recipes are lost.
- **Q20 paragraph incipits:** 241 distinct first words among 285 paragraphs. The commonest is `tchedy`, 6 times. First
  glyph: p 155, t 61, k 20, f 15. Only 69 of the 285 first words also occur in the Q20 body. Stripping the initial
  gallows from the 251 gallows-initial first words leaves 193 distinct forms, and 163 of those occur in the body
  (`chedy` 8, `ol` 7, `olaiin` 6). That is Grove's "detachable gallows".
  **Read:** there is no formulaic incipit. A Latin "Recipe…/Item…/Ad…" collection puts one or a few words in the
  first slot of most entries. Q20 has at most 3% for any single form. That fits name-first entries (an antidotary: "X
  is made thus") or an enciphered incipit spread over homophones. It does not fit a plain formula word under a
  word-level code.

## 2. Leads ranked

### Rank 1: Recipe quire Q20 as an antidotary (Antidotarium Nicolai, Myrepsus type)

- **Prior art.** voynich.nu Q20 gives the star and paragraph counts and calls the paragraphs similar to recipes in
  medical manuscripts ([voynich.nu/q20](https://voynich.nu/q20/index.html)). Ninja threads record star/paragraph
  mismatches and an estimated original total near 360
  ([tid 1039](https://www.voynich.ninja/printthread.php?tid=1039)). A Ninja analysis reports 280 paragraphs averaging
  36 words and compares them with Alfonso X's *Lapidario*
  ([thread 2263](https://www.voynich.ninja/archive/index.php/thread-2263-22.html); unverified detail). Stolfi and
  Grove cover first words and detachable gallows
  ([Stolfi Note 062](https://www.ic.unicamp.br/~stolfi/voynich/Notes/062/Note-062.txt)). A CEUR 2022 paper gives the
  p-initial paragraph rate by scribe (35% / 54% / 52%) ([CEUR 3313 paper13](https://ceur-ws.org/Vol-3313/paper13.pdf);
  figures from a search summary, unverified). TheVoynich.org register lists "Q20 page-shape match to Myrepsos
  *Dynameron*" as Confirmed (local `data/external/thevoynich-register/research-snapshot.json`). That is one
  researcher's status with no evidence notes, so treat it as a Candidate. I found no prior comparison with the
  *Antidotarium Nicolai*.
- **Comparator facts.** The *Antidotarium Nicolai* is an alphabetical antidotary whose entries open with the
  compound's name. The Latin editio princeps (1471) is reprinted in van den Berg 1917, which is not online
  ([Wellcome](https://wellcomecollection.org/works/brcnk5ur)). The recipe count is usually given as about 115–150
  (unverified; no figure was opened). Myrepsus *Dynameron* has about 2,600 recipes, so it is far too large to align
  page for page. A Middle English version is edited in a 2018 Glasgow thesis
  ([theses.gla.ac.uk/8965](https://theses.gla.ac.uk/8965/7/2018GonzalezBlancoMPhilR.pdf)). CREMMA (local) may hold
  15th-century medical or recipe prose; s37 groups its sidecars by genre, so the controls may already be in hand.
- **Smallest test (pre-registerable).**
  - **T1a, incipit formulaicity.** Statistic: the share of paragraphs whose first token is the modal first token, and
    the entropy of first tokens relative to body tokens, with and without the gallows stripped.
  - **Comparators:** CREMMA recipe prose, split into "Recipe/Item" collections and name-first antidotary entries.
  - **Null:** first tokens drawn at random from paragraph-internal line starts on the same pages.
  - **Prediction for an antidotary:** first-token entropy at or above the null, and the modal share under 5%. A
    "Recipe/Item" collection gives a modal share of 30% or more.
  - **T1b, alphabetical order.** Alphabetical order puts runs of shared initial letters in sequence. Statistic: lag-1
  identity of the post-gallows second glyph, and of the second word's first glyph, across consecutive paragraphs, in
  folio order and in the Layfield–Davis order.
  - **Null:** 10k within-quire permutations of paragraphs, plus a page-block permutation that controls for scribe and
    page drift.
  - **Prediction:** an alphabetical antidotary in any letter-preserving cipher gives a run excess. Homophony dilutes
    the excess but does not erase it if the vowels alone are homophonic, as in the Mantua 1401 key.
  - **Size and power:** about 285 paragraphs. Power must be checked first by planting an alphabetical Latin
    antidotary through Naibbe and a nomenclator twin.
- **What would be a crib.** T1b passing, *plus* recipe lengths that track a specific antidotary entry by entry (length
  correlation on aligned order above a re-ordered-comparator null). That would give an aligned plaintext candidate:
  "paragraph n ≈ compound n". It would predict paragraph lengths on held-out pages and the lost bifolio's alphabetic
  span.
- **Cost.** T1a and T1b take an agent-session on local data. Alignment needs a transcribed Latin antidotary. That
  is human-only (library access to van den Berg 1917 or a Goltz edition) unless a Latin e-text turns up.

### Rank 2: Zodiac as a degree-text list (monomoiria, Abano *Astrolabium planum*, Alfonsine *Astromagia*)

- **Prior art.** Pelling suggested per-degree astrology for the 30 figures per sign
  ([Cipher Mysteries 2009](https://ciphermysteries.com/2009/05/12/per-degree-astrology-old-and-new)). Zandbergen, in
  Stolfi's notes, compared the labels with Abano's *Astrolabium planum* and the *Heidelberger Schicksalsbuch* (Cpg
  832) and found that the labels "do not match well". Abano's descriptions repeat several times, more often than the
  Voynich labels do ([Stolfi zod note](https://www.ic.unicamp.br/~stolfi/voynich/Notes/040/data-sections/zod);
  preliminary). Ninja thread 6021 (Aug 2026) records Alfonso X's *Astromagia* (BAV Reg. lat. 1283) and *Lapidario*
  degree images, and a claimed degree-by-degree Taurus match between Reg. lat. 1283 and Abano 1488. That match comes
  from a video and was not checked. The thread also cites Panofsky's early resemblance remark
  ([tid 6021](https://www.voynich.ninja/printthread.php?tid=6021)). Saxl Project has a 2023 PDF on prosopa and
  paranatellonta in the Tübinger Hausbuch
  ([PDF](https://www.thesaxlproject.com/assets/Uploads/Tubinger-Hausbuch-prosopa-and-paranatellonta-R-1-Dec-2023.pdf);
  not readable here, unverified content).
- **What the counts already say.** A **monomoiria** proper assigns a planet to each degree in a fixed 7-cycle. That
  predicts about 7 label types recurring with period 7. The text has 264 types in 299 labels, so the monomoiria is
  contradicted descriptively, unless each planet name is spread over many homophones, which the period-7 test below
  would still detect. "30 per sign" itself predicts nothing new, because the counts are already 30 (Cancer 29).
  **Degree-image lists** (Abano/Alfonsine) predict about 360 distinct descriptions with some cross-sign repeats. That
  is compatible with high uniqueness, but those repeats should then show up as shared label *stems* at specific
  degrees.
- **Smallest test.**
  - **T2a, period-7 test.** Do label-initial or label-final classes repeat with period 7 along each ring? Null: ring
    rotation and reflection. A monomoiria under any homophonic cipher predicts a lag-7 excess.
  - **T2b, cross-sign stem test.** For each pair of signs, compare the shared-stem (core) rate at matched ring
    positions with the rate at all other offsets. Null: per-ring circular shifts, with the start point and direction
    left free and paid for in the multiple-comparison count.
  - **Prediction:** a degree list with recurring images predicts an excess at offset 0 for the sign pairs where Abano
    or Alfonso repeat an image. That needs the transcribed list.
  - **Cost:** T2a and T2b are one session and local. The Abano 1488 and Reg. lat. 1283 degree lists have to be
    *transcribed* into a 360-row table. That is human-led image work, or several sessions reading scans.
- **What would be a crib.** Positional stem agreement with a named list, holding on signs not used to fit the start
  point. It would predict which nymph labels on held-out signs share stems, and the content of the lost Capricorn and
  Aquarius rings, which are untestable.
- **Lunar mansions and decans.** f68r1 has 29 star labels, against 28 mansions or 29–30 lunar days. Ponzi links the
  page layout to Getty MS 72 (c.1405) ([Bax blog](https://stephenbax.net/?p=803)). There is no star-by-star mapping
  in the prior art. Test: label count and order against the 28 mansions, starting from the Pleiades (f68r3 cluster) as
  the anchor. The power is tiny (n ≈ 29), so this is a pilot only. Decans (36) do not match any page count I found
  (unverified beyond this ZL3b census).

### Rank 3: Section order against a German iatromathematical Hausbuch or regimen (Laufenberg 1429)

- **Prior art.** TheVoynich.org register (local snapshot) has a "three-position section-ordering match Laufenberg ↔
  VMS" (Supported) and a "post-rebinding misordering, original followed Laufenberg" claim (Supported). It cites
  Berlin SBB Ms. germ. fol. 1191 (1429) and Wellcome MS 438. Laufenberg's *Regimen*, finished in 1429, has 6,012
  verses and five chapters: months, planets and signs, seasons and temperaments, and health order. Pregnancy and
  plague treatises were added by 1429 ([HLS](https://hls-dhs-dss.ch/articles/012755)). It is verse, which matters
  because A1 says single verse hands can approach the line-start profile. The Tübinger Hausbuch Md 2 dates c.1470–80
  but derives from an Ulm exemplar of 1404 ([UB Tübingen](https://uni-tuebingen.de/de/27503),
  [OpenDigi](https://opendigi.ub.uni-tuebingen.de/opendigi/Md2)). Pelling compares the zodiac roundels with Diebold
  Lauber workshop *Hausbücher* and finds partial matches only
  ([Cipher Mysteries 2018](https://ciphermysteries.com/2018/09/10/voynich-zodiac-gemini-and-the-workshop-of-diebold-lauber)).
- **Smallest test.**
  - **Statistic:** Kendall distance between the Voynich section order and the comparator's chapter order, using both
    the folio and the Layfield–Davis orders.
  - **Null:** all orderings of the six section labels, or quire-constrained orderings.
  - **Caveat:** with six sections only 720 orders exist, so a match is weak by construction (best p ≈ 1/720 only for
    an exact match). Pre-register the comparator list *before* looking, or the test is a garden of forking paths.
- **What would be a crib.** Order alone is not one. A crib needs chapter lengths that predict Voynich section token
  counts **and** a sub-chapter order inside a section (e.g. Laufenberg's month or sign order against the zodiac page
  order) that predicts unexamined pages.
- **Cost.** One session for the order test. Chapter-length data for Laufenberg needs Menge 1976 or a digitized
  witness, which is human-only or several sessions of scan reading.

### Rank 4: Bath section (f75–f84) against bath treatises

- **Prior art.** McLean compares the bath scenes with Valencia MS 860 "Balneum Sulphatara". He thinks the author knew
  *De balneis* but that the bath section is *not* an enciphered copy
  ([alchemywebsite](https://www.alchemywebsite.com/Voynich_baths_01.html);
  [Cipher Mysteries tag](https://ciphermysteries.com/tag/de-balneis)). Local notes cover the same ground
  (`research_notes/.../physical_provenance.md` Q7).
- ***De balneis Puteolanis*:** 35 bath epigrams, one bath per image. The only complete Latin edition is d'Amato's
  unpublished 1975 dissertation ([Traditio 2016](https://www.cambridge.org/core/journals/traditio/article/an-edition-of-richart-eudess-french-translation-of-pietro-da-ebolis-de-balneis-puteolanis/D3CC18134DE2CBA1618BB06489B320E4)).
  The Valencia and Bodmer facsimiles are digital. The Voynich bath quire is about 20 pages of continuous text and
  labels, not 35 discrete short poems in distichs. The structure is unlike, so it is **not testable as an exemplar**.
  The only cheap test: does the bath section split into about 35 text units with near-constant length, against a
  page-break null? Not expected.
- **Better comparators (new):** Felix Hemmerli, *Tractatus de balneis naturalibus*, about 1420, Baden in Aargau.
  This is in-window, in the southern German/Swiss zone, and prose (register record; PubMed title only; contents
  unverified). Also Hartlieb/Tömlinger *Bäderbuch* (BSB Clm 8244, 1498) and Kyeser's bath plates in the *Bellifortis*
  ([Wikipedia](https://en.wikipedia.org/wiki/Bellifortis);
  [Medievalists](https://www.medievalists.net/2014/07/medieval-siege-machines-the-bellifortis-by-conrad-keyser/)).
  These are image-to-image comparators, which is human-only.
- **What would be a crib:** none from images alone. Bath-name labels matched to a bath list would be one, but there is
  no candidate list with the right count.

### Rank 5: Herbal against alphabetical or chaptered herbals (Circa instans, Pseudo-Apuleius, Hartlieb *Kräuterbuch*)

- ***Circa instans*:** about 250–277 chapters in the Latin "B" version, alphabetical, with the formulaic opening
  "X calidus/frigidus est in … gradu". There is no online Latin e-text (FAMA and Wellcome have catalogue records only)
  ([brewminate summary](https://brewminate.com/a-medieval-pharmaceutical-bestseller-the-circa-instans/),
  [FAMA](https://fama.irht.cnrs.fr/manuscrit/37396)).
- **Test:** a formula prediction. Does the second- or third-word slot on herbal pages carry a low-entropy "quality" word
  (the hot/cold/dry/moist degree) above a within-page null? The Voynich herbal has about 130 pages, against 250+
  chapters, so alphabetical alignment is impossible without a missing-leaf model. It is cheap and local, but my prior
  is that it fails: Stolfi reports the first word per herbal page is usually unique, which fits name-first entries but
  is not diagnostic.
- **Hartlieb *Kräuterbuch* (c.1450):** the Hayer/Schnell 2010 critical edition exists (register). It postdates the
  window and has no cipher. It is a context comparator only.

### Rank 6 (context only, not a crib): *Tacuinum sanitatis*

Its table and image-per-item format, with very short text, does not match running paragraphs. There is no structural
test worth registering.

## 3. Candidate authors and demonstrated cipher practice, 1404–1438

| Person or source | Dates | Demonstrated cipher | Bearing |
|---|---|---|---|
| Giovanni Fontana (Padua/Venice) | *Bellicorum instrumentorum liber* c.1420 (BSB Cod.icon. 242); *Secretum de thesauro* (BnF NAL 635) | Simple **monoalphabetic** substitution in symbol shapes, applied to *some* captions; Battisti 1984 edition with decipherments ([review](https://ciphermysteries.com/2008/12/06/review-of-le-macchine-cifrate-di-giovanni-fontana), [Wikipedia](https://en.wikipedia.org/wiki/Giovanni_Fontana_(engineer))). Schulte 1910 transcription (forum claim, unverified). Register claims a multi-layer cipher (single researcher, unverified). | In-window, Italian, technical-illustrated. Monoalphabetic is ruled out for the Voynich by h2 (A11), so Fontana shows *motive and format*, not mechanism. Fontana's deciphered captions are a ready **positive control**: run the project's line and edge battery on a 15th-c. enciphered technical caption corpus. |
| Konrad Kyeser | *Bellifortis* 1402–05, Eichstätt | No cipher found in search (unverified absence) | Bath and technical imagery context only. |
| Mantua chancery (Simeone de Crema key) | 1401 | Reversed alphabet plus **homophones only on vowels** (about 4 per vowel); nulls and small nomenclators in Lavinde-type keys ([Cipher Mysteries](https://ciphermysteries.com/2016/07/06/fifteenth-century-cryptography); Kahn; recipient disputed) | The only in-window homophonic practice. It is a concrete mechanism prior for T1b (vowel-only homophony preserves consonant runs). |
| Tranchedino ledgers (Milan/Mantua) | c.1450 | Homophones on consonants and vowels, nulls, nomenclators of 80+, **syllable-group signs** | Just after the window. Closest attested period form to a syllabic or verbose cipher. |
| Johannes Hartlieb | c.1410–68; Padua doctorate 1439; onomancy 1436; *Secreta* translation 1460–65 (BSB Cgm 261) | Called for "secret letters" to hide abortifacient recipes (Brewer & Lewis 2024, SHM 37(3):559–582; Brewer 2022 [CEUR 3313 paper3](https://ceur-ws.org/Vol-3313/paper3.pdf)). The decoded comparators (incl. a 21-line N. Italian recipe cipher) are known only from press summaries: **unverified**; the PDF was not readable here. | Motive prior for enciphered *recipes*. Ties directly to the Q20 lead. Getting the comparator cipher types is a human task (OUP full text). |

## 4. What is human-only

- OUP full text of Brewer & Lewis 2024: their decoded recipe ciphers are the most direct practice comparator for Q20.
- A Latin *Antidotarium Nicolai* text (van den Berg 1917 / Goltz), for T1 alignment.
- Transcribing the Abano 1488 or *Astromagia* 360 degree descriptions, for T2b.
- Image-to-image comparison of baths and roundels (Valencia MS 860, Bellifortis, Lauber Hausbücher). This is art
  history and produces no statistical crib.
- A Voynich Ninja account, for hidden links in threads 1039, 2263 and 6021 (registration is Jon's call).

## 5. Recommended next pre-registration (one file, local data only)

The P4-COMP-1 pre-registration bundles T1a, T1b, T2a and T2b. Each test has a planted-genre positive control: an
alphabetical Latin antidotary and a 7-cycle planet ring, each passed through Naibbe and a nomenclator twin, run before
the Voynich. Kill rule: if a planted control is not detected at the registered alpha, the test is underpowered and
reported as such, not as a negative. A pass is Tier 3 (a genre constraint). It becomes a Tier 1 crib only after a
named comparator's aligned lengths or stems predict held-out paragraphs or rings.
