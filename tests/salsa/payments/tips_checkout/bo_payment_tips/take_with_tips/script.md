# Script: take payment with tips (BO)

Playwright-oriented HOW for `take_with_tips`. Reuses `tips_checkout_bo`.

## Preconditions (from _setup)

- Isolated account, point_of_sale denied, tips enabled for BO, logged in.
- Client "first last", suggest-to-pay $100 service "service", specific package
  "package" ($150, assigned), past appointment scheduled via API.

## Actions and assertions

1. `close_client_balance(page, context, client_id, record_type="ACH",
   tip_option="55%", send_receipt=True)`
   - Open `/app/clients/{id}` -> client-card take payment -> close-balance dialog
     -> Record -> method ACH (`md-select[name='payment_method']`) -> tip 55%
     (`md-select[name='tip_option']`) -> send-receipt checkbox -> confirm.
2. `assert_payment_page_with_tip(..., {client_name: "first last", name: "Payment
   for Multi-item #0000001", amount: "$387.50", type: "ACH", items:
   "package,service", tip: "$137.50"})`.
3. `record_custom_payment_with_tip(page, context, client_name="first last",
   item_name="some_item", amount="5", tip_option="Custom", tip_amount="4.5")`.
4. `assert_payment_page_with_tip(..., {name: "Payment for some_item", tip:
   "$4.50", search: "first"})`.

## Selectors of note (legacy, no product data-qa - documented)

- Tip picker `md-select[name='tip_option']`; custom amount `input[name='tip_amount']`.
- Payment-page tip row `.tip-row .invoice-right-side`.
- Suggest adding `data-qa` to the tip picker and tip row in product code.
