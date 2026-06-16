"""Setup for the wizard populated-profession scenario.

Enable the onboarding-wizard flags, set business_category 'legal_services' (the source of
the prepopulated profession), and log in.
"""

from playwright.sync_api import Page

from tests.salsa.payments.gateway_setups.gateway_setups_account import prepare_wizard_account


def setup_profession_populated(page: Page, context: dict) -> None:
    prepare_wizard_account(page, context, business_category="legal_services")
