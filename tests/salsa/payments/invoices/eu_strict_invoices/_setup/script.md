# EU Strict Invoices Setup - Script

## Initial State
- Runner switched to an isolated auto account with `account_profile.country_name: Italy`.
- `context["auto_account"]`, `context["base_url"]`, and `context["api_base_url"]` are available.

## Actions

### Step 1: Log in
- Call the shared login function with `context["username"]` and `context["password"]`.
- Wait for the dashboard readiness signal from the login helper.

### Step 2: Create client via API
- POST `/platform/v1/clients` with the isolated account bearer token.
- Use first name `first`, last name `last`, and a generated email.
- Store the full name for the invoice picker.

### Step 3: Create paid service via API
- Fetch the last service category from `/platform/v1/categories`.
- Fetch the first staff member from `/platform/v1/businesses/{business_uid}/staffs`.
- POST `/v2/settings/services` with `charge_type: paid_non_secured`, `price: 100`, and `currency: USD`.
- Store service name and price for invoice creation.

## Success Verification
- Dashboard is reachable after login.
- API responses include a client id and service payload.
- Context contains the client and service keys needed by `refund_credit_notes`.
