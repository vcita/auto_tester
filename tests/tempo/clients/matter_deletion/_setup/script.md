# Matter Deletion Setup - Script

## Initial State
- Runner created an isolated account; not yet logged in.

## Actions
1. `fn_login(page, context, username, password)` with isolated-account credentials.
2. `account_api.create_client(context, "contact", "last", "contact+<ts>@vmeetme.com")`;
   store `contact_id` / `contact_name` / `contact_email` in context.

## Success Verification
- Login completes; the create-client API returns an id + portal token.

## Waits / Stability
- Login readiness handled by `fn_login`; the API call raises on non-2xx.
