"""
统一异常处理
"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.response import error_response
from app.i18n import DEFAULT_LOCALE, t


def _request_locale(request: Request) -> str:
    return getattr(request.state, "locale", None) or DEFAULT_LOCALE


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    locale = _request_locale(request)
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "")
        error_messages.append(f"{field}: {message}")

    prefix = t(locale, "error.validation_prefix")
    body = f"{prefix}: {'; '.join(error_messages)}"

    return JSONResponse(
        status_code=200,  # 统一返回200，错误码在body中
        content=error_response(400, body),
    )


async def http_exception_handler(request: Request, exc):
    """处理HTTP异常"""
    status_code = exc.status_code
    detail = exc.detail
    
    # 根据HTTP状态码转换为业务错误码
    code_map = {
        400: 400,
        401: 401,
        403: 403,
        404: 404,
        422: 422,
        500: 500,
    }
    code = code_map.get(status_code, status_code)
    
    return JSONResponse(
        status_code=200,  # 统一返回200，错误码在body中
        content=error_response(code, str(detail))
    )


async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    locale = _request_locale(request)
    return JSONResponse(
        status_code=200,  # 统一返回200，错误码在body中
        content=error_response(500, t(locale, "error.internal", detail=str(exc))),
    )
