import time

from playwright.sync_api import Page

from tests.account_api import create_client
from tests.clients.crm_selection_logic.crm_selection_helpers import (
    assert_summary_text,
    open_clients_list,
    search_clients,
    select_all_pages,
    select_client_by_name,
    select_current_page,
    set_rows_per_page,
    sort_by_client_name,
)

NAMED_CLIENTS = 11  # first01..first11
TOTAL_CLIENTS = 12  # + "other other"


def test_selection_counts(page: Page, context: dict) -> None:
    """Verify CRM checkbox selection summary counts.

    Migrates automation-js `crm-selection-logic.feature` scenario
    `Check checkbox selection logic`.
    """
    token = str(int(time.time() * 1000))
    print(f"  Step 1: Creating {TOTAL_CLIENTS} clients via API...")
    for i in range(1, NAMED_CLIENTS + 1):
        create_client(context, f"first{i:02d}", f"last{i:02d}", f"test{i:02d}+{token}@vmeetme.com")
    create_client(context, "other", "other", f"test22+{token}@vmeetme.com")

    print("  Step 2: Opening clients list, setting 10 rows/page, sorting by client name...")
    open_clients_list(page)
    set_rows_per_page(page, "10")
    sort_by_client_name(page)

    print("  Step 3: Selecting single client, current page, all pages (full list)...")
    select_client_by_name(page, "first01 last01")
    assert_summary_text(page, "1 SELECTED OF 12 CLIENTS")
    select_current_page(page)
    assert_summary_text(page, "10 SELECTED OF 12 CLIENTS")
    select_all_pages(page)
    assert_summary_text(page, "12 SELECTED OF 12 CLIENTS")

    print("  Step 4: Searching 'first' (11 clients) and re-verifying selection counts...")
    search_clients(page, "first")
    # Wait for the search to settle and clear the prior selection before selecting
    # again, so select_client toggles a settled row (avoids the re-render race where
    # the stale "...SELECTED..." text is still present).
    assert_summary_text(page, "11 CLIENTS")
    select_client_by_name(page, "first01 last01")
    assert_summary_text(page, "1 SELECTED OF 11 CLIENTS")
    select_current_page(page)
    assert_summary_text(page, "10 SELECTED OF 11 CLIENTS")
    select_all_pages(page)
    assert_summary_text(page, "11 SELECTED OF 11 CLIENTS")

    print("  [OK] CRM selection summary counts verified for full and filtered lists")
