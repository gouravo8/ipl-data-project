# C:\Users\Gourav Rajput\CropCareConnect\cropcare_project\urls.py

from django.contrib import admin # This line must start at column 1
from django.urls import path, include
# In production, static and media files are served by Whitenoise or cloud storage.
# The development server's static/media serving helpers should NOT be used in production.
# So, we remove the `from django.conf import settings` and `static` imports,
# and the `if settings.DEBUG:` block for static/media serving.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('agriculture.urls')), # Your agriculture app is at the root
]
