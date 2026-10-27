
def switch_language(request, lang_code):
    """
    Bulletproof language switcher supporting GET and POST.
    Sets session and cookie for the selected language.
    """
    next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    if not next_url or '/i18n/' in next_url or '/change-language/' in next_url:
        next_url = '/'

    from django.utils.translation import activate, check_for_language
    from django.conf import settings
    from django.http import HttpResponseRedirect

    response = HttpResponseRedirect(next_url)
    if check_for_language(lang_code):
        activate(lang_code)
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
            request.session['_language'] = lang_code
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=365 * 24 * 60 * 60,
            path='/',
            samesite='Lax'
        )
    return response


from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Journal, JournalIssue, Article, ArticleCategory, StaffMember, SiteVisit, Conference, News, Document
from .forms import ArticleSubmissionForm, CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm
from django.utils.translation import gettext as _


def portal_home(request):
    q = request.GET.get('q', '').strip()
    journals = Journal.objects.filter(is_active=True, publication_status='published')
    
    if q:
        journals = journals.filter(
            Q(title__icontains=q) |
            Q(title_uz__icontains=q) |
            Q(title_ru__icontains=q) |
            Q(title_en__icontains=q) |
            Q(issn__icontains=q) |
            Q(short_description__icontains=q) |
            Q(full_description__icontains=q) |
            Q(description__icontains=q) |
            Q(research_areas__icontains=q) |
            Q(categories__name__icontains=q)
        ).distinct()
    
    journals = journals.order_by('display_order', 'id')
    
    context = {
        'journals': journals,
        'search_query': q,
        'current_journal': None,
    }
    return render(request, 'portal_home.html', context)


import urllib.parse
import re

def _clean_tokens(s):
    s = urllib.parse.unquote(str(s)).lower()
    s = s.replace("'", "").replace("’", "").replace("`", "").replace("ʻ", "")
    s = s.replace('ll', 'l').replace('nn', 'n').replace('ss', 's').replace('mm', 'm')
    import re
    return set(re.findall(r'[a-z0-9]+', s))

def _get_current_journal(journal_slug):
    """
    Resilient journal finder:
    1. Exact slug match
    2. URL decoded slug match
    3. Normalized hyphenated lowercase match
    4. Architecture journal aliases
    5. Case-insensitive title match
    6. Token / typo-tolerant match
    7. Fallback 404
    """
    raw_slug = str(journal_slug).strip()
    decoded_slug = urllib.parse.unquote(raw_slug).strip()

    # 1. Exact match
    j = Journal.objects.filter(slug=raw_slug).first()
    if j:
        return j
    if decoded_slug != raw_slug:
        j = Journal.objects.filter(slug=decoded_slug).first()
        if j:
            return j

    # 2. Normalized slug (replace spaces, underscores with hyphens, lowercase)
    norm_slug = re.sub(r'[\s_]+', '-', decoded_slug.lower()).strip('-')
    j = Journal.objects.filter(slug__iexact=norm_slug).first()
    if j:
        return j

    # 3. Architecture journal aliases
    arch_aliases = [
        'arxitektura', 'arxitektura-va-talim', 'arxitektura va talim',
        'arxitektura-va-ta-lim', "arxitektura-va-ta'lim", "arxitektura va ta'lim",
        'aritektura', 'aritektura-va-talim', 'aritektura va talim',
        'architect-edu', 'architecture', 'architecture-and-education'
    ]
    if norm_slug in arch_aliases or decoded_slug.lower() in arch_aliases:
        j = Journal.objects.filter(Q(slug='arxitektura-va-talim') | Q(slug='arxitektura')).first()
        if j:
            return j
        j = Journal.objects.filter(is_active=True).first()
        if j:
            return j

    # 4. Search by title
    space_slug = decoded_slug.replace('-', ' ')
    j = Journal.objects.filter(
        Q(title__iexact=decoded_slug) |
        Q(title__iexact=space_slug) |
        Q(title_uz__iexact=decoded_slug) |
        Q(title_uz__iexact=space_slug) |
        Q(title_ru__iexact=decoded_slug) |
        Q(title_en__iexact=decoded_slug)
    ).first()
    if j:
        return j

    # 5. Token / typo-tolerant match
    input_tokens = _clean_tokens(decoded_slug)
    meaningful = {t for t in input_tokens if t not in {'va', 'and', 'i', 'the', 'of'}} or input_tokens
    if meaningful:
        best_journal = None
        best_score = 0.0
        for cand in Journal.objects.all():
            cand_tokens = _clean_tokens(cand.slug) | _clean_tokens(cand.title)
            intersection = meaningful & cand_tokens
            if intersection:
                score = len(intersection) / len(meaningful)
                if score > best_score and score >= 0.5:
                    best_score = score
                    best_journal = cand
        if best_journal:
            return best_journal

    # 6. Fallback
    return get_object_or_404(Journal, slug=raw_slug)


