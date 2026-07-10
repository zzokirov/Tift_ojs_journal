from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import Article

User = get_user_model()

css_input  = 'w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white transition-colors'
css_textarea = 'w-full px-4 py-3 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:bg-white transition-colors resize-none'


class ArticleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'abstract', 'keywords', 'pdf_file']
        widgets = {
            'title':    forms.TextInput(attrs={'class': css_input, 'placeholder': 'Maqola sarlavhasi'}),
            'abstract': forms.Textarea(attrs={'class': css_textarea, 'rows': 5}),
            'keywords': forms.TextInput(attrs={'class': css_input, 'placeholder': 'Kalit so\'zlar (vergul bilan)'}),
            'pdf_file': forms.FileInput(attrs={'class': 'hidden', 'accept': '.docx'}),
        }


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


class CustomPasswordChangeForm(PasswordChangeForm):
    """Parol o'zgartirish"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': css_input})
        self.fields['old_password'].widget.attrs['placeholder']  = 'Joriy parol'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Yangi parol'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Yangi parolni tasdiqlang'
