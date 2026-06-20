# Check assigned package's credits when redeeming for appointments (and refunding)

## Objective
Verify that a client's package credit quota decreases when an appointment redeems a credit
and is restored when the redemption is cancelled or the appointment is cancelled with refund.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create a fresh client via API.
2. Create a package `package` via the UI: specific service, offering `service`, 2 credits,
   price 150. (Legacy uses "all services / any service"; on the current build the one-click
   redeem action is exposed only for a specific-type package, so the package is specific and both
   meetings use `service` — the 2-credit quota coverage is identical.)
3. Assign `package` to the client via the client card.
4. Schedule appointment `meeting1` (service) as a DUE appointment via the scheduling API
   (out-of-scope prerequisite: a BO-calendar-scheduled appointment cannot be redeemed on this
   build — its card exposes only `link-to-package`, never `redeem_package`).
5. Redeem `meeting1` with the package — consumes a package credit.
6. Verify the client's package credit quota is 1.
7. Cancel the package redemption for `meeting1`.
8. Verify the client's package credit quota is 2.
9. Schedule appointment `meeting2` (service) as a DUE appointment via the scheduling API.
10. Redeem `meeting2` with the package (consumes a credit).
11. Cancel `meeting2` (the appointment) with refund.
12. Verify the client's package credit quota is 2.

## Expected Result
- Quota goes 2 → 1 on redemption, back to 2 on redemption-cancel, and back to 2 after the
  redeemed appointment is cancelled with refund.

## Notes
- The appointment payment-status card behaviour (DUE/PAID/redeemed caption) is already covered
  by `appointment_payments/packaged_service`; this test asserts the distinct **client-card
  credit quota** number, using the redemption/refund actions only as the means to change it.
- Legacy redeems at schedule time via the create-meeting dialog's auto-redeem checkbox. On the
  current build that checkbox produces an UNLINKED appointment (credit unconsumed), so the
  in-scope redemption is exercised via the explicit "Redeem package" action on the DUE
  appointment card (the proven packaged_service mechanism).
