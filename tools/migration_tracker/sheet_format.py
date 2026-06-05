"""Sheets batchUpdate request builders for one-time coverage-sheet styling."""

from __future__ import annotations

_HEADER_BG = {"red": 0.17, "green": 0.24, "blue": 0.31}
_HEADER_FG = {"red": 1, "green": 1, "blue": 1}
_BAND_BG = {"red": 0.96, "green": 0.97, "blue": 0.98}

# Wider columns for the two long free-text fields (0-indexed: Scope=3, Stability=7).
_WIDE_COLS = {3: 420, 7: 360}
_DEFAULT_WIDTH = 150


def build_init_requests(sheet_id: int, column_count: int, row_count: int) -> list[dict]:
    """Return the formatting requests applied once after the sheet is populated."""
    return [
        _freeze_header(sheet_id),
        _header_style(sheet_id, column_count),
        _wrap_and_top_align(sheet_id, column_count, row_count),
        *_column_widths(sheet_id, column_count),
        _banding(sheet_id, column_count, row_count),
        _auto_filter(sheet_id, column_count, row_count),
    ]


def _freeze_header(sheet_id: int) -> dict:
    return {
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }
    }


def _header_style(sheet_id: int, cols: int) -> dict:
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1,
                      "startColumnIndex": 0, "endColumnIndex": cols},
            "cell": {"userEnteredFormat": {
                "backgroundColor": _HEADER_BG,
                "textFormat": {"foregroundColor": _HEADER_FG, "bold": True},
                "verticalAlignment": "MIDDLE",
                "wrapStrategy": "WRAP",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,verticalAlignment,wrapStrategy)",
        }
    }


def _wrap_and_top_align(sheet_id: int, cols: int, rows: int) -> dict:
    return {
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": rows,
                      "startColumnIndex": 0, "endColumnIndex": cols},
            "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
        }
    }


def _column_widths(sheet_id: int, cols: int) -> list[dict]:
    requests = []
    for index in range(cols):
        width = _WIDE_COLS.get(index, _DEFAULT_WIDTH)
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                          "startIndex": index, "endIndex": index + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })
    return requests


def _banding(sheet_id: int, cols: int, rows: int) -> dict:
    return {
        "addBanding": {
            "bandedRange": {
                "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": rows,
                          "startColumnIndex": 0, "endColumnIndex": cols},
                "rowProperties": {
                    "firstBandColor": {"red": 1, "green": 1, "blue": 1},
                    "secondBandColor": _BAND_BG,
                },
            }
        }
    }


def _auto_filter(sheet_id: int, cols: int, rows: int) -> dict:
    return {
        "setBasicFilter": {
            "filter": {"range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": rows,
                                  "startColumnIndex": 0, "endColumnIndex": cols}}
        }
    }
