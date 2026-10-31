"""Проверка сборки: python -m incidents.check.

Вопросы, на которые сборка отвечает верно. Прогон до и после правки
показывает, что правка не сломала то, что работало.
"""
import json
import re

from .app.config import FIXTURES
from .app.loop import answer

def norm(text):
    """Нижний регистр, ё → е, без пробелов любого вида: «1 180» и «1180» совпадают."""
    return re.sub(r"\s+", "", text.lower().replace("ё", "е"))


def matches(answer_text, expect):
    """Каждый элемент expect — строка или список вариантов, годится любой из них."""
    got = norm(answer_text)
    return all(any(norm(v) in got for v in ([e] if isinstance(e, str) else e)) for e in expect)


if __name__ == "__main__":
    cases = json.loads((FIXTURES / "control.json").read_text(encoding="utf-8"))
    ok = 0
    for i, case in enumerate(cases, 1):
        result = answer(case["q"])
        hit = matches(result["answer"], case["expect"])
        ok += hit
        print(f"{i}. {'верно ' if hit else 'НЕВЕРНО'}  шагов {result['steps']}  "
              f"{result['request_id']}  {case['q']}")
    print(f"итого: {ok} из {len(cases)}")
    raise SystemExit(0 if ok == len(cases) else 1)
