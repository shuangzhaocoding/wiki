# 小林 coding 爬虫（xiaolincoding_spider）

从 [小林 coding](https://www.xiaolincoding.com) VuePress 站点抓取系列教程文章，将正文转为 Markdown / Quill Delta，并可上传图片到华为 OBS、写入 wiki 数据库。

## 功能概览

1. 解析系列入口页左侧 sidebar，仅保留 `.html` 文章链接  
2. 逐篇抓取正文 HTML，用 [markdownify](https://github.com/matthewwithanm/python-markdownify) 转为 Markdown  
3. 可选：下载正文中的图片并上传 OBS，替换 Markdown / Delta 中的图片 URL  
4. Markdown 经 [mistune](https://github.com/lepture/mistune) AST **直接**转为 Quill Delta（与站内 FluentEditor 格式一致）  
5. 可选：将结果写入 MySQL `articles` 表（按 sidebar 分组创建目录节点）

## 目录结构

```
scripts/spider/xiaolincoding/
├── xiaolincoding_spider.py   # 主入口：抓取、转换、入库
├── markdown_quill.py         # 图片迁移、HTML→Delta、Markdown→Delta 封装
├── md_ast_quill.py           # Markdown AST → Quill Delta
├── db_import.py              # Tortoise ORM 写入 articles
└── README.md
```

## 环境准备

在 **wiki-backend 项目根目录** 下执行（脚本会加载 `app`、`config` 等模块）。

```bash
cd /path/to/wiki-backend
pip install -r requirements.txt
```

爬虫相关依赖（已写入 `requirements.txt`）：

| 包 | 用途 |
|----|------|
| `markdownify` | 正文 HTML → Markdown |
| `mistune` | Markdown → Quill Delta（≥3.0.2） |
| `lxml` | `--delta-from-html` 时 HTML → Delta |
| `quill-delta` | Delta 序列化（可选校验） |

还需配置可用的 **华为 OBS**（图片上传）及 **MySQL**（`--import-db` 时）。

## 快速开始

### 1. 仅查看目录

```bash
python scripts/spider/xiaolincoding/xiaolincoding_spider.py \
  --url https://www.xiaolincoding.com/redis/ \
  --toc-only
```

### 2. 抓取少量文章并输出 JSON

```bash
python scripts/spider/xiaolincoding/xiaolincoding_spider.py \
  --url https://www.xiaolincoding.com/redis/ \
  --limit 5 \
  -o redis_import.json
```

### 3. 抓取并入库（常用）

```bash
python scripts/spider/xiaolincoding/xiaolincoding_spider.py \
  --url https://www.xiaolincoding.com/redis/ \
  --import-db \
  --knowledge-base-id 35 \
  --author-id 15 \
  --parent-id 762 \
  --image-obs-prefix wiki/xiaolincoding/redis \
  -o redis_import.json
```

- `--knowledge-base-id` / `--author-id`：入库必填  
- `--parent-id`：各 **section 目录** 挂在此父目录下（须为同知识库下的**目录节点**）；不传则 section 挂在知识库根  
- `--image-obs-prefix`：OBS object key 前缀，实际路径为 `{前缀}/{uuid}.{ext}`  
- `-o`：同时保存完整 JSON 备份（含 `markdown`、`quill_delta` 等）

### 4. 不上传图片，仅做 Quill 转换

```bash
python scripts/spider/xiaolincoding/xiaolincoding_spider.py \
  --limit 2 \
  --no-migrate-images \
  -o out.json
```

## 命令行参数

### 抓取与输出

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--url` | `https://www.xiaolincoding.com/redis/` | 系列入口页 URL |
| `--toc-only` | - | 只打印 sidebar 目录，不抓取正文 |
| `--limit` | 无限制 | 最多抓取篇数 |
| `--delay` | `0.5` | 每篇抓取间隔（秒） |
| `-o`, `--output` | - | 结果写入 JSON 文件；未指定且未 `--import-db` 时打印到 stdout |

### 图片与 Quill

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--image-cache-dir` | `.cache/xiaolincoding_images` | 图片下载临时目录 |
| `--image-obs-prefix` | `wiki/import/xiaolincoding` | OBS 上传路径前缀 |
| `--no-migrate-images` | - | 不上传 OBS，不替换图片 URL |
| `--delta-from-html` | - | 用正文 HTML 转 Delta；**默认**为 Markdown 直转 Delta |

### 数据库入库

| 参数 | 说明 |
|------|------|
| `--import-db` | 写入 MySQL `articles` 表 |
| `--knowledge-base-id` | 目标知识库 ID（入库必填） |
| `--author-id` | 文章作者用户 ID（入库必填） |
| `--parent-id` | section 目录的父节点 ID（可选，须为目录 `node_type=2`） |
| `--force-update` | 不跳过同标题文章（仍会新建，默认同标题跳过） |
| `--db-host` / `--db-port` / `--db-user` / `--db-password` / `--db-name` | 数据库连接（有脚本内默认值，可按环境覆盖） |

## 处理流程

```
入口页 URL
    ↓
解析 sidebar（仅 .html）
    ↓
逐篇请求正文 HTML
    ↓
markdownify → Markdown
    ↓
[可选] 图片下载 → OBS（--image-obs-prefix）→ 替换 URL
    ↓
mistune AST → Quill Delta（或 --delta-from-html 走 HTML 解析）
    ↓
[可选] 写入 MySQL（按 section 建目录 + 文章）
```

## 入库结构

在指定 `--parent-id` 时（推荐）：

```
父目录（--parent-id）
├── section A（目录节点，title = sidebar 分组名）
│   ├── 文章 1
│   └── 文章 2
└── section B
    └── 文章 3
```

未指定 `--parent-id` 时，section 目录挂在知识库根（`parent_id = NULL`）。

- 文章 `content` 字段为 Quill Delta 的 JSON 字符串（`{"ops":[...]}`）  
- 同 section、同标题且 `status > 0` 的文章默认**跳过**（除非 `--force-update`）  
- 若父节点下已有同名 section 目录，会复用该目录，避免重复创建

## 输出 JSON 说明

`articles` 数组中每篇大致包含：

| 字段 | 说明 |
|------|------|
| `section` | sidebar 分组标题 |
| `title` | 正文标题 |
| `sidebar_title` | 目录中的标题 |
| `url` | 源站 URL |
| `markdown` | 转换后的 Markdown（含 OBS 图片 URL） |
| `content_html` | 原始正文 HTML 片段 |
| `quill_delta` | Quill Delta 对象 |
| `content` | `quill_delta` 的 JSON 字符串（与入库字段一致） |
| `image_map` | 源图片 URL → OBS URL 映射（启用图片迁移时） |
| `error` | 抓取或处理失败时的错误信息 |

使用 `--import-db` 时，额外包含 `import_results` 数组。

## 常见问题

**Q: 列表、表格、代码块在编辑器里显示异常？**  
A: 默认请使用 Markdown 直转 Delta；若与源站 HTML 差异大，可尝试 `--delta-from-html`。表格使用 `quill-table-up` 格式。

**Q: 图片仍是源站链接？**  
A: 不要加 `--no-migrate-images`，并确认 OBS 配置可用。

**Q: 入库报父节点错误？**  
A: `--parent-id` 必须是该知识库下已存在的**目录**节点（`node_type = 2`）。

**Q: mistune 相关报错？**  
A: 需安装 `mistune>=3.0.2`（不要用系统自带的 mistune 2.x）。

## 查看帮助

```bash
python scripts/spider/xiaolincoding/xiaolincoding_spider.py --help
```
