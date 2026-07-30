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
a = Article.objects.filter(status='published').first()
if a:
    try:
        resp = download_pdf(req, a.pk)
        print('Response type:', type(resp))
        print('Content type:', resp.get('Content-Type'))
        if resp.get('Content-Type') != 'application/pdf':
            print('Redirect URL:', resp.url)
    except Exception as e:
        print('Error:', e)
else:
    print('No published articles found')

