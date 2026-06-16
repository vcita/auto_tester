"""Staff role management (VCITA2-14059, scenario 3).

Migrates automation-js roles-and-permissions.feature "Staff Role page": open a
role=User staff's Edit staff permissions page, verify the staff name + current
role (User), change the role to Manager, and verify the staff list reflects it.
"""

from playwright.sync_api import Page

from tests.spotlights.settings.roles_permissions.roles_helpers import (
    assert_staff_role_in_list,
    change_staff_role,
    open_staff_permissions,
    selected_role_name,
    staff_name_on_role_page,
)

INITIAL_ROLE = "User"
NEW_ROLE = "Manager"


def test_staff_role(page: Page, context: dict) -> None:
    staff = context["roles_permissions"]["user_staff"]
    staff_name = staff["name"]
    print(f"  Managing role for staff {staff_name!r} ({staff['email']})")

    open_staff_permissions(page, staff_name)
    assert staff_name_on_role_page(page) == staff_name, (
        f"role page should show staff name {staff_name!r}, "
        f"got {staff_name_on_role_page(page)!r}"
    )
    assert selected_role_name(page) == INITIAL_ROLE, (
        f"staff role should be {INITIAL_ROLE!r}, got {selected_role_name(page)!r}"
    )
    print(f"  [OK] Staff role page shows name {staff_name!r} and role {INITIAL_ROLE!r}")

    change_staff_role(page, NEW_ROLE)
    print(f"  Changed staff role to {NEW_ROLE!r}")

    assert_staff_role_in_list(page, staff_name, NEW_ROLE)
    print(f"  [OK] Staff {staff_name!r} role changed to {NEW_ROLE!r} in the staff list")
