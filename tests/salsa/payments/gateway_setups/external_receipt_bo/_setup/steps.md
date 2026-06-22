# Setup: External receipt - back office

Prerequisites for the back-office external-receipt scenario (not the behaviour under test).

1. Deny the `point_of_sale` feature flag (before login) so Quick Actions exposes the
   legacy Record payment dialog rather than the POS flow.
2. Log in to the isolated account.
3. Create the `simon bolivar` client via API.
4. Assign the `mockreceipts` external-receipt app to the business via API, so recorded
   payments expose an external "View receipt" link.
