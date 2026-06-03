# Reassign Matter Primary Staff — Script (HOW)

Source: `steps.md`. Legacy: `client.js` `reassignMatterPrimaryStaff` + `getAssignedStaff`,
`emails.js` `getEmailBySubject`. Helpers live in
`tests/clients/reassign_primary_staff/reassign_helpers.py`.

## Data

- `STAFF_B_NAME = "Staff B"`, email `staffb+<ms>@vmeetme.com`, role `user`.
- Client `first last`, email `contact+<ms>@vmeetme.com`.
- Service `test_service` (free, appointment, duration 60).
- `ASSIGNMENT_EMAIL_SUBJECT = "first last was assigned to you"`.

## API setup (no UI; isolated auto-account)

Shared account primitives live in `tests/account_api.py` (`account_request`, `first_staff_uid`,
`create_service_via_api`, `create_appointment_via_api`); reassign-specific helpers (Platform staff,
client, directory token, email poll) live in `reassign_helpers.py`. On `context["auto_account"]`
(api_token + pivot_uid):
0. `first_staff_uid` → resolve and cache the **account owner** staff uid BEFORE Staff B exists, so the
   owner-assigned seeding below is deterministic regardless of staff-list ordering.
1. `create_platform_staff_via_api` → POST `/platform/v1/businesses/{pivot}/staffs`
   `{staff:{display_name, email, role}}` → Staff B.
2. `create_client_via_api` → POST `/platform/v1/clients` → client `first last` (capture id).
3. `create_service_via_api` → POST `/v2/settings/services` (free appointment) → `test_service`.
4. `create_appointment_via_api` → POST `/business/scheduling/v1/bookings`
   `{business_id, staff_id=<owner>, service_id, client_id, start_time=+30d}` — assigned to owner,
   NOT Staff B (the reassign must be a real change).

Save `created_client_id` to context for navigation.

## UI: reassign primary staff

Iframe layers (mirror `edit_matter/test.py`):
- `angular_iframe = page.locator('iframe[title="angularjs"]')` (outer Angular).
- `outer = page.frame_locator('iframe[title="angularjs"]')`.
- `inner = outer.frame_locator('#vue_iframe_layout')` (Vue matter view).

Flow:
1. Navigate to `/app/clients/{client_id}`; wait for the angular iframe, then the inner Vue
   matter view to render (matter title visible).
2. In `inner`: open the matter primary-staff editor — click the matter title card, then the
   change-staff control. Prefer `data-qa`; legacy CSS fallbacks: matter card `.matter-name-title`,
   change button `.matter-staff__change--btn.matter-staff__change--initials`.
   (Confirm exact frame + selector via browser MCP on first run — see open items.)
3. The reassign dialog is Angular-Material in the **outer** (angular) frame:
   - open the staff dropdown and pick `Staff B` (role `option`/`md-option` by text).
   - check the "Reassign these appointments to the new assignee" checkbox
     (`md-checkbox[aria-label="Reassign these appointments to the new assignee"]`).
   - click `Save` (`get_by_role("button", name=/Save/i)`); wait for the dialog to close.

Selector policy: `data-qa` first, then role/text, raw CSS only for the existing stable matter/booking
selectors. Where a stable `data-qa` is missing, document the fallback and the suggested `data-qa`.

## Assertion 1 — appointment reassigned

In `inner`: open the matter **Bookings** tab. Find the booking row whose title equals `test_service`
(`.matter-page-list-item` → `.v-list-item__title.booking-title`), read its subtitle
(`.v-list-item__subtitle.booking-with`, format "With <name>"), strip the leading word, and assert it
equals `Staff B`. Re-read with a bounded condition wait (per attempt ≤ 5s) because the reassignment
can propagate asynchronously.

## Assertion 2 — assignment email

`get_business_email_by_subject(context, ASSIGNMENT_EMAIL_SUBJECT)`:
- directory token via `resolve_directory_token` (env `VCITA_DIRECTORY_TOKEN`, else
  `directory_id` + admin token — proven by VCITA2-13777).
- GET `{api_base}/infra/automation/message/content?business_uid={pivot}` with
  `Authorization: Token <dirtoken>`.
- Poll until an item with `subject == ASSIGNMENT_EMAIL_SUBJECT` appears. Bounded total budget ~90s,
  each request 5s timeout (documented exception to the 5s element cap — async email delivery,
  same class as reviews email). Assert the email is found.

## Waits / risks

- No fixed action-completion sleeps. UI waits are explicit state conditions capped at 5s.
- Booking propagation re-check loop is capped at 2 retries (3 attempts), per the project retry policy.
- The async email poll uses a fixed ~3s poll cadence within a bounded ~90s budget (documented
  exception to the 5s element cap — this is a poll interval, not a wait-for-action sleep).
- Dialog frame/selectors and the email endpoint shape were confirmed on integration (validated runs).
