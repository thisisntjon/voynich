"""vx01_b0_fitter_recovery.py -- B0 fitter recovery + four controls on true whole words (script 7). UNVERIFIED.

Plan: PLAN-X01-B-FALLBACK, cited only by sha256 4ed0314a7c8aef4d925dee4fbab3ef8eca3a005352062563e3708a0273e63f3e
(sections 1, 2, 4, 5, 6, 7, 8, 9). Base plan PLAN-X01-v5.1 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393.
WRITTEN FOR IV CODE REVIEW. NOT RUN. NOT FROZEN. Open code decisions: vx01_bf_CODE_DECISIONS_1.md (D-numbers below).

Modes (plan section 9 order; every mode is single process, BelowNormal, audit hook on):
  --build-params                 no seed, no planting: writes vx01_bf_plant_params.json (theta_plant, sources + sha256,
                                 fitter grids by module constant name, page-id agreement S67 vs S71 loaders).
  --calibrate-mei --cap-seconds S    dev masters 20261101 (oracle band) and 20261102 (4 books per candidate):
                                 writes vx01_b0_mei_map.json.
  --oracle --cap-seconds S       dev masters 20261101-103 x 3 transliterations: oracle-power >= 10/15 and oracle-MEI
                                 <= 4/15 in each of 9 dev cells; writes vx01_b0_oracle_results.json.
  --dev --cap-seconds S [--master 20261103] [--T ZL3b] [--producer P] [--control C] [--fold Q] [--W W]
                                 one dev cell (default ZL3b, all producers, all units) or a probe of one unit.
                                 Wall seconds per unit/producer go to the dev log (timing, plan section 9).
  --freeze-check                 no compute: unions the dev traces of THIS script hash and checks rules (a), (b), (d),
                                 the environment pin and coverage; writes runs/vx01_b0/freeze_check_<utc>.json.
  --write-stub --plan PATH --freeze-report PATH   writes vx01_b0_fitter_recovery.prereg.sha256 (refuses if it exists).
  --pin-check                    environment pin check only; one line to vx01_b0_fitter_recovery_pin_checks.log.
  --gate                         the one-shot gate (gate seeds 20261201-203), only after the stub verifies.
Heavy modes refuse without --cap-seconds (Eve: cap every heavy run; the cap is a hard stop, D-21).
"""
import sys
sys.dont_write_bytecode = True   # no .pyc writes: a write under ROOT would void a gate run (rule (c))
import ctypes  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import platform  # noqa: E402
import random  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from collections import Counter, OrderedDict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = Path(__file__).resolve().parent
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)
import vx01_common as C  # noqa: E402

# ===== BEGIN SHARED BLOCK (byte-identical in vx01_bf_rk.py and vx01_b0_fitter_recovery.py) =====
# Plan cited ONLY by sha256 (its title line still reads v4; IV-REVIEW-X01-B-FALLBACK-v5 nit 1).
BF_PLAN_SHA256 = "4ed0314a7c8aef4d925dee4fbab3ef8eca3a005352062563e3708a0273e63f3e"
V51_PLAN_SHA256 = "af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393"

# Environment pin (plan 4ed0314a section 8 rule (d), "Environment pin"). Values as written in the plan.
PIN_EXE = r"<home>/AppData/Local/Programs/Python/Python311/python.exe"
PIN_EXE_SHA256 = "5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec"
PIN_SYS_VERSION = "3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]"
PIN_SITECUSTOMIZE_SHA256 = "14bae2b6c8862fa98f4fa0396014c545c8daefdb871a2911203cc56be630e113"
PIN_DISTS = OrderedDict([
    ("numpy", "2.4.6"), ("scipy", "1.17.0"), ("torch", "2.11.0.dev20260115+cu128"), ("openpyxl", "3.1.5"),
    ("scikit-learn", "1.8.0"), ("joblib", "1.5.3"), ("threadpoolctl", "3.6.0"), ("pandas", "2.3.3"),
    ("pyarrow", "22.0.0"), ("Pillow", "12.1.0"), ("lxml", "6.0.2"), ("psutil", "7.2.1"), ("defusedxml", "0.7.1"),
    ("python-dateutil", "2.9.0.post0"), ("pytz", "2025.2"), ("six", "1.17.0"), ("tqdm", "4.67.1"),
    ("typing_extensions", "4.15.0"), ("colorama", "0.4.6"), ("charset-normalizer", "3.4.4"), ("pywin32", "311"),
])
# Module -> distribution exceptions named in the plan: torchgen belongs to torch; pywin32_bootstrap maps to no
# distribution and is pinned through pywin32 311 plus a hash of its file (taken at freeze).
PIN_MODULE_DIST = {"torchgen": "torch", "pywin32_bootstrap": "pywin32"}

# Process-creation audit events (plan section 8 rule (d) table). Any one = GATE-VOID / NO freeze. No allow-list.
PROC_EVENTS = frozenset([
    "subprocess.Popen", "_winapi.CreateProcess", "os.system", "os.spawn", "os.exec", "os.posix_spawn",
    "os.startfile", "os.startfile/2", "os.fork", "os.forkpty", "pty.spawn",
])

FOLDS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "M", "N", "O", "Q", "S", "T"]  # plan section 1
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
STAT_NAMES = ["Rw1_line", "h2", "rhythm", "TTR_300", "mean_len_eva", "CHARWIN_w"]  # k = 1..6, plan section 2
TTR_N, TTR_R = 300, 50
MIN_FREE_GB = 4.0
EXIT_VOID = 4
EXIT_CAP = 5

