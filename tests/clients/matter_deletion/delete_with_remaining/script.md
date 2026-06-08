# Delete Matter From A Contact With Other Matters Remaining - Script

## Initial State
- Logged in to the isolated account (from _setup).
- Contact `contact last` exists with a single default matter `contact last`.

## Actions
1. **Add matter from pane**
   - `open_matter_page(page, context, contact_id)` -> contact's matter page.
   - `add_matter_from_pane(page, inner, outer, "matter")` (reused from matters_management).
2. **Delete the added matter**
   - `delete_matter(page, context, contact_id, "matter")`:
     resolve matter uid via API, navigate `?matter_uid=`, More -> "Delete client" -> confirm.
3. **CRM Email filter -> remaining matter**
   - `open_clients_list` -> `clear_all_filters` -> `add_text_filter("item-fields_filter.email", email)`.
   - `assert_filtered_clients(page, ["contact last"])`.
4. **Delete the last matter**
   - `delete_matter(page, context, contact_id, "contact last")`.
5. **CRM Email filter -> empty**
   - Re-apply the Email filter; `assert_filtered_clients(page, [])`.

## Success Verification
- After deleting `matter`, the Email filter still returns the contact via `contact last`.
- After deleting `contact last`, the Email filter returns no clients.
- This is the real validation (CRM content), not a toast.

## Waits / Stability
- Matter navigation: bounded open retry (1 + 2), 5s cap per wait (matters_management policy).
- Delete: wait on the DELETE response so a follow-up navigation can't abort the request.
- CRM reads: `assert_filtered_clients` polls + reloads to absorb CRM index lag.
