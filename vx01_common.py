"""vx01_common.py - shared guard, logger and stub check for the X-01 plan (script 0).

Plan: PLAN-X01-v5.1, SHA256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393
(signed by the Independent Verifier). Sections used: 3 (rules 1-4), 3a (seeds), 6 (script table).
Frozen FIRST (script 0). Never edited after freeze; a change = new versioned file (vx01_common_v2.py).
No analysis here. Library only; it is never started directly, so it has no dev log of its own.
All results of anything built on this module are UNVERIFIED until the Independent Verifier signs.

What it does
  * GATE_SEED_SHA256: SHA256 of EACH gate seed written as decimal text (156 values, plan 3 rule 3).
  * dev mode: every seed handed to a vx01 script is hashed; if it is in GATE_SEED_SHA256 -> exit 3.
    A dev run is also refused (exit 3) once the script's own stub file exists (plan 3 rule 4).
  * gate mode (--gate): recompute SHA256 of the script, of this module, of vx01_gate_seeds.json and of
    the script's dev log; compare with stub lines script_sha256= common_sha256= gate_seeds_sha256=
    dev_log_sha256=; check every seed in vx01_gate_seeds.json hashes into GATE_SEED_SHA256; also verify
    the plan hash line and every "<sha256>  <path>" line of the stub (imports and data). Any mismatch or
    missing stub -> exit 3 BEFORE any gate seed is used. Refuse if the gate log already holds a
    GATE-COMPLETE for this script_sha256 (single shot).
  * dev log: vx01_<name>_dev_runs.log, one per top-level script, hash-chained (each line holds the SHA256
    of the previous line; first line holds 64 zeros). The stub fixes SHA256 of the whole file.
  * gate log: vx01_<name>_gate_runs.log, same line format, NOT hashed in the stub.
This is code discipline, not cryptography; the IV recomputes the hashes independently.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAN_ID = "PLAN-X01-v5.1"
PLAN_SHA256 = "af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393"
EXIT_REFUSE = 3
MAX_WORKERS = 2          # plan 3 rule 8: <= 2 BelowNormal workers
ZERO64 = "0" * 64
GATE_SEEDS_FILE = ROOT / "vx01_gate_seeds.json"

# SHA256 of str(seed) for each of the 156 gate seeds of plan section 3a (sorted).
GATE_SEED_SHA256 = frozenset((
    "00f6f677fb6d00fee3ff8d47e32637b77927ea04a388563ed37c06319ddef9c9",
    "03eacf88f0df1357781867ef3f3947270909b66b3f9fe9f1321f82d050ac2ba1",
    "05fca5f7b1d46fac6f2a4416afe0b442f0be9d84774c4a9d92d49a7dd930a2e5",
    "0ec66f5f61277f9d73a5ea3f9bf6f4a94ed647ed9d4f191537bed004c7002061",
    "126938ba9933c4448574f16adb9b70e3623410b4e7ad1069f3900e511b036751",
    "13fad42a9648076bf53dc4e9d48d7b7331919bb816e6dddf3828099314334709",
    "1433a95b77e8c1b38f6358663b21aac75e941d765e84e6e1bb4d30d451d4ea53",
    "179f204b78746ab6df4fbab4adb8f82a78561de42a35f89fca97bc845fe7ab07",
    "17a8f0049aa3440cbe0d2756923844df5c50f66e1ce51be349582219dc274ce3",
    "19d96179d481de7fd46cfa5792171c307ac2968c7a4505110d5ae13be860293d",
    "1c1352590f99df9807cb3f74e9f9815824ddca2eafaa9fec5e13a19213d855c9",
    "1c89041d13e4e36e029b6d62cb0e1cb19cd16fbad9f53c94e2c7c688888644e5",
    "1e11163342dc21f0ac5cc7057d5fb45e078949aeef0108c8cf6a997cd71850de",
    "20d3ba9dd6f15c744b04242578057aa906698b9068c5c3a3b1c57774506f87d6",
    "21710f5303f4fdfa6776c7f97faf8cbba1d784f1535a89f9148e24a7c57b921b",
    "22578b145b0ff25125f1f6bd6055938cee78573ac5c80db0af57663238e33dc3",
    "234a83b6c00d40c066d24b8da2c15c5ac5a54e56b73c0de5861b183090c32028",
    "24715aecf8015e22c238d3c3882fddf252d6c60ad2282b549f08c5c221515c94",
    "25cd861a1d1b80363902fc7b9cedc5628d7573e59ea61858e7e71208cbb53891",
    "27bee1168c4ba54eeb989e0956f35a5e9acb445a36529691b11bd687312722fd",
    "27dabe54cbf561472f927b6835f0254addeb61c68d5248c67e93b8f0a1a3b9ef",
    "27f1667c8b8428b6ef3987a557cdd8f113b29b1299bdb592ac1c978c8331021f",
    "2c0a5347b519868c7817d6a7f33fa6dceebddeb4a360fbdc3704349873376aca",
    "2c2b4e4f8d2fd7460057db66564058f250c50660def0f7ec346aa259e5b42463",
    "2c531502f85700fd9159f23a24d4bc008896ba68d092dd79446d314b5999a3de",
    "2ef08b53dd38fc8065d0ffd445ad2b0a9312aaaa81c57f7bf72831686e659bfd",
    "3207daa356d7a26f32a052c5432c8e7736e4dbba881e9698627cbcea51cb55bc",
    "3218b0759b52ac05bcde1fd6835469275531ab08a4f386417833bffa0e567ed9",
    "329e3c12389fe77bbd68a766b9b8f4e579fb6b205901c388ea47c23e9ffe87c6",
    "33122eed59ab18f5af953797f4ac4a3ecd5dd1865ed96b2e50b391536484c9ae",
    "337afdaa957370f9d217c5a52064416350dcdd9a86b4f70e74626c8a098ea515",
    "35d9ffcde22b6db3b4d690f68c5847d29255454190640d35c5c817470d082683",
    "370699f33ce862cfe1002538bbdf9669b29a8ff98e8068987ad55195cccf134f",
    "37121756ff237cd5d61d135f4846f9d9dfdd8dedbbb24f1785d7fd7aabbfbec3",
    "37ec85125213c28a9594e2350b265276387b7ce0ce257ff3c36a81745999b8ff",
    "394c42039d1eb01f97b97b47a87efaed5505657dd74a358a7cdcea2eed46c86e",
    "3baddd62ec5098355cc72344cf8137a9ad51f6e3211710d44824a60167a63d71",
    "3bd784826f3c74033e2e082bd09f2109c762c71f06333a5eccd24b304bc37849",
    "3ddb04747b2b6757c1439379fcfb31e3c1fa85d2197b108bd53218964302ec93",
    "3fc8d72128ed916f01d2c687f5785c81da064371bfa9aee06894a4342a643736",
    "4031bc7bdacb9b4f645c64c0f7a7750fc0963fadbb38e7764d63ca9de111d72f",
    "416a3001e3f15ad2042dbaea2ae5b089fd501424e6fabbebed6979a40ae134bd",
    "4290f35b4aaa4c0f67c1933760be4e281a39694669d9b05b6a456d10f455796d",
    "42bf5f249fb469ec40569aa1b037a7692042ef7b81661aefc1c6bc83518e1022",
    "439fa9877d4b4323c8ed44686466acb2d47aa9fad04833665cfe2bc0fa74220f",
    "46883a7bc4cffd93dca31128afed57aba1756861aca4a20eb927f64222937c4f",
    "497e34d798b0a07425140ad28220fc306dd1d616653f195d96b26f0b125d4e6e",
    "49bff68bb9583b30b9e347b1da3b0aec87cfece97d73a49c6ba228431b3a65e8",
    "4a2206727822e75d44c35ba5af8558adf4129247447ac825bba4c3e732c721d3",
    "4ba009b94ab06df09886749dfd59877731eab21e8be802653f20f4b3f948be96",
    "4cdf0eff82fa521d31aa8fbe41245c347b49dc08a3b18530909bafeaa2ff3eee",
    "4d262c68bd0e974d97573ecbddc48ea0beaa958f7fc7a3ee15b677eb2acce1ce",
    "502def460f57cc25abf9920a62e104a1688dc6031c0aa617d47f7199710524d6",
    "5508c74a6d1e42d8908bf340143086a130cc108c6398d4e295b2e8b8e5e86c90",
    "553c064bc6e769106b9e2b8173e95ef76a95e8bd96cc90dc56e588a497cee6d3",
    "55a95c615088ce9970ec037ae16fed374273ee94e093af4093e77fba3667e6ab",
    "593375fee545c5470c9f8276b6384d7785aa6fd5be3e78e1fbade041eb10bdc4",
    "5b03e9db80f1c2e936bb20e34853cdbb062c1a29607da16bc6ef94aaa1be7c5f",
    "5c71aed3b3bc47af44e663458f874ab91308229b7facb40b56d9dba77414cdee",
    "5f2507099a1cdf306e7ec23daea14036f1e04ece4dbd0df98823a21e635ce9cc",
    "604c4816aa2077cfda9266f53c87ea888a8bebaf8259f2c26d1196707027e489",
    "63926e2a84a3354d4e090a282475f9d967b8c18e308beb94e8332a4fd80d5b5a",
    "66eb5d30c1c6c409b6cbdb4541c383300c6b7fcf6eb4dce5af142dde829cd60e",
    "672f17dcd957a3de032335c812baceaf8cf0d6ef1d9b9141cef0f069174613b0",
    "674063a2e50f006b70f2a563121ca13118a83e04d3da878119030063cc8c6d5f",
    "6cda93fe0b6e31fef557c6a78511108ca834264f02fd468566297f1c237f0e08",
    "6d985139d35cbcbc757cb8677f1133b87aa277018ba9255d6d6093d9aab6f9c1",
    "6dd71c1e8a99a4eae7c52132a2b3fabbf65436ad9166d3668967fc59ffe8d796",
    "72c0ec3e5d54ff2d8e434a226bad32f84e85dcfa2c5e9b11ed450fa8a9285f8a",
    "74b52f78a0c5ff4a214230fc383b40840147c5dcf788bed53413d31d606f1755",
    "74ce083699683c9229986f87cc491bc4e2d023b5ee3817aab0f67593ac7ca767",
    "771b49e4d1f6cff870df1f5cc832529772da4277b7be244943f9ab263e537d5d",
    "7bb5b89cc1f7541d732709bc1aa065baac4f1230eee316489fa7d4b8100f4961",
    "7f4ef756d244eaa9080c1434e81d34f002a55140243dcb9d87d6cf6ee559461f",
    "823b2ad25c6f9c415bfe028818e81de1b37a53bb9ee11c10e6c73d5518658123",
    "8331b5d1e00543ac6ccdc4f70c65f011a6c83f6bbae59990709ba01c310f5230",
    "857136e5fe5fdcd9a50bc77ec09467cb4348ddcd4fcc3580e0acdf275e9e3a55",
    "8640852ca0b3d966ffcd39335f097e6889b654590569526e0cc3cd056ca37d5b",
    "874837758946e1ee63618c1f603df0e32cb6d8022cc3437f512696f1aafb61b7",
    "8780178214485ad268c555188efa0378d8d38f3e3f04d2e24493d4d945048943",
    "87dc57f58b2ed7ebf2e87dfe31f58fec9fdeceb7f98ac997707c00e0c119600c",
    "894daf881b85be2bab8d4573d76d27821e5ec8d5bfa4d02b9f56d9b30b9ab596",
    "895ef4ea7c2db12ed34ed99e52c229939feda6ad5be5670d44721572beddd1eb",
    "895f58df1e12bc5a205be34cdfb2a03631de7a4023799c87ead9f3dd5a53c913",
    "89763e27a9ef8f621c367cfed414dafa217119fe89a4584ffec1102adba2b0c2",
    "8a6df7546816fc84e4e1cdb918a9c1b504cf37661dbb1f48a7847323ffe792be",
    "8c99b1f63c6b1cd41438e0ff278d4d7be3b8a1c6efd80b91356465ed37b0d585",
    "94686b40319d02f39c3b701b98af60bf3bcce997b674037962a6cc61df1d529f",
    "94f4e68affb116d3c199e1667458eb2e7c01dce6f058e93bda7708bfbe152634",
    "968cd90a4ab0c6ff26ef88be095f79a849e45ebc1f04e036e4565e3304372815",
    "9865522a5d2a895ebed70b44e103cb0e0b5427763e5b900288dbb422f606d6f4",
    "9925cb5d88d4bb9813237ce92abf27adaa3edc2130380baf370f9dd1989f66fa",
    "992ef44d692c5bc60ef2e11ff6537cd36453544472d5ecaa0d3d53ecd3fb06fb",
    "994c5cd882fdf4a1b528a747b26dd52d9cbac4a38a6ddc0bdcd36832b2d26f95",
    "99e76f8633291af71c06a42d6c9ccc18d07f6df392ef01a9e0d1b3e3f46871ec",
    "9afa43dfe581ba080082a5ea6d77fca881e3429381949a9009fc61075866689a",
    "9bcb67b884bf4eb34912f8bcfe378440ea7fc35b2acc9965abfcc9636e60bd5b",
    "9d0e3a0f44e99a751cd163b0a3042ce9da1f0fc6bd05f0e899b0e877960a46a3",
    "9f5e4558e1034032e1b7693707dee9ab8c3f3e8778cda70c0fac3d44a7aa2084",
    "a27579ed4c1b8c23dfd4b0485df735fb89d6bf6c2f81ef22eb5cf1bd15dab236",
    "a5fd6fb8b1ce3cae0b9d2bfd8fd66104da9faa168357277fddabf661e6eff69d",
    "a76a4c326fc74807adf0a7a53fab0cceb4e8fa416d93efa23e91e5fb943aca82",
    "a789490144f41e5e4dbecbc2061bfcd1e4741ff73530ee9117d58df1d345d326",
    "a7ea97ce72e2864d86d9ca4670f7610bd8c0314b5d31e0b0d3a983d16a642700",
    "a94e4c81c876573ff1ce111ef5165b2c6ad61b32e0e5b684899f0d14d7fa8f89",
    "aa963aaa6790d606b72a2391b69473493fcf91d5872f7e473dd98b157cefb4d1",
    "ad6b3ac61a27b588379f08fba62157c06cd944d6188f6c262dfb547d8910fb25",
    "ae6bb0a293b5941d0ef20c641cae5f3c4bf90c8420aefc7a120e8ce9054faff7",
    "b33349072e8d229a57892d52f83f0c8cb4759d68080d26b49b790ceba590e14e",
    "b42d38b9484a5c49d8ca13ae91d030bebea49330184746da4de520293ffc0b32",
    "b8982b17b24a74f80ad4ee5c52f8d00cfdb68a3ea2324fa6e98543aa374527b4",
    "b8f890c7365dc6e426075a36daea428a5bad12fb0704fa8d49c96b092582e6fe",
    "b93c343b701eb34e964a08cd01e354cc47a33631f69687f002b625e4a2dff292",
    "b9e3a944219d116c99acb4e5ee385631b93be75c62005a3e6db35bce23a97700",
    "ba01be2830467898c6b5581d4fe6629aaba380262ac193faf59e2bd72f39c722",
    "ba15d3ed84c1170476239289f748306253944d2e9e9ba9dab220929c2f0d4be1",
    "bac722c9671365625ff45e0cf1d95495967b26ed6dfed751591cc2955e168f41",
    "bafb479ddbd0c6ffa143b23d9af7b286533151710167c8b3d82b9bfc8b8cdb00",
    "becc25a60eba60e4f221fe9569667fc61add989db21fe0f47c4c9bb920775506",
    "bf5915a0469cc0eecc0fbfcbb421664f5f09c773a1647e6ceb535509c22cfceb",
    "c0ba79a143613872ea817477b4c1f349ce159b86d7612863c9d3e68877a9880b",
    "c12bfa817b5fd5ea9a9ac1963799c22271ee93b6a86a18d8e7623da0ce06e923",
    "c20f9db3f2ec6cd2e56b43796e1b0366b8e5882dad41d7b60c2dd2389420d8f3",
    "c3f6f61d60c3037b4eba78be6e6fe9ffaea284742ac7aa86d00c2e6ffd137437",
    "c5a5f96f422ab450f53a043cff4947e07a8b08af01018d563f3f6b1f5551c42a",
    "c737bf362b7ad2a5be8e3e79b8b30b9958b9cbfa13e555b9371f2fea89665ae3",
    "c7d6efd726009914da58a45499615223bd564c04059bc649acd4b794cda79d79",
    "caa9bfd8c5d7977ea17f040ff2efe658a0b98234145e9767469b1d72f8e82638",
    "cb2cf9b0867d19ee6b87bf1441c7dc9d715f5a1fcba17ba5a2a958da086b9c95",
    "cd737a306a43ae785827d6cde7f04105c087f9e7f52c44ba42286fb681314a57",
    "ce0cd1c07fb316f549c4db70d9060607312e14cdd517077c54edff397d8ba6b5",
    "d2102907555bb2d1027540acbed30a6c1045c7fa7ef01583aecf4f09eb683e92",
    "d33f3ba521db5ebda2282658746b46ae7de5dd12e0d8dbe38d1223e82d40491c",
    "d55d116a24a3e9b41436674c67b8e7fa33ee2144ab2f33dc80a07a5644eec579",
    "d6243d217a9f1df78b1feeef2d697f0ff75ccf2ad2ff287d9d46f0f56a3ff50e",
    "d6b7d04de8311a8a0ffcce4ba290c47a7d09ac784fa8993e2d2ebd438cefe6a4",
    "d971ca1d54429b972e05521b523d38baba156704a698f0465a54e79ea67c4778",
    "d9d15bb682cdc4d0acf933ff217e05e6a3ef8fca4edbe86cf56e3898febaa2fe",
    "e0a653aa30912df12397733d93c5c272db53fe693e19324280c96050e5d2c486",
    "e1056ea7efb0786cabad4c66d5ec24eb729ed24323e9d18f2af50171de465230",
    "e69118af8a308fc5263598d17f862accafe1db73f4363a25f33a7328fa472da7",
    "e87dcbb842a1031c75e5a5521f961e53edc8f7364fefa001c5adf6a11dd703b0",
    "eb006d48dac53a431111d208a2c6d5cc659dfe828fdcb25705d715a5b9ae0520",
    "eba8c0183b88afd7c7231dc9a28042078f7ed61425af61570b3a964fd850c9c2",
    "ebd19809f98e925f6c283080dfb367521db55c44bbbf79e5fafd43d9ae7e03d8",
    "ec0b7cf7792cb86ecb19d8b48ccb2f1171a791a647102c69265f0f48e453ea13",
    "ed3a57b117d4e5b9fecc7e9bace401877de89b977950fce3ce71b56cb1fea41b",
    "ee02ea89a603a874c211f4b4a4fd0e575edf43ca87f08376c2fcd56c62a82d8f",
    "f4ed421e71d0ae2638d16ed333247e65ffc91cd42fb25e7bb69fd79ba446d74d",
    "f4fe98e0e02db0f5aac829dd3da506f34c61ebb8bde21e032a3d91169d6d9ca4",
    "f82d70e0fe2c3f5c0ac074beba567708b1bb646046432a11431113036e6c9561",
    "f8a3e7349ac7e785e259752cae7e26507a13e7484cffde7586c03f35241aa582",
    "f9edff618df96ff11956ef73337e8f3a4c5c272765cb0c76591ddc75cf6c5182",
    "fa2847f1330ee7d2caed49879dee524d1936ecdba69c09ff22cc888cd63e083b",
    "fb75d92460dc1cde81df3e825e864452ca3066b36a5b19d2740336b804d0160f",
    "fef90aa7f2cd1e797504322caa6a57eab053fd267c4185d98fe31b8d59c05b91",
))

# Dev seeds of plan section 3a (36). Arbitrary constants chosen before any run; disjoint from gate seeds.
DEV_SEEDS = {
    "A1": [
     20261111,
     20261112,
     20261113,
     20261114,
     20261115
    ],
    "A2_copy_edit": [
     20262141,
     20262142,
     20262143,
     20262144,
     20262145
    ],
    "A2_core_pool": [
     20262101,
     20262102,
     20262103,
     20262104,
     20262105
    ],
    "A2_label_events": [
     20262161,
     20262162,
     20262163,
     20262164,
     20262165
    ],
    "A2_line_sticky": [
     20262121,
     20262122,
     20262123,
     20262124,
     20262125
    ],
    "A4": [
     20263101,
     20263102,
     20263103,
     20263104,
     20263105
    ],
    "B0": [
     20261101,
     20261102,
     20261103
    ],
    "B2": [
     20264101,
     20264102,
     20264103
    ]
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def sha256_file_or_empty(p) -> str:
    """SHA256 of the file, or of the empty byte string if the file does not exist (no runs yet)."""
    p = Path(p)
    return sha256_file(p) if p.exists() else sha256_bytes(b"")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def set_below_normal() -> None:
    """Lower this process to BelowNormal on Windows (plan 3 rule 8). No-op elsewhere."""
    if os.name == "nt":
        try:
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
        except Exception:
            pass


def derive_seed(master: int, transliteration: str, family: str, control: str, fold) -> int:
    """Plan 3a: first 8 bytes of SHA256 of the text 'master|transliteration|family|control|fold'."""
    text = "%s|%s|%s|%s|%s" % (master, transliteration, family, control, fold)
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def seed_is_gate(seed) -> bool:
    return sha256_text(str(seed)) in GATE_SEED_SHA256


def refuse(msg: str) -> None:
    sys.stderr.write("vx01 REFUSE (exit 3): %s\n" % msg)
    sys.stderr.flush()
    sys.exit(EXIT_REFUSE)


def guard_dev_seeds(seeds) -> None:
    """Dev mode: exit 3 if any given seed hashes into the gate set (plan 3 rule 3a)."""
    for s in seeds:
        if seed_is_gate(s):
            refuse("seed %s is a gate seed; dev runs may not use it" % s)


def script_name(script_path) -> str:
    return Path(script_path).stem          # e.g. vx01_a1_known_answer


def dev_log_path(script_path) -> Path:
    return ROOT / (script_name(script_path) + "_dev_runs.log")


def gate_log_path(script_path) -> Path:
    return ROOT / (script_name(script_path) + "_gate_runs.log")


def stub_path(script_path) -> Path:
    return ROOT / (script_name(script_path) + ".prereg.sha256")


def _last_line(path: Path):
    if not path.exists():
        return None
    data = path.read_bytes()
    if not data:
        return None
    lines = data.split(b"\n")
    while lines and lines[-1] == b"":
        lines.pop()
    return lines[-1] if lines else None


def append_chained(path: Path, record: dict) -> str:
    """Append one JSON line whose prev_sha256 is the SHA256 of the previous line. Returns this line's SHA256."""
    prev = _last_line(path)
    record = dict(record)
    record["prev_sha256"] = sha256_bytes(prev) if prev is not None else ZERO64
    line = json.dumps(record, sort_keys=True, ensure_ascii=True, separators=(", ", ": "))
    with open(path, "a", newline="\n", encoding="ascii") as f:
        f.write(line + "\n")
    return sha256_text(line)


