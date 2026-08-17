"""
文件上传相关路由
"""
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Form, HTTPException, status
from fastapi.responses import FileResponse as FastAPIFileResponse
from pydantic import BaseModel
from app.enums import PermissionType, ResourceType
from app.models.user import User
from app.models.file import File
from app.models.article import Article
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.outer_apis.huawei_obs_api import HuaweiOBSClient
from app.utils.permissions import require_permission
from app.core.logging_config import setup_logging
logger = setup_logging()
router = APIRouter()

# 文件上传配置
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型和MIME类型映射
ALLOWED_EXTENSIONS = {
    # 图片
    "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"},
    # 视频
    "video": {".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"},
    # Office文档
    "document": {".pptx", ".xlsx", ".docx", ".ppt", ".xls", ".doc", ".csv"},
    # PDF
    "pdf": {".pdf"},
    # 压缩包
    "archive": {".zip", ".rar", ".7z", ".tar", ".gz"},
}

# MIME类型映射
MIME_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".wmv": "video/x-ms-wmv",
    ".flv": "video/x-flv",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".ppt": "application/vnd.ms-powerpoint",
    ".xls": "application/vnd.ms-excel",
    ".doc": "application/msword",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".rar": "application/x-rar-compressed",
    ".7z": "application/x-7z-compressed",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
}

# 文件大小限制（字节）
MAX_FILE_SIZE = {
    "image": 500 * 1024 * 1024,  # 10MB
    "video": 500 * 1024 * 1024,  # 100MB
    "document": 500 * 1024 * 1024,  # 50MB
    "pdf": 500 * 1024 * 1024,  # 50MB
    "archive": 500 * 1024 * 1024,  # 200MB
}


def get_file_type(extension: str) -> Optional[str]:
    """根据文件扩展名获取文件类型"""
    extension_lower = extension.lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension_lower in extensions:
            return extension_lower
    return None


def get_mime_type(extension: str) -> str:
    """根据文件扩展名获取MIME类型"""
    return MIME_TYPE_MAP.get(extension.lower(), "application/octet-stream")


class FileUploadResponse(BaseModel):
    id: int
    filename: str
    file_url: str
    file_type: str
    file_size: int
    article_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/upload/local", summary="上传文件", description="支持上传图片、视频、Office文档、PDF、压缩包等")
async def upload_file(
    file: UploadFile = FastAPIFile(..., description="要上传的文件"),
    article_id: Optional[int] = Form(None, description="关联的文章ID（可选）"),
    current_user: User = Depends(get_current_active_user),
):
    """上传文件"""
    # 如果提供了article_id，验证文章是否存在
    article = None
    if article_id is not None:
        article = await Article.get_or_none(id=article_id, status__gt=0)
        if not article:
            return error_response(404, "文章不存在")
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.EDIT)
    # 获取文件扩展名
    filename = file.filename
    if not filename:
        return error_response(400, "文件名不能为空")
    
    extension = Path(filename).suffix
    if not extension:
        return error_response(400, "文件必须包含扩展名")
    
    # 检查文件类型是否允许
    file_type = get_file_type(extension)
    if not file_type:
        allowed = ", ".join([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])
        return error_response(400, f"不支持的文件类型。支持的类型：{allowed}")
    
    # 读取文件内容
    content = await file.read()
    file_size = len(content)
    
    # 检查文件大小
    max_size = MAX_FILE_SIZE.get(file_type)
    if max_size and file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return error_response(400, f"文件大小超过限制（{file_type}类型最大{max_size_mb}MB）")
    
    # 生成唯一文件名
    file_hash = hashlib.md5(content).hexdigest()
    stored_filename = f"{file_hash}_{uuid.uuid4().hex[:8]}{extension}"
    
    # 按日期组织目录结构：uploads/YYYY/MM/DD/
    now = datetime.now()
    date_dir = UPLOAD_DIR / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # 文件存储路径
    file_path = date_dir / stored_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        return error_response(500, f"文件保存失败：{str(e)}")
    
    # 生成文件URL（相对路径）
    relative_path = file_path.relative_to(UPLOAD_DIR)
    file_url = f"/api/files/{relative_path.as_posix()}"
    
    # 保存文件记录到数据库
    file_record = await File.create(
        filename=filename,
        stored_filename=stored_filename,
        file_path=str(relative_path),
        file_url=file_url,
        file_type=file_type,
        mime_type=get_mime_type(extension),
        file_size=file_size,
        uploader=current_user,
        article=article,
    )
    
    # 构建响应数据
    data = {
        "id": file_record.id,
        "filename": file_record.filename,
        "file_url": file_record.file_url,
        "file_type": file_record.file_type,
        "file_size": file_record.file_size,
        "article_id": file_record.article_id,
        "created_at": file_record.created_at,
    }
    return success_response(data=data, message="上传成功")


