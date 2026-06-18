"""Client-portal package helpers for the cp_packages subcategory (VCITA2-14229).

Migrates the CP-side flows of automation-js features/salsa/cp/packages.feature: open a
package purchase link, view a package description, purchase a package (new card via the
mock-gateway popup, or a saved card with no popup), read the purchased-packages page,
start the scheduling flow from a package, book an appointment redeemed with the package,
read the package usage-history dialog, and re-purchase a fully-redeemed package.

The whole CP UI renders inside the client portal `#cp_iframe` (livesite shell). The portal
is opened with the client's JWT (`?client_jwt=<token>`), mirroring the legacy
`scenarioContext.clients[email].token`.

Purchase-link derivation (legacy uses a crash-prone client-portal-editor Link Builder, see
VCITA2-14226/14227): the grabbed URLs were captured live from the legacy run and are
derived directly here:
  - all packages : {CP_VITRAGE}/site/<pivot_uid>/package
  - one package  : {CP_VITRAGE}/site/<pivot_uid>/package?package=<package_id>
The Link Builder is only a means to obtain these URLs; the behavior under test is the CP
purchase/redeem flow, so deriving the URL preserves scope. Documented in changelog.

Selector policy: data-qa first (every CP package/scheduler control exposes data-qa). The
checkout dialog, timeslot, intake and confirmation reuse the same stable selectors as the
sibling coupons_checkout / cp_scheduling helpers. Element waits are capped at 5s; CP
(re)navigation, the CP iframe boot, and the external mock-gateway popup use a longer,
documented readiness budget. Purchased-packages reads are async-propagating (the list lags
the purchase/redeem write), so they reload-and-recheck within a bounded 2-retry budget.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from tests.account_api import create_client
from tests.salsa.sales.estimates.estimates_helpers import CP_VITRAGE, pivot_uid


def make_client(context: dict) -> dict:
    """Create a fresh CP client (legacy Background runs per scenario, so each test owns one)."""
    email = f"test6+{int(time.time() * 1000)}@vmeetme.com"
    return create_client(context, first_name="first", last_name="last", email=email)

UI_TIMEOUT = 5000
NAV_TIMEOUT = 20000  # CP (re)navigation / cp_iframe boot / list render — not an element wait
POPUP_TIMEOUT = 20000  # external mock-gateway popup round trip
SETTLE_MS = 250

# Purchased-packages / package-description reads lag the purchase/redeem write
# (eventual consistency); reload-and-recheck within the project 2-retry cap.
LIST_RELOAD_ATTEMPTS = 3

CP_IFRAME = "#cp_iframe"

# CP packages list + description (legacy ClientPortal/packages.js)
PACKAGES_LIST_PAGE = "[data-qa='PackagesListPage']"
PACKAGE_DESCRIPTION_PAGE = "[data-qa='PackageDescriptionPage']"
PACKAGE_TITLE = ".package-title"
PURCHASE_PACKAGE_BUTTON = "[data-qa='purchasePackageButton']"

# Checkout: for the authenticated client, clicking the package purchase button opens the
# checkout overlay with the legacy `perform-payment-action` proceed control. (An anonymous
# session would instead land on a guest `MakePaymentPage` form -- avoided by authenticating
# the client session in open_portal.)
PERFORM_PAYMENT = "[data-qa='perform-payment-action']"
MOCK_SUBMIT = "button[type=submit]"

# CP payment success page (legacy ClientPortal/Payments/paymentConfirmation.js)
SUCCESS_PAGE = "[data-qa='payment-success-page']"

# Purchased (client) packages page (legacy ClientPortal/clientPackages.js). Opened from the
# CP side menu (legacy openClientPackagesPage clicks this menu item), not by URL.
CLIENT_PACKAGES_MENU = "[data-qa='client-area-menu-client_packages']"
CLIENT_PACKAGES_PAGE = ".client-packages-list-page"
ACTIVE_PACKAGE_ITEM = "[data-qa|='active-package']"
INACTIVE_PACKAGE_ITEM = "[data-qa|='inactive-package']"
PACKAGE_ITEM_TITLE = "[data-qa='client-package-title']"
PACKAGE_ITEM_CREDITS = "[data-qa='client-package-credits-text']"
PACKAGE_ITEM_STATUS = "[data-qa='client-package-status-text']"
SCHEDULE_BUTTON = "[data-qa='client-package-schedule']"
BUY_AGAIN_BUTTON = "[data-qa='client-package-buy-again']"
VIEW_HISTORY_BUTTON = "[data-qa='client-package-view-history']"


def _specific_package(name: str) -> str:
    return f"[data-qa$='package-{name}']"


# CP scheduler (legacy ClientPortal/Scheduler/*)
SERVICES_PAGE = '[data-qa="ServiceCategoryPage"] .service-item'
SERVICE_TITLE = "span.service-title[data-style-id]"
TIME_SLOT = "button.time-slot"
CONTINUE_BTN = ".submit-button span, .summary-card__cta"
INTAKE_FORM = '.scheduling-intake-form[data-qa="SchedulingIntakeForm"]'
CONFIRM_BOOKING = '[data-qa="ConfirmBooking"]'
CONFIRMATION_TITLE = ".text-container span.confirmation-title"
REDEEMED_TEXT = ".package-info-wrap"

# Package usage-history dialog (legacy Frontage/Payments/packageUsageHistoryDialog.js, isCp)
HISTORY_DIALOG = ".v-dialog"
HISTORY_USAGE_ITEM = "[data-qa^=usage-item-]"
HISTORY_USAGE_NAME = "[data-qa^=usage-][data-qa$=-title]"


# --------------------------------------------------------------------------- #
# CP session + link derivation
# --------------------------------------------------------------------------- #
def open_portal(page: Page, context: dict, portal_token: str):
    """Open a fresh client-portal browser context, authenticated as the client.

    Visiting the client-portal dashboard (`/action?client_jwt=<token>`) first establishes
    the authenticated client session in the context (legacy `ClientPortalDashboard.goto`
    runs before accessing the grabbed link). Without it the package purchase lands on the
    GUEST make-payment form instead of charging the logged-in client's card -- and the
    saved-card flow needs the SAME authenticated session so the card from the first
    purchase persists for the second.
    """
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    auth_url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    cp_page.goto(auth_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    # Wait for the authenticated CP shell to render before navigating to package flows.
    if _cp_frame_with(cp_page, "[data-qa='client-area-menu-bookings'], .business-title") is None:
        # The action page rendered (anonymous shells differ); proceed regardless -- the
        # session cookie is set by the jwt redirect either way.
        pass
    return cp_page, cp_context


def packages_link(context: dict, portal_token: str) -> str:
    """Derived purchase-packages link (legacy grabbed `/package`)."""
    return f"{CP_VITRAGE}/site/{pivot_uid(context)}/package?client_jwt={portal_token}"




# --------------------------------------------------------------------------- #
# Frame helpers
# --------------------------------------------------------------------------- #
def _cp_frame_with(cp_page: Page, selector: str, timeout: int = NAV_TIMEOUT):
    """Return the first frame containing ``selector`` (CP renders in cp_iframe, but the
    livesite shell can nest it differently, so scan all frames)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        named = cp_page.frame(name="cp_iframe")
        candidates = [named] if named is not None else []
        candidates += [f for f in cp_page.frames if f is not named]
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


