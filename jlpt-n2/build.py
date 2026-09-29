"""Build the single practice page: exams/*.json + catalog.json + app.html -> dist/index.html."""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent


def main():
    exams = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "exams").glob("*.json"))]
    exams.sort(key=lambda e: e["no"])
    for e in exams:
        assert all(len(q["o"]) == 4 and 1 <= q["a"] <= 4 for q in e["qs"]), e["title"]
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    dump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "app.html").read_text(encoding="utf-8")
    html = html.replace("__EXAMS__", dump(exams)).replace("__CATALOG__", dump(catalog))
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print("built dist/index.html with", len(exams), "exams:", ", ".join(e["title"] for e in exams))


if __name__ == "__main__":
    main()
