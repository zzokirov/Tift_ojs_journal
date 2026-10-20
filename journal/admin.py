from django import forms
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, JournalIssue, Article, ArticleCategory, StaffMember, Conference, News, NewsMedia, Document, Journal, ReviewRecord


# ─── USER ADMIN ───────────────────────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 'get_full_name',
        'role', 'institution', 'article_count',
        'is_active', 'is_staff', 'date_joined'
    )
    list_display_links = ('email', 'get_full_name')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'institution')
    ordering = ('-date_joined',)
    list_per_page = 20
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            'fields': ('email', 'password')
        }),
        (_("Shaxsiy ma'lumotlar"), {
            'fields': ('first_name', 'last_name', 'institution', 'phone', 'gender', 'country', 'bio', 'avatar')
        }),
        (_("Rol va ruxsatlar"), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_("Muhim sanalar"), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'institution', 'role', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.username and obj.email:
            base = obj.email.split('@')[0][:25]
            import random, string
            un = base
            while User.objects.filter(username=un).exists():
                un = base + ''.join(random.choices(string.digits, k=4))
            obj.username = un
        super().save_model(request, obj, form, change)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _("Maqolalar soni")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('articles')



@admin.register(Journal)
class JournalAdmin(TranslationAdmin):
    list_display = ('title', 'slug', 'issn', 'publication_frequency', 'display_order', 'is_active', 'publication_status')
    list_editable = ('display_order', 'is_active', 'publication_status')
    list_filter = ('publication_status', 'is_active', 'primary_language')
    search_fields = ('title', 'slug', 'issn', 'research_areas')
    prepopulated_fields = {'slug': ('title_uz',)}

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.title_uz or obj.title or 'journal', allow_unicode=True)
        super().save_model(request, obj, form, change)
    ordering = ('display_order', 'id')

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            'fields': ('title', 'slug', 'issn', 'publisher_name', 'publication_frequency', 'founded_year', 'website_url')
        }),
        (_("Muqovalar va logotip (3 tilda)"), {
            'fields': ('logo', 'cover_uz', 'cover_ru', 'cover_en', 'cover_image'),
            'description': _("Har bir til uchun alohida muqova yuklash mumkin. Saytda tashrif buyuruvchi tanlagan til muqovasi avtomatik ko'rsatiladi.")
        }),
        (_("Tavsif va ilmiy yo'nalishlar"), {
            'fields': ('short_description', 'full_description', 'description', 'research_areas', 'submission_guidelines')
        }),
        (_("Sozlamalar va holat"), {
            'fields': ('primary_language', 'supported_languages', 'editorial_email', 'theme_color', 'secondary_color', 'display_order', 'is_featured', 'is_active', 'publication_status', 'published_at')
        }),
    )

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(TranslationAdmin):
    list_display = ('journal', 'code', 'name', 'icon', 'order', 'article_count')
    list_display_links = ('code', 'name')
    list_editable = ('icon', 'order')
    search_fields = ('code', 'name')
    ordering = ('order', 'code')
    list_per_page = 30

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _("Maqolalar soni")




@admin.register(JournalIssue)
class JournalIssueAdmin(admin.ModelAdmin):
    list_display = ('journal', 
        'issue_label', 'year', 'period', 'quarter', 'status', 'article_count_tag',
        'is_published', 'created_at'
    )
    list_display_links = ('issue_label',)
    list_filter = ('journal', 'status', 'year', 'is_published')
    list_editable = ('status', 'is_published')
    ordering = ('-year', '-volume', '-number')
    list_per_page = 20

    fieldsets = (
        (_("Jurnal soni ma'lumotlari"), {
            'fields': ('journal', 'volume', 'number', 'year', 'quarter', 'period', 'title', 'description', 'status', 'is_published')
        }),
        (_("Muqovalar va fayllar"), {
            'fields': ('cover_image', 'back_cover_image', 'toc_pdf', 'editorial_doc', 'full_pdf', 'publication_date')
        }),
    )

    def issue_label(self, obj):
        return f"{obj.year}-yil, {obj.number}-son"
    issue_label.short_description = _('Jurnal soni')

    def article_count_tag(self, obj):
        return obj.articles.filter(status='published').count()
    article_count_tag.short_description = _("Chop etilgan maqolalar soni")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('articles')


