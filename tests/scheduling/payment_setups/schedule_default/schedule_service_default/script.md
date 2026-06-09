# Schedule Service Default — Script

Migrated from `payment-setups.feature` scenario "Schedule service default".

## Flow

1. **Setup (`_setup/test.py`)** — create client `first1 last1` via API, log in, connect the
   mock payment gateway. The gateway is a prerequisite (not under test): "require to pay"
   only renders its price/"required" type when an online payment method is connected. A
   bare isolated account shows a "No payment method" warning and drops require-to-pay.

2. **Create six services via the UI** (`payment_setups_ui.create_service_ui`):
   - Open the New-service dialog (`_open_new_service`): navigate to
     `/app/settings/services`, wait for the "Settings / Services" heading (cold SPA module
     load → 20s bounded), click **New service**, pick **1 on 1 appointment**. Retries the
     open up to 3x (Angular split-button handler binds late on cold load).
   - Fill the service name, set Face-to-face → Other address (fresh account has no business
     address), click `no-fee`, then route to the advanced editor
     (`saveNewService("advanced")`).
   - In the advanced editor pick the payment type from the price dropdown
     (`div.service-price md-select-value`) by its option label (`EDITOR_OPTION`), and fill
     the price (`div.service-price div.paid-service input`) for the three paid types. Save.

   | service     | payment_setting    | editor option                          | price |
   |-------------|--------------------|----------------------------------------|-------|
   | require2pay | require to pay     | Paid - Require to pay at booking       | 100   |
   | suggest2pay | suggest to pay     | Paid - Suggest to pay at booking       | 50    |
   | displayFee  | display a fee      | Paid - No online payment at booking    | 10    |
   | variedPrice | display for a fee  | Price varies - Display as "For a fee"  | —     |
   | displayFree | display free       | Free - Display as "Free"               | —     |
   | noDisplay   | dont display       | Free - Don't display a fee             | —     |

3. **Verify the services list** (`assert_service_details`, reads the rendered row text):
   - require2pay → `$100`, suggest2pay → `$50`, displayFee → `$10`,
     variedPrice → `For a fee`, displayFree → `Free`, noDisplay → no `$`.

4. **Schedule an appointment for each service** (`multistaff_helpers.schedule_appointment`)
   for `first1 last1`, then read the meeting price (`read_meeting_price`):
   - require2pay → 100, suggest2pay → 50, displayFee → 10,
     variedPrice → blank, displayFree → Free, noDisplay → blank.

## Locator decisions

- **New-service option label** — `getByRole("menuitem", name=/1 on 1 appointment/)` (legacy
  `appointmentOption`). The shared `goto_services` waits for a category card, which a fresh
  account lacks (only "+ Add category"); the local `_open_new_service` waits for the heading
  + New-service button instead, since the first service auto-creates "My Services".
- **Payment dropdown** — `div.service-price md-select-value` + `getByRole("option", name=…)`
  (legacy `serviceEditor.paymentTypeDropdown`). JS click on md-select/md-option per the
  Angular click guidance.
- **Meeting price** — `[data-qa="appointment-free"]` → "Free", else `[data-qa="balance-due-amount"]`
  (legacy `getBOMeetingDetails`).

## Verified

- 2026-06-09: focused run PASSED (2/2). require2pay shows `$100`/`required` only with the
  mock gateway connected; without it the list/meeting price are blank.
