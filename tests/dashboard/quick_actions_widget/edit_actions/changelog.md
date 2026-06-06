# Changelog — edit_actions

## 2026-06-07 — Initial migration (VCITA2-13863)
- Migrated from `automation-js/features/spotlights/quick_actions_widget.feature`
  scenario `Quick actions widget - edit actions and error messages`.
- Covers remove/add actions, drag-reorder, and the min/max validation errors.
- Key discoveries / fixes during bring-up:
  - Checkboxes are visually-hidden Vuetify `<input role='checkbox'>`; click the parent
    wrapper, not the input (direct click times out).
  - The edit modal loads its saved checked-state lazily — wait for an `aria-checked='true'`
    checkbox before toggling, else `event` add raced and was lost.
  - The widget re-renders lazily after save — poll the displayed actions.
  - Drag-reorder needs a SortableJS-friendly mouse sequence (not a single `drag_to`).
  - Strengthened the error check: invalid save keeps the modal open + shows the alert.
