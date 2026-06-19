"""Notification Center pane + badge flow (VCITA2-14247).

Migrated from automation-js/features/tango/notification_center.feature — Scenario 1
("Create notification template + notification flow").

An app-created `messages` notification template (channel pane, deep link app/clients) is
delivered to staff; the test drives the in-app notification pane and badge end to end:
empty state, badge counter, read/unread toggles, show-only-unread, mark-all-as-read, the
deep-link redirect, and per-staff isolation via "Log in as" impersonation.
"""

from playwright.sync_api import Page

from tests.account_api import create_platform_staff_via_api, first_staff_uid
from tests.tango.notifications.notification_center import notifications_helpers as nc


def test_notification_flow(page: Page, context: dict) -> None:
    seq = context["nc"]["seq"]
    app_code = f"automationjs{seq % 100000}"  # app_code_name
    app_name = f"AutoJS {seq % 100000}"  # name must be 3..25 chars
    ncode = f"auto_notification{seq % 100000}"
    display_name = f"Automation Notification {seq % 100000}"

    # ----- API preconditions: app + token + assign + notification template -----
    app = nc.create_app(context, app_code, app_name)
    app_token = nc.app_service_token(context, app)
    nc.assign_app_to_account(context, app_code)
    nc.create_notification_template(
        context,
        app_token,
        code=ncode,
        notification_type="messages",
        channel={"pane": True},
        deep_link="app/clients",
        text={
            "en": {
                "title": "Check this out!",
                "body": "Hi ${first_name} ${last_name}! A new message is available",
                "display_name": display_name,
                "description": "Notification Description",
            }
        },
    )
    # Resolve and cache the owner staff uid before any extra staff exists.
    owner_staff_uid = first_staff_uid(context)
    print(f"  [OK] App {app_code} + template {ncode} created; owner staff resolved")

    # Start from a known, fully-mounted dashboard (the setup login may leave the page on a
    # transitional view); the dashboard is the stable host for the pane operations.
    nc.goto_dashboard(page, context)

    # ----- 1. Empty state -----
    nc.open_pane(page)
    nc.assert_pane_empty(page)
    nc.close_pane(page)
    print("  [OK] Notification pane shows 'last 30 days' empty state")

    # ----- 2. New notification shows on badge -----
    nc.send_notification(
        context, app_token, ncode, owner_staff_uid,
        params={"first_name": "auto", "last_name": "notification"},
    )
    nc.assert_badge_counter(page, "1")
    print("  [OK] Badge counter is 1 after a new notification")

    # ----- 3. Pane displays notification; opening resets the badge -----
    nc.open_pane(page)
    nc.assert_notification_displayed(
        page,
        title="Check this out!",
        body="Hi auto notification! A new message is available",
        timestamp="Just now",
        status="unread",
    )
    nc.assert_no_badge_counter(page)
    nc.close_pane(page)
    print("  [OK] Notification displays unread; badge counter cleared on open")

    # ----- 4. Clicking the notification follows the deep link to the Clients page -----
    nc.open_pane(page)
    nc.click_notification(page)
    nc.assert_redirected_to_clients(page)
    print("  [OK] Clicking the notification redirected to the new Clients page")

    # Return to the dashboard for the remaining pane operations: the notification pane is a
    # global toolbar control, but it opens far more reliably on the light dashboard than on
    # the heavy CRM/Clients page (which intermittently lost the open-pane race under load).
    nc.goto_dashboard(page, context)

    # ----- 5. Notification is now read -----
    nc.open_pane(page)
    nc.assert_notification_status(page, "read")
    nc.close_pane(page)

    # ----- 6. Set unread / read via the blue dot -----
    nc.open_pane(page)
    nc.toggle_read_status(page)
    nc.assert_notification_status(page, "unread")
    nc.close_pane(page)
    nc.open_pane(page)
    nc.toggle_read_status(page)
    nc.assert_notification_status(page, "read")
    nc.close_pane(page)
    print("  [OK] Blue dot toggles the notification read/unread")

    # ----- 7. Three more notifications; pane shows 4 -----
    for params in (
        {"first_name": "Notification", "last_name": "1"},
        {"first_name": "Notification", "last_name": "2"},
        {"first_name": "Notification", "last_name": "3"},
    ):
        nc.send_notification(context, app_token, ncode, owner_staff_uid, params=params)
    nc.assert_badge_counter(page, "3")
    nc.open_pane(page)
    nc.assert_pane_count(page, 4)
    print("  [OK] Badge counter 3; pane shows 4 notifications")

    # ----- 8. Show-only-unread toggle + mark-all-as-read -----
    nc.toggle_only_unread(page)
    nc.assert_pane_count(page, 3)
    nc.toggle_only_unread(page)
    nc.assert_pane_count(page, 4)
    nc.mark_all_as_read(page)
    nc.toggle_only_unread(page)
    nc.assert_pane_read_all_empty(page)
    nc.close_pane(page)
    print("  [OK] Only-unread toggle + mark-all-as-read reach the 'all read' empty state")

    # ----- 9. Per-staff isolation via impersonation -----
    staff = create_platform_staff_via_api(
        context, name="Staff Admin", email=f"staff+a{seq}@vmeetme.com", role="admin"
    )
    nc.send_notification(
        context, app_token, ncode, owner_staff_uid,
        params={"first_name": "staff", "last_name": "notification"},
    )
    nc.assert_badge_counter(page, "1")
    nc.impersonate_staff(page, context, staff["name"])
    nc.assert_no_badge_counter(page)
    nc.open_pane(page)
    nc.assert_pane_empty(page)
    nc.close_pane(page)
    print("  [OK] Impersonated staff sees no notifications (per-staff isolation)")
