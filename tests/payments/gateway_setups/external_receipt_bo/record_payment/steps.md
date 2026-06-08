# External receipt - back office

Legacy scenario: "Create payment while using external receipt app".

1. Record a payment via Quick Actions → Record payment for `simon bolivar`: a custom item
   `some_item` for `$5`, paid by Cash.
2. The payment page displays client `simon bolivar` and title `Payment for some_item`.
3. The (first) payment has an external receipt — the View-receipt link opens the
   mockreceipts redirect (URL contains `this-is-a-receipt-for-pdf-`).
