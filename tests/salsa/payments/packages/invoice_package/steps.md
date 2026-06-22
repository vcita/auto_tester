# Pay for an invoiced (single-service) package

## Objective
Create and assign a single-service package, raise an invoice for the package's purchase
order, pay that invoice, and verify the client-package payment request becomes PAID and the
payment is searchable in Payments Received.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create a fresh client via API.
2. Create a package `single1` via the UI: specific service `service`, 2 credits, price 150,
   expires in 1 week.
3. Assign `single1` to the client via the client card.
4. Create an invoice `single1_invoice` from the package's purchase order (billing address set).
5. Pay the invoice `single1_invoice #0000001` ($150).
6. Verify the client-package payment request: state `PAID`, amount `$150.00`,
   client `first last`, package `single1`.
7. Search Payments Received by first name `first` and verify a payment titled
   `Payment for single1_invoice #0000001` appears.

## Expected Result
- Client-package request is PAID for $150.00.
- The invoice payment is listed in Payments Received.
