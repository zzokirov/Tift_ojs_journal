import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from journal.models import ArticleCategory, StaffMember
from deep_translator import GoogleTranslator

def translate(text, target):
    if not text or len(text) < 2:
        return text
    try:
        time.sleep(0.5)
        return GoogleTranslator(source='uz', target=target).translate(text)
    except Exception as e:
        print("ERR:", e)
        time.sleep(3)
        try:
            return GoogleTranslator(source='uz', target=target).translate(text)
        except:
            return text

# Translate categories
for cat in ArticleCategory.objects.all():
    print("Cat:", cat.name_uz)
    cat.name_ru = translate(cat.name_uz, 'ru')
    cat.name_en = translate(cat.name_uz, 'en')
    cat.save()
    print("  RU:", cat.name_ru)
    print("  EN:", cat.name_en)

# Translate staff bio/position/workplace (NOT full_name - user said don't translate names)
for staff in StaffMember.objects.filter(is_active=True):
    print("Staff:", staff.full_name_uz)
    # Keep full_name same (it's a person's name, don't translate)
    staff.full_name_ru = staff.full_name_uz
    staff.full_name_en = staff.full_name_uz
    # Translate bio
    if staff.bio_uz:
        staff.bio_ru = translate(staff.bio_uz, 'ru')
        staff.bio_en = translate(staff.bio_uz, 'en')
    # Translate workplace
    if staff.workplace_uz:
        staff.workplace_ru = translate(staff.workplace_uz, 'ru')
        staff.workplace_en = translate(staff.workplace_uz, 'en')
    # position field is a choice (e.g. 'member', 'editor_in_chief') - no translation needed
    staff.save()
    print("  workplace_ru:", staff.workplace_ru)

print("DONE!")
