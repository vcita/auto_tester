"""Setup for the Generate PDFs subcategories.

Mirrors the legacy generate_pdfs.feature Background, which is API-only (no UI login):
create the shared client used by all three PDF scenarios. The isolated account's
api_token / pivot_uid are already injected into context by the runner, so no browser
login is needed for these purely API-driven document checks.
"""

import time

from playwright.sync_api import Page

from tests.account_api import create_client

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"


def setup_generate_pdfs(page: Page, context: dict) -> None:
    print("  Setup Step 1: Create shared client 'first last' via API")
    stamp = int(time.time() * 1000)
    email = f"test+{stamp}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["pdf_client"] = client
    context["pdf_client_id"] = client["id"]
    context["pdf_client_email"] = email

    print(f"  [OK] generate_pdfs setup complete - client '{client['full_name']}' ready")
