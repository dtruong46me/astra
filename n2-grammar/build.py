"""Assemble index.html from src/template.html and the grammar data files."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
DATA = ["data1.js", "data2.js", "data3.js", "data4.js", "compare.js", "mindmap.js"]

template = open(os.path.join(SRC, "template.html"), encoding="utf-8").read()
data = "\n".join(open(os.path.join(SRC, f), encoding="utf-8").read() for f in DATA)
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(template.replace("/*DATA*/", data))
