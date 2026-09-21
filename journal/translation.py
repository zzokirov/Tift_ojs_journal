from modeltranslation.translator import register, TranslationOptions
from .models import ArticleCategory, StaffMember, Article, News, Conference, Document

@register(ArticleCategory)
class ArticleCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(StaffMember)
class StaffMemberTranslationOptions(TranslationOptions):
    fields = ('full_name', 'position', 'workplace', 'bio')

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'abstract', 'keywords')

@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(Conference)
class ConferenceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Document)
class DocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
