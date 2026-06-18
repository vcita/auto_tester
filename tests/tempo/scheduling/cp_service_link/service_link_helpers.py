"""Helpers for the CP service-link migration (VCITA2-14226).

Legacy chain: features/tempo/CP/service-link.feature — grab scheduler links and access them
anonymously, asserting the client-portal scheduler calendar / staff-select / services pages
under different provider/service states.

Reuses the proven, current-product CP helper ``grab_service_link`` (the services-row "Copy
public link") from the sibling payment_setups subcategory. Frame scanning + the calendar /
staff-select / services-page assertions are local: the general link lands on the staff-select
page when >1 provider exists, so the calendar wait cannot be assumed.

Staff-scoped link (deviation, documented in changelog): the legacy linkBuilderDialog combined
service+staff into one link. The current Create-a-Link builder lives in the client-portal-editor
(heavy nested Angular+Vue), separates service vs staff scoping, and is crash-prone in headless
CI (TargetClosedError) with an async-propagating staff list. The scheduler link is simply
``https://<live-host>/site/<token>/online-scheduling?staff=<staff_uid>``, so the staff-scoped
link is DERIVED from the UI-grabbed general link's portal base + the staff uid; the general link
is still grabbed via the UI, and accessing both links + every assertion remain UI.
"""
from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.account_api import account_request, pivot_uid
from tests.tempo.scheduling.payment_setups.cp_scheduling_helpers import grab_service_link

UI_TIMEOUT = 10_000  # CP scheduler interactions (matches sibling cp_scheduling_helpers)
NAV_TIMEOUT = 20_000  # back-office nav + live-site portal loads
SETTLE_MS = 300

# Client-portal scheduler (cp_iframe) selectors (legacy calendar.js / staffList.js / serviceList.js).
SUMMARY_SERVICE = ".service-section"
SUMMARY_STAFF = ".staff-section span"
STAFF_SELECT_CONTAINER = '[data-qa="StaffSecondSelection"]'
STAFF_SELECT_NAME = ".staff-details .display-name"
SERVICES_PAGE_CONTAINER = '[data-qa="ServiceCategoryPage"] .service-item'
SERVICE_TITLE = "span.service-title[data-style-id]"
SERVICE_DETAILS = ".service-details span"


def cp_frame_with(page: Page, selector: str, timeout: int = UI_TIMEOUT):
    """Return the first frame containing ``selector`` (CP renders in cp_iframe, but the
    livesite shell sometimes nests it differently, so scan all frames)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        named = page.frame(name="cp_iframe")
        candidates = ([named] if named is not None else []) + [f for f in page.frames if f is not named]
        for frame in candidates:
            if frame is None:
                continue
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:  # noqa: BLE001 - frame may be navigating
                continue
        time.sleep(SETTLE_MS / 1000)
    return None


def _text(frame, selector: str) -> str:
    loc = frame.locator(selector).first
    loc.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (loc.inner_text(timeout=UI_TIMEOUT) or "").strip()


def access_link(page: Page, link: str) -> None:
    """Navigate (anonymously, same browser context) to a grabbed scheduler link."""
    page.goto(link, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)


def grab_general_service_link(page: Page, service_name: str, app_base: str) -> str:
    """Grab the service's general public link (reused proven helper). Returns to the
    back-office app host first — after accessing a live portal link the page is on the
    live-site host, where the services-settings page does not exist."""
    page.goto(f"{app_base}/app/settings/services", wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    return grab_service_link(page, service_name)


def derive_staff_scoped_link(general_link: str, staff_uid: str) -> str:
    """Derive the staff-scoped scheduler link from a UI-grabbed general scheduler link
    (same ``/site/<token>/online-scheduling`` base) by scoping it to ``staff_uid``."""
    base = general_link.split("?")[0]
    return f"{base}?staff={staff_uid}"


def assert_calendar(page: Page, *, service_name: str, providing_staff: str) -> None:
    """CP scheduler calendar booking summary shows the service + providing staff."""
    frame = cp_frame_with(page, SUMMARY_SERVICE)
    if frame is None:
        raise AssertionError("Scheduler calendar booking summary did not render")
    actual_service = _text(frame, SUMMARY_SERVICE)
    assert service_name in actual_service, f"calendar service {actual_service!r} missing {service_name!r}"
    actual_staff = _text(frame, SUMMARY_STAFF)
    assert providing_staff in actual_staff, f"calendar staff {actual_staff!r} missing {providing_staff!r}"


def assert_staff_select(page: Page, expected_staff: list[str]) -> None:
    """CP scheduler staff-select page lists exactly ``expected_staff`` (ordered)."""
    frame = cp_frame_with(page, STAFF_SELECT_CONTAINER)
    if frame is None:
        raise AssertionError("Scheduler staff-select page did not render")
    names_loc = frame.locator(STAFF_SELECT_NAME)
    names_loc.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual = [(names_loc.nth(i).inner_text() or "").strip() for i in range(names_loc.count())]
    assert actual == expected_staff, f"staff-select shows {actual!r}, expected {expected_staff!r}"


def assert_services_page(page: Page, expected: list[dict]) -> None:
    """CP scheduler services page shows each expected {name, duration} service."""
    frame = cp_frame_with(page, SERVICES_PAGE_CONTAINER)
    if frame is None:
        raise AssertionError("Scheduler services page did not render")
    items = frame.locator(SERVICES_PAGE_CONTAINER)
    items.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual = {}
    for i in range(items.count()):
        item = items.nth(i)
        name = (item.locator(SERVICE_TITLE).first.inner_text() or "").strip()
        details = item.locator(SERVICE_DETAILS)
        duration = (details.nth(0).inner_text() or "").strip() if details.count() else ""
        actual[name] = duration
    for exp in expected:
        assert exp["name"] in actual, f"services page missing {exp['name']!r}; has {list(actual)}"
        if exp.get("duration"):
            assert exp["duration"] in actual[exp["name"]], (
                f"service {exp['name']!r} duration {actual[exp['name']]!r} missing {exp['duration']!r}"
            )


def delete_staff_api(context: dict, staff_uid: str) -> None:
    """Delete a staff member (legacy `delete latest staff via API`)."""
    account_request(context, "DELETE", f"/platform/v1/businesses/{pivot_uid(context)}/staffs/{staff_uid}")


def delete_service_api(context: dict, service_uid: str) -> None:
    """Delete the service via API (legacy deletes via the services-row UI; deletion here is a
    state prerequisite for the services-page assertion, not the behavior under test, so API
    keeps it stable)."""
    account_request(context, "DELETE", f"/v2/settings/services/{service_uid}")
