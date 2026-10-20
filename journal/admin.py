from django import forms
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
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



class JournalAdminMixin:
    """Admin formalari ochilganda tanlangan jurnalni avtomatik to'ldirish"""
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'journal' not in initial and request.session.get('admin_active_journal_id'):
            initial['journal'] = request.session.get('admin_active_journal_id')
        return initial


@admin.register(Journal)
class JournalAdmin(TranslationAdmin):
    list_display = ('counter_col', 'journal_col', 'issn_col', 'status_col', 'languages_col', 'actions_col')
    list_display_links = None
    list_filter = ('is_active', 'publication_status')
    search_fields = ('title', 'title_uz', 'title_ru', 'title_en', 'slug', 'issn', 'research_areas')
    prepopulated_fields = {'slug': ('title_uz',)}
    ordering = ('display_order', 'id')
    list_per_page = 20

    @admin.display(description="№")
    def counter_col(self, obj):
        all_ids = list(Journal.objects.order_by('display_order', 'id').values_list('id', flat=True))
        try:
            return all_ids.index(obj.id) + 1
        except ValueError:
            return obj.id

    @admin.display(description=_("Jurnal nomi"))
    def journal_col(self, obj):
        cover = obj.get_cover_for_language()
        cover_url = cover.url if cover else "/static/images/tift.png"
        select_url = f"{reverse('admin:journal_journalissue_changelist')}?journal__id__exact={obj.pk}"
        return format_html(
            '<div style="display:flex; align-items:center; gap:14px;">'
            '<div style="width:36px; height:48px; border-radius:4px; overflow:hidden; flex-shrink:0; border:1px solid #e2e8f0; background:#f1f5f9; box-shadow:0 1px 2px rgba(0,0,0,0.06);">'
            '<img src="{}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src=\'/static/images/tift.png\'">'
            '</div>'
            '<div>'
            '<a href="{}" title="Jurnalni tanlash va boshqarish" style="font-weight:700; color:#0f172a; font-size:13.5px; text-decoration:none; line-height:1.35; display:block;" onmouseover="this.style.color=\'#1d4ed8\'" onmouseout="this.style.color=\'#0f172a\'">{}</a>'
            '</div>'
            '</div>',
            cover_url, select_url, obj.title
        )

    @admin.display(description=_("ISSN"))
    def issn_col(self, obj):
        if obj.issn:
            return format_html('<span style="font-family:monospace; font-weight:600; color:#334155; font-size:13px;">{}</span>', obj.issn)
        return "—"

    @admin.display(description=_("Holat"))
    def status_col(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="display:inline-block; padding:4px 14px; border-radius:9999px; font-size:11.5px; font-weight:700; background-color:#dcfce7; color:#16a34a; line-height:1.2;">Faol</span>'
            )
        return mark_safe(
            '<span style="display:inline-block; padding:4px 14px; border-radius:9999px; font-size:11.5px; font-weight:700; background-color:#f1f5f9; color:#64748b; line-height:1.2;">Nofaol</span>'
        )

    @admin.display(description=_("Tillar"))
    def languages_col(self, obj):
        return mark_safe('<span style="color:#475569; font-size:13px; font-weight:500;">O\'z, Rus, Eng</span>')

    @admin.display(description=_("Boshqarish"))
    def actions_col(self, obj):
        select_url = f"{reverse('admin:journal_journalissue_changelist')}?journal__id__exact={obj.pk}"
        change_url = reverse('admin:journal_journal_change', args=[obj.pk])
        view_url = reverse('index', kwargs={'journal_slug': obj.slug})
        return format_html(
            '<div style="display:flex; align-items:center; gap:8px;">'
            '<a href="{}" title="Ushbu jurnalni tanlash" style="display:inline-flex; align-items:center; gap:5px; padding:6px 12px; border-radius:6px; background:#1d4ed8; color:#ffffff; font-weight:700; font-size:12px; text-decoration:none; transition:all 0.2s;" onmouseover="this.style.background=\'#1e40af\'" onmouseout="this.style.background=\'#1d4ed8\'"><i class="fas fa-folder-open" style="font-size:11px;"></i> Tanlash</a>'
            '<a href="{}" title="Jurnal sozlamalari" style="display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:6px; background:#eff6ff; color:#2563eb; text-decoration:none; border:1px solid #bfdbfe; transition:all 0.2s;" onmouseover="this.style.background=\'#dbeafe\'" onmouseout="this.style.background=\'#eff6ff\'"><i class="fas fa-cog" style="font-size:11px;"></i></a>'
            '<a href="{}" target="_blank" title="Saytda ko\'rish" style="display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:6px; background:#f8fafc; color:#64748b; text-decoration:none; border:1px solid #e2e8f0; transition:all 0.2s;" onmouseover="this.style.background=\'#e2e8f0\'" onmouseout="this.style.background=\'#f8fafc\'"><i class="fas fa-external-link-alt" style="font-size:10px;"></i></a>'
            '</div>',
            select_url, change_url, view_url
        )

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.title_uz or obj.title or 'journal', allow_unicode=True)
        super().save_model(request, obj, form, change)

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
class ArticleCategoryAdmin(JournalAdminMixin, TranslationAdmin):
    list_filter = ('journal',)
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
class JournalIssueAdmin(JournalAdminMixin, admin.ModelAdmin):
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
class ArticleAdmin(JournalAdminMixin, admin.ModelAdmin):
    change_list_template = 'admin/journal/article/change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_issues'] = JournalIssue.objects.all().order_by('-year', '-number')
        extra_context['selected_issue'] = request.GET.get('issue__id__exact')
        return super().changelist_view(request, extra_context=extra_context)

    list_display = (
        'title_short', 'authors_display', 'journal', 'issue',
        'status', 'pdf_link', 'downloads_count', 'created_at'
    )
    list_display_links = ('title_short',)
    list_filter = ('journal', 'status', 'issue__year', 'issue')
    search_fields = ('title', 'authors')
    list_editable = ('status', 'issue')
    ordering = ('-created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    readonly_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at', 'pdf_link')
    inlines = []

    fieldsets = (
        (_("Maqolani chop qilish"), {
            'fields': ('title', 'authors', 'journal', 'issue', 'pdf_file', 'status'),
            'description': _("Maqola ma'lumotlarini to'ldiring va PDF faylini biriktiring.")
        }),
    )

    actions = ['make_published', 'make_under_review', 'make_rejected']

    def title_short(self, obj):
        return obj.title[:70] + '…' if len(obj.title) > 70 else obj.title
    title_short.short_description = _('Sarlavha')

    def authors_display(self, obj):
        return obj.authors or (obj.author.get_full_name() if obj.author else '—')
    authors_display.short_description = _("Mualliflar")

    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.pdf_file.url, _("PDF ni ochish"))
        return '—'
    pdf_link.short_description = _('PDF fayl')

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['status'] = 'published'
        active_journal_id = request.session.get('admin_active_journal_id')
        if active_journal_id:
            initial['journal'] = active_journal_id
        return initial

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'issue':
            active_journal_id = request.session.get('admin_active_journal_id')
            if active_journal_id:
                kwargs['queryset'] = JournalIssue.objects.filter(journal_id=active_journal_id).order_by('-year', '-number')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if not obj.abstract:
            obj.abstract = obj.title
        if not obj.keywords:
            obj.keywords = ''
        if not obj.status:
            obj.status = 'published'
        if hasattr(obj, 'title_uz') and not obj.title_uz:
            obj.title_uz = obj.title
        if hasattr(obj, 'abstract_uz') and not obj.abstract_uz:
            obj.abstract_uz = obj.abstract
        if hasattr(obj, 'keywords_uz') and not obj.keywords_uz:
            obj.keywords_uz = obj.keywords
        super().save_model(request, obj, form, change)

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
class StaffMemberAdmin(JournalAdminMixin, TranslationAdmin):
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
class ConferenceAdmin(JournalAdminMixin, TranslationAdmin):
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
class NewsAdmin(JournalAdminMixin, TranslationAdmin):
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
class DocumentAdmin(JournalAdminMixin, TranslationAdmin):
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
