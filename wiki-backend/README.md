# 知识库系统后端API

基于 Python 3.11 + FastAPI + Tortoise ORM 的知识库系统后端接口。

## 技术栈

- **Python**: 3.11
- **Web框架**: FastAPI
- **ORM**: Tortoise ORM
- **数据库**: MySQL 8.0+
- **缓存**: Redis
- **认证**: JWT Token

## 项目结构

```
wiki-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── team_space.py
│   │   ├── knowledge_base.py
│   │   ├── article.py
│   │   ├── permission.py
│   │   └── comment.py
│   ├── schemas/             # Pydantic模型
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── user.py
│   ├── routers/             # 路由
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证
│   │   ├── users.py         # 用户
│   │   ├── team_spaces.py   # 团队空间
│   │   ├── knowledge_bases.py # 知识库
│   │   ├── articles.py      # 文章
│   │   ├── permissions.py   # 权限
│   │   └── comments.py      # 评论
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py      # 安全相关
│   │   └── dependencies.py  # 依赖项
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── permissions.py   # 权限检查
├── config.py                # 配置文件
├── requirements.txt         # 依赖包
├── run.py                   # 启动文件
└── README.md
```

## 安装与运行

### 1. 创建虚拟环境（推荐）

**Windows:**
```bash
# 方法1: 使用脚本（推荐）
setup_venv.bat

# 方法2: 手动创建
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
# 或使用脚本
activate_venv.bat
```

**Linux/Mac:**
```bash
# 方法1: 使用脚本（推荐）
chmod +x setup_venv.sh
bash setup_venv.sh

# 方法2: 手动创建
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate
# 或使用脚本
source activate_venv.sh
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

修改 `config.py` 中的数据库配置（已配置为提供的数据库信息）。

### 3. 运行应用

```bash
python run.py
```

或使用 uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

### 用户相关
- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/me` - 更新当前用户信息
- `GET /api/users/{user_id}` - 获取用户信息

### 团队空间
- `POST /api/team-spaces` - 创建团队空间
- `GET /api/team-spaces` - 获取团队空间列表
- `GET /api/team-spaces/{id}` - 获取团队空间详情
- `PUT /api/team-spaces/{id}` - 更新团队空间
- `DELETE /api/team-spaces/{id}` - 删除团队空间
- `POST /api/team-spaces/{id}/members` - 添加成员
- `DELETE /api/team-spaces/{id}/members/{user_id}` - 移除成员

### 知识库
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases` - 获取知识库列表
- `GET /api/knowledge-bases/{id}` - 获取知识库详情
- `PUT /api/knowledge-bases/{id}` - 更新知识库
- `DELETE /api/knowledge-bases/{id}` - 删除知识库

### 文章
- `POST /api/articles` - 创建文章
- `GET /api/articles` - 获取文章列表
- `GET /api/articles/{id}` - 获取文章详情
- `PUT /api/articles/{id}` - 更新文章
- `DELETE /api/articles/{id}` - 删除文章
- `POST /api/articles/{id}/publish` - 发布文章
- `GET /api/articles/{id}/versions` - 获取版本历史
- `POST /api/articles/{id}/rollback/{version_id}` - 回滚文章

### 权限
- `POST /api/permissions` - 授予权限
- `GET /api/permissions` - 获取权限列表
- `DELETE /api/permissions/{id}` - 撤销权限
- `GET /api/permissions/check` - 检查权限

### 评论
- `POST /api/comments` - 创建评论
- `GET /api/comments/article/{article_id}` - 获取文章评论
- `PUT /api/comments/{id}` - 更新评论
- `DELETE /api/comments/{id}` - 删除评论

## 认证方式

使用 JWT Token 认证，在请求头中添加：

```
Authorization: Bearer <token>
```

## 权限说明

- **resource_type**: 1-团队空间，2-知识库，3-文章
- **permission_type**: 1-只读，2-可编辑，3-管理员
- **visibility**: 1-个人可见，2-团队成员可见，3-公开可见

## 注意事项

1. 首次运行会自动创建数据库表结构
2. 生产环境需要修改 `config.py` 中的 `SECRET_KEY`
3. 建议使用环境变量管理敏感配置信息
