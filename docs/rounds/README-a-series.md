> Current map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). The tables below are the a-series only. Later measurements live in `results_*.txt`.

# Voynich manuscript: a decipherment attempt with controls

Run 2026-10-17. **Result: not deciphered.** Every test below was run against
natural-language controls processed the same way. The solver was required to
crack a known cipher before its Voynich output was read.

## Data

- `data/ZL3b-n.txt`: Zandbergen–Landini EVA transliteration v3b (13/05/2025), voynich.nu.
  Parsed by `vparse.py`: 5,385 lines, 39,020 tokens, 8,295 types. Analyses use running-text
  units (P*) only. Tokens containing unreadable glyphs are dropped.
- `data/controls/`: Project Gutenberg texts — Caesar *De Bello Gallico*, Augustine
  *Confessiones* (Latin), Dante *Commedia* (Italian), Goethe *Faust*, Kafka *Verwandlung*
  (German), Carroll *Alice* (English). They are lowercased, accent-stripped, letters only.

Each script `aN_*.py` writes `results_aN*.txt`. Run with `python aN_*.py` from this folder.

## Findings

### 1. The text is far too predictable at the character level (`a1_profile.py`)

All samples are 25k tokens.

| | h2 (bits) | word-length SD | immediate word repeat | top-10 words share |
|---|---|---|---|---|
| Voynich (EVA) | **2.13** | **1.76** | **0.90 %** | 13.8 % |
| Latin, Italian, German, English | 3.11–3.30 | 1.95–2.91 | 0.00–0.16 % | 13–26 % |

Vocabulary size, hapax rate and the Zipf slope (−1.05) all fall inside the natural-language
range. The character-level behaviour does not. Collapsing EVA digraphs (ch, sh, cth, …) into
single glyphs only raises h2 to 2.26–2.40.

### 2. The line is a structural unit (`a2_position.py`)

Comparing line-initial words with mid-line words gives a first-glyph JSD of 0.176, against a
shuffle null of 0.002. Dante and Faust verse score 0.034. Line-initial `p` is 17.9×
over-represented and `t` 5.1×. Line-final `m` is 16× and `g` 25×. 86 % of page-first lines open
with a gallows glyph (p/f alone 48 %), against 19 % of other lines. Line position shapes word
form more strongly than metre and rhyme do in verse.

### 3. Labels: weak or no reference signal (`a3_labels.py`)

A label word appears in its own page's text 12.1 % of the time. The null, which permutes labels
within a section, gives 10.7 ± 1.0 % (p ≈ 0.11, 40 pages). Rare vocabulary does cluster on nearby
pages (herbal: Jaccard 1.55× adjacent vs distant). That fits topical content, but it also fits
gradual drift in a generating process, so it doesn't decide anything.

### 4. Copy-with-mutation is present but modest (`a4_selfcite.py`, `a4b_selfcite_matched.py`)

This measures how often a word is one edit away from a word in the previous 10. The "far"
comparison windows are matched on Currier language, section and hand:

| | d=1 local/far | d≤1 local/far |
|---|---|---|
| Voynich (matched, W=10) | **1.30** | **1.39** |
| Controls (W=10) | 0.93–1.13 | 0.95–1.33 |

This favours the Timm–Schinner self-citation idea, where words are copied from nearby words with
small changes. But the effect is only somewhat above Augustine and Faust, and with a W=40 window
it shrinks to 1.08. Without the language/section matching the ratio looks larger (1.24), so that
matching matters to the result.

### 5. A letter-level verbose cipher gives words that are too short (`a5_verbose.py`)

A verbose cipher writes each plaintext letter as several glyphs. To test it, glyph pairs were
merged greedily (BPE) until h2 reached the Latin level (~3.2–3.3). That takes about 28–32 merges,
which leaves an inventory of about 53–57 units at **2.5–2.6 units per word**. Latin averages 5–6
letters per word. If each Voynich word is a plaintext word, the units behave like syllables or
code fragments, not letters.

