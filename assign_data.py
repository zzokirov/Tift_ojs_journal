import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from journal.models import Journal, Article, ArticleCategory, Conference, Document, JournalIssue, News, StaffMember

j, created = Journal.objects.get_or_create(
    slug='arxitektura',
    defaults={
        'title': 'Arxitektura va Ta\'lim',
        'description': 'Jurnal arxitektura, qurilish, geodeziya, kartografiya, kadastr va ta\'lim sohasidagi ilmiy-amaliy tadqiqotlarni chop etishga ixtisoslashgan.',
        'issn': '2181-1230',
        'founded_year': 2024,
    }
)

print(f"Journal created/found: {j.title}")

print("Updating Article:", Article.objects.filter(journal__isnull=True).update(journal=j))
print("Updating ArticleCategory:", ArticleCategory.objects.filter(journal__isnull=True).update(journal=j))
print("Updating Conference:", Conference.objects.filter(journal__isnull=True).update(journal=j))
print("Updating Document:", Document.objects.filter(journal__isnull=True).update(journal=j))
print("Updating JournalIssue:", JournalIssue.objects.filter(journal__isnull=True).update(journal=j))
print("Updating News:", News.objects.filter(journal__isnull=True).update(journal=j))
print("Updating StaffMember:", StaffMember.objects.filter(journal__isnull=True).update(journal=j))
print("Data migration completed.")
