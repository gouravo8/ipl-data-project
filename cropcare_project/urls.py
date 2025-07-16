    # C:\Users\Gourav Rajput\CropCareConnect\cropcare_project\urls.py

    from django.contrib import admin
    from django.urls import path, include
    # No need to import settings or static for production static/media serving here
    # WhiteNoise handles static files, and for media, a cloud storage solution
    # is typically used in production (or it's ephemeral on free tiers like Render).

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('agriculture.urls')),
    ]

    # In production, static and media files are served differently (e.g., WhiteNoise, S3).
    # The development server's static/media serving helpers should NOT be used in production.
    # If you need to serve media files in development from MEDIA_ROOT, you can add:
    # from django.conf import settings
    # from django.conf.urls.static import static
    # if settings.DEBUG:
    #     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    