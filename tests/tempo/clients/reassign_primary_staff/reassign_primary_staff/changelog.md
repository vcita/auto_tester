# Changelog — Reassign Matter Primary Staff

## 2026-06-03 - Code review fixes (VCITA2-13791)

- Determinism: resolve and cache the account **owner** staff uid (`first_staff_uid`) BEFORE creating
  Staff B, and pass it explicitly to the seeded appointment, so the appointment is reliably
  owner-assigned (the UI reassign is a genuine change) regardless of staff-list ordering.
- DRY: moved the shared account-API primitives (`account_request`, `first_staff_uid`,
  `create_service_via_api`, `create_appointment_via_api`, base-url/headers/pivot resolution) into
  `tests/account_api.py`; `reassign_helpers.py` and `recently_active_helpers.py` now reuse them.
  `reassign_helpers.py` keeps only the reassign-specific staff/client/directory-token/email helpers
  and drops the unused staff-parsing dead code.
- Wait caps: all UI waits capped at the 5s project policy (`PAGE_READY_TIMEOUT` 15000→5000, page
  navigation 30000→5000).
- Retries: appointment-reassignment re-check loop reduced from 6 attempts to 3 (1 attempt + 2 retries),
  matching the project retry cap.
- Docs: clarified that the email poll cadence is a bounded poll interval (not a fixed action sleep);
  closed the "confirm on first run" open items (validated on integration).

## 2026-06-03 - Initial migration (VCITA2-13791)

Migrated from `automation-js/features/steps/reassign-matter-primary-staff.feature`
(scenario "user sets a new primary staff member to a client").

- New subcategory `tests/clients/reassign_primary_staff` under the `clients` category.
- API setup (isolated `auto_account`, mirrors `recently_active_helpers`): create Staff B
  (Platform API), client `first last`, free service `test_service`, and an appointment for
  `test_service` assigned to the account owner (not Staff B).
- UI: open the matter, change the matter primary staff to Staff B with "reassign these
  appointments to the new assignee" checked, Save. Nested-iframe access mirrors `edit_matter`
  (angular outer frame + `#vue_iframe_layout` inner frame); the reassign dialog is Angular-Material
  in the outer frame.
- Assertion 1: the `test_service` appointment shows assignee `Staff B` in the matter Bookings tab
  (bounded condition-wait reload loop, per attempt ≤ 5s — reassignment can propagate async).
- Assertion 2: business receives an email with subject `first last was assigned to you`
  (`get_business_email_by_subject` polls `/infra/automation/message/content` with directory-token
  auth; bounded ~90s budget — documented exception to the 5s element cap for async email).
- No fixed sleeps; all waits are explicit condition waits capped at the project policy.

Open items pending first live run (see `migration_mapping.md`): confirm the change-staff dialog
frame/selectors via browser MCP, confirm the Bookings subtitle format, and confirm the email
endpoint shape/auth in integration.
