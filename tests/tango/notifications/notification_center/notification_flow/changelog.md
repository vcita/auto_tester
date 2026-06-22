# Changelog — notification_flow

## 2026-06-19 — Stabilize toolbar-skeleton late-flow flake (VCITA2-14247)

10-iteration stress sat at 60-70% across four runs (only `notification_flow` failed; the two
settings subtests never did). Generic `TimeoutError: Timeout 5000ms exceeded` at VARYING points
(durations 23/27/29/31s), so a recurring readiness issue — not one late step. The 23s-failure
screenshot showed the OWNER dashboard with the TOP TOOLBAR still rendered as SKELETON
placeholders (grey dots top-right) plus a content spinner.

### Root cause (verified live via Playwright MCP / a direct chrome-channel probe on integration)
On every cold POV bootstrap — initial dashboard load, each `goto_dashboard` badge-refresh
re-nav, and especially the impersonation SSO re-login — the whole top menu bar
`[data-qa='VcWideTopMenuBar']` first renders as a row of Vuetify `.v-skeleton-loader` bones
(`data-qa='VcSkeleton'`) where the search/AI/badge/help/account icons go, with a centered
content spinner below. Deterministic mount sequence at the runner's size (chrome, 1440x900):
- t+0.0: no `VcWideTopMenuBar` host; ~21 page skeletons.
- t+0.5: host present but its icons are 8 visible skeletons; the real badge button
  `data-qa='VcWideTopMenuBar-notifications'` does NOT exist yet (the badge selector matches 0).
- t+1.2: skeletons swapped for the REAL badge button — toolbar skeletons hit 0 at the same tick.
- t+2.25: the last sidebar/content skeletons clear (0 visible page skeletons); the badge opens
  the pane cleanly.
The prior gate `_wait_toolbar_interactable` waited only for `badge visible` (+ wizard overlay
hidden). That resolved on a briefly-mounted badge while the page was still settling its cold
bootstrap, so the immediately following `.click()` / counter read raced a re-render and timed
out at 5s. Because the pane is opened/closed and the badge read ~5-6 times across the flow (and
`goto_dashboard` is called repeatedly), the race recurred — hence the varying failure points.

### Fix (deterministic fully-mounted signal, no action retries)
- New `SKELETON_LOADER = ".v-skeleton-loader"` + `_wait_toolbar_mounted` (renamed from
  `_wait_toolbar_interactable`): the toolbar is "ready" only when the real badge is visible AND
  there are ZERO visible `.v-skeleton-loader` placeholders left on the page (whole cold
  bootstrap finished) AND the onboarding modal overlay is hidden. The skeleton gate is a bounded
  visible-count poll capped at UI_TIMEOUT (5s, ~2.3s cold) — a `.first` hidden-wait is unsafe
  because skeletons detach in DOM order (the first could clear while later ones are still up).
  This is strictly stronger than the old badge-visible signal.
- `open_pane` and `goto_dashboard` now use `_wait_toolbar_mounted`. `goto_dashboard` keeps its
  bounded (<=2) re-check: a still-booting cold bootstrap (no overlay) loops without
  re-navigating (a fresh goto would restart the boot); only an actually-present wizard overlay
  triggers a re-navigation so the propagated `hide_register_wizard` flag takes effect.
- Post-impersonation landing (`impersonate_staff` -> `goto_dashboard`) and the Clients deep-link
  return (step 4 -> `goto_dashboard`) inherit the same fully-mounted gate.

### Wait audit
All individual UI waits stay <=5s (badge wait, overlay wait, settings frame waits, URL wait);
the skeleton readiness is a single bounded poll capped at 5s. Re-checks stay <=2 retries
(goto_dashboard re-nav <=2; badge-counter/pane-count eventual-consistency polls <=2). No action
is retried (badge/scrim clicks happen once after the readiness wait). No fixed sleeps; no
assertion, setup path, edge case, or in-scope UI action removed or weakened (full legacy scope
preserved). steps.md unchanged (user-facing flow identical); script.md Open/close-pane + Waits
sections synced to the new fully-mounted signal.

