# Reviews Invite Setup — Steps

Prepares an isolated account so the review test starts from a deterministic state.

1. Enable the reviews feature flags (`reviews_rollout`, `collect_reviews`,
   `enable_reviews_auto_publishing`) so the POV reviews settings page renders with
   enabled fields.
2. Log in to the isolated account.
3. Create one client (`first last`) via API, capturing the client-portal JWT token
   used to open the portal as that client.

Saves to context: `review_client` (with `token`), `created_client_name`.
