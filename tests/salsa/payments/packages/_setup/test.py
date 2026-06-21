# Auto-generated from script.md
# Source: tests/salsa/payments/packages/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Setup for the packages (back-office) subcategory (isolated account).

Mirrors the Background of automation-js features/salsa/packages.feature: log in to the
isolated account, connect the mock payment gateway (UI; required by the BO take-payment /
POS / invoice flows), and create via API the 3 services the packages are built from
(`service`, `service2` suggest-to-pay $100 appointments; `r2p_event` require-to-pay $1 event).

Clients are created per test (legacy Background runs per scenario) so each test owns a fresh
client and a clean client-package list; taxes / products / feature-flag changes are created
per test that needs them.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_service_via_api
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_packages(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Connect mock payment gateway (UI)")
    connect_mock_gateway(page, context)

    print("  Setup Step 3: Create 3 services via API (service, service2, r2p_event)")
    service = create_service_via_api(
        context, "service",
        charge_type="paid", price="100",
        service_type="appointment", interaction_type="business_location",
        meeting_interaction_details="blablablabla",
    )
    service2 = create_service_via_api(
        context, "service2",
        charge_type="paid", price="100",
        service_type="appointment", interaction_type="business_location",
        meeting_interaction_details="blablablabla",
    )
    r2p_event = create_service_via_api(
        context, "r2p_event",
        charge_type="paid_force", price="1",
        service_type="event", interaction_type="business_location",
        meeting_interaction_details="",
    )
    context["packages_services"] = {
        "service": service,
        "service2": service2,
        "r2p_event": r2p_event,
    }
    print("  [OK] packages setup complete - mock gateway + 3 services ready")
