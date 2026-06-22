# Setup: POS Payment With Tips

Mirrors tips.feature scenario 2 Background + prerequisites. Same seed as the BO
scenario but **point_of_sale stays enabled** so Quick Actions exposes the POS
(Take payment) large action.

1. Enable tips feature flags (`rollout.payments.tips_settings`, checkout/follow-up flags).
2. Assign the `tips` app (Admin auth).
3. Set tip options `55,66,77` + enable tips for BO (POST /platform/v1/payment/settings, read-back).
4. Create client `first last`.
5. Create suggest-to-pay service `service` ($100).
6. Create specific package `package` (2x service, $150) and assign to the client.
7. Schedule a past appointment (previous month, day 10) so service + package are payable.
8. Log in LAST so the Account model loads tips (showTips depends on Account.settings).
