# Literature consumption, 2026-10-18

Stamped 2026-10-18 01:31 PDT from `date`. Literature subagent for the main session. Scope: four requested sources. Rule: a
paper counts as used only if it changes a method, a comparison or a decision. Downloads are in
`data/external/lit-20261018/<name>/`. They are untrusted, nothing in them was executed, and their text was treated as data.
Overlap was judged against `workflow/CONSTRAINTS-MAP.md` (A1–A19, dots 1–19) and `workflow/research/public-baseline.md`.

| # | Source | What was read | Status |
|---|---|---|---|
| 1a | Parisel 2026, arXiv 2604.25979 (Currier A/B) | full text, 13 pp. | **full** |
| 1b | Parisel 2026, arXiv 2604.19762 (positional/directional constraints) | full text, already on disk | **full** |
| 2 | Steckley & Steckley 2024, arXiv 2404.13069 | full text + Tables 1–3 (images) | **full** |
| 3 | Greshko 2025, Cryptologia | main article blocked; author's Supplementary Materials 1–4 read in full; secondary summaries | **main text blocked** (supplement full, abstract not reachable) |
| 4 | Meister 1902, pp. 30–31 | nothing | **blocked** |

---

## 1a. Parisel (2026b): "A Quantitative Confirmation of the Currier Language Distinction"

- **Citation:** Christophe Parisel, *A Quantitative Confirmation of the Currier Language Distinction*, arXiv:2604.25979v2
  [cs.CR], 5 May 2026. Code: github.com/labyrinthinesecurity/currier-models (not fetched, not run).
