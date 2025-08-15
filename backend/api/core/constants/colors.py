# project/backend/api/categories/core/constants/colors.py
COLORS = [
    {"id": "red", "hex": "#FF5252", "name": "Red", "name_ru": "Красный"},
    {"id": "pink", "hex": "#FF4081", "name": "Pink", "name_ru": "Розовый"},
    {"id": "purple", "hex": "#E040FB", "name": "Purple", "name_ru": "Фиолетовый"},
    {"id": "deep_purple", "hex": "#7C4DFF", "name": "Deep Purple", "name_ru": "Темно-фиолетовый"},
    {"id": "indigo", "hex": "#536DFE", "name": "Indigo", "name_ru": "Индиго"},
    {"id": "blue", "hex": "#448AFF", "name": "Blue", "name_ru": "Синий"},
    {"id": "light_blue", "hex": "#40C4FF", "name": "Light Blue", "name_ru": "Голубой"},
    {"id": "cyan", "hex": "#18FFFF", "name": "Cyan", "name_ru": "Бирюзовый"},
    {"id": "teal", "hex": "#64FFDA", "name": "Teal", "name_ru": "Морской волны"},
    {"id": "green", "hex": "#69F0AE", "name": "Green", "name_ru": "Зеленый"},
    {"id": "light_green", "hex": "#B2FF59", "name": "Light Green", "name_ru": "Светло-зеленый"},
    {"id": "lime", "hex": "#EEFF41", "name": "Lime", "name_ru": "Лаймовый"},
    {"id": "yellow", "hex": "#FFFF00", "name": "Yellow", "name_ru": "Желтый"},
    {"id": "amber", "hex": "#FFD740", "name": "Amber", "name_ru": "Янтарный"},
    {"id": "orange", "hex": "#FFAB40", "name": "Orange", "name_ru": "Оранжевый"},
    {"id": "deep_orange", "hex": "#FF6E40", "name": "Deep Orange", "name_ru": "Темно-оранжевый"},
    {"id": "brown", "hex": "#BCAAA4", "name": "Brown", "name_ru": "Коричневый"},
    {"id": "grey", "hex": "#9E9E9E", "name": "Grey", "name_ru": "Серый"},
    {"id": "blue_grey", "hex": "#78909C", "name": "Blue Grey", "name_ru": "Серо-голубой"},
]

def get_color_by_id(color_id):
    """Поиск цвета по ID"""
    return next((color for color in COLORS if color["id"] == color_id), None)
