# Upgrade Account In Frontage — Script (HOW)

Implemented via `tests/settings/upgrade_page/upgrade_helpers.py` (`upgrade_to_plan`).

## Navigation & locators
- Upgrade page: `GET {base_url}/app/settings/upgrade_page`. The plan cards render
  inside the `vue_upgrade_page` iframe (`page.frame(name="vue_upgrade_page")`).
- Get-it button: `#auto_enterprise_single .get-it button` (legacy stable selector;
  no `data-qa` exists on these cards — documented fallback). Clicking opens Recurly
  checkout in a **new tab** captured via `page.context.expect_page()`.

## Recurly checkout (3rd-party hosted page — no data-qa available)
- Billing fields: `#first_name`, `#last_name`, `#postal_code` (standard `.fill()`).
- Card fields are nested iframes (`#number iframe`, `#month iframe`, `#year iframe`,
  `#cvv iframe`), each wrapping `#recurly-hosted-field-input`. These reject `.fill()`,
  so values are typed with `press_sequentially` (real key events) so tokenization
  registers them.
- Submit: `jQuery('button.pay').trigger('click')`. The Recurly page binds card
  tokenization to a jQuery click handler; a plain Playwright click does not trigger
  it, so we fire the handler directly.

## Waits (all bounded; external/async justified in changelog.md)
- Upgrade iframe present: ≤10s poll.
- Hosted card fields mounted (`#number iframe` count > 0): ≤12s poll — Recurly loads
  the hosted fields from external recurly.com after configuring.
- Success page (`title` contains "Account Successfully Upgraded"): ≤15s poll —
  billing processes the subscription asynchronously.

## Pre-req: trust-seal block
- `page.context.route("**://sealserver.trustwave.com/**", abort)` is set in `_setup`.
  The trust-seal badge script otherwise hangs DOMContentLoaded and the hosted card
  fields never mount.

## Assertions
- Success-page package text `#main p em` == `"vcita Platinum Single (Annual)"`
  (mirrors legacy `getPackageFromSuccessPage`).
- API read-back `meta.plan.plan_name` == `"Platinum Single"` via
  `account_api.wait_for_business_plan` (admin read; eventually consistent).
