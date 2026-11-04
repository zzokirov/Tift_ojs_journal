
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from journal.models import Journal

Journal.objects.get_or_create(
    slug='moliya',
    defaults={
        'title': 'Moliya va Iqtisodiyot',
        'title_uz': 'Moliya va Iqtisodiyot',
        'title_ru': 'Финансы и Экономика',
        'title_en': 'Finance and Economics',
        'description': 'Moliya, raqamli iqtisodiyot, buxgalteriya hisobi, bank ishi va soliqqa tortish bo\'yicha zamonaviy tadqiqotlar va innovatsion yechimlar jurnali.',
        'description_uz': 'Moliya, raqamli iqtisodiyot, buxgalteriya hisobi, bank ishi va soliqqa tortish bo\'yicha zamonaviy tadqiqotlar va innovatsion yechimlar jurnali.',
        'description_ru': 'Журнал современных исследований и инновационных решений в области финансов, цифровой экономики, бухгалтерского учета, банковского дела и налогообложения.',
        'description_en': 'Journal of modern research and innovative solutions in finance, digital economy, accounting, banking and taxation.',
        'issn': '2181-XXXX',
        'founded_year': 2024,
    }
)
