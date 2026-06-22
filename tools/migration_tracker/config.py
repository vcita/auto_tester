"""
Configuration for the migration coverage tracker tool.

All secrets and IDs come from the environment (loaded from `~/dev/.env` and the
repo `.env`), so any teammate can run the tracker without editing code:

- MIGRATION_TRACKER_GSA_KEY   path to the Google service-account JSON key
                              (default: ~/dev/.gsa-migration-tracker.json)
- MIGRATION_TRACKER_SHEET_ID  spreadsheet id of the coverage sheet
- MIGRATION_TRACKER_SHEET_TAB worksheet/tab name (default: Coverage)
- CONFLUENCE_BASE_URL         wiki base (default: https://myvcita.atlassian.net/wiki)
- CONFLUENCE_PAGE_ID          tracker page id (default: 4690444289)
- CONFLUENCE_EMAIL            Atlassian account email (for direct REST publish)
- CONFLUENCE_API_TOKEN        Atlassian API token (for direct REST publish)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load ~/dev/.env first, then the repo .env (repo overrides shared defaults).
load_dotenv(Path.home() / "dev" / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

DEFAULT_GSA_KEY = str(Path.home() / "dev" / ".gsa-migration-tracker.json")

GSA_KEY_PATH = os.getenv("MIGRATION_TRACKER_GSA_KEY", DEFAULT_GSA_KEY)
SHEET_ID = os.getenv("MIGRATION_TRACKER_SHEET_ID", "")
SHEET_TAB = os.getenv("MIGRATION_TRACKER_SHEET_TAB", "Coverage")

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL", "https://myvcita.atlassian.net/wiki")
CONFLUENCE_PAGE_ID = os.getenv("CONFLUENCE_PAGE_ID", "4690444289")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL", "")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN", "")

# Sheet schema. Jira and PR render as HYPERLINK formulas; everything else is text.
COLUMNS = [
    "Feature file",
    "autotester path",
    "Status",
    "Scope covered",
    "Original result",
    "Migrated result",
    "Duration improvement",
    "Stability",
    "Jira",
    "PR",
]

# Progress-bar color thresholds (fraction migrated) for the Confluence page.
BAR_RED = "#ff5630"
BAR_AMBER = "#ffab00"
BAR_GREEN = "#36b37e"
BAR_EMPTY = "#dfe1e6"
BAR_CELLS = 20


def require(name: str, value: str) -> str:
    """Return value or raise a clear error naming the missing env var."""
    if not value:
        raise SystemExit(
            f"Missing required configuration: {name}. "
            f"Set it in ~/dev/.env or the repo .env (see tools/migration_tracker/README.md)."
        )
    return value
