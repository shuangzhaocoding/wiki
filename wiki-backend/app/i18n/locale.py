"""
从 Accept-Language 解析语言标签，映射到项目支持的语言。
前端约定：zh→zh-CN, en→en-US, ko→ko-KR, de→de-DE, ja→ja-JP, fr→fr-FR
"""
from typing import Optional

from app.i18n.constants import DEFAULT_LOCALE, SUPPORTED_LOCALES


def _normalize_primary_tag(tag: str) -> Optional[str]:
    """将单个语言标签（不含 q=）映射到 SUPPORTED_LOCALES 中的值。"""
    t = tag.strip().lower().replace("_", "-")
    if not t:
        return None

    # 完整标签优先
    exact = {
        "zh-cn": "zh-CN",
        "zh-hans": "zh-CN",
        "zh-sg": "zh-CN",
        "en-us": "en-US",
        "en-gb": "en-US",
        "ko-kr": "ko-KR",
        "de-de": "de-DE",
        "ja-jp": "ja-JP",
        "fr-fr": "fr-FR",
    }
    if t in exact:
        return exact[t]

    if t.startswith("zh"):
        return "zh-CN"
    if t.startswith("en"):
        return "en-US"
    if t.startswith("ko"):
        return "ko-KR"
    if t.startswith("de"):
        return "de-DE"
    if t.startswith("ja"):
        return "ja-JP"
    if t.startswith("fr"):
        return "fr-FR"

    # 单段主语言码
    primary = t.split("-", 1)[0]
    primary_map = {
        "zh": "zh-CN",
        "en": "en-US",
        "ko": "ko-KR",
        "de": "de-DE",
        "ja": "ja-JP",
        "fr": "fr-FR",
    }
    loc = primary_map.get(primary)
    if loc and loc in SUPPORTED_LOCALES:
        return loc
    return None


def parse_accept_language(header: Optional[str]) -> str:
    """
    解析 RFC 7231 Accept-Language，返回首个支持的语言，否则 DEFAULT_LOCALE。
    例：zh-CN,zh;q=0.9,en;q=0.8
    """
    if not header or not header.strip():
        return DEFAULT_LOCALE

    for part in header.split(","):
        tag = part.split(";", 1)[0].strip()
        loc = _normalize_primary_tag(tag)
        if loc:
            return loc
    return DEFAULT_LOCALE
