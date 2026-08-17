"""
邮箱验证码与邀请邮件服务
"""
import random
import smtplib
import ssl
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from os import getenv

import redis.asyncio as redis

from app.core.redis_url import build_redis_url
from app.i18n import DEFAULT_LOCALE, t
from config import settings


SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = int(settings.SMTP_PORT)
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
SMTP_FROM_NAME = settings.SMTP_FROM_NAME


REDIS_URL = build_redis_url()
REGISTER_EMAIL_CODE_EXPIRE_SECONDS = int(
    getenv("REGISTER_EMAIL_CODE_EXPIRE_SECONDS", "60")
)
REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS = int(
    getenv("REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS", "60")
)


def _code_key(scene: str, email: str) -> str:
    return f"{scene}_email_code:{email}"


def _cooldown_key(scene: str, email: str) -> str:
    return f"{scene}_email_code_cooldown:{email}"


def _format_addr(s: str):
    name, addr = parseaddr(s)
    return formataddr((Header(name, "utf-8").encode(), addr))


def _generate_code(length: int = 6) -> str:
    return "".join(random.choice("0123456789") for _ in range(length))


async def _save_email_code(scene: str, email: str, code: str) -> None:
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await client.setex(
            _code_key(scene, email),
            REGISTER_EMAIL_CODE_EXPIRE_SECONDS,
            code,
        )
    finally:
        await client.aclose()


async def save_register_email_code(email: str, code: str) -> None:
    await _save_email_code("register", email, code)


async def save_reset_password_email_code(email: str, code: str) -> None:
    await _save_email_code("reset_password", email, code)


async def _can_send_email_code(scene: str, email: str) -> bool:
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        cooldown_key = _cooldown_key(scene, email)
        return not await client.exists(cooldown_key)
    finally:
        await client.aclose()


async def can_send_register_email_code(email: str) -> bool:
    return await _can_send_email_code("register", email)


async def can_send_reset_password_email_code(email: str) -> bool:
    return await _can_send_email_code("reset_password", email)


async def _mark_email_code_sent(scene: str, email: str) -> None:
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        cooldown_key = _cooldown_key(scene, email)
        await client.setex(
            cooldown_key,
            REGISTER_EMAIL_CODE_SEND_INTERVAL_SECONDS,
            "1",
        )
    finally:
        await client.aclose()


async def mark_register_email_code_sent(email: str) -> None:
    await _mark_email_code_sent("register", email)


async def mark_reset_password_email_code_sent(email: str) -> None:
    await _mark_email_code_sent("reset_password", email)


async def _verify_email_code(scene: str, email: str, code: str) -> bool:
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        key = _code_key(scene, email)
        cached_code = await client.get(key)
        if not cached_code or cached_code.lower() != code.lower():
            return False
        await client.delete(key)
        return True
    finally:
        await client.aclose()


async def verify_register_email_code(email: str, code: str) -> bool:
    return await _verify_email_code("register", email, code)


async def verify_reset_password_email_code(email: str, code: str) -> bool:
    return await _verify_email_code("reset_password", email, code)


def send_email_code(email: str, locale: str = DEFAULT_LOCALE) -> str:
    """发送注册验证码邮件，并返回验证码。locale 与 Accept-Language 解析结果一致。"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise RuntimeError(t(locale, "email.smtp_incomplete"))

    code = _generate_code()
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

        body = t(
            locale,
            "email.register.body",
            code=code,
            seconds=REGISTER_EMAIL_CODE_EXPIRE_SECONDS,
        )
        message = MIMEText(body, "plain", "utf-8")
        message["From"] = _format_addr(f"{SMTP_FROM_NAME} <{SMTP_USERNAME}>")
        message["To"] = _format_addr(f"Wiki User <{email}>")
        message["Subject"] = Header(t(locale, "email.register.subject"), "utf-8")

        smtp.sendmail(SMTP_USERNAME, [email], message.as_string())
        return code
    finally:
        smtp.quit()


def send_reset_password_email_code(email: str, locale: str = DEFAULT_LOCALE) -> str:
    """发送重置密码验证码邮件，并返回验证码。locale 与 Accept-Language 解析结果一致。"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise RuntimeError(t(locale, "email.smtp_incomplete"))

    code = _generate_code()
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

        body = t(
            locale,
            "email.reset.body",
            code=code,
            seconds=REGISTER_EMAIL_CODE_EXPIRE_SECONDS,
        )
        message = MIMEText(body, "plain", "utf-8")
        message["From"] = _format_addr(f"{SMTP_FROM_NAME} <{SMTP_USERNAME}>")
        message["To"] = _format_addr(f"Wiki User <{email}>")
        message["Subject"] = Header(t(locale, "email.reset.subject"), "utf-8")

        smtp.sendmail(SMTP_USERNAME, [email], message.as_string())
        return code
    finally:
        smtp.quit()
