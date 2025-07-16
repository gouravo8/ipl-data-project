    # C:\Users\Gourav Rajput\CropCareConnect\cropcare_project\settings.py

    import os
    from pathlib import Path
    import dj_database_url # ADD THIS IMPORT

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent


    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    # IMPORTANT: Fetch SECRET_KEY from environment variable for production security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-local-dev-only')

    # SECURITY WARNING: don't run with debug turned on in production!
    # IMPORTANT: Fetch DEBUG from environment variable. Default to False for production.
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'

    # IMPORTANT: Fetch ALLOWED_HOSTS from environment variable.
    # Render will provide your app's URL (e.g., your-app-name.onrender.com)
    # In production, this should include your Render domain and any custom domains.
    # For local development, it will still allow 127.0.0.1,localhost.
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


    # Application definition

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'agriculture', # Your app
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware', # ADD THIS LINE FOR WHITENOISE
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'cropcare_project.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'], # Added project-level templates directory
            'APP_DIRS': True, # Keep this True to find templates within app directories
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

    WSGI_APPLICATION = 'cropcare_project.wsgi.application'


    # Database
    # https://docs.djangoproject.com/en/5.0/ref/settings/#databases

    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3', # Default for local development
            conn_max_age=600 # Optional: connection longevity
        )
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
    STATIC_ROOT = BASE_DIR / 'staticfiles' # This is where collectstatic will put files for WhiteNoise
    
    # Configure WhiteNoise to serve compressed and cached static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    STATICFILES_DIRS = [
        # Django's AppDirectoriesFinder (default) will find static files inside agriculture/static/agriculture/
        # No need to add BASE_DIR / 'static' here unless you have project-level static files outside of apps.
    ]


    # Default primary key field type
    # https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    # Media files (user-uploaded content)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'mediafiles_dev' # This is where user-uploaded files will go in local dev
    # For production, you'd typically use cloud storage (e.g., S3) for MEDIA_ROOT.
    # For free tier, Render's ephemeral storage means media files won't persist across deploys.
    