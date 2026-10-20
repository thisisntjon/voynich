"""s129: Fontana folio-1v known-answer, ciphertext-only key recovery (D-077, D-072 step 2).

Modes:
  fixture            positive control (planted homophonic keys on held-out Latin, K in 25/35/45, 3% noise)
                     and negative control (token order shuffled); prints CONTROL_PASS / CONTROL_FAIL
  agree A.tsv B.tsv  step A gate: token agreement of two independent transcriptions on the lines B covers
  solve A.tsv        step B: ciphertext-only solve of the transcription, scored against the manual plaintext
Transcription TSV: one row per cipher line, "Lnn<TAB>tokens"; tokens are glyph IDs separated by spaces,
"/" = word gap, "?" = unreadable glyph (dropped from decode and score), "." = point (treated as word gap).
The plaintext ground truth is read only in `solve`, after the key is fixed, for scoring.
"""
import math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TRAIN = [os.path.join(ROOT, "data", "controls", f) for f in ("latin_caesar.txt", "latin_augustine.txt", "latin_pliny_herbal.txt")]
FIXTURE_TEXT = os.path.join(ROOT, "data", "controls", "latin_macer_floridus.txt")
GT = "C:/Users/thisi/Desktop/yonichmanuscript/fontana_v1/transcription_gt_0007_manual.txt"
ALPHA = "abcdefghiklmnopqrstuxyz "  # j->i, v->u, w->u; 23 letters + space
IDX = {c: i for i, c in enumerate(ALPHA)}
SP = IDX[" "]
N = len(ALPHA)
SEED = 129
ITERS, RESTARTS = 40000, 24
CALL_RECOVERED, CALL_PARTIAL = 0.80, 0.50
CONTROL_MIN = 0.85


def norm(t):
    t = t.lower().replace("j", "i").replace("v", "u").replace("w", "u")
    t = re.sub(r"[^a-z]+", " ", t)
    t = "".join(c for c in t if c in IDX)
    return re.sub(r" +", " ", t).strip()


def lm():
    txt = " ".join(norm(open(p, encoding="utf-8", errors="replace").read()) for p in TRAIN)
    a = np.array([IDX[c] for c in txt], dtype=np.int64)
    q = a[:-3] * N ** 3 + a[1:-2] * N ** 2 + a[2:-1] * N + a[3:]
    # add-k smoothing toward the unigram distribution: an unseen context backs off to letter frequency,
    # so strings of rare letters in unseen contexts cannot outscore real Latin
    m = np.bincount(q, minlength=N ** 4).astype(float).reshape(N ** 3, N)
    uni = np.bincount(a, minlength=N).astype(float) + 1.0
    uni /= uni.sum()
    k = 2.0
    return np.log((m + k * uni) / (m.sum(1, keepdims=True) + k)).ravel()


def parse(path):
    lines = {}
    for row in open(path, encoding="utf-8"):
        row = row.rstrip("\n")
        if not row.strip() or row.startswith("#"):
            continue
        k, _, toks = row.partition("\t")
        lines[k.strip()] = [t for t in toks.replace(".", " / ").split() if t]
    return lines


def to_stream(lines):
    """Cipher IDs as ints with -1 for word gaps; line ends are word gaps; '?' dropped."""
    ids, out = {}, []
    for k in sorted(lines):
        for t in lines[k] + ["/"]:
            if t == "?":
                continue
            if t == "/":
                if out and out[-1] != -1:
                    out.append(-1)
                continue
            out.append(ids.setdefault(t, len(ids)))
    return np.array(out, dtype=np.int64), ids


def score(stream, key, Q):
    d = np.where(stream < 0, SP, key[np.clip(stream, 0, None)])
    q = d[:-3] * N ** 3 + d[1:-2] * N ** 2 + d[2:-1] * N + d[3:]
    return Q[q].sum()


def solve(stream, nid, Q, rng):
    best, bkey = -1e18, None
    for r in range(RESTARTS):
        key = rng.integers(N - 1, size=nid)
        cur = score(stream, key, Q)
        for it in range(ITERS):
            T = 12.0 * (1 - it / ITERS) + 0.2
            i = rng.integers(nid)
            old = key[i]
            key[i] = rng.integers(N - 1)
            s = score(stream, key, Q)
            if s >= cur or rng.random() < math.exp((s - cur) / T):
                cur = s
            else:
                key[i] = old
        if cur > best:
            best, bkey = cur, key.copy()
    return bkey, best


def decode(stream, key):
    return "".join(" " if x < 0 else ALPHA[key[x]] for x in stream).strip()


