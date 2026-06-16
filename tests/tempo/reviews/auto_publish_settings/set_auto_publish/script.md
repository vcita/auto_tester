# Set Auto-publish Setting — Script

Two surfaces: the back-office POV reviews settings page and the client-portal review
page (vitrage `cp_iframe`). The business lives in a directory with an external review
site (`vcita`), so the auto-publish UI is available and is configured here. All UI
waits are condition-based and capped at 5s; page loads use a longer page-readiness
budget. Each settings step re-opens the page so assertions read persisted state
(no reload otherwise, so DOM alone would not prove persistence).

## Login
- `fresh_login(page, context, username=<business email>, password=<business pw>)` — clears
  cookies + localStorage/sessionStorage, then `fn_login`. Required because the runner reuses
  one browser context across the subcategory; without a clean slate POV keeps the previous
  test's staff session and resolves the wrong business (no review site).

## Back-office (POV `/app/settings/reviews`), via `reviews_settings_ui.py`
- `set_review_platform(page, context, "Facebook", "vcitainc")` (reused from scenario 1):
  enable public reviews `[data-qa="review-public-reviews-checkbox"]`, select Facebook in
  `[data-qa="review-platform-select"]`, fill `[data-qa="review-platform-id-input"]`, and
  save — save is confirmed by the 2xx `POST/PUT /v3/reviews/business_reviews_settings`.
- `toggle_auto_publish_and_save(page, context)`: re-open settings, force-click
  `[data-qa="reviews-settings-auto-publish-checkbox"] input[role="checkbox"]` until
  `aria-checked=true`, then save (same v3 endpoint).
- `assert_auto_publish_checked_and_label(page, context, "vcita")`: re-open settings and
  assert the checkbox `aria-checked=true` (persisted `display_review_sharing_consent`)
  and that `[data-qa="reviews-settings-auto-publish-checkbox"] .v-label` contains "vcita".

## Client portal (vitrage `cp_iframe`), via `reviews_cp_ui.py`
- `assert_cp_auto_publish_visibility(page, context, should_display=True)`:
  - Open `{vitrage}/site/{business_uid}/activity/review?client_jwt=<token>`.
  - Wait for `.review-page` and the `[data-qa="review-settings-loaded"]` marker.
  - Assert `.auto-publish-container` is displayed (CP `shouldDisplayAutoPublish` requires
    collect_reviews + enable_reviews_auto_publishing + display_review_sharing_consent +
    external_review_site_url, all satisfied here).

## Scope preservation vs legacy
- Login, platform selection, auto-publish toggle all via UI (legacy in-scope UI actions).
- "auto-publish checkbox is checked" preserved, strengthened by re-opening to prove persistence.
- "review site display name is vcita" preserved (label text assertion).
- Client-portal "auto-publish checkbox is displayed" preserved.
- Directory + business + client created via API (legacy setup steps).
