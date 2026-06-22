# Packages (BO) Setup — Detailed Script

## Initial State
- Isolated account just created by the runner; credentials in context (`username`/`password`).

## Actions

### Step 1: Log in to the isolated account
- **Action**: Call function `fn_login` with the isolated-account credentials.
- **VERIFIED PLAYWRIGHT CODE**: `fn_login(page, context, username=username, password=password)`
- Reuses the proven login function (same pattern as cp_packages/_setup).

### Step 2: Connect the mock payment gateway (UI)
- **Action**: Call `connect_mock_gateway(page, context)`.
- Reuses `tests/salsa/payments/tips_settings/tips_gateway.connect_mock_gateway` (the shared
  mock-gateway UI setup used by cp_packages/coupons_checkout). The BO take-payment / POS /
  invoice-pay flows require a connected gateway.

### Step 3: Create 3 services via API
- **Action**: `create_service_via_api` three times (account_api).
- `service`  : suggest-to-pay appointment, $100, business_location ("blablablabla").
- `service2` : suggest-to-pay appointment, $100, business_location ("blablablabla").
- `r2p_event`: require-to-pay event, $1, business_location.
- Legacy payment mapping: "suggest to pay" -> charge_type=paid; "require to pay" -> paid_force.
- Stored in `context["packages_services"]` for the tests to build packages from.

## Success Verification
- Login succeeds, gateway connected, 3 service ids present in context.
