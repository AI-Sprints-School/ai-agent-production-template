"""Выгрузка трейса текстом.

python -m incidents.export_trace <request_id>                  — всё дерево
python -m incidents.export_trace <request_id> --only search,tool — корень и спаны,
    имя которых начинается с перечисленного; для отчёта, чтобы он не разрастался.
"""
import argparse
import json

from .app.config import TRACES


def load(request_id):
    path = TRACES / f"{request_id}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def render(spans, only=None):
    children = {}
    for s in spans:
        children.setdefault(s["parent_id"], []).append(s)
    for items in children.values():
        items.sort(key=lambda s: s["start"])
    lines = []

    def walk(parent, depth):
        for s in children.get(parent, []):
            shown = only is None or s["parent_id"] is None or s["name"].startswith(tuple(only))
            if shown:
                lines.append(f"{'  ' * depth}{s['name']}  [{s['kind']}]  {s['duration_ms']} мс  {s['status']}")
                for key, value in s["attrs"].items():
                    lines.append(f"{'  ' * depth}  · {key}: {value}")
            walk(s["span_id"], depth + 1)

    walk(None, 0)
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    parser.add_argument("--only", help="имена спанов через запятую: search,context,generation,tool")
    args = parser.parse_args()
    only = [x.strip() for x in args.only.split(",")] if args.only else None
    print(f"trace {args.request_id}")
    print(render(load(args.request_id), only))