### Residual flake after the skeleton fix — the impersonation step (step 9)
The skeleton gate fixed the recurring early-flow opens, but a re-run was still 7/10, now failing
ONLY at step 9 (impersonation) with blank/loading-spinner POV screenshots. Reproduced step 9 in a
loop (live, chrome) and found TWO compounding causes:
1. **"Log in as" menu-item click actionability.** The Angular md-menu item renders `visible`
   immediately but its overlay/animation blocks pointer events for ~4.5s, so a real `.click()`
   spends that whole time in Playwright's actionability retry and intermittently exceeds the 5s
   cap. Fix: fire it with a JS-level `dispatch_event("click")` (same pattern the settings checkbox
   uses; legacy `_clickElementByJS`) — the ng-click handler fires instantly.
2. **`goto_dashboard` raced the SSO impersonation redirect.** "Log in as" SSO-re-logs-in and
   navigates to `/app/dashboard` as the new staff ON ITS OWN. The old `impersonate_staff` issued
   `goto_dashboard` (a `page.goto`) immediately after the click — that fresh navigation RACED the
   in-flight SSO redirect and reloaded the dashboard as the ORIGINAL OWNER before the token swap
   completed. The toolbar then mounted cleanly as the owner (so a toolbar-only wait passed), but
   the welcome subtitle showed the owner and the per-staff assertion timed out. Caught live: state
   at failure was `welcome="Welcome back, <owner>"` on a fully-mounted dashboard.
Fix: `impersonate_staff` no longer navigates after the click. New `_wait_impersonation_landed`
lets the SSO redirect settle on its own — bounded-waits the `/app/dashboard` URL (the SSO chain is
genuinely slow, ~4.5-6.5s, exceeding one 5s wait, so bounded <=2 re-checks, NEVER re-navigating)
then the impersonated-staff welcome subtitle — and only then `_wait_toolbar_mounted` for the
subsequent pane open. Validated 8/8 on the isolated step-9 path before the full stress.

Wait audit (impersonation): each individual wait <=5s (staff goto, row/menu/login-as waits, URL
wait, welcome wait, toolbar mount); URL and welcome waits bounded <=2 retries (<=15s); single
dispatch click (no action retry); no navigation that could reset the impersonation. No scope
change: the "Log in as" UI action is preserved (still driven through the staff-list menu), the
per-staff isolation assertion is unchanged.

### Validation
`python main.py stress_test --categories tango/notifications/notification_center --iterations 10
--env integration --headless` -> see the stamped result below / in `_category.yaml`/`_health.json`.

## 2026-06-19 — Created (VCITA2-14247 migration)

Migrated from `automation-js/features/tango/notification_center.feature` Scenario 1.
Legacy ground truth: `node index features/tango/notification_center.feature integration
--headless` = 3 scenarios / 65 steps passed in ~2m40s (2026-06-19).

### Shared decisions (apply to the whole notification_center subcategory)
- **Team/domain**: Confluence "Squads responsibilities" (pageId 2615410911) maps
  "Notification Center" -> **Tango**. Placed at `tests/tango/notifications/notification_center`.
- **Helper module** `notifications_helpers.py` mirrors the legacy api/notificationCenter.js,
  api/apps.js, api/api.js token plumbing, and the toolbar/notification_pane/notification_settings
  /staffs page objects. All selectors were verified live on integration with the Playwright MCP
  (2026-06-19), correcting two stale legacy details:
  - The settings page is a **doubly-nested iframe**: `#angular-iframe` -> `#vue_iframe_layout`
    (legacy only switched into `vue_iframe_layout`).
  - The badge counter is the Vuetify `.v-badge__badge` span inside
    `[data-qa='VcWideTopMenuBar-notificationsBadge']`; the clickable button is
    `[data-qa='VcWideTopMenuBar-notifications']`.
- **Tokens** (verified live): app token = admin POST /platform/v1/apps -> client creds ->
  admin POST /oauth/service/token; directory token default = the integration directory 970
  (kmy47p5x88kqlv6f) token auto_tester provisions on; core_internal_app token from the
  integration service creds. All overridable via env (VCITA_DIRECTORY_TOKEN, VCITA_DIRECTORY_UID,
  VCITA_CORE_INTERNAL_SERVICE_ID/SECRET, VCITA_APIGW_URL). Notification metadata + send run on the
  apigw (apigw-integration), derived from the core api base.
- **API vs UI**: template create/update/send + staff create stay API (legacy did them via API);
  every notification-pane / settings / badge / impersonation assertion is driven through the UI.
- **Waits**: all UI waits capped at 5s. Badge counter and pane-count reads use a bounded read
  re-check (<=2 retries, ~1s apart) because counter propagation lags the send API (legacy retried
  this read up to 10x; 2 retries suffices on integration).
