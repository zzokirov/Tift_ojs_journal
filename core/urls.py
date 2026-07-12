from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('journal.urls')),
]

# Media va statik fayllarni har doim lokal papkadan taqdim etish
# (DEBUG=False bo'lganda ham ishlaydi — Nginx yoki WhiteNoise bilan birga)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)