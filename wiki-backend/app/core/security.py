"""
安全相关功能：密码加密、JWT Token
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from config import settings

# bcrypt密码最大长度限制（字节）
BCRYPT_MAX_PASSWORD_LENGTH = 72


def _truncate_password_bytes(password: str) -> bytes:
    """
    截断密码到bcrypt允许的最大长度（72字节），返回bytes
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
        # 截断到72字节
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # 截断密码到72字节
        password_bytes = _truncate_password_bytes(plain_password)
        # 验证密码
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # 截断密码到72字节
    password_bytes = _truncate_password_bytes(password)
    # 生成盐并哈希密码
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    # JWT标准要求sub字段必须是字符串
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 将sub字段转换回整数（如果存在）
        if "sub" in payload and isinstance(payload["sub"], str):
            try:
                payload["sub"] = int(payload["sub"])
            except (ValueError, TypeError):
                pass
        return payload
    except JWTError as e:
        # 记录详细错误信息用于调试
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"JWT解码错误: {str(e)}, Token前20字符: {token[:20] if token else 'None'}")
        return None
    except Exception as e:
        # 捕获其他异常（如令牌格式错误等）
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"令牌解码异常: {str(e)}, Token前20字符: {token[:20] if token else 'None'}")
        return None
