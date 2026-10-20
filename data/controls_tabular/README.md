# controls_tabular: period tabular medical / combinatory texts for s107 (D-066 (k))

Downloaded 2026-10-18 13:35-13:41 PDT by s107 (README written 13:47:39 PDT, from `date`). Each `raw_*` folder is a new folder
holding untrusted data: byte-exact downloads, read as text by `s107_tabular_medical_reference.py` (run with `python -I`),
never executed. The layout rules (entry boundaries, head removal, re-cut of table cells) live in that script's docstring
and loaders, not here.

## Used by s107

| Folder / file | Text | Source URL | Edition / witness | Licence | sha256 |
|---|---|---|---|---|---|
| raw_tacuinum_medimanus/tacuinum_sanitatis.html | T1 Tacuinum sanitatis (Latin translation of Ibn Butlan's Taqwim al-sihha), one table entry per line | https://medimanus.chs.harvard.edu/app/pharmantica/tacuinum_sanitatis | MS Paris, BnF latin 9333 (1445-1450), transcription published by MediManus (Center for Hellenic Studies, Harvard) | The medieval text is public domain. The page states no licence for the transcription; it is used here as research data only and not redistributed | 396f9bb41124d9d70e0a410b5554a535d1acc2731555ad8bfc3278af1faa23c5 |
| raw_degradibus/BIUSante_00128x01_djvu.txt | T2 Constantinus Africanus, Liber de gradibus (OCR lines after the DE GRADIBVS title to 'Liber graduum finit'), one entry (simple) per line by the source's entry boundaries (the source is running entries, not a ruled table) | https://archive.org/download/BIUSante_00128x01/BIUSante_00128x01_djvu.txt | Constantini Africani ... opera (Basel: Henricus Petrus, 1536), BIU Sante copy, archive.org OCR | Licence Ouverte / Open Licence (Etalab), per archive.org metadata `rights` | 6b2bf4267dab93500c80f4b652e02f641988202cd43258e2146c58c91764c194 |
| raw_lull_1515/ARes54311_djvu.txt | T3 Ramon Llull, Tabula generalis combinatory table (OCR lines 18100-18599), one printed table row per line | https://archive.org/download/ARes54311/ARes54311_djvu.txt | Diui Raymundi Lulli ... Ars inuentiua veritatis; Tabula generalis; ... (1515), archive.org OCR | Public Domain Mark 1.0, per archive.org metadata | aa0bb346dc8110a59c67966b8973eaa373313831fc386ef52c455cdcf408a4be |

## Inspected and not used (kept in place; nothing deleted)

| Folder / file | Why not used | Source | sha256 |
|---|---|---|---|
| raw_tacuinum/bub_gb_9lIU1a_-ddAC_djvu.txt | Tacuini sanitatis, Strasbourg: Schott 1531. Its tables are printed as rotated grids, and the OCR of those pages cannot be read; the rest is canons in prose | https://archive.org/download/bub_gb_9lIU1a_-ddAC/bub_gb_9lIU1a_-ddAC_djvu.txt (PDM 1.0) | c049895be16f6a8b52c6b5237e83403eb711b4aef6b333d1eb02a85988c15ca3 |
| raw_tacuinum/gri_33125012607426_djvu.txt | same 1531 edition, Getty copy, same problem | https://archive.org/download/gri_33125012607426/gri_33125012607426_djvu.txt (NOT_IN_COPYRIGHT) | 3589db3dca8ace1680976e2bc7ac8d1f76ee287b3c17f34daee8b214c107eb43 |
| raw_tacuinum_biu/BIUSante_00188x01_djvu.txt | same 1531 edition, BIU Sante copy, same problem | https://archive.org/download/BIUSante_00188x01/BIUSante_00188x01_djvu.txt (Etalab) | 8281acf9a155d1d4e2385fd0ee80a066f6a72777a8e316b9dce41083d6f025e2 |
| raw_tacuinum_aegr/bub_gb__AoMWu4PEoIC_djvu.txt | Tacuini aegritudinum (Buhahylyha Byngezla, Schott 1532): canons in prose; the OCR does not recover the tables | https://archive.org/download/bub_gb__AoMWu4PEoIC/bub_gb__AoMWu4PEoIC_djvu.txt (PDM 1.0) | 0c9087d48f05969606035d012c411198f483d0011daa5d55c6a608fd39eda70a |
| raw_degradibus/ita-bnc-ald-00000692-001_djvu.txt | De gradibus medicinarum (1497 incunable): a treatise on how degrees are found, not a list of simples; its OCR is poor | https://archive.org/download/ita-bnc-ald-00000692-001/ita-bnc-ald-00000692-001_djvu.txt | ca1a1421573ecfc7cbabb7b2f7fa84c80f519c842f9c45b40c9e7cc7daba76f4 |
| raw_lull/bub_gb_ZvBb1_8xBIYC_djvu.txt | Artificium siue Ars breuis (1565): the OCR came out in Cyrillic and cannot be used | https://archive.org/download/bub_gb_ZvBb1_8xBIYC/bub_gb_ZvBb1_8xBIYC_djvu.txt (PDM 1.0) | 2d7859c62f9a978390a36505bf13d313ae545ebb18f472777e6d1428346ebf62 |
| raw_lull_1596/bub_gb_k334cEAvl5gC_djvu.txt | Ars magna (1596): the table OCR is illegible (44 lines) | https://archive.org/download/bub_gb_k334cEAvl5gC/bub_gb_k334cEAvl5gC_djvu.txt (PDM 1.0) | df7b15c9a1955045eb9743dbfb38ae697235414d2a01e229a4b914d1fe382d32 |
| raw_lull_1617/BIUSante_pharma_res011289_djvu.txt | Raymundi Lullii opera (Zetzner 1617): the tabula is OCR'd one cell per line, under 200 cells | https://archive.org/download/BIUSante_pharma_res011289/BIUSante_pharma_res011289_djvu.txt (Etalab) | 8cad40e58b6709dec4099f92cd26f5a3ae29e94cc21db94a71fe3c69efbac82e |

No recipe-list text (Antidotarium Nicolai) was found whose entry boundaries can be read by machine. The on-disk Dispensarium
OCR (data/external/genre-s87) has no recoverable recipe boundaries, so no recipe-list text is run.