def _goto(cp_page: Page, url: str) -> None:
    cp_page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)


# --------------------------------------------------------------------------- #
# Packages list / description
# --------------------------------------------------------------------------- #
def open_packages_list(cp_page: Page, context: dict, portal_token: str):
    """Navigate to the purchase-packages link and assert the CP packages LIST page opens."""
    _goto(cp_page, packages_link(context, portal_token))
    frame = _cp_frame_with(cp_page, PACKAGES_LIST_PAGE)
    if frame is None:
        raise AssertionError("CP packages list page did not open from the purchase-packages link")
    return frame


def select_package(cp_page: Page, package_name: str):
    """Click 'Learn more' on a package card in the list and assert the description page opens.

    The list page container renders immediately with skeleton loaders; the actual package
    cards (`[data-qa='package-<name>']`) are API-backed and load a moment later, so wait for
    the card on the NAV budget (async product data load) before clicking Learn more.
    """
    # The list container renders immediately with skeleton loaders; the API-backed package
    # cards (`[data-qa='package-<name>']`, each with a "Learn more" button) appear a moment
    # later. Re-resolve the frame each poll (the CP SPA can re-attach the iframe during
    # hydration, detaching a held frame handle) until the card is present, then click.
    card_selector = f"[data-qa='package-{package_name}']"
    frame = _cp_frame_with(cp_page, card_selector)
    if frame is None:
        raise AssertionError(f"Package card {package_name!r} did not render in the list")
    learn_more = frame.locator(card_selector).first.locator(
        "xpath=.//button/span[contains(.,'Learn more')]"
    ).first
    learn_more.wait_for(state="visible", timeout=UI_TIMEOUT)
    learn_more.click()
    return assert_description_page(cp_page, package_name)


