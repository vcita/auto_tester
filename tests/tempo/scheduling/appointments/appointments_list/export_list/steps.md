# Export appointments list (export_list)

Migrated from `automation-js/features/tempo/appointments-list.feature` (VCITA2-13953),
scenario 2 ("export appointments list - with no changes").

## Objective
Verify a business user can export the appointments list and that a "Bookings" file is
downloaded.

## Prerequisites
- From `_setup`: logged in on a fresh account (no bookings required for the export).

## Steps
1. Open the appointments list page.
2. Open the export dialog from the list action bar.
3. Confirm the export (accept the dialog defaults).
4. Verify a file whose name identifies it as the bookings export ("Bookings") is downloaded.

## Expected Result
- The export triggers a browser download whose filename contains "Bookings".

## In scope (UI)
- Opening the export dialog, confirming the export, and the resulting download are all
  in-scope UI behavior (kept UI, as in the legacy `exportMeetings` page object).
