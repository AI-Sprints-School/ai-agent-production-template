"""Трейс в файл: одна строка JSON на спан, файл на запрос — traces/<request_id>.jsonl."""
import contextvars
import json
import time
import uuid
from contextlib import contextmanager

from .config import TRACES

_request_id = contextvars.ContextVar("request_id", default=None)
_parent = contextvars.ContextVar("parent_span", default=None)

CUT = 400


def _short(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= CUT else text[:CUT] + f"… (+{len(text) - CUT})"


def new_request_id():
    return "inc-" + uuid.uuid4().hex[:12]


@contextmanager
def request(request_id):
    token = _request_id.set(request_id)
    TRACES.mkdir(exist_ok=True)
    (TRACES / f"{request_id}.jsonl").write_text("", encoding="utf-8")
    try:
        with span("request", "request") as root:
            yield root
    finally:
        _request_id.reset(token)


@contextmanager
def span(name, kind, **attrs):
    record = {"span_id": uuid.uuid4().hex[:8], "parent_id": _parent.get(), "name": name,
              "kind": kind, "attrs": {k: _short(v) for k, v in attrs.items()}}
    token = _parent.set(record["span_id"])
    start = time.perf_counter()
    record["start"] = round(time.time(), 3)
    status = "ok"
    try:
        yield record["attrs"]
    except Exception as e:
        status = f"error: {type(e).__name__}"
        raise
    finally:
        _parent.reset(token)
        record["duration_ms"] = round((time.perf_counter() - start) * 1000)
        record["status"] = status
        record["attrs"] = {k: _short(v) for k, v in record["attrs"].items()}
        with open(TRACES / f"{_request_id.get()}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
