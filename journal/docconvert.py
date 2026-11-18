"""Word (.docx/.doc) maqola fayllarini brauzerda ochiladigan PDF'ga aylantirish.

Ba'zi maqolalarga PDF o'rniga Word fayl yuklangan. Brauzer ularni PDF sifatida ocha
olmaydi ("We can't open this file"). Bu yerda fayl turi baytlaridan aniqlanadi, Word
bo'lsa bir marta PDF'ga aylantiriladi va MEDIA_ROOT/converted_pdf/ ichida keshlanadi.

1-usul: LibreOffice (soffice) — asl ko'rinish (jadval, formula, rasm) saqlanadi.
2-usul (LibreOffice yo'q bo'lsa): matn va rasmlar PyMuPDF orqali oddiy PDF qilib chiqariladi.
"""
import hashlib
import os
import shutil
import subprocess
import tempfile

from django.conf import settings

PDF_MAGIC = b'%PDF'
ZIP_MAGIC = b'PK\x03\x04'
OLE_MAGIC = b'\xd0\xcf\x11\xe0'  # eski .doc


def sniff(path):
    """'pdf', 'docx', 'doc' yoki 'other'."""
    try:
        with open(path, 'rb') as f:
            head = f.read(1024)
    except OSError:
        return 'other'
    if PDF_MAGIC in head[:1024]:
        return 'pdf'
    if head.startswith(ZIP_MAGIC):
        return 'docx'
    if head.startswith(OLE_MAGIC):
        return 'doc'
    return 'other'


def _cache_path(src):
    st = os.stat(src)
    key = hashlib.sha1(os.path.realpath(src).encode('utf-8')).hexdigest()[:16]
    folder = os.path.join(settings.MEDIA_ROOT, 'converted_pdf')
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{key}_{int(st.st_mtime)}_{st.st_size}.pdf")


def _with_soffice(src, dest):
    exe = shutil.which('soffice') or shutil.which('libreoffice')
    if not exe:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        ext = '.docx' if sniff(src) == 'docx' else '.doc'
        tmp_src = os.path.join(tmp, 'source' + ext)
        shutil.copyfile(src, tmp_src)
        env = dict(os.environ, HOME=tmp)  # LibreOffice profili uchun yoziladigan papka
        try:
            subprocess.run(
                [exe, '--headless', '--norestore', '--nolockcheck', '--convert-to', 'pdf', '--outdir', tmp, tmp_src],
                env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120, check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            return False
        out = os.path.join(tmp, 'source.pdf')
        if os.path.exists(out) and sniff(out) == 'pdf':
            shutil.move(out, dest)
            return True
    return False


def _with_pymupdf(src, dest):
    """LibreOffice bo'lmasa: python-docx -> HTML -> PDF (PyMuPDF Story)."""
    if sniff(src) != 'docx':
        return False
    import fitz
    from .views import _extract_docx_text_as_html

    body = _extract_docx_text_as_html(src) or ''
    if not body.strip():
        return False
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'certificate')
    css = """
        @font-face { font-family: doc; src: url(DejaVuSerif.ttf); }
        @font-face { font-family: doc; src: url(DejaVuSerif-Bold.ttf); font-weight: bold; }
        * { font-family: doc; }
        body { font-size: 11pt; line-height: 1.45; }
        h1, h2, h3 { font-weight: bold; }
        table { border-collapse: collapse; } td, th { border: 1px solid #999; padding: 3px; }
        img { max-width: 100%; }
    """
    story = fitz.Story(html=body, user_css=css, archive=fitz.Archive(font_dir))
    tmp_dest = dest + '.tmp'
    writer = fitz.DocumentWriter(tmp_dest)
    page = fitz.paper_rect('a4')
    where = page + (56, 56, -56, -56)
    more = True
    while more:
        dev = writer.begin_page(page)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
    writer.close()
    if sniff(tmp_dest) == 'pdf':
        os.replace(tmp_dest, dest)
        return True
    return False


def pdf_path_for(path):
    """Brauzerda ochiladigan PDF yo'li. PDF bo'lsa o'zi; Word bo'lsa keshlangan PDF.
    Aylantirib bo'lmasa None."""
    if not path or not os.path.exists(path):
        return None
    kind = sniff(path)
    if kind == 'pdf':
        return path
    if kind not in ('docx', 'doc'):
        return None
    dest = _cache_path(path)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    try:
        if _with_soffice(path, dest) or _with_pymupdf(path, dest):
            return dest
    except Exception:
        pass
    return None
