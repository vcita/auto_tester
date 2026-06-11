# Changelog: Send payment request emails (non-POS)

## 2026-06-11 - Initial migration (VCITA2-14027)

- Migrated from `automation-js/features/salsa/payments-emails.feature` scenario 1
  "Send payment request emails to client" (@gate).
- Setup denies point_of_sale so take payment opens the legacy send-payment-link
  dialog; require-to-pay $100 service + API appointment + mock gateway.
- Service seeded as "require to pay" instead of the legacy "suggest to pay":
  invoicing is POV-routed via the Billing & Invoicing order row, which only exists
  for a DUE request (same established pattern as
  appointment_payments/invoiced_appointment). The three emails under test are
  identical for either charge type, so no email-scope is lost.
- Sends the appointment payment-request link by email, invoices the appointment,
  and sends the invoice payment-request link by email; each email is verified by
  the outbound-email count growing (2x "New payment request from ", 1x "New invoice
  from "), matched by prefix because the business-name suffix is the dynamic
  isolated-account name.
- Email delivery is async; `email_api.wait_for_email_count` polls on a bounded
  deadline (documented exception to the 5s UI cap). All UI waits stay <=5s.
