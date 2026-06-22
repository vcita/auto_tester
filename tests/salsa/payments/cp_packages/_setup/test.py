"""Setup for the cp_packages subcategory (isolated account).

Mirrors the Background of automation-js features/salsa/cp/packages.feature: log in to the
isolated account, connect the mock payment gateway (UI), and create via API the 3 services
(r2p_appointment require-to-pay, s2p_appointment suggest-to-pay, r2p_event event
require-to-pay), the 2 packages (package1 offering all 3 / 1 credit / $150; package2
offering s2p_appointment / 2 credits / $150) and 1 client. All prerequisites are account-
level and shared by both tests; the client portal token is reused across both tests.

Payment-type mapping (legacy api/service.js _setPaymentType): "require to pay" -> paid_force,
"suggest to pay" -> paid. Location mapping (_setLocationType): f2f_other -> business_location,
business_phone -> business_phone.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (
    create_package_via_api,
    create_service_via_api,
)
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_cp_packages(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Connect mock payment gateway (UI)")
    connect_mock_gateway(page, context)

    print("  Setup Step 3: Create 3 services via API (r2p_appointment, s2p_appointment, r2p_event)")
    r2p_appointment = create_service_via_api(
        context, "r2p_appointment",
        charge_type="paid_force", price="1",
        service_type="appointment", interaction_type="business_location",
        meeting_interaction_details="tlv12",
    )
    s2p_appointment = create_service_via_api(
        context, "s2p_appointment",
        charge_type="paid", price="1",
        service_type="appointment", interaction_type="business_phone",
        meeting_interaction_details="1 202 222 2222",
    )
    r2p_event = create_service_via_api(
        context, "r2p_event",
        charge_type="paid_force", price="1",
        service_type="event", interaction_type="business_location",
        meeting_interaction_details="",
    )
    services = {
        "r2p_appointment": r2p_appointment,
        "s2p_appointment": s2p_appointment,
        "r2p_event": r2p_event,
    }
    context["cp_packages_services"] = services

    print("  Setup Step 4: Create 2 packages via API (package1 all-3/1cr/$150, package2 s2p/2cr/$150)")
    package1 = create_package_via_api(
        context, "package1",
        services=[r2p_appointment, s2p_appointment, r2p_event],
        total_bookings=1, price=150, expiration="2", expiration_unit="w",
    )
    package2 = create_package_via_api(
        context, "package2",
        services=[s2p_appointment],
        total_bookings=2, price=150, expiration="6", expiration_unit="m",
    )
    context["cp_packages_packages"] = {"package1": package1, "package2": package2}

    # Each test creates its OWN client (legacy Background runs per scenario): test 1
    # purchases packages for its client and test 2 assigns packages to a different client,
    # so a shared client would accumulate both tests' packages and break the assertions.
    print(
        f"  [OK] cp_packages setup complete - mock gateway + {len(services)} services "
        f"+ 2 packages ready (client created per test)"
    )
