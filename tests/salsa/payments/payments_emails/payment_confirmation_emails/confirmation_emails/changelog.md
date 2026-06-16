# Changelog: Payment confirmation emails (non-POS)

## 2026-06-11 - Initial migration (VCITA2-14027)

- Migrated from `automation-js/features/salsa/payments-emails.feature` scenario 3
  "payments confirmation emails" (@gate).
- Setup denies point_of_sale; suggest-to-pay $100 service + API appointment + a $10
  product assigned to the client (gives an open balance to close).
- Records a $30 payment for the appointment, then closes the client's balance via
  record/ACH; each ensures the "Send receipt to client" checkbox is checked, so the
  client gets a "Payment Confirmation" email. Verified by exact-subject email count
  reaching 2.
- Email delivery is async; verified via `email_api.wait_for_email_count` (bounded
  poll, documented exception to the 5s cap). UI waits stay <=5s.
