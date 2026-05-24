# Migration Mapping: Recently Active Clients

Source: `automation-js/features/steps/clients-recently-active.feature`

## Legacy Scenario

- `Recently active clients shown in dashboard`
  - Creates a fresh account.
  - Denies `new_dashboard` so the legacy dashboard is used.
  - Creates one service via API.
  - Creates one client via API.
  - Logs in via API and verifies the dashboard has no recently active clients.
  - Creates an appointment for the first client via API.
  - Verifies the dashboard shows `first last`.
  - Creates a second client via API.
  - Creates an appointment for the second client via API.
  - Verifies the dashboard shows `first2 last2` before `first last`.

## Legacy Step Mapping

- `user creates account`
  - Auto_tester runner creates a fresh auto account for the run.
- `user denies feature flags ... new_dashboard`
  - Integration currently serves the POV dashboard. Auto_tester preserves the same behavior by selecting the dashboard Clients widget's recently active view before asserting.
- `user creates new service via API`
  - `create_service_via_api()` posts to `/v2/settings/services` with the last category and first staff member.
- `user creates new client via API`
  - `create_client_via_api()` posts to `/platform/v1/clients` with `source_name: automation`.
- `user logged in to automatic account via API`
  - The clients category setup performs UI login using the fresh auto account credentials.
- `dashboard shows that there are no recently active clients`
  - `assert_no_recently_active_clients()` verifies the visible empty state in the current dashboard Clients widget, with a legacy `.dashboard-clients-container` fallback.
- `user schedules new appointment via API`
  - `create_appointment_via_api()` posts to `business/scheduling/v1/bookings`.
- `dashboard shows the following recently active clients`
  - `assert_recently_active_clients()` polls the dashboard until the expected number and order of client names appears in the selected recently active view.

## Auto Tester Structure

- Category: `clients`
- Subcategory: `recently_active`
- Test: `recently_active_clients`

## Helper Gaps

- Existing auto_tester API helpers for clients are local to `custom_status`, so this migration adds local helpers for recently active setup rather than coupling the new test to another subcategory.
- The legacy test denied `new_dashboard`; the migrated test supports the current POV dashboard using stable `data-qa` selectors and keeps the legacy selector path as a fallback.
- The legacy scenario is tagged `@unstable` because seeker indexing can lag; the migrated test preserves this by using a bounded condition wait and dashboard reloads.

## Scope Preservation

- Preserved no-active-clients assertion.
- Preserved one-active-client assertion.
- Preserved two-active-clients ordering assertion, with the newest active client expected first.
- Preserved API setup for service, clients, and appointments while keeping the user-visible dashboard as the assertion surface.
