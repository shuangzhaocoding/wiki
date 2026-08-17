# 系统权限管理 API 文档

## 概述

系统权限管理模块用于定义和管理系统中的所有权限项。每个权限包含权限名称、代码、描述、分类等信息，可以启用或禁用。

## 数据模型

### 系统权限表 (SystemPermission)

- `id`: 权限ID
- `name`: 权限名称（唯一）
- `code`: 权限代码（唯一标识），如：`create_user`, `edit_user`
- `description`: 权限描述
- `category`: 权限分类，如：`user`, `article`, `team_space`
- `status`: 状态（0-禁用，1-启用）
- `sort_order`: 排序顺序
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 系统权限管理 API

### 1. 创建权限

**接口**: `POST /api/system-permissions`

**请求体**:
```json
{
  "name": "创建用户",
  "code": "create_user",
  "description": "允许创建新用户",
  "category": "user",
  "status": 1,
  "sort_order": 1
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "创建用户",
    "code": "create_user",
    "description": "允许创建新用户",
    "category": "user",
    "status": 1,
    "sort_order": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:00:00"
  },
  "message": "权限创建成功"
}
```

### 2. 获取权限列表

**接口**: `GET /api/system-permissions`

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10，最大100）
- `status`: 状态筛选（0-禁用，1-启用，不传则返回所有）
- `category`: 权限分类筛选
- `keyword`: 关键词搜索（权限名称、代码或描述）

**响应**:
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "创建用户",
        "code": "create_user",
        "description": "允许创建新用户",
        "category": "user",
        "status": 1,
        "sort_order": 1,
        "created_at": "2026-02-05T10:00:00",
        "updated_at": "2026-02-05T10:00:00"
      },
      {
        "id": 2,
        "name": "编辑用户",
        "code": "edit_user",
        "description": "允许编辑用户信息",
        "category": "user",
        "status": 1,
        "sort_order": 2,
        "created_at": "2026-02-05T10:00:00",
        "updated_at": "2026-02-05T10:00:00"
      }
    ],
    "total": 2,
    "page": 1,
    "page_size": 10
  },
  "message": "获取成功"
}
```

### 3. 获取权限详情

**接口**: `GET /api/system-permissions/{permission_id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "创建用户",
    "code": "create_user",
    "description": "允许创建新用户",
    "category": "user",
    "status": 1,
    "sort_order": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:00:00"
  },
  "message": "获取成功"
}
```

### 4. 更新权限

**接口**: `PUT /api/system-permissions/{permission_id}`

**请求体**（所有字段可选）:
```json
{
  "name": "创建用户（更新）",
  "description": "更新后的权限描述",
  "category": "user",
  "status": 1,
  "sort_order": 1
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "创建用户（更新）",
    "code": "create_user",
    "description": "更新后的权限描述",
    "category": "user",
    "status": 1,
    "sort_order": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:30:00"
  },
  "message": "权限更新成功"
}
```

### 5. 启用权限

**接口**: `PUT /api/system-permissions/{permission_id}/enable`

**说明**: 重新启用已禁用的权限（将状态设为1）。

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "创建用户",
    "code": "create_user",
    "description": "允许创建新用户",
    "category": "user",
    "status": 1,
    "sort_order": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:40:00"
  },
  "message": "权限已启用"
}
```

### 6. 禁用权限

**接口**: `PUT /api/system-permissions/{permission_id}/disable`

**说明**: 禁用权限（将状态设为0）。

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "创建用户",
    "code": "create_user",
    "description": "允许创建新用户",
    "category": "user",
    "status": 0,
    "sort_order": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:45:00"
  },
  "message": "权限已禁用"
}
```

### 7. 删除权限

**接口**: `DELETE /api/system-permissions/{permission_id}`

**说明**: 软删除，将权限状态设为0。删除后可以通过启用接口重新启用。

**响应**:
```json
{
  "code": 200,
  "data": null,
  "message": "权限删除成功"
}
```

### 8. 获取权限分类列表

**接口**: `GET /api/system-permissions/categories/list`

**说明**: 获取系统中所有权限分类。

**响应**:
```json
{
  "code": 200,
  "data": {
    "categories": [
      "article",
      "team_space",
      "user"
    ]
  },
  "message": "获取成功"
}
```

## 使用示例

### 创建权限并管理

```bash
# 1. 创建用户相关权限
curl -X POST "http://localhost:8000/api/system-permissions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "创建用户",
    "code": "create_user",
    "description": "允许创建新用户",
    "category": "user",
    "status": 1,
    "sort_order": 1
  }'

