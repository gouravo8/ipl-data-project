# C:\Users\Gourav Rajput\CropCareConnect\agriculture\admin.py

from django.contrib import admin
from .models import MarketPrice, RainfallData, CropAdvisory # Import your new model

# Register your models here.
admin.site.register(MarketPrice)
admin.site.register(RainfallData)
admin.site.register(CropAdvisory) # Register the CropAdvisory model



# agriculture/admin.py
from django.contrib import admin
from .models import MarketPrice, CropAdvisory, PMKisanBeneficiary, RainfallData, CropProduction, FarmerDiaryEntry # NEW: Import FarmerDiaryEntry

# ... (your existing admin registrations) ...

admin.site.register(FarmerDiaryEntry) # NEW: Register the FarmerDiaryEntry model