def read_chain(path: Path):
    """Return the parsed records of a chained log; verify the chain; raise ValueError on a break."""
    recs, prev = [], ZERO64
    if not path.exists():
        return recs
    for raw in path.read_bytes().split(b"\n"):
        if not raw:
            continue
        r = json.loads(raw.decode("ascii"))
        if r.get("prev_sha256") != prev:
            raise ValueError("hash chain broken in %s" % path)
        prev = sha256_bytes(raw)
        recs.append(r)
    return recs


def parse_stub(path: Path):
    """Stub: '#' header lines; 'key=value' lines; '<sha256>  <path>' hash lines. Returns (kv, hash_lines)."""
    kv, hl = {}, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if "=" in s and " " not in s.split("=", 1)[0]:
            k, v = s.split("=", 1)
            kv[k.strip()] = v.strip()
        else:
            parts = s.split(None, 1)
            if len(parts) == 2 and len(parts[0]) == 64:
                hl.append((parts[0].lower(), parts[1].lstrip("*").strip()))
    return kv, hl


class RunContext:
    def __init__(self, script_path, argv, seeds, gate: bool):
        self.script_path = Path(script_path).resolve()
        self.name = script_name(self.script_path)
        self.argv = list(argv)
        self.seeds = [int(s) for s in seeds]
        self.gate = gate
        self.script_sha256 = sha256_file(self.script_path)
        self.common_sha256 = sha256_file(Path(__file__).resolve())
        self.gate_seeds_sha256 = sha256_file(GATE_SEEDS_FILE) if GATE_SEEDS_FILE.exists() else "missing"
        self.dev_log = dev_log_path(self.script_path)
        self.gate_log = gate_log_path(self.script_path)
        self.stub = stub_path(self.script_path)
        self.stub_match = None
        self.stub_files_match = None
        self.prior_gate_starts = 0
        self.header_extra = {}

    # ---- header lines for the result file (plan 3 rule 3c) -------------------------------------
    def header(self) -> list:
        h = [
            "# UNVERIFIED (not yet seen by the Independent Verifier)",
            "plan_id=%s plan_sha256=%s" % (PLAN_ID, PLAN_SHA256),
            "mode=%s" % ("GATE" if self.gate else "DEV"),
            "script=%s.py script_sha256=%s" % (self.name, self.script_sha256),
            "common_sha256=%s" % self.common_sha256,
            "gate_seeds_sha256=%s" % self.gate_seeds_sha256,
            "dev_log_sha256=%s" % sha256_file_or_empty(self.dev_log),
            "stub_match=%s stub_files_match=%s" % (self.stub_match, self.stub_files_match),
            "earlier_GATE_START_without_complete=%d" % self.prior_gate_starts,
            "argv=%s" % " ".join(self.argv),
            "seeds=%s" % ",".join(str(s) for s in self.seeds),
        ]
        for k, v in self.header_extra.items():
            h.append("%s=%s" % (k, v))
        return h

    # ---- start / finish -------------------------------------------------------------------------
    def start(self) -> "RunContext":
        if not self.gate:
            guard_dev_seeds(self.seeds)
            if self.stub.exists():
                refuse("stub %s exists; a dev run after the stub would change the dev log hash" % self.stub.name)
            append_chained(self.dev_log, {"t": utc_now(), "event": "DEV-START", "script_sha256": self.script_sha256,
                                          "args": self.argv, "seeds": self.seeds, "outputs": {}})
            return self
        # ---- gate mode: every check happens before any gate seed is used ----
        if not self.stub.exists():
            refuse("no stub %s" % self.stub.name)
        if not GATE_SEEDS_FILE.exists():
            refuse("vx01_gate_seeds.json missing")
        kv, hl = parse_stub(self.stub)
        need = {"script_sha256": self.script_sha256, "common_sha256": self.common_sha256,
                "gate_seeds_sha256": self.gate_seeds_sha256,
                "dev_log_sha256": sha256_file_or_empty(self.dev_log), "plan_sha256": PLAN_SHA256}
        bad = [k for k, v in need.items() if kv.get(k, "").lower() != v]
        self.stub_match = not bad
        if bad:
            refuse("stub mismatch on %s" % ",".join(bad))
        gs = json.loads(GATE_SEEDS_FILE.read_text(encoding="utf-8"))
        for key, lst in gs.items():
            for s in lst:
                if not seed_is_gate(s):
                    refuse("seed %s in vx01_gate_seeds.json is not in GATE_SEED_SHA256" % s)
        badf = []
        for h, rel in hl:
            p = ROOT / rel
            if not p.exists() or sha256_file(p) != h:
                badf.append(rel)
        self.stub_files_match = not badf
        if badf:
            refuse("stub file hash mismatch: %s" % ", ".join(badf[:5]))
        recs = read_chain(self.gate_log)
        done = [r for r in recs if r.get("event") == "GATE-COMPLETE" and r.get("script_sha256") == self.script_sha256]
        if done:
            refuse("gate run already completed for this script hash (single shot)")
        self.prior_gate_starts = sum(1 for r in recs if r.get("event") == "GATE-START"
                                     and r.get("script_sha256") == self.script_sha256)
        append_chained(self.gate_log, {"t": utc_now(), "event": "GATE-START", "script_sha256": self.script_sha256,
                                       "args": self.argv, "seeds": self.seeds, "outputs": {}})
        return self

    def finish(self, outputs=(), note: str = "") -> str:
        outs = {str(Path(p)): sha256_file(p) for p in outputs}
        ev = "GATE-COMPLETE" if self.gate else "DEV-END"
        path = self.gate_log if self.gate else self.dev_log
        return append_chained(path, {"t": utc_now(), "event": ev, "script_sha256": self.script_sha256,
                                     "args": self.argv, "seeds": self.seeds, "outputs": outs, "note": note})


def gate_seed_list(key: str) -> list:
    return list(json.loads(GATE_SEEDS_FILE.read_text(encoding="utf-8"))[key])


def dev_seed_list(key: str) -> list:
    return list(DEV_SEEDS[key])


# self-check at import: dev and gate seeds are disjoint and counted as the plan says
assert len(GATE_SEED_SHA256) == 156
assert sum(len(v) for v in DEV_SEEDS.values()) == 36
assert not any(seed_is_gate(s) for v in DEV_SEEDS.values() for s in v)
