"""Shared helpers for the Sales > Estimates tests (migrated from automation-js).

Covers API setup (client, tax mode), the POV itemizable estimate dialog
(existing/custom items, taxes, sections, reorder, send), and parsing of the
back-office and client-portal estimate views.
"""
import re
import time

import requests
from playwright.sync_api import Page

UI_TIMEOUT = 5000
NAV_TIMEOUT = 20000  # Angular iframe (re)load points; conditional, not a fixed sleep
REQUEST_TIMEOUT = 30
CP_VITRAGE = "https://live.meet2know.com"


# --------------------------------------------------------------------------- #
# API helpers
# --------------------------------------------------------------------------- #
def _api_base(context: dict) -> str:
    api_base_url = context.get("api_base_url")
    if api_base_url:
        return api_base_url.rstrip("/")
    base_url = (context.get("base_url") or "").rstrip("/")
    if "meet2know.com" in base_url:
        return "https://api2.meet2know.com"
    if "vcita.com" in base_url:
        return "https://api.vcita.biz"
    if "app-" in base_url and ".external.int-eks.vchost.co" in base_url:
        return base_url.replace("https://app-", "https://core-", 1)
    raise ValueError("api_base_url is missing from context and could not be inferred")


def _headers(context: dict) -> dict:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")
    return {"Authorization": f"Bearer {token}"}


def _api(context: dict, method: str, path: str, **kwargs) -> dict:
    url = f"{_api_base(context)}{path}"
    response = requests.request(
        method, url, headers=_headers(context), timeout=REQUEST_TIMEOUT, **kwargs
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {url}: {response.text[:500]}",
            response=response,
        )
    return response.json()


def pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return uid


def create_client(context: dict, first: str = "first", last: str = None) -> dict:
    """Create a client with a unique name and return {id, name, email, portal_token}.

    The name must be unique: the estimate dialog's client picker matches by name, and
    all estimate tests share one account, so a fixed name would collide across tests."""
    stamp = int(time.time() * 1000)
    if last is None:
        last = f"last{stamp}"
    email = f"client+{stamp}@vmeetme.com"
    response = _api(
        context,
        "POST",
        "/platform/v1/clients",
        json={"first_name": first, "last_name": last, "email": email, "source_name": "automation"},
    )
    payload = response.get("data") or response
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")
    return {
        "id": client_id,
        "name": f"{client.get('first_name') or first} {client.get('last_name') or last}",
        "email": client.get("email") or email,
        "portal_token": payload.get("token") or response.get("token"),
    }


def set_tax_mode(context: dict, mode: str) -> None:
    """Set the account-wide tax mode ('include' or 'exclude') and verify it."""
    _api(context, "PUT", "/v2/settings", json={"tax_mode": mode})
    settings = _api(context, "GET", "/platform/v1/payment/settings")
    data = settings.get("data") or settings
    actual = (data.get("payment_settings") or data).get("tax_mode")
    if actual != mode:
        raise AssertionError(f"tax_mode did not update: expected {mode}, got {actual}")


def _estimate_client_id(estimate: dict) -> str:
    if estimate.get("client_id"):
        return estimate["client_id"]
    client = estimate.get("client") or {}
    return client.get("id") or client.get("uid")


def estimates_for_client(context: dict, client_id: str) -> list:
    """Return all estimates for a client, newest first, as [{uid, title}]."""
    response = _api(context, "GET", "/platform/v1/estimates?per_page=100")
    data = response.get("data") or response
    estimates = data.get("estimates") if isinstance(data, dict) else data
    mine = [e for e in (estimates or []) if _estimate_client_id(e) == client_id]
    mine.sort(key=lambda e: e.get("created_at") or "", reverse=True)
    return [{"uid": e.get("id") or e.get("uid"), "title": e.get("title")} for e in mine]


def latest_estimate_for_client(context: dict, client_id: str) -> dict:
    """Return the newest estimate for a client as {uid, title}."""
    mine = estimates_for_client(context, client_id)
    if not mine:
        raise AssertionError(f"No estimates returned for client {client_id}")
    return mine[0]


# --------------------------------------------------------------------------- #
# Frame scopes
# --------------------------------------------------------------------------- #
def billing_scope(page: Page):
    angular = page.locator('iframe[title="angularjs"]')
    try:
        angular.first.wait_for(state="visible", timeout=NAV_TIMEOUT)
        return page.frame_locator('iframe[title="angularjs"]')
    except Exception:
        return page


