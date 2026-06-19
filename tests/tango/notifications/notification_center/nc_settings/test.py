"""Notification Center settings (VCITA2-14247).

Migrated from automation-js/features/tango/notification_center.feature — Scenario 2
("Notification Center Settings").

A directory-created `payments` template drives the Notification Center settings page:
show_in_settings visibility, push/pane channel visibility, opening notification settings,
pane delivery, and unchecking the pane channel to suppress delivery.
"""

from playwright.sync_api import Page

from tests.account_api import first_staff_uid
from tests.tango.notifications.notification_center import notifications_helpers as nc


def test_nc_settings(page: Page, context: dict) -> None:
    seq = context["nc"]["seq"]
    ncode = f"auto_nc_settings{seq % 100000}"
    display_name = f"Automation NC Settings {seq % 100000}"
    dir_token = nc.directory_token(context)
    staff_uid = first_staff_uid(context)

    # Ensure we run as the account owner (a prior test may have impersonated another staff).
    nc.ensure_owner_session(page, context)

    # ----- API precondition: directory template, hidden from settings -----
    nc.create_notification_template(
        context,
        dir_token,
        code=ncode,
        notification_type="payments",
        channel={"pane": True, "push": True},
        deep_link="app/clients",
        show_in_settings=False,
        text={
            "en": {
                "title": "Check this out!",
                "body": "Hi! A new message is available",
                "display_name": display_name,
                "description": "Notification description",
            }
        },
    )

    # ----- 1. Hidden when show_in_settings=false -----
    nc.goto_settings(page, context)
    nc.assert_template_not_in_settings(page, ncode)
    print("  [OK] Template not shown in settings (show_in_settings=false)")

    # ----- 2. Visible when show_in_settings=true; push+pane on -----
    nc.update_notification_template(context, dir_token, ncode, {"show_in_settings": True})
    nc.goto_settings(page, context)  # "refresh" = re-navigate
    nc.assert_template_in_settings(
        page, ncode, display_name=display_name, description="Notification description"
    )
    nc.assert_channel_values(page, ncode, {"push": "true", "pane": "true"})
    print("  [OK] Template shows with display name/description; push+pane on")

    # ----- 3. Remove push channel -> push hidden, pane on -----
    nc.update_notification_template(context, dir_token, ncode, {"channel": {"push": False}})
    nc.goto_settings(page, context)
    nc.assert_channel_values(page, ncode, {"push": "hidden", "pane": "true"})
    print("  [OK] Push channel removed -> push hidden, pane on")

    # ----- 4. Open notification settings from the pane -----
    nc.open_notification_settings(page)
    print("  [OK] Notification settings page displayed from the pane")

    # ----- 5. Directory sends notification -> badge + pane delivery -----
    nc.send_notification(context, dir_token, ncode, staff_uid)
    # Read the badge from a normal POV page: the live push is reliable on the dashboard but
    # stale on the heavy settings-iframe page we were just on.
    nc.goto_dashboard(page, context)
    nc.assert_badge_counter(page, "1")
    nc.open_pane(page)
    nc.assert_notification_displayed(
        page,
        title="Check this out!",
        body="Hi! A new message is available",
        timestamp="Just now",
        status="unread",
    )
    nc.close_pane(page)
    print("  [OK] Notification delivered to the pane")

    # ----- 6. Uncheck pane -> delivery suppressed -----
    nc.goto_settings(page, context)
    nc.set_channel_checkbox(page, ncode, "pane", checked=False)
    nc.send_notification(context, dir_token, ncode, staff_uid)
    nc.goto_dashboard(page, context)
    nc.assert_no_badge_counter(page)
    print("  [OK] Unchecking pane suppresses pane delivery (no badge)")