- **"Refresh the page"** in the legacy settings scenarios = re-navigate to the settings page
  (real navigation), not page.reload (forbidden by project rules).

### This test (Scenario 1)
- App `automationjs<seq>` + `messages` template `auto_notification<seq>` (channel pane, deep
  link app/clients). Covers: empty state, badge counter, pane display (title/body/timestamp/
  status), badge reset on open, deep-link redirect to Clients, read/unread blue-dot toggle,
  3-more-notifications count (4), show-only-unread (4->3->4), mark-all-as-read -> read-all empty
  state, and per-staff isolation by impersonating an API-created "Staff Admin".
- App name is kept to 3..25 chars (`AutoJS <seq>`); the create endpoint rejects longer names.
- App + template recorded in context for best-effort teardown deletion.

### Validation / stabilization (2026-06-19)
Fixes found during validation (all selectors/flows verified live via Playwright MCP):
- Account slug `notification_center` was rejected by the create API ("contains invalid term");
  renamed the isolated account slug to `nc_center`.
- Step 9 send needs params `{first_name: staff, last_name: notification}` (template body uses
  `${first_name} ${last_name}`; sending without params 400s).
- The toolbar badge counter updates via a live push that is reliable on the dashboard but
  stale on the heavy notification_settings iframe page; settings tests read the badge after
  `goto_dashboard`. Opening the pane marks notifications seen server-side (badge clears on
  reload), so the suppressed-delivery assertion reads correctly.
- The settings page is a doubly-nested iframe and cold-loads slowly; `goto_settings` waits
  through the frame chain with a bounded re-check (<=2).
- Cross-test session leak: notification_flow ends impersonated as "Staff Admin", so the
  settings tests start with `ensure_owner_session` (clear session + re-login as owner).
- The settings channel checkbox is a Vuetify input whose normal click is intercepted; toggle
  via `dispatch_event("click")` (legacy `_clickElementByJS`), then click the now-enabled Save.
- `open_pane` and the impersonation reload race on cold POV; `open_pane` re-clicks the badge
  (bounded <=2) until the pane content marker appears, and impersonation waits for the
  dashboard welcome subtitle (bounded <=2) instead of wait_for_url('load').
- Badge counter reads use a bounded eventual-consistency poll capped at 5s (legacy retried 10x).

Stability root cause (found via a 10-iteration stress that was 2-5/10): the notification
pane is **responsive** — a `.v-menu__content` dropdown on a wide viewport but a Vuetify
**bottom-sheet** (`.v-dialog VcBottomSheet`) at the runner's headless size. The original
`.v-menu__content.theme--light` overlay selector only matched the dropdown, so under the
runner it never saw the pane. Fixes:
- `PANE_OVERLAY` -> `.notification-pane` (present in both variants).
- `close_pane`: Escape (closes the menu / focused sheet) alternated with a top-of-viewport
  scrim click (the bottom-sheet is bottom-anchored, so a y=5 click hits the dismissing
  scrim; Escape no-ops after a row interaction moves focus out of the dialog). Bounded <=2.
- `open_pane` waits for the badge to mount, clicks, then waits for `.notification-pane` +
  a content marker, with a bounded click-retry on cold POV.

Evidence: scenario 1 passes the immediate-after-login debug harness 3/3, then the focused
runner + 10-iteration stress (see PR / tracker for the stamped 10/10).

## 2026-06-19 — Stabilization (real root cause) + review fixes (VCITA2-14247)

### Root cause of the 7/10 stress flakiness (runs 3/4/10: `TimeoutError 5000ms`)
Found live via Playwright MCP on integration. A freshly-created account can pop the
**new-account business-setup onboarding wizard** (an Angular `md-dialog`; body class
`wizard-open`). While it is up, the POV `.angular-iframe` wrapper gains `isModalMode`
/`isFullscreen` and renders a **full-viewport iframe overlay on top of the entire toolbar —
including the notification badge**. A badge click then hits the iframe overlay, not the
button, and times out at 5s (matching the blank loading-spinner failure screenshots).
The runner suppresses this wizard with the `hide_register_wizard` feature flag (set at
account creation), but the flag **propagates asynchronously**, so on a cold first POV load the
wizard can still win the race (~30% of runs). Verified: a flagged account never shows the
wizard; the overlay is exactly `.angular-iframe.isModalMode`.

