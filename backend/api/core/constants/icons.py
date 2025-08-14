# icons.py
CATEGORY_ICONS = [
    "food",
    "transport",
    "shopping",
    "home",
    "health",
    "education",
    "entertainment",
    "salary"
]

WALLET_ICONS = [
    "cash",
    "card",
    "bank",
    "savings",
    "investment"
]

def get_all_icons():
    """Возвращает словарь с разделенными иконками"""
    return {
        "categories": CATEGORY_ICONS,
        "wallets": WALLET_ICONS,
        "base_path": "static/icons/"
    }

def get_icon_path(icon_name):
    """Генерирует путь к иконке"""
    if icon_name in CATEGORY_ICONS:
        return f"static/icons/categories/{icon_name}.svg"
    elif icon_name in WALLET_ICONS:
        return f"static/icons/wallets/{icon_name}.svg"
    return None
