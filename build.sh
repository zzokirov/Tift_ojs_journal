#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Default yo'nalishlarni yaratish
python manage.py shell -c "
from journal.models import ArticleCategory
directions = [
    ('01.00.00', 'Fizika-matematika fanlari', 1),
    ('04.00.00', 'Geologiya-mineralogiya fanlari', 2),
    ('05.00.00', 'Texnika fanlari', 3),
    ('07.00.00', 'Tarix fanlari', 4),
    ('08.00.00', 'Iqtisodiyot fanlari', 5),
    ('09.00.00', 'Falsafa fanlari', 6),
    ('10.00.00', 'Filologiya fanlari', 7),
    ('13.00.00', 'Pedagogika fanlari', 8),
    ('18.00.00', 'Arxitektura fanlari', 9),
    ('19.00.00', 'Psixologiya fanlari', 10),
    ('22.00.00', 'Sotsiologiya fanlari', 11),
]
for code, name, order in directions:
    ArticleCategory.objects.get_or_create(code=code, defaults={'name': name, 'order': order})
print('Yo\'nalishlar yaratildi')
"

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
