# Script: redeem_and_repurchase

Same frame/wait policy as purchase_packages. Implemented in
`tests/salsa/payments/cp_packages/cp_packages_helpers.py`. The test creates its OWN client
(`make_client`) and authenticates the CP session (`open_portal` visits `/action?client_jwt`).

### Step 1: Assign packages via API
- `assign_package_to_client(context, client_id, package1_id, price)` and same for package2
  (POST /platform/v1/payment/client_packages, legacy validity window).

### Step 2: Navigate to purchased-packages
- `navigate_purchased_packages` → dashboard `/action?client_jwt`, click the side menu
  `[data-qa='client-area-menu-client_packages']`, wait for `.client-packages-list-page` + a card.

### Step 3: Start scheduling from package1
- `start_scheduling_from_package("package1")` → within `[data-qa$='package-package1']` click
  `[data-qa='client-package-schedule']`.

### Step 4: Services page shows the package's services
- `assert_scheduler_services(["r2p_appointment", "s2p_appointment"])` → read
  `[data-qa="ServiceCategoryPage"] .service-item` titles `span.service-title[data-style-id]`,
  compare sorted. (r2p_event is an event, not offered as a bookable appointment service.)

### Step 5: Schedule an r2p_appointment
- `schedule_appointment("r2p_appointment")` → click the service item, pick first
  `button.time-slot`, click continue (`.submit-button span, .summary-card__cta`); if the
  intake `.scheduling-intake-form[data-qa="SchedulingIntakeForm"]` shows without a
  confirmation, click continue again (the known client's details are prefilled).

### Step 6: Booking confirmation
- `assert_booking_confirmation(title="Confirmed!", redeemed_with_package=True)` →
  `[data-qa="ConfirmBooking"]` present, title `.text-container span.confirmation-title`
  contains "Confirmed!", `.package-info-wrap` present (redeemed-with-package).

### Step 7: Purchased-packages after redemption
- `assert_purchased_packages` expected: package2 0/2 [s2p_appointment] active; package1 1/1
  [r2p_appointment, s2p_appointment, r2p_event] state "fully" (fully_redeemed). The
  fully_redeemed card renders under `[data-qa|='inactive-package']` and the inactive section
  lags the active one by a render cycle, so the helper polls/scrolls until the expected card
  count renders (NAV budget) before reading. Verified independently: the redeem sets the
  package to bookings_usage 1 / total_bookings 1 via the client_packages API.

### Step 8: package1 history dialog
- `open_history_dialog("package1")` → within the package1 card click
  `[data-qa='client-package-view-history']`, wait `.v-dialog`; `assert_history_has_service`
  checks usage items `[data-qa^=usage-item-]` names `[data-qa^=usage-][data-qa$=-title]`
  contain r2p_appointment. The legacy `appointment_date: default` (dynamic timeslot string)
  is intentionally not re-derived (see changelog). `close_history_dialog` clicks `.close-icon`.

### Step 9: Re-purchase from the finished package
- `navigate_purchased_packages`, then
  `start_repurchase_from_package("package1", package1_id, token)` → within the package1 card
  click `[data-qa='client-package-buy-again']`; assert the description page (fallback: open
  package1 from the list). `assert_description_page("package1")`.

### Step 10: Purchase with a new card
- `purchase_package(new_card=True)` (mock-gateway popup).

### Step 11: Purchased-packages after re-purchase
- `assert_purchased_packages` expected: package1 0/1 [...] active; package2 0/2
  [s2p_appointment] active; package1 1/1 [...] fully (the fully_redeemed copy, inactive section).
