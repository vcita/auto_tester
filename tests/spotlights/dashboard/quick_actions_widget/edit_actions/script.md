# Script — Edit Actions And Error Messages

## Flow
1. `open_dashboard(page)`.
2. `remove_actions(page, ["invoice", "point_of_sale"])` — open edit modal, uncheck both, save.
3. `add_actions(page, ["event"])` — open edit modal, check event, save.
4. `assert_actions(page, [client, appointment, message, estimate, event])` (polled).
5. `reorder_actions(page, "message", "client")` — drag message's handle above client, save.
6. `assert_actions_in_order(page, "message,client")` — adjacency check (matches legacy
   `join(",").indexOf("message,client") > -1`).
7. `save_all_actions_expecting_error(page, checked=False)` — uncheck all, save, assert the
   modal stays open + alert visible, cancel.
8. `save_all_actions_expecting_error(page, checked=True)` — check all, save, same error assert.

## Selector / timing notes
- Edit modal is top-level POV: `[data-qa='edit-quick-actions-modal']`,
  list `[data-qa='vc-draggable-list']`.
- Each checkbox is a **visually-hidden Vuetify `<input role='checkbox' data-qa='item-<name>'>`**;
  clicking the input itself times out, so `_set_checkbox` clicks its parent wrapper and asserts
  `aria-checked` flips.
- The modal loads its saved checked-state **lazily** — `open_edit_modal` waits for at least one
  `[aria-checked='true']` checkbox before toggling, so we never save a half-loaded selection.
- The widget re-renders lazily after save — `assert_actions` / `assert_actions_in_order` poll up
  to 5s.
- Reorder uses a SortableJS-friendly mouse sequence (mousedown on handle, nudge to initiate,
  travel, settle past the insert line, mouseup) — a single `drag_to` does not trigger it.
- Error checks are **stronger than legacy**: an invalid save must keep the modal open (a valid
  save closes it) AND show `[data-qa='vc-alert']`.