def semiglobal_acc(dec, gt):
    """1 - edit distance / len(dec) on letters only; gt prefix and suffix are free (the rubric and the continuation)."""
    a, b = dec.replace(" ", ""), gt.replace(" ", "")
    n, m = len(a), len(b)
    bb = np.frombuffer(b.encode(), np.uint8)
    prev = np.zeros(m + 1, dtype=np.int64)
    for i in range(1, n + 1):
        cur = np.empty(m + 1, dtype=np.int64)
        cur[0] = i
        cur[1:] = np.minimum(prev[:-1] + (bb != ord(a[i - 1])), prev[1:] + 1)
        # left-to-right insertion pass: cur[j] = min(cur[j], cur[j-1] + 1), done as a running minimum
        cur = np.minimum.accumulate(cur - np.arange(m + 1)) + np.arange(m + 1)
        prev = cur
    return 1 - prev.min() / max(n, 1)


def plant(text, K, rng, noise=0.03):
    letters = sorted(set(text) - {" "})
    freq = {c: text.count(c) for c in letters}
    homs = {c: 1 for c in letters}
    for _ in range(max(0, K - len(letters))):
        c = max(letters, key=lambda c: freq[c] / homs[c])
        homs[c] += 1
    table, nxt = {}, 0
    for c in letters:
        table[c] = list(range(nxt, nxt + homs[c]))
        nxt += homs[c]
    toks = []
    for w in text.split(" "):
        for c in w:
            t = int(rng.choice(table[c]))
            if rng.random() < noise:
                t = int(rng.integers(nxt))
            toks.append(f"G{t:02d}")
        toks.append("/")
    return {"L01": toks}


def fixture():
    Q = lm()
    rng = np.random.default_rng(SEED)
    src = norm(open(FIXTURE_TEXT, encoding="utf-8", errors="replace").read())
    start = len(src) // 3
    text = src[start:start + 1100]
    text = text[text.index(" ") + 1:text.rindex(" ")]
    ok = True
    for K in (25, 35, 45):
        st, ids = to_stream(plant(text, K, rng))
        key, _ = solve(st, len(ids), Q, rng)
        acc = semiglobal_acc(decode(st, key), text)
        print(f"positive K={K}: n_ids={len(ids)} acc={acc:.3f}", flush=True)
        ok &= acc >= CONTROL_MIN
    st, ids = to_stream(plant(text, 35, rng))
    toks = [int(t) for t in st if t >= 0]
    rng.shuffle(toks)
    sh = []
    for i, t in enumerate(toks):
        sh.append(t)
        if (i + 1) % 6 == 0:
            sh.append(-1)
    sh = np.array(sh, dtype=np.int64)
    key, _ = solve(sh, len(ids), Q, rng)
    nacc = semiglobal_acc(decode(sh, key), text)
    print(f"negative shuffled: acc={nacc:.3f} (must be < {CALL_PARTIAL})")
    ok &= nacc < CALL_PARTIAL
    print("CONTROL_PASS" if ok else "CONTROL_FAIL")


def agree(pa, pb):
    A, B = parse(pa), parse(pb)
    tot = err = 0
    for k, bt in sorted(B.items()):
        at = A.get(k, [])
        n, m = len(at), len(bt)
        D = list(range(m + 1))
        for i in range(1, n + 1):
            prev, D[0] = D[0], i
            for j in range(1, m + 1):
                cur = min(D[j] + 1, D[j - 1] + 1, prev + (at[i - 1] != bt[j - 1]))
                prev, D[j] = D[j], cur
        tot += max(n, m)
        err += D[m]
        print(f"{k}: tokens A {n} B {m} edits {D[m]}")
    a = 1 - err / max(tot, 1)
    print(f"agreement={a:.4f} over {len(B)} lines")
    print("STEP_A_GATE=PASS" if a >= 0.95 else "STEP_A_GATE=FAIL")


def run_solve(pa):
    Q = lm()
    rng = np.random.default_rng(SEED)
    st, ids = to_stream(parse(pa))
    key, best = solve(st, len(ids), Q, rng)
    dec = decode(st, key)
    gt = norm(open(GT, encoding="utf-8").read())
    acc = semiglobal_acc(dec, gt)
    null = [semiglobal_acc(decode(st, rng.permutation(key)), gt) for _ in range(100)]
    q99 = float(np.quantile(null, 0.99))
    inv = {v: k for k, v in ids.items()}
    print(f"n_tokens={int((st >= 0).sum())} n_ids={len(ids)} lm_score={best:.1f}")
    print("key: " + " ".join(f"{inv[i]}={ALPHA[key[i]]}" for i in range(len(ids))))
    print("decoded: " + dec)
    print(f"accuracy={acc:.4f} null_q99={q99:.4f} (100 permuted keys)")
    call = "KEY_RECOVERED" if acc >= CALL_RECOVERED and acc > q99 else "PARTIAL" if acc >= CALL_PARTIAL else "FAILED"
    print(f"CALL={call}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "fixture":
        fixture()
    elif mode == "agree":
        agree(sys.argv[2], sys.argv[3])
    elif mode == "solve":
        run_solve(sys.argv[2])
