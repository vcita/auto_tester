# Setup: CP Service Link

Mirrors the legacy `features/tempo/CP/service-link.feature` Background.

## Steps

1. Log in to the isolated account.
2. Resolve the business owner staff (display name = legacy "Automation test business").
3. Create a staff member "staff" via API.
4. Create a service "service" via API, provided by both the owner and the new staff (so the
   general scheduler link offers two providers → staff-select page).
