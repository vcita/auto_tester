# Script — CP Deny Payments Setup

Phase 2 (HOW). API-only.

```python
client = create_client(context, "first1", "last1", email)
context["cp_client_token"] = client["token"]
```
The portal token opens the client portal as the client (`?client_jwt=<token>`).
