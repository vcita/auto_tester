# Source: tests/clients/crm_views/create_edit_views/script.md
# Migrated from automation-js/features/steps/crm-view-create-and-edit.feature (VCITA2-13951)

from playwright.sync_api import Page

from tests.clients.crm_views.crm_views_helpers import (
    assert_view_description,
    assert_view_not_available,
    assert_view_not_editable,
    assert_view_permission,
    close_tab,
    create_view,
    delete_view,
    edit_view,
    login_as_admin,
    select_view,
    switch_to_staff,
)


def test_create_edit_views(page: Page, context: dict) -> None:
    """Admin creates/edits/deletes CRM views and staff-level permission enforcement.

    Migrates automation-js `crm-view-create-and-edit.feature` scenario
    `Admin creates and edits views` (single, sequential scenario).
    """
    data = context["crm_views"]
    owner = data["owner"]
    staff_user = data["staff_user"]

    print("  Step 1: As admin, create 3 views (2 account-level, 1 staff-level)")
    create_view(page, "account view", "description1", "account")
    create_view(page, "account view 2", "description2", "account")
    create_view(page, "staff view", "description3", "staff")

    print("  Step 2: Verify descriptions and permission levels in the view menus")
    assert_view_description(page, "account view", "description1")
    assert_view_permission(page, "account view", "account")
    assert_view_permission(page, "staff view", "staff")

    print(f"  Step 3: Switch logged-in staff to '{staff_user['name']}' (SSO)")
    switch_to_staff(page, context, owner, staff_user)
    close_tab(page, "New inquiries")
    select_view(page, "account view")

    print("  Step 4: As staff, verify staff view hidden + account view read-only")
    assert_view_not_available(page, "staff view")
    assert_view_not_editable(page, "account view")

    print("  Step 5: Switch back to admin (SSO)")
    login_as_admin(page, context, owner)

    print("  Step 6: As admin, edit 'account view' -> 'now staff' (staff level)")
    edit_view(page, "account view", "now staff", "description1 new", "staff")
    assert_view_description(page, "now staff", "description1 new")
    assert_view_permission(page, "now staff", "staff")

    print("  Step 7: As admin, delete 'staff view'")
    delete_view(page, "staff view")
    assert_view_not_available(page, "staff view")

    print(f"  Step 8: Switch to '{staff_user['name']}' again and verify enforcement")
    switch_to_staff(page, context, owner, staff_user)
    assert_view_not_available(page, "now staff")
    assert_view_not_editable(page, "account view 2")

    print("  [OK] CRM view create/edit/delete + staff permission enforcement verified")
