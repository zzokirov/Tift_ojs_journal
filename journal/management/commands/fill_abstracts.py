from django.core.management.base import BaseCommand

from journal.models import Article
from journal.pdf_meta import fill_article_meta


class Command(BaseCommand):
    help = "Annotatsiya yoki kalit so'zlari bo'sh maqolalarni PDF/DOCX fayldan to'ldiradi"

    def handle(self, *args, **options):
        done = 0
        qs = Article.objects.exclude(pdf_file='').exclude(pdf_file__isnull=True)
        for article in qs.iterator():
            if fill_article_meta(article):
                done += 1
                self.stdout.write(f"  + {article.pk}: {article.title[:70]}")
        self.stdout.write(self.style.SUCCESS(f"To'ldirildi: {done} ta maqola"))
