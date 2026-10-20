# controls_tabular_ruled: ruled period medical tables for s108 (D-066 (m))

Downloaded 2026-10-18 14:32-14:39 PDT by s108 (README written Sun Oct 18 15:05:56 PDT 2026, from `date`). Each source folder is a new folder of untrusted
data: byte-exact archive.org downloads, read as data by `s108_ruled_medical_tables.py` (run with `python -I`; XML parsed with
defusedxml), never executed. The row-selection rule, the cell rule and the legibility gate live in that script's docstring.
Page images are the archive.org BookReader JPGs `https://archive.org/download/<id>/page/n<k>_w1200.jpg` as served (most at half the
scan size; a few at full size), one per OCR page index k; their sha256 are listed in each folder's `pages_manifest.sha256`.

| Folder / file | Text | Source URL | Licence (archive.org metadata) | sha256 |
|---|---|---|---|---|
| schott1531_biusante/BIUSante_00188x01_djvu.xml | Tacuini sanitatis (Strasbourg: Schott, 1531), with Albengnefit and Al-Kindi De rerum gradibus; BIU Sante copy. OCR word boxes (used: T1 Al-Kindi, T2 Tacuinum) | https://archive.org/download/BIUSante_00188x01/BIUSante_00188x01_djvu.xml | Licence Ouverte / Open Licence (Etalab) | d2b3d9cfef00131fff9e05eb43d77ab222816cb7dd1dbcd03b0c8621d0700e67 |
| schott1531_biusante/BIUSante_00188x01_djvu.txt | same, plain OCR text (inspected; Argon's pointer lines 12548-12803 are Tacuinum 'Opiniones philosophorum' prose, not the Al-Kindi tables, which sit near OCR lines 20710-20900) | https://archive.org/download/BIUSante_00188x01/BIUSante_00188x01_djvu.txt | Etalab | 8281acf9a155d1d4e2385fd0ee80a066f6a72777a8e316b9dce41083d6f025e2 (= data/controls_tabular/raw_tacuinum_biu copy) |
| schott1531_biusante/pages/n000-n171.jpg | page images of the same item (172) | https://archive.org/download/BIUSante_00188x01/page/n<k>_w1200.jpg | Etalab | pages_manifest.sha256 |
| schott1531_bub/bub_gb_9lIU1a_-ddAC_djvu.txt, _djvu.xml | the same 1531 edition, second copy (Google Books scan). Not scored: same edition as the BIU copy | https://archive.org/download/bub_gb_9lIU1a_-ddAC/ | Public Domain Mark 1.0 | txt c049895be16f6a8b52c6b5237e83403eb711b4aef6b333d1eb02a85988c15ca3; xml bfa941fe6398412f70631c20ada716f1a38d26ead403cbf40e12b21a39b45574 |
| ibnjazlah1532/b14562455_0002_djvu.xml | Ibn Jazlah (Buhahylyha Byngezla), Tacuini aegritudinum et morborum ferme omnium corporis humani (Strasbourg: Schott, 1532). OCR word boxes (used: T3) | https://archive.org/download/b14562455_0002/b14562455_0002_djvu.xml | Public Domain Mark 1.0 | 8092b1a8a1d74ae400c4bb99c56eba99cc0817c647bcaa5dd666304db64edcf0 |
| ibnjazlah1532/b14562455_0002_djvu.try1.txt | same, plain OCR text (inspected only) | https://archive.org/download/b14562455_0002/b14562455_0002_djvu.txt | PDM 1.0 | ec89b2897685df7e9820d346a40bbaae6ef97a1c3fd29587569558d697724764 |
| ibnjazlah1532/b14562455_0002_djvu.txt | NOT the text: the first download attempt returned an nginx '500 Internal Server Error' page (170 bytes). Kept, not used | same URL | - | 9e93ecf12d78a8c4c278708706bd249fe086983fb28f82eb880f5c7795043962 |
| ibnjazlah1532/pages/n000-n163.jpg | page images (164) | https://archive.org/download/b14562455_0002/page/n<k>_w1200.jpg | PDM 1.0 | pages_manifest.sha256 |
