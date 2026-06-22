# Changelog — multistaff / schedule_as_user_staff

## 2026-06-08 — Initial migration (VCITA2-13950)

Migrated the "Schedule a meeting as a user staff" scenario of
`automation-js/features/tempo/multistaff.feature` into autotester as part of the isolated
subcategory `scheduling/appointments/multistaff`.

- **Setup (API, in `_setup`):** shared with `multi_staff_meeting` (multistaff enabled;
  `user_staff`/`manager_staff`; client `rina success`; require-to-pay `r2p_appointment`).
- **Test (SSO + UI):** switch the browser session to `user_staff` via the partner SSO API
  (reusing `calendar_helpers.switch_logged_in_staff`), schedule `r2p_appointment` /
  `rina success`, then assert assigned staff = `user_staff`, client `rina success`, and
  price `$1.00`.
- **Selectors:** `data-qa` first (`service-picker-modal`, `service-name`, `assigned-staff`,
  `display-name`, `balance-due-amount`); `div.summary-header h3` for the service header.
- **Decisions:** assigned staff defaults to the logged-in (switched-in) `user_staff`, so no
  explicit staff selection is needed; the appointments read-back uses the owner token (the
  SSO switch only changes the browser session), so the new meeting is still resolvable.
