# Changelog — services_categories / manage_categories_services

## 2026-06-08 — Initial migration (VCITA2-13993)

Migrated `automation-js/features/tempo/ServiceSetups/categories-and-services.feature`
(1 scenario) into auto_tester as the isolated subcategory
`scheduling/services_categories`.

- **Setup (UI):** log in to a fresh isolated account, open `/app/settings/services`,
  verify the three default services are present.
- **Test (UI):** full categories-and-services management on the Services index page —
  create a category; create a require-to-pay event service ($100, 10 attendees) and a
  don't-display-fee 1-on-1 service inside a category; move a service between categories;
  rename / move-up / delete categories; delete / rename / clone services. Asserts the
  ordered category→service mapping at every stage and the event service's
  price/attendees + the 1-on-1 service's `1 on 1` / no-price display.
- **Selectors:** mirror the current legacy page objects (`servicesSettings.js`,
  `serviceEditor.js`) — `data-qa="newCategory"`, `[name=category_name]`,
  `md-card[data-qa="services-category-container"]`, `.header-titles .title`,
  `.header-actions md-icon[aria-label="icon-arrow-up-s"|"icon-menu-s"]`,
  `div.list-item:not(.main-actions)`, `.titles .title`, `md-checkbox[ng-model~=
  'newService.require_to_pay']`, `button[data-qa=no-fee]`, the advanced-create button,
  and the editor category dropdown (`.settings-input-container .md-text`) — plus verified
  role/text selectors from the existing stable services tests (New service menu, dialog
  fields, editor name/Save, `icon-pencil-s`, Ok confirm).
- **Decisions:**
  - Isolated account so the three defaults + ordering assertions are deterministic.
  - Each action re-enters the services page (mirrors the legacy page object) so reads
    see a freshly rendered list; reads scroll the endless-scroll list until the
    category-card count stabilises.
  - Angular-Material menus / md-select / md-checkbox / category move-up use JS clicks
    (overlays intercept the standard click — project Angular click guidance).
  - New services set an explicit "Other address" because a fresh account has no business
    address (the default radio would fail validation), matching the legacy default.
  - `delete_service` deletes via the service editor's Delete button (verified in the
    existing delete_service test) instead of the row 3-dot menu — same in-scope action
    (service removed), lower selector risk.
  - `assert_service_details` checks the rendered row tokens (`$100`, `10 attendees`,
    `1 on 1`, no `$`) rather than re-implementing the brittle legacy field parser,
    preserving the `search services` assertion intent.

### Wait audit
- No fixed `sleep`-as-synchronization. `goto_services` and every action wait on explicit
  conditions (heading, category card, dialog, menu item, editor name field, URL change).
- `SETTLE_MS` (300ms) is used only as a brief post-mutation settle before the next
  re-navigation/read and between endless-scroll steps — not as a substitute for a state
  wait. The event-times dialog dismissal uses a bounded 3s `wait_for` that is expected to
  time out when the dialog does not appear.
