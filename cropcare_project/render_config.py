# render_config.py
import os
import dj_database_url

# Production settings for Render.
# These will override local settings when deployed on Render.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# IMPORTANT: BASE_DIR here refers to the parent directory of settings.py,
# which is usually your 'cropcare_project' folder.
# For static/media files, paths are relative to the project root 'CropCareConnect'
# on Render, so we need to adjust BASE_DIR logic slightly here.
# On Render, the build process usually puts your app at /opt/render/project/src/
# If your project structure is CropCareConnect/cropcare_project/settings.py,
# then BASE_DIR needs to point to CropCareConnect/
#
# A robust way is to make BASE_DIR point to the outer directory where manage.py is.
# This assumes render_config.py is in cropcare_project/
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
# Get the secret key from the environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-insecure-default-key-for-local-development-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False # Always set to False in production

# Allowed Hosts for Render deployment
# This will be updated with your actual Render URL after first deployment
ALLOWED_HOSTS = ['cropcare-gourav.onrender.com'] # IMPORTANT: Update this after deployment!


# Database configuration for Render PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600  # Persistent connections
    )
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT must point to a directory accessible by Render's web server
# It should be relative to your overall project root (CropCareConnect/)
STATIC_ROOT = os.path.join(PROJECT_ROOT_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIR, 'mediafiles')

# Other production-specific security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True