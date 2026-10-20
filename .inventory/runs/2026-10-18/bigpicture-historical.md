# Big picture: historical and external context

Stamp: Sun Oct 18 20:56:03 PDT 2026 (from `date`). Read-only pass; this file is the only write; nothing is filed. Tags: **[disk]** checked on disk, **[online]** checked online this pass, **[unverified]** neither.

## 1. Hard external facts

- **Vellum C-14, 1404-1438 (95%).** Four folios (f8, f26, f47, f68), calf skin, cover goat. The test dates the skin, not the writing. [disk: `physical_provenance.md` Q1; VKB `physi-c14-dating-arizona-2009`, prose only] The per-sample table at voynich.nu/extra/carbon.html answers 200 [online] but is not saved.
- **Inks and pigments.** Iron-gall ink, azurite, copper green, gum [disk, secondary only]. The Beinecke report URL now returns HTML, not the PDF [online].
- **Davis's five scribes.** ZL3b `$H`: 113/46/33/27/7 pages [disk]. Davis 2020 (*Manuscript Studies* 5(1)) is open access [online], not on disk; X-08 unverified.
- **Provenance.** Tepenec ex libris on f1r (MSI 2024 confirms); Baresch's 1639 letter to Kircher; Marci owner 1662, letter 1665; the Rudolf II purchase is hearsay, "probable" per Guzy 2023. [disk: `physical_provenance.md` 96-131, secondary]
- **Marginalia.** f116v and f17r embed unglossed Voynichese words (`oror sheey`, `otaiol oim`). The f1r columns are probably Marci's, not row-aligned, and give garbage as a substitution. No provenanced crib exists. [disk: `multispectral_marginalia.md`; O-029]
- **Zodiac month names, later hand.** mars, aberil, may, jong ... decebre: N. French or Occitan. [disk: `zodiac_months.md`, secondary]
- **Layfield & Davis 2026**, "Singulion Structure and the Voynich Manuscript", *Digital Medievalist*. The DOI 10.4000/16k0a resolves to that title [online]. Its claims, as reported in a news summary [unverified]: the book was conceived as loose folded bifolios, and text similarity within a bifolium is raised (Timm, forum, agrees that the similarity is real). The conjoint/confoliate/facing values 0.433/0.383/0.298 are unverified (audit A). There is no stain catalogue [disk: VKB gap note]. Painting came before binding, and on f93r the text is written over a pigment stain [disk, secondary].

## 2. Period practices that could produce such a text

- **Cipher practice c.1400-1440.** Mantua 1401: about 33 signs, homophones for the vowels only. 15th-century keys: about 80% have nomenclators under 100 elements, 96% use nulls, and about 93% of nomenclature tables are simple substitution. [disk: `period_nomenclators.md`, from Megyesi 2021/2022, CC BY] Alberti's polyalphabetic disk (1467) and Trithemius (1499-1518) come **after** the vellum. So the Trithemius controls (O-065) are valid only as constructed-text controls, never as a candidate mechanism [inference].
- **Giovanni Fontana, Venice/Padua, 1420-1430.** *Bellicorum instrumentorum liber* (BSB Cod.icon. 242): captions partly in an invented-sign monoalphabetic cipher. The IIIF manifest answers 200, has 149 canvases and is licensed **PDM 1.0** [online]. His *Secretum de thesauro* (BnF NAL 635, c.1430) describes mnemonic machines, written in the same cipher. A Gallica scan was not found [unverified]. Transcriptions: Schulte 1910 (BSB Cod.icon. 242 a) and the Battisti 1984 decipherment [online, catalogue/forum only]. Argon's Fontana *simulator* was rejected (D-065, L-320) [disk]. Fontana's real ciphertext has never been scored.
- **Lullian tables.** 1515 Tabula generalis, 957 OCR tokens [disk, F-49]; `lull_ars_brevis_table`, 1,680 tokens [disk, VKB]. BC Ms 3075: Llull collection dated 1450/1457, 176 ff. [online: catalogue snippet]; digitisation and its 4-character cells [unverified, audit B].
- **Shorthand.** Tironian lexicon (Schmitz 1893, PD) on archive.org [online]; never scored [disk: VKB]. **Decknamen:** nothing on disk, no corpus located [unverified]. **Ars memoriae:** only an untested H-19 variant [disk]; Fontana's *Secretum* is the one memory-art text of the right date and region we know of.
- **Women's secrets.** Brewer & Lewis 2024 (*Soc. Hist. Med.* 37(3)): Hartlieb (c.1410-68) called for "secret letters" for abortifacient recipes; his cipher is lost [disk: `BREWER-LEWIS-CHECK.md`, abstract only; full text unverified]. Motive, not a testable mechanism.

## 3. Constraints we have not yet used

1. **The cipher must be one that existed then.** H-02/H-03/H-14 builds should use only 1400-1440 parts: ≤ ~40 signs, vowel homophony, nulls, a nomenclator of tens of entries. F-45 used synthetic keys, never a real period ciphertext.
2. **Five scribes means a teachable, shared procedure.** Free improvisation (H-08) or a private self-citing habit (H-07) should leave a mechanism that changes by hand, not just choices that change. This is untested: s114 controls hand but does not compare mechanism parameters between hands.
3. **The book was made of loose bifolios before binding.** If true, the unit of production is the bifolio, and the quire effects (F-17, F-42, F-50) may really be bifolio or session effects. F-09 has 52-bifolio blocks, but the drift tests use quire.
4. **Paint came before text.** Labels were written onto pictures already drawn, which favours label-to-picture tests (A1/A2) over label-to-body tests.

