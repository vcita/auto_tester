# Upgrade Account With Long Country Name — Script (HOW)

Same upgrade flow as `upgrade_in_frontage`, shared via
`tests/settings/upgrade_page/upgrade_helpers.py` (`upgrade_to_plan`). The only
differences are the account's long country name (set at creation via the isolated
`account_profile.country_name`) and the customer last name on the card form.

## Navigation & locators
- Upgrade page: `GET {base_url}/app/settings/upgrade_page`, plan cards inside the
  `vue_upgrade_page` iframe; get-it button `#auto_enterprise_single .get-it button`.
  Clicking opens Recurly checkout in a new tab.

## Recurly checkout (3rd-party hosted page — no data-qa)
- `#first_name` = "Automation", `#last_name` = "long country", `#postal_code` = 34241.
- Card fields are nested iframes typed with `press_sequentially`.
- Submit via `jQuery('button.pay').trigger('click')`.

## Waits (bounded; external/async — see changelog.md)
- Upgrade iframe ≤10s; hosted-field mount ≤12s; success page ≤15s.

## Pre-req: trust-seal block
- `page.context.route("**://sealserver.trustwave.com/**", abort)` set in `_setup`.

## Assertions
- Success-page package text `#main p em` == `"vcita Platinum Single (Annual)"`.
  (No business-plan API assertion in this scenario — matches the legacy scenario,
  which asserts only the package on the success page.)
