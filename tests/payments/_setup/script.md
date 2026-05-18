# Payments Setup - Detailed Script

## Overview
Login, create the client required by invoice picker flows, and create a paid service via API for invoice line items.

## Prerequisites
- vcita account credentials configured

---

## Step 1: Login

- **Action**: Call function
- **Function**: login
- **Parameters**: username, password from config

**VERIFIED PLAYWRIGHT CODE**:
```python
from tests._functions.login.test import fn_login
fn_login(page, context, username=username, password=password)
```

- **Wait for**: Dashboard loads
- **Context**: `logged_in_user` saved by login function

---

## Step 2: Create Invoice Picker Client

- **Action**: POST `/platform/v1/clients` with the auto account Bearer token.
- **Reason**: Avoid the full Add Matter UI setup path; invoice tests only need a selectable existing client.
- **Parameters**: first_name = `Appt`, last_name = `TestClient`, generated test email

**VERIFIED PLAYWRIGHT CODE**:
```python
_create_invoice_picker_client(context)
```

- **Context**: `created_client_id`, `created_client_name`, `created_client_email`, and `invoice_client_search_term`

---

## Step 3: Create Required-Payment Service Via API

- **Action**: POST `/v2/settings/services` with the auto account Bearer token.
- **Reason**: Mirrors automation-js `user creates new service via API`; invoice tests should select a real paid service instead of relying on `$0.00` default services or UI-created custom items.
- **Payload highlights**:
  - `charge_type`: `paid_force`
  - `price`: `100`
  - `currency`: `USD`
  - `service_type`: `appointment`

**VERIFIED PLAYWRIGHT CODE**:
```python
_create_required_payment_service(context)
```

- **Context**: `invoice_service`, `invoice_service_name`, and `invoice_service_price`

---

## Success Verification
- Dashboard is visible after login
- Context contains `logged_in_user`
- Context contains `invoice_client_search_term`
- Context contains `invoice_service_name`
