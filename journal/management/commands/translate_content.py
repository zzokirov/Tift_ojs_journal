"""Jurnal va yo'nalishlarning rus/ingliz maydonlari bo'sh (yoki o'zbekcha bilan bir xil)
bo'lsa, ularni o'zbekchadan avtomatik tarjima qiladi.

Maqola sarlavhalari va annotatsiyalari tarjima qilinmaydi — ilmiy maqola o'z tilida qoladi.
Qo'lda kiritilgan tarjimalarga tegilmaydi.
"""
from django.core.management.base import BaseCommand

from journal.models import Journal, ArticleCategory, Conference
from journal.signals import translate_text, _fit

TARGETS = (
    (Journal, ('title', 'short_description', 'full_description', 'research_areas', 'publication_frequency')),
    (ArticleCategory, ('name',)),
    (Conference, ('title', 'organization', 'location')),
)


class Command(BaseCommand):
    help = "Jurnal va yo'nalishlarning bo'sh RU/EN tarjimalarini to'ldiradi"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help="Faqat nimalar tarjima qilinishini ko'rsatadi")

    def handle(self, *args, dry_run=False, **options):
        changed = 0
        for model, fields in TARGETS:
            for obj in model.objects.all():
                updates = {}
                for field in fields:
                    uz = (getattr(obj, f'{field}_uz', '') or '').strip()
                    if not uz:
                        continue
                    for lang in ('ru', 'en'):
                        cur = (getattr(obj, f'{field}_{lang}', '') or '').strip()
                        if cur and cur != uz:
                            continue  # allaqachon tarjima qilingan
                        if dry_run:
                            self.stdout.write(f"  {model.__name__}#{obj.pk}.{field}_{lang}: {uz[:60]}")
                            continue
                        tr = (translate_text(uz, lang) or '').strip()
                        if tr and tr != uz:
                            updates[f'{field}_{lang}'] = _fit(obj, f'{field}_{lang}', tr)
                if updates:
                    # update(): pre_save signallari qayta ishga tushmaydi
                    model.objects.filter(pk=obj.pk).update(**updates)
                    changed += 1
                    self.stdout.write(f"  + {model.__name__} #{obj.pk}: {', '.join(updates)}")
        self.stdout.write(self.style.SUCCESS(f"Tarjima qilindi: {changed} ta yozuv"))
