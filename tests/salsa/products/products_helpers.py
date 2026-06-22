"""Shared UI helpers for the import_products subcategories.

iframe topology on integration:
- Products settings header (Import button) lives in the frontage angular iframe.
- Products list / search / product tax live in the inner vuetage iframe.
- The Import wizard is a top-level POV modal (rendered on the main frame).

``_frame_with`` finds whichever frame currently holds a selector, so callers do
not hard-code the (changing) iframe nesting. All UI state waits honor the 5s cap;
the two genuinely asynchronous backend steps (file analysis after upload, and the
import-execution success screen) use a longer, documented bounded wait.
"""

import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000
# File analysis (upload -> "Add taxes") and import execution (-> success) are async
# backend jobs the wizard polls; bounded above the 5s UI cap for that processing.
# Under stress-test load the Excel-analysis job intermittently exceeded 15s, so this
# is bounded at 30s (same class as the backend-index waits elsewhere), not a selector
# wait used to mask flakiness.
IMPORT_JOB_TIMEOUT = 30000

PRODUCTS_URL_PATH = "/app/settings/products"

# Products page (angular header + vuetage list)
IMPORT_BUTTON = "[data-qa='action-button-products-settings-import']"
SEARCH_INPUT = "[data-qa='filter-search']"
PRODUCT_NAME = ".product-row .product-name"

# Import wizard (POV top-level modal)
MODAL = "[data-qa='import-products-modal']"
WIZARD_NEXT = "[data-qa='wizard-wizard-next-button']"
CLOSE_BUTTON = "[data-qa='vc-header-close-button']"
STEP_TITLE = "[data-qa='wizard-step-title']"
DROPZONE_INPUT = "[data-qa='vc-dropzone--input']"
ERROR_ROW = ".error-row-item"
GOT_IT_BUTTON = "Got it"
DOWNLOAD_TEMPLATE_BUTTON = "Download template"

STEP_UPLOAD = "Upload file"
STEP_ADD_TAXES = "Add taxes"
STEP_IMPORT = "Import"

# Each wizard step transition fires an async backend call (file analysis after upload,
# review build after tax selection). Under stress load these intermittently return a
# transient "something went wrong, please try again" banner instead of advancing; the
# UI itself invites a retry, so re-trigger the step action a bounded number of times.
WIZARD_ERROR = "text=/something went wrong/i"
WIZARD_RETRY_ATTEMPTS = 3
# The file-analysis backend error persists within a wedged wizard session; recovery is a
# fresh wizard (close + reopen). 4 independent sessions take a ~30% per-session flake to
# ~0.8% so a strict 10/10 stress run is reliable.
UPLOAD_SESSION_ATTEMPTS = 4


def _frame_with(page: Page, selector: str, timeout: int = UI_TIMEOUT):
    """Return the first frame whose DOM currently contains ``selector``."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.1)
    return None


def _require_frame(page: Page, selector: str, timeout: int = UI_TIMEOUT):
    frame = _frame_with(page, selector, timeout)
    if frame is None:
        raise AssertionError(f"No frame contained selector {selector!r} within {timeout}ms")
    return frame


def products_url(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return f"{base}{PRODUCTS_URL_PATH}"


# The products settings page is gated by the import_products feature flag. Right
# after the flag is enabled the session can still serve the fallback billing/taxes
# settings tab for a beat (the Import action is then absent), and under cumulative
# suite load the page itself boots slowly. Reload-retry until the Import action
# renders rather than failing on the first cold load.
PRODUCTS_PAGE_RETRIES = 3
PRODUCTS_LIST_TIMEOUT = 10000


def open_products_page(page: Page, context: dict) -> None:
    """Navigate to the products settings page and wait for the Import action."""
    last_error: Exception | None = None
    for _ in range(PRODUCTS_PAGE_RETRIES):
        page.goto(products_url(context), wait_until="domcontentloaded")
        frame = _frame_with(page, IMPORT_BUTTON, timeout=PRODUCTS_LIST_TIMEOUT)
        if frame is not None:
            try:
                frame.locator(IMPORT_BUTTON).first.wait_for(state="visible", timeout=UI_TIMEOUT)
                return
            except Exception as err:
                last_error = err
        page.wait_for_timeout(1500)
    raise AssertionError(
        "Products settings page did not render the Import action (feature flag not "
        f"active yet or page on fallback tab) after {PRODUCTS_PAGE_RETRIES} attempts: {last_error!r}"
    )


def _wizard_step(page: Page) -> str:
    frame = _frame_with(page, STEP_TITLE)
    if frame is None:
        return ""
    return (frame.locator(STEP_TITLE).first.inner_text() or "").strip()


def _wait_for_step(page: Page, title: str, timeout: int = UI_TIMEOUT) -> None:
    frame = _require_frame(page, STEP_TITLE, timeout=timeout)
    expect(frame.locator(STEP_TITLE).first).to_have_text(title, timeout=timeout)


def _wizard_has_error(page: Page, timeout: int = 200) -> bool:
    """True only when the transient error banner is actually VISIBLE. The banner element
    is pre-rendered (hidden) in the wizard DOM, so a presence/count check would always
    match; visibility is what distinguishes a real backend failure."""
    deadline = time.monotonic() + timeout / 1000
    while True:
        for frame in page.frames:
            try:
                banner = frame.locator(WIZARD_ERROR)
                if banner.count() > 0 and banner.first.is_visible():
                    return True
            except Exception:
                continue
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def _wait_error_cleared(page: Page, timeout: int = 3000) -> None:
    """Wait (bounded) for the error banner to stop being visible after a (re)trigger, so
    the next poll does not re-detect a stale banner from a prior failed attempt. Returns
    even if it never clears (the poll loop then treats it as a fresh error and retries)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        if not _wizard_has_error(page, timeout=100):
            return
        time.sleep(0.1)


