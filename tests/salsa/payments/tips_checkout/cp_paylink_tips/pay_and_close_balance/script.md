# Playwright HOW-TO — CP pay-link + CP close-balance tips

All UI lives in the Vue client portal inside `#cp_iframe`, served from the public
livesite (`CP_VITRAGE`). Payment is completed in an external mock-gateway popup. Both CP
sessions run in their own fresh browser context (no BO cookies), exactly like
`coupons_checkout_cp`. The back-office assertions reuse `tips_checkout_bo`.

## Part A — public make-payment form (new client + percent tip)
- Open `CP_VITRAGE/site/<pivot_uid>/make-payment?title=<service>&amount=100` in a fresh
  context (`tips_checkout_cp.open_payment_form`).
- Identity fields have no product data-qa; select by adjacent label
  (`xpath=//label[contains(.,"Email")]/../input`, same for First Name). Pay button:
  `[data-qa='payButton'], .checkout-btn`.
- In the checkout dialog (`.checkout-dialog`), tip segments are `button.checkout-tips__segment`
  (no data-qa — reused from legacy `clientPortalDialogs`). Click the `55%` segment, then
  `[data-qa="perform-payment-action"]` which opens the mock-gateway popup; submit it
  (`button[type=submit]`).

## Part B — CP payments list close-balance (existing client + custom tip)
- Open the authenticated portal with the client's portal token (`open_portal`).
- Payments menu `[data-qa='client-area-menu-payments']` → unpaid tab
  `[data-qa="tab-selector-pending"]` → checkout `.checkout-btn`.
- In the checkout dialog, open the custom-tip segment (last `.checkout-tips__segment`),
  fill `.v-text-field__slot input` with `5`, apply `button.action-dialog__apply-btn`,
  then perform payment + submit the mock popup.

## Back-office assertions
- `tips_checkout_bo.assert_payment_page_with_tip` searches Payments Received by client
  name and verifies name/amount/items/tip on the payment detail page.

## Selector notes (data-qa gaps)
- Checkout tip bar (`.checkout-tips__segment`, `.custom-tip-modal`) and the public form
  identity inputs have no product data-qa; stable legacy CSS / label-anchored XPath are
  used and documented. Suggest adding data-qa to the CP checkout tip controls.
