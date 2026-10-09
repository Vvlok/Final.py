"""Расчёт приблизительного углеродного следа человека за год.

Коэффициенты округлены и сильно упрощены: калькулятор показывает порядок
величин и помогает понять, где можно сократить выбросы, а не даёт точный учёт.
Все значения в килограммах CO₂-эквивалента.
"""

# --- Коэффициенты ---
CAR_KG_PER_KM = 0.19          # легковой автомобиль, на 1 км
PUBLIC_KG_PER_KM = 0.06       # автобус, трамвай, метро, поезд, на 1 пассажиро-км (усреднённо)
FLIGHT_SHORT_KG = 250         # один короткий перелёт (до ~3 часов)
FLIGHT_LONG_KG = 1000         # один дальний перелёт
ELECTRICITY_KG_PER_KWH = 0.45 # среднемировой «вес» одной кВт·ч

DIET_TONS = {                 # выбросы от питания за год, т
    "meat_daily": 2.5,
    "meat_sometimes": 1.9,
    "vegetarian": 1.5,
    "vegan": 1.1,
}
DIET_NAMES = {
    "meat_daily": "Мясо почти каждый день",
    "meat_sometimes": "Мясо несколько раз в неделю",
    "vegetarian": "Вегетарианское питание",
    "vegan": "Растительное питание",
}

WASTE_TONS_SORTED = 0.3
WASTE_TONS_NOT_SORTED = 0.6

WORLD_AVERAGE_TONS = 4.7      # примерно, т CO₂ на человека в год
TARGET_TONS = 2.0             # ориентир на середину века


def _number(value, default=0.0, maximum=100000):
    """Безопасно превращает текст из формы в число (пустое или кривое = 0)."""
    try:
        number = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default
    if number < 0:
        return default
    return min(number, maximum)


def calculate(form):
    """Принимает данные формы (request.form) и возвращает словарь с итогами."""
    car_km_week = _number(form.get("car_km"))
    public_km_week = _number(form.get("public_km"))
    flights_short = _number(form.get("flights_short"), maximum=200)
    flights_long = _number(form.get("flights_long"), maximum=200)
    kwh_month = _number(form.get("kwh"))
    diet = form.get("diet", "meat_sometimes")
    if diet not in DIET_TONS:
        diet = "meat_sometimes"
    sorts_waste = form.get("sort_waste") == "on"

    parts = {
        "Автомобиль": car_km_week * 52 * CAR_KG_PER_KM / 1000,
        "Общественный транспорт": public_km_week * 52 * PUBLIC_KG_PER_KM / 1000,
        "Перелёты": (flights_short * FLIGHT_SHORT_KG + flights_long * FLIGHT_LONG_KG) / 1000,
        "Электричество": kwh_month * 12 * ELECTRICITY_KG_PER_KWH / 1000,
        "Питание": DIET_TONS[diet],
        "Отходы": WASTE_TONS_SORTED if sorts_waste else WASTE_TONS_NOT_SORTED,
    }
    total = sum(parts.values())

    # для столбиков: доля каждой части от самой большой
    biggest_value = max(parts.values()) or 1
    breakdown = [
        {
            "name": name,
            "tons": round(value, 2),
            "width": round(value / biggest_value * 100),
        }
        for name, value in sorted(parts.items(), key=lambda item: item[1], reverse=True)
    ]

    biggest_name = breakdown[0]["name"]
    return {
        "total": round(total, 1),
        "breakdown": breakdown,
        "biggest": biggest_name,
        "tips": TIPS[biggest_name],
        "world_average": WORLD_AVERAGE_TONS,
        "target": TARGET_TONS,
        "vs_average": round(total / WORLD_AVERAGE_TONS * 100),
        "trees": round(total * 1000 / 22),  # одно дерево поглощает порядка 22 кг CO₂ в год
        "verdict": verdict(total),
        "values": {
            "car_km": car_km_week, "public_km": public_km_week,
            "flights_short": flights_short, "flights_long": flights_long,
            "kwh": kwh_month, "diet": diet, "sort_waste": sorts_waste,
        },
    }


def verdict(total):
    if total < TARGET_TONS:
        return "Отлично! Твой след уже ниже ориентира на середину века."
    if total < WORLD_AVERAGE_TONS:
        return "Ниже среднего по миру, но до ориентира в 2 т ещё есть куда стремиться."
    return "Выше среднего по миру. Хорошая новость в том, что есть из чего сокращать."


# Советы для самой «тяжёлой» категории
TIPS = {
    "Автомобиль": [
        "Короткие поездки заменяй пешком или велосипедом",
        "Ездить вместе: одна машина на четверых даёт в четыре раза меньше выбросов на человека",
        "Если можно, выбирай общественный транспорт",
    ],
    "Общественный транспорт": [
        "Это уже один из лучших вариантов, так что здесь выбросы невелики",
        "Для коротких расстояний попробуй ходить пешком",
    ],
    "Перелёты": [
        "Один дальний перелёт может «весить» больше, чем весь год пользования транспортом в городе",
        "Для близких расстояний выбирай поезд или автобус",
        "Летай реже, но дольше: одна длинная поездка вместо нескольких коротких",
    ],
    "Электричество": [
        "Выключай свет и технику, которой не пользуешься",
        "Заменяй лампы на светодиодные, выбирай технику с высоким классом энергоэффективности",
        "Если есть выбор, подключайся к «зелёной» электроэнергии",
    ],
    "Питание": [
        "Заменяй мясо растительными блюдами хотя бы несколько раз в неделю",
        "Покупай столько еды, сколько реально съешь",
        "Местные сезонные продукты часто выгоднее для климата",
    ],
    "Отходы": [
        "Сортируй отходы",
        "Покупай меньше одноразового и ремонтируй вместо замены",
        "Компост и меньше выброшенной еды уменьшают метан со свалок",
    ],
}
