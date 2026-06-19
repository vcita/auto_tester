"""Setup for the notification_center subcategory (VCITA2-14247).

Mirrors the shared `Given user logged in to automatic account` prerequisite of every legacy
notification_center.feature scenario: log in to the isolated account via the UI. Each test
creates its own notification template via API with the token kind its scenario uses.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_notification_center(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    context["nc"] = {"seq": int(time.time())}
    print("  [OK] Logged in; notification_center context ready")
