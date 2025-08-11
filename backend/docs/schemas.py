from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)

# Пример кастомной схемы для ViewSet
example_schema = extend_schema(
    description="Детальное описание эндпоинта",
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Фильтрация по ID пользователя",
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)

# Или декоратор для всего ViewSet
extend_schema_view(
    list=extend_schema(description="Получение списка объектов"),
    create=extend_schema(description="Создание нового объекта"),
)
