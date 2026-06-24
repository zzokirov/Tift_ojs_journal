from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, JournalIssue, Article, StaffMember


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


# ─── JOURNAL ISSUE ADMIN ──────────────────────────────────────────────────────

@admin.register(JournalIssue)
class JournalIssueAdmin(admin.ModelAdmin):
    list_display = (
        'issue_label', 'year', 'article_count_tag',
        'is_published', 'created_at'
    )
    list_display_links = ('issue_label',)
    list_filter = ('year', 'is_published')
    list_editable = ('is_published',)
    ordering = ('-year', '-volume', '-number')
    list_per_page = 20

    fieldsets = (
        ("Jurnal soni ma'lumotlari", {
            'fields': ('volume', 'number', 'year', 'is_published')
        }),
    )

    def issue_label(self, obj):
        return f"Jild {obj.volume}, Son {obj.number}"
    issue_label.short_description = 'Jurnal soni'

    def article_count_tag(self, obj):
        return obj.articles.count()
    article_count_tag.short_description = "Maqolalar soni"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('articles')


# ─── ARTICLE ADMIN ────────────────────────────────────────────────────────────

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
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
            'fields': ('title', 'abstract', 'keywords')
        }),
        ("Muallif va jurnal", {
            'fields': ('author', 'issue')
        }),
        ("Holat va fayl", {
            'fields': ('status', 'pdf_file', 'pdf_link')
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
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} ta maqola rad etildi.')


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
