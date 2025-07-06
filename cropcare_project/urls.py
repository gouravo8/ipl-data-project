# C:\Users\Gourav Rajput\CropCareConnect\CropCareConnect\urls.py

from django.contrib import admin
from django.urls import path, include
# We'll import your new home_page view here from the agriculture app
from agriculture import views # Add this line to import views from your agriculture app

urlpatterns = [
    path('admin/', admin.site.urls),
    # This will be your new landing page / home page
    path('', views.home_page, name='home'), # NEW: Home page mapping
    path('agriculture/', include('agriculture.urls')),
    # Other paths you might have...
]