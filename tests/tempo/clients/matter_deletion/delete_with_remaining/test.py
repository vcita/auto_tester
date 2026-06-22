# Delete Matter From A Contact With Other Matters Remaining
# Migrated from automation-js/features/steps/matter-deletion.feature (VCITA2-13990)
# Legacy: clients.js "user deletes matter" + client.js deleteMatter + newClients getClientsFromTable
# Source: tests/clients/matter_deletion/delete_with_remaining/script.md

from playwright.sync_api import Page

from tests.tempo.clients.crm_filters.crm_filters_helpers import (
    add_text_filter,
    assert_filtered_clients,
    clear_all_filters,
    open_clients_list,
)
from tests.tempo.clients.matter_deletion.matter_deletion_helpers import delete_matter
from tests.tempo.clients.matters_management.matters_helpers import (
    add_matter_from_pane,
    open_matter_page,
)

ADDED_MATTER = "matter"
EMAIL_FILTER_OPTION = "item-fields_filter.email"


def _email_filter(page: Page, email: str) -> None:
    open_clients_list(page)
    clear_all_filters(page)
    add_text_filter(page, EMAIL_FILTER_OPTION, email)


def test_delete_with_remaining(page: Page, context: dict) -> None:
    """Delete a nested matter, confirm the contact's remaining matter still surfaces in
    the CRM Email filter, then delete that last matter and confirm the contact is gone."""
    contact_id = context["contact_id"]
    contact_email = context["contact_email"]
    contact_name = context["contact_name"]

    print(f"  Step 1: Add matter {ADDED_MATTER!r} under the contact from the pane")
    inner, outer = open_matter_page(page, context, contact_id)
    add_matter_from_pane(page, inner, outer, ADDED_MATTER)

    print(f"  Step 2: Delete matter {ADDED_MATTER!r}")
    delete_matter(page, context, contact_id, ADDED_MATTER)

    print("  Step 3: Email filter -> only the remaining default matter shows")
    _email_filter(page, contact_email)
    assert_filtered_clients(page, [contact_name])

    print(f"  Step 4: Delete the last remaining matter {contact_name!r}")
    delete_matter(page, context, contact_id, contact_name)

    print("  Step 5: Email filter -> no clients remain")
    _email_filter(page, contact_email)
    assert_filtered_clients(page, [])
