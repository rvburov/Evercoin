# evercoin/backend/api/analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Сводка за месяц
    path('analytics/monthly-summary/', views.MonthlySummaryView.as_view(), name='monthly-summary'),
    
    # Тренды за 6 месяцев
    path('analytics/trends/', views.TrendsView.as_view(), name='trends'),
    
    # Статистика по категориям
    path('analytics/category-stats/', views.CategoryAnalyticsView.as_view(), name='category-stats'),
    
    # Дневная статистика
    path('analytics/daily-stats/', views.DailyStatsView.as_view(), name='daily-stats'),
    
    # Журнал операций
    path('analytics/operation-journal/', views.OperationJournalView.as_view(), name='operation-journal'),
    
    # Общий обзор
    path('analytics/overview/', views.AnalyticsOverviewView.as_view(), name='overview'),
    
    # Список пресетов отчетов
    path('analytics/report-presets/', views.ReportPresetListView.as_view(), name='report-preset-list'),
    
    # Создание пресета
    path('analytics/report-presets/create/', views.ReportPresetCreateView.as_view(), name='report-preset-create'),
    
    # Обновление пресета
    path('analytics/report-presets/<int:pk>/update/', views.ReportPresetUpdateView.as_view(), name='report-preset-update'),
    
    # Удаление пресета
    path('analytics/report-presets/<int:pk>/delete/', views.ReportPresetDeleteView.as_view(), name='report-preset-delete'),
    
    # Очистка кеша
    path('analytics/clear-cache/', views.clear_analytics_cache, name='clear-cache'),
]