def wizard_scope(scope):
    editor = scope.locator("#vue_wizard_iframe")
    try:
        editor.first.wait_for(state="attached", timeout=NAV_TIMEOUT)
        return scope.frame_locator("#vue_wizard_iframe")
    except Exception:
        return scope


def _collect_text(page: Page) -> str:
    parts = []
    for frame in page.frames:
        try:
            parts.append(frame.locator("body").inner_text(timeout=UI_TIMEOUT))
        except Exception:
            continue
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Open the estimate dialog
# --------------------------------------------------------------------------- #
def _app_base(page: Page) -> str:
    match = re.match(r"(https?://[^/]+)", page.url)
    return match.group(1) if match else ""


def open_estimates_list(page: Page) -> None:
    """Load a fresh estimates list view. The app keeps the list URL even when showing
    an estimate's detail (master-detail), so always reload to guarantee the list view."""
    page.goto(f"{_app_base(page)}/app/payments/estimates", wait_until="domcontentloaded")
    billing = billing_scope(page)
    billing.get_by_role("button", name="New").first.wait_for(state="visible", timeout=NAV_TIMEOUT)


def open_new_estimate(page: Page, client_name: str):
    """Open the new-estimate dialog for a client. Returns (billing, wizard)."""
    open_estimates_list(page)
    billing = billing_scope(page)

    new_button = billing.get_by_role("button", name="New")
    new_button.first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    new_button.first.click()

    estimate_item = billing.get_by_role("menuitem", name="Estimate")
    estimate_item.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    estimate_item.first.click()

    _select_client(page, billing, client_name)

    wizard = wizard_scope(billing)
    wizard.locator('[data-qa="itemizable-details-header"]').first.wait_for(
        state="visible", timeout=NAV_TIMEOUT
    )
    return billing, wizard


def _select_client(page: Page, billing, client_name: str) -> None:
    dialog = billing.get_by_role("dialog")
    scope = dialog.first if dialog.count() > 0 else billing
    search = scope.locator("input").first
    search.wait_for(state="visible", timeout=UI_TIMEOUT)
    search.click()
    search.fill(client_name)
    page.wait_for_timeout(1500)

    candidate = scope.get_by_text(client_name, exact=True)
    if candidate.count() == 0:
        candidate = scope.get_by_text(client_name)
    candidate.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    candidate.first.click()


# --------------------------------------------------------------------------- #
# Fill the dialog
# --------------------------------------------------------------------------- #
def set_title(wizard, title: str) -> None:
    field = wizard.locator('[data-qa="itemizable-details-header"] input')
    if field.count() == 0:
        field = wizard.locator('[data-qa="itemizable-details-header"]')
    field.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    field.first.fill(title)


def add_existing_item(wizard, name: str) -> None:
    item_box = wizard.get_by_role("textbox", name="Please select an item")
    item_box.wait_for(state="visible", timeout=UI_TIMEOUT)
    item_box.click()
    option = wizard.get_by_role("option", name=re.compile(re.escape(name), re.I))
    if option.count() == 0:
        option = wizard.get_by_text(name, exact=True)
    if option.count() == 0:
        option = wizard.get_by_text(re.compile(re.escape(name), re.I))
    option.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.first.click()


def add_custom_item(wizard, name: str, price: str, description: str = "",
                    tax_name: str = "", tax_rate: str = "13", save_item: bool = False) -> None:
    item_box = wizard.get_by_role("textbox", name="Please select an item")
    item_box.wait_for(state="visible", timeout=UI_TIMEOUT)
    item_box.click()
    wizard.get_by_text("Add custom item", exact=True).first.click(timeout=UI_TIMEOUT)

    dialog = wizard.locator('[data-qa="custom-item-dialog"]')
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)

    wizard.locator('[data-qa="item-name"]').first.fill(name, timeout=UI_TIMEOUT)
    if description:
        wizard.locator('[data-qa="item-description"]').first.fill(description, timeout=UI_TIMEOUT)
    wizard.locator('[data-qa="price"]').first.fill(price, timeout=UI_TIMEOUT)

    if save_item:
        checkbox = wizard.locator('[data-qa="display-product-checkbox"]')
        if checkbox.count() > 0:
            checkbox.first.wait_for(state="attached", timeout=UI_TIMEOUT)
            checkbox.first.evaluate("el => el.click()")  # hidden Vuetify checkbox
    if tax_name:
        _select_tax(wizard, tax_name, tax_rate)

    wizard.locator('[data-qa="vc-footer-Add"]').first.click(timeout=UI_TIMEOUT)
    dialog.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _select_tax(wizard, tax_name: str, tax_rate: str = "13") -> None:
    """Open the tax picker and check the tax option (data-qa="tax-{name}-{rate}").

    The option is a Vuetify checkbox whose <input> is visually hidden, so toggle it
    with a native click rather than a Playwright click (which waits for visibility)."""
    wizard.locator(".tax-picker").first.click(timeout=UI_TIMEOUT)
    option = wizard.locator(f'[data-qa="tax-{tax_name}-{tax_rate}"]')
    if option.count() == 0:
        option = wizard.locator(f'[data-qa^="tax-{tax_name}"]')
    option.first.wait_for(state="attached", timeout=UI_TIMEOUT)
    option.first.evaluate("el => el.click()")
    # close the picker overlay so the Add button is reachable
    header = wizard.locator('[data-qa="custom-item-dialog-header"]')
    if header.count() > 0:
        header.first.click(timeout=UI_TIMEOUT)


