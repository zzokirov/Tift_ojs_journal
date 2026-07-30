import os
import django
from django.conf import settings
from django.test import RequestFactory
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from jazzmin.templatetags.jazzmin import get_side_menu

req = RequestFactory().get('/admin/')
class DummyUser:
    is_active = True
    is_staff = True
    is_superuser = True
    def has_module_perms(self, app): return True
    def has_perm(self, perm): return True
req.user = DummyUser()

menu = get_side_menu({'request': req})
print("Found apps:", [app['app_label'] for app in menu])
for app in menu:
    print(f"\nAPP: {app['app_label']}")
    for model in app.get('models', []):
        print(f" - {model['name']}: {model.get('url', 'NO_URL')}")
