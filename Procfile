web: gunicorn cropcare_project.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A cropcare_project worker -l INFO
beat: celery -A cropcare_project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler