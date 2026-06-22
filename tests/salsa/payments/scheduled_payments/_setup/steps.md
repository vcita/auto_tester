# Scheduled Payments Setup — Steps

Prepares an isolated account so the scheduled-payments test starts from a deterministic state.

1. Enable the payments checkout/gateway rollout feature flags (so the gateway providers UI and the redesigned scheduled-payments dialog render).
2. Log in to the isolated account.
3. Create one client (`first last<stamp>`) via API, with a unique last name so the Quick Actions client picker is deterministic.
4. Connect a mock payment gateway (enables checkout, which makes the Schedule payment quick action available).
5. Enable credit-card checkout via API (required before a card can be saved on file).
6. Save a credit card on file for the client (UI, via the mock gateway).

Saves to context: `sp_client`, `sp_client_id`, `sp_client_name`.
