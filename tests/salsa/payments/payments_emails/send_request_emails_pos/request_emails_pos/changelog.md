# Changelog: Send payment request emails via POS

## 2026-06-11 - Initial migration (VCITA2-14027)

- Migrated from `automation-js/features/salsa/payments-emails.feature` scenario 2
  "Send payment request emails to client via Point of Sale".
- point_of_sale enabled (default); require-to-pay $100 service + API appointment +
  mock gateway.
- POS checkout send-link for api1, then a second appointment (api2 on "service2")
  is scheduled + invoiced, then the invoice payment-request link is sent by email.
  Verified by email count: 2x "New payment request from ", 1x "New invoice from "
  (prefix match for the dynamic business-name suffix).
- api2 uses its own require-to-pay service so the Orders-routed invoice targets it
  unambiguously (workflow-only difference vs the legacy shared service; identical
  asserted behavior, no scope loss).
- Email delivery is async; verified via `email_api.wait_for_email_count` (bounded
  poll, documented exception to the 5s cap). UI waits stay <=5s.
