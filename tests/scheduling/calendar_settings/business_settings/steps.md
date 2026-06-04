# Test: Calendar business settings

Migrated from `automation-js/features/tempo/calendar-settings.feature` — Scenario
"Calendar business settings".

## Objective

Change the business calendar settings (start-of-week, time format), hide weekends, and
verify the resulting Week-view header.

## Preconditions

- Logged in as the account owner (subcategory `_setup`).

## Steps

1. Open the Calendar page.
2. Open the scheduler settings dropdown and choose Business settings.
3. Set Start week on to `Tuesday`.
4. Set time format to `24 hours`.
5. Save the business settings and close the side pane.
6. Switch the calendar to Week view and hide weekends.

## Expected Result

The Week view header shows:

- First weekday label: `Tue`
- First hour label: `00:00` (24-hour format)
- Number of visible days: `5` (weekends hidden)
