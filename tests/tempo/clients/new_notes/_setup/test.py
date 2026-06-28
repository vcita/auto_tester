"""Setup for the new_notes (POV) subcategory.

`rollout.clients.new_notes` is a per-business feature flag the Angular/Vue SPA
reads at app-load time. It MUST be enabled BEFORE login — enabling it mid-session
(after the app has loaded) leaves the legacy notes dialog in place. This runs on an
isolated account so enabling the flag here does not affect the legacy notes tests
under clients/notes (which require it OFF).

Steps: enable the flag (before login) -> log in -> create a client matter via API ->
navigate to the matter page so the note flow starts on the matter detail page.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import enable_features
from tests.tempo.clients.notes.note_helpers import (
    create_note_matter_via_api,
    navigate_to_matter_page,
)


def setup_new_notes(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    # Per-business flag — enable BEFORE the SPA loads (i.e. before login).
    print("  Setup Step 1: Enable rollout.clients.new_notes (before login)")
    enable_features(context, "rollout.clients.new_notes")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Create client matter via API")
    matter = create_note_matter_via_api(context)
    print(f"  [OK] Created matter {matter['name']} ({matter['id']})")

    print("  Setup Step 4: Navigate to the matter page")
    navigate_to_matter_page(page, context, matter["id"])
    if matter["id"] not in page.url:
        raise AssertionError(f"Expected to be on matter {matter['id']}, got {page.url}")
