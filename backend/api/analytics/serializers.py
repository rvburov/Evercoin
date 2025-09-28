# evercoin/backend/api/analytics/serializers.py
from rest_framework import serializers
from .models import CachedAnalytics, ReportPreset


class MonthlySummarySerializer(serializers.Serializer):
    """
    Сериализатор для сводки за месяц
    """
    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    income_categories = serializers.ListField()
    expense_categories = serializers.ListField()


class CategoryStatsSerializer(serializers.Serializer):
    """
    Сериализатор для статистики по категориям
    """
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    category_icon = serializers.CharField()
    category_color = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    operation_count = serializers.IntegerField()
    percentage = serializers.FloatField()
    category_type = serializers.CharField()


class DailyStatsSerializer(serializers.Serializer):
    """
    Сериализатор для дневной статистики
    """
    date = serializers.DateField()
    income = serializers.DecimalField(max_digits=15, decimal_places=2)
    expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)


class TrendsSerializer(serializers.Serializer):
    """
    Сериализатор для трендов за 6 месяцев
    """
    period = serializers.CharField()
    income = serializers.DecimalField(max_digits=15, decimal_places=2)
    expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)


class AnalyticsFilterSerializer(serializers.Serializer):
    """
    Сериализатор для параметров фильтрации аналитики
    """
    period = serializers.ChoiceField(
        choices=[
            ('day', 'День'),
            ('week', 'Неделя'),
            ('month', 'Месяц'),
            ('year', 'Год'),
            ('custom', 'Произвольный период')
        ],
        default='month'
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    wallets = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    operation_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[('income', 'Доход'), ('expense', 'Расход'), ('transfer', 'Перевод')]),
        required=False
    )
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )


class ReportPresetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пресетов отчетов
    """
    class Meta:
        model = ReportPreset
        fields = [
            'id',
            'name',
            'report_type',
            'filters',
            'is_default',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        """
        Создание пресета с автоматическим назначением пользователя
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class ReportPresetCreateSerializer(ReportPresetSerializer):
    """
    Сериализатор для создания пресетов
    """
    pass


class ReportPresetUpdateSerializer(ReportPresetSerializer):
    """
    Сериализатор для обновления пресетов
    """
    pass


class OperationJournalSerializer(serializers.Serializer):
    """
    Сериализатор для журнала операций
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    operation_type = serializers.CharField()
    operation_date = serializers.DateTimeField()
    wallet_name = serializers.CharField()
    wallet_currency = serializers.CharField()
    category_name = serializers.CharField(allow_null=True)
    category_icon = serializers.CharField(allow_null=True)
    category_color = serializers.CharField(allow_null=True)


class AnalyticsOverviewSerializer(serializers.Serializer):
    """
    Сериализатор для общего обзора аналитики
    """
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    top_categories = serializers.ListField()
    recent_operations = serializers.ListField()
    wallet_distribution = serializers.ListField()