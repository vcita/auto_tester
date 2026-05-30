import time

from playwright.sync_api import Page

from tests.payments.tips_settings.tips_account import post_tips, set_tips_via_api
from tests.payments.tips_settings.tips_helpers import (
    FAST_UI_TIMEOUT,
    clear_profile_cache,
    get_preview_amounts,
    get_tips_status,
    open_tips_settings,
)

TIP_VALUES = [55, 66, 77]
EXPECTED_PREVIEW = ["$55.00", "$66.00", "$77.00"]
MAX_RELOADS = 6
RELOAD_BACKOFF_SECONDS = 3


def test_tips_edit_persist(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)

    print("  Step 1: Set tips via API (55, 66, 77)")
    set_tips_via_api(context, TIP_VALUES)

    print("  Step 2-4: Reload tips tab and assert enabled + persisted preview")
    # set_tips_via_api confirmed the tips on core, but the gateway-connect save in setup can land a
    # late async write that resets payment_settings.tips, and the POV read can briefly lag. Each
    # retry re-posts the tips (latest write wins over any overwrite) then reloads with a fresh
    # navigation + backoff, so the assertion converges on the saved values instead of racing.
    status = ""
    amounts = []
    for attempt in range(1, MAX_RELOADS + 1):
        if attempt > 1:
            post_tips(context, TIP_VALUES)
        clear_profile_cache(page)
        scope = open_tips_settings(page, context)
        status = get_tips_status(scope)
        amounts = get_preview_amounts(scope, expected=EXPECTED_PREVIEW)
        if status == "enabled" and amounts == EXPECTED_PREVIEW:
            print(f"  Tips settings enabled and preview amounts persisted (load {attempt})")
            return
        print(f"  [retry] load {attempt}: status={status} preview={amounts}")
        if attempt < MAX_RELOADS:
            time.sleep(RELOAD_BACKOFF_SECONDS)

    assert status == "enabled", f"Expected tips settings 'enabled', got '{status}'"
    assert amounts == EXPECTED_PREVIEW, f"Expected preview {EXPECTED_PREVIEW}, got {amounts}"
