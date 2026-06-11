# Changelog: Paying for an invoiced event

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 4 "Paying for and invoiced event".
- Isolated subcategory `invoiced_event`.
- Adds `invoice_event` (create invoice from the event payment request via the
  `#vue_wizard_iframe` itemizable wizard, frame-scanned), `pay_for_invoice` (reuses
  the take-payment record flow), and `assert_invoice_page`; verifies the payment in
  Payments Received.
