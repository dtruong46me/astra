"""Build the single practice page: exams/NN.json + app.html -> dist/index.html.

Each exam JSON carries `no` (folder number 1-20 on Drive), `folderLabel` (the category
in the Drive folder name), `file` (the PDF's own title) and `src` = Drive IDs of the
folder, the original PDF (goc) and the worked-solution PDF (chua).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
DRIVE_ROOT = "https://drive.google.com/drive/folders/1ujdYXmBtiFlgbPR2gAYXLPkJh9cVlEcv"


def main():
    exams = []
    for p in sorted((ROOT / "exams").glob("*.json")):
        e = json.loads(p.read_text(encoding="utf-8"))
        for i, q in enumerate(e["qs"], 1):
            assert len(q["o"]) == 4 and 1 <= q["a"] <= 4, (p.name, i)
            if "order" in q:
                assert sorted(q["order"]) == [1, 2, 3, 4], (p.name, i)
                assert q["order"][q["s"].replace("［★］", "*").replace("［　］", "_").count("_", 0, q["s"].replace("［★］", "*").replace("［　］", "_").index("*"))] == q["a"], (p.name, i)
        s = e.pop("src")
        e["source"] = {
            "folder": f"https://drive.google.com/drive/folders/{s['folder']}",
            "goc": f"https://drive.google.com/file/d/{s['goc']}/view",
            "chua": f"https://drive.google.com/file/d/{s['chua']}/view",
        }
        e["series"] = f"DORA Nihongo · Đề {e['no']} · {e['folderLabel']} N5–N2 trúng tủ"
        exams.append(e)
    exams.sort(key=lambda e: e["no"])
    have = {e["no"] for e in exams}
    catalog = {"root": DRIVE_ROOT, "slots": [{"no": n, "cat": None, "folder": DRIVE_ROOT} for n in range(1, 21) if n not in have]
               + [{"no": e["no"]} for e in exams]}
    catalog["slots"].sort(key=lambda s: s["no"])
    dump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "app.html").read_text(encoding="utf-8")
    html = html.replace("__EXAMS__", dump(exams)).replace("__CATALOG__", dump(catalog))
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"built dist/index.html: {len(exams)} exams, {sum(len(e['qs']) for e in exams)} questions")


if __name__ == "__main__":
    main()