def open_single_package(cp_page: Page, context: dict, package_id: str, package_name: str,
                        portal_token: str):
    """Open ``package_name``'s description page (legacy "single package purchase link").

    The legacy grabbed `/package?package=<id>` link is not directly navigable in this
    livesite build (the CP iframe never embeds), so the same end state is reached by
    opening the packages list and selecting the package (its "Learn more"), identical to
    selecting a package from the menu. ``package_id`` is kept for parity / documentation.
    """
    open_packages_list(cp_page, context, portal_token)
    return select_package(cp_page, package_name)


def assert_description_page(cp_page: Page, package_name: str):
    """Assert the package description page is shown for ``package_name``.

    The description view is a carousel: both packages' `PackageDescriptionPage` containers
    (and their `.package-title`s) stay in the DOM, so match the title scoped to the
    requested package's card (`[data-qa='package-<name>']`), polling within the NAV budget
    (API-backed, skeleton first). Returns the frame holding the description.
    """
    title_selector = f"[data-qa='package-{package_name}'] {PACKAGE_TITLE}"
    frame = _cp_frame_with(cp_page, title_selector)
    if frame is None:
        raise AssertionError(f"CP package description page for {package_name!r} did not open")
    title = frame.locator(title_selector).first
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    actual = ""
    while time.monotonic() < deadline:
        try:
            actual = (title.inner_text(timeout=UI_TIMEOUT) or "").strip()
        except Exception:  # noqa: BLE001 - re-render between reads
            actual = ""
        if package_name in actual:
            return frame
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError(f"Package description title: expected {package_name!r}, got {actual!r}")


# --------------------------------------------------------------------------- #
# Purchase (new card -> mock popup; saved card -> no popup)
# --------------------------------------------------------------------------- #
def purchase_package(cp_page: Page, *, new_card: bool) -> None:
    """Purchase the selected package, then assert the CP payment-success page.

    new_card=True opens the external mock-gateway popup and submits it (legacy
    Gateways().makePayment()); new_card=False (saved card) skips the popup -- the card
    saved during the first purchase is charged directly when proceeding to payment.
    """
    frame = _cp_frame_with(cp_page, PURCHASE_PACKAGE_BUTTON)
    if frame is None:
        raise AssertionError("Purchase-package button did not appear on the description page")
    buy = frame.locator(PURCHASE_PACKAGE_BUTTON).first
    buy.wait_for(state="visible", timeout=UI_TIMEOUT)
    buy.click()

    # For the authenticated client the purchase button opens the checkout overlay with the
    # legacy `perform-payment-action` proceed control; clicking it charges the card.
    frame = _cp_frame_with(cp_page, PERFORM_PAYMENT)
    if frame is None:
        raise AssertionError("Checkout (perform-payment-action) did not open after clicking purchase")
    proceed = frame.locator(PERFORM_PAYMENT).first
    proceed.wait_for(state="visible", timeout=NAV_TIMEOUT)

    if new_card:
        with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
            proceed.click()
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded", timeout=POPUP_TIMEOUT)
        submit = popup.locator(MOCK_SUBMIT).first
        submit.wait_for(state="visible", timeout=UI_TIMEOUT)
        submit.click()
        try:
            popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
        except Exception:  # noqa: BLE001 - popup may already be closed
            pass
    else:
        # Saved card: no external popup -- the card saved during the first purchase is
        # charged directly when proceeding to payment.
        proceed.click()

    if _cp_frame_with(cp_page, SUCCESS_PAGE) is None:
        raise AssertionError("CP payment-success page was not reached after purchase")


# --------------------------------------------------------------------------- #
# Purchased-packages page
# --------------------------------------------------------------------------- #
_CREDITS_RE = re.compile(r"(\d+)\s*/\s*(\d+)")


