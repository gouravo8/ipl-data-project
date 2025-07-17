#!/usr/bin/env bash
# This line tells the system to run this script using bash.
# Exit immediately if any command fails.
set -e

echo "Running Django database migrations..."
# This command updates your PostgreSQL database in Render with your Django app's structure.
# It's like setting up all the shelves and sections in your new shop.
python manage.py migrate

echo "Collecting static files..."
# This command gathers all your shop's display items (CSS, JS, images like your logo)
# into one organized folder ('staticfiles') for Whitenoise to serve efficiently.
# '--noinput' means it won't ask you questions during the process.
python manage.py collectstatic --noinput

# Optional: Create a superuser for admin access.
# You can uncomment the line below if you want Render to automatically create an admin user
# for your Django admin panel. REMEMBER TO CHANGE 'your_secure_password' to something strong!
# For better security, you might prefer to create the superuser manually after the first deploy
# by connecting to the Render shell or running a one-off command.
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'your_secure_password') if not User.objects.filter(username='admin').exists() else ''" | python manage.py shell
