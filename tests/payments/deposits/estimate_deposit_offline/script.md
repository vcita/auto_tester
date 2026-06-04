# Script: estimate_deposit_offline

## Setup (API)
- No mock-gateway connect: an offline deposit is never paid online (and the shared account
  already has the gateway connected from the prior CP scenario).
- `product = create_product(context, "product21", "80", "description for payable item21")`
- `estimate = create_estimate_via_api(context, "bestimate_offline", client, [product], send_email=True)`
- `create_deposit_request(context, estimate, amount="10", total="10", can_client_pay=False)`
- Resolve display title: `latest_estimate_for_client(context, client_id)["title"]`.

## Client portal flow
1. `cp_page, cp_context = open_portal(page, context, token)`
2. `open_estimate(cp_page, title)`
3. `assert_cp_deposit(cp_page, deposit_state="DUE", deposit_amount="$10.00", can_client_pay=False)`
   — only the `button[data-qa="approve"]` action is present.
4. `approve_offline(cp_page)` — approve → confirm dialog (`button.approve-button-text`).
5. `assert_offline_deposit_page(cp_page, "$10.00")` — `.offline-deposit-container .deposit-amount`.
6. `goto_estimates_list(cp_page, context, token, done_tab=True)` then `open_estimate(cp_page, title)`.
7. `assert_cp_deposit(cp_page, deposit_state="OFFLINE", deposit_amount="$10.00")`.
8. Close `cp_context`.
