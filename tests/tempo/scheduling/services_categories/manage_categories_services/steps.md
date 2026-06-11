# Categories & services management (manage_categories_services)

Migrated from `automation-js/features/tempo/ServiceSetups/categories-and-services.feature`
(VCITA2-13993), the single scenario "categories and services - create, rename, move,
clone and delete". All actions run on the Services index settings page (Angular frontage
iframe). Category cards list their service rows in order; assertions compare the full
category→service mapping (order-sensitive), mirroring the legacy `search categories`
table, plus the `search services` payment/price/attendees checks.

Prerequisite (from `_setup`): logged in on a fresh account whose `My Services` category
holds the three default services.

## WHAT the test verifies (legacy behaviour note: a new service is placed above the default services)

1. **Create category** `category_one` → mapping: `My Services` = [Demo class / event,
   In-office appointment, Introductory phone call], `category_one` = [].
2. **Create services** — a require-to-pay event `r2p_event` ($100, 10 attendees, lands in
   `My Services` above the defaults) and a don't-display-fee 1-on-1 `Gong` inside
   `category_one`. Verify `r2p_event` shows `$100` + `10 attendees`, `Gong` shows
   `1 on 1` and no price.
3. **Move a service** — edit `In-office appointment` into `category_one` → `My Services`
   = [r2p_event, Demo class / event, Introductory phone call], `category_one` =
   [Gong, In-office appointment].
4. **Rename category + delete service** — rename `category_one`→`New_name`, delete
   `Introductory phone call` → `My Services` = [r2p_event, Demo class / event],
   `New_name` = [Gong, In-office appointment].
5. **Reorder + rename service** — move `New_name` up, rename `In-office appointment`→
   `service_one` → `New_name` = [Gong, service_one], `My Services` =
   [r2p_event, Demo class / event].
6. **Clone service** — clone `service_one` → `New_name` = [Gong, service_one,
   Copy of service_one], `My Services` = [r2p_event, Demo class / event].
7. **Delete category** — delete `My Services`; its services merge to the end of
   `New_name` → `New_name` = [Gong, service_one, Copy of service_one, r2p_event,
   Demo class / event].

## In scope (UI) vs prerequisite (API)

- UI (in scope): every category and service create/edit/move/rename/clone/delete and all
  mapping / payment-detail assertions on the Services settings page.
- API (prerequisite, in `_setup`): account creation + login only.
