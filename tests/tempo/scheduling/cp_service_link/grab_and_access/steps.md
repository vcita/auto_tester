# Grab and Access Scheduler Links

Migrates automation-js `features/tempo/CP/service-link.feature` scenario
`Grab and Access scheduler links` (full file, single scenario). Sequential steps.

## Preconditions

- Logged in to the isolated account; service "service" provided by the business owner +
  one staff "staff" (setup).

## Steps

1. Grab the general public link of "service" (services-row "Copy public link").
2. Access the general link (anonymous): the CP scheduler staff-select page lists the
   business and "staff".
3. Access the staff-scoped link (same scheduler, scoped to "staff"): the CP scheduler
   calendar shows the service and "staff".
4. Delete the staff via API; access the general link: the calendar now shows the business.
5. Delete the service via API; access the general link: the scheduler services page shows
   the default services (In-office appointment / 1 hour, Introductory phone call / 30 min).

## Expected results

- The general link offers both providers (staff-select), the staff-scoped link opens on the
  chosen staff's calendar, then falls back to the business after staff deletion, and to the
  default services list after the service is deleted.

> The staff-scoped link is derived from the grabbed general link's portal base (see
> `changelog.md` — the current Link Builder UI is a crash-prone, structurally-changed editor
> flow); access and all assertions remain through the UI.
