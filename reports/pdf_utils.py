from functools import lru_cache
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph

FONT_NAME = 'Vazirmatn'
FONT_REGISTERED = False


def _font_paths():
    base = Path(settings.BASE_DIR) / 'static' / 'fonts'
    return [
        base / 'Vazirmatn-Regular.ttf',
        Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),
        Path('/Library/Fonts/Arial Unicode.ttf'),
    ]


def register_persian_font():
    global FONT_REGISTERED
    if FONT_REGISTERED:
        return FONT_NAME
    for font_path in _font_paths():
        if font_path.exists():
            pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
            FONT_REGISTERED = True
            return FONT_NAME
    raise FileNotFoundError(
        'فونت فارسی یافت نشد. فایل static/fonts/Vazirmatn-Regular.ttf را قرار دهید.'
    )


def shape_persian(text):
    if text is None:
        return ''
    text = str(text)
    if not any('\u0600' <= ch <= '\u06FF' or '\uFB50' <= ch <= '\uFDFF' for ch in text):
        return text
    return get_display(arabic_reshaper.reshape(text))


@lru_cache(maxsize=1)
def get_pdf_styles():
    font = register_persian_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleFA',
        parent=styles['Heading1'],
        fontName=font,
        fontSize=16,
        alignment=1,
        spaceAfter=20,
        leading=22,
    )
    normal = ParagraphStyle(
        'NormalFA',
        parent=styles['Normal'],
        fontName=font,
        fontSize=11,
        spaceAfter=8,
        alignment=2,
        leading=16,
    )
    table_cell = ParagraphStyle(
        'TableFA',
        parent=styles['Normal'],
        fontName=font,
        fontSize=9,
        alignment=2,
        leading=13,
    )
    return title_style, normal, table_cell


def fa_paragraph(text, style):
    return Paragraph(shape_persian(text), style)


def fa_cell(text, style):
    return Paragraph(shape_persian(text), style)