# ─── ARTICLE ADMIN ────────────────────────────────────────────────────────────


class ReviewRecordInline(admin.StackedInline):
    model = ReviewRecord
    extra = 0
    fields = ('reviewer_name', 'reviewer_affiliation', 'date_sent', 'deadline', 'date_received', 'status', 'decision', 'confidential_comments', 'report_file')


@admin.register(ReviewRecord)
class ReviewRecordAdmin(admin.ModelAdmin):
    list_display = ('article', 'reviewer_name', 'date_sent', 'deadline', 'date_received', 'status', 'decision')
    list_filter = ('status', 'decision', 'date_sent')
    search_fields = ('reviewer_name', 'reviewer_affiliation', 'article__title', 'confidential_comments')
    date_hierarchy = 'date_sent'
    list_per_page = 25

@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    change_list_template = 'admin/journal/article/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_issues'] = JournalIssue.objects.all().order_by('-year', '-number')
        extra_context['selected_issue'] = request.GET.get('issue__id__exact')
        return super().changelist_view(request, extra_context=extra_context)

    list_display = (
        'title_short', 'author_name', 'category', 'assigned_reviewer', 'issue',
        'status', 'views_count', 'downloads_count', 'created_at'
    )
    list_display_links = ('title_short',)
    list_filter = ('journal', 'status', 'assigned_reviewer', 'category', 'issue__year', 'issue')
    search_fields = (
        'title', 'abstract', 'keywords',
        'author__first_name', 'author__last_name', 'author__email'
    )
    list_editable = ('assigned_reviewer', 'status', 'issue')
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    readonly_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at', 'pdf_link')
    inlines = [ReviewRecordInline]

    fieldsets = (
        (_("Maqola ma'lumotlari"), {
            'fields': ('title', 'authors', 'abstract', 'keywords')
        }),
        (_("Muallif va jurnal"), {
            'fields': ('journal', 'author', 'issue', 'category', 'article_language', 'order_in_issue')
        }),
        (_("Bog'lanish uchun muallif (Tahririyat uchun)"), {
            'fields': ('corresponding_author_name', 'corresponding_author_email', 'corresponding_author_phone', 'admin_notes')
        }),
        (_("Fayllar (PDF va Word)"), {
            'fields': ('pdf_file', 'pdf_link', 'word_file', 'template_pdf')
        }),
        (_("Taqrizchi va ko'rib chiqish"), {
            'fields': ('assigned_reviewer', 'review_notes', 'reviewed_by', 'reviewed_at')
        }),
        (_("Sahifalash (Paginatsiya)"), {
            'fields': ('start_page', 'end_page'),
            'description': _("Agar maqola uchun alohida PDF yuklanmasa, To'plam PDF faylidan shu sahifalar oralig'i avtomatik qirqib olinadi.")
        }),
        (_("Holat va fayllar"), {
            'fields': ('status', 'published_at')
        }),
        (_("Statistika"), {
            'fields': ('views_count', 'downloads_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_published', 'make_under_review', 'make_rejected']

    def title_short(self, obj):
        return obj.title[:70] + '…' if len(obj.title) > 70 else obj.title
    title_short.short_description = _('Sarlavha')

    def author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
    author_name.short_description = _('Muallif')

    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.pdf_file.url, _("PDF ni ochish"))
        return '—'
    pdf_link.short_description = _('PDF fayl')

    @admin.action(description=_('Tanlangan maqolalarni nashr etish'))
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, _('{updated} ta maqola nashr etildi.').format(updated=updated))

    @admin.action(description=_("Taqriz jarayoniga o'tkazish"))
    def make_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, _("{updated} ta maqola taqriz jarayoniga o'tkazildi.").format(updated=updated))

    @admin.action(description=_('Rad etish'))
    def make_rejected(self, request, queryset):
        updated = queryset.update(status='rejected', issue=None)
        self.message_user(request, _('{updated} ta maqola rad etildi va jurnaldan chiqarildi.').format(updated=updated))


