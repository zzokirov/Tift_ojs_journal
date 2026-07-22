from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Article

User = get_user_model()

css_input  = 'w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white transition-colors'
css_textarea = 'w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white transition-colors resize-none'

# Ruxsat etilgan MIME turlari va ularning kengaytmalari
ALLOWED_ARTICLE_MIME = {
    'application/pdf': ['.pdf'],
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
        raise ValidationError(f"Fayl hajmi 20 MB dan oshmasligi kerak. Hozirgi hajm: {file.size // (1024*1024)} MB")

    # Kengaytma tekshiruvi
    import os
    ext = os.path.splitext(file.name)[1].lower()
    allowed_exts = [e for exts in ALLOWED_ARTICLE_MIME.values() for e in exts]
    if ext not in allowed_exts:
        raise ValidationError(f"Faqat PDF va DOCX fayllar qabul qilinadi. Yuborilgan: {ext}")

    # MIME tekshiruvi
    mime = _get_mime_type(file)
    if mime and mime not in ALLOWED_ARTICLE_MIME:
        raise ValidationError(f"Fayl turi qabul qilinmaydi. Aniqlangan tur: {mime}")


def validate_image_file(file):
    """Rasm faylini MIME va hajm bo'yicha tekshiradi."""
    if not file:
        return

    # Hajm tekshiruvi
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(f"Rasm hajmi 5 MB dan oshmasligi kerak.")

    # Kengaytma tekshiruvi
    import os
    ext = os.path.splitext(file.name)[1].lower()
    allowed_exts = [e for exts in ALLOWED_IMAGE_MIME.values() for e in exts]
    if ext not in allowed_exts:
        raise ValidationError(f"Faqat JPG, PNG, WEBP, GIF rasmlari qabul qilinadi.")

    # MIME tekshiruvi
    mime = _get_mime_type(file)
    if mime and mime not in ALLOWED_IMAGE_MIME:
        raise ValidationError(f"Rasm turi qabul qilinmaydi. Aniqlangan tur: {mime}")


class ArticleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'abstract', 'keywords', 'pdf_file']
        widgets = {
            'title':    forms.TextInput(attrs={'class': css_input, 'placeholder': 'Maqola sarlavhasi'}),
            'abstract': forms.Textarea(attrs={'class': css_textarea, 'rows': 5}),
            'keywords': forms.TextInput(attrs={'class': css_input, 'placeholder': 'Kalit so\'zlar (vergul bilan)'}),
            'pdf_file': forms.FileInput(attrs={'class': 'hidden', 'accept': '.pdf,.docx'}),
        }

    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if file:
            validate_article_file(file)
        return file


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = css_input + ' ' + existing
        self.fields['username'].widget.attrs['placeholder']   = 'Foydalanuvchi nomi'
        self.fields['email'].widget.attrs['placeholder']      = 'Email manzil'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ism'
        self.fields['last_name'].widget.attrs['placeholder']  = 'Familiya'
        self.fields['password1'].widget.attrs['placeholder']  = 'Parol'
        self.fields['password2'].widget.attrs['placeholder']  = 'Parolni tasdiqlang'


class ProfileUpdateForm(forms.ModelForm):
    """Profil ma'lumotlarini yangilash"""
    class Meta:
        model = User
        fields = ['avatar', 'first_name', 'last_name', 'email', 'institution', 'phone', 'bio']
        widgets = {
            'first_name':  forms.TextInput(attrs={'class': css_input, 'placeholder': 'Ism'}),
            'last_name':   forms.TextInput(attrs={'class': css_input, 'placeholder': 'Familiya'}),
            'email':       forms.EmailInput(attrs={'class': css_input, 'placeholder': 'Email'}),
            'institution': forms.TextInput(attrs={'class': css_input, 'placeholder': 'Universitet / Tashkilot'}),
            'phone':       forms.TextInput(attrs={'class': css_input, 'placeholder': '+998 XX XXX XX XX'}),
            'bio':         forms.Textarea(attrs={'class': css_textarea, 'rows': 4, 'placeholder': 'O\'zingiz haqingizda qisqacha...'}),
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
        self.fields['old_password'].widget.attrs['placeholder']  = 'Joriy parol'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Yangi parol'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Yangi parolni tasdiqlang'
