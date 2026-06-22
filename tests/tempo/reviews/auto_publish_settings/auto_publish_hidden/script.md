# Auto-publish Hidden Without Review Site — Script

Two surfaces: the back-office POV reviews settings page and the client-portal review
page (vitrage `cp_iframe`). The business lives in a directory with no external review
site, so the auto-publish UI must be absent on both. All UI waits are condition-based
and capped at 5s; page loads use a longer page-readiness budget.

## Login
- `fresh_login(page, context, username=<business email>, password=<business pw>)` — clears
  cookies + storage then `fn_login`, as the in-directory business owner (not the runner's
  isolated account). The clean slate avoids inheriting another test's POV session.

## Back-office (POV `/app/settings/reviews`), via `reviews_settings_ui.py`
- `assert_auto_publish_section_absent(page, context)`:
  - `open_review_settings` first waits for `[data-qa="review-public-reviews-checkbox"]`
    to render — this proves the page loaded (reviews_rollout + collect_reviews) instead
    of redirecting to the dashboard, so an absent section is a real "not displayed".
  - Then asserts `[data-qa="reviews-settings-auto-publish-checkbox"]` count is 0
    (POV renders that section only `v-if="reviewSite"`).

## Client portal (vitrage `cp_iframe`), via `reviews_cp_ui.py`
- `assert_cp_auto_publish_visibility(page, context, should_display=False)`:
  - Open `{vitrage}/site/{business_uid}/activity/review?client_jwt=<token>`.
  - Wait for `.review-page` and the `[data-qa="review-settings-loaded"]` marker
    (display:none; matched by presence) so the auto-publish decision is computed.
  - Assert `.auto-publish-container` count is 0.

## Scope preservation vs legacy
- Login via UI (legacy `user logins to vcita account`).
- Back-office "auto-publish checkbox is not displayed" preserved, strengthened by also
  proving the page rendered.
- Client-portal "auto-publish checkbox is not displayed" preserved
  (legacy `client's client portal reviews page ... auto-publish checkbox "is not" displayed`).
- Directory + business + client created via API (legacy `admin creates directory` /
  `creates business in directory` / `creates new client for business in directory`).
