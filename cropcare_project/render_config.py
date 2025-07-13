# render_config.py

import os
import dj_database_url # <--- Make sure this line is here

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- DATABASE CONFIGURATION ---
# This tells Django to use the DATABASE_URL environment variable provided by Render
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///tmp/mydatabase.sqlite3', # This is just a fallback, Render will use the actual DATABASE_URL
        conn_max_age=600 # Optional: connection timeout
    )
}

# --- SECRET KEY ---
SECRET_KEY = os.environ.get('SECRET_KEY')

# --- ALLOWED HOSTS ---
ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME')]

# --- DEBUG SETTING ---
DEBUG = False

# --- STATIC FILES ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'