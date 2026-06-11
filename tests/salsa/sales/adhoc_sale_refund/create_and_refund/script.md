# Script: create_and_refund

Helpers in `tests/sales/adhoc_sale_refund/adhoc_sale_helpers.py`. Mock gateway via
`tests/payments/tips_settings/tips_gateway.connect_mock_gateway`.

## Constants
- `PAY_FOR = "meeting"`, `AMOUNT = "20"`
- `SALE_NAME = "Sale #1 - meeting"`, `PAYMENT_NAME = "Payment for Sale #1 - meeting"`
- `AMOUNT_DISPLAY = "$20.00"`

## Flow
1. `connect_mock_gateway(page, context)` — back-office payment providers, connect mock (prerequisite UI).
2. `cp_page, cp_context = open_payment_form(page, context, pay_for="meeting", amount="20")`
   → `{CP_VITRAGE}/site/{pivot}/make-payment?title=meeting&amount=20` in a fresh browser context.
3. `pay_via_mock_gateway(cp_page, email=<setup email>, first_name="first")`
   → fill Email (`[data-qa="email-input"]`) / First Name (`get_by_label`) in `#cp_iframe`,
   click the CHECKOUT button (`get_by_role("button", name=/checkout/i)`), then checkout
   `[data-qa="perform-payment-action"]` opens the mock popup, submit `button[type=submit]`.
4. `assert_payment_success(cp_page, title="Payment confirmed", subtitle="confirmation email", amount="Amount received: $20.00")`
   → `[data-qa='payment-success-page']`, `span.briliant` / `span.thanks` / `span.paymet-text`. Close `cp_context`.
5. `assert_order_in_status(page, context, "Paid", SALE_NAME)` → `/app/payments/orders`, status filter PAID, row `f-ellipsis-tooltip.payment-title`.
6. `assert_payment_in_search(page, context, "first", PAYMENT_NAME)` → `/app/payments/transactions`, `name_filter`, row title.
7. `assert_sale_page(page, context, sale_name=SALE_NAME, client_full_name="first last", state="PAID", amount="$20.00")`
   → open order, read nested sale iframe (`span.main-title/price/status-text/data-part`).
8. `refund_payment(page, "first", PAYMENT_NAME)` → open payment (Payments Received), refund action
   (`[data-qa="refund"]` / `[data-qa="ps-more-actions"]`), confirm full refund (`[data-qa="vc-footer-Refund"]`).
9. `assert_order_in_status(page, context, "Cancelled", SALE_NAME)` then
   `assert_sale_state(page, context, sale_name=SALE_NAME, state="CANCELLED")`.

## Selectors / fallbacks
- CP form fields: Email via `[data-qa="email-input"]`, First Name via `get_by_label("First Name")`
  → fallback legacy `//label[contains(.,"…")]/../input`. Submit via the CHECKOUT role button
  (rendered `data-qa="vc-btn"` is not unique, so match by accessible name).
- Orders status filter has no data-qa: reuse legacy `[name="status_filter"]` + `[value="paid"|"cancelled"]`.
  These should get `data-qa` in product code.
- Sale detail has no data-qa: reuse legacy `span.main-title/price/status-text/data-part`, read across `page.frames`
  (deeply nested `vue_iframe_main`).

## Waits
- Element/dialog/state waits ≤ 5s (`FAST_UI_TIMEOUT`/`STATE_TIMEOUT`).
- `NAV_TIMEOUT` (20s) only for portal/app navigation readiness; `POPUP_TIMEOUT` (20s) only for the
  external mock-gateway popup. Orders/payments reload retries ≤ 2 (indexing lag).
