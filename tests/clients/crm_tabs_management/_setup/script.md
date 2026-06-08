# Setup Script: CRM Tabs Management

## Login
- `fn_login(page, context, username=context["username"], password=context["password"])`.

## Self-client (API)
- `create_self_client(context, "form_first", "form_last", context["username"])`
  -> `POST /platform/v1/clients` with the owner email and `source_name="automation"`.
- The owner email makes the CRM render the row with the `(You as a client)` suffix, which
  the scenario asserts. Store the expected label in `context["self_client_label"]`.

## Recently-active activity (API)
- `create_service_via_api(context, "CRM Tabs Service <ts>")` then
  `create_appointment_via_api(context, service, client)`.
- A bare API client has no last-activity and never appears in the "Recently active" view.
  Booking an appointment registers recent activity (proven by the recently_active
  migration), reproducing what the legacy livesite form submission did.

## Notes
- The livesite leave-details submission is Background setup (not scenario scope), so it is
  replaced by the equivalent API client creation + booking. The `(You as a client)` label
  and the "Recently active" search assertions validate the setup produced the same state.
