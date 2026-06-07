# Take payment with tips via Point of Sale

Migrated from tips.feature scenario "edit tips options & take payment with tips via
Point of Sale". POS is reached from Quick Actions -> Take payment.

## Action 1 - Sale from open requests + tip
- Quick Actions -> Take payment (POS), select client `first last`.
- Add all open payment requests (the unpaid service + package).
- Checkout -> Record payment, method `ACH`, tip `55%`, confirm.
- **Assert** Payments Received payment page:
  - client_name `first last`, name `Payment for Sale #1 - package (+1 item)`,
    amount `$387.50`, type `ACH`, items `package,service` (sorted), tip `$137.50`.

## Action 2 - Custom-item sale + custom tip
- Quick Actions -> Take payment (POS), select client `first last`.
- Add a custom item `some_item` priced `5`.
- Checkout -> Record payment, method `ACH`, tip `Custom` `4.5`, confirm.
- **Assert** payment page: name `Payment for Sale #2 - some_item`, tip `$4.50`.
