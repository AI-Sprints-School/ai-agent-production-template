"""База знаний сборки: строки прайса и пункты регламентов как фрагменты."""
import csv
import json
import re

from .config import FIXTURES


def _price_chunks():
    versions = json.loads((FIXTURES / "versions.json").read_text(encoding="utf-8"))["prays"]
    chunks = []
    for v in versions:
        with open(FIXTURES / v["file"], encoding="utf-8") as f:
            for row in csv.DictReader(f):
                chunks.append({
                    "id": f"{v['file']}:{row['artikul']}",
                    "doc": "prays",
                    "version": v["month"],
                    "text": (f"Прайс {v['month']}: {row['artikul']} {row['naimenovanie']}, "
                             f"{row['edinica']}, цена {row['cena']} ₽"),
                })
    return chunks


def _reglament_chunks():
    chunks = []
    for path in sorted(FIXTURES.glob("reglament-*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        for m in re.finditer(r"^(\d+)\. (.+?)(?=^\d+\. |\Z)", text, re.S | re.M):
            chunks.append({
                "id": f"{path.name}:п.{m.group(1)}",
                "doc": path.stem,
                "version": "2026-03-01",
                "text": f"{title}, п. {m.group(1)}: {' '.join(m.group(2).split())}",
            })
    return chunks


def load_chunks():
    return _price_chunks() + _reglament_chunks()


def load_counterparties():
    with open(FIXTURES / "kontragenty.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))
