"""UI helpers for the clients_quota test (VCITA2-14005).

Migrated from automation-js features/steps/clients-quota.feature and its page
objects: NewClients, NewClientDialog, UpgradeDialog, ImportClientsDialog, Layout.

Frame topology on the POV app (verified live during runner/MCP exploration):
- CRM list, "+ New" menu, "More actions" menu, system notification and the left
  dashboard menu item: top-level POV page.
- New-client dialog (and its quota banner) and the import wizard: outer Angular
  frame ``iframe[title="angularjs"]`` (legacy md-dialog / import-contacts-wizard).
- The upsell/upgrade dialog renders at top-level POV.

CRM list navigation / selection / bulk delete are reused from
``crm_bulk_helpers`` so there is a single CRM implementation.
"""

import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.clients.crm_bulk_actions.crm_bulk_helpers import (
    bulk_delete,
    open_clients_list,
    select_client,
)

UI_TIMEOUT = 5_000
# After the 11th client is created the quota system notification is updated
# asynchronously (legacy navigates to the dashboard specifically "to allow time for
# system notifications to update"). Re-check the dashboard a bounded number of times,
# each wait capped at the 5s UI policy.
NOTIFICATION_ATTEMPTS = 5
# After a client is deleted the freed-quota state also propagates asynchronously
# through the billing/quota system; observed tail latency can exceed a minute. Until
# it propagates, "+ New -> New client" / import still show the upsell instead of the
# form/wizard. Retry (with a dashboard round-trip to refresh quota) a bounded number
# of times, each wait capped at the 5s UI policy. The common case resolves in 1-2
# attempts; the wider budget only absorbs the rare slow tail.
QUOTA_FREE_ATTEMPTS = 12

OUTER_IFRAME = 'iframe[title="angularjs"]'

# POV CRM action bar / menus
NEW_BUTTON = '[data-qa="new-button"]'
NEW_CLIENT_OPTION = '[data-qa="more-actions-button_new_matter"]'
MORE_ACTIONS_BUTTON = '[data-qa="more-actions-button"]'
IMPORT_OPTION = '[data-qa="more-actions-button_matter_import"]'

# New-client dialog (outer Angular frame, legacy md-dialog.new-client-dialog-component)
DIALOG_ROOT = "md-dialog.new-client-dialog-component"
DIALOG_FIRST = "input[name='first_name']"
DIALOG_LAST = "input[name='last_name']"
DIALOG_EMAIL = "input[name='email']"
DIALOG_SAVE = "//button/div[text()='Save']"
DIALOG_CANCEL = "//button[text()='Cancel']"
# The dialog renders three notification-message banners; only the visible quota
# banner carries the `fully-clickable` class (the other two are `ng-hide`).
DIALOG_BANNER = "div.notification-message.announce.fully-clickable"

# Upsell / upgrade dialog (POV top-level, legacy GenericUpsellDialog)
UPGRADE_ROOT = '[data-qa="GenericUpsellDialog-upsell-modal"]'
UPGRADE_CLOSE = '[data-qa="GenericUpsellDialog-upsell-modal-close-button"]'

# Import wizard (outer Angular frame, legacy import-contacts-wizard)
IMPORT_WIZARD = ".import-contacts-wizard"

# Layout (POV top-level)
DASHBOARD_MENU = '[data-qa="VcMenuItem-dashboard"]'
QUOTA_NOTIFICATION = '[data-qa="vc-notification-clients_quota_exceeded"]'


def _outer(page: Page):
    return page.frame_locator(OUTER_IFRAME)


def _open_new_client_menu(page: Page) -> None:
    new_button = page.locator(NEW_BUTTON).first
    new_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    new_button.click()
    option = page.locator(NEW_CLIENT_OPTION).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _open_import_menu(page: Page) -> None:
    more_button = page.locator(MORE_ACTIONS_BUTTON).first
    more_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    more_button.click()
    option = page.locator(IMPORT_OPTION).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _fill_text(locator, value: str) -> None:
    locator.wait_for(state="visible", timeout=UI_TIMEOUT)
    locator.click()
    locator.fill(value)


def _type_dynamic_email(page: Page, locator, value: str) -> None:
    """Type into the email field via real keystrokes.

    The email input is a dynamic field that "blinks" in and out of an interactable
    state (legacy enterTextToDynamicField), so Playwright's .fill() (which waits for
    a stable editable state) hangs. Focus it and type through the keyboard, mirroring
    the legacy sendKeys path. The short settle lets the dynamic field stop blinking
    before typing (legacy shortSleep), it is not an action-completion wait.
    """
    locator.wait_for(state="visible", timeout=UI_TIMEOUT)
    locator.click()
    page.wait_for_timeout(300)
    page.keyboard.type(value, delay=40)


def create_client_via_ui(page: Page, first_name: str, last_name: str, email: str) -> None:
    """Create a client through the new-CRM "+ New -> New client" dialog (legacy
    NewClients.createClient)."""
    open_clients_list(page)
    _open_new_client_menu(page)

    outer = _outer(page)
    dialog = outer.locator(DIALOG_ROOT)
    dialog.locator(DIALOG_FIRST).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    _fill_text(dialog.locator(DIALOG_FIRST).first, first_name)
    _fill_text(dialog.locator(DIALOG_LAST).first, last_name)
    _type_dynamic_email(page, dialog.locator(DIALOG_EMAIL).first, email)
    save = dialog.locator(f"xpath={DIALOG_SAVE}").first
    save.wait_for(state="visible", timeout=UI_TIMEOUT)
    save.click()
    # Dialog closes once the create request commits; wait for it to detach so a
    # follow-up navigation does not abort the in-flight create.
    dialog.locator(DIALOG_FIRST).first.wait_for(state="detached", timeout=UI_TIMEOUT)