def add_section(wizard, name: str) -> None:
    wizard.locator('[data-qa="add-section-button"]').first.click()
    section_input = wizard.locator('[data-qa="add-section-input"] input, [data-qa="add-section-input"]')
    section_input.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    section_input.first.fill(name)
    wizard.locator('[data-qa="add-section-save"]').first.click()


OPTIONAL_TIMEOUT = 2000  # best-effort, unverified fields — fail fast rather than block


def set_billing_address(wizard, address: str) -> None:
    """Set the sender (From) billing address, mirroring the legacy flow: expand the
    From fold, click edit, type, then collapse.

    Best-effort: this field is optional and is not asserted in any back-office or
    client-portal view (exactly as in the legacy test), so a failure here must not
    block estimate creation and should fail fast."""
    fold = wizard.locator('[data-qa="itemizable-from-fold"]').first
    try:
        if fold.count() > 0:
            fold.click(timeout=OPTIONAL_TIMEOUT)
        edit_button = wizard.locator('[data-qa="itemizable-from-business-address-edit-button"]')
        if edit_button.count() > 0:
            edit_button.first.click(timeout=OPTIONAL_TIMEOUT)
        field = wizard.locator('[data-qa="itemizable-from-business-address-edit"] textarea')
        field.first.fill(address, timeout=OPTIONAL_TIMEOUT)
        save = wizard.locator('[data-qa="itemizable-from-business-address-save"]')
        if save.count() > 0:
            save.first.click(timeout=OPTIONAL_TIMEOUT)
        if fold.count() > 0:
            fold.click(timeout=OPTIONAL_TIMEOUT)
    except Exception as exc:
        print(f"    [set_billing_address] skipped optional address: {exc}")


def reorder_first_two_items(page: Page, wizard, from_index: int = 0, to_index: int = 1) -> bool:
    """Move the item at from_index to to_index in the sortable list. Returns True if the
    order changed. Mirrors the legacy reorder action so the asserted item order matches."""
    list_el = wizard.locator('[data-qa="vc-draggable-list"]')
    if list_el.count() == 0:
        return False
    rows = wizard.locator('[data-qa="vc-draggable-list--item"]')
    before = _row_texts(rows)

    # Mirror the legacy reorder: drive the draggable component's Vue instance
    # directly (updatePosition + end listener), which a synthetic mouse drag on
    # SortableJS does not reliably trigger.
    list_el.first.evaluate(
        "(el, [from, to]) => {"
        "  const vm = el.__vue__;"
        "  vm.updatePosition(from, to);"
        "  vm.$listeners.end({ oldIndex: from, newIndex: to });"
        "}",
        [from_index, to_index],
    )
    page.wait_for_timeout(500)

    after = _row_texts(wizard.locator('[data-qa="vc-draggable-list--item"]'))
    return before != after and len(after) == len(before)


def _row_texts(rows) -> list:
    texts = []
    for index in range(rows.count()):
        try:
            texts.append(rows.nth(index).inner_text()[:40])
        except Exception:
            texts.append("")
    return texts


def send_estimate(wizard) -> None:
    send = wizard.get_by_role("button", name=re.compile(r"^Send$", re.I))
    send.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    send.first.click()


