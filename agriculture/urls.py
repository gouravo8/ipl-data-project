# C:\Users\Gourav Rajput\CropCareConnect\agriculture\urls.py

from django.urls import path
from . import views

# IMPORTANT: This line is crucial for namespacing (e.g., agriculture:home_page)
app_name = 'agriculture' 

urlpatterns = [
    # Main Home Page for the agriculture app
    # When included at the project root, this will be http://127.0.0.1:8000/
    path('', views.home_page, name='home_page'),

    # Market Prices Feature
    path('market-prices/', views.market_price_list, name='market_price_list'),

    # Crop Advisories Feature
    path('crop-advisories/', views.crop_advisory_list, name='crop_advisory_list'),

    # Real-time Weather Feature
    path('realtime-weather/', views.realtime_weather_view, name='realtime_weather'),

    # Weather Forecast Feature
    path('weather-forecast/', views.weather_forecast_view, name='weather_forecast'),

    # Farmer Diary Feature URLs
    path('diary/add/', views.diary_create_view, name='diary_create'),
    path('diary/', views.diary_list_view, name='diary_list'),
    path('diary/<int:pk>/', views.diary_detail_view, name='diary_detail'),
    path('diary/<int:pk>/edit/', views.diary_update_view, name='diary_update'),
    path('diary/<int:pk>/delete/', views.diary_delete_view, name='diary_delete'),
]