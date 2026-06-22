# CP Scheduling With Taxes — Script

Migrated from `payment-setups.feature` scenario "CP Scheduling with taxes".

## Flow

1. **Setup (`_setup/test.py`)** — create a default-for-services 10% tax via API
   (`payment_setups_api.create_tax`), create the `suggest2pay` service ($100, suggest to pay)
   with that tax attached (`account_api.create_service_via_api(tax_uids=[...])`), and log in to
   the business (needed to grab the public link).

2. **Grab the service public link** (`cp_scheduling_helpers.grab_service_link`) — services
   settings, the service row 3-dot menu → "Copy public link", read the http link from the
   "Copy link to share publicly" dialog.

3. **Open the link anonymously** (`open_scheduler`) — the public livesite embeds the client
   portal in the `cp_iframe`; a single-service link opens straight to the scheduler calendar.

4. **Assert the calendar booking summary** (`assert_calendar_summary`) — service `suggest2pay`,
   tax `+Tax`, price `$100.00`.

5. **Book** (`book_appointment`) — pick the default timeslot, continue, fill the intake form
   (first name `jimmy`, an email), confirm; the `ConfirmBooking` page is the success signal.

6. **Open the meeting page** (`open_meeting`) — from the post-booking session, click the
   dashboard button, open the bookings menu, select the `suggest2pay` booking.

7. **Assert the meeting page** (`assert_meeting`) — meeting `suggest2pay`, price `$100.00`,
   tax `+Tax`.

## Locator decisions

- **Copy-link dialog** — the URL is no longer a `.link-container__link` span; the current
  "Copy link to share publicly" dialog can mount at any nesting level, so the helper scans
  every frame for the http link (text element or readonly input value).
- **CP frame** — `cp_iframe` (preferred by name), falling back to scanning all frames for the
  expected selector, since the livesite shell nests the portal differently across pages.
- **Calendar summary** — `.service-section` / `.tax` / `.service-summary-container .price`
  (legacy `calendar.js` booking-summary elements).
- **Intake** — `.scheduling-intake-form[data-qa="SchedulingIntakeForm"]`, email
  `input[type=email]`, first name by adjacent label, confirm `.submit-button span,
  .summary-card__cta`.
- **Meeting page** — `.booking-title` / `.booking-detail .price` / `.tax`; the rendered price
  is `$100.00` (the `$` conveys USD — the legacy `m_currency=USD` is the formatter input, not
  literal page text).

## Verified

- 2026-06-09: focused run PASSED (2/2), body ~36s.
