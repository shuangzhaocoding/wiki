"""根据 Accept-Language 设置 request.state.locale，供路由与异常处理使用。"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.i18n import parse_accept_language


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.locale = parse_accept_language(
            request.headers.get("accept-language")
        )
        return await call_next(request)
