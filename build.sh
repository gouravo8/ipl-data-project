    #!/usr/bin/env bash
    # Exit immediately if a command exits with a non-zero status.
    set -e

    echo "Running Django migrations..."
    python manage.py migrate

    echo "Collecting static files..."
    python manage.py collectstatic --noinput

    # Optional: Create a superuser for admin access. Uncomment and set credentials.
    # Remember to change these for security!
    # echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'your_secure_password') if not User.objects.filter(username='admin').exists() else ''" | python manage.py shell
    