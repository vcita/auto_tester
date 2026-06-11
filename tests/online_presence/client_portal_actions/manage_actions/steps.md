# Steps — Add/Edit/Hide/Show/Delete Client Portal Action

Migrated from `automation-js/features/tempo/client-portal-actions.feature`
(Scenario: "Create, edit, hide, show, delete new client portal action").

**Precondition (setup):** logged in to the isolated account; verification client
created via API with its client portal token captured.

1. **Add action** — In the Client Portal editor, add a `Contact us` action with
   button text `Leave details 1`.
2. **Verify portal displays it** — Open the client portal livesite as the client;
   it displays `Leave details 1`.
3. **Edit action** — Rename the action's button text `Leave details 1` → `Leave details 2`.
   *(No portal re-check — legacy commented this out due to CP cache timing.)*
4. **Hide action** — Hide the `Leave details 2` action.
5. **Verify portal hides it** — The client portal no longer displays `Leave details 2`.
6. **Show action** — Show the `Leave details 2` action again. *(No portal re-check — CP cache.)*
7. **Delete action** — Delete the `Leave details 2` action.
8. **Verify portal removes it** — The client portal no longer displays `Leave details 2`.
