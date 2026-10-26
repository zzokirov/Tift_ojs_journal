"""
Qidiruv tizimlari uchun: robots.txt, sitemap.xml va favicon.ico
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import escape

from .models import Journal, JournalIssue, Article


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /reviewer/",
        "Disallow: /my-articles/",
        "Disallow: /profile/",
        "Disallow: /login/",
        "Disallow: /signup/",
        "Disallow: /change-language/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_xml(request):
    urls = [(request.build_absolute_uri('/'), None)]

    journals = Journal.objects.filter(is_active=True, publication_status='published')
    for j in journals:
        for name in ('index', 'archive', 'about'):
            urls.append((request.build_absolute_uri(reverse(name, args=[j.slug])), None))

    issues = JournalIssue.objects.filter(is_published=True, journal__in=journals).select_related('journal')
    for i in issues:
        urls.append((request.build_absolute_uri(reverse('issue_detail', args=[i.journal.slug, i.pk])), i.updated_at))

    articles = Article.objects.filter(status='published', journal__in=journals).select_related('journal')
    for a in articles:
        urls.append((request.build_absolute_uri(reverse('article_detail', args=[a.journal.slug, a.pk])), a.updated_at))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        parts.append(f"<url><loc>{escape(loc)}</loc>")
        if lastmod:
            parts.append(f"<lastmod>{lastmod.date().isoformat()}</lastmod>")
        parts.append("</url>")
    parts.append("</urlset>")
    return HttpResponse("\n".join(parts), content_type="application/xml")


def favicon_ico(request):
    return redirect(static('images/tift.png'), permanent=True)
