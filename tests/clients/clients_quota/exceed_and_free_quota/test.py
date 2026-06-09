"""Exceed and free up the account clients quota (VCITA2-14005).

Migrated from automation-js/features/steps/clients-quota.feature.
Setup seeded 10 clients via API on an 11-client-capped isolated account; this test
reaches the cap via the UI, asserts the quota notification + upsell dialogs, frees a
slot by deleting a client, and asserts the quota banner + import wizard below the cap.
"""

from playwright.sync_api import Page

from tests.clients.clients_quota.clients_quota_helpers import (
    assert_import_wizard_opens,
    assert_new_client_dialog_banner,
    assert_quota_notification,
    assert_upgrade_dialog_on_import,
    assert_upgrade_dialog_on_new_client,
    create_client_via_ui,
    go_to_dashboard_from_menu,
    select_and_delete_client,
)


def test_exceed_and_free_quota(page: Page, context: dict) -> None:
    data = context["clients_quota"]
    seq = data["seq"]

    create_client_via_ui(page, "first11", "last11", f"test11+{seq}@vmeetme.com")
    print("  [OK] Created 11th client via UI (account at cap 11/11)")

    go_to_dashboard_from_menu(page)
    assert_quota_notification(page)
    print("  [OK] Clients-quota system notification appears")

    assert_upgrade_dialog_on_new_client(page)
    print("  [OK] Upgrade dialog blocks new-client creation at the cap")

    assert_upgrade_dialog_on_import(page)
    print("  [OK] Upgrade dialog blocks client import at the cap")

    select_and_delete_client(page, "first10 last10")
    print("  [OK] Freed a slot by bulk-deleting 'first10 last10' (account at 10/11)")

    go_to_dashboard_from_menu(page)

    assert_new_client_dialog_banner(page)
    print("  [OK] New-client dialog quota banner appears below the cap")

    assert_import_wizard_opens(page)
    print("  [OK] Import wizard opens below the cap")
