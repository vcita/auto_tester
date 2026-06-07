# Script: take payment with tips via POS

Helpers in `tips_checkout_pos.py` (reuse the tip/method/confirm primitives from
`tips_checkout_bo`) and `assert_payment_page_with_tip` from `tips_checkout_bo`.

## Action 1
- `take_open_requests_via_pos(page, context, client_name="first last", record_type="ACH", tip_option="55%")`:
  - `_open_quick_action(POS_QUICK_ACTION="[data-qa=VcLargeQuickAction-point_of_sale]")` + `_select_client`.
  - Add open requests: `.client-details-container [role="alert"] [type="button"]`.
  - `[data-qa=checkout-actions-activator]` -> `[data-qa=checkout-action-record]`.
  - In the Angular take-payment dialog: `md-select[name=payment_method]` -> ACH,
    `md-select[name=tip_option]` -> 55%, `[data-qa=take-payment-confirmation]`.
- `assert_payment_page_with_tip` reads the payment from Payments Received.

## Action 2
- `take_custom_item_via_pos(..., item_name="some_item", amount="5", record_type="ACH", tip_option="Custom", tip_amount="4.5")`:
  - POS for client -> `[data-qa=pos-add-custom-item]` -> `[data-qa=item-name]` +
    `[data-qa=custom-item-price]` -> `[data-qa=vc-footer-Add]`.
  - Checkout -> Record -> ACH -> Custom tip 4.5 -> confirm.

## Notes
- The POS take-payment dialog has no product `data-qa` for the tip picker; the stable
  legacy `md-select[name=tip_option]` / `input[name=tip_amount]` selectors are reused.
- point_of_sale must be enabled (setup leaves it on).
