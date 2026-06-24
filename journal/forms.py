from django import forms
from .models import Article

class ArticleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Article
        # Muallif o'zi to'ldirishi kerak bo'lgan maydonlar
        fields = ['title', 'abstract', 'keywords', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Maqola sarlavhasi'}),
            'abstract': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 5}),
            'keywords': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'pdf_file': forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# O'zimizning User modelimiz bilan ishlaydigan ro'yxatdan o'tish formasi
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')