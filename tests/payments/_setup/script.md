# Payments Setup - Detailed Script

## Overview
Login to prepare for payments tests.

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

## Success Verification
- Dashboard is visible after login
- Context contains `logged_in_user`
