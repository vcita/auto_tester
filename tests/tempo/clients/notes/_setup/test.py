from playwright.sync_api import Page

from tests.tempo.clients.notes.note_helpers import create_note_matter_via_api, navigate_to_matter_page


def setup_notes(page: Page, context: dict) -> None:
    """Open an existing full-category matter, or create one for isolated notes runs."""
    matter_id = context.get("created_matter_id")
    if matter_id:
        print(f"  [>] Reusing existing matter for notes: {matter_id}")
        navigate_to_matter_page(page, context, matter_id)
        if matter_id not in page.url:
            raise AssertionError(f"Expected to be on matter {matter_id}, got {page.url}")
        return

    matter = create_note_matter_via_api(context)
    context["notes_setup_matter_id"] = matter["id"]
    context["notes_setup_matter_name"] = matter["name"]
    context["notes_setup_matter_email"] = matter["email"]
    print(f"  [OK] Created isolated note matter via API: {matter['name']} ({matter['id']})")

    navigate_to_matter_page(page, context, matter["id"])
    if matter["id"] not in page.url:
        raise AssertionError(f"Expected to be on matter {matter['id']}, got {page.url}")
