# Greshko 2025, "The Naibbe cipher" (Cryptologia) — external anchor notes

Stamped: 2026-10-17 20:02 PDT (from `date`). Inventory item: O-018.
Paper: doi 10.1080/01611194.2025.2566408. Full title (per Semantic Scholar API): "The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext".

## 1. Was the main text reachable? No.

| Route | Result | URL |
|---|---|---|
| tandfonline /doi/full/ (WebFetch) | HTTP 403 | https://www.tandfonline.com/doi/full/10.1080/01611194.2025.2566408 |
| tandfonline /doi/epdf/ (WebFetch) | HTTP 403 | https://www.tandfonline.com/doi/epdf/10.1080/01611194.2025.2566408 |
| tandfonline in a real browser pane | Cloudflare "Just a moment..." bot check that did not clear in 8 s; not bypassed | same |
| Unpaywall | is_oa true, oa_status hybrid, licence public-domain, OA date 2025-11-26, **no PDF URL**, only the publisher landing page | https://api.unpaywall.org/v2/10.1080/01611194.2025.2566408?email=research@example.org |
| Semantic Scholar API | openAccessPdf points back to the DOI; abstract null; web page 403 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1080/01611194.2025.2566408 |
| ResearchGate | listed with no full text (per search snippet, not opened) | https://www.researchgate.net/publication/398028327 |
| Wayback availability API | HTTP 429 | https://archive.org/wayback/available?url=tandfonline.com/doi/full/10.1080/01611194.2025.2566408 |
| Author site | summary only, links to paper and talk | https://www.michaelgreshko.com/naibbe-cipher |
| Preprint | in a Dropbox folder linked from forum thread 4848, link hidden behind forum login | https://www.voynich.ninja/thread-4848.html |

Note: the local `data/external/naibbe-greshko/greshko_cryptologia_2025.html` (5.5 KB) is the Cloudflare challenge page, **not** the paper.

What remains open for O-018: a human browser fetch of the OA HTML/PDF, or the Dropbox preprint from thread 4848 (needs forum login). The paper is OA and public-domain-licensed per Unpaywall, so a human copy is legitimate.

