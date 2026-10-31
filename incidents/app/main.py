"""Сервис сборки: POST /ask {"question": "..."} → ответ и request_id."""
import re
from typing import Optional

from fastapi import FastAPI, Header, Response
from pydantic import BaseModel

from .loop import answer

app = FastAPI(title="Сборка агента к уроку 17")


class Ask(BaseModel):
    question: str


# Входящий id идёт в имя файла трейса, поэтому берём только безопасные символы.
_SAFE_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")


@app.post("/ask")
def ask(body: Ask, response: Response, x_request_id: Optional[str] = Header(default=None)):
    # Пришёл X-Request-Id — он и есть request_id запроса; нет или некорректный — новый.
    rid = x_request_id if x_request_id and _SAFE_ID.fullmatch(x_request_id) else None
    result = answer(body.question, rid)
    response.headers["X-Request-Id"] = result["request_id"]
    return result
