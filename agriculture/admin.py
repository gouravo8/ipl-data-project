# C:\Users\Gourav Rajput\CropCareConnect\agriculture\admin.py

from django.contrib import admin
from .models import MarketPrice, RainfallData, CropAdvisory # Import your new model

# Register your models here.
admin.site.register(MarketPrice)
admin.site.register(RainfallData)
admin.site.register(CropAdvisory) # Register the CropAdvisory model