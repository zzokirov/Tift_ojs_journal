from django.core.management.base import BaseCommand

from journal.docconvert import pdf_path_for, sniff
from journal.models import Article


class Command(BaseCommand):
    help = "PDF o'rniga Word fayl yuklangan maqolalar uchun PDF nusxani oldindan tayyorlaydi (kesh)"

    def handle(self, *args, **options):
        done = failed = 0
        for a in Article.objects.exclude(pdf_file='').exclude(pdf_file__isnull=True).iterator():
            try:
                path = a.pdf_file.path
            except Exception:
                continue
            if sniff(path) in ('docx', 'doc'):
                if pdf_path_for(path):
                    done += 1
                    self.stdout.write(f"  + {a.pk}: {a.title[:70]}")
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(f"  ! {a.pk}: aylantirib bo'lmadi — {a.title[:60]}"))
        self.stdout.write(self.style.SUCCESS(f"Word -> PDF: {done} ta tayyor, {failed} ta xato"))
