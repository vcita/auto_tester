# Setup Script — Calendar Settings

Isolated-account setup. Logs in as the account owner; no API fixtures are created here.

## Step 1: Log in to the isolated account

VERIFIED PLAYWRIGHT CODE:

```python
fn_login(page, context, username=context["username"], password=context["password"])
```

The isolated account owner is an admin (has `can_access_settings` and
`can_access_staff_management`), which both scenarios depend on for the owner view.
