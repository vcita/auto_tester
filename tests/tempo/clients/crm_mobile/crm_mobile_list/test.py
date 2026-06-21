# Auto-generated from script.md
# Last updated: 2026-06-20
# Source: tests/tempo/clients/crm_mobile/crm_mobile_list/script.md
# DO NOT EDIT MANUALLY - This file is regenerated from script.md
#
# CRM mobile list (migrated from automation-js crm-mobile.feature, @mobile_web).
# On a mobile-emulated device, close the welcome modal, then verify the CRM client list
# counter / search / empty-state with 10 API-seeded clients.

from playwright.sync_api import Page

from tests.tempo.clients.crm_mobile.crm_mobile_helpers import (
    assert_clients_counter,
    assert_empty_state,
    close_crm_mobile_welcome_modal,
    open_clients_list,
    search_in_tab,
    select_tab,
    set_mobile_viewport,
)

NEW_INQUIRIES = "New inquiries"
ALL_TAB = "All"


def test_crm_mobile_list(page: Page, context: dict) -> None:
    """On a mobile-emulated device, close the welcome modal, then verify the CRM client
    list counter / search / empty-state with 10 API-seeded clients."""
    # Step 1: Emulate a mobile device so the CRM mobile layout mounts
    print("  Step 1: Enable mobile emulation")
    set_mobile_viewport(page)

    # Step 2: Open the CRM clients list
    print("  Step 2: Open the CRM clients list")
    open_clients_list(page)

    # Step 3: Close the CRM mobile welcome modal
    print("  Step 3: Close the CRM mobile welcome modal")
    close_crm_mobile_welcome_modal(page)

    # Step 4: Select "New inquiries" then "All" (tab switch gives the seeker time
    # to index the freshly API-seeded clients)
    print("  Step 4: Select 'New inquiries' then 'All' tab")
    select_tab(page, NEW_INQUIRIES)
    select_tab(page, ALL_TAB)

    # Step 5: Counter shows 10 clients
    print("  Step 5: Counter shows 10 CLIENTS")
    assert_clients_counter(page, "10 CLIENTS")

    # Step 6: Search "first7" in the All tab -> the "first7 last7" row
    print("  Step 6: Search 'first7' in the All tab -> 'first7 last7'")
    search_in_tab(page, ALL_TAB, "first7", ["first7 last7"])

    # Step 7: Counter shows 1 client
    print("  Step 7: Counter shows 1 CLIENTS")
    assert_clients_counter(page, "1 CLIENTS")

    # Step 8: Select "New inquiries" tab
    print("  Step 8: Select 'New inquiries' tab")
    select_tab(page, NEW_INQUIRIES)

    # Step 9: CRM table shows its empty state
    print("  Step 9: CRM table shows empty state")
    assert_empty_state(page)

    # Step 10: Counter shows 0 clients
    print("  Step 10: Counter shows 0 CLIENTS")
    assert_clients_counter(page, "0 CLIENTS")
