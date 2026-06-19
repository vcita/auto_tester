"""UI helpers for the auto_client_messages test (VCITA2-14249).

Migrated from automation-js:
  steps/desktop/settings.js          (user updates auto reply message)
  steps/desktop/businessPage.js      (client leaves details / success page)
  pages/desktop/Frontage/Settings/autoClientMessages.js
  pages/desktop/Vitrage/livesite.js  (Livesite + LeaveDetailsForm)

All selectors below were verified live on integration (app.meet2know.com /
live.meet2know.com) via Playwright MCP.

Two surfaces:
- Back office (settings): /app/settings/messages. The whole legacy settings page
  renders inside `#angular-iframe`. Tabs (Booking / Payments / Messages & Documents
  / SMS Settings) live there; the auto-reply text is a TinyMCE editor nested one
  level deeper (`.mce-edit-area iframe` -> `#tinymce`). Save:
  `button[data-qa="action-button-client_notifications-save"]`. The save
  confirmation ("Changes saved") renders at the TOP page level, not inside the
  angular iframe (matches the legacy `successToast` switching to default content).
- Public livesite: <CP_VITRAGE>/site/<pivot_uid> (same CP base + `#cp_iframe`
  pattern as the estimates / coupons CP helpers). The "Leave details" action opens
  a Vuetify contact form inside `#cp_iframe` (fields resolved by accessible label);
  the success page shows the configured auto-reply text in `div.second-row`.

All element/interaction waits are capped at 5s (UI_TIMEOUT) per project policy.
A larger NAV budget is used only for the settings/livesite/iframe (re)load points,
tied to a concrete readiness signal. The single fixed wait in this flow is the
bounded (<2s) TinyMCE->Angular debounce sync before save, which has no external
readiness signal (see EDITOR_SYNC_DEBOUNCE_MS).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.salsa.sales.estimates.estimates_helpers import CP_VITRAGE, pivot_uid

UI_TIMEOUT = 5000
# TinyMCE -> Angular ng-model sync is debounced; the save payload only includes the
# new auto-reply text after this debounce fires. No external readiness signal is
# exposed, so a minimal bounded wait is unavoidable here (verified at 1.5s).
EDITOR_SYNC_DEBOUNCE_MS = 1500
# Angular settings iframe / livesite / client-portal iframe (re)load points only;
# conditional waits on a real readiness signal (tab, TinyMCE body, leave-details
# link, form field, success row), not a sleep.
NAV_TIMEOUT = 20000

# Back-office settings (everything is inside #angular-iframe)
SETTINGS_IFRAME = "#angular-iframe"
MESSAGES_TAB = 'span[translate="settings.client_notifications.tabs.messages"][aria-hidden="false"]'
AUTO_REPLY_IFRAME = ".mce-edit-area iframe"
AUTO_REPLY_BODY = "#tinymce"
SAVE_BUTTON = 'button[data-qa="action-button-client_notifications-save"]'
SAVE_CONFIRMATION = "Changes saved"  # top-level toast text

# Public livesite leave-details
LEAVE_DETAILS_ACTION = 'a.business-action[ng-href*="leave-details"]'
CP_IFRAME = "#cp_iframe"
SUCCESS_ROW = "div.second-row"
# Vuetify form fields are resolved by their accessible label inside #cp_iframe.
FIELD_LABELS = {
    "subject": "Subject",
    "message": "Message",
    "email": "Email",
    "first_name": "First Name",
    "last_name": "Last Name",
}


def _app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def update_auto_reply(page: Page, context: dict, text: str) -> None:
    """Update the auto-reply message text in settings and save it.

    Mirrors AutoClientMessages.updateMessageAutoReply: open the Messages &
    Documents tab, type the new value into the TinyMCE auto-reply editor, save, and
    wait for the top-level "Changes saved" confirmation (the legacy success toast)."""
    base = _app_base(context)
    page.goto(f"{base}/app/settings/messages", wait_until="domcontentloaded")

    settings = page.frame_locator(SETTINGS_IFRAME)
    # The save button is always present once the settings form has rendered.
    save = settings.locator(SAVE_BUTTON).first
    save.wait_for(state="visible", timeout=NAV_TIMEOUT)

    tab = settings.locator(MESSAGES_TAB).first
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()

    # TinyMCE auto-reply editor: contenteditable body inside its own iframe nested
    # within the angular iframe.
    body = settings.frame_locator(AUTO_REPLY_IFRAME).locator(AUTO_REPLY_BODY)
    body.wait_for(state="visible", timeout=NAV_TIMEOUT)
    body.click()
    # Clear existing content then type the new value (legacy clears before sendKeys).
    # Control+a selects all, Delete clears, then press_sequentially types char by
    # char. Per-char typing is required so TinyMCE's keyup handler fires and the
    # editor marks the Angular model dirty (a bulk type() does NOT trigger the
    # binding, and the save payload then omits messages_auto_response — verified).
    body.press("Control+a")
    body.press("Delete")
    body.press_sequentially(text, delay=40)
    expect(body).to_have_text(text, timeout=UI_TIMEOUT)

    # The TinyMCE -> Angular ng-model sync is DEBOUNCED on input: the save payload
    # only carries messages_auto_response once the debounce has fired after the last
    # keystroke (verified via network capture — without this pause PUT /v2/settings
    # drops the field and the livesite keeps the default reply). No external state
    # signal exposes the debounce, so this is a minimal, bounded (<2s) wait — the
    # only place a fixed wait is genuinely unavoidable in this flow.
    page.wait_for_timeout(EDITOR_SYNC_DEBOUNCE_MS)

    save.click()
    # The "Changes saved" alert renders at the top page level (the legacy success
    # toast). This is the real save-committed signal.
    page.get_by_text(SAVE_CONFIRMATION, exact=False).first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def leave_details_on_livesite(page: Page, context: dict, details: dict) -> None:
    """Open the public livesite, choose "Leave details", fill and submit the form.

    Mirrors Livesite.leaveDetails + LeaveDetailsForm.submit. The form renders inside
    the client-portal iframe (`#cp_iframe`); fields are resolved by accessible
    label (the Vuetify form no longer nests input under label, so a label-text
    locator is the stable choice)."""
    livesite_url = f"{CP_VITRAGE}/site/{pivot_uid(context)}"
    page.goto(livesite_url, wait_until="domcontentloaded")

    leave_details = page.locator(LEAVE_DETAILS_ACTION).first
    leave_details.wait_for(state="visible", timeout=NAV_TIMEOUT)
    leave_details.click()

    cp = page.frame_locator(CP_IFRAME)
    # The Subject field is the readiness signal that the CP form rendered.
    subject = cp.get_by_label(FIELD_LABELS["subject"], exact=True).first
    subject.wait_for(state="visible", timeout=NAV_TIMEOUT)

    for key, label in FIELD_LABELS.items():
        value = details.get(key)
        if not value:
            continue
        field = cp.get_by_label(label, exact=True).first
        field.wait_for(state="visible", timeout=UI_TIMEOUT)
        field.click()
        field.fill(value)

    submit = cp.get_by_role("button", name="Submit").first
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click()


def assert_success_message(page: Page, expected: str) -> None:
    """Assert the livesite success page shows the auto-reply text exactly.

    Mirrors Livesite.verifySuccessMessage: read `div.second-row` inside `#cp_iframe`
    and assert it equals the configured auto-reply message."""
    cp = page.frame_locator(CP_IFRAME)
    success = cp.locator(SUCCESS_ROW).first
    success.wait_for(state="visible", timeout=NAV_TIMEOUT)
    expect(success).to_have_text(expected, timeout=UI_TIMEOUT)
