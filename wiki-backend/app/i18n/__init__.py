"""国际化：Accept-Language 解析与文案翻译。"""
from app.i18n.constants import DEFAULT_LOCALE, SUPPORTED_LOCALES
from app.i18n.locale import parse_accept_language
from app.i18n.translate import t

__all__ = [
    "DEFAULT_LOCALE",
    "SUPPORTED_LOCALES",
    "parse_accept_language",
    "t",
]
