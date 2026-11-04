
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from journal.models import Journal, JournalIssue

for j in Journal.objects.all():
    if j.cover_image and not j.cover_uz:
        j.cover_uz = j.cover_image
    j.publication_status = 'published'
    j.is_active = True
    if not j.publication_frequency:
        j.publication_frequency = 'Yiliga 4 marta'
    if not j.publisher_name:
        j.publisher_name = 'Toshkent Xalqaro Moliyaviy Boshqaruv va Texnologiyalar Universiteti'
    j.save()
    print('Updated journal:', j.title, 'cover_uz:', bool(j.cover_uz))

for issue in JournalIssue.objects.all():
    if issue.is_published:
        issue.status = 'published'
    else:
        issue.status = 'draft'
    issue.save()
print('Issues updated.')
