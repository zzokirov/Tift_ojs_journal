from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ArticleCategory, StaffMember, Article, News, Conference, Document
import threading

def translate_text(text, target_lang):
    if not text:
        return text
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='uz', target=target_lang)
        # Deep translator supports up to 5k chars natively
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def auto_translate_fields(instance, fields):
    for field in fields:
        uz_val = getattr(instance, f"{field}_uz", None)
        ru_val = getattr(instance, f"{field}_ru", None)
        en_val = getattr(instance, f"{field}_en", None)

        if uz_val:
            # Only translate if RU or EN are missing or empty
            if not ru_val or not ru_val.strip():
                setattr(instance, f"{field}_ru", translate_text(uz_val, 'ru'))
            if not en_val or not en_val.strip():
                setattr(instance, f"{field}_en", translate_text(uz_val, 'en'))

@receiver(pre_save, sender=ArticleCategory)
def translate_category(sender, instance, **kwargs):
    auto_translate_fields(instance, ['name'])

@receiver(pre_save, sender=StaffMember)
def translate_staff(sender, instance, **kwargs):
    auto_translate_fields(instance, ['full_name', 'position', 'workplace', 'bio'])

@receiver(pre_save, sender=Article)
def translate_article(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'abstract', 'keywords'])

@receiver(pre_save, sender=News)
def translate_news(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'content'])

@receiver(pre_save, sender=Conference)
def translate_conference(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'description'])

@receiver(pre_save, sender=Document)
def translate_document(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'description'])
