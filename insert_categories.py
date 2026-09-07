import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from journal.models import ArticleCategory

categories = [
    ("01.00.00", "Fizika-matematika fanlari"),
    ("04.00.00", "Geologiya-mineralogiya fanlari"),
    ("05.00.00", "Texnika fanlari"),
    ("07.00.00", "Tarix fanlari"),
    ("08.00.00", "Iqtisodiyot fanlari"),
    ("09.00.00", "Falsafa fanlari"),
    ("10.00.00", "Filologiya fanlari"),
    ("13.00.00", "Pedagogika fanlari"),
    ("18.00.00", "Arxitektura fanlari"),
    ("19.00.00", "Psixologiya fanlari"),
    ("22.00.00", "Sotsiologiya fanlari"),
]

for i, (code, name) in enumerate(categories):
    ArticleCategory.objects.get_or_create(code=code, defaults={'name': name, 'order': i})

print('Categories added successfully!')
