# Setup: Wizard - populated profession

Prerequisites for the populated-profession wizard scenario (not the behaviour under test).

1. Enable the vcita-payments onboarding wizard feature flags
   (`vcita_payments_preliminary_step`, `vcitaPayments_wizard`,
   `merchant_vcita_payments_onboarding_wizard`) before login.
2. Set the business `business_category` to `legal_services` (the source of the
   prepopulated profession).
3. Log in to the isolated account.
