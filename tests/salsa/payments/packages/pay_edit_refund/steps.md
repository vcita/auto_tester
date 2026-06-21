# Pay, edit, and refund an assigned (any-service) package

## Objective
With Point of Sale denied (so payments use the record-payment dialog), partially pay a
client-package request, edit the request amount, pay the remainder to PAID, and verify the
two payments are searchable.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Deny the `point_of_sale` feature flag via API.
2. Create a fresh client via API.
3. Create a package `bundle1` via the UI: any service (`service`, `r2p_event`), 5 credits,
   price 150, expires in 1 week.
4. Assign `bundle1` to the client via the client card.
5. Pay $10 toward the package request → verify state `DUE`, amount `$140.00 (out of $150.00)`.
6. Edit the package payment request amount to $50 → verify `DUE`, `$40.00 (out of $50.00)`.
7. Pay $40 → verify state `PAID`, amount `$50.00`.
8. Search Payments Received by first name `first` and verify two payments titled
   `Payment for bundle1 - Package purchased`.

## Expected Result
- Partial payments and the edited request amount are reflected on the card.
- Final state is PAID for $50.00 with two recorded payments.
