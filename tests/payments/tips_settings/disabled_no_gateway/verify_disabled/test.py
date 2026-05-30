import time

from playwright.sync_api import Page

from tests.payments.tips_settings.tips_helpers import (
    FAST_UI_TIMEOUT,
    get_tips_status,
    open_tips_settings,
)

MAX_RELOADS = 4
RELOAD_BACKOFF_SECONDS = 3


def test_tips_disabled_no_gateway(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)

    print("  Step 1-2: Open tips settings and assert it is disabled (no payment provider)")
    # The gateway_platform deny + cache reset happen in setup, but propagation to the POV
    # checkout-enabled read can lag on a cold first load, briefly showing the enabled state.
    # Reload with a backoff so the assertion converges on the denied (disabled) state.
    status = ""
    for attempt in range(1, MAX_RELOADS + 1):
        scope = open_tips_settings(page, context)
        status = get_tips_status(scope)
        if status == "disabled":
            print(f"  Tips settings correctly disabled without a payment provider (load {attempt})")
            return
        print(f"  [retry] load {attempt}: status={status}")
        if attempt < MAX_RELOADS:
            time.sleep(RELOAD_BACKOFF_SECONDS)

    assert status == "disabled", f"Expected tips settings 'disabled', got '{status}'"
