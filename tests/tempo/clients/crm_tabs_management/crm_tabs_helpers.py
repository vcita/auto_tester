"""CRM tabs-management UI helpers for the crm_tabs_management migration (VCITA2-13992).

Ports the legacy `pages/desktop/Frontage/Clients/newClients.js` tab actions not already
covered by `crm_views_helpers`: empty-state and filtered-clients-counter reads, search
inside a tab's action bar, tab drag-reorder, and pinned-tab ordering. Navigation, tab
clicking, view selection, close-tab and the views-dropdown read are reused from
`crm_views_helpers` (same stable `data-qa` selectors).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, expect

from tests.account_api import account_request
from tests.tempo.clients.crm_views.crm_views_helpers import (
    UI_TIMEOUT,
    _active,
    _dq_variants,
    _tab,
    _unpinned_view_names,
    open_clients_list,
    wait_for_clients_table,
)

# CRM seeker indexing can lag an API-created client/booking; bounded re-search with a
# short inter-attempt wait so each retry gives the index a beat (legacy used 8 retries
# with 3-7s delays; this is tighter while still tied to that real async readiness signal).
SEARCH_ATTEMPTS = 6
SEARCH_RETRY_WAIT_MS = 1500
EMPTY_STATE = '[data-qa="VcEmptyState"]'
SUMMARY_TEXT = '[data-qa="summary-text"]'


def create_self_client(context: dict, first_name: str, last_name: str, email: str) -> dict:
    """Create a client whose email is the account owner's, so the CRM row renders the
    "(You as a client)" suffix (legacy livesite leave-details with the owner email).

    Returns ``{id, name, label, email}``. No portal token is needed here (unlike
    account_api.create_client), so this uses the raw clients endpoint."""
    response = account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "source_name": "automation",
        },
    )
    payload = response.get("data") or response
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")
    return {
        "id": client_id,
        "name": f"{first_name} {last_name}",
        "label": f"{first_name} {last_name} (You as a client)",
        "email": email,
    }


def assert_empty_state(page: Page) -> None:
    """Assert the active CRM table shows its empty state (legacy getCrmTableEmptyState)."""
    _active(page).locator(EMPTY_STATE).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def assert_clients_counter(page: Page, expected: str) -> None:
    """Assert the active view's filtered-clients counter (legacy filteredClientsCounter)."""
    counter = _active(page).locator(SUMMARY_TEXT).first
    counter.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(counter).to_have_text(expected, timeout=UI_TIMEOUT)


def _search_bar(page: Page, tab_name: str):
    return page.locator(_dq_variants("CrmTable-", tab_name, "-actionBar-searchBar")).first


def _row_names(page: Page, tab_name: str) -> list[str]:
    squashed = tab_name.replace(" ", "")
    selector = (
        f"{_dq_variants('CrmTable-', tab_name, '-item-matter_name')}, "
        f'[data-qa="CrmTable-{squashed}_mainClientName"]'
    )
    rows = page.locator(selector)
    return [rows.nth(i).inner_text().strip() for i in range(rows.count())]


def search_in_tab(page: Page, tab_name: str, query: str, expected: list[str]) -> None:
    """Search inside a tab's action bar and assert the resulting rows (legacy
    clientsSearchBar). The seeker can lag the API-created client, so the search is
    re-issued a bounded number of times (no fixed sleeps — each refill gives the index a
    beat) until the rows match."""
    search = _search_bar(page, tab_name)
    search.wait_for(state="visible", timeout=UI_TIMEOUT)

    last: list[str] = []
    for attempt in range(SEARCH_ATTEMPTS):
        search.fill("")
        search.fill(query)
        try:
            wait_for_clients_table(page)
        except Exception:
            pass
        last = _row_names(page, tab_name)
        if last == expected:
            return
        # The seeker can lag the API-created client/booking; give the index a beat before
        # re-issuing (bounded; mirrors the legacy clientsSearchBar retry delays).
        if attempt < SEARCH_ATTEMPTS - 1:
            page.wait_for_timeout(SEARCH_RETRY_WAIT_MS)
    raise AssertionError(f"Search {query!r} in {tab_name!r}: expected {expected}, got {last}")


def _tab_x(page: Page, name: str) -> float:
    tab = _tab(page, name)
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    box = tab.bounding_box()
    if not box:
        raise AssertionError(f"Tab {name!r} has no bounding box")
    return box["x"]


def drag_tab(page: Page, from_tab: str, to_tab: str) -> None:
    """Drag ``from_tab`` to precede ``to_tab`` (legacy dragTab: click the tab, then drag
    its grab handle onto the target tab). Vuedraggable needs an intermediate hover, so a
    manual mouse sequence backs up Playwright's drag_to."""
    open_clients_list(page)
    _tab(page, from_tab).click()
    wait_for_clients_table(page)

    handle = page.locator(_dq_variants("VcTabs-drag-", from_tab)).first
    handle.wait_for(state="visible", timeout=UI_TIMEOUT)
    target = _tab(page, to_tab)
    target.wait_for(state="visible", timeout=UI_TIMEOUT)

    try:
        handle.drag_to(target)
    except Exception:
        src = handle.bounding_box()
        dst = target.bounding_box()
        if not (src and dst):
            raise
        page.mouse.move(src["x"] + src["width"] / 2, src["y"] + src["height"] / 2)
        page.mouse.down()
        page.mouse.move(dst["x"] + dst["width"] / 2, dst["y"] + dst["height"] / 2, steps=10)
        page.mouse.up()
    wait_for_clients_table(page)


def assert_tab_before(page: Page, first_tab: str, second_tab: str) -> None:
    """Assert ``first_tab`` is positioned before ``second_tab`` in the pinned tab bar
    (legacy getPinnedTabs + indexOf comparison), using horizontal order."""
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _tab_x(page, first_tab) < _tab_x(page, second_tab):
            return
        time.sleep(0.3)
    raise AssertionError(f"Tab {first_tab!r} is not displayed before {second_tab!r}")


def assert_tab_in_views_dropdown(page: Page, name: str) -> None:
    """Assert a (now-unpinned) tab appears in the views overflow dropdown (legacy
    "tab X is displayed in views dropdown list")."""
    open_clients_list(page)
    names = _unpinned_view_names(page)
    assert name in names, f"Expected {name!r} in views dropdown, got {names}"
