# Card on File Setup — Steps

Prepares an isolated account so the card-on-file test starts from a deterministic state.

1. Enable the payments checkout/gateway rollout feature flags (so the redesigned add-payment-method dialog with the "Request card on file" segment renders).
2. Log in to the isolated account.
3. Create one client (`first last`) via API.
4. Connect a mock payment gateway (required before a card-on-file request can be sent).
5. Enable credit-card checkout via API (the "Request card on file" segment requires it).

Saves to context: `card_on_file_client`, `card_on_file_client_id`, `created_client_name`.