### 6. Homophonic decipherment into Latin, Italian, German: negative (`a6_solver.py`, `a6b_calibrate.py`)

The solver uses simulated annealing over many-to-one unit→letter keys. It scores against a
character-trigram language model plus a letter-frequency penalty. It gets 2,500-word samples at
three segmentation levels (k = 0, 8, 20 BPE merges).

- **Positive control:** Caesar enciphered with a random 21-symbol homophonic key. Recovery is
  100 % (the first version failed this check and was fixed before any Voynich result was used).
- Scores are mean log₂ P per character; higher is better:

| LM | k | Voynich | pseudo-Voynich null | same-language ceiling | real wrong-language text |
|---|---|---|---|---|---|
| Latin | 0 / 8 / 20 | −3.89 / −3.75 / −4.01 | −4.18 / −3.81 / −4.07 | −3.06 | −3.76 … −4.37 |
| Italian | 0 / 8 / 20 | −3.86 / −3.84 / −3.78 | −4.26 / −3.88 / −3.74 | −2.77 … −2.80 | −4.23 … −4.60 |
| German | 0 / 8 / 20 | −4.15 / −3.91 / −4.22 | −4.27 / −4.03 / −4.34 | −2.52 … −2.60 | −4.19 … −4.49 |

The null is meaningless text sampled from Voynich's own unit-trigram model. Voynich ends up
0.7–1.7 bits/char below every ceiling, which is where a real text in the wrong language lands.
From k=8 up it is within ~0.1 bit of the null, and under the Italian LM at k=20 it scores slightly
worse. Its best "readings" (e.g. `putia inur um unullo ater atemi`) are noise.

**Ruled out within this test's scope:** a simple or homophonic substitution, letter-for-unit,
of Latin, Italian or German, with Voynich word breaks kept.

### 7. Weak law of abbreviation (`a7_abbrev.py`)

The frequency–length correlation is −0.25 for Voynich and −0.34 to −0.41 for controls. Voynich's
50 most frequent words are 82 % of mean token length, against 60–77 %. Natural languages lean on
short, very frequent function words; Voynich largely doesn't have them.

## What this adds up to

Here are the observations side by side:

- Character entropy is very low.
- Word lengths are unusually uniform.
- Words often repeat.
- Line-edge glyphs are strongly over-represented.
- Function words are missing.
- Near-copy locality is somewhat elevated.
- No simple-substitution reading reaches a European language.

A text written in a known European language and enciphered letter by letter does not fit this
pattern. Two families remain compatible with every measurement here:

1. **Constructed or generated text.** This would be a slot grammar or a copy-and-mutate process
   (Rugg, Timm–Schinner), with layout rules at line starts and ends. Points 2, 4 and 7 lean this
   way.
2. **A non-alphabetic encoding of real language.** This could be a syllabic or abbreviation-based
   script, a nomenclator/codebook, or a verbose cipher whose Voynich "words" are not plaintext
   words. Point 5 and the natural-range Zipf and vocabulary figures keep this open. None of these
   tests can refute it, because a codebook removes exactly the letter statistics they measure.

My reading is that (1) fits more of the evidence and needs fewer extra assumptions. I'm not claiming
that as a finding: no test here separates the two families decisively.

## Limits (what would change these conclusions)

- **Languages tested:** only Latin, Italian and German, against one trigram LM each. Hebrew,
  Arabic, Czech, Occitan, Greek and others were not tested. Neither were abjad readings
  (no vowels written).
- **Cipher families tested:** only substitution with Voynich spacing kept. Transposition, null
  glyphs, unreliable word breaks and word-level codes were not tested.
- **Labels test:** only 40 pages, so its statistical power is low.
- **Alignment:** the line-position comparison uses verse controls. A prose text with preserved line
  breaks would be a better control. The "paragraph start" figure is approximated as the first line
  of each page.
