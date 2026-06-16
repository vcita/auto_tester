# Changelog: Payment confirmation emails via POS

## 2026-06-11 - Initial migration (VCITA2-14027)

- Migrated from `automation-js/features/salsa/payments-emails.feature` scenario 4
  "payments confirmation emails via Point of Sale".
- point_of_sale enabled (default); require-to-pay $100 service + API appointment +
  a $10 product assigned to the client. No gateway connected (offline Cash records,
  matching the legacy scenario).
- Records the appointment's request via POS, then records all the client's open
  requests via POS; each ensures the send-receipt checkbox is checked so the client
  gets a "Payment Confirmation" email. Verified by exact-subject email count of 2.
- Client selected by the seeded full name "first last" (the account's only client)
  instead of the legacy "client last" search text - deterministic, identical
  asserted behavior.
- Email delivery is async; verified via `email_api.wait_for_email_count` (bounded
  poll, documented exception to the 5s cap). UI waits stay <=5s.

## 2026-06-11 - POS checkout stabilization

- Step 1 records the appointment's require-to-pay request through its Billing &
  Invoicing order (`_open_appt_via_orders`), not an ad-hoc appointment sale, so the
  request is genuinely fulfilled and the only request left open for Step 2 is the
  assigned product.
- Step 2's "add all open requests" can asynchronously re-offer the already-paid
  appointment line a moment after the product. A sale containing that stale paid
  line never finishes computing its checkout total, so the take-payment dialog never
  opens. Fix: detect the stall (dialog absent within a fast wait) and drop the stale
  line, then retry. The remove button is revealed by hover and clicked with
  `click(force=True)` (a JS `el.click()` did not reliably trigger the Vue handler).
- Bounded retry: only one stale line is ever re-added, so the detect-drop-retry loop
  is capped at <=2 retries (`range(2)` + a final attempt) — within the wait-audit cap.
- POS activator/record menu use synthetic JS clicks to bypass a transient Angular
  Material backdrop left by the prior record (per the project Vue/Angular click
  guidance).
