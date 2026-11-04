import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from journal.models import ArticleCategory, StaffMember

# Category translations
cat_translations = {
    'Geologiya-mineralogiya fanlari': {
        'ru': 'Науки о геологии и минералогии',
        'en': 'Geology and Mineralogy Sciences'
    },
    'Arxitektura va shaharsozlik fanlari': {
        'ru': 'Науки об архитектуре и градостроительстве',
        'en': 'Architecture and Urban Planning Sciences'
    },
    'Texnika fanlari va qurilish muhandisligi': {
        'ru': 'Технические науки и строительная инженерия',
        'en': 'Technical Sciences and Construction Engineering'
    },
    "Pedagogika va ta'lim texnologiyalari": {
        'ru': 'Педагогика и образовательные технологии',
        'en': 'Pedagogy and Educational Technologies'
    },
    "San'atshunoslik va dizayn fanlari": {
        'ru': 'Науки об искусстве и дизайне',
        'en': 'Arts and Design Sciences'
    },
    'Iqtisodiyot va biznesni boshqarish': {
        'ru': 'Экономика и управление бизнесом',
        'en': 'Economics and Business Management'
    },
    "Filologiya va tillarni o'qitish metodikasi": {
        'ru': 'Филология и методика преподавания языков',
        'en': 'Philology and Language Teaching Methodology'
    },
    'Fizika-matematika fanlari': {
        'ru': 'Физико-математические науки',
        'en': 'Physics and Mathematics Sciences'
    },
    'Tarix va madaniy meros fanlari': {
        'ru': 'История и науки о культурном наследии',
        'en': 'History and Cultural Heritage Sciences'
    },
    'Falsafa va ijtimoy-gumanitar fanlar': {
        'ru': 'Философия и социально-гуманитарные науки',
        'en': 'Philosophy and Social Humanities'
    },
    'Psixologiya va inson resurslari': {
        'ru': 'Психология и управление человеческими ресурсами',
        'en': 'Psychology and Human Resources'
    },
    'Sotsiologiya va jamiyatshunoslik': {
        'ru': 'Социология и обществоведение',
        'en': 'Sociology and Social Studies'
    },
}

for cat in ArticleCategory.objects.all():
    t = cat_translations.get(cat.name_uz)
    if t:
        cat.name_ru = t['ru']
        cat.name_en = t['en']
        cat.save()
        print('OK CAT:', cat.name_uz)
    else:
        print('MISSING CAT:', cat.name_uz)

# Staff - set workplace translations
# For workplace 'TIFT universiteti' -> RU/EN
workplace_translations = {
    'TIFT universiteti': {'ru': 'ТИФТ университет', 'en': 'TIFT University'},
    'TIFT Universiteti': {'ru': 'ТИФТ университет', 'en': 'TIFT University'},
    'O\'zbekiston milliy pedagogika universiteti': {'ru': 'Национальный педагогический университет Узбекистана', 'en': 'National Pedagogical University of Uzbekistan'},
    'Toshkent davlat iqtisodiyot universiteti': {'ru': 'Ташкентский государственный экономический университет', 'en': 'Tashkent State University of Economics'},
    'Toshkent davlat sharqshunoslik universiteti': {'ru': 'Ташкентский государственный университет востоковедения', 'en': 'Tashkent State University of Oriental Studies'},
    'Samarqand davlat universiteti': {'ru': 'Самаркандский государственный университет', 'en': 'Samarkand State University'},
    'O\'zbekiston Milliy universiteti': {'ru': 'Национальный университет Узбекистана', 'en': 'National University of Uzbekistan'},
    'Ijtimoiy-ma\'naviy tadqiqotlar instituti': {'ru': 'Институт социально-духовных исследований', 'en': 'Institute of Social and Spiritual Research'},
    '"Profi University"': {'ru': '«Profi University»', 'en': 'Profi University'},
    'O\'zDJTSU': {'ru': 'УзДЖТСУ', 'en': 'UzDJTSU'},
}

for staff in StaffMember.objects.all():
    # Names stay the same (don't translate names)
    staff.full_name_ru = staff.full_name_uz
    staff.full_name_en = staff.full_name_uz

    # Translate workplace
    wp = staff.workplace_uz or ''
    wt = workplace_translations.get(wp)
    if wt:
        staff.workplace_ru = wt['ru']
        staff.workplace_en = wt['en']
    else:
        # Default: keep same but at least copy
        staff.workplace_ru = wp
        staff.workplace_en = wp

    staff.save()
    print('OK STAFF:', staff.full_name_uz, '| workplace_ru:', staff.workplace_ru)

print('ALL DONE')
