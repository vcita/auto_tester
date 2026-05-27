from playwright.sync_api import Page

from tests.clients.notes.note_helpers import delete_note_matter_via_api


def teardown_notes(page: Page, context: dict) -> None:
    """Clean up only the matter created by isolated notes setup."""
    delete_note_matter_via_api(context)
