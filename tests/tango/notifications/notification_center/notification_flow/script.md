# Script — Notification Center Pane And Badge Flow

`test_notification_flow(page, context)` — all helpers in `notifications_helpers.py`.

## API preconditions (mirrors legacy api/apps + api/notificationCenter)
- `app = create_app(context, code, name)` — admin `POST /platform/v1/apps`; name ≤25 chars.
- `app_token = app_service_token(context, app)` — admin `POST /oauth/service/token`.
- `assign_app_to_account(context, code)` — admin `POST /platform/v1/apps/<code>/assign`
  {business_uid, directoryUid} (legacy assign_unassign_app_to_business).
- `create_notification_template(context, app_token, code=auto_notification<seq>, type=messages,`
  `channel={pane:true}, deep_link="app/clients", text={...})` — apigw
  `POST /business/notificationscenter/v1/notificationsmetadata/`.
- `staff_uid = first_staff_uid(context)` (account_api) — owner staff for sending.

## UI actions / locators (POV, see notifications_helpers constants)
Badge button `[data-qa="VcWideTopMenuBar-notifications"]`; counter span
`[data-qa="VcWideTopMenuBar-notificationsBadge"] .v-badge__badge` (hidden at 0). Pane content
container `.notification-pane` (the badge opens a `.v-menu__content` dropdown that holds it).
Empty state `[data-qa="empty-state-no-notifications"]`; read-all empty
`[data-qa="empty-state-read-all"]`. Row `.pane-row`; title `.pane-row__body__title`;
body `.pane-row__body__description`; time `[data-qa="vc-time-since"]`; unread
`.pane-row__body--active`; read `.pane-row__body--inactive`; dot `div.pane-row__body__dot`;
only-unread toggle `.notification-pane .v-input--selection-controls__input`; mark-all
`.notification-pane__header [data-qa="VcLink"]`.

### Open / close pane (deterministic; readiness-then-act-once)
- **Readiness signal — toolbar FULLY MOUNTED**: the toolbar badge is hittable only once (a) the
  POV cold-bootstrap skeleton placeholders are gone — the whole top menu bar
  `[data-qa="VcWideTopMenuBar"]` first renders as a row of `.v-skeleton-loader` bones
  (`data-qa="VcSkeleton"`) where the search/AI/badge/help/account icons go, with a content
  spinner below (this is the failure screenshot: owner dashboard with grey skeleton dots
  top-right) — AND (b) the new-account onboarding wizard's modal overlay
  `.angular-iframe.isModalMode` is gone. `badge visible` alone is NOT enough: the prior wait
  could resolve on a briefly-mounted badge while the page was still settling its cold bootstrap,
  and the next click/counter read raced a re-render and timed out at 5s (the dominant ~30-40%
  late-flow flake). Verified live on integration (chrome, 1440x900): cold mount goes
  skeleton-toolbar → real badge appears (toolbar skeletons gone at the same tick, ~1.2s) → all
  page skeletons gone (~2.3s); the badge opens the pane cleanly only at the all-skeletons-gone
  point. The wizard is suppressed by the `hide_register_wizard` flag, which can lose a
  propagation race on a cold POV load.
- **open_pane** = `_wait_toolbar_mounted` (real badge visible + zero visible `.v-skeleton-loader`
  + `.angular-iframe.isModalMode` hidden) → single click of the badge → wait for
  `.notification-pane` visible → wait for a content marker (`.pane-row` |
  `[data-qa="empty-state-no-notifications"]` | `[data-qa="empty-state-read-all"]`). No click
  retry; if the pane does not appear, fail.
- **close_pane** = single click of the transparent scrim `.v-overlay__scrim.transparent`, then
  wait for `.notification-pane` hidden. Escape does NOT dismiss the dropdown variant, so it is
  not used (one dismissal method, no fallback). Idempotent if the pane is already closed.
- **goto_dashboard** navigates to `/app/dashboard` and waits for the toolbar to be FULLY MOUNTED
  via `_wait_toolbar_mounted` (real badge visible + zero visible skeletons + overlay hidden),
  bounded re-checked (<=2 re-navigations): if a cold POV bootstrap has not finished mounting the
  toolbar yet (the skeleton/loading-spinner shell reached after the impersonation SSO re-login) it
  KEEPS WAITING on the booting page; if the onboarding wizard won the flag race (its overlay is
  present) it re-navigates so the propagated flag takes effect, rather than failing against the
  still-booting shell.

