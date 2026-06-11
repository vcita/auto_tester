# Changelog — Exceed And Free Up Clients Quota

## 2026-06-09 — Initial migration (VCITA2-14005)
- Migrated from `automation-js/features/steps/clients-quota.feature`
  (Scenario: "Exceed and free up clients quota").
- Account provisioning: added operator-token + custom-quota-package infrastructure to
  the runner/account_factory (`operator_package: {clients_credit: 11}` in
  `_category.yaml`), faithful to the legacy operatorPortal `get_operator_token` +
  `create_package` + account-on-package flow. The package is created before account
  provisioning and deleted in cleanup.
- Setup seeds 10 clients via API (out-of-scope prerequisite); the 11th (cap-reaching)
  client is created via the UI as in the legacy scenario.
- Reuses `crm_bulk_helpers` for CRM list navigation, client selection and bulk delete
  (single CRM implementation).
- All 5 legacy assertions preserved: quota system notification, upgrade dialog on
  create, upgrade dialog on import, new-client dialog banner, import wizard opens.

## 2026-06-09 — Stabilization (stress hardening)
- Freed-quota propagation through the billing/quota system can occasionally exceed a
  minute; widened the bounded freed-quota retry budget (`QUOTA_FREE_ATTEMPTS` 6 -> 12,
  each wait still capped at the 5s UI policy) so the rare slow tail is absorbed. The
  common case still resolves in 1-2 attempts, so average runtime is unchanged.
- Fixed a frame-resolution race on the new-client dialog banner: the clients list
  reloads right after the dashboard round-trip, so the outer Angular iframe is briefly
  re-attaching when the banner is asserted (Playwright failed "waiting for frame" even
  though the banner was rendered). The banner visibility is now polled inside the same
  frame-tolerant loop that opens the form, so we only return once both the form and
  banner are stably visible.
