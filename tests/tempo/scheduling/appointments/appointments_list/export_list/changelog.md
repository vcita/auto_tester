# Changelog — appointments_list / export_list

## 2026-06-08 — Initial migration (VCITA2-13953)

Migrated `automation-js/features/tempo/appointments-list.feature` scenario 2
("export appointments list - with no changes").

- **Test (UI):** open the appointments list page, open the export dialog from the action
  bar (`.icon-export`), confirm the export, capture the browser download, and assert the
  `suggested_filename` contains "Bookings".
- **Download verification:** the page exports via a `data:` anchor download named
  `Bookings_<start>_to_<end>` (BookingsPage.vue `downloadFile`). Capturing the Playwright
  download and asserting the filename faithfully reproduces the legacy
  `Then "Bookings" downloaded` (which checked the latest download filename includes
  `getExpectedDownloadTitle("Bookings")`).
- **Selectors / label change:** the legacy clicked `[data-qa="vc-footer-Export"]`, but the
  current export dialog's OK button label is `booking.extract.extract` ("Extract"), so the
  primary action is `[data-qa="vc-footer-Extract"]` with a fallback chain
  (`vc-footer-Export`, then `role=button name=/Extract|Export/`) for resilience.
- **Waits:** export-icon, dialog and download-capture waits are all capped at 5s.
