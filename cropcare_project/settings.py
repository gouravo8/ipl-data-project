# settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Default to an insecure key for local development. This will be overridden by Render.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-k3+j!&x_#g*d9^!m!^7e2q#3k&d(o3r*@1b_1l-2q5o_6p7s8')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # Keep True for local development, will be False on Render

ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] # Only for local development


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Add your Django apps here, e.g.:
    # 'my_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add this line for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cropcare_project.urls' # Ensure this matches your inner project name

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cropcare_project.wsgi.application' # Ensure this matches your inner project name


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT for local development (optional, but good for consistency)
# This isn't strictly needed for local `runserver` but for `collectstatic` locally.
STATIC_ROOT = BASE_DIR / 'staticfiles_dev'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles_dev' # For local media files


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Import Render-specific settings if running on Render
# This checks for an environment variable 'RENDER' which is automatically set by Render.
if 'RENDER' in os.environ:
    # Ensure this path is correct relative to your settings.py
    # If render_config.py is in the same directory as settings.py
    try:
        import render_config
        # Apply all settings from render_config.py
        for setting in dir(render_config):
            # Only copy uppercase attributes (which are typically Django settings)
            if setting.isupper():
                globals()[setting] = getattr(render_config, setting)
    except ImportError:
        print("Warning: render_config.py not found. Ensure it's in the same directory as settings.py for Render deployment.")