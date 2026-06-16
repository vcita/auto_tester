# Playwright HOW-TO — BO follow-up tip on a paid event attendance (record)

Reuses `tips_checkout_bo`:
- `open_paid_payment_detail(page, context, title="Payment for r2p_event", search="first")`
  opens the pre-paid $10 attendance payment from Payments Received (search by client name,
  click the row) — the transaction detail that exposes Add a tip (mirrors legacy
  PaymentPage.addTipFromCurrentPayment). The attendance is pre-paid via API, so its order
  is PAID and absent from the Billing & Invoicing OVERDUE/DUE default filter, and the
  platform payment id is not the `/app/transactions/{uid}` key — the Payments Received
  search/open path (same as the assertion) is the stable entry point.
- `add_followup_tip(page, context, tip_option="Custom", payment_type="record", tip_amount="5")`:
  - Clicks Add a tip (`[data-qa="add_tip"]`, opening `[data-qa='ps-more-actions']` first
    if needed).
  - In the add-tip dialog, opens the record section (`[data-qa="record_payment_button"]`),
    selects `Custom` in `md-select[name='tip_option']`, fills `input[name='tip_amount']`
    with `5`, and confirms `[data-qa="take-payment-confirmation"]` (Cash default).
- `assert_payment_page_with_tip(page, context, {...})` searches Payments Received by client
  name and verifies name/amount/type/items/tip.

## Selector notes (data-qa gaps)
- Tip picker `md-select[name='tip_option']` + custom amount `input[name='tip_amount']`
  have no product data-qa; stable legacy selectors are reused and documented.
- The scenario title says "from clients list", but the legacy implementation reaches the
  attendee payment-status detail (event → attendee → payment status); this migration
  reaches the equivalent detail via Billing & Invoicing Orders, which is more stable.
