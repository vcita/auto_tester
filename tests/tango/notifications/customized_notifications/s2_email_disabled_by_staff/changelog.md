# Changelog — s2_email_disabled_by_staff

## 2026-06-19 — Created (VCITA2-14248 migration)
- Migrated from automation-js/features/tango/customized-email-notification.feature — Scenario 2.
- Strict phase order steps.md -> script.md -> test.py.
- Scope: v3 EMAIL template create + shows in settings; staff UNCHECKS email channel (UI action,
  kept as UI) + save; persists email=false after refresh; v3 send then FAILS (no uid).
- Reuses shared `notifications_helpers`: ensure_owner_session, goto_settings,
  assert_template_in_settings, set_channel_checkbox, assert_channel_values, directory_token.
- `send_notification_v3` is a single non-retrying POST returning None on a non-2xx.
- BACKEND BEHAVIOR CHANGE (verified live integration 2026-06-19): the legacy scenario asserted
  the v3 SEND itself FAILED (null uid on a non-2xx) when the only channel was staff-disabled.
  On the current backend the same send returns **201** with the notification record created but
  the disabled channel NOT dispatched — a normally-enabled email send stamps
  `email_status: ["in_progress"]`, while the staff-disabled-email send leaves `email_status: null`
  (no channel processed). Diagnostic captured both responses on a live run. The user-visible
  behavior the scenario owns ("a staff-disabled channel is not delivered") is PRESERVED and is
  asserted via the new `assert_v3_channel_not_dispatched` helper on the empty channel status —
  a more direct check than the old HTTP-failure proxy. No scope loss: the uncheck-email UI action,
  the persistence assertion (email=false), and the not-delivered outcome are all kept.
- Waits: all UI ≤5s via reused helpers.
