# TIFT Ilmiy Jurnali — "Arxitektura va Ta'lim"

**Toshkent Xalqaro Moliyaviy Boshqaruv va Texnologiyalar Universiteti**  
Ilmiy-elektron jurnal boshqaruv tizimi

🌐 **Demo:** https://tift-ojs-journal.onrender.com

---

## Loyiha haqida

Bu loyiha **Django** asosida qurilgan ilmiy jurnal boshqaruv tizimi bo'lib, quyidagi imkoniyatlarni taqdim etadi:

- Ilmiy maqolalar nashr etish va boshqarish
- Muallif ro'yxatdan o'tish va shaxsiy kabinet
- PDF maqolalar yuklash va yuklab olish
- Jurnal arxivlari (jild/son bo'yicha)
- Double-blind peer review jarayoni
- Tahririyat a'zolari sahifasi
- Tashrif buyuruvchilar statistikasi
- Zamonaviy responsive dizayn

---

## Texnologiyalar

| Texnologiya | Maqsad |
|-------------|--------|
| Django 6.0 | Backend framework |
| PostgreSQL | Ma'lumotlar bazasi |
| Tailwind CSS | UI dizayn |
| Django Jazzmin | Admin panel |
| Whitenoise | Static fayllar |
| Gunicorn | Production server |
| Render.com | Hosting |

---

## Mahalliy o'rnatish

```bash
# 1. Repozitoriyani klonlash
git clone https://github.com/zzokirov/Tift_ojs_journal.git
cd Tift_ojs_journal

# 2. Virtual muhit yaratish
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 4. Migration
python manage.py migrate

# 5. Superuser yaratish
python manage.py createsuperuser

# 6. Serverni ishga tushirish
python manage.py runserver
```

Brauzerda: `http://127.0.0.1:8000`

---

## Muhit o'zgaruvchilari (.env)

```
DATABASE_URL=postgres://...
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=yourpassword
DJANGO_SUPERUSER_EMAIL=admin@tift.uz
```

---

## Loyiha tuzilmasi

```
journal_tift/
├── core/               # Django sozlamalari
│   ├── settings.py
│   └── urls.py
├── journal/            # Asosiy ilova
│   ├── models.py       # User, Article, JournalIssue, StaffMember
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── forms.py
├── templates/          # HTML shablonlar
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── archive.html
│   ├── article_detail.html
│   ├── dashboard_base.html
│   ├── my_articles.html
│   ├── profile.html
│   └── ...
├── static/             # CSS, JS, rasmlar
├── media/              # Yuklangan fayllar
├── build.sh            # Render deploy skripti
└── requirements.txt
```

---

## Admin panel

`/admin/` — Jazzmin admin paneli orqali boshqarish:
- **Maqolalar** — holat o'zgartirish, jurnal soniga biriktirish
- **Jurnal sonlari** — nashr/yashirish
- **Foydalanuvchilar** — rollarni boshqarish
- **Tahririyat a'zolari** — rasm, lavozim, ish joyi

---

## Muallif

**Sanjar Zokirov**  
TIFT Universiteti  
📧 journal@tift.uz

---

## Litsenziya

© 2026 TIFT Ilmiy Jurnali. Barcha huquqlar himoyalangan.
