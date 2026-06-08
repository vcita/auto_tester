# export_list — HOW (locators + flow)

Helpers: `tests/scheduling/appointments/appointments_list/appointments_list_helpers.py`.
Frames: outer `iframe[title="angularjs"]` → inner `#vue_iframe_layout` (Vue bookings page).

## Locators (verified against frontage source)

| Purpose | Frame | Locator |
| --- | --- | --- |
| Export icon (action bar) | inner | `.icon-export` page-action (BookingActionBar `action-export`) |
| Export dialog primary action | inner | `[data-qa="vc-footer-Extract"]` (VcInputModal ok-button-label `booking.extract.extract`) |
| Export dialog (fallbacks) | inner | `[data-qa="vc-footer-Export"]`, then `role=button name=/Extract\|Export/` |

## Flow

1. `open_appointment_list(page)` — navigate to `/app/appointment-list`, wait for the list to be ready.
2. `export_appointment_list(page)`:
   - click the `.icon-export` page-action to open the export dialog,
   - wrap the confirm click in Playwright `page.expect_download()`,
   - click the dialog's primary action (Extract/Export),
   - return the captured `download`.
3. Assert `download.suggested_filename` contains "Bookings" (case-insensitive).

## Notes / decisions

- **Download verification**: the page exports by building a `data:` anchor with
  `download = "Bookings_<start>_to_<end>"` (`downloadFile` in BookingsPage.vue). Capturing the
  Playwright download and asserting the filename contains "Bookings" faithfully reproduces the legacy
  `Then "Bookings" downloaded` (which checked the latest download filename includes
  `getExpectedDownloadTitle("Bookings")` = `Bookings_<start>_to_<end>`).
- **Label change**: the legacy clicked `[data-qa="vc-footer-Export"]`, but the current dialog's OK button
  label is `booking.extract.extract` ("Extract"), so the primary action is `[data-qa="vc-footer-Extract"]`.
  A small fallback chain keeps the click resilient if the design-system label/data-qa differs.
- **Waits**: the export-icon and dialog waits use the 5s cap; the download capture timeout is also ≤5s.
