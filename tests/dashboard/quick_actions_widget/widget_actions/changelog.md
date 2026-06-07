# Changelog — widget_actions

## 2026-06-07 — Initial migration (VCITA2-13863)
- Migrated from `automation-js/features/spotlights/quick_actions_widget.feature`
  scenario `Quick actions widget - actions`.
- Verifies the six default quick actions and that the client action opens the
  Angular new-client modal.
- Discovered live that the widget is top-level POV (frame `''`) and the new-client
  dialog is in the angular iframe.
