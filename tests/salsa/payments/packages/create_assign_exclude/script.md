# Create + assign taxed package (exclude mode) — Detailed Script

All UI locator decisions live in `tests/salsa/payments/packages/packages_helpers.py` (the
shared BO package helpers), reused across the 9 subtests. This script maps each step to the
helper call that performs the verified UI action.

## Initial State
- Logged in to the isolated account; mock gateway connected; `service`/`service2`/`r2p_event`
  created in setup (in `context["packages_services"]`).

## Actions

### Step 1: Create two taxes (API prerequisite)
- `create_tax_via_api(context, "TS<seq>", "13")`, `create_tax_via_api(context, "TS 2<seq>", "13.13")`.
- Taxes are an account prerequisite (not the behavior under test) → API.

### Step 2: Create a fresh client (API prerequisite)
- `make_client(context, seq)` → returns client with `id` and portal `token`.

### Step 3: Create package via UI (Settings/Packages)
- `create_package(page, context, name="package", service_name="service", amount="2",
  price="150", package_type="specific", taxes=[{name:TS, rate:13}])`.
- LOCATOR DECISION (in helper): name `#package_name`; service md-autocomplete; credits
  `name='dummyServiceQuantity'`; price `name='packagePrice'`; tax flow `.link-part` +
  `[data-qa='tax-<name>-<rate>']`; save `[data-qa='action-button-package-save']` (legacy verbatim).

### Step 4: Assign package via the client card UI
- `assign_package_via_client_card(page, context, client_id, package_name="package",
  taxes=[TS, TS 2])`.
- LOCATOR DECISION (in helper): client-card Payments new-payment menu
  `.add-payment-btn-desktop button` -> `[data-qa='packages']`; dialog picker
  `[data-qa='package-select-input']`; taxes `[data-qa*='tax_assigned']` + tax options; Add
  `[data-qa='vc-footer-Add']` (legacy verbatim).

### Step 5: Assert client-package payment request (BO card)
- Resolve id via `get_client_package_id`, then `assert_client_package(...)`:
  state `DUE`, amount `$189.20 ($150.00 + Tax)`, client `first last`, package `package`.
- Card reads from `div.status-payment` / `div.balance-due-amount` / header (legacy verbatim).

### Step 6: Assert CP conversation title
- `assert_cp_conversation_title(page, context, token, "Package added: package")`.
- Opens the authenticated CP, clicks `[data-qa='headerChatBtn']`, reads `[data-qa='bubble-header']`.

## Success Verification
- Client-package DUE $189.20 (150 + 13% + 13.13%) and CP conversation shows "Package added: package".
