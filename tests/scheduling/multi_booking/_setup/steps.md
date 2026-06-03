# Setup — Multi-booking

Preconditions for the multi-booking scenarios, mirroring the legacy feature
Background (minus the unused staff member).

## Steps

1. Log in to the isolated account (UI), using the account credentials from context.
2. Create three free 1-on-1 appointment services via API: `service1-<stamp>`,
   `service2-<stamp>`, `service3-<stamp>`. Stored in `context["mb_service_names"]`.
3. Create one client via API (Chuck Norris<stamp>). Stored in
   `context["mb_client"]`, `context["mb_client_id"]`, `context["mb_client_name"]`.

## Notes

- The legacy Background also creates a staff member via Platform API, but neither
  scenario assigns or asserts that staff, so it is not recreated (out of scope).
- Services and the client are created via API because they are prerequisites, not
  the behavior under test (the multi-booking scheduling itself is done via the UI).
