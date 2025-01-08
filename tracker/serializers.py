from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'user', 'name', 'quantity', 'ticker', 'buy_price']
        read_only_fields = ['user']
class StockPerformanceSerializer(serializers.ModelSerializer):
    performance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [ 'name', 'ticker', 'performance_percentage']

    def get_performance_percentage(self, obj):
        return obj.performance_percentage