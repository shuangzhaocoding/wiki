"""
主应用入口
"""
import sys
from pathlib import Path

# 项目根目录在 sys.path 中，以便从 app/ 目录执行 `uvicorn main:app` 时能加载根目录的 config 模块
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from config import settings, TORTOISE_ORM
from app.routers import (
    auth,
    users,
    team_spaces,
    knowledge_bases,
    knowledge_base_tags,
    articles,
    permissions,
    comments,
    files,
    applications,
    roles,
    user_roles,
    system_permissions,
    banners,
    reading_tasks,
    notifications,
)
from app.middleware.logging import LoggingMiddleware
from app.middleware.locale import LocaleMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.logging_config import setup_logging
from app.core.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# 初始化日志
logger = setup_logging()
logger.info("=" * 50)
logger.info("知识库系统API启动")
logger.info("=" * 50)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="知识库系统后端API"
)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 限流中间件（最先执行，限制每分钟2次请求）
app.add_middleware(RateLimitMiddleware, max_requests=120, window_seconds=60)

# 请求日志中间件
app.add_middleware(LoggingMiddleware)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 语言环境（最后注册，作为最外层中间件，优先解析 Accept-Language）
app.add_middleware(LocaleMiddleware)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(team_spaces.router, prefix="/api/team-spaces", tags=["团队空间"])
app.include_router(knowledge_bases.router, prefix="/api/knowledge-bases", tags=["知识库"])
app.include_router(
    knowledge_base_tags.router,
    prefix="/api/knowledge-bases/{kb_id}/tags",
    tags=["知识库标签"],
)
app.include_router(articles.router, prefix="/api/articles", tags=["文章"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["权限"])
app.include_router(comments.router, prefix="/api/comments", tags=["评论"])
app.include_router(files.router, prefix="/api/files", tags=["文件"])
app.include_router(applications.router, prefix="/api/applications", tags=["资源申请"])
app.include_router(roles.router, prefix="/api/roles", tags=["角色管理"])
app.include_router(user_roles.router, prefix="/api/user-roles", tags=["用户角色管理"])
app.include_router(system_permissions.router, prefix="/api/system-permissions", tags=["系统权限管理"])
app.include_router(banners.router, prefix="/api/banners", tags=["Banner 管理"])
app.include_router(reading_tasks.router, prefix="/api/reading-tasks", tags=["阅读任务"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["站内消息"])

# 注册Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=not settings.IS_PRODUCT_ENV,  # 自动生成表结构（仅开发环境）
    add_exception_handlers=True,
)


@app.get("/")
async def root():
    return {
        "message": "知识库系统API",
        "version": settings.APP_VERSION
    }


@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok"}
