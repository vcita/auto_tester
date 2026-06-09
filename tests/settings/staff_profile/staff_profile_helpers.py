"""Shared UI helpers for the staff_profile tests.

The POV staff-profile form renders at the top-level page context (legacy
switchToPageContext), so the field locators resolve directly on `page`. The
scenario-2 "settings tiles" landing is reached from the Angular staff list, which
renders inside the Frontage iframe (`iframe[title="angularjs"]`).

Selectors are sourced from the legacy page objects
(automation-js/pages/desktop/Frontage/Settings/staffProfilePage.js and
.../Frontage/staffs.js) and verified live against POV during MCP exploration.
"""

import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5_000
PAGE_TIMEOUT = 5_000

DISPLAY_NAME = '[data-qa="staff-display-name-input"]'
FIRST_NAME = '[data-qa="staff-first-name-input"]'
LAST_NAME = '[data-qa="staff-last-name-input"]'
EMAIL = '[data-qa="staff-email-input"]'
PHONE = '[data-qa="staff-phone-input_number-text"]'
COUNTRY_PREFIX = '[data-qa="staff-phone-input_number-prefix"]'
PROF_TITLE = '[data-qa="staff-professional-title-input"]'
PASSWORD = '[data-qa="staff-password-input"]'
SAVE = '[data-qa="save-profile-button"]'
# Homepage is a single Vuetify v-select on the page; its display value lives in
# `.selection-text` and its <input> is intercepted, so we open via the wrapper.
HOMEPAGE_OPEN = '.v-input:has([data-qa="staff-default-homepage"]) .v-select__selections'
HOMEPAGE_VALUE = '.v-input:has([data-qa="staff-default-homepage"]) .selection-text'

FRONTAGE_FRAME = 'iframe[title="angularjs"]'
STAFF_LIST_CONTAINER = ".cards-list-container"
SETTINGS_TILES = ".card_inner_content"


def app_base(page: Page) -> str:
    return page.url.split("/app/")[0]


def _wait_form_ready(page: Page) -> None:
    page.locator(DISPLAY_NAME).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def open_own_profile(page: Page) -> None:
    page.goto(
        f"{app_base(page)}/app/settings/staff_profile",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )
    _wait_form_ready(page)


def open_staff_profile(page: Page, staff_uid: str) -> None:
    page.goto(
        f"{app_base(page)}/app/settings/staff_profile/{staff_uid}",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )
    _wait_form_ready(page)


def open_staff_settings_landing(page: Page, staff_name: str) -> None:
    """Open the per-staff settings landing (tiles) via the Angular staff-list kebab.

    Mirrors legacy Staffs().goto() + goToStaffSettings(name).
    """
    page.goto(
        f"{app_base(page)}/app/settings/staff",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )
    frame = page.frame_locator(FRONTAGE_FRAME)
    frame.locator(STAFF_LIST_CONTAINER).first.wait_for(state="visible", timeout=UI_TIMEOUT)

    row = frame.locator(
        f"xpath=//div[contains(text(), '{staff_name}')]"
        f"/ancestor::div[contains(@class, 'list-item')]"
    ).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.hover(timeout=UI_TIMEOUT)
    row.locator("button[aria-haspopup='true']").first.click(timeout=UI_TIMEOUT)

    # The Angular Material menu renders inside the same iframe; target the
    # clickable menuitem by role+name (get_by_text matched the md-menu-item
    # wrapper, whose click was intercepted).
    frame.get_by_role("menuitem", name="Staff settings").click(timeout=UI_TIMEOUT)


def settings_tiles_count(page: Page) -> int:
    """Count the settings tiles on the staff-settings landing.

    The landing may render either top-level (POV) or inside the Frontage iframe,
    so poll both contexts until tiles appear.
    """
    frame = page.frame_locator(FRONTAGE_FRAME)
    deadline = time.time() + UI_TIMEOUT / 1000
    while time.time() < deadline:
        for ctx in (page, frame):
            try:
                count = ctx.locator(SETTINGS_TILES).count()
            except Exception:  # noqa: BLE001
                count = 0
            if count > 0:
                return count
        page.wait_for_timeout(250)
    return 0


def read_profile(page: Page) -> dict:
    _wait_form_ready(page)
    return {
        "email": page.locator(EMAIL).first.input_value(),
        "mobile_number": page.locator(PHONE).first.input_value(),
        "first_name": page.locator(FIRST_NAME).first.input_value(),
        "last_name": page.locator(LAST_NAME).first.input_value(),
        "display_name": page.locator(DISPLAY_NAME).first.input_value(),
        "professional_title": page.locator(PROF_TITLE).first.input_value(),
        "default_homepage": (page.locator(HOMEPAGE_VALUE).first.inner_text() or "").strip(),
        "country_name": page.locator(COUNTRY_PREFIX).first.get_attribute("data-country-name"),
        "password_field": "displayed" if page.locator(PASSWORD).count() > 0 else "not displayed",
    }


def _set_text(page: Page, selector: str, value: str) -> None:
    field = page.locator(selector).first
    field.click()
    field.fill("")
    field.press_sequentially(value)


def _set_country(page: Page, code: str) -> None:
    page.locator(COUNTRY_PREFIX).first.click()
    option = page.locator(f'.vc-list [data-qa="vc-list-{code}"]').first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _set_default_homepage(page: Page, name: str) -> None:
    page.locator(HOMEPAGE_OPEN).first.click()
    option = page.get_by_role("option", name=name, exact=True).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def update_profile(page: Page, data: dict) -> None:
    """Update each provided field then save. Mirrors legacy updateProfileInformation order."""
    if data.get("country_code"):
        _set_country(page, data["country_code"])
    if data.get("mobile_number"):
        _set_text(page, PHONE, data["mobile_number"])
    if data.get("first_name"):
        _set_text(page, FIRST_NAME, data["first_name"])
    if data.get("last_name"):
        _set_text(page, LAST_NAME, data["last_name"])
    if data.get("display_name"):
        _set_text(page, DISPLAY_NAME, data["display_name"])
    if data.get("professional_title"):
        _set_text(page, PROF_TITLE, data["professional_title"])
    if data.get("default_homepage"):
        _set_default_homepage(page, data["default_homepage"])
    save_button = page.locator(SAVE).first
    save_button.click()
    # The Save button auto-disables once the form is dirty-saved and reset to
    # pristine, so a disabled state is the reliable (non-transient) save signal.
    expect(save_button).to_be_disabled(timeout=UI_TIMEOUT)


def assert_profile(page: Page, expected: dict) -> None:
    actual = read_profile(page)
    for field, value in expected.items():
        assert actual.get(field) == value, (
            f"profile field {field!r}: expected {value!r}, got {actual.get(field)!r}"
        )
