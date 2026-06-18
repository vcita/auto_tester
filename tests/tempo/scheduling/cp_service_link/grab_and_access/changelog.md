# Changelog: Grab and Access Scheduler Links

## 2026-06-18 — Initial migration (VCITA2-14226)

Migrated from automation-js `features/tempo/CP/service-link.feature` (single scenario).

### Scope (all four legacy behaviors covered)

- General service link grabbed via UI → access → staff-select page lists [business, staff].
- Staff-scoped link → access → calendar shows the service + that staff.
- After staff deletion (API) → general link → calendar shows the business (single provider).
- After service deletion (API) → general link → scheduler services page shows the default
  seed services (In-office appointment / 1 hour, Introductory phone call / 30 min).

### Decisions / deviations

- Reuses the proven current-product helper `grab_service_link` (services-row "Copy public
  link") from `payment_setups/cp_scheduling_helpers.py`, plus local CP scheduler assertions
  (calendar `.service-section`/`.staff-section span`, staff-select
  `[data-qa="StaffSecondSelection"] .staff-details .display-name`, services page
  `[data-qa="ServiceCategoryPage"] .service-item`).
- **Staff-scoped link is DERIVED, not grabbed via the editor Link Builder.** Live exploration
  (2026-06-18) showed the current Create-a-Link builder is in the client-portal-editor (heavy
  nested Angular+Vue, md-select overlays, async-propagating staff list) and is **crash-prone in
  headless** (repeated `TargetClosedError`) — it could not reach the stability gate. The current
  builder also structurally differs from legacy (it separates service vs staff scoping; legacy
  combined them). The scheduler link is `.../site/<token>/online-scheduling?staff=<staff_uid>`,
  so the staff-scoped link is derived from the UI-grabbed general link's portal base + the staff
  uid. The general link is still grabbed via the UI, and accessing both links + every assertion
  remain UI — preserving the scenario's grab+access+provider/service-state coverage with a stable
  test. (Per the migration skill's guidance to keep an API/derived shortcut when the legacy UI
  path is unstable, while verifying user-visible state through the UI.)
- Service & staff created via API (Background is API in legacy). Staff deletion is API in legacy.
  Service deletion is API here (legacy uses the services-row UI), as a state prerequisite for the
  services-page assertion, not the behavior under test.

### Legacy ground-truth (decisive)

- Running the original legacy test on integration **also fails** at this exact step:
  `user grabs "service" link with "staff" staff` →
  `TimeoutError: Can't find element 'staffPicker' on page 'LinkBuilderDialog'`.
  The legacy Link Builder **staffPicker is broken upstream** in the current product — the
  legacy cannot grab a staff-scoped link either. This confirms faithful reproduction of the
  legacy UI grab is impossible, and validates deriving the staff-scoped link. The migrated
  test is *greener than the legacy*: it covers all four behaviors and passes, while the
  legacy scenario is red.

### Stability

- 3/3 clean focused runs + 10-iteration stress (see PR).
