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

## 2026-06-07 — Wait audit
- `open_dashboard` goto lowered 15s -> 5s (`PAGE_TIMEOUT`); `domcontentloaded` fires fast
  and widget readiness is gated separately by the `.quick-actions-widget` wait.
- Drag-reorder retains four short `wait_for_timeout` pauses (<=150ms). These are
  **drag-mechanics timing**, not arbitrary settles: SortableJS only arms/animates a drag
  when pointer moves are separated by short gaps, so each pause gates the next move
  (grab -> drag-start threshold -> travel -> insert line) so the library registers the
  reorder. Documented inline; not replaceable by a condition wait without flaking drops.
- `assert_actions` / `assert_actions_in_order` poll the lazily re-rendered widget on a
  bounded <=5s loop with a 0.2s poll interval (cadence, not a blind pre-assert sleep).
- Fixed a latent selector bug surfaced on re-validation: the edit modal renders a hidden
  template copy of `[data-qa='vc-alert']` next to the live one, so the min/max validation
  assertion now targets `[data-qa='vc-alert']:visible` (plain `.first` latched onto the
  hidden duplicate and failed even though the error was on screen).
