"""Upgrade a Trial account to Platinum Single via the upgrade page (VCITA2-14028, S1).

Migrates automation-js upgrade_page.feature scenario 1. The Trial account is
provisioned + logged in by _setup; this test runs the upgrade-page UI flow and
asserts both the success-page package and the business plan (API read-back).
"""

from playwright.sync_api import Page

from tests.account_api import wait_for_business_plan
from tests.settings.upgrade_page.upgrade_helpers import upgrade_to_plan

PLAN = "enterprise_single"
FIRST_NAME = "Automation"
LAST_NAME = "upgrade page"
EXPECTED_PACKAGE = "vcita Platinum Single (Annual)"
EXPECTED_BUSINESS_PLAN = "Platinum Single"


def test_upgrade_in_frontage(page: Page, context: dict) -> None:
    base_url = context.get("base_url")
    package = upgrade_to_plan(page, PLAN, FIRST_NAME, LAST_NAME, base_url)
    assert package == EXPECTED_PACKAGE, (
        f"success-page package expected {EXPECTED_PACKAGE!r}, got {package!r}"
    )
    print(f"  [OK] success page package = {package!r}")

    plan = wait_for_business_plan(context, EXPECTED_BUSINESS_PLAN)
    print(f"  [OK] business plan = {plan!r}")
