# Changelog — multistaff / multi_staff_meeting

## 2026-06-08 — Initial migration (VCITA2-13950)

Migrated the "Schedule a multi staff meeting as an admin" scenario of
`automation-js/features/tempo/multistaff.feature` into autotester as part of the isolated
subcategory `scheduling/appointments/multistaff`.

- **Setup (API, in `_setup`):** enable `multistaff_features`; create `user_staff` (user) +
  `manager_staff` (manager); create client `rina success`; create the require-to-pay
  service `r2p_appointment` assigned to owner + both staff — each confirmed with a GET
  read-back. Owner display name captured for the assertion.
- **Test (UI):** owner schedules `r2p_appointment` / `rina success` selecting both
  additional staff, removes `user_staff` from the meeting, then asserts assigned staff =
  owner and additional staff = `manager_staff` only.
- **Selectors:** `data-qa` first (`service-picker-modal`, `service-name`,
  `additional-staff-listbox(-<name>)`, `vc-footer-Done`, `assigned-staff`,
  `assigned-additional-staff`, `display-name`); legacy `.additional-staff__button` and
  `div.summary-header h3` retained; listbox row text fallback when the per-name data-qa
  is absent.
- **Decisions:** assigned staff defaults to the logged-in user (only additional staff is
  selected explicitly, faithful to legacy); the new appointment id is resolved with a
  before/after appointments read-back (legacy `addBookingToContext`); the edit dialog is
  located by scanning frames for `vc-footer-Done`.
