import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


def user_avatar_path(instance, filename):
    # Path traversal himoyasi: faqat kengaytmani olish, yo'lni butunlay almashtirish
    import os
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    allowed = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
    if ext not in allowed:
        ext = 'jpg'
    return f"avatars/{uuid.uuid4()}.{ext}"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('author', _('Muallif')),
        ('reviewer', _('Taqrizchi')),
        ('editor', _('Muharrir')),
    )
    GENDER_CHOICES = (
        ('male', _('Erkak')),
        ('female', _('Ayol')),
    )
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='author')
    institution = models.CharField(max_length=255, blank=True, verbose_name=_("Ish/O'qish joyi"))
    avatar      = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, verbose_name=_("Profil rasmi"))
    bio         = models.TextField(blank=True, verbose_name=_("O'zim haqimda"))
    phone       = models.CharField(max_length=20, blank=True, verbose_name=_("Telefon raqam"))
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name=_("Jinsi"))
    country     = models.CharField(max_length=100, null=True, blank=True, default="O'zbekiston", verbose_name=_("Davlat"))

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"



class Journal(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Qoralama')),
        ('published', _('Nashr etilgan')),
        ('archived', _('Arxivlangan')),
    )

    title = models.CharField(max_length=255, verbose_name=_("Jurnal nomi"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("URL Slug (masalan: arxitektura)"))
    short_description = models.TextField(blank=True, verbose_name=_("Qisqacha tavsif"))
    full_description = models.TextField(blank=True, verbose_name=_("To'liq tavsif"))
    description = models.TextField(blank=True, verbose_name=_("Jurnal haqida (eski)"))
    logo = models.ImageField(upload_to='journals/logos/', blank=True, null=True, verbose_name=_("Jurnal logotipi"))

    # Uch tildagi alohida muqovalar
    cover_image = models.ImageField(upload_to='journals/', blank=True, null=True, verbose_name=_("Asosiy muqova (eski)"))
    cover_uz = models.ImageField(upload_to='journals/covers/', blank=True, null=True, verbose_name=_("Muqova (O'zbekcha)"))
    cover_ru = models.ImageField(upload_to='journals/covers/', blank=True, null=True, verbose_name=_("Muqova (Ruscha)"))
    cover_en = models.ImageField(upload_to='journals/covers/', blank=True, null=True, verbose_name=_("Muqova (Inglizcha)"))

    # Identifikator va nashriyot ma'lumotlari
    issn = models.CharField(max_length=50, blank=True, verbose_name=_("ISSN (Print)"))
    eissn = models.CharField(max_length=50, blank=True, verbose_name=_("eISSN (Online)"))
    publisher_name = models.CharField(max_length=255, default="Toshkent Xalqaro Moliyaviy Boshqaruv va Texnologiyalar Universiteti", verbose_name=_("Nashriyot"))
    publication_frequency = models.CharField(max_length=100, default=_("Yiliga 4 marta"), verbose_name=_("Nashr davriyligi"))
    primary_language = models.CharField(max_length=10, default="uz", choices=(('uz', "O'zbek"), ('ru', "Rus"), ('en', "Ingliz")), verbose_name=_("Asosiy til"))
    supported_languages = models.CharField(max_length=100, default="uz,ru,en", verbose_name=_("Qo'llab-quvvatlanadigan tillar"))
    research_areas = models.TextField(blank=True, verbose_name=_("Ilmiy yo'nalishlar"))

    # Aloqa va talablar
    editorial_email = models.EmailField(blank=True, default="journal@tift.uz", verbose_name=_("Tahririyat elektron pochtasi"))
    submission_guidelines = models.TextField(blank=True, verbose_name=_("Maqola yuborish talablari"))
    website_url = models.URLField(blank=True, verbose_name=_("Tashqi vebsayt havolasi"))

    # Tashqi ko'rinish va tartib
    theme_color = models.CharField(max_length=20, default="#1B5B9E", verbose_name=_("Asosiy rang"))
    secondary_color = models.CharField(max_length=20, default="#16a34a", verbose_name=_("Qo'shimcha rang"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Tartib raqami"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Tavsiya etilgan"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))
    publication_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', verbose_name=_("Nashr holati"))
    founded_year = models.PositiveIntegerField(default=2024, verbose_name=_("Tashkil etilgan yili"))

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Nashr etilgan sana"))
    
    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = _("Jurnal")
        verbose_name_plural = _("Jurnallar")

    def __str__(self):
        return self.title

    def get_cover_for_language(self, lang_code=None):
        if not lang_code:
            from django.utils.translation import get_language
            lang_code = get_language() or 'uz'
        
        # 1. Tanlangan til muqovasi
        if lang_code == 'ru' and self.cover_ru:
            return self.cover_ru
        elif lang_code == 'en' and self.cover_en:
            return self.cover_en
        elif lang_code == 'uz' and self.cover_uz:
            return self.cover_uz

        # 2. Asosiy til muqovasi
        if self.primary_language == 'ru' and self.cover_ru:
            return self.cover_ru
        if self.primary_language == 'en' and self.cover_en:
            return self.cover_en
        if self.cover_uz:
            return self.cover_uz

        # 3. Eski cover_image
        if self.cover_image:
            return self.cover_image

        # 4. Mavjud bo'lgan har qanday muqova
        return self.cover_ru or self.cover_en or None

    @property
    def active_cover(self):
        return self.get_cover_for_language()

class JournalIssue(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='issues', verbose_name=_("Jurnal"), null=True, blank=True)
    volume = models.PositiveIntegerField(verbose_name=_("Jurnal jildi (Volume)"))
    number = models.PositiveIntegerField(verbose_name=_("Jurnal soni (Issue)"))
    year = models.PositiveIntegerField(verbose_name=_("Chop etilgan yili"))
    period = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Davri (Masalan: 1-chorak, Yanvar-Mart)"))
    cover_image = models.ImageField(upload_to='issues/', blank=True, null=True, verbose_name=_("Oldi muqovasi (rasmi)"))
    back_cover_image = models.ImageField(upload_to='issues/', blank=True, null=True, verbose_name=_("Orqa muqovasi (rasmi)"))
    editorial_doc = models.FileField(upload_to='issues_docs/', blank=True, null=True, verbose_name=_("Muqova va Tahririyat Word hujjati (.docx)"), help_text=_("Word (.docx) fayl. Nashr boshidagi muqova va tahririyat a'zolari sahifasi uchun."))
    full_pdf = models.FileField(upload_to='issues_pdf/', blank=True, null=True, verbose_name=_("To'liq to'plam (PDF)"))
    STATUS_CHOICES = (
        ('draft', _('Qoralama')),
        ('preparation', _('Tayyorlanmoqda')),
        ('ready', _('Nashrga tayyor')),
        ('published', _('Nashr etilgan')),
        ('archived', _('Arxivlangan')),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', verbose_name=_("Holati"))
    quarter = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Chorak (1-4)"))
    title = models.CharField(max_length=255, blank=True, verbose_name=_("Mavzu / Maxsus son nomi"))
    description = models.TextField(blank=True, verbose_name=_("Son haqida tavsif"))
    toc_pdf = models.FileField(upload_to='issues_toc/', blank=True, null=True, verbose_name=_("Mundarija (PDF)"))
    publication_date = models.DateField(null=True, blank=True, verbose_name=_("Rasmiy nashr sanasi"))
    is_published = models.BooleanField(default=False, verbose_name=_("Saytda ko'rsatish"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-year', '-volume', '-number']
        verbose_name = _("Jurnal soni")
        verbose_name_plural = _("Jurnal sonlari")

    def __str__(self):
        return f"{self.year}-yil, {self.number}-son"


def article_upload_path(instance, filename):
    # Path traversal himoyasi: kengaytmani tekshirish
    import os
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    allowed = {'pdf', 'doc', 'docx'}
    if ext not in allowed:
        ext = 'pdf'
    return f"articles_pdf/{uuid.uuid4()}.{ext}"


def article_template_pdf_path(instance, filename):
    import os
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    allowed = {'pdf', 'docx'}
    if ext not in allowed:
        ext = 'pdf'
    return f"articles_template/{uuid.uuid4()}.{ext}"


# ─── YO'NALISH / KATEGORIYA ───────────────────────────────────────────────────

class ArticleCategory(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='categories', verbose_name=_("Jurnal"), null=True, blank=True)
    code  = models.CharField(max_length=20, unique=True, verbose_name=_("Kod (masalan: 18.00.00)"))
    name  = models.CharField(max_length=200, verbose_name=_("Nomi"))
    icon  = models.CharField(max_length=50, blank=True, default='', verbose_name=_("Ikona klasi (masalan: fa-building)"), help_text=_("FontAwesome ikona klasi (bo'sh bo'lsa avtomatik mos ikona tanlanadi)"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Tartib"))

    class Meta:
        ordering = ['order', 'code']
        verbose_name = _("Yo'nalish")
        verbose_name_plural = _("Yo'nalishlar")

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def icon_class(self):
        if self.icon:
            return self.icon
        mapping = {
            "18.00.00": "fa-building",         # Arxitektura va shaharsozlik fanlari
            "05.00.00": "fa-tools",            # Texnika fanlari va qurilish muhandisligi
            "13.00.00": "fa-graduation-cap",   # Pedagogika va ta'lim texnologiyalari
            "17.00.00": "fa-palette",          # San'atshunoslik va dizayn fanlari
            "08.00.00": "fa-chart-line",       # Iqtisodiyot va biznesni boshqarish
            "10.00.00": "fa-language",         # Filologiya va tillarni o'qitish metodikasi
            "01.00.00": "fa-atom",             # Fizika-matematika fanlari
            "07.00.00": "fa-landmark",         # Tarix va madaniy meros fanlari
            "09.00.00": "fa-brain",            # Falsafa va ijtimoy-gumanitar fanlar
            "19.00.00": "fa-user-friends",     # Psixologiya va inson resurslari
            "22.00.00": "fa-users",            # Sotsiologiya va jamiyatshunoslik
        }
        return mapping.get(self.code, "fa-microscope")


class Article(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='articles_set', verbose_name=_("Jurnal"), null=True, blank=True)
    STATUS_CHOICES = (
        ('submitted', _('Yangi maqola')),
        ('initial_review', _('Dastlabki tekshiruv')),
        ('under_review', _('Taqriz jarayonida')),
        ('returned', _('Tuzatish uchun qaytarilgan')),
        ('accepted', _('Qabul qilingan')),
        ('rejected', _('Rad etilgan')),
        ('ready_to_publish', _('Nashrga tayyor')),
        ('published', _('Nashr etilgan')),
    )

    # Asosiy ma'lumotlar
    title    = models.CharField(max_length=500, verbose_name=_("Maqola sarlavhasi"))
    authors  = models.CharField(max_length=500, blank=True, verbose_name=_("Mualliflar (to'liq ro'yxat)"))
    abstract = models.TextField(verbose_name=_("Annotatsiya / Abstract"))
    keywords = models.CharField(max_length=255, verbose_name=_("Kalit so'zlar (vergul bilan ajrating)"))
    ARTICLE_LANG_CHOICES = (
        ('uz', "O'zbek"),
        ('ru', "Русский"),
        ('en', "English"),
    )
    article_language = models.CharField(max_length=10, choices=ARTICLE_LANG_CHOICES, default='uz', verbose_name=_("Maqola tili"))
    word_file        = models.FileField(upload_to='articles_word/', null=True, blank=True, verbose_name=_("Asl Word hujjati (.docx)"))
    admin_notes      = models.TextField(blank=True, verbose_name=_("Maxfiy tahririyat qaydlari"))
    order_in_issue   = models.PositiveIntegerField(default=0, verbose_name=_("Sondagi tartib raqami"))
    corresponding_author_name  = models.CharField(max_length=255, blank=True, verbose_name=_("Aloqa uchun muallif"))
    corresponding_author_email = models.EmailField(blank=True, verbose_name=_("Aloqa uchun email"))
    corresponding_author_phone = models.CharField(max_length=50, blank=True, verbose_name=_("Aloqa uchun telefon"))

    # Muallif (tizim foydalanuvchisi) va jurnal
    author   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name=_("Muallif (foydalanuvchi)"))
    issue    = models.ForeignKey(JournalIssue, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name=_("Jurnal soni"))
    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name=_("Yo'nalish"))

    # Sahifalash (Paginatsiya)
    start_page = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Boshlanish sahifasi (To'plamda)"))
    end_page   = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Tugash sahifasi (To'plamda)"))

    # Holat
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted', verbose_name=_("Maqola holati"))

    # Maqola matni (HTML)
    content = models.TextField(blank=True, verbose_name=_("Maqola matni (HTML)"))

    # Fayllar
    pdf_file     = models.FileField(upload_to=article_upload_path, null=True, blank=True, verbose_name=_("Fayl (PDF yoki Word .docx)"))
    template_pdf = models.FileField(upload_to=article_template_pdf_path, null=True, blank=True, verbose_name=_("Shablon PDF (tahririyat tomonidan)"))

    # Taqriz va tahririyat xulosasi
    assigned_reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_articles', verbose_name=_("Biriktirilgan taqrizchi"))
    review_notes = models.TextField(blank=True, verbose_name=_("Taqrizchi izohi / Rad etish sababi"))
    reviewed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_articles', verbose_name=_("Taqrizchi / Muharrir"))
    reviewed_at  = models.DateTimeField(null=True, blank=True, verbose_name=_("Taqriz qilingan sana"))

    # Chop etilgan sana
    published_at = models.DateField(null=True, blank=True, verbose_name=_("Chop etilgan sana"))

    # Statistika
    views_count     = models.PositiveIntegerField(default=0, verbose_name=_("Ko'rishlar soni"))
    downloads_count = models.PositiveIntegerField(default=0, verbose_name=_("Yuklab olishlar soni"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yuborilgan sana"))
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def parsed_authors(self):
        authors_list = []
        if self.authors and '|' in self.authors:
            for block in self.authors.split(';'):
                parts = [p.strip() for p in block.split('|')]
                if len(parts) >= 2:
                    authors_list.append({"name": parts[0], "inst": parts[1]})
                elif len(parts) == 1:
                    authors_list.append({"name": parts[0], "inst": ""})
        return authors_list

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Maqola")
        verbose_name_plural = _("Maqolalar")

    def __str__(self):
        return self.title


class SiteVisit(models.Model):
    date       = models.DateField(auto_now_add=True, verbose_name=_("Sana"))
    ip_address = models.GenericIPAddressField(verbose_name=_("IP manzil"))

    class Meta:
        verbose_name = _("Tashrif")
        verbose_name_plural = _("Tashriflar")
        unique_together = ('date', 'ip_address')

    def __str__(self):
        return f"{self.ip_address} — {self.date}"


def staff_photo_path(instance, filename):
    import os
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    allowed = {'jpg', 'jpeg', 'png', 'webp'}
    if ext not in allowed:
        ext = 'jpg'
    return f"staff_photos/{uuid.uuid4()}.{ext}"


class StaffMember(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='staff', verbose_name=_("Jurnal"), null=True, blank=True)
    POSITION_CHOICES = (
        ('editor_in_chief', _('Bosh muharrir')),
        ('deputy_editor',   "O'rinbosar muharrir"),
        ('editor', _('Muharrir')),
        ('reviewer', _('Taqrizchi')),
        ('secretary', _('Kotib')),
        ('member',          'A\'zo'),
    )

    full_name   = models.CharField(max_length=255, verbose_name=_("Ism Familiya"))
    position    = models.CharField(max_length=30, choices=POSITION_CHOICES, default='member', verbose_name=_("Lavozim"))
    academic_degree = models.CharField(max_length=100, blank=True, verbose_name=_("Ilmiy daraja (DSc, PhD, f.n., h.k.)"))
    academic_title  = models.CharField(max_length=100, blank=True, verbose_name=_("Ilmiy unvon (Professor, Dotsent, h.k.)"))
    workplace   = models.CharField(max_length=255, verbose_name=_("Ish joyi"))
    institution = models.CharField(max_length=255, blank=True, verbose_name=_("Muassasa / Tashkilot"))
    email       = models.EmailField(blank=True, verbose_name=_("Email (maxfiy)"))
    show_email  = models.BooleanField(default=False, verbose_name=_("Emailni saytda ko'rsatish"))
    age         = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Yoshi"))
    photo       = models.ImageField(upload_to=staff_photo_path, null=True, blank=True, verbose_name=_("Rasmi"))
    bio         = models.TextField(blank=True, verbose_name=_("Qisqacha ma'lumot"))
    order       = models.PositiveIntegerField(default=0, verbose_name=_("Tartib raqami"))
    is_active   = models.BooleanField(default=True, verbose_name=_("Ko'rsatish"))

    class Meta:
        ordering = ['order', 'full_name']
        verbose_name = _("Jurnal a'zosi")
        verbose_name_plural = _("Jurnal a'zolari")

    def __str__(self):
        return f"{self.full_name} — {self.get_position_display()}"


# ─── KONFERENSIYALAR ─────────────────────────────────────────────────────────

class Conference(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='conferences', verbose_name=_("Jurnal"), null=True, blank=True)
    title       = models.CharField(max_length=300, verbose_name=_("Nomi"))
    description = models.TextField(blank=True, verbose_name=_("Tavsif"))
    pdf_file    = models.FileField(upload_to="conferences/pdfs/", blank=True, null=True, verbose_name=_("Axborot xati / Fayl (PDF)"))
    date        = models.DateField(verbose_name=_("Sana"))
    location    = models.CharField(max_length=255, blank=True, verbose_name=_("Joyi"))
    url         = models.URLField(blank=True, verbose_name=_("Havola"))
    is_active   = models.BooleanField(default=True, verbose_name=_("Ko'rsatish"))
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = _("Konferensiya")
        verbose_name_plural = _("Konferensiyalar")

    def __str__(self):
        return self.title


# ─── YANGILIKLAR ─────────────────────────────────────────────────────────────

class News(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='news', verbose_name=_("Jurnal"), null=True, blank=True)
    title       = models.CharField(max_length=300, verbose_name=_("Sarlavha"))
    content     = models.TextField(verbose_name=_("Matn"))
    image       = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name=_("Rasm"))
    is_active   = models.BooleanField(default=True, verbose_name=_("Ko'rsatish"))
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Yangilik")
        verbose_name_plural = _("Yangiliklar")

    def __str__(self):
        return self.title


def news_media_path(instance, filename):
    import os, uuid
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    return f"news_media/{uuid.uuid4()}.{ext}"


class NewsMedia(models.Model):
    MEDIA_TYPES = (
        ('image', _('Rasm')),
        ('video', _('Video fayl (MP4/WebM)')),
        ('video_url', _('Video havola (YouTube/Vimeo/Web URL)')),
    )
    news        = models.ForeignKey(News, on_delete=models.CASCADE, related_name='media_files', verbose_name=_("Yangilik"))
    media_type  = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image', verbose_name=_("Media turi"))
    file        = models.FileField(upload_to=news_media_path, null=True, blank=True, verbose_name=_("Fayl (Rasm yoki Video)"))
    video_url   = models.URLField(blank=True, verbose_name=_("Video URL (YouTube/Vimeo/MP4 havolasi)"))
    caption     = models.CharField(max_length=255, blank=True, verbose_name=_("Izoh / Sarlavha"))
    order       = models.PositiveIntegerField(default=0, verbose_name=_("Tartib"))
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("Yangilik media fayli")
        verbose_name_plural = _("Yangilik media fayllari (Rasmlar va Videolar)")

    def __str__(self):
        return f"{self.news.title[:25]} - {self.get_media_type_display()}"

    @property
    def youtube_embed_url(self):
        if not self.video_url:
            return ''
        url = self.video_url.strip()
        if 'youtube.com/watch' in url:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            v = params.get('v', [''])[0]
            if v:
                return f"https://www.youtube.com/embed/{v}"
        elif 'youtu.be/' in url:
            v = url.split('youtu.be/')[-1].split('?')[0]
            if v:
                return f"https://www.youtube.com/embed/{v}"
        return url


# ─── ME'YORIY HUJJATLAR ──────────────────────────────────────────────────────

class Document(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='documents', verbose_name=_("Jurnal"), null=True, blank=True)
    CATEGORY_CHOICES = (
        ('normative', "Me'yoriy hujjat"),
        ('requirement', _('Maqola talablari')),
        ('template', _('Shablon')),
        ('other', _('Boshqa')),
    )
    title       = models.CharField(max_length=300, verbose_name=_("Nomi"))
    category    = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='normative', verbose_name=_("Kategoriya"))
    description = models.TextField(blank=True, verbose_name=_("Tavsif"))
    file        = models.FileField(upload_to='documents/', null=True, blank=True, verbose_name=_("Fayl"))
    url         = models.URLField(blank=True, verbose_name=_("Tashqi havola"))
    is_active   = models.BooleanField(default=True, verbose_name=_("Ko'rsatish"))
    order       = models.PositiveIntegerField(default=0, verbose_name=_("Tartib"))
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("Hujjat")
        verbose_name_plural = _("Hujjatlar")

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"


# ─── TAQRIZ QAYDLARI (REVIEW RECORD) ──────────────────────────────────────────

class ReviewRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Kutilmoqda')),
        ('sent', _('Taqrizchiga yuborildi')),
        ('received', _('Taqriz qabul qilindi')),
        ('revision_requested', _("Qo'shimcha tahrir so'raldi")),
        ('completed', _('Yakunlandi')),
    )
    DECISION_CHOICES = (
        ('none', _("Hali qaror yo'q")),
        ('accept', _('Qabul qilinsin')),
        ('revision', _('Qayta ishlash talab etiladi')),
        ('reject', _('Rad etilsin')),
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='review_records', verbose_name=_("Maqola"))
    reviewer_name = models.CharField(max_length=255, verbose_name=_("Taqrizchi ismi"))
    reviewer_affiliation = models.CharField(max_length=255, blank=True, verbose_name=_("Taqrizchi ish joyi / tashkiloti"))
    date_sent = models.DateField(null=True, blank=True, verbose_name=_("Yuborilgan sana"))
    deadline = models.DateField(null=True, blank=True, verbose_name=_("Taqriz muddati"))
    date_received = models.DateField(null=True, blank=True, verbose_name=_("Qabul qilingan sana"))
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending', verbose_name=_("Holat"))
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default='none', verbose_name=_("Taqriz xulosasi"))
    confidential_comments = models.TextField(blank=True, verbose_name=_("Maxfiy taqriz izohlari (faqat admin uchun)"))
    report_file = models.FileField(upload_to='review_reports/', blank=True, null=True, verbose_name=_("Taqriz xulosasi fayli"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Taqriz qaydi")
        verbose_name_plural = _("Taqriz qaydlari")

    def __str__(self):
        return f"{self.article.title[:30]} — {self.reviewer_name} ({self.get_status_display()})"
