"""Back-office (POV) reviews settings page flow.

Mirrors the legacy `Reviews` page object (`/app/settings/reviews`): enable public
reviews, pick a review platform (Google/Facebook), enter the platform id, and save.
The page is gated by the `reviews_rollout` + `collect_reviews` flags (otherwise it
redirects to the dashboard) and the fields are enabled by `enable_reviews_auto_publishing`;
the setup enables all three. Save persists to `/v3/reviews/business_reviews_settings`,
which is the readiness signal this helper waits on (no reload, so DOM alone would
not prove persistence).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
PAGE_LOAD_TIMEOUT = 20000
SAVE_SETTLE_TIMEOUT = 10000

PUBLIC_REVIEWS_CHECKBOX = '[data-qa="review-public-reviews-checkbox"]'
PLATFORM_SELECT = '[data-qa="review-platform-select"]'
PLATFORM_ID_INPUT = '[data-qa="review-platform-id-input"]'
SAVE_BUTTON = '[data-qa="review-settings-action-save"]'
# Vuetify forwards data-qa to the inner (readonly/hidden) controls; the v-select
# opens on a click of its enclosing slot, not the input.
SELECT_SLOT_XPATH = "xpath=ancestor::div[contains(@class,'v-input__slot')][1]"
MENU_OPTION = ".v-list-item"

SAVE_ENDPOINT = "/v3/reviews/business_reviews_settings"


def open_review_settings(page: Page, context: dict) -> None:
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}/app/settings/reviews", wait_until="domcontentloaded")
    if _find_control(page, PUBLIC_REVIEWS_CHECKBOX, timeout=PAGE_LOAD_TIMEOUT) is None:
        raise AssertionError(
            "Reviews settings page did not render the public-reviews checkbox "
            "(check reviews_rollout / collect_reviews / enable_reviews_auto_publishing flags)"
        )


def set_review_platform(page: Page, context: dict, platform: str, platform_id: str) -> None:
    """Enable public reviews, select `platform`, set its id, and save."""
    open_review_settings(page, context)
    _enable_public_reviews(page)
    _select_platform(page, platform)

    platform_id_field = _find_control(page, PLATFORM_ID_INPUT)
    if platform_id_field is None:
        raise AssertionError("Platform id input did not appear after selecting a platform")
    platform_id_field.fill(platform_id, timeout=FAST_UI_TIMEOUT)

    _save(page)


def _enable_public_reviews(page: Page) -> None:
    if _is_checked(page):
        return
    checkbox = _locate_any(page, PUBLIC_REVIEWS_CHECKBOX)
    if checkbox is None:
        raise AssertionError("Public-reviews checkbox not found")
    # `data-qa` sits on the real (visually hidden) input that Vuetify overlays with the
    # icon, so a normal click hits the icon, not the input; force-click the input itself.
    checkbox.click(force=True, timeout=FAST_UI_TIMEOUT)

    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _is_checked(page):
            return
        time.sleep(0.1)
    raise AssertionError("Public-reviews checkbox did not become checked after clicking")


def _is_checked(page: Page) -> bool:
    """`data-qa` is on the input; read its aria-checked state."""
    checkbox = _locate_any(page, PUBLIC_REVIEWS_CHECKBOX)
    if checkbox is None:
        return False
    return (checkbox.get_attribute("aria-checked") or "").lower() == "true"


def _locate_any(page: Page, selector: str):
    """Return the first existing match for `selector` (no visibility requirement)."""
    for scope in [page, *page.frames]:
        try:
            locator = scope.locator(selector)
            if locator.count() > 0:
                return locator.first
        except Exception:
            continue
    return None


def _select_platform(page: Page, platform: str) -> None:
    select_input = _locate_any(page, PLATFORM_SELECT)
    if select_input is None:
        raise AssertionError("Review platform select did not appear")
    select_input.locator(SELECT_SLOT_XPATH).first.click(timeout=FAST_UI_TIMEOUT)

    option = _wait_option(page, platform)
    if option is None:
        raise AssertionError(f"Platform option '{platform}' did not appear in the select menu")
    option.click(timeout=FAST_UI_TIMEOUT)


def _save(page: Page) -> None:
    save_button = _find_control(page, SAVE_BUTTON)
    if save_button is None:
        raise AssertionError("Save button did not appear on the reviews settings page")
    with page.expect_response(
        lambda response: SAVE_ENDPOINT in response.url
        and response.request.method in ("POST", "PUT")
        and response.ok,
        timeout=SAVE_SETTLE_TIMEOUT,
    ):
        save_button.click(timeout=FAST_UI_TIMEOUT)


def _wait_option(page: Page, text: str, timeout: int = FAST_UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                options = scope.locator(MENU_OPTION)
                for index in range(options.count()):
                    candidate = options.nth(index)
                    if candidate.is_visible() and text.lower() in (
                        candidate.inner_text(timeout=1000) or ""
                    ).lower():
                        return candidate
            except Exception:
                continue
        time.sleep(0.1)
    return None


def _find_control(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the first visible match for `selector` across the page and all frames."""
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
        time.sleep(0.1)
    return None
