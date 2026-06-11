"""Setup for the wizard funnel-v1 upgrade scenario.

Enable the onboarding-wizard flags plus the payment funnel-v1 flags
(vp_payment_conversion_one, payment_gateways_disabled), set business_category
'legal_services' (matches the legacy row), and log in.
"""

from playwright.sync_api import Page

from tests.salsa.payments.gateway_setups.gateway_setups_account import prepare_wizard_account


def setup_funnel_upgrade(page: Page, context: dict) -> None:
    prepare_wizard_account(page, context, business_category="legal_services", funnel_v1=True)
