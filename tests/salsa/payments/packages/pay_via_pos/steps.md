# Pay for an assigned (any-service) package with POS

## Objective
Pay a client-package request through Point of Sale checkout and verify the request becomes
PAID for the full price and the POS sale is searchable in Payments Received.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create a fresh client via API.
2. Create a package `bundle1` via the UI: any service (`service`, `r2p_event`), 5 credits,
   price 150, expires in 1 week.
3. Assign `bundle1` to the client via the client card.
4. Pay the package's full balance ($150) via the BO Take-payment record path. On this build the
   client-package "Take payment" CTA opens the Take Payment dialog directly (no separate POS sale
   page exists for a client-package); with `point_of_sale` enabled, recording the full balance
   through that dialog books a POS Sale (yielding the "Sale #1" title asserted in step 6).
5. Verify the client-package payment request: state `PAID`, amount `$150.00`,
   client `first last`, package `bundle1`.
6. Search Payments Received by first name `first` and verify a payment titled
   `Payment for bundle1 - Package purchased`. PRODUCT CHANGE: the current build has no POS sale
   page for a client-package take-payment, so the standard package payment title is emitted
   instead of the legacy POS `Sale #N` title (verified live; see changelog).

## Expected Result
- Client-package request is PAID for $150.00 via a real BO take-payment action.
- The payment is listed in Payments Received.
