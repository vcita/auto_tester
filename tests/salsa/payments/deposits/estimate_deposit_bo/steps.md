# Estimate with a deposit request, approve and take payment (back office)

Migrated from `automation-js/features/salsa/deposits.feature` scenario 3
("Business creates an estimate with a deposit request, approve & pay").

## Objective
Create and send an estimate with a fixed deposit request, verify it is SENT with the
deposit DUE, then approve and take payment and verify it is APPROVED with the deposit PAID.

## Preconditions (from _setup)
- Logged in to the isolated account.
- Client "Torry Deposi" created via API.

## Steps
1. Create and send an estimate for Torry Deposi titled `bestimate`, billing address
   `susa, persia`, with a custom item `desired_item1` priced `50` and a `10` fixed
   deposit request.
2. Verify the back-office estimate shows **SENT** with deposit **DUE $10.00**.
3. Approve the estimate and take payment (record the deposit as Cash).
4. Verify the back-office estimate shows **APPROVED** with deposit **PAID $10.00**.
