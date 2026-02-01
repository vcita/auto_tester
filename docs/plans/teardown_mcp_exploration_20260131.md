# Appointments Teardown – MCP Exploration (2026-01-31)

## Scope

Full teardown flow explored in browser via Playwright MCP, using the same account as config (`itzik+autotest.1769462440@vcita.com`), to confirm behavior before assuming fixes.

## Flow Executed

1. **Step 0 (Dashboard)**  
   - Already on dashboard; Quick actions visible.  
   - Sidebar: Dashboard, Inbox, Calendar, **Properties** (4th item), Sales, etc.

2. **Step 1 – Delete client (fn_delete_client)**  
   - Clicked **Properties** in sidebar → `/app/clients`.  
   - List toolbar: **Filters** button and list searchbox **"Search by name, email, or phone number"** (this account had the aria-label; other runs may not).  
   - Searchbox: `page.get_by_role("searchbox").nth(1)` is the list searchbox (first is header "Search").  
   - Typed "Appt TestClient", clicked row → client detail `/app/clients/{id}`.  
   - Client detail is in iframe; **More** button has `name='More icon-caret-down'`.  
   - More → menu with **menuitem "Delete property"** (role=menuitem and text "Delete property" both present).  
   - Clicked "Delete property" → confirmation dialog: **"This will delete the property, continue?"** with **Cancel** and **Ok**.  
   - **Finding:** Confirm button in this vertical is **"Ok"**, not **"Delete"**.  
   - Clicked **Ok** → dialog closed; page showed "(deleted)" and "Properties (0)". Delete succeeded.

3. **Step 2 – Delete service (fn_delete_service)**  
   - Not fully re-run in this session; delete_client was the focus.  
   - delete_service goes: Settings → "Define the services your" → services list → click service → Delete → confirm (delete_service uses `name='Ok'` for confirm).

## Findings

| Item | Observation |
|------|-------------|
| **Delete confirm button (Properties)** | Dialog shows **"Ok"** and **"Cancel"**. Code uses `dialog.get_by_role('button', name='Delete')`, which does **not** match "Ok" and would timeout. |
| **Menuitem** | "Delete property" is exposed as `role="menuitem"` and text "Delete property". Both `get_by_role("menuitem")` and `menu.get_by_text(re.compile(r"^Delete ", re.I))` can work; text is more resilient if menuitem is missing elsewhere. |
| **List searchbox** | On this run the list searchbox had aria-label "Search by name, email, or phone number". Heal had noted it missing on Properties; strategy of waiting for Filters then `searchbox.nth(1)` is correct. |

## Required fix

- **delete_client Step 6:** Support both **"Delete"** and **"Ok"** for the confirm button (e.g. `dialog.get_by_role('button').filter(has_text=re.compile(r'^(Delete|Ok)$', re.IGNORECASE))` or equivalent) so Properties (Ok) and other verticals (Delete) both work.

## Conclusion

The full delete-client leg of teardown was exercised in MCP. The only blocking issue found is the confirm button label: **Properties uses "Ok"**, so the test must accept both "Ok" and "Delete" for the confirm action.
