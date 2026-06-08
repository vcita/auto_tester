"""Shared UI helpers for the matters_management subcategory.

Migrated from automation-js page objects (VCITA2-13952):
  pages/desktop/Frontage/Clients/client.js  (Client, NestingDialog, NewClientDialog)
  pages/desktop/Frontage/quickactions.js     (QuickActions.addClient)

The matter detail page is the legacy Frontage page rendered inside nested iframes:
  page -> iframe[title="angularjs"] (outer/Angular) -> #vue_iframe_layout (inner/Vue).

Selectors verified live on integration (app.meet2know.com), 2026-06-08.
All waits are capped at 5s per the project wait policy; transient matter-page load
slowness is absorbed by a bounded open retry (1 attempt + 2 retries), not longer waits.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000
OPEN_ATTEMPTS = 3  # 1 + 2 retries (project policy)

OUTER_IFRAME = 'iframe[title="angularjs"]'
INNER_IFRAME = "#vue_iframe_layout"

# Matter detail (inner Vue frame)
MATTER_TITLE = ".matter-name-title"
MATTER_LIST_ROW = ".matter-list-row"
CONTACT_EMAIL = ".tooltips-wrapper .info-row_text-value"
ADD_MATTER_BUTTON = ".add-matter-button"

# Nesting dialog (inner Vue frame)
NEST_SEARCH = "#clientSearchAutocomplete input"
NEST_ROW = ".client-row"
NEST_CONFIRM = "[data-qa='dialog-submit-button']"

# Matter More menu (outer Angular frame)
MORE_OPTION = "[data-qa='more-option']"
NESTING_ACTION = "[data-qa='nesting']"

# New-client/matter dialog (outer Angular frame, md-dialog)
DIALOG_CONTINUE = "[ng-click='continue()']"
MATTER_NAME_INPUT = "f-client-field[field*='matterName'] input"
DIALOG_SAVE = "button:has-text('Save')"
DIALOG_FIRST_NAME = "input[name='first_name']"

# Quick Actions (top POV page)
QA_BUTTON = "[data-qa='vcMenu-QuickAction']"
QA_ADD_CLIENT = "[data-qa='item-client']"
QA_EMAIL_FIELD = "input[name='email']"
QA_EMAIL_AUTOCOMPLETE = "#autocomplete-email"
# "This email already exists" dialog: click the md-radio-button element itself —
# its inner label span is not the pointer-event target, so clicking the text hangs
# on actionability (this was the original 30s timeout).
QA_NEW_UNDER_CONTACT_RADIO = 'md-radio-button[aria-label="Create a new client under this contact"]'
QA_EXISTS_CONTINUE = "button[ng-click='ok()']"          # confirm the radio choice
QA_ADD_CLIENT_CONFIRM = "button[ng-click='continue()']"  # "Add new client under <contact>" confirm


def app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def matter_frames(page: Page):
    """Return (inner Vue frame_locator, outer Angular frame_locator)."""
    outer = page.frame_locator(OUTER_IFRAME)
    inner = outer.frame_locator(INNER_IFRAME)
    return inner, outer


def open_matter_page(page: Page, context: dict, client_id: str):
    """Navigate to a matter detail page and wait for it to be ready.

    Bounded retry (1 + 2) absorbs transient integration load spikes without any
    single wait exceeding the 5s cap.
    """
    base = app_base(context)
    last_error: Exception | None = None
    for attempt in range(OPEN_ATTEMPTS):
        try:
            page.goto(f"{base}/app/clients/{client_id}", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
        except Exception as error:  # navigation hiccup -> retry
            last_error = error
        inner, outer = matter_frames(page)
        try:
            inner.locator(MATTER_TITLE).first.wait_for(state="visible", timeout=UI_TIMEOUT)
            return inner, outer
        except Exception as error:
            last_error = error
            print(f"    [open_matter] retry {attempt + 1}/{OPEN_ATTEMPTS}")
    raise AssertionError(f"Matter page {client_id} did not become ready: {last_error}")


def matter_list_names(inner) -> list[str]:
    rows = inner.locator(MATTER_LIST_ROW)
    rows.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return [t.strip() for t in rows.all_inner_texts()]


def wait_matter_listed(inner, matter_name: str) -> None:
    """Wait (in-place) for a newly created matter to appear in the matter list.

    The create POST completes shortly after the dialog closes; confirming the row
    here both verifies success and prevents a follow-up navigation from aborting
    the in-flight request.
    """
    inner.locator(MATTER_LIST_ROW).filter(has_text=matter_name).first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def displayed_contact_email(inner) -> str:
    field = inner.locator(CONTACT_EMAIL).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    return field.inner_text().strip()


def matter_title(inner) -> str:
    title = inner.locator(MATTER_TITLE).first
    title.wait_for(state="visible", timeout=UI_TIMEOUT)
    return title.inner_text().strip()


def assert_matter_under_contact(page: Page, context: dict, contact_id: str,
                                matter_name: str, contact_email: str) -> None:
    """Open the contact's matter page and assert the matter is listed and the
    displayed contact email matches (legacy `matter exists under contact`)."""
    inner, _ = open_matter_page(page, context, contact_id)
    # Bounded re-check (1 + 2): a just-created matter can lag one render.
    for attempt in range(OPEN_ATTEMPTS):
        names = matter_list_names(inner)
        if any(matter_name in n for n in names):
            break
        print(f"    [assert] '{matter_name}' not in {names}; reload {attempt + 1}")
        inner, _ = open_matter_page(page, context, contact_id)
    else:
        raise AssertionError(f"Matter {matter_name!r} not found under contact {contact_id}: {matter_list_names(inner)}")

    email = displayed_contact_email(inner)
    assert email == contact_email, f"Contact email expected {contact_email!r}, got {email!r}"
    print(f"  [OK] '{matter_name}' exists under contact {contact_email}")


def _type_matter_name(name_input, matter_name: str) -> None:
    # Angular f-client-field input: real keystrokes are required for ng-model to
    # register (plain .fill() sets the value but Angular ignores it, so Save would
    # submit an empty matter name). Mirrors legacy enterText / create_matter.
    # The keystroke->ng-model commit can lag, so verify the value landed and
    # re-type once if the field is still empty (bounded, no fixed sleeps).
    for _ in range(2):
        name_input.click()
        name_input.press_sequentially(matter_name, delay=40)
        try:
            expect(name_input).to_have_value(matter_name, timeout=2000)
            return
        except AssertionError:
            name_input.fill("")
    expect(name_input).to_have_value(matter_name, timeout=2000)


def _click_continue_if_present(outer) -> None:
    """Click the dialog CONTINUE step if it is shown; the matter form otherwise renders directly.

    Waits for whichever of {CONTINUE, matter-name field} appears first (bounded at 5s),
    so an absent CONTINUE costs no extra wait.
    """
    continue_btn = outer.locator(DIALOG_CONTINUE).first
    name_input = outer.locator(MATTER_NAME_INPUT).first
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if continue_btn.is_visible():
            continue_btn.click()
            return
        if name_input.is_visible():
            return
    # Fall through: let the caller's explicit wait surface a clear error.


def _fill_matter_name_and_save(page: Page, outer, matter_name: str) -> None:
    name_input = outer.locator(MATTER_NAME_INPUT).first
    name_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    _type_matter_name(name_input, matter_name)
    save_btn = outer.locator(DIALOG_SAVE).first
    save_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_btn.click()
    # The dialog closes immediately, but the create POST is still in flight.
    # Wait for the save control to detach so a follow-up navigation does not abort
    # the request (which would silently drop the new matter).
    save_btn.wait_for(state="detached", timeout=UI_TIMEOUT)


def add_matter_from_pane(page: Page, inner, outer, matter_name: str) -> None:
    """Add a matter under the open contact via the contact-pane Add matter action."""
    add_btn = inner.locator(ADD_MATTER_BUTTON).first
    add_btn.wait_for(state="attached", timeout=UI_TIMEOUT)
    # Regular click is intercepted on this control; dispatch a native click (matches
    # legacy clickWebElementByJS usage for Angular-Material controls).
    add_btn.evaluate("el => el.click()")

    # The Add-Client dialog sometimes opens on a CONTINUE confirmation step and
    # sometimes straight on the matter form; click CONTINUE only when it appears.
    _click_continue_if_present(outer)

    _fill_matter_name_and_save(page, outer, matter_name)
    # Confirm in-place: the contact's matter list refreshes with the new matter.
    wait_matter_listed(inner, matter_name)


def _qa_confirm_create_under_contact(outer) -> None:
    """Advance from the "email already exists" choice to the new-matter form.

    The first CONTINUE (``ok()``) is always shown. A second "Add client under
    <contact>" CONTINUE (``continue()``) appears only sometimes (it is absent when a
    matter was just added under the same contact). So click ``ok()``, then click the
    second confirm only while it is visible, returning once the matter-name field is
    reachable (i.e. no confirmation modal is on top). Bounded at the 5s cap with no
    fixed sleeps. Mirrors the existing ``_click_continue_if_present`` pattern.
    """
    ok_btn = outer.locator(QA_EXISTS_CONTINUE).first
    ok_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    ok_btn.click()

    confirm2 = outer.locator(QA_ADD_CLIENT_CONFIRM).first
    name_input = outer.locator(MATTER_NAME_INPUT).first
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if confirm2.is_visible():
            confirm2.click()
            continue
        if name_input.is_visible():
            return
    # Fall through: the caller's explicit matter-name wait surfaces a clear error.


def add_matter_from_quick_actions(page: Page, context: dict, contact_email: str, matter_name: str) -> None:
    """Add a matter under an existing contact via Quick Actions -> Add client
    (suggested-contact flow). The dialog renders in the outer Angular frame.

    Entry is normalized to the dashboard so the Quick Actions menu opens from a
    consistent state regardless of where the previous test left the page.
    """
    page.goto(f"{app_base(context)}/app/dashboard", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    _, outer = matter_frames(page)

    qa_btn = page.locator(QA_BUTTON).first
    qa_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    qa_btn.click(timeout=UI_TIMEOUT)
    add_client = page.locator(QA_ADD_CLIENT).first
    add_client.wait_for(state="visible", timeout=UI_TIMEOUT)
    add_client.click(timeout=UI_TIMEOUT)

    email_field = outer.locator(QA_EMAIL_FIELD).first
    email_field.wait_for(state="visible", timeout=UI_TIMEOUT)
    email_field.click(timeout=UI_TIMEOUT)
    autocomplete = outer.locator(QA_EMAIL_AUTOCOMPLETE).first
    autocomplete.wait_for(state="visible", timeout=UI_TIMEOUT)
    autocomplete.fill(contact_email, timeout=UI_TIMEOUT)

    suggestion = outer.get_by_text(contact_email, exact=True).first
    suggestion.wait_for(state="visible", timeout=UI_TIMEOUT)
    suggestion.click(timeout=UI_TIMEOUT)

    # "This email already exists" -> create a NEW client (matter) under the contact.
    # Click the md-radio-button element itself; its inner label span is not the
    # pointer-event target (clicking the text hangs on actionability -> 30s timeout).
    radio = outer.locator(QA_NEW_UNDER_CONTACT_RADIO).first
    radio.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Angular-Material radio: the rendered ripple/overlay intercepts a normal click,
    # so force the click on the md-radio-button element itself (legacy used JS click).
    radio.click(force=True, timeout=UI_TIMEOUT)
    _qa_confirm_create_under_contact(outer)

    # First name pre-populates from the chosen contact; then name the matter and save.
    outer.locator(DIALOG_FIRST_NAME).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    _fill_matter_name_and_save(page, outer, matter_name)
    # Saving auto-navigates to the new matter (the create POST has already committed
    # server-side), so the follow-up assertion navigation is safe; no in-place wait.


def nest_matter_under_contact(page: Page, inner, outer, contact_query: str,
                              expected_email: str) -> None:
    """Nest the open matter under another contact via More -> Move client under….

    After confirming, wait in-place for the contact email to switch to the target
    so the nest request finishes before any follow-up navigation/reload.
    """
    more_btn = outer.locator(MORE_OPTION).first
    more_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    more_btn.click()

    nesting_btn = outer.locator(NESTING_ACTION).first
    nesting_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    nesting_btn.click()

    search = inner.locator(NEST_SEARCH).first
    search.wait_for(state="visible", timeout=UI_TIMEOUT)
    search.fill(contact_query)

    row = inner.locator(NEST_ROW).filter(has_text=contact_query).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.click()

    confirm = inner.locator(NEST_CONFIRM).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    confirm.wait_for(state="hidden", timeout=UI_TIMEOUT)
    expect(inner.locator(CONTACT_EMAIL).first).to_have_text(expected_email, timeout=UI_TIMEOUT)


def click_matter_in_list(inner, matter_name: str) -> None:
    """Click a matter row in the matter list (legacy clickOnMatter)."""
    row = inner.locator(MATTER_LIST_ROW).filter(has_text=matter_name).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.click()


def expect_title(inner, matter_name: str) -> None:
    """Assert the matter title heading shows the given matter (legacy `title shows`)."""
    expect(inner.locator(MATTER_TITLE).first).to_have_text(
        re.compile(rf"^\s*{re.escape(matter_name)}\s*$"), timeout=UI_TIMEOUT
    )
