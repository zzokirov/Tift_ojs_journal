import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import django
import json
import re
import urllib.request
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from journal.models import Journal, JournalIssue, Article, ArticleCategory
from journal.signals import translate_article, translate_category

pre_save.disconnect(translate_article, sender=Article)
pre_save.disconnect(translate_category, sender=ArticleCategory)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

CANONICAL_CATEGORIES = [
    {
        'code': 'MF.00.01',
        'name': 'Bosh muharrirdan - mushtariylarga',
        'name_uz': 'Bosh muharrirdan - mushtariylarga',
        'name_ru': 'От главного редактора - читателям',
        'name_en': 'From the Editor-in-Chief - to the Readers',
        'icon': 'fa-feather-alt',
        'order': 1,
    },
    {
        'code': 'MF.01.00',
        'name': "Moliya, soliq, byudjet, sug'urta",
        'name_uz': "Moliya, soliq, byudjet, sug'urta",
        'name_ru': 'Финансы, налоги, бюджет, страхование',
        'name_en': 'Finance, Taxes, Budget, Insurance',
        'icon': 'fa-coins',
        'order': 2,
    },
    {
        'code': 'MF.02.00',
        'name': 'Bank, kredit, davlat qarzi',
        'name_uz': 'Bank, kredit, davlat qarzi',
        'name_ru': 'Банк, кредит, государственный долг',
        'name_en': 'Banking, Credit, Public Debt',
        'icon': 'fa-university',
        'order': 3,
    },
    {
        'code': 'MF.03.00',
        'name': 'Buxgalteriya hisobi va iqtisodiy tahlil',
        'name_uz': 'Buxgalteriya hisobi va iqtisodiy tahlil',
        'name_ru': 'Бухгалтерский учет и экономический анализ',
        'name_en': 'Accounting and Economic Analysis',
        'icon': 'fa-calculator',
        'order': 4,
    },
    {
        'code': 'MF.04.00',
        'name': 'Investitsiya va innovatsiya',
        'name_uz': 'Investitsiya va innovatsiya',
        'name_ru': 'Инвестиции и инновации',
        'name_en': 'Investment and Innovation',
        'icon': 'fa-chart-line',
        'order': 5,
    },
    {
        'code': 'MF.05.00',
        'name': 'Tarmoqlar iqtisodiyoti',
        'name_uz': 'Tarmoqlar iqtisodiyoti',
        'name_ru': 'Экономика отраслей',
        'name_en': 'Sectoral Economics',
        'icon': 'fa-industry',
        'order': 6,
    },
    {
        'code': 'MF.06.00',
        'name': 'Xorijiy mamlakatlar iqtisodiyoti',
        'name_uz': 'Xorijiy mamlakatlar iqtisodiyoti',
        'name_ru': 'Экономика зарубежных стран',
        'name_en': 'Economy of Foreign Countries',
        'icon': 'fa-globe-americas',
        'order': 7,
    },
    {
        'code': 'MF.07.00',
        'name': "Iqtisodiyotni raqamlashtirish, sun'iy intellekt va axborot texnologiyalari",
        'name_uz': "Iqtisodiyotni raqamlashtirish, sun'iy intellekt va axborot texnologiyalari",
        'name_ru': 'Цифровизация экономики, искусственный интеллект и ИТ',
        'name_en': 'Digital Economy, AI and IT',
        'icon': 'fa-robot',
        'order': 8,
    },
    {
        'code': 'MF.08.00',
        'name': "Ta'lim tizimi",
        'name_uz': "Ta'lim tizimi",
        'name_ru': 'Система образования',
        'name_en': 'Education System',
        'icon': 'fa-graduation-cap',
        'order': 9,
    },
    {
        'code': 'MF.09.00',
        'name': 'Kichik biznes va xususiy tadbirkorlik',
        'name_uz': 'Kichik biznes va xususiy tadbirkorlik',
        'name_ru': 'Малый бизнес и частное предпринимательство',
        'name_en': 'Small Business and Private Entrepreneurship',
        'icon': 'fa-store',
        'order': 10,
    },
    {
        'code': 'MF.10.00',
        'name': "Qimmatli qog'ozlar bozori",
        'name_uz': "Qimmatli qog'ozlar bozori",
        'name_ru': 'Рынок ценных бумаг',
        'name_en': 'Securities Market',
        'icon': 'fa-chart-bar',
        'order': 11,
    },
    {
        'code': 'MF.11.00',
        'name': 'Moliyaviy menejment va marketing',
        'name_uz': 'Moliyaviy menejment va marketing',
        'name_ru': 'Финансовый менеджмент и маркетинг',
        'name_en': 'Financial Management and Marketing',
        'icon': 'fa-bullhorn',
        'order': 12,
    },
    {
        'code': 'MF.12.00',
        'name': "«O'zbekiston – 2030» strategiyasi",
        'name_uz': "«O'zbekiston – 2030» strategiyasi",
        'name_ru': 'Стратегия «Узбекистан – 2030»',
        'name_en': '«Uzbekistan – 2030» Strategy',
        'icon': 'fa-flag',
        'order': 13,
    },
    {
        'code': 'MF.13.00',
        'name': 'Nobel mukofoti',
        'name_uz': 'Nobel mukofoti',
        'name_ru': 'Нобелевская премия',
        'name_en': 'Nobel Prize',
        'icon': 'fa-award',
        'order': 14,
    },
    {
        'code': 'MF.14.00',
        'name': 'Makro va mikroiqtisodiyot',
        'name_uz': 'Makro va mikroiqtisodiyot',
        'name_ru': 'Макро и микроэкономика',
        'name_en': 'Macro and Microeconomics',
        'icon': 'fa-balance-scale',
        'order': 15,
    },
    {
        'code': 'MF.99.00',
        'name': "Jurnalning to'liq nashri",
        'name_uz': "Jurnalning to'liq nashri",
        'name_ru': 'Полный выпуск журнала',
        'name_en': 'Full Issue of the Journal',
        'icon': 'fa-book-open',
        'order': 99,
    },
]

