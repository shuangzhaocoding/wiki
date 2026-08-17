"""
文件模型
"""
from tortoise.models import Model
from tortoise import fields


class File(Model):
    """文件表"""
    id = fields.BigIntField(pk=True)
    filename = fields.CharField(max_length=255, description="原始文件名")
    stored_filename = fields.CharField(max_length=255, description="存储文件名")
    file_path = fields.CharField(max_length=500, description="文件存储路径（相对路径）")
    file_url = fields.CharField(max_length=500, description="文件访问URL")
    file_type = fields.CharField(max_length=50, description="文件类型（image/video/document/archive等）")
    mime_type = fields.CharField(max_length=100, description="MIME类型")
    file_size = fields.BigIntField(description="文件大小（字节）")
    uploader = fields.ForeignKeyField("models.User", related_name="uploaded_files", description="上传者")
    article = fields.ForeignKeyField("models.Article", related_name="files", null=True, description="关联的文章")
    status = fields.IntField(default=1, description="状态：0-已删除，1-正常")
    created_at = fields.DatetimeField(auto_now_add=True, description="上传时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "files"
        table_description = "文件表"
        indexes = (("uploader", "status"), ("file_type", "status"), ("article", "status"))

    def __str__(self):
        return f"{self.filename} ({self.file_size} bytes)"
