#!/usr/bin/env bash
# This line ensures the script exits immediately if any command fails.
set -e

echo "Running Django database migrations..."
# This command applies all pending database migrations.
# It creates tables like "agriculture_marketprice" if they don't exist.
python manage.py migrate

echo "Collecting static files..."
# This command gathers all static files (CSS, JS, images) into the 'staticfiles' directory.
# '--noinput' prevents it from asking questions during the process.
python manage.py collectstatic --noinput

# Optional: Create a superuser for admin access.
# Uncomment and customize this if you want an admin user created on first deploy.
# Remember to change 'your_secure_password' to a strong password.
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'your_secure_password') if not User.objects.filter(username='admin').exists() else ''" | python manage.py shell
