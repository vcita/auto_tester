# Multi-staff meeting (multi_staff_meeting) — Detailed Script

> Migrated from automation-js/features/tempo/multistaff.feature (VCITA2-13950).
> BO scheduling dialog is a Vue iframe (`#vue_iframe_layout`) inside the Angular iframe
> (`iframe[title="angularjs"]`); the meeting page renders in the Angular iframe.

## Initial state

- Owner is logged in (from `_setup`) on a fresh multistaff account.
- Two staff (`user_staff<seq>`, `manager_staff<seq>`), client `rina success`, and the
  service `r2p_appointment<seq>` (require to pay, assigned to owner + both staff) exist.

## Step 1 — Schedule with additional staff (UI)

`schedule_appointment(page, context, client, service, additional_staff=[user_staff, manager_staff])`

- Snapshot business appointment ids (GET `/platform/v1/scheduling/appointments`) for new-id
  resolution (legacy `addBookingToContext`).
- Calendar `New` (`inner.get_by_role('button', name='New')`) -> `Appointment` menuitem.
- Client picker: `outer.get_by_role('textbox', name='Search by name, email or tag')`, then the
  client button by text. Retries the New->client handoff once (proven create_appointment race).
- Service picker (`inner [data-qa="service-picker-modal"]:visible`): search + click the
  `.service-item` row's `[data-qa="service-name"]`.
- Set tomorrow 10:00 AM (best-effort) and fill Address if present.
- Additional staff: click `.additional-staff__button`, wait `[data-qa="additional-staff-listbox"]`,
  check `[data-qa="additional-staff-listbox-<display_name>"] input` for each name (verify
  `aria-checked`/checkbox; fallback to listbox row by text), then `[data-qa="vc-footer-Done"]`.
  Selectors from legacy createMeetingDialog.js (`selectMultiStaff`) + additionalStaff(Popover).vue.
- Click Schedule (`button name ~ /Schedule appointment|^Schedule$/`, force), then poll the
  appointments read-back until a new id appears -> the new appointment id.

## Step 2 — Remove an additional staff (UI)

`open_meeting_page(page, id)` -> `remove_additional_staff(page, user_staff)`

- Meeting page URL `/app/appointments/<id>`; wait `div.summary-header h3`.
- Click `[data-qa='assigned-additional-staff'] a` (the Add/remove link, appointment-t.html.haml).
- The edit dialog mounts in a Vue iframe — locate the frame containing `[data-qa="vc-footer-Done"]`.
- Uncheck `[data-qa="additional-staff-listbox-<user_staff>"] input`, click `[data-qa="vc-footer-Done"]`,
  wait for `.v-overlay--active` to close. (Legacy appointment.js `removeAdditionalStaff`.)

## Step 3 — Assert the meeting (UI)

Re-open the meeting page for a fresh read, then assert:

| Field | Selector | Expected |
| --- | --- | --- |
| meeting_name | `div.summary-header h3` | contains `r2p_appointment<seq>` |
| client | `[data-qa='display-name']` | contains `rina success` |
| assigned_staff | `[data-qa='assigned-staff']` | contains the owner display name |
| additional_staff | `[data-qa='assigned-additional-staff']` | contains `manager_staff<seq>`, not `user_staff<seq>` |

## Notes

- Assigned staff defaults to the logged-in user (owner here); only additional staff is
  selected explicitly, faithful to the legacy scenario.
- Owner display name is captured in `_setup` (fresh accounts auto-generate the business
  name that the legacy table hard-coded as "Automation test business").
