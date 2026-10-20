# Audit: Layfield & Davis 2026 Table 5 and scribe map vs VKB; impact on s120

Written 2026-10-18 21:39:43 PDT (from `date`). Read-only audit; this file is the only project write.

Source: Layfield & Davis 2026, *Digital Medievalist* 19, https://journals.openedition.org/digitalmedievalist/2331.
Fetched twice with WebFetch, 2026-10-18 ~21:37 PDT. WebFetch passes the page through a summarising model; the numbers below agreed across both fetches. A direct curl got an Anubis bot-challenge page, so **no byte-level copy of the HTML is on disk** and the quotes are not checked against a raw copy. The page states "The text only may be used under licence CC BY 4.0" (second fetch). That updates the "licence unverified" line in reports/Voynich public source gaps.md, but only as relayed by WebFetch.

## 1. Table 5 (section "Manuscript Structure") as fetched

Q1 1|8 2|7 3|6 4|5; Q2 9|16 10|15 11|14 [12]|13; Q3 17|24 18|23 19|22 20|21; Q4 25|32 26|31 27|30 28|29; Q5 33|40 34|39 35|38 36|37; Q6 41|48 42|47 43|46 44|45; Q7 49|56 50|55 51|54 52|53; Q8 57|66 58|65 [59|64] [60|63] [61|62]; Q9 67|68; Q10 69|70; Q11 71|72; Q12 73|[74]; Q13 75|84 76|83 77|82 78|81 79|80; Q14 85|86; Q15 87|90 88|89; [Q16 91|92 lost]; Q17 93|96 94|95; [Q18 97|98 lost]; Q19 99|102 100|101; Q20 103|116 104|115 105|114 106|113 107|112 108|111 [109|110].
(The summariser garbled the Q15 to Q18 rows. The reading above uses the collation formula in the report and research_notes/Voynich public source gaps/physical_codicology.md line 12. It matches that note's Table 5 transcription.)

Scribe statements (para. 9 and fn. 4): "with only two exceptions (bifolia 57|66 and 85|86), all four pages of each of the fifty-two extant bifolia were written by a single scribe (Davis, 2020)." "All four pages of bifolium 26|31 (26r, 26v, 31r, and 31v) were written by Scribe 2." "The other three bifolia were entirely written by Scribe 1." Fn. 4: "There is also one page - 115r - on which two scribes (2 and 3) collaborated." Table 1 (section level, per physical_codicology.md line 90): Rose = scribes 2 and 4; Stars = scribes 3 and 2. The paper does not say which scribes share 57|66 (unverified; it would be in Davis 2020, not opened).

## 2. Discrepancy table (VKB `folios` vs Table 5 / paper)

Comparison script: scratchpad `t5/code/cmp.py` (read-only sqlite). The VKB quires A-T map one-to-one onto Table 5 quires 1-20 (P and R are absent, i.e. lost quires 16 and 18).

| # | Leaf/page | VKB | Table 5 / paper | Kind | In s120 analysis? |
|---|---|---|---|---|---|
| 1 | f13 (r, v) | conjugate NULL | [12]\|13: f12 lost | conjoint (coding of a lost partner) | f13r and f13v are in the analysis set (>=50 tokens, cell 1\|H). No pair with f12 exists, so no conjugate pair is lost. **Not affected** |
| 2 | f73 (r, v) | conjugate NULL | 73\|[74]: f74 lost | conjoint (lost partner) | f73 has no page with >=50 tokens in ZL3b. No f74 exists. **Not affected** |
| 3 | 85\|86 (f85r1, f85r2, f86v3-6) | hand 2 on every numbered page; fRos = hand 4 | mixed-scribe bifolio; Rose = scribes 2 and 4 | hand. VKB puts scribe 4 only on fRos, which has no leaf number | f85r1, f86v5 and f86v6 are kept (cell 2\|T). Every different-leaf pair in quire N is conjugate, so no stratum has a non-conjugate partner. fRos is dropped (no leaf number). **Not in the used set** |
| 4 | 57\|66 | f57r=5, f57v=1, f66r=5, f66v=5 (mixed) | mixed-scribe bifolio | agrees (VKB is mixed); paper's scribe split unverified | f57r and f66v are kept (5\|H). The pair is not among the 35 used leaf pairs (no informative stratum). **Not in the used set** |
| 5 | f115r | hand 3 | scribes 2 and 3 on one page | hand (VKB gives one label) | **In the used set**: f104/f115 is one of the 35 leaf pairs, and f115r is in the analysis set on all three transliterations |
| 6 | Stars section | hand 3 only (section S) | Table 1: scribes 3 and 2 | hand, section level. Scribe 2 in Stars is probably f115r only (unverified; the 2020 folio table was not read) | same as row 5 |

No leaf pairs differently: apart from the two lost partners, every VKB conjugate equals Table 5. Every other bifolio has one VKB hand. Quire 4 matches the paper's example (26|31 = 2; 25|32, 27|30, 28|29 = 1). Refuter not checked: a page-level hand that differs inside a bifolio the paper calls single-scribe, which only the Davis 2020 folio table would show (not opened).

## 3. Impact on s120

- s120 used 35 conjugate leaf pairs and 108 page pairs on each transliteration (`results_s120_20261018_211618.txt`). None of the conjoint discrepancies (rows 1-2) can enter a pair. Substituting Table 5 conjoints changes only the conj field of f13r, f13v, f73r and f73v.
- Descriptive rerun, not a result and not a run id. The hashed script was copied unchanged (sha256 7f16b420...5f612, matches the stub) to scratchpad `t5/code/s120_copy.py`. The driver `t5/code/drive.py` computes only the real statistic and its B = 10,000 permutation null (same seeds), with no gates and no results file. Output: `<home>/AppData/Local/Temp/claude/<agent-project>/<session>/scratchpad/t5/drive_out.txt` (temporary).

| Variant | ZL3b T / p_more | RF1b T / p_more | IT2a T / p_more | K (page pairs) |
|---|---|---|---|---|
| VKB (reproduces s120) | -0.1540 / 0.00010 | -0.1546 / 0.00010 | -0.1623 / 0.00010 | 108 |
| Table 5 conjoints | -0.1540 / 0.00010 | -0.1546 / 0.00010 | -0.1623 / 0.00010 | 108 |
| Table 5 + f115r dropped | -0.1507 / 0.00010 | -0.1522 / 0.00010 | -0.1604 / 0.00010 | 106 |
| Table 5 + f115r relabelled hand 2 | identical to dropped (a 2\|S cell has < 3 pages) | | | 106 |

p_less = 1.00000 in every row. **Conclusion: Table 5 does not change s120. The f115r two-scribe page moves T by about 0.002-0.003, and p stays at the permutation floor.**

## 4. Layfield & Davis's own within-bifolium numbers (F-51's external line)

Method (paras. 12, 22-23, 27-28, fn. 12, para. 46): LSA; Voynich pages split into documents of "approximately size 40"; TF-IDF weighting; k = 75; "We use cosine as the comparison/scoring operator". Scores are page-level; conjoint = "first verso vs. second recto". Tests (para. 43, fn. 15): Shapiro-Wilk and D'Agostino-Pearson for normality, then "The independent samples t-test (parametric) and the Mann Whitney test (non-parametric) are used to compare mean scores between two independent samples (e.g. Facing vs Conjoint)". The threshold is p < 0.05. Pairs are treated as independent. No effect size beyond mean cosines, no CI, no multiple-comparison correction.

- **Table 10** ("Aberdeen Bestiary/Speculum/Voynich Overall Confoliate, Facing and Conjoint Average Scores"), Voynich: confoliate 0.383, facing 0.298, **conjoint 0.433** (Aberdeen 0.428/0.398/0.207; Speculum 0.398/0.398/0.277).
- **Table 11** ("Statistical Test Results for Overall Aberdeen Bestiary, Speculum and Voynich Quire Comparisons"), Voynich p: conf/facing **0.005**, conf/conj **0.168**, facing/conj **0.000**.
- **Table 12** ("Overall Bifolum 1st Confoliate, Conjoint, and 2nd Confoliate Averages"), Voynich: 0.395 / **0.431** / 0.374 (conjoint 0.433 in Table 10 vs 0.431 here, as printed).
- **Table 13** ("Statistical Test Results for Bifolium Ordering"), Voynich p: 1st confol./conjoint **0.283**, 1st/2nd confol. 0.872, conjoint/2nd confol. **0.148**.
- **Table 8** (Voynich quire conjoint averages): Q1 0.399, Q2 0.206, Q3 0.394, Q4 0.296, Q5 0.430, Q6 0.448, Q7 0.336, Q13 0.603, Q20 0.600.
- Para. 40: the central-conjoint effect "was observed only inconsistently, in three of nine quires." Para. 49: "the average conjoint score for the Voynich is quite high and compares favorably to the respective confoliate values". Para. 56: "The confoliate/conjoint scores behave in a similar way, with no significant difference between them."

**What this means for F-51's external line.** The paper's only significant conjoint contrast is conjoint above *facing* pages (0.433 vs 0.298, p 0.000, Table 11). Conjoint vs confoliate (same leaf) is **not significant** (p 0.168, Table 11; 0.283 and 0.148, Table 13). The paper does not compare conjoints with same-quire pages at matched bound distance, which is s120's contrast, and it does not control for hand or section. So "confirms Layfield & Davis 2026" in the F-51 title is a direction-level agreement with their conjoint > facing result, on a different baseline and with no hand or section control. It is not a replication of a matched contrast. Their p-values also treat overlapping page pairs as independent. The external line can drop `unverified` for the numbers, keeping the caveat that they come through WebFetch only, but it should name the facing baseline. This audit does not edit FINDINGS-GRAPH.yaml.
