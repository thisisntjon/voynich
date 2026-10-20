"""vx01_bf_rk.py -- nuisance spread r_k,q on the REAL whole-word text (script 6b). UNVERIFIED.

Plan: PLAN-X01-B-FALLBACK, cited only by sha256 4ed0314a7c8aef4d925dee4fbab3ef8eca3a005352062563e3708a0273e63f3e
(section 3; statistics section 2; load list section 8). Base plan PLAN-X01-v5.1 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393.
WRITTEN FOR IV CODE REVIEW. NOT RUN. NOT FROZEN. Open code decisions: vx01_bf_CODE_DECISIONS_1.md.

What it computes (plan section 3): for each fold quire q (the 15 of S67.folds_of on ZL3b) and statistic k (section 2),
r_k,q = max - min over ZL3b / RF1b / IT2a of statistic k on real quire q, tag "vx01_bf|real|<T>", CHARWIN train =
the other real quires of the same transliteration. 15 x 6 numbers, plus (reported, not used) the median over q.
No model, no hypothesis, no random seed except the fixed F.seed tags.

Modes
  --dev        pre-freeze run (also the freeze trace for this script): writes runs/vx01_bf_rk/dev_<utc>/ only.
  --gate       the ONE frozen run (needs the stub): writes vx01_bf_rk_table.json and results_vx01_bf_rk.txt.
  --pin-check  environment pin check only; one line to vx01_bf_rk_pin_checks.log (not in the stub).
  --write-stub builds vx01_bf_rk.prereg.sha256 from the dev trace (refuses if it exists). Needs --plan PATH.
Single process. BelowNormal. Audit hook on open + process-creation events in every mode (rules (a), (c), (d)).
"""
import sys
sys.dont_write_bytecode = True   # no .pyc writes: a write under ROOT would void a gate run (rule (c))
import ctypes  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import platform  # noqa: E402
from collections import OrderedDict  # noqa: E402
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
NAME = C.script_name(SELF)
STUB = C.stub_path(SELF)
DEV_LOG = C.dev_log_path(SELF)
GATE_LOG = C.gate_log_path(SELF)
PIN_LOG = ROOT / (NAME + "_pin_checks.log")
OUT_TABLE = ROOT / "vx01_bf_rk_table.json"
OUT_TXT = ROOT / "results_vx01_bf_rk.txt"
RUN_DIR = ROOT / "runs" / "vx01_bf_rk"
ARGS = sys.argv[1:]
MODE = next((a for a in ARGS if a in ("--dev", "--gate", "--pin-check", "--write-stub")), None)
if MODE is None:
    print(__doc__)
    sys.exit(2)

# ---------------------------------------------------------------- early hook (before the heavy imports)
_stub_kv, _stub_hl = ({}, [])
if MODE == "--gate":
    if not STUB.exists():
        C.refuse("no stub %s" % STUB.name)
    _stub_kv, _stub_hl = C.parse_stub(STUB)
    if _stub_kv.get("bf_plan_sha256", "").lower() != BF_PLAN_SHA256:
        C.refuse("stub bf_plan_sha256 is not %s" % BF_PLAN_SHA256)
    for _r in C.read_chain(GATE_LOG) if GATE_LOG.exists() else []:
        if _r.get("event") == "GATE-VOID" and _r.get("script_sha256") == C.sha256_file(SELF):
            C.refuse("an earlier gate run of this script was VOID; it counts as the one run")


def _gate_void(line, info):
    C.append_chained(GATE_LOG, dict(t=C.utc_now(), t_pt=pt_now(), event="GATE-VOID", line=line, info=info,
                                    script_sha256=C.sha256_file(SELF)))


if MODE == "--gate":
    _allowed = [p for _, p in _stub_hl] + [rel_root(x) for x in (SELF, STUB, DEV_LOG, GATE_LOG, C.GATE_SEEDS_FILE,
                                                              Path(C.__file__), OUT_TABLE, OUT_TXT)]
    HOOK = install_hook(AuditHook(True, _gate_void, _allowed, [GATE_LOG, OUT_TABLE, OUT_TXT], []))
elif MODE == "--dev":
    HOOK = install_hook(AuditHook(False))
else:
    HOOK = None

import numpy as np  # noqa: E402
import corpora  # noqa: E402
import m3_bakeoff_reconcile as M3  # noqa: E402
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("vkb_features", str(ROOT / "tools" / "vkb" / "features.py"))
F = _iu.module_from_spec(_spec)
_spec.loader.exec_module(F)
import s67_constrained_assembly_loqo as S67  # noqa: E402  (text loader S67.load_pages, s67:193-202; folds s67:579-581)


def load_real():
    """{T: [(pid, quire, lines)]} via S67.load_pages (plan section 1)."""
    return OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / ("%s.meta.json" % fn)))
                       for T, fn in TRANSLITS.items())


