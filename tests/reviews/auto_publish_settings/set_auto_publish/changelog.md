# Changelog — Set Auto-publish Setting

## 2026-06-06 — Migration from automation-js (VCITA2-13853)
- Created from reviews.feature scenario 3 ("Set review auto-publish settings").
- Setup provisions a directory **with** an external review site (`https://www.vcita.com`,
  label `vcita`) + an in-directory business + a client (API), verified on integration
  with a read-back.
- Reuses `set_review_platform` from the sibling invite_to_review migration for the
  Facebook/vcitainc platform configuration (in-scope UI action, not replaced by API).
- Added `toggle_auto_publish_and_save` and `assert_auto_publish_checked_and_label` to
  `reviews_settings_ui.py`; each re-opens the settings page so assertions read the
  persisted `display_review_sharing_consent` rather than transient DOM state (stronger
  than the legacy read-after-goto).
- Verified against POV source: auto-publish section renders `v-if="reviewSite"` and the
  label includes the review site name via `provider: reviewSite`.
- Verified against client-portal source (`ReviewPage.vue`): with auto-publish enabled and
  an external review site, `shouldDisplayAutoPublish` is true so `.auto-publish-container`
  is shown.
- All UI waits condition-based; element-level waits capped at 5s. Longer waits are
  justified page-load/network/eventual-consistency budgets only: `PAGE_LOAD_TIMEOUT`/
  `AUTO_PUBLISH_RENDER_TIMEOUT` (20s) for full-navigation readiness — the auto-publish
  section is gated on `directory_settings` which the BusinessStore fetches during app init,
  a beat after the public-reviews checkbox paints; `SAVE_SETTLE_TIMEOUT` (10s) waits on the
  v3 reviews settings save response; CP page load uses `CP_LOAD_TIMEOUT` (15s). No retry
  loop exceeds 2 retries.

## 2026-06-06 — Fix: session isolation between tests (root cause of flaky section)
- Symptom: scenario 3's back-office auto-publish section never rendered even though the
  directory's review site was correct (admin/opaque-token reads of
  `business/accounts/v1/attributes` returned `review_site_display_name=vcita`).
- Root cause: the runner reuses one browser context across the subcategory's tests, so the
  prior test's POV session (cookies + persisted staff JWT) leaked into this test. The
  decisive evidence: POV's own attributes response (its staff JWT) returned
  `review_site=None`, and the staff JWT's `business_uid` equalled the **no-site** business
  from scenario 2 — i.e. POV was still authenticated as the previous (no-review-site)
  business, so `hasReviewSite` was false and the section was correctly hidden for the wrong
  business. `fn_login` short-circuits when a session already exists.
- Fix: added `fresh_login` (in `directory_setup.py`) which clears cookies + localStorage/
  sessionStorage before delegating to `fn_login`, forcing a real re-login as the intended
  in-directory business. Both auto_publish tests now use it. After the fix the staff JWT
  resolves the correct business and the section renders within a few seconds.
- Also added polling (`_wait_present`) to the platform select and auto-publish controls so
  Vuetify's post-paint re-render of those fields no longer races a single-shot lookup.
