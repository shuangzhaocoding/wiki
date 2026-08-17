"""
Markdown AST（mistune）→ Quill Delta ops。

不经过 HTML 字符串，输出格式与站内 FluentEditor / quill-table-up 一致。
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

import mistune
from mistune.plugins.table import table as table_plugin

BLOT_TABLE_COL = "table-up-col"
BLOT_TABLE_CELL_INNER = "table-up-cell-inner"
_MERGED_CELL = object()

_MD = mistune.create_markdown(
    renderer="ast",
    plugins=[table_plugin, "strikethrough"],
)


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


def _merge_attrs(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    out.update(extra)
    return out


def _table_random_id() -> str:
    return uuid.uuid4().hex[:12]


def _render_inlines(
    nodes: Optional[list[dict[str, Any]]],
    ops: list[dict],
    attrs: Optional[dict[str, Any]] = None,
) -> None:
    base = dict(attrs or {})
    for node in nodes or []:
        ntype = node.get("type")
        if ntype == "text":
            _append_text(ops, node.get("raw", ""), base or None)
        elif ntype in ("strong", "bold"):
            _render_inlines(node.get("children"), ops, _merge_attrs(base, {"bold": True}))
        elif ntype in ("emphasis", "em"):
            _render_inlines(node.get("children"), ops, _merge_attrs(base, {"italic": True}))
        elif ntype == "strikethrough":
            _render_inlines(node.get("children"), ops, _merge_attrs(base, {"strike": True}))
        elif ntype == "codespan":
            _append_text(ops, node.get("raw", ""), _merge_attrs(base, {"font": "monospace"}))
        elif ntype == "link":
            url = (node.get("attrs") or {}).get("url", "")
            _render_inlines(
                node.get("children"),
                ops,
                _merge_attrs(base, {"link": url}) if url else base,
            )
        elif ntype == "image":
            url = (node.get("attrs") or {}).get("url", "")
            if url:
                ops.append({"insert": {"image": url}})
                _append_newline(ops)
        elif ntype in ("linebreak", "softbreak"):
            _append_newline(ops, base or None)
        elif ntype == "inline_html":
            raw = (node.get("raw") or "").strip()
            if raw:
                _append_text(ops, raw, base or None)


def _apply_blockquote_to_ops(block_ops: list[dict]) -> list[dict]:
    if not block_ops:
        return block_ops
    out: list[dict] = []
    for op in block_ops:
        merged = dict(op.get("attributes") or {})
        merged["blockquote"] = True
        out.append({**op, "attributes": merged})
    return out


def _render_block_code(node: dict[str, Any], ops: list[dict]) -> None:
    info = (node.get("attrs") or {}).get("info") or ""
    language = (info.split()[0] if info else "") or "plain"
    text = (node.get("raw") or "").replace("\r\n", "\n").replace("\r", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    cb = {"code-block": language}
    if not text:
        _append_newline(ops, cb)
        return
    for line in text.split("\n"):
        ops.append({"insert": line})
        _append_newline(ops, cb)


def _render_heading(node: dict[str, Any], ops: list[dict]) -> None:
    level = int((node.get("attrs") or {}).get("level", 1))
    _render_inlines(node.get("children"), ops)
    _append_newline(
        ops,
        {
            "text-indent": "0px",
            "line-height": "1.2",
            "header": {"value": level},
        },
    )


def _render_paragraph(node: dict[str, Any], ops: list[dict]) -> None:
    _render_inlines(node.get("children"), ops)
    _append_newline(ops, {"text-indent": "0px"})


def _render_blockquote(node: dict[str, Any], ops: list[dict]) -> None:
    bq = {"blockquote": True}
    for child in node.get("children") or []:
        if child.get("type") == "paragraph":
            block: list[dict] = []
            _render_inlines(child.get("children"), block)
            if block:
                ops.extend(_apply_blockquote_to_ops(block))
            _append_newline(ops, bq)
        else:
            start = len(ops)
            _render_block(child, ops)
            for i in range(start, len(ops)):
                merged = dict(ops[i].get("attributes") or {})
                merged["blockquote"] = True
                ops[i]["attributes"] = merged


def _emit_list_item_line(li_ops: list[dict], list_type: str, ops: list[dict]) -> None:
    """单条列表项：正文 ops 均带 list，末尾换行也带 list（与 Quill 一致）。"""
    if not li_ops:
        ops.append({"attributes": {"list": list_type}, "insert": ""})
    else:
        for op in li_ops:
            insert = op.get("insert")
            if isinstance(insert, dict):
                ops.append(op)
                continue
            attrs = dict(op.get("attributes") or {})
            attrs["list"] = list_type
            ops.append({"attributes": attrs, "insert": insert if isinstance(insert, str) else ""})
    _append_newline(ops, {"list": list_type})


def _render_list_item_block(child: dict[str, Any], li_ops: list[dict]) -> None:
    ctype = child.get("type")
    if ctype in ("paragraph", "block_text"):
        # mistune 3：紧凑列表用 block_text，松散列表用 paragraph，正文均在 children 里
        _render_inlines(child.get("children"), li_ops)
    else:
        chunk: list[dict] = []
        _render_block(child, chunk)
        li_ops.extend(chunk)


def _render_list(node: dict[str, Any], ops: list[dict]) -> None:
    list_type = "ordered" if (node.get("attrs") or {}).get("ordered") else "bullet"
    for item in node.get("children") or []:
        if item.get("type") != "list_item":
            continue
        li_ops: list[dict] = []
        for child in item.get("children") or []:
            if child.get("type") == "list":
                if li_ops:
                    _emit_list_item_line(li_ops, list_type, ops)
                    li_ops = []
                _render_list(child, ops)
            else:
                _render_list_item_block(child, li_ops)
        _emit_list_item_line(li_ops, list_type, ops)


def _cell_inline_ops(inline_nodes: list[dict[str, Any]]) -> list[dict]:
    out: list[dict] = []
    _render_inlines(inline_nodes, out)
    return out


def _finalize_cell_ops(cell_ops: list[dict], cell_value: dict[str, Any]) -> list[dict]:
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


def _convert_table_ast(table_node: dict[str, Any], ops: list[dict]) -> None:
    rows: list[tuple[str, list[list[dict[str, Any]]]]] = []
    for section in table_node.get("children") or []:
        stype = section.get("type")
        if stype not in ("table_head", "table_body"):
            continue
        wrap = "thead" if stype == "table_head" else "tbody"
        for row in section.get("children") or []:
            if row.get("type") != "table_row":
                continue
            cells: list[list[dict[str, Any]]] = []
            for cell in row.get("children") or []:
                if cell.get("type") == "table_cell":
                    cells.append(cell.get("children") or [])
            if cells:
                rows.append((wrap, cells))

    if not rows:
        return

    ncols = max(len(cells) for _, cells in rows)
    table_id = _table_random_id()
    col_ids = [_table_random_id() for _ in range(ncols)]
    col_width = 100.0 / ncols

    ops.extend(
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
    )

    for ri, (wrap_tag, cells) in enumerate(rows):
        row_id = _table_random_id()
        for ci in range(ncols):
            inlines = cells[ci] if ci < len(cells) else []
            tag = "th" if wrap_tag == "thead" else "td"
            cell_value = {
                "tableId": table_id,
                "rowId": row_id,
                "colId": col_ids[ci],
                "rowspan": 1,
                "colspan": 1,
                "tag": tag,
                "wrapTag": wrap_tag,
            }
            cell_ops = _cell_inline_ops(inlines)
            ops.extend(_finalize_cell_ops(cell_ops, cell_value))


def _render_block(node: dict[str, Any], ops: list[dict]) -> None:
    ntype = node.get("type")
    if ntype == "heading":
        _render_heading(node, ops)
    elif ntype == "paragraph":
        _render_paragraph(node, ops)
    elif ntype == "block_code":
        _render_block_code(node, ops)
    elif ntype == "block_quote":
        _render_blockquote(node, ops)
    elif ntype == "list":
        _render_list(node, ops)
    elif ntype == "table":
        _convert_table_ast(node, ops)
    elif ntype == "thematic_break":
        _append_newline(ops)
    elif ntype == "block_html":
        raw = (node.get("raw") or "").strip()
        if raw:
            _append_text(ops, raw)
            _append_newline(ops)


def markdown_ast_to_quill_delta(md_text: str) -> dict[str, Any]:
    """Markdown 文本 → Quill Delta（mistune AST，不经 HTML）。"""
    if not (md_text or "").strip():
        return {"ops": [{"insert": "\n"}]}

    ast = _MD(md_text)
    ops: list[dict] = []
    for node in ast:
        _render_block(node, ops)

    if not ops:
        ops.append({"insert": "\n"})
    elif ops[-1].get("insert") != "\n":
        ops.append({"insert": "\n"})

    return {"ops": ops}
