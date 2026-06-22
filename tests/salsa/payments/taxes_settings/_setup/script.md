# Taxes Settings Setup - Script

## Initial State
- Runner switched to an isolated auto account (default country, USD).
- `context["username"]`, `context["password"]`, and `context["base_url"]` are available.

## Actions

### Step 1: Log in
- Call the shared login function `fn_login` with `context["username"]` and `context["password"]`.
- The login helper waits for the dashboard readiness signal.

## Success Verification
- Dashboard is reachable after login.
- No taxes exist on the fresh isolated account (verified implicitly by the empty starting list in `manage_taxes`).
