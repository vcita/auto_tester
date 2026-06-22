import time

from playwright.sync_api import Page, expect

from tests.account_api import get_business

UI_TIMEOUT = 5_000
# goto budget for the top-level POV settings page; domcontentloaded fires fast.
PAGE_TIMEOUT = 5_000
# POV mounts the Angular settings page inside an iframe; its boot is a documented
# cross-iframe readiness exception (slower than a same-document element wait).
IFRAME_TIMEOUT = 10_000

ANGULAR_IFRAME = 'iframe[title="angularjs"]'
NAME_FIELD = 'input[name="name"]'
EMAIL_FIELD = "input[ng-model='owner.email']"
COUNTRY_VALUE = '[name="country_name"] md-select-value'


def _input_value_when_ready(locator) -> str:
    """Return an Angular-bound input's value once it is populated (polls up to 5s)."""
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    value = ""
    while time.monotonic() < deadline:
        value = locator.input_value()
        if value:
            return value
        time.sleep(0.2)
    return value


def test_business_info_display(page: Page, context: dict) -> None:
    """The business info page shows the business name, Israel (972) country, and owner email.

    Migrates automation-js `business_info_page.feature` scenario
    `Update email in business info page`. The account's actual business name/email
    (read from the API) are asserted, since autotester names accounts dynamically.
    """
    info = get_business(context)
    expected_name = info["business"]["name"]
    expected_email = info["admin_account"]["email"]
    print(f"  Expecting name={expected_name!r}, email={expected_email!r}, country='Israel (972)'")

    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/settings/business", wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)

    # Wait for the Angular settings iframe to boot before reaching into it, so the
    # field reads run against a mounted frame rather than racing the iframe load.
    page.locator(ANGULAR_IFRAME).first.wait_for(state="visible", timeout=IFRAME_TIMEOUT)
    frame = page.frame_locator(ANGULAR_IFRAME)
    name_field = frame.locator(NAME_FIELD).first
    name_field.wait_for(state="visible", timeout=UI_TIMEOUT)

    actual_name = _input_value_when_ready(name_field)
    actual_email = _input_value_when_ready(frame.locator(EMAIL_FIELD).first)
    assert actual_name == expected_name, f"business name: expected {expected_name!r}, got {actual_name!r}"
    assert actual_email == expected_email, f"owner email: expected {expected_email!r}, got {actual_email!r}"
    expect(frame.locator(COUNTRY_VALUE).first).to_have_text("Israel (972)", timeout=UI_TIMEOUT)
    print("  [OK] Business info page displays name, owner email, and Israel (972) country")
