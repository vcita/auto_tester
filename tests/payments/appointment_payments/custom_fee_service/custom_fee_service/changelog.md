# Changelog: Paying for custom fee service appointment

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 7 "paying for custom fee service appointment".
- Records a POS payment for a "display for a fee" (price varies) appointment:
  price $90, 13% tax (TStax), 10% percentage discount, then asserts
  "Payment for Sale #1 - service" in Payments Received.
- New helper `pay_custom_fee_via_pos` mirrors PaymentStatusCard.payForPriceVaries
  + Pos.applyPriceForActivity (price-value, tax-picker-tf, discount-value,
  vc-footer save) then the shared POS record-sale flow.
- Service name uses a fixed "service" (isolated account) instead of the legacy
  "service+[seq]"; the sale payment title is "Payment for Sale #1 - service".