curl -X POST "http://localhost:8000/api/system-permissions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "编辑用户",
    "code": "edit_user",
    "description": "允许编辑用户信息",
    "category": "user",
    "status": 1,
    "sort_order": 2
  }'

curl -X POST "http://localhost:8000/api/system-permissions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "删除用户",
    "code": "delete_user",
    "description": "允许删除用户",
    "category": "user",
    "status": 1,
    "sort_order": 3
  }'

# 2. 创建文章相关权限
curl -X POST "http://localhost:8000/api/system-permissions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "创建文章",
    "code": "create_article",
    "description": "允许创建文章",
    "category": "article",
    "status": 1,
    "sort_order": 1
  }'

# 3. 获取所有权限
curl -X GET "http://localhost:8000/api/system-permissions?page=1&page_size=10" \
  -H "Authorization: Bearer <token>"

# 4. 按分类获取权限
curl -X GET "http://localhost:8000/api/system-permissions?category=user&page=1&page_size=10" \
  -H "Authorization: Bearer <token>"

# 5. 获取启用的权限
curl -X GET "http://localhost:8000/api/system-permissions?status=1&page=1&page_size=10" \
  -H "Authorization: Bearer <token>"

# 6. 搜索权限
curl -X GET "http://localhost:8000/api/system-permissions?keyword=用户&page=1&page_size=10" \
  -H "Authorization: Bearer <token>"

# 7. 禁用权限
curl -X PUT "http://localhost:8000/api/system-permissions/1/disable" \
  -H "Authorization: Bearer <token>"

# 8. 启用权限
curl -X PUT "http://localhost:8000/api/system-permissions/1/enable" \
  -H "Authorization: Bearer <token>"

# 9. 获取权限分类列表
curl -X GET "http://localhost:8000/api/system-permissions/categories/list" \
  -H "Authorization: Bearer <token>"
```

## 权限说明

所有接口都需要用户登录认证（Bearer Token）。

## 注意事项

1. **权限代码唯一性**: 权限代码（code）必须唯一，用于在系统中标识权限。

2. **权限分类**: 建议使用分类来组织权限，便于管理和展示，如：
   - `user`: 用户相关权限
   - `article`: 文章相关权限
   - `team_space`: 团队空间相关权限
   - `knowledge_base`: 知识库相关权限

3. **软删除**: 删除权限时采用软删除方式（status=0），保留历史记录，可以通过启用接口重新启用。

4. **事务处理**: 所有涉及数据库更新的操作都使用了事务，确保数据一致性。

5. **状态管理**:
   - 权限状态：0-禁用，1-启用
   - 删除权限实际上是将状态设为0，可以通过启用接口恢复

6. **排序**: 权限列表按 `sort_order` 和创建时间排序，可以通过更新 `sort_order` 来控制显示顺序。

## 权限分类建议

### 用户管理 (user)
- `create_user`: 创建用户
- `edit_user`: 编辑用户
- `delete_user`: 删除用户
- `view_user`: 查看用户
- `manage_user_roles`: 管理用户角色

### 文章管理 (article)
- `create_article`: 创建文章
- `edit_article`: 编辑文章
- `delete_article`: 删除文章
- `view_article`: 查看文章
- `publish_article`: 发布文章

### 团队空间管理 (team_space)
- `create_team_space`: 创建团队空间
- `edit_team_space`: 编辑团队空间
- `delete_team_space`: 删除团队空间
- `manage_team_members`: 管理团队成员

### 知识库管理 (knowledge_base)
- `create_knowledge_base`: 创建知识库
- `edit_knowledge_base`: 编辑知识库
- `delete_knowledge_base`: 删除知识库
- `manage_knowledge_base_members`: 管理知识库成员
