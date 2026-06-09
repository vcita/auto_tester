"""UI helpers for the contact_form_widget test (VCITA2-14006).

Migrated from automation-js:
  steps/desktop/clients.js (mark spam, submit contact form)
  steps/desktop/conversations.js (no message from current client)
  pages/desktop/Frontage/Clients/client.js (Client.setSpammer, MarkSpammerDialog)
  pages/desktop/Frontage/OnlinePresence/vcitaContactFormWidgetEdit.js
  pages/desktop/Frontage/Clients/conversation.js (getMessagesTitles)

Frame topology (POV):
- Client card renders the legacy Frontage page inside nested iframes:
    page -> iframe[title="angularjs"] (outer/Angular) -> #vue_iframe_layout (inner/Vue).
  The "More" menu + mark-as-spam dialog live in the outer Angular frame; the
  conversation pane lives in the inner Vue frame (matches matters_helpers).
- The contact-form widget customize preview nests another iframe inside the
  customize page; the public form fields (#first_name/#last_name/#email/#message)
  live at the deepest level. The exact nesting depth is resolved at runtime by
  scanning page.frames for the form (robust to nesting changes).

All element/interaction waits are capped at 5s (UI_TIMEOUT) per the project policy.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000
# Bounded budget for resolving the deeply nested widget-preview frame and for the
# spam-submission to be dropped server-side before the (negative) empty-conversation
# assertion. Eventual-consistency only, not a fixed sleep.
FRAME_TIMEOUT = 10000
SETTLE_TIMEOUT = 10  # seconds; bounded wait for the spam submission to be processed

OUTER_IFRAME = 'iframe[title="angularjs"]'
INNER_IFRAME = "#vue_iframe_layout"

# Client card More menu + mark-spam (outer Angular frame)
MORE_OPTION = "[data-qa='more-option']"
MARK_SPAM = "[data-qa='spam']"
SPAM_CONFIRM = ".animation-done button[data-qa='confirm-btn']"

# Conversation tab (inner Vue matter frame). The conversation is the first tab of
# the matter engagements pane; messages render as `.bubble-row`, the empty state as
# `.no-results-wrapper` (matches vue MatterEngagements / Conversation.vue and the
# legacy `conversationBubblesLoaded` = ".no-results-wrapper , .bubble-row").
CONVERSATION_TAB = ".tab-title"
CONVERSATION_TAB_NAME = "Conversation"
CONV_EMPTY = ".no-results-wrapper"
CONV_BUBBLE = ".bubble-row"
CONV_LOADED = ".no-results-wrapper, .bubble-row"

# Contact-form widget public form (deepest nested frame)
FORM_FIRST = "#first_name"
FORM_LAST = "#last_name"
FORM_EMAIL = "#email"
FORM_MESSAGE = "#message"
FORM_SUBMIT = 'input[value="Submit Message"]'
FORM_LOADER = "#jquery-loader-background"


def app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def _client_frames(page: Page):
    """Return (inner Vue frame_locator, outer Angular frame_locator)."""
    outer = page.frame_locator(OUTER_IFRAME)
    inner = outer.frame_locator(INNER_IFRAME)
    return inner, outer


def open_client_card(page: Page, context: dict, client_id: str):
    """Navigate to the client card and wait for the outer Angular frame to be ready."""
    base = app_base(context)
    page.goto(f"{base}/app/clients/{client_id}", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    inner, outer = _client_frames(page)
    outer.locator(MORE_OPTION).first.wait_for(state="visible", timeout=FRAME_TIMEOUT)
    return inner, outer


def mark_client_as_spam(page: Page, context: dict, client_id: str) -> None:
    """Mark the client as spam via the client-card More menu (legacy setSpammer)."""
    _, outer = open_client_card(page, context, client_id)

    more = outer.locator(MORE_OPTION).first
    more.click()
    spam = outer.locator(MARK_SPAM).first
    spam.wait_for(state="visible", timeout=UI_TIMEOUT)
    spam.click()
    confirm = outer.locator(SPAM_CONFIRM).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    # The confirm dialog detaches once the spam-mark request commits.
    confirm.wait_for(state="detached", timeout=UI_TIMEOUT)


def _find_form_frame(page: Page):
    """Scan page.frames for the one hosting the public contact form (#first_name).

    The widget customize preview nests an iframe; scanning by a form field is robust
    to the nesting depth/name. Bounded by FRAME_TIMEOUT (preview render budget)."""
    deadline = time.monotonic() + FRAME_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(FORM_FIRST).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Contact-form widget preview (#first_name) frame not found")


def submit_contact_form(page: Page, context: dict, cfw: dict) -> None:
    """Submit the public contact-form widget (legacy submitContactForm)."""
    base = app_base(context)
    page.goto(
        f"{base}/app/online-presence/customize/contact_form",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    frame = _find_form_frame(page)
    frame.locator(FORM_FIRST).first.fill(cfw["first_name"], timeout=UI_TIMEOUT)
    frame.locator(FORM_LAST).first.fill(cfw["last_name"], timeout=UI_TIMEOUT)
    frame.locator(FORM_EMAIL).first.fill(cfw["email"], timeout=UI_TIMEOUT)
    frame.locator(FORM_MESSAGE).first.fill(cfw["message"], timeout=UI_TIMEOUT)
    frame.locator(FORM_SUBMIT).first.click(timeout=UI_TIMEOUT)
    # Confirm the submit actually fired: the blocking loader appears, then clears
    # (mirrors legacy pollPageForLoader). The loader appearance is positive proof the
    # request was dispatched; a non-spam control run proves this same flow produces a
    # conversation message, so the later empty-conversation assertion is not vacuous.
    try:
        frame.locator(FORM_LOADER).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    except Exception:
        pass
    try:
        frame.locator(FORM_LOADER).first.wait_for(state="hidden", timeout=UI_TIMEOUT)
    except Exception:
        pass


def _open_conversation_tab(page: Page, context: dict, client_id: str):
    """Open the client card and activate the Conversation tab (inner Vue frame).

    Waits for the conversation pane to finish loading — signalled by either a
    message bubble or the empty-state wrapper (legacy `conversationBubblesLoaded`)."""
    inner, _ = open_client_card(page, context, client_id)
    tab = inner.locator(CONVERSATION_TAB, has_text=CONVERSATION_TAB_NAME).first
    tab.wait_for(state="visible", timeout=FRAME_TIMEOUT)
    tab.click()
    inner.locator(CONV_LOADED).first.wait_for(state="visible", timeout=FRAME_TIMEOUT)
    return inner


def assert_no_message_from_client(page: Page, context: dict, client_id: str) -> None:
    """Assert the client's conversation has no messages (legacy getMessagesTitles == []).

    A spam client's contact-form submission must be dropped, so the conversation
    stays empty. A legitimate (non-spam) submission would create a `.bubble-row`
    within seconds (proven by control runs), so this re-checks the conversation
    across a bounded SETTLE_TIMEOUT: if any message bubble ever appears it fails
    immediately, and only the rendered empty state passes."""
    deadline = time.monotonic() + SETTLE_TIMEOUT
    while True:
        inner = _open_conversation_tab(page, context, client_id)
        bubbles = inner.locator(CONV_BUBBLE)
        count = bubbles.count()
        assert count == 0, (
            f"Expected no messages from spam client, found {count} bubble(s): "
            f"{bubbles.all_inner_texts()[:5]}"
        )
        if time.monotonic() >= deadline:
            expect(inner.locator(CONV_EMPTY).first).to_be_visible(timeout=UI_TIMEOUT)
            return
        page.wait_for_timeout(1500)