def compute_rk(real):
    folds = S67.folds_of(real["ZL3b"])
    if folds != FOLDS:
        C.refuse("S67.folds_of(ZL3b) = %s, not the plan's 15 quires %s" % (folds, FOLDS))
    vals = OrderedDict()
    for T, pages in real.items():
        vals[T] = text_quire_stats(pages, "vx01_bf|real|%s" % T)
    rk = OrderedDict()
    for q in FOLDS:
        rk[q] = OrderedDict()
        for k in range(1, 7):
            v = [vals[T][q][k] for T in TRANSLITS]
            rk[q][k] = (max(v) - min(v)) if all(x is not None for x in v) else None
    med = OrderedDict()
    for k in range(1, 7):
        d = [rk[q][k] for q in FOLDS if rk[q][k] is not None]
        med[k] = float(np.median(d)) if d else None
    return vals, rk, med


def render(vals, rk, med, header):
    lines = list(header)
    lines.append("# r_k,q = max - min over ZL3b/RF1b/IT2a of statistic k on real quire q (plan 4ed0314a section 3)")
    lines.append("quire\t" + "\t".join("k%d_%s" % (k, STAT_NAMES[k - 1]) for k in range(1, 7)))
    for q in FOLDS:
        lines.append(q + "\t" + "\t".join("NA" if rk[q][k] is None else "%.10g" % rk[q][k] for k in range(1, 7)))
    lines.append("median_q (reported, not used)\t" + "\t".join("NA" if med[k] is None else "%.10g" % med[k]
                                                               for k in range(1, 7)))
    lines.append("")
    lines.append("# per-transliteration quire values")
    for T in TRANSLITS:
        for q in FOLDS:
            lines.append("%s\t%s\t" % (T, q) + "\t".join("NA" if vals[T][q][k] is None else "%.10g" % vals[T][q][k]
                                                        for k in range(1, 7)))
    return "\n".join(lines) + "\n"


def table_json(vals, rk, med):
    return json.dumps(dict(bf_plan_sha256=BF_PLAN_SHA256, folds=FOLDS, stat_names=STAT_NAMES,
                           rk={q: {str(k): rk[q][k] for k in range(1, 7)} for q in FOLDS},
                           median={str(k): med[k] for k in range(1, 7)},
                           values={T: {q: {str(k): vals[T][q][k] for k in range(1, 7)} for q in FOLDS} for T in vals}),
                      indent=1, sort_keys=False) + "\n"


def trace_record(ctx_dir, mode):
    dists, unmapped = run_path_distributions()
    mods = sorted(set(r for r in (rel_root(getattr(m, "__file__", "") or "") for m in list(sys.modules.values())
                                  if getattr(m, "__file__", None) and os.path.isabs(m.__file__)) if r))
    snap = HOOK.snapshot()
    return dict(script=NAME, script_sha256=C.sha256_file(SELF), mode=mode, t=C.utc_now(), t_pt=pt_now(),
                reads_root=snap["reads_root"], modules_root=mods, writes=snap["writes"],
                proc_events=snap["proc_events"], dists=dists, unmapped_modules=unmapped)


def main():
    C.set_below_normal()
    if MODE == "--pin-check":
        env = env_measure()
        bad = env_mismatch(env)
        h = C.append_chained(PIN_LOG, env_log_record(env, "manual --pin-check", bad))
        print(json.dumps(env, indent=1))
        print("pin match:", not bad, bad, "log line", h)
        return 0 if not bad else 3
    if MODE == "--write-stub":
        return write_stub()
    fg = free_gb()
    if not (fg >= MIN_FREE_GB):
        C.refuse("free RAM %.2f GB < %.1f GB" % (fg, MIN_FREE_GB))
    gate = MODE == "--gate"
    env = env_measure()
    bad = env_mismatch(env, _stub_kv if gate else None)
    ctx = C.RunContext(SELF, ARGS, [], gate)
    if gate and bad:
        C.append_chained(GATE_LOG, env_log_record(env, "gate start (refused)", bad))
        C.refuse("environment pin mismatch: %s" % ", ".join(bad))
    if gate and (OUT_TABLE.exists() or OUT_TXT.exists()):
        C.refuse("rk output exists; this script runs once")
    ctx.start()
    logp = GATE_LOG if gate else DEV_LOG
    C.append_chained(logp, env_log_record(env, "gate start" if gate else "dev start", bad))
    real = load_real()
    vals, rk, med = compute_rk(real)
    header = ["# vx01_bf_rk UNVERIFIED", "bf_plan_sha256=%s" % BF_PLAN_SHA256] + ctx.header()
    txt = render(vals, rk, med, header)
    tj = table_json(vals, rk, med)
    if gate:
        outs = [OUT_TABLE, OUT_TXT]
        write_new(OUT_TABLE, tj)
        write_new(OUT_TXT, txt)
    else:
        d = RUN_DIR / ("dev_" + C.utc_now().replace(":", ""))
        outs = [d / "rk_table.json", d / "rk_table.txt", d / "trace_dev.json"]
        write_new(outs[0], tj)
        write_new(outs[1], txt)
        write_new(outs[2], json.dumps(trace_record(d, "--dev"), indent=1) + "\n")
    env2 = env_measure()
    bad2 = env_mismatch(env2, _stub_kv if gate else None)
    C.append_chained(logp, env_log_record(env2, "end", bad2))
    head = ctx.finish(outs, note="env_end_match=%s" % (not bad2))
    print("done; outputs:", [str(o) for o in outs], "log head", head)
    return 0


