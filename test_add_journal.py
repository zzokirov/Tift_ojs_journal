
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from journal.models import Journal

# Test adding a journal
j, created = Journal.objects.get_or_create(
    slug='moliya-va-intellektual-texnologiyalar',
    defaults={
        'title': 'Moliya va intellektual texnologiyalar',
        'title_uz': 'Moliya va intellektual texnologiyalar',
        'issn': '2181-9988',
        'publication_status': 'published',
        'is_active': True,
        'short_description': 'Moliyaviy menejment va sun\'iy intellekt bo\'yicha ilmiy nashr.'
    }
)
print('Journal exists:', j.title, 'slug =', j.slug)
