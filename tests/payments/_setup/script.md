# Payments Setup - Detailed Script

## Overview
Login and create the client required by invoice picker flows.

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

- **Action**: Call function
- **Function**: create_client
- **Parameters**: first_name = `Appt`, last_name = `TestClient`

**VERIFIED PLAYWRIGHT CODE**:
```python
from tests._functions.create_client.test import fn_create_client
fn_create_client(page, context, first_name="Appt", last_name="TestClient")
context["invoice_client_search_term"] = context["created_client_name"]
```

- **Wait for**: Client profile URL after save
- **Context**: `created_client_id`, `created_client_name`, `created_client_email`, and `invoice_client_search_term`

---

## Success Verification
- Dashboard is visible after login
- Context contains `logged_in_user`
- Context contains `invoice_client_search_term`
