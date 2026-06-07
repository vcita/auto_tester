# Script: External receipt - back office

- Alias `context["deposit_client_name"] = receipt_client_name` and reuse
  `deposits_invoice_ui.record_custom_payment(page, context, "some_item", "5")` — Quick
  Actions → Record payment → Custom Item → Cash → confirm (data-qa selectors, ≤5s waits).
- `gateway_setups_ui.open_payment(page, client_name, "Payment for some_item")` →
  `open_payment_by_name` (Payments Received, `input[name="name_filter"]`, payment-title link).
- `assert_payment_page(client_name, "Payment for some_item")` → `div.summary-header h3`
  (title) + `span.contact-name, div .display-name-component span` (client).
- `assert_external_receipt(page)` → `[data-qa='view_receipt']`, capture the new tab via
  `page.context.expect_page` (15s budget for the external redirect), assert URL contains
  `this-is-a-receipt-for-pdf-`.
