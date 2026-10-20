from modeltranslation.translator import register, TranslationOptions
from .models import Journal, ArticleCategory, StaffMember, Article, News, Conference, Document

@register(Journal)
class JournalTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'full_description', 'description', 'research_areas', 'publication_frequency')

@register(ArticleCategory)
class ArticleCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(StaffMember)
class StaffMemberTranslationOptions(TranslationOptions):
    fields = ('full_name', 'position', 'workplace', 'bio', 'academic_degree', 'academic_title', 'institution')

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
