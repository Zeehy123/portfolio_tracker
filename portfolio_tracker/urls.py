"""
URL configuration for portfolio_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from user.views import  RegisterationViewSet,LoginViewSet,RefreshViewset, UserDetailsView,ChangePasswordView,ChangeEmailView
from tracker.views import StockListView,StockDetailView,PortfolioValueView,TopPortfolioValueView,PortfolioPerformanceView,TopPerformingStocksView,StockDataView,BarChartDataView,DailyGainLossView,WorstPerformingStockView,BestPerformingStockView,TopThreeStocksView
router = DefaultRouter()
router.register(r'auth/register', RegisterationViewSet,basename='auth-register')
router.register(r'auth/login',LoginViewSet,basename='auth-login')
router.register(r'auth/refresh',RefreshViewset,basename='auth-refresh')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((router.urls, "api"))),
     path('api/stocks/', StockListView.as_view(), name='stock-list'),
     path('api/stocks/<int:id>/', StockDetailView.as_view(), name='stock-detail'),
     path('api/portfolio/value/', PortfolioValueView.as_view(), name='portfolio-value'),
     path('api/top-portfolio/', TopPortfolioValueView.as_view(), name='top-portfolio-value'),
     path('api/portfolio-performance/', PortfolioPerformanceView.as_view(), name='portfolio-performance'),
    path('api/top-performing-stocks/', TopPerformingStocksView.as_view(), name='top-performing-stocks'),
    path('api/table/stocks/', StockDataView.as_view(), name='stock-data'),
    path('api/bar-chart-dashboard/', BarChartDataView.as_view(), name='bar-chart-data'),
     path('api/stocks/daily-gain-loss/', DailyGainLossView.as_view(), name='daily-gain-loss'),
     path('api/stocks/worst-performing', WorstPerformingStockView.as_view(), name='worst-performing-stocks'),
      path('api/stocks/best-performing/', BestPerformingStockView.as_view(), name='best-performing-stock'),
     path('api/stocks/top-three-stocks',TopThreeStocksView.as_view(), name='top-three-stocks'),


     path("api/user/details/", UserDetailsView.as_view({'get': 'list'}), name='user-details'),
      path('api/user/details/update/', UserDetailsView.as_view({'put': 'update'}), name='update-user-details'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/profile/change-email/', ChangeEmailView.as_view(), name='change_email'),
]