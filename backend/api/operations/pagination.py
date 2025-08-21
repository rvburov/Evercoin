from rest_framework.pagination import CursorPagination

class OperationCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-date'
    cursor_query_param = 'cursor'

class OperationHistoryCursorPagination(CursorPagination):
    page_size = 50
    ordering = '-date'
    cursor_query_param = 'cursor'
