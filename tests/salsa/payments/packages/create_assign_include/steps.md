# Create and assign package, check payment request (tax INCLUDE mode)

## Objective
With the account tax mode set to "include", create a taxed package via the UI and assign it
to a client, then verify the client-package payment request shows the tax-inclusive total
(tax folded into the price, so the displayed amount equals the package price).

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create two taxes via API: `TS` (13%) and `TS 2` (13.13%).
2. Set the account tax mode to `include` via API.
3. Create a fresh client via API.
4. Create a package `package` in Settings/Packages via the UI:
   - service `service`, 2 credits, price 150, tax `TS` (13%).
5. Assign `package` to the client via the client card (taxes `TS` and `TS 2`).
6. Verify the client-package payment request:
   - state `DUE`, amount `$150.00`, client `first last`, package `package`.

## Expected Result
- Client-package request is DUE for $150.00 (tax included in the price, not added on top).