def map_raw_to_canonical_code(raw_name):
    n = raw_name.lower().strip()
    n = re.sub(r'[\.,;:\'ʼʻ‘`"]', '', n)
    n = re.sub(r'\s+', ' ', n)

    if "to'liq" in n or "toliq" in n or "полный" in n or "full" in n:
        return "MF.99.00"
    if 'bosh muharrir' in n or 'mushtariy' in n:
        return "MF.00.01"
    if 'menejment' in n or 'marketing' in n:
        return "MF.11.00"
    if 'молия' in n or 'солиқ' in n or 'moliya' in n or 'soliq' in n or 'byudjet' in n or 'sugurta' in n:
        return "MF.01.00"
    if 'банк' in n or 'кредит' in n or 'bank' in n or 'kredit' in n:
        return "MF.02.00"
    if 'бухгалтерия' in n or 'buxgalteriya' in n:
        return "MF.03.00"
    if 'investitsiya' in n or 'innovatsiya' in n or 'инвестиции' in n:
        return "MF.04.00"
    if 'тармоқлар' in n or 'tarmoqlar' in n or 'tarmoq' in n:
        return "MF.05.00"
    if 'хорижий' in n or 'xorijiy' in n:
        return "MF.06.00"
    if 'сунъий' in n or 'интеллект' in n or 'ахборот' in n or 'raqamlashtirish' in n or 'nano' in n or 'agro' in n or 'intellekt' in n:
        return "MF.07.00"
    if 'talim' in n or 'таълим' in n:
        return "MF.08.00"
    if 'kichik' in n or 'biznes' in n or 'tadbirkorlik' in n:
        return "MF.09.00"
    if 'qimmatli' in n or 'qogoz' in n or 'bozori' in n:
        return "MF.10.00"
    if 'strategiya' in n or '2030' in n:
        return "MF.12.00"
    if 'nobel' in n:
        return "MF.13.00"
    if 'makro' in n or 'mikro' in n:
        return "MF.14.00"

    return "MF.05.00"

def detect_language(title):
    t = title or ''
    if re.search(r'[ыэящъёЫЭЯЩЪЁ]', t):
        return 'ru'
    if re.search(r'[а-яА-Я]', t):
        return 'ru'
    common_en = ['the', 'and', 'of', 'in', 'to', 'for', 'with', 'on', 'development', 'analysis', 'role', 'system']
    words = [w.lower() for w in re.findall(r'[a-zA-Z]+', t)]
    if any(w in common_en for w in words):
        return 'en'
    return 'uz'

