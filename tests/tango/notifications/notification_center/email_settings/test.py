"""Email channel in Notification Center settings (VCITA2-14247).

Migrated from automation-js/features/tango/notification_center.feature — Scenario 3
("Email in Notification Center Settings").

A core_internal_app `payments` template starts with the email channel hidden (not
configured); enabling the email channel makes the email toggle visible and on in settings.
"""

from playwright.sync_api import Page

from tests.tango.notifications.notification_center import notifications_helpers as nc


def test_email_settings(page: Page, context: dict) -> None:
    seq = context["nc"]["seq"]
    ncode = f"auto_nc_email_settings{seq % 100000}"
    display_name = f"Automation NC Email Settings {seq % 100000}"
    ci_token = nc.core_internal_app_token(context)

    # Ensure we run as the account owner (independent of prior tests in the subcategory).
    nc.ensure_owner_session(page, context)

    # ----- API precondition: core_internal_app template (pane+push, no email) -----
    nc.create_notification_template(
        context,
        ci_token,
        code=ncode,
        notification_type="payments",
        channel={"pane": True, "push": True},
        deep_link="app/reports",
        text={
            "en": {
                "title": "Check this out!",
                "body": "Hi! A new message is available",
                "display_name": display_name,
                "description": "Notification description",
            }
        },
    )

    # ----- 1. Shows in settings; email hidden by default -----
    nc.goto_settings(page, context)
    nc.assert_template_in_settings(
        page, ncode, display_name=display_name, description="Notification description"
    )
    nc.assert_channel_values(page, ncode, {"push": "true", "pane": "true", "email": "hidden"})
    print("  [OK] Template shows; push+pane on, email hidden")

    # ----- 2. Enable email -> email toggle visible and on -----
    nc.update_notification_template(context, ci_token, ncode, {"channel": {"email": True}})
    nc.goto_settings(page, context)  # "refresh" = re-navigate
    nc.assert_channel_values(page, ncode, {"push": "true", "pane": "true", "email": "true"})
    print("  [OK] Enabling email makes the email toggle visible and on")
