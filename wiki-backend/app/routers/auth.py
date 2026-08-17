"""
认证相关路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from app.models.user import User
from app.models.role import Role, UserRole
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_active_user, get_request_locale
from app.i18n import t
from app.core.response import success_response, error_response
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SendRegisterCodeRequest,
    SendResetPasswordCodeRequest,
    TokenResponse,
    UserResponse,
)
from config import settings
from app.outer_apis.after_sale_api import NarwalTech
from tortoise.transactions import in_transaction
from app.utils.email_service import (
    REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS,
    REGISTER_EMAIL_CODE_EXPIRE_SECONDS,
    can_send_register_email_code,
    can_send_reset_password_email_code,
    mark_register_email_code_sent,
    mark_reset_password_email_code_sent,
    save_register_email_code,
    save_reset_password_email_code,
    send_email_code,
    send_reset_password_email_code,
    verify_register_email_code,
    verify_reset_password_email_code,
)

router = APIRouter()

DEFAULT_ROLE_ID = 7  # 首次登录用户的默认角色ID  普通用户


@router.post("/login")
async def login(
    login_data: LoginRequest,
    locale: str = Depends(get_request_locale),
):
    """用户登录"""
    user = await User.get_or_none(email=login_data.username)
    if not user:
        return error_response(401, t(locale, "auth.login.user_not_found"))
    if not verify_password(login_data.password, user.password):
            return error_response(401, t(locale, "auth.login.invalid_credentials"))

    if user.status != 1:
        return error_response(403, t(locale, "auth.login.user_disabled"))
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await user.save()
    
    # 生成Token
    access_token = create_access_token(data={"sub": user.id})
    token_data = {"access_token": access_token, "token_type": "bearer"}
    return success_response(data=token_data, message=t(locale, "auth.login.success"))


@router.post("/register")
async def register(
    register_data: RegisterRequest,
    locale: str = Depends(get_request_locale),
):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = await User.get_or_none(username=register_data.username)
    if existing_user:
        return error_response(400, t(locale, "auth.register.duplicate_username"))

    # 检查邮箱是否已存在
    if register_data.email:
        existing_email = await User.get_or_none(email=register_data.email)
        if existing_email:
            return error_response(400, t(locale, "auth.register.duplicate_email"))

    # 校验邮箱验证码
    code_ok = await verify_register_email_code(
        register_data.email,
        register_data.email_code.strip(),
    )
    if not code_ok:
        return error_response(400, t(locale, "auth.register.code_invalid"))
    
    default_role = await Role.get_or_none(id=DEFAULT_ROLE_ID, status=1)
    async with in_transaction():
        # 创建用户
        user = await User.create(
            username=register_data.username,
            password=get_password_hash(register_data.password),
            email=register_data.email,
            nickname=register_data.nickname or register_data.username
        )
        if default_role:
            await UserRole.create(
                user=user,
                role=default_role,
                status=1,
            )
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "status": user.status
    }
    return success_response(data=user_data, message=t(locale, "auth.register.success"))


@router.post("/send-register-code")
async def send_register_code(
    body: SendRegisterCodeRequest,
    locale: str = Depends(get_request_locale),
):
    """发送注册邮箱验证码"""
    existing_email = await User.get_or_none(email=body.email)
    if existing_email:
        return error_response(400, t(locale, "auth.send_register.email_taken"))

    can_send = await can_send_register_email_code(body.email)
    if not can_send:
        return error_response(
            400,
            t(
                locale,
                "auth.send_register.rate_limit",
                seconds=REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS,
            ),
        )

    try:
        code = send_email_code(body.email, locale=locale)
        await save_register_email_code(body.email, code)
        await mark_register_email_code_sent(body.email)
    except Exception as e:
        return error_response(
            500, t(locale, "auth.send_register.send_failed"), data={"detail": str(e)}
        )

    return success_response(
        data={
            "expire_seconds": REGISTER_EMAIL_CODE_EXPIRE_SECONDS,
            "send_interval_seconds": REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS,
        },
        message=t(locale, "auth.send_register.success"),
    )


@router.post("/send-reset-password-code")
async def send_reset_password_code(
    body: SendResetPasswordCodeRequest,
    locale: str = Depends(get_request_locale),
):
    """发送重置密码邮箱验证码"""
    user = await User.get_or_none(email=body.email, status=1)
    if not user:
        return error_response(404, t(locale, "auth.send_reset.user_not_found"))

    can_send = await can_send_reset_password_email_code(body.email)
    if not can_send:
        return error_response(
            400,
            t(
                locale,
                "auth.send_reset.rate_limit",
                seconds=REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS,
            ),
        )

    try:
        code = send_reset_password_email_code(body.email, locale=locale)
        await save_reset_password_email_code(body.email, code)
        await mark_reset_password_email_code_sent(body.email)
    except Exception as e:
        return error_response(
            500, t(locale, "auth.send_reset.send_failed"), data={"detail": str(e)}
        )

    return success_response(
        data={
            "expire_seconds": REGISTER_EMAIL_CODE_EXPIRE_SECONDS,
            "send_interval_seconds": REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS,
        },
        message=t(locale, "auth.send_reset.success"),
    )


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    locale: str = Depends(get_request_locale),
):
    """忘记密码后通过邮箱验证码重置密码"""
    user = await User.get_or_none(email=body.email, status=1)
    if not user:
        return error_response(404, t(locale, "auth.reset.user_not_found"))

    code_ok = await verify_reset_password_email_code(
        body.email,
        body.email_code.strip(),
    )
    if not code_ok:
        return error_response(400, t(locale, "auth.reset.code_invalid"))

    user.password = get_password_hash(body.new_password)
    await user.save()
    return success_response(message=t(locale, "auth.reset.success"))


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    locale: str = Depends(get_request_locale),
):
    """获取当前用户信息"""
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "status": current_user.status,
        "last_login_at": current_user.last_login_at,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }
    return success_response(data=user_data, message=t(locale, "auth.me.success"))
