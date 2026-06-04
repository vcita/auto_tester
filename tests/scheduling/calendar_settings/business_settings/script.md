# Script: Calendar business settings

Phase 2 for the `business_settings` test. UI actions are owned by the test (legacy used
the calendar settings side pane + view menu); helpers live in
`calendar_settings_helpers.py` and reuse the proven calendar frame/side-pane utilities.

## Step 1: Open the Calendar page

VERIFIED PLAYWRIGHT CODE:

```python
open_calendar_page(page)
```

## Step 2-5: Set business settings (start-of-week + time format), save, close

Open the scheduler settings dropdown -> Business settings. The side pane is a Vuetage
component (`BusinessSettings.vue`); the two `SettingsSelectBlock` selects are reached via
their `data-qa` blocks and the inner `.settings-select__select-aria_select` control, then
the option is picked by exact text (`Tuesday`, `24 hours` from `settings.en.yml`). The
side-pane save button (`business-settings-layout_save-mobile`) is clicked and we wait for
it to disable (the save confirmation), then close the side pane.

VERIFIED PLAYWRIGHT CODE:

```python
set_business_settings(page, week_start_day="Tuesday", time_format="24 hours")
```

## Step 6: Switch to Week view and hide weekends

Mirrors legacy `hideWeekEnds`: ensure Week view via the view menu, then toggle
`option-toggle_show_weekend` off.

VERIFIED PLAYWRIGHT CODE:

```python
hide_weekends(page)
```

## Verification: Week-view header

Read the rendered Week header (first weekday label, first hour label, weekday count) and
assert against the legacy expected values. Polls the header instead of a fixed sleep.

VERIFIED PLAYWRIGHT CODE:

```python
display = get_calendar_week_display(page)
assert display == {"week_start_day": "Tue", "time_format": "00:00", "num_of_days": "5"}, display
```
