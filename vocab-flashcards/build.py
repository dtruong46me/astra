"""Inline every data/vocab-*.json file into template.html -> index.html (the published artifact page)."""
import glob, json, os

here = os.path.dirname(os.path.abspath(__file__))
vocab = []
for path in sorted(glob.glob(os.path.join(here, "data", "vocab-*.json"))):
    vocab += json.load(open(path, encoding="utf-8"))
vocab.sort(key=lambda v: v["id"])
# jlpt.json: {id: number of times the word appeared in JLPT N2 2010-2024}; stored as "jl" on each word.
jl = json.load(open(os.path.join(here, "data", "jlpt.json"), encoding="utf-8"))
for v in vocab:
    if str(v["id"]) in jl: v["jl"] = jl[str(v["id"])]
ids = [v["id"] for v in vocab]
assert len(ids) == len(set(ids)), "duplicate ids"

tpl = open(os.path.join(here, "template.html"), encoding="utf-8").read()
data = json.dumps(vocab, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = tpl.replace("/*__VOCAB__*/[]", data)
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(out)
print(f"{len(vocab)} words ({sum(1 for v in vocab if v['l'])} from the book, {sum(1 for v in vocab if not v['l'])} exam-only, {sum(1 for v in vocab if 'jl' in v)} tagged JLPT), {len(out)//1024} KB")
