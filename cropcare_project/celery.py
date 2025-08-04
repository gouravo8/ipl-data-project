# C:\Users\Gourav Rajput\CropCareConnect\cropcare_project\celery.py

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
# This must be done before creating the Celery app instance.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cropcare_project.settings')

# Create a Celery instance and name it based on the current project's name.
app = Celery('cropcare_project')

# Load task settings from the Django settings file.
# The `namespace` argument ensures that all Celery-related settings
# are prefixed with 'CELERY_' in your settings.py.
app.config_from_object('django.conf.settings', namespace='CELERY')

# Automatically discover tasks in all Django apps
# by looking for a 'tasks.py' file.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# A debug task to check if Celery is running correctly.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
