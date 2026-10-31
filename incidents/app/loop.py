"""Агентный цикл сборки: поиск → контекст → модель ⇄ инструмент."""
import json

import httpx

from . import config
from .search import search
from .tools import TOOLS, run_tool
from .trace import new_request_id, request, span

SYSTEM = (
    "Ты отвечаешь сотрудникам ООО «Полярис-Снаб» по фрагментам базы знаний ниже. "
    "Отвечай только по фрагментам. Если ответа во фрагментах нет — так и скажи. "
    "Для вопросов о контрагентах пользуйся инструментом find_counterparty. "
    "В конце ответа укажи id фрагментов, на которые опирался."
)


def call_model(messages):
    resp = httpx.post(
        f"{config.LLM_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
        json={"model": config.LLM_MODEL, "messages": messages, "tools": TOOLS},
        timeout=config.TIMEOUT_S,
    )
    resp.raise_for_status()
    return resp.json(), resp.headers.get("x-request-id", "")


def answer(question, request_id=None):
    request_id = request_id or new_request_id()
    with request(request_id) as root:
        root["question"] = question
        with span("search", "retrieval", query=question) as s:
            found = search(question)
            s["found"] = [f"{c['id']} (v {c['version']}, score {c['score']})" for c in found]
        with span("context", "context", chunks_found=len(found)) as s:
            used = found[: config.CONTEXT_CHUNKS]
            s["chunks_used"] = [c["id"] for c in used]
            context = "\n".join(f"[{c['id']}] {c['text']}" for c in used)
        messages = [
            {"role": "system", "content": SYSTEM + "\n\nФрагменты:\n" + context},
            {"role": "user", "content": question},
        ]
        text, steps = "", 0
        for steps in range(1, config.MAX_STEPS + 1):
            with span(f"generation #{steps}", "generation", model=config.LLM_MODEL) as g:
                data, gw_id = call_model(messages)
                msg = data["choices"][0]["message"]
                usage = data.get("usage", {})
                g.update(gateway_request_id=gw_id, created=data.get("created"),
                         prompt_tokens=usage.get("prompt_tokens"),
                         completion_tokens=usage.get("completion_tokens"),
                         cost=usage.get("cost"), finish_reason=data["choices"][0].get("finish_reason"),
                         tool_calls=[c["function"]["name"] for c in msg.get("tool_calls") or []],
                         output=msg.get("content") or "")
            calls = msg.get("tool_calls") or []
            if not calls:
                text = msg.get("content") or ""
                break
            messages.append({"role": "assistant", "content": msg.get("content"), "tool_calls": calls})
            for call in calls:
                args = json.loads(call["function"]["arguments"] or "{}")
                with span(f"tool:{call['function']['name']}", "tool", args=args) as t:
                    result = run_tool(call["function"]["name"], args)
                    t["result"] = result
                messages.append({"role": "tool", "tool_call_id": call["id"],
                                 "content": json.dumps(result, ensure_ascii=False)})
        else:
            text = "Не удалось ответить: исчерпан лимит шагов. Вопрос передан оператору."
        root.update(answer=text, steps=steps)
    return {"request_id": request_id, "answer": text, "steps": steps}
