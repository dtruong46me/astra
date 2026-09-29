"""Build one self-contained HTML page per exam: exams/*.json + template.html -> dist/*.html.

siblings.json (optional) lists the published pages so each exam links to the others:
[{"id": "...", "label": "...", "url": "https://claude.ai/..."}]
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
TITLES = {"de13-kanji-n2": "Đề 13 Kanji N2", "de7-tuvung-n2": "Đề 7 Từ vựng N2"}


def main():
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    sib_file = ROOT / "siblings.json"
    siblings = json.loads(sib_file.read_text(encoding="utf-8")) if sib_file.exists() else []
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    for path in sorted((ROOT / "exams").glob("*.json")):
        exam = json.loads(path.read_text(encoding="utf-8"))
        assert all(len(q["o"]) == 4 and 1 <= q["a"] <= 4 for q in exam["qs"]), path
        html = (template
                .replace("__TITLE__", TITLES.get(exam["id"], exam["title"]))
                .replace("__DATA__", json.dumps(exam, ensure_ascii=False).replace("</", "<\\/"))
                .replace("__SIBLINGS__", json.dumps(siblings, ensure_ascii=False)))
        (out / f"{exam['id']}.html").write_text(html, encoding="utf-8")
        print("built", out / f"{exam['id']}.html", len(exam["qs"]), "questions")


if __name__ == "__main__":
    main()
