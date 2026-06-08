# Script — Terms and Policies Setup

Phase 2 (HOW).

```python
fn_login(page, context, username=..., password=...)
connect_mock_gateway(page, context)  # reused from tips_settings.tips_gateway
```
`connect_mock_gateway` opens `/app/settings/payments`, reveals providers, connects the
mock provider via the external popup, and saves (proven, stable helper).
