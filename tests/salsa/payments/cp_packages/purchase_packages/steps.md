# Test: purchase_packages

## Objective
A client purchases packages via the business purchase links: package2 with a new card and
package1 with the saved card, verifying the purchased-packages page after each.
Migrates the first scenario of automation-js features/salsa/cp/packages.feature.

## Preconditions
Setup created the mock gateway, 3 services, 2 packages and 1 client (with portal token).

## Steps
1. The client accesses the purchase-packages link. → The CP packages page opens.
2. Select package2 from the package list. → The package description page opens (title package2).
3. Purchase the selected package with a NEW card (mock gateway). → Payment success.
4. The purchased-packages page shows: package2 | 0/2, s2p_appointment | active | any.
5. The client accesses the single package1 purchase link. → The package description page opens (title package1).
6. Purchase the selected package with the SAVED card (no gateway popup; card from step 3 is reused).
7. The purchased-packages page shows:
   - package1 | 0/1, r2p_appointment s2p_appointment r2p_event | active | any
   - package2 | 0/2, s2p_appointment | active | any

## Assertions
- CP packages list page and package description page (with correct title) are reached.
- Payment-success page is reached after each purchase.
- Purchased-packages rows match expected name / credits (used/total + services) / state.
