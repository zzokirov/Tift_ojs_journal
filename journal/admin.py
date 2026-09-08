from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, JournalIssue, Article, ArticleCategory, StaffMember, Conference, News, NewsMedia, Document


# ─── USER ADMIN ───────────────────────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'get_full_name', 'email',
        'role', 'institution', 'article_count',
        'is_active', 'is_staff', 'date_joined'
    )
    list_display_links = ('username',)
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'institution')
    ordering = ('-date_joined',)
    list_per_page = 20

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('username', 'password')
        }),
        ("Shaxsiy ma'lumotlar", {
            'fields': ('first_name', 'last_name', 'email', 'institution')
        }),
        ("Rol va ruxsatlar", {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ("Muhim sanalar", {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name',
                       'institution', 'role', 'password1', 'password2'),
        }),
    )

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = "Maqolalar soni"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('articles')


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'icon', 'order', 'article_count')
    list_display_links = ('code', 'name')
    list_editable = ('icon', 'order')
    search_fields = ('code', 'name')
    ordering = ('order', 'code')
    list_per_page = 30

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = "Maqolalar soni"




@admin.register(JournalIssue)
class JournalIssueAdmin(admin.ModelAdmin):
    list_display = (
        'issue_label', 'year', 'period', 'article_count_tag',
        'is_published', 'created_at'
    )
    list_display_links = ('issue_label',)
    list_filter = ('year', 'is_published')
    list_editable = ('is_published',)
    ordering = ('-year', '-volume', '-number')
    list_per_page = 20

    fieldsets = (
        ("Jurnal soni ma'lumotlari", {
            'fields': ('volume', 'number', 'year', 'period', 'cover_image', 'back_cover_image', 'full_pdf', 'is_published')
        }),
    )

    def issue_label(self, obj):
        return f"{obj.year}-yil, {obj.number}-son"
    issue_label.short_description = 'Jurnal soni'

    def article_count_tag(self, obj):
        return obj.articles.filter(status='published').count()
    article_count_tag.short_description = "Chop etilgan maqolalar soni"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('articles')


# ─── ARTICLE ADMIN ────────────────────────────────────────────────────────────

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    change_list_template = 'admin/journal/article/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_issues'] = JournalIssue.objects.all().order_by('-year', '-number')
        extra_context['selected_issue'] = request.GET.get('issue__id__exact')
        return super().changelist_view(request, extra_context=extra_context)

    list_display = (
        'title_short', 'author_name', 'issue',
        'status', 'views_count', 'downloads_count', 'created_at'
    )
    list_display_links = ('title_short',)
    list_filter = ('status', 'issue__year', 'issue')
    search_fields = (
        'title', 'abstract', 'keywords',
        'author__first_name', 'author__last_name', 'author__username'
    )
    list_editable = ('status', 'issue')
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    readonly_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at', 'pdf_link')

    fieldsets = (
        ("Maqola ma'lumotlari", {
            'fields': ('title', 'authors', 'abstract', 'keywords')
        }),
        ("Muallif va jurnal", {
            'fields': ('author', 'issue', 'category')
        }),
        ("Sahifalash (Paginatsiya)", {
            'fields': ('start_page', 'end_page'),
            'description': "Agar maqola uchun alohida PDF yuklanmasa, To'plam PDF faylidan shu sahifalar oralig'i avtomatik qirqib olinadi."
        }),
        ("Holat va fayllar", {
            'fields': ('status', 'published_at', 'pdf_file', 'pdf_link', 'template_pdf')
        }),
        ("Statistika", {
            'fields': ('views_count', 'downloads_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_published', 'make_under_review', 'make_rejected']

    def title_short(self, obj):
        return obj.title[:70] + '…' if len(obj.title) > 70 else obj.title
    title_short.short_description = 'Sarlavha'

    def author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
    author_name.short_description = 'Muallif'

    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">PDF ni ochish</a>', obj.pdf_file.url)
        return '—'
    pdf_link.short_description = 'PDF fayl'

    @admin.action(description='Tanlangan maqolalarni nashr etish')
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} ta maqola nashr etildi.')

    @admin.action(description="Taqriz jarayoniga o'tkazish")
    def make_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, f"{updated} ta maqola taqriz jarayoniga o'tkazildi.")

    @admin.action(description='Rad etish')
    def make_rejected(self, request, queryset):
        updated = queryset.update(status='rejected', issue=None)
        self.message_user(request, f'{updated} ta maqola rad etildi va jurnaldan chiqarildi.')


# ─── STAFF MEMBER ADMIN ───────────────────────────────────────────────────────

@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('photo_tag', 'full_name', 'position', 'workplace', 'age', 'order', 'is_active')
    list_display_links = ('full_name',)
    list_filter = ('position', 'is_active')
    search_fields = ('full_name', 'workplace')
    list_editable = ('position', 'order', 'is_active')
    ordering = ('order', 'full_name')
    list_per_page = 20

    fieldsets = (
        ("Shaxsiy ma'lumotlar", {
            'fields': ('full_name', 'age', 'photo')
        }),
        ("Ish ma'lumotlari", {
            'fields': ('position', 'workplace', 'bio')
        }),
        ("Sozlamalar", {
            'fields': ('order', 'is_active')
        }),
    )

    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;">',
                obj.photo.url
            )
        initials = obj.full_name[:1].upper()
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;background:#16a34a;'
            'display:flex;align-items:center;justify-content:center;'
            'color:white;font-weight:700;font-size:14px;">{}</div>',
            initials
        )
    photo_tag.short_description = 'Rasm'


