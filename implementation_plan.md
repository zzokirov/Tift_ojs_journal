# Zamonaviy Jurnal Boshqaruv Paneli (Admin Dashboard) Rejasi

Foydalanuvchi talabiga asosan, Django Admin (Jazzmin) panelini OJS va Elsevier uslubidagi zamonaviy, premium SaaS ko'rinishiga keltirish rejalashtirildi. 

## User Review Required
> [!IMPORTANT]
> Admin panelga TailwindCSS ulasak, Jazzmin (Bootstrap 4) dizayni bilan ziddiyat (conflict) kelib chiqishi mumkin. Shuning uchun, men dashboard sahifasi uchun maxsus scoped (ajratilgan) CSS va Bootstrap 4 utilitalarini ishlatishni taklif qilaman. 
> 
> Shuningdek, siz so'ragan ayrim maqola holatlari (Masalan: "Tuzatish uchun qaytarilgan", "Nashrga tayyor", "Dastlabki tekshiruv") hozirgi bazada (`STATUS_CHOICES`) yo'q. Ushbu holatlarni modelga qo'shish kerak bo'ladi.

## Open Questions
1. Yangi maqola holatlari bazaga (va ma'lumotlar bazasi migratsiyasiga) qo'shilsinmi?
2. Boshqaruv panelida ishlatiladigan til faqat O'zbek tilida bo'ladimi yoki ko'p tillikni (i18n) saqlab qolaylikmi?

## Proposed Changes

### Model va Sozlamalar (Backend)
---
#### [MODIFY] journal/models.py
- `Article.STATUS_CHOICES` ga yangi holatlar qo'shiladi (Yangi, Dastlabki tekshiruv, Tuzatishga qaytarilgan, Nashrga tayyor).

#### [MODIFY] core/settings.py
- `JAZZMIN_SETTINGS` da yon panel (sidebar) menyusi sozlanadi.
- `custom_links` orqali "Maqolalar" menyusiga sub-menyular (status bo'yicha filtrlar, masalan `?status__exact=submitted`) qo'shiladi.

#### [NEW] core/templatetags/admin_dashboard.py
- Dashboard uchun ma'lumotlarni bazadan olib beradigan maxsus Django template taglari yoziladi:
  - `get_dashboard_stats()`: Jami maqolalar, yangi, qabul qilingan va h.k.
  - `get_latest_articles()`: Oxirgi kelib tushgan maqolalar ro'yxati.
  - `get_upcoming_issue()`: Kelgusi nashr soni haqida progress bar ma'lumotlari.
  - `get_admin_logs()`: So'nggi harakatlar (Recent Activity) tarixi.

### Shablonlar (Frontend)
---
#### [NEW] templates/admin/index.html
- Jazzminning standart dashboard'ini to'liq qayta yozamiz.
- **Top Cards**: O'qilishi oson, katta raqamlar va piktogrammalar (Lucide/FontAwesome).
- **Charts**: Chart.js orqali oylik statistika va maqolalar yo'nalishi bo'yicha grafiklar.
- **Data Table**: Eng so'nggi maqolalar ro'yxati, chiroyli status badgelari bilan.
- **Quick Actions & Activity**: O'ng tomonda tezkor amallar va xronologiya (timeline).

#### [NEW] static/css/admin_dashboard.css
- Zamonaviy dizayn (soft shadows, rounded corners, professional typography) uchun maxsus CSS stillari.

## Verification Plan
### Manual Verification
1. Admin panelga kirilganda yangi chiroyli dashboard ochilishi tekshiriladi.
2. Yon paneldagi "Maqolalar" ro'yxatida statuslar bo'yicha saralash ishlayotgani tekshiriladi.
3. Barcha grafiklar va statistikalar ma'lumotlar bazasiga ulanib, to'g'ri ishlashi tekshiriladi.
