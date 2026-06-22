# Changelog — invoice_followup_tip / charge_tip

## Migration (VCITA2-13899)
Migrated from `automation-js/features/salsa/tips.feature`, scenario
"create invoice and add follow up tip - BO - charge".

### Setup (API + minimal UI)
- `seed_invoice_followup_tip_account`: tips flags, `tips` app (Admin auth), tip options
  `10/20/30` enabled for BO (POST `/platform/v1/payment/settings` + read-back), client
  `first last`, an invoice (`invoice` → server title `invoice #0000001`) with a saved
  `product_item200` $20 line, and a recorded $20 Cash payment for the invoice so it is
  fully paid (the prerequisite for the invoice "Add a tip" follow-up action).
- UI: BO login + connect mock payment gateway (required for the charge tip).

### Test actions (UI under test)
- Open the paid invoice, click Add a tip, choose charge (mock card), select the `10%`
  tip, confirm; assert the BO payment page: `Tip for invoice #0000001`, `$2.00`,
  `Credit Card (Online)`, item `product_item200`, tip `$2.00`.

### Reused helpers
- `tips_checkout_bo.open_invoice_payment_page` + `add_followup_tip` (charge) +
  `assert_payment_page_with_tip`. `add_followup_tip` was hardened to open the
  `ps-more-actions` overflow when Add a tip is not directly visible, to open the charge
  section via the legacy `translate` button, and to confirm robustly (dialog-keyed).

### Selector considerations (data-qa gaps)
- Tip picker `md-select[name='tip_option']` and the add-tip charge opener
  (`button[translate="payment.take_payment.charge"]`) have no product data-qa; stable
  legacy selectors are reused and documented. The invoice number is taken from the
  create-invoice API response rather than hard-coded.
