# Script: Grab and Access Scheduler Links

Implemented in `service_link_helpers.py`. Reuses
`payment_setups/cp_scheduling_helpers.grab_service_link` for the general link.

## Frames

- Services settings (general grab): `iframe[title="angularjs"]` (row 3-dot menu) + Vue
  `[data-qa="vc-input-modal"]`.
- Client-portal scheduler: `#cp_iframe` (scanned across frames via `cp_frame_with`).

## Actions

1. `grab_general_service_link(page, service, app_base)` — return to `app_base/app/settings/services`
   (after a live link the page is on the live-site host), then reuse `grab_service_link`.
2. `assert_staff_select(page, [business, staff])` — `[data-qa="StaffSecondSelection"]` +
   `.staff-details .display-name`.
3. `derive_staff_scoped_link(general_link, staff_uid)` — `<base>/online-scheduling?staff=<uid>`;
   `access_link` then `assert_calendar` (`.service-section` + `.staff-section span`).
4. `delete_staff_api` then re-access general link + `assert_calendar` (business).
5. `delete_service_api` (DELETE `/v2/settings/services/{uid}`) then re-access general link +
   `assert_services_page` — `[data-qa="ServiceCategoryPage"] .service-item`,
   `span.service-title[data-style-id]`, `.service-details span`.

## Waits

- `UI_TIMEOUT` 10s for CP elements (matches sibling), `NAV_TIMEOUT` 20s for back-office nav +
  live-site portal loads. No fixed sleeps (bounded frame-scan polling only for cp_iframe nesting).
