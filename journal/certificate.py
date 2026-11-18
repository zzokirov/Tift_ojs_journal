"""Maqola nashr etilganligi to'g'risidagi sertifikat (PDF, A4 albom).

PyMuPDF yordamida chiziladi: tizimdagi shriftlarga bog'liq emas
(DejaVu shriftlari static/fonts/certificate ichida), lotin, kirill va
o'zbekcha ʻ belgilarini to'g'ri ko'rsatadi.
"""
import io
import os
import re

from django.conf import settings
from django.utils import timezone

UNIVERSITY_UZ = "TOSHKENT XALQARO MOLIYAVIY BOSHQARUV VA TEXNOLOGIYALAR UNIVERSITETI"
UNIVERSITY_EN = "Tashkent International University of Financial Management and Technologies"

THEME_COLORS = {
    'arch': (0x9a, 0x44, 0x25),
    'finance': (0x04, 0x78, 0x57),
    'default': (0x14, 0x2d, 0x54),
}

_INSTITUTION_HINT = re.compile(
    r'universitet|university|университет|institut|институт|\btift\b|kafedra|кафедра|'
    r'fakultet|факультет|toshkent|tashkent|ташкент|akademiya|academy|академия|'
    r'professor|dotsent|o.qituvchi|talaba|student|magistr|doktorant|tadqiqotchi|phd|dsc|@|\d',
    re.IGNORECASE,
)


def author_display_names(authors_text):
    """Mualliflar matnidan sertifikat uchun ism-familiyalar ro'yxati (tashkilotsiz)."""
    names = []
    for block in re.split(r'[;\n]', authors_text or ''):
        name_part = block.split('|')[0]
        for chunk in re.split(r',| va | and | и ', name_part):
            chunk = ' '.join(chunk.split())
            if not chunk or _INSTITUTION_HINT.search(chunk):
                continue
            if not (2 <= len(chunk.split()) <= 4):
                continue
            if chunk not in names:
                names.append(chunk)
    return names


def certificate_number(article, author_index=0):
    year = article.published_at.year if article.published_at else (article.issue.year if article.issue else timezone.now().year)
    return f"TIFT-{(article.journal_id or 0):02d}-{year}-{article.pk:05d}-{author_index + 1}"


def _font(name):
    return os.path.join(settings.BASE_DIR, 'static', 'fonts', 'certificate', name)


def _static_image(name):
    for base in (os.path.join(settings.BASE_DIR, 'static', 'images'), os.path.join(settings.STATIC_ROOT or '', 'images')):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return path
    return None


def _qr_png(url):
    import qrcode
    qr = qrcode.QRCode(version=None, box_size=8, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
    return buf.getvalue()


def _fit_text(page, rect, text, fontname, max_size, min_size, color, align=1, lineheight=None):
    """Matnni to'rtburchakka sig'guncha shriftni kichraytirib yozadi."""
    import fitz
    size = max_size
    while size >= min_size:
        kwargs = dict(fontname=fontname, fontsize=size, color=color, align=align)
        if lineheight:
            kwargs['lineheight'] = lineheight
        # Avval sinab ko'ramiz (yozmasdan), keyin haqiqiy yozamiz
        shape = page.new_shape()
        rc = shape.insert_textbox(rect, text, **kwargs)
        if rc >= 0:
            shape.commit()
            return size
        size -= 0.5
    page.insert_textbox(fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1 + 200), text, fontname=fontname, fontsize=min_size, color=color, align=align)
    return min_size


