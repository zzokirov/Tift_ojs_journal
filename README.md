# TIFT Ilmiy Jurnallari Portali — Markazlashgan Ilmiy Nashriyot Platformasi

**Toshkent Xalqaro Moliyaviy Boshqaruv va Texnologiyalar Universiteti**  
Ilmiy-elektron jurnallar portali (Multi-Journal Publishing Platform)

🌐 **Rasmiy portal:** https://jurnal.tift.uz / https://architect-edu.tift.uz  
⚙️ **Backend:** Python 3.10+ / Django 5.2 / 6.0  
🗄 **Ma'lumotlar bazasi:** PostgreSQL 16  
🎨 **Frontend:** HTML5, Tailwind CSS, JavaScript  
📄 **PDF Dvigateli:** PyMuPDF (fitz), xhtml2pdf  
🛡 **Xavfsizlik & Tahririyat:** Double-blind review (Taqrizchilarsiz ichki nazorat)

---

## 1. Loyiha arxitekturasi va umumiy ma'lumot

Ushbu platforma TIFT Universiteti tasarrufidagi barcha ilmiy jurnallarni yagona markazlashgan boshqaruv tizimi ostida birlashtiradi. Har bir jurnal mustaqil ilmiy yo'nalishga, o'zining tahririyat hay'atiga, ISSN raqamlariga, muqovalariga va chop etilgan sonlar arxiviga ega bo'ladi.

### Asosiy tamoyillar:
- **Ko'p jurnallilik (Multi-tenant):** Yangi jurnal ochish uchun alohida veb-sayt yoki alohida Django loyihasi yaratish shart emas. Bosh administrator barcha jurnallarni yagona boshqaruv panelidan (`/admin/`) qo'shadi va boshqaradi.
- **Akademik bosh sahifa (Journal Catalog First):** Kirish sahifasida ortiqcha dashboard panellari yoki soxta statistika ko'rsatilmaydi. Bosh sahifa to'liq ilmiy katalog, real qidiruv (nomi, ISSN, ilmiy yo'nalish bo'yicha) va jurnallarga to'g'ridan-to'g'ri kirish imkonini beradi.
- **Uch tildagi mustaqil muqovalar:** Har bir jurnal uchun o'zbekcha (`cover_uz`), ruscha (`cover_ru`) va inglizcha (`cover_en`) vertikal muqovalar yuklanadi. Foydalanuvchi tilni o'zgartirganda tizim mos muqovani avtomatik ko'rsatadi (fallback kaskadi: tanlangan til → asosiy til → o'zbekcha).
- **Taqrizchilar hisobisiz tahririyat nazorati:** Taqrizchilar uchun alohida ro'yxatdan o'tish yoki login parollari talab etilmaydi. Administrator maqola PDF nusxasini taqrizchiga tashqaridan (masalan, email orqali) yuboradi va uning xulosasi hamda maxfiy hisobotini `ReviewRecord` modelida qayd etadi.
- **Boshqariladigan PDF nashr tizimi:** Maqolalar qabul qilingandan so'ng tegishli jurnal soniga biriktiriladi. Tizim avtomatik tarzda sahifalar oralig'ini hisoblaydi, mundarija (TOC) tuzadi va to'liq to'plam PDF faylini yig'adi. Administrator tasdiqlamasidan oldin hech qanday son saytda ommaviy ko'rsatilmaydi.

---

## 2. Loyiha tuzilmasi

```
Tift_ojs_journal/
├── core/                       # Django asosiy sozlamalari
│   ├── settings.py             # I18N, Jazzmin, PostgreSQL, xavfsizlik sozlamalari
│   ├── urls.py                 # Asosiy marshrutlar va i18n
│   └── wsgi.py
├── journal/                    # Asosiy jurnal ilovasi
│   ├── models.py               # Journal, JournalIssue, Article, StaffMember, ReviewRecord
│   ├── views.py                # Portal, jurnal, arxiv, maqola va PDF generatsiya
│   ├── admin.py                # Jazzmin admin boshqaruvi va ReviewRecordInline
│   ├── forms.py                # Maqola topshirish va foydalanuvchi shakllari
│   ├── tests.py                # 10 ta avtomatlashtirilgan unit testlar
│   ├── translation.py          # Modeltranslation (uz, ru, en)
│   └── urls.py                 # Jurnallar bo'yicha dinamik URL lar
├── templates/                  # HTML shablonlar
│   ├── base.html               # Asosiy shablon va navigatsiya
│   ├── portal_home.html        # Akademik katalog va qidiruvli bosh sahifa
│   ├── index.html              # Tanlangan jurnalning asosiy sahifasi
│   ├── about.html              # Tahririyat hay'ati va jurnal haqida ma'lumot
│   ├── archive.html            # Chop etilgan sonlar arxivi
│   └── journal/
│       └── issue_detail.html   # Jurnal soni va maqolalar ro'yxati
├── static/                     # CSS, JS, TIFT rasmiy logotipi
├── media/                      # Yuklangan maqola, muqova va tahririyat fayllari
└── requirements.txt
```

