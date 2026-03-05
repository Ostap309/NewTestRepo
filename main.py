import json

REQUIRED_ROOT_CATEGORY = "Инвентарь"
IGNORED_CATEGORIES = ["Потерянное"]
REQUIRED_QUANTITY_KEYWORD = "Количество: "
REQUIRED_COST_KEYWORD = "Стоимость: "
REQUIRED_WEIGHT_KEYWORD = "Вес: "
EMPTY_LOGS = False
DEFAULT_LOGS = {"cost": False, "weight": True, "quantity": False}
MAX_COLUMN_WIDTH = 30
NONE_REPLACER = "??"

with open("input.json", "r", encoding="utf-8") as f:
    # Загружаем данные из файла в переменную
    data = json.loads(json.load(f)["campaignsData"])

total_cost = {"ММ": 0, "СМ": 0, "ЭМ": 0, "ЗМ": 0, "ПМ": 0}
total_weight = 0
total_quantity = 0

# subjects: category_id, fullDescription, description
# categories: parentCategory_id, name, id

inventory_id: int = next((c for c in data["categories"] if c["name"] == REQUIRED_ROOT_CATEGORY))["id"]
inventory_categories_ids: list[int] = [inventory_id]

# Поиск категорий входящих в раздел Инвентарь
for c in data["categories"]:
    if c["name"] not in IGNORED_CATEGORIES and c["parentCategory_id"] in inventory_categories_ids:
        inventory_categories_ids.append(c["id"])


def rep(inp):
    if inp != None:
        return inp

    return NONE_REPLACER


def find_quantity(text: str, keyword: str, default, need_unit: bool = False) -> list:
    start_pos = text.find(keyword)
    if start_pos != -1:
        value_part = text[start_pos + len(keyword):]
        parts = value_part.split(maxsplit=2)[:2]
        result = [None, None]

        if not parts:
            return result + ["EMPTY"]

        if parts[0].isdigit():
            result[0] = int(parts[0])
        if need_unit and len(parts) == 2 and parts[1] in total_cost.keys():
            result[1] = parts[1]

        if not result[0] or (not result[1] and need_unit):
            return result + ["EMPTY"]

        return result + ["FULL"]

    # Возврат значения по умолчанию
    return default + ["DEFAULT"]


if EMPTY_LOGS or DEFAULT_LOGS:
    print(f"ТРЕБ. ЗАПОЛНЕНИЕ: |{'Название'.center(MAX_COLUMN_WIDTH)}|    Цена    |   Вес   |  Кол-во  |     Тип     |")

for s in data["subjects"]:
    if s["category_id"] in inventory_categories_ids:
        cost = find_quantity(s["fullDescription"], REQUIRED_COST_KEYWORD, [0, "ММ"], need_unit=True)
        weight = find_quantity(s["fullDescription"], REQUIRED_WEIGHT_KEYWORD, [0, None])
        quantity = find_quantity(s["description"], REQUIRED_QUANTITY_KEYWORD, [1, None])

        if EMPTY_LOGS and any([cost[2] == "EMPTY", weight[2] == "EMPTY", quantity[2] == "EMPTY"]):
            print(
                f"                  |{s['name'].center(MAX_COLUMN_WIDTH)}|{(str(rep(cost[0])) + ' ' + rep(cost[1])).center(12)}|{str(rep(weight[0])).center(9)}|{str(rep(quantity[0])).center(10)}|{'EMPTY'.center(13)}|")
        elif any([cost[2] == "DEFAULT" and DEFAULT_LOGS["cost"], weight[2] == "DEFAULT" and DEFAULT_LOGS["weight"],
                  quantity[2] == "DEFAULT" and DEFAULT_LOGS["quantity"]]):
            try:
                print(
                    f"                  |{s['name'].center(MAX_COLUMN_WIDTH)}|{(str(cost[0]) + ' ' + cost[1]).center(12)}|{str(weight[0]).center(9)}|{str(quantity[0]).center(10)}|{'DEFAULT'.center(13)}|")
            except Exception:
                print("-----!--->", s["name"])
        if cost[2] != "EMPTY" and quantity[2] != "EMPTY":
            total_cost[cost[1]] += cost[0] * quantity[0]
        if weight[2] != "EMPTY" and quantity[2] != "EMPTY":
            total_weight += weight[0] * quantity[0]
        if quantity[2] != "EMPTY":
            total_quantity += quantity[0]

print(f"""
<=============ИТОГ=============>
    Категория: {REQUIRED_ROOT_CATEGORY}
    Общая {REQUIRED_COST_KEYWORD}{total_cost}
    Приведенная {REQUIRED_COST_KEYWORD}{total_cost["ММ"] * 0.01 + total_cost["СМ"] * 0.1 + total_cost["ЭМ"] * 0.5 + total_cost["ЗМ"] + total_cost["ПМ"] * 10} ЗМ
    Общий {REQUIRED_WEIGHT_KEYWORD}{total_weight} фнт (или {total_weight * 0.4536} кг)
    Общее {REQUIRED_QUANTITY_KEYWORD}{total_quantity} предметов
""")
