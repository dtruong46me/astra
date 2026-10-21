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

# chains-*.txt: word-chain trees (熟語しりとり), see the header of data/chains-1.txt for the format.
# Each node becomes [deck id, kids] for words in the deck, or [[w, r, level, hv, vi], kids] for the rest.
by_word = {}
for v in vocab: by_word.setdefault(v["w"], v)
chains, seen, errs = [], {}, []
def check(ok, msg):
    if not ok: errs.append(msg)
    return ok
for path in sorted(glob.glob(os.path.join(here, "data", "chains-*.txt"))):
    stack = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if not line.strip() or line.startswith("#"): continue
        depth = (len(line) - len(line.lstrip(" "))) // 2
        head, _, vi = line.strip().partition(" | ")
        f = head.split(" ")
        where = f"{os.path.basename(path)}:{n} {f[0]}"
        if len(f) == 1:
            if not check(f[0] in by_word, f"{where}: not in the deck, needs reading/level/Hán Việt/meaning"): continue
            ref = by_word[f[0]]["id"]
        else:
            check(len(f) >= 4 and f[2] in "12345" and vi, f"{where}: bad line")
            if f[0] in by_word: check(False, f"{where}: in the deck (No.{by_word[f[0]]['id']}), list the word alone")
            ref = [f[0], f[1], int(f[2]), " ".join(f[3:]), vi]
        node = [ref, []]
        assert depth <= len(stack), f"{where}: indentation jumps a level"
        del stack[depth:]
        if stack:
            parent = stack[-1][0]
            pw = parent[0] if isinstance(parent, list) else next(v for v in vocab if v["id"] == parent)["w"]
            check(pw[-1] == f[0][0], f"{where}: does not start with the last kanji of {pw}")
            stack[-1][1].append(node)
        else:
            chains.append(node)
        check(f[0] not in seen, f"{where}: already used at {seen.get(f[0])}")
        seen.setdefault(f[0], where)
        stack.append(node)
assert not errs, "\n".join(errs)
nodes = len(seen)
in_deck = sum(1 for w in seen if w in by_word)

tpl = open(os.path.join(here, "template.html"), encoding="utf-8").read()
data = json.dumps(vocab, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = tpl.replace("/*__VOCAB__*/[]", data)
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(out)
# chains.html: the separate word-chain page, carrying the card data of every deck word it uses.
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
deck_ids = set()
def collect(n):
    if isinstance(n[0], int): deck_ids.add(n[0])
    for k in n[1]: collect(k)
for c in chains: collect(c)
deck = {v["id"]: {k: v[k] for k in ("w", "r", "hv", "vi", "l", "s", "jl") if k in v} for v in vocab if v["id"] in deck_ids}
ctpl = open(os.path.join(here, "chains-template.html"), encoding="utf-8").read()
cout = ctpl.replace("/*__CHAINS__*/[]", js(chains)).replace("/*__DECK__*/{}", js(deck))
open(os.path.join(here, "chains.html"), "w", encoding="utf-8").write(cout)
print(f"{len(vocab)} words ({sum(1 for v in vocab if v['l'])} from the book, {sum(1 for v in vocab if not v['l'])} exam-only, {sum(1 for v in vocab if 'jl' in v)} tagged JLPT), {len(out)//1024} KB; {len(chains)} chains ({nodes} words, {in_deck} in the deck), {len(cout)//1024} KB")
