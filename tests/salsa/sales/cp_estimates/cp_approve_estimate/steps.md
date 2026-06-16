# Client Approves Estimate In CP

## Objective
A client opens a pending estimate in the client portal, approves it, and the
back-office estimate page reflects the approval (migrated from automation-js
CP Estimates scenario "Client approves estimate").

## Prerequisites
- User logged in (Sales category _setup).

## Steps
1. Create a client (via API).
2. Create a pending estimate `approveEstimate` for that client (via API) with two
   line items: `service` ($100) and `product_item200` ($20, "short desc"),
   total `$120.00`.
3. Open the client portal as the client and open the pending estimate ->
   it shows price `$120.00`, the client name, both items, and pending actions
   (Approve / Reject available).
4. Approve the estimate (confirm the approve dialog).
5. The client-portal estimate page now shows the estimate as approved
   ("Approved on ...").
6. Open the back-office estimate page -> state `APPROVED`, price `$120.00`, client
   name, total `$120.00`, items `service` ($100) and `product_item200` ($20).

## Expected Result
- The client portal shows the estimate as approved and the back-office shows it as APPROVED.
