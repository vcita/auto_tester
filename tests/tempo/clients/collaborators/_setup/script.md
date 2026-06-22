# Collaborators Setup — Script (HOW)

Source: `steps.md`. Reuses shared primitives in `tests/account_api.py`.

On the isolated `context["auto_account"]` (api_token + pivot_uid):

1. `fn_login(page, context, username, password)` — UI login with the isolated-account creds.
2. `create_platform_staff_via_api` x2 → POST `/platform/v1/businesses/{pivot}/staffs`
   `{staff:{display_name, email, role:"user"}}` for `Staff B` and `Staff C`. Capture each uid.
   Save `context["collab_staff_b"]` / `context["collab_staff_c"]` = `{uid,name,email}`.
3. `first_staff_uid(context)` → resolve the account owner uid (before the service is created).
4. `create_service_via_api(context, "service", staff_uids=[owner, staff_c.uid])` → POST
   `/v2/settings/services` (free appointment), offered by the owner AND Staff C so the warning-trigger
   appointment (assigned to Staff C) is accepted by `/business/scheduling/v1/bookings`.
   Save `context["collab_service"]`.
5. `create_client(context, "new", "client", email)` → POST `/platform/v1/clients`.
   Save `context["collab_client"]`, `collab_client_id`, `collab_client_name` (= "new client").

Notes:
- The warning-trigger appointment is NOT seeded here: creating it auto-adds Staff C as a matter
  collaborator (observed product behavior), which would break the test's initial "Staff C absent"
  assertions. It is created mid-test (after Staff C is added as a collaborator), mirroring the legacy
  ordering where the appointment is scheduled only after Staff C is a collaborator.
- Legacy scheduled the appointment via the back-office UI; scheduling is a precondition (not the
  behavior under test), so it moves to API per migration rules.
- Static names (`Staff B`, `Staff C`, `new client`) are intentional: the avatar initials (`SB`, `SC`)
  and the warning copy (`new client has upcoming appointments with: Staff C`) are asserted by the test.
