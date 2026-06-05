"""CRM bulk-action UI helpers for the crm_bulk_actions migration (VCITA2-13798).

Covers the three legacy bulk actions on the POV new-CRM page (`/app/clients`):
share document, send message, delete — plus the client-card conversation and
documents-page assertions. API client creation reuses ``tests.account_api``.

Frame topology (verified live on integration):
- CRM list + bulk-action bar/menu + delete dialogs: top-level POV page.
- Share / message dialogs: ``iframe[title="angularjs"] -> #vue_wizard_iframe``.
- Client-card conversation: ``iframe[title="angularjs"] -> #vue_iframe_layout``.
- Documents page list: ``iframe[title="angularjs"] -> #vue_iframe_main``.
"""

import time
from typing import Iterable

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

UI_TIMEOUT = 5_000
CLIENTS_PAGE_TIMEOUT = 5_000
CLIENTS_READY_TIMEOUT = 5_000
# Conversation / documents propagation goes through the async communication
# pipeline; reload-and-recheck a bounded number of times (same class as the
# seeker-index lag handled elsewhere), each wait capped at the 5s UI policy.
PROPAGATION_ATTEMPTS = 3
# Deletion leaves the CRM seeker index asynchronously and can lag longer than the
# conversation/document propagation, so give the delete verification more reloads.
DELETE_ATTEMPTS = 5
# The documents list renders a desktop or mobile docuform item depending on the
# inner iframe's Vuetify breakpoint (mdAndUp). Both share data-qa="docuform-status"
# but the desktop item shows the full label ("Pending review") while the mobile
# item shows the short label ("Pending"). The shared plain document is always in
# the pending_review state (no signature required → never pending_approval), so
# accept either rendering of that single state.
PENDING_REVIEW = "PENDING REVIEW"
PENDING_REVIEW_LABELS = ("PENDING REVIEW", "PENDING")


# --------------------------------------------------------------------------- #
# Frame accessors
# --------------------------------------------------------------------------- #
def _wizard_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_wizard_iframe")


def _conversation_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_iframe_layout")


def _documents_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_iframe_main")


# --------------------------------------------------------------------------- #
# CRM navigation / readiness (pattern from crm_filters_helpers)
# --------------------------------------------------------------------------- #
def open_clients_list(page: Page) -> None:
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/clients", wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
    wait_for_clients_table(page)


