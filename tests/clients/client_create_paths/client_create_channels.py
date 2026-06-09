"""Livesite leave-details + client-portal conversation channels (VCITA2-14007).

Split from client_create_helpers to keep each helper module focused. These two
surfaces (public Vitrage livesite and the client portal) live on separate domains
derived from the app base url.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.clients.client_create_paths.client_create_helpers import app_base

UI_TIMEOUT = 5000
PAGE_TIMEOUT = 20000

# Livesite (Vitrage) — public business site
LIVESITE_ACTIONS = "a.business-action, .action-content"
LEAVE_DETAILS_ACTION = 'a.business-action[href*="leave-details"], a.business-action[ng-href*="leave-details"]'
CP_IFRAME = 'iframe[name="cp_iframe"], #cp_iframe'
# The leave-details form renders inside cp_iframe (clients portal). Fields share generic
# data-qa values, so anchor each on its label via the document-order `following` axis.
LD_SUBJECT = "xpath=//label[normalize-space()='Subject']/following::input[1]"
LD_MESSAGE = "xpath=//label[normalize-space()='Message']/following::textarea[1]"
LD_EMAIL = "xpath=//label[normalize-space()='Email']/following::input[1]"
LD_FIRST = "xpath=//label[normalize-space()='First Name']/following::input[1]"
LD_LAST = "xpath=//label[normalize-space()='Last Name']/following::input[1]"
LD_SUBMIT = "xpath=//button[contains(., 'Submit')]"


def vitrage_base(context: dict) -> str:
    """Public Vitrage livesite base, matching the convention used across auto_tester
    (`reviews_cp_ui`, `estimates_helpers`): app.meet2know -> live.meet2know,
    app.vcita -> live.vcita, fenv app-<name>... -> vitrage-<name>...."""
    base = app_base(context)
    if "app.meet2know.com" in base:
        return "https://live.meet2know.com"
    if "app.vcita.com" in base:
        return "https://live.vcita.com"
    if "app-" in base and ".external.int-eks.vchost.co" in base:
        return base.replace("https://app-", "https://vitrage-", 1)
    raise ValueError(f"Cannot derive vitrage base URL from base_url={base!r}")


def livesite_leave_details(page: Page, context: dict, details: dict) -> None:
    """Open the public livesite, pick Leave-details, fill and submit the form."""
    pivot = context["auto_account"]["pivot_uid"]
    page.goto(f"{vitrage_base(context)}/site/{pivot}", wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    page.locator(LIVESITE_ACTIONS).first.wait_for(state="visible", timeout=PAGE_TIMEOUT)
    page.locator(LEAVE_DETAILS_ACTION).first.click(timeout=UI_TIMEOUT)

    frame = page.frame_locator(CP_IFRAME)
    frame.locator(LD_SUBJECT).first.wait_for(state="visible", timeout=PAGE_TIMEOUT)
    if details.get("subject"):
        frame.locator(LD_SUBJECT).first.fill(details["subject"], timeout=UI_TIMEOUT)
    if details.get("message"):
        frame.locator(LD_MESSAGE).first.fill(details["message"], timeout=UI_TIMEOUT)
    if details.get("email"):
        frame.locator(LD_EMAIL).first.fill(details["email"], timeout=UI_TIMEOUT)
    if details.get("first_name"):
        frame.locator(LD_FIRST).first.fill(details["first_name"], timeout=UI_TIMEOUT)
    if details.get("last_name"):
        frame.locator(LD_LAST).first.fill(details["last_name"], timeout=UI_TIMEOUT)
    frame.locator(LD_SUBMIT).first.click(timeout=UI_TIMEOUT)


# Client portal conversation (legacy conversations.js + clientPortalSettings.js).
# Flow: open the Client Portal editor, click "View as demo client" (opens a popup
# window onto the business owner's own client portal), open the conversation page,
# and read the conversation bubble headers.
PORTAL_EDITOR_PATH = "/app/client-portal-editor"
VIEW_AS_DEMO_BTN = 'button:has-text("View as demo client")'
CP_PRIMARY_ACTIVITY = ".primary-activity"
CP_CHAT_BUTTON = '[data-qa="headerChatBtn"]'
CP_VAPP = ".v-application--wrap"
CP_BUBBLE_HEADER = '[data-qa="bubble-header"]'


def _frame_with(page: Page, selector: str, timeout_ms: int):
    """Return the first frame whose tree contains ``selector`` (scans page.frames).

    Robust to angular/vue iframe nesting and name changes."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError(f"No frame containing {selector!r} found within {timeout_ms}ms")


def assert_portal_conversation(page: Page, context: dict, title: str) -> None:
    """Assert a conversation titled ``title`` shows in the client portal.

    Mirrors legacy: ClientPortalSettings.viewAsDemoClient ->
    ClientPortalDashboard.OpenConversationPage -> ClientPortalConversation.getConversationTitles."""
    page.goto(f"{app_base(context)}{PORTAL_EDITOR_PATH}", wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    editor_frame = _frame_with(page, VIEW_AS_DEMO_BTN, PAGE_TIMEOUT)
    editor_frame.locator(VIEW_AS_DEMO_BTN).first.wait_for(state="visible", timeout=PAGE_TIMEOUT)

    with page.context.expect_page() as popup_info:
        editor_frame.locator(VIEW_AS_DEMO_BTN).first.click(timeout=UI_TIMEOUT)
    portal = popup_info.value
    portal.wait_for_load_state("domcontentloaded")

    cp = _frame_with(portal, CP_PRIMARY_ACTIVITY, PAGE_TIMEOUT)
    cp.locator(CP_CHAT_BUTTON).first.wait_for(state="visible", timeout=PAGE_TIMEOUT)
    cp.locator(CP_CHAT_BUTTON).first.click(timeout=UI_TIMEOUT)

    conv = _frame_with(portal, CP_VAPP, PAGE_TIMEOUT)
    deadline = time.monotonic() + PAGE_TIMEOUT / 1000
    while time.monotonic() < deadline:
        headers = conv.locator(CP_BUBBLE_HEADER)
        if headers.count():
            texts = headers.all_inner_texts()
            if any(title in t for t in texts):
                portal.close()
                return
        portal.wait_for_timeout(1000)
    portal.close()
    raise AssertionError(f"Client portal did not show a conversation titled {title!r}")
