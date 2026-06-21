# Changelog — s1_email_create_send

## 2026-06-19 — Created (VCITA2-14248 migration)
- Migrated from automation-js/features/tango/customized-email-notification.feature — Scenario 1.
- Strict phase order steps.md -> script.md -> test.py.
- Scope: v3 EMAIL template create (configurable_by_staff) + shows in NC settings; v3 send
  (passed -> uid) + GET created; v3 update (title + CTA) -> refreshed display; badge counter "1";
  v3 email status contains "processed".
- Reuses shared `notifications_helpers`: ensure_owner_session, goto_settings,
  assert_template_in_settings, goto_dashboard, assert_badge_counter, directory_token.
- Extended the shared module with the v3 API helpers (create/update/send/get/status/delete).
- Legacy ground truth (integration, 2026-06-19): full feature 3 scenarios / 23 steps PASS in 1m31s;
  v3 endpoints confirmed live.
- Waits: all UI ≤5s via reused helpers; badge + v3 email status are bounded eventual-consistency
  polls (≤5s), no action retried. "Refresh the page" = re-navigate to settings (no page.reload).