# ─── STAFF MEMBER ADMIN ───────────────────────────────────────────────────────

@admin.register(StaffMember)
class StaffMemberAdmin(TranslationAdmin):
    list_display = ('journal', 'photo_tag', 'full_name', 'position', 'academic_degree', 'academic_title', 'workplace', 'order', 'is_active')
    list_display_links = ('full_name',)
    list_filter = ('journal', 'position', 'academic_degree', 'academic_title', 'is_active')
    search_fields = ('full_name', 'workplace', 'institution', 'bio')
    list_editable = ('position', 'order', 'is_active')
    ordering = ('order', 'full_name')
    list_per_page = 20

    fieldsets = (
        (_("Shaxsiy ma'lumotlar"), {
            'fields': ('journal', 'full_name', 'age', 'photo', 'email', 'show_email')
        }),
        (_("Ilmiy daraja va ish ma'lumotlari"), {
            'fields': ('position', 'academic_degree', 'academic_title', 'workplace', 'institution', 'bio')
        }),
        (_("Sozlamalar"), {
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
    photo_tag.short_description = _('Rasm')


# ─── CONFERENCE ADMIN ─────────────────────────────────────────────────────────

@admin.register(Conference)
class ConferenceAdmin(TranslationAdmin):
    list_display = ('journal', 'title', 'date', 'location', 'is_active', 'created_at')
    list_filter = ('journal', 'is_active',)
    search_fields = ('title', 'description', 'location')
    list_editable = ('is_active',)
    ordering = ('-date',)
    list_per_page = 20
    fieldsets = (
        (_("Konferensiya ma'lumotlari"), {
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
        label=_("Ko'plab rasmlar yuklash (Bir vaqtda bir nechta rasm tanlash)"),
        help_text=_("Kompyuteringizdan bir nechta rasmni bir vaqtda belgilab (Ctrl/Shift) yuklashingiz mumkin.")
    )
    upload_videos = MultipleFileField(
        widget=MultipleFileInput(attrs={'accept': 'video/*'}),
        required=False,
        label=_("Ko'plab video fayllar yuklash (MP4/WebM)"),
        help_text=_("Bir nechta video fayllarni bir vaqtning o'zida tanlab yuklashingiz mumkin.")
    )
    video_urls_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': "https://www.youtube.com/watch?v=...\nhttps://youtu.be/...\nhttps://vimeo.com/..."}),
        required=False,
        label=_("Video havolalar (YouTube/Vimeo)"),
        help_text=_("Har bir satrga bittadan video havolasini yozing.")
    )

    class Meta:
        model = News
        fields = '__all__'


class NewsMediaInline(admin.TabularInline):
    model = NewsMedia
    extra = 1
    fields = ('media_type', 'file', 'video_url', 'caption', 'order')


@admin.register(News)
class NewsAdmin(TranslationAdmin):
    form = NewsAdminForm
    list_display = ('title', 'media_count_display', 'is_active', 'created_at')
    list_filter = ('journal', 'is_active',)
    search_fields = ('title', 'content')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [NewsMediaInline]
    fieldsets = (
        (_("Yangilik ma'lumotlari"), {
            'fields': ('title', 'content', 'image', 'is_active')
        }),
        (_("Ommaviy foto va video yuklash (Ko'plab rasmlar va videolar)"), {
            'fields': ('upload_images', 'upload_videos', 'video_urls_text'),
            'description': _("Bu yerda bir vaqtning o'zida 10-20 ta rasmlarni tanlab yuklashingiz, ko'plab video fayllarni yoki YouTube/Vimeo havolalarini joylashingiz mumkin.")
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
    media_count_display.short_description = _("Media fayllar")

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
class DocumentAdmin(TranslationAdmin):
    list_display = ('journal', 'title', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('journal', 'category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('category', 'order', 'is_active')
    ordering = ('order', '-created_at')
    list_per_page = 20
    fieldsets = (
        (_("Hujjat ma'lumotlari"), {
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
