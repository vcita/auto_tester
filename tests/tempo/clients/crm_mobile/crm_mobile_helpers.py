"""CRM-mobile UI/API helpers for the crm_mobile migration (VCITA2-14251).

Ports `automation-js/features/steps/crm-mobile.feature` (`@mobile_web`, scenario
"CRM mobile list"). The CRM renders a distinct mobile layout that mounts only under
mobile emulation (legacy used Chrome `Nexus 5` emulation); `set_mobile_viewport`
replicates that via CDP (mobile device metrics + touch + mobile user-agent).

Reuse map:
- client seeding -> `tests.account_api.create_client` (legacy `POST /platform/v1/clients`).
- counter / empty-state / tab-search asserts use the same stable `data-qa` selectors as
  `crm_tabs_management.crm_tabs_helpers` (`summary-text`, `VcEmptyState`, the per-tab
  search bar) and are validated identical to the legacy `newClients.js` page object.

The mobile CRM layout does NOT render the desktop `.table-actions__filter` toolbar
(it uses `CrmTable-<tab>-filter-button` + a bottom-nav shell), so the desktop
`crm_*_helpers.wait_for_clients_table` readiness gate cannot be reused. The mobile
readiness signal is the active view's `summary-text` counter becoming visible — handled
by the mobile-local navigation/tab helpers below (confirmed via DOM probe).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.account_api import create_client

UI_TIMEOUT = 5_000
# CRM seeker indexing can lag API-created clients; bounded poll for the expected counter
# (mirrors the legacy clientsSearchBar retry budget, tied to a real async readiness signal).
COUNTER_TIMEOUT_SECONDS = 5
COUNTER_RELOAD_ATTEMPTS = 3

# Legacy newClients.closeCrmMobileWelcomeModal selector (RolloutBottomSheet footer).
WELCOME_MODAL_BUTTON = '[data-qa="RolloutBottomSheet-footer-button"]'

SUMMARY_TEXT = '[data-qa="summary-text"]'
EMPTY_STATE = '[data-qa="VcEmptyState"]'

# Mobile emulation: legacy @mobile_web used Chrome mobile-emulation (Nexus 5), which
# applies mobile device metrics + touch + a mobile user-agent together. vcita keys its
# mobile CRM layout (and the welcome bottom-sheet) on that mobile signal, not on raw
# viewport width alone, so a plain set_viewport_size left the desktop layout mounted.
# We replicate Nexus 5 emulation via CDP (device metrics mobile:true + touch + mobile UA).
MOBILE_WIDTH = 360
MOBILE_HEIGHT = 640
MOBILE_SCALE = 3
MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)

# The 10 CSV clients (runtime/resources/crm_mobile_clients.csv). The legacy [seq]
# token (one random int per scenario, shared across rows) only keeps emails unique
# per legacy run; here we make each run's emails unique via a per-run seq suffix.
# Tags (rows 2 & 3 -> tag4) are intentionally NOT seeded: the only step that used
# tags (the "Tags" filter) is commented out / out of scope in the legacy scenario.
CSV_CLIENTS = [
    ("first1", "last1"),
    ("first2", "last2"),
    ("first3", "last3"),
    ("no-tag", "last4"),
    ("first5", "last5"),
    ("first6", "last6"),
    ("first7", "last7"),
    ("first8", "last8"),
    ("first9", "last9"),
    ("first10", "last10"),
]


# --------------------------------------------------------------------------- #
# Mobile emulation + seeding
# --------------------------------------------------------------------------- #
def set_mobile_viewport(page: Page) -> None:
    """Emulate a mobile device so the CRM mobile layout mounts.

    Replicates the legacy ``@mobile_web`` Chrome mobile-emulation (``Nexus 5``) via CDP:
    mobile device metrics (``mobile: true``), touch emulation, and a mobile user-agent.
    Raw viewport width alone leaves vcita on its desktop layout; the mobile signal is
    what mounts the mobile CRM and its welcome bottom-sheet. Must be applied before the
    clients list is loaded.
    """
    cdp = page.context.new_cdp_session(page)
    cdp.send(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": MOBILE_WIDTH,
            "height": MOBILE_HEIGHT,
            "deviceScaleFactor": MOBILE_SCALE,
            "mobile": True,
            "screenWidth": MOBILE_WIDTH,
            "screenHeight": MOBILE_HEIGHT,
        },
    )
    cdp.send("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
    cdp.send("Emulation.setUserAgentOverride", {"userAgent": MOBILE_USER_AGENT})
    page.set_viewport_size({"width": MOBILE_WIDTH, "height": MOBILE_HEIGHT})


def seed_csv_clients(context: dict, seq: str) -> list[dict]:
    """Seed the 10 crm_mobile_clients.csv clients via API (legacy `user creates new
    clients via API | crm_mobile_clients.csv |`).

    ``seq`` makes the emails unique per run (the legacy [seq] token). Returns the
    created client dicts.
    """
    created = []
    for first, last in CSV_CLIENTS:
        email = f"test_{first}_{seq}@vmeetme.com"
        created.append(create_client(context, first, last, email))
    return created


# --------------------------------------------------------------------------- #
# Mobile CRM navigation / readiness
# --------------------------------------------------------------------------- #
def _active(page: Page):
    """The currently visible CRM view panel (Vuetify keeps every visited view mounted)."""
    return page.locator(".v-window-item--active").first


def wait_for_mobile_crm_ready(page: Page) -> None:
    """Mobile CRM readiness: the active view's summary-text counter is visible.

    The mobile layout has no desktop `.table-actions__filter`, so the counter (always
    rendered with the list) is the stable ready signal.
    """
    _active(page).locator(SUMMARY_TEXT).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def open_clients_list(page: Page) -> None:
    """Navigate to the CRM clients list (mobile-safe; legacy newClients.goto -> /app/clients)."""
    if not page.url.rstrip("/").endswith("/app/clients"):
        app_base = page.url.split("/app/")[0]
        page.goto(f"{app_base}/app/clients", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
        page.wait_for_url("**/app/clients**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    wait_for_mobile_crm_ready(page)


def close_crm_mobile_welcome_modal(page: Page) -> None:
    """Close the CRM mobile welcome bottom-sheet (legacy closeCrmMobileWelcomeModal).

    Wait for the welcome modal's footer button, then click it. One detection, one
    action; if the modal never appears within the cap the step fails (the legacy
    scenario unconditionally closes it on a fresh account).
    """
    button = page.locator(WELCOME_MODAL_BUTTON).first
    button.wait_for(state="visible", timeout=UI_TIMEOUT)
    button.click()
    button.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _tab(page: Page, tab_name: str):
    return page.locator(
        f'[data-qa="VcTabs-tab-{tab_name.replace(" ", "-")}"], '
        f'[data-qa="VcTabs-tab-{tab_name.replace(" ", "")}"]'
    ).first


def select_tab(page: Page, tab_name: str) -> None:
    """Select a CRM tab (legacy newClients.clickOnTab) and wait for the mobile list to
    settle (active view's counter visible)."""
    tab = _tab(page, tab_name)
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()
    wait_for_mobile_crm_ready(page)


# --------------------------------------------------------------------------- #
# Reads / assertions
# --------------------------------------------------------------------------- #
def _counter_text(page: Page) -> str:
    counter = _active(page).locator(SUMMARY_TEXT).first
    try:
        counter.wait_for(state="visible", timeout=UI_TIMEOUT)
        return (counter.inner_text(timeout=UI_TIMEOUT) or "").strip()
    except PlaywrightTimeoutError:
        return ""


def assert_clients_counter(page: Page, expected: str) -> None:
    """Assert the active view's filtered-clients counter (legacy filteredClientsCounter,
    `summary-text`). Bounded poll-and-reload: CRM seeker indexing can lag the just-seeded
    clients, so re-read (and, within the cap, reload) until the counter settles."""
    expected_u = expected.upper()
    actual = ""
    for attempt in range(COUNTER_RELOAD_ATTEMPTS):
        deadline = time.monotonic() + COUNTER_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            actual = _counter_text(page)
            if actual.upper() == expected_u:
                return
            time.sleep(0.3)
        if attempt < COUNTER_RELOAD_ATTEMPTS - 1:
            page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
            wait_for_mobile_crm_ready(page)
    raise AssertionError(f"Expected counter {expected!r}, got {actual!r}")


def assert_empty_state(page: Page) -> None:
    """Assert the active CRM table shows its empty state (legacy getCrmTableEmptyState)."""
    _active(page).locator(EMPTY_STATE).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def _row_names(page: Page, tab_name: str) -> list[str]:
    squashed = tab_name.replace(" ", "")
    rows = page.locator(f'[data-qa="CrmTable-{squashed}_mainClientName"]')
    return [rows.nth(i).inner_text().strip() for i in range(rows.count())]


def search_in_tab(page: Page, tab_name: str, query: str, expected: list[str]) -> None:
    """Search inside a tab's action bar and assert the resulting rows (legacy
    clientsSearchBar). The seeker can lag the API-created client, so the search is
    re-issued a bounded number of times (each refill gives the index a beat) until the
    rows match."""
    search = page.locator(
        f'[data-qa="CrmTable-{tab_name.replace(" ", "-")}-actionBar-searchBar"], '
        f'[data-qa="CrmTable-{tab_name.replace(" ", "")}-actionBar-searchBar"]'
    ).first
    search.wait_for(state="visible", timeout=UI_TIMEOUT)

    last: list[str] = []
    for attempt in range(COUNTER_RELOAD_ATTEMPTS):
        search.fill("")
        search.fill(query)
        try:
            wait_for_mobile_crm_ready(page)
        except PlaywrightTimeoutError:
            pass
        last = _row_names(page, tab_name)
        if last == expected:
            return
        if attempt < COUNTER_RELOAD_ATTEMPTS - 1:
            page.wait_for_timeout(1_500)
    raise AssertionError(f"Search {query!r} in {tab_name!r}: expected {expected}, got {last}")
