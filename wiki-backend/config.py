"""
配置文件

敏感信息从环境变量或 wiki-backend/.env 读取，勿把密钥写入仓库。
"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # 是否生产环境
    IS_PRODUCT_ENV: bool = True

    # 华为 OBS
    OBS_ACCESS_KEY_ID: str = ""
    OBS_SECRET_ACCESS_KEY: str = ""
    OBS_ENDPOINT: str = "obs.cn-south-1.myhuaweicloud.com"
    OBS_BUCKET_NAME: str = "zs-wiki"

    # 应用配置
    APP_NAME: str = "知识库系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # MySQL
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "wiki"

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    # JWT
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # CORS：逗号分隔，例如 http://localhost:5173,https://wiki.example.com
    CORS_ORIGINS: str = "http://localhost:5173"

    # 邮箱
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 587
    SMTP_FROM_NAME: str = "YuGongWiki"

    @property
    def cors_origin_list(self) -> list[str]:
        text = (self.CORS_ORIGINS or "").strip()
        if not text:
            return ["http://localhost:5173"]
        if text.startswith("["):
            import json

            parsed = json.loads(text)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in text.split(",") if item.strip()]


settings = Settings()

# Tortoise ORM配置
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "database": settings.DB_NAME,
                "charset": "utf8mb4",
            }
        }
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}