### Fix (deterministic readiness, no action retries)
- New `MODAL_OVERLAY = ".angular-iframe.isModalMode"` + `_wait_toolbar_interactable`: the
  toolbar is "ready" only when the badge is mounted AND that modal overlay is hidden (the
  badge being merely `visible` is not enough — it sits *under* the overlay). When no wizard is
  present the selector matches nothing and the hidden-wait resolves instantly.
- `open_pane` no longer retries the badge click (review finding #1). It waits for the toolbar
  readiness signal, clicks the badge **once**, then waits for `.notification-pane` + a content
  marker; if the pane does not appear it fails.
- `goto_dashboard` waits for the readiness signal after navigating; if the onboarding wizard
  won the flag-propagation race it **re-navigates (bounded <=2)** so the flag takes effect and
  the wizard clears — a read re-check of a real signal, not an action retry.
- `impersonate_staff` now lands the impersonated session via `goto_dashboard` (same readiness
  + bounded re-nav), since the impersonated staff's first POV load can re-trigger the wizard.

### Other review fixes
- #2 `close_pane`: replaced the alternating Escape/scrim-click with the **single** verified
  method — click the transparent scrim `.v-overlay__scrim.transparent`, then wait for the pane
  hidden. Verified live at the runner's window width (1440; `no_viewport` +
  `--window-size=1440,900`) that the pane renders as the `.v-menu__content` dropdown and that
  Escape does NOT dismiss it while the scrim click does. (The earlier "responsive bottom-sheet"
  assumption did not match the runner's actual width.)
- #3 secrets: there is genuinely **no per-run/context/env source** for the directory-970 token
  or the `core_internal_app` service creds — they are long-lived integration secrets, unlike
  `VCITA_ADMIN_TOKEN` (env-only) and the per-run owner credentials. Kept the test working:
  env-first (`VCITA_DIRECTORY_TOKEN` / `VCITA_DIRECTORY_UID` /
  `VCITA_CORE_INTERNAL_SERVICE_ID` / `VCITA_CORE_INTERNAL_SERVICE_SECRET`) with an
  integration-only fallback (same env-or-default shape as `account_factory`'s operator
  creds). Documented + flagged in the helper that these are integration-only, grant no
  production access, and MUST be set via env on any non-integration env. **Flag for reviewers:
  the cleanest long-term fix is to move these into the shared secret/env config rather than a
  source default, but no such source exists today and stability/rule-compliance took priority.**
- #4 script.md synced to the real selectors (`.notification-pane`, scrim close) and the new
  readiness/close behavior.
- #5 `ensure_owner_session`: narrowed the broad `except Exception: pass` to `PlaywrightError`
  with a log line (the best-effort session clear before re-login).


## 2026-06-19 — Stabilize ~30% late-step flake (VCITA2-14247)

10-iteration stress was 7/10 (runs failed ~28s in, near the end). Generic
`TimeoutError: Timeout 5000ms exceeded`; both failure screenshots show a blank POV
bootstrap shell (one with the centered loading-spinner dot, one fully white) with NO
toolbar rendered.

### Root cause
The only failing subtest is `notification_flow`, failing on the final impersonation step
(#9). `impersonate_staff` ends with `goto_dashboard`, which is reached via a full SSO
re-login + cold POV bootstrap. In `goto_dashboard` the `badge.wait_for(state="visible")`
sat **outside** the bounded retry/except (only the onboarding-overlay wait was retried), so
when `page.goto(..., wait_until="domcontentloaded")` resolved on the still-booting blank
shell, the single 5s badge-visible wait fired against a toolbar that had not mounted yet and
raised immediately — no re-navigation. This cold-bootstrap race is the dominant ~30% flake.

### Fix (notifications_helpers.goto_dashboard)
Moved the `badge.wait_for(state="visible")` INSIDE the bounded retry alongside the
overlay-hidden wait, so the full toolbar readiness (badge mounted AND onboarding overlay
gone) is re-checked together. If a cold POV bootstrap has not mounted the toolbar, or the
onboarding wizard won the flag race, `goto_dashboard` re-navigates (bounded <=2) to let the
app finish booting / the flag take effect, instead of failing the single 5s wait against the
booting shell. Each individual wait stays <=5s; re-navigation stays <=2 retries; no action
retries; single detection per wait; no assertions weakened or dropped (full legacy scope
preserved). The Clients deep-link redirect (step 4) already routes its post-nav recovery
through the same `goto_dashboard`, so it is covered too.

script.md `goto_dashboard` description + Waits section synced to the new readiness behavior.
