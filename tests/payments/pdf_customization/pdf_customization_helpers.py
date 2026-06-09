"""UI helpers for the pdf_customization subcategory.

The PDF customization settings live in a Vue app (`#vue-app-tab`) nested inside the
frontage angular iframe (`iframe[title="angularjs"]`), same host page as the Taxes tab.
Controls are resolved by scanning the page and every frame for the target selector
(mirroring `payment_wizard_ui._scan`), which is robust to the nested-iframe depth.

Selector policy: legacy `data-qa` first (`{template}-pro` / `{template}-select`,
`radio-{type}`, `brand-color-value-container_input`, the Save button). The selected-state
read-backs (`.vc-gallery-item--selected`, `.logo-size-container .selection-text`,
`.v-item--active .label-container`) are existing stable legacy CSS with no data-qa
equivalent. Element waits are capped at 5s; page (re)navigation gets the longer NAV budget
because the settings page mounts nested frames.
"""

import time

from playwright.sync_api import Page

UI_TIMEOUT = 5000
NAV_TIMEOUT = 20000
SAVE_TIMEOUT = 10000

SAVE_BUTTON = 'button[data-qa="action-button-payments_settings-save"]'
SELECTED_TEMPLATE = ".vc-gallery-item--selected"
LOGO_SIZE_DROPDOWN = ".logo-size-container.VcSelectField .v-input__slot"
SELECTED_LOGO_SIZE = ".logo-size-container .selection-text"
SELECTED_BRAND_TYPE = ".v-item--active .label-container"
BRAND_COLOR_VALUE = '[data-qa="brand-color-value-container_input"]'
# Vuetify renders the open select menu options under one of these; scan all of them.
OPTION_SELECTORS = (".v-list-item__title", ".v-list-item", "[role='option']")

# The Save button persists PDF customization to the account settings endpoint; waiting for
# the 2xx write response is a true save confirmation (the page is not reloaded by the click).
SETTINGS_ENDPOINT = "/v2/settings"


def _template_tile(name: str) -> str:
    return f'[data-qa="{name}-pro"]'


def _template_select(name: str) -> str:
    return f'[data-qa="{name}-select"]'


def _brand_radio(brand_type: str) -> str:
    return f'[data-qa="radio-{brand_type}"]'


def _scan(page: Page, selector: str, timeout: int = UI_TIMEOUT):
    """Return the first visible match for `selector` across the page and every frame."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                locator = scope.locator(selector)
                for index in range(locator.count()):
                    candidate = locator.nth(index)
                    if candidate.is_visible():
                        return candidate
            except Exception:
                continue
        time.sleep(0.15)
    return None


def _require(page: Page, selector: str, label: str, timeout: int = UI_TIMEOUT):
    control = _scan(page, selector, timeout=timeout)
    if control is None:
        raise AssertionError(f"{label} did not appear ({selector})")
    return control


def _option_by_text(page: Page, text: str, timeout: int = UI_TIMEOUT):
    """Find an open-dropdown option whose trimmed text equals `text` across frames.

    Vuetify renders options under varying classes, so several selectors are scanned. The
    locator's own click waits for actionability, so a strict is_visible() pre-check (which
    is flaky during the menu's open transition) is not required here.
    """
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            for selector in OPTION_SELECTORS:
                try:
                    options = scope.locator(selector)
                    for index in range(options.count()):
                        candidate = options.nth(index)
                        try:
                            label = (candidate.inner_text() or "").strip()
                        except Exception:
                            continue
                        if label == text:
                            return candidate
                except Exception:
                    continue
        time.sleep(0.15)
    return None


def _app_base(page: Page) -> str:
    return page.url.split("/app/")[0]


def open_pdf_customization(page: Page) -> None:
    """Navigate to the PDF customization tab and wait for the template gallery to render."""
    page.goto(
        f"{_app_base(page)}/app/settings/billing_and_invoicing?tab=pdf_customization",
        wait_until="domcontentloaded",
        timeout=NAV_TIMEOUT,
    )
    if _scan(page, SELECTED_TEMPLATE, timeout=NAV_TIMEOUT) is None:
        raise AssertionError("PDF customization page did not render the template gallery")


def set_template(page: Page, name: str) -> None:
    # The select button is revealed on hover over the template tile (legacy hoverElement).
    _require(page, _template_tile(name), f"template tile '{name}'", timeout=UI_TIMEOUT).hover()
    _require(page, _template_select(name), f"template select button '{name}'").click()


def set_logo_size(page: Page, size: str) -> None:
    _require(page, LOGO_SIZE_DROPDOWN, "logo size dropdown").click()
    option = _option_by_text(page, size)
    if option is None:
        raise AssertionError(f"Logo size option '{size}' did not appear in the dropdown")
    option.click()


def set_brand_color_type(page: Page, brand_type: str) -> None:
    _require(page, _brand_radio(brand_type), f"brand color radio '{brand_type}'").click()


def save_settings(page: Page) -> None:
    save_button = _require(page, SAVE_BUTTON, "save button")
    with page.expect_response(_is_save_response, timeout=SAVE_TIMEOUT):
        save_button.click()


def _is_save_response(response) -> bool:
    if response.request.method in ("GET", "OPTIONS"):
        return False
    return SETTINGS_ENDPOINT in response.url and response.ok


def read_pdf_settings(page: Page) -> dict:
    """Reload the settings page and read the persisted PDF customization values.

    Reloading (vs the legacy re-read of the same loaded page) verifies true persistence.
    """
    open_pdf_customization(page)
    template_qa = _require(page, SELECTED_TEMPLATE, "selected template").get_attribute("data-qa") or ""
    logo_size = (_require(page, SELECTED_LOGO_SIZE, "selected logo size").inner_text() or "").strip()
    brand_type_qa = _require(page, SELECTED_BRAND_TYPE, "selected brand color type").get_attribute("data-qa") or ""
    brand_color = (_require(page, BRAND_COLOR_VALUE, "brand color value").input_value() or "").strip()
    return {
        "template": template_qa.split("-")[0],
        "logo_size": logo_size,
        "brand_color_type": brand_type_qa.split("-")[1] if "-" in brand_type_qa else brand_type_qa,
        "brand_color": brand_color,
    }