def build_certificate_pdf(article, author_name, author_index, article_url, theme='default', chief_editor=None):
    import fitz

    accent = tuple(c / 255 for c in THEME_COLORS.get(theme, THEME_COLORS['default']))
    ink = (0.11, 0.11, 0.10)
    muted = (0.42, 0.40, 0.37)
    gold = (0.72, 0.58, 0.30)

    doc = fitz.open()
    W, H = fitz.paper_size("a4-l")
    page = doc.new_page(width=W, height=H)

    page.insert_font(fontname="serif", fontfile=_font("DejaVuSerif.ttf"))
    page.insert_font(fontname="serifb", fontfile=_font("DejaVuSerif-Bold.ttf"))
    page.insert_font(fontname="sans", fontfile=_font("DejaVuSans.ttf"))
    page.insert_font(fontname="sansb", fontfile=_font("DejaVuSans-Bold.ttf"))

    # Fon va ramkalar
    page.draw_rect(page.rect, color=None, fill=(0.992, 0.984, 0.965))
    page.draw_rect(fitz.Rect(18, 18, W - 18, H - 18), color=accent, width=3)
    page.draw_rect(fitz.Rect(26, 26, W - 26, H - 26), color=gold, width=0.8)
    # Burchak bezaklari
    for (x, y, dx, dy) in ((26, 26, 1, 1), (W - 26, 26, -1, 1), (26, H - 26, 1, -1), (W - 26, H - 26, -1, -1)):
        page.draw_line(fitz.Point(x, y + 34 * dy), fitz.Point(x + 34 * dx, y), color=gold, width=0.8)

    # Logotiplar
    logo = _static_image('tiftlogo.png') or _static_image('tift.png')
    if logo:
        page.insert_image(fitz.Rect(52, 46, 106, 100), filename=logo, keep_proportion=True)
    journal = article.journal
    journal_logo = None
    try:
        if journal and journal.logo and os.path.exists(journal.logo.path):
            journal_logo = journal.logo.path
    except Exception:
        journal_logo = None
    if journal_logo:
        page.insert_image(fitz.Rect(W - 106, 46, W - 52, 100), filename=journal_logo, keep_proportion=True)

    # Universitet nomi
    page.insert_textbox(fitz.Rect(120, 50, W - 120, 72), UNIVERSITY_UZ, fontname="sansb", fontsize=10.5, color=ink, align=1)
    page.insert_textbox(fitz.Rect(120, 70, W - 120, 86), UNIVERSITY_EN, fontname="sans", fontsize=8.5, color=muted, align=1)
    if journal:
        page.insert_textbox(fitz.Rect(120, 86, W - 120, 102), f"«{journal.title}» ilmiy jurnali", fontname="serif", fontsize=9.5, color=accent, align=1)
    page.draw_line(fitz.Point(W / 2 - 160, 112), fitz.Point(W / 2 + 160, 112), color=gold, width=0.6)

    # Sarlavha
    page.insert_textbox(fitz.Rect(40, 116, W - 40, 176), "SERTIFIKAT", fontname="serifb", fontsize=40, color=accent, align=1)
    page.insert_textbox(fitz.Rect(40, 174, W - 40, 192), "ilmiy maqola nashr etilganligi to‘g‘risida  ·  CERTIFICATE OF PUBLICATION", fontname="sans", fontsize=9.5, color=muted, align=1)

    # Muallif
    page.insert_textbox(fitz.Rect(40, 204, W - 40, 222), "Ushbu sertifikat", fontname="serif", fontsize=12, color=ink, align=1)
    _fit_text(page, fitz.Rect(70, 222, W - 70, 258), author_name, "serifb", 26, 16, ink)
    page.draw_line(fitz.Point(W / 2 - 200, 262), fitz.Point(W / 2 + 200, 262), color=gold, width=0.6)
    page.insert_textbox(fitz.Rect(40, 270, W - 40, 288), "quyidagi ilmiy maqolaning muallifi ekanligini tasdiqlaydi:", fontname="serif", fontsize=12, color=ink, align=1)

    # Maqola nomi
    _fit_text(page, fitz.Rect(90, 294, W - 90, 352), f"«{article.title}»", "serifb", 15, 9, accent, lineheight=1.25)

    # Nashr ma'lumotlari
    parts = []
    if journal:
        parts.append(f"Jurnal: {journal.title}")
        if journal.issn:
            parts.append(f"ISSN {journal.issn}")
        if journal.eissn:
            parts.append(f"eISSN {journal.eissn}")
    if article.issue:
        parts.append(f"{article.issue.year}-yil, {article.issue.volume}-jild, {article.issue.number}-son")
    if article.start_page and article.end_page:
        parts.append(f"{article.start_page}–{article.end_page}-betlar")
    line1 = "  ·  ".join(parts)
    parts2 = []
    if article.category:
        parts2.append(f"Yo‘nalish: {article.category.code} — {article.category.name}")
    if article.published_at:
        pub = article.published_at
        if hasattr(pub, 'tzinfo') and getattr(pub, 'hour', None) is not None and timezone.is_aware(pub):
            pub = timezone.localtime(pub)
        parts2.append(f"Nashr sanasi: {pub.strftime('%d.%m.%Y')}")
    line2 = "  ·  ".join(parts2)
    _fit_text(page, fitz.Rect(70, 360, W - 70, 376), line1, "sans", 10, 7, ink)
    if line2:
        _fit_text(page, fitz.Rect(70, 377, W - 70, 393), line2, "sans", 10, 7, muted)

    # Pastki qism: imzo, raqam, QR
    y = H - 140
    page.draw_line(fitz.Point(70, y + 52), fitz.Point(290, y + 52), color=ink, width=0.6)
    page.insert_textbox(fitz.Rect(70, y + 56, 290, y + 72), "Bosh muharrir", fontname="sans", fontsize=9, color=muted, align=0)
    if chief_editor:
        page.insert_textbox(fitz.Rect(70, y + 32, 290, y + 50), chief_editor, fontname="serifb", fontsize=11, color=ink, align=0)

    number = certificate_number(article, author_index)
    issued = timezone.localtime().strftime('%d.%m.%Y')
    page.insert_textbox(fitz.Rect(W / 2 - 150, y + 30, W / 2 + 150, y + 46), f"Sertifikat № {number}", fontname="sansb", fontsize=10, color=ink, align=1)
    page.insert_textbox(fitz.Rect(W / 2 - 150, y + 47, W / 2 + 150, y + 62), f"Berilgan sana: {issued}", fontname="sans", fontsize=9, color=muted, align=1)

    try:
        page.insert_image(fitz.Rect(W - 150, y + 6, W - 72, y + 84), stream=_qr_png(article_url))
        page.insert_textbox(fitz.Rect(W - 190, y + 86, W - 52, y + 112), "Tekshirish uchun QR kodni skanerlang", fontname="sans", fontsize=6.5, color=muted, align=1)
    except Exception:
        pass

    doc.set_metadata({
        'title': f"Sertifikat — {article.title}",
        'author': UNIVERSITY_UZ,
        'subject': number,
        'creator': 'TIFT ilmiy jurnallari',
    })
    try:
        doc.subset_fonts()  # faqat ishlatilgan belgilar — fayl hajmi kichik bo'ladi
    except Exception:
        pass
    data = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return data
