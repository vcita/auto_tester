# Changelog — Add/Remove Matter Collaborators

## 2026-06-03 - Initial migration (VCITA2-13794)

Migrated from `automation-js/features/steps/add-remove-staff-in-matter.feature`
(scenario "go to client page and prepare tests").

- New isolated subcategory `tests/clients/collaborators` under the `clients` category
  (`account_profile: isolated` — the test creates two staff, so it needs a dedicated account).
- `_setup` (API on the isolated account): create Staff B and Staff C (Platform API), one service
  offered by the owner + Staff C, and the client "new client". The warning-trigger appointment is
  created mid-test (see below), not in setup.
- UI (`manage_collaborators`): open the matter, open the additional-staff (collaborators) editor in
  the inner Vue frame (`#vue_iframe_layout`), then:
  - assert Staff B and Staff C are not collaborators initially;
  - add Staff B → assert shown; add Staff C → assert shown;
  - remove Staff B → assert removed and Staff C still shown;
  - seed a future appointment for the client assigned to Staff C (warning trigger) via API;
  - remove Staff C → assert the upcoming-appointments warning names the client and Staff C, confirm,
    and assert no collaborators remain (neither Staff B nor Staff C avatar present).
- DRY: moved `create_platform_staff_via_api` into shared `tests/account_api.py` (resolves the uid via
  the staff-list GET, returns `{uid,name,email}`); `reassign_helpers.py` re-exports it.
  `create_service_via_api` gained an optional `staff_uids` arg (default = owner only).

### Validation findings (resolved during first runs)

- Avatar `.avatar-initials` elements carry the full staff name as textContent while only the initials
  render; matching now uses Playwright `:text-is("SB")`/`:text-is("SC")` on the rendered initials.
- Seeding the warning-trigger appointment in setup auto-added Staff C as a matter collaborator, which
  broke the initial "Staff C absent" assertions. Moved appointment creation mid-test (after Staff C is
  a collaborator), matching the legacy ordering.
- The API service must be offered by Staff C, otherwise `/business/scheduling/v1/bookings` returns
  422 ("The provided staff member doesn't offer the provided service").
- Empty-state is asserted by the absence of both staff avatars (stronger than the legacy
  change-button "add" substring check, which is always true because the control reads "Add/Remove").

Quality vs legacy: exact rendered-initials matching (no fixed sleeps; all UI waits are explicit
condition waits capped at the 5s project policy). Validated with 3 clean focused runs on integration.
