# Create and assign package, check payment request (tax EXCLUDE mode)

## Objective
Create a taxed package in Settings/Packages via the UI, assign it to a client via the client
card, and verify the resulting client-package payment request shows the tax-exclusive total,
and that the client's portal conversation announces the added package.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create two taxes via API: `TS` (13%) and `TS 2` (13.13%).
2. Create a fresh client via API.
3. Create a package `package` in Settings/Packages via the UI:
   - service `service`, 2 credits, price 150, tax `TS` (13%).
4. Assign `package` to the client via the client card (taxes `TS` and `TS 2`).
5. Verify the client-package payment request:
   - state `DUE`, amount `$189.20 ($150.00 + Tax)`, client `first last`, package `package`.
6. Verify the client's client-portal conversation includes a message titled
   `Package added: package`.

## Expected Result
- Client-package request is DUE for $189.20 (150 + 13% + 13.13%), tax shown separately.
- The CP conversation shows "Package added: package".
