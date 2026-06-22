# Changelog — Upgrade In Frontage

## 2026-06-11 — Initial migration (VCITA2-14028)
- Migrated automation-js `upgrade_page.feature` scenario 1.
- Account: isolated Trial account (`account_profile.package_subscription_id: 28`).
  Required a small framework extension so the isolated-account path honors an
  explicit `package_subscription_id` (default stays Platinum 14); the upgrade test
  must start below the target plan.
- UI flow kept in scope: open upgrade page (`vue_upgrade_page` iframe) → click
  `#auto_enterprise_single .get-it button` → Recurly checkout (new tab) → fill name
  + card → submit.
- Assertions: success-page package text == "vcita Platinum Single (Annual)" (UI,
  mirrors legacy getPackageFromSuccessPage) + business `meta.plan.plan_name` ==
  "Platinum Single" (API admin read, mirrors legacy `business ... has plan`).

### Recurly integration findings (proven on integration)
- Blocked `sealserver.trustwave.com` (trust-seal script) — it hangs DOMContentLoaded
  so Recurly never configures and the hosted card fields never mount.
- Hosted card-field iframes reject `.fill()`; typed with `press_sequentially`
  (cleared with select-all+Backspace first so a re-fill on retry replaces, not
  appends).
- Submit is driven deterministically by calling `recurly.token(form, cb)` then the
  native `form.submit()` in-page (a plain Playwright click on `button.pay` does not
  reliably trigger Recurly tokenization). Mirrors the legacy submit behavior.

### Pre-PR Wait Audit (VCITA2-14028) — bounded polls justified, retries ≤2
All waits below are bounded polls around the **third-party Recurly checkout tab**
(nested iframe + external billing round-trip), not masks for flaky local selectors.
Per-element waits are all ≤5s (button visible 3s, hosted-field click 5s, success
package read 5s). Items intentionally kept >5s and why:
- **Get-it click loop deadline 30s** (`_click_get_it`): the `vue_upgrade_page` iframe
  is nested in the POV/Angular iframes and re-renders after first paint, and the
  click must open a new third-party tab. The loop re-acquires the frame and uses a
  short `expect_page(timeout=6s)` per attempt so a missed popup retries fast.
- **Hosted-field mount poll ≤12s** (`IFRAME_MOUNT_TIMEOUT_S`): Recurly loads hosted
  fields from external recurly.com after a load-time redirect — genuine 3rd-party
  async.
- **Submit success poll ≤8s/attempt** (`SUBMIT_WAIT_S`, ≤2 retries): waits for
  Recurly tokenization + redirect to the success page (external billing round-trip).
- **In-page token guard 10s** (JS `setTimeout`): Recurly tokenization network
  round-trip guard so the evaluate always resolves.
- **Success-page / business-plan reads ≤5s / ≤15s**: success package read is ≤5s; the
  business `meta.plan.plan_name` API read-back is an eventually-consistent poll
  (billing writes the subscription asynchronously after the success page).
- No `data-qa` exists on the plan cards or the 3rd-party Recurly page; documented
  the legacy stable CSS selectors as the fallback.
- Stability re-confirmed after the final hardening: **10/10** focused stress
  (`settings/upgrade_page/upgrade_in_frontage`, integration, headless).