def _advance_to_step(page: Page, target_title: str, trigger, *,
                     timeout: int = IMPORT_JOB_TIMEOUT) -> None:
    """Run ``trigger`` (the action that should advance the wizard), then wait for
    ``target_title``. Re-run ``trigger`` (bounded) if the wizard either surfaces the
    transient backend-error banner or silently fails to advance within the window
    (e.g. a file-set/Next that did not register, or a stalled analysis job). Raises
    only after every attempt fails to reach the target step."""
    last_step = ""
    for _ in range(WIZARD_RETRY_ATTEMPTS):
        trigger()
        _wait_error_cleared(page)  # let the (re)trigger clear a banner from a prior attempt
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if _wizard_step(page) == target_title:
                return
            if _wizard_has_error(page):
                break  # transient backend error -> re-trigger this step
            time.sleep(0.25)
        # Reached here on either an error banner or a silent stall; both recover by
        # re-running the trigger (idempotent re-click Next).
        last_step = _wizard_step(page)
    raise AssertionError(
        f"Import wizard did not reach {target_title!r} after {WIZARD_RETRY_ATTEMPTS} "
        f"attempts of {timeout}ms each (last step {last_step!r})"
    )


def open_import_wizard(page: Page, context: dict) -> None:
    """Open the products page and launch the Import wizard (Get started step)."""
    open_products_page(page, context)
    frame = _require_frame(page, IMPORT_BUTTON)
    frame.locator(IMPORT_BUTTON).first.click()
    _require_frame(page, MODAL).locator(MODAL).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def _click_next(page: Page) -> None:
    frame = _require_frame(page, WIZARD_NEXT)
    frame.locator(WIZARD_NEXT).first.click()


def _await_step_or_error(page: Page, target_title: str, *, timeout: int) -> bool:
    """Poll until the wizard reaches ``target_title`` (return True) or surfaces the
    transient error banner / the window expires (return False)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        if _wizard_step(page) == target_title:
            return True
        if _wizard_has_error(page):
            return False
        time.sleep(0.25)
    return False


def _upload_in_session(page: Page, file_path: str) -> None:
    """Within the already-open wizard: Get started -> Upload, set the file, wait for the
    analysis job to advance to Add taxes. Raises if the analysis errors/stalls (the
    caller recovers by reopening the wizard for a fresh session)."""
    _click_next(page)  # Get started -> Upload file
    _wait_for_step(page, STEP_UPLOAD)
    _require_frame(page, DROPZONE_INPUT).locator(DROPZONE_INPUT).first.set_input_files(file_path)
    if not _await_step_or_error(page, STEP_ADD_TAXES, timeout=IMPORT_JOB_TIMEOUT):
        raise AssertionError("Import wizard file analysis did not reach 'Add taxes' (wedged session)")


def import_via_wizard(page: Page, context: dict, file_path: str, *,
                      tax: tuple | None = None, expect_invalid_rows: bool = False) -> None:
    """Run the full import wizard (upload -> select/skip tax -> [review check] -> submit
    -> success). Each async backend step (file analysis, review build, import execution)
    intermittently returns a 'something went wrong' banner that re-triggering within the
    same wizard session does NOT clear; only a fresh wizard recovers. So on any wedge,
    close and reopen the wizard and redo the whole import. Bounded."""
    last_err: Exception | None = None
    for _ in range(UPLOAD_SESSION_ATTEMPTS):
        open_import_wizard(page, context)
        try:
            _upload_in_session(page, file_path)
            if tax:
                select_tax(page, tax[0], tax[1])
            else:
                skip_taxes(page)
            if expect_invalid_rows:
                assert_error_rows_present(page)
            submit_import(page)
            return
        except AssertionError as err:
            last_err = err
            close_wizard(page)
            try:
                _wait_modal_closed(page)
            except AssertionError:
                pass
    raise AssertionError(
        f"Import wizard did not complete after {UPLOAD_SESSION_ATTEMPTS} fresh sessions "
        f"(persistent backend error): {last_err}"
    )


def select_tax(page: Page, name: str, rate: int) -> None:
    """Check a tax in the Add taxes step and continue to the Import (review) step."""
    option = f"[data-qa='add-taxes-listbox-{name}-({rate}%)-checkbox']"
    frame = _require_frame(page, option)
    checkbox = frame.locator(option).first
    if not checkbox.is_checked():
        frame.locator(f"[data-qa='add-taxes-listbox-{name}-({rate}%)']").first.click()
    expect(checkbox).to_be_checked(timeout=UI_TIMEOUT)
    _advance_to_step(page, STEP_IMPORT, lambda: _click_next(page))


def skip_taxes(page: Page) -> None:
    """Continue from Add taxes to the Import (review) step without selecting a tax."""
    _wait_for_step(page, STEP_ADD_TAXES)
    _advance_to_step(page, STEP_IMPORT, lambda: _click_next(page))


def assert_error_rows_present(page: Page) -> int:
    """Assert the review step lists at least one row that will not be imported."""
    frame = _require_frame(page, ERROR_ROW)
    count = frame.locator(ERROR_ROW).count()
    assert count > 0, "Expected invalid-row errors in the review step, found none"
    return count


def _wait_modal_closed(page: Page, timeout: int = UI_TIMEOUT) -> None:
    """Poll until the wizard modal is gone from every frame."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        if _frame_with(page, MODAL, timeout=200) is None:
            return
        time.sleep(0.1)
    raise AssertionError("Import wizard modal did not close")


