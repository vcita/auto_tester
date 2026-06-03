# Business Creates Estimate

## Objective
Create estimates and verify the search results, the back-office estimate page, and
the client-portal estimate page (migrated from automation-js Estimates scenario
"Business creates estimate").

## Prerequisites
- User logged in (Sales category _setup).
- Shared service ($100), product ($10) and tax (13%) created via API in _setup.

## Steps
1. Set account tax mode to `exclude`; create a client.
2. Create estimate `bestimate` for the client with existing items `service` + `product2`,
   billing address `susa, persia`, reorder the two items, and send it.
3. Search estimates by client name -> result list is exactly the first estimate.
4. Open the back-office estimate page -> price `$110.00`, state `SENT`, client name,
   total `$110.00`, items `product2` ($10) then `service` ($100) (reordered order).
5. Create a second estimate `bestimate` with custom items `desired_item1` ($50, tax 13%,
   not saved) + `desired_item2` ($20, saved), billing `susa, persia`, and send it.
6. Search estimates by client name -> [second estimate, first estimate] (newest first).
7. Open the back-office second estimate -> price/total `$76.50` (tax excluded), items
   `desired_item1` ($50) + `desired_item2` ($20).
8. Open the client portal as the client and view the first (pending) estimate ->
   price `$110.00`, client name, items `product2` + `service`, pending action (Approve).

## Expected Result
- Search, back-office and client-portal views all show the expected estimate data.

## Context Updates
- `created_estimate_one_title`, `created_estimate_two_title`