# ─── CONFERENCE ADMIN ─────────────────────────────────────────────────────────

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description', 'location')
    list_editable = ('is_active',)
    ordering = ('-date',)
    list_per_page = 20
    fieldsets = (
        ("Konferensiya ma'lumotlari", {
            'fields': ('title', 'description', 'pdf_file', 'date', 'location', 'url', 'is_active')
        }),
    )


# ─── NEWS ADMIN ───────────────────────────────────────────────────────────────

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [super(MultipleFileField, self).clean(d, initial) for d in data]
        return [super(MultipleFileField, self).clean(data, initial)]

class NewsAdminForm(forms.ModelForm):
    upload_images = MultipleFileField(
        widget=MultipleFileInput(attrs={'accept': 'image/*'}),
        required=False,
        label="Ko'plab rasmlar yuklash (Bir vaqtda bir nechta rasm tanlash)",
        help_text="Kompyuteringizdan bir nechta rasmni bir vaqtda belgilab (Ctrl/Shift) yuklashingiz mumkin."
    )
    upload_videos = MultipleFileField(
        widget=MultipleFileInput(attrs={'accept': 'video/*'}),
        required=False,
        label="Ko'plab video fayllar yuklash (MP4/WebM)",
        help_text="Bir nechta video fayllarni bir vaqtning o'zida tanlab yuklashingiz mumkin."
    )
    video_urls_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': "https://www.youtube.com/watch?v=...\nhttps://youtu.be/...\nhttps://vimeo.com/..."}),
        required=False,
        label="Video havolalar (YouTube/Vimeo)",
        help_text="Har bir satrga bittadan video havolasini yozing."
    )

    class Meta:
        model = News
        fields = '__all__'


class NewsMediaInline(admin.TabularInline):
    model = NewsMedia
    extra = 1
    fields = ('media_type', 'file', 'video_url', 'caption', 'order')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('title', 'media_count_display', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [NewsMediaInline]
    fieldsets = (
        ("Yangilik ma'lumotlari", {
            'fields': ('title', 'content', 'image', 'is_active')
        }),
        ("Ommaviy foto va video yuklash (Ko'plab rasmlar va videolar)", {
            'fields': ('upload_images', 'upload_videos', 'video_urls_text'),
            'description': "Bu yerda bir vaqtning o'zida 10-20 ta rasmlarni tanlab yuklashingiz, ko'plab video fayllarni yoki YouTube/Vimeo havolalarini joylashingiz mumkin."
        }),
    )

    def media_count_display(self, obj):
        images_count = obj.media_files.filter(media_type='image').count()
        videos_count = obj.media_files.exclude(media_type='image').count()
        res = []
        if images_count:
            res.append(f"📷 {images_count} rasm")
        if videos_count:
            res.append(f"🎥 {videos_count} video")
        return " | ".join(res) if res else "Media yo'q"
    media_count_display.short_description = "Media fayllar"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 1. Multiple images
        images = request.FILES.getlist('upload_images')
        for idx, img in enumerate(images):
            NewsMedia.objects.create(
                news=obj,
                media_type='image',
                file=img,
                order=idx + 10
            )

        # 2. Multiple videos
        videos = request.FILES.getlist('upload_videos')
        for idx, vid in enumerate(videos):
            NewsMedia.objects.create(
                news=obj,
                media_type='video',
                file=vid,
                order=idx + 20
            )

        # 3. Multiple video URLs
        video_urls = form.cleaned_data.get('video_urls_text')
        if video_urls:
            lines = [l.strip() for l in video_urls.splitlines() if l.strip()]
            for idx, url in enumerate(lines):
                NewsMedia.objects.create(
                    news=obj,
                    media_type='video_url',
                    video_url=url,
                    order=idx + 30
                )


# ─── DOCUMENT ADMIN ───────────────────────────────────────────────────────────

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('category', 'order', 'is_active')
    ordering = ('order', '-created_at')
    list_per_page = 20
    fieldsets = (
        ("Hujjat ma'lumotlari", {
            'fields': ('title', 'category', 'description', 'file', 'url', 'order', 'is_active')
        }),
    )


# --- LOG ENTRY ADMIN ---

from django.contrib.admin.models import LogEntry
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_time', 'action_flag', 'content_type', 'user')
    search_fields = ('object_repr', 'change_message')
    date_hierarchy = 'action_time'
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
