# Beinecke MS 408 — Folio-by-Folio Empirical Evidence Inventory

**Generated**: `2026-10-17` by `tools/build_folio_inventory.py`  
**Machine-readable full table (all 226 transcribed folios)**: [`data/folio_evidence_inventory.tsv`](../data/folio_evidence_inventory.tsv)  
**Policy**: Tracks verified codicological metadata (`quire`, `bifolio`, `section`, `hand`, `Currier language`), measured token/label/entropy/boundary statistics, coordinate bounding boxes (`223` folios), blind direct-pixel ink-gap measurements (`286` QC sites across 6 pilot folios), local Yale IIIF facsimiles (`6` high-res canvases), and external crib files (`data/external/cribs/`). **No page is assigned an unverified translation.**

---

## 1. Section-Level Inventory Summary (All 226 Folios in `ZL3b-n.txt`)

| Section Code (`$I`) | Description | Folios | Running Tokens (`P*`) | Label/Ring Tokens (`L*/C*/R*`) | Blind Direct-Pixel Sites | Folios with Local Crib Files |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| **`A`** | Astronomical | 8 | 279 | 604 | 0 | 3 |
| **`B`** | Biological / Balneological | 19 | 6,260 | 127 | 0 | 0 |
| **`C`** | Cosmological / Rosettes | 11 | 703 | 1,552 | 0 | 1 |
| **`H`** | Herbal (A & B) | 129 | 11,545 | 37 | 283 | 110 |
| **`P`** | Pharmaceutical | 16 | 2,339 | 250 | 0 | 0 |
| **`S`** | Starred Recipes / Text-Only | 25 | 11,646 | 0 | 0 | 0 |
| **`T`** | Text-Only | 7 | 2,297 | 65 | 0 | 1 |
| **`Z`** | Zodiac Medallions | 12 | 0 | 1,316 | 0 | 12 |

---

## 2. High-Priority Anchor Folios (Direct-Pixel Pilots, Facsimiles, & Special Structural Pages)

| Folio | Quire/Bifolio | Sec / Lang / Hand | `P*` Tok / Types | `L*/C*` Tok | `h2` | Para Gallows | `m`-Final Lines | Box File | Direct-Pixel Sites | Facsimile | Crib / Structural Role |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **`f1r`** | Q`A` / F`a` | `T` / `A` / H`1` | 215 / 167 | 0 | 2.073 | 1/1 | 1/28 | `f1r.js` | 0 | `-` | Standard folio |
| **`f1v`** | Q`A` / F`a` | `H` / `A` / H`1` | 92 / 70 | 0 | 1.893 | 1/1 | 1/10 | `f1v.js` | 0 | `f1v.jpg` | Standard folio |
| **`f7v`** | Q`A` / F`y` | `H` / `A` / H`1` | 78 / 59 | 0 | 1.764 | 1/1 | 0/9 | `f7v.js` | 36 (36c/0u) | `-` | Standard folio |
| **`f14v`** | Q`B` / F`x` | `H` / `A` / H`1` | 75 / 59 | 0 | 1.755 | 1/1 | 1/9 | `f14v.js` | 30 (24c/6u) | `-` | Standard folio |
| **`f23r`** | Q`C` / F`y` | `H` / `A` / H`1` | 110 / 80 | 0 | 1.839 | 1/1 | 0/11 | `f23r.js` | 59 (55c/4u) | `-` | Standard folio |
| **`f39v`** | Q`E` / F`y` | `H` / `B` / H`2` | 146 / 106 | 0 | 1.871 | 1/1 | 1/14 | `f39v.js` | 76 (73c/3u) | `-` | Standard folio |
| **`f42v`** | Q`F` / F`b` | `H` / `A` / H`1` | 116 / 96 | 0 | 1.907 | 0/1 | 1/16 | `f42v.js` | 31 (29c/2u) | `-` | Standard folio |
| **`f56v`** | Q`G` / F`z` | `H` / `A` / H`1` | 91 / 67 | 0 | 1.588 | 1/1 | 0/16 | `f56v.js` | 51 (45c/6u) | `-` | Standard folio |
| **`f57v`** | Q`H` / F`a` | `C` / `?` / H`1` | 0 / 0 | 198 | - | 0/0 | 0/0 | `f57v.js` | 0 | `f57v.jpg` | 4-ring wheel; Ring 3 exact 13-box / 17-unit 4x cycle (p=0.000) |
| **`f68r1`** | Q`I` / F`z` | `A` / `?` / H`4` | 31 / 31 | 34 | 1.896 | 0/2 | 1/7 | `f68r1.js` | 0 | `f68r.jpg` | Star-diagram foldout; Bax/Stolfi star-label cribs |
| **`f68r2`** | Q`I` / F`z` | `A` / `?` / H`4` | 37 / 36 | 45 | 1.818 | 1/1 | 1/5 | `f68r2.js` | 0 | `f68r.jpg` | Star-diagram foldout; Bax/Stolfi star-label cribs |
| **`f68r3`** | Q`I` / F`z` | `A` / `?` / H`4` | 0 / 0 | 106 | - | 0/0 | 0/0 | `f68r3.js` | 0 | `f68r.jpg` | Star-diagram foldout; Bax/Stolfi star-label cribs |
| **`f70v2`** | Q`J` / F`z` | `Z` / `?` / H`4` | 0 / 0 | 131 | - | 0/0 | 0/0 | `f70v2.js` | 0 | `-` | Zodiac medallion + ~30 nymph star labels + Romance month gloss |
| **`f70v1`** | Q`J` / F`z` | `Z` / `?` / H`4` | 0 / 0 | 86 | - | 0/0 | 0/0 | `f70v1.js` | 0 | `-` | Zodiac medallion + ~30 nymph star labels + Romance month gloss |
| **`f72v2`** | Q`K` / F`z` | `Z` / `?` / H`4` | 0 / 0 | 108 | - | 0/0 | 0/0 | `f72v2.js` | 0 | `-` | Zodiac medallion + ~30 nymph star labels + Romance month gloss |
| **`f75r`** | Q`M` / F`a` | `B` / `B` / H`2` | 418 / 203 | 0 | 1.698 | 1/2 | 7/53 | `f75r.js` | 0 | `f75r.jpg` | Balneological/biological pools & ducts; peak qo-/-edy density |
| **`f85r1`** | Q`N` / F`a` | `T` / `B` / H`2` | 347 / 239 | 0 | 1.954 | 1/1 | 13/35 | `f85r1.js` | 0 | `-` | Rosettes 6-panel cosmological foldout (Ghibelline merlons) |
| **`f86v4`** | Q`N` / F`z` | `C` / `B` / H`2` | 49 / 37 | 142 | 1.719 | 1/1 | 1/5 | `f86v4.js` | 0 | `-` | Rosettes 6-panel cosmological foldout (Ghibelline merlons) |
| **`f99r`** | Q`S` / F`a` | `P` / `A` / H`1` | 158 / 114 | 36 | 1.931 | 4/4 | 2/18 | `f99r.js` | 0 | `f99r.jpg` | Pharmaceutical jars (albarelli) + roots + recipes |
| **`f116v`** | Q`T` / F`z` | `T` / `?` / H`3` | 0 / 0 | 2 | - | 0/0 | 0/0 | `-` | 0 | `f116v.jpg` | Marginalia charm w/ embedded Voynich 'oror sheey'; 2024 MSI |