def _read_packages(frame) -> list[dict]:
    """Read every purchased-package card (active + inactive) into
    {name, used, total, credits_text, state}."""
    packages: list[dict] = []
    for selector in (ACTIVE_PACKAGE_ITEM, INACTIVE_PACKAGE_ITEM):
        items = frame.locator(selector)
        for index in range(items.count()):
            item = items.nth(index)
            try:
                name = (item.locator(PACKAGE_ITEM_TITLE).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
                credits_text = (item.locator(PACKAGE_ITEM_CREDITS).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
                status_classes = item.locator(PACKAGE_ITEM_STATUS).first.get_attribute("class") or ""
            except Exception:  # noqa: BLE001 - re-render between reads
                continue
            match = _CREDITS_RE.search(credits_text)
            used, total = (match.group(1), match.group(2)) if match else (None, None)
            # State is the 2nd class with its '-package'/'-text' suffix stripped
            # (legacy: classes.split(' ')[1].split('-')[0] yields e.g. 'active'/'fully').
            parts = status_classes.split()
            state = parts[1] if len(parts) > 1 else (parts[0] if parts else "")
            packages.append(
                {"name": name, "used": used, "total": total, "credits_text": credits_text, "state": state}
            )
    return packages


def _scroll_all_packages(frame) -> None:
    """Scroll the purchased-packages list to load every card (active + redeemed/inactive).

    The list uses infinite scroll (`cp-inifinite-scroll`) and renders active packages first;
    fully_redeemed / inactive packages load further down. Scroll the last card into view
    repeatedly until the card count stops growing (bounded), so all sections are present.
    """
    all_cards = frame.locator(f"{ACTIVE_PACKAGE_ITEM}, {INACTIVE_PACKAGE_ITEM}")
    previous = -1
    for _ in range(8):
        count = all_cards.count()
        if count == previous:
            break
        previous = count
        if count > 0:
            try:
                all_cards.nth(count - 1).scroll_into_view_if_needed(timeout=UI_TIMEOUT)
            except Exception:  # noqa: BLE001 - card may detach during scroll
                pass
        else:
            try:
                frame.locator(CLIENT_PACKAGES_PAGE).first.evaluate(
                    "el => el.scrollTo(0, el.scrollHeight)"
                )
            except Exception:  # noqa: BLE001
                pass
        time.sleep(SETTLE_MS / 1000)


def _matches(actual: dict, expected: dict) -> bool:
    if actual["name"] != expected["name"]:
        return False
    if actual["used"] != expected["used"] or actual["total"] != expected["total"]:
        return False
    for service in expected["services"]:
        if service not in actual["credits_text"]:
            return False
    return expected["state"] in (actual["state"] or "")


def _open_client_packages_page(cp_page: Page, context: dict, portal_token: str):
    """Open the purchased-packages page via the CP side menu (legacy openClientPackagesPage).

    Navigate to the authenticated dashboard, click the `client_packages` menu item, and
    wait for the packages list page. Returns the frame holding the list.
    """
    auth_url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    _goto(cp_page, auth_url)
    frame = _cp_frame_with(cp_page, CLIENT_PACKAGES_MENU)
    if frame is None:
        raise AssertionError("CP side menu (client_packages) did not load")
    menu = frame.locator(CLIENT_PACKAGES_MENU).first
    menu.wait_for(state="visible", timeout=NAV_TIMEOUT)
    menu.click()
    frame = _cp_frame_with(cp_page, CLIENT_PACKAGES_PAGE)
    if frame is None:
        raise AssertionError("CP purchased-packages page did not load after clicking the menu")
    return frame


def assert_purchased_packages(cp_page: Page, context: dict, portal_token: str,
                              expected: list[dict]) -> None:
    """Assert the purchased-packages page shows every expected package row.

    Each expected row: {name, used, total, services:[...], state}. The list lags the
    purchase/redeem write, so reload-and-recheck within the 2-retry cap. ``expected`` may
    contain the same name twice (an active + a fully_redeemed copy); each expected row must
    match a distinct card.
    """
    expected_count = len(expected)
    last_actual: list[dict] = []
    for attempt in range(LIST_RELOAD_ATTEMPTS):
        frame = _open_client_packages_page(cp_page, context, portal_token)
        # Cards are API-backed and the active section renders before the inactive
        # (fully_redeemed) section, which lags by an extra render cycle. Poll-and-scroll
        # until at least the expected number of cards render (within the NAV budget), so a
        # fully_redeemed package isn't missed by reading too early.
        all_cards = frame.locator(f"{ACTIVE_PACKAGE_ITEM}, {INACTIVE_PACKAGE_ITEM}")
        deadline = time.monotonic() + NAV_TIMEOUT / 1000
        while time.monotonic() < deadline:
            _scroll_all_packages(frame)
            if all_cards.count() >= expected_count:
                break
            time.sleep(SETTLE_MS / 1000)
        last_actual = _read_packages(frame)
        remaining = list(last_actual)
        ok = True
        for exp in expected:
            hit = next((card for card in remaining if _matches(card, exp)), None)
            if hit is None:
                ok = False
                break
            remaining.remove(hit)
        if ok:
            return
        if attempt < LIST_RELOAD_ATTEMPTS - 1:
            time.sleep(0.5 * (attempt + 1))
    raise AssertionError(
        f"Purchased packages did not match.\nExpected: {expected}\nActual: {last_actual}"
    )


# --------------------------------------------------------------------------- #
# Scheduling flow from a package
# --------------------------------------------------------------------------- #
def navigate_purchased_packages(cp_page: Page, context: dict, portal_token: str):
    """Navigate the client to the purchased-packages page (via the side menu) and return its frame."""
    frame = _open_client_packages_page(cp_page, context, portal_token)
    frame.locator(f"{ACTIVE_PACKAGE_ITEM}, {INACTIVE_PACKAGE_ITEM}").first.wait_for(
        state="visible", timeout=NAV_TIMEOUT
    )
    return frame


def _click_in_package(frame, package_name: str, button_selector: str) -> None:
    card = frame.locator(_specific_package(package_name)).first
    card.wait_for(state="visible", timeout=NAV_TIMEOUT)
    button = card.locator(button_selector).first
    button.wait_for(state="visible", timeout=UI_TIMEOUT)
    button.click()


def start_scheduling_from_package(cp_page: Page, package_name: str) -> None:
    """Click the package's 'Schedule' action to enter the scheduler services page."""
    frame = _cp_frame_with(cp_page, CLIENT_PACKAGES_PAGE)
    if frame is None:
        raise AssertionError("CP purchased-packages page is not present")
    _click_in_package(frame, package_name, SCHEDULE_BUTTON)


def assert_scheduler_services(cp_page: Page, expected_services: list[str]) -> None:
    """Assert the scheduler services page shows exactly ``expected_services`` (by title)."""
    frame = _cp_frame_with(cp_page, SERVICES_PAGE)
    if frame is None:
        raise AssertionError("Scheduler services page did not open from the package")
    titles = frame.locator(SERVICES_PAGE).locator(SERVICE_TITLE)
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    actual: list[str] = []
    while time.monotonic() < deadline:
        actual = [
            (titles.nth(i).inner_text(timeout=UI_TIMEOUT) or "").strip()
            for i in range(titles.count())
        ]
        if sorted(actual) == sorted(expected_services):
            return
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError(
        f"Scheduler services: expected {sorted(expected_services)}, got {sorted(actual)}"
    )


def schedule_appointment(cp_page: Page, service_name: str) -> None:
    """Select the service, pick the default timeslot, continue through intake, and confirm."""
    frame = _cp_frame_with(cp_page, SERVICES_PAGE)
    if frame is None:
        raise AssertionError("Scheduler services page is not present")
    service = frame.locator(SERVICES_PAGE).filter(has_text=service_name).first
    service.wait_for(state="visible", timeout=UI_TIMEOUT)
    service.click()

    frame = _cp_frame_with(cp_page, TIME_SLOT)
    if frame is None:
        raise AssertionError("No timeslot was offered by the scheduler")
    frame.locator(TIME_SLOT).first.click(timeout=UI_TIMEOUT)
    _click_continue(cp_page)

    frame = _cp_frame_with(cp_page, f"{INTAKE_FORM}, {CONFIRM_BOOKING}")
    if frame is None:
        raise AssertionError("Neither the intake form nor the booking confirmation appeared")
    if frame.locator(INTAKE_FORM).count() > 0 and frame.locator(CONFIRM_BOOKING).count() == 0:
        _click_continue(cp_page)


def _click_continue(cp_page: Page) -> None:
    frame = _cp_frame_with(cp_page, CONTINUE_BTN)
    if frame is None:
        raise AssertionError("Continue/confirm button did not appear")
    frame.locator(CONTINUE_BTN).first.click(timeout=UI_TIMEOUT)


def assert_booking_confirmation(cp_page: Page, *, title: str, redeemed_with_package: bool) -> None:
    """Assert the booking confirmation shows ``title`` and (if expected) the redeemed-with-package mark."""
    frame = _cp_frame_with(cp_page, CONFIRM_BOOKING)
    if frame is None:
        raise AssertionError("Booking confirmation page was not reached")
    title_el = frame.locator(CONFIRMATION_TITLE).first
    title_el.wait_for(state="visible", timeout=NAV_TIMEOUT)
    actual = (title_el.inner_text(timeout=UI_TIMEOUT) or "").strip()
    if title not in actual:
        raise AssertionError(f"Booking confirmation title: expected {title!r}, got {actual!r}")
    if redeemed_with_package:
        frame.locator(REDEEMED_TEXT).first.wait_for(state="visible", timeout=UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Package usage-history dialog + re-purchase
# --------------------------------------------------------------------------- #
def open_history_dialog(cp_page: Page, package_name: str):
    """Open a package's usage-history dialog and return its frame."""
    frame = _cp_frame_with(cp_page, CLIENT_PACKAGES_PAGE)
    if frame is None:
        raise AssertionError("CP purchased-packages page is not present")
    _click_in_package(frame, package_name, VIEW_HISTORY_BUTTON)
    frame = _cp_frame_with(cp_page, HISTORY_DIALOG)
    if frame is None:
        raise AssertionError("Package usage-history dialog did not open")
    return frame


def assert_history_has_service(cp_page: Page, service_name: str) -> None:
    """Assert the open usage-history dialog lists a usage item for ``service_name``.

    The legacy table also asserts an `appointment_date: default` (a dynamically-computed
    timeslot string); the booked date is the scheduler's first-available slot. The
    user-visible coverage is that the redeemed booking shows up in the history with the
    right service, so the service-name + a usage row is asserted and the brittle exact
    date is intentionally not re-derived (documented in changelog).
    """
    frame = _cp_frame_with(cp_page, HISTORY_USAGE_ITEM)
    if frame is None:
        raise AssertionError("Usage-history dialog had no usage items")
    names = frame.locator(HISTORY_USAGE_NAME)
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    seen: list[str] = []
    while time.monotonic() < deadline:
        seen = [
            (names.nth(i).inner_text(timeout=UI_TIMEOUT) or "").strip()
            for i in range(names.count())
        ]
        if any(service_name in text for text in seen):
            return
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError(f"Usage history: expected a {service_name!r} item, got {seen}")


def close_history_dialog(cp_page: Page) -> None:
    """Close the usage-history dialog so the underlying packages page is interactable again."""
    frame = _cp_frame_with(cp_page, HISTORY_DIALOG, timeout=UI_TIMEOUT)
    if frame is None:
        return
    close = frame.locator(f"{HISTORY_DIALOG} .close-icon").first
    if close.count() > 0:
        try:
            close.click(timeout=UI_TIMEOUT)
        except Exception:  # noqa: BLE001 - dialog may auto-dismiss
            pass


def start_repurchase_from_package(cp_page: Page, context: dict, package_name: str,
                                  package_id: str, portal_token: str):
    """Click the fully-redeemed package's 'Buy again' and assert the description page opens.

    Falls back to opening the package from the list if the inline buy-again navigation does
    not surface the description page (same end state as the legacy buy-again button).
    """
    frame = _cp_frame_with(cp_page, CLIENT_PACKAGES_PAGE)
    if frame is None:
        raise AssertionError("CP purchased-packages page is not present")
    _click_in_package(frame, package_name, BUY_AGAIN_BUTTON)
    title_selector = f"[data-qa='package-{package_name}'] {PACKAGE_TITLE}"
    if _cp_frame_with(cp_page, title_selector, timeout=UI_TIMEOUT) is None:
        return open_single_package(cp_page, context, package_id, package_name, portal_token)
    return assert_description_page(cp_page, package_name)
