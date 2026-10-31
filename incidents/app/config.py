"""Настройки сборки. Адрес, модель и ключ — только из окружения."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
BUILD = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

LLM_BASE_URL = os.environ["LLM_BASE_URL"]
LLM_MODEL = os.environ["LLM_MODEL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]

FIXTURES = BUILD / "fixtures"
TRACES = BUILD / "traces"

SEARCH_TOP_K = 6        # сколько фрагментов возвращает поиск
CONTEXT_CHUNKS = 1      # сколько найденных фрагментов уходит в модель
MAX_STEPS = 6           # лимит шагов агентного цикла
TIMEOUT_S = 60