def wait_for_clients_table(page: Page) -> None:
    page.wait_for_url("**/app/clients**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    page.locator(".table-actions__filter").first.wait_for(state="visible", timeout=CLIENTS_READY_TIMEOUT)
    try:
        expect(page.locator(".v-skeleton-loader__list-item")).to_have_count(0, timeout=CLIENTS_READY_TIMEOUT)
    except (PlaywrightTimeoutError, AssertionError):
        pass


def _client_row(page: Page, client_name: str):
    return page.locator('[data-qa="CrmTable-All"] tbody tr').filter(has_text=client_name).first


# --------------------------------------------------------------------------- #
# Selection
# --------------------------------------------------------------------------- #
def select_all_pages(page: Page) -> None:
    page.locator('[data-qa="checkbox-dropdown-icon"]').first.click()
    option = page.locator('[data-qa="item-all"]').first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()
    _wait_for_selection(page)


def select_client(page: Page, client_name: str) -> None:
    row = _client_row(page, client_name)
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Vuetify hides the real <input> behind an icon overlay; click the rendered
    # checkbox wrapper (like the legacy JS click on the row checkbox).
    row.locator(".v-input--selection-controls__input").first.click()
    _wait_for_selection(page)


def _wait_for_selection(page: Page) -> None:
    summary = page.locator('[data-qa="summary-text"]').first
    summary.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(summary).to_contain_text("SELECTED", timeout=UI_TIMEOUT)


def _open_more_menu(page: Page) -> None:
    page.locator('[data-qa="bulk-action-button-more"]').first.click()


# --------------------------------------------------------------------------- #
# Bulk actions
# --------------------------------------------------------------------------- #
def bulk_share_document(page: Page, file_path: str) -> None:
    _open_more_menu(page)
    share_option = page.locator('[data-qa="item-share_document"]').first
    share_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    share_option.click()

    wizard = _wizard_frame(page)
    dropzone = wizard.locator('[data-qa="vc-dropzone--input"]')
    dropzone.wait_for(state="attached", timeout=UI_TIMEOUT)
    dropzone.set_input_files(file_path)
    wizard.locator('[data-qa="notify-by-email"]').check()
    share_button = wizard.locator('[data-qa="vc-footer-Share"]')
    expect(share_button).to_be_enabled(timeout=UI_TIMEOUT)
    share_button.click()
    # Share completes by closing the wizard (and POV routing to documents).
    share_button.wait_for(state="hidden", timeout=UI_TIMEOUT)


def bulk_send_message(page: Page, subject: str, content: str) -> None:
    message_button = page.locator('[data-qa="bulk-action-button-message"]').first
    message_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    message_button.click()

    wizard = _wizard_frame(page)
    subject_field = wizard.locator('[data-qa="message-dialog-subject"]')
    subject_field.wait_for(state="visible", timeout=UI_TIMEOUT)
    subject_field.fill(subject)
    # The message body is a contenteditable div, not an <input>; focus then type.
    body = wizard.locator('[data-testid="conversation-input-dialog-message-page_textarea"]')
    body.wait_for(state="visible", timeout=UI_TIMEOUT)
    body.click()
    page.keyboard.type(content)
    send_button = wizard.locator(".message-dialog button.send-btn")
    send_button.click()
    send_button.wait_for(state="hidden", timeout=UI_TIMEOUT)


def bulk_delete(page: Page) -> None:
    _open_more_menu(page)
    delete_option = page.locator('[data-qa="item-delete"]').first
    delete_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    delete_option.click()
    confirm = page.locator('[data-qa="vc-footer-Delete"]').first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    ok_button = page.locator('[data-qa="vc-footer-OK"]').first
    ok_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    ok_button.click()
    ok_button.wait_for(state="hidden", timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


# --------------------------------------------------------------------------- #
# Client-card conversation / documents assertions
# --------------------------------------------------------------------------- #
def open_client_card(page: Page, client_id: str) -> None:
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/clients/{client_id}", wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
    page.wait_for_url("**/app/clients/**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    _conversation_frame(page).locator(".conversation-content").first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def assert_conversation_has_document(page: Page, client_id: str, file_name: str) -> None:
    file_locator = _conversation_frame(page).locator(".conversation-content .file-name").filter(
        has_text=file_name
    )
    for attempt in range(PROPAGATION_ATTEMPTS):
        try:
            expect(file_locator.first).to_be_visible(timeout=UI_TIMEOUT)
            return
        except (PlaywrightTimeoutError, AssertionError):
            if attempt == PROPAGATION_ATTEMPTS - 1:
                raise AssertionError(
                    f"Document {file_name!r} not shown in client {client_id} conversation"
                )
            open_client_card(page, client_id)


def assert_document_status(page: Page, file_name: str) -> None:
    """Assert the shared document is in the pending-review state on the documents page.

    The list is search-index backed and reloads asynchronously, so reload-and-recheck
    a bounded number of times. The status label is read via text_content (raw DOM
    text) and matched against both the desktop and mobile renderings (see
    PENDING_REVIEW_LABELS).
    """
    app_base = page.url.split("/app/")[0]
    actual = ""
    for _ in range(PROPAGATION_ATTEMPTS):
        page.goto(f"{app_base}/app/documents", wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
        docs = _documents_frame(page)
        item = docs.locator(".list-item").filter(has_text=file_name).first
        item.wait_for(state="visible", timeout=UI_TIMEOUT)
        status_locator = item.locator('[data-qa="docuform-status"]').first
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            actual = (status_locator.text_content() or "").strip()
            if actual.upper() in PENDING_REVIEW_LABELS:
                return
            time.sleep(0.3)
    raise AssertionError(
        f"Document {file_name!r} status expected one of {PENDING_REVIEW_LABELS}, got {actual!r}"
    )


def assert_last_message_bubble(page: Page, client_id: str, subject: str, content: str) -> None:
    for attempt in range(PROPAGATION_ATTEMPTS):
        last_row = _conversation_frame(page).locator(".bubble-row").last
        try:
            expect(last_row.locator(".bubble-header")).to_have_text(subject, timeout=UI_TIMEOUT)
            expect(last_row.locator(".bubble-text-row")).to_have_text(content, timeout=UI_TIMEOUT)
            return
        except (PlaywrightTimeoutError, AssertionError):
            if attempt == PROPAGATION_ATTEMPTS - 1:
                raise AssertionError(
                    f"Last message bubble expected subject {subject!r}/content {content!r} "
                    f"for client {client_id}"
                )
            open_client_card(page, client_id)


# --------------------------------------------------------------------------- #
# CRM search + client-list reads (delete verification)
# --------------------------------------------------------------------------- #
def search_clients(page: Page, term: str) -> None:
    search_box = page.locator('[data-qa="CrmTable-All-actionBar-searchBar"]').first
    search_box.wait_for(state="visible", timeout=UI_TIMEOUT)
    # fill is atomic (clear + type + input event) and avoids click interception
    # from the post-delete success toast.
    search_box.fill(term, timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


def visible_client_names(page: Page) -> list[str]:
    empty_state = page.locator('[data-qa="VcEmptyState"]')
    if empty_state.count() > 0 and empty_state.first.is_visible():
        return []
    # all_inner_texts() reads every row in one snapshot, avoiding the default 30s
    # hang that nth(i).inner_text() can hit while the list re-renders during the
    # post-delete seeker-index update.
    return [name.strip() for name in page.locator('[data-qa="matter-name"]').all_inner_texts()]


def assert_visible_clients(page: Page, expected_names: Iterable[str]) -> None:
    expected = sorted(expected_names)
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    actual: list[str] = []
    while time.monotonic() < deadline:
        actual = sorted(visible_client_names(page))
        if actual == expected:
            return
        time.sleep(0.3)
    raise AssertionError(f"Expected visible clients {expected}, got {actual}")


def verify_client_deleted(
    page: Page,
    *,
    remaining_query: str,
    remaining_name: str,
    deleted_query: str,
) -> None:
    """Verify the bulk delete: ``remaining_name`` is still found by ``remaining_query``
    and ``deleted_query`` returns no clients.

    The CRM search ignores a bare numeric token but matches the alpha-prefixed
    name, so each client is looked up by its token-unique first name. The deleted
    client leaves the seeker index asynchronously, so reload the list and re-search
    a bounded number of times before failing.
    """
    for attempt in range(DELETE_ATTEMPTS):
        try:
            open_clients_list(page)
            search_clients(page, remaining_query)
            assert_visible_clients(page, [remaining_name])
            open_clients_list(page)
            search_clients(page, deleted_query)
            assert_visible_clients(page, [])
            return
        except AssertionError:
            if attempt == DELETE_ATTEMPTS - 1:
                raise
