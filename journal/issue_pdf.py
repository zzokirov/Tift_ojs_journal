"""To'liq son PDF'i uchun xizmat sahifalari: mundarija, tahririyat, footer.

xhtml2pdf "Times" shriftida o‘, g‘ va kirill harflari yo'q (qora kvadrat chiqadi),
shuning uchun bu sahifalar PyMuPDF orqali DejaVu shriftlari bilan chiziladi.
"""
import io
import os
from html import escape

import fitz
from django.conf import settings
from django.utils.translation import gettext as _

FONT_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'certificate')
SANS = os.path.join(FONT_DIR, 'DejaVuSans.ttf')

A4 = fitz.paper_rect('a4')
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 70.0, 56.0, 62.0, 62.0
NAVY = '#0a2540'
FOOTER_GRAY = (0.35, 0.35, 0.35)
FOOTER_NAVY = (0.04, 0.145, 0.251)
LINE = (0.82, 0.85, 0.88)

CSS = """
@font-face { font-family: serif; src: url(DejaVuSerif.ttf); }
@font-face { font-family: serif; src: url(DejaVuSerif-Bold.ttf); font-weight: bold; }
@font-face { font-family: sans; src: url(DejaVuSans.ttf); }
@font-face { font-family: sans; src: url(DejaVuSans-Bold.ttf); font-weight: bold; }
* { font-family: serif; }
html, body, p, div { margin: 0; padding: 0; }
.sans { font-family: sans; }
"""


def _archive():
    return fitz.Archive(FONT_DIR)


def _e(value):
    return escape(str(value or '').strip())


def _issue_label(issue):
    label = _("%(year)s-yil, %(num)s-son") % {'year': issue.year, 'num': issue.number}
    if getattr(issue, 'volume', None):
        label += f" · {_('Jild')} {issue.volume}"
    return label


def _title_html(title):
    return (f'<p style="text-align:center;font-size:20pt;font-weight:bold;color:{NAVY};letter-spacing:1pt;">'
            f'{_e(title)}</p>')


# ---------------------------------------------------------------- mundarija
def _measure(html, width, arc):
    story = fitz.Story(html=html, user_css=CSS, archive=arc)
    _more, filled = story.place(fitz.Rect(0, 0, width, 2000))
    return fitz.Rect(filled).y1
def build_toc(issue, journal, items):
    """items: [{'article', 'start_page', 'end_page'}]. Qaytaradi (doc, link_zonalar).

    Har bir maqola: chapda sarlavha + muallif, o'ngda bet oralig'i sarlavhaning
    birinchi qatori bilan bir balandlikda. link_zonalar[i] = (toc_page_index, Rect).
    """
    doc = fitz.open()
    arc = _archive()
    right = A4.width - MARGIN_R
    num_w = 62.0
    bottom = A4.height - MARGIN_B

    page = doc.new_page(width=A4.width, height=A4.height)
    page.insert_htmlbox(fitz.Rect(MARGIN_L, MARGIN_T, right, MARGIN_T + 40), _title_html(_("Mundarija")),
                        css=CSS, archive=arc)
    y = MARGIN_T + 52

    links = []
    for n, item in enumerate(items, 1):
        art = item['article']
        authors = art.authors or (art.author.get_full_name() if getattr(art, 'author', None) else '')
        html = (
            f'<p style="font-size:11pt;font-weight:bold;line-height:1.3;color:#111;">'
            f'<span style="color:{NAVY}">{n}.</span> {_e(art.title)}</p>'
        )
        if authors:
            html += (f'<p class="sans" style="font-size:8.5pt;color:#555;margin-top:3pt;line-height:1.3;">'
                     f'{_e(authors)}</p>')
        used = _measure(html, right - num_w - 10 - MARGIN_L, arc)
        if y + used > bottom:
            page = doc.new_page(width=A4.width, height=A4.height)
            y = MARGIN_T
        page.insert_htmlbox(fitz.Rect(MARGIN_L, y, right - num_w - 10, y + used + 6),
                            html, css=CSS, archive=arc)

        sp, ep = item['start_page'], item['end_page']
        pages = f"{sp}" if sp == ep else f"{sp}–{ep}"
        page.insert_htmlbox(
            fitz.Rect(right - num_w, y, right, y + 20),
            f'<p style="text-align:right;font-size:11pt;font-weight:bold;color:{NAVY};">{pages}</p>',
            css=CSS, archive=arc)
        links.append((doc.page_count - 1, fitz.Rect(MARGIN_L, y - 3, right, y + used + 3)))

        y += used + 7
        if n < len(items):
            page.draw_line((MARGIN_L, y), (right, y), color=LINE, width=0.5)
        y += 9
    return doc, links