## 4. Ranked leads

### Lead 1: bifolio versus quire as the unit of production
- **Evidence.** Layfield & Davis 2026 (title [online]; claim [unverified]); F-50 drift and F-42 locality are measured by quire; the VKB has bifolio/conjugate [disk].
- **Test.** Rerun the frozen s114 omnibus and the F-42 locality statistic with bifolio labels nested in quire. Compare variance explained by bifolio within quire against quire, with hand x section held fixed.
- **Refuted if** bifolio adds nothing beyond quire at power (MDE ≤ 0.8 SD).
- **Cost.** Low: data on disk, 1 CPU-hour.
- **Splits.** A drift by writing session or sheet (H-05/H-14 state; H-07 local memory) versus subject-driven vocabulary (H-06). It also re-scopes X-04.

### Lead 2: per-scribe mechanism constancy (the teachability test)
- **Evidence.** Five scribes [disk, ZL3b $H]; F-16; s114 found constancy not supported, borderline.
- **Test.** Fit the G2b and line-pool producer parameters (Rw1, rhythm excess, prefix first-order matrix, core-pool locality) separately per Davis hand, within the herbal and bio sections. Use a permutation null of hand labels within section.
- **Refuted if** the mechanism parameters differ by hand beyond section while the planted-constant control stays clean. That would favour individual habit (H-07/H-08) over a taught system (H-05/H-06/H-19).
- **Cost.** Low. Needs Davis 2020 fetched (open access) to settle the ambiguous pages, f115r for example.

### Lead 3: Fontana's real 1420s cipher as a period positive control
- **Evidence.** BSB Cod.icon. 242: Venice 1420-30, PDM, 149 canvases [online]. It is the only invented-sign ciphertext from the right decade and region. The cipher is said to be monoalphabetic [online, secondary].
- **Test.** Key the cipher captions (or obtain Schulte 1910). Score them on the joint profile (h2, rhythm, in-line reuse, slot battery). Then check whether F-45's synthetic period ciphers reproduce Fontana's own statistics.
- **Refuted / informative.** Fontana fails like F-45: the synthetic emulation is confirmed and H-02 is closed on real period data. Fontana shows low h2 or in-line reuse: F-45's synthetic encodings are inadequate, and H-02/H-03 reopen.
- **Cost.** Medium: manual keying of a few thousand signs. It is small, so the test is also size-limited.
- **Splits.** H-02/H-03 (period cipher) from H-16/H-18 (notation, constructed language).

### Lead 4: a labelled herbal with body text, for the db-s109 / A2 calibration
- **Evidence.** s115-A0 used captions only (c-559) [disk]. A real link is r ≈ 0.09; the label-to-own-page test has never been calibrated.
- **Candidates.**
  - Macer Floridus, on disk, 14k tokens, entry headings [disk]. Usable now for a text-only label-to-own-entry check.
  - Cockayne, *Leechdoms* vol. 1 (Old English Herbarium, PD), archive.org 200 [online]. Chapters are headed by plant name; the images (Cotton Vitellius C.iii) and their licence are unverified.
- **Test.** Strip each heading from its entry and run db-s109 retrieval at Voynich size (N≈119), with shuffled-label controls.
- **Refuted / informative.** The real herbal recovers its link with power ≥ 0.8: F-43/F-44 nulls become informative. It does not: they are uninformative, like F-33.
- **Cost.** Low (Macer); medium (Cockayne OCR check).
- **Splits.** H-06 (content) from H-05/H-19 (procedure without content).

### Lead 5: a period combinatory table at length, and real chancery ciphertext
- **Evidence.** Llull's rule is deterministic, so the table can be generated; the open question is period *layout* (reading direction, cell length), which needs a manuscript. BC Ms 3075 (1457) is the nearest; digitisation unverified. DECODE has 1,667 keys; account needed, data terms unverified; 15th-century items are mostly keys, not ciphertexts [disk + online].
- **Test.** Generate full G2a tables under each attested layout; score any 15th-century DECODE ciphertext of ≥1k tokens on the joint profile (F-10's premise).
- **Refuted if** all layouts give the same profile (images add nothing), or no usable-length ciphertext exists.
- **Cost.** Medium; human browser access to MDC/DECODE. **Splits** H-19 from H-05; F-10's support for H-03.

## 5. Source list

| URL | licence | lets us test | status |
|---|---|---|---|
| https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00013084/manifest | PDM 1.0 | Lead 3 | 200, 149 canvases [online] |
| https://muse.jhu.edu/article/754633 ; https://repository.upenn.edu/mss_sims/vol5/iss1/6 | open access | Lead 2, X-08 | listed OA [online]; Penn 301 redirect |
| https://doi.org/10.4000/16k0a | OpenEdition (licence unverified) | Lead 1 | 200, title matches [online] |
| https://archive.org/details/leechdomswortcun01cock | PD | Lead 4 | 200 [online] |
| https://archive.org/details/commentariinotar00schm | PD | H-16 shorthand control | 200 [online] |
| https://www.voynich.nu/extra/carbon.html ; /letters.html | research use | dating, provenance facts | 200 [online] |
| https://beinecke.library.yale.edu/sites/default/files/files/voynich_analysis.pdf | Yale | pigment sequence | returns HTML, not PDF [online] |
| https://ecp.ep.liu.se/index.php/histocrypt/article/view/397 (DECODE v2) | paper CC BY; data unverified | Lead 5 | [online, search] |
