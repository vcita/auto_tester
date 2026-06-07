# Script: External receipt - POS

- Alias `context["deposit_client_name"] = receipt_client_name` and reuse
  `deposits_pos_ui.record_pos_custom_payment(page, context, "some_item", "20")` — Quick
  Actions → Take payment (POS) → custom item → checkout → Record (Cash), data-qa selectors.
- `gateway_setups_ui.open_payment(page, client_name, "Payment for Sale #1 - some_item")`.
- `assert_payment_page(client_name, "Payment for Sale #1 - some_item")`.
- `assert_external_receipt(page)` → `[data-qa='view_receipt']` new-tab URL contains
  `this-is-a-receipt-for-pdf-`.
