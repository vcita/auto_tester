# BO follow-up tip on a paid invoice (charge)

Migrated from automation-js/features/salsa/tips.feature
Scenario: "create invoice and add follow up tip - BO - charge"

Prerequisites are API-seeded in `_setup` (tips app + 10/20/30 BO tips, a paid
`invoice #0000001` with a `product_item200` $20 line, BO login + mock gateway connected).

## Actions and assertions

1. Open the paid invoice page.
2. Click **Add a tip**, choose **charge** (fill the mock card), select the `10%` tip,
   and confirm.
3. **Assert** the back-office payment page (Payments Received) shows:
   - client_name: `first last`
   - name: `Tip for invoice #0000001`
   - amount: `$2.00`
   - type: `Credit Card (Online)`
   - items: `product_item200`
   - tip: `$2.00`
