"""Client-portal review flow + conversation verification (vitrage `cp_iframe`).

Mirrors the legacy `ClientPortalReview` / `CPConversation` chain: open the client
portal as the client (`?client_jwt=<token>`), leave a 5-star review with feedback
text, assert the submitted page (default "Thanks for your review!" or the social
"rate on <platform>" button), and verify the review text shows in the client's
conversation `.review-bubble`.

The client portal renders inside a vitrage `cp_iframe`, so all controls are
resolved against that frame. All explicit UI waits are capped at 5s; the portal
page-load uses a longer page-readiness budget (like login waiting for a
dashboard, not an element wait).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
CP_LOAD_TIMEOUT = 15000
# Review bubbles post to the conversation asynchronously (realtime); poll a bit
# longer for eventual consistency, mirroring the legacy operation_timeout retry.
CONVERSATION_POLL_TIMEOUT = 15000

REVIEW_READY = ".review-page, .matter-indicator"
RATING_STAR = 'button[aria-label="Rating 5 of 5"]'
FEEDBACK_FIELD = "textarea"
SUBMIT_BUTTON = ".submit-review-button"
SUCCESS_TITLE = ".after-review-submit__title"
SOCIAL_BUTTON = ".after-review-submit__rate-on-social-button"

CP_DASHBOARD_READY = ".quick-actions, .matter-picker"
CHAT_BUTTON = '[data-qa="headerChatBtn"]'
REVIEW_BUBBLE = ".review-bubble"

# Auto-publish (reviews.feature scenarios 2 & 3). The CP shows it only when the
# directory has an external review site AND the business enabled auto-publish.
# `review-settings-loaded` is a display:none marker emitted once settings are fetched,
# so it must be matched by presence (not visibility).
AUTO_PUBLISH_CONTAINER = ".auto-publish-container"
REVIEW_SETTINGS_LOADED = '[data-qa="review-settings-loaded"]'

DEFAULT_SUCCESS_TEXT = "Thanks for your review!"


def vitrage_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if "app.meet2know.com" in base:
        return "https://live.meet2know.com"
    if "app.vcita.com" in base:
        return "https://live.vcita.com"
    if "app-" in base and ".external.int-eks.vchost.co" in base:
        return base.replace("https://app-", "https://vitrage-", 1)
    raise ValueError(f"Cannot derive vitrage base URL from base_url={base!r}")


def leave_review(page: Page, context: dict, text: str) -> None:
    """Open the client-portal review page as the client and submit a 5-star review."""
    client = context["review_client"]
    pivot_uid = context["auto_account"]["pivot_uid"]
    url = (
        f"{vitrage_base(context)}/site/{pivot_uid}/activity/review"
        f"?client_jwt={client['token']}"
    )
    page.goto(url, wait_until="domcontentloaded")

    frame = _wait_cp_frame(page, REVIEW_READY, timeout=CP_LOAD_TIMEOUT)
    if frame is None:
        raise AssertionError("Client-portal review page (cp_iframe) did not become ready")

    star = _wait_in_frame(page, REVIEW_READY, RATING_STAR)
    if star is None:
        raise AssertionError("5-star rating control did not appear on the review page")
    star.click(timeout=FAST_UI_TIMEOUT)

    feedback = _wait_in_frame(page, REVIEW_READY, FEEDBACK_FIELD)
    if feedback is None:
        raise AssertionError("Review feedback field did not appear")
    feedback.fill(text, timeout=FAST_UI_TIMEOUT)

    submit = _wait_in_frame(page, REVIEW_READY, SUBMIT_BUTTON)
    if submit is None:
        raise AssertionError("Submit-review button did not appear")
    submit.click(timeout=FAST_UI_TIMEOUT)


def assert_default_submitted(page: Page) -> None:
    """The default submitted page shows the 'Thanks for your review!' title."""
    title = _wait_in_frame(page, SUCCESS_TITLE, SUCCESS_TITLE)
    if title is None:
        raise AssertionError("Default review submitted title did not appear")
    text = (title.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    assert DEFAULT_SUCCESS_TEXT.lower() in text.lower(), (
        f"Expected default submitted title to contain '{DEFAULT_SUCCESS_TEXT}', got '{text}'"
    )


def assert_social_submitted(page: Page, platform: str) -> None:
    """After a platform is configured, the submitted page shows a 'rate on <platform>' button."""
    button = _wait_in_frame(page, SOCIAL_BUTTON, SOCIAL_BUTTON)
    if button is None:
        raise AssertionError(f"'{platform}' social review button did not appear after submitting")
    text = (button.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    assert platform.lower() in text.lower(), (
        f"Expected social submitted button to mention '{platform}', got '{text}'"
    )


def assert_review_in_conversation(page: Page, context: dict, text: str) -> None:
    """Open the client's conversation and verify the review bubble shows `text`."""
    _open_conversation(page, context)
    deadline = time.monotonic() + CONVERSATION_POLL_TIMEOUT / 1000
    last_seen: list = []
    while time.monotonic() < deadline:
        frame = _frame_with(page, REVIEW_BUBBLE) or _frame_with(page, CHAT_BUTTON)
        if frame is not None:
            bubbles = frame.locator(REVIEW_BUBBLE)
            last_seen = []
            for index in range(bubbles.count()):
                try:
                    content = bubbles.nth(index).inner_text(timeout=1000) or ""
                except Exception:
                    continue
                last_seen.append(content)
                if text in content:
                    return
        time.sleep(0.3)
    raise AssertionError(
        f"Review '{text}' did not appear in the client-portal conversation. Bubbles seen: {last_seen}"
    )


