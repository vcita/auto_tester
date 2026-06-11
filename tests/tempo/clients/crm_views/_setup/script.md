# CRM Views Setup — Script

## Function
`setup_crm_views(page, context)` in `_setup/test.py`.

## Steps (HOW)
1. **Capture owner** — `crm_views_helpers.capture_owner(context)`: GET
   `/platform/v1/businesses/{pivot}/staffs?status=all`, take `staff[0]` as the owner
   (admin). Done before creating extra staff so the owner is unambiguous. Cache uid.
2. **Create staff** — `create_staff_user(context, "Staff User", staff+<seq>@vmeetme.com, "user")`
   → `account_api.create_platform_staff_via_api` (POST staffs + GET read-back).
3. **Admin login** — `fn_login(page, context, username, password)` (UI login with the
   isolated account credentials → owner session).
4. **Close default tabs** — `open_clients_list` then `close_tab` for "New inquiries",
   "Open payments", "All" (click tab `VcTabs-tab-<name>`, click close
   `VcTabs-close-<name>`, assert the tab is gone).

## Context
- `context["crm_views"] = {"owner": {...}, "staff_user": {...}}`.

## Waits
- All UI waits are explicit visibility/URL/count waits capped at 5s; no fixed sleeps.
- API calls use the shared 5s-timeout `account_request`.
