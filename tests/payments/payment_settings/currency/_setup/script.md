# Script — Currency Setup

Phase 2 (HOW). API-only.

```python
service = create_service_via_api(context, "test service", charge_type="paid_force", price="100")
client = create_client(context, "first1", "last1", email)
```
`create_service_via_api` → `POST /v2/settings/services`; `create_client` →
`POST /platform/v1/clients`. Both stored on context for the scheduling steps.
