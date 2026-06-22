# Manage CRM Table Tabs
# Migrated from automation-js/features/steps/crm-tabs-management.feature
# Scenario: "Manage CRM table tabs" (VCITA2-13992)
# Source: tests/clients/crm_tabs_management/manage_crm_tabs/script.md

from playwright.sync_api import Page

from tests.tempo.clients.crm_tabs_management.crm_tabs_helpers import (
    assert_clients_counter,
    assert_empty_state,
    assert_tab_before,
    assert_tab_in_views_dropdown,
    drag_tab,
    search_in_tab,
)
from tests.tempo.clients.crm_views.crm_views_helpers import close_tab, open_clients_list, select_view

NEW_INQUIRIES = "New inquiries"
ALL_TAB = "All"
RECENTLY_ACTIVE = "Recently active"


def test_manage_crm_tabs(page: Page, context: dict) -> None:
    """Select the New inquiries tab (empty, 0 clients); switch to the Recently active view
    and search the self-client (1 client); drag New inquiries before All; close New
    inquiries and verify it returns to the views dropdown."""
    self_client_label = context["self_client_label"]
    open_clients_list(page)

    print("  Step 1: Select 'New inquiries' tab - empty state, 0 clients")
    select_view(page, NEW_INQUIRIES)
    assert_empty_state(page)
    assert_clients_counter(page, "0 CLIENTS")

    print("  Step 2: Select 'Recently active' view, search 'form_first' - 1 client")
    select_view(page, RECENTLY_ACTIVE)
    search_in_tab(page, RECENTLY_ACTIVE, "form_first", [self_client_label])
    assert_clients_counter(page, "1 CLIENTS")

    print("  Step 3: Drag 'New inquiries' to precede 'All'")
    drag_tab(page, NEW_INQUIRIES, ALL_TAB)
    assert_tab_before(page, NEW_INQUIRIES, ALL_TAB)

    print("  Step 4: Close 'New inquiries' tab - appears in views dropdown")
    close_tab(page, NEW_INQUIRIES)
    assert_tab_in_views_dropdown(page, NEW_INQUIRIES)
