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

def _fit(instance, field_name, value):
    """Tarjima o'zbekchadan uzunroq bo'lishi mumkin: maydon chegarasidan oshsa baza
    (PostgreSQL) xato beradi va saqlash 500 bilan tugaydi. Shuning uchun qisqartiramiz."""
    if not isinstance(value, str):
        return value
    try:
        limit = instance._meta.get_field(field_name).max_length
    except Exception:
        limit = None
    if limit and len(value) > limit:
        value = value[:limit - 1].rstrip() + '…'
    return value


def auto_translate_fields(instance, fields, update_fields=None):
    # save(update_fields=[...]) tarjima maydonlariga tegmasa — tarmoqqa so'rov yubormaymiz
    if update_fields is not None and not any(
            f == fld or f.startswith(fld + '_') for f in update_fields for fld in fields):
        return
    for field in fields:
        uz_val = getattr(instance, f"{field}_uz", None)
        ru_val = getattr(instance, f"{field}_ru", None)
        en_val = getattr(instance, f"{field}_en", None)

        if uz_val:
            # Only translate if RU or EN are missing or empty
            if not ru_val or not ru_val.strip():
                setattr(instance, f"{field}_ru", _fit(instance, f"{field}_ru", translate_text(uz_val, 'ru')))
            if not en_val or not en_val.strip():
                setattr(instance, f"{field}_en", _fit(instance, f"{field}_en", translate_text(uz_val, 'en')))

@receiver(pre_save, sender=ArticleCategory)
def translate_category(sender, instance, **kwargs):
    auto_translate_fields(instance, ['name'], kwargs.get('update_fields'))

@receiver(pre_save, sender=StaffMember)
def translate_staff(sender, instance, **kwargs):
    auto_translate_fields(instance, ['full_name', 'position', 'workplace', 'bio'], kwargs.get('update_fields'))

@receiver(pre_save, sender=Article)
def translate_article(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'abstract', 'keywords'], kwargs.get('update_fields'))

@receiver(pre_save, sender=News)
def translate_news(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'content'], kwargs.get('update_fields'))

@receiver(pre_save, sender=Conference)
def translate_conference(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'description', 'organization', 'location'], kwargs.get('update_fields'))

@receiver(pre_save, sender=Document)
def translate_document(sender, instance, **kwargs):
    auto_translate_fields(instance, ['title', 'description'], kwargs.get('update_fields'))
