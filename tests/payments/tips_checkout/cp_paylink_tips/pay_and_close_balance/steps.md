# CP pay-link with percent tip and CP close-balance with custom tip

Migrated from automation-js/features/salsa/tips.feature
Scenario: "take payment with tips in cp via pay link"

Prerequisites are API-seeded in `_setup` (tips app + 55/66/77 CP tips, suggest-to-pay
`service` $100, client `first last` with a payable past appointment, BO login + mock
gateway connected).

## Actions and assertions

### Part A — new client pays a service via the public pay link (percent tip)
1. Open the public client-portal make-payment form for `service` with amount `100`.
2. As a new client `steve`, fill identity (first name + email), submit, then in the Vue
   checkout dialog pick the `55%` tip and pay via the mock payment gateway popup.
3. **Assert** the back-office payment page (Payments Received) shows:
   - client_name: `steve`
   - name: `Payment for Sale #1 - service`
   - amount: `$155.00`
   - items: `service`
   - tip: `$55.00`

### Part B — existing client closes their CP balance (custom tip)
4. As client `first last`, open the client portal payments list, go to the unpaid tab,
   start checkout for the outstanding `service` balance, add a `5` custom tip, and pay
   via the mock payment gateway popup.
5. **Assert** the back-office payment page (Payments Received) shows:
   - client_name: `first last`
   - name: `Payment for Sale #2 - service`
   - amount: `$105.00`
   - items: `service`
   - tip: `$5.00`
