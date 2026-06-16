"""Open non-editable role page (VCITA2-14059, scenario 1).

Migrates automation-js roles-and-permissions.feature "Open non-editable role
page": the built-in Administrator role opens in view mode (no Save button).
"""

from playwright.sync_api import Page

from tests.spotlights.settings.roles_permissions.roles_helpers import (
    is_save_button_present,
    open_role,
    open_roles_page,
)

ROLE_NAME = "Administrator"


def test_view_role_page(page: Page, context: dict) -> None:
    open_roles_page(page)
    open_role(page, ROLE_NAME)
    print(f"  Opened built-in role {ROLE_NAME!r}")

    assert not is_save_button_present(page), (
        f"{ROLE_NAME} role page should open in view mode (no Save button), "
        "but a Save button was present"
    )
    print("  [OK] Administrator role page opened in view mode (no Save button)")
