from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JournalIssue, Article, ArticleCategory, StaffMember, SiteVisit, Conference, News, Document
from .forms import ArticleSubmissionForm, CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm


def index(request):
    try:
        # Login qilgan user bosh sahifaga kelsa — hisobiga yo'naltir (agar qidiruv so'rovi bo'lmasa)
        if request.user.is_authenticated and not request.GET.get('q'):
            return redirect('my_articles')
    except Exception:
        pass

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
    try:
        recent_qs = Article.objects.filter(status='published').order_by('-created_at')
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
        recent_articles = list(recent_qs[:10])
    except Exception:
        recent_articles = []

    issues = []
    try:
        issues = list(JournalIssue.objects.all().order_by('-year', '-number'))
    except Exception:
        issues = []

    total_articles = 0
    try:
        total_articles = Article.objects.filter(status='published').count()
    except Exception:
        total_articles = 0

    categories = ArticleCategory.objects.all().order_by('order', 'code')

    return render(request, 'index.html', {
        'recent_articles': recent_articles,
        'issues': issues,
        'query': query,
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'week_labels': week_labels,
        'week_data': week_data,
        'total_articles': total_articles,
        'categories': categories,
    })


def archive(request):
    issues = JournalIssue.objects.all().order_by('-year', '-number')
    return render(request, 'archive.html', {'issues': issues})


def about(request):
    staff = StaffMember.objects.filter(is_active=True).order_by('order', 'full_name')
    leadership = staff.filter(position__in=['editor_in_chief', 'deputy_editor', 'secretary'])
    editorial_board = staff.filter(position='member')
    categories = ArticleCategory.objects.all().order_by('order', 'code')
    return render(request, 'about.html', {
        'staff': staff,
        'leadership': leadership,
        'editorial_board': editorial_board,
        'categories': categories,
    })


def issue_detail(request, issue_pk):
    issue = get_object_or_404(JournalIssue, pk=issue_pk)
    articles = Article.objects.filter(issue=issue, status='published')
    return render(request, 'journal/issue_detail.html', {
        'issue': issue,
        'articles': articles,
    })


