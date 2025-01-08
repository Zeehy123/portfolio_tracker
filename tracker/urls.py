from django.urls import path
from .views import StockListView, PortfolioView

urlpatterns = [
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('portfolio/<int:user_id>/', PortfolioView.as_view(), name='portfolio-detail'),
]
