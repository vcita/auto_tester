# Add Matter From Contact Pane
# Migrated from automation-js matters-management.feature (VCITA2-13952)
# Legacy: client.js createMatterFromContactPane + getMattersNameList + getContact
# Source: tests/clients/matters_management/add_from_pane/script.md

from playwright.sync_api import Page

from tests.clients.matters_management.matters_helpers import (
    add_matter_from_pane,
    assert_matter_under_contact,
    open_matter_page,
)

MATTER_NAME = "matter_1"


def test_add_from_pane(page: Page, context: dict) -> None:
    """Add matter_1 under the contact via the contact-pane Add-matter action."""
    contact_id = context["contact_client_id"]
    contact_email = context["contact_client_email"]

    print(f"  Step 1: Opening contact matter page ({contact_id})...")
    inner, outer = open_matter_page(page, context, contact_id)

    print(f"  Step 2: Adding matter {MATTER_NAME!r} from the contact pane...")
    add_matter_from_pane(page, inner, outer, MATTER_NAME)

    print(f"  Step 3: Verifying {MATTER_NAME!r} exists under the contact...")
    assert_matter_under_contact(page, context, contact_id, MATTER_NAME, contact_email)
