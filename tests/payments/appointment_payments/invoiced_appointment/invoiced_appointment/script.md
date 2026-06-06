# Script: Paying for invoiced appointment

Playwright-oriented HOW for `invoiced_appointment`. Reuses appointment + event
payment helpers (the invoice wizard / invoice order flow is entity-agnostic).

## Preconditions (from _setup)

- Isolated account, logged in.
- Client "first last", "require to pay" $100 service "service", appointment
  scheduled via API.

## Actions and assertions

1. `invoice_appointment(page, context, "appointment_invoice", "blablablabla",
   identifier="service")`
   - Billing & Invoicing -> click the appointment's order row (SPA nav into the
     appointment page) -> Create invoice -> wizard: title + billing -> send.
   - SPA navigation is required: the appointment-page Create invoice button only
     mounts the POV invoice wizard when entered via in-app routing; a deep-link
     `goto` leaves the wizard host unmounted and the click is a silent no-op.
     The order row is present only for a DUE (require-to-pay) request, hence the
     require-to-pay service. The invoice->PAID behavior is identical.
2. `pay_for_invoice(page, context, "appointment_invoice #0000001", "100")`
   - Open the invoice order -> record $100 Cash.
3. `assert_appt_payment_request(..., {state: "PAID", amount: "$100.00", ...})`.
4. `search_payments(page, context, "first", "Payment for appointment_invoice
   #0000001", 1)`.