def _success_button_visible(page: Page) -> bool:
    frame = _frame_with(page, MODAL, timeout=200)
    if frame is None:
        return False
    button = frame.get_by_role("button", name=GOT_IT_BUTTON)
    return button.count() > 0 and button.first.is_visible()


def submit_import(page: Page) -> None:
    """Click Import on the review step and confirm the success screen, then close.

    The import execution is an async backend job that can intermittently return the
    transient error banner under load; re-click Import (bounded) when it does."""
    _wait_for_step(page, STEP_IMPORT)
    for _ in range(WIZARD_RETRY_ATTEMPTS):
        _click_next(page)
        deadline = time.monotonic() + IMPORT_JOB_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if _success_button_visible(page):
                frame = _require_frame(page, MODAL)
                frame.get_by_role("button", name=GOT_IT_BUTTON).first.click()
                _wait_modal_closed(page)
                return
            if _wizard_has_error(page):
                break  # transient backend error -> re-click Import
            time.sleep(0.25)
        else:
            raise AssertionError(
                f"Import success screen did not appear within {IMPORT_JOB_TIMEOUT}ms (no error banner)"
            )
    raise AssertionError(
        f"Import did not complete after {WIZARD_RETRY_ATTEMPTS} retries on transient backend errors"
    )


def download_template(page: Page) -> str:
    """Click Download template on the Get started step; return the downloaded name."""
    frame = _require_frame(page, MODAL)
    with page.expect_download(timeout=UI_TIMEOUT) as download_info:
        frame.get_by_role("button", name=DOWNLOAD_TEMPLATE_BUTTON).first.click()
    return download_info.value.suggested_filename


def close_wizard(page: Page) -> None:
    frame = _frame_with(page, CLOSE_BUTTON)
    if frame is not None:
        frame.locator(CLOSE_BUTTON).first.click()


def _product_names(frame) -> list:
    # all_inner_texts() snapshots every currently-matched row in one call. Using
    # count()+nth().inner_text() instead races with the list re-rendering (a row can
    # detach between the two calls, making inner_text() wait the full 5s timeout).
    return [t.strip() for t in frame.locator(PRODUCT_NAME).all_inner_texts()]


# The vuetage list re-renders its search input when results change, so a fill can
# race with the element being replaced. Re-acquire and retry with a short
# actionability timeout (<=2 retries) instead of one long, racy fill.
_SEARCH_FILL_TIMEOUT = 2000
# After a post-import page reload the product-list component (which owns the search
# input) mounts a beat after the page shell that open_products_page gates on, and is
# slower under cumulative suite load. Give the search input a page-boot-class budget
# rather than the 5s element-interaction default (documented wait-audit exception).
_SEARCH_READY_TIMEOUT = 15000


def _fill_search(page: Page, query: str):
    last_err = None
    for _ in range(3):
        frame = _require_frame(page, SEARCH_INPUT, timeout=_SEARCH_READY_TIMEOUT)
        box = frame.locator(SEARCH_INPUT).first
        try:
            box.fill(query, timeout=_SEARCH_FILL_TIMEOUT)
            return frame
        except Exception as err:  # input replaced mid-action; re-acquire and retry
            last_err = err
            time.sleep(0.2)
    raise last_err


def search_products(page: Page, query: str, expected_names: list) -> list:
    """Type into the products search and poll until the visible names match."""
    frame = _fill_search(page, query)
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    names = _product_names(frame)
    while time.monotonic() < deadline:
        names = _product_names(frame)
        if names == expected_names:
            return names
        time.sleep(0.1)
    return names


def get_product_tax(page: Page, product_name: str) -> str:
    """Return the tax text shown on a product row (e.g. 'ImportTax (13%)')."""
    frame = _require_frame(page, f"[data-qa='{product_name}']")
    row = frame.locator(f"[data-qa='{product_name}']").first
    tax = row.locator(".product-taxes-desktop div").first
    tax.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (tax.inner_text() or "").strip()
