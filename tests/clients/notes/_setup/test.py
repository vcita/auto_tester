from playwright.sync_api import Page

from tests.clients.notes.note_helpers import create_note_matter_via_api, navigate_to_matter_page


def setup_notes(page: Page, context: dict) -> None:
    """Create a matter so notes can be stress-tested as an independent subcategory."""
    matter = create_note_matter_via_api(context)
    print(f"  [OK] Created note matter via API: {matter['name']} ({matter['id']})")

    navigate_to_matter_page(page, context, matter["id"])
    if matter["id"] not in page.url:
        raise AssertionError(f"Expected to be on matter {matter['id']}, got {page.url}")
