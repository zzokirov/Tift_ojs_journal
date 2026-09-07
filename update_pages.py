import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from journal.models import JournalIssue

def update_all_article_pages():
    try:
        from journal.views import recalculate_issue_pages
        for issue in JournalIssue.objects.all():
            print(f"Recalculating pages for issue {issue.year} #{issue.number}...")
            master_doc, article_items = recalculate_issue_pages(issue)
            for item in article_items:
                art = item['article']
                print(f"  -> Article '{art.title[:35]}': pages {item['start_page']}-{item['end_page']}")
    except (ImportError, AttributeError):
        print("recalculate_issue_pages function not available, skipping.")

if __name__ == '__main__':
    update_all_article_pages()
