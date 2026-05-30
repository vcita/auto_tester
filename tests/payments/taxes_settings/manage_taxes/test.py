"""Manage taxes: create, edit, delete, and toggle tax mode.

Migrates automation-js features/salsa/payments-settings/taxes-settings.feature
(scenario: Create, update & delete taxes).
"""

from playwright.sync_api import Page

from tests.payments.taxes_settings.taxes_helpers import (
    add_tax,
    assert_tax_mode,
    assert_taxes,
    delete_tax,
    edit_tax,
    open_taxes_settings,
    save_changes,
    set_tax_mode,
)

TAX_ONE = ("taylor swift 1", "13")
TAX_TWO = ("taylor swift 2", "13.13131")
TAX_ONE_EDITED = ("taylor swift 13", "13.14")


def _row_qa(name: str, rate: str) -> str:
    return f"line-tax-{name}-{rate}"


def test_manage_taxes(page: Page, context: dict) -> None:
    print("  Step 1: Open Taxes settings...")
    scope = open_taxes_settings(page)

    print("  Step 2: Create two taxes...")
    add_tax(scope, *TAX_ONE)
    add_tax(scope, *TAX_TWO)
    save_changes(page)

    print("  Step 3: Verify both taxes are listed...")
    assert_taxes(page, [_row_qa(*TAX_ONE), _row_qa(*TAX_TWO)])

    print("  Step 4: Edit the first tax...")
    edit_tax(open_taxes_settings(page), *TAX_ONE, *TAX_ONE_EDITED)
    save_changes(page)

    print("  Step 5: Verify the edited tax is listed...")
    assert_taxes(page, [_row_qa(*TAX_ONE_EDITED), _row_qa(*TAX_TWO)])

    print("  Step 6: Delete the edited tax...")
    delete_tax(open_taxes_settings(page), *TAX_ONE_EDITED)
    save_changes(page)

    print("  Step 7: Verify only the second tax remains...")
    assert_taxes(page, [_row_qa(*TAX_TWO)])

    print("  Step 8: Change tax mode to include...")
    set_tax_mode(page, open_taxes_settings(page), "include")

    print("  Step 9: Verify tax mode is include...")
    assert_tax_mode(page, "include")

    context["taxes_remaining"] = [_row_qa(*TAX_TWO)]
    context["tax_mode"] = "include"
    print("  [OK] Taxes create/edit/delete and tax-mode change verified")
