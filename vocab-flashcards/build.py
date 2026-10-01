"""Inline every data/vocab-*.json file into template.html -> index.html (the published artifact page)."""
import glob, json, os

here = os.path.dirname(os.path.abspath(__file__))
vocab = []
for path in sorted(glob.glob(os.path.join(here, "data", "vocab-*.json"))):
    vocab += json.load(open(path, encoding="utf-8"))
vocab.sort(key=lambda v: v["id"])
ids = [v["id"] for v in vocab]
assert len(ids) == len(set(ids)), "duplicate ids"

tpl = open(os.path.join(here, "template.html"), encoding="utf-8").read()
data = json.dumps(vocab, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = tpl.replace("/*__VOCAB__*/[]", data)
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(out)
print(f"{len(vocab)} words, lessons {vocab[0]['l']}-{vocab[-1]['l']}, {len(out)//1024} KB")
