"""Один вопрос сборке без сервера: python -m incidents.ask "вопрос"."""
import sys

from .app.loop import answer

if __name__ == "__main__":
    result = answer(" ".join(sys.argv[1:]))
    print(f"request_id: {result['request_id']}")
    print(f"шагов цикла: {result['steps']}")
    print(result["answer"])