# ---------------------------------------------------------------- tahririyat
def _person_html(p, show_role):
    degree = ', '.join(x for x in (p.academic_degree, p.academic_title) if x)
    place = p.workplace or p.institution or ''
    out = '<div style="margin-bottom:8pt;">'
    if show_role:
        out += (f'<p class="sans" style="font-size:7.5pt;letter-spacing:1pt;color:#6b7c93;">'
                f'{_e(p.get_position_display()).upper()}</p>')
    out += f'<p style="font-size:11.5pt;font-weight:bold;color:#111;margin-top:1pt;">{_e(p.full_name)}'
    if degree:
        out += f'<span style="font-weight:normal;font-size:9.5pt;color:{NAVY};"> — {_e(degree)}</span>'
    out += '</p>'
    if place:
        out += f'<p class="sans" style="font-size:8.5pt;color:#555;line-height:1.3;margin-top:1pt;">{_e(place)}</p>'
    return out + '</div>'


def build_editorial(journal, leadership, board):
    html = _title_html(_("Tahririyat"))
    html += '<div style="margin-top:22pt;"></div>'
    for p in leadership:
        html += _person_html(p, show_role=True)
    if leadership and board:
        html += '<div style="margin-top:8pt;"></div>'
    for p in board:
        html += _person_html(p, show_role=False)

    story = fitz.Story(html=html, user_css=CSS, archive=_archive())
    buf = io.BytesIO()
    writer = fitz.DocumentWriter(buf)
    where = fitz.Rect(MARGIN_L, MARGIN_T, A4.width - MARGIN_R, A4.height - MARGIN_B)
    more = True
    while more:
        dev = writer.begin_page(A4)
        more, _f = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()
    return fitz.open(stream=buf.getvalue(), filetype='pdf')


# ---------------------------------------------------------------- footer
def _is_page_number(text):
    t = text.strip().strip('-–—.|[]()').strip()
    return t.isdigit() and len(t) <= 4


def remove_original_page_numbers(page):
    """Maqola faylining o'z bet raqamini (1, 2, - 3 -) sahifa tepasi/pastidan olib tashlaydi."""
    h = page.rect.height
    lines = {}
    for w in page.get_text('words'):
        if w[1] > h * 0.88 or w[3] < h * 0.08:
            lines.setdefault((w[5], w[6]), []).append(w)
    rects = []
    for words in lines.values():
        text = ''.join(w[4] for w in words)
        if _is_page_number(text):
            r = fitz.Rect(words[0][:4])
            for w in words[1:]:
                r |= fitz.Rect(w[:4])
            rects.append(r)
    if not rects:
        return
    for r in rects:
        page.add_redact_annot(r + (-1, -1, 1, 1), fill=(1, 1, 1))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=getattr(fitz, 'PDF_REDACT_LINE_ART_NONE', 0))


def draw_footer(page, left_text, page_num):
    w, h = page.rect.width, page.rect.height
    y = h - 40.0
    page.draw_line((MARGIN_L, y), (w - MARGIN_R, y), color=LINE, width=0.5)
    page.insert_textbox(fitz.Rect(MARGIN_L, y + 5, w - 110, h - 12), left_text,
                        fontsize=7.5, fontname='dejavu', fontfile=SANS, color=FOOTER_GRAY, align=0)
    page.insert_textbox(fitz.Rect(w - 110, y + 4, w - MARGIN_R, h - 12), str(page_num),
                        fontsize=9, fontname='dejavu', fontfile=SANS, color=FOOTER_NAVY, align=2)


# ---------------------------------------------------------------- yo'nalish nomi
TIMES_BOLD = os.path.join(FONT_DIR, 'LiberationSerif-Bold.ttf')  # Times New Roman bilan bir xil o'lcham


def _content_top(page):
    tops = [b[1] for b in page.get_text('blocks') if b[4].strip()]
    tops += [r.y0 for img in page.get_images(full=True) for r in page.get_image_rects(img[0])]
    tops += [d['rect'].y0 for d in page.get_drawings() if d['rect'].height < page.rect.height * 0.9]
    return min(tops) if tops else page.rect.height


def add_category_heading(doc, index, name, size=16):
    """Yo'nalishning birinchi maqolasi boshiga yo'nalish nomini (Times New Roman, 16, qalin)
    bir marta yozadi. Tepada joy yetmasa sahifa mazmuni biroz kichraytirib pastga suriladi."""
    page = doc[index]
    w, h = page.rect.width, page.rect.height
    font = fitz.Font(fontfile=TIMES_BOLD)
    lines, line = [], ''
    for word in name.split():
        trial = f"{line} {word}".strip()
        if line and font.text_length(trial, size) > w - MARGIN_L - MARGIN_R:
            lines.append(line); line = word
        else:
            line = trial
    lines.append(line)
    need = len(lines) * size * 1.25 + 14
    top = 28.0
    if _content_top(page) < top + need:
        src = fitz.open()
        src.insert_pdf(doc, from_page=index, to_page=index)
        doc.delete_page(index)
        page = doc.new_page(pno=index, width=w, height=h)
        page.show_pdf_page(fitz.Rect(0, top + need - 20, w, h), src, 0, keep_proportion=True)
    y = top + size
    for ln in lines:
        x = (w - font.text_length(ln, size)) / 2
        page.insert_text((x, y), ln, fontsize=size, fontname='timesbd', fontfile=TIMES_BOLD, color=(0, 0, 0))
        y += size * 1.25
