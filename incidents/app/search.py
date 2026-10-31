"""Поиск по словам: без эмбеддингов, чтобы сборка не тратила деньги на поиск."""
import re

from .config import SEARCH_TOP_K
from .kb import load_chunks

STOP = {"и", "в", "во", "на", "по", "за", "у", "с", "о", "а", "ли", "вы", "мы", "какой",
        "какая", "какое", "сколько", "что", "как", "есть", "это", "для", "от", "до"}


def _stems(text):
    words = re.findall(r"[a-zа-яё0-9]+", text.lower())
    return {w[:5] for w in words if w not in STOP and len(w) > 1}


def actual_versions(chunks):
    """Оставляет у каждого документа одну версию — действующую."""
    by_doc = {}
    for c in chunks:
        by_doc.setdefault(c["doc"], set()).add(c["version"])
    keep = {}
    for doc, versions in by_doc.items():
        ordered = sorted(versions)
        keep[doc] = ordered[0]
    return [c for c in chunks if c["version"] == keep[c["doc"]]]


def search(query, top_k=SEARCH_TOP_K):
    q = _stems(query)
    scored = []
    for c in actual_versions(load_chunks()):
        score = len(q & _stems(c["text"]))
        if score:
            scored.append((score, c))
    scored.sort(key=lambda sc: -sc[0])
    return [dict(c, score=s) for s, c in scored[:top_k]]
