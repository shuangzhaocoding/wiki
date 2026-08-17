"""支持的界面语言（与前端 accept-language 约定一致）。"""

DEFAULT_LOCALE = "zh-CN"

SUPPORTED_LOCALES = frozenset(
    {"zh-CN", "en-US", "ko-KR", "de-DE", "ja-JP", "fr-FR"}
)