def write_stub():
    """Build the stub text from the latest dev trace of THIS script hash. Refuses if the stub exists.
    The decision rules are copied from the plan file given with --plan (its sha256 must be 4ed0314a...)."""
    if STUB.exists():
        C.refuse("stub exists")
    plan = Path(ARGS[ARGS.index("--plan") + 1]) if "--plan" in ARGS else None
    if plan is None or C.sha256_file(plan) != BF_PLAN_SHA256:
        C.refuse("--plan PATH with sha256 %s required" % BF_PLAN_SHA256)
    me = C.sha256_file(SELF)
    traces = sorted(RUN_DIR.glob("dev_*/trace_dev.json"))
    traces = [t for t in traces if json.loads(t.read_text(encoding="utf-8"))["script_sha256"] == me]
    if not traces:
        C.refuse("no dev trace for this script hash")
    tr = json.loads(traces[-1].read_text(encoding="utf-8"))
    problems, rows = freeze_problems(tr)
    if problems:
        C.refuse("NO freeze: " + "; ".join(problems[:10]))
    env = env_measure()
    bad = env_mismatch(env)
    C.append_chained(PIN_LOG, env_log_record(env, "freeze (--write-stub)", bad))
    if bad:
        C.refuse("NO freeze: environment pin mismatch: %s" % ", ".join(bad))
    out = ["# vx01_bf_rk.prereg.sha256 -- UNVERIFIED until the Independent Verifier signs",
           "# plan PLAN-X01-B-FALLBACK cited by sha256 only (title reads v4): bf_plan_sha256 below",
           "plan_sha256=%s" % V51_PLAN_SHA256, "bf_plan_sha256=%s" % BF_PLAN_SHA256,
           "script_sha256=%s" % me, "common_sha256=%s" % C.sha256_file(C.__file__),
           "gate_seeds_sha256=%s" % C.sha256_file(C.GATE_SEEDS_FILE),
           "dev_log_sha256=%s" % C.sha256_file_or_empty(DEV_LOG),
           "dev_log_head=%s" % C.sha256_bytes(C._last_line(DEV_LOG) or b""),
           "trace_file=%s trace_sha256=%s" % (rel_root(traces[-1]), C.sha256_file(traces[-1]))]
    for k in ENV_KEYS:
        out.append("env_%s=%s" % (k, env[k]))
    out.append("env_exe=%s" % env["exe"])
    out.append("env_sys_version=%s" % env["sys_version"])
    out.append("env_dists=%s" % json.dumps(env["dists"], separators=(",", ":")))
    out.append("# decision rules copied from the plan (sections 2 and 3):")
    out += ["# " + l for l in plan_sections(plan, ("## 2.", "## 3."))]
    out.append("# files loaded at run time (trace), each against disk:")
    out += ["%s  %s" % (h, p) for p, h in rows]
    write_new(STUB, "\n".join(out) + "\n")
    print("stub written", STUB, C.sha256_file(STUB))
    return 0


def plan_sections(plan, starts):
    lines = plan.read_text(encoding="utf-8").splitlines()
    out, on = [], False
    for l in lines:
        if l.startswith("## "):
            on = any(l.startswith(s) for s in starts)
        if on:
            out.append(l)
    return out


def freeze_problems(tr):
    """Plan section 8 rules (a), (b), (d): every file under ROOT that was read (or is a module __file__) must be in
    LOAD_LIST with the same sha256 on disk; own files are allowed; 0 process events; every run-path distribution
    must be pinned; no module may map to no distribution (except the plan's named exceptions)."""
    own = {norm_load_key(rel_root(p)) for p in (SELF, DEV_LOG, GATE_LOG, PIN_LOG, STUB)}
    ll = {norm_load_key(p): (p, h) for p, h in LOAD_LIST.items()}
    problems, rows = [], OrderedDict()
    for r in sorted(set(tr["reads_root"]) | set(tr["modules_root"])):
        k = norm_load_key(r)
        if k in own or r.startswith("runs/vx01_bf_rk/"):
            continue
        if k not in ll:
            problems.append("unlisted file %s" % r)
            continue
        p, h = ll[k]
        if not (ROOT / p).exists() or C.sha256_file(ROOT / p) != h:
            problems.append("hash differs %s" % p)
        rows[p] = h
    if tr["proc_events"]:
        problems.append("%d process events" % len(tr["proc_events"]))
    for d in tr["dists"]:
        if d not in PIN_DISTS:
            problems.append("unlisted distribution %s" % d)
    for m in tr["unmapped_modules"]:
        problems.append("module %s maps to no distribution" % m)
    foreign = [w for w in tr["writes"] if not os.path.normcase(w).startswith(os.path.normcase(str(RUN_DIR)))
               and os.path.normcase(w) not in {os.path.normcase(str(x)) for x in (DEV_LOG, GATE_LOG, PIN_LOG)}]
    if foreign:
        problems.append("writes outside declared outputs: %s" % foreign[:5])
    return problems, list(rows.items())


if __name__ == "__main__":
    sys.exit(main())