---

## 3. Complete 226-Folio Register

| Folio | Quire | Bifolio | Sec | Lang | Hand | `P*` Tok | `P*` Types | `L*/C*` Tok | `h2` | Para Gallows | `m`-Final | Box File | Direct-Pixel | Crib Sources |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- |
| `f1r` | A | a | T | A | 1 | 215 | 167 | 0 | 2.073 | 1/1 | 1/28 | `f1r.js` | 0 | - |
| `f1v` | A | a | H | A | 1 | 92 | 70 | 0 | 1.893 | 1/1 | 1/10 | `f1v.js` | 0 | sherwood_botanical_index |
| `f2r` | A | b | H | A | 1 | 101 | 80 | 4 | 1.856 | 1/1 | 0/13 | `f2r.js` | 0 | sherwood_botanical_index |
| `f2v` | A | b | H | A | 1 | 61 | 47 | 0 | 1.562 | 1/1 | 0/8 | `f2v.js` | 0 | sherwood_botanical_index |
| `f3r` | A | c | H | A | 1 | 114 | 89 | 0 | 1.864 | 1/1 | 6/20 | `f3r.js` | 0 | sherwood_botanical_index |
| `f3v` | A | c | H | A | 1 | 85 | 75 | 0 | 1.982 | 1/1 | 3/14 | `f3v.js` | 0 | sherwood_botanical_index |
| `f4r` | A | d | H | A | 1 | 64 | 48 | 0 | 1.568 | 1/1 | 2/13 | `f4r.js` | 0 | sherwood_botanical_index |
| `f4v` | A | d | H | A | 1 | 84 | 72 | 0 | 1.745 | 1/1 | 1/14 | `f4v.js` | 0 | sherwood_botanical_index |
| `f5r` | A | w | H | A | 1 | 54 | 45 | 0 | 1.708 | 1/1 | 0/7 | `f5r.js` | 0 | sherwood_botanical_index |
| `f5v` | A | w | H | A | 1 | 48 | 38 | 0 | 1.552 | 1/1 | 0/6 | `f5v.js` | 0 | sherwood_botanical_index |
| `f6r` | A | x | H | A | 1 | 86 | 68 | 0 | 1.859 | 1/1 | 4/14 | `f6r.js` | 0 | sherwood_botanical_index |
| `f6v` | A | x | H | A | 1 | 116 | 90 | 0 | 1.972 | 1/1 | 3/21 | `f6v.js` | 0 | sherwood_botanical_index |
| `f7r` | A | y | H | A | 1 | 66 | 60 | 0 | 1.797 | 1/1 | 0/10 | `f7r.js` | 0 | sherwood_botanical_index |
| `f7v` | A | y | H | A | 1 | 78 | 59 | 0 | 1.764 | 1/1 | 0/9 | `f7v.js` | 36 (36c/0u) | sherwood_botanical_index |
| `f8r` | A | z | H | A | 1 | 151 | 120 | 0 | 1.956 | 1/1 | 4/21 | `f8r.js` | 0 | sherwood_botanical_index |
| `f8v` | A | z | H | A | 1 | 118 | 88 | 0 | 1.783 | 0/1 | 2/17 | `f8v.js` | 0 | sherwood_botanical_index |
| `f9r` | B | a | H | A | 1 | 85 | 75 | 0 | 1.939 | 1/1 | 1/10 | `f9r.js` | 0 | sherwood_botanical_index |
| `f9v` | B | a | H | A | 1 | 86 | 67 | 0 | 1.856 | 1/1 | 1/12 | `f9v.js` | 0 | sherwood_botanical_index |
| `f10r` | B | b | H | A | 1 | 92 | 72 | 0 | 1.785 | 1/1 | 2/12 | `f10r.js` | 0 | sherwood_botanical_index |
| `f10v` | B | b | H | A | 1 | 57 | 41 | 0 | 1.534 | 1/1 | 0/7 | `f10v.js` | 0 | sherwood_botanical_index |
| `f11r` | B | c | H | A | 1 | 59 | 43 | 0 | 1.632 | 1/1 | 0/7 | `f11r.js` | 0 | sherwood_botanical_index |
| `f11v` | B | c | H | A | 1 | 49 | 44 | 1 | 1.802 | 1/1 | 0/6 | `f11v.js` | 0 | sherwood_botanical_index |
| `f13r` | B | w | H | A | 1 | 77 | 61 | 0 | 1.692 | 1/1 | 0/10 | `f13r.js` | 0 | sherwood_botanical_index |
| `f13v` | B | w | H | A | 1 | 69 | 58 | 0 | 1.833 | 1/1 | 0/10 | `f13v.js` | 0 | sherwood_botanical_index |
| `f14r` | B | x | H | A | 1 | 76 | 65 | 0 | 1.814 | 1/1 | 0/13 | `f14r.js` | 0 | sherwood_botanical_index |
| `f14v` | B | x | H | A | 1 | 75 | 59 | 0 | 1.755 | 1/1 | 1/9 | `f14v.js` | 30 (24c/6u) | sherwood_botanical_index |
| `f15r` | B | y | H | A | 1 | 94 | 73 | 0 | 1.829 | 1/1 | 1/15 | `f15r.js` | 0 | sherwood_botanical_index |
| `f15v` | B | y | H | A | 1 | 72 | 50 | 0 | 1.585 | 1/1 | 0/12 | `f15v.js` | 0 | sherwood_botanical_index |
| `f16r` | B | z | H | A | 1 | 84 | 72 | 0 | 1.982 | 1/1 | 1/13 | `f16r.js` | 0 | sherwood_botanical_index |
| `f16v` | B | z | H | A | 1 | 76 | 61 | 0 | 1.803 | 1/1 | 0/13 | `f16v.js` | 0 | sherwood_botanical_index |
| `f17r` | C | a | H | A | 1 | 78 | 74 | 2 | 2.021 | 1/1 | 4/12 | `f17r.js` | 0 | sherwood_botanical_index |
| `f17v` | C | a | H | A | 1 | 135 | 106 | 0 | 1.843 | 1/1 | 3/23 | `f17v.js` | 0 | sherwood_botanical_index |
| `f18r` | C | b | H | A | 1 | 84 | 63 | 0 | 1.733 | 1/1 | 1/14 | `f18r.js` | 0 | sherwood_botanical_index |
| `f18v` | C | b | H | A | 1 | 69 | 60 | 0 | 1.791 | 1/1 | 4/10 | `f18v.js` | 0 | sherwood_botanical_index |
| `f19r` | C | c | H | A | 1 | 78 | 51 | 0 | 1.632 | 1/1 | 0/13 | `f19r.js` | 0 | sherwood_botanical_index |
| `f19v` | C | c | H | A | 1 | 78 | 62 | 0 | 1.736 | 1/1 | 3/14 | `f19v.js` | 0 | sherwood_botanical_index |
| `f20r` | C | d | H | A | 1 | 89 | 79 | 0 | 1.701 | 1/1 | 0/13 | `f20r.js` | 0 | sherwood_botanical_index |
| `f20v` | C | d | H | A | 1 | 86 | 69 | 0 | 1.878 | 1/1 | 0/11 | `f20v.js` | 0 | sherwood_botanical_index |
| `f21r` | C | w | H | A | 1 | 104 | 80 | 0 | 1.866 | 1/1 | 0/12 | `f21r.js` | 0 | sherwood_botanical_index |
| `f21v` | C | w | H | A | 1 | 58 | 43 | 0 | 1.613 | 1/1 | 0/8 | `f21v.js` | 0 | sherwood_botanical_index |
| `f22r` | C | x | H | A | 1 | 111 | 80 | 0 | 1.750 | 1/1 | 2/13 | `f22r.js` | 0 | sherwood_botanical_index |
| `f22v` | C | x | H | A | 1 | 77 | 61 | 0 | 1.699 | 1/1 | 2/16 | `f22v.js` | 0 | sherwood_botanical_index |
| `f23r` | C | y | H | A | 1 | 110 | 80 | 0 | 1.839 | 1/1 | 0/11 | `f23r.js` | 59 (55c/4u) | sherwood_botanical_index |
| `f23v` | C | y | H | A | 1 | 95 | 75 | 0 | 1.880 | 1/1 | 1/12 | `f23v.js` | 0 | sherwood_botanical_index |
| `f24r` | C | z | H | A | 1 | 110 | 85 | 0 | 1.922 | 1/1 | 1/20 | `f24r.js` | 0 | sherwood_botanical_index |
| `f24v` | C | z | H | A | 1 | 85 | 80 | 0 | 2.161 | 1/1 | 4/16 | `f24v.js` | 0 | sherwood_botanical_index |
| `f25r` | D | a | H | A | 1 | 47 | 40 | 0 | 1.581 | 1/1 | 0/7 | `f25r.js` | 0 | sherwood_botanical_index |
| `f25v` | D | a | H | A | 1 | 60 | 45 | 0 | 1.619 | 1/1 | 0/7 | `f25v.js` | 0 | sherwood_botanical_index |
| `f26r` | D | b | H | B | 2 | 90 | 65 | 0 | 1.794 | 1/1 | 0/10 | `f26r.js` | 0 | sherwood_botanical_index |
| `f26v` | D | b | H | B | 2 | 93 | 78 | 0 | 1.815 | 1/1 | 0/9 | `f26v.js` | 0 | sherwood_botanical_index |
| `f27r` | D | c | H | A | 1 | 94 | 63 | 0 | 1.690 | 1/1 | 2/13 | `f27r.js` | 0 | sherwood_botanical_index |
| `f27v` | D | c | H | A | 1 | 61 | 55 | 0 | 1.850 | 1/1 | 0/8 | `f27v.js` | 0 | sherwood_botanical_index |
| `f28r` | D | d | H | A | 1 | 68 | 57 | 0 | 1.782 | 1/1 | 1/9 | `f28r.js` | 0 | sherwood_botanical_index |
| `f28v` | D | d | H | A | 1 | 68 | 50 | 0 | 1.540 | 1/1 | 1/9 | `f28v.js` | 0 | sherwood_botanical_index |
| `f29r` | D | w | H | A | 1 | 65 | 57 | 0 | 1.659 | 1/1 | 1/9 | `f29r.js` | 0 | sherwood_botanical_index |
| `f29v` | D | w | H | A | 1 | 94 | 75 | 0 | 1.824 | 1/1 | 0/12 | `f29v.js` | 0 | sherwood_botanical_index |
| `f30r` | D | x | H | A | 1 | 99 | 84 | 0 | 1.791 | 0/1 | 1/13 | `f30r.js` | 0 | sherwood_botanical_index |
| `f30v` | D | x | H | A | 1 | 63 | 52 | 0 | 1.725 | 0/1 | 0/11 | `f30v.js` | 0 | sherwood_botanical_index |
| `f31r` | D | y | H | B | 2 | 103 | 79 | 0 | 1.764 | 1/1 | 1/16 | `f31r.js` | 0 | sherwood_botanical_index |
| `f31v` | D | y | H | B | 2 | 110 | 97 | 0 | 1.966 | 1/1 | 2/11 | `f31v.js` | 0 | sherwood_botanical_index |
| `f32r` | D | z | H | A | 1 | 76 | 63 | 0 | 1.704 | 1/1 | 1/19 | `f32r.js` | 0 | sherwood_botanical_index |
| `f32v` | D | z | H | A | 1 | 89 | 63 | 0 | 1.649 | 1/1 | 0/11 | `f32v.js` | 0 | sherwood_botanical_index |
| `f33r` | E | a | H | B | 2 | 74 | 60 | 0 | 1.661 | 1/1 | 3/7 | `f33r.js` | 0 | sherwood_botanical_index |
| `f33v` | E | a | H | B | 2 | 114 | 75 | 0 | 1.795 | 1/1 | 2/11 | `f33v.js` | 0 | sherwood_botanical_index |
| `f34r` | E | b | H | B | 2 | 143 | 119 | 0 | 2.039 | 1/1 | 5/15 | `f34r.js` | 0 | sherwood_botanical_index |
| `f34v` | E | b | H | B | 2 | 117 | 92 | 0 | 1.736 | 1/1 | 5/11 | `f34v.js` | 0 | sherwood_botanical_index |
| `f35r` | E | c | H | A | 1 | 94 | 71 | 0 | 1.649 | 0/1 | 0/15 | `f35r.js` | 0 | sherwood_botanical_index |
| `f35v` | E | c | H | A | 1 | 91 | 73 | 0 | 1.752 | 1/1 | 0/21 | `f35v.js` | 0 | sherwood_botanical_index |
| `f36r` | E | d | H | A | 1 | 63 | 56 | 0 | 1.862 | 1/1 | 0/9 | `f36r.js` | 0 | sherwood_botanical_index |
| `f36v` | E | d | H | A | 1 | 76 | 60 | 0 | 1.912 | 1/1 | 1/14 | `f36v.js` | 0 | sherwood_botanical_index |
| `f37r` | E | w | H | A | 1 | 78 | 63 | 0 | 1.725 | 1/1 | 0/11 | `f37r.js` | 0 | sherwood_botanical_index |
| `f37v` | E | w | H | A | 1 | 89 | 66 | 0 | 1.715 | 1/1 | 1/23 | `f37v.js` | 0 | sherwood_botanical_index |
| `f38r` | E | x | H | A | 1 | 44 | 39 | 0 | 1.755 | 1/1 | 0/6 | `f38r.js` | 0 | sherwood_botanical_index |
| `f38v` | E | x | H | A | 1 | 68 | 46 | 0 | 1.527 | 0/1 | 1/8 | `f38v.js` | 0 | sherwood_botanical_index |
| `f39r` | E | y | H | B | 2 | 157 | 119 | 0 | 1.941 | 1/1 | 1/16 | `f39r.js` | 0 | sherwood_botanical_index |
| `f39v` | E | y | H | B | 2 | 146 | 106 | 0 | 1.871 | 1/1 | 1/14 | `f39v.js` | 76 (73c/3u) | sherwood_botanical_index |
| `f40r` | E | z | H | B | 2 | 103 | 77 | 0 | 1.830 | 1/1 | 2/11 | `f40r.js` | 0 | sherwood_botanical_index |
| `f40v` | E | z | H | B | 2 | 105 | 80 | 0 | 1.775 | 1/1 | 2/19 | `f40v.js` | 0 | sherwood_botanical_index |
| `f41r` | F | a | H | B | 5 | 97 | 78 | 0 | 1.798 | 1/1 | 1/11 | `f41r.js` | 0 | sherwood_botanical_index |
| `f41v` | F | a | H | B | 5 | 65 | 57 | 1 | 1.798 | 1/1 | 1/7 | `f41v.js` | 0 | sherwood_botanical_index |
| `f42r` | F | b | H | A | 1 | 141 | 107 | 0 | 1.778 | 0/1 | 2/23 | `f42r.js` | 0 | sherwood_botanical_index |
| `f42v` | F | b | H | A | 1 | 116 | 96 | 0 | 1.907 | 0/1 | 1/16 | `f42v.js` | 31 (29c/2u) | sherwood_botanical_index |
| `f43r` | F | c | H | B | 2 | 153 | 116 | 0 | 1.942 | 1/1 | 4/14 | `f43r.js` | 0 | sherwood_botanical_index |
| `f43v` | F | c | H | B | 2 | 151 | 127 | 0 | 2.022 | 1/1 | 3/16 | `f43v.js` | 0 | sherwood_botanical_index |
| `f44r` | F | d | H | A | 1 | 74 | 67 | 0 | 2.019 | 1/1 | 3/11 | `f44r.js` | 0 | sherwood_botanical_index |
| `f44v` | F | d | H | A | 1 | 100 | 78 | 0 | 1.902 | 1/1 | 0/13 | `f44v.js` | 0 | sherwood_botanical_index |
| `f45r` | F | w | H | A | 1 | 89 | 75 | 0 | 1.821 | 1/1 | 3/11 | `f45r.js` | 0 | sherwood_botanical_index |
| `f45v` | F | w | H | A | 1 | 85 | 76 | 0 | 2.044 | 1/1 | 3/11 | `f45v.js` | 0 | sherwood_botanical_index |
| `f46r` | F | x | H | B | 2 | 163 | 125 | 0 | 1.990 | 1/1 | 5/15 | `f46r.js` | 0 | sherwood_botanical_index |
| `f46v` | F | x | H | B | 2 | 111 | 89 | 0 | 1.887 | 1/1 | 6/13 | `f46v.js` | 0 | sherwood_botanical_index |
| `f47r` | F | y | H | A | 1 | 76 | 55 | 0 | 1.572 | 0/1 | 2/11 | `f47r.js` | 0 | sherwood_botanical_index |
| `f47v` | F | y | H | A | 1 | 85 | 67 | 0 | 1.667 | 1/1 | 0/14 | `f47v.js` | 0 | sherwood_botanical_index |
| `f48r` | F | z | H | B | 5 | 89 | 87 | 0 | 1.968 | 1/1 | 2/9 | `f48r.js` | 0 | sherwood_botanical_index |
| `f48v` | F | z | H | B | 5 | 128 | 105 | 0 | 1.895 | 1/1 | 5/11 | `f48v.js` | 0 | sherwood_botanical_index |
| `f49r` | G | a | H | A | 1 | 114 | 85 | 0 | 1.714 | 1/1 | 0/21 | `f49r.js` | 0 | sherwood_botanical_index |
| `f49v` | G | a | H | A | 1 | 143 | 103 | 26 | 1.743 | 1/1 | 1/26 | `f49v.js` | 0 | sherwood_botanical_index |
| `f50r` | G | b | H | B | 2 | 93 | 78 | 0 | 1.842 | 1/1 | 3/10 | `f50r.js` | 0 | sherwood_botanical_index |
| `f50v` | G | b | H | B | 2 | 100 | 85 | 0 | 1.870 | 1/1 | 2/11 | `f50v.js` | 0 | sherwood_botanical_index |
| `f51r` | G | c | H | A | 1 | 89 | 79 | 0 | 1.907 | 1/1 | 3/15 | `f51r.js` | 0 | sherwood_botanical_index |
| `f51v` | G | c | H | A | 1 | 82 | 70 | 0 | 1.803 | 1/1 | 1/13 | `f51v.js` | 0 | sherwood_botanical_index |
| `f52r` | G | d | H | A | 1 | 69 | 58 | 0 | 1.951 | 1/1 | 2/8 | `f52r.js` | 0 | sherwood_botanical_index |
| `f52v` | G | d | H | A | 1 | 78 | 69 | 0 | 1.842 | 1/1 | 2/14 | `f52v.js` | 0 | sherwood_botanical_index |
| `f53r` | G | w | H | A | 1 | 61 | 57 | 0 | 2.034 | 1/1 | 0/9 | `f53r.js` | 0 | sherwood_botanical_index |
| `f53v` | G | w | H | A | 1 | 73 | 67 | 0 | 1.868 | 1/1 | 2/13 | `f53v.js` | 0 | sherwood_botanical_index |
| `f54r` | G | x | H | A | 1 | 110 | 75 | 0 | 1.959 | 1/1 | 5/12 | `f54r.js` | 0 | sherwood_botanical_index |
| `f54v` | G | x | H | A | 1 | 93 | 75 | 0 | 1.834 | 1/1 | 5/16 | `f54v.js` | 0 | sherwood_botanical_index |
| `f55r` | G | y | H | B | 2 | 124 | 92 | 0 | 1.955 | 1/1 | 2/13 | `f55r.js` | 0 | sherwood_botanical_index |
| `f55v` | G | y | H | B | 2 | 105 | 74 | 0 | 1.797 | 1/1 | 3/12 | `f55v.js` | 0 | sherwood_botanical_index |
| `f56r` | G | z | H | A | 1 | 103 | 80 | 0 | 1.707 | 0/1 | 0/19 | `f56r.js` | 0 | sherwood_botanical_index |
| `f56v` | G | z | H | A | 1 | 91 | 67 | 0 | 1.588 | 1/1 | 0/16 | `f56v.js` | 51 (45c/6u) | sherwood_botanical_index |
| `f57r` | H | a | H | B | 5 | 87 | 77 | 0 | 1.847 | 1/1 | 5/11 | `f57r.js` | 0 | sherwood_botanical_index |
| `f57v` | H | a | C | ? | 1 | 0 | 0 | 198 | - | 0/0 | 0/0 | `f57v.js` | 0 | - |
| `f58r` | H | b | S | A | 3 | 378 | 288 | 0 | 2.094 | 1/1 | 12/41 | `f58r.js` | 0 | - |
| `f58v` | H | b | S | A | 3 | 375 | 236 | 0 | 1.959 | 1/1 | 10/39 | `f58v.js` | 0 | - |
| `f65r` | H | y | H | ? | 3 | 0 | 0 | 3 | - | 0/0 | 0/0 | `f65r.js` | 0 | - |
| `f65v` | H | y | H | ? | 3 | 45 | 44 | 0 | 2.004 | 0/1 | 1/6 | `f65v.js` | 0 | - |
| `f66r` | H | z | T | B | 5 | 294 | 220 | 54 | 2.024 | 1/1 | 2/32 | `f66r.js` | 0 | - |
| `f66v` | H | z | H | B | 5 | 114 | 94 | 0 | 2.041 | 0/1 | 2/13 | `f66v.js` | 0 | - |
| `f67r1` | I | a | A | ? | 4 | 41 | 33 | 126 | 1.715 | 1/1 | 1/4 | `f67r1.js` | 0 | - |
| `f67r2` | I | a | A | ? | 4 | 126 | 106 | 64 | 2.122 | 1/13 | 2/35 | `f67r2.js` | 0 | - |
| `f67v2` | I | a | C | ? | 4 | 34 | 33 | 28 | 1.836 | 2/4 | 3/8 | `f67v2.js` | 0 | voynich_nu_q09_f067v2_tr.txt |
| `f67v1` | I | a | A | ? | 4 | 0 | 0 | 73 | - | 0/0 | 0/0 | `f67v1.js` | 0 | - |
| `f68r1` | I | z | A | ? | 4 | 31 | 31 | 34 | 1.896 | 0/2 | 1/7 | `f68r1.js` | 0 | f68r1_event_jvs.pdf,voynich_nu_f068r1_tr.txt |
| `f68r2` | I | z | A | ? | 4 | 37 | 36 | 45 | 1.818 | 1/1 | 1/5 | `f68r2.js` | 0 | voynich_nu_f068r2_tr.txt |
| `f68r3` | I | z | A | ? | 4 | 0 | 0 | 106 | - | 0/0 | 0/0 | `f68r3.js` | 0 | stolfi_f68r3.htm,stolfi_f68r3_data.txt,voynich_nu_f068r3_tr.txt |
| `f68v3` | I | z | C | ? | 4 | 55 | 48 | 114 | 1.855 | 1/2 | 1/7 | `f68v3.js` | 0 | - |
| `f68v2` | I | z | A | ? | 4 | 44 | 43 | 59 | 1.775 | 1/1 | 2/5 | `f68v2.js` | 0 | - |
| `f68v1` | I | z | A | ? | 4 | 0 | 0 | 97 | - | 0/0 | 0/0 | `f68v1.js` | 0 | - |
| `f69r` | J | a | C | ? | 4 | 36 | 33 | 122 | 1.676 | 1/1 | 2/4 | `f69r.js` | 0 | - |
| `f69v` | J | a | C | ? | 4 | 0 | 0 | 142 | - | 0/0 | 0/0 | `f69v.js` | 0 | - |
| `f70r1` | J | z | C | ? | 4 | 0 | 0 | 112 | - | 0/0 | 0/0 | `f70r1.js` | 0 | - |
| `f70r2` | J | z | C | ? | 4 | 101 | 75 | 145 | 1.935 | 0/1 | 4/14 | `f70r2.js` | 0 | - |
| `f70v2` | J | z | Z | ? | 4 | 0 | 0 | 131 | - | 0/0 | 0/0 | `f70v2.js` | 0 | stolfi_f70v2.htm,voynich_nu_f070v2_tr.txt |
| `f70v1` | J | z | Z | ? | 4 | 0 | 0 | 86 | - | 0/0 | 0/0 | `f70v1.js` | 0 | voynich_nu_f070v1_tr.txt |
| `f71r` | K | a | Z | ? | 4 | 0 | 0 | 90 | - | 0/0 | 0/0 | `f71r.js` | 0 | voynich_nu_f071r_tr.txt |
| `f71v` | K | a | Z | ? | 4 | 0 | 0 | 100 | - | 0/0 | 0/0 | `f71v.js` | 0 | voynich_nu_f071v_tr.txt |
| `f72r1` | K | z | Z | ? | 4 | 0 | 0 | 105 | - | 0/0 | 0/0 | `f72r1.js` | 0 | voynich_nu_f072r1_tr.txt |
| `f72r2` | K | z | Z | ? | 4 | 0 | 0 | 113 | - | 0/0 | 0/0 | `f72r2.js` | 0 | voynich_nu_f072r2_tr.txt |
| `f72r3` | K | z | Z | ? | 4 | 0 | 0 | 165 | - | 0/0 | 0/0 | `f72r3.js` | 0 | voynich_nu_f072r3_tr.txt |
| `f72v3` | K | z | Z | ? | 4 | 0 | 0 | 119 | - | 0/0 | 0/0 | `f72v3.js` | 0 | voynich_nu_f072v3_tr.txt |
| `f72v2` | K | z | Z | ? | 4 | 0 | 0 | 108 | - | 0/0 | 0/0 | `f72v2.js` | 0 | stolfi_f72v2_data.txt,voynich_nu_f072v2_tr.txt |
| `f72v1` | K | z | Z | ? | 4 | 0 | 0 | 104 | - | 0/0 | 0/0 | `f72v1.js` | 0 | voynich_nu_f072v1_tr.txt |
| `f73r` | L | a | Z | ? | 4 | 0 | 0 | 96 | - | 0/0 | 0/0 | `f73r.js` | 0 | voynich_nu_f073r_tr.txt |
| `f73v` | L | a | Z | ? | 4 | 0 | 0 | 99 | - | 0/0 | 0/0 | `f73v.js` | 0 | voynich_nu_f073v_tr.txt |
| `f75r` | M | a | B | B | 2 | 418 | 203 | 0 | 1.698 | 1/2 | 7/53 | `f75r.js` | 0 | - |
| `f75v` | M | a | B | B | 2 | 324 | 173 | 36 | 1.713 | 3/3 | 3/37 | `f75v.js` | 0 | - |
| `f76r` | M | b | T | B | 2 | 561 | 257 | 9 | 1.762 | 1/1 | 2/47 | `f76r.js` | 0 | - |
| `f76v` | M | b | B | B | 2 | 400 | 227 | 0 | 1.763 | 1/1 | 2/41 | `f76v.js` | 0 | - |
| `f77r` | M | c | B | B | 2 | 321 | 167 | 11 | 1.559 | 1/1 | 2/40 | `f77r.js` | 0 | - |
| `f77v` | M | c | B | B | 2 | 321 | 164 | 11 | 1.615 | 0/1 | 2/37 | `f77v.js` | 0 | - |
| `f78r` | M | d | B | B | 2 | 290 | 161 | 8 | 1.728 | 1/1 | 3/41 | `f78r.js` | 0 | - |
| `f78v` | M | d | B | B | 2 | 295 | 159 | 0 | 1.666 | 0/1 | 2/32 | `f78v.js` | 0 | - |
| `f79r` | M | e | B | B | 2 | 383 | 214 | 0 | 1.799 | 1/1 | 3/44 | `f79r.js` | 0 | - |
| `f79v` | M | e | B | B | 2 | 356 | 201 | 0 | 1.725 | 1/1 | 6/42 | `f79v.js` | 0 | - |
| `f80r` | M | v | B | B | 2 | 436 | 230 | 10 | 1.788 | 1/1 | 8/43 | `f80r.js` | 0 | - |
| `f80v` | M | v | B | B | 2 | 376 | 199 | 0 | 1.770 | 1/1 | 2/44 | `f80v.js` | 0 | - |
| `f81r` | M | w | B | B | 2 | 210 | 128 | 0 | 1.676 | 1/1 | 1/31 | `f81r.js` | 0 | - |
| `f81v` | M | w | B | B | 2 | 253 | 155 | 2 | 1.815 | 1/1 | 1/27 | `f81v.js` | 0 | - |
| `f82r` | M | x | B | B | 2 | 278 | 161 | 13 | 1.663 | 1/2 | 2/32 | `f82r.js` | 0 | - |
| `f82v` | M | x | B | B | 2 | 306 | 178 | 14 | 1.705 | 1/1 | 3/34 | `f82v.js` | 0 | - |
| `f83r` | M | y | B | B | 2 | 341 | 196 | 4 | 1.702 | 1/4 | 1/51 | `f83r.js` | 0 | - |
| `f83v` | M | y | B | B | 2 | 257 | 144 | 4 | 1.590 | 2/2 | 1/31 | `f83v.js` | 0 | - |
| `f84r` | M | z | B | B | 2 | 354 | 182 | 14 | 1.710 | 1/2 | 5/34 | `f84r.js` | 0 | - |
| `f84v` | M | z | B | B | 2 | 341 | 164 | 0 | 1.650 | 1/4 | 4/51 | `f84v.js` | 0 | - |
| `f85r1` | N | a | T | B | 2 | 347 | 239 | 0 | 1.954 | 1/1 | 13/35 | `f85r1.js` | 0 | - |
| `f85r2` | N | a | C | B | 2 | 108 | 85 | 48 | 1.839 | 1/4 | 3/22 | `f85r2.js` | 0 | - |
| `fRos` | N | ? | C | B | 4 | 39 | 37 | 501 | 1.744 | 2/4 | 0/11 | `-` | 0 | - |
| `f86v4` | N | z | C | B | 2 | 49 | 37 | 142 | 1.719 | 1/1 | 1/5 | `f86v4.js` | 0 | - |
| `f86v6` | N | z | T | B | 2 | 490 | 287 | 0 | 1.955 | 1/1 | 11/45 | `f86v6.js` | 0 | - |
| `f86v5` | N | z | T | B | 2 | 390 | 231 | 0 | 1.958 | 1/1 | 11/39 | `f86v5.js` | 0 | - |
| `f86v3` | N | z | C | B | 2 | 281 | 198 | 0 | 1.843 | 5/5 | 13/36 | `f86v3.js` | 0 | - |
| `f87r` | O | a | H | A | 1 | 102 | 91 | 0 | 1.963 | 1/1 | 1/16 | `f87r.js` | 0 | - |
| `f87v` | O | a | H | A | 1 | 92 | 88 | 0 | 2.132 | 0/1 | 3/16 | `f87v.js` | 0 | - |
| `f88r` | O | b | P | A | 1 | 134 | 95 | 16 | 1.835 | 2/3 | 4/16 | `f88r.js` | 0 | - |
| `f88v` | O | b | P | A | 1 | 131 | 105 | 14 | 1.888 | 2/2 | 3/17 | `f88v.js` | 0 | - |
| `f89r1` | O | y | P | A | 1 | 126 | 95 | 15 | 1.858 | 1/2 | 2/14 | `f89r1.js` | 0 | - |
| `f89r2` | O | y | P | A | 1 | 212 | 135 | 22 | 1.835 | 2/3 | 2/14 | `f89r2.js` | 0 | - |
| `f89v2` | O | y | P | A | 1 | 165 | 120 | 16 | 2.002 | 1/2 | 4/12 | `f89v2.js` | 0 | - |
| `f89v1` | O | y | P | A | 1 | 145 | 117 | 9 | 1.888 | 1/1 | 1/16 | `f89v1.js` | 0 | - |
| `f90r1` | O | z | H | A | 1 | 69 | 66 | 0 | 2.101 | 1/1 | 1/9 | `f90r1.js` | 0 | - |
| `f90r2` | O | z | H | A | 1 | 47 | 40 | 0 | 1.947 | 1/1 | 0/6 | `f90r2.js` | 0 | - |
| `f90v2` | O | z | H | A | 1 | 68 | 60 | 0 | 1.885 | 0/1 | 2/8 | `f90v2.js` | 0 | - |
| `f90v1` | O | z | H | A | 1 | 96 | 84 | 0 | 1.944 | 1/1 | 1/11 | `f90v1.js` | 0 | - |
| `f93r` | Q | a | H | A | 1 | 152 | 117 | 0 | 1.949 | 1/1 | 2/32 | `f93r.js` | 0 | - |
| `f93v` | Q | a | H | A | 1 | 89 | 75 | 0 | 1.925 | 1/1 | 2/10 | `f93v.js` | 0 | - |
| `f94r` | Q | b | H | B | 3 | 79 | 74 | 0 | 1.801 | 1/1 | 3/9 | `f94r.js` | 0 | - |
| `f94v` | Q | b | H | B | 3 | 97 | 85 | 0 | 1.849 | 1/1 | 2/12 | `f94v.js` | 0 | - |
| `f95r1` | Q | y | H | B | 3 | 102 | 80 | 0 | 1.650 | 1/1 | 1/11 | `f95r1.js` | 0 | - |
| `f95r2` | Q | y | H | B | 3 | 79 | 62 | 0 | 1.740 | 1/1 | 4/9 | `f95r2.js` | 0 | - |
| `f95v2` | Q | y | H | B | 3 | 60 | 55 | 0 | 1.696 | 1/1 | 0/7 | `f95v2.js` | 0 | - |
| `f95v1` | Q | y | H | B | 3 | 118 | 104 | 0 | 1.817 | 0/1 | 2/13 | `f95v1.js` | 0 | - |
| `f96r` | Q | z | H | A | 1 | 84 | 75 | 0 | 1.823 | 1/1 | 0/13 | `f96r.js` | 0 | - |
| `f96v` | Q | z | H | A | 1 | 56 | 56 | 0 | 1.984 | 1/1 | 1/13 | `f96v.js` | 0 | - |
| `f99r` | S | a | P | A | 1 | 158 | 114 | 36 | 1.931 | 4/4 | 2/18 | `f99r.js` | 0 | - |
| `f99v` | S | a | P | A | 1 | 148 | 117 | 28 | 1.824 | 0/4 | 4/19 | `f99v.js` | 0 | - |
| `f100r` | S | b | P | A | 1 | 91 | 75 | 19 | 1.946 | 2/2 | 1/10 | `f100r.js` | 0 | - |
| `f100v` | S | b | P | A | 1 | 79 | 67 | 14 | 1.983 | 0/1 | 0/9 | `f100v.js` | 0 | - |
| `f101r` | S | y | P | A | 1 | 227 | 145 | 0 | 1.857 | 1/1 | 2/10 | `-` | 0 | - |
| `f101v` | S | y | P | A | 1 | 197 | 149 | 18 | 1.953 | 1/1 | 1/10 | `-` | 0 | - |
| `f102r1` | S | z | P | A | 1 | 103 | 89 | 4 | 1.965 | 3/3 | 1/13 | `f102r1.js` | 0 | - |
| `f102r2` | S | z | P | A | 1 | 137 | 106 | 7 | 2.059 | 1/3 | 2/15 | `f102r2.js` | 0 | - |
| `f102v2` | S | z | P | A | 1 | 168 | 127 | 22 | 1.974 | 2/2 | 0/17 | `f102v2.js` | 0 | - |
| `f102v1` | S | z | P | A | 1 | 118 | 96 | 10 | 1.792 | 2/2 | 3/14 | `f102v1.js` | 0 | - |
| `f103r` | T | a | S | B | 3 | 532 | 290 | 0 | 1.835 | 1/1 | 5/54 | `f103r.js` | 0 | - |
| `f103v` | T | a | S | B | 3 | 454 | 238 | 0 | 1.830 | 1/1 | 5/46 | `f103v.js` | 0 | - |
| `f104r` | T | b | S | B | 3 | 448 | 313 | 0 | 1.959 | 1/1 | 14/45 | `f104r.js` | 0 | - |
| `f104v` | T | b | S | B | 3 | 477 | 312 | 0 | 1.908 | 1/1 | 13/44 | `f104v.js` | 0 | - |
| `f105r` | T | c | S | B | 3 | 379 | 273 | 0 | 2.025 | 0/1 | 8/37 | `f105r.js` | 0 | - |
| `f105v` | T | c | S | B | 3 | 399 | 284 | 0 | 2.049 | 1/1 | 11/38 | `f105v.js` | 0 | - |
| `f106r` | T | d | S | B | 3 | 432 | 306 | 0 | 1.942 | 1/1 | 9/47 | `f106r.js` | 0 | - |
| `f106v` | T | d | S | B | 3 | 444 | 313 | 0 | 1.961 | 1/1 | 11/47 | `f106v.js` | 0 | - |
| `f107r` | T | e | S | B | 3 | 487 | 317 | 0 | 1.965 | 1/1 | 12/51 | `f107r.js` | 0 | - |
| `f107v` | T | e | S | B | 3 | 462 | 260 | 0 | 1.812 | 1/1 | 8/49 | `f107v.js` | 0 | - |
| `f108r` | T | f | S | B | 3 | 494 | 279 | 0 | 1.787 | 1/1 | 12/50 | `f108r.js` | 0 | - |
| `f108v` | T | f | S | B | 3 | 581 | 299 | 0 | 1.738 | 1/1 | 17/53 | `f108v.js` | 0 | - |
| `f111r` | T | u | S | B | 3 | 624 | 356 | 0 | 1.860 | 1/1 | 15/54 | `f111r.js` | 0 | - |
| `f111v` | T | u | S | B | 3 | 568 | 305 | 0 | 1.797 | 1/1 | 13/51 | `f111v.js` | 0 | - |
| `f112r` | T | v | S | B | 3 | 401 | 257 | 0 | 1.909 | 1/1 | 14/45 | `f112r.js` | 0 | - |
| `f112v` | T | v | S | B | 3 | 420 | 261 | 0 | 1.820 | 1/1 | 12/47 | `f112v.js` | 0 | - |
| `f113r` | T | w | S | B | 3 | 529 | 370 | 0 | 2.002 | 1/1 | 8/51 | `f113r.js` | 0 | - |
| `f113v` | T | w | S | B | 3 | 502 | 317 | 0 | 1.983 | 1/1 | 10/49 | `f113v.js` | 0 | - |
| `f114r` | T | x | S | B | 3 | 460 | 320 | 0 | 1.916 | 1/1 | 6/45 | `f114r.js` | 0 | - |
| `f114v` | T | x | S | B | 3 | 376 | 265 | 0 | 1.864 | 1/1 | 10/41 | `f114v.js` | 0 | - |
| `f115r` | T | y | S | B | ? | 461 | 310 | 0 | 1.926 | 1/1 | 7/45 | `f115r.js` | 0 | - |
| `f115v` | T | y | S | B | 3 | 410 | 317 | 0 | 2.019 | 1/1 | 15/45 | `f115v.js` | 0 | - |
| `f116r` | T | z | S | B | 3 | 553 | 273 | 0 | 1.903 | 1/1 | 17/50 | `f116r.js` | 0 | - |
| `f116v` | T | z | T | ? | 3 | 0 | 0 | 2 | - | 0/0 | 0/0 | `-` | 0 | ciphermysteries_f116v_p4559.html,ciphermysteries_f116v_p4559.html.txt,stolfi_f116v.htm |
