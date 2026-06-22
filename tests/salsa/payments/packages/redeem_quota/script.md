# Package credit quota on redeem / refund — Detailed Script

## Actions
1. Create a fresh client via API (`make_client(..., unique_name=True)`) — a per-test unique name
   keeps the shared account's client list unambiguous; this test does not assert the client name.
2. Create package `package` via UI (`create_package`, `package_type="specific"`, offering
   `service`, 2cr, $150). Legacy uses "all services / any service", but on the current build the
   one-click `[data-qa='redeem_package']` action is exposed ONLY for a specific-type package (an
   any/all-services package's appointment exposes only `[data-qa='link-to-package']`, no redeem —
   verified live). So the package is specific and both meetings use `service`; the 2-credit quota
   coverage (2 -> 1 -> 2 -> 2) is identical to the legacy.
3. Assign `package` to the client via the client card (`assign_package_via_client_card`).
4. Schedule appointment `meeting1` (service) as a DUE appointment via the scheduling API
   (`schedule_appointment_via_api`). A BO-calendar-scheduled appointment cannot be redeemed on
   this build (its payment-status card exposes only `link-to-package`, never `redeem_package`, and
   the dialog's auto-redeem checkbox leaves the appointment unlinked / bookings_usage 0 — verified
   live). The scheduling API (the same path the proven appointment_payments/packaged_service flow
   uses) produces a DUE appointment whose card exposes the working `redeem_package` action, so UI
   scheduling is treated as an out-of-scope prerequisite (as packaged_service documents).
5. Redeem `meeting1` with the package (`redeem_appt_with_package_by_id`, clicks
   `[data-qa='redeem_package']`) — consumes a credit, request -> PAID (quota 2 -> 1).
6. Assert client credit quota == 1 (`assert_credit_quota`, client-card
   `.package-value-balance-number`).
7. Cancel the package redemption for `meeting1` (`cancel_package_redemption_by_id`).
8. Assert client credit quota == 2.
9. Schedule appointment `meeting2` (service) as a DUE appointment via the scheduling API.
10. Redeem `meeting2` with the package (`redeem_appt_with_package_by_id`) -> quota 1.
11. Cancel `meeting2` (the appointment) with refund (`cancel_appointment_by_id` refund=True) —
    restores the credit.
12. Assert client credit quota == 2.

## Scope note
The appointment payment-status card behaviour (DUE/PAID/redeemed caption/credit-refund caption)
is already covered by `appointment_payments/packaged_service`; this test asserts the distinct
**client-card credit quota** (2 -> 1 -> 2 -> 2), using the schedule/redeem/cancel actions only as
the means to change the quota. No DUE/PAID card assertions are duplicated here.

## Success Verification
- Quota goes 2 -> 1 on redemption, back to 2 on redemption-cancel, and stays 2 after the
  redeemed appointment is cancelled with refund.
