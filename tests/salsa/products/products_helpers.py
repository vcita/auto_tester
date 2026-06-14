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


def open_import_wizard(page: Page, context: dict) -> None:
    """Open the products page and launch the Import wizard (Get started step)."""
    open_products_page(page, context)
    frame = _require_frame(page, IMPORT_BUTTON)
    frame.locator(IMPORT_BUTTON).first.click()
    _require_frame(page, MODAL).locator(MODAL).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def _click_next(page: Page) -> None:
    frame = _require_frame(page, WIZARD_NEXT)
    frame.locator(WIZARD_NEXT).first.click()


def upload_file(page: Page, file_path: str) -> None:
    """From Get started: go to Upload, set the file, and wait for analysis to
    auto-advance to the Add taxes step (async backend job)."""
    _click_next(page)
    _wait_for_step(page, STEP_UPLOAD)
    _require_frame(page, DROPZONE_INPUT).locator(DROPZONE_INPUT).first.set_input_files(file_path)
    _wait_for_step(page, STEP_ADD_TAXES, timeout=IMPORT_JOB_TIMEOUT)


def select_tax(page: Page, name: str, rate: int) -> None:
    """Check a tax in the Add taxes step and continue to the Import (review) step."""
    option = f"[data-qa='add-taxes-listbox-{name}-({rate}%)-checkbox']"
    frame = _require_frame(page, option)
    checkbox = frame.locator(option).first
    if not checkbox.is_checked():
        frame.locator(f"[data-qa='add-taxes-listbox-{name}-({rate}%)']").first.click()
    expect(checkbox).to_be_checked(timeout=UI_TIMEOUT)
    _click_next(page)
    _wait_for_step(page, STEP_IMPORT)


def skip_taxes(page: Page) -> None:
    """Continue from Add taxes to the Import (review) step without selecting a tax."""
    _wait_for_step(page, STEP_ADD_TAXES)
    _click_next(page)
    _wait_for_step(page, STEP_IMPORT)


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


def submit_import(page: Page) -> None:
    """Click Import on the review step and confirm the success screen, then close."""
    _wait_for_step(page, STEP_IMPORT)
    _click_next(page)
    frame = _require_frame(page, MODAL, timeout=IMPORT_JOB_TIMEOUT)
    got_it = frame.get_by_role("button", name=GOT_IT_BUTTON)
    got_it.wait_for(state="visible", timeout=IMPORT_JOB_TIMEOUT)
    got_it.click()
    _wait_modal_closed(page)


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


def _fill_search(page: Page, query: str):
    last_err = None
    for _ in range(3):
        frame = _require_frame(page, SEARCH_INPUT)
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
