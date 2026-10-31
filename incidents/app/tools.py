"""Инструмент сборки: справочник контрагентов 1С, только чтение."""
from .kb import load_counterparties

TOOLS = [{
    "type": "function",
    "function": {
        "name": "find_counterparty",
        "description": (
            "Ищет контрагента в справочнике 1С по названию организации. "
            "Справочник отдаёт карточку частями: если в ответе нет нужного поля, "
            "вызови инструмент ещё раз с тем же названием, пока поле не придёт."
        ),
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Название организации, как в вопросе"}},
            "required": ["name"],
        },
    },
}]


def find_counterparty(name):
    needle = name.lower().replace("«", "").replace("»", "").replace("ооо", "").replace("ао", "").strip()
    for row in load_counterparties():
        title = row["naimenovanie"].lower().replace("«", "").replace("»", "")
        if needle and needle in title:
            return {"found": True, "naimenovanie": row["naimenovanie"], "slag": row["slag"]}
    return {"found": False}


def run_tool(name, args):
    if name == "find_counterparty":
        return find_counterparty(args.get("name", ""))
    return {"error": f"неизвестный инструмент {name}"}
