"""
Banner 模型：用于存储首页或模块的轮播/横幅信息
"""
from tortoise.models import Model
from tortoise import fields


class Banner(Model):
    """Banner 表"""
    id = fields.BigIntField(pk=True)
    title = fields.CharField(max_length=200, null=True, description="Banner 标题")
    image_url = fields.CharField(max_length=500, description="Banner 图片链接 URL")
    link_url = fields.CharField(max_length=500, null=True, description="点击跳转链接 URL")
    description = fields.TextField(null=True, description="描述/文案")
    position = fields.CharField(
        max_length=50,
        default="default",
        description="展示位置标识（如 home_top、kb_top 等）",
    )
    sort_order = fields.IntField(default=0, description="排序顺序，值越小越靠前")
    status = fields.IntField(
        default=1,
        description="状态：0-禁用/下线，1-启用/上线",
    )
    created_by = fields.ForeignKeyField(
        "models.User",
        related_name="created_banners",
        description="创建人",
    )
    updated_by = fields.ForeignKeyField(
        "models.User",
        related_name="updated_banners",
        null=True,
        description="最后更新人",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "banners"
        table_description = "Banner 配置表（图片链接、跳转链接等）"

    def __str__(self) -> str:
        return self.title or f"Banner {self.id}"

