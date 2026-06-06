# Script: Paying for custom fee service appointment

Playwright-oriented HOW for `custom_fee_service`. Mirrors
PaymentStatusCard.payForPriceVaries -> Pos.applyPriceForActivity +
performPaymentAction('record').

## Preconditions (from _setup)

- Isolated account, point_of_sale enabled, logged in.
- Client "first last", "display for a fee" (price varies) service "service",
  appointment scheduled via API, 13% tax "TStax".

## Actions and assertions

1. `pay_custom_fee_via_pos(page, context, amount="90",
   tax_label="TStax (13%)", discount_value="10", discount_type="percentage",
   identifier="service")`
   - Appointment page -> Take payment (opens POS price-varies item-edit panel).
   - Set price `[data-qa="price-value"]` = 90.
   - Tax picker `[data-qa="tax-picker-tf"]` -> option "TStax (13%)".
   - Discount `[data-qa="discount-value"]` = 10 (percentage default), save.
   - Checkout activator -> record-payment -> take-payment dialog -> Cash ->
     confirm; wait for the dialog to close.
2. `search_payments(page, context, "first",
   "Payment for Sale #1 - service", 1)`.