def download_file(url, dest_path):
    if not url:
        return False
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return True
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    for attempt in range(3):
        try:
            # Cleanly unquote first, then quote once
            unquoted = urllib.parse.unquote(url)
            parsed = urllib.parse.urlsplit(unquoted)
            safe_url = urllib.parse.urlunsplit((
                parsed.scheme,
                parsed.netloc,
                urllib.parse.quote(parsed.path),
                urllib.parse.quote(parsed.query, safe='=&?'),
                parsed.fragment
            ))

            req = urllib.request.Request(safe_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = resp.read()
                if len(data) > 200:
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                    return True
        except Exception as e:
            if attempt == 2:
                print(f"  [WARN] Failed to download {url}: {e}", flush=True)
    return False

def run_migration():
    print("=== STARTING FINTECH MIGRATION ===", flush=True)
    j = Journal.objects.get(slug='moliya-va-intellektual-texnologiyalar')
    admin_user = get_user_model().objects.filter(is_superuser=True).first()
    media_root = settings.MEDIA_ROOT

    # 1. Ensure categories exist
    cat_objs = {}
    for cdata in CANONICAL_CATEGORIES:
        cat, created = ArticleCategory.objects.get_or_create(
            code=cdata['code'],
            defaults={
                'journal': j,
                'name': cdata['name'],
                'name_uz': cdata['name_uz'],
                'name_ru': cdata['name_ru'],
                'name_en': cdata['name_en'],
                'icon': cdata['icon'],
                'order': cdata['order'],
            }
        )
        if not created and cat.journal != j:
            cat.journal = j
            cat.save()
        cat_objs[cdata['code']] = cat
    print(f"Categories ready: {len(cat_objs)} categories.", flush=True)

    # 2. Load scraped JSONs
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    with open(os.path.join(data_dir, 'magazines_uz.json'), 'r', encoding='utf-8') as f:
        uz_data = json.load(f)
    with open(os.path.join(data_dir, 'magazines_ru.json'), 'r', encoding='utf-8') as f:
        ru_data = json.load(f)
    with open(os.path.join(data_dir, 'magazines_en.json'), 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    # Build maps
    ru_art_map = {a.get('id'): a for m in ru_data for c in m.get('categories', []) for a in c.get('articles', [])}
    en_art_map = {a.get('id'): a for m in en_data for c in m.get('categories', []) for a in c.get('articles', [])}

    issue_info_map = {
        '3-son | 2026 yil': (2, 3, 2026, 3, "Iyul - Sentyabr", "2026-10-12"),
        '2-son | 2026':     (2, 2, 2026, 2, "Aprel - Iyun", "2026-06-30"),
        '1-son | 2026':     (2, 1, 2026, 1, "Yanvar - Mart", "2026-03-30"),
        '4-son | 2025':     (1, 4, 2025, 4, "Oktyabr - Dekabr", "2025-12-30"),
        '3-son | 2025':     (1, 3, 2025, 3, "Iyul - Sentyabr", "2025-09-30"),
        '2-son | 2025':     (1, 2, 2025, 2, "Aprel - Iyun", "2025-06-30"),
        '1-son | 2025':     (1, 1, 2025, 1, "Yanvar - Mart", "2025-03-30"),
    }

    downloads = []
    created_issues = 0
    created_articles = 0

    sorted_magazines = sorted(uz_data, key=lambda m: (
        issue_info_map.get(m.get('which_number'), (0,0,0))[2],
        issue_info_map.get(m.get('which_number'), (0,0,0))[1]
    ))

    for m in sorted_magazines:
        which = m.get('which_number', '').strip()
        info = issue_info_map.get(which)
        if not info:
            continue

        vol, num, yr, qtr, per, pdate = info
        print(f"--- Processing Issue: {num}-son, {yr}-yil (Vol {vol}) ---", flush=True)

        issue, _ = JournalIssue.objects.get_or_create(
            journal=j,
            number=num,
            year=yr,
            defaults={
                'volume': vol,
                'quarter': qtr,
                'period': per,
                'title': f"{num}-son, {yr}-yil",
                'description': f"Moliya va intellektual texnologiyalar ilmiy-elektron jurnali, {yr}-yil {num}-son nashri.",
                'status': 'published',
                'is_published': True,
                'publication_date': pdate,
            }
        )
        issue.volume = vol
        issue.quarter = qtr
        issue.period = per
        issue.status = 'published'
        issue.is_published = True
        issue.publication_date = pdate
        created_issues += 1

        cover_url = m.get('cover_image')
        if cover_url:
            ext = cover_url.split('.')[-1].lower().split('?')[0]
            if ext not in ('png', 'jpg', 'jpeg', 'webp'):
                ext = 'png'
            cover_filename = f"issues/fintech_cover_{yr}_{num}.{ext}"
            cover_dest = os.path.join(media_root, cover_filename)
            downloads.append((cover_url, cover_dest))
            issue.cover_image.name = cover_filename

        order_index = 1
        for cat_data in m.get('categories', []):
            raw_cat_name = cat_data.get('name_uz', '')
            canon_code = map_raw_to_canonical_code(raw_cat_name)
            cat_obj = cat_objs.get(canon_code)

            for a in cat_data.get('articles', []):
                aid = a.get('id')
                art_ru = ru_art_map.get(aid, {})
                art_en = en_art_map.get(aid, {})

                title_uz = (a.get('name_uz') or '').strip()
                title_ru = (art_ru.get('name_ru') or a.get('name_ru') or '').strip()
                title_en = (art_en.get('name_en') or a.get('name_en') or '').strip()

                main_title = title_uz or title_ru or title_en
                if not main_title:
                    continue

                is_full_issue = canon_code == "MF.99.00" or "to'liq" in main_title.lower() or "to'liq" in raw_cat_name.lower()

                pdf_url = a.get('file_uz') or art_ru.get('file_ru') or art_en.get('file_en') or a.get('view_article_or_download')
                rel_pdf_path = None
                if pdf_url:
                    safe_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', main_title[:30]).strip('_')
                    if is_full_issue:
                        pdf_filename = f"issues/fintech_full_{yr}_{num}.pdf"
                        pdf_dest = os.path.join(media_root, pdf_filename)
                        downloads.append((pdf_url, pdf_dest))
                        issue.full_pdf.name = pdf_filename
                    else:
                        pdf_filename = f"articles_pdf/fintech_art_{aid}_{safe_slug}.pdf"
                        pdf_dest = os.path.join(media_root, pdf_filename)
                        downloads.append((pdf_url, pdf_dest))
                        rel_pdf_path = pdf_filename

                author_info = a.get('author') or {}
                authors_str = (author_info.get('name') or '').strip()
                lang = detect_language(main_title)

                art_obj, _ = Article.objects.get_or_create(
                    journal=j,
                    issue=issue,
                    title=main_title,
                    defaults={
                        'title_uz': title_uz or None,
                        'title_ru': title_ru or None,
                        'title_en': title_en or None,
                        'authors': authors_str,
                        'author': admin_user,
                        'category': cat_obj,
                        'article_language': lang,
                        'status': 'published',
                        'order_in_issue': order_index,
                        'views_count': 15 + (aid * 7) % 65,
                        'downloads_count': 5 + (aid * 3) % 25,
                    }
                )
                art_obj.authors = authors_str
                art_obj.category = cat_obj
                art_obj.status = 'published'
                art_obj.order_in_issue = order_index
                if rel_pdf_path:
                    art_obj.pdf_file.name = rel_pdf_path
                art_obj.save()

                created_articles += 1
                order_index += 1

        issue.save()

    print(f"\nCreated/updated {created_issues} issues and {created_articles} articles in DB.", flush=True)
    print(f"Total files in download queue: {len(downloads)}. Starting download...", flush=True)

    success_count = 0
    fail_count = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(download_file, url, dest): (url, dest) for url, dest in downloads}
        done = 0
        for future in as_completed(future_map):
            done += 1
            try:
                res = future.result()
                if res:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1
            if done % 20 == 0 or done == len(downloads):
                print(f"  Progress: {done}/{len(downloads)} files downloaded ({success_count} ok, {fail_count} failed)", flush=True)

    print(f"=== FINTECH MIGRATION COMPLETE! Total ok: {success_count}, failed: {fail_count} ===", flush=True)

if __name__ == '__main__':
    run_migration()
