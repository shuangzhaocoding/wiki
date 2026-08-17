# 用户角色管理 API 文档

## 概述

用户角色管理模块提供了角色管理和用户角色分配的功能。每个角色拥有不同的权限（用JSON表示），一个用户可以有多个角色。

## 数据模型

### 角色表 (Role)

- `id`: 角色ID
- `name`: 角色名称（唯一）
- `code`: 角色代码（唯一标识）
- `description`: 角色描述
- `permissions`: 角色权限（JSON格式），如：`{"create_user": {"desc": "创建用户", "auth": true}, "edit_user": {"desc": "编辑用户", "auth": false}}`
- `status`: 状态（0-禁用，1-启用）
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 用户-角色关联表 (UserRole)

- `id`: 关联ID
- `user_id`: 用户ID
- `role_id`: 角色ID
- `status`: 状态（0-已移除，1-有效）
- `assigned_by`: 分配人ID
- `assigned_at`: 分配时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 角色管理 API

### 1. 创建角色

**接口**: `POST /api/roles`

**请求体**:
```json
{
  "name": "管理员",
  "code": "admin",
  "description": "系统管理员角色",
  "permissions": {
    "create_user": {
      "desc": "创建用户",
      "auth": true
    },
    "edit_user": {
      "desc": "编辑用户",
      "auth": true
    },
    "delete_user": {
      "desc": "删除用户",
      "auth": true
    },
    "view_user": {
      "desc": "查看用户",
      "auth": true
    }
  },
  "status": 1
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "管理员",
    "code": "admin",
    "description": "系统管理员角色",
    "permissions": {
      "create_user": {
        "desc": "创建用户",
        "auth": true
      },
      "edit_user": {
        "desc": "编辑用户",
        "auth": true
      },
      "delete_user": {
        "desc": "删除用户",
        "auth": true
      },
      "view_user": {
        "desc": "查看用户",
        "auth": true
      }
    },
    "status": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:00:00"
  },
  "message": "角色创建成功"
}
```

### 2. 获取角色列表

**接口**: `GET /api/roles`

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10，最大100）
- `status`: 状态筛选（0-禁用，1-启用，不传则返回所有角色包括已禁用的）
- `keyword`: 关键词搜索（角色名称或代码）

**响应**:
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "管理员",
        "code": "admin",
        "description": "系统管理员角色",
        "permissions": {
          "create_user": {"desc": "创建用户", "auth": true},
          "edit_user": {"desc": "编辑用户", "auth": true},
          "delete_user": {"desc": "删除用户", "auth": true}
        },
        "status": 1,
        "created_at": "2026-02-05T10:00:00",
        "updated_at": "2026-02-05T10:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  },
  "message": "获取成功"
}
```

### 3. 获取角色详情

**接口**: `GET /api/roles/{role_id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "管理员",
    "code": "admin",
    "description": "系统管理员角色",
    "permissions": {
      "create_user": {"desc": "创建用户", "auth": true},
      "edit_user": {"desc": "编辑用户", "auth": true},
      "delete_user": {"desc": "删除用户", "auth": true}
    },
    "status": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:00:00"
  },
  "message": "获取成功"
}
```

### 4. 更新角色

**接口**: `PUT /api/roles/{role_id}`

**请求体**（所有字段可选）:
```json
{
  "name": "超级管理员",
  "description": "更新后的描述",
  "permissions": {
    "create_user": {
      "desc": "创建用户",
      "auth": true
    },
    "edit_user": {
      "desc": "编辑用户",
      "auth": true
    },
    "delete_user": {
      "desc": "删除用户",
      "auth": true
    },
    "view_user": {
      "desc": "查看用户",
      "auth": true
    },
    "manage_users": {
      "desc": "管理用户",
      "auth": true
    }
  },
  "status": 1
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "超级管理员",
    "code": "admin",
    "description": "更新后的描述",
    "permissions": {
      "create": true,
      "edit": true,
      "delete": true,
      "view": true,
      "manage_users": true
    },
    "status": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:30:00"
  },
  "message": "角色更新成功"
}
```

### 5. 更新角色权限

**接口**: `PUT /api/roles/{role_id}/permissions`

**请求体**:
```json
{
  "permissions": {
    "create_user": {
      "desc": "创建用户",
      "auth": true
    },
    "edit_user": {
      "desc": "编辑用户",
      "auth": true
    },
    "delete_user": {
      "desc": "删除用户",
      "auth": false
    },
    "view_user": {
      "desc": "查看用户",
      "auth": true
    }
  }
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "管理员",
    "code": "admin",
    "permissions": {
      "create": true,
      "edit": true,
      "delete": false,
      "view": true
    },
    "status": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:35:00"
  },
  "message": "角色权限更新成功"
}
```

### 6. 启用角色

**接口**: `PUT /api/roles/{role_id}/enable`

**说明**: 重新启用已禁用的角色（将状态设为1）。

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "管理员",
    "code": "admin",
    "description": "系统管理员角色",
    "permissions": {
      "create_user": {"desc": "创建用户", "auth": true},
      "edit_user": {"desc": "编辑用户", "auth": true}
    },
    "status": 1,
    "created_at": "2026-02-05T10:00:00",
    "updated_at": "2026-02-05T10:40:00"
  },
  "message": "角色已启用"
}
```

