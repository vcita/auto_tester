# Client Declines Estimate In CP

## Objective
A client opens a pending estimate in the client portal, declines it, and the
back-office estimate page reflects the rejection (migrated from automation-js
CP Estimates scenario "Client declines estimate").

## Prerequisites
- User logged in (Sales category _setup).

## Steps
1. Create a client (via API).
2. Create a pending estimate `rejectEstimate` for that client (via API) with a single
   line item `product2` ($10, "description for payable item2").
3. Open the client portal as the client and open the pending estimate ->
   it shows price `$10.00`, the client name, the item `product2`, and pending
   actions (Approve / Reject available).
4. Decline the estimate (confirm the decline dialog).
5. The client-portal estimate page now shows the estimate as declined
   ("Declined on ...").
6. Open the back-office estimate page -> state `REJECTED`, price `$10.00`, client
   name, total `$10.00`, item `product2` ($10).

## Expected Result
- The client portal shows the estimate as declined and the back-office shows it as REJECTED.
