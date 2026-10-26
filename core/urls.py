from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from journal import seo

# Admin bosh sahifasi o'rniga to'g'ridan-to'g'ri Jurnallar ro'yxatiga yo'naltirish
def admin_redirect_to_journals(request, extra_context=None):
    return redirect('/admin/journal/journal/')

admin.site.index = admin_redirect_to_journals

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('robots.txt', seo.robots_txt),
    path('sitemap.xml', seo.sitemap_xml),
    path('favicon.ico', seo.favicon_ico),
    path('admin/', admin_redirect_to_journals),
    path('admin/', admin.site.urls),
    path('', include('journal.urls')),
]

# Media va statik fayllarni har doim lokal papkadan taqdim etish
# (DEBUG=False bo'lganda ham ishlaydi — Nginx yoki WhiteNoise bilan birga)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
