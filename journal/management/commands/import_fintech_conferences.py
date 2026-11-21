"""Eski tift-fintech.uz saytidagi konferensiyalarni Moliya jurnaliga import qiladi.

Ma'lumot: data/conferences_fintech.json (back.tift-fintech.uz/<til>/conferences/ dan olingan).
Qayta ishga tushirish xavfsiz: legacy_id bo'yicha mavjudlari yangilanmaydi (admin
tahrirlari saqlanadi), faqat yangilari qo'shiladi. PDF fayllar eski serverdan yuklab olinadi.
"""
import datetime
import json
import os
import re
import urllib.request

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db.models.signals import pre_save

from journal.models import Conference, Journal
from journal.signals import translate_conference

DATA = os.path.join(settings.BASE_DIR, 'data', 'conferences_fintech.json')


def parse_date(text, year):
    """'28.03.2026', '25-09-2026', '30.05.2025–31.05.2025' -> (date, date_text)."""
    dates = re.findall(r'(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})', text or '')
    if not dates:
        return datetime.date(int(year), 1, 1), (text or '').strip()
    d, m, y = (int(x) for x in dates[0])
    try:
        first = datetime.date(y, m, d)
    except ValueError:
        return datetime.date(int(year), 1, 1), text.strip()
    norm = ['.'.join(x for x in (a.zfill(2), b.zfill(2), c)) for a, b, c in dates]
    return first, ('–'.join(norm) if len(norm) > 1 else '')


def download(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


class Command(BaseCommand):
    help = "tift-fintech.uz konferensiyalarini Moliya jurnaliga import qiladi"

    def add_arguments(self, parser):
        parser.add_argument('--slug', default='moliya-va-intellektual-texnologiyalar')

    def handle(self, *args, slug, **opts):
        journal = Journal.objects.filter(slug=slug).first()
        if not journal:
            self.stdout.write(self.style.WARNING(f"Jurnal topilmadi: {slug}"))
            return
        with open(DATA, encoding='utf-8') as fh:
            items = json.load(fh)

        pre_save.disconnect(translate_conference, sender=Conference)
        added = 0
        try:
            for it in items:
                if Conference.objects.filter(legacy_id=it['id']).exists():
                    continue
                date, date_text = parse_date(it.get('held_date'), it['year'])
                c = Conference(journal=journal, legacy_id=it['id'], date=date, date_text=date_text,
                               participants=(it.get('participants') or '').strip(),
                               url=(it.get('link') or '').strip(), order=it.get('order') or 0)
                for field, src in (('title', 'topic'), ('organization', 'organization'), ('location', 'location')):
                    uz = it.get(f'{src}_uz', '')
                    setattr(c, field, uz)
                    setattr(c, f'{field}_uz', uz)
                    for lang in ('ru', 'en'):
                        v = it.get(f'{src}_{lang}', '')
                        if v and v != uz:  # eski saytda tarjima bo'lsa
                            setattr(c, f'{field}_{lang}', v)
                c.save()
                if it.get('pdf'):
                    try:
                        name = os.path.basename(it['pdf'].split('?')[0]) or f"conference_{it['id']}.pdf"
                        c.pdf_file.save(name, ContentFile(download(it['pdf'])), save=True)
                    except Exception as e:  # PDF bo'lmasa ham konferensiya qoladi
                        self.stdout.write(self.style.WARNING(f"  PDF yuklanmadi ({it['pdf']}): {e}"))
                        if not c.url:
                            Conference.objects.filter(pk=c.pk).update(url=it['pdf'])
                added += 1
                self.stdout.write(f"  + {c.date:%Y} {c.title[:70]}")
        finally:
            pre_save.connect(translate_conference, sender=Conference)
        self.stdout.write(self.style.SUCCESS(f"Konferensiyalar: {added} ta qo'shildi"))
