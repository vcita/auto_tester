# Schedule as a user staff (schedule_as_user_staff) — Detailed Script

> Migrated from automation-js/features/tempo/multistaff.feature (VCITA2-13950).
> BO scheduling dialog is a Vue iframe (`#vue_iframe_layout`) inside the Angular iframe
> (`iframe[title="angularjs"]`); the meeting page renders in the Angular iframe.

## Initial state

- Fresh multistaff account (from `_setup`) with two staff (`user_staff<seq>`,
  `manager_staff<seq>`), client `rina success`, and the service `r2p_appointment<seq>`
  (require to pay, assigned to owner + both staff).

## Step 1 — Switch logged-in staff (API/SSO)

`switch_logged_in_staff(page, context, user_staff)` (reused from calendar_helpers)

- GET `/v1/partners/sso/token?staff_uid=<uid>` (partner base URL + directory token), then
  navigate to `/v1/partners/sso/login?staff_uid=...&sso_token=...&redirect_to=/app/dashboard`.
- Mirrors legacy `switching logged in staff to "user_staff" via API` (loginBySso).

## Step 2 — Schedule an appointment (UI)

`schedule_appointment(page, context, client, service)` (no additional staff)

- Same calendar `New` -> `Appointment` -> client picker -> service picker -> set tomorrow
  10:00 AM -> Schedule flow as multi_staff_meeting. Assigned staff defaults to the
  logged-in `user_staff` (no explicit staff selection), faithful to the legacy scenario.
- New appointment id resolved via the appointments read-back snapshot.

## Step 3 — Assert the meeting (UI)

`open_meeting_page(page, id)` then assert:

| Field | Selector | Expected |
| --- | --- | --- |
| meeting_name | `div.summary-header h3` | contains `r2p_appointment<seq>` |
| client | `[data-qa='display-name']` | contains `rina success` |
| assigned_staff | `[data-qa='assigned-staff']` | contains `user_staff<seq>` |
| price | `[data-qa='balance-due-amount']` | contains `$1.00` (formatPrice(1, USD)) |

## Notes

- The API token used for the appointments read-back stays the owner token (the SSO switch
  only changes the browser session), so the new meeting is still resolvable by id.
