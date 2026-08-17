"""
FastAPI依赖项
"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.core.security import decode_access_token
from app.i18n import parse_accept_language, t

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_request_locale(request: Request) -> str:
    """请求语言：优先中间件写入的 state.locale，否则解析 Accept-Language。"""
    loc = getattr(request.state, "locale", None)
    if loc:
        return loc
    return parse_accept_language(request.headers.get("accept-language"))


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> User:
    """获取当前登录用户"""
    locale = get_request_locale(request)

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t(locale, "deps.token_expired"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")

    user = await User.get_or_none(id=user_id, status=1)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t(locale, "deps.user_not_found"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    locale = get_request_locale(request)
    if current_user.status != 1:
        raise HTTPException(status_code=401, detail=t(locale, "deps.user_disabled"))
    return current_user
