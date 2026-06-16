# Setup: CP Follow-up Tip

Mirrors tips.feature scenario "take followup tip in cp" Background + prerequisites.

1. Enable tips feature flags.
2. Assign the `tips` app (Admin auth).
3. Set tip options `55,66,77` + enable tips for CP (POST /platform/v1/payment/settings, read-back).
4. Create client `first last` (keep its portal token for the CP action).
5. Create require-to-pay service `require` ($100) and suggest-to-pay service `suggest` ($50).
6. Schedule a past appointment for each service for `first last`
   (`require` previous month day 10, `suggest` previous month day 20).
7. Record a $100 Cash payment for the `require` meeting via API so it is fully paid
   (prerequisite for the CP "Add a tip" follow-up action).
8. Log in to the back office.
9. Connect the mock payment gateway via the providers UI (required for the CP tip checkout).
