# Changelog — Default then Facebook Review

## 2026-06-01 — Initial migration (VCITA2-13759)

Migrated `automation-js/features/tempo/reviews.feature` scenario 1
(*Set review settings and invite client to review*) to auto_tester as the new
`tests/reviews` category.

- New category `tests/reviews` with isolated subcategory `invite_to_review`.
- Setup: isolated account, reviews flags enabled, client created via API (capturing
  the client-portal JWT token).
- Test: client leaves a default review (assert `Thanks for your review!` + conversation
  bubble), business configures the Facebook platform, client leaves a second review
  (assert the Facebook social button + conversation bubble).
- Reused the offset_fees client-portal patterns (`cp_iframe` resolution, vitrage base);
  added a shared `tests/account_api.create_client` that captures the portal token.
- Replaced legacy fixed waits with condition-based waits (≤5s) and a 15s realtime poll
  for the conversation review bubble; settings save confirmed via the
  `/v3/reviews/business_reviews_settings` response.
