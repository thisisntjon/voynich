"""s115-A1b: independent second labeller (different architecture) for the A1 image codebook.

Blind: reads only data/anchor_A1/CODEBOOK.md (category definitions), the stem column of
data/anchor_A1/images.tsv, and the masked images data/anchor_A1/masked/<stem>.png.
Never reads transliterations, labels, results or any other column of images.tsv.

Model: local Ollama vision model (default qwen2.5vl:7b), temperature 0, seed 115, format=json.
Outputs (never overwritten):
  data/anchor_A1b/raw/<stem>.json   full Ollama response per image
  data/anchor_A1b/prompt.txt        the exact text prompt (same for every image)
  data/anchor_A1b/labels_gemma.tsv  A1 column order, one row per image; levels as written by the model
                                    (missing key -> MISSING; invalid levels kept verbatim)
Usage: python -I tools/s115_a1b_label.py [--model NAME] [--limit N]
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A1 = os.path.join(ROOT, "data", "anchor_A1")
OUT = os.path.join(ROOT, "data", "anchor_A1b")
RAW = os.path.join(OUT, "raw")
CODEBOOK_SHA = "8b72197f2dcdfae86c48a0739ea56031eab1d4b5775907a128f7c40df81e8f62"
COLS = ["PT", "P_plants", "P_root", "P_leafshape", "P_leafcount", "P_flower", "P_habit",
        "J_shape", "J_count", "J_fragcount", "J_fragtype", "C_centre", "C_animal", "C_figures",
        "C_rings", "C_diagrams", "C_rays", "B_pools", "B_figures", "B_tubes", "note"]
URL = "http://localhost:11434/api/generate"


def codebook_definitions():
    raw = open(os.path.join(A1, "CODEBOOK.md"), "rb").read()
    if hashlib.sha256(raw).hexdigest() != CODEBOOK_SHA:
        sys.exit("CODEBOOK.md hash mismatch; refusing to run")
    text = raw.decode("utf-8")
    start = text.index("## Unit")
    end = text.index("## Agreement and keep rules")
    body = text[start:end]
    # drop the TSV output-row instructions; the model answers in JSON instead
    o0 = body.index("## Output row")
    o1 = body.index("## C0.")
    return body[:o0] + body[o1:]


def build_prompt():
    keys = ", ".join('"%s"' % c for c in COLS)
    return (
        "You are labelling one scanned manuscript page from its drawings only, using a fixed codebook.\n"
        "Writing and writing-like marks have been painted out or must be ignored; judge the drawing only.\n"
        "Do not try to read or interpret any writing.\n\n"
        "CODEBOOK (category definitions and allowed levels):\n\n"
        + codebook_definitions()
        + "\nRules: every key takes exactly one level token from its list in the codebook, spelled exactly "
        "as shown (for example 1-4, 3+, PRESENT). Use NA when the category does not apply "
        "(the page type is not the one the category belongs to, or its stated condition is not met). "
        "note is free text of at most 12 words, or -.\n\n"
        "Answer with ONE JSON object and nothing else, with exactly these keys in this order: "
        + keys + ".\n"
    )


def stems():
    out = []
    with open(os.path.join(A1, "images.tsv"), encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        i = header.index("stem")
        for line in f:
            line = line.rstrip("\r\n")
            if line:
                out.append(line.split("\t")[i])
    return out


def call(model, prompt, img_path):
    b64 = base64.b64encode(open(img_path, "rb").read()).decode()
    req = {"model": model, "prompt": prompt, "images": [b64], "stream": False, "format": "json",
           "keep_alive": "10m",
           "options": {"temperature": 0, "seed": 115, "top_k": 1, "num_ctx": 8192, "num_predict": 600}}
    r = urllib.request.Request(URL, json.dumps(req).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=900))


def clean(v):
    if v is None:
        return "MISSING"
    s = v if isinstance(v, str) else json.dumps(v)
    s = " ".join(s.split())
    return s if s else "EMPTY"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5vl:7b")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    prompt = build_prompt()
    pp = os.path.join(OUT, "prompt.txt")
    if os.path.exists(pp):
        if open(pp, encoding="utf-8").read() != prompt:
            sys.exit("prompt.txt exists and differs; refusing")
    else:
        with open(pp, "w", encoding="utf-8", newline="\n") as f:
            f.write(prompt)
    todo = stems()
    if a.limit:
        todo = todo[: a.limit]
    t0 = time.time()
    for k, s in enumerate(todo):
        rp = os.path.join(RAW, s + ".json")
        if os.path.exists(rp):
            continue  # resume; never overwrite
        img = os.path.join(A1, "masked", s + ".png")
        for attempt in range(3):
            try:
                resp = call(a.model, prompt, img)
                break
            except Exception as e:  # transient server error
                print("retry", s, attempt, e, flush=True)
                time.sleep(10)
        else:
            sys.exit("failed on " + s)
        resp.pop("context", None)
        resp["stem"] = s
        with open(rp + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            json.dump(resp, f, ensure_ascii=False, indent=1)
        os.replace(rp + ".tmp", rp)
        print("%d/%d %s %.0fs" % (k + 1, len(todo), s, time.time() - t0), flush=True)
    if a.limit:
        return
    lp = os.path.join(OUT, "labels_gemma.tsv")
    if os.path.exists(lp):
        sys.exit("labels_gemma.tsv exists; not overwriting")
    rows = ["stem\t" + "\t".join(COLS)]
    bad = 0
    for s in todo:
        resp = json.load(open(os.path.join(RAW, s + ".json"), encoding="utf-8"))
        try:
            obj = json.loads(resp.get("response", ""))
            if not isinstance(obj, dict):
                raise ValueError
        except Exception:
            obj = {}
            bad += 1
        vals = [clean(obj.get(c)) for c in COLS]
        if vals[-1] in ("MISSING", "EMPTY"):
            vals[-1] = "-"
        rows.append(s + "\t" + "\t".join(vals))
    with open(lp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rows) + "\n")
    print("wrote", lp, "rows", len(todo), "unparseable", bad)


if __name__ == "__main__":
    main()