def _open_conversation(page: Page, context: dict) -> None:
    """Reopen the client portal dashboard as the client and open the conversation page."""
    client = context["review_client"]
    pivot_uid = context["auto_account"]["pivot_uid"]
    url = (
        f"{vitrage_base(context)}/site/{pivot_uid}/action"
        f"?client_jwt={client['token']}"
    )
    page.goto(url, wait_until="domcontentloaded")
    if _wait_cp_frame(page, CP_DASHBOARD_READY, timeout=CP_LOAD_TIMEOUT) is None:
        raise AssertionError("Client-portal dashboard did not become ready")

    chat = _wait_in_frame(page, CP_DASHBOARD_READY, CHAT_BUTTON)
    if chat is None:
        raise AssertionError("Conversation (chat) button did not appear in the client portal")
    chat.click(timeout=FAST_UI_TIMEOUT)


def assert_cp_auto_publish_visibility(page: Page, context: dict, should_display: bool) -> None:
    """Open the CP review page as the client and assert the auto-publish checkbox visibility.

    Waits for the review page and the `review-settings-loaded` marker (so the
    auto-publish decision has been computed) before checking `.auto-publish-container`.
    """
    client = context["review_client"]
    pivot_uid = context["auto_account"]["pivot_uid"]
    url = (
        f"{vitrage_base(context)}/site/{pivot_uid}/activity/review"
        f"?client_jwt={client['token']}"
    )
    page.goto(url, wait_until="domcontentloaded")

    if _wait_cp_frame(page, REVIEW_READY, timeout=CP_LOAD_TIMEOUT) is None:
        raise AssertionError("Client-portal review page (cp_iframe) did not become ready")
    if not _wait_presence(page, REVIEW_SETTINGS_LOADED, timeout=CP_LOAD_TIMEOUT):
        raise AssertionError("CP review settings did not finish loading (review-settings-loaded absent)")

    if should_display:
        if _wait_in_frame(page, REVIEW_READY, AUTO_PUBLISH_CONTAINER) is None:
            raise AssertionError("Expected the CP auto-publish checkbox to be displayed, but it was not")
    else:
        if _count_in_frames(page, AUTO_PUBLISH_CONTAINER) != 0:
            raise AssertionError("Expected the CP auto-publish checkbox to NOT be displayed, but it was")


def _wait_presence(page: Page, selector: str, timeout: int = CP_LOAD_TIMEOUT) -> bool:
    """Wait until `selector` exists in any frame (presence only; ignores visibility)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        if _count_in_frames(page, selector) > 0:
            return True
        time.sleep(0.2)
    return False


def _count_in_frames(page: Page, selector: str) -> int:
    frame = page.frame(name="cp_iframe")
    candidates = [frame, *page.frames] if frame is not None else list(page.frames)
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            count = candidate.locator(selector).count()
            if count > 0:
                return count
        except Exception:
            continue
    return 0


def _frame_with(page: Page, selector: str):
    """Return the cp_iframe (or any frame) that currently contains `selector`."""
    frame = page.frame(name="cp_iframe")
    candidates = [frame, *page.frames] if frame is not None else list(page.frames)
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            if candidate.locator(selector).count() > 0:
                return candidate
        except Exception:
            continue
    return None


def _wait_cp_frame(page: Page, ready_selector: str, timeout: int = CP_LOAD_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _frame_with(page, ready_selector)
        if frame is not None:
            return frame
        time.sleep(0.2)
    return None


def _wait_in_frame(page: Page, ready_selector: str, target_selector: str,
                   timeout: int = FAST_UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _frame_with(page, target_selector) or _frame_with(page, ready_selector)
        if frame is not None:
            locator = frame.locator(target_selector)
            for index in range(locator.count()):
                candidate = locator.nth(index)
                try:
                    if candidate.is_visible():
                        return candidate
                except Exception:
                    continue
        time.sleep(0.1)
    return None
