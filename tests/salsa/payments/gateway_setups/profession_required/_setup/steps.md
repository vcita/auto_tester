# Setup: Wizard - profession required

Prerequisites for the profession-required wizard scenario (not the behaviour under test).

1. Enable the vcita-payments onboarding wizard feature flags before login.
2. Do NOT set a `business_category` (so the preliminary profession starts empty and the
   next button is disabled until it is filled).
3. Log in to the isolated account.
