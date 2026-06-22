# Create, Edit and Remove CRM Filters

Migrated from `automation-js/features/steps/crm-filters-create-and-edit.feature`
scenario **User creates, edits and removes filters** (VCITA2-13790).

## Goal
Verify the CRM client list filters can be applied, edited, removed and cleared,
that the active-filter chips, filtered client list and counter update
correctly, and that a fixed-as-new view and a custom view can be saved.

## Preconditions (created via account API)
- 4 clients: `first1 last1` (no tag), `first2 last2` (tag4), `first3 last3`
  (tag4 + an open payment), `no-tag last4` (no tag).
- A product `payable_item1` (price 10) assigned to `first3` so that client has
  an open payment.

## Steps
1. Open the clients list.
2. Select the **Recently active** view → active filter is `Last activity time`.
3. Select the **All** tab → no active filters, counter shows `4 CLIENTS`.
4. Add **First Name** = `first` → clients: first1, first2, first3.
5. Add **Tags** = `tag4` → clients: first2, first3.
6. Edit the **First Name** filter to `first2` → clients: first2.
7. Remove the **First Name** filter → clients: first2, first3.
8. Add **Open payments**, save fixed as new view → clients: first3, counter `1 CLIENTS`.
9. Clear all filters, save the custom view → all 4 clients.

## Expected results
- The active-filter chips match the expected filters at each step.
- The filtered client list matches the expected clients at each step.
- The counter shows `4 CLIENTS` (All) and `1 CLIENTS` (Open payments).
