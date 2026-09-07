from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JournalIssue, Article, StaffMember, SiteVisit, Conference, News, Document
from .forms import ArticleSubmissionForm, CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm


def index(request):
    try:
        # Login qilgan user bosh sahifaga kelsa — hisobiga yo'naltir
        if request.user.is_authenticated:
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

    return render(request, 'index.html', {
        'recent_articles': recent_articles,
        'issues': issues,
        'query': query,
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'week_labels': week_labels,
        'week_data': week_data,
        'total_articles': total_articles,
    })


def archive(request):
    issues = JournalIssue.objects.all().order_by('-year', '-number')
    return render(request, 'archive.html', {'issues': issues})


def about(request):
    staff = StaffMember.objects.filter(is_active=True).order_by('order', 'full_name')
    leadership = staff.filter(position__in=['editor_in_chief', 'deputy_editor', 'secretary'])
    editorial_board = staff.filter(position='member')
    areas = [
        "Arxitektura nazariyasi", "Binolar konstruksiyasi",
        "Shaharsozlik va landshaft", "Geodeziya va kartografiya",
        "Ta'lim metodikasi", "Raqamli texnologiyalar",
        "Sun'iy idrok", "Kadastr va er resurslari",
    ]
    return render(request, 'about.html', {
        'staff': staff,
        'leadership': leadership,
        'editorial_board': editorial_board,
        'areas': areas
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
        if request:
            qr_url = request.build_absolute_uri(f"/article/{article.pk}/")
        else:
            qr_url = f"https://architect-edu.tift.uz/article/{article.pk}/"
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode('ascii')
    except Exception as e:
        print("QR code generation error:", e)
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


def _add_header_footer_to_pdf(pdf_bytes, article):
    """
    PyMuPDF yordamida asl PDF faylning har sahifasiga
    yuqori va pastki kolontitullarni qo'shadi.
    Matn, rasmlar, jadvallar o'zgarmaydi.
    """
    try:
        import fitz
        import io

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Ranglar
        DARK_BLUE = (0.04, 0.086, 0.157)   # #0a1628
        GREEN     = (0.086, 0.502, 0.239)   # #15803d
        GRAY      = (0.4, 0.4, 0.4)

        # Jurnal ma'lumotlari
        journal_name  = "TIFT JOURNAL"
        journal_sub   = '"Arxitektura va Ta\'lim" Ilmiy-Elektron Jurnali'
        footer_text   = "Toshkent sh., Amir Temur ko'chasi, 108  |  Tel: +998 71 238-74-80  |  journal@tift.uz  |  www.tift.uz"

        if article.issue:
            issue_text = f"Jild {article.issue.volume}, Son {article.issue.number}, {article.issue.year}"
        else:
            issue_text = "ISSN: 2181-XXXX"

        for page in doc:
            w = page.rect.width    # sahifa kengligi (pt)
            h = page.rect.height   # sahifa balandligi (pt)

            margin_x = 71.0  # 2.5cm
            header_y = 22.0  # yuqoridan 0.77cm
            footer_y = h - 25.0  # pastdan

            # ── YUQORI KOLONTITUL ──

            # Logo kvadrat (chap)
            logo_rect = fitz.Rect(margin_x, header_y - 2, margin_x + 28, header_y + 26)
            page.draw_rect(logo_rect, color=DARK_BLUE, fill=DARK_BLUE, width=0)
            page.insert_text(
                (margin_x + 7, header_y + 19),
                "T", fontsize=16,
                color=(0.133, 0.773, 0.369),  # #22c55e
                fontname="Helvetica-Bold"
            )

            # Jurnal nomi (o'rta)
            page.insert_text(
                (margin_x + 34, header_y + 10),
                journal_name, fontsize=10,
                color=DARK_BLUE, fontname="Helvetica-Bold"
            )
            page.insert_text(
                (margin_x + 34, header_y + 22),
                journal_sub, fontsize=7,
                color=GRAY, fontname="Helvetica"
            )

            # Jurnal soni (o'ng)
            page.insert_text(
                (w - margin_x - 140, header_y + 10),
                issue_text, fontsize=8,
                color=GRAY, fontname="Helvetica"
            )
            page.insert_text(
                (w - margin_x - 140, header_y + 20),
                "ISSN: 2181-XXXX", fontsize=7,
                color=GRAY, fontname="Helvetica"
            )

            # QR kod (1-sahifada o'ng yuqori burchakda haqiqiyligini tekshirish uchun)
            if page.number == 0:
                try:
                    import qrcode
                    qr = qrcode.QRCode(version=1, box_size=4, border=0)
                    qr_url = f"https://architect-edu.tift.uz/article/{article.pk}/"
                    qr.add_data(qr_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    qr_buf = io.BytesIO()
                    img.save(qr_buf, format="PNG")
                    qr_rect = fitz.Rect(w - margin_x - 30, header_y - 2, w - margin_x, header_y + 28)
                    page.insert_image(qr_rect, stream=qr_buf.getvalue())
                except Exception as qr_err:
                    print("QR insert error:", qr_err)

            # Yuqori chiziq (yashil)
            page.draw_line(
                (margin_x, header_y + 30),
                (w - margin_x, header_y + 30),
                color=GREEN, width=1.2
            )

            # ── PASTKI KOLONTITUL ──

            # Pastki chiziq (yashil)
            page.draw_line(
                (margin_x, footer_y - 4),
                (w - margin_x, footer_y - 4),
                color=GREEN, width=0.8
            )

            # Sahifa raqami
            page_num = f"– {page.number + 1} / {doc.page_count} –"
            page.insert_text(
                (w / 2 - 20, footer_y + 8),
                page_num, fontsize=8,
                color=DARK_BLUE, fontname="Helvetica-Bold"
            )

            # Manzil
            page.insert_text(
                (margin_x, footer_y + 18),
                footer_text, fontsize=6.5,
                color=GRAY, fontname="Helvetica"
            )

        # Yangi PDF bytes
        out = io.BytesIO()
        doc.save(out)
        doc.close()
        return out.getvalue()

    except Exception as e:
        # Xatolik bo'lsa asl bytes qaytaradi
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
    Word (.docx) faylni PDF ga aylantirib qaytaradi.
    Kolontitullar bilan birga xhtml2pdf shablon ishlatiladi.
    """
    from django.http import HttpResponse, Http404
    from django.shortcuts import redirect as _redirect
    from django.template.loader import render_to_string

    article = get_object_or_404(Article, pk=pk, status='published')
    Article.objects.filter(pk=pk).update(downloads_count=article.downloads_count + 1)

    safe_title = article.title[:40].replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"TIFT_{safe_title}.pdf"

    if not article.pdf_file:
        raise Http404("Maqola fayli topilmadi.")

    try:
        from xhtml2pdf import pisa
        import io
        from django.conf import settings

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
        base_url = request.build_absolute_uri('/')
        res = pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8', base_url=base_url)
        if not res.err:
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception:
        pass

    # Fallback: asl faylni qaytarish
    return _redirect(article.pdf_file.url)


def generate_article_pdf(request, pk):
    """Maqolani brauzerda ko'rish uchun PDF ga aylantiradi (Word → PDF)."""
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    import io

    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse("xhtml2pdf o'rnatilmagan.", status=500)

    article = get_object_or_404(Article, pk=pk, status='published')
    if not request.session.get(f'pdf_viewed_{pk}'):
        Article.objects.filter(pk=pk).update(downloads_count=article.downloads_count + 1)
        request.session[f'pdf_viewed_{pk}'] = True

    from django.conf import settings as django_settings

    content_html = ''
    if article.pdf_file:
        try:
            content_html = _get_article_content_html(article.pdf_file, article=article)
        except Exception:
            pass

    html_string = render_to_string('article_pdf.html', {
        'article': article,
        'request': request,
        'pdf_content_html': content_html,
        'static_root': django_settings.STATIC_ROOT,
        'logo_base64': _get_logo_base64(),
        'qr_code_base64': _get_qr_code_base64(article, request),
    })
    buffer = io.BytesIO()
    base_url = request.build_absolute_uri('/')
    pisa_status = pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8', base_url=base_url)

    if pisa_status.err:
        return HttpResponse("PDF yaratishda xatolik yuz berdi.", status=500)

    safe_title = article.title[:40].replace(' ', '_').replace('/', '_').replace('\\', '_')
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="TIFT_{safe_title}.pdf"'
    return response


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


def conferences(request):
    items = Conference.objects.filter(is_active=True).order_by('-date')
    return render(request, 'conferences.html', {'items': items})


def news_list(request):
    items = News.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'news.html', {'items': items})


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
    except ImportError:
        return b''
    
    content_html = ''
    if article.pdf_file:
        try:
            content_html = _get_article_content_html(article.pdf_file, article=article)
        except Exception:
            pass

    html_string = render_to_string('article_pdf.html', {
        'article': article,
        'request': request,
        'pdf_content_html': content_html,
        'static_root': django_settings.STATIC_ROOT,
        'logo_base64': _get_logo_base64(),
        'qr_code_base64': _get_qr_code_base64(article, request),
    })
    buffer = io.BytesIO()
    base_url = request.build_absolute_uri('/') if request else ''
    pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8', base_url=base_url)
    return buffer.getvalue()


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
            return redirect(issue.full_pdf.url)
        except Exception:
            pass

    articles = list(Article.objects.filter(issue=issue, status='published').order_by('created_at', 'id'))
    if not articles:
        return HttpResponse("Ushbu sonda hali chop etilgan maqolalar mavjud emas.", status=404)

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
        return HttpResponse("Maqolalar PDF larini shakllantirishda xatolik yuz berdi.", status=500)

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

    # 5. UZLUKSIZ RAQAMLASH VA HEADER/FOOTER QO'SHISH
    total_pages = len(master_doc)
    unbound_count = cover_page_count + len(toc_doc)
    hdr_text = f"TIFT \"Arxitektura va Ta'lim\" Ilmiy-elektron jurnali | {issue.year}-yil, {issue.number}-son"

    for idx in range(total_pages):
        page = master_doc[idx]
        if idx < unbound_count:
            continue

        page_num = idx + 1
        rect = page.rect
        width, height = rect.width, rect.height

        header_y = 25
        page.insert_text((40, header_y), hdr_text, fontsize=8, fontname="helv", color=(0.2, 0.2, 0.2))
        page.draw_line(fitz.Point(40, header_y + 4), fitz.Point(width - 40, header_y + 4), color=(0.6, 0.6, 0.6), width=0.5)

        footer_y = height - 30
        page.draw_line(fitz.Point(40, footer_y - 8), fitz.Point(width - 40, footer_y - 8), color=(0.6, 0.6, 0.6), width=0.5)
        
        num_str = str(page_num)
        page.insert_text((width / 2 - 5, footer_y), num_str, fontsize=9, fontname="helv", color=(0, 0, 0))

    # 6. YUKLAB OLISH UCHUN QAYTARISH
    final_bytes = master_doc.tobytes()
    response = HttpResponse(final_bytes, content_type='application/pdf')
    filename = f"TIFT_Journal_{issue.year}_Son_{issue.number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