## 2. Sources actually used
- S1 = local supplement `data/naibbe_zenodo_17219445/Greshko2025_Supplementary_1-4.pdf` (author's own text; Zenodo https://zenodo.org/records/17219445). **Primary, by the author.**
- GH = reference code https://github.com/greshko/naibbe-cipher (raw `naibbe.py`: https://raw.githubusercontent.com/greshko/naibbe-cipher/main/naibbe.py). Author's code; the code may differ from the paper's hand procedure.
- F1 = forum thread 4848 (preprint discussion), https://www.voynich.ninja/printthread.php?tid=4848 (author posts as "magnesium").
- F2 = forum thread 5081 (publication announcement), https://www.voynich.ninja/thread-5081.html, local copy `data/external/naibbe-greshko/voynich_ninja_thread5081.txt`.
- H = Jürgen Hermes blog (German, based on the talk and Zenodo, not the paper), https://texperimentales.hypotheses.org/5898.
- N = Newsweek, https://www.newsweek.com/voynich-manuscript-15th-century-book-cards-dice-cipher-naibbe-11316017.

## 3. Procedure
- Type: verbose homophonic substitution, doable by hand with 15th-century materials (GH README abstract; author site).
- Plaintext: Latin and Italian. The author says it worked "especially well" with those two, and others have used it on German (F2, author reply to Skoove; S1 header title).
- Respacing: plaintext is cut at random into unigrams and bigrams, about 50/50 (F1, H). In code: P(unigram) = RESPACING/36 with RESPACING = 17, so about 47 % unigrams. A comment says 18 gives 50/50 (GH). The /36 suggests a two-dice roll; that is my inference, **unverified** against the paper. Newsweek also says a die splits the word (N).
- Tables: **six** tables (alpha, beta1–3, gamma1–2 in code), each with three slots: unigram, bigram prefix, bigram suffix (GH, H). A bigram is prefix glyphs + suffix glyphs written as one token, and each half gets its own card draw (GH).
- Table choice by playing cards: 52-card deck weights 20:8:8:8:4:4, and 78-card deck weights 28:14:11:11:7:7 (GH). H gives 5:2:2:2:1:1 out of 13. S1 uses "78-card" ciphertexts throughout. A fresh shuffled deck starts on each input line in code (GH), which **does not** amount to any line-edge rule.
- Alphabet: 23 letters (J→I, K→C, W→UU) (GH; S1 Table 2 lists A–Z without J, K, W).
- Homophones per letter: 6 unigram word types, one per table (S1 Table 2). Bigram space: H counts (23×6)² = 19,044 theoretical bigram types. Its unigram count of "142" is an arithmetic slip for 138.
- Unigram tables are built from 5 conserved beginnings (qok-, ok-, qot-, ot-, olk-) plus regular suffixes, Trithemius-style (S1 §1.5, Table 2). Examples: E = chedy (primary table), I = shedy / qokedy, N = daiin, O = aiin.
- No nulls in the current version (F1). Rare glyphs x and g are included as a proof of concept (S1 §1.1). Standalone s, l, o, r, d cannot be unigram words (F2, author).
- Code option UNAMBIGUOUS redraws a bigram whose glyph string equals a unigram word (GH).
- Scope: fitted to **Voynich B only**, because there is more text and because of B's frequency-rank shape (F2, author reply). No Currier A fit is reported.

## 4. Statistics reported (supplement only; main-text numbers not seen)
| Property | Naibbe | VMS | Source |
|---|---|---|---|
| Hapax share of types at ~Voynich B length | "about half" | consistent (Zandbergen 2024) | S1 §1.1 |
| Immediate word repetition | 0.18 ± 0.04 % | 0.8–0.9 % | S1 §1.6 |
| MCW70 | 0.44 ± 0.01 | ~0.40–0.44 | S1 §1.9 |
| MATTR (1,000-token window) | 0.56 ± 0.01 (overshoots) | 0.49–0.53 | S1 §1.9 |
| Similarity network longest path | 21 | 21 | S1 §1.7 |
| Token autocorrelation (Stars section) | no periodic peaks; matches | — | S1 §1.10 |
| Topic signal (TF-IDF clusters) | recovers plaintext sections | recovers VMS sections | S1 §1.8 |
| Can generate Voynich B tokens | about 5/6 of tokens | — | F1 (forum summary) |

- **h2 / conditional character entropy, word-length distribution, type counts:** the supplement and forum say the cipher was tuned to match these, but **I saw no Naibbe number for them**. They are presumably in the main text. **Unverified.**
- **Currier A/B:** not reported for Naibbe (B only). Voynichesque (S2 §2.2.1) has a mechanism to mimic A-like and B-like types, but that is a different generator.

## 5. What the author says it fails to reproduce
- Line, paragraph and page properties: per the forum summary of §4.3, the cipher has no mechanism that reliably produces them (F1). **Primary text unverified.**
- Proposed fixes, all speculative: a paragraph-initial gallows or "pch" prefix as a null, and line-final -m tokens as padding nulls (F1).
- The exact diversity of VMS word types, "especially rare ones" (quoted from the paper by Mark Knowles in F2).
- Word repetition is too low, about one-fifth of the VMS rate (S1 §1.6). The author suggests Roman-numeral-heavy plaintext or reuse of the previous line's choices as possible fixes (S1 §1.6).
- Labels: unigram/bigram tokens make poor individual labels (S1 §1.2). oshfdk adds that the verbosity is too high for meaningful labels (F1).
- Per H: no position-specific glyphs or words at line starts, and unigram/bigram parsing ambiguity remains.
- Live Science, via Newsweek: the author says it is almost certainly not how the manuscript was made (N).

## 6. Line edges, edge coupling, vocabulary size
- Line edges: the author concedes these are not modelled (F1, H). The deck reset per line in code is not a positional rule (GH).
- Edge coupling (cross-space dependence between the end of one word and the start of the next): **not discussed in any source I reached**. Unigram/bigram respacing and independent card draws give no reason to expect it. That is my inference.
- Vocabulary: the 78-card, 32,000-letter Latin ciphertext has 3,679 word types within one edit of the 1,200 commonest (S1 Fig. 1). No total type count was seen. The type count is bounded by 138 unigram types plus up to 19,044 bigram types (H, arithmetic).

## 7. Comparison with our runs
Our runs: results_c4.txt and results_f3.txt, on Zenodo 17219445's cached Four-Text Sampler ciphertext, 20,923 tokens.
- **h2 2.08** (c4, Naibbe) vs 2.09–2.11 (our Voynich). No paper number to compare against. This is consistent with the author's claim to match conditional entropy. **No contradiction found, but not checked against the main text.**
- **No line-edge effect** (c4: JSD first/last ≈ null; p-init ×0.8–0.9, m-final ×1.0–1.1) **agrees** with the author's own concession (F1, H).
- **Coupling ~1 % of Voynich** (c4: EVA excess +0.0018–0.0022 vs +0.1809) is **not contradicted**, since no source addresses it.
- **Repeat rate**: our 0.18–0.19 % (c4) **matches** S1's 0.18 ± 0.04 % exactly. Our Voynich 0.87 % sits inside S1's 0.8–0.9 %.
- **Hapax 0.48** (f3) **matches** S1's "about half". Note: our Voynich hapax of 0.68 is computed on the whole manuscript, while the paper's comparison is to Voynich B, so the two are not comparable as is.
- **23 letters and a median of 6 homophones per unigram letter** (f3) **match** S1 Table 2 and GH.
- Our Naibbe mean word length of 5.26 vs our Voynich 4.99 has no paper number to compare against. **Unverified.**

Net: no number from the sources reached contradicts results_c4 or results_f3. Two of our numbers (repeat rate, hapax share) independently reproduce the supplement.
