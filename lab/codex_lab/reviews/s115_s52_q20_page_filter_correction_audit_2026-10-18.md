# S115 audit: correction of the S52 Q20 page filter

## Checked outcome

The original S52 result is invalid **only for its reported Q20 population and
the T1a values calculated from that population**. Its page-number predicate
converted `f102r1` to `1021` and `f102v2` to `1022`, adding ten f102 paragraphs
to a test registered for `f103r-f116r`.

The frozen Amendment 1 changes only the folio predicate to extract the digits
immediately following `f` and require folios 103 through 116. The original
source and result are preserved. The amended source hash is
`2B24D5DC2156389BA58AC22433AC0BEA1C18744E5E138FBDF1C2CDDF00F2DCCB`;
the frozen manifest hash is
`BFC1C556FC00060D5CEDAF7DD1ADD89A8C95866B42A17A5F23B78984EDD8511B`.

## Corrected population

| Transcription | Original N | Corrected N | Out-of-scope f102 paragraphs removed |
|---|---:|---:|---:|
| ZL3b | 295 | **285** | 10 |
| RF1b | 27 | **23** | 4 |
| IT2a | 301 | **289** | 12 |

For ZL3b, the corrected raw paragraph-initial inventory is 241/285 types,
with modal share `6/285 = .0211` and entropy `7.7741` bits versus an internal
line-start null mean of `6.9012`. Gallows-stripped entropy is `7.5902`; the
modal share is `8/285 = .0281`. The non-formulaic-incpit call therefore
survives.

The T1b ordering values and null verdict remain effectively unchanged. That
code assembles its tested sequence from an explicit f103-f116 page list, so the
accidentally admitted f102 records never entered the observed order. ZL3b
still fails the page-block-controlled alphabetical/ordered-incpit test
(`p=.8152` raw post-gallows initial, `.7025` core initial, and `.1617` second
word initial in folio order). The alternative order also remains null.

T2 and T3 reproduce their earlier outcomes and are not new evidence.

## Change in meaning

1. Replace every statement that Q20 contains 295 tested paragraphs with **285
   ZL3b paragraphs on f103r-f116r**.
2. Preserve S52's qualitative conclusions: Q20 incipits are not governed by a
   simple repeated `Recipe/Item` marker, and the tested alphabetical/ordered
   incipit signature is null after page control.
3. Do not read the T1a result as identification of an antidotary. It is a
   non-formulaicity result compatible with many genres.
4. Reject the post-hoc observation `295 = 2*147 + 1`: 295 was produced by the
   defective page filter. No doublet experiment is warranted from that count.

## New external resource

Separately, S115 froze DBNL's TEI edition of the *Antidotarium Nicolai* and
extracted 141 unique numbered Latin preparations, numbered 1 through 147 with
six absent numbers. The corpus is suitable for a future entry-level test, but
its count has no special match to the corrected 285 Voynich paragraphs.

## Reopen condition

Reopen the S52 scope correction only if a physical or independently curated
Q20 paragraph inventory shows that f102 belongs to the registered recipe
quire or changes the f103-f116 paragraph boundaries. Reopen an Antidotarium
identity claim only after a powered, outcome-blind entry-level relationship
test predicts held-out structure.