### 7. 删除角色

**接口**: `DELETE /api/roles/{role_id}`

**说明**: 软删除，将角色状态设为0。如果角色正在被用户使用，则无法删除。删除后可以通过启用接口重新启用。

**响应**:
```json
{
  "code": 200,
  "data": null,
  "message": "角色删除成功"
}
```

## 用户角色管理 API

### 1. 为用户分配角色

**接口**: `POST /api/user-roles/assign`

**说明**: 为用户分配一个或多个角色，会替换用户现有的所有角色。

**请求体**:
```json
{
  "user_id": 1,
  "role_ids": [1, 2, 3]
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 1,
    "username": "admin",
    "roles": [
      {
        "id": 1,
        "name": "管理员",
        "code": "admin",
        "permissions": {
          "create_user": {"desc": "创建用户", "auth": true},
          "edit_user": {"desc": "编辑用户", "auth": true},
          "delete_user": {"desc": "删除用户", "auth": true}
        },
        "assigned_at": "2026-02-05T10:00:00"
      },
      {
        "id": 2,
        "name": "编辑者",
        "code": "editor",
        "permissions": {
          "create_user": {"desc": "创建用户", "auth": true},
          "edit_user": {"desc": "编辑用户", "auth": true},
          "delete_user": {"desc": "删除用户", "auth": false}
        },
        "assigned_at": "2026-02-05T10:00:00"
      }
    ]
  },
  "message": "角色分配成功"
}
```

### 2. 为用户添加单个角色

**接口**: `POST /api/user-roles/{user_id}/roles/{role_id}`

**说明**: 为用户添加一个角色（不替换现有角色）。

**响应**:
```json
{
  "code": 200,
  "data": null,
  "message": "角色添加成功"
}
```

### 3. 移除用户的单个角色

**接口**: `DELETE /api/user-roles/{user_id}/roles/{role_id}`

**响应**:
```json
{
  "code": 200,
  "data": null,
  "message": "角色移除成功"
}
```

### 4. 获取用户的角色列表

**接口**: `GET /api/user-roles/{user_id}/roles`

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 1,
    "username": "admin",
    "roles": [
      {
        "id": 1,
        "name": "管理员",
        "code": "admin",
        "permissions": {
          "create_user": {"desc": "创建用户", "auth": true},
          "edit_user": {"desc": "编辑用户", "auth": true},
          "delete_user": {"desc": "删除用户", "auth": true}
        },
        "assigned_at": "2026-02-05T10:00:00",
        "assigned_by": 1
      }
    ]
  },
  "message": "获取成功"
}
```

### 5. 禁用用户

**接口**: `PUT /api/user-roles/{user_id}/disable`

**说明**: 将用户状态设为0（禁用）。不能禁用自己。

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 1,
    "username": "admin",
    "status": 0
  },
  "message": "用户已禁用"
}
```

