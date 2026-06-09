# Delete Matter From A Contact With Other Matters Remaining - Steps

## Objective
Verify that deleting a matter from a contact that has other matters remaining leaves the
contact discoverable in the CRM (via its remaining matter), and that deleting the contact's
last matter removes it from the CRM entirely.

## Prerequisites (from _setup)
- Logged in to the isolated account.
- A contact `contact last` exists (created via API) with one default matter `contact last`.
- `context["contact_id"]`, `context["contact_name"]`, `context["contact_email"]` are set.

## Steps
1. Add a matter named `matter` under the contact from the contact pane.
2. Delete the `matter` matter via the matter-detail More menu (Delete client -> confirm).
3. Apply the CRM `Email` filter with the contact email; the filtered list shows only
   `contact last` (the remaining default matter).
4. Delete the last remaining matter `contact last` the same way.
5. Re-apply the CRM `Email` filter with the contact email; the filtered list is empty.

## Expected Result
- After step 3: filtered clients == [`contact last`].
- After step 5: filtered clients == [] (no clients).

## Notes
- "Matter" is vcita's general entity (Property/Patient/etc. by vertical).
- CRM index lags API/UI state, so list assertions poll and reload.