def select_and_delete_client(page: Page, client_name: str) -> None:
    """Select a single client in the CRM and bulk-delete it (legacy selectClient +
    bulkActionDelete)."""
    open_clients_list(page)
    select_client(page, client_name)
    bulk_delete(page)


def go_to_dashboard_from_menu(page: Page) -> None:
    """Click the left-menu Dashboard item and wait for the dashboard (legacy
    Layout.goToDashboardFromMenu). Navigating away lets the system notifications
    refresh, per the legacy comment."""
    menu_item = page.locator(DASHBOARD_MENU).first
    menu_item.wait_for(state="visible", timeout=UI_TIMEOUT)
    menu_item.click()
    page.wait_for_url("**/app/dashboard**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")


def assert_quota_notification(page: Page) -> None:
    """Assert the clients-quota-exceeded system notification is shown (POV top-level).

    The notification is produced asynchronously after the account hits the cap, so
    re-navigate to the dashboard a bounded number of times until it appears (each
    wait capped at the 5s UI policy)."""
    notification = page.locator(QUOTA_NOTIFICATION).first
    for attempt in range(NOTIFICATION_ATTEMPTS):
        try:
            expect(notification).to_be_visible(timeout=UI_TIMEOUT)
            return
        except (PlaywrightTimeoutError, AssertionError):
            if attempt == NOTIFICATION_ATTEMPTS - 1:
                raise
            go_to_dashboard_from_menu(page)


def assert_upgrade_dialog_on_new_client(page: Page) -> None:
    """At the cap, opening "+ New -> New client" shows the upsell dialog instead of
    the form (legacy getUpgradeDialogOnClientCreation)."""
    open_clients_list(page)
    _open_new_client_menu(page)
    _assert_and_close_upgrade(page)


def assert_upgrade_dialog_on_import(page: Page) -> None:
    """At the cap, opening "More actions -> Import" shows the upsell dialog
    (legacy getUpgradeDialogOnClientImport)."""
    open_clients_list(page)
    _open_import_menu(page)
    _assert_and_close_upgrade(page)


def _assert_and_close_upgrade(page: Page) -> None:
    expect(page.locator(UPGRADE_ROOT).first).to_be_visible(timeout=UI_TIMEOUT)
    _dismiss_upsell(page)
    expect(page.locator(UPGRADE_ROOT).first).to_be_hidden(timeout=UI_TIMEOUT)


def _dismiss_upsell(page: Page) -> None:
    close = page.locator(UPGRADE_CLOSE).first
    if close.count() and close.is_visible():
        close.click()
        return
    page.keyboard.press("Escape")


def _open_new_client_form_below_cap(page, also_visible=None):
    """Open the new-client FORM once the freed-quota state has propagated.

    Right after a delete the account can still read as at-cap, so "+ New -> New
    client" shows the upsell. Retry, dismissing the upsell and refreshing quota via a
    dashboard round-trip, until the form appears. Returns the dialog locator.

    ``also_visible`` (e.g. the quota banner) is an extra locator that must also be
    visible before returning. It is polled with ``is_visible()`` inside the same loop
    so a momentarily re-attaching Angular iframe (the clients list reloads right after
    the dashboard round-trip) just triggers another poll instead of a hard
    "waiting for frame" failure on a follow-up assertion."""
    outer = _outer(page)
    dialog = outer.locator(DIALOG_ROOT)
    form_field = dialog.locator(DIALOG_FIRST).first
    upsell = page.locator(UPGRADE_ROOT).first
    for attempt in range(QUOTA_FREE_ATTEMPTS):
        open_clients_list(page)
        _open_new_client_menu(page)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if form_field.is_visible() and (also_visible is None or also_visible.is_visible()):
                return dialog
            if upsell.count() and upsell.is_visible():
                break
            page.wait_for_timeout(200)
        _dismiss_upsell(page)
        if attempt < QUOTA_FREE_ATTEMPTS - 1:
            go_to_dashboard_from_menu(page)
    raise AssertionError("New-client form/banner did not become available after freeing quota")


def assert_new_client_dialog_banner(page: Page) -> None:
    """Below the cap, opening the new-client dialog shows the quota banner
    (legacy getNewClientDialogBanner). Closes the dialog afterwards."""
    outer = _outer(page)
    banner = outer.locator(DIALOG_BANNER).first
    dialog = _open_new_client_form_below_cap(page, also_visible=banner)
    expect(banner).to_be_visible(timeout=UI_TIMEOUT)
    cancel = dialog.locator(f"xpath={DIALOG_CANCEL}").first
    cancel.wait_for(state="visible", timeout=UI_TIMEOUT)
    cancel.click()


def assert_import_wizard_opens(page: Page) -> None:
    """Below the cap, opening import shows the import wizard (legacy getImportWizard).

    Quota frees asynchronously, so retry (refreshing via dashboard) until the wizard
    appears instead of the upsell."""
    outer = _outer(page)
    wizard = outer.locator(IMPORT_WIZARD).first
    upsell = page.locator(UPGRADE_ROOT).first
    for attempt in range(QUOTA_FREE_ATTEMPTS):
        open_clients_list(page)
        _open_import_menu(page)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if wizard.count() and wizard.is_visible():
                return
            if upsell.count() and upsell.is_visible():
                break
            page.wait_for_timeout(200)
        _dismiss_upsell(page)
        if attempt < QUOTA_FREE_ATTEMPTS - 1:
            go_to_dashboard_from_menu(page)
    raise AssertionError("Import wizard did not open after freeing quota")
