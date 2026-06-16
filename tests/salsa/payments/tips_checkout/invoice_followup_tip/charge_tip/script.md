# Playwright HOW-TO — BO follow-up tip on a paid invoice (charge)

Reuses `tips_checkout_bo`:
- `open_invoice_payment_page(page, context, invoice_uid)` → `/app/invoices/<uid>`.
- `add_followup_tip(page, context, tip_option="10%", payment_type="charge")`:
  - Clicks Add a tip (`[data-qa="add_tip"]`, opening `[data-qa='ps-more-actions']` first
    if needed).
  - In the add-tip dialog (`md-dialog.add-tip-content`), opens the charge section
    (`button[translate="payment.take_payment.charge"]`), fills the mock gateway card
    (`#card` = 4242…), selects the `10%` tip in `md-select[name='tip_option']`, and confirms
    `[data-qa="take-payment-confirmation"]`.
- `assert_payment_page_with_tip(page, context, {...})` searches Payments Received by client
  name and verifies name/amount/type/items/tip on the payment detail.

## Selector notes (data-qa gaps)
- The tip picker is the Angular `md-select[name='tip_option']` (no data-qa); the charge
  section opener uses a `translate` attribute. Stable legacy selectors are reused and
  documented (suggest adding data-qa). `add_tip`/`ps-more-actions` expose data-qa.
- The invoice number `invoice #0000001` is read from the create-invoice API response
  (`store["invoice"]["title"]`) and used to build the expected payment title
  `Tip for <invoice title>`.