LOAD_LIST = OrderedDict([
    ('data/external/voynich-nu-ivtff/RF1b-er.txt', 'eb857a1f353b18983fbc25b954e1bbce227a26d99cefabfda9206ff9b57644d2'),  # D
    ('data/external/voynich-nu-ivtff/IT2a-n.txt', '7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5'),  # D
    ('vx01_bf_pathmap.py', '5629800d5e0dd27d69a426b269a47c648c10b0e635cf136c804d3754965c6fe4'),  # C
    ('m3_bakeoff_reconcile.py', '598472b8b6e2e08186241a0e44e23860d933e4c0c8e42653c5222a9335b2b299'),  # C1
    ('corpora.py', '2f2b3d4af32a054a63f4c90492e56dd0e2e76d7157de1317a0d62aeb40223518'),  # C2
    ('vparse.py', '0e317c9a762e77c2f9002a1b95af367911a6714a7585803ab8715178a95a91c1'),  # C3
    ('scoreboard/__init__.py', '4b9a400be433c2429864c638e823c742d6a54899e36597c0e6a2269eaf24c06f'),  # C4
    ('scoreboard/metrics_new.py', 'a59c9c17f8abe4cc8e29347854b02304eaa6a13c90b32f1890c1b1a60e7b23ed'),  # C5
    ('tools/vkb/features.py', '0a1f266fa7798448eb3791ba61752d9ab7aa8b3b52092d8e9dc9184a46493017'),  # C6
    ('tools/vkb/common.py', '0d47dd5579cdd397f87f744f1ca422919fa6c170457c51355b9cd3449800d56b'),  # C7
    ('tools/vkb/evidence.py', 'b70b99f3efa52931d7400cb72d5230b7b7394660276adf809cfb2c309fdb791d'),  # C8
    ('tools/findings_graph.py', 'afbed346288544232eaf31d97d954e383e27632dcdb8e81428513f8e2509e925'),  # C9
    ('vx01_common.py', 'cd4e5960f6e4058fd75f63478be58acf3b27ac54c6168a818c2d19a89325360a'),  # C10
    ('s57_local_memory_model.py', '4adc4796938b68f97d69e9d0b3b35fba6cb40ae68576538445352dfeb6063155'),  # C11
    ('a2_position.py', '426b7b649361a8776a2152b95ddde4380d23af73f2e5096ed70891abee7937b3'),  # C12
    ('g1_edge_joint.py', '4f955d34794293725c0063020ff00b1c5ed401aa38ee361cd2e4b345eca57ba7'),  # C13
    ('n1_habit_table.py', 'a40137f5ea2b8ef54d8829cf4bdecefa43f393cb53d0e7a526afe8010489afc1'),  # C14
    ('a1_profile.py', '0b20e37ec2254d277a7ed8e1bf73e03c9fbfd15f92c4289496dd0ee07392f3b2'),  # C15
    ('c2_section_generator.py', 'f21281d9fe41d309823117ab2517af5fddae6aead7ae84b5fec6114ea7c78c0a'),  # C16
    ('b4_selfcite_sim.py', '5fcdfdeb5e819ad33bbb1641cf2c5ce850b61b7fb9c85ec4bc21933caaf69d5a'),  # C17
    ('b5_nmf_topics.py', '0f1722dea55b3cceda5e6f622e6cedc99c779506b160862ad2c41e5168d41007'),  # C18
    ('c3_edge_coupling.py', '30b6ba47c9de4a36379ea0fea92a39a10da5ec6da4f4488266d4b3f68a827ffb'),  # C19
    ('f1_residual_order.py', '5bd3e11f07c7231d37efbedb644aa0d5644a4678b33ca030065fa9241c26ab76'),  # C20
    ('c4_naibbe_lines.py', '46b5e002aee66f6ee95f43c8f4edccffb68629e3a526416333eb8e552465260b'),  # C21
    ('f3_flow_choice.py', 'e0ac0ac62d6de16da094501a3fff26afd0551de681421ba66e6b8383d121e0ca'),  # C22
    ('f2_syllable_control.py', '440ff45dee9087abe9a6aa77976bbe46b369790cb113416bf5779658f49008bd'),  # C23
    ('s58_two_layer_heldout.py', '634e2534941bc1fc0b0942f2e6b331049835d8c61a4be8efe43e358ef6f5c0e3'),  # C24
    ('s61_joint_word_producer.py', '059a218127de9fbbde080dc78c658e6b31dec3ecae33be7c5b8b511b81266622'),  # C25
    ('s67_constrained_assembly_loqo.py', '8e5299212a84ec552ec00d34aaa9871333e65e98c2bacc7ae45ebf12cc8cc354'),  # C26
    ('s71_weakened_grille_and_sticky_naibbe_loqo.py', '9b4f024792c778ae300fd14d7d1e85f03243d50964b1f7f61ba09f1553c11a18'),  # C27
    ('s55_code_vs_generator.py', '56485b42c5c928c908a04be1a9b888a06c85088bc0b49589ef340d69ca220cec'),  # C28
    ('s64_naibbe_taxonomy.py', '6af7dbf59486209a8f5d0fac79850a9130a6d56797662e89a9e2a90111e30fe3'),  # C29
    ('s69_prefix_stream_memory.py', '11e722d4a0391d34228637da8b9c1872a6dc4ddd5dc1f2ff4e94f8c6a903c458'),  # C30
    ('s81_sticky_table_loqo.py', '418515ad0ecd7544fb4bba2fb0efcce1ecdbe198809c6bf830cbf31b57cd5063'),  # C31
    ('s91_line_pool_producer_loqo.py', '92dba656c9d74dfb972837d3bba070bb945c3ed59ef444448d5bd7aafcdee21a'),  # C32
    ('s87_core_layer_genre.py', 'd5ed585681670bc9e9eaf76449b7497a43bb33d6d4e689b0f0c337387f49d8db'),  # C33
    ('s80_a14_size_matched.py', '196cf61f3ca5af440e03fa5e1550d1ac7ee25ad32b35de3ec61d1965d6485a5b'),  # C34
    ('p4d1_core_order.py', '5a400968081214ba5f38bbe29bdabe42ddcfe6f949f491e5f579ce3f0e8b7a39'),  # C35
    ('s34_morphology_syntax_geography.py', '406b6d9fd5cfafc8830dec85ddb05cf6743a49024220bbc7429c9d303aba8625'),  # C36
    ('c1_quire_null.py', '9f0bb9a84f8b104804ced4743ae0a85d29b4428ad7982474f56b1090fb1d3f57'),  # C37
    ('p1_bifolio_null.py', '3aba99a6cdd124a50d6dba5636fb5c37e1bbec25a5568600ca07b9bfcd342dea'),  # C38
    ('m1_coordinates.py', '0ddc1eaafd22eb852b46f0fe2023b6cefaae3c3cbc9d59c47efc57a74e01626b'),  # C39
    ('tools/boxes.py', '8b4d2fdb08aa01f4b3402386b3ff1ccbc2041f662e10e8a440cae5d784874a65'),  # C40
    ('s29_q1_label_controls.py', '5676bd92ae940c63c7a55ba468558fb9119692bd6fe144fb9e56e07a2b730c02'),  # C41
    ('s76_segmenter_independence.py', '43f7aab7ad8c2bfa12e9d020f4749eb11281d51d7262c898cb499452c0184a29'),  # C42
    ('s56_core_repetition_lag.py', '1e5987dfee74c819b1f1c11abe0d386ce19f1ca730c39a30d45d4a534391b6a7'),  # C43
    ('runs/roach-r13/r13.py', 'd3c91e27791781b3d047ca56a926ae6862a0b9b3c37fd38cc89b1bc0215b3d94'),  # C44
    ('runs/roach-r10/r10.py', 'ada3231f0b6b0992767c7bd98fb206a4b1f138dcdb11d190cfc521ddaff4f69b'),  # C45
    ('runs/roach-r7/r7.py', '0d5e65db45b3c410bfbcab5b56d45adaab09b09c9af007b3546538a5b9f69b96'),  # C46
    ('scoreboard/score.py', '3a7b7c3efea13b884362f9f7f07551835bab8ca158ecdb43b946c96a8b3fbf1d'),  # C47
    ('data/translit/ZL3b_eva.meta.json', 'ce233477803a865365e53418f5e2b78c324fa0ea124b0aa46a9eb6a5189f7ef0'),  # D
    ('data/translit/RF1b.meta.json', 'c7d9bccba99b2610b9d80b4ce5f26f7d1ab54c12ec2364d0423d6b89f51da9df'),  # D
    ('data/translit/IT2a.meta.json', '0d0d3e758d1e308b0aee4b4d006f90cbc8090c081e0fcb3327de6734ac5e5fdf'),  # D
    ('data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx', '890835df665d33b96228d4a587030fee2bc1637783dc627b4e6aa584186cadcd'),  # D
    ('runs/s49/lang_latin_cremma.meta.json', '2f63d4beabdbc1b84821a74ce462eb3dcc80d43117ec33db6a5f8eb5aa7da3fc'),  # D
    ('runs/s57/fit_ZL3b.json', 'f329b589b20090096ff97df8fa61cda0eb826a7aec9d7b04a7fc3798024d96d6'),  # D
    ('runs/s57/fit_RF1b.json', '2291e6669f97965dc16cd8109f916e9f08f9abd3b58b4e81e54a30086484f096'),  # D
    ('runs/s57/fit_IT2a.json', '2187b06b94db4e5b8f79c8575adfba7f7aea1408c0e05f831ad4035c22a221bb'),  # D
    ('runs/s58/fit_ZL3b.json', '90c32cda1b0f932ac600d655a0360d5632e45ad6df9aeb282899685c86de4ff8'),  # D
    ('runs/s58/fit_RF1b.json', '43e4e0e41bd359594b0756b6614ae8a607e6219c17589476ad095d75b020903b'),  # D
    ('runs/s58/fit_IT2a.json', '0eadf610f64a5481d8cae184f83d30abd9010ab6591ab570568aaed481353a95'),  # D
    ('runs/s61/fit_ZL3b.json', 'c2a194731811c7f4a1bfaffa3fe7c8f4483fc6164028a1068f0a7dc792bb85c1'),  # D
    ('runs/s61/fit_RF1b.json', '945eb987cdc8720795a357df9a4f7770447d2223d611b3a136e418306b15d7b8'),  # D
    ('runs/s61/fit_IT2a.json', '5312811de64e508de6929522b6adc4dadb23a70477dda33b53b7f2ec1de0e6e4'),  # D
    ('runs/s67/cells.json', '607fa9d91d5f3b359324f1cb42ae45b6a360684fc273b2f6bd58fcd57856d8b8'),  # D
    ('runs/s81/cells.json', '297f598ed396d3c0ce511c185dec5e010fae8fe86cac6704d396fc1f01f23b1d'),  # D
    ('data/ZL3b-n.txt', 'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'),  # D
    ('vx01_gate_seeds.json', 'bd9961f3510c7f4ae50f45a693ff73b143447f89fdc1c10d7ed95cfb1068a3dd'),  # D
    ('runs/s91/folds/IT2a_A.json', '002a50c97cab5a0050d675876d12f367f494fb5d8b84aa08772aafc2313ed3a2'),  # D
    ('runs/s91/folds/IT2a_B.json', 'eb4b9ec51415456e4ae47163146f9d5f88451ffb2840f1cd687a27a366ff8100'),  # D
    ('runs/s91/folds/IT2a_C.json', '4b0980611ebf8962c1c3a7c9481415c7309e6e0e3f69bc0d4b1ae4bc6f84496f'),  # D
    ('runs/s91/folds/IT2a_D.json', 'eeef211231d9535070999ce21582b8d648ea0bd312fd3375516ddc4cb3372e00'),  # D
    ('runs/s91/folds/IT2a_E.json', '94f17130822ec0c5063ed78506303dbf742068483ad9188478e5cc594fb21a4a'),  # D
    ('runs/s91/folds/IT2a_F.json', 'fcf488a1d87b0dd9861fc31ab46f09700b522fe24ec81597a2ddb38358d508d2'),  # D
    ('runs/s91/folds/IT2a_G.json', 'c82d71a85a0256558508a2f590b818ec5c52d8226fe105b974e29585eec00459'),  # D
    ('runs/s91/folds/IT2a_H.json', 'ca208092b278fb448a11b327ca95ee3dcc98d4f3d35554e3ce95b367a5e1e392'),  # D
    ('runs/s91/folds/IT2a_I.json', 'ce773d52dbcbd86f871ac9c98b64d38a60cfb6ec04bd93452eb5773a4005b95f'),  # D
    ('runs/s91/folds/IT2a_M.json', '890db08e956b9e1173ac954b82af779f7408fc85d41275058b17933937e36519'),  # D
    ('runs/s91/folds/IT2a_N.json', '3dfebe76f50fe1f6d12878fca64dd13d76c32fbd028d4a07ee98c5a1f36d777f'),  # D
    ('runs/s91/folds/IT2a_O.json', 'eeec4faa6b649638842a29b7dd6999581676922ec7ef51c70945412a589757ac'),  # D
    ('runs/s91/folds/IT2a_Q.json', '4af7b6b9027d20ae66736a2a18bbde070fdf292efc7578998fc16b07ce246aac'),  # D
    ('runs/s91/folds/IT2a_S.json', 'dacda0b5bfc9236dbd65dc435c8799746a3daeb5c869f5dd1dac3c2e27d4335c'),  # D
    ('runs/s91/folds/IT2a_T.json', '1f4a4b89d2d75b372bdec20b9a556f0ff4cc138e5092f5e2c2d787bf7ba9a0b0'),  # D
    ('runs/s91/folds/RF1b_A.json', 'fa0f366e99d067cb507a3129061a5062518017cd483205bc969c67bb7242bbab'),  # D
    ('runs/s91/folds/RF1b_B.json', '18273cc47515e1132cc6842f47c10a5fbe344da05cd1be56b932628defbca137'),  # D
    ('runs/s91/folds/RF1b_C.json', '52510de8620bb777819cb62a2a9a3fac55defdb383e1fcfc198c99ffcd624059'),  # D
    ('runs/s91/folds/RF1b_D.json', '532932473a7074dda7be186cac69dac4223149b174c11dff4944c8c9310be34b'),  # D
    ('runs/s91/folds/RF1b_E.json', '60bd9f399531fb7e625a4e902d8e295fe7285d3a59a0e947f2b1db24d6e2fadd'),  # D
    ('runs/s91/folds/RF1b_F.json', 'b02ee6c15fb07acbb6a3df1884f9555c43d2978f87ed3160414c575402bcf347'),  # D
    ('runs/s91/folds/RF1b_G.json', 'ff728e2c0a4d4980e855d0d5f45afbd5a907dc865eaab6933ed6f66cd6884a44'),  # D
    ('runs/s91/folds/RF1b_H.json', '51cfe4a6b6f1df6bd6b51a32907022b8f0d9e365b27b8c29611921d8713c4bbb'),  # D
    ('runs/s91/folds/RF1b_I.json', 'f0f0f70a4caa4cb322d8c7e6baaab95ec9dd839fd17162bf8793867bafb8066f'),  # D
    ('runs/s91/folds/RF1b_M.json', '0820fdcedf534ea9f36557bbbdee55f7c4dae582bcb50977c34ae9a284f16491'),  # D
    ('runs/s91/folds/RF1b_N.json', '72662746548d7e9049542459e813f5e46e585f5b30d6af1d5ab7a93972c30efc'),  # D
    ('runs/s91/folds/RF1b_O.json', 'e482fb1cd0e34bdd1ffa4c7f78af87912a8c7d41dfdd7838198335a9f7c4edac'),  # D
    ('runs/s91/folds/RF1b_Q.json', '5d16372dcf05adad831267297e891d2dd0baef6de112797347f58f9d2b264c81'),  # D
    ('runs/s91/folds/RF1b_S.json', 'a22c43627db8c028105a8423d85cae43b3808387d97e91f851f21e35de58e496'),  # D
    ('runs/s91/folds/RF1b_T.json', '7420f0f53a04bde38f550dba8fa39d30f94b43758ffccdf497bee450e97f769a'),  # D
    ('runs/s91/folds/ZL3b_A.json', '7d1d88baf53eec15233b971e60828387baef06aaf6e73806562e56a42ea1ccc0'),  # D
    ('runs/s91/folds/ZL3b_B.json', '49e2a666cb2e534e74091e875b070c04bb9e661cf91312e8a6a4699687ac60b3'),  # D
    ('runs/s91/folds/ZL3b_C.json', '35c9b382246c45f44c8c4adf86c3515831690407af0b79201331b2790ab31499'),  # D
    ('runs/s91/folds/ZL3b_D.json', 'bcedd6986d5844b226306b80c5eb9b4079ff42b4a67b9f103363086393f66a4b'),  # D
    ('runs/s91/folds/ZL3b_E.json', 'b5e8fccb08cef267b893d3a7baeb0380e843212c80cc07133acedd13e2df0c96'),  # D
    ('runs/s91/folds/ZL3b_F.json', '65dbf71bbf9e81f3b976e2fd53b9be902c58dd2f05bfe30b935e1abc90583f65'),  # D
    ('runs/s91/folds/ZL3b_G.json', '911146dc81f836ad1532528a9ae6690d9ecd6eadec1b3074ecf20a7b74aa2bf6'),  # D
    ('runs/s91/folds/ZL3b_H.json', 'cd5d0f1a2ec8a12bd6ac660a77734d6b09953500e34c6972d0170352cf6beada'),  # D
    ('runs/s91/folds/ZL3b_I.json', '4e94bf414ade34c0df22976687fcf577305aa3504812047af7cb68220fe63f6c'),  # D
    ('runs/s91/folds/ZL3b_M.json', 'f6dcdd58f02600d78546d0aec73a032a2eed405e8b12f2b365a6712149629cfd'),  # D
    ('runs/s91/folds/ZL3b_N.json', '11e4a84d3d14f9efa655dc4c9a51a64904126c7002d3ea5ef07a0b9b5b8e3862'),  # D
    ('runs/s91/folds/ZL3b_O.json', '9f71834af67c53df98dfc23b75c4a5654e1ed7b6a2d02c2420b797dd2aca4f16'),  # D
    ('runs/s91/folds/ZL3b_Q.json', 'a024bd5a6bb07f432f1c5a761dd41e412d0e0742c2d90ec64504043012a9324b'),  # D
    ('runs/s91/folds/ZL3b_S.json', '0f3139a0e0a122c6dbf34e5c73050060fdd8940653900fa46efca3d464b2d82c'),  # D
    ('runs/s91/folds/ZL3b_T.json', '15524a438cb85e6d46e4cacae58f77ecdbc164f9f92fa1cab7662f8bb36f3975'),  # D
])


def rel_root(p):
    """Normalised path relative to ROOT with '/' separators, or None if outside ROOT.
    A __pycache__/<name>.cpython-*.pyc read is mapped to its <name>.py (plan section 8 rule (a))."""
    try:
        ap = os.path.normcase(os.path.abspath(os.fsdecode(p)))
    except Exception:
        return None
    rt = os.path.normcase(ROOT_STR)
    if not (ap == rt or ap.startswith(rt + os.sep)):
        return None
    r = os.path.relpath(ap, rt).replace("\\", "/")
    parts = r.split("/")
    if len(parts) >= 2 and parts[-2] == "__pycache__" and parts[-1].endswith(".pyc"):
        r = "/".join(parts[:-2] + [parts[-1].split(".")[0] + ".py"])
    return r


def norm_load_key(r):
    return os.path.normcase(r) if r is not None else None


def _open_is_write(mode, flags):
    if isinstance(mode, str):
        return any(c in mode for c in "wax+")
    try:
        f = int(flags)
    except Exception:
        return False
    if f < 0:
        return False
    return bool(f & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))


class AuditHook:
    """One hook for every mode (plan section 8 rules (a), (c), (d)).
    record mode (dev / freeze trace): every open (read or write) and every process event is recorded; a process
      event is also BLOCKED (the hook raises, so the spawn does not happen) and the run is marked NO-FREEZE.
    gate mode: a read of a file under ROOT that is not allowed, a write anywhere that is not a declared output,
      or any process event writes the final gate-log line GATE-VOID and stops the process (os._exit(4)).
    sys.addaudithook hooks cannot be removed; the hook lives until the process ends."""

    def __init__(self, gate, gate_void_cb=None, allowed_reads=(), allowed_write_files=(), allowed_write_dirs=()):
        self.gate = gate
        self.void_cb = gate_void_cb
        self.allowed_reads = set(norm_load_key(r) for r in allowed_reads)
        self.allowed_write_files = set(os.path.normcase(os.path.abspath(p)) for p in allowed_write_files)
        self.allowed_write_dirs = [os.path.normcase(os.path.abspath(d)) for d in allowed_write_dirs]
        self.reads_root = set()
        self.writes = set()
        self.proc_events = []
        self.busy = False

    def _write_ok(self, ap):
        if ap in self.allowed_write_files:
            return True
        return any(ap == d or ap.startswith(d + os.sep) for d in self.allowed_write_dirs)

    def __call__(self, event, args):
        if self.busy:
            return
        if event == "open":
            path = args[0] if args else None
            if path is None or isinstance(path, int):
                return
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            w = _open_is_write(mode, flags)
            try:
                ap = os.path.normcase(os.path.abspath(os.fsdecode(path)))
            except Exception:
                return
            r = rel_root(path)
            if w:
                self.writes.add(ap)
                if self.gate and not self._write_ok(ap):
                    self._void("GATE-VOID " + ap, dict(kind="write", path=ap))
            elif r is not None:
                self.reads_root.add(r)
                if self.gate and norm_load_key(r) not in self.allowed_reads:
                    self._void("GATE-VOID " + r, dict(kind="read", path=r))
            return
        if event in PROC_EVENTS:
            desc = []
            for a in args[:3]:
                try:
                    desc.append(str(a)[:300])
                except Exception:
                    desc.append("?")
            self.proc_events.append([event] + desc)
            if self.gate:
                self._void("GATE-VOID PROC %s %s" % (event, " ".join(desc)), dict(kind="proc", event=event, args=desc))
            raise RuntimeError("vx01_bf audit hook: process creation blocked (%s); NO freeze" % event)

    def _void(self, line, info):
        self.busy = True
        try:
            if self.void_cb is not None:
                self.void_cb(line, info)
        finally:
            sys.stderr.write(line + "\n")
            sys.stderr.flush()
            os._exit(EXIT_VOID)

    def snapshot(self):
        return dict(reads_root=sorted(self.reads_root), writes=sorted(self.writes), proc_events=list(self.proc_events))


