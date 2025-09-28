# evercoin/backend/api/core/constants/default_categories.py
DEFAULT_CATEGORIES = [
    # Категории расходов
    {'name': 'Продукты', 'icon': 'food', 'color': '#00B894', 'category_type': 'expense'},
    {'name': 'Транспорт', 'icon': 'transport', 'color': '#0984E3', 'category_type': 'expense'},
    {'name': 'Жилье', 'icon': 'home', 'color': '#F9A826', 'category_type': 'expense'},
    {'name': 'Здоровье', 'icon': 'health', 'color': '#FF6B6B', 'category_type': 'expense'},
    {'name': 'Развлечения', 'icon': 'entertainment', 'color': '#6C5CE7', 'category_type': 'expense'},
    {'name': 'Одежда', 'icon': 'clothing', 'color': '#FD79A8', 'category_type': 'expense'},
    {'name': 'Коммунальные услуги', 'icon': 'utilities', 'color': '#45B7D1', 'category_type': 'expense'},
    {'name': 'Подписки', 'icon': 'subscription', 'color': '#FDCB6E', 'category_type': 'expense'},
    
    # Категории доходов
    {'name': 'Зарплата', 'icon': 'salary', 'color': '#00B894', 'category_type': 'income'},
    {'name': 'Фриланс', 'icon': 'education', 'color': '#4ECDC4', 'category_type': 'income'},
    {'name': 'Инвестиции', 'icon': 'investment', 'color': '#6C5CE7', 'category_type': 'income'},
    {'name': 'Подарки', 'icon': 'gift', 'color': '#FD79A8', 'category_type': 'income'},
]