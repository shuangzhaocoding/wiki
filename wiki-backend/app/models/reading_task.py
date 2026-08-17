"""
阅读任务模型：主从表设计
- ReadingTaskBatch: 签读任务批次（主表）
- ReadingTask: 任务明细（从表）
"""
from tortoise.models import Model
from tortoise import fields


class ReadingTaskBatch(Model):
    """签读任务批次表（主表）"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField(
        "models.Article",
        related_name="reading_task_batches",
        description="关联文章",
    )
    knowledge_base = fields.ForeignKeyField(
        "models.KnowledgeBase",
        related_name="reading_task_batches",
        description="所属知识库",
    )
    required_seconds = fields.IntField(description="要求最少阅读时长（秒）")
    deadline = fields.DatetimeField(
        null=True,
        description="阅读截止时间（可为空）",
    )
    role_ids = fields.JSONField(
        default=list,
        description="下发的角色ID列表，如 [1, 2, 3]",
    )
    status = fields.IntField(
        default=0,
        description="批次状态：0-有效，1-已取消",
    )
    created_by = fields.ForeignKeyField(
        "models.User",
        related_name="created_reading_task_batches",
        description="创建人（下发人）",
    )
    updated_by = fields.ForeignKeyField(
        "models.User",
        related_name="updated_reading_task_batches",
        null=True,
        description="最后更新人",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "reading_task_batches"
        table_description = "签读任务批次表"

    def __str__(self) -> str:
        return f"Batch {self.id} - article {self.article_id}"


class ReadingTask(Model):
    """阅读任务明细表（从表）"""
    id = fields.BigIntField(pk=True)
    batch = fields.ForeignKeyField(
        "models.ReadingTaskBatch",
        related_name="tasks",
        description="所属批次",
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="reading_tasks",
        description="被要求阅读的用户",
    )
    role = fields.ForeignKeyField(
        "models.Role",
        related_name="reading_tasks",
        null=True,
        description="来源角色（通过哪个角色下发）",
    )
    status = fields.IntField(
        default=0,
        description="状态：0-未开始，1-进行中，2-已完成，3-已过期，4-已取消",
    )
    started_at = fields.DatetimeField(
        null=True,
        description="开始阅读时间",
    )
    finished_at = fields.DatetimeField(
        null=True,
        description="完成阅读时间",
    )
    actual_seconds = fields.IntField(
        null=True,
        description="实际累计阅读时长（秒）",
    )
    updated_by = fields.ForeignKeyField(
        "models.User",
        related_name="updated_reading_tasks",
        null=True,
        description="最后更新人",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "reading_tasks"
        table_description = "阅读任务明细表"
        indexes = (("batch", "user", "status"),)

    def __str__(self) -> str:
        return f"Task {self.id} - batch {self.batch_id} -> user {self.user_id}"
