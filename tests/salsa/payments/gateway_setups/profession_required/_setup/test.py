"""Setup for the wizard profession-required scenario.

Enable the onboarding-wizard flags WITHOUT a business_category (so the preliminary
profession starts empty and must be filled), and log in.
"""

from playwright.sync_api import Page

from tests.salsa.payments.gateway_setups.gateway_setups_account import prepare_wizard_account


def setup_profession_required(page: Page, context: dict) -> None:
    prepare_wizard_account(page, context, business_category=None)
