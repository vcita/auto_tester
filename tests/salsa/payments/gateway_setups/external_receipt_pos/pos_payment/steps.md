# External receipt - POS

Legacy scenario: "Create payment while using external receipt app - with pos".

1. Create custom items and record a payment for `simon bolivar` from the Point of Sale:
   a custom item `some_item` priced `$20` (saved), recorded by Cash.
2. The payment page displays client `simon bolivar` and title `Payment for Sale #1 - some_item`.
3. The (first) payment has an external receipt — the View-receipt link opens the
   mockreceipts redirect (URL contains `this-is-a-receipt-for-pdf-`).
