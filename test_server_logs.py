import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from journal.models import Article; from journal.views import download_pdf; class DummyRequest:
    def build_absolute_uri(self, location): return 'http://localhost' + location
try:
    download_pdf(DummyRequest(), 8) # Using one of the IDs I found earlier
except Exception as e:
    print('Failed:', e)

