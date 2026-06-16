# Changelog: Paying for invoiced appointment

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 5 "Paying for invoiced appointment".
- Invoices the appointment, pays the invoice $100, asserts the appointment
  payment request becomes PAID $100.00, and that Payments Received shows the
  invoice payment.
- Deviation (documented): legacy used a "display a fee" service and invoiced
  from a deep-linked appointment page. In auto_tester the appointment-page
  "Create invoice" button only mounts the POV invoice wizard
  (`/vue/#/itemizable`) when the appointment is reached via in-app SPA
  navigation; a `page.goto` deep-link loads the appointment app without the
  POV wizard host, so the click fires no request (confirmed via console/network
  capture: no invoice request, only unrelated conversation-panel 401/500). The
  fix navigates from Billing & Invoicing and clicks the appointment's order row
  (SPA nav). That order row exists only for a DUE request, so the service is
  seeded as "require to pay". The invoice->appointment-PAID behavior under test
  is unchanged.
