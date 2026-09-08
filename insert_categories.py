import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from journal.models import ArticleCategory

categories = [
    ("18.00.00", "Arxitektura va shaharsozlik fanlari"),
    ("05.00.00", "Texnika fanlari va qurilish muhandisligi"),
    ("13.00.00", "Pedagogika va ta'lim texnologiyalari"),
    ("17.00.00", "San'atshunoslik va dizayn fanlari"),
    ("08.00.00", "Iqtisodiyot va biznesni boshqarish"),
    ("10.00.00", "Filologiya va tillarni o'qitish metodikasi"),
    ("01.00.00", "Fizika-matematika fanlari"),
    ("07.00.00", "Tarix va madaniy meros fanlari"),
    ("09.00.00", "Falsafa va ijtimoy-gumanitar fanlar"),
    ("19.00.00", "Psixologiya va inson resurslari"),
    ("22.00.00", "Sotsiologiya va jamiyatshunoslik"),
]

for i, (code, name) in enumerate(categories):
    cat, created = ArticleCategory.objects.update_or_create(
        code=code,
        defaults={'name': name, 'order': i + 1}
    )
    status = "Qo'shildi" if created else "Yangilandi"
    print(f"[{status}] {code} - {name}")

print("Barcha yo'nalishlar ma'lumotlar bazasiga muvaffaqiyatli saqlandi!")
