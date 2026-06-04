# Add/Remove Matter Collaborators — Script (HOW)

Source: `steps.md`. Legacy: `clients.js` `Clients.editCollaborators` /
`Clients.checkCollaboratorWarning` + `CollaboratorsDialog.*`. UI helpers live in
`tests/clients/collaborators/collaborators_ui.py`.

## Frames

Mirror `reassign_primary_staff` / `edit_matter`:
- outer Angular frame: `iframe[title="angularjs"]`
- inner Vue matter frame: `#vue_iframe_layout`

Unlike the primary-staff reassign dialog (outer Angular frame), the collaborators dialog renders in
the **inner** Vue frame (legacy `editCollaborators` switches to the vue iframe before clicking).

## Selectors (inner frame; confirmed by legacy baseline run)

- matter card: `.matter-name-title`
- open collaborators editor: `.additional-staff .matter-staff__change--btn`
- dialog body: `.dialog-cmp-content`
- staff select input: `div.v-select__selections`
- dropdown option: `.list-item-wrapper .chip-text.list-item` (filter by staff name)
- selected chip (remove): `span.chip-text` (filter by staff name)
- save: `.staff__confirm`
- collaborator avatar: `.avatar-initials`. The avatar element's textContent is the full staff name
  while only the initials render, so match the rendered initials with Playwright `:text-is("SB")`
  (`:text-is("SC")`). Initials = first letter of the first two name words. The matter primary-staff
  (owner) avatar shares `.avatar-initials`, but `SB`/`SC` never collide with the owner initials.
- removal warning: `.staff__comming-meeting`

## Flow

1. `open_matter(page, collab_client_id)`; `matter_frame(page)` opens the matter card and returns the
   inner frame.
2. Assert `assert_collaborator_absent(inner, "Staff B")` and `assert_collaborator_absent(inner,
   "Staff C")` on the matter card — neither `SB` nor `SC` avatar exists yet.
3. `open_collaborators_dialog(inner)`; `add_staff_in_dialog(inner, "Staff B")` →
   `save_dialog(inner)` → `assert_collaborator_shown(inner, "Staff B")`.
4. `open_collaborators_dialog`; `add_staff_in_dialog(inner, "Staff C")` → `save_dialog` →
   `assert_collaborator_shown(inner, "Staff C")`.
5. `open_collaborators_dialog`; `remove_staff_in_dialog(inner, "Staff B")` → `save_dialog` →
   `assert_collaborator_absent(inner, "Staff B")` + `assert_collaborator_shown(inner, "Staff C")`.
6. `create_appointment_via_api(context, service, client, staff_uid=staff_c)` — the warning trigger,
   created here (not in setup) so the initial "Staff C absent" assertions hold. Seeding the
   appointment in setup auto-adds Staff C as a collaborator (observed product behavior), which would
   break step 2; legacy also schedules it only after Staff C is a collaborator.
7. `open_collaborators_dialog`; `remove_staff_in_dialog(inner, "Staff C")` →
   `read_removal_warning(inner)`; assert it contains the client name ("new client") and "Staff C"
   (substring match — resilient to copy tweaks; legacy expected
   `"<client> has upcoming appointments with: <staff>"`). `save_dialog` →
   `assert_no_collaborators(inner, ["Staff B", "Staff C"])` (neither avatar remains — stronger than
   the legacy change-button "add" substring check, which is always true because the control reads
   "Add/Remove").

## Waits / risks

- No fixed sleeps. All UI waits are explicit Playwright condition waits capped at the 5s policy.
- Presence/absence assertions match the exact rendered initials (`:text-is`), which is stronger than
  the legacy "some avatar differs" check (a quality improvement, no scope loss).
- Confirmed on integration (3 clean runs): chip-remove via `span.chip-text` click deselects;
  dropdown option select + save persists; the owner primary-staff avatar never collides with the
  `SB`/`SC` initials; the removal warning reads "new client has upcoming appointments with: Staff C".
