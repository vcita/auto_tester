"""
ADF (Atlassian Document Format) helpers for editing the Confluence tracker page
in place. We update only the dynamic nodes — the progress bars, their captions,
the Summary metric rows, and the coverage-table → Google Sheet link — and leave
every other section (Scope Counting Rules, Update Instructions, Status
Definitions) untouched.
"""

from __future__ import annotations

from . import config


def text_of(node) -> str:
    """Concatenate all text content under a node."""
    out: list[str] = []

    def walk(n):
        if isinstance(n, dict):
            if n.get("type") == "text":
                out.append(n.get("text", ""))
            for child in n.get("content", []) or []:
                walk(child)
        elif isinstance(n, list):
            for child in n:
                walk(child)

    walk(node)
    return "".join(out)


def _text(value: str, marks: list | None = None) -> dict:
    node = {"type": "text", "text": value}
    if marks:
        node["marks"] = marks
    return node


def link_node(value: str, url: str) -> dict:
    return _text(value, [{"type": "link", "attrs": {"href": url}}])


def _bar_color(fraction: float) -> str:
    if fraction < 0.25:
        return config.BAR_RED
    if fraction <= 0.66:
        return config.BAR_AMBER
    return config.BAR_GREEN


def _pct(migrated: int, total: int) -> str:
    return f"{(migrated / total * 100) if total else 0:.1f}%"


def bar_table(migrated: int, total: int) -> dict:
    fraction = migrated / total if total else 0.0
    filled = round(fraction * config.BAR_CELLS)
    color = _bar_color(fraction)
    cells = []
    for i in range(config.BAR_CELLS):
        bg = color if i < filled else config.BAR_EMPTY
        cells.append({
            "type": "tableCell",
            "attrs": {"background": bg},
            "content": [{"type": "paragraph", "content": []}],
        })
    return {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
        "content": [{"type": "tableRow", "content": cells}],
    }


def caption_paragraph(label: str, migrated: int, total: int) -> dict:
    return {"type": "paragraph", "content": [
        _text(f"{label}: ", [{"type": "strong"}]),
        _text(f"{migrated} / {total}", [{"type": "code"}]),
        _text(f"  ({_pct(migrated, total)})"),
    ]}


def sheet_link_paragraph(sheet_url: str) -> dict:
    return {"type": "paragraph", "content": [
        _text("The full per-feature coverage table (scope, runtime comparison, "
              "stability, Jira, PR) now lives in this "),
        link_node("Google Sheet", sheet_url),
        _text(". It is updated by the "),
        _text("tools/migration_tracker", [{"type": "code"}]),
        _text(" tool — do not edit it by hand."),
    ]}


def is_coverage_table(node: dict) -> bool:
    if node.get("type") != "table":
        return False
    rows = node.get("content", [])
    if not rows:
        return False
    return text_of(rows[0]).startswith("Feature file")


def is_summary_table(node: dict) -> bool:
    if node.get("type") != "table":
        return False
    rows = node.get("content", [])
    return bool(rows) and text_of(rows[0]).startswith("Metric")


def has_link(node: dict) -> bool:
    return node.get("type") == "paragraph" and any(
        m.get("type") == "link"
        for child in node.get("content", []) or []
        for m in child.get("marks", []) or []
    )


def set_cell_text(cell: dict, value: str) -> None:
    cell["content"] = [{"type": "paragraph", "content": [_text(value)]}]


def update_summary_rows(table: dict, updates: dict[str, str]) -> None:
    """Set the value cell for each Summary row whose label is in `updates`."""
    for row in table.get("content", []):
        cells = row.get("content", [])
        if len(cells) < 2:
            continue
        label = text_of(cells[0]).strip()
        if label in updates:
            set_cell_text(cells[1], updates[label])
