
import os
import django
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from journal.models import ArticleCategory, StaffMember, Article, News, Conference, Document

def fix_translations(instance, fields):
    from deep_translator import GoogleTranslator
    changed = False
    for field in fields:
        uz_val = getattr(instance, f"{field}_uz", None)
        ru_val = getattr(instance, f"{field}_ru", None)
        en_val = getattr(instance, f"{field}_en", None)

        if uz_val:
            if ru_val == uz_val:
                try:
                    setattr(instance, f"{field}_ru", GoogleTranslator(source='uz', target='ru').translate(uz_val))
                    changed = True
                    time.sleep(1)
                except:
                    pass
            if en_val == uz_val:
                try:
                    setattr(instance, f"{field}_en", GoogleTranslator(source='uz', target='en').translate(uz_val))
                    changed = True
                    time.sleep(1)
                except:
                    pass
    if changed:
        instance.save()
        print("Force translated " + str(instance.pk))

for obj in ArticleCategory.objects.all():
    fix_translations(obj, ['name'])
for obj in StaffMember.objects.all():
    fix_translations(obj, ['full_name', 'position', 'workplace', 'bio'])
