# Setup: cp_packages (isolated account)

## Objective
Create the account-level prerequisites shared by both cp_packages tests, mirroring the
Background of automation-js features/salsa/cp/packages.feature.

## Steps
1. Log in to the isolated account (UI entry-point login).
2. Connect the mock payment gateway (UI) so checkout/purchase is enabled.
3. Create 3 services via API:
   - r2p_appointment: appointment, "require to pay" (paid_force), f2f_other
     (business_location, "tlv12"), price 1.
   - s2p_appointment: appointment, "suggest to pay" (paid), business_phone
     ("1 202 222 2222"), price 1.
   - r2p_event: event, "require to pay" (paid_force), no location, price 1.
4. Create 2 packages via API:
   - package1: offers r2p_appointment + s2p_appointment + r2p_event, 1 credit, price 150,
     expires 2 weeks, type any.
   - package2: offers s2p_appointment, 2 credits, price 150, expires 6 months, type any.
## Context produced
- `cp_packages_services` = {r2p_appointment, s2p_appointment, r2p_event} dicts (id/name/price/currency)
- `cp_packages_packages` = {package1, package2} dicts (id/name/price)

The client is NOT created in setup: each test creates its OWN client via API (the legacy
Background runs per scenario). Test 1 purchases packages and test 2 assigns packages, so a
shared client would accumulate both tests' packages and break the assertions.

## Notes
- Payment-type mapping is the legacy source of truth (api/service.js _setPaymentType):
  require to pay -> paid_force, suggest to pay -> paid.
- All prerequisites are created via API except the mock gateway (UI), which has no
  reliable API equivalent and is a setup prerequisite, not the behavior under test.
