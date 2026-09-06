import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import fitz
from journal.models import JournalIssue, Article
from journal.views import _get_pdf_bytes

def update_all_article_pages():
    for issue in JournalIssue.objects.all():
        articles = list(Article.objects.filter(issue=issue, status='published').order_by('created_at', 'id'))
        if not articles:
            continue
        
        cover_count = (1 if issue.cover_image and issue.cover_image.name else 0) + \
                      (1 if issue.back_cover_image and issue.back_cover_image.name else 0) + 1
        
        toc_count = 1
        current_page = cover_count + toc_count + 1
        
        for art in articles:
            pages = 1
            try:
                if art.pdf_file:
                    raw_bytes = _get_pdf_bytes(art.pdf_file)
                    if raw_bytes:
                        doc = fitz.open(stream=raw_bytes, filetype="pdf")
                        pages = len(doc)
                        doc.close()
            except Exception as e:
                print(f"Error calculating pages for article {art.pk}: {e}")
            
            start_p = current_page
            end_p = current_page + pages - 1
            Article.objects.filter(pk=art.pk).update(start_page=start_p, end_page=end_p)
            print(f"Issue {issue.number} - Article '{art.title[:30]}': {start_p}-{end_p}")
            current_page = end_p + 1

if __name__ == '__main__':
    update_all_article_pages()