def install_hook(hook):
    """platform.uname() is called BEFORE the hook goes in (plan section 8 rule (e)): it caches the result, so the
    later platform.machine() call reached through scipy/numpy.testing spawns nothing. No allow-list."""
    platform.uname()
    sys.addaudithook(hook)
    return hook


def pt_now():
    """Local wall time with its UTC offset (Skynet runs in America/Los_Angeles). No process is spawned."""
    d = datetime.now().astimezone()
    return d.isoformat(timespec="seconds") + " " + (d.tzname() or "")


def free_gb():
    try:
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / (2 ** 30)
    except Exception:
        return float("nan")


def run_path_distributions():
    """Distributions of every site-packages module in sys.modules (by distribution name), plus module names that
    map to no distribution. Read-only (importlib.metadata)."""
    import importlib.metadata as md
    pdist = md.packages_distributions()
    sp = [os.path.normcase(os.path.abspath(p)) for p in sys.path if p and "site-packages" in p.lower()]
    dists, unmapped = set(), set()
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if not f or not os.path.isabs(f):
            continue  # relative __file__ (torch _ops.py / _classes.py) are filtered, plan section 8 rule (a)
        af = os.path.normcase(os.path.abspath(f))
        if not any(af.startswith(s + os.sep) for s in sp):
            continue
        top = name.split(".")[0]
        if top in PIN_MODULE_DIST:
            dists.add(PIN_MODULE_DIST[top])
            continue
        ds = pdist.get(top)
        if ds:
            dists.update(ds)
        else:
            unmapped.add(top)
    return sorted(dists), sorted(unmapped)


def env_measure():
    """The whole-environment pin, measured on the running process (plan section 8 rule (d))."""
    import importlib.metadata as md
    exe = sys.executable
    sc = os.path.join(sys.prefix, "Lib", "site-packages", "sitecustomize.py")
    vers = OrderedDict()
    for d in PIN_DISTS:
        try:
            vers[d] = md.version(d)
        except md.PackageNotFoundError:
            vers[d] = "MISSING"
    pyb = None
    try:
        import importlib.util as iu
        spb = iu.find_spec("pywin32_bootstrap")
        if spb is not None and spb.origin and os.path.exists(spb.origin):
            pyb = (spb.origin, C.sha256_file(spb.origin))
    except Exception:
        pyb = None
    dl = json.dumps(vers, separators=(",", ":"))
    return OrderedDict([
        ("exe", exe), ("exe_sha256", C.sha256_file(exe) if os.path.exists(exe) else "MISSING"),
        ("sys_version", sys.version), ("sys_version_sha256", C.sha256_text(sys.version)),
        ("vv_sha256", C.sha256_text("Python " + sys.version)),      # the `python -VV` output line (D-26)
        ("sitecustomize_sha256", C.sha256_file(sc) if os.path.exists(sc) else "MISSING"),
        ("dists", vers), ("dists_sha256", C.sha256_text(dl)),
        ("pywin32_bootstrap_path", pyb[0] if pyb else "MISSING"),
        ("pywin32_bootstrap_sha256", pyb[1] if pyb else "MISSING"),
    ])


ENV_KEYS = ("exe_sha256", "sys_version_sha256", "vv_sha256", "sitecustomize_sha256", "dists_sha256",
            "pywin32_bootstrap_sha256")


def env_mismatch(env, want=None):
    """List of mismatches against the plan's pin values, and (if given) against stub values `want`."""
    bad = []
    if os.path.normcase(env["exe"]) != os.path.normcase(PIN_EXE):
        bad.append("exe path")
    if env["exe_sha256"].lower() != PIN_EXE_SHA256:
        bad.append("exe sha256")
    if env["sys_version"] != PIN_SYS_VERSION:
        bad.append("sys.version")
    if env["sitecustomize_sha256"].lower() != PIN_SITECUSTOMIZE_SHA256:
        bad.append("sitecustomize sha256")
    for d, v in PIN_DISTS.items():
        if env["dists"].get(d) != v:
            bad.append("dist %s=%s" % (d, env["dists"].get(d)))
    if want is not None:
        for k in ENV_KEYS:
            if str(want.get("env_" + k, "")).lower() != str(env[k]).lower():
                bad.append("stub env_" + k)
    return bad


def env_log_record(env, where, bad):
    """IV add-on: every pin check writes one log line with its PT time and the output hashes."""
    return dict(event="ENV-PIN-CHECK", where=where, t=C.utc_now(), t_pt=pt_now(),
                exe_sha256=env["exe_sha256"], sys_version_sha256=env["sys_version_sha256"], vv_sha256=env["vv_sha256"],
                sitecustomize_sha256=env["sitecustomize_sha256"], dists_sha256=env["dists_sha256"],
                pywin32_bootstrap_sha256=env["pywin32_bootstrap_sha256"], match=not bad, mismatches=bad)


