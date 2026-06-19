"""Teardown for the notification_center subcategory (VCITA2-14247).

Best-effort cleanup of API-created artifacts (notification templates + the app). The whole
isolated account is also deleted by the runner on a passing run, so this only bounds
leftovers. Mirrors the legacy best-effort delete_notification_metadata / delete_app, which
the legacy run itself tolerates a 401 on.
"""

from playwright.sync_api import Page

from tests.tango.notifications.notification_center import notifications_helpers as nc


def teardown_notification_center(page: Page, context: dict) -> None:
    for code, token in context.get("nc_templates", []):
        nc.delete_notification_template(context, token, code)
    for code in context.get("nc_apps", []):
        nc.delete_app(context, code)
    print("  [teardown] Notification templates and apps cleaned up (best-effort)")
