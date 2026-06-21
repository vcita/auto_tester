"""Teardown for the customized_notifications subcategory (VCITA2-14248).

Best-effort cleanup of the API-created v3 notification templates. The whole isolated account
is also deleted by the runner on a passing run, so this only bounds leftovers. Mirrors the
legacy best-effort `Deleting created notification metadata`.
"""

from playwright.sync_api import Page

from tests.tango.notifications.notification_center import notifications_helpers as nc


def teardown_customized_notifications(page: Page, context: dict) -> None:
    for uid, token in context.get("nc_templates_v3", []):
        nc.delete_notification_template_v3(context, token, uid)
    print("  [teardown] v3 notification templates cleaned up (best-effort)")
