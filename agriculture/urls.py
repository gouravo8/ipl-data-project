# C:\Users\Gourav Rajput\CropCareConnect\agriculture\urls.py

from django.urls import path
from . import views

app_name = 'agriculture'

urlpatterns = [
    path('prices/', views.market_price_list, name='market_price_list'),
    # NEW URL FOR CROP ADVISORIES
    path('advisories/', views.crop_advisory_list, name='crop_advisory_list'),
]