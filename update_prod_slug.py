
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from journal.models import Journal

j = Journal.objects.filter(id=1).first()
if j:
    j.slug = 'arxitektura-va-talim'
    j.save()
    print('Updated Journal #1 slug to:', j.slug)
for x in Journal.objects.all():
    print('Journal in DB:', x.id, x.title, 'slug =', x.slug)
