# Auto-generated from script.md
# Source: tests/salsa/payments/packages/redeem_quota/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
"""Package credit quota on redeem / refund (2 -> 1 -> 2 -> 2).

Migrates automation-js features/salsa/packages.feature scenario
"Check assigned package's credits when redeeming for appointments (and refunding)".

The in-scope behaviour — redeem a package credit, cancel the redemption, and cancel an
appointment with refund — is driven through the UI, reusing the PROVEN
appointment_payments/packaged_service redemption flow (mark completed -> "Redeem with package"
-> cancel-redemption), which is the only redemption path that renders the redeem action on the
current build (a "display a fee" appointment covered by a specific package, redeemed after
completion). Appointment scheduling + client/service/package creation are out-of-scope
prerequisites done via API (the same path packaged_service uses). The distinct coverage here is
the CLIENT-CARD credit quota transition 2 -> 1 -> 2 -> 2 across two redemptions of one 2-credit
package, plus cancel-redemption and cancel-with-refund.
"""

import time

from playwright.sync_api import Page

from tests.salsa.payments.appointment_payments.appointment_payments_api import (
    schedule_appointment,
    seed_client,
    seed_package,
    seed_service,
)
from tests.salsa.payments.appointment_payments.appointment_payments_helpers import (
    cancel_package_redemption,
    mark_appt_completed,
    redeem_appt_with_package,
)
from tests.salsa.payments.packages.packages_helpers import (
    assert_credit_quota,
    cancel_appointment_by_id,
    get_client_package_id,
    track_for_cleanup,
)


def test_redeem_quota(page: Page, context: dict) -> None:
    from tests._functions.login.test import fn_login
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")
    fn_login(page, context, username=username, password=password)

    seq = str(int(time.time() * 1000))
    print("  Step 1: Seed client + 'display a fee' $100 service (API)")
    client = seed_client(context, first=f"first{seq}", last="last",
                         email=f"test+{seq}@vmeetme.com")
    client_id = client["id"]
    service = seed_service(context, name=f"redeem_svc_{seq}",
                           payment_setting="display a fee", price=100)

    print("  Step 2: Create 2-credit $150 package offering the service + assign to client (API)")
    seed_package(context, name="package", service=service, credits=2, price=150)
    track_for_cleanup(
        context, client_package_id=get_client_package_id(context, client_id, "package"))

    print("  Step 3: Schedule meeting1 earlier today (completable) as a prerequisite (API)")
    schedule_appointment(context, service=service, identifier="meeting1", lead_days=0)

    print("  Step 4: Complete meeting1, then redeem it with the package via the UI (credit used)")
    mark_appt_completed(page, context, identifier="meeting1")
    redeem_appt_with_package(page, context, identifier="meeting1")

    print("  Step 5: Assert client credit quota == 1")
    assert_credit_quota(page, context, client_id, 1)

    print("  Step 6: Cancel the package redemption for meeting1 via the UI (restores the credit)")
    cancel_package_redemption(page, context, identifier="meeting1")

    print("  Step 7: Assert client credit quota == 2")
    assert_credit_quota(page, context, client_id, 2)

    print("  Step 8: Schedule meeting2 earlier today (completable) as a prerequisite (API)")
    meeting2 = schedule_appointment(context, service=service, identifier="meeting2", lead_days=0)

    print("  Step 9: Complete meeting2, then redeem it with the package via the UI (-> quota 1)")
    mark_appt_completed(page, context, identifier="meeting2")
    redeem_appt_with_package(page, context, identifier="meeting2")

    print("  Step 10: Cancel meeting2 with refund via the UI (restores the credit)")
    cancel_appointment_by_id(page, context, meeting2["id"], refund=True)

    print("  Step 11: Assert client credit quota == 2")
    assert_credit_quota(page, context, client_id, 2)
