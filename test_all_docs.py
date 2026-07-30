import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from journal.models import Article
from journal.views import download_pdf

class DummyRequest:
    def build_absolute_uri(self, location):
        return 'http://localhost' + location

req = DummyRequest()
for a in Article.objects.filter(status='published', pdf_file__icontains='.doc'):
    print(f'Testing {a.pk} - {a.title}')
    try:
        resp = download_pdf(req, a.pk)
        if resp.get('Content-Type') != 'application/pdf':
            print('   -> Failed, returned Redirect')
        else:
            print('   -> Success PDF')
    except Exception as e:
        print('   -> Error:', e)

