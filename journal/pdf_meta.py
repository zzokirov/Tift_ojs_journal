"""Maqola faylidan (PDF yoki DOCX) annotatsiya va kalit so'zlarni ajratib olish.

Ko'p maqolalarda annotatsiya admin panelga kiritilmagan, faqat faylning o'zida bor.
Bu yerda o'zbek (lotin/kirill), rus va ingliz tilidagi sarlavhalar tanib olinadi.
"""
import re

ABSTRACT_HEAD = re.compile(
    r"(?im)^[\s\W]*(annotatsiya|аннотация|annotation|abstract|резюме|аннотация)\b[\s:.\-–—]*",
)
KEYWORDS_HEAD = re.compile(
    r"(?i)(kalit\s+so[ʻ'’‘`]?z(?:lar)?|калит\s+с[ўу]злар|ключевые\s+слова|key\s*-?\s*words?)\s*[:.\-–—]*\s*",
)
STOP_HEAD = re.compile(
    r"(?im)^[\s\W]*(kirish|введение|introduction|annotatsiya|аннотация|annotation|abstract|резюме|"
    r"adabiyotlar|литература|references|i\.\s|1\.\s)",
)

MAX_PAGES = 3


def _pdf_text(path):
    import fitz
    with fitz.open(path) as doc:
        return "\n".join(doc[i].get_text() for i in range(min(MAX_PAGES, doc.page_count)))


def _docx_text(path):
    import docx
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs[:200])


def _clean(s):
    s = re.sub(r"(\w)-\n(\w)", r"\1\2", s)       # satr oxiridagi bo'g'in ko'chirish
    s = re.sub(r"\s+", " ", s)
    return s.strip(" \t\n:;.-–—")


def extract_from_text(text):
    """(annotatsiya, kalit_so'zlar) qaytaradi; topilmasa bo'sh satrlar."""
    if not text:
        return "", ""
    abstract, keywords = "", ""

    m = ABSTRACT_HEAD.search(text)
    if m:
        rest = text[m.end():]
        k = KEYWORDS_HEAD.search(rest)
        if k and k.start() < 6000:
            abstract = rest[:k.start()]
        else:
            stop = STOP_HEAD.search(rest)
            abstract = rest[:stop.start()] if stop and stop.start() > 80 else rest[:2500]
        abstract = _clean(abstract)
        if not (80 <= len(abstract) <= 5000):
            abstract = ""

    k = KEYWORDS_HEAD.search(text, m.end() if m else 0) or KEYWORDS_HEAD.search(text)
    if k:
        rest = text[k.end():k.end() + 600]
        stop = STOP_HEAD.search(rest)
        if stop and stop.start() > 3:
            rest = rest[:stop.start()]
        # Kalit so'zlar odatda bitta xatboshi: bo'sh qatorgacha olamiz
        rest = re.split(r"\n\s*\n", rest)[0]
        keywords = _clean(rest)
        if len(keywords) > 400 or len(keywords) < 3:
            keywords = ""
    return abstract, keywords


def extract_from_file(path):
    from .docconvert import sniff
    kind = sniff(path)  # kengaytmaga emas, fayl ichidagi baytlarga qaraymiz
    try:
        if kind == "pdf":
            text = _pdf_text(path)
        elif kind == "docx":
            text = _docx_text(path)
        else:
            return "", ""
    except Exception:
        return "", ""
    return extract_from_text(text)


def fill_article_meta(article):
    """Annotatsiya/kalit so'zlar bo'sh bo'lsa, fayldan to'ldiradi va bazaga yozadi
    (save() emas — tarjima signallari ishga tushmaydi). O'zgargan bo'lsa True."""
    import os
    from .models import Article

    need_abs = not (article.abstract or "").strip()
    need_kw = not (article.keywords or "").strip()
    if not (need_abs or need_kw) or not article.pdf_file:
        return False
    try:
        path = article.pdf_file.path
    except Exception:
        return False
    if not os.path.exists(path):
        return False

    abstract, keywords = extract_from_file(path)
    updates = {}
    if need_abs and abstract:
        updates["abstract_uz"] = abstract
        article.abstract = abstract
    if need_kw and keywords:
        updates["keywords_uz"] = keywords[:255]
        article.keywords = keywords[:255]
    if updates:
        Article.objects.filter(pk=article.pk).update(**updates)
        return True
    return False
