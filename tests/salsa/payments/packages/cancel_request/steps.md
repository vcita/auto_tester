# Cancel a package payment request

## Objective
Cancel (waive) a client-package payment request and verify it is marked CANCELLED.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create a fresh client via API.
2. Create a package `package` via API: specific service `r2p_event`, 2 credits, price 150.
3. Assign `package` to the client via API.
4. Cancel (waive) the client-package payment request via the UI.
5. Verify the client-package payment request: state `CANCELLED`, amount `$150.00`,
   client `first last`, package `package`.

## Expected Result
- The client-package request is CANCELLED for $150.00.