def index(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    # User can browse the journal directly without forced redirect

    # Tashrif buyuruvchilarni sanash
    total_visitors = 0
    today_visitors = 0
    week_labels = []
    week_data = []
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1'))
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        from datetime import date, timedelta
        SiteVisit.objects.get_or_create(date=date.today(), ip_address=ip)
        total_visitors = SiteVisit.objects.count()
        today_visitors = SiteVisit.objects.filter(date=date.today()).count()
        # So'nggi 7 kunlik statistika
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            week_labels.append(d.strftime('%d.%m'))
            week_data.append(SiteVisit.objects.filter(date=d).count())
    except Exception:
        pass

    query = request.GET.get('q')
    recent_articles = []
    grouped_categories = []
    latest_issue = None
    try:
        latest_issue = JournalIssue.objects.filter(journal=current_journal).order_by('-year', '-number').first()
        if latest_issue and not query:
            recent_qs = Article.objects.filter(journal=current_journal, issue=latest_issue, status='published').select_related('category', 'author').order_by('category__order', 'category__id', 'order_in_issue', 'start_page', 'id')
        else:
            recent_qs = Article.objects.filter(journal=current_journal, status='published').select_related('category', 'author').order_by('category__order', 'category__id', 'order_in_issue', 'start_page', 'id')

        if query:
            recent_qs = recent_qs.filter(
                Q(title__icontains=query) |
                Q(abstract__icontains=query) |
                Q(keywords__icontains=query) |
                Q(authors__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query) |
                Q(author__username__icontains=query)
            )

        from collections import OrderedDict
        categories_dict = OrderedDict()
        uncategorized = []
        for art in recent_qs:
            if art.category:
                if art.category not in categories_dict:
                    categories_dict[art.category] = []
                categories_dict[art.category].append(art)
            else:
                uncategorized.append(art)

        for cat, arts in categories_dict.items():
            grouped_categories.append({
                'category': cat,
                'articles': arts
            })
        if uncategorized:
            grouped_categories.append({
                'category': None,
                'articles': uncategorized
            })
        recent_articles = list(recent_qs)
    except Exception:
        recent_articles = []
        grouped_categories = []

    issues = []
    try:
        issues = list(JournalIssue.objects.filter(journal=current_journal).order_by('-year', '-number'))
    except Exception:
        issues = []

    total_articles = 0
    try:
        total_articles = Article.objects.filter(journal=current_journal, status='published').count()
    except Exception:
        total_articles = 0

    categories = ArticleCategory.objects.filter(journal=current_journal).order_by('order', 'code')
    staff = StaffMember.objects.filter(journal=current_journal, is_active=True).order_by('order', 'full_name')[:6]

    from .context_processors import journal_theme_for_slug
    theme = journal_theme_for_slug(current_journal.slug)
    return render(request, [f'themes/{theme}/index.html', 'index.html'], {
        'current_journal': current_journal,
        'recent_articles': recent_articles,
        'grouped_categories': grouped_categories,
        'latest_issue': latest_issue,
        'issues': issues,
        'staff': staff,
        'query': query,
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'week_labels': week_labels,
        'week_data': week_data,
        'total_articles': total_articles,
        'categories': categories,
    })


def archive(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    issues = JournalIssue.objects.filter(journal=current_journal, is_published=True).order_by('-year', '-number')
    return render(request, 'archive.html', {'current_journal': current_journal, 'issues': issues})


def about(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    staff = StaffMember.objects.filter(journal=current_journal, is_active=True).order_by('order', 'full_name')
    leadership = staff.filter(position__in=['editor_in_chief', 'deputy_editor', 'secretary'])
    editorial_board = staff.filter(position='member')
    categories = ArticleCategory.objects.filter(journal=current_journal).order_by('order', 'code')
    return render(request, 'about.html', {
        'current_journal': current_journal,
        'staff': staff,
        'leadership': leadership,
        'editorial_board': editorial_board,
        'categories': categories,
    })


def issue_detail(request, journal_slug, issue_pk):
    current_journal = _get_current_journal(journal_slug)
    issue = get_object_or_404(JournalIssue, pk=issue_pk, journal=current_journal)
    if not issue.is_published and issue.status != 'published':
        if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
            raise Http404(_("Ushbu jurnal soni hali chop etilmagan."))
    articles = Article.objects.filter(issue=issue, status='published').select_related('category', 'author').order_by('category__order', 'category__id', 'order_in_issue', 'start_page', 'id')

    from collections import OrderedDict
    categories_dict = OrderedDict()
    uncategorized = []
    for art in articles:
        if art.category:
            if art.category not in categories_dict:
                categories_dict[art.category] = []
            categories_dict[art.category].append(art)
        else:
            uncategorized.append(art)

    grouped_categories = []
    for cat, arts in categories_dict.items():
        grouped_categories.append({
            'category': cat,
            'articles': arts
        })
    if uncategorized:
        grouped_categories.append({
            'category': None,
            'articles': uncategorized
        })

    return render(request, 'journal/issue_detail.html', {
        'current_journal': current_journal,
        'issue': issue,
        'articles': articles,
        'grouped_categories': grouped_categories,
    })


def article_detail(request, journal_slug, pk):
    current_journal = _get_current_journal(journal_slug)
    try:
        article = get_object_or_404(Article, pk=pk, journal=current_journal)

        # 1. Views count update
        try:
            if not request.session.get(f'viewed_article_{pk}'):
                article.views_count = (article.views_count or 0) + 1
                article.save(update_fields=['views_count'])
                request.session[f'viewed_article_{pk}'] = True
        except Exception:
            pass

        if article.issue and article.start_page is None:
            try:
                recalculate_issue_page_numbers(article.issue)
                article.refresh_from_db()
            except Exception:
                pass

        # 2. Muallif ma'lumotlari
        author_name = ''
        author_initial = 'A'
        author_institution = ''
        try:
            if article.authors:
                author_name = article.authors
                author_initial = article.authors[0].upper()
            elif article.author:
                author_name = article.author.get_full_name() or article.author.username
                author_initial = (author_name[0] if author_name else 'A').upper()
                author_institution = getattr(article.author, 'institution', '') or ''
        except Exception:
            pass

        # 3. Shu muallifning boshqa nashr etilgan maqolalari (faqat shu muallifga tegishli maqolalar)
        author_articles = []
        try:
            if article.authors:
                author_names = [n.strip() for n in article.authors.replace(';', ',').split(',') if len(n.strip()) > 3]
                if author_names:
                    q_author = Q()
                    for aname in author_names:
                        parts = aname.split()
                        if len(parts) >= 2:
                            q_author |= Q(authors__icontains=f"{parts[0]} {parts[1]}")
                        elif len(parts) == 1:
                            q_author |= Q(authors__icontains=parts[0])
                    author_articles = Article.objects.filter(
                        journal=current_journal,
                        status='published'
                    ).filter(q_author).exclude(pk=pk).order_by('-published_at', '-created_at')[:8]
            elif article.author and article.author.username not in ('tift', 'admin'):
                author_articles = Article.objects.filter(
                    author=article.author,
                    status='published',
                    journal=current_journal
                ).exclude(pk=pk).order_by('-created_at')[:8]
        except Exception:
            author_articles = []

        # 4. Maqola matnini HTML formatda olish (reader uchun)
        article_content_html = ''
        if article.pdf_file:
            try:
                article_content_html = _get_article_content_html(article.pdf_file) or ''
            except Exception:
                article_content_html = ''

        # 5. Kalit so'zlar ro'yxati
        keywords_list = []
        if article.keywords:
            try:
                keywords_list = [k.strip() for k in str(article.keywords).replace(';', ',').split(',') if k.strip()]
            except Exception:
                keywords_list = []

        return render(request, 'article_detail.html', {
            'current_journal': current_journal,
            'article': article,
            'author_name': author_name,
            'author_initial': author_initial,
            'author_institution': author_institution,
            'author_articles': author_articles,
            'article_content_html': article_content_html,
            'keywords_list': keywords_list,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            article = get_object_or_404(Article, pk=pk, journal=current_journal)
            return render(request, 'article_detail.html', {
                'current_journal': current_journal,
                'article': article,
                'author_name': getattr(article, 'authors', '') or _('Muallif'),
                'author_initial': 'A',
                'author_institution': '',
                'author_articles': [],
                'article_content_html': '',
                'keywords_list': [],
            })
        except Exception:
            from django.http import HttpResponse
            return HttpResponse(_("Maqola topilmadi yoki xatolik yuz berdi."), status=404)


def _clean_text(text):
    """
    Unicode belgilarni xhtml2pdf tushuna oladigan ko'rinishga keltiradi.
    Qora to'rtburchak (replacement char) va maxsus belgilarni almashtiradi.
    """
    import unicodedata
    # Normalizatsiya
    text = unicodedata.normalize('NFC', text)
    # Tez-tez muammo chiqaradigan Unicode belgilarni ASCII ga almashtirish
    replacements = {
        '\u2019': "'",   # ' (right single quotation)
        '\u2018': "'",   # ' (left single quotation)
        '\u201c': '"',   # " (left double quotation)
        '\u201d': '"',   # " (right double quotation)
        '\u2013': '-',   # – (en dash)
        '\u2014': '-',   # — (em dash)
        '\u2026': '...',  # … (ellipsis)
        '\u00a0': ' ',   # non-breaking space
        '\u00ad': '-',   # soft hyphen
        '\ufffd': '',    # replacement character (qora to'rtburchak)
        '\u25a0': '',    # ■ (qora kvadrat)
        '\u25a1': '',    # □ (oq kvadrat)
        '\u2022': '-',   # • (bullet)
        '\u00b7': '-',   # · (middle dot)
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _extract_pdf_text_as_html(pdf_path):
    """
    PDF fayldan matn, jadval va rasmlarni o'qib HTML qaytaradi.
    - Matn bloklari: paragraf/sarlavha sifatida
    - Rasm bloklari: PyMuPDF bilan render qilib base64 PNG sifatida
    PyMuPDF (fitz) ishlatiladi.
    """
    try:
        import fitz
        import html as html_lib
        import base64

        doc = fitz.open(pdf_path)
        result_html = []

        for page_idx, page in enumerate(doc):
            page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            page_rect = page.rect

            for block in page_dict.get("blocks", []):
                block_type = block.get("type", -1)

                # ── RASM BLOKI (type=1) ──
                if block_type == 1:
                    try:
                        # Rasm bbox ni olish
                        bbox = block.get("bbox")
                        if not bbox:
                            continue
                        rect = fitz.Rect(bbox)
                        # Clip rect orqali faqat shu qismni render qilamiz
                        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom — sifat uchun
                        clip = rect
                        pix = page.get_pixmap(matrix=mat, clip=clip)
                        img_bytes = pix.tobytes("png")
                        b64 = base64.b64encode(img_bytes).decode('ascii')
                        # Kenglikni pt da hisoblash (xhtml2pdf % ni tushunmaydi)
                        img_width_pt = rect.width
                        page_width_pt = page_rect.width
                        # Maksimal kenglik = sahifa kengligi (margins hisobga olingan)
                        content_width_pt = page_width_pt - 142  # ~5cm margin jami
                        render_width_pt = min(img_width_pt, content_width_pt)
                        result_html.append(
                            f'<div class="doc-img-wrap">'
                            f'<img src="data:image/png;base64,{b64}" '
                            f'style="width:{render_width_pt:.0f}pt;max-width:100%;height:auto;display:block;margin:6pt auto;"/>'
                            f'</div>'
                        )
                    except Exception:
                        pass
                    continue

                # ── MATN BLOKI (type=0) ──
                if block_type != 0:
                    continue

                block_lines = []
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    stripped = line_text.strip()
                    if stripped:
                        block_lines.append(stripped)

                if not block_lines:
                    continue

                block_text = " ".join(block_lines)

                # Font o'lcham va bold tekshirish
                font_size = 11
                is_bold = False
                if block.get("lines"):
                    first_spans = block["lines"][0].get("spans", [])
                    if first_spans:
                        font_size = first_spans[0].get("size", 11)
                        flags = first_spans[0].get("flags", 0)
                        is_bold = bool(flags & 16)

                escaped = html_lib.escape(_clean_text(block_text))

                if font_size >= 14 or (font_size >= 12 and is_bold):
                    result_html.append(f'<h2 class="doc-heading">{escaped}</h2>')
                elif font_size >= 12:
                    result_html.append(f'<h3 class="doc-subheading">{escaped}</h3>')
                else:
                    result_html.append(f'<p>{escaped}</p>')

        doc.close()
        return '\n'.join(result_html)
    except Exception:
        return ''


def _extract_docx_text_as_html(docx_path):
    """
    Word (.docx) fayldan matn, sarlavha, jadval va rasmlarni HTML ga o'giradi.
    - Paragraflar: stil bo'yicha sarlavha/paragraf
    - Jadvallar: to'liq HTML jadval
    - Rasmlar: base64 PNG sifatida inline embed
    python-docx ishlatiladi.
    """
    try:
        import docx
        import html as html_lib
        import base64
        from docx.oxml.ns import qn
        from lxml import etree

        doc = docx.Document(docx_path)

        # Barcha relationships (rImage) dan rasm ma'lumotlarini olish
        # doc.part.rels: {rId: rel}
        def get_image_base64(rel_id):
            try:
                rel = doc.part.rels.get(rel_id)
                if rel and "image" in rel.reltype:
                    img_data = rel.target_part.blob
                    ext = rel.target_part.content_type.split('/')[-1]
                    if ext == 'jpeg':
                        ext = 'jpg'
                    b64 = base64.b64encode(img_data).decode('ascii')
                    return f"data:image/{ext};base64,{b64}"
            except Exception:
                pass
            return None

        result_html = []

        # Body ichidagi barcha elementlarni tartib bilan o'tamiz
        for child in doc.element.body:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

            # ── PARAGRAF ──
            if tag == 'p':
                para = None
                for p in doc.paragraphs:
                    if p._element is child:
                        para = p
                        break
                if para is None:
                    continue

                # Paragrafda rasm borligini tekshirish (drawing/blipFill)
                drawings = child.findall('.//' + qn('a:blip'))
                if drawings:
                    # Rasmlar embed yoki link orqali
                    for blip in drawings:
                        r_embed = blip.get(qn('r:embed'))
                        r_link = blip.get(qn('r:link'))
                        rid = r_embed or r_link
                        if rid:
                            src = get_image_base64(rid)
                            if src:
                                result_html.append(
                                    f'<div class="doc-img-wrap">'
                                    f'<img src="{src}" style="max-width:100%;height:auto;display:block;margin:6pt auto;"/>'
                                    f'</div>'
                                )
                    # Agar paragrafda matn ham bor bo'lsa
                    text = para.text.strip()
                    if text:
                        escaped = html_lib.escape(text)
                        result_html.append(f'<p class="img-caption">{escaped}</p>')
                    continue

                text = para.text.strip()
                if not text:
                    continue

                style_name = para.style.name.lower() if para.style else ''
                escaped = html_lib.escape(_clean_text(text))

                if 'heading 1' in style_name or style_name == 'title':
                    result_html.append(f'<h2 class="doc-heading">{escaped}</h2>')
                elif 'heading 2' in style_name:
                    result_html.append(f'<h3 class="doc-subheading">{escaped}</h3>')
                elif 'heading' in style_name:
                    result_html.append(f'<h4 class="doc-subheading">{escaped}</h4>')
                else:
                    is_bold = any(run.bold for run in para.runs if run.text.strip())
                    if is_bold and len(text) < 120:
                        result_html.append(f'<p><strong>{escaped}</strong></p>')
                    else:
                        result_html.append(f'<p>{escaped}</p>')

            # ── JADVAL ──
            elif tag == 'tbl':
                tbl = None
                for t in doc.tables:
                    if t._element is child:
                        tbl = t
                        break
                if tbl is None:
                    continue

                table_html = ['<table class="doc-table">']
                for i, row in enumerate(tbl.rows):
                    table_html.append('<tr>')
                    for cell in row.cells:
                        cell_text = html_lib.escape(_clean_text(cell.text.strip()))
                        if i == 0:
                            table_html.append(f'<th>{cell_text}</th>')
                        else:
                            table_html.append(f'<td>{cell_text}</td>')
                    table_html.append('</tr>')
                table_html.append('</table>')
                result_html.append('\n'.join(table_html))

        return '\n'.join(result_html)
    except Exception:
        return ''


def _get_logo_base64():
    """TIFT logosini base64 PNG ga o'giradi (PDF uchun inline embed).
    WebP bo'lsa Pillow bilan PNG ga konvertatsiya qilinadi.
    """
    import base64, os, io
    from django.conf import settings

    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'tift.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'tift.png')

    try:
        from PIL import Image
        img = Image.open(logo_path).convert('RGBA')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        return 'data:image/png;base64,' + b64
    except Exception:
        return ''


def _get_qr_code_base64(article, request=None):
    """
    Maqola sahifasiga yo'naltiruvchi QR kodni tayyorlaydi (base64 string).
    """
    try:
        import qrcode
        import io
        import base64
        qr = qrcode.QRCode(version=1, box_size=5, border=0)
        qr_url = None
        if request:
            try:
                qr_url = request.build_absolute_uri(f"/article/{article.pk}/")
            except BaseException:
                pass
        if not qr_url:
            qr_url = f"https://architect-edu.tift.uz/article/{article.pk}/"

        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode('ascii')
    except BaseException:
        return ""


def _get_file_bytes(article_file):
    """
    Fayl maydonidan bytes qaytaradi.
    Lokal (path) bo'lsa — disk dan o'qiydi.
    Cloudinary (URL) bo'lsa — HTTP orqali yuklab oladi.
    """
    import os
    try:
        # Lokal fayl
        path = article_file.path
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read(), path
    except (NotImplementedError, AttributeError, Exception):
        pass

    # Cloudinary yoki tashqi URL
    try:
        import requests as req
        url = article_file.url
        if url:
            resp = req.get(url, timeout=30)
            if resp.status_code == 200:
                # Vaqtinchalik fayl sifatida saqlash
                import tempfile
                suffix = '.' + url.split('?')[0].rsplit('.', 1)[-1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(resp.content)
                tmp.close()
                return resp.content, tmp.name
    except Exception:
        pass

    return None, None


def _strip_duplicate_header_from_html(html_str, title="", authors_str=""):
    """
    pdf_content_html boshidagi barcha takroriy sarlavha, muallif ismlari,
    ish joylari va e-mail manzillari (ABSTRACT bo'limigacha) olib tashlaydi.
    """
    if not html_str:
        return ''

    import re

    # Abstract/Annotatsiya sarlavhasini izlash
    abstract_pattern = re.compile(
        r'(<p[^>]*>\s*(?:<[^>]+>)*\s*(?:abstract|annotatsiya|аннотация|abstrakt|summary)[\s:]*.*?</p>|'
        r'<h[1-6][^>]*>.*?(?:abstract|annotatsiya|аннотация|abstrakt|summary).*?</h[1-6]>|'
        r'<div[^>]*>.*?(?:abstract|annotatsiya|аннотация|abstrakt|summary).*?</div>)',
        re.IGNORECASE | re.DOTALL
    )

    match = abstract_pattern.search(html_str)
    if match:
        start_pos = match.start()
        return html_str[start_pos:]

    # Gar abstract sarlavhasi topilmasa, e-mail/muallif/sarlavha bloklarini tozalaymiz
    blocks = re.split(r'(</(?:p|h1|h2|h3|h4|div)>)', html_str, flags=re.IGNORECASE)
    reconstructed = []
    i = 0
    skip_mode = True

    norm_title = re.sub(r'\s+', ' ', (title or '').lower().strip())
    norm_authors = re.sub(r'\s+', ' ', (authors_str or '').lower().strip())
    title_words = set(w for w in norm_title.split() if len(w) > 3)
    author_words = set(w for w in norm_authors.split() if len(w) > 3)

    while i < len(blocks):
        block = blocks[i]
        tag_close = blocks[i+1] if i+1 < len(blocks) else ''
        full_block = block + tag_close
        i += 2

        clean_text = re.sub(r'<[^>]+>', '', block).strip()
        norm_clean = re.sub(r'\s+', ' ', clean_text.lower())

        if not norm_clean:
            continue

        if 'abstract' in norm_clean or 'annotatsiya' in norm_clean or 'key words' in norm_clean or 'kalit so' in norm_clean or 'kirish' in norm_clean or 'introduction' in norm_clean:
            skip_mode = False

        if skip_mode:
            # E-mail, PhD, Student, Agency, University va h.k. bo'lsa tashlab yuboramiz
            if ('e-mail' in norm_clean or 'email' in norm_clean or '@' in norm_clean or 
                'phd' in norm_clean or 'student' in norm_clean or 'tashkent' in norm_clean or 
                'university' in norm_clean or 'agency' in norm_clean or 'institut' in norm_clean or 
                'academy' in norm_clean or len(norm_clean) < 15):
                continue

            words_in_block = set(w for w in norm_clean.split() if len(w) > 3)

            if len(title_words) > 0 and len(words_in_block) > 0:
                overlap = title_words.intersection(words_in_block)
                if len(overlap) / len(title_words) >= 0.25:
                    continue

            if len(author_words) > 0 and len(words_in_block) > 0:
                auth_overlap = author_words.intersection(words_in_block)
                if len(auth_overlap) / len(author_words) >= 0.3:
                    continue

            skip_mode = False

        reconstructed.append(full_block)

    return ''.join(reconstructed) if reconstructed else html_str


def _get_article_content_html(article_file, article=None):
    """
    Fayl ob'ektidan (FileField) matn/rasm HTML qaytaradi.
    Lokal va Cloudinary (URL) ni qo'llab-quvvatlaydi.
    """
    if not article_file:
        return ''

    import os, tempfile

    # Lokal fayl
    file_path = None
    is_tmp = False
    try:
        path = article_file.path
        if os.path.exists(path):
            file_path = path
    except Exception:
        pass

    # URL (Cloudinary)
    if not file_path:
        try:
            import requests as req
            url = article_file.url
            resp = req.get(url, timeout=30)
            if resp.status_code == 200:
                url_name = url.split('?')[0]
                suffix = '.' + url_name.rsplit('.', 1)[-1]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(resp.content)
                tmp.close()
                file_path = tmp.name
                is_tmp = True
        except Exception:
            pass

    if not file_path:
        return ''

    try:
        url_or_name = getattr(article_file, 'name', '') or ''
        ext = url_or_name.lower().rsplit('.', 1)[-1].split('?')[0] if '.' in url_or_name else ''
        if ext in ('doc', 'docx'):
            res = _extract_docx_text_as_html(file_path) or ''
        else:
            res = _extract_pdf_text_as_html(file_path) or ''

        if article and res:
            authors_str = getattr(article, 'authors', '') or (article.author.get_full_name() if getattr(article, 'author', None) else '')
            res = _strip_duplicate_header_from_html(res, title=getattr(article, 'title', ''), authors_str=authors_str)

        return res
    except Exception:
        return ''
    finally:
        if is_tmp and file_path:
            try:
                os.unlink(file_path)
            except Exception:
                pass


def recalculate_issue_page_numbers(issue):
    """
    Jurnal sonidagi barcha chop etilgan maqolalarning to'plamdagi
    boshlanish (start_page) va tugash (end_page) sahifalarini avtomatik hisoblaydi va saqlaydi.
    """
    if not issue:
        return
    articles = list(Article.objects.filter(issue=issue, status='published').order_by('created_at', 'id'))
    if not articles:
        return

    # Muqovalar va tahririyat sahifalari (taxminan 5 sahifa)
    cover_pages = 5
    current_page = cover_pages + 1

    for art in articles:
        pages = 1
        if art.pdf_file:
            try:
                raw_bytes = _get_pdf_bytes(art.pdf_file)
                if raw_bytes:
                    import fitz
                    art_doc = fitz.open(stream=raw_bytes, filetype="pdf")
                    if len(art_doc) > 0:
                        pages = len(art_doc)
                    art_doc.close()
            except Exception:
                pass

        start_p = current_page
        end_p = current_page + pages - 1

        if art.start_page != start_p or art.end_page != end_p:
            Article.objects.filter(pk=art.pk).update(start_page=start_p, end_page=end_p)
            art.start_page = start_p
            art.end_page = end_p

        current_page = end_p + 1


def _add_header_footer_to_pdf(pdf_bytes, article):
    """
    PyMuPDF yordamida har bir PDF sahifasining pastki qismiga (Running Footer)
    toza va chiroyli kolontitul qo'shadi. Yuqori header olib tashlangan.
    Sahifa raqamlari toza ASCII matn shaklida ('Sahifa 7') bosiladi.
    """
    try:
        import fitz
        import io

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        NAVY = (0.04, 0.145, 0.251)       # #0a2540
        GRAY_TEXT = (0.35, 0.35, 0.35)   # #555555
        LINE_COLOR = (0.82, 0.85, 0.88)  # Och kulrang chiziq
        PRIMARY_LINE = (0.04, 0.145, 0.251)

        if article.issue:
            issue_full = f"{article.issue.year}-yil, {article.issue.number}-son (Jild {article.issue.volume})"
        else:
            issue_full = _("Maxsus son, 2026")

        for idx, page in enumerate(doc):
            w = page.rect.width
            h = page.rect.height
            margin_left = 85.0    # 3.0 cm (maqola matni bilan bir liniyada)
            margin_right = 42.5   # 1.5 cm
            footer_line_y = h - 40.0

            # PASTKI KOLONTITUL CHIZIQ
            try:
                line_color = PRIMARY_LINE if idx == 0 else LINE_COLOR
                page.draw_line(fitz.Point(margin_left, footer_line_y), fitz.Point(w - margin_right, footer_line_y), color=line_color, width=0.75 if idx == 0 else 0.5)
            except Exception:
                pass

            # CHAP TOMON MATNI (3cm uzoqlikdan)
            rect_f_left = fitz.Rect(margin_left, footer_line_y + 4, w - 100, h - 15)
            try:
                page.insert_textbox(rect_f_left, f"{getattr(article, 'journal', None) and article.journal.title or ''} | {issue_full}", fontsize=8, color=GRAY_TEXT, align=0)
            except Exception:
                pass

            # O'NG TOMON SAHIFA RAQAMI
            rect_f_right = fitz.Rect(w - 100, footer_line_y + 4, w - margin_right, h - 15)
            if article.start_page:
                actual_p = article.start_page + idx
                p_str = f"{actual_p}"
            else:
                p_str = f"{idx + 1}"
            try:
                page.insert_textbox(rect_f_right, p_str, fontsize=8.5, color=NAVY, align=2)
            except Exception:
                pass

        out = io.BytesIO()
        doc.save(out)
        doc.close()
        return out.getvalue()

    except Exception as e:
        print("Error stamping PDF footers:", e)
        return pdf_bytes


def _get_pdf_bytes(article_file):
    """
    FileField dan PDF bytes oladi.
    Lokal: disk dan, Cloudinary/URL: HTTP orqali.
    """
    import os
    # Lokal
    try:
        path = article_file.path
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()
    except Exception:
        pass
    # URL (Cloudinary)
    try:
        import requests as req
        resp = req.get(article_file.url, timeout=30)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass
    return None


def download_pdf(request, journal_slug, pk):
    """
    Maqola PDF faylini to'g'ridan-to'g'ri yuklab beradi.
    Eski murakkab algoritmlar va cheklovlar olib tashlangan.
    """
    import os
    from django.http import FileResponse, Http404
    from django.shortcuts import redirect as _redirect

    current_journal = _get_current_journal(journal_slug)
    article = get_object_or_404(Article, pk=pk, journal=current_journal)

    # Huquq tekshiruvi: Chop etilgan bo'lsa barchaga, aks holda muallif va xodimlarga
    is_author = request.user.is_authenticated and article.author_id == request.user.pk
    is_reviewer_or_staff = request.user.is_authenticated and (
        getattr(request.user, 'role', '') in ['reviewer', 'editor'] or
        request.user.is_staff or
        request.user.is_superuser or
        article.assigned_reviewer_id == request.user.pk
    )
    if article.status != 'published' and not (is_author or is_reviewer_or_staff):
        raise Http404(_("Maqola hali chop etilmagan."))

    Article.objects.filter(pk=pk).update(downloads_count=article.downloads_count + 1)

    if not article.pdf_file:
        raise Http404(_("Maqola PDF fayli yuklanmagan."))

    safe_title = "".join(c for c in article.title if c.isalnum() or c in (' ', '_', '-')).strip()[:60]
    filename = f"{safe_title or 'maqola'}.pdf"

    try:
        if hasattr(article.pdf_file, 'path') and os.path.exists(article.pdf_file.path):
            return FileResponse(open(article.pdf_file.path, 'rb'), as_attachment=True, filename=filename, content_type='application/pdf')
        return FileResponse(article.pdf_file.open('rb'), as_attachment=True, filename=filename, content_type='application/pdf')
    except Exception:
        if article.pdf_file.url:
            return _redirect(article.pdf_file.url)
        raise Http404(_("Faylni ochishda xatolik yuz berdi."))


def generate_article_pdf(request, journal_slug, pk):
    """
    Maqola PDF faylini brauzerda inline ko'rish uchun to'g'ridan-to'g'ri ochadi.
    """
    import os
    from django.http import FileResponse, Http404
    from django.shortcuts import redirect as _redirect

    current_journal = _get_current_journal(journal_slug)
    article = get_object_or_404(Article, pk=pk, journal=current_journal)

    is_author = request.user.is_authenticated and article.author_id == request.user.pk
    is_reviewer_or_staff = request.user.is_authenticated and (
        getattr(request.user, 'role', '') in ['reviewer', 'editor'] or
        request.user.is_staff or
        request.user.is_superuser or
        article.assigned_reviewer_id == request.user.pk
    )
    if article.status != 'published' and not (is_author or is_reviewer_or_staff):
        raise Http404(_("Maqola hali chop etilmagan."))

    if not request.session.get(f'pdf_viewed_{pk}'):
        Article.objects.filter(pk=pk).update(downloads_count=article.downloads_count + 1)
        request.session[f'pdf_viewed_{pk}'] = True

    if not article.pdf_file:
        raise Http404(_("Maqola PDF fayli yuklanmagan."))

    safe_title = "".join(c for c in article.title if c.isalnum() or c in (' ', '_', '-')).strip()[:60]
    filename = f"{safe_title or 'maqola'}.pdf"

    try:
        if hasattr(article.pdf_file, 'path') and os.path.exists(article.pdf_file.path):
            return FileResponse(open(article.pdf_file.path, 'rb'), as_attachment=False, filename=filename, content_type='application/pdf')
        return FileResponse(article.pdf_file.open('rb'), as_attachment=False, filename=filename, content_type='application/pdf')
    except Exception:
        if article.pdf_file.url:
            return _redirect(article.pdf_file.url)
        raise Http404(_("Faylni ochishda xatolik yuz berdi."))


def signup(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login as auth_login
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('my_articles')
    else:
        form = CustomUserCreationForm()

    current_journal = None
    if next_url:
        parts = [p for p in next_url.strip('/').split('/') if p]
        if parts:
            current_journal = Journal.objects.filter(slug=parts[0]).first()
    if not current_journal:
        current_journal = Journal.objects.first()

    return render(request, 'registration/signup.html', {
        'form': form,
        'current_journal': current_journal,
        'next': next_url,
    })


@login_required
def submit_article(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES)
        form.fields['category'].queryset = ArticleCategory.objects.filter(journal=current_journal).order_by('order', 'code')
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.journal = current_journal
            article.status = 'submitted'
            article.save()
            messages.success(request, _("Maqolangiz tahririyatga muvaffaqiyatli topshirildi."))
            return redirect('my_articles')
    else:
        form = ArticleSubmissionForm()
        form.fields['category'].queryset = ArticleCategory.objects.filter(journal=current_journal).order_by('order', 'code')
    return render(request, 'submit_article.html', {'current_journal': current_journal, 'form': form})


@login_required
def my_articles(request):
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    status_counts = {
        'submitted':    articles.filter(status='submitted').count(),
        'under_review': articles.filter(status='under_review').count(),
        'accepted':     articles.filter(status='accepted').count(),
        'published':    articles.filter(status='published').count(),
        'rejected':     articles.filter(status='rejected').count(),
    }
    default_journal = Journal.objects.first()
    return render(request, 'my_articles.html', {
        'articles': articles,
        'status_counts': status_counts,
        'current_journal': default_journal,
    })


@login_required
def profile(request):
    """Profil ko'rish + ma'lumotlarni yangilash"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profil muvaffaqiyatli yangilandi!'))
            return redirect('profile')
        else:
            messages.error(request, _("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."))
    else:
        form = ProfileUpdateForm(instance=request.user)

    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    status_counts = {
        'submitted':    articles.filter(status='submitted').count(),
        'under_review': articles.filter(status='under_review').count(),
        'accepted':     articles.filter(status='accepted').count(),
        'published':    articles.filter(status='published').count(),
        'rejected':     articles.filter(status='rejected').count(),
    }
    return render(request, 'profile.html', {
        'form': form,
        'articles': articles,
        'status_counts': status_counts,
    })


@login_required
def change_password(request):
    """Parol o'zgartirish"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _("Parol muvaffaqiyatli o'zgartirildi!"))
            return redirect('profile')
        else:
            messages.error(request, _('Xatolik yuz berdi.'))
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def reviewer_dashboard(request):
    """
    Taqrizchilar va Muharrirlar uchun maxsus ishchi paneli.
    Maqolalarni ko'rib chiqish, taqrizchiga biriktirish, tahrirlash, chop etish (publish) va rad etish / izoh berish.
    """
    if not (request.user.role in ['reviewer', 'editor'] or request.user.is_staff or request.user.is_superuser):
        messages.error(request, _("Ushbu sahifa faqat taqrizchi va muharrirlar uchun mo'ljallangan."))
        return redirect('my_articles')

    tab = request.GET.get('tab', '')
    query = request.GET.get('q', '').strip()

    is_editor = (request.user.role == 'editor' or request.user.is_staff or request.user.is_superuser)

    # Oddiy taqrizchi uchun standart tab = 'my_assigned'
    if not is_editor and not tab:
        tab = 'my_assigned'
    elif not tab:
        tab = 'pending'

    all_articles = Article.objects.all().select_related('author', 'category', 'issue', 'assigned_reviewer', 'reviewed_by').order_by('-created_at')

    if query:
        all_articles = all_articles.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(keywords__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(author__email__icontains=query)
        )

    # Oddiy taqrizchiga faqat o'ziga biriktirilgan yoki o'zi taqriz qilgan maqolalarni ko'rsatamiz
    if not is_editor:
        user_articles = all_articles.filter(Q(assigned_reviewer=request.user) | Q(reviewed_by=request.user))
    else:
        user_articles = all_articles

    counts = {
        'my_assigned': all_articles.filter(assigned_reviewer=request.user).count(),
        'pending': user_articles.filter(status__in=['submitted', 'initial_review', 'under_review']).count(),
        'published': user_articles.filter(status__in=['published', 'accepted', 'ready_to_publish']).count(),
        'rejected': user_articles.filter(status__in=['rejected', 'returned']).count(),
        'all': user_articles.count(),
    }

    # Tab filtering
    if tab == 'my_assigned':
        articles = all_articles.filter(assigned_reviewer=request.user)
    elif tab == 'pending':
        articles = user_articles.filter(status__in=['submitted', 'initial_review', 'under_review'])
    elif tab == 'published':
        articles = user_articles.filter(status__in=['published', 'accepted', 'ready_to_publish'])
    elif tab == 'rejected':
        articles = user_articles.filter(status__in=['rejected', 'returned'])
    else:
        articles = user_articles

    issues = JournalIssue.objects.all().order_by('-year', '-number')
    categories = ArticleCategory.objects.all().order_by('order', 'code')
    reviewers = User.objects.filter(Q(role__in=['reviewer', 'editor']) | Q(is_staff=True) | Q(is_superuser=True)).order_by('first_name', 'last_name', 'email')

    return render(request, 'reviewer_dashboard.html', {
        'articles': articles,
        'counts': counts,
        'tab': tab,
        'query': query,
        'issues': issues,
        'categories': categories,
        'reviewers': reviewers,
        'is_editor': is_editor,
    })


@login_required
def assign_reviewer_action(request, pk):
    """
    Muharrir yoki admin maqolaga taqrizchini biriktiradi yoki almashtiradi.
    """
    # Taqrizchi biriktirish faqat muharrir/admin huquqi
    if not (request.user.role == 'editor' or request.user.is_staff or request.user.is_superuser):
        messages.error(request, _("Ushbu harakatni bajarishga ruxsat yo'q."))
        return redirect('reviewer_dashboard')

    if request.method == 'POST':
        article = get_object_or_404(Article, pk=pk)
        reviewer_id = request.POST.get('reviewer_id', '').strip()
        if reviewer_id:
            reviewer = get_object_or_404(User, pk=reviewer_id)
            article.assigned_reviewer = reviewer
            if article.status in ['submitted', 'initial_review']:
                article.status = 'under_review'
            article.save()
            rev_name = reviewer.get_full_name() or reviewer.email
            messages.success(request, _("Maqola taqrizchi %(name)sga muvaffaqiyatli biriktirildi!") % {'name': rev_name})
        else:
            article.assigned_reviewer = None
            article.save()
            messages.info(request, _("Taqrizchi biriktiruvi bekor qilindi."))

    return redirect(request.META.get('HTTP_REFERER', 'reviewer_dashboard'))


@login_required
def review_article_action(request, pk):
    """
    Taqrizchi/Muharrir maqolani tahrirlash, chop etish (publish) va rad etish / izoh berish (reject/return with notes) harakatlari.
    """
    if not (request.user.role in ['reviewer', 'editor'] or request.user.is_staff or request.user.is_superuser):
        messages.error(request, _("Ruxsat etilmagan harakat."))
        return redirect('my_articles')

    article = get_object_or_404(Article, pk=pk)

    # Oddiy taqrizchi faqat o'ziga biriktirilgan maqola ustida ishlay oladi
    is_editor = (request.user.role == 'editor' or request.user.is_staff or request.user.is_superuser)
    if not is_editor and article.assigned_reviewer_id != request.user.pk:
        messages.error(request, _("Ruxsat etilmagan harakat."))
        return redirect('reviewer_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')  # 'publish', 'reject', 'return', 'under_review', 'edit_details'
        review_notes = request.POST.get('review_notes', '').strip()
        issue_id = request.POST.get('issue_id')
        published_at_str = request.POST.get('published_at')

        from django.utils import timezone
        import datetime

        article.reviewed_by = request.user
        article.reviewed_at = timezone.now()

        if action == 'publish':
            article.status = 'published'
            if issue_id:
                issue = JournalIssue.objects.filter(pk=issue_id).first()
                if issue:
                    article.issue = issue
            if published_at_str:
                try:
                    article.published_at = datetime.datetime.strptime(published_at_str, '%Y-%m-%d').date()
                except Exception:
                    pass
            if not article.published_at:
                article.published_at = datetime.date.today()
            if review_notes:
                article.review_notes = review_notes
            article.save()
            messages.success(request, _("Maqola ('%(title)s...') muvaffaqiyatli nashr etildi!") % {'title': article.title[:35]})

        elif action in ['reject', 'return', 'returned', 'rejected']:
            new_status = 'rejected' if action in ['reject', 'rejected'] else 'returned'
            article.status = new_status
            article.issue = None
            if review_notes:
                article.review_notes = review_notes
            article.save()
            msg_text = _("rad etildi") if new_status == 'rejected' else _("tuzatish uchun qaytarildi")
            messages.warning(request, _("Maqola %(status)s va muallif uchun izoh saqlandi!") % {'status': msg_text})

        elif action == 'under_review':
            article.status = 'under_review'
            if review_notes:
                article.review_notes = review_notes
            article.save()
            messages.info(request, _("Maqola holati 'Taqriz jarayonida' ga o'tkazildi."))

        elif action == 'edit_details':
            title = request.POST.get('title', '').strip()
            authors = request.POST.get('authors', '').strip()
            abstract = request.POST.get('abstract', '').strip()
            keywords = request.POST.get('keywords', '').strip()
            category_id = request.POST.get('category_id')
            start_page = request.POST.get('start_page')
            end_page = request.POST.get('end_page')

            if title: article.title = title
            if authors: article.authors = authors
            if abstract: article.abstract = abstract
            if keywords: article.keywords = keywords
            if category_id:
                cat = ArticleCategory.objects.filter(pk=category_id).first()
                if cat: article.category = cat
            if start_page:
                try: article.start_page = int(start_page)
                except Exception: pass
            if end_page:
                try: article.end_page = int(end_page)
                except Exception: pass

            if 'pdf_file' in request.FILES:
                article.pdf_file = request.FILES['pdf_file']
            if 'template_pdf' in request.FILES:
                article.template_pdf = request.FILES['template_pdf']

            if review_notes:
                article.review_notes = review_notes

            article.save()
            messages.success(request, _("Maqola ma'lumotlari muvaffaqiyatli tahrirlandi!"))

        return redirect(request.META.get('HTTP_REFERER', 'reviewer_dashboard'))

    return redirect('reviewer_dashboard')


def conferences(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    items = Conference.objects.filter(journal=current_journal, is_active=True).order_by('-date')
    return render(request, 'conferences.html', {'current_journal': current_journal, 'items': items})


def news_list(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    items = News.objects.filter(journal=current_journal, is_active=True).order_by('-created_at')
    return render(request, 'news.html', {'current_journal': current_journal, 'items': items})


def news_detail(request, journal_slug, pk):
    current_journal = _get_current_journal(journal_slug)
    item = get_object_or_404(News, pk=pk, journal=current_journal, is_active=True)
    return render(request, 'news_detail.html', {'current_journal': current_journal, 'item': item})


def documents(request, journal_slug):
    current_journal = _get_current_journal(journal_slug)
    normative = Document.objects.filter(journal=current_journal, is_active=True, category='normative').order_by('order')
    requirements = Document.objects.filter(journal=current_journal, is_active=True, category='requirement').order_by('order')
    templates = Document.objects.filter(journal=current_journal, is_active=True, category='template').order_by('order')
    other = Document.objects.filter(journal=current_journal, is_active=True, category='other').order_by('order')
    return render(request, 'documents.html', {
        'current_journal': current_journal,
        'normative': normative,
        'requirements': requirements,
        'templates': templates,
        'other': other,
    })


def _build_pdf_from_html_xhtml2pdf(article, request=None):
    from django.template.loader import render_to_string
    from django.conf import settings as django_settings
    import io
    try:
        from xhtml2pdf import pisa
        content_html = ''
        if article.pdf_file:
            try:
                content_html = _get_article_content_html(article.pdf_file, article=article)
            except Exception:
                pass

        safe_logo = _get_logo_base64()
        safe_qr = _get_qr_code_base64(article, request)

        html_string = render_to_string('article_pdf.html', {
            'article': article,
            'pdf_content_html': content_html,
            'static_root': django_settings.STATIC_ROOT,
            'logo_base64': safe_logo,
            'qr_code_base64': safe_qr,
        })

        buffer = io.BytesIO()
        base_url = 'https://architect-edu.tift.uz/'
        if request:
            try:
                base_url = request.build_absolute_uri('/')
            except BaseException:
                pass

        pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8', base_url=base_url)
        return buffer.getvalue()
    except BaseException as e:
        print(f"Error building PDF for article {getattr(article, 'pk', None)}:", e)
        return b''


def download_issue_pdf(request, journal_slug, issue_pk):
    """
    Jurnalning to'liq sonini PDF sifatida yaratadi va yuklab beradi.
    Faqat chop etilgan ('published') maqolalarni ketma-ket bir joyga yig'adi.
    """
    import io
    import base64
    from django.shortcuts import redirect
    from django.template.loader import render_to_string
    from django.http import HttpResponse, Http404

    current_journal = _get_current_journal(journal_slug)
    issue = get_object_or_404(JournalIssue, pk=issue_pk, journal=current_journal)

    # 0. Agar admin tayyor full_pdf yuklagan bo'lsa
    if issue.full_pdf:
        try:
            import os
            from django.http import FileResponse
            if hasattr(issue.full_pdf, 'path') and os.path.exists(issue.full_pdf.path):
                filename = f"TIFT_Journal_{issue.year}_Son_{issue.number}.pdf"
                return FileResponse(open(issue.full_pdf.path, 'rb'), content_type='application/pdf', as_attachment=True, filename=filename)
            elif issue.full_pdf.url:
                return redirect(issue.full_pdf.url)
        except Exception as e:
            print("full_pdf redirect error:", e)

    articles = list(Article.objects.filter(issue=issue, status='published').order_by('created_at', 'id'))
    if not articles:
        return HttpResponse(_("Ushbu sonda hali chop etilgan maqolalar mavjud emas."), status=404)

    try:
        import fitz
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(_("PDF yaratish kutubxonalari topilmadi."), status=500)

    # 1. OLDI MUQOVA SAHIFASI
    doc_cover = None
    if issue.cover_image and issue.cover_image.name:
        try:
            cover_bytes = _get_pdf_bytes(issue.cover_image)
            if cover_bytes:
                ext_img = issue.cover_image.name.split('.')[-1].lower().split('?')[0]
                if ext_img not in ('jpg', 'jpeg', 'png', 'webp'):
                    ext_img = 'jpeg'
                cover_b64 = f"data:image/{ext_img};base64," + base64.b64encode(cover_bytes).decode('ascii')
            else:
                cover_b64 = None

            cover_html = render_to_string('issue_cover_pdf.html', {
                'issue': issue,
                'cover_image_base64': cover_b64,
            })
            buf = io.BytesIO()
            pisa.CreatePDF(src=cover_html, dest=buf, encoding='utf-8')
            doc_cover = fitz.open(stream=buf.getvalue(), filetype="pdf")
        except Exception as e:
            print("Cover image error:", e)

    # 1.2. ORQA MUQOVA SAHIFASI
    doc_back_cover = None
    if issue.back_cover_image and issue.back_cover_image.name:
        try:
            back_bytes = _get_pdf_bytes(issue.back_cover_image)
            if back_bytes:
                ext_img = issue.back_cover_image.name.split('.')[-1].lower().split('?')[0]
                if ext_img not in ('jpg', 'jpeg', 'png', 'webp'):
                    ext_img = 'jpeg'
                back_b64 = f"data:image/{ext_img};base64," + base64.b64encode(back_bytes).decode('ascii')
            else:
                back_b64 = None

            back_html = render_to_string('issue_cover_pdf.html', {
                'issue': issue,
                'cover_image_base64': back_b64,
            })
            buf = io.BytesIO()
            pisa.CreatePDF(src=back_html, dest=buf, encoding='utf-8')
            doc_back_cover = fitz.open(stream=buf.getvalue(), filetype="pdf")
        except Exception as e:
            print("Back cover error:", e)

    # 1.5. TAHRIRIYAT A'ZOLARI SAHIFASI
    doc_editorial = None
    try:
        staff = StaffMember.objects.filter(journal=current_journal, is_active=True).order_by('order', 'full_name')
        leadership = staff.filter(position__in=['editor_in_chief', 'deputy_editor', 'secretary'])
        editorial_board = staff.filter(position='member')
        
        editorial_html = render_to_string('issue_editorial_pdf.html', {
            'leadership': leadership,
            'editorial_board': editorial_board,
        })
        buf_ed = io.BytesIO()
        pisa.CreatePDF(src=editorial_html, dest=buf_ed, encoding='utf-8')
        doc_editorial = fitz.open(stream=buf_ed.getvalue(), filetype="pdf")
    except Exception as e:
        print("Editorial page generation error:", e)

    cover_page_count = (len(doc_cover) if doc_cover else 0) + (len(doc_back_cover) if doc_back_cover else 0) + (len(doc_editorial) if doc_editorial else 0)

    # 2. MAQOLALAR PDF NUSXASINI TAYYORLASH
    prepared_articles = []
    for art in articles:
        try:
            raw_bytes = None
            file_name = getattr(art.pdf_file, 'name', '') or ''
            ext = file_name.lower().rsplit('.', 1)[-1].split('?')[0] if art.pdf_file else ''

            if ext == 'pdf':
                raw_bytes = _get_pdf_bytes(art.pdf_file)
            
            if not raw_bytes:
                raw_bytes = _build_pdf_from_html_xhtml2pdf(art, request)

            if raw_bytes:
                art_doc = fitz.open(stream=raw_bytes, filetype="pdf")
                if len(art_doc) > 0:
                    prepared_articles.append({
                        'article': art,
                        'doc': art_doc,
                        'pages': len(art_doc)
                    })
        except Exception as e:
            print(f"Error preparing article {art.pk}:", e)

    if not prepared_articles:
        master_doc = fitz.open()
        if doc_cover and len(doc_cover) > 0:
            master_doc.insert_pdf(doc_cover)
        if doc_back_cover and len(doc_back_cover) > 0:
            master_doc.insert_pdf(doc_back_cover)
        if doc_editorial and len(doc_editorial) > 0:
            master_doc.insert_pdf(doc_editorial)

        if len(master_doc) > 0:
            final_bytes = master_doc.tobytes()
            response = HttpResponse(final_bytes, content_type='application/pdf')
            filename = f"TIFT_Journal_{issue.year}_Son_{issue.number}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse(_("Ushbu jurnal soni va uning maqolalari hali to'liq shakllantirilmagan."), status=404)

    # 3. MUNDARIJA (TABLE OF CONTENTS) YARATISH VA SAHIFALARNI HISOBLASH
    toc_doc = None
    article_items = []
    
    for attempt in range(2):
        article_items = []
        current_page = cover_page_count + (len(toc_doc) if toc_doc else 1) + 1

        for item in prepared_articles:
            art = item['article']
            pages = item['pages']
            start_p = current_page
            end_p = current_page + pages - 1

            if art.start_page != start_p or art.end_page != end_p:
                Article.objects.filter(pk=art.pk).update(start_page=start_p, end_page=end_p)
                art.start_page = start_p
                art.end_page = end_p

            article_items.append({
                'article': art,
                'start_page': start_p,
                'end_page': end_p,
            })
            current_page = end_p + 1

        toc_html = render_to_string('issue_toc_pdf.html', {
            'issue': issue,
            'article_items': article_items,
        })
        buf_toc = io.BytesIO()
        pisa.CreatePDF(src=toc_html, dest=buf_toc, encoding='utf-8')
        new_toc_doc = fitz.open(stream=buf_toc.getvalue(), filetype="pdf")
        
        if toc_doc and len(new_toc_doc) == len(toc_doc):
            break
        toc_doc = new_toc_doc

    # 4. BARCHA QISMLARNI BITTA MASTER PDF GA BIRLASHTIRISH
    master_doc = fitz.open()
    if doc_cover and len(doc_cover) > 0:
        master_doc.insert_pdf(doc_cover)
    if doc_back_cover and len(doc_back_cover) > 0:
        master_doc.insert_pdf(doc_back_cover)
    if doc_editorial and len(doc_editorial) > 0:
        master_doc.insert_pdf(doc_editorial)
    if toc_doc and len(toc_doc) > 0:
        master_doc.insert_pdf(toc_doc)
    for item in prepared_articles:
        master_doc.insert_pdf(item['doc'])

    # 5. UZLUKSIZ RAQAMLASH VA FOOTER QO'SHISH
    total_pages = len(master_doc)
    unbound_count = cover_page_count + (len(toc_doc) if toc_doc else 0)

    issue_full = f"{issue.year}-yil, {issue.number}-son (Jild {issue.volume})"
    NAVY = (0.04, 0.145, 0.251)
    GRAY_TEXT = (0.35, 0.35, 0.35)
    LINE_COLOR = (0.82, 0.85, 0.88)

    for idx in range(total_pages):
        page = master_doc[idx]
        if idx < unbound_count:
            continue

        w = page.rect.width
        h = page.rect.height
        margin_left = 85.0    # 3.0 cm (maqola matni bilan bir liniyada)
        margin_right = 42.5   # 1.5 cm
        footer_line_y = h - 40.0

        try:
            page.draw_line(fitz.Point(margin_left, footer_line_y), fitz.Point(w - margin_right, footer_line_y), color=LINE_COLOR, width=0.5)
        except Exception:
            pass

        rect_f_left = fitz.Rect(margin_left, footer_line_y + 4, w - 100, h - 15)
        try:
                page.insert_textbox(rect_f_left, f"{getattr(article, 'journal', None) and article.journal.title or ''} | {issue_full}", fontsize=8, color=GRAY_TEXT, align=0)
        except Exception:
            pass

        rect_f_right = fitz.Rect(w - 100, footer_line_y + 4, w - margin_right, h - 15)
        page_num = idx + 1
        try:
            page.insert_textbox(rect_f_right, f"{page_num}", fontsize=8.5, color=NAVY, align=2)
        except Exception:
            pass

    # 5.5. MUNDARIJADAGI MAVZULARGA VA NATIVE PDF BOOKMARK (OUTLINE) GA INTERAKTIV GOTO HAVOLALAR QO'SHISH
    try:
        toc_page_offset = cover_page_count  # Mundarija boshlanadigan 0-indeksli sahifa
        toc_num_pages = len(toc_doc) if toc_doc else 0
        pdf_toc_outline = []

        if toc_num_pages > 0:
            pdf_toc_outline.append([1, _("Mundarija / Contents"), toc_page_offset + 1])

        for item_idx, item in enumerate(article_items, 1):
            art = item['article']
            target_page_idx = item['start_page'] - 1  # Maqola boshlanadigan 0-indeksli sahifa
            art_title = _clean_text(art.title)
            
            # PDF native bookmark outline ro'yxatiga qo'shish
            pdf_toc_outline.append([1, f"{item_idx}. {art_title[:75]}", item['start_page']])

            # Mundarija sahifalarida matnni izlash va bosiladigan ichki havolalar (internal links) o'rnatish
            title_query = _clean_text(art.title[:30]).strip()
            num_query = f"{item_idx}."

            for p_offset in range(toc_num_pages):
                current_toc_p_idx = toc_page_offset + p_offset
                if current_toc_p_idx >= total_pages:
                    break
                toc_page = master_doc[current_toc_p_idx]

                # Sarlavha matnini topish
                rects = toc_page.search_for(title_query) if title_query else []
                if not rects:
                    rects = toc_page.search_for(num_query)

                for r in rects:
                    # Mundarijadagi ushbu qatorni to'liq bosiladigan zona (link rect) qilish
                    link_rect = fitz.Rect(36.0, max(0.0, r.y0 - 4.0), toc_page.rect.width - 36.0, min(toc_page.rect.height, r.y1 + 14.0))
                    toc_page.insert_link({
                        'kind': fitz.LINK_GOTO,
                        'from': link_rect,
                        'page': target_page_idx,
                        'to': fitz.Point(0.0, 0.0),
                    })

        if pdf_toc_outline:
            master_doc.set_toc(pdf_toc_outline)
    except Exception as e:
        print("Error adding interactive TOC links/bookmarks:", e)

    # 6. YUKLAB OLISH UCHUN QAYTARISH
    final_bytes = master_doc.tobytes()
    response = HttpResponse(final_bytes, content_type='application/pdf')
    filename = f"TIFT_Journal_{issue.year}_Son_{issue.number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
