"""Upgrade a long-country-name Trial account to Platinum Single (VCITA2-14028, S2).

Migrates automation-js upgrade_page.feature scenario 2. The Trial account is created
with country "Bolivia, Plurinational State of" + logged in by _setup; this test runs
the upgrade-page UI flow and asserts the success-page package, proving the long
country name does not break the upgrade.
"""

from playwright.sync_api import Page

from tests.settings.upgrade_page.upgrade_helpers import upgrade_to_plan

PLAN = "enterprise_single"
FIRST_NAME = "Automation"
LAST_NAME = "long country"
EXPECTED_PACKAGE = "vcita Platinum Single (Annual)"


def test_upgrade_long_country(page: Page, context: dict) -> None:
    base_url = context.get("base_url")
    package = upgrade_to_plan(page, PLAN, FIRST_NAME, LAST_NAME, base_url)
    assert package == EXPECTED_PACKAGE, (
        f"success-page package expected {EXPECTED_PACKAGE!r}, got {package!r}"
    )
    print(f"  [OK] success page package = {package!r}")
