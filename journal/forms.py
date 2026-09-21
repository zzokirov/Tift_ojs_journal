from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Article, ArticleCategory

User = get_user_model()

css_input  = 'w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white transition-colors'
css_textarea = 'w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white transition-colors resize-none'

# Ruxsat etilgan MIME turlari va ularning kengaytmalari
ALLOWED_ARTICLE_MIME = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/msword': ['.doc'],
}
ALLOWED_IMAGE_MIME = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/webp': ['.webp'],
    'image/gif': ['.gif'],
}

# Maksimal fayl o'lchamlari
MAX_ARTICLE_SIZE = 20 * 1024 * 1024   # 20 MB
MAX_IMAGE_SIZE   = 5  * 1024 * 1024   # 5 MB


def _get_mime_type(file_obj):
    """python-magic yordamida MIME turini aniqlaydi."""
    try:
        import magic
        header = file_obj.read(2048)
        file_obj.seek(0)
        return magic.from_buffer(header, mime=True)
    except ImportError:
        # python-magic o'rnatilmagan bo'lsa — kengaytma bo'yicha
        return None


def validate_article_file(file):
    """Maqola faylini MIME va hajm bo'yicha tekshiradi."""
    if not file:
        return

    # Hajm tekshiruvi
    if file.size > MAX_ARTICLE_SIZE:
        raise ValidationError(_("Fayl hajmi 20 MB dan oshmasligi kerak. Hozirgi hajm: {file.size // (1024*1024)} MB"))

    # Kengaytma tekshiruvi
    import os
    ext = os.path.splitext(file.name)[1].lower()
    allowed_exts = [e for exts in ALLOWED_ARTICLE_MIME.values() for e in exts]
    if ext not in allowed_exts:
        raise ValidationError(_("Faqat Word (.docx, .doc) format qabul qilinadi. Yuborilgan: {ext}"))

    # MIME tekshiruvi
    mime = _get_mime_type(file)
    if mime and mime not in ALLOWED_ARTICLE_MIME:
        raise ValidationError(_("Fayl turi qabul qilinmaydi. Aniqlangan tur: {mime}"))


def validate_image_file(file):
    """Rasm faylini MIME va hajm bo'yicha tekshiradi."""
    if not file:
        return

    # Hajm tekshiruvi
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(_("Rasm hajmi 5 MB dan oshmasligi kerak."))

    # Kengaytma tekshiruvi
    import os
    ext = os.path.splitext(file.name)[1].lower()
    allowed_exts = [e for exts in ALLOWED_IMAGE_MIME.values() for e in exts]
    if ext not in allowed_exts:
        raise ValidationError(_("Faqat JPG, PNG, WEBP, GIF rasmlari qabul qilinadi."))

    # MIME tekshiruvi
    mime = _get_mime_type(file)
    if mime and mime not in ALLOWED_IMAGE_MIME:
        raise ValidationError(_("Rasm turi qabul qilinmaydi. Aniqlangan tur: {mime}"))


class ArticleSubmissionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ArticleCategory.objects.all().order_by('order', 'code'),
        required=False,
        empty_label=_("--- Maqola yo'nalishini tanlang ---"),
        label=_("Maqola yo'nalishi (Kategoriya)"),
        help_text=_("Maqolangiz tegishli bo'lgan ilmiy yo'nalishni ro'yxatdan tanlang."),
        widget=forms.Select(attrs={
            'class': css_input + ' cursor-pointer'
        })
    )

    class Meta:
        model = Article
        fields = ['title', 'category', 'authors', 'abstract', 'keywords', 'pdf_file']
        labels = {
            'title': _("Maqola sarlavhasi"),
            'category': _("Yo'nalish (Kategoriya)"),
            'authors': _("Mualliflar va ularning ish joyi"),
            'abstract': _("Annotatsiya / Abstract"),
            'keywords': _("Kalit so'zlar"),
            'pdf_file': _("Maqola fayli (.docx)"),
        }
        widgets = {
            'title':    forms.TextInput(attrs={'class': css_input, 'placeholder': _('Maqola sarlavhasi')}),
            'authors':  forms.TextInput(attrs={'class': css_input, 'placeholder': _('Barcha mualliflar (Ism Familiya, ...)')}),
            'abstract': forms.Textarea(attrs={'class': css_textarea, 'rows': 5}),
            'keywords': forms.TextInput(attrs={'class': css_input, 'placeholder': _("Kalit so'zlar (vergul bilan)")}),
            'pdf_file': forms.FileInput(attrs={'class': 'hidden', 'accept': '.docx,.doc'}),
        }

    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if file:
            validate_article_file(file)
        return file


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': css_input,
            'placeholder': _('email@example.com'),
            'autocomplete': 'email',
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # username ni majburiy emas qilamiz (auto-generatsiya)
        if 'username' in self.fields:
            self.fields['username'].required = False
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            if css_input not in existing:
                field.widget.attrs['class'] = css_input + ' ' + existing
        self.fields['email'].widget.attrs['placeholder']      = _('email@example.com')
        self.fields['first_name'].widget.attrs['placeholder'] = _('Ism')
        self.fields['last_name'].widget.attrs['placeholder']  = _('Familiya')
        self.fields['password1'].widget.attrs['placeholder']  = _('Parol')
        self.fields['password2'].widget.attrs['placeholder']  = _('Parolni tasdiqlang')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Bu email allaqachon ro'yxatdan o'tgan."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].lower().strip()
        user.email = email
        # Username: email local part + random digits if taken
        base = email.split('@')[0][:28]
        import random, string
        username = base
        while User.objects.filter(username=username).exists():
            username = base + ''.join(random.choices(string.digits, k=4))
        user.username = username
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Profil ma'lumotlarini yangilash"""
    class Meta:
        model = User
        fields = ['avatar', 'first_name', 'last_name', 'email', 'institution', 'phone', 'bio']
        widgets = {
            'first_name':  forms.TextInput(attrs={'class': css_input, 'placeholder': _('Ism')}),
            'last_name':   forms.TextInput(attrs={'class': css_input, 'placeholder': _('Familiya')}),
            'email':       forms.EmailInput(attrs={'class': css_input, 'placeholder': _('Email')}),
            'institution': forms.TextInput(attrs={'class': css_input, 'placeholder': _('Universitet / Tashkilot')}),
            'phone':       forms.TextInput(attrs={'class': css_input, 'placeholder': _('+998 XX XXX XX XX')}),
            'bio':         forms.Textarea(attrs={'class': css_textarea, 'rows': 4, 'placeholder': _("O'zingiz haqingizda qisqacha...")}),
            'avatar':      forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'}),
        }

    def clean_avatar(self):
        file = self.cleaned_data.get('avatar')
        if file and hasattr(file, 'size'):
            validate_image_file(file)
        return file


class CustomPasswordChangeForm(PasswordChangeForm):
    """Parol o'zgartirish"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': css_input})
        self.fields['old_password'].widget.attrs['placeholder']  = _('Joriy parol')
        self.fields['new_password1'].widget.attrs['placeholder'] = _('Yangi parol')
        self.fields['new_password2'].widget.attrs['placeholder'] = _('Yangi parolni tasdiqlang')
