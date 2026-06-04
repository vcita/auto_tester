# Add/Remove Matter Collaborators — Steps (WHAT)

Migrated from `automation-js/features/steps/add-remove-staff-in-matter.feature`
(scenario "go to client page and prepare tests").

Preconditions (created via API in `_setup` on the isolated account): Staff B, Staff C,
a service (offered by Staff C), and the client "new client".

1. Open the matter page for **new client** and open the matter detail card.
2. Open the additional-staff (collaborators) editor.
   - Verify **Staff B** is **not** a collaborator yet.
   - Verify **Staff C** is **not** a collaborator yet.
3. Add **Staff B** as a collaborator and save.
   - Verify **Staff B** is now shown as a collaborator.
4. Add **Staff C** as a collaborator and save.
   - Verify **Staff C** is now shown as a collaborator.
5. Remove **Staff B** and save.
   - Verify **Staff B** is no longer shown, and **Staff C** is still shown.
6. Seed a future appointment for **new client** assigned to **Staff C** (warning trigger).
   This mirrors the legacy ordering, where the appointment is scheduled after Staff C is a
   collaborator and just before Staff C is removed.
7. Remove **Staff C**.
   - Verify a warning is shown: the client has upcoming appointments with Staff C.
   - Confirm the removal (save).
   - Verify there are no remaining collaborators (no Staff B or Staff C avatar remains).
