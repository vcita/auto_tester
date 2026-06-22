# Setup script — Multi-booking

## Entry function
`setup_multi_booking(page, context)`

## Implementation
1. Validate `context["username"]` / `context["password"]` (isolated account).
2. `fn_login(page, context, username, password)`.
3. Loop 1..3: `create_service_via_api(context, f"service{i}-{stamp}")`; collect
   names into `context["mb_service_names"]`.
4. `create_client(context, "Chuck", f"Norris{stamp}", f"mb{stamp}@vmeetme.com")`;
   store client dict / id / full_name in context.

## Reused helpers
- `tests._functions.login.test.fn_login`
- `tests.account_api.create_service_via_api`, `create_client`

## Notes
- `<stamp>` = milliseconds, keeps service names and client name unique so the
  Quick Actions / service picker searches stay deterministic across runs on the
  shared isolated account.
