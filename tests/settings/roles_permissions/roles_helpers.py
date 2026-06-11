"""Shared UI helpers for the roles_permissions tests.

The Roles & Permissions page renders at the top-level POV page context (legacy
`switchToPageContext`), so its locators resolve directly on `page`. The staff
list (scenario 3) is the Angular page rendered inside the Frontage iframe
(`iframe[title="angularjs"]`); the "Edit staff permissions" kebab action there
navigates the top-level app to the POV role page.

Selectors are sourced from the legacy page objects
(automation-js/pages/desktop/Frontage/Settings/rolesAndPermissions.js and
.../Frontage/staffs.js) and verified live against POV during runner runs.
"""

from playwright.sync_api import Page

UI_TIMEOUT = 5_000
PAGE_TIMEOUT = 5_000

ROLE_ROW = lambda name: f'[data-role="{name}"]'  # noqa: E731
ROLE_HEADER = ".role-page__header"
SAVE_BUTTON = '[data-qa="save-btn"]'
ROLE_PICKER = ".role-picker"
ROLE_SELECTION_TEXT = ".role-picker .selection-text"

FRONTAGE_FRAME = 'iframe[title="angularjs"]'
STAFF_LIST_CONTAINER = ".cards-list-container"


def app_base(page: Page) -> str:
    return page.url.split("/app/")[0]


def open_roles_page(page: Page) -> None:
    page.goto(
        f"{app_base(page)}/app/settings/roles_and_permissions",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )


def open_role(page: Page, role_name: str) -> None:
    row = page.locator(ROLE_ROW(role_name)).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.click()
    page.locator(ROLE_HEADER).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def is_save_button_present(page: Page) -> bool:
    """Edit-mode signal: the role page renders a Save button only when editable."""
    return page.locator(SAVE_BUTTON).count() > 0


def open_staff_permissions(page: Page, staff_name: str) -> None:
    """Open a staff's Edit staff permissions (role) page via the Angular staff-list kebab.

    Mirrors legacy Staffs().goto() + goToStaffPermissions(name).
    """
    page.goto(
        f"{app_base(page)}/app/settings/staff",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )
    frame = page.frame_locator(FRONTAGE_FRAME)
    frame.locator(STAFF_LIST_CONTAINER).first.wait_for(state="visible", timeout=UI_TIMEOUT)

    row = frame.locator(
        f"xpath=//div[contains(text(), '{staff_name}')]"
        f"/ancestor::div[contains(@class, 'list-item')]"
    ).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.hover(timeout=UI_TIMEOUT)
    row.locator("button[aria-haspopup='true']").first.click(timeout=UI_TIMEOUT)
    frame.get_by_role("menuitem", name="Edit staff permissions").click(timeout=UI_TIMEOUT)

    page.locator(ROLE_HEADER).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def staff_name_on_role_page(page: Page) -> str:
    header = page.locator(ROLE_HEADER).first
    header.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (header.get_attribute("data-staff-name") or "").strip()


def selected_role_name(page: Page) -> str:
    return (page.locator(ROLE_SELECTION_TEXT).first.inner_text() or "").strip()


def change_staff_role(page: Page, new_role: str) -> None:
    page.locator(ROLE_PICKER).first.click()
    option = page.get_by_role("option", name=new_role, exact=True).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()
    page.locator(SAVE_BUTTON).first.click()
    # The picker selection text changes the moment the option is picked (before the
    # save round-trip), so it is NOT a valid "persisted" signal. onSave persists the
    # role then redirects to the staff list — waiting for that navigation is the
    # reliable signal that the change was saved before we re-read the staff list.
    page.wait_for_url("**/settings/staff*", timeout=UI_TIMEOUT)


def assert_staff_role_in_list(page: Page, staff_name: str, role_name: str) -> None:
    page.goto(
        f"{app_base(page)}/app/settings/staff",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )
    frame = page.frame_locator(FRONTAGE_FRAME)
    frame.locator(STAFF_LIST_CONTAINER).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    row = frame.locator(
        f"xpath=//dnd-nodrag[contains(., '{staff_name}') and contains(., '{role_name}')]"
    ).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
