import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"avatars/{uuid.uuid4()}.{ext}"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('author', 'Muallif'),
        ('reviewer', 'Taqrizchi'),
        ('editor', 'Muharrir'),
    )
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='author')
    institution = models.CharField(max_length=255, blank=True, verbose_name="Ish/O'qish joyi")
    avatar      = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, verbose_name="Profil rasmi")
    bio         = models.TextField(blank=True, verbose_name="O'zim haqimda")
    phone       = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqam")

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class JournalIssue(models.Model):
    volume = models.PositiveIntegerField(verbose_name="Jurnal jildi (Volume)")
    number = models.PositiveIntegerField(verbose_name="Jurnal soni (Issue)")
    year = models.PositiveIntegerField(verbose_name="Chop etilgan yili")
    is_published = models.BooleanField(default=False, verbose_name="Saytda ko'rsatish")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-volume', '-number']
        verbose_name = "Jurnal soni"
        verbose_name_plural = "Jurnal sonlari"

    def __str__(self):
        return f"Jild {self.volume}, Son {self.number} ({self.year})"


def article_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"articles_pdf/{filename}"


def article_template_pdf_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"articles_template/{uuid.uuid4()}.{ext}"


# ─── YO'NALISH / KATEGORIYA ───────────────────────────────────────────────────

class ArticleCategory(models.Model):
    code  = models.CharField(max_length=20, unique=True, verbose_name="Kod (masalan: 18.00.00)")
    name  = models.CharField(max_length=200, verbose_name="Nomi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        ordering = ['order', 'code']
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"

    def __str__(self):
        return f"{self.code} — {self.name}"


class Article(models.Model):
    STATUS_CHOICES = (
        ('submitted',    'Yuborildi'),
        ('under_review', 'Taqriz jarayonida'),
        ('accepted',     'Qabul qilindi'),
        ('rejected',     'Rad etildi'),
        ('published',    'Chop etildi'),
    )

    # Asosiy ma'lumotlar
    title    = models.CharField(max_length=500, verbose_name="Maqola sarlavhasi")
    authors  = models.CharField(max_length=500, blank=True, verbose_name="Mualliflar (to'liq ro'yxat)")
    abstract = models.TextField(verbose_name="Annotatsiya / Abstract")
    keywords = models.CharField(max_length=255, verbose_name="Kalit so'zlar (vergul bilan ajrating)")

    # Muallif (tizim foydalanuvchisi) va jurnal
    author   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name="Muallif (foydalanuvchi)")
    issue    = models.ForeignKey(JournalIssue, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name="Jurnal soni")
    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name="Yo'nalish / Kategoriya")

    # Holat
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted', verbose_name="Maqola holati")

    # Maqola matni (HTML)
    content = models.TextField(blank=True, verbose_name="Maqola matni (HTML)")

    # Fayllar
    pdf_file     = models.FileField(upload_to=article_upload_path, verbose_name="PDF Fayl (muallif tomonidan yuborilgan)")
    template_pdf = models.FileField(upload_to=article_template_pdf_path, null=True, blank=True, verbose_name="Shablon PDF (tahririyat tomonidan)")

    # Chop etilgan sana
    published_at = models.DateField(null=True, blank=True, verbose_name="Chop etilgan sana")

    # Statistika
    views_count     = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni")
    downloads_count = models.PositiveIntegerField(default=0, verbose_name="Yuklab olishlar soni")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan sana")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"

    def __str__(self):
        return self.title


class SiteVisit(models.Model):
    date       = models.DateField(auto_now_add=True, verbose_name="Sana")
    ip_address = models.GenericIPAddressField(verbose_name="IP manzil")

    class Meta:
        verbose_name = "Tashrif"
        verbose_name_plural = "Tashriflar"
        unique_together = ('date', 'ip_address')

    def __str__(self):
        return f"{self.ip_address} — {self.date}"


def staff_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"staff_photos/{uuid.uuid4()}.{ext}"


class StaffMember(models.Model):
    POSITION_CHOICES = (
        ('editor_in_chief', 'Bosh muharrir'),
        ('deputy_editor',   "O'rinbosar muharrir"),
        ('editor',          'Muharrir'),
        ('reviewer',        'Taqrizchi'),
        ('secretary',       'Kotib'),
        ('member',          'A\'zo'),
    )

    full_name   = models.CharField(max_length=255, verbose_name="Ism Familiya")
    position    = models.CharField(max_length=30, choices=POSITION_CHOICES, default='member', verbose_name="Lavozim")
    workplace   = models.CharField(max_length=255, verbose_name="Ish joyi")
    age         = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Yoshi")
    photo       = models.ImageField(upload_to=staff_photo_path, null=True, blank=True, verbose_name="Rasmi")
    bio         = models.TextField(blank=True, verbose_name="Qisqacha ma'lumot")
    order       = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")
    is_active   = models.BooleanField(default=True, verbose_name="Ko'rsatish")

    class Meta:
        ordering = ['order', 'full_name']
        verbose_name = "Jurnal a'zosi"
        verbose_name_plural = "Jurnal a'zolari"

    def __str__(self):
        return f"{self.full_name} — {self.get_position_display()}"


# ─── KONFERENSIYALAR ─────────────────────────────────────────────────────────

class Conference(models.Model):
    title       = models.CharField(max_length=300, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    date        = models.DateField(verbose_name="Sana")
    location    = models.CharField(max_length=255, blank=True, verbose_name="Joyi")
    url         = models.URLField(blank=True, verbose_name="Havola")
    is_active   = models.BooleanField(default=True, verbose_name="Ko'rsatish")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Konferensiya"
        verbose_name_plural = "Konferensiyalar"

    def __str__(self):
        return self.title


# ─── YANGILIKLAR ─────────────────────────────────────────────────────────────

class News(models.Model):
    title       = models.CharField(max_length=300, verbose_name="Sarlavha")
    content     = models.TextField(verbose_name="Matn")
    image       = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name="Rasm")
    is_active   = models.BooleanField(default=True, verbose_name="Ko'rsatish")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"

    def __str__(self):
        return self.title


# ─── ME'YORIY HUJJATLAR ──────────────────────────────────────────────────────

class Document(models.Model):
    CATEGORY_CHOICES = (
        ('normative', "Me'yoriy hujjat"),
        ('requirement', 'Maqola talablari'),
        ('template', 'Shablon'),
        ('other', 'Boshqa'),
    )
    title       = models.CharField(max_length=300, verbose_name="Nomi")
    category    = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='normative', verbose_name="Kategoriya")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    file        = models.FileField(upload_to='documents/', null=True, blank=True, verbose_name="Fayl")
    url         = models.URLField(blank=True, verbose_name="Tashqi havola")
    is_active   = models.BooleanField(default=True, verbose_name="Ko'rsatish")
    order       = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Hujjat"
        verbose_name_plural = "Hujjatlar"

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"
