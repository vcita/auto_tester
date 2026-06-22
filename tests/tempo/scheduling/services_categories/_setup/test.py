"""Setup for the categories-and-services scenario (isolated account).

Mirrors the legacy categories-and-services.feature Background
(`user logged in to "services settings" page in automatic account via API`): a fresh
account is created by the runner, we log in and land on the Services settings page. The
fresh account ships the three default services the scenario asserts against
(`Demo class / event`, `In-office appointment`, `Introductory phone call`), so we verify
they are present up front to fail fast if the account template ever changes.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.tempo.scheduling.services_categories.services_categories_helpers import goto_services

DEFAULT_SERVICES = [
    "Demo class / event",
    "In-office appointment",
    "Introductory phone call",
]


def setup_services_categories(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Open Services settings page")
    ng = goto_services(page)

    print("  Setup Step 3: Verify the three default services are present")
    for name in DEFAULT_SERVICES:
        ng.get_by_text(name, exact=True).first.wait_for(state="visible", timeout=5_000)

    context["default_services"] = DEFAULT_SERVICES
    print("  [OK] setup complete - on Services page with default services")
