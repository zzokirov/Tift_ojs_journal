"""Bazadagi ba'zi qisqa matnlarni tanlangan tilga moslash (tarjima maydoni bo'sh qolgan holatlar uchun)."""
import re

from django import template
from django.utils.translation import get_language

register = template.Library()

_FREQ = re.compile(r"^\s*yiliga\s+(\d+)\s*(?:marta|son)\s*$", re.IGNORECASE)


@register.filter
def frequency(value):
    """'Yiliga 4 marta' -> '4 раза в год' / '4 times a year' (agar tarjima kiritilmagan bo'lsa)."""
    text = str(value or '').strip()
    m = _FREQ.match(text)
    lang = (get_language() or 'uz')[:2]
    if not m or lang == 'uz':
        return text
    n = int(m.group(1))
    if lang == 'ru':
        if n % 10 == 1 and n % 100 != 11:
            word = 'раз'
        elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            word = 'раза'
        else:
            word = 'раз'
        return f"{n} {word} в год"
    if lang == 'en':
        return {1: 'Once a year', 2: 'Twice a year'}.get(n, f"{n} times a year")
    return text
