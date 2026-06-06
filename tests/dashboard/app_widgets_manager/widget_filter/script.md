# Script — Sales Widget Feature-Flag Filter

## Flow
1. `deny_features(context, "payments_module")` — blacklist the FF + reset cache.
2. `open_dashboard(page)` (reload) → `assert_widget_count(page, 5)` and
   `is_widget_shown(page, "sales")` is False.
3. `enable_features(context, "payments_module")` — whitelist the FF + reset cache.
4. `open_dashboard(page)` (reload) → `is_widget_shown(page, "sales")` is True.

## Notes
- `is_widget_shown` mirrors legacy `isWidgetFound` (`.sales-widget`, 5s try-loop).
- The FF change is applied via the admin API and a full dashboard reload, so the
  widget set re-renders from the new flag state (no fixed sleeps).
- The flag is restored to enabled at the end, leaving the shared dashboard account
  in its default state.
