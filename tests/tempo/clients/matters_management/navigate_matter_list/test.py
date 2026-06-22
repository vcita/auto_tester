# Navigate Matter From List
# Migrated from automation-js matters-management.feature (VCITA2-13952)
# Legacy: client.js clickOnMatter + getMatterTitleName ("title shows")
# Source: tests/clients/matters_management/navigate_matter_list/script.md

from playwright.sync_api import Page

from tests.tempo.clients.matters_management.matters_helpers import (
    click_matter_in_list,
    expect_title,
    open_matter_page,
)


def test_navigate_matter_list(page: Page, context: dict) -> None:
    """From the shared contact's matter list, click matters and confirm the title follows.

    After nesting, the contact's page lists the whole family (contact client, matter_1,
    matter_2, matter client). Click the nested 'matter client' row, then the
    'contact client' row, asserting the title heading follows each selection (legacy
    `user clicks on matter <x> from matter list` / `title shows <x>`).
    """
    contact_client_id = context["contact_client_id"]
    contact_client_name = context["contact_client_name"]    # "contact client"
    matter_client_name = context["matter_client_name"]      # "matter client" (nested)

    print(f"  Step 1: Opening the shared contact's matter page ({contact_client_id})...")
    inner, _ = open_matter_page(page, context, contact_client_id)

    print(f"  Step 2: Clicking {matter_client_name!r} from the matter list...")
    click_matter_in_list(inner, matter_client_name)
    expect_title(inner, matter_client_name)

    print(f"  Step 3: Clicking {contact_client_name!r} from the matter list...")
    click_matter_in_list(inner, contact_client_name)
    expect_title(inner, contact_client_name)

    print(f"  [OK] matter title follows list selection; shows {contact_client_name}")
