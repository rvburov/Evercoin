# project/backend/api/core/constants/currencies.py

CURRENCIES = [
    {
        "code": "RUB",
        "symbol": "₽",
        "name": "Russian Ruble",
        "name_ru": "Российский рубль",
        "decimal_places": 2
    },
    {
        "code": "USD",
        "symbol": "$",
        "name": "US Dollar",
        "name_ru": "Доллар США",
        "decimal_places": 2
    },
    {
        "code": "EUR",
        "symbol": "€",
        "name": "Euro",
        "name_ru": "Евро",
        "decimal_places": 2
    },
    {
        "code": "GBP",
        "symbol": "£",
        "name": "British Pound",
        "name_ru": "Фунт стерлингов",
        "decimal_places": 2
    },
    {
        "code": "JPY",
        "symbol": "¥",
        "name": "Japanese Yen",
        "name_ru": "Японская иена",
        "decimal_places": 0
    },
    {
        "code": "CNY",
        "symbol": "¥",
        "name": "Chinese Yuan",
        "name_ru": "Китайский юань",
        "decimal_places": 2
    },
    {
        "code": "CHF",
        "symbol": "CHF",
        "name": "Swiss Franc",
        "name_ru": "Швейцарский франк",
        "decimal_places": 2
    },
    {
        "code": "AED",
        "symbol": "د.إ",
        "name": "UAE Dirham",
        "name_ru": "Дирхам ОАЭ",
        "decimal_places": 2
    },
    {
        "code": "KZT",
        "symbol": "₸",
        "name": "Kazakhstani Tenge",
        "name_ru": "Казахстанский тенге",
        "decimal_places": 2
    },
    {
        "code": "UAH",
        "symbol": "₴",
        "name": "Ukrainian Hryvnia",
        "name_ru": "Украинская гривна",
        "decimal_places": 2
    }
]

def get_currency_by_code(code):
    """Получить валюту по коду ISO"""
    return next((curr for curr in CURRENCIES if curr["code"] == code.upper()), None)

def get_all_currencies():
    """Получить все валюты"""
    return CURRENCIES
