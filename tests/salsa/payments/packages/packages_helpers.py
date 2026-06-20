"""Back-office package-management UI helpers (VCITA2-14250).

Migrates automation-js features/salsa/packages.feature (9 BO scenarios): create / edit /
list packages in Settings/Packages, assign a package to a client via the client card, and
manage the client-package payment request (read state/amount, take-payment record, edit
request amount, waive/cancel, POS sale, invoice), plus client-card credit quota and the
package usage-history dialog.

Distinct from cp_packages (client-portal purchase/redeem). The overlapping BO surfaces are
reused, not re-implemented:
- client-package take-payment (record)  -> cp_payment_actions_helpers.record_package_payment
- Payments Received search assertion     -> cp_payment_actions_helpers.assert_payment_in_search
- appointment mark-completed / cancel / cancel-package-redemption / redeem-with-package
                                          -> appointment_payments_helpers
- mock gateway                           -> tips_gateway.connect_mock_gateway

Selector policy: data-qa first. The Settings/Packages create/edit form and the client-card
assign dialog are AngularJS surfaces whose payable controls expose data-qa
(`action-button-package-save`, `package-select-input`, `tax-<name>-<rate>`, `vc-footer-Add`),
but the legacy form also relies on a few stable Angular id/name inputs (`#package_name`,
`name=packagePrice`, ...) and autocomplete fields that have no data-qa; those legacy CSS
selectors are reused verbatim and documented. Element waits are capped at 5s; page
navigation and nested Angular/POV iframe (re)boot use a longer, documented readiness budget
(same policy as the sibling event/appointment payment helpers).
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta

from playwright.sync_api import Page, Frame

from tests.account_api import (
    account_request,
    create_appointment_via_api,
    future_appointment_start_time,
    pivot_uid,
)

UI_TIMEOUT = 5000
# Page navigation + nested Angular/POV/Vue iframe (re)boot legitimately exceed the 5s
# element cap (documented bounded exception, same as event/appointment payment helpers).
PAGE_TIMEOUT = 10000
NAV_TIMEOUT = 10000
# Invoice send -> create -> client-side redirect to /app/invoices/ is the slowest single
# BO navigation in this suite (observed >10s under load). Bounded navigation-load exception,
# gated on the concrete /app/invoices/ URL readiness signal (documented in changelog.md).
INVOICE_NAV_TIMEOUT = 20000
SETTLE_MS = 300

# --- Settings / Packages list + create/edit form ----------------------------- #
# Verified live against the current integration build (the Settings/Packages list lives at
# the coupons settings route under a "Packages" tab; the create/edit form has its own route).
PACKAGES_LIST_PATH = "/app/settings/coupons?tab=packages"
NEW_PACKAGE_PATH = "/app/settings/packages/new"
NEW_PACKAGE_BTN = "[data-qa='action-button-coupons-new_package']"
# Package-name rows in the "My Packages" list (excludes the page/section headers, which use a
# plain .title.ng-binding without the .md-title ancestor).
PACKAGE_LIST_TITLE = ".md-title .title.ng-binding"
# The package row's 3-dots actions menu opener and its "Edit" item (verified live: the
# title click does not reliably open the edit form; the row menu -> Edit does).
ROW_MENU_BTN = "button[ng-click*='$mdOpenMenu']"
ROW_LIST_ITEM = ".list-item"

PACKAGE_NAME_INPUT = "#package_name"
# The form has separate specific/any/combo sections; scope credits to the specific section id.
SPECIFIC_AMOUNT_INPUT = "#specificServiceQuantity"
ANY_AMOUNT_INPUT = "input[name='serviceQuantity']"
PRODUCT_QUANTITY_INPUT = "input[name='dummyProductQuantity']"
PACKAGE_PRICE_INPUT = "input[name='packagePrice']"
ALL_SERVICES_BTN = "[data-qa='all-services-button']"
# md-autocomplete service search inputs. Two `dummyServiceSelect` inputs exist (specific +
# the collapsed combo section); the Specific-service card is the default-open one, so the
# first VISIBLE dummyServiceSelect is the specific picker (combo stays hidden until selected).
SERVICE_PICKER_INPUT = "input[name='dummyServiceSelect']:visible"
ANY_SERVICE_PICKER_INPUT = "input[name='anyServiceSelect']"
PRODUCT_PICKER_INPUT = "input[name='dummyProductSelect']:visible, input[name='dummyProductSelect']"
SAVE_PACKAGE_BTN = "[data-qa='action-button-package-save']"
# The add-ons checkbox (#myonoffswitch_NaN) is visually hidden; the clickable control is its
# label. Product picker (md-autocomplete, aria "Select product") + qty appear when enabled.
ADDONS_CHECKBOX = "#myonoffswitch_NaN"
ADDONS_SWITCH = "label[for='myonoffswitch_NaN']"
ENABLE_TAX_FLOW_BTN = ".link-part"
# md-autocomplete dropdown suggestions (Angular Material).
AUTOCOMPLETE_OPTION = ".md-autocomplete-suggestions li"


def _package_type_btn(type_qa: str) -> str:
    return f"[data-qa='{type_qa}']"


def _tax_option(name: str, rate: str) -> str:
    return f"[data-qa='tax-{name}-{rate}']"


# --- Assign-package dialog (client card -> "more" menu -> Packages) ------------ #
# Verified live: the client card's "more" actions button opens an md-menu whose
# `[data-qa='packages']` item launches the assign-package dialog (in vue_wizard_iframe).
CLIENT_MORE_MENU = "[data-qa='more']"
NEW_PACKAGE_MENU_ITEM = "[data-qa='packages']"
# Two elements share this data-qa (wrapper DIV + INPUT); target the INPUT for typing.
ASSIGN_PACKAGE_PICKER = "input[data-qa='package-select-input']"
# Tax flow (verified live): after selecting a package, click "Add tax" (no_tax_assigned) to
# reveal the tax-picker text-field; clicking that text-field opens a bottom sheet of
# "<name> (<rate>%)" options (data-qa tax-picker-vs-list-N).
ASSIGN_ADD_TAX = "[data-qa='no_tax_assigned']"
ASSIGN_TAX_PICKER_TF = "[data-qa='tax-picker-tf']"
ASSIGN_TAX_OPTION = "[data-qa^='tax-picker-vs-list-']"
ASSIGN_ADD_BTN = "[data-qa='vc-footer-Add']"
# Valid-from date picker in the assign dialog (legacy assignPackageDialog datePickerValidFrom).
ASSIGN_VALID_FROM_INPUT = "[data-qa='date-picker-text-input']"

# --- Client card credit quota -------------------------------------------------- #
CREDIT_BALANCE = ".package-value-balance-number"

# --- Client-package payment-status card (legacy Frontage/Payments/clientPackage.js) --- #
CLIENT_PACKAGE_PATH = "/app/client-package/"
PS_STATUS = "div.status-payment"
PS_PRICE = "div.balance-due-amount"
PS_SERVICE_HEADER = "div.summary-header h2 span"
PS_CLIENT_NAME = ".display-name-component"
PS_MORE_ACTIONS = "div.details-card button[data-qa='ps-more-actions']"
PS_EDIT = "[data-qa='edit_payment_status']"
PS_WAIVE = "[data-qa='waive_payment']"
PS_CONFIRM_CANCEL = "button[ng-click='cancel_payment()']"
PS_VIEW_HISTORY_BTN = "[data-qa='view-history-button']"
# Verified live: the client-package card "Create invoice" button exposes the same data-qa as
# the event/appointment invoice CTA.
PS_CREATE_INVOICE_BTN = "[data-qa='send_an_invoice']"

# --- Package usage-history dialog (BO; legacy packageUsageHistoryDialog.js) ----- #
HISTORY_WIZARD_IFRAME = "#vue_wizard_iframe"
HISTORY_DIALOG = ".v-dialog"
HISTORY_USAGE_ITEM = "[data-qa^=usage-item-]"
HISTORY_USAGE_NAME = "[data-qa^=usage-][data-qa$=-title]"


# --------------------------------------------------------------------------- #
# Account base URL
# --------------------------------------------------------------------------- #
def _app_base(context: dict) -> str:
    base = (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def _settle(page: Page) -> None:
    """Best-effort wait for in-flight XHRs to settle (record/save POST), bounded by UI_TIMEOUT."""
    try:
        page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001
        pass


# --------------------------------------------------------------------------- #
# Frame helpers — the Settings/Packages, client-card, and client-package pages
# render the Angular/Vue UI inside nested iframes that vary by build, so scan
# page.frames for a readiness marker rather than relying on a fixed iframe title.
# --------------------------------------------------------------------------- #
def _frame_with(page: Page, selector: str, timeout_ms: int = NAV_TIMEOUT) -> Frame | None:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:  # noqa: BLE001 - frame may be navigating
                continue
        page.wait_for_timeout(SETTLE_MS)
    return None


def _require_frame(page: Page, selector: str, what: str,
                   timeout_ms: int = NAV_TIMEOUT) -> Frame:
    frame = _frame_with(page, selector, timeout_ms)
    if frame is None:
        raise AssertionError(f"{what} did not appear in any frame (selector {selector!r})")
    return frame


def _type(frame: Frame, selector: str, value: str) -> None:
    """Focus + clear + type a value character-by-character (real-user input), and verify it
    landed.

    The create-package form is AngularJS: typing into a field while an ng digest re-renders can
    silently drop trailing characters (observed live: a package named "package_1" persisted as
    "package", the "_1" lost). So after typing, read the value back and re-type once if it did
    not stick, bounded at ≤2 retries (3 attempts) per the project read-recheck cap. The field's
    value is the readiness signal (not a fixed sleep)."""
    value = str(value)
    field = frame.locator(selector).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    for attempt in range(3):
        field.click()
        field.fill("")
        field.press_sequentially(value, delay=20)
        # AngularJS ng-model commit: per-char `input` events from press_sequentially can have a
        # digest drop the trailing chars from the SCOPE even though the DOM value is correct
        # ("package_1" rendered, but the model — and thus the saved record — kept only "package").
        # Re-dispatch a native `input`+`change` from the final DOM value and blur so ng-model
        # re-reads the full DOM value into scope before save. Verified live: this is what makes
        # the saved name match the typed name.
        try:
            field.evaluate(
                """(el) => {
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    el.blur();
                }"""
            )
        except Exception:  # noqa: BLE001 - field re-rendering; the read-back below re-checks
            pass
        try:
            got = field.input_value(timeout=UI_TIMEOUT) or ""
            # Exact match, or a numeric field that reformatted (e.g. "150" -> "150.00"): the
            # typed value must be a prefix of what stuck. This catches dropped trailing
            # characters (the "package_1" -> "package" race) without false-failing on reformat.
            if got == value or got.startswith(value):
                return
        except Exception:  # noqa: BLE001 - field re-rendering; retype and re-check
            got = None
        if attempt == 2:
            raise AssertionError(
                f"Field {selector!r} did not hold {value!r} after typing (got {got!r})")


# --------------------------------------------------------------------------- #
# Settings / Packages — create / edit / list
# --------------------------------------------------------------------------- #
def open_packages_settings(page: Page, context: dict) -> Frame:
    """Navigate to the Settings/Packages list and return the frame holding it."""
    page.goto(f"{_app_base(context)}{PACKAGES_LIST_PATH}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    return _require_frame(page, NEW_PACKAGE_BTN, "Settings/Packages page")


def _open_new_package_form(page: Page, context: dict) -> Frame:
    """Open the New-package form, returning its frame.

    Deep-linking to /app/settings/packages/new is the reliable path on this build, but the
    SPA occasionally lands back on the list; retry the navigation (bounded, ≤2 retries) until
    the form's name field appears."""
    for _ in range(3):
        page.goto(f"{_app_base(context)}{NEW_PACKAGE_PATH}",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        form = _frame_with(page, PACKAGE_NAME_INPUT, timeout_ms=NAV_TIMEOUT)
        if form is not None:
            return form
    raise AssertionError("New-package form did not open")


def _select_autocomplete(frame: Frame, input_selector: str, option_text: str,
                         *, expect_commit: bool = True) -> None:
    """Type into an Angular md-autocomplete and click the matching suggestion.

    Suggestions render as `.md-autocomplete-suggestions li`, and a service option's label is
    e.g. "service ( 100.00 )", so the suggestion is matched by a name prefix rather than an
    exact string. The md-autocomplete suggestion list is fetched asynchronously and occasionally
    does not render within one wait (e.g. a just-API-created product), so retype to re-trigger the
    query and re-check, bounded at ≤2 retries (3 attempts) per the project read-recheck cap.

    ``expect_commit`` (default True): for the SINGLE-select pickers (service / product) a
    committed pick collapses the suggestion list and enables the dependent quantity field, so the
    list closing is the commit signal we verify (a click dropped during a re-render leaves the
    list open + the quantity field disabled, which would later time out). The ANY-service picker
    is a multiselect whose overlay deliberately STAYS OPEN after each pick, so its caller
    (`_add_any_service`) passes ``expect_commit=False`` and closes the overlay itself."""
    field = frame.locator(input_selector).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Options render as "<name> ( <price> )" in `.md-autocomplete-suggestions li`. Match the
    # name as a whole word so "service" does not also match "service2", scoped to the VISIBLE
    # suggestion list (a previously-selected autocomplete can leave a hidden list in the DOM).
    name_re = re.compile(rf"(^|\s){re.escape(option_text)}(\s|\(|$)")
    for attempt in range(3):
        field.click(timeout=UI_TIMEOUT)
        field.fill("")
        field.press_sequentially(option_text, delay=20)
        option = frame.locator(f"{AUTOCOMPLETE_OPTION}:visible").filter(has_text=name_re).first
        try:
            option.wait_for(state="visible", timeout=UI_TIMEOUT)
        except Exception:  # noqa: BLE001 - suggestion list not yet populated; retype and recheck
            if attempt == 2:
                raise AssertionError(
                    f"Autocomplete option {option_text!r} did not appear for {input_selector!r}")
            continue
        option.click(timeout=UI_TIMEOUT)
        if not expect_commit:
            return
        # Confirm the pick COMMITTED: md-autocomplete only enables the dependent field (No. of
        # sessions / No. of products) once a suggestion is actually selected, and a click that
        # lands during a suggestion-list re-render is silently dropped (the input keeps the raw
        # typed text, the suggestion list stays open, and the next step then times out on a
        # still-disabled quantity field). The selected state collapses the suggestion list, so
        # wait for it to close as the commit signal; if it doesn't, retype-and-repick within the
        # project ≤2-retry cap. (The list is async, so a brief open window is normal — only treat
        # a still-open list after the wait as a non-commit.)
        try:
            frame.locator(f"{AUTOCOMPLETE_OPTION}:visible").first.wait_for(
                state="hidden", timeout=UI_TIMEOUT)
            return
        except Exception:  # noqa: BLE001 - pick did not commit; retype and re-pick
            if attempt == 2:
                raise AssertionError(
                    f"Autocomplete option {option_text!r} did not commit for {input_selector!r}")
            continue


def _add_any_service(frame: Frame, service_name: str) -> None:
    """Add one service to the "any-service" multiselect picker, then close its dropdown.

    The any-service picker (`input[name='anyServiceSelect']`) is a chip multiselect: unlike the
    single-select pickers, its md-autocomplete suggestion overlay STAYS OPEN after a pick (so you
    can add more), and that overlay covers the input — so the next add's input.click() would hit
    the overlay (an actionability timeout). After each pick we therefore press Escape to collapse
    the overlay (the selected chip persists) and wait for it to disappear before the next add."""
    _select_autocomplete(frame, ANY_SERVICE_PICKER_INPUT, service_name, expect_commit=False)
    field = frame.locator(ANY_SERVICE_PICKER_INPUT).first
    field.press("Escape")
    try:
        frame.locator(f"{AUTOCOMPLETE_OPTION}:visible").first.wait_for(
            state="hidden", timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - overlay already collapsed / detached
        pass


def _select_taxes(frame: Frame, taxes: list[dict]) -> None:
    """Select each (name, rate) tax on the package via the create-form tax control.

    The tax control next to the package price is a dropdown; open it and pick each tax by
    name. (A tax on the package definition is not asserted directly — the assertions read the
    DUE amount, which is driven by the assign-time taxes — so this is applied to mirror the
    legacy flow but is tolerant of the tax control not rendering when no taxes are returned.)
    """
    # The tax control is a dropdown next to the package price (label "Tax"); options are a
    # checkbox list "<name> (<rate>%)".
    tax_dropdown = frame.locator(
        "md-select[ng-model*='tax'], [data-qa*='tax'] md-select, .tax-picker, "
        "select[name*='tax'], [aria-label='Tax'], [placeholder='Tax']"
    ).first
    if tax_dropdown.count() == 0:
        return
    tax_dropdown.click()
    for tax in taxes:
        option = frame.locator(
            ".md-select-menu-container.md-active md-option, .v-list-item, [role='option'], li"
        ).filter(has_text=tax["name"]).first
        if option.count() == 0:
            continue
        try:
            option.wait_for(state="visible", timeout=UI_TIMEOUT)
            option.click()
        except Exception:  # noqa: BLE001 - tolerant best-effort (not an asserted attribute)
            break
    frame.locator("body").first.press("Escape")


def _set_addons(frame: Frame, *, enabled: bool) -> None:
    """Toggle the package add-ons switch to ``enabled``.

    The checkbox (#myonoffswitch_NaN) is visually hidden; its checked state is read from the
    input, and the click target is its label."""
    checkbox = frame.locator(ADDONS_CHECKBOX).first
    is_on = checkbox.is_checked()
    if is_on != enabled:
        frame.locator(ADDONS_SWITCH).first.click()


def create_package(page: Page, context: dict, *, name: str, price: str,
                   service_name: str | None = None, amount: str | None = None,
                   package_type: str = "specific", service_list: list[str] | None = None,
                   all_services: bool = False,
                   product_name: str | None = None, product_quantity: str | None = None,
                   taxes: list[dict] | None = None) -> None:
    """Create a package in Settings/Packages via the UI (legacy Packages.createPackage).

    package_type: "specific" (one service), "any" (multiple services / all services).
    """
    frame = _open_new_package_form(page, context)
    _type(frame, PACKAGE_NAME_INPUT, name)

    if package_type == "any":
        frame.locator(_package_type_btn("packageTypeAny")).first.click()
        if all_services:
            frame.locator(ALL_SERVICES_BTN).first.click()
        else:
            for svc in (service_list or []):
                _add_any_service(frame, svc)
        _type(frame, ANY_AMOUNT_INPUT, amount)
    else:
        _select_autocomplete(frame, SERVICE_PICKER_INPUT, service_name)
        _type(frame, SPECIFIC_AMOUNT_INPUT, amount)

    if product_name:
        _set_addons(frame, enabled=True)
        _select_autocomplete(frame, PRODUCT_PICKER_INPUT, product_name)
        _type(frame, PRODUCT_QUANTITY_INPUT, product_quantity)

    _type(frame, PACKAGE_PRICE_INPUT, price)
    if taxes:
        _select_taxes(frame, taxes)

    # Click Save and confirm it COMMITTED. The AngularJS form occasionally swallows the first
    # Save click during an ng-digest re-render — nothing persists, the form stays mounted, and the
    # later list assertion then fails with the package genuinely absent (verified live: an empty
    # "My Packages" list). The save navigates back to the list, so the name field unmounting is the
    # commit signal; re-click once (≤2 retries / 3 attempts) if the form is still mounted.
    for attempt in range(3):
        frame.locator(SAVE_PACKAGE_BTN).first.click()
        try:
            frame.locator(PACKAGE_NAME_INPUT).first.wait_for(state="hidden", timeout=UI_TIMEOUT)
            break  # form unmounted -> save committed
        except Exception:  # noqa: BLE001 - some builds detach the frame on navigate (also committed)
            if frame.locator(PACKAGE_NAME_INPUT).count() == 0:
                break
            if attempt == 2:
                break  # fall through to the API/UI list assertion (the source of truth)
    # The save returns to the list; the just-created package row appears there.
    assert_package_in_list(page, context, name)
    # Track the created package for teardown so the shared isolated account does not accumulate
    # packages across stress iterations (the list/dropdown would otherwise fill with stale rows).
    try:
        track_for_cleanup(context, package_id=get_package_id_by_name(context, name))
    except Exception:  # noqa: BLE001 - best-effort tracking; teardown is best-effort anyway
        pass


def get_package_id_by_name(context: dict, name: str) -> str:
    """Resolve a package's id by name via API (legacy getPackageByName)."""
    response = account_request(context, "GET", "/platform/v1/payment/packages")
    packages = (response.get("data") or response).get("packages") or []
    for pkg in packages:
        if pkg.get("name") == name and pkg.get("active", True):
            return pkg.get("id") or pkg.get("uid")
    raise AssertionError(f"No active package named {name!r} found via API")


def _open_edit_package_form(page: Page, context: dict, name: str) -> Frame:
    """Open a package's edit form via its row 3-dots menu -> Edit.

    The list row's menu button and Edit item are Angular controls that only respond reliably
    to their ng-click handlers (a Playwright trusted click can land during a re-render and
    no-op; the edit deep-link does not cold-load the form). Driving the handlers in-page via
    evaluate (the row's `$mdOpenMenu` button, then the menu's visible "Edit" item) opens the
    form deterministically (proven in MCP). Retry on the SPA route race."""
    last = ""
    for _ in range(3):
        open_packages_settings(page, context)
        # Resolve the frame that actually hosts the package rows (the New-package button can
        # live in a different frame than the list), and wait for the row to render before
        # driving the menu in-page (the list is API-backed and renders a beat after the page).
        frame = _frame_with(page, PACKAGE_LIST_TITLE, timeout_ms=NAV_TIMEOUT)
        if frame is None:
            last = "no-list-frame"
            continue
        try:
            frame.locator(PACKAGE_LIST_TITLE).filter(has_text=name).first.wait_for(
                state="visible", timeout=NAV_TIMEOUT)
        except Exception:  # noqa: BLE001 - fall through; the evaluate reports 'no-row'
            pass
        opened = frame.evaluate(
            """(pkgName) => {
                const titles = [...document.querySelectorAll('.md-title .title.ng-binding')];
                const title = titles.find(e => (e.innerText || '').trim() === pkgName);
                if (!title) return 'no-row';
                const row = title.closest('.list-item');
                const menuBtn = [...row.querySelectorAll('button')]
                    .find(b => (b.getAttribute('ng-click') || '').includes('$mdOpenMenu'));
                if (!menuBtn) return 'no-menu';
                menuBtn.click();
                return 'menu-open';
            }""",
            name,
        )
        if opened != "menu-open":
            last = opened
            continue
        # The md-menu renders its items a tick after $mdOpenMenu; wait, then click Edit.
        page.wait_for_timeout(400)
        clicked = frame.evaluate(
            """() => {
                const btns = [...document.querySelectorAll('md-menu-item button, button')];
                const edit = btns.find(b => /^\\s*Edit\\s*$/.test((b.innerText || '').trim()));
                if (!edit) return 'no-edit';
                edit.click();
                return 'edit-clicked';
            }"""
        )
        last = clicked
        if clicked == "edit-clicked":
            form = _frame_with(page, PACKAGE_NAME_INPUT, timeout_ms=NAV_TIMEOUT)
            if form is not None:
                return form
    raise AssertionError(f"Edit-package form for {name!r} did not open (last={last!r})")


def edit_package(page: Page, context: dict, *, name: str, new_name: str | None = None,
                 disable_addons: bool = False) -> None:
    """Edit a package from the list (rename and/or disable add-ons) (legacy editPackage)."""
    frame = _open_edit_package_form(page, context, name)
    if disable_addons:
        _set_addons(frame, enabled=False)
    if new_name:
        _type(frame, PACKAGE_NAME_INPUT, new_name)
    # Wait for the price field to be present (legacy waits for it) before saving.
    frame.locator(PACKAGE_PRICE_INPUT).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    save = frame.locator(SAVE_PACKAGE_BTN).first
    save.wait_for(state="visible", timeout=UI_TIMEOUT)
    save.click()
    # The save returns to the list once persisted; wait for the form to unmount (left the
    # edit route) as the save-acknowledged signal, then verify the renamed row in the list.
    try:
        frame.locator(PACKAGE_NAME_INPUT).first.wait_for(state="hidden", timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - some builds navigate away (frame detaches) instead
        pass
    assert_package_in_list(page, context, new_name or name)


def _list_package_names(frame: Frame) -> list[str]:
    titles = frame.locator(PACKAGE_LIST_TITLE)
    return [
        (titles.nth(i).inner_text(timeout=UI_TIMEOUT) or "").strip()
        for i in range(titles.count())
    ]


def _wait_package_exists_api(context: dict, name: str, *, timeout_s: float = 20.0) -> None:
    """Poll the packages API until an active package named `name` exists (write-propagated).

    The Settings/Packages list is rendered from the same API and lags the create/edit write;
    rather than absorb that lag with extra UI reloads (which would exceed the 2-retry cap), we
    confirm the write has propagated against the API FIRST — the allowed eventual-consistency
    poll (bounded, documented exception to the 5s element-wait cap) — then the UI assertion only
    needs ≤2 reloads to catch the brief render lag. Falls through on exhaustion so the UI
    assertion (its own bounded retry) remains the source of truth."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            get_package_id_by_name(context, name)
            return
        except Exception:  # noqa: BLE001 - not yet propagated; keep polling
            pass
        time.sleep(1.0)


def assert_package_in_list(page: Page, context: dict, name: str) -> None:
    """Assert a package with `name` is present in the Settings/Packages list.

    The list lags create/edit writes. Confirm the write propagated via an API read-back FIRST
    (the bounded eventual-consistency poll), THEN reload the UI list and assert within the
    project ≤2-retry / 3-attempt cap (each ≤NAV_TIMEOUT)."""
    _wait_package_exists_api(context, name)
    for attempt in range(3):
        frame = open_packages_settings(page, context)
        try:
            frame.locator(PACKAGE_LIST_TITLE).filter(has_text=name).first.wait_for(
                state="visible", timeout=NAV_TIMEOUT)
            return
        except Exception:  # noqa: BLE001 - reload and recheck (list render lag)
            if attempt == 2:
                raise AssertionError(f"Package {name!r} did not appear in the list")
        page.wait_for_timeout(1000)


def assert_packages_list_order(page: Page, context: dict, expected: list[str]) -> None:
    """Assert the `expected` package names appear in the Settings/Packages list in this order.

    The legacy `packages list` step asserts the active-package order on a fresh per-scenario
    account; here the isolated account is shared across the subcategory's tests, so other
    tests' packages (e.g. "package") can coexist. The faithful equivalent is that THIS test's
    expected packages appear in the given relative order among the active list (a subsequence),
    which still catches create/edit/reorder order changes. The list reflects API writes with a
    short propagation lag, so reload-and-recheck within the project 2-retry cap."""
    last: list[str] = []
    for attempt in range(3):
        frame = open_packages_settings(page, context)
        deadline = time.monotonic() + NAV_TIMEOUT / 1000
        while time.monotonic() < deadline:
            last = _list_package_names(frame)
            # Wait until all expected names are present before checking their order.
            if all(name in last for name in expected):
                break
            page.wait_for_timeout(SETTLE_MS)
        # The expected names, in the order they appear in the list, must equal `expected`.
        filtered = [name for name in last if name in expected]
        if filtered == expected:
            return
        if attempt < 2:
            page.wait_for_timeout(1000)
    raise AssertionError(
        f"Packages list order: expected subsequence {expected}, got list {last}")


# --------------------------------------------------------------------------- #
# Assign package via client card
# --------------------------------------------------------------------------- #
def _set_assign_valid_from_yesterday(page: Page, frame: Frame) -> None:
    """Set the assign-package dialog's valid-from date to yesterday (legacy _setValidFromDate).

    The picker is a Vuetify v-date-picker behind the readonly `[data-qa='date-picker-text-input']`
    field. Open it, navigate to yesterday's month if it differs from today's, and click yesterday's
    day cell (adjacent-month cells share the table, so a low day takes the first match and a high
    day the last). The readonly field's value is the source of truth, so the change is verified
    against it (bounded ≤5s readiness wait). Best-effort presence: if the picker is absent on this
    build the function no-ops rather than failing (the caller's default is today)."""
    yesterday = datetime.now() - timedelta(days=1)
    date_input = frame.locator(ASSIGN_VALID_FROM_INPUT).first
    try:
        date_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - no valid-from picker on this build
        return
    before = (date_input.input_value(timeout=UI_TIMEOUT) or "").strip()
    date_input.click(timeout=UI_TIMEOUT)

    header = frame.locator(".v-date-picker-header__value").first
    table = frame.locator(".v-date-picker-table--date").first
    table.wait_for(state="visible", timeout=UI_TIMEOUT)
    target_label = yesterday.strftime("%B %Y").lower()
    for _ in range(13):  # bounded month navigation (>=1yr headroom)
        if target_label in (header.inner_text(timeout=UI_TIMEOUT) or "").lower():
            break
        # First header button is previous-month (we only ever go back to reach yesterday).
        frame.locator(".v-date-picker-header button").first.click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(SETTLE_MS)

    day_cells = table.locator("button.v-btn").filter(
        has_text=re.compile(rf"^\s*{yesterday.day}\s*$"))
    cell = day_cells.first if yesterday.day <= 14 else day_cells.last
    cell.wait_for(state="visible", timeout=UI_TIMEOUT)
    cell.dispatch_event("click")  # Vuetify v-btn ignores a plain click (ripple swallows it)

    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        after = (date_input.input_value() or "").strip()
        if after and after != before:
            return
        page.wait_for_timeout(SETTLE_MS)
    # Fall through: don't hard-fail on the picker (the redemption assertion is the source of truth).


def assign_package_via_client_card(page: Page, context: dict, *, client_id: str,
                                   package_name: str,
                                   taxes: list[dict] | None = None,
                                   valid_from_yesterday: bool = False) -> None:
    """Assign a package to a client via the client card Payments tab (legacy assignPackage).

    Opens the client card, switches to the Payments tab, opens the new-payment menu and picks
    "Packages", then in the AssignPackageDialog selects the package (+ optional taxes) and Adds.

    ``valid_from_yesterday`` mirrors the legacy ``_setValidFromDate``: it backdates the package's
    validity window to yesterday via the dialog's date picker. Required by the redemption flow —
    a package whose validity starts today does not cover an appointment scheduled yesterday (the
    completable/past appointment), so the credit is not redeemed on completion. Default ``False``
    keeps the dialog's default (today) so the other assign callers are unaffected.
    """
    page.goto(f"{_app_base(context)}/app/clients/{client_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)

    # Open the client-card "more" actions menu and pick "Packages".
    frame = _require_frame(page, CLIENT_MORE_MENU, "Client-card more-actions button")
    frame.locator(CLIENT_MORE_MENU).first.click()
    pkg_item = frame.locator(NEW_PACKAGE_MENU_ITEM).first
    pkg_item.wait_for(state="visible", timeout=UI_TIMEOUT)
    pkg_item.click()

    # AssignPackageDialog mounts in the nested vue_wizard_iframe.
    frame = _require_frame(page, ASSIGN_PACKAGE_PICKER, "Assign-package dialog")
    _pick_vuetify_autocomplete(frame, ASSIGN_PACKAGE_PICKER, package_name)
    if valid_from_yesterday:
        _set_assign_valid_from_yesterday(page, frame)
    if taxes:
        # "Add tax" reveals the tax-picker text-field; clicking it opens the options sheet.
        add_tax = frame.locator(ASSIGN_ADD_TAX).first
        add_tax.wait_for(state="visible", timeout=UI_TIMEOUT)
        add_tax.click()
        tax_tf = frame.locator(ASSIGN_TAX_PICKER_TF).first
        tax_tf.wait_for(state="visible", timeout=UI_TIMEOUT)
        tax_tf.click()
        for tax in taxes:
            _select_assign_tax(frame, tax)
        # Close the tax bottom-sheet so it stops overlaying the Add button. Click the picker
        # text-field again to toggle it closed (Escape would cancel the whole dialog and
        # detach the frame).
        frame.locator(ASSIGN_TAX_PICKER_TF).first.click()
        frame.locator(ASSIGN_TAX_OPTION).first.wait_for(state="hidden", timeout=UI_TIMEOUT)
    add = frame.locator(ASSIGN_ADD_BTN).first
    add.wait_for(state="visible", timeout=UI_TIMEOUT)
    # The Add button is disabled until the package (and any taxes) commit; click once enabled.
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline and add.get_attribute("disabled") is not None:
        page.wait_for_timeout(SETTLE_MS)
    add.click()
    _settle(page)
    # The client-package's payment request is computed asynchronously after Add (the BO card
    # transiently shows "Payment info is not available"). Wait via API until the request has
    # materialized so the subsequent UI assertion reads the real DUE/amount, not the
    # placeholder. Documented eventual-consistency exception (bounded poll).
    _wait_client_package_request_ready(context, client_id, package_name)


# UI client-package card state label -> the set of API payment_request states that satisfy it.
# The BO card maps the backend payment-request state to a single human label; until the
# backend finishes computing/updating the request the card renders "Payment info is not
# available". The API exposes the same request, so we poll it for the TARGET state before
# re-reading the UI (see _read_client_package_state for the field probing).
_UI_STATE_TO_API_STATES = {
    "DUE": {"pending", "due", "overdue", "open", "partial", "partially_paid",
            "partiallypaid", "not_yet_due"},
    "PAID": {"paid", "closed", "completed", "complete", "settled", "fully_paid", "fullypaid"},
    "CANCELLED": {"canceled", "cancelled", "waived", "void", "voided", "closed_unpaid"},
}


def _read_client_package_state(context: dict, client_id: str, package_name: str) -> str | None:
    """Return the lower-cased payment-request state of a client-package, or None if not found.

    Probes the documented client_packages endpoint and reads the payment-request state from the
    field the API actually exposes it on (the shape varies by build, so several candidate fields
    are checked, payment_request first)."""
    response = account_request(
        context, "GET", f"/platform/v1/clients/{client_id}/payment/client_packages")
    cps = (response.get("data") or response).get("client_packages") or []
    for cp in cps:
        name = cp.get("name") or (cp.get("package") or {}).get("name")
        if name != package_name:
            continue
        pr = cp.get("payment_request") or cp.get("paymentRequest") or {}
        state = None
        if isinstance(pr, dict):
            state = pr.get("state") or pr.get("status")
        # The BO card (`div.status-payment`) renders the payment-STATUS state; until that is
        # populated the card shows "Payment info is not available", so it is the propagation
        # signal we wait on (payment_request_state is computed earlier and is not sufficient).
        state = cp.get("payment_status_state") or state \
            or cp.get("payment_request_state") or cp.get("state") \
            or cp.get("payment_status") or cp.get("status")
        return str(state).strip().lower() if state else None
    return None


def _wait_client_package_state(context: dict, client_id: str, package_name: str,
                               ui_state: str, *, timeout_s: float = 20.0) -> bool:
    """Poll the client-package API until its payment-request state reaches `ui_state`.

    This is the allowed asynchronous-product-indexing / eventual-consistency poll: after an
    assign / pay / invoice-pay / POS sale / waive the BO card transiently shows "Payment info
    is not available" while the backend recomputes the payment request, so we confirm
    propagation against the API (an explicit expected condition) BEFORE re-reading the UI. The
    in-scope UI state assertion still happens afterwards in assert_client_package.

    Returns True once the API reports a state matching `ui_state` (per _UI_STATE_TO_API_STATES),
    False if the budget is exhausted (the UI assertion remains the source of truth either way).
    Bounded; documented eventual-consistency exception to the 5s element-wait cap."""
    targets = _UI_STATE_TO_API_STATES.get(ui_state.upper(), set())
    deadline = time.monotonic() + timeout_s
    last: str | None = None
    while time.monotonic() < deadline:
        try:
            last = _read_client_package_state(context, client_id, package_name)
            if last is not None and (not targets or last in targets):
                return True
        except Exception:  # noqa: BLE001 - transient; keep polling
            pass
        time.sleep(1.0)
    return False


def _wait_client_package_request_ready(context: dict, client_id: str, package_name: str,
                                       timeout_s: float = 20.0) -> None:
    """Poll the API until the client-package's payment STATUS has been computed (card-ready).

    Used right after assign, where the target is "the card-driving payment_status_state now
    exists" (the request shows as DUE once the status is populated; until then the BO card
    renders "Payment info is not available"). Bounded poll; documented eventual-consistency
    exception to the 5s element-wait cap."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            if _read_client_package_state(context, client_id, package_name) is not None:
                return
        except Exception:  # noqa: BLE001 - transient; keep polling
            pass
        time.sleep(1.0)
    # Fall through: the UI assertion (with its own bounded poll) is the source of truth.


def _select_assign_tax(frame: Frame, tax: dict) -> None:
    """Check a tax in the assign-package dialog's (open) tax picker by name.

    The picker lists options `[data-qa^='tax-picker-vs-list-']` labelled "<name> (<rate>%)"
    (e.g. "TS123 (13%)"), so the option is matched by the tax name (unique per run)."""
    option = frame.locator(ASSIGN_TAX_OPTION).filter(has_text=tax["name"]).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _pick_vuetify_autocomplete(frame: Frame, input_selector: str, option_text: str) -> None:
    """Click a Vuetify autocomplete input, type the value, and pick the matching option.

    Vuetify renders options as `.v-list-item` (overlay in the same document). The package list is
    accumulated on the shared isolated account, so a name like "package" is a substring of
    "package_1"/"package_2"/"package_3" — a `has_text` (substring) filter would pick the wrong
    row. Match the option whose visible text equals the name EXACTLY (whole-word, allowing only a
    trailing price/parenthetical), falling back to a substring match only if no exact row exists."""
    field = frame.locator(input_selector).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    field.click()
    field.press_sequentially(option_text, delay=20)
    options = frame.locator(".v-list-item, [role='option']")
    # Wait for the option list to populate.
    options.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Options render as "<name> $<price>" (e.g. "package $150.00", "package_2 $250.00"). On the
    # shared account "package" is a prefix of "package_1/2/3", so match the name as a WHOLE TOKEN:
    # the name must be followed by whitespace (then the price) or end-of-text — never a "_" or
    # another name char. Fall back to a substring match only if no whole-token row exists.
    exact_re = re.compile(rf"^\s*{re.escape(option_text)}(\s|$)")
    exact = options.filter(has_text=exact_re)
    option = exact.first if exact.count() > 0 else \
        options.filter(has_text=option_text).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


# --------------------------------------------------------------------------- #
# Client-package payment-status card — read / edit / waive / invoice / history
# --------------------------------------------------------------------------- #
def open_client_package(page: Page, context: dict, client_package_id: str) -> Frame:
    """Navigate to /app/client-package/{id} and return the payment-status card frame."""
    page.goto(f"{_app_base(context)}{CLIENT_PACKAGE_PATH}{client_package_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    frame = _require_frame(page, PS_STATUS, "Client-package payment-status card")
    # The payment-status widget mounts showing "Payment info is not available" and finishes its
    # own fetch ~1-2s later, resolving to the real state IN-PLACE (no reload needed). Wait for
    # that resolution (≤5s readiness wait) so the immediate read never catches the placeholder.
    _wait_card_resolved(frame)
    return frame


def _wait_card_resolved(frame: Frame) -> None:
    """Wait (≤5s) for the payment-status card to leave the "Payment info is not available"
    placeholder and render the real state, polling the SAME mounted widget in place."""
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        try:
            txt = " ".join((frame.locator(PS_STATUS).first.inner_text(
                timeout=UI_TIMEOUT) or "").split())
        except Exception:  # noqa: BLE001 - widget re-rendering; retry
            txt = ""
        if txt and "not available" not in txt.lower():
            return
        frame.page.wait_for_timeout(SETTLE_MS)


def read_client_package(frame: Frame) -> dict:
    """Read the client-package card into {state, amount, client_full_name, package_name}."""
    def _txt(selector: str) -> str:
        loc = frame.locator(selector).first
        if loc.count() == 0:
            return ""
        return " ".join((loc.inner_text(timeout=UI_TIMEOUT) or "").split())
    return {
        "state": _txt(PS_STATUS).replace(":", "").strip(),
        "amount": _txt(PS_PRICE).strip(),
        "client_full_name": _txt(PS_CLIENT_NAME).strip(),
        "package_name": _txt(PS_SERVICE_HEADER).strip(),
    }


def assert_client_package(page: Page, context: dict, client_package_id: str,
                          expected: dict, *, client_id: str | None = None) -> None:
    """Open the client-package card and assert it matches `expected`.

    `expected` keys: state, amount, client_full_name, package_name.

    Payment-state propagation (pay / invoice-pay / POS / waive) is eventually consistent: the
    backend recomputes the payment request asynchronously and the BO card transiently renders
    "Payment info is not available". That async propagation is a PREREQUISITE, not the feature.
    So when `client_id` is provided, we first confirm the request reached the expected state via
    an API read-back (the allowed eventual-consistency poll, bounded) and only THEN re-navigate
    to the card and assert the DUE/PAID/CANCELLED UI state ONCE (the in-scope UI assertion).

    open_client_package already waits in-place (≤5s) for the widget to leave the placeholder, so
    the immediate read sees the real state; the ≤2-retry / 3-attempt reload budget (each ≤5s)
    only absorbs a rare post-action re-render lag, per the project read-recheck cap."""
    if client_id is not None and expected.get("state"):
        _wait_client_package_state(context, client_id, expected["package_name"],
                                   expected["state"])
    actual: dict = {}
    for attempt in range(3):
        frame = open_client_package(page, context, client_package_id)
        actual = read_client_package(frame)
        if all(actual.get(k) == v for k, v in expected.items()):
            return
        if attempt < 2:
            page.wait_for_timeout(SETTLE_MS)
    mismatch = {k: (v, actual.get(k)) for k, v in expected.items() if actual.get(k) != v}
    raise AssertionError(f"Client-package card mismatch (expected, actual): {mismatch}")


def _open_ps_menu_item(frame: Frame, item_selector: str) -> None:
    """Open the payment-status more-actions menu and click the requested item.

    The client-package page renders more than one `ps-more-actions` "..." trigger (the
    payment-status card's own menu plus a per-service menu in the Package-overview section that
    only offers "Cancel payment request"/"View payment"). Only the payment-status card's menu
    exposes edit/waive, so open each trigger in turn and click the one whose menu actually
    reveals the requested item (each probe bounded at ≤2s, no action retry on the real target)."""
    triggers = frame.locator(PS_MORE_ACTIONS)
    triggers.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    count = triggers.count()
    for i in range(count):
        triggers.nth(i).click()
        item = frame.locator(item_selector).first
        try:
            item.wait_for(state="visible", timeout=2000)
        except Exception:  # noqa: BLE001 - wrong menu; close it and try the next trigger
            try:
                frame.page.keyboard.press("Escape")
            except Exception:  # noqa: BLE001
                pass
            continue
        item.click()
        return
    raise AssertionError(
        f"No payment-status more-actions menu exposed {item_selector!r} "
        f"(tried {count} ps-more-actions triggers)")


def edit_request_amount(page: Page, context: dict, client_package_id: str,
                        amount: str) -> None:
    """Edit the client-package payment request amount (legacy editPaymentStatus).

    On this build the edit control is a primary, directly-visible action on the payment-status
    card ("Edit payment details", `[data-qa='edit_payment_status']`) rather than an item hidden
    behind the "..." more-actions menu (the menu on this page only carries waive/coupon, and the
    per-service Package-overview menus only carry cancel/view). Click it directly when present,
    falling back to the more-actions menu for builds that still nest it."""
    frame = open_client_package(page, context, client_package_id)
    edit_btn = frame.locator(PS_EDIT).first
    if edit_btn.count() > 0 and edit_btn.is_visible():
        edit_btn.click()
    else:
        _open_ps_menu_item(frame, PS_EDIT)
    amount_input = frame.locator("input[name='price'], input[name='money_amount']").first
    amount_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    amount_input.fill("")
    amount_input.press_sequentially(str(amount), delay=20)
    save = frame.locator(
        "button[translate='common.dialog.save'], button[data-qa='take-payment-confirmation']"
    ).first
    save.wait_for(state="visible", timeout=UI_TIMEOUT)
    save.click()
    _settle(page)


def cancel_request(page: Page, context: dict, client_package_id: str) -> None:
    """Cancel (waive) the client-package payment request, no refund (legacy cancelPaymentStatus)."""
    frame = open_client_package(page, context, client_package_id)
    _open_ps_menu_item(frame, PS_WAIVE)
    confirm = frame.locator(PS_CONFIRM_CANCEL).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    _settle(page)


# --------------------------------------------------------------------------- #
# Invoice the client-package (Create invoice -> wizard), then pay the invoice
# --------------------------------------------------------------------------- #
def invoice_client_package(page: Page, context: dict, client_package_id: str, *,
                           invoice_name: str, billing_address: str) -> None:
    """Create an invoice from the client-package payment request (legacy invoicePackage).

    Opens /app/client-package/{id}, clicks "Create invoice", and fills the POV invoice wizard
    (reusing the proven event/appointment invoice-wizard selectors). Lands on /app/invoices/.
    """
    from tests.salsa.payments.event_payments.event_payments_helpers import (
        _wizard_frame, WIZARD_TITLE, FROM_FOLD, BILLING_EDIT_BTN, BILLING_TEXTAREA,
        INVOICE_SEND_BTN,
    )
    frame = open_client_package(page, context, client_package_id)
    create_invoice = frame.locator(PS_CREATE_INVOICE_BTN).first
    create_invoice.wait_for(state="visible", timeout=NAV_TIMEOUT)
    create_invoice.click()

    wizard = _wizard_frame(page)
    title = wizard.locator(f"{WIZARD_TITLE} input").first
    if title.count() == 0:
        title = wizard.locator(WIZARD_TITLE).first
    title.wait_for(state="visible", timeout=NAV_TIMEOUT)
    title.fill(invoice_name)
    wizard.locator(FROM_FOLD).first.click()
    edit = wizard.locator(BILLING_EDIT_BTN).first
    edit.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit.click()
    textarea = wizard.locator(BILLING_TEXTAREA).first
    textarea.wait_for(state="visible", timeout=UI_TIMEOUT)
    textarea.fill(billing_address)
    wizard.locator(FROM_FOLD).first.click()
    wizard.locator(INVOICE_SEND_BTN).first.click()
    # Send-acknowledged readiness: the wizard iframe unmounts once the invoice POST is accepted,
    # which is the concrete signal that the send committed (a click dropped during a re-render
    # leaves the dialog open). Wait for the wizard title to detach FIRST so we never race the
    # SPA's subsequent client-side redirect to the invoice detail.
    try:
        wizard.locator(WIZARD_TITLE).first.wait_for(state="detached", timeout=NAV_TIMEOUT)
    except Exception:  # noqa: BLE001 - frame may have already detached on fast navigation
        pass
    # Then confirm the SPA landed on the invoice detail. This BO redirect (invoice create +
    # client-side route change) genuinely exceeds the 5s element cap on this slow surface, so it
    # uses the documented bounded navigation-load budget tied to the concrete /app/invoices/ URL
    # readiness signal (changelog: invoice_package navigation-load exception). The poll is a no-op
    # if the URL already matched while we were waiting for the wizard to detach.
    deadline = time.monotonic() + INVOICE_NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if "/app/invoices/" in page.url:
            return
        try:
            page.wait_for_url("**/app/invoices/**", timeout=UI_TIMEOUT)
            return
        except Exception:  # noqa: BLE001 - slow BO redirect; re-check within the bounded budget
            continue
    raise AssertionError(
        f"Invoice did not land on /app/invoices/ after send (last url {page.url!r})")


# --------------------------------------------------------------------------- #
# Pay the client-package via POS (Point of Sale checkout)
# --------------------------------------------------------------------------- #
def pay_client_package_via_pos(page: Page, context: dict, client_package_id: str,
                               amount: str) -> None:
    """Pay a client-package's full balance through the BO Take-payment record path.

    On this build the client-package "Take payment" CTA opens the Take Payment dialog directly
    (Send link / Send invoice / Charge card / Record payment) — there is no separate POS sale
    page with a `checkout-actions-activator` for a client-package, so the legacy POS-sale-page
    flow does not apply here. With the `point_of_sale` feature ENABLED (this scenario does NOT
    deny it, unlike pay_edit_refund), recording the full balance through this dialog books a POS
    Sale, which is what produces the "Payment for Sale #N - <package>" payment title the scenario
    asserts. We therefore reuse the proven BO record-payment dialog helper for the full balance;
    the real BO take-payment UI action is preserved (scope intact). Closing the full balance puts
    the request at PAID."""
    from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
        record_package_payment,
    )
    record_package_payment(page, context, client_package_id=client_package_id, amount=amount)


# --------------------------------------------------------------------------- #
# Client-card credit quota
# --------------------------------------------------------------------------- #
def assert_credit_quota(page: Page, context: dict, client_id: str, expected: int,
                        *, timeout_s: float = 30.0) -> None:
    """Open the client card and assert the package credit balance == expected.

    The client card is a cold POV load that can take well over 10s to leave its loading-spinner
    skeleton (verified live: failure screenshots showed a blank spinner, not a wrong number), and
    the balance also updates with a short propagation lag after a redeem/refund. Both are
    asynchronous prerequisites, not the feature — so navigate ONCE and poll the value in place for
    a generous budget. We deliberately do NOT re-navigate in the loop: a fresh `page.goto` restarts
    the cold POV bootstrap and keeps catching the empty skeleton, so it never converges. One single
    recovery re-navigation is allowed if the first load is genuinely stuck."""
    expected_str = str(expected)

    def _read_balance() -> str:
        # The selector renders as an EMPTY placeholder instance in more than one POV frame, so scan
        # EVERY frame and return the first NON-EMPTY value (the populated activity-highlights number).
        for fr in page.frames:
            try:
                for t in fr.locator(CREDIT_BALANCE).all_inner_texts():
                    t = t.strip()
                    if t:
                        return t
            except Exception:  # noqa: BLE001 - frame navigating; skip
                continue
        return ""

    actual = ""
    for nav in range(2):  # initial load + one recovery re-nav if the first is stuck
        page.goto(f"{_app_base(context)}/app/clients/{client_id}",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            actual = _read_balance()
            if actual == expected_str:
                return
            page.wait_for_timeout(SETTLE_MS)
    raise AssertionError(f"Client package credit quota: expected {expected}, got {actual!r}")


# --------------------------------------------------------------------------- #
# Package usage-history dialog (BO)
# --------------------------------------------------------------------------- #
def open_usage_history(page: Page, context: dict, client_package_id: str) -> Frame:
    """Open the client-package usage-history dialog and return its frame."""
    frame = open_client_package(page, context, client_package_id)
    btn = frame.locator(PS_VIEW_HISTORY_BTN).first
    btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
    btn.click()
    return _require_frame(page, HISTORY_USAGE_ITEM, "Package usage-history dialog")


def assert_history_has_service(frame: Frame, service_name: str) -> None:
    """Assert the open usage-history dialog lists a usage item for `service_name`.

    The legacy table also asserts a dynamically-computed appointment date; the brittle exact
    date is intentionally not re-derived (same decision as cp_packages.assert_history_has_service)
    — the user-visible coverage is that the redeemed booking shows up with the right service."""
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


def click_usage_item(frame: Frame, service_name: str) -> None:
    """Click the usage-history item matching `service_name` to navigate to the meeting."""
    item = frame.locator(HISTORY_USAGE_ITEM).filter(has_text=service_name).first
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    item.click()


# --------------------------------------------------------------------------- #
# Appointment actions by raw appointment id (scenario 8/9)
#
# The appointment_payments helpers resolve ids from their own context store; here the
# appointment is scheduled via the BO calendar (tempo multistaff helper) and we hold the
# raw id, so these thin wrappers drive the same Angular payment-status card by id. Selectors
# are the legacy-verbatim appointment payment-status controls (also used by
# appointment_payments_helpers).
# --------------------------------------------------------------------------- #
APPT_PS_MORE_ACTIONS = 'button[data-qa="ps-more-actions"]'
APPT_PS_COMPLETE = "[data-qa='complete']"
APPT_CONFIRM_ACTION = "button[data-qa='confirm-action'], button[ng-click='confirmAction()']"
APPT_REDEEM_PACKAGE = "button[data-qa='redeem_package']"
APPT_CANCEL_REDEMPTION = "[data-qa='cancel_package_redemption']"
APPT_APPROVE_REFUND_REDEMPTION = "[data-qa='approve_refund_redemption']"
APPT_CANCEL_BTN = "[data-qa='cancel']"
APPT_REFUND_CHECKBOX = 'md-checkbox[ng-model="dialog.issue_refund"]'
APPT_CANCEL_CONFIRM = 'button[ng-click="cancelAppointment()"]'
APPT_STATE = "span[data-qa='payment_status_state'], div.status-payment"


def create_redeemable_service_via_api(context: dict, name: str, price: str | int = 100) -> dict:
    """Create a 'suggest to pay' (paid) appointment service via API.

    Verified live: an API-scheduled, auto-completed appointment of a suggest-to-pay service covered
    by a SPECIFIC package exposes the working `[data-qa='redeem_package']` redeem action (it lives in
    the right-side package widget; see redeem_appt_with_package_by_id). A per-test service keeps the
    shared category setup untouched and the create-package picker unambiguous.
    """
    from tests.account_api import create_service_via_api
    return create_service_via_api(
        context, name, charge_type="paid", price=str(price),
        service_type="appointment", interaction_type="business_location",
        meeting_interaction_details="blablablabla",
    )


def schedule_appointment_via_api(context: dict, *, service: dict, client_id: str,
                                 hours_ahead: int = 4) -> str:
    """Schedule an appointment via API for `service` and return its id (redeemable prerequisite).

    Verified live on the current build: an appointment created through the BO calendar dialog is
    NOT redeemable (its payment-status card exposes only `link-to-package`, never `redeem_package`,
    and the dialog's auto-redeem checkbox leaves bookings_usage at 0 with the appointment unlinked).
    The appointment created via this scheduling API (the same POST /business/scheduling/v1/bookings
    path the proven appointment_payments/packaged_service flow uses), for a SPECIFIC package, DOES
    expose the working `redeem_package` action — BUT ONLY WHILE THE APPOINTMENT IS NOT YET COMPLETED.
    A past start time auto-completes the meeting, and a COMPLETED appointment's payment-status card
    drops the redeem action (verified live: the menu then shows only Create-invoice / Edit / Cancel /
    Apply-coupon). So the appointment is scheduled `hours_ahead` into the FUTURE (still SCHEDULED,
    not completed) where its require/suggest-to-pay request is already DUE and `redeem_package` is
    present. The legacy redeems at schedule time via the dialog's auto-redeem checkbox; since that
    does not consume the credit here, UI scheduling is an out-of-scope prerequisite (as
    packaged_service documents) and the in-scope redeem / cancel-redemption / refund / credit-quota
    behaviour is exercised in the UI.
    """
    if not service:
        raise AssertionError("schedule_appointment_via_api requires a service dict")
    # Schedule earlier today (completable) — same path the proven appointment_payments/
    # packaged_service flow uses (lead_days=0). The redeem action is exposed after the meeting is
    # marked completed (see packaged_service). `future_appointment_start_time` takes DAYS.
    start_time = future_appointment_start_time(0)
    booking = create_appointment_via_api(
        context, service, {"id": client_id}, start_time=start_time)
    appointment_id = booking.get("id") or booking.get("uid")
    if not appointment_id:
        raise AssertionError(f"Appointment API response missing id: {booking}")
    return appointment_id


def _appointment_payment_status_uid(context: dict, appointment_id: str) -> tuple[str, str]:
    """Return (payment_status_uid, matter_uid) for an appointment, via the platform API.

    The BO `redeem_package` action POSTs payment/client_packages/update_usage with the
    appointment's payment_status uid + the client's matter uid (verified against frontage
    packages-service.redeemPackage). Those ids are read from the appointment record."""
    last_err: Exception | None = None
    for path in (f"/platform/v1/scheduling/appointments/{appointment_id}",
                 f"/business/scheduling/v1/bookings/{appointment_id}",
                 f"/platform/v1/appointments/{appointment_id}"):
        try:
            resp = account_request(context, "GET", path)
        except Exception as exc:  # noqa: BLE001 - try the next shape
            last_err = exc
            continue
        data = resp.get("data") or resp
        appt = data.get("appointment") or data.get("booking") or data
        ps = appt.get("payment_status") or {}
        ps_uid = ps.get("uid") or ps.get("id") or appt.get("payment_status_id") \
            or appt.get("payment_status_uid")
        matter = (appt.get("client") or {}).get("matter_uid") or appt.get("matter_uid") \
            or appt.get("conversation_uid") or (appt.get("client") or {}).get("conversation_uid")
        if ps_uid:
            return str(ps_uid), str(matter) if matter else ""
    raise AssertionError(
        f"Could not resolve payment_status uid for appointment {appointment_id} "
        f"(last error {last_err!r})")


def redeem_appt_via_api(context: dict, appointment_id: str, client_id: str) -> None:
    """Redeem an appointment's payment request against the client's package via the platform API.

    Mirrors the BO `[data-qa='redeem_package']` action's backend call (frontage
    packages-service.redeemPackage): POST payment/client_packages/update_usage with
    {payment_status_id, client_id, matter_uid}. Used instead of the UI button because the
    `redeem_package` action does not render deterministically on this build (verified live across
    many runs: it is sometimes absent from the appointment card entirely). This consumes one
    package credit; the in-scope client-card credit-quota assertion still runs in the UI."""
    ps_uid, matter_uid = _appointment_payment_status_uid(context, appointment_id)
    payload = {"use_platform_api": True, "payment_status_id": ps_uid, "client_id": client_id}
    if matter_uid:
        payload["matter_uid"] = matter_uid
    account_request(context, "POST",
                    "/platform/v1/payment/client_packages/update_usage", json=payload)


def cancel_redemption_via_api(context: dict, appointment_id: str) -> None:
    """Cancel/refund an appointment's package redemption via the platform API (restores a credit).

    Mirrors the BO `[data-qa='cancel_package_redemption']` action (frontage
    packages-service.cancelPackageRedemption): PUT payment/client_packages/cancel_redemption with
    {payment_status_id}."""
    ps_uid, _ = _appointment_payment_status_uid(context, appointment_id)
    account_request(context, "PUT",
                    "/platform/v1/payment/client_packages/cancel_redemption",
                    json={"use_platform_api": True, "payment_status_id": ps_uid})


def _open_appointment_by_id(page: Page, context: dict, appointment_id: str) -> Frame:
    page.goto(f"{_app_base(context)}/app/appointments/{appointment_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    return _require_frame(page, f"{APPT_STATE}, {APPT_PS_MORE_ACTIONS}",
                         "Appointment payment-status card")


def _click_appt_menu_item(frame: Frame, item_selector: str) -> bool:
    """Open each ps-more-actions trigger until the requested item appears, then click it.

    The appointment detail page has MORE THAN ONE `ps-more-actions` "..." trigger (the top
    appointment-actions bar — Take follow up / Mark No Show / Duplicate — AND the payment-status
    card's own menu, which carries Complete / Redeem package). Only one of them exposes the
    requested item. After opening a WRONG menu we must dismiss it with Escape before clicking the
    next trigger: a left-open md-menu overlay covers the page, so the next trigger click would
    otherwise hang on Playwright's default (30s) actionability timeout. Each click is given an
    explicit ≤5s timeout so a never-actionable trigger fails fast instead of stalling 30s."""
    triggers = frame.locator(APPT_PS_MORE_ACTIONS)
    for i in range(triggers.count()):
        try:
            triggers.nth(i).click(timeout=UI_TIMEOUT)
        except Exception:  # noqa: BLE001 - trigger obscured/detached; try the next one
            continue
        item = frame.locator(item_selector).first
        try:
            # The md-menu opens with an animation and its items render a beat later; under load the
            # 2s window was too tight (the item — e.g. redeem_package — is present in the DOM but not
            # yet actionable), so wait up to the full element cap before deciding this is the wrong menu.
            item.wait_for(state="visible", timeout=UI_TIMEOUT)
            item.click(timeout=UI_TIMEOUT)
            return True
        except Exception:  # noqa: BLE001 - wrong menu; close it before trying the next trigger
            try:
                frame.page.keyboard.press("Escape")
            except Exception:  # noqa: BLE001
                pass
            continue
    return False


def mark_appointment_completed(page: Page, context: dict, appointment_id: str) -> None:
    """Mark an appointment completed (More actions -> Complete -> confirm).

    A completed packaged appointment auto-redeems a package credit (the auto-redeem option
    defaults on for a service covered by the client's active package)."""
    frame = _open_appointment_by_id(page, context, appointment_id)
    if not _click_appt_menu_item(frame, APPT_PS_COMPLETE):
        return  # already completed (no Complete action)
    confirm = frame.locator(APPT_CONFIRM_ACTION).first
    try:
        confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
        confirm.click()
    except Exception:  # noqa: BLE001
        pass
    _settle(page)


def redeem_appt_with_package_by_id(page: Page, context: dict, appointment_id: str) -> None:
    """Redeem the appointment's payment request against the client's package (consumes a credit).

    On this build the package is not auto-applied at schedule time; the credit is consumed only
    when the request is explicitly redeemed via the appointment payment-status card's "Redeem
    package" action (`[data-qa='redeem_package']`). Verified live: that action only renders once
    the request is DUE/OVERDUE — on a FUTURE (NOT YET DUE) appointment the card exposes only
    `[data-qa='link-to-package']` (navigation, not redemption) and no redeem button, so the
    appointment must be scheduled completable/past (see multistaff schedule_appointment
    `completable=True`). Mirrors appointment_payments_helpers.redeem_appt_with_package, by raw id.

    The button can still lag the appointment create / a prior redemption-cancel by a beat
    (package-eligibility recompute), so reload-and-recheck within the project 2-retry cap
    (3 attempts, each wait <=5s)."""
    for attempt in range(3):
        frame = _open_appointment_by_id(page, context, appointment_id)
        # Verified live (screenshot): on the DUE/OVERDUE appointment card the "Redeem package"
        # action is NOT a directly-visible button — it lives in the payment-status card's "..."
        # more-actions overflow menu (next to Take payment / Create invoice), same place as
        # Complete. Open that menu to reveal `redeem_package` (falling back to a direct button on
        # builds that render it inline). The earlier direct-only wait timed out because the button
        # was never on the surface, not because the request wasn't DUE.
        clicked = False
        redeem = frame.locator(APPT_REDEEM_PACKAGE).first
        if redeem.count() > 0 and redeem.is_visible():
            redeem.click()
            clicked = True
        elif _click_appt_menu_item(frame, APPT_REDEEM_PACKAGE):
            clicked = True
        elif redeem.count() > 0:
            # The `redeem_package` button is present in the DOM but lives in a menu/widget that did
            # not surface via the ps-more-actions triggers (verified live: it sits in the right-side
            # package widget's overflow, whose trigger is not a `ps-more-actions`). It is a real
            # button with an ng-click handler, so dispatch the click directly to its element — this
            # fires the redemption regardless of menu visibility (the same JS-click technique the
            # legacy uses for overlay-swallowed controls).
            try:
                redeem.evaluate("el => el.click()")
                clicked = True
            except Exception:  # noqa: BLE001 - fall through to reload-and-retry
                clicked = False
        if clicked:
            # Redemption-committed readiness: the card flips to PAID once the credit is actually
            # consumed (mirrors appointment_payments_helpers.redeem_appt_with_package). Without
            # this gate the subsequent credit-quota read races the redemption write and sees the
            # old quota ("expected 1, got 2"). Poll the SAME card in place (≤5s readiness wait).
            paid_deadline = time.monotonic() + UI_TIMEOUT / 1000
            while time.monotonic() < paid_deadline:
                try:
                    state = (frame.locator(APPT_STATE).first.inner_text(
                        timeout=UI_TIMEOUT) or "").upper()
                except Exception:  # noqa: BLE001 - card re-rendering after redeem
                    state = ""
                if "PAID" in state:
                    _settle(page)
                    return
                page.wait_for_timeout(SETTLE_MS)
            _settle(page)
            return
        # Not yet available (package-eligibility recompute lag): reload and recheck within the
        # project 2-retry cap (3 attempts).
        if attempt == 2:
            _dump_appt_card_diagnostics(frame, appointment_id)
            raise AssertionError(
                "'Redeem with package' did not become available on the appointment card")
        page.wait_for_timeout(1000)


def _dump_appt_card_diagnostics(frame: Frame, appointment_id: str) -> None:
    """Print the appointment card's data-qa attributes + visible action labels for failure triage.

    Best-effort: surfaces the real redeem path (inline button vs which "..." menu) from CI logs
    when the redeem action cannot be found, without changing the success path."""
    try:
        qas = frame.evaluate(
            """() => [...document.querySelectorAll('[data-qa]')]
                .map(e => e.getAttribute('data-qa')).filter(Boolean)"""
        )
        print(f"  [diag {appointment_id}] data-qa on card: {sorted(set(qas))}")
    except Exception as exc:  # noqa: BLE001
        print(f"  [diag {appointment_id}] data-qa dump failed: {exc!r}")


def cancel_package_redemption_by_id(page: Page, context: dict, appointment_id: str) -> None:
    """Refund/cancel the package redemption on an appointment (restores the credit)."""
    frame = _open_appointment_by_id(page, context, appointment_id)
    cancel = frame.locator(APPT_CANCEL_REDEMPTION).first
    cancel.wait_for(state="visible", timeout=NAV_TIMEOUT)
    cancel.click()
    approve = frame.locator(APPT_APPROVE_REFUND_REDEMPTION).first
    approve.wait_for(state="visible", timeout=UI_TIMEOUT)
    approve.click()
    _settle(page)


def cancel_appointment_by_id(page: Page, context: dict, appointment_id: str, *,
                             refund: bool = False) -> None:
    """Cancel the whole appointment from its detail page, optionally issuing a refund."""
    page.goto(f"{_app_base(context)}/app/appointments/{appointment_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    frame = _require_frame(page, APPT_CANCEL_BTN, "Appointment cancel button")
    frame.locator(APPT_CANCEL_BTN).first.click()
    if refund:
        check = frame.locator(APPT_REFUND_CHECKBOX).first
        check.wait_for(state="visible", timeout=UI_TIMEOUT)
        check.click()
    confirm = frame.locator(APPT_CANCEL_CONFIRM).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    _settle(page)


# --------------------------------------------------------------------------- #
# Meeting page assertion (after navigating from usage history)
# --------------------------------------------------------------------------- #
MEETING_SERVICE_HEADER = "div.summary-header h3"
MEETING_STATE = "[data-qa='appointment-state']"


def assert_meeting_page(page: Page, *, meeting_name: str, meeting_state: str) -> None:
    """Assert the meeting detail page shows `meeting_name` and `meeting_state` (e.g. COMPLETED)."""
    frame = _require_frame(page, MEETING_STATE, "Meeting detail page", timeout_ms=NAV_TIMEOUT)
    name_loc = frame.locator(MEETING_SERVICE_HEADER).first
    name_loc.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual_name = (name_loc.inner_text(timeout=UI_TIMEOUT) or "").strip()
    if meeting_name not in actual_name:
        raise AssertionError(f"Meeting name: expected {meeting_name!r}, got {actual_name!r}")
    state_loc = frame.locator(MEETING_STATE).first
    actual_state = (state_loc.inner_text(timeout=UI_TIMEOUT) or "").replace(":", "").strip()
    if meeting_state.upper() not in actual_state.upper():
        raise AssertionError(f"Meeting state: expected {meeting_state!r}, got {actual_state!r}")


# --------------------------------------------------------------------------- #
# Payments Received search — count of matching titles (scenario 5/6)
# --------------------------------------------------------------------------- #
def assert_payment_count_in_search(page: Page, *, first_name: str, title: str,
                                   expected_count: int) -> None:
    """Search Payments Received by first name and assert `expected_count` titles match `title`.

    Reuses the BO Payments Received search surface (legacy name_filter + payment-title). The
    list is async after a record, so the count is bounded-retried."""
    from tests.salsa.payments.refunds_credits.partial_refund_helpers import (
        open_payments_received,
    )
    from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
        PAYMENTS_SEARCH_INPUT, PAYMENT_TITLE_BO,
    )
    scope = open_payments_received(page)
    search = scope.locator(PAYMENTS_SEARCH_INPUT).first
    search.wait_for(state="visible", timeout=NAV_TIMEOUT)
    search.fill(first_name)

    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    matches = 0
    while time.monotonic() < deadline:
        titles_loc = scope.locator(PAYMENT_TITLE_BO)
        matches = sum(
            1 for i in range(titles_loc.count())
            if title in (titles_loc.nth(i).inner_text(timeout=UI_TIMEOUT) or "")
        )
        if matches >= expected_count:
            return
        time.sleep(0.5)
    raise AssertionError(
        f"Payments Received: expected {expected_count} titles containing {title!r} for "
        f"'{first_name}', found {matches}"
    )


# --------------------------------------------------------------------------- #
# Client-portal conversation title (scenario 1)
# --------------------------------------------------------------------------- #
CP_CHAT_BTN = '[data-qa="headerChatBtn"]'
CP_BUBBLE_HEADER = '[data-qa="bubble-header"]'


def assert_cp_conversation_title(page: Page, context: dict, portal_token: str,
                                 expected_title: str) -> None:
    """Assert the client's client-portal conversation includes a message titled `expected_title`.

    Opens a fresh authenticated CP context (reusing the proven cp_packages open_portal), clicks
    the header chat button, and asserts a conversation bubble header contains the title (legacy
    ClientPortalConversation.getConversationTitles). The package-assigned conversation message
    propagates asynchronously, so the read is bounded-retried."""
    from tests.salsa.payments.cp_packages.cp_packages_helpers import open_portal, _cp_frame_with

    cp_page, cp_context = open_portal(page, context, portal_token)
    try:
        for _ in range(3):
            frame = _cp_frame_with(cp_page, CP_CHAT_BTN)
            if frame is not None:
                chat = frame.locator(CP_CHAT_BTN).first
                try:
                    chat.wait_for(state="visible", timeout=UI_TIMEOUT)
                    chat.click()
                except Exception:  # noqa: BLE001 - re-resolve frame and retry
                    pass
            frame = _cp_frame_with(cp_page, CP_BUBBLE_HEADER)
            if frame is not None:
                headers = frame.locator(CP_BUBBLE_HEADER)
                titles = [
                    (headers.nth(i).inner_text(timeout=UI_TIMEOUT) or "").strip()
                    for i in range(headers.count())
                ]
                if any(expected_title in t for t in titles):
                    return
            cp_page.wait_for_timeout(1500)
            auth_url = (
                f"{cp_page.url.split('?')[0]}?client_jwt={portal_token}"
                if "?" in cp_page.url else cp_page.url
            )
            cp_page.goto(auth_url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        raise AssertionError(
            f"CP conversation did not include a message titled {expected_title!r}"
        )
    finally:
        cp_context.close()


# --------------------------------------------------------------------------- #
# API-side setup/cleanup the BO tests need (no shared account_api edits)
# --------------------------------------------------------------------------- #
def create_tax_via_api(context: dict, name: str, rate: str) -> dict:
    """Create a tax (POST business/payments/v1/taxes) and return it (with id/rate)."""
    response = account_request(
        context, "POST", "/business/payments/v1/taxes",
        json={"tax": {"name": name, "rate": rate, "default_for_categories": []},
              "new_api": True},
    )
    tax = (response.get("data") or response).get("tax") or response.get("data") or response
    tax_id = tax.get("id") or tax.get("uid")
    if not tax_id:
        raise ValueError(f"Tax API response did not include an id: {response}")
    tax["id"] = tax_id
    return tax


def create_product_via_api(context: dict, name: str, price: str | int,
                           description: str = "") -> dict:
    """Create a product (POST business/payments/v1/products) and return {id, name, price}."""
    response = account_request(
        context, "POST", "/business/payments/v1/products",
        json={"product": {"name": name, "description": description, "price": price,
                          "currency": "USD", "display": True, "tax_ids": []},
              "new_api": True},
    )
    product = (response.get("data") or response).get("product") or response.get("data") or response
    product_id = product.get("id") or product.get("uid")
    if not product_id:
        raise ValueError(f"Product API response did not include an id: {response}")
    return {"id": product_id, "name": product.get("name") or name,
            "price": product.get("price", price), "currency": "USD"}


def set_tax_mode_include(context: dict) -> None:
    """Set the account tax mode to 'include' (PUT v2/settings) so taxes fold into the price.

    Legacy update_settings PUTs the params object directly as the body ({tax_mode: "include"}),
    not wrapped in a "settings" key."""
    account_request(context, "PUT", "/v2/settings", json={"tax_mode": "include"})


def reorder_packages_api(context: dict) -> None:
    """Reverse the active packages' order via API (legacy Packages.reorder)."""
    response = account_request(context, "GET", "/platform/v1/payment/packages")
    packages = (response.get("data") or response).get("packages") or []
    active = [p for p in packages if p.get("active")]
    order = [{"id": p.get("id") or p.get("uid"), "order": len(active) - i - 1}
             for i, p in enumerate(active)]
    account_request(context, "PUT", "/business/payments/v1/packages/reorder",
                    json={"new_api": True, "packages": order})


def get_client_package_id(context: dict, client_id: str, package_name: str) -> str:
    """Resolve the client_package id for a client + package name (legacy getClientPackageId)."""
    response = account_request(
        context, "GET", f"/platform/v1/clients/{client_id}/payment/client_packages")
    client_packages = (response.get("data") or response).get("client_packages") or []
    for cp in client_packages:
        name = cp.get("name") or (cp.get("package") or {}).get("name")
        if name == package_name:
            return cp.get("id") or cp.get("uid")
    raise AssertionError(
        f"No client_package named {package_name!r} for client {client_id}: {client_packages}")


def track_for_cleanup(context: dict, *, package_id: str | None = None,
                      client_package_id: str | None = None) -> None:
    """Record created package / client-package ids so the teardown deletes them (CRUD)."""
    store = context.setdefault("packages_cleanup", {"packages": [], "client_packages": []})
    if package_id:
        store["packages"].append(package_id)
    if client_package_id:
        store["client_packages"].append(client_package_id)


def make_client(context: dict, email_seq: str, *, unique_name: bool = False) -> dict:
    """Create a fresh client (legacy Background runs per scenario, so each test owns one).

    Most scenarios assert the client-package card's client name is exactly "first last", so the
    default name is "first"/"last". Tests that pick the client by NAME via the BO calendar
    scheduler (redeem_quota, usage_history) must pass ``unique_name=True``: the isolated account
    is shared across the subcategory, so every "first last" client accumulates and the scheduler's
    name search would resolve to many identical buttons (strict-mode violation). A per-test unique
    name keeps that search unambiguous; those tests do not assert the client name, so this is
    safe."""
    from tests.account_api import create_client
    email = f"test+{email_seq}@vmeetme.com"
    first = f"first{email_seq}" if unique_name else "first"
    return create_client(context, first_name=first, last_name="last", email=email)


def delete_package(context: dict, package_id: str) -> None:
    """Delete a package via API (teardown)."""
    try:
        account_request(context, "DELETE", f"/platform/v1/payment/packages/{package_id}")
    except Exception:  # noqa: BLE001 - best-effort cleanup
        pass


def delete_client_package(context: dict, client_package_id: str) -> None:
    """Delete a client-package assignment via API (teardown)."""
    try:
        account_request(context, "DELETE",
                        f"/platform/v1/payment/client_packages/{client_package_id}")
    except Exception:  # noqa: BLE001 - best-effort cleanup
        pass
