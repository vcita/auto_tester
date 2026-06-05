"""
Thin Google Sheets + Drive client backed by a service account.

Uses google-auth (service account) + an AuthorizedSession (requests), so there is
no interactive browser consent: any teammate with the shared key file can run it.
The target spreadsheet must be shared with the service-account email as Editor.
"""

from __future__ import annotations

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"


class SheetsClient:
    """Minimal Sheets/Drive wrapper scoped to a single spreadsheet."""

    def __init__(self, key_path: str, spreadsheet_id: str):
        creds = service_account.Credentials.from_service_account_file(
            key_path, scopes=SCOPES
        )
        self._service_account_email = creds.service_account_email
        self._session = AuthorizedSession(creds)
        self._id = spreadsheet_id

    @property
    def service_account_email(self) -> str:
        return self._service_account_email

    def _check(self, resp, action: str):
        if not resp.ok:
            raise RuntimeError(f"Sheets API {action} failed ({resp.status_code}): {resp.text}")
        return resp.json() if resp.text else {}

    def sheet_id(self, tab: str) -> int:
        """Resolve a tab name to its numeric sheetId (creates nothing)."""
        resp = self._session.get(f"{SHEETS_API}/{self._id}", params={"fields": "sheets.properties"})
        data = self._check(resp, "get metadata")
        for sheet in data.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("title") == tab:
                return props["sheetId"]
        raise RuntimeError(f"Tab '{tab}' not found in spreadsheet {self._id}")

    def ensure_tab(self, tab: str) -> int:
        """Return the sheetId for `tab`, renaming the first sheet to it if absent."""
        resp = self._session.get(f"{SHEETS_API}/{self._id}", params={"fields": "sheets.properties"})
        data = self._check(resp, "get metadata")
        sheets = [s.get("properties", {}) for s in data.get("sheets", [])]
        for props in sheets:
            if props.get("title") == tab:
                return props["sheetId"]
        first = sheets[0]
        self.batch_update([
            {"updateSheetProperties": {
                "properties": {"sheetId": first["sheetId"], "title": tab},
                "fields": "title",
            }}
        ])
        return first["sheetId"]

    def get_values(self, a1_range: str) -> list[list[str]]:
        resp = self._session.get(f"{SHEETS_API}/{self._id}/values/{a1_range}")
        return self._check(resp, "get values").get("values", [])

    def update_values(self, a1_range: str, values: list[list]):
        resp = self._session.put(
            f"{SHEETS_API}/{self._id}/values/{a1_range}",
            params={"valueInputOption": "USER_ENTERED"},
            json={"values": values},
        )
        return self._check(resp, "update values")

    def append_values(self, a1_range: str, values: list[list]):
        resp = self._session.post(
            f"{SHEETS_API}/{self._id}/values/{a1_range}:append",
            params={"valueInputOption": "USER_ENTERED", "insertDataOption": "INSERT_ROWS"},
            json={"values": values},
        )
        return self._check(resp, "append values")

    def batch_update(self, requests: list[dict]):
        resp = self._session.post(
            f"{SHEETS_API}/{self._id}:batchUpdate", json={"requests": requests}
        )
        return self._check(resp, "batchUpdate")

    def share_anyone_reader(self):
        """Best-effort: make the sheet viewable by anyone with the link."""
        resp = self._session.post(
            f"{DRIVE_API}/{self._id}/permissions",
            params={"sendNotificationEmail": "false"},
            json={"type": "anyone", "role": "reader"},
        )
        if not resp.ok:
            return f"share skipped ({resp.status_code}): {resp.text[:200]}"
        return "shared: anyone with link can view"