---

## 3. O'rnatish va mahalliy (Local) ishga tushirish

### 3.1 Talablar:
- Python 3.10 yoki undan yuqori
- PostgreSQL 14+ (yoki lokal test uchun SQLite)
- Virtual muhit (venv)

### 3.2 O'rnatish qadamlari:

```bash
# 1. Repozitoriyani klonlash
git clone https://github.com/zzokirov/Tift_ojs_journal.git
cd Tift_ojs_journal

# 2. Virtual muhit yaratish va faollashtirish
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Kerakli paketlarni o'rnatish
pip install -r requirements.txt

# 4. Muhit o'zgaruvchilarini sozlash (.env)
cp .env.example .env
# .env faylida DATABASE_URL, SECRET_KEY va ALLOWED_HOSTS ni to'ldiring

# 5. Migratsiyalarni qo'llash
python manage.py migrate

# 6. Administrator (Superuser) yaratish
python manage.py createsuperuser

# 7. Mahalliy serverni ishga tushirish
python manage.py runserver
```

Brauzerda: `http://127.0.0.1:8000/`

---

## 4. Avtomatlashtirilgan testlarni ishga tushirish

Loyiha to'liq xavfsizlik va izolyatsiya testlari bilan ta'minlangan. Testlarni ishga tushirish:

```bash
python manage.py test journal
```

### Sinovdan o'tuvchi mezonlar:
1. **Jurnallar izolyatsiyasi:** Bir nechta jurnallarda bir xil son raqamlarining mustaqil ishlashi, ayni bir jurnalda dublikat sonlarning rad etilishi.
2. **Tahririyat hay'ati chegaralanishi:** A'zolar faqat o'zlari biriktirilgan jurnal sahifasida ko'rinishi.
3. **Maqolalar nazorati:** Maqolani boshqa jurnal soniga biriktirish taqiqlanishi; faqat qabul qilingan maqolalar sonlarga qo'shilishi.
4. **Taqriz tizimi:** Taqrizchi hisobisiz `ReviewRecord` yaratilishi va maxfiy ma'lumotlarning himoyasi.
5. **Ommaviy sahifalar:** Bosh sahifa (200), qidiruv filtrlari va mavjud bo'lmagan jurnallar uchun 404 xatosi.

---

## 5. Tahririyat va nashr jarayoni (Administrator qo'llanmasi)

1. **Yangi jurnal yaratish:** `/admin/` panelida `Jurnallar` bo'limiga kirib, yangi jurnal nomi, slug (masalan: `moliya`), ISSN, tavsif va 3 tildagi muqovalarni yuklang.
2. **Tahririyat a'zolarini kiritish:** `Tahririyat a'zolari` bo'limida har bir a'zoning lavozimi, ilmiy darajasi (DSc, PhD), ilmiy unvoni (Professor, Dotsent) va ish joyini ko'rsatib, tegishli jurnalga biriktiring.
3. **Maqola qabul qilish va taqriz:** Muallif maqolani sayt orqali yuboradi. Administrator uni ko'rib chiqib, tashqi taqrizchiga yuboradi va natijasini maqola ichidagi `Taqriz qaydlari` (Review Records) qismida qayd etadi.
4. **Jurnal sonini shakllantirish va chop etish:** Qabul qilingan maqolalar jurnal soniga biriktiriladi. Barcha maqolalar tartiblangach, administrator son holatini `Nashr etilgan` (Published) qilib tasdiqlaydi.

---

## 6. Litsenziya va mualliflik huquqi

© 2026 Toshkent Xalqaro Moliyaviy Boshqaruv va Texnologiyalar Universiteti (TIFT).  
Barcha huquqlar himoyalangan.
