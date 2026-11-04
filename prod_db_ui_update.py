
import os, sys, django, shutil
sys.path.insert(0, '/home/devuser/apps/architect-edu/Tift_ojs_journal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from journal.models import Journal

# Make media covers dir
media_dir = '/home/devuser/apps/architect-edu/Tift_ojs_journal/media/journals/covers'
os.makedirs(media_dir, exist_ok=True)
static_img = '/home/devuser/apps/architect-edu/Tift_ojs_journal/static/images'

if os.path.exists(f'{static_img}/cover_architecture.jpg'):
    shutil.copy(f'{static_img}/cover_architecture.jpg', f'{media_dir}/cover_architecture.jpg')
if os.path.exists(f'{static_img}/cover_finance.jpg'):
    shutil.copy(f'{static_img}/cover_finance.jpg', f'{media_dir}/cover_finance.jpg')

# 1. Architecture Journal
j1 = Journal.objects.filter(id=1).first() or Journal.objects.filter(slug__icontains='arxitektura').first()
if j1:
    j1.slug = 'arxitektura-va-talim'
    j1.title_uz = "Arxitektura va ta'lim"
    j1.title_ru = "Архитектура и образование"
    j1.title_en = "Architecture and Education"
    j1.short_description_uz = "Arxitektura, qurilish va ta'lim sohalaridagi zamonaviy tadqiqotlar va ilmiy maqolalar uchun ilmiy jurnal."
    j1.short_description_ru = "Научный журнал современных исследований и научных статей в области архитектуры, строительства и образования."
    j1.short_description_en = "Scientific journal for modern research and academic articles in the fields of architecture, construction, and education."
    j1.full_description_uz = "Ushbu jurnal arxitektura, qurilish va ta'lim sohalarida olib borilayotgan ilmiy tadqiqotlar, innovatsion yondashuvlar va zamonaviy texnologiyalarni o'z ichiga oladi. Jurnal ilmiy hamjamiyat, talaba va tadqiqotchilar uchun muhim platforma hisoblanadi."
    j1.full_description_ru = "Данный журнал включает в себя научные исследования, инновационные подходы и современные технологии в области архитектуры, строительства и образования. Журнал является важной платформой для научного сообщества, студентов и исследователей."
    j1.full_description_en = "This journal covers scientific research, innovative approaches, and modern technologies in architecture, construction, and education. The journal serves as an essential platform for the academic community, students, and researchers."
    j1.research_areas_uz = "Arxitektura, Qurilish, Ta'lim, BIM, GIS, Dizayn"
    j1.research_areas_ru = "Архитектура, Строительство, Образование, BIM, ГИС, Дизайн"
    j1.research_areas_en = "Architecture, Construction, Education, BIM, GIS, Design"
    j1.issn = "3162-1554"
    j1.eissn = "3162-1562"
    j1.publisher_name = "TIFT universiteti"
    j1.publication_frequency = "4 marta yiliga"
    j1.cover_uz = 'journals/covers/cover_architecture.jpg'
    j1.cover_ru = 'journals/covers/cover_architecture.jpg'
    j1.cover_en = 'journals/covers/cover_architecture.jpg'
    j1.cover_image = 'journals/covers/cover_architecture.jpg'
    j1.save()
    print("Prod Journal #1 (Architecture) updated!")

# 2. Finance Journal
j2 = Journal.objects.filter(slug__icontains='moliya').first()
if not j2:
    j2 = Journal.objects.create(
        title="Moliya va intellektual texnologiyalar",
        slug="moliya-va-intellektual-texnologiyalar",
        issn="3162-1562",
        eissn="3162-1570",
        publication_status="published",
        is_active=True
    )

if j2:
    j2.slug = 'moliya-va-intellektual-texnologiyalar'
    j2.title_uz = "Moliya va intellektual texnologiyalar"
    j2.title_ru = "Финансы и интеллектуальные технологии"
    j2.title_en = "Finance and Intelligent Technologies"
    j2.short_description_uz = "Moliya, iqtisodiyot va raqamli texnologiyalar sohasidagi ilmiy tadqiqotlar uchun platforma."
    j2.short_description_ru = "Платформа для научных исследований в области финансов, экономики и цифровых технологий."
    j2.short_description_en = "Platform for scientific research in the fields of finance, economics, and digital technologies."
    j2.full_description_uz = "Moliya, bank ishi, sug'urta, investitsiyalar, sun'iy intellekt va raqamli texnologiyalarning iqtisodiyotdagi o'rni bo'yicha ilmiy maqolalar nashr etiladi."
    j2.full_description_ru = "Публикация научных статей о роли финансов, банковского дела, страхования, инвестиций, искусственного интеллекта и цифровых технологий в экономике."
    j2.full_description_en = "Publishing scientific articles on the role of finance, banking, insurance, investments, artificial intelligence, and digital technologies in the economy."
    j2.research_areas_uz = "Moliya, Raqamli iqtisodiyot, Bank ishi, FinTech, Sun'iy intellekt"
    j2.research_areas_ru = "Финансы, Цифровая экономика, Банковское дело, ФинТех, Искусственный интеллект"
    j2.research_areas_en = "Finance, Digital Economy, Banking, FinTech, Artificial Intelligence"
    j2.issn = "3162-1562"
    j2.eissn = "3162-1570"
    j2.publisher_name = "TIFT universiteti"
    j2.publication_frequency = "4 marta yiliga"
    j2.cover_uz = 'journals/covers/cover_finance.jpg'
    j2.cover_ru = 'journals/covers/cover_finance.jpg'
    j2.cover_en = 'journals/covers/cover_finance.jpg'
    j2.cover_image = 'journals/covers/cover_finance.jpg'
    j2.save()
    print("Prod Journal #2 (Finance) updated!")
