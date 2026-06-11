# Changelog: Pay for an invoiced product

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 5 "user pays for an invoiced product".
- Background (client + $10 product) and the product assignment are API-seeded.
- Creates an invoice from the product order (POV-routed via Billing & Invoicing,
  matching the legacy goToOrder -> createInvoice flow), pays it in full, and
  asserts the product payment request becomes PAID $10.00 with the invoice
  payment in Payments Received.
- The legacy `type | invoice` column is documentation only (legacy
  parseProductOrderParams ignores it); PAID state + amount are asserted instead.

## 2026-06-06 - Fix account-creation 403 + missing pay helper
- Account creation failed with HTTP 403 `{"business_name":["contains invalid
  term"]}`. Root cause: the isolated account business name is derived from
  `account_profile.slug`, and the directory content filter bans "invoice".
  Renamed the slug `prodpay_invoice` -> `prodpay_billed` (folder/scenario
  semantics unchanged). This was previously misdiagnosed as an env rate limit.
- `test.py` imported a non-existent `pay_for_invoice`; re-exported the
  entity-agnostic `pay_for_invoice` from `event_payments_helpers` (same flow as
  the invoiced-event scenario). Scenario now passes 2/2.
