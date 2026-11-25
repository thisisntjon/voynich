# Voynich Reconstruction Atlas

Explore the manuscript one photograph, word or fold at a time. This edition covers 204 Yale photographs of Beinecke MS 408 and lets readers follow an observation back to the page where it was made.

- **[Start reading here](START-READING.md).** Inspect a real disagreement between two transcriptions directly in your browser.
- **[Compare all 707 cases](spacing-differences.csv).** Each row identifies a passage where the selected EVA characters match and the word divisions differ.
- **[Fold the first gathering](https://github.com/thisisntjon/voynich/raw/refs/heads/reconstruction-atlas-v1/fold-quire-1.pdf)** or **[rerun the experiments](https://github.com/thisisntjon/voynich/raw/refs/heads/reconstruction-atlas-v1/replication-v1.zip)**. The packet includes inputs, verification code and reference predictions.
- **[Download the complete offline Atlas](https://github.com/thisisntjon/voynich/releases/download/reconstruction-atlas-1.0/Voynich-Reconstruction-Atlas-1.0.zip).** Extract the portable ZIP and open `index.html`. The reader, comparison and puzzles work offline. The [19 MB research dataset](https://github.com/thisisntjon/voynich/releases/download/reconstruction-atlas-1.0/atlas-data-v1.zip) contains the manuscript-part catalog and coordinates.

The reader lines up two transcriptions, gives each photograph, passage and word an address, and distinguishes traced geometry from estimated positions. The 61 fragment puzzles let you try a reconstruction and see where the documented scoring method succeeds or fails. The [photograph inventory](photograph-coverage.csv) documents coverage. The [passage inventory](compare-readings.csv) records both shared locations and locations found in only one edition.

## Reuse and corrections

Courtesy of the Yale University Library. The original images are Beinecke MS 408. Each upstream edition and geometry source has its own terms. See [credits and reuse](CREDITS.txt) and [edition citation](CITATION.cff).

For a correction, include the Atlas version, folio or photo ID, the locus or region, and the detail you can see in Yale's image. [Report a correction](https://github.com/thisisntjon/voynich/issues).

## Verify the download

The complete edition contains a SHA-256 manifest for 1,128 files. [Release checksums](SHA256SUMS.txt) identify the four downloads. To reproduce the portable ZIP from a source checkout of this branch, run `python assemble.py` with Python 3.8 or newer.
