from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalDomainMiddleware:
    """Eski domen (masalan architect-edu.tift.uz) orqali kelgan so'rovlarni asosiy domenga
    301 bilan yo'naltiradi. Faqat REDIRECT_OLD_DOMAINS=True bo'lganda ishlaydi, shunda
    yangi domen DNS/SSL'i tayyor bo'lmaguncha sayt buzilmaydi."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'REDIRECT_OLD_DOMAINS', False):
            host = request.get_host().split(':')[0].lower()
            if host in [h.lower() for h in getattr(settings, 'OLD_DOMAINS', [])] and host != settings.SITE_DOMAIN:
                return HttpResponsePermanentRedirect(f"https://{settings.SITE_DOMAIN}{request.get_full_path()}")
        return self.get_response(request)
