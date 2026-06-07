# Setup: CP Pay-link With Tips

Mirrors tips.feature scenario 3 Background + prerequisites (client-portal, mock gateway).

1. Enable tips feature flags.
2. Assign the `tips` app (Admin auth).
3. Set tip options `55,66,77` + enable tips for CP (POST /platform/v1/payment/settings, read-back).
4. Create suggest-to-pay service `service` ($100).
5. Create client `first last` (keep its portal token for the CP close-balance action).
6. Schedule a past appointment (previous month, day 10) for `first last` so it has a
   payable CP balance (used by the close-balance action).
7. Log in to the back office.
8. Connect the mock payment gateway via the providers UI (required for CP checkout).