def write_new(path, text):
    """Never overwrite: refuse if the file exists."""
    path = Path(path)
    if path.exists():
        C.refuse("output %s exists; never overwrite" % path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return C.sha256_file(path)


# ---------------------------------------------------------------- the six statistics (plan section 2)
def gl(w):
    return corpora.to_glyphs(w, corpora.GLYPHS)


def _num(x):
    if x is None:
        return None
    try:
        x = float(x)
    except Exception:
        return None
    return x if math.isfinite(x) else None


def stat_rw1(lines_q):                     # k=1, features.py:56-80
    return _num(F.rw1(lines_q)[1])


def stat_h2(toks_q):                       # k=2, features.py:39-53
    return _num(F.h1_h2([gl(w) for w in toks_q])[1])


def stat_rhythm(pages_q, tag):             # k=3, features.py:30-31, 83-112; pair-weighted as s113:150-156
    num = den = 0.0
    for pid, lines_p in pages_q:
        _, exc, n = F.rhythm([[len(gl(w)) for w in l] for l in lines_p if l],
                             np.random.default_rng(F.seed(tag, pid, "rhythm")))
        if exc is not None and n:
            num += float(exc) * n
            den += n
    return _num(num / den) if den > 0 else None


def stat_ttr300(toks_q, tag, q):           # k=4, own code
    if len(toks_q) < TTR_N:
        return None
    rng = np.random.default_rng(F.seed(tag, q, "ttr"))
    vals = []
    for _ in range(TTR_R):
        idx = rng.choice(len(toks_q), TTR_N, replace=False)
        vals.append(len(set(toks_q[i] for i in idx)) / TTR_N)
    return float(np.mean(vals))


def stat_meanlen(toks_q):                  # k=5, = r13 t8 (r13.py:206), EVA characters
    return float(np.mean([len(w) for w in toks_q])) if toks_q else None


def stat_charwin(train_pages, pages_q):    # k=6, m3_bakeoff_reconcile.py:87-97, 100-111, 118-140
    pages = [dict(id=pid, lines=ls) for pid, ls in train_pages] + [dict(id=pid, lines=ls) for pid, ls in pages_q]
    n_train = len(train_pages)
    acc = M3.score_folds(pages, [list(range(n_train, len(pages)))])
    a, b = acc["unigram-GT-renorm"], acc["char3-WB"]
    if not a["tok"] or not b["tok"]:
        return None
    return _num(a["bits"] / a["tok"] - b["bits"] / b["tok"])


def quire_stats(pages_q, q, tag, charwin_train=None, ks=(1, 2, 3, 4, 5, 6)):
    """pages_q: [(pid, lines)] of ONE quire in file order. charwin_train: [(pid, lines)] train pages (needed for k=6).
    Returns {k: value or None}."""
    lines_q = [l for _, ls in pages_q for l in ls]
    toks_q = [w for l in lines_q for w in l]
    out = {}
    for k in ks:
        if k == 1:
            out[k] = stat_rw1(lines_q)
        elif k == 2:
            out[k] = stat_h2(toks_q)
        elif k == 3:
            out[k] = stat_rhythm(pages_q, tag)
        elif k == 4:
            out[k] = stat_ttr300(toks_q, tag, q)
        elif k == 5:
            out[k] = stat_meanlen(toks_q)
        elif k == 6:
            out[k] = stat_charwin(charwin_train, pages_q)
    return out


def text_quire_stats(pages, tag, quires=FOLDS, ks=(1, 2, 3, 4, 5, 6)):
    """pages: [(pid, quire, lines)]. CHARWIN train for quire q = all pages of the SAME text with quire != q."""
    out = {}
    for q in quires:
        pq = [(p, ls) for p, qq, ls in pages if qq == q]
        tr = [(p, ls) for p, qq, ls in pages if qq != q] if 6 in ks else None
        out[q] = quire_stats(pq, q, tag, tr, ks)
    return out
# ===== END SHARED BLOCK =====


SELF = Path(__file__).resolve()
SELF_SHA256 = C.sha256_file(SELF)
NAME = C.script_name(SELF)
STUB = C.stub_path(SELF)
DEV_LOG = C.dev_log_path(SELF)
GATE_LOG = C.gate_log_path(SELF)
PIN_LOG = ROOT / (NAME + "_pin_checks.log")
RUN_DIR = ROOT / "runs" / "vx01_b0"
PARAMS_FILE = ROOT / "vx01_bf_plant_params.json"
MEI_FILE = ROOT / "vx01_b0_mei_map.json"
ORACLE_FILE = ROOT / "vx01_b0_oracle_results.json"
RESULTS_GATE = ROOT / "results_vx01_b0.txt"
RK_SCRIPT = ROOT / "vx01_bf_rk.py"
RK_STUB = ROOT / "vx01_bf_rk.prereg.sha256"
RK_GATE_LOG = ROOT / "vx01_bf_rk_gate_runs.log"
RK_TABLE = ROOT / "vx01_bf_rk_table.json"
DEV_MASTERS = list(C.DEV_SEEDS["B0"])            # 20261101, 20261102, 20261103 (plan section 6)
MEI_BAND_MASTER, MEI_BOOK_MASTER, TIMING_MASTER = 20261101, 20261102, 20261103
N_COPY = 200                                     # plan section 4 "Band"
ENV_Q = (0.5, 99.5)
UNDEF_COPY_FRAC = 0.10                           # plan section 2: undefined on >10% of the 200 copies
N_MEI_BOOKS = 4                                  # plan section 5
HARD_FACTOR = 1.5                                # plan section 7 hardness
POWER_MIN, CTRL_MAX = 10, 4                      # v5.1 rule 2 counts
PAIRS = [(i, j) for i in range(1, 7) for j in range(i + 1, 7)]   # 15 pairs, lexicographic (plan section 5)
ARGS = sys.argv[1:]
MODES = ("--build-params", "--calibrate-mei", "--oracle", "--dev", "--freeze-check", "--write-stub", "--pin-check",
         "--gate")
MODE = next((a for a in ARGS if a in MODES), None)
if MODE is None:
    print(__doc__)
    sys.exit(2)


def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


# Producers (plan section 1 table), in the gate order of plan section 9 condition (ii): F-34 C1, F-41 C2, F-23, F-30.
PRODUCERS = OrderedDict([
    ("s81_fit",    dict(finding="F-34 C1", unit_label="no qualifier", fitted=True)),
    ("s81_75",     dict(finding="F-34 C1", unit_label="no qualifier", fitted=False)),
    ("LP91",       dict(finding="F-41 C2", unit_label="built on Slot units", fitted=True)),
    ("s57",        dict(finding="F-23", unit_label="built on Slot units", fitted=True)),
    ("s58",        dict(finding="F-23", unit_label="built on Slot units", fitted=True)),
    ("s61",        dict(finding="F-23", unit_label="built on Slot units", fitted=True)),
    ("CA",         dict(finding="F-23", unit_label="built on Slot units", fitted=True)),
    ("CA0",        dict(finding="F-23", unit_label="built on Slot units", fitted=True)),
    ("r13A",       dict(finding="F-23", unit_label="no qualifier", fitted=True)),
    ("WTG_global", dict(finding="F-30", unit_label="built on Slot units", fitted=False)),
    ("WTG_scribe", dict(finding="F-30", unit_label="built on Slot units", fitted=False)),
    ("r13B",       dict(finding="F-30", unit_label="built on S1 units", fitted=True)),
])
FINDING_ORDER = ["F-34 C1", "F-41 C2", "F-23", "F-30"]
# Wrong-family pairings, primary then alternate (v5.1:145 list, unchanged; plan section 7). "WTG" = WTG_global (D-11).
PAIRINGS = {"s57": ["WTG_global", "LP91"], "s58": ["WTG_global", "LP91"], "s61": ["WTG_global", "LP91"],
            "CA": ["LP91", "WTG_global"], "CA0": ["LP91", "WTG_global"],
            "WTG_global": ["s57", "LP91"], "WTG_scribe": ["s57", "LP91"],
            "s81_fit": ["s57", "LP91"], "s81_75": ["s57", "LP91"],
            "LP91": ["WTG_global", "s57"], "r13A": ["r13B"], "r13B": ["r13A"]}
SLOT_BUILT = {"s57", "s58", "s61", "CA", "CA0", "WTG_global", "WTG_scribe", "LP91"}

# ---------------------------------------------------------------- early checks + hook (before the heavy imports)
_stub_kv, _stub_hl = ({}, [])
if MODE == "--gate":
    if not STUB.exists():
        C.refuse("no stub %s" % STUB.name)
    _stub_kv, _stub_hl = C.parse_stub(STUB)
    if _stub_kv.get("bf_plan_sha256", "").lower() != BF_PLAN_SHA256:
        C.refuse("stub bf_plan_sha256 is not %s" % BF_PLAN_SHA256)
    if GATE_LOG.exists():
        _me = C.sha256_file(SELF)
        for _r in C.read_chain(GATE_LOG):
            if _r.get("event") == "GATE-VOID" and _r.get("script_sha256") == _me:
                C.refuse("an earlier gate run of this script was VOID; it counts as the one gate run (rule (c))")


def _gate_void(line, info):
    C.append_chained(GATE_LOG, dict(t=C.utc_now(), t_pt=pt_now(), event="GATE-VOID", line=line, info=info,
                                    script_sha256=C.sha256_file(SELF)))


if MODE == "--gate":
    _allowed = [p for _, p in _stub_hl] + [rel_root(x) for x in (SELF, STUB, DEV_LOG, GATE_LOG, C.GATE_SEEDS_FILE,
                                                              Path(C.__file__), RESULTS_GATE)]
    HOOK = install_hook(AuditHook(True, _gate_void, _allowed, [GATE_LOG, RESULTS_GATE], [RUN_DIR / "gate"]))
elif MODE in ("--build-params", "--calibrate-mei", "--oracle", "--dev"):
    HOOK = install_hook(AuditHook(False))
else:
    HOOK = None

# ---------------------------------------------------------------- heavy imports (read-only use of frozen modules)
import numpy as np  # noqa: E402
import corpora  # noqa: E402
import m3_bakeoff_reconcile as M3  # noqa: E402
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("vkb_features", str(ROOT / "tools" / "vkb" / "features.py"))
F = _iu.module_from_spec(_spec)
_spec.loader.exec_module(F)
import s57_local_memory_model as S57  # noqa: E402
import s58_two_layer_heldout as S58  # noqa: E402
import s61_joint_word_producer as S61  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s71_weakened_grille_and_sticky_naibbe_loqo as S71  # noqa: E402
import s81_sticky_table_loqo as S81  # noqa: E402
import s91_line_pool_producer_loqo as S91  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402
import vx01_bf_pathmap as PM  # noqa: E402
R13 = None          # loaded in main() through vx01_bf_pathmap.load_r13, so its PATHMAP records reach this run's log
LOG_PATH = None     # dev or gate log of this run


def log(rec):
    rec = dict(rec)
    rec.setdefault("t", C.utc_now())
    rec.setdefault("script_sha256", SELF_SHA256)
    return C.append_chained(LOG_PATH, rec)


# ---------------------------------------------------------------- data (plan sections 1 and 4 "Page meta")
REAL, META, LAYOUT = {}, {}, {}


def load_data():
    for T, fn in TRANSLITS.items():
        REAL[T] = S67.load_pages(ROOT / "data" / "translit" / ("%s.meta.json" % fn))    # s67:193-202
        META[T] = OrderedDict((str(p["id"]), p) for p in S71.load_translit_meta(T))     # s71:983-1004
    folds = S67.folds_of(REAL["ZL3b"])                                                    # s67:579-581
    if folds != FOLDS:
        C.refuse("S67.folds_of(ZL3b) = %s, not the plan's 15 quires" % folds)
    _letters_and_tables()


def page_meta(T, pid):
    m = META[T].get(pid, {})
    return dict(hand=str(m.get("hand", "?")), section=str(m.get("section", "?")), para=m.get("para"))


def full_layout(T, P):
    """T's full layout for a planted book: (pid, quire, words-per-line). WTG uses the meta lines (s101:718-722, D-07);
    every other producer uses S67.load_pages lines (s101:685-686). WTG takes every meta page, as s101:718 does."""
    if P.startswith("WTG"):
        return [(pid, str(m.get("quire", "?")), [len(l) for l in m["lines"]]) for pid, m in META[T].items()]
    return [(pid, q, [len(l) for l in ls]) for pid, q, ls in REAL[T]]


def layout_of(pages):
    return [(pid, q, [len(l) for l in ls]) for pid, q, ls in pages]


_LT = {}


def _letters_and_tables():
    _LT["K"] = S81.key_tables()                      # s81:205-208 -> S64.load_greshko (openpyxl)
    _LT["letters"] = S81.plain_letters("latin_cremma")   # s81:211-215


# ---------------------------------------------------------------- producer objects (s101:683-743 rule, plan section 4)
def build(P, T, train_pages):
    """Producer object trained on train_pages [(pid, quire, lines)] of the text under test (or of real T, quires != 'A',
    for planting). seg_voy = SlotSegmenter on those training words, for the Slot-built producers only."""
    tr = [ls for _, _, ls in train_pages]
    words = [w for ls in tr for l in ls for w in l]
    if P == "s57":
        return dict(prod=S57.Producer(tr, SlotSegmenter(words)))                    # s101:689
    if P == "s58":
        return dict(prod=S58.TLProducer(tr, SlotSegmenter(words)))                  # s101:695
    if P == "s61":
        return dict(prod=S61.JWProducer(tr, SlotSegmenter(words), use_state=True))  # s101:701
    if P in ("CA", "CA0"):
        return dict(prod=S67.CAProducer(tr, SlotSegmenter(words), use_class=True))  # s101:707
    if P in ("WTG_global", "WTG_scribe"):
        tm = [dict(id=pid, quire=q, lines=ls, **page_meta(T, pid)) for pid, q, ls in train_pages]
        return dict(prod=S71.WTGProducer(tm, SlotSegmenter(words), S71.WTG_PARAMS))  # s101:713-714; s71:420-425
    if P in ("s81_fit", "s81_75"):
        return dict()                                                                # plaintext + tables only (s101:729)
    if P == "LP91":
        seg = SlotSegmenter(words)                                                   # s101:734-737
        ctr = [(pid, q, [[seg.segment(w)[1] for w in l] for l in ls]) for pid, q, ls in train_pages]
        glob = Counter(c for _, _, ls in ctr for l in ls for c in l if c)
        B = S91.bigram_of([(pid, ls) for pid, q, ls in ctr])
        return dict(prod=S91.LP91(glob, B), seg=seg)
    if P in ("r13A", "r13B"):
        return dict(fit=R13.Fit([(q, pid, ws) for pid, q, ls in train_pages for ws in ls]))   # r13.py:110-123
    raise ValueError(P)


def _regroup(layout, out_lines):
    """r13 generators return one (quire, page, words) tuple per line; regroup them into pages in layout order."""
    by = OrderedDict((pid, []) for pid, _, _ in layout)
    for _, pid, ws in out_lines:
        by[pid].append(list(ws))
    return [(pid, q, by[pid]) for pid, q, _ in layout]


def gen(P, T, obj, prm, layout, seed):
    """One text on `layout` [(pid, quire, words-per-line)] with parameters prm and integer seed. -> [(pid, q, lines)]."""
    if P in ("s57", "s58", "s61", "CA", "CA0"):
        prod = obj["prod"]
        prod.set_params(prm)
        pg = prod.text(seed, [len(lens) for _, _, lens in layout])       # line counts only (s101:691, D-06)
        return [(pid, q, pg[i]) for i, (pid, q, _) in enumerate(layout)]
    if P in ("WTG_global", "WTG_scribe"):
        prod, rng, out = obj["prod"], random.Random(seed), []
        for pid, q, lens in layout:
            m = page_meta(T, pid)
            hand = m["hand"] if P == "WTG_scribe" else "ALL"              # s101:721-722 (page hand, D-08)
            out.append((pid, q, prod.generate_page(rng, len(lens), hand=hand, line_lens=lens, para_flags=m["para"])))
        return out
    if P in ("s81_fit", "s81_75"):
        lines = S81.encipher(_LT["letters"], _LT["K"], [lens for _, _, lens in layout], "line", prm["p"], seed=seed)
        return [(pid, q, lines[i]) for i, (pid, q, _) in enumerate(layout)]                # s101:729
    if P == "LP91":
        prod, seg = obj["prod"], obj["seg"]
        prod.set_params(prm)
        skel = [lens for _, _, lens in layout]
        cipher = S81.encipher(_LT["letters"], _LT["K"], skel, "line", S91.STICKY_P, seed=seed)  # s101:740 (D-13)
        _, wp = prod.text(list(layout), seed, cipher=cipher, seg=seg)                           # s101:741
        return [(pid, q, wp[i][1]) for i, (pid, q, _) in enumerate(layout)]
    if P == "r13A":
        lay = [(q, pid, n) for pid, q, lens in layout for n in lens]
        return _regroup(layout, R13.gen_A(obj["fit"], lay, np.random.default_rng(seed), prm["q"], prm["e"]))
    if P == "r13B":
        lay = [(q, pid, n) for pid, q, lens in layout for n in lens]
        out = R13.gen_B(obj["fit"], lay, np.random.default_rng(seed), int(prm["R"]), prm.get("table"), prm.get("offs"))
        return _regroup(layout, out)
    raise ValueError(P)


def public(prm):
    return {k: v for k, v in prm.items() if k not in ("table", "offs")}


# ---------------------------------------------------------------- fitter schedules with L (plan section 4 "Fitter")
class Evaluator:
    """Cache by parameter key (as the original fitters); eval index = order of first evaluation (seed rule, D-04)."""

    def __init__(self, keys, Lfun, force=None):
        self.keys, self.Lfun, self.force = keys, Lfun, force
        self.cache = OrderedDict()

    def __call__(self, prm):
        prm = dict(prm)
        if self.force:
            prm = self.force(prm)
        key = tuple(round(float(prm[k]), 6) for k in self.keys)
        if key not in self.cache:
            e = len(self.cache)
            self.cache[key] = (float(self.Lfun(prm, e)), dict(prm))
        return self.cache[key]


def sched_s57(ev):
    """Rebuilds s57_local_memory_model.py:416-446 (stages A, B, C; fit() ends at :446), L in place of loss."""
    q0 = dict(q_pre=0.25, q_suf=0.25, q_core=0.25)
    best = None
    for pc in S57.GRID_P:
        for tau in S57.GRID_TAU:
            for a in S57.GRID_A:
                prm = dict(p_copy=pc, tau=tau, a=a, **q0)
                L = ev(prm)[0]
                if best is None or L < best[0]:
                    best = (L, prm)
    bA = best[1]
    for i in range(11):
        for j in range(11 - i):
            for k in range(11 - i - j):
                prm = dict(bA, q_pre=i / 10, q_suf=j / 10, q_core=k / 10)
                L = ev(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    bq = {k: best[1][k] for k in ("q_pre", "q_suf", "q_core")}
    ip, it, ia = S57.GRID_P.index(bA["p_copy"]), S57.GRID_TAU.index(bA["tau"]), S57.GRID_A.index(bA["a"])
    for pc in S57.GRID_P[max(0, ip - 2): ip + 3]:
        for tau in S57.GRID_TAU[max(0, it - 1): it + 2]:
            for a in S57.GRID_A[max(0, ia - 1): ia + 2]:
                prm = dict(p_copy=pc, tau=tau, a=a, **bq)
                L = ev(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    return ev(best[1])


def sched_s58(ev):
    """Rebuilds s58_two_layer_heldout.py:290-321 (stages A, B, C; fit() ends at :321), L in place of loss."""
    best = None
    for pc in S58.GRID_P:
        for tau in S58.GRID_TAU:
            for a in S58.GRID_A:
                prm = dict(p_copy=pc, tau=tau, a=a, q_core=0.25)
                L = ev(prm)[0]
                if best is None or L < best[0]:
                    best = (L, prm)
    bA = best[1]
    for qc in S58.GRID_QC:
        prm = dict(bA, q_core=qc)
        L = ev(prm)[0]
        if L < best[0]:
            best = (L, prm)
    qc = best[1]["q_core"]
    ip, it, ia = S58.GRID_P.index(bA["p_copy"]), S58.GRID_TAU.index(bA["tau"]), S58.GRID_A.index(bA["a"])
    for pc in S58.GRID_P[max(0, ip - 2): ip + 3]:
        for tau in S58.GRID_TAU[max(0, it - 1): it + 2]:
            for a in S58.GRID_A[max(0, ia - 1): ia + 2]:
                prm = dict(p_copy=pc, tau=tau, a=a, q_core=qc)
                L = ev(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    return ev(best[1])


def sched_s61(ev):
    """Rebuilds s61_joint_word_producer.py:315-360 (stages A0, A, B, C, D; fit() ends at :361), L in place of loss.
    Stage A0 used only the types part of the s57 loss (s61:319); L has no types part, so A0 uses the full L (D-09)."""
    a0 = None
    for pn in S61.GRID_PN:
        prm = dict(p_copy=0.0, tau=1.0, a=0.0, q_edit=0.25, p_new=pn)
        lv = ev(prm)[0]
        if a0 is None or lv < a0[0]:
            a0 = (lv, prm)
    pn0 = a0[1]["p_new"]
    best = None
    for pc in S61.GRID_P:
        for tau in S61.GRID_TAU:
            for a in S61.GRID_A:
                prm = dict(p_copy=pc, tau=tau, a=a, q_edit=0.25, p_new=pn0)
                L = ev(prm)[0]
                if best is None or L < best[0]:
                    best = (L, prm)
    bA = best[1]
    for qe in S61.GRID_QE:
        for pn in S61.GRID_PN:
            prm = dict(bA, q_edit=qe, p_new=pn)
            L = ev(prm)[0]
            if L < best[0]:
                best = (L, prm)
    qe, pn = best[1]["q_edit"], best[1]["p_new"]
    ip, it, ia = S61.GRID_P.index(bA["p_copy"]), S61.GRID_TAU.index(bA["tau"]), S61.GRID_A.index(bA["a"])
    for pc in S61.GRID_P[max(0, ip - 2): ip + 3]:
        for tau in S61.GRID_TAU[max(0, it - 1): it + 2]:
            for a in S61.GRID_A[max(0, ia - 1): ia + 2]:
                prm = dict(p_copy=pc, tau=tau, a=a, q_edit=qe, p_new=pn)
                L = ev(prm)[0]
                if L < best[0]:
                    best = (L, prm)
    bC = best[1]
    for pn in S61.GRID_PN:
        prm = dict(bC, p_new=pn)
        L = ev(prm)[0]
        if L < best[0]:
            best = (L, prm)
    return ev(best[1])


def _ca_force(prm):
    return dict(prm, rho=0.0) if prm["gamma"] == 0 else prm          # s67:426-427


def sched_CA(ev):
    """Rebuilds s67_constrained_assembly_loqo.py:439-465 (stage A, B, two refines; fit() ends at :469),
    use_class=True, L in place of ca_loss. ev returns (L, prm) like s67's cache entries."""
    gp, gt, gg, gr = S67.GRID_PREP, S67.GRID_TAU, S67.GRID_G, S67.GRID_RHO

    def better(best, prm):
        r = ev(prm)
        return r if best is None or r[0] < best[0] else best
    best = None
    for a in gp:
        for t in gt:
            best = better(best, dict(p_rep=a, tau=t, gamma=0.0, rho=0.0))
    bA = best
    bestB = None
    for g in gg:
        if g == 0:
            continue
        for r in gr:
            bestB = better(bestB, dict(bA[1], gamma=g, rho=r))
    best = bestB if bestB[0] < best[0] else best
    ia, it = gp.index(bA[1]["p_rep"]), gt.index(bA[1]["tau"])
    for a in gp[max(0, ia - 1): ia + 2]:
        for t in gt[max(0, it - 1): it + 2]:
            best = better(best, dict(best[1], p_rep=a, tau=t))
    ig, ir = gg.index(bestB[1]["gamma"]), gr.index(bestB[1]["rho"])
    for g in gg[max(0, ig - 1): ig + 2]:
        for r in gr[max(0, ir - 1): ir + 2]:
            best = better(best, dict(best[1], gamma=g, rho=r))
    return best


def sched_CA0(ev):
    """CA0 = CA stage A only (s67:439-443; s67:518 "CA0": F["p0"]): GRID_PREP x GRID_TAU, gamma = rho = 0."""
    best = None
    for a in S67.GRID_PREP:
        for t in S67.GRID_TAU:
            r = ev(dict(p_rep=a, tau=t, gamma=0.0, rho=0.0))
            if best is None or r[0] < best[0]:
                best = r
    return best


def sched_s81_fit(ev):
    """Rebuilds s81_sticky_table_loqo.py:288-300 (fit_p ends at :300): 1-D search over GRID_P; ties -> lower p
    (min over (loss, p), s81:298)."""
    rows = [(ev(dict(p=p))[0], p) for p in S81.GRID_P]
    best = min(rows, key=lambda r: (r[0], r[1]))
    return ev(dict(p=best[1]))


def sched_s81_75(ev):
    """line_sticky75: p fixed at 0.75, nothing to fit (plan section 4). L is still computed once (hardness, D-10)."""
    return ev(dict(p=0.75))


def sched_LP91(ev):
    """Rebuilds s91_line_pool_producer_loqo.py:399-433 (fit_lp ends at :433): coordinate descent over SWEEP from each of
    STARTS, MAX_SWEEPS, improvement > 1e-12, lower final loss kept (ties -> first start). ONE copy per candidate as
    plan section 4 says, not the FIT_SEEDS average of s91:408 (D-12)."""
    runs = []
    for st in S91.STARTS:
        best = ev(dict(st))
        for _ in range(S91.MAX_SWEEPS):
            improved = False
            for k in S91.SWEEP:
                for v in S91.GRID[k]:
                    r = ev(dict(best[1], **{k: v}))
                    if r[0] < best[0] - 1e-12:
                        best = r
                        improved = True
            if not improved:
                break
        runs.append(best)
    return min(runs, key=lambda x: x[0])


def sched_r13A(ev):
    """Rebuilds r13.py:180-186 (fit_params, ends at :193): QGRID x EGRID, strict <, first wins."""
    best = None
    for q in R13.QGRID:
        for e in R13.EGRID:
            r = ev(dict(q=q, e=e))
            if best is None or r[0] < best[0]:
                best = r
    return best


def sched_r13B(ev):
    """Rebuilds r13.py:187-192: RGRID, strict <, first wins. Each evaluation draws its own table (gen_B, table=None)."""
    best = None
    for R in R13.RGRID:
        r = ev(dict(R=R))
        if best is None or r[0] < best[0]:
            best = r
    return best


def sched_WTG(ev):
    """WTG: no free parameter (WTG_PARAMS fixed, s71:105-116). 'Refit' = rebuild WTGProducer on the training pages
    (s71:420-425; plan section 4, IV v1 ruling 4). L is computed once, for the hardness check."""
    return ev(dict())


SCHED = dict(s57=(sched_s57, ("p_copy", "tau", "a", "q_pre", "q_suf", "q_core"), None),
             s58=(sched_s58, ("p_copy", "tau", "a", "q_core"), None),
             s61=(sched_s61, tuple(S61.KEYS), None),
             CA=(sched_CA, tuple(S67.KEYS), _ca_force),
             CA0=(sched_CA0, tuple(S67.KEYS), _ca_force),
             s81_fit=(sched_s81_fit, ("p",), None), s81_75=(sched_s81_75, ("p",), None),
             LP91=(sched_LP91, tuple(S91.KEYS), None),
             r13A=(sched_r13A, ("q", "e"), None), r13B=(sched_r13B, ("R",), None),
             WTG_global=(sched_WTG, (), None), WTG_scribe=(sched_WTG, (), None))

# MEI grids and key order (plan section 5 table). Grid constants imported by name.
TENTHS = [i / 10 for i in range(11)]
MEI_GRID = {
    "s57": [("p_copy", S57.GRID_P), ("tau", S57.GRID_TAU), ("a", S57.GRID_A), ("q_pre", TENTHS), ("q_suf", TENTHS),
            ("q_core", TENTHS)],
    "s58": [("p_copy", S58.GRID_P), ("tau", S58.GRID_TAU), ("a", S58.GRID_A), ("q_core", S58.GRID_QC)],
    "s61": [("p_copy", S61.GRID_P), ("tau", S61.GRID_TAU), ("a", S61.GRID_A), ("q_edit", S61.GRID_QE),
            ("p_new", S61.GRID_PN)],
    "CA": [("p_rep", S67.GRID_PREP), ("tau", S67.GRID_TAU), ("gamma", S67.GRID_G), ("rho", S67.GRID_RHO)],
    "CA0": [("p_rep", S67.GRID_PREP), ("tau", S67.GRID_TAU)],
    "LP91": [(k, S91.GRID[k]) for k in S91.KEYS],
    "s81_fit": [("p", S81.GRID_P)],
    "r13A": [("q", None), ("e", None)],     # QGRID, EGRID: filled after R13 is loaded
    "r13B": [("R", None)],                  # RGRID
}


# ---------------------------------------------------------------- planting (plan section 5 "Planting rule")
PARAMS = {}        # theta_plant[P][T]
PLANT_OBJ = {}


def plant_train(P, T):
    """Producer trained on the real quires != 'A' of T (s101:683, 713, 734). WTG uses the meta pages (s101:713)."""
    if P.startswith("WTG"):
        return [(pid, str(m.get("quire", "?")), m["lines"]) for pid, m in META[T].items() if str(m.get("quire")) != "A"]
    return [(pid, q, ls) for pid, q, ls in REAL[T] if q != "A"]


def plant_obj(P, T):
    if (P, T) not in PLANT_OBJ:
        PLANT_OBJ[(P, T)] = build(P, T, plant_train(P, T))
    return PLANT_OBJ[(P, T)]


def _r13_lines(pages):
    return [(q, pid, ws) for pid, q, ls in pages for ws in ls]


def r13b_table(fit, R, rng):
    """Table and grille offsets drawn as r13.py:297 does: make_table, then two offsets in 1..R-1, same rng."""
    table = R13.make_table(fit, R, rng)
    return table, (int(rng.integers(1, R)), int(rng.integers(1, R)))


def plant(P, T, prm, master, control, fold="book", table_control=None):
    """One planted book of P on T's full layout. Seed = derive_seed(master, T, P, control, fold) (plan 3a rule; D-03).
    r13B: without a table in prm, table and offsets come from the book's own rng first (r13.py:297-298); with
    table_control (MEI books, plan section 5 r13 B row) they come from rng derive_seed(master, T, 'r13B', table_control,
    'book'). Returns (pages, seed, prm_used)."""
    seed = C.derive_seed(master, T, P, control, fold)
    obj = plant_obj(P, T)
    lay = full_layout(T, P)
    prm = dict(prm)
    if P == "r13B" and "table" not in prm:
        R = int(prm["R"])
        if table_control is None:
            rng = np.random.default_rng(seed)
            prm["table"], prm["offs"] = r13b_table(obj["fit"], R, rng)
            out = R13.gen_B(obj["fit"], [(q, pid, n) for pid, q, lens in lay for n in lens], rng, R, prm["table"], prm["offs"])
            return _regroup(lay, out), seed, prm
        trng = np.random.default_rng(C.derive_seed(master, T, "r13B", table_control, "book"))
        prm["table"], prm["offs"] = r13b_table(obj["fit"], R, trng)
    return gen(P, T, obj, prm, lay, seed), seed, prm


def book_stats(pages, seed):
    return text_quire_stats(pages, "vx01_bf|%d" % seed)


# ---------------------------------------------------------------- loss, refit, band, match (plan sections 2 and 4)
def loss_targets(Xstats, qtr):
    """s_k(X) and d_k over the defined quires of Qtr, k = 1..5; undefined if defined on < 10 of the 14 (plan section 4).
    SD = numpy std, ddof 0 (D-05)."""
    s, d = {}, {}
    for k in range(1, 6):
        v = [Xstats[x][k] for x in qtr if Xstats[x][k] is not None]
        if len(v) < 10:
            s[k], d[k] = None, None
        else:
            s[k] = float(np.mean(v))
            d[k] = max(float(np.std(v)), 1e-9)
    return s, d


def make_band(copy_vals):
    """Per statistic: undefined if > 10% of the copies are undefined; else np.percentile(defined, [0.5, 99.5])."""
    out = {}
    n = len(copy_vals)
    for k in range(1, 7):
        d = [c[k] for c in copy_vals if c[k] is not None]
        if n == 0 or (n - len(d)) > UNDEF_COPY_FRAC * n or not d:
            out[k] = None
        else:
            lo, hi = np.percentile(d, list(ENV_Q))
            out[k] = dict(lo=float(lo), hi=float(hi), sd=float(np.std(d)), n_def=len(d))
    return out


def match(vals, band, shift=None):
    """A fold MATCHES iff >= 5 statistics are both defined AND inside the band (inclusive edges, D-14). Fewer than 5
    defined = NON-MATCH reported as UNDEFINED (plan section 2)."""
    inside = defined = 0
    det = {}
    for k in range(1, 7):
        v = vals.get(k)
        if shift is not None:
            v = None if (v is None or shift.get(k) is None) else v + shift[k]
        b = band.get(k)
        if v is None or b is None:
            det[k] = "undef"
            continue
        defined += 1
        ok = b["lo"] <= v <= b["hi"]
        inside += ok
        det[k] = "in" if ok else "out"
    status = "MATCH" if inside >= 5 else ("UNDEFINED" if defined < 5 else "NON-MATCH")
    return dict(match=inside >= 5, status=status, defined=defined, inside=inside, detail=det)


def refit(P, T, master, X, Xstats, q, ctl, with_band=True):
    """Fit P on the training pages of the text under test X (quire != q) with L, then (optionally) the 200-copy band on
    the layout of quire q of X. Seeds: control '<ctl>|fit|<q>|<eval>' and '<ctl>|copy|<r>', fold q (D-03, D-04)."""
    train = [pg for pg in X if pg[1] != q]
    obj = build(P, T, train)
    qtr = [x for x in FOLDS if x != q]
    s, d = loss_targets(Xstats, qtr)
    tlay = layout_of(train)

    def Lfun(prm, e):
        sd = C.derive_seed(master, T, P, "%s|fit|%s|%d" % (ctl, q, e), q)
        cs = text_quire_stats(gen(P, T, obj, prm, tlay, sd), "vx01_bf|%d" % sd, qtr, ks=(1, 2, 3, 4, 5))
        tot = 0.0
        for k in range(1, 6):
            v = [cs[x][k] for x in qtr if cs[x][k] is not None]
            g = float(np.mean(v)) if len(v) >= 10 else None
            tot += 25.0 if (g is None or s[k] is None) else ((g - s[k]) / d[k]) ** 2
        return tot
    sched, keys, force = SCHED[P]
    ev = Evaluator(keys, Lfun, force)
    L, prm = sched(ev)
    res = dict(prm=public(prm), L=L, n_evals=len(ev.cache))
    if not with_band:
        return res, None
    qlay = layout_of([pg for pg in X if pg[1] == q])
    cw_train = [(pid, ls) for pid, _, ls in train]
    vals = []
    for r in range(N_COPY):
        sd = C.derive_seed(master, T, P, "%s|copy|%d" % (ctl, r), q)
        cp = gen(P, T, obj, prm, qlay, sd)
        vals.append(quire_stats([(pid, ls) for pid, _, ls in cp], q, "vx01_bf|%d" % sd, cw_train))
    return res, make_band(vals)


def oracle_band(P, T, master, book, q, prm_true):
    """Oracle band: copies by the SAME planting object at the TRUE theta_plant (r13B: the book's own table and offsets),
    no refit, no rebuild; only the seed differs: control 'oracle-power|copy|<r>' (plan section 7)."""
    obj = plant_obj(P, T)
    qlay = layout_of([pg for pg in book if pg[1] == q])
    cw_train = [(pid, ls) for pid, qq, ls in book if qq != q]
    vals = []
    for r in range(N_COPY):
        sd = C.derive_seed(master, T, P, "oracle-power|copy|%d" % r, q)
        cp = gen(P, T, obj, prm_true, qlay, sd)
        vals.append(quire_stats([(pid, ls) for pid, _, ls in cp], q, "vx01_bf|%d" % sd, cw_train))
    return make_band(vals)


def nuisance_shift(master, T, P, q, rk):
    """sigma = +1 if the first byte of SHA256('master|T|P|sign|k|q') is even, else -1; shift = sigma * r_k,q.
    r_k,q undefined -> that statistic is undefined for the fold (D-15)."""
    out = {}
    for k in range(1, 7):
        b = hashlib.sha256(("%s|%s|%s|sign|%d|%s" % (master, T, P, k, q)).encode("utf-8")).digest()[0]
        r = rk[q][str(k)]
        out[k] = None if r is None else (1.0 if b % 2 == 0 else -1.0) * float(r)
    return out


# ---------------------------------------------------------------- MEI candidates (plan section 5)
def mei_candidates(P, theta):
    out = []
    for ki, (key, grid) in enumerate(MEI_GRID[P]):
        S = sorted(set(list(grid) + [theta[key]]))
        i0 = S.index(theta[key])
        for v in grid:
            if abs(float(v) - float(theta[key])) <= 1e-12:
                continue            # the theta_plant value itself is not a candidate
            cand = dict(theta, **{key: v})
            if P == "s57" and cand["q_pre"] + cand["q_suf"] + cand["q_core"] > 1 + 1e-9:
                continue            # s57 row: a move that makes q_pre + q_suf + q_core > 1 is not a candidate
            out.append(dict(name="%s=%r" % (key, v), key=key, value=v, key_index=ki, step=abs(S.index(v) - i0),
                            prm=cand))
    return out


def mei_theta(P, T, pair_index):
    """theta_MEI(P, T, pair i) from the frozen map, or None (pair not reached)."""
    e = MEI_MAP.get(P, {}).get(T)
    if not e:
        return None
    c = e["pairs"][pair_index]["choice"]
    return None if c is None else dict(PARAMS[P][T], **{c["key"]: c["value"]})


def mei_built(P, T):
    e = MEI_MAP.get(P, {}).get(T)
    return bool(e) and all(p["choice"] is not None for p in e["pairs"])


MEI_MAP = {}
RK = {}


# ---------------------------------------------------------------- --build-params (plan section 5 "Params file")
def _jl(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def build_params():
    src = OrderedDict()

    def note(p):
        src[p] = C.sha256_file(ROOT / p)
    s67c, s81c = _jl("runs/s67/cells.json"), _jl("runs/s81/cells.json")
    note("runs/s67/cells.json"), note("runs/s81/cells.json")
    out = OrderedDict((P, OrderedDict()) for P in PRODUCERS)
    for T in TRANSLITS:
        for P, f, sub in (("s57", "runs/s57/fit_%s.json" % T, None), ("s58", "runs/s58/fit_%s.json" % T, None),
                          ("s61", "runs/s61/fit_%s.json" % T, "JW")):                   # s101:291-293
            d = _jl(f)["params"]
            out[P][T] = dict(d[sub] if sub else d)
            note(f)
        for P, key in (("CA", "CA"), ("CA0", "CA0")):                                  # s101:295-296; plan s5 CA0
            prms = [s67c[k]["params"][key] for k in sorted(s67c) if k.startswith("%s|" % T)]
            if len(prms) != 15:
                C.refuse("runs/s67/cells.json: %d %s cells for %s, expected 15" % (len(prms), key, T))
            out[P][T] = {k: float(np.median([p[k] for p in prms])) for k in S67.KEYS}
        pv = [s81c[k]["models"]["line_sticky_fit|latin_cremma"]["p"] for k in sorted(s81c) if k.startswith("%s|" % T)]
        out["s81_fit"][T] = dict(p=float(np.median(pv)))                               # s101:298-303
        out["s81_75"][T] = dict(p=0.75)                                                # p fixed 0.75
        fl = [rel_root(x) for x in sorted((ROOT / "runs" / "s91" / "folds").glob("%s_*.json" % T))]  # s101:304-309
        if fl != ["runs/s91/folds/%s_%s.json" % (T, q) for q in FOLDS]:
            C.refuse("runs/s91/folds/%s_*.json is not exactly the 15 load-listed files: %s" % (T, fl))
        prms = [_jl(f)["fit"]["params"] for f in fl]
        for f in fl:
            note(f)
        out["LP91"][T] = {k: float(np.median([p[k] for p in prms])) for k in S91.KEYS}
        out["WTG_global"][T] = dict()                                                  # S71.WTG_PARAMS, fixed
        out["WTG_scribe"][T] = dict()
        lines_tr = _r13_lines([(pid, q, ls) for pid, q, ls in REAL[T] if q != "A"])
        fit = R13.Fit(lines_tr)                                                        # r13.py:177-193, seeds 13001/2
        out["r13A"][T] = R13.fit_params("A", fit, lines_tr)
        out["r13B"][T] = R13.fit_params("B", fit, lines_tr)
    for T, fn in TRANSLITS.items():
        note("data/translit/%s.meta.json" % fn)
    agree = OrderedDict()
    for T in TRANSLITS:
        a = [pid for pid, _, _ in REAL[T]]
        b = list(META[T].keys())
        agree[T] = dict(equal=(a == b), n_s67=len(a), n_s71=len(b), only_s67=sorted(set(a) - set(b))[:50],
                        only_s71=sorted(set(b) - set(a))[:50])
    grids = OrderedDict([
        ("S57.GRID_P", S57.GRID_P), ("S57.GRID_TAU", S57.GRID_TAU), ("S57.GRID_A", S57.GRID_A),
        ("S58.GRID_QC", S58.GRID_QC), ("S61.GRID_QE", S61.GRID_QE), ("S61.GRID_PN", S61.GRID_PN),
        ("S61.KEYS", list(S61.KEYS)), ("S67.GRID_PREP", S67.GRID_PREP), ("S67.GRID_TAU", S67.GRID_TAU),
        ("S67.GRID_G", S67.GRID_G), ("S67.GRID_RHO", S67.GRID_RHO), ("S67.KEYS", list(S67.KEYS)),
        ("S81.GRID_P", S81.GRID_P), ("S91.KEYS", list(S91.KEYS)), ("S91.GRID", dict(S91.GRID)),
        ("S91.STARTS", S91.STARTS), ("S91.SWEEP", S91.SWEEP), ("S91.MAX_SWEEPS", S91.MAX_SWEEPS),
        ("S91.STICKY_P", S91.STICKY_P), ("r13.QGRID", R13.QGRID), ("r13.EGRID", R13.EGRID), ("r13.RGRID", R13.RGRID),
        ("S71.WTG_PARAMS", dict(S71.WTG_PARAMS)),
    ])
    doc = OrderedDict(bf_plan_sha256=BF_PLAN_SHA256, note="UNVERIFIED", theta_plant=out, sources=src,
                      page_id_agreement=agree, fitter_grids=grids,
                      schedules={P: SCHED[P][0].__doc__.strip() for P in PRODUCERS})
    h = write_new(PARAMS_FILE, json.dumps(doc, indent=1) + "\n")
    if not all(v["equal"] for v in agree.values()):
        log(dict(event="PAGE-ID-DISAGREE", agree=agree, note="no freeze until IV rules (plan section 4 Page meta)"))
    return [PARAMS_FILE], dict(params_sha256=h, page_ids_agree=all(v["equal"] for v in agree.values()))


def load_params():
    d = json.loads(PARAMS_FILE.read_text(encoding="utf-8"))
    for P in PRODUCERS:
        PARAMS[P] = d["theta_plant"][P]
    return d


def load_rk():
    """r_k,q from the frozen vx01_bf_rk run. The rk stub must exist and the table hash must match the GATE-COMPLETE
    record of the rk gate log (plan section 3: measured FIRST, before any producer is planted or scored)."""
    if not (RK_STUB.exists() and RK_TABLE.exists() and RK_GATE_LOG.exists()):
        C.refuse("vx01_bf_rk is not frozen and run yet (stub, table or gate log missing)")
    h = C.sha256_file(RK_TABLE)
    ok = any(r.get("event") == "GATE-COMPLETE" and h in r.get("outputs", {}).values() for r in C.read_chain(RK_GATE_LOG))
    if not ok:
        C.refuse("vx01_bf_rk_table.json hash is not in a GATE-COMPLETE record of the rk gate log")
    RK.update(json.loads(RK_TABLE.read_text(encoding="utf-8"))["rk"])
    return h


def load_mei():
    d = json.loads(MEI_FILE.read_text(encoding="utf-8"))
    MEI_MAP.update(d["map"])
    return d


# ---------------------------------------------------------------- --calibrate-mei (plan section 5 "MEI map rule")
def calibrate_mei(cover):
    res = OrderedDict()
    for P in PRODUCERS:
        if P not in MEI_GRID:
            continue                         # WTG global/scribe, line_sticky75: no MEI control, no EXCLUDED call
        res[P] = OrderedDict()
        for T in TRANSLITS:
            t0 = time.time()
            theta = PARAMS[P][T]
            book, bseed, tp = plant(P, T, theta, MEI_BAND_MASTER, "power")
            bands = {q: oracle_band(P, T, MEI_BAND_MASTER, book, q, tp) for q in FOLDS}
            cands = mei_candidates(P, theta)
            crow = []
            for c in cands:
                bvals = []
                for r in range(N_MEI_BOOKS):
                    tc = ("meitable|%s" % c["name"]) if P == "r13B" else None
                    pg, sd, _ = plant(P, T, c["prm"], MEI_BOOK_MASTER, "meimap|%s|%d" % (c["name"], r), "book", tc)
                    bvals.append(book_stats(pg, sd))
                side = {}
                for k in range(1, 7):
                    ups, dns = [], []
                    for q in FOLDS:
                        b = bands[q][k]
                        mv = [bv[q][k] for bv in bvals if bv[q][k] is not None]
                        if b is None or not mv or not (b["sd"] > 0):
                            continue                      # D-16: quire left out of the median
                        m = float(np.mean(mv))
                        ups.append((m - b["hi"]) / b["sd"])
                        dns.append((b["lo"] - m) / b["sd"])
                    side[k] = max(float(np.median(ups)), float(np.median(dns))) if ups else None
                crow.append(dict(c, side=side, prm=public(c["prm"])))
            pairs = []
            for (i, j) in PAIRS:
                reach = [c for c in crow if c["side"][i] is not None and c["side"][j] is not None
                         and c["side"][i] >= 0.5 and c["side"][j] >= 0.5]
                # rules 1-4: closeness to 0.5, step count, key order, lower value
                reach.sort(key=lambda c: (max(abs(c["side"][i] - 0.5), abs(c["side"][j] - 0.5)), c["step"],
                                          c["key_index"], float(c["value"])))
                ch = reach[0] if reach else None
                pairs.append(dict(pair=[i, j], choice=None if ch is None else dict(name=ch["name"], key=ch["key"],
                                                                                    value=ch["value"])))
            res[P][T] = dict(book_seed=bseed, candidates=crow, pairs=pairs,
                             built=all(p["choice"] is not None for p in pairs))
            cover.append(("calibrate-mei", P, T))
            log(dict(event="DEV-TIMING", mode="--calibrate-mei", P=P, T=T, seconds=round(time.time() - t0, 3)))
    doc = OrderedDict(bf_plan_sha256=BF_PLAN_SHA256, note="UNVERIFIED", band_master=MEI_BAND_MASTER,
                      book_master=MEI_BOOK_MASTER, params_sha256=C.sha256_file(PARAMS_FILE), map=res)
    h = write_new(MEI_FILE, json.dumps(doc, indent=1) + "\n")
    return [MEI_FILE], dict(mei_sha256=h)


# ---------------------------------------------------------------- --oracle (plan section 7 "Oracle control")
def mei_book(P, T, master, i):
    """MEI book i: theta_MEI(P, T, pair i), control 'mei', fold = the i-th fold quire. r13B table: 'meitable|<cand>'."""
    q = FOLDS[i]
    th = mei_theta(P, T, i)
    c = MEI_MAP[P][T]["pairs"][i]["choice"]
    tc = ("meitable|%s" % c["name"]) if P == "r13B" else None
    pg, sd, _ = plant(P, T, th, master, "mei", q, tc)
    return pg, sd


def oracle_mode(cover):
    res = OrderedDict()
    for P in PRODUCERS:
        res[P] = OrderedDict()
        for T in TRANSLITS:
            for master in DEV_MASTERS:
                t0 = time.time()
                book, bseed, tp = plant(P, T, PARAMS[P][T], master, "power")
                st = book_stats(book, bseed)
                bands = {q: oracle_band(P, T, master, book, q, tp) for q in FOLDS}
                op = [match(st[q], bands[q]) for q in FOLDS]
                rec = dict(oracle_power=sum(m["match"] for m in op), power_folds=[m["status"] for m in op])
                if mei_built(P, T):
                    om = []
                    for i, q in enumerate(FOLDS):
                        pg, sd = mei_book(P, T, master, i)
                        om.append(match(book_stats(pg, sd)[q], bands[q]))
                    rec["oracle_mei"] = sum(m["match"] for m in om)
                    rec["mei_folds"] = [m["status"] for m in om]
                else:
                    rec["oracle_mei"] = None          # no MEI control: oracle-power only
                rec["cell_pass"] = rec["oracle_power"] >= POWER_MIN and (rec["oracle_mei"] is None
                                                                       or rec["oracle_mei"] <= CTRL_MAX)
                res[P]["%s|%d" % (T, master)] = rec
                cover.append(("oracle", P, T))
                log(dict(event="DEV-TIMING", mode="--oracle", P=P, T=T, master=master, seconds=round(time.time() - t0, 3)))
        res[P]["PASS"] = all(v["cell_pass"] for k, v in res[P].items() if k != "PASS")
        if not res[P]["PASS"]:
            res[P]["label"] = "UNINFORMATIVE BY FIXTURE"
    doc = OrderedDict(bf_plan_sha256=BF_PLAN_SHA256, note="UNVERIFIED", dev_masters=DEV_MASTERS,
                      params_sha256=C.sha256_file(PARAMS_FILE), mei_sha256=C.sha256_file(MEI_FILE), result=res)
    h = write_new(ORACLE_FILE, json.dumps(doc, indent=1) + "\n")
    return [ORACLE_FILE], dict(oracle_sha256=h)


def oracle_pass():
    d = json.loads(ORACLE_FILE.read_text(encoding="utf-8"))["result"]
    return {P: bool(d[P]["PASS"]) for P in d}


# ---------------------------------------------------------------- one cell (plan section 7 controls)
CONTROLS = ("power", "wrongfam", "mei", "nuisance")


def run_cell(P, T, master, controls=CONTROLS, folds=FOLDS, wlist=None, timing=None):
    """One cell = (P, T, master): Power, Wrong-family (every pairing of P, D-17), MEI, Nuisance; 15 folds each.
    Returns a dict with the per-fold match records and the counts. timing: list that gets (unit, seconds)."""
    out = OrderedDict(P=P, T=T, master=master)
    theta = PARAMS[P][T]

    def tick(unit, t0):
        if timing is not None:
            timing.append((unit, round(time.time() - t0, 3)))
    need_power_book = ("power" in controls) or ("wrongfam" in controls)
    if need_power_book:
        book, bseed, _ = plant(P, T, theta, master, "power")
        bst = book_stats(book, bseed)
    if "power" in controls:
        rows, LP = [], []
        for q in folds:
            t0 = time.time()
            res, band = refit(P, T, master, book, bst, q, "power")
            rows.append(dict(q=q, fit=res, **match(bst[q], band)))
            LP.append(res["L"])
            tick("power|%s" % q, t0)
        out["power"] = dict(book_seed=bseed, folds=rows, count=sum(r["match"] for r in rows),
                            median_L=float(np.median(LP)))
    if "nuisance" in controls:
        nb, nseed, _ = plant(P, T, theta, master, "nuisance")
        nst = book_stats(nb, nseed)
        rows = []
        for q in folds:
            t0 = time.time()
            res, band = refit(P, T, master, nb, nst, q, "nuisance")
            sh = nuisance_shift(master, T, P, q, RK)
            rows.append(dict(q=q, fit=res, shift=sh, **match(nst[q], band, sh)))
            tick("nuisance|%s" % q, t0)
        out["nuisance"] = dict(book_seed=nseed, folds=rows, count=sum(r["match"] for r in rows))
    if "mei" in controls:
        if not mei_built(P, T):
            out["mei"] = dict(built=False, note="no MEI control (v5.1:134): no EXCLUDED call")
        else:
            rows = []
            for i, q in enumerate(FOLDS):
                if q not in folds:
                    continue
                t0 = time.time()
                mb, mseed = mei_book(P, T, master, i)
                mst = book_stats(mb, mseed)     # all quires: the refit's loss targets need Qtr of this book
                res, band = refit(P, T, master, mb, mst, q, "mei")
                rows.append(dict(q=q, pair=MEI_MAP[P][T]["pairs"][i]["pair"], book_seed=mseed, fit=res,
                                 **match(mst[q], band)))
                tick("mei|%s" % q, t0)
            out["mei"] = dict(built=True, folds=rows, count=sum(r["match"] for r in rows))
    if "wrongfam" in controls:
        wf = OrderedDict()
        for W in (wlist or PAIRINGS[P]):
            wb, wseed, _ = plant(W, T, PARAMS[W][T], master, "wrongfam")
            wst = book_stats(wb, wseed)
            rows, LW = [], []
            for q in folds:
                t0 = time.time()
                res, band = refit(P, T, master, wb, wst, q, "wrongfam-%s" % W)
                hres, _ = refit(W, T, master, book, bst, q, "power", with_band=False)   # hardness: W on P's training
                rows.append(dict(q=q, fit=res, W_fit=hres, **match(wst[q], band)))
                LW.append(hres["L"])
                tick("wrongfam-%s|%s" % (W, q), t0)
            wf[W] = dict(book_seed=wseed, folds=rows, count=sum(r["match"] for r in rows),
                         median_L_W=float(np.median(LW)))
        out["wrongfam"] = wf
    return out


def calls_for(P, cells):
    """Plan section 7 + v5.1 rule 2 counts. cells: the 9 run_cell dicts of P. Returns the call record."""
    pw = all(c["power"]["count"] >= POWER_MIN for c in cells)
    nu = all(c["nuisance"]["count"] >= POWER_MIN for c in cells)
    built = all(c["mei"]["built"] for c in cells)
    me = built and all(c["mei"]["count"] <= CTRL_MAX for c in cells)
    chosen, hard = None, OrderedDict()
    for W in PAIRINGS[P]:
        hard[W] = all(c["wrongfam"][W]["median_L_W"] <= HARD_FACTOR * c["power"]["median_L"] for c in cells)
        if hard[W] and chosen is None:
            chosen = W
    wf = chosen is not None and all(c["wrongfam"][chosen]["count"] <= CTRL_MAX for c in cells)
    rec = OrderedDict(power_ok=pw, nuisance_ok=nu, mei_built=built, mei_ok=me, hardness=hard, pairing=chosen,
                      wrongfam_ok=wf)
    if chosen is None:
        rec["status"] = "UNINFORMATIVE (no hard pairing)"
    rec["B1_EXCLUDED_allowed"] = bool(pw and me and nu)          # B1 table: EXCLUDED needs Power + MEI + Nuisance
    rec["B1_NOT_EXCLUDED_allowed"] = bool(pw and wf)             # NOT EXCLUDED needs Power + Wrong-family
    rec["unit_label"] = PRODUCERS[P]["unit_label"]
    return rec


# ---------------------------------------------------------------- timing / hard cap for the dev modes (D-21)
def start_cap_timer(seconds, where):
    def fire():
        try:
            log(dict(event="CAP-STOP", mode=where, cap_seconds=seconds, t_pt=pt_now()))
        finally:
            os._exit(EXIT_CAP)
    t = threading.Timer(seconds, fire)
    t.daemon = True
    t.start()
    return t


def dev_mode(cover):
    """Timing run of plan section 9 (default: master 20261103, ZL3b, every producer that passed the oracle fixture,
    all 4 controls, 15 folds). --producer/--control/--fold/--W narrow it to one unit (the Eve probe)."""
    master = int(arg("--master", TIMING_MASTER))
    T = arg("--T", "ZL3b")
    if T not in TRANSLITS:
        C.refuse("--T %s unknown" % T)
    ok = oracle_pass()
    prods = [arg("--producer")] if arg("--producer") else [P for P in PRODUCERS if ok.get(P)]
    ctl = (arg("--control"),) if arg("--control") else CONTROLS
    folds = [arg("--fold")] if arg("--fold") else FOLDS
    wl = [arg("--W")] if arg("--W") else None
    for P in prods:
        if P not in PRODUCERS or not ok.get(P):
            C.refuse("producer %s unknown or failed its oracle fixture" % P)
    for c in ctl:
        if c not in CONTROLS:
            C.refuse("--control %s unknown" % c)
    for q in folds:
        if q not in FOLDS:
            C.refuse("--fold %s unknown" % q)
    full = (len(ctl) == 4 and len(folds) == 15 and wl is None)
    res = OrderedDict()
    for P in prods:
        t0 = time.time()
        tm = []
        res[P] = run_cell(P, T, master, ctl, folds, wl, tm)
        sec = round(time.time() - t0, 3)
        res[P]["timing"] = tm
        log(dict(event="DEV-TIMING", mode="--dev", P=P, T=T, master=master, controls=list(ctl), folds=folds,
                 W=wl, seconds=sec, full_cell=full, t_pt=pt_now()))
        for c in ctl:
            cover.append(("dev", P, T, c))
    return res


def estimate_from_log():
    """E = sum over producers that passed the oracle fixture of (seconds of their latest FULL ZL3b dev cell on
    master 20261103 x 9); cap = 2 x E (plan section 9). Returns (E, cap, rows) or refuses if a producer has no
    full-cell timing. A probe (one unit) is never used here; the probe extrapolation is a separate, reported step
    (Eve ruling (c), D-22)."""
    ok = oracle_pass()
    me = C.sha256_file(SELF)
    last = {}
    for r in C.read_chain(DEV_LOG):
        if (r.get("event") == "DEV-TIMING" and r.get("mode") == "--dev" and r.get("full_cell") and r.get("T") == "ZL3b"
                and r.get("master") == TIMING_MASTER and r.get("script_sha256", me) == me):
            last[r["P"]] = float(r["seconds"])
    rows = OrderedDict()
    for P in PRODUCERS:
        if ok.get(P):
            if P not in last:
                C.refuse("no full-cell dev timing for %s" % P)
            rows[P] = last[P]
    E = sum(v * 9 for v in rows.values())
    return E, 2 * E, rows


# ---------------------------------------------------------------- the gate (plan sections 7 and 9)
def gate_mode(ctx, kv):
    cap = float(kv["cap_seconds"])
    t_start = time.time()
    ok = oracle_pass()
    gdir = RUN_DIR / "gate"
    seeds = C.gate_seed_list("B0")
    results, calls, order_done = OrderedDict(), OrderedDict(), []
    stopped = None
    for P in PRODUCERS:                          # fixed order F-34 C1, F-41 C2, F-23, F-30 (condition ii)
        if stopped is None and time.time() - t_start > cap:
            stopped = P
        if stopped is not None:
            calls[P] = dict(status="not run, no call (cap stop)")
            continue
        if not ok.get(P):
            calls[P] = dict(status="UNINFORMATIVE BY FIXTURE")
            continue
        cells = []
        for T in TRANSLITS:
            for m in seeds:
                cells.append(run_cell(P, T, m))
        results[P] = cells
        calls[P] = calls_for(P, cells)
        write_new(gdir / ("cells_%s.json" % P), json.dumps(cells, indent=1) + "\n")
        log(dict(event="GATE-PRODUCER-DONE", P=P, elapsed=round(time.time() - t_start, 3), t_pt=pt_now()))
        order_done.append(P)
    lines = ["# vx01_b0_fitter_recovery GATE result. UNVERIFIED.", "bf_plan_sha256=%s" % BF_PLAN_SHA256]
    lines += ctx.header()
    lines.append("cap_seconds=%s elapsed_seconds=%.1f cap_stop_before=%s" % (cap, time.time() - t_start, stopped))
    for P, c in calls.items():
        lines.append("%s\t%s\t%s" % (P, PRODUCERS[P]["finding"], json.dumps(c, separators=(",", ":"))))
        if P in results:
            for cell in results[P]:
                lines.append("  %s|%s power=%s nuisance=%s mei=%s wrongfam=%s" % (
                    cell["T"], cell["master"], cell["power"]["count"], cell["nuisance"]["count"],
                    cell["mei"].get("count"), {W: v["count"] for W, v in cell["wrongfam"].items()}))
    write_new(RESULTS_GATE, "\n".join(lines) + "\n")
    outs = [RESULTS_GATE] + [gdir / ("cells_%s.json" % P) for P in order_done]
    return outs, ("CAP-STOP before %s" % stopped) if stopped else "complete"


# ---------------------------------------------------------------- trace, freeze check, stub (plan section 8)
def trace_record(mode, cover):
    dists, unmapped = run_path_distributions()
    mods = sorted(set(r for r in (rel_root(getattr(m, "__file__", "") or "") for m in list(sys.modules.values())
                                  if getattr(m, "__file__", None) and os.path.isabs(m.__file__)) if r))
    snap = HOOK.snapshot()
    return dict(script=NAME, script_sha256=C.sha256_file(SELF), mode=mode, t=C.utc_now(), t_pt=pt_now(),
                argv=ARGS, reads_root=snap["reads_root"], modules_root=mods, writes=snap["writes"],
                proc_events=snap["proc_events"], dists=dists, unmapped_modules=unmapped, cover=cover)


def own_outputs():
    return [PARAMS_FILE, MEI_FILE, ORACLE_FILE, DEV_LOG, GATE_LOG, PIN_LOG, STUB, RESULTS_GATE]


def freeze_check():
    """Union of all trace_*.json of THIS script hash under runs/vx01_b0/ (D-19). Rules (a), (b), (d) + coverage."""
    me = C.sha256_file(SELF)
    trs = []
    for t in sorted(RUN_DIR.glob("*_*/trace_*.json")):
        d = json.loads(t.read_text(encoding="utf-8"))
        if d["script_sha256"] == me:
            trs.append((t, d))
    problems = []
    if not trs:
        problems.append("no trace for this script hash")
    reads = set()
    mods, procs, dists, unm, writes, cover = set(), [], set(), set(), set(), set()
    for _, d in trs:
        reads |= set(d["reads_root"])
        mods |= set(d["modules_root"])
        procs += d["proc_events"]
        dists |= set(d["dists"])
        unm |= set(d["unmapped_modules"])
        writes |= set(d["writes"])
        cover |= set(tuple(c) for c in d["cover"])
    own = {norm_load_key(rel_root(p)) for p in own_outputs() + [SELF]}
    own |= {norm_load_key(rel_root(p)) for p in (RK_SCRIPT, RK_STUB, RK_GATE_LOG, RK_TABLE)}
    own |= {norm_load_key(rel_root(C.GATE_SEEDS_FILE)), norm_load_key(rel_root(Path(C.__file__)))}
    ll = {norm_load_key(p): (p, h) for p, h in LOAD_LIST.items()}
    rows = OrderedDict()
    for r in sorted(reads | mods):
        k = norm_load_key(r)
        if k in own or r.startswith("runs/vx01_b0/"):
            continue
        if k not in ll:
            problems.append("unlisted file %s" % r)
            continue
        p, h = ll[k]
        if not (ROOT / p).exists() or C.sha256_file(ROOT / p) != h:
            problems.append("hash differs %s" % p)
        rows[p] = h
    if procs:
        problems.append("%d process events" % len(procs))
    for d in dists:
        if d not in PIN_DISTS:
            problems.append("unlisted distribution %s" % d)
    for m in unm:
        problems.append("module %s maps to no distribution" % m)
    okw = {os.path.normcase(os.path.abspath(p)) for p in own_outputs()}
    rd = os.path.normcase(os.path.abspath(RUN_DIR))
    foreign = [w for w in writes if not (w.startswith(rd + os.sep) or w in okw)]
    if foreign:
        problems.append("writes outside declared outputs: %s" % sorted(foreign)[:5])
    need = {("build-params",)}
    need |= {("calibrate-mei", P, T) for P in MEI_GRID for T in TRANSLITS}
    need |= {("oracle", P, T) for P in PRODUCERS for T in TRANSLITS}
    okp = oracle_pass() if ORACLE_FILE.exists() else {}
    need |= {("dev", P, T, c) for P in PRODUCERS if okp.get(P) for T in TRANSLITS for c in CONTROLS}  # D-20
    missing = sorted(need - cover)
    if missing:
        problems.append("coverage missing %d units, e.g. %s" % (len(missing), missing[:5]))
    env = env_measure()
    bad = env_mismatch(env)
    C.append_chained(PIN_LOG, env_log_record(env, "--freeze-check", bad))
    if bad:
        problems.append("environment pin mismatch: %s" % bad)
    rep = OrderedDict(script_sha256=me, t=C.utc_now(), t_pt=pt_now(), traces=[(rel_root(t), C.sha256_file(t))
                                                                              for t, _ in trs],
                      problems=problems, freeze_ok=not problems, files=list(rows.items()), dists=sorted(dists),
                      env=env)
    path = RUN_DIR / ("freeze_check_%s.json" % C.utc_now().replace(":", ""))
    write_new(path, json.dumps(rep, indent=1) + "\n")
    print("freeze check:", "OK" if not problems else "NO FREEZE", path)
    for p in problems:
        print("  ", p)
    return 0 if not problems else 3


def plan_sections(plan, starts):
    lines = plan.read_text(encoding="utf-8").splitlines()
    out, on = [], False
    for l in lines:
        if l.startswith("## "):
            on = any(l.startswith(s) for s in starts)
        if on:
            out.append(l)
    return out


def write_stub():
    if STUB.exists():
        C.refuse("stub exists")
    plan = Path(arg("--plan", "")) if arg("--plan") else None
    if plan is None or C.sha256_file(plan) != BF_PLAN_SHA256:
        C.refuse("--plan PATH with sha256 %s required" % BF_PLAN_SHA256)
    rp = Path(arg("--freeze-report", "")) if arg("--freeze-report") else None
    if rp is None or not rp.exists():
        C.refuse("--freeze-report PATH required")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    me = C.sha256_file(SELF)
    if not rep.get("freeze_ok") or rep.get("script_sha256") != me:
        C.refuse("freeze report is not OK for this script hash")
    for p, h in rep["files"]:
        if C.sha256_file(ROOT / p) != h:
            C.refuse("file changed since the freeze check: %s" % p)
    for f in (RK_STUB, RK_TABLE, RK_GATE_LOG, PARAMS_FILE, MEI_FILE, ORACLE_FILE):
        if not f.exists():
            C.refuse("missing %s" % f.name)
    load_rk()
    E, cap, rows = estimate_from_log()
    env = env_measure()
    bad = env_mismatch(env)
    C.append_chained(PIN_LOG, env_log_record(env, "freeze (--write-stub)", bad))
    if bad:
        C.refuse("NO freeze: environment pin mismatch: %s" % ", ".join(bad))
    out = ["# vx01_b0_fitter_recovery.prereg.sha256 (B0-F) -- UNVERIFIED until the Independent Verifier signs",
           "# plan PLAN-X01-B-FALLBACK cited by sha256 only (title reads v4): bf_plan_sha256 below",
           "plan_sha256=%s" % V51_PLAN_SHA256, "bf_plan_sha256=%s" % BF_PLAN_SHA256,
           "script_sha256=%s" % me, "common_sha256=%s" % C.sha256_file(C.__file__),
           "gate_seeds_sha256=%s" % C.sha256_file(C.GATE_SEEDS_FILE),
           "dev_log_sha256=%s" % C.sha256_file_or_empty(DEV_LOG),
           "dev_log_head=%s" % C.sha256_bytes(C._last_line(DEV_LOG) or b""),
           "rk_stub_sha256=%s" % C.sha256_file(RK_STUB), "rk_table_sha256=%s" % C.sha256_file(RK_TABLE),
           "params_sha256=%s" % C.sha256_file(PARAMS_FILE), "mei_map_sha256=%s" % C.sha256_file(MEI_FILE),
           "oracle_sha256=%s" % C.sha256_file(ORACLE_FILE),
           "freeze_report=%s freeze_report_sha256=%s" % (rel_root(rp) or str(rp), C.sha256_file(rp)),
           "estimate_seconds=%.3f" % E, "cap_seconds=%.3f" % cap,
           "estimate_formula=E = sum over producers that passed the oracle fixture of (full ZL3b dev cell seconds on "
           "master 20261103 x 9); cap = 2 x E",
           "estimate_rows=%s" % json.dumps(rows, separators=(",", ":"))]
    for k in ENV_KEYS:
        out.append("env_%s=%s" % (k, env[k]))
    out.append("env_exe=%s" % env["exe"])
    out.append("env_sys_version=%s" % env["sys_version"])
    out.append("env_dists=%s" % json.dumps(env["dists"], separators=(",", ":")))
    out.append("# fit schedules (rebuilt; source file:line per producer):")
    out += ["#   %s: %s" % (P, " ".join(SCHED[P][0].__doc__.split())) for P in PRODUCERS]
    out.append("# decision rules copied from the plan (sections 2, 4, 5, 7, 8):")
    out += ["# " + l for l in plan_sections(plan, ("## 2.", "## 4.", "## 5.", "## 7.", "## 8."))]
    out.append("# files loaded at run time (trace) and run inputs, each against disk:")
    hl = OrderedDict(rep["files"])
    for f in (RK_SCRIPT, RK_STUB, RK_TABLE, RK_GATE_LOG, PARAMS_FILE, MEI_FILE, ORACLE_FILE):
        hl[rel_root(f)] = C.sha256_file(f)
    out += ["%s  %s" % (h, p) for p, h in hl.items()]
    write_new(STUB, "\n".join(out) + "\n")
    print("stub written", STUB, C.sha256_file(STUB))
    return 0


# ---------------------------------------------------------------- main
def _load_r13():
    global R13
    exp = {p: h for p, h in LOAD_LIST.items() if p.startswith("runs/roach-r10/") or p.startswith("runs/roach-r7/")}
    R13 = PM.load_r13(log, expected=exp)
    MEI_GRID["r13A"] = [("q", R13.QGRID), ("e", R13.EGRID)]
    MEI_GRID["r13B"] = [("R", R13.RGRID)]


def main():
    global LOG_PATH
    C.set_below_normal()
    if MODE == "--pin-check":
        env = env_measure()
        bad = env_mismatch(env)
        h = C.append_chained(PIN_LOG, env_log_record(env, "manual --pin-check", bad))
        print(json.dumps(env, indent=1))
        print("pin match:", not bad, bad, "log line", h)
        return 0 if not bad else 3
    if MODE == "--freeze-check":
        return freeze_check()
    if MODE == "--write-stub":
        load_params()
        return write_stub()
    fg = free_gb()
    if not (fg >= MIN_FREE_GB):
        C.refuse("free RAM %.2f GB < %.1f GB" % (fg, MIN_FREE_GB))
    gate = MODE == "--gate"
    env = env_measure()
    bad = env_mismatch(env, _stub_kv if gate else None)
    if gate:
        seeds = C.gate_seed_list("B0")
    elif MODE == "--build-params":
        seeds = []
    elif MODE == "--calibrate-mei":
        seeds = [MEI_BAND_MASTER, MEI_BOOK_MASTER]
    elif MODE == "--oracle":
        seeds = DEV_MASTERS
    else:
        seeds = [int(arg("--master", TIMING_MASTER))]
    ctx = C.RunContext(SELF, ARGS, seeds, gate)
    if gate and bad:
        C.append_chained(GATE_LOG, env_log_record(env, "gate start (refused)", bad))
        C.refuse("environment pin mismatch: %s" % ", ".join(bad))
    if not gate and bad:
        C.refuse("environment pin mismatch (dev runs use the pinned 3.11.9 only): %s" % ", ".join(bad))
    if MODE != "--build-params":
        for f in (RK_STUB, RK_TABLE):
            if not f.exists():
                C.refuse("vx01_bf_rk not frozen and run (missing %s)" % f.name)
    if MODE == "--dev" and not ORACLE_FILE.exists():
        C.refuse("--dev needs the oracle result file (oracle fixture first, plan section 9)")
    if MODE in ("--calibrate-mei", "--oracle", "--dev"):
        cs = arg("--cap-seconds")
        if cs is None:
            C.refuse("--cap-seconds S required for %s" % MODE)
    ctx.start()
    LOG_PATH = GATE_LOG if gate else DEV_LOG
    log(env_log_record(env, MODE + " start", bad))
    if MODE in ("--calibrate-mei", "--oracle", "--dev"):
        start_cap_timer(float(arg("--cap-seconds")), MODE)
    load_data()
    _load_r13()
    cover = []
    if MODE == "--build-params":
        outs, info = build_params()
        cover.append(("build-params",))
    else:
        load_params()
        load_rk()
        if MODE != "--calibrate-mei":
            load_mei()
        if MODE == "--calibrate-mei":
            outs, info = calibrate_mei(cover)
        elif MODE == "--oracle":
            outs, info = oracle_mode(cover)
        elif MODE == "--dev":
            res = dev_mode(cover)
            d = RUN_DIR / ("dev_" + C.utc_now().replace(":", ""))
            outs = [d / "dev_cells.json"]
            write_new(outs[0], json.dumps(res, indent=1) + "\n")
            info = {}
        else:
            outs, note = gate_mode(ctx, _stub_kv)
            info = dict(note=note)
    if not gate:
        d = RUN_DIR / ("%s_%s" % (MODE.strip("-"), C.utc_now().replace(":", "")))
        tp = d / ("trace_%s.json" % MODE.strip("-"))
        write_new(tp, json.dumps(trace_record(MODE, cover), indent=1) + "\n")
        outs = list(outs) + [tp]
    env2 = env_measure()
    bad2 = env_mismatch(env2, _stub_kv if gate else None)
    log(env_log_record(env2, MODE + " end", bad2))
    head = ctx.finish(outs, note="env_end_match=%s %s" % (not bad2, json.dumps(info, separators=(",", ":"))))
    print("done; outputs:", [str(o) for o in outs], "log head", head)
    return 0


if __name__ == "__main__":
    sys.exit(main())
