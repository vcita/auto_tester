"""Setup for the customized_notifications subcategory (VCITA2-14248).

Mirrors the shared `Given user logged in to automatic account via API` prerequisite of every
legacy customized-email-notification.feature scenario: log in to the isolated account via the
UI. Each test creates its own customized v3 notification template via API (directory token).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_customized_notifications(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    context["nc"] = {"seq": int(time.time())}
    print("  [OK] Logged in; customized_notifications context ready")
