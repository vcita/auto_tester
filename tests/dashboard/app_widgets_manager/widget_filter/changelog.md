# Changelog — widget_filter

## 2026-06-07 — Initial migration (VCITA2-13864)
- Migrated from `automation-js/features/tempo/app-widgets-manager.feature`
  scenario `widget filter`.
- Denies/re-enables payments_module and asserts the sales widget visibility and
  the widget count (5 vs 6) via dashboard reloads.

## 2026-06-07 — Wait audit + dashboard readiness
- `open_dashboard` goto lowered 15s -> 5s (`PAGE_TIMEOUT`); `domcontentloaded` fires fast
  and readiness is gated by the `.main` + `[data-qa="EmbeddedAppDelegator"]` waits.
- `open_dashboard` and `is_widget_shown` now gate on the dashboard `.main` section before
  probing widgets, mirroring legacy `isWidgetFound` (waits `main_section` first) so a
  still-mounting grid is never read as an absent widget — the reliability fix the legacy
  step relied on. Feature-flag writes already reset the features cache server-side
  (`_set_features` -> `reset_features_cache`), so no separate FF GET read-back is needed
  (legacy did not read back either; it relied on cache reset + main-section readiness).
- `assert_widget_count` polls the exact count on a bounded <=5s loop (0.2s cadence).
