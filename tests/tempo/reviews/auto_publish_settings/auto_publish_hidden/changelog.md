# Changelog — Auto-publish Hidden Without Review Site

## 2026-06-06 — Migration from automation-js (VCITA2-13853)
- Created from reviews.feature scenario 2 ("Auto-publish settings does not appear in
  review settings page").
- Setup provisions a directory with **no** external review site + an in-directory
  business + a client (API), verified on integration with a read-back.
- Verified against POV source (`ReviewsPage.vue`/`ReviewSettings.vue`): the auto-publish
  section renders only `v-if="reviewSite"` (directory external review site), so with no
  review site the section is absent even with the reviews feature flags enabled. The
  page still renders because reviews_rollout + collect_reviews are enabled — asserting
  the public-reviews checkbox first guards against a false pass from a dashboard redirect.
- Verified against client-portal source (`ReviewPage.vue`): `shouldDisplayAutoPublish`
  also requires `external_review_site_url`, so the CP `.auto-publish-container` is absent.
- All UI waits condition-based; element-level waits capped at 5s (the negative-assertion
  settle, `ABSENCE_STABILITY_TIMEOUT`, is exactly 5s and polls that the section never
  appears after the page renders). Longer waits are justified page-load/eventual-consistency
  budgets only (settings/CP page-readiness). No retry loop exceeds 2 retries.

## 2026-06-06 — Fix: session isolation between tests
- Switched login to `fresh_login` (clears cookies + storage before `fn_login`). The runner
  reuses one browser context across the subcategory, so without a clean slate this test
  could inherit the previous test's POV session and assert against the wrong business. See
  the set_auto_publish changelog for the full root-cause analysis.
