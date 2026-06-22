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
# The auto-publish section is gated on the business' directory_settings, which the
# BusinessStore fetches during app init and which resolve a beat AFTER getReviewSettings
# (the public-reviews checkbox can paint first, then the section re-renders once
# directory_settings arrive). Treat the section's appearance as page-load readiness and
# wait the same budget used for the public-reviews checkbox. The negative assertion polls
# the same budget so an absent section means "never renders", not "not yet loaded".
AUTO_PUBLISH_RENDER_TIMEOUT = PAGE_LOAD_TIMEOUT
# Negative-assertion settle (<=5s cap): open_review_settings already waited for the page to
# render (public-reviews checkbox), and directory_settings resolve within a few seconds of
# that, so 5s reliably covers the load window while keeping scenario 2 fast.
ABSENCE_STABILITY_TIMEOUT = FAST_UI_TIMEOUT

PUBLIC_REVIEWS_CHECKBOX = '[data-qa="review-public-reviews-checkbox"]'
PLATFORM_SELECT = '[data-qa="review-platform-select"]'
PLATFORM_ID_INPUT = '[data-qa="review-platform-id-input"]'
SAVE_BUTTON = '[data-qa="review-settings-action-save"]'
# The auto-publish section renders only when the business' directory has an external
# review site (POV `v-if="reviewSite"`); data-qa sits on the wrapping div, and the real
# Vuetify checkbox input carries the aria-checked state.
AUTO_PUBLISH_SECTION = '[data-qa="reviews-settings-auto-publish-checkbox"]'
AUTO_PUBLISH_CHECKBOX = '[data-qa="reviews-settings-auto-publish-checkbox"] input[role="checkbox"]'
AUTO_PUBLISH_LABEL = '[data-qa="reviews-settings-auto-publish-checkbox"] .v-label'
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


def _wait_present(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Poll `_locate_any` until `selector` exists in any frame (Vuetify re-renders the
    select/auto-publish controls a beat after the page's first paint)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        locator = _locate_any(page, selector)
        if locator is not None:
            return locator
        time.sleep(0.1)
    return None


def _select_platform(page: Page, platform: str) -> None:
    select_input = _wait_present(page, PLATFORM_SELECT)
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


# --------------------------------------------------------------------------- #
# Auto-publish settings (reviews.feature scenarios 2 & 3)
# --------------------------------------------------------------------------- #
def assert_auto_publish_section_absent(page: Page, context: dict) -> None:
    """The reviews settings page renders, but the auto-publish section is not present.

    `open_review_settings` already proves the page rendered (public-reviews checkbox
    visible) instead of redirecting to the dashboard, so an absent auto-publish
    section is a real "not displayed", not a missing page.
    """
    open_review_settings(page, context)
    # Poll the full page-load budget: directory_settings (which would render the section)
    # resolve a beat after the public-reviews checkbox, so an absent section across this
    # window means "no review site", not "not yet loaded".
    deadline = time.monotonic() + ABSENCE_STABILITY_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _auto_publish_checkbox_count(page) != 0:
            raise AssertionError(
                "Auto-publish section was displayed on the reviews settings page but was not expected"
            )
        time.sleep(0.2)


def toggle_auto_publish_and_save(page: Page, context: dict) -> None:
    """Open settings, enable the auto-publish checkbox, and save."""
    open_review_settings(page, context)
    checkbox = _wait_present(page, AUTO_PUBLISH_CHECKBOX, timeout=AUTO_PUBLISH_RENDER_TIMEOUT)
    if checkbox is None:
        raise AssertionError("Auto-publish checkbox not found on the reviews settings page")
    if not _auto_publish_is_checked(page):
        # data-qa is on the wrapper; the icon overlays the real input, so force-click the input.
        checkbox.click(force=True, timeout=FAST_UI_TIMEOUT)
        deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
        while time.monotonic() < deadline and not _auto_publish_is_checked(page):
            time.sleep(0.1)
        if not _auto_publish_is_checked(page):
            raise AssertionError("Auto-publish checkbox did not become checked after clicking")
    _save(page)


def assert_auto_publish_checked_and_label(page: Page, context: dict, expected_name: str) -> None:
    """Re-open settings (proving persistence) and assert the checkbox is checked and labelled.

    Re-opening forces a reload of the saved settings, so this asserts the persisted
    `display_review_sharing_consent`, not just transient DOM state.
    """
    open_review_settings(page, context)
    if _wait_present(page, AUTO_PUBLISH_CHECKBOX, timeout=AUTO_PUBLISH_RENDER_TIMEOUT) is None:
        raise AssertionError("Auto-publish checkbox did not appear after saving")
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline and not _auto_publish_is_checked(page):
        time.sleep(0.1)
    if not _auto_publish_is_checked(page):
        raise AssertionError("Auto-publish checkbox was not checked after saving")
    label = _find_control(page, AUTO_PUBLISH_LABEL)
    if label is None:
        raise AssertionError("Auto-publish checkbox label did not appear")
    text = (label.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    assert expected_name.lower() in text.lower(), (
        f"Expected auto-publish label to contain review site name '{expected_name}', got '{text}'"
    )


def _auto_publish_is_checked(page: Page) -> bool:
    checkbox = _locate_any(page, AUTO_PUBLISH_CHECKBOX)
    if checkbox is None:
        return False
    return (checkbox.get_attribute("aria-checked") or "").lower() == "true"


def _auto_publish_checkbox_count(page: Page) -> int:
    for scope in [page, *page.frames]:
        try:
            count = scope.locator(AUTO_PUBLISH_SECTION).count()
            if count > 0:
                return count
        except Exception:
            continue
    return 0