### 6. 启用用户

**接口**: `PUT /api/user-roles/{user_id}/enable`

**说明**: 将用户状态设为1（启用）。

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 1,
    "username": "admin",
    "status": 1
  },
  "message": "用户已启用"
}
```

### 7. 获取用户及其角色信息

**接口**: `GET /api/user-roles/users/{user_id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "user_id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "nickname": "管理员",
    "avatar": null,
    "user_status": 1,
    "roles": [
      {
        "id": 1,
        "name": "管理员",
        "code": "admin",
        "permissions": {
          "create_user": {"desc": "创建用户", "auth": true},
          "edit_user": {"desc": "编辑用户", "auth": true},
          "delete_user": {"desc": "删除用户", "auth": true}
        },
        "assigned_at": "2026-02-05T10:00:00"
      }
    ]
  },
  "message": "获取成功"
}
```

### 8. 获取用户角色列表（分页）

**接口**: `GET /api/user-roles`

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10，最大100）
- `status`: 用户状态筛选（0-禁用，1-启用）
- `keyword`: 关键词搜索（用户名、邮箱、昵称）

**响应**:
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "user_id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "nickname": "管理员",
        "avatar": null,
        "user_status": 1,
        "roles": [
          {
            "id": 1,
            "name": "管理员",
            "code": "admin",
            "permissions": {
              "create_user": {"desc": "创建用户", "auth": true},
              "edit_user": {"desc": "编辑用户", "auth": true},
              "delete_user": {"desc": "删除用户", "auth": true}
            },
            "assigned_at": "2026-02-05T10:00:00"
          }
        ]
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  },
  "message": "获取成功"
}
```

## 权限说明

所有接口都需要用户登录认证（Bearer Token）。

## 注意事项

1. **角色权限格式**: 权限使用JSON格式存储，每个权限项包含 `desc`（权限描述）和 `auth`（是否有权限）字段，如：
   - `{"create_user": {"desc": "创建用户", "auth": true}, "edit_user": {"desc": "编辑用户", "auth": false}}`
   - `{"create_article": {"desc": "创建文章", "auth": true}, "edit_article": {"desc": "编辑文章", "auth": true}, "delete_article": {"desc": "删除文章", "auth": false}}`

2. **用户角色**: 一个用户可以有多个角色，角色信息以JSON列表形式返回。

3. **软删除**: 
   - 删除角色时，如果角色正在被用户使用，则无法删除
   - 移除用户角色时，采用软删除方式（status=0），保留历史记录

4. **事务处理**: 所有涉及数据库更新的操作都使用了事务，确保数据一致性。

5. **状态管理**:
   - 角色状态：0-禁用，1-启用
   - 用户状态：0-禁用，1-启用
   - 用户角色关联状态：0-已移除，1-有效

## 使用示例

### 创建角色并分配权限

```bash
# 1. 创建管理员角色
curl -X POST "http://localhost:8000/api/roles" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "管理员",
    "code": "admin",
    "permissions": {
      "create_user": {
        "desc": "创建用户",
        "auth": true
      },
      "edit_user": {
        "desc": "编辑用户",
        "auth": true
      },
      "delete_user": {
        "desc": "删除用户",
        "auth": true
      },
      "view_user": {
        "desc": "查看用户",
        "auth": true
      },
      "manage_users": {
        "desc": "管理用户",
        "auth": true
      }
    }
  }'

# 2. 为用户分配角色
curl -X POST "http://localhost:8000/api/user-roles/assign" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "role_ids": [1]
  }'

# 3. 查看用户的角色
curl -X GET "http://localhost:8000/api/user-roles/1/roles" \
  -H "Authorization: Bearer <token>"
```