- **URL read:** https://arxiv.org/pdf/2604.25979 → `data/external/lit-20261018/parisel-2604.25979/` (pdf + pdftotext).
- **Read:** full text (all sections and appendices A–C).
- **Key claims:**
  - §2.1: EVA IVTFF, about 36,500 tokens, 200 folios. 185 folios with confident A/B labels (108 A, 77 B). ch/sh are parsed as single glyphs.
  - §3.1, Table 2: folio-level ratios for 11 "similar-glyph" pairs. Six pairs beat all 1,000 label shuffles. Strongest are d/l (Cramér's V 0.375), or/ar (0.337), s/r (0.228) and e/ee (0.203). o/a, ch/sh and f/p show near-zero V.
  - §3.2: a single order-2 character Markov source gives 3–11× less inter-folio variance than the manuscript. A split A/B Markov model still underestimates folio-level variance (100th percentile for 10 of 11 pairs).
  - §3.3, Table 3: language changes inside a quire jump 58 % more than same-language transitions (p 6.9e-5, n 18), so the split is "not codicological".
  - §3.5–3.6, Tables 4–5: an unsupervised Beta-Binomial mixture selects k = 2 by BIC (ARI 0.383 against Currier's labels). Supervised cross-validation gives 89.2 % accuracy. **The A/B label explains only 29 % of inter-folio variance (R² 0.293).**
  - §5, Tables 7–9: a "boolean switch" f, set per folio, is cho/(cho+che) after ch/sh. It is bimodal (BC 0.661), ΔAIC 2,549 over one state, p1 0.68 vs p0 0.16, and 195/197 folios are assigned at posterior > 0.8. It survives inside Herbal (92 f=1 vs 32 f=0) and is flat across line positions 0–9 (§5.3).
  - §6, Tables 10–11: under the switch, word templates (chXdy, chXey, …) are either fixed or switchable. Template identity carries 92 % of the cho-rate variance and no template reverses direction.
  - §7: the d/l ratio is gradient, not bimodal, and is orthogonal to f (r −0.016 in Herbal).
  - §9.1: consecutive classifiable words share type (+12 to +17 points, Z 4.5–5.6).
  - §9.3 lists three compatible classes and does not choose among them: two orthographic registers, two table variants, or a cipher with a per-folio key bit.
  - §9.4 limitations: one transcription; **no test of whether f changes below folio level (paragraph, quire)**; multi-panel folios merged.
- **Against our map:**
  - *Replicates* dot 12 and A9 in part: A/B is a real, label-free split. It also replicates the "A/B differences everywhere" premise behind A1, A3 and A13's A/B rows.
  - *Does not address* our c-374/dot 12 point that A/B is also a scribe split (hand 1 = all A). Parisel never conditions on Davis hands. The "per-folio switch" f could therefore be scribe identity, not a bit set per folio. Herbal f = 1 on 92 folios and f = 0 on 32 roughly matches Herbal A (hand 1) vs Herbal B (hand 2). This is unverified: we have not computed f per hand.
  - *Extends* dot 8/10/19, the two-layer word: the switch acts inside the core region (the vowel after the ch/sh bench), and only in some templates. That is the joint choice of frame and core that s58/s61 point to (the "scribe chose prefix, core and suffix together").
  - *Anticipates* dot 16, local memory: the +12–17 point same-type persistence between consecutive words (§9.1) is a coarse version of our short-range core recurrence.
- **Changes (method):** every A-vs-B comparison on the map, and the s61 joint-word test, gains a **within-hand control**. Compute Parisel's f (cho/(cho+che) after ch/sh) per folio and test its bimodality *inside hand 1 alone* and *inside hand 2 alone*. If f is bimodal within a hand, it is a real per-folio state that any producer must set (a new constraint, A20 candidate). If f is constant within each hand, the "switch" is scribe identity and folds into dot 12. Also add f and d/l as two separate axes in place of the single A/B label wherever we report A/B splits (A1, A3, A13): Parisel's R² 0.29 says the binary label discards most folio-level variance.

## 1b. Parisel (2026a): "Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript"

- **Citation:** Christophe Parisel, *Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript:
  Implications for Cipher-Like Structure*, arXiv:2604.19762v2 [cs.CL], 16 Jun 2026. Code: github.com/labyrinthinesecurity/currier-signatures (not fetched, not run).
- **URL read:** already on disk at `data/external/papers/parisel_2026_arxiv_2604.19762.{pdf,txt}`, from https://arxiv.org/pdf/2604.19762. Not re-downloaded.
- **Read:** full text (§1–6 and tables).
- **Key claims:**
  - §3.1: RF1b-e. A ≈ 9.9k words, B ≈ 19.6k. Comparators are English, French, Hebrew and Arabic only.
  - §4.1.1, Table 2: a 2:1 start/end ratio classifies graphemes. Voynich's end-class→start-class rate across a space is **80.6 %**, against 19.8–35.5 % for the comparators. Under "bilateral extremity", graphemes above 100:1 fall in both classes (q 1762:1 initial; iin 3958:0 final).
  - §4.1.2, Table 3: cross-boundary MI is 0.230 bits (highest of 5). 97 % of it is within-class grapheme identity, and the class labels carry 3 %. Shuffling word order leaves 21 % (0.049), the most of any corpus. Forward/backward MI is 4.5:1.
  - §4.2, Table 4: the RTL-character/LTR-boundary "directional dissociation" is reproduced 10/10 by a word-level Markov chain. Parisel himself calls it *non-diagnostic*.
  - §3.5, Table 1: a four-signature joint criterion calibrated per dialect. Sig1 E→S is A 71.0 % / B 64.3 %. Sig2 is bilateral extremity. Sig3 raw MI is **A 0.586 / B 0.498** (net of shuffle A 0.181 / B 0.165, §4.3.3). Sig4 is a non-plateau boundary shape (A Zipfian, B intermediate).
  - §4.3, Tables 5–8: a slot generator (≈1,000-word lexicon + sparse word Markov) reaches at most 3/4 and fails MI. The Rugg grille reaches at most 3/4 in its "circular" pre-split pools and ≤1/4 in honest form. A sequential English row-grille gives a net MI of ≈0.002.
  - §5.4 and §5.5 item 2: "generators where E→S and Zipfian shape arise from genuinely independent mechanisms remain untested".
- **Against our map:**
  - *Replicates* A3 (cross-space last→first coupling is real, order-dependent and above the four languages) and A4's warning in spirit: the class-level E→S rate is near-constant and carries 3 % of MI.
  - *Replicates* A2 and the public-baseline item 7/8 slot asymmetry.
  - *Contradicts on the surface* A3's "strongest in Currier B". Parisel has A > B (0.586 vs 0.498 raw; 0.181 vs 0.165 net). The measures differ. Ours is coupling excess over shuffle. His is plug-in MI on n-gram boundary pairs in 10 chunks per dialect, and A's chunks are half the size of B's (≈990 vs ≈1,960 words), which inflates plug-in MI for A. Which difference drives the sign is **unverified**.
  - *Extends* A17/dot 11: our two-layer wrapper (s36, s58) is exactly the "independent mechanisms" generator he says is untested.
  - His slot generator failing MI is consistent with our A4 only if lexicon size is the bottleneck. His lexicon is ≈1k words against our 7k-type wrappers. This is unverified.
- **Changes (comparison):** add Parisel's four signatures as an **external benchmark row** on the board, reimplemented from §3.2–3.5 definitions (not by running his code): E→S %, bilateral extremity count, MI and net-of-shuffle MI, and boundary shape (R², CV). Score Voynich A/B, s36/s58 two-layer outputs, s28, Naibbe (c4) and the Rugg grille, at **matched token counts per chunk**. This (a) reconciles the A/B sign conflict with A3 and (b) answers his open question with our generator. If the s58 wrapper passes 4/4, his "cipher-like" inference is answered with a generator; if it fails Sig3, it is a new miss for A17.

## 2. Steckley & Steckley (2024): "Subtle Signs of Scribal Intent in the Voynich Manuscript"

- **Citation:** Andrew Steckley and Noah Steckley (QuantumLynx Research), *Subtle Signs of Scribal Intent in the Voynich Manuscript*,
  arXiv:2404.13069v1 [cs.CL], 14 Apr 2024. Journal version per web search: DOI 10.58009/aere-perennius0112 (University of Tartu DSpace). That version is not read: dspace.ut.ee timed out on connect.
- **URLs read:** https://arxiv.org/pdf/2404.13069 → `data/external/lit-20261018/steckley-2404.13069/`. Table images from https://arxiv.org/html/2404.13069v1/ → `data/external/lit-20261018/steckley-arxiv-html-tables/`, read visually.
- **Read:** full text, 6 pp., plus Tables 1–3. Supplemental tables at quantumlynxresearch.com/research were not fetched.
- **Key claims:**
  - §4: ZL3a. **Herbal, Davis Scribe 1 only, paragraph text.** Ambiguous glyphs, uncertain spaces and paragraph-final tokens are dropped, leaving 7,660 tokens / 1,223 lines / 95 folios.
  - §5, Table 1: mutually exclusive cohorts with mean glyph length. MIDDLE is 4.58 (n 3,807). TOP 5.04, FIRST 5.13, LAST 4.47, **BEFORE a drawing 4.24 (n 349, 71 folios)**, AFTER a drawing 4.66 (n 278). SECOND 4.66, FOURTH 4.68 and six random MIDDLE draws 4.58–4.64 are the controls.
  - §6, Fig. 5: χ² on the length distributions at p < 0.01. FIRST differs from all. **BEFORE and LAST differ from all others but resemble each other.** MIDDLE, AFTER, SECOND and FOURTH are indistinguishable.
  - §7, Tables 2–3: per-token binomial p ≤ 0.01 and ln B ≥ 5.
    - LAST affinitive: am, chory, om, g, sal, chotaiin, dam (9.8×), dy (4.9×), dal, dar, daiin. LAST aversive: chol (37 expected → 1), shol, sho, chy, chey, chor.
    - **BEFORE affinitive: qotaiin, dy (9.0×, 3 expected → 23), dam (7.8×), s (2.8×). BEFORE aversive: chor (10 → 0), chol (17 → 3).**
  - §8: the conclusion is "extrinsic positioning", meaning token choice depends on drawing adjacency.
  - Weaknesses: no multiple-testing correction across hundreds of tokens × 5 cohorts beyond the strict thresholds; χ² assumes independent tokens; one scribe and section only.
- **Against our map:**
  - *Contradicts in part* A15 ("drawing gaps inside a line do not behave as line edges") and dot 9. Our own s35 Part 2C (`results_s35_physical_codicology_quire_network.txt`, lines 99–105) agrees with Steckley more than A15's wording does:
    - pre-drawing −m is 2.42 % against 0.92 % mid-line (2.6×) and 15.50 % at true line end;
    - post-drawing o/y/d/s-initial is **74.46 %** against 43.63 % mid-line and 58.34 % line-initial;
    - only the gallows (0.27 % vs 22.32 %) and the m/g flourish are absent at drawing gaps.

    So the gap is a **weak edge**. It lacks the paragraph/gallows and m/g markers but shifts word length and choice toward line-end-like (dy, dam, short) before it and line-start-like after it.
  - *Replicates* A1 and A2 for hand 1 Herbal: FIRST is longer and LAST is shorter, with m-final types (am, om, dam) favoured line-finally.
  - *Anticipates* B2's prior-art note (Ponzi 2019, drawing interruptions) and Schwartz's "text written onto finished drawings" (`data/external/README.md` item 20).
  - *Bears on* A5: the within-line length rhythm could be partly **space-fitting** (shorter words where space runs out). Lines broken by drawings carry two such points.
- **Changes (decision + method):**
  - (1) Reword A15 and dot 9. Drawing gaps do not trigger gallows or the m/g flourish, but they are not neutral: word length and choice shift as at a line end (Steckley Tables 1–3; our s35 2C). Dot 9 keeps "the line signatures are the scribe's lines" but loses "drawing gaps are not edges" as an unqualified statement.
  - (2) Add a robustness row to A5 (Moran) and A1: recompute both (a) excluding tokens adjacent to `<->` drawing breaks and (b) treating `<->` as a line break. Then state how much of the rhythm survives.

## 3. Greshko (2025): "The Naibbe cipher"

- **Citation:** Michael A. Greshko, *The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich
  Manuscript-like ciphertext*, Cryptologia (online 2025-11-26), pp. 1–37, doi:10.1080/01611194.2025.2566408. CC-BY-4.0 per Crossref, "HYBRID/public-domain" open-access flag per Semantic Scholar. Title, author, pages, date and licence were read from api.crossref.org and api.semanticscholar.org; **neither returns an abstract**.
- **Routes tried (4):**
  1. WebFetch of tandfonline /doi/full: HTTP 403.
  2. curl of the Crossref-listed /doi/pdf link with browser headers: HTTP 403, Cloudflare challenge. Saved as `lit-20261018/greshko-tandf-pdf/greshko.pdf`, which is **an HTML error page despite the name**.
  3. Search for an author preprint or arXiv copy: none found.
  4. Secondary: sci.news, read; and the forum thread already on disk (`data/external/naibbe-greshko/voynich_ninja_thread5081.txt`).
- **Read:** **main article not read.** Read in full: the author's *Supplementary Materials 1–4* (`data/naibbe_zenodo_17219445/Greshko2025_Supplementary_1-4.pdf`, already on disk, text extracted to scratch). Secondary summaries were also read.
- **Key claims (supplement, by section):**
  - S1.1: about half of word types are hapax at Voynich-B length.
  - S1.2: drawing interruptions are trivial because tokens encode 1–2 plaintext letters.
  - S1.3: skewed word pairs, AB ≫ BA (Table S1: e.g. qokain qokar = UM).
  - S1.5, Table S2: unigram tables are organised as **5 conserved prefixes {qok, ok, qot, ot, olk} × a letter-dependent suffix**. The table (prefix family) is chosen by a card draw; the letter sets the suffix.
  - S1.6: word repetition is **0.18 ± 0.04 % vs VMS 0.8–0.9 %** (author's admission).
  - S1.7: Levenshtein-1 networks resemble Timm & Schinner's four domains, with longest path 21.
  - S1.8: TF-IDF/k-means recovers plaintext topic sections from ciphertext; LDA fails on both.
  - S1.9: MCW70 is 0.44 ± 0.01 (VMS 0.40–0.44). **MATTR is 0.56 vs VMS 0.49–0.53 (overshoot).**
  - S1.10: no periodic token autocorrelation.
  - S2: the Voynichesque generator draws on Zattera slots 0–3, 4–7 and 8–10, with a "Voynichesque A/B" bigram switch.
  - Forum (author, 30-11-2025): fitted to **Voynich B only**; tables cannot produce standalone s, l, o, r, d.
  - sci.news: "incomplete replication of Voynich B's properties" (author quote fragment).
- **Against our map:**
  - Already tested here (`results_c4.txt`, c-105, c-177, c-345): first-glyph JSD 0.0006 vs 0.172 and edge excess +0.0018. It misses A1 and A3, reaches F1, and misses CHARWIN and Moran. Naibbe as-is is on the D-012 stop list.
  - The supplement *confirms* and *explains* two misses: the repeat rate is 5× too low, consistent with our dot 16 local-memory finding, and MATTR is too high.
  - *Contradicts* dots 10 and 15 structurally. In Naibbe the prefix family is a random card draw (i.i.d. per token) and the letter lives in the suffix. Its prefix stream should therefore be close to orderless. Our manuscript's prefix stream is "more predictable than any code or generator" (dot 15) and the content-like order sits in the cores (A16). This contrast is **predicted, not yet measured**: Naibbe is not among the s55 rows (`results_s55.txt` imports `c4_naibbe_lines.py` but lists no Naibbe row).
  - *Replicates* S1.8 vs D-012: topic models recover sections from a cipher too, so section vocabulary (A8) is not evidence for or against content.
- **Changes (comparison):** add the c4 Naibbe ciphertext as a named row in the s55 wrapper-free taxonomy (f4 prefix gain, f2 core→core, f5 core cover). Naibbe is the one published period-plausible cipher, and its architecture makes a sharp prediction (low prefix gain) against dot 15. This turns "Naibbe as-is fails" from a board miss into a structural exclusion of the whole "random table per token" design. The main-text read stays open (O-018), and it does not block this.

## 4. Meister (1902), *Die Anfänge der modernen diplomatischen Geheimschrift*, pp. 30–31

- **Citation:** Aloys Meister, *Die Anfänge der modernen diplomatischen Geheimschrift. Beiträge zur Geschichte der italienischen
  Kryptographie des XV. Jahrhunderts*, Paderborn: F. Schöning, 1902. HathiTrust record 006176726.
- **Routes tried (4 + 1 lead):**
  1. HathiTrust babel `pt`/`ssd` for hvd.hxub2m: HTTP 403 (Cloudflare). The HathiTrust catalog API *did* answer: rights `pdus`, "Full view" (US). It also shows **a second full-view copy, uc1.b4177709**, which is new to us.
  2. WebFetch of uc1.b4177709 plaintext: HTTP 403.
  3. archive.org advanced search on the title: 0 hits.
  4. Google Books API: HTTP 429, daily quota 0 for the shared key.
  5. Lead from the local Pelling page (line 235): http://www.nickpelling.com/voynich/Meister1902.zip returned HTTP 404. It is saved as `lit-20261018/meister-1902-pelling-zip/Meister1902.zip`, which is **an HTML 404 page despite the name**.
- **Read:** nothing of Meister. Only secondary: Pelling (`data/external/nomenclators/ciphermysteries_tranchedino_p3700.html.txt`, lines 47–48).
  - p. 30 is a "surprisingly complex" Milanese key and nomenclator of 14 March 1448 (Milan, Staatsarchiv, Pot. Est. Cifre Fasc. 2 Nr 5).
  - p. 31 is a 1483 key with a "4o" sign for z.
  - Also p. 35, Modena 1435, "4" = Q and "4o" = "Qua"; and p. 50, Florence 1424, "4o" for Q.
  - No symbol counts, homophone counts or null counts are given.
- **Against our map:** it bears on A11 (period bound: ~80 % of nomenclatures under 100 entries; 96 % use nulls). Unread, it can neither tighten nor loosen that bound.
- **Changes nothing:** no primary text was obtained. O-017 stays open with two new facts: a second full-view HathiTrust copy (uc1.b4177709) exists, and the volume is `pdus`, so a US-IP page-image fetch is legal.

---

## Follow-ups (computational only, ranked)

1. **Parisel's f within hand.** From ZL3b + Davis hands: per-folio cho/(cho+che), bimodality and 2-state ΔAIC inside hand 1 and inside hand 2. Decides whether the switch is a new per-folio state (A20 candidate) or scribe identity (dot 12). It is cheap, and it sharpens the input to s61.
2. **Naibbe in the s55 taxonomy.** Score the existing c4 Naibbe lines on f2, f4 and f5 at matched size. The prediction is low prefix gain against Voynich's highest. A clean structural exclusion of the random-table-per-token cipher class.
3. **Parisel four-signature benchmark,** reimplemented from §3.2–3.5. Run it on Voynich A/B (matched chunk sizes), s36/s58 wrappers, s28, Naibbe and Rugg. It reconciles A > B (Parisel) with B > A (A3) and tests his "untested independent-mechanism generator" with ours.
4. **Drawing-gap robustness for A5/A1.** Recompute Moran and line-initial JSD (a) excluding `<->`-adjacent tokens and (b) treating `<->` as a line break. Replicate Steckley's length and propensity cohorts on ZL3b, all hands, with FDR correction. Rewords A15/dot 9 on a number.
5. **Space-fitting test.** With the Rozanova word boxes already on disk (`data/external/word-coordinates/`), regress the length of the word before a drawing gap or margin on the remaining physical space. If length tracks space, A5's rhythm has a layout component that any producer model must include.
6. **Meister retry (fetch only):** a Wayback Machine snapshot of the dead Pelling zip URL, and HathiTrust page images for uc1.b4177709. Machine fetches only; stop on the first block.
