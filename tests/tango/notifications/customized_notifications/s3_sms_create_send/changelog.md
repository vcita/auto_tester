# Changelog — s3_sms_create_send

## 2026-06-19 — Created (VCITA2-14248 migration)
- Migrated from automation-js/features/tango/customized-email-notification.feature — Scenario 3.
- Strict phase order steps.md -> script.md -> test.py.
- Scope: v3 SMS template create + shows in settings; staff ENABLES the SMS channel (UI action,
  kept as UI) + save; v3 send (passed -> uid); v3 sms status contains "in_progress".
- Reuses shared `notifications_helpers`: ensure_owner_session, goto_settings,
  assert_template_in_settings, set_channel_checkbox, directory_token + the v3 API helpers.
- Waits: all UI ≤5s via reused helpers; v3 sms status is a bounded eventual-consistency poll (≤5s).
