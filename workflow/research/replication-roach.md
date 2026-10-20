# Independent replication on the second machine (roach): R1 line-initial profile, R2 across-space coupling

Recorded 2026-10-17 22:34 PDT by voynich-08 from the replication session's status report, which Jon pasted at 22:33. The
session was stopped for compute before it wrote its own REPORT.md, so this file is that report. The source files stay on
the other machine at <home>/voynich-replication: results_r1.txt and results_r2.txt (both finished, stubs matched),
scripts/prep.py and PREREG_LOG.txt. They have not been copied here, so every number below is as the replication session
reported it, unverified against its files by this session. The replication used public sources only and its own code, and
by design it never read this project's tree.

## Data
| source | file | size | sha256 (start) |
|---|---|---|---|
| ZL | voynich.nu/data/ZL3b-n.txt (v3b, 13/05/2025) | 411,671 B | bf5b6d4a… |
| IT | voynich.nu/data/IT2a-n.txt | 342,104 B | 7f27a8b0… |
| RF | voynich.nu/data/RF1b-e.txt (EVA "full", not -er) | 362,373 B | e7d3238e… |
| CREMMA Medii Aevi v0.1.2 | XML + metadata from the GitHub tag commit 9439fe33… cited by Zenodo 8407213 (Zenodo zip 356.7 MB was over the 200 MB limit) | 12.4 MB | manifest c3222ed9… (47 files) |
| Dante | Gutenberg #1000, one verse per line | 597,903 B | 4669dcc0… |

Fifteenth-century rule: notBefore ≥ 1400 and notAfter ≤ 1499 in data-registry.csv → 7 manuscripts, with genres fixed
before the run. Prose: PalLat373, Laur. 53.08, Laur. 53.09. Formulaic: SBB Hdschr25 (Book of Hours), BGO-511 (penitential
psalms). Verse: Laur. 39.34 (Priapea), Latin8236 (Prudentius/Tibullus).

## R1, the line-initial profile: PASS
| corpus | lines | excess (bits) |
|---|---|---|
| Voynich ZL / IT / RF | ~4,040 | +0.175 / +0.173 / +0.185 |
| ZL Currier A / B | 1,515 / 2,449 | +0.137 / +0.221 |
| pooled prose | 768 | +0.005 |
| prose manuscripts | 125–427 | +0.005, +0.007, +0.017 |
| verse / formulaic manuscripts | 39–212 | +0.001 to +0.066 |
| Dante | 14,233 | +0.030 |
At matched size (773 lines, 200 draws), ZL gives +0.175 [+0.155, +0.198], with IT and RF the same. The lead session's
predictions held: Voynich about +0.17, prose pool about +0.01, and no prose manuscript above +0.05. The side prediction that
verse at 100–200 lines reaches +0.10 to +0.14 did not appear in this selection, where the maximum was +0.066. This session's
s18/s32 rows that reached +0.13 to +0.14 came from LaurPlut33.31 and Egerton821, and neither is in the replication's
seven manuscripts.

## R2, across-space coupling A vs B: marginal, not robust
| corpus | excess (bits) |
|---|---|
| ZL all / A / B | +0.181 / +0.119 / +0.234 |
| IT all / A / B | +0.168 / +0.101 / +0.218 |
| RF all / A / B | +0.177 / +0.108 / +0.231 |
| prose manuscripts / prose pool | +0.026 to +0.060 / +0.028 |
| formulaic manuscripts | −0.085 (BGO-511, 114 pairs), +0.038 |
| verse manuscripts | +0.227 (Priapea, Laur. 39.34), +0.169 (Latin8236) |
| all-Latin pool / Dante | +0.037 / +0.097 |
B against the controls: ZL B beats the highest control by only +0.007, IT B fails (+0.218 < +0.227), and RF passes. A is
inside the control range, but that range runs from −0.085 to +0.227, so the test is weak; A is above every prose control.
The lead session's "controls below +0.13" and "clear margin" were NOT reproduced. Post hoc (labelled): cut to 116 lines, the
Priapea's size, Voynich B's 95 % range is +0.171 to +0.260 and contains +0.227, so at matched size B cannot be told apart
from that verse manuscript.

## Deviations the replication declared
1. Before any statistic ran, it fixed the page regex in prep.py, which had skipped page fRos. The script was re-hashed and the change logged in PREREG_LOG.txt.
2. It treated the comma (uncertain space) as a word break. Treating the comma as no break lowers R2 (ZL B +0.195, A +0.081) and leaves R1 almost unchanged.
3. Voynich: paragraph loci only. @NNN; codes count as one character each. [a:b] readings take the first option. ? is kept as a character.
4. Latin: normalised (chocomufin) files with combining marks removed, so abbreviation marks are dropped. Punctuation is deleted, not spaced. Main-zone default lines only.
5. Its prose pool has 768 lines against the lead's 773, probably the same three manuscripts with slightly different filtering (unverified).

## Cross-check against this project's own files (voynich-08, 22:34)
This project's per-manuscript CREMMA rows show the same thing. They were excluded from the s20 range by its 5,000-token
floor (results_s20.txt line 6):
| manuscript | tokens | cross_excess_eva | file |
|---|---|---|---|
| LaurPlut33.31 (Priapea) | 1,267 | 0.248 | results_s18_cremma_LaurPlut33.31.json |
| LaurPlut39.34 (Priapea) | 770 | 0.209 | results_s18_cremma_LaurPlut39.34.json |
| Latin8236 | 1,403 | 0.178 | results_s18_cremma_Latin8236.json |
| Egerton821 (Sortes/charms) | 1,088 | 0.160 | results_s18_cremma_Egerton821.json |
| Voynich B (s20) | ~23k | 0.232 | results_s20.txt |
So the claim "B above every real-line row" holds only for pooled rows of 6,900 tokens or more. Short Latin verse
manuscripts reach B or pass it. Plug-in MI excess at about 1k tokens may still carry small-sample inflation that the
within-line null does not remove (unverified). The open comparison is a matched-size Voynich B draw against these rows,
pre-registered, which the replication ran only post hoc.

## Raw files (2026-10-18 02:31 PDT)
Roach's raw files (results_r1.txt, results_r2.txt, prep.py, PREREG_LOG.txt, REPORT.md) are copied unchanged into
runs/roach-r1r2-raw/ from a shared folder on roach; all five match MANIFEST.sha256. REPORT.md section 7 lists definition
differences to reconcile (comma rule: R2 B +0.234 with commas as spaces vs +0.195 without; chocomufin Latin normalisation;
the R2 control set includes two verse manuscripts; 768 vs 773 matched lines). These do not change A3's downgraded status.
prep.py is kept as data and was not executed.