@router.post("/upload", summary="上传文件至华为OBS", description="上传文件至华为OBS，并返回文件URL")
async def upload_file_to_obs(
    file: UploadFile = FastAPIFile(..., description="要上传的文件"),
    article_id: Optional[int] = Form(None, description="关联的文章ID（可选）"),
    current_user: User = Depends(get_current_active_user),
):
    """上传文件"""
    # 如果提供了article_id，验证文章是否存在
    article = None
    if article_id is not None:
        article = await Article.get_or_none(id=article_id, status__gt=0)
        if not article:
            return error_response(404, "文章不存在")
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.EDIT)
    # 获取文件扩展名
    filename = file.filename
    if not filename:
        return error_response(400, "文件名不能为空")
    
    extension = Path(filename).suffix
    if not extension:
        return error_response(400, "文件必须包含扩展名")
    
    # 检查文件类型是否允许
    file_type = get_file_type(extension)
    if not file_type:
        allowed = ", ".join([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])
        return error_response(400, f"不支持的文件类型。支持的类型：{allowed}")
    
    # 读取文件内容
    content = await file.read()
    file_size = len(content)
    
    # 检查文件大小
    max_size = MAX_FILE_SIZE.get(file_type)
    if max_size and file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return error_response(400, f"文件大小超过限制（{file_type}类型最大{max_size_mb}MB）")
    
    # 生成唯一文件名
    file_hash = hashlib.md5(content).hexdigest()
    stored_filename = f"{file_hash}_{uuid.uuid4().hex[:8]}{extension}"
    
    # 按日期组织目录结构：uploads/YYYY/MM/DD/
    now = datetime.now()
    date_dir = UPLOAD_DIR / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # 文件存储路径
    file_path = date_dir / stored_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        return error_response(500, f"文件保存失败：{str(e)}")

    # 对象key组装
    date_part = datetime.now().strftime("%Y-%m-%d")
    key_parts = [p for p in ['wiki', date_part, stored_filename] if p]
    object_key = "/".join(key_parts)

    # 图片/视频则设为 public-read，以返回长期有效直链；其他类型返回签名短链
    # image_exts = {"png","jpg","jpeg","gif","webp","bmp","svg","tiff"}
    # video_exts = {"mp4","avi","mov","wmv","rmvb","mkv","m4v","webm"}
    is_public = True
    # if mime:
    #     is_public = mime.startswith("image/") or mime.startswith("video/")
    # elif ext:
    #     ext_lower = ext.lower()
    #     is_public = (ext_lower in image_exts) or (ext_lower in video_exts)
    client = HuaweiOBSClient()
    try:
        upload_resp = await client.upload_file(
            object_key=object_key,
            file_path=file_path,
            public_read=is_public,
        )
    except Exception as e:
        # 只记录异常类型和简要消息，避免记录文件内容
        error_msg = str(e)[:500] if len(str(e)) > 500 else str(e)
        logger.error(
            f"OBS文件上传失败 - 文件名: {file.filename}, "
            f"文件类型: {file_type or 'unknown'}, "
            f"文件大小: {file_size / 1048576:.2f} MB, "
            f"对象key: {object_key}, "
            f"异常类型: {type(e).__name__}, "
            f"异常消息: {error_msg}"
        )
        return error_response(500, "文件上传失败，请重试")
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass

    if not upload_resp.get("success"):
        error_detail = upload_resp.get("error") or "文件上传失败"
        logger.error(
            f"OBS文件上传失败 - 文件名: {file.filename}, "
            f"文件类型: {file_type or 'unknown'}, "
            f"文件大小: {file_size / 1048576:.2f} MB, "
            f"对象key: {object_key}, "
            f"错误信息: {error_detail[:500]}"
        )
        return error_response(500, error_detail)

    data = upload_resp["data"]

    # 保存文件记录到数据库
    file_record = await File.create(
        filename=filename,
        stored_filename=stored_filename,
        file_path=object_key,
        file_url=data.get("url"),
        file_type=file_type,
        mime_type=get_mime_type(extension),
        file_size=file_size,
        uploader=current_user,
        article=article,
    )
    
    # 构建响应数据
    data = {
        "id": file_record.id,
        "filename": file_record.filename,
        "file_url": file_record.file_url,
        "file_type": file_record.file_type,
        "file_size": file_record.file_size,
        "article_id": file_record.article_id,
        "created_at": file_record.created_at,
    }

    return success_response(message="上传成功", data=data)


@router.get("/{file_path:path}", summary="获取文件", description="根据文件路径获取文件")
async def get_file(
    file_path: str,
):
    """获取文件"""
    # 安全检查：防止路径遍历攻击
    safe_path = Path(file_path)
    if ".." in safe_path.parts:
        raise HTTPException(status_code=400, detail="无效的文件路径")
    
    # 构建完整文件路径
    full_path = UPLOAD_DIR / safe_path
    
    # 检查文件是否存在
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 从数据库获取文件信息（可选，用于记录访问日志等）
    file_record = await File.get_or_none(file_path=str(safe_path), status=1)
    
    # 返回文件
    mime_type = file_record.mime_type if file_record else None
    return FastAPIFileResponse(
        path=str(full_path),
        media_type=mime_type,
        filename=file_record.filename if file_record else safe_path.name,
    )


@router.delete("/{file_id}", summary="删除文件", description="删除已上传的文件")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """删除文件"""
    file_record = await File.get_or_none(id=file_id, status=1)
    if not file_record:
        return error_response(404, "文件不存在")
    
    # 只有上传者可以删除
    if file_record.uploader_id != current_user.id:
        return error_response(403, "只能删除自己上传的文件")
    
    # 删除物理文件
    file_path = UPLOAD_DIR / file_record.file_path
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # 记录错误但不阻止数据库记录删除
            pass
    
    # 标记为已删除
    file_record.status = 0
    await file_record.save()
    
    return success_response(message="删除成功")

