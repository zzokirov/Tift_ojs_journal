
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from journal.models import Journal
Journal.objects.filter(slug='moliya').delete()
