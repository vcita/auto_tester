# CRM Mobile List

## Objective
On a mobile viewport, close the CRM mobile welcome modal, then verify the CRM client
list behaves correctly with 10 API-seeded clients: the filtered-clients counter, a
search in the "All" tab, and the empty "New inquiries" tab.

Migrated from `automation-js/features/steps/crm-mobile.feature` (`@mobile_web`,
scenario "CRM mobile list"). Only the active legacy steps are in scope; the
commented-out legacy steps (products, open-payments tab, tags filter, scroll-load,
client-card redirect) are disabled in legacy and out of scope.

## Prerequisites
- Isolated account with 10 clients seeded via API (handled in `_setup`):
  first1 last1 .. first10 last10 (row 4 first name "no-tag").
- Owner logged in.

## Steps
1. Emulate a mobile device so the CRM mobile layout mounts.
2. Open the CRM clients list.
3. Close the CRM mobile welcome modal.
4. Select the "New inquiries" CRM tab, then the "All" tab.
   (Switching tabs gives the search indexer time to index the new clients.)
5. Verify the filtered clients counter shows "10 CLIENTS".
6. Search "first7" via the search bar in the "All" tab and verify the result row is
   "first7 last7".
7. Verify the filtered clients counter shows "1 CLIENTS".
8. Select the "New inquiries" CRM tab.
9. Verify the CRM table shows its empty state.
10. Verify the filtered clients counter shows "0 CLIENTS".

## Expected Result
- The welcome modal is dismissed.
- Counter reads "10 CLIENTS" in the All tab with all seeded clients.
- Searching "first7" yields exactly the "first7 last7" row and counter "1 CLIENTS".
- The "New inquiries" tab shows the empty state and counter "0 CLIENTS".
