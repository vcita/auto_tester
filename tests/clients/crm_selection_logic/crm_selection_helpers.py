"""CRM selection-count UI helpers for the crm_selection_logic migration (VCITA2-13862).

Covers the legacy crm-selection-logic.feature checkbox selection logic: the
rows-per-page footer control, client-name sort, current-page selection, and the CRM
summary line ("N SELECTED OF M CLIENTS").

Generic CRM navigation/selection primitives (open list, select client, select all
pages, search) are reused from the already-migrated, live-verified crm_bulk_actions
helpers to keep one source of truth.
"""

import re
import time

from playwright.sync_api import Page, expect

from tests.clients.crm_bulk_actions.crm_bulk_helpers import (  # noqa: F401  (re-exported for the test)
    UI_TIMEOUT,
    open_clients_list,
    search_clients,
    select_all_pages,
    wait_for_clients_table,
)

ROWS_PER_PAGE_DROPDOWN = ".VcTableFooter--itemsPerPage"
ROWS_PER_PAGE_OPTION = ".option-text"
CHECKBOX_DROPDOWN = '[data-qa="checkbox-dropdown-icon"]'
CURRENT_PAGE_OPTION = '[data-qa="item-current"]'
SUMMARY_TEXT = '[data-qa="summary-text"]'
CLIENT_NAME_HEADER = '[data-qa="CrmTable-All-header-matter_name"]'
CLIENT_ROW = '[data-qa="CrmTable-All"] tbody tr'
ROW_CHECKBOX = ".v-input--selection-controls__input"


def select_first_client(page: Page) -> None:
    """Select the first client row on the current page.

    The single-client selection only needs the count ("1 SELECTED OF M") to update;
    which client is irrelevant, so target the first visible row. This avoids any
    dependency on sort order / which page a specific named client lands on.
    """
    row = page.locator(CLIENT_ROW).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.locator(ROW_CHECKBOX).first.click()
    summary = page.locator(SUMMARY_TEXT).first
    expect(summary).to_contain_text("SELECTED", timeout=UI_TIMEOUT)


def set_rows_per_page(page: Page, rows: str) -> None:
    page.locator(ROWS_PER_PAGE_DROPDOWN).first.click()
    option = page.locator(ROWS_PER_PAGE_OPTION).filter(has_text=re.compile(rf"^\s*{rows}\s*$"))
    option.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.first.click()
    wait_for_clients_table(page)


def sort_by_client_name(page: Page) -> None:
    page.locator(CLIENT_NAME_HEADER).first.click()
    wait_for_clients_table(page)


def select_current_page(page: Page) -> None:
    page.locator(CHECKBOX_DROPDOWN).first.click()
    option = page.locator(CURRENT_PAGE_OPTION).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def assert_summary_text(page: Page, expected: str) -> None:
    """Assert the CRM summary line equals ``expected`` (case-insensitive, whitespace-normalized).

    Read via inner_text (rendered text, respecting CSS text-transform) to match the
    legacy Selenium getText() which returned the rendered uppercase label. Poll up to
    the 5s UI cap so the count assertion absorbs the post-selection re-render.
    """
    summary = page.locator(SUMMARY_TEXT).first
    summary.wait_for(state="visible", timeout=UI_TIMEOUT)
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    actual = ""
    while time.monotonic() < deadline:
        actual = " ".join((summary.inner_text() or "").split())
        if actual.upper() == expected.upper():
            return
        time.sleep(0.2)
    raise AssertionError(f"CRM summary expected {expected!r}, got {actual!r}")