def article_detail(request, pk):
    try:
        article = get_object_or_404(Article, pk=pk)

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

        # 3. Shu muallifning boshqa nashr etilgan maqolalari
        author_articles = []
        try:
            author_obj = getattr(article, 'author', None)
            if author_obj:
                author_articles = Article.objects.filter(
                    author=author_obj,
                    status='published'
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
            article = get_object_or_404(Article, pk=pk)
            return render(request, 'article_detail.html', {
                'article': article,
                'author_name': getattr(article, 'authors', '') or 'Muallif',
                'author_initial': 'A',
                'author_institution': '',
                'author_articles': [],
                'article_content_html': '',
                'keywords_list': [],
            })
        except Exception:
            from django.http import HttpResponse
            return HttpResponse("Maqola topilmadi yoki xatolik yuz berdi.", status=404)


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
    PyMuPDF yordamida har bir PDF sahifasiga xalqaro ilmiy jurnal standartidagi
    yuqori (Running Header) va pastki (Running Footer) kolontitullarni qo'shadi.
    2-sahifadan boshlab jurnal nomi, soni, mualliflar va sahifa raqami joylashtiriladi.
    """
    try:
        import fitz
        import io

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        NAVY = (0.04, 0.145, 0.251)       # #0a2540
        GRAY_TEXT = (0.35, 0.35, 0.35)   # #555555
        LINE_COLOR = (0.82, 0.85, 0.88)  # Och kulrang chiziq
        PRIMARY_LINE = (0.04, 0.145, 0.251)

        authors_raw = getattr(article, 'authors', '') or (article.author.get_full_name() if getattr(article, 'author', None) else "Muallif")
        title_raw = getattr(article, 'title', '') or "Maqola"

        # Qisqartirilgan matnlar
        short_authors = authors_raw[:35] + ("..." if len(authors_raw) > 35 else "")
        short_title = title_raw[:45] + ("..." if len(title_raw) > 45 else "")

        if article.issue:
            issue_full = f"{article.issue.year}-yil, {article.issue.number}-son (Jild {article.issue.volume})"
            issue_short = f"{article.issue.year}, {article.issue.number}-son"
        else:
            issue_full = "Maxsus son, 2026"
            issue_short = "2026-yil"

        for idx, page in enumerate(doc):
            w = page.rect.width
            h = page.rect.height
            margin_x = 36.0

            if idx == 0:
                # 1-SAHIFA PASTKI KOLONTITUL
                footer_line_y = h - 40.0
                try:
                    page.draw_line(fitz.Point(margin_x, footer_line_y), fitz.Point(w - margin_x, footer_line_y), color=PRIMARY_LINE, width=0.75)
                except Exception:
                    pass

                rect_left = fitz.Rect(margin_x, footer_line_y + 4, w - 120, h - 15)
                try:
                    page.insert_textbox(rect_left, f"Maqola | \"Arxitektura va Ta'lim\" jurnali | {issue_full} | http://architect-edu.tift.uz", fontsize=8, color=GRAY_TEXT, align=0)
                except Exception:
                    pass

                rect_right = fitz.Rect(w - 120, footer_line_y + 4, w - margin_x, h - 15)
                if article.start_page:
                    p_str = f"S. {article.start_page}"
                else:
                    p_str = f"S. 1 / {doc.page_count}"
                try:
                    page.insert_textbox(rect_right, p_str, fontsize=8, color=NAVY, align=2)
                except Exception:
                    pass

            else:
                # 2-SAHIFADAN BOSHLAB YUQORI KOLONTITUL (RUNNING HEADER)
                header_line_y = 36.0
                try:
                    page.draw_line(fitz.Point(margin_x, header_line_y), fitz.Point(w - margin_x, header_line_y), color=LINE_COLOR, width=0.5)
                except Exception:
                    pass

                rect_h_left = fitz.Rect(margin_x, 18, w - 180, header_line_y - 2)
                try:
                    page.insert_textbox(rect_h_left, f"{short_authors} // {short_title}", fontsize=8, color=GRAY_TEXT, align=0)
                except Exception:
                    pass

                rect_h_right = fitz.Rect(w - 180, 18, w - margin_x, header_line_y - 2)
                try:
                    page.insert_textbox(rect_h_right, f"TIFT JOURNAL | {issue_short}", fontsize=8, color=NAVY, align=2)
                except Exception:
                    pass

                # 2-SAHIFADAN BOSHLAB PASTKI KOLONTITUL (RUNNING FOOTER)
                footer_line_y = h - 40.0
                try:
                    page.draw_line(fitz.Point(margin_x, footer_line_y), fitz.Point(w - margin_x, footer_line_y), color=LINE_COLOR, width=0.5)
                except Exception:
                    pass

                rect_f_left = fitz.Rect(margin_x, footer_line_y + 4, w - 140, h - 15)
                try:
                    page.insert_textbox(rect_f_left, f"\"Arxitektura va Ta'lim\" ilmiy-elektron jurnali | ISSN: 2181-3422 | http://architect-edu.tift.uz", fontsize=8, color=GRAY_TEXT, align=0)
                except Exception:
                    pass

                rect_f_right = fitz.Rect(w - 140, footer_line_y + 4, w - margin_x, h - 15)
                if article.start_page:
                    actual_p = article.start_page + idx
                    p_str = f"– {actual_p} –"
                else:
                    p_str = f"– {idx + 1} / {doc.page_count} –"
                try:
                    page.insert_textbox(rect_f_right, p_str, fontsize=8.5, color=NAVY, align=2)
                except Exception:
                    pass

        out = io.BytesIO()
        doc.save(out)
        doc.close()
        return out.getvalue()

    except Exception as e:
        print("Error stamping PDF headers/footers:", e)
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


def download_pdf(request, pk):
    """
    Maqola PDF ini tayyorlab yuklab beradi.
    Colontitullar, QR kod va to'plamdagi haqiqiy sahifa raqamlarini bosib beradi.
    """
    from django.http import HttpResponse, Http404
    from django.shortcuts import redirect as _redirect
    from django.template.loader import render_to_string
    from django.conf import settings

    article = get_object_or_404(Article, pk=pk, status='published')
    Article.objects.filter(pk=pk).update(downloads_count=article.downloads_count + 1)

    if article.issue and article.start_page is None:
        recalculate_issue_page_numbers(article.issue)
        article.refresh_from_db()

    safe_title = article.title[:40].replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"TIFT_{safe_title}.pdf"

    if not article.pdf_file:
        raise Http404("Maqola fayli topilmadi.")

    file_name = getattr(article.pdf_file, 'name', '') or ''
    ext = file_name.lower().rsplit('.', 1)[-1].split('?')[0] if article.pdf_file else ''

    # 1. Asl fayl tayyor PDF bo'lsa
    if ext == 'pdf':
        raw_bytes = _get_pdf_bytes(article.pdf_file)
        if raw_bytes:
            stamped = _add_header_footer_to_pdf(raw_bytes, article)
            response = HttpResponse(stamped, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    # 2. Word (.docx) yoki HTML matn bo'lsa xhtml2pdf orqali
    try:
        from xhtml2pdf import pisa
        import io

        content_html = _get_article_content_html(article.pdf_file, article=article)
        html_string = render_to_string('article_pdf.html', {
            'article': article,
            'request': request,
            'pdf_content_html': content_html,
            'static_root': settings.STATIC_ROOT,
            'logo_base64': _get_logo_base64(),
            'qr_code_base64': _get_qr_code_base64(article, request),
        })
        buffer = io.BytesIO()
        try:
            base_url = request.build_absolute_uri('/') if request else 'https://architect-edu.tift.uz/'
        except Exception:
            base_url = 'https://architect-edu.tift.uz/'
        res = pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8', base_url=base_url)
        if not res.err:
            stamped = _add_header_footer_to_pdf(buffer.getvalue(), article)
            response = HttpResponse(stamped, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception as e:
        print("download_pdf xhtml2pdf error:", e)

    return _redirect(article.pdf_file.url)


def generate_article_pdf(request, pk):
    """Maqolani brauzerda inline ko'rish uchun PDF ga aylantiradi."""
    from django.template.loader import render_to_string
    from django.http import HttpResponse, Http404
    from django.shortcuts import redirect as _redirect
    import io

    article = get_object_or_404(Article, pk=pk, status='published')
    if not request.session.get(f'pdf_viewed_{pk}'):
        Article.objects.filter(pk=pk).update(downloads_count=article.downloads_count + 1)
        request.session[f'pdf_viewed_{pk}'] = True

    if article.issue and article.start_page is None:
        recalculate_issue_page_numbers(article.issue)
        article.refresh_from_db()

    safe_title = article.title[:40].replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"TIFT_{safe_title}.pdf"

    if article.pdf_file:
        file_name = getattr(article.pdf_file, 'name', '') or ''
        ext = file_name.lower().rsplit('.', 1)[-1].split('?')[0]
        if ext == 'pdf':
            raw_bytes = _get_pdf_bytes(article.pdf_file)
            if raw_bytes:
                stamped = _add_header_footer_to_pdf(raw_bytes, article)
                response = HttpResponse(stamped, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response

    try:
        from xhtml2pdf import pisa
        from django.conf import settings as django_settings

        content_html = ''
        if article.pdf_file:
            try:
                content_html = _get_article_content_html(article.pdf_file, article=article)
            except Exception:
                pass

        html_string = render_to_string('article_pdf.html', {
            'article': article,
            'pdf_content_html': content_html,
            'static_root': django_settings.STATIC_ROOT,
            'logo_base64': _get_logo_base64(),
            'qr_code_base64': _get_qr_code_base64(article, request),
        })
        buffer = io.BytesIO()
        try:
            base_url = request.build_absolute_uri('/') if request else 'https://architect-edu.tift.uz/'
        except Exception:
            base_url = 'https://architect-edu.tift.uz/'
        pisa_status = pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8', base_url=base_url)

        if not pisa_status.err:
            stamped = _add_header_footer_to_pdf(buffer.getvalue(), article)
            response = HttpResponse(stamped, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    except Exception as e:
        print("generate_article_pdf error:", e)

    return _redirect(article.pdf_file.url if article.pdf_file else '/')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my_articles')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def submit_article(request):
    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = 'submitted'
            article.save()
            return redirect('my_articles')
    else:
        form = ArticleSubmissionForm()
    return render(request, 'submit_article.html', {'form': form})


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
    return render(request, 'my_articles.html', {
        'articles': articles,
        'status_counts': status_counts,
    })


@login_required
def profile(request):
    """Profil ko'rish + ma'lumotlarni yangilash"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('profile')
        else:
            messages.error(request, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.')
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
            messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi!')
            return redirect('profile')
        else:
            messages.error(request, 'Xatolik yuz berdi.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def reviewer_dashboard(request):
    """
    Taqrizchilar va Muharrirlar uchun maxsus ishchi paneli.
    Maqolalarni ko'rib chiqish, tahrirlash, chop etish (publish) va rad etish / izoh berish (reject/return with notes).
    """
    if not (request.user.role in ['reviewer', 'editor'] or request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Ushbu sahifa faqat taqrizchi va muharrirlar uchun mo'ljallangan.")
        return redirect('my_articles')

    tab = request.GET.get('tab', 'pending')
    query = request.GET.get('q', '').strip()

    all_articles = Article.objects.all().select_related('author', 'category', 'issue').order_by('-created_at')

    if query:
        all_articles = all_articles.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(keywords__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(author__username__icontains=query)
        )

    # Status counts
    counts = {
        'pending': all_articles.filter(status__in=['submitted', 'initial_review', 'under_review']).count(),
        'published': all_articles.filter(status__in=['published', 'accepted', 'ready_to_publish']).count(),
        'rejected': all_articles.filter(status__in=['rejected', 'returned']).count(),
        'all': all_articles.count(),
    }

    # Tab filtering
    if tab == 'pending':
        articles = all_articles.filter(status__in=['submitted', 'initial_review', 'under_review'])
    elif tab == 'published':
        articles = all_articles.filter(status__in=['published', 'accepted', 'ready_to_publish'])
    elif tab == 'rejected':
        articles = all_articles.filter(status__in=['rejected', 'returned'])
    else:
        articles = all_articles

    issues = JournalIssue.objects.all().order_by('-year', '-number')
    categories = ArticleCategory.objects.all().order_by('order', 'code')

    return render(request, 'reviewer_dashboard.html', {
        'articles': articles,
        'counts': counts,
        'tab': tab,
        'query': query,
        'issues': issues,
        'categories': categories,
    })


@login_required
def review_article_action(request, pk):
    """
    Taqrizchi/Muharrir maqolani tahrirlash, chop etish (publish) va rad etish / izoh berish (reject/return with notes) harakatlari.
    """
    if not (request.user.role in ['reviewer', 'editor'] or request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Ruxsat etilmagan harakat.")
        return redirect('my_articles')

    article = get_object_or_404(Article, pk=pk)

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
            messages.success(request, f"Maqola ('{article.title[:35]}...') muvaffaqiyatli nashr etildi!")

        elif action in ['reject', 'return', 'returned', 'rejected']:
            new_status = 'rejected' if action in ['reject', 'rejected'] else 'returned'
            article.status = new_status
            if review_notes:
                article.review_notes = review_notes
            article.save()
            msg_text = "rad etildi" if new_status == 'rejected' else "tuzatish uchun qaytarildi"
            messages.warning(request, f"Maqola {msg_text} va muallif uchun izoh saqlandi!")

        elif action == 'under_review':
            article.status = 'under_review'
            if review_notes:
                article.review_notes = review_notes
            article.save()
            messages.info(request, "Maqola holati 'Taqriz jarayonida' ga o'tkazildi.")

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
            messages.success(request, "Maqola ma'lumotlari muvaffaqiyatli tahrirlandi!")

        return redirect(request.META.get('HTTP_REFERER', 'reviewer_dashboard'))

    return redirect('reviewer_dashboard')


def conferences(request):
    items = Conference.objects.filter(is_active=True).order_by('-date')
    return render(request, 'conferences.html', {'items': items})


def news_list(request):
    items = News.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'news.html', {'items': items})


def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk, is_active=True)
    recent_news = News.objects.filter(is_active=True).exclude(pk=pk).order_by('-created_at')[:5]
    return render(request, 'news_detail.html', {
        'item': item,
        'recent_news': recent_news
    })


def documents(request):
    normative = Document.objects.filter(is_active=True, category='normative').order_by('order')
    requirements = Document.objects.filter(is_active=True, category='requirement').order_by('order')
    templates = Document.objects.filter(is_active=True, category='template').order_by('order')
    other = Document.objects.filter(is_active=True, category='other').order_by('order')
    return render(request, 'documents.html', {
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


def download_issue_pdf(request, issue_pk):
    """
    Jurnalning to'liq sonini PDF sifatida yaratadi va yuklab beradi.
    Ketma-ketlik:
    1. Oldi muqova rasm (cover_image)
    2. Orqa muqova rasm (back_cover_image)
    3. Tahririyat a'zolari (issue_editorial_pdf.html)
    4. Kitob shaklidagi Mundarija (Table of Contents)
    5. Nashrdagi barcha chop etilgan maqolalar ketma-ketligi
    """
    import io
    import base64
    from django.shortcuts import redirect
    from django.template.loader import render_to_string
    from django.http import HttpResponse, Http404

    issue = get_object_or_404(JournalIssue, pk=issue_pk)

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
        articles = list(Article.objects.filter(issue=issue).order_by('created_at', 'id'))
    if not articles:
        return HttpResponse("Ushbu sonda hali maqolalar mavjud emas.", status=404)

    try:
        import fitz
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse("PDF yaratish kutubxonalari topilmadi.", status=500)

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
        staff = StaffMember.objects.filter(is_active=True).order_by('order', 'full_name')
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
        return HttpResponse("Ushbu jurnal soni va uning maqolalari hali to'liq shakllantirilmagan.", status=404)

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

    # 5. UZLUKSIZ RAQAMLASH QO'SHISH
    total_pages = len(master_doc)
    unbound_count = cover_page_count + len(toc_doc)

    for idx in range(total_pages):
        page = master_doc[idx]
        if idx < unbound_count:
            continue

        page_num = idx + 1
        rect = page.rect
        width, height = rect.width, rect.height

        footer_y = height - 20.0
        num_str = f"– {page_num} –"
        try:
            page.insert_text((width / 2 - 14, footer_y), num_str, fontsize=9, fontname="helv", color=(0.04, 0.086, 0.157))
        except Exception:
            try:
                page.insert_text((width / 2 - 14, footer_y), num_str, fontsize=9, color=(0.04, 0.086, 0.157))
            except Exception:
                pass

    # 6. YUKLAB OLISH UCHUN QAYTARISH
    final_bytes = master_doc.tobytes()
    response = HttpResponse(final_bytes, content_type='application/pdf')
    filename = f"TIFT_Journal_{issue.year}_Son_{issue.number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
