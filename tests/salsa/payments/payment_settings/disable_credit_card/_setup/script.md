# Script — Disable Credit Card Setup

Phase 2 (HOW).

```python
fn_login(page, context, username=..., password=...)
client = create_client(context, "first1", "last1", email)
context["cc_client_email"] = email
```