# --------------------------------------------------------------------------- #
# Back-office assertions
# --------------------------------------------------------------------------- #
def open_bo_estimate(page: Page, context: dict, estimate_uid: str):
    app_base = (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")
    page.goto(f"{app_base}/app/payments/estimates/{estimate_uid}", wait_until="domcontentloaded")
    billing_scope(page)
    # Wait for the estimate detail to actually render (a price always appears) rather
    # than a blind sleep, capped at the iframe-load NAV_TIMEOUT.
    deadline = time.time() + NAV_TIMEOUT / 1000
    while time.time() < deadline:
        if "$" in _collect_text(page):
            break
        page.wait_for_timeout(250)
    return billing_scope(page)


def assert_bo_estimate(page: Page, *, title: str, price: str, state: str,
                       client: str, items: list, total: str,
                       ordered_names: list = None) -> None:
    text = _collect_text(page)
    _assert_contains(text, title, "BO estimate title")
    _assert_contains(text, f"${price}", "BO estimate price")
    _assert_contains(text, state, "BO estimate state")
    _assert_contains(text, client, "BO estimate client")
    _assert_contains(text, f"${total}", "BO estimate total")
    for item in items:
        _assert_contains(text, item["name"], f"BO item {item['name']}")
        if item.get("description"):
            _assert_contains(text, item["description"], f"BO item desc {item['name']}")
        _assert_contains(text, f"${item['price']}", f"BO item price {item['name']}")
    if ordered_names:
        positions = [text.find(name) for name in ordered_names]
        if any(pos < 0 for pos in positions):
            raise AssertionError(f"BO ordered items not all found: {ordered_names}")
        if positions != sorted(positions):
            raise AssertionError(
                f"BO items not in expected order {ordered_names} (positions {positions})"
            )


def assert_bo_section(page: Page, *, section_name: str, section_total: str,
                      section_item: dict) -> None:
    text = _collect_text(page)
    _assert_contains(text, section_name, "BO section name")
    _assert_contains(text, section_total, "BO section total")
    _assert_contains(text, section_item["name"], "BO section item")
    if section_item.get("description"):
        _assert_contains(text, section_item["description"], "BO section item desc")


def _assert_contains(haystack: str, needle: str, label: str) -> None:
    if needle and needle not in haystack:
        raise AssertionError(f"{label}: expected to find '{needle}' on the page")


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
def search_estimates_by_client(page: Page, client_name: str) -> list:
    """Filter the estimates list by client name; return result titles (top-to-bottom)."""
    open_estimates_list(page)
    page.wait_for_timeout(1500)
    billing = billing_scope(page)

    search = billing.get_by_placeholder(re.compile("client name", re.I))
    if search.count() == 0:
        search = billing.locator('input[name="name_filter"], input[placeholder*="client" i]')
    search.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    search.first.fill("")
    search.first.type(client_name, delay=20)
    page.wait_for_timeout(2000)

    titles = []
    rows = billing.get_by_text(re.compile(r"bestimate\s+#\d+"))
    for index in range(rows.count()):
        try:
            titles.append(rows.nth(index).inner_text().strip())
        except Exception:
            continue
    # de-duplicate preserving order, keep only the "bestimate #N" token
    seen, result = set(), []
    for raw in titles:
        match = re.search(r"bestimate\s+#\d+", raw)
        if match and match.group(0) not in seen:
            seen.add(match.group(0))
            result.append(match.group(0))
    return result


# --------------------------------------------------------------------------- #
# Client portal
# --------------------------------------------------------------------------- #
def open_cp_estimate_page(page: Page, context: dict, portal_token: str):
    """Open the client portal estimates list as the client (in a fresh context).

    Mirrors the legacy flow: load /site/{uid}/action?client_jwt=... (no route hash),
    then click the estimates menu item to reach the estimates list."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    cp_page.goto(url, wait_until="domcontentloaded")

    cp_frame = cp_page.frame_locator("#cp_iframe")
    estimates_menu = cp_frame.locator('[data-qa="client-area-menu-estimates"]')
    estimates_menu.first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    estimates_menu.first.click()
    cp_frame.locator(".estimates-list-page").first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return cp_page, cp_context


def create_estimate_api(context: dict, *, title: str, client_id: str, items: list,
                        billing_address: str = "susa, persia", currency: str = "USD") -> dict:
    """Create an estimate via API with free-form line items and return {uid, title}.

    Mirrors the legacy automation-js `user creates new estimate via API` setup
    (POST /platform/v1/estimates). ``items`` is a list of
    {"title", "amount", "description", "quantity"} dicts."""
    now = time.gmtime()
    estimate_date = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", now)
    due_date = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() + 30 * 86400))
    payload = {
        "title": title,
        "client_id": client_id,
        "address": billing_address,
        "currency": currency,
        "due_date": due_date,
        "estimate_date": estimate_date,
        "items": items,
        "send_email": False,
    }
    response = _api(context, "POST", "/platform/v1/estimates", json=payload)
    estimate = (response.get("data") or response).get("estimate") or response.get("estimate")
    uid = estimate.get("id") or estimate.get("uid")
    if not uid:
        raise AssertionError(f"Estimate API response did not include an id: {response}")
    return {"uid": uid, "title": estimate.get("title") or title}


# Client-portal estimate action selectors (verified live on integration).
_CP_ACTION = {
    "approve": {"button": 'button[data-qa="approve"]', "confirm": "button.approve-button-text"},
    "decline": {"button": 'button[data-qa="estimate-decline"]', "confirm": "button.decline-button-text"},
}


def cp_click(locator, *, timeout: int = UI_TIMEOUT) -> None:
    """Click a client-portal (Vue) element with a bounded timeout.

    The CP runs inside an Angular->Vue iframe where overlays/animations can
    transiently intercept pointer events. We wait for visibility, then click with
    an explicit (bounded) timeout, falling back to a forced click on intercept so
    a transient overlay can never stall on Playwright's 30s default."""
    locator.wait_for(state="visible", timeout=NAV_TIMEOUT)
    try:
        locator.scroll_into_view_if_needed(timeout=timeout)
    except Exception:
        pass
    try:
        locator.click(timeout=timeout)
    except Exception:
        locator.click(timeout=timeout, force=True)


def cp_perform_estimate_action(cp_page: Page, action: str) -> None:
    """Approve or decline the estimate shown on the open CP estimate detail page.

    Clicks the action button, waits for the confirmation dialog, and confirms.
    ``action`` is 'approve' or 'decline'. The estimate detail page must already be
    open (e.g. after assert_cp_estimate)."""
    selectors = _CP_ACTION[action]
    cp_frame = cp_page.frame_locator("#cp_iframe")
    cp_click(cp_frame.locator(selectors["button"]).first)
    dialog = cp_frame.locator(".dialog-containter")
    dialog.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    cp_click(cp_frame.locator(selectors["confirm"]).first)


def assert_cp_estimate_status(cp_page: Page, expected_status: str) -> None:
    """Wait until the CP estimate detail shows the expected status text.

    e.g. 'Declined on' after a decline, 'Approved on' after an approve. The status
    label renders asynchronously after the confirmation toast."""
    cp_frame = cp_page.frame_locator("#cp_iframe")
    body = cp_frame.locator("body")
    deadline = time.time() + NAV_TIMEOUT / 1000
    text = ""
    while time.time() < deadline:
        text = body.first.inner_text(timeout=NAV_TIMEOUT)
        if expected_status in text:
            return
        cp_page.wait_for_timeout(500)
    raise AssertionError(
        f"CP estimate status '{expected_status}' not found. Body:\n{text[:600]}"
    )


def assert_cp_estimate(cp_page: Page, *, title: str, price: str, client: str,
                       items: list, status_actions: list) -> None:
    cp_frame = cp_page.frame_locator("#cp_iframe")
    estimate_link = cp_frame.locator("span.payment-title", has_text=re.compile(re.escape(title)))
    cp_click(estimate_link.first)

    # Wait until the entity page has actually rendered the selected estimate's title
    # (the detail pane loads asynchronously after navigation).
    body = cp_frame.locator("body")
    deadline = time.time() + NAV_TIMEOUT / 1000
    text = ""
    while time.time() < deadline:
        text = body.first.inner_text(timeout=NAV_TIMEOUT)
        if title in text and client in text:
            break
        cp_page.wait_for_timeout(500)
    _assert_contains(text, title, "CP estimate title")
    _assert_contains(text, f"${price}", "CP estimate price")
    _assert_contains(text, client, "CP estimate client")
    for item in items:
        _assert_contains(text, item["name"], f"CP item {item['name']}")
        _assert_contains(text, f"${item['price']}", f"CP item price {item['name']}")
    found_action = any(re.search(action, text, re.I) for action in status_actions)
    if status_actions and not found_action:
        raise AssertionError(f"CP estimate status actions not found: {status_actions}")
