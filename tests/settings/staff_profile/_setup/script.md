# Staff Profile — Setup Script

> API-only setup + login. No UI exploration required (prerequisites are out of the
> behavior under test, per migrate skill: prefer API for prerequisites).

## Actions

### Step 1: Deny pov_landing_page_routing
- `deny_features(context, "pov_landing_page_routing")` (tests.account_api).

### Step 2: Capture owner staff
- `get_owner_staff(context)` (staff_profile_api) → `{uid, display_name, email}`.
- Store under `context["staff_profile"]["owner"]`.

### Step 3: Create second staff (role user)
- `create_user_staff(context, "user_staff", f"user+role+{seq}@vmeetme.com")`.
- Store under `context["staff_profile"]["user_staff"]`.

### Step 4: Log in
- `fn_login(page, context, username, password)`.

## Success Verification
- Owner display_name captured; user_staff has a uid; session logged in.
