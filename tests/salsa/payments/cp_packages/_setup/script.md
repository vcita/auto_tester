# Script: cp_packages/_setup

All steps are API except the login and mock-gateway connection (UI). Implemented in
`tests/salsa/payments/cp_packages/_setup/test.py`.

### Step 1: Login
- `fn_login(page, context, username, password)` (isolated-account credentials).

### Step 2: Connect mock gateway
- `connect_mock_gateway(page, context)` (reuse tips_settings/tips_gateway): open
  Settings/Payments providers, reveal + connect the mock provider via its popup, save.

### Step 3: Create services (API)
- `create_service_via_api(context, "r2p_appointment", charge_type="paid_force", price="1",
  service_type="appointment", interaction_type="business_location",
  meeting_interaction_details="tlv12")`
- `create_service_via_api(context, "s2p_appointment", charge_type="paid", price="1",
  service_type="appointment", interaction_type="business_phone",
  meeting_interaction_details="1 202 222 2222")`
- `create_service_via_api(context, "r2p_event", charge_type="paid_force", price="1",
  service_type="event", interaction_type="business_location",
  meeting_interaction_details="")`
- Stored in `context["cp_packages_services"]`.

### Step 4: Create packages (API)
- `create_package_via_api(context, "package1", services=[r2p_appointment, s2p_appointment,
  r2p_event], total_bookings=1, price=150, expiration="2", expiration_unit="w")`
- `create_package_via_api(context, "package2", services=[s2p_appointment], total_bookings=2,
  price=150, expiration="6", expiration_unit="m")`
- Stored in `context["cp_packages_packages"]`.

### Client creation (per test, not in setup)
- Each test calls `make_client(context)` (helper wraps `create_client` with a unique
  `test6+<ts>@vmeetme.com` email) and uses the returned client-portal token. The legacy
  Background creates a client per scenario; sharing one across both tests would mix
  test 1's purchased packages with test 2's assigned packages.
