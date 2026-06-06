# Script: Schedule appointment with packaged service

Playwright-oriented HOW for `packaged_service`.

## Preconditions (from _setup)

- Isolated account, logged in.
- Client "first last", "display a fee" $100 service "service".
- Two API-scheduled appointments: meeting1, meeting2.
- 2-credit $150 package offering "service", assigned to the client.

## Actions and assertions

1. `mark_appt_completed(page, context, identifier="meeting1")` then
   `assert_appt_payment_request(..., {state: DUE, amount: $100.00},
   identifier="meeting1")`.
2. `mark_appt_completed(page, context, identifier="meeting2")`,
   `redeem_appt_with_package(page, context, identifier="meeting2")`, then
   `assert_appt_payment_request(..., {state: PAID, amount: $0.00,
   redeemed_with_package: true, package_name: package}, identifier="meeting2")`.
3. `cancel_package_redemption(page, context, identifier="meeting2")` then
   `assert_appt_payment_request(..., {state: DUE, amount: $100.00,
   package_credit_refunded: true, package_name: package}, identifier="meeting2")`.

## Deviation (documented)

The legacy scenario schedules both appointments through the QuickActions UI to
pick the redeem-with-package option at scheduling time. Here the appointments
are API-seeded and redemption is driven by the appointment-page redeem-package
button (the same package-redemption UI exercised by the event redeem scenario).
The UI scheduling dialog is an out-of-scope prerequisite; all three payment-
request states (DUE $100, PAID $0 redeemed, DUE $100 refunded) are preserved.
