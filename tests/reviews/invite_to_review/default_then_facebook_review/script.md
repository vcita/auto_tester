# Default then Facebook Review — Script

Two surfaces: the client-portal review page + conversation (vitrage `cp_iframe`),
and the back-office POV reviews settings page. Setup creates the client (capturing
the portal JWT) and enables the reviews flags. All UI waits are condition-based and
capped at 5s; client-portal/settings page loads use a longer page-readiness budget,
and the conversation review bubble is polled up to 15s for realtime eventual
consistency (mirroring the legacy `operation_timeout` retry).

## Client portal (vitrage `cp_iframe`), via `reviews_cp_ui.py`

- Open review page: `{vitrage}/site/{pivot_uid}/activity/review?client_jwt=<token>`; ready `.review-page, .matter-indicator`.
- 5-star rating: `button[aria-label="Rating 5 of 5"]`.
- Feedback: `textarea`. Submit: `.submit-review-button`.
- Default submitted title: `.after-review-submit__title` (contains `Thanks for your review!`).
- Social submitted button: `.after-review-submit__rate-on-social-button` (contains the platform name).
- Conversation: reopen `{vitrage}/site/{pivot_uid}/action?client_jwt=<token>` (ready `.quick-actions, .matter-picker`), click chat `[data-qa="headerChatBtn"]`, poll review bubble `.review-bubble` for the text.

## Back-office reviews settings (POV `/app/settings/reviews`), via `reviews_settings_ui.py`

- Public reviews checkbox: `[data-qa="review-public-reviews-checkbox"] input[role="checkbox"]` (enabled if `aria-checked != true`).
- Platform select: `[data-qa="review-platform-select"]`; pick the `.v-list-item` option containing `Facebook`.
- Platform id input: `[data-qa="review-platform-id-input"] input` filled with `vcitainc`.
- Save: `[data-qa="review-settings-action-save"]`; save is confirmed by the 2xx
  `POST/PUT /v3/reviews/business_reviews_settings` response (no reload, so DOM alone
  would not prove persistence).

Page gating: the POV reviews page redirects to the dashboard without
`reviews_rollout` + `collect_reviews`, and keeps the fields disabled without
`enable_reviews_auto_publishing`; setup enables all three.

## Steps

1. **Default review** — `leave_review(page, context, "very good")`.
2. **Default submitted** — `assert_default_submitted(page)` (`Thanks for your review!`).
3. **Default in conversation** — `assert_review_in_conversation(page, context, "very good")`.
4. **Configure platform** — `set_review_platform(page, context, "Facebook", "vcitainc")`.
5. **Facebook review** — `leave_review(page, context, "still very good")`.
6. **Facebook submitted** — `assert_social_submitted(page, "Facebook")`.
7. **Facebook in conversation** — `assert_review_in_conversation(page, context, "still very good")`.

## Scope preservation vs legacy

- Both reviews are submitted through the UI (legacy `client leaves review ... in client portal`).
- Both submitted-page assertions kept (legacy `"default"` / `"Facebook"` review submitted page appears).
- The review platform is configured through the back-office UI (legacy `user selects review platform`), an in-scope UI action — not replaced by API.
- Both conversation review bubbles asserted (legacy `review message ... displayed in client portal conversation`).
- Client created via API (legacy `creates new client via API`); login via UI.
