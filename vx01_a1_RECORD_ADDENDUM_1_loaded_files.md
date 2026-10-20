# vx01 A1 record addendum 1: every file the A1 gate run loaded (UNVERIFIED until IV signs)
Date 2026-10-18 PDT. Plan PLAN-X01-v5.1 (af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393). A1 result: results_vx01_a1.txt (1e2ff8bd326878c80e77b2eaf0b6ea98d66edb7a9ac823bcb2534e2074e39de6). IV re-score: IV-RESCORE-X01-A1.md (e7be4afc4003bfe515c1f55bca43b0eca05dc7df63daaf7fd0cb1b292d0e0fa9, checked). New file; no frozen file edited.

## Stub gap (IV must-fix 1)
- `scoreboard/score.py` SHA256 **3a7b7c3efea13b884362f9f7f07551835bab8ca158ecdb43b946c96a8b3fbf1d** (computed by me on Skynet; matches Eve's 3a7b7c3e...f1d and the IV value). It is loaded by a spec loader (`g1_edge_joint.py:49`, reached through s76) and was NOT listed in `vx01_a1_known_answer.prereg.sha256`, so the gate stub check did not cover it. It is added to the A1 record here.

## Full list of files loaded at run time (code, data, sidecars)
How found: a read-only trace on Skynet, 2026-10-18 ~23:40 PDT (one BelowNormal process; no vx01 script started, no log or output written). It imported the frozen A1 modules, called `load_set` for the 3 sets, `make_segmenters` on 5 toy words and `gate_seed_list`, and recorded (a) every file opened under the project root (audit hook; .pyc mapped to its .py) and (b) every loaded module file under the root. 33 files. 31 equal the stub's hash lines exactly. The other 2 are score.py (gap above) and vx01_gate_seeds.json (covered by the stub key line gate_seeds_sha256=).
| SHA256 | File |
|---|---|
| 0b20e37ec2254d277a7ed8e1bf73e03c9fbfd15f92c4289496dd0ee07392f3b2 | `a1_profile.py` |
| 426b7b649361a8776a2152b95ddde4380d23af73f2e5096ed70891abee7937b3 | `a2_position.py` |
| 5fcdfdeb5e819ad33bbb1641cf2c5ce850b61b7fb9c85ec4bc21933caaf69d5a | `b4_selfcite_sim.py` |
| 0f1722dea55b3cceda5e6f622e6cedc99c779506b160862ad2c41e5168d41007 | `b5_nmf_topics.py` |
| f21281d9fe41d309823117ab2517af5fddae6aead7ae84b5fec6114ea7c78c0a | `c2_section_generator.py` |
| 30b6ba47c9de4a36379ea0fea92a39a10da5ec6da4f4488266d4b3f68a827ffb | `c3_edge_coupling.py` |
| 46b5e002aee66f6ee95f43c8f4edccffb68629e3a526416333eb8e552465260b | `c4_naibbe_lines.py` |
| 2f2b3d4af32a054a63f4c90492e56dd0e2e76d7157de1317a0d62aeb40223518 | `corpora.py` |
| 0d0d3e758d1e308b0aee4b4d006f90cbc8090c081e0fcb3327de6734ac5e5fdf | `data/translit/IT2a.meta.json` |
| c7d9bccba99b2610b9d80b4ce5f26f7d1ab54c12ec2364d0423d6b89f51da9df | `data/translit/RF1b.meta.json` |
| ce233477803a865365e53418f5e2b78c324fa0ea124b0aa46a9eb6a5189f7ef0 | `data/translit/ZL3b_eva.meta.json` |
| 5bd3e11f07c7231d37efbedb644aa0d5644a4678b33ca030065fa9241c26ab76 | `f1_residual_order.py` |
| 440ff45dee9087abe9a6aa77976bbe46b369790cb113416bf5779658f49008bd | `f2_syllable_control.py` |
| e0ac0ac62d6de16da094501a3fff26afd0551de681421ba66e6b8383d121e0ca | `f3_flow_choice.py` |
| 4f955d34794293725c0063020ff00b1c5ed401aa38ee361cd2e4b345eca57ba7 | `g1_edge_joint.py` |
| a40137f5ea2b8ef54d8829cf4bdecefa43f393cb53d0e7a526afe8010489afc1 | `n1_habit_table.py` |
| 56485b42c5c928c908a04be1a9b888a06c85088bc0b49589ef340d69ca220cec | `s55_code_vs_generator.py` |
| 1e5987dfee74c819b1f1c11abe0d386ce19f1ca730c39a30d45d4a534391b6a7 | `s56_core_repetition_lag.py` |
| 11e722d4a0391d34228637da8b9c1872a6dc4ddd5dc1f2ff4e94f8c6a903c458 | `s69_prefix_stream_memory.py` |
| ae0a00e8df8b053677451a5dd96b55dc5a9e0942052a59147383129bec95b5cb | `s70_canonical_segmentation_and_rare_cores.py` |
| 43f7aab7ad8c2bfa12e9d020f4749eb11281d51d7262c898cb499452c0184a29 | `s76_segmenter_independence.py` |
| 56eb6afdafdc57654b56a7019ee6a9410752db9ffb08c3a9112f83dd0798cc5d | `s77_deconfounded_scribe_and_comma_ablation_loqo.py` |
| 4b9a400be433c2429864c638e823c742d6a54899e36597c0e6a2269eaf24c06f | `scoreboard/__init__.py` |
| a59c9c17f8abe4cc8e29347854b02304eaa6a13c90b32f1890c1b1a60e7b23ed | `scoreboard/metrics_new.py` |
| 3a7b7c3efea13b884362f9f7f07551835bab8ca158ecdb43b946c96a8b3fbf1d | `scoreboard/score.py` |
| 8b4d2fdb08aa01f4b3402386b3ff1ccbc2041f662e10e8a440cae5d784874a65 | `tools/boxes.py` |
| 0e317c9a762e77c2f9002a1b95af367911a6714a7585803ab8715178a95a91c1 | `vparse.py` |
| 8c0d51155a37240fa6fa628bcae85bc72774a31b18fbcb2c5ca535c5e19f2079 | `vx01_a1_gen.py` |
| 5c408207c9668f203e3f716caa1d4db1412ea1943fc4c6707aac0eaa00b39d9e | `vx01_a1_known_answer.py` |
| 0b35605650a8af411d180905f9d5db0b30e2b985bf6d8877e14f5f1f0d5e94a9 | `vx01_a1_metrics.py` |
| cd4e5960f6e4058fd75f63478be58acf3b27ac54c6168a818c2d19a89325360a | `vx01_common.py` |
| bd9961f3510c7f4ae50f45a693ff73b143447f89fdc1c10d7ed95cfb1068a3dd | `vx01_gate_seeds.json` |
| 35c6f781dbdac466beb0e06cf4226ef20957e95d3b90fad5e984a43becd27718 | `vx01_seg_mdl.py` |

The gate run also read its own stub `vx01_a1_known_answer.prereg.sha256` (1ea30288e6ff1cd9b415db30305a955cc362eb8925ec2eda874e637c3f74480e), its dev log (c8f6f7893aceb8d2ffda8d2e34be14c2ed63d5e8dc74a949ea33ef3f99f7a49f) and its gate log (written by it; final ac0b0562b00148db23690f19e33b63f5449e19c05143e4abeee17fa242bdfc50). Standard-library and site-packages files (numpy etc.) are not listed.

## Rule from now on
Every vx01 stub lists EVERY file loaded at run time (imports, spec/importlib loads, data files, sidecars), found by a run-time trace like the one above, not by reading import lines only.
