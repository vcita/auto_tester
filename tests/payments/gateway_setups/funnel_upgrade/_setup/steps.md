# Setup: Wizard - funnel v1 upgrade

Prerequisites for the funnel-v1 upgrade wizard scenario (not the behaviour under test).

1. Enable the vcita-payments onboarding wizard feature flags plus the payment funnel-v1
   flags (`vp_payment_conversion_one`, `payment_gateways_disabled`) before login.
2. Set the business `business_category` to `legal_services` (matches the legacy row).
3. Log in to the isolated account.