## Flow
1. `open_pane` (click badge); `expect empty-state-no-notifications visible`; `close_pane`.
2. `send_notification(app_token, code, staff_uid, params={first_name:auto,last_name:notification})`.
   `assert_badge_counter("1")` — badge counter is async; bounded read re-check ≤2 retries
   (legacy retried 10x), each attempt re-reads the counter text within 5s.
3. `open_pane`; `assert_notification_displayed(title="Check this out!",`
   `body="Hi auto notification! A new message is available", timestamp="Just now",`
   `status="unread")` — match the row by body, compare title/body/time/status.
   `assert_no_badge_counter` (counter span hidden after open). `close_pane`.
4. `open_pane`; `click_notification` (click `.pane-row`); assert URL is the new Clients page
   (`/app/clients` list) — wait for the clients list to be visible (deep link redirect).
   Then `goto_dashboard` for the remaining pane operations: the pane is a global toolbar
   control but opens far more reliably on the light dashboard than on the heavy CRM page.
5. `open_pane`; `assert_notification_read` (`.pane-row__body--inactive` present). `close_pane`.
6. `open_pane`; `toggle_read_status` (click dot) → `assert_notification_unread`; `close_pane`.
   `open_pane`; `toggle_read_status` → `assert_notification_read`; `close_pane`.
7. `send_notification` x3 (Notification 1/2/3). `assert_badge_counter("3")`.
   `open_pane`; `assert_pane_notification_count(4)` (count `.pane-row`).
8. `toggle_only_unread` (click switch) → count 3. `toggle_only_unread` → count 4.
   `mark_all_as_read` (click VcLink). `toggle_only_unread` → `expect empty-state-read-all`.
   `close_pane`.
9. `staff = create_platform_staff_via_api(context, "Staff Admin", email, role="admin")`
   (account_api). `send_notification` to current (owner) staff. `assert_badge_counter("1")`.
   `impersonate_staff(page, context, "Staff Admin")` — Staff settings page, hover row, open the
   actions menu, fire "Log in as" via a JS-level `dispatch_event("click")` (the Angular md-menu
   item is `visible` instantly but its overlay blocks pointer-event actionability for ~4.5s, so a
   real `.click()` spends that in the actionability retry and intermittently exceeds 5s — the
   residual ~30% flake; the JS click fires the handler instantly). "Log in as" triggers a full
   SSO logout + re-login that NAVIGATES to `/app/dashboard` as the new staff by itself — we do NOT
   `page.goto` (that would race the redirect and reload as the OWNER, failing the per-staff
   check). Instead `_wait_impersonation_landed` bounded-waits the dashboard URL (the SSO chain is
   slow, ~4.5-6.5s — exceeds one 5s wait, so bounded <=2 re-checks, no re-navigation) then the
   impersonated-staff welcome subtitle, then `_wait_toolbar_mounted` for the pane open.
   `assert_logged_staff`; `assert_no_badge_counter`; `open_pane`;
   `expect empty-state-no-notifications` (per-staff isolation); `close_pane`.

## Waits
All UI waits `timeout=5000`. The toolbar fully-mounted gate (`_wait_toolbar_mounted`) is: real
badge visible (≤5s) + zero visible `.v-skeleton-loader` placeholders (bounded poll capped at 5s,
~2.3s cold) + `.angular-iframe.isModalMode` hidden (≤5s). Badge counter and pane-count reads use a
bounded re-check (≤2 retries) because counter propagation lags the send API. `goto_dashboard`
re-navigates at most twice (≤2) to let a cold POV bootstrap finish mounting the toolbar (the
skeleton/loading-spinner shell after the impersonation SSO re-login) and to let the
`hide_register_wizard` flag propagate when the onboarding wizard wins the cold-load race — the
fully-mounted wait is inside that bounded retry, not a single un-retried 5s wait against the
still-booting shell. No action retries (badge/scrim clicks happen once after a readiness
wait); no fixed sleeps.
