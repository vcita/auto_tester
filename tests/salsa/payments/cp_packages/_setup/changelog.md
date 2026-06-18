# Changelog: cp_packages/_setup

## 2026-06-18 - Created (migration VCITA2-14229)
**Phase**: steps.md, test.py
**Author**: Cursor AI (migrate)
**Reason**: Migrate the Background of automation-js features/salsa/cp/packages.feature.
**Details**:
- Login (UI), connect mock gateway (reuse tips_gateway.connect_mock_gateway).
- Create 3 services via `create_service_via_api` (extended with service_type /
  interaction_type / meeting_interaction_details / duration). Payment-type mapping per
  legacy api/service.js `_setPaymentType`: require to pay -> paid_force, suggest to pay
  -> paid. (Prompt suggested suggest-to-pay = paid_non_secured; that is the "display a
  fee" mapping, so the legacy `paid` is used as the source of truth.)
- Create package1 (all 3 services, 1 credit, $150, 2w) + package2 (s2p, 2 credits, $150,
  6m) via `create_package_via_api`.
- Client is created per test (not in setup): each test calls `make_client` so test 1's
  purchases and test 2's assignments do not accumulate on one shared client.
- Shared-file edit: `tests/account_api.py::create_service_via_api` extended (backward
  compatible defaults) to support events/location-typed services, and now returns
  price/currency so package items can reference the service.
