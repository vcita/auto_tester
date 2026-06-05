"""
Update the Confluence tracker page in place.

The page is a rich dashboard (Summary, progress bars, Scope Counting Rules,
Update Instructions, Status Definitions). Only the dynamic parts are refreshed —
the two progress bars + captions and the Summary metric rows — and the big
per-feature coverage table is replaced once by a link to the Google Sheet. Every
other section is preserved verbatim.

Published as ADF (atlas_doc_format): the storage/HTML importer silently strips
table-cell background colors and status lozenges, so ADF is the only format that
keeps the colored bars.
"""

from __future__ import annotations

import json

import requests

from . import adf, config

CAPTION_FF = "Candidate feature files migrated"
CAPTION_SC = "Candidate scenario definitions migrated"
COVERAGE_HEADING = "Migration Coverage"


def fetch_current() -> tuple[dict, int, str]:
    """Return (adf_doc, version_number, title) for the tracker page."""
    auth = (config.require("CONFLUENCE_EMAIL", config.CONFLUENCE_EMAIL),
            config.require("CONFLUENCE_API_TOKEN", config.CONFLUENCE_API_TOKEN))
    base = config.CONFLUENCE_BASE_URL.rstrip("/")
    resp = requests.get(
        f"{base}/api/v2/pages/{config.CONFLUENCE_PAGE_ID}",
        params={"body-format": "atlas_doc_format"}, auth=auth, timeout=30,
    )
    resp.raise_for_status()
    page = resp.json()
    doc = json.loads(page["body"]["atlas_doc_format"]["value"])
    return doc, page["version"]["number"], page["title"]


def refresh(doc: dict, sheet_url: str, totals: dict, summary_updates: dict) -> dict:
    """Apply in-place edits to the ADF doc and return it."""
    content = [n for n in doc.get("content", []) if not adf.is_coverage_table(n)]
    _refresh_bars(content, totals)
    _ensure_sheet_link(content, sheet_url)
    for node in content:
        if adf.is_summary_table(node):
            adf.update_summary_rows(node, summary_updates)
    doc["content"] = content
    return doc


def _refresh_bars(content: list, totals: dict) -> None:
    pairs = [
        (CAPTION_FF, totals["feature_files_migrated"], totals["feature_files_total"]),
        (CAPTION_SC, totals["scenarios_migrated"], totals["scenarios_total"]),
    ]
    for label, migrated, total in pairs:
        index = _find_caption(content, label)
        if index is None:
            continue
        content[index] = adf.caption_paragraph(label, migrated, total)
        bar = adf.bar_table(migrated, total)
        if index + 1 < len(content) and content[index + 1].get("type") == "table":
            content[index + 1] = bar
        else:
            content.insert(index + 1, bar)


def _ensure_sheet_link(content: list, sheet_url: str) -> None:
    heading = _find_heading(content, COVERAGE_HEADING)
    link_para = adf.sheet_link_paragraph(sheet_url)
    if heading is None:
        return
    nxt = heading + 1
    if nxt < len(content) and adf.has_link(content[nxt]):
        content[nxt] = link_para
    else:
        content.insert(nxt, link_para)


def _find_caption(content: list, prefix: str) -> int | None:
    for i, node in enumerate(content):
        if node.get("type") == "paragraph" and adf.text_of(node).startswith(prefix):
            return i
    return None


def _find_heading(content: list, text: str) -> int | None:
    for i, node in enumerate(content):
        if node.get("type") == "heading" and adf.text_of(node).strip() == text:
            return i
    return None


def publish(doc: dict, version: int, title: str) -> dict:
    auth = (config.CONFLUENCE_EMAIL, config.CONFLUENCE_API_TOKEN)
    base = config.CONFLUENCE_BASE_URL.rstrip("/")
    resp = requests.put(
        f"{base}/api/v2/pages/{config.CONFLUENCE_PAGE_ID}",
        auth=auth, timeout=30,
        json={
            "id": config.CONFLUENCE_PAGE_ID,
            "status": "current",
            "title": title,
            "body": {"representation": "atlas_doc_format", "value": json.dumps(doc)},
            "version": {"number": version + 1, "message": "Migration tracker auto-update"},
        },
    )
    resp.raise_for_status()
    return {"version": version + 1, "url": f"{base}/pages/{config.CONFLUENCE_PAGE_ID}"}
