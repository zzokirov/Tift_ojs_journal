#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Superuser avtomatik yaratish (faqat mavjud bo'lmasa)
python manage.py shell -c "
from journal.models import User
if not User.objects.filter(is_superuser=True).exists():
    import os
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@tift.uz')
    User.objects.create_superuser(username=username, password=password, email=email)
    print(f'Superuser yaratildi: {username}')
else:
    print('Superuser allaqachon mavjud')
"
