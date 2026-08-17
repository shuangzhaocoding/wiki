"""
Markdown / HTML → Quill Delta。

流程：Markdown --(markdown 库)--> HTML --(lxml 解析)--> Delta ops

说明：`quill-delta` 的 `delta.html.render` 仅支持 Delta → HTML，不支持反向；
此处 HTML → Delta 为自定义解析，输出格式与站内 Quill 编辑器一致。
"""
from __future__ import annotations

import asyncio
import json
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import markdown
from lxml import html as lxml_html

IMAGE_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
IMAGE_URL_RE = re.compile(
    r"https?://[^\s\)\"']+\.(?:png|jpe?g|gif|webp|bmp|svg)(?:\?[^\s\"']*)?",
    re.I,
)

_BLOCK_TAGS = frozenset(
    {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "pre", "blockquote", "div"}
)
_INLINE_CONTAINER = frozenset({"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "a", "td", "th"})

# 与 wiki 前端 quill-table-up 模块 blot 名一致
BLOT_TABLE_COL = "table-up-col"
BLOT_TABLE_CELL_INNER = "table-up-cell-inner"
_MERGED_CELL = object()

_CODE_LANG_RE = re.compile(r"language-([\w+#.-]+)", re.I)
_CUSTOM_BLOCK_RE = re.compile(r"\bcustom-block\b", re.I)


def extract_markdown_image_urls(markdown: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for _alt, url in IMAGE_MD_RE.findall(markdown):
        u = url.strip()
        if u and u not in seen:
            seen.add(u)
            urls.append(u)
    for u in IMAGE_URL_RE.findall(markdown):
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def download_image(url: str, dest: Path, user_agent: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Referer": "https://www.xiaolincoding.com/",
        },
    )
    with urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def _guess_ext(url: str, file_path: Path) -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}:
        return ext
    guessed = mimetypes.guess_extension(
        mimetypes.guess_type(str(file_path))[0] or "image/png"
    )
    return guessed or ".png"


async def migrate_markdown_images(
    markdown: str,
    *,
    upload_fn: Callable[[str, str], Any],
    cache_dir: Path,
    user_agent: str,
) -> tuple[str, dict[str, str]]:
    """下载 markdown 图片并上传 OBS，返回替换后的 markdown。"""
    mapping: dict[str, str] = {}
    for url in extract_markdown_image_urls(markdown):
        if url in mapping:
            continue
        tmp_path = cache_dir / uuid.uuid4().hex
        try:
            await asyncio.to_thread(download_image, url, tmp_path, user_agent)
            ext = _guess_ext(url, tmp_path)
            key = f"wiki/import/xiaolincoding/{uuid.uuid4().hex}{ext}"
            obs_url = await upload_fn(str(tmp_path), key)
            mapping[url] = obs_url
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    result = markdown
    for old, new in mapping.items():
        result = result.replace(old, new)
    return result, mapping


def markdown_to_html(md_text: str) -> str:
    """Markdown → HTML（Python-Markdown + 常用扩展）。"""
    if not (md_text or "").strip():
        return ""
    return markdown.markdown(
        md_text,
        extensions=["extra", "fenced_code", "tables", "nl2br", "sane_lists"],
        output_format="html5",
    )


def _merge_attrs(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    out.update(extra)
    return out


def _text_op(text: str, attrs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    if not text:
        return {"insert": ""}
    if attrs:
        return {"attributes": attrs, "insert": text}
    return {"insert": text}


def _append_text(ops: list[dict], text: str, attrs: Optional[dict[str, Any]] = None) -> None:
    if not text:
        return
    if ops and "attributes" not in ops[-1] and attrs is None:
        prev = ops[-1].get("insert")
        if isinstance(prev, str):
            ops[-1] = {"insert": prev + text}
            return
    ops.append(_text_op(text, attrs))


def _append_newline(ops: list[dict], attrs: Optional[dict[str, Any]] = None) -> None:
    if attrs:
        ops.append({"attributes": attrs, "insert": "\n"})
    else:
        ops.append({"insert": "\n"})


def _inline_ops(element: lxml_html.HtmlElement, attrs: Optional[dict[str, Any]] = None) -> list[dict]:
    """递归解析行内节点为 Quill ops。"""
    base = dict(attrs or {})
    out: list[dict] = []

    if element.text:
        _append_text(out, element.text, base or None)

    tag = (element.tag or "").lower()
    for child in element:
        child_tag = (child.tag or "").lower()
        child_attrs = dict(base)

        if child_tag in ("strong", "b"):
            child_attrs["bold"] = True
        elif child_tag in ("em", "i"):
            child_attrs["italic"] = True
        elif child_tag == "u":
            child_attrs["underline"] = True
        elif child_tag in ("s", "strike", "del"):
            child_attrs["strike"] = True
        elif child_tag == "code":
            child_attrs["font"] = "monospace"
        elif child_tag == "a":
            href = child.get("href")
            if href:
                child_attrs["link"] = href
        elif child_tag == "img":
            src = child.get("src") or child.get("data-src") or ""
            if src:
                out.append({"insert": {"image": src}})
                _append_newline(out)
            if child.tail:
                _append_text(out, child.tail, base or None)
            continue
        elif child_tag == "br":
            _append_newline(out)
            if child.tail:
                _append_text(out, child.tail, base or None)
            continue

        if child_tag in _INLINE_CONTAINER or child_tag in ("strong", "b", "em", "i", "u", "s", "code", "span"):
            out.extend(_inline_ops(child, child_attrs))
        else:
            # 嵌套块级（少见）按块处理
            _convert_element(child, out)

        if child.tail:
            _append_text(out, child.tail, base or None)

    return out


def _convert_heading(el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    level = int(el.tag[1]) if el.tag and el.tag.startswith("h") else 1
    ops.extend(_inline_ops(el))
    _append_newline(
        ops,
        {
            "text-indent": "0px",
            "line-height": "1.2",
            "header": {"value": level},
        },
    )


def _convert_paragraph(el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    inline = _inline_ops(el)
    if inline:
        ops.extend(inline)
    _append_newline(ops, {"text-indent": "0px"})


def _element_class(el: lxml_html.HtmlElement) -> str:
    return el.get("class") or ""


def _is_custom_block(el: lxml_html.HtmlElement) -> bool:
    return bool(_CUSTOM_BLOCK_RE.search(_element_class(el)))


def _find_pre_in_code_wrapper(el: lxml_html.HtmlElement) -> Optional[lxml_html.HtmlElement]:
    tag = (el.tag or "").lower()
    if tag == "pre":
        return el
    if tag == "div" and (
        _CODE_LANG_RE.search(_element_class(el)) or el.find("./pre") is not None
    ):
        pre = el.find("./pre") or el.find(".//pre")
        return pre if pre is not None else None
    return None


def _code_language(pre_el: lxml_html.HtmlElement, code_el: Optional[lxml_html.HtmlElement]) -> str:
    """与 Quill Syntax 模块一致：使用 language-xxx 或 plain。"""
    nodes: list[lxml_html.HtmlElement] = []
    if code_el is not None:
        nodes.append(code_el)
    nodes.append(pre_el)
    parent = pre_el.getparent()
    if parent is not None and (parent.tag or "").lower() == "div":
        nodes.append(parent)
    for node in nodes:
        m = _CODE_LANG_RE.search(_element_class(node))
        if m:
            return m.group(1).lower()
    return "plain"


def _code_block_newline_attrs(language: str) -> dict[str, Any]:
    return {"code-block": language}


def _convert_pre(el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    """fenced code → 每行一个 code-block op（FluentEditor Syntax / 行号样式）。"""
    code_el = el.find(".//code")
    text = (code_el.text_content() if code_el is not None else el.text_content()) or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    language = _code_language(el, code_el)

    if not text:
        _append_newline(ops, _code_block_newline_attrs(language))
        return

    for line in text.split("\n"):
        ops.append({"insert": line})
        _append_newline(ops, _code_block_newline_attrs(language))


def _apply_blockquote_to_ops(block_ops: list[dict]) -> list[dict]:
    """引用块内所有 op 均带 blockquote（与 Quill clipboard 行为一致）。"""
    if not block_ops:
        return block_ops
    out: list[dict] = []
    for op in block_ops:
        attrs = dict(op.get("attributes") or {})
        attrs["blockquote"] = True
        out.append({**op, "attributes": attrs})
    return out


def _convert_blockquote(el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    """blockquote / custom-block：按子块逐段转换，避免把标题等块级元素压成纯文本。"""
    bq = {"blockquote": True}
    has_child = False

    for child in el:
        has_child = True
        child_tag = (child.tag or "").lower()
        if child_tag == "p":
            inline = _inline_ops(child)
            if inline:
                ops.extend(_apply_blockquote_to_ops(inline))
            _append_newline(ops, bq)
        elif child_tag in ("ul", "ol"):
            start = len(ops)
            _convert_list(child, ops)
            for i in range(start, len(ops)):
                attrs = dict(ops[i].get("attributes") or {})
                attrs["blockquote"] = True
                ops[i]["attributes"] = attrs
        elif child_tag == "pre" or _find_pre_in_code_wrapper(child) is not None:
            pre = _find_pre_in_code_wrapper(child) or child
            _convert_pre(pre, ops)
        elif child_tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            inline = _inline_ops(child)
            if inline:
                ops.extend(_apply_blockquote_to_ops(inline))
            _append_newline(ops, bq)
        elif child_tag == "blockquote" or _is_custom_block(child):
            _convert_blockquote(child, ops)
        else:
            inline = _inline_ops(child)
            if inline:
                ops.extend(_apply_blockquote_to_ops(inline))
            _append_newline(ops, bq)
        if child.tail:
            _append_text(ops, child.tail, bq)

    if not has_child and (el.text or "").strip():
        _append_text(ops, el.text.strip(), bq)
        _append_newline(ops, bq)


def _table_random_id() -> str:
    return uuid.uuid4().hex[:12]


def _valid_span(raw: Optional[str], default: int = 1) -> int:
    try:
        n = int(raw) if raw else default
        return n if n > 0 else default
    except (TypeError, ValueError):
        return default


def _row_wrap_tag(tr: lxml_html.HtmlElement) -> str:
    node: Any = tr
    while node is not None:
        tag = (getattr(node, "tag", None) or "").lower()
        if tag in ("thead", "tbody", "tfoot"):
            return tag
        node = node.getparent()
    return "tbody"


def _table_column_count(table_el: lxml_html.HtmlElement) -> int:
    max_cols = 0
    for tr in table_el.findall(".//tr"):
        cols = 0
        for cell in tr:
            if (cell.tag or "").lower() in ("td", "th"):
                cols += _valid_span(cell.get("colspan"), 1)
        max_cols = max(max_cols, cols)
    return max_cols or 1


def _build_table_grid(
    table_el: lxml_html.HtmlElement,
) -> tuple[list[list[Any]], int]:
    """二维网格；锚点单元为 dict，被 rowspan/colspan 占用的格为 _MERGED_CELL。"""
    rows_els = table_el.findall(".//tr")
    if not rows_els:
        return [], 0

    ncols = _table_column_count(table_el)
    grid: list[list[Any]] = []

    for ri, tr in enumerate(rows_els):
        while len(grid) <= ri:
            grid.append([None] * ncols)
        col_idx = 0
        for cell in tr:
            tag = (cell.tag or "").lower()
            if tag not in ("td", "th"):
                continue
            while col_idx < ncols and grid[ri][col_idx] is not None:
                col_idx += 1
            if col_idx >= ncols:
                break
            rowspan = _valid_span(cell.get("rowspan"), 1)
            colspan = _valid_span(cell.get("colspan"), 1)
            grid[ri][col_idx] = {
                "element": cell,
                "tag": tag,
                "wrap_tag": _row_wrap_tag(tr),
                "rowspan": rowspan,
                "colspan": colspan,
            }
            for dr in range(rowspan):
                for dc in range(colspan):
                    if dr == 0 and dc == 0:
                        continue
                    r, c = ri + dr, col_idx + dc
                    while len(grid) <= r:
                        grid.append([None] * ncols)
                    grid[r][c] = _MERGED_CELL
            col_idx += colspan

    return grid, ncols


def _cell_content_ops(cell_el: lxml_html.HtmlElement) -> list[dict]:
    """单元格内联内容 → ops（不含 table-up-cell-inner，由 _finalize_cell_ops 补上）。"""
    out: list[dict] = []
    for child in cell_el:
        child_tag = (child.tag or "").lower()
        if child_tag == "pre" or _find_pre_in_code_wrapper(child) is not None:
            pre = _find_pre_in_code_wrapper(child) or child
            _convert_pre(pre, out)
        elif child_tag in ("ul", "ol"):
            _convert_list(child, out)
        elif child_tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "blockquote"):
            inline = _inline_ops(child)
            if inline:
                out.extend(inline)
            out.append({"insert": "\n"})
        else:
            out.extend(_inline_ops(child))
        if child.tail:
            _append_text(out, child.tail)
    if not out and (cell_el.text or "").strip():
        out.extend(_inline_ops(cell_el))
    return out


def _finalize_cell_ops(cell_ops: list[dict], cell_value: dict[str, Any]) -> list[dict]:
    """为单元格 ops 附加 table-up-cell-inner（与 quill-table-up 粘贴逻辑一致）。"""
    if not cell_ops:
        return [{"attributes": {BLOT_TABLE_CELL_INNER: cell_value}, "insert": "\n"}]

    result: list[dict] = []
    for op in cell_ops:
        attrs = dict(op.get("attributes") or {})
        attrs[BLOT_TABLE_CELL_INNER] = dict(cell_value)
        result.append({**op, "attributes": attrs})
    last_insert = result[-1].get("insert")
    if not isinstance(last_insert, str) or not last_insert.endswith("\n"):
        result.append({"attributes": {BLOT_TABLE_CELL_INNER: dict(cell_value)}, "insert": "\n"})
    return result


def _convert_table(table_el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    """HTML table → quill-table-up Delta ops。"""
    grid, ncols = _build_table_grid(table_el)
    if not grid or ncols <= 0:
        return

    table_id = _table_random_id()
    col_ids = [_table_random_id() for _ in range(ncols)]
    row_ids = [_table_random_id() for _ in range(len(grid))]
    col_width = 100.0 / ncols

    col_ops: list[dict] = [
        {
            "insert": {
                BLOT_TABLE_COL: {
                    "tableId": table_id,
                    "colId": col_id,
                    "width": col_width,
                    "full": True,
                }
            }
        }
        for col_id in col_ids
    ]

    body_ops: list[dict] = []
    for ri, row in enumerate(grid):
        row_id = row_ids[ri]
        for ci in range(ncols):
            cell_info = row[ci] if ci < len(row) else None
            if cell_info is None or cell_info is _MERGED_CELL:
                continue
            cell_value = {
                "tableId": table_id,
                "rowId": row_id,
                "colId": col_ids[ci],
                "rowspan": cell_info["rowspan"],
                "colspan": cell_info["colspan"],
                "tag": cell_info["tag"],
                "wrapTag": cell_info["wrap_tag"],
            }
            cell_ops = _cell_content_ops(cell_info["element"])
            body_ops.extend(_finalize_cell_ops(cell_ops, cell_value))

    ops.extend(col_ops)
    ops.extend(body_ops)


def _convert_list(el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    list_type = "ordered" if el.tag == "ol" else "bullet"
    for li in el.findall("./li"):
        li_ops = _inline_ops(li)
        if li_ops:
            for op in li_ops:
                if "attributes" in op:
                    op["attributes"] = _merge_attrs(op["attributes"], {"list": list_type})
                elif isinstance(op.get("insert"), str):
                    op = {"attributes": {"list": list_type}, "insert": op["insert"]}
                ops.append(op)
        else:
            ops.append({"attributes": {"list": list_type}, "insert": ""})
        _append_newline(ops, {"list": list_type})


def _convert_element(el: lxml_html.HtmlElement, ops: list[dict]) -> None:
    tag = (el.tag or "").lower()
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        _convert_heading(el, ops)
    elif tag == "p":
        _convert_paragraph(el, ops)
    elif tag == "pre":
        _convert_pre(el, ops)
    elif tag == "blockquote":
        _convert_blockquote(el, ops)
    elif tag == "div" and _is_custom_block(el):
        _convert_blockquote(el, ops)
    elif tag == "div" and _find_pre_in_code_wrapper(el) is not None:
        pre = _find_pre_in_code_wrapper(el)
        if pre is not None:
            _convert_pre(pre, ops)
    elif tag in ("ul", "ol"):
        _convert_list(el, ops)
    elif tag == "li":
        _convert_paragraph(el, ops)
    elif tag == "img":
        src = el.get("src") or el.get("data-src") or ""
        if src:
            ops.append({"insert": {"image": src}})
            _append_newline(ops)
    elif tag in ("article", "section"):
        for child in el:
            _convert_element(child, ops)
    elif tag == "div":
        for child in el:
            _convert_element(child, ops)
    elif tag == "table":
        _convert_table(el, ops)
    elif tag in ("thead", "tbody", "tfoot", "tr"):
        pass
    else:
        text = el.text_content()
        if text and text.strip():
            _append_text(ops, text.strip())
            _append_newline(ops)


def html_to_quill_delta(html_content: str) -> dict[str, Any]:
    """HTML 片段 → Quill Delta（{"ops": [...]}）。"""
    html_content = (html_content or "").strip()
    if not html_content:
        return {"ops": [{"insert": "\n"}]}

    root = lxml_html.fromstring(f'<div class="ql-html-root">{html_content}</div>')

    ops: list[dict] = []
    for child in root:
        _convert_element(child, ops)

    if not ops:
        ops.append({"insert": "\n"})
    elif ops[-1].get("insert") != "\n":
        ops.append({"insert": "\n"})

    return {"ops": ops}


def markdown_to_delta_via_html(md_text: str) -> dict[str, Any]:
    """
    Markdown → HTML → Quill Delta。

    与 `delta.html.render` 方向相反：render 仅用于 Delta → HTML 导出校验。
    """
    html_content = markdown_to_html(md_text)
    return html_to_quill_delta(html_content)


def markdown_to_quill_delta(md_text: str) -> dict[str, Any]:
    """对外统一入口：Markdown → Quill Delta。"""
    return markdown_to_delta_via_html(md_text)


def html_content_to_quill_delta(html_content: str) -> dict[str, Any]:
    """爬虫可直接用页面正文 HTML 转 Delta，跳过 Markdown 中间态。"""
    return html_to_quill_delta(html_content)


def quill_delta_to_json(delta: dict[str, Any]) -> str:
    return json.dumps(delta, ensure_ascii=False)


def delta_to_html(delta: dict[str, Any]) -> str:
    """可选：用 quill-delta 将 Delta 渲染回 HTML（校验/预览）。"""
    from delta import html as delta_html
    from delta.base import Delta

    return delta_html.render(Delta(delta.get("ops", [])))
