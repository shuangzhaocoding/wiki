"""翻译函数：按 locale 取文案，缺键时回退到默认语言。"""

from app.i18n.constants import DEFAULT_LOCALE
from app.i18n.translations import get_messages


def t(locale: str, key: str, **kwargs) -> str:
    """
    返回本地化字符串。kwargs 传入 format 命名参数。
    若当前语言缺键，回退到 DEFAULT_LOCALE；仍缺则返回 key。
    """
    catalog = get_messages(locale)
    template = catalog.get(key)
    if template is None and locale != DEFAULT_LOCALE:
        template = get_messages(DEFAULT_LOCALE).get(key)
    if template is None:
        return key
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template
