# Invoice Late Fee (UI) Setup - Script

## Initial State
- Runner created an isolated US account; not yet logged in.

## Actions
1. `fn_login(page, context, username, password)`.
2. `account_api.create_client(context, "first", "last", "test+<ts>@vmeetme.com")`;
   store `created_client_id` / `created_client_name` / `created_client_email` /
   `client_portal_token`.
3. `account_api.create_service_via_api(context, "service<ts>", charge_type="paid_non_secured",
   price="100")`; store `invoice_service_name`.

## Success Verification
- Login completes; create-client returns id + portal token; service create returns a name.

## Waits / Stability
- Login readiness handled by `fn_login`; API calls raise on non-2xx.
