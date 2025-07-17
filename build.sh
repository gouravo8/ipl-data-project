#!/usr/bin/env bash
set -e

echo "Running Django database migrations..."
python manage.py migrate

echo "Fetching initial/daily market data..." # This line should be present
python manage.py fetch_agmarknet_data # This line should be present and correctly named

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optional: Create a superuser for admin access.
# Uncomment and customize this if you want an admin user created on first deploy.
# Remember to change 'your_secure_password' to a strong password.
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'your_secure_password') if not User.objects.filter(username='admin').exists() else ''" | python manage.py shell
