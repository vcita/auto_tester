# Script: estimate_deposit_cp_sign

## Setup (API + BO)
- `connect_mock_gateway(page, context)` — back-office payment providers, connect mock.
- `product = create_product(context, "product21", "80", "description for payable item21")`
- `estimate = create_estimate_via_api(context, "bestimate_sign", client, [product], send_email=True, is_signature_required=True)`
- `create_deposit_request(context, estimate, amount="10", total="10", can_client_pay=True)`
- Resolve display title: `latest_estimate_for_client(context, client_id)["title"]`.

## Client portal flow
1. `cp_page, cp_context = open_portal(page, context, token)`
2. `open_estimate(cp_page, title)`
3. `assert_cp_deposit(cp_page, deposit_state="DUE", deposit_amount="$10.00", can_client_pay=True)`
4. `sign_and_pay_deposit(cp_page)` — approve-and-pay → sign canvas → approve signature → proceed → mock popup submit.
5. `assert_payment_success(cp_page, "$10.00")`
6. `goto_estimates_list(cp_page, context, token, done_tab=True)` then `open_estimate(cp_page, title)`
7. `assert_cp_deposit(cp_page, deposit_state="PAID", deposit_amount="$10.00")`
8. Close `cp_context`.

## Selectors (deposits_cp_ui.py)
- estimates menu `[data-qa="client-area-menu-estimates"]`, list `.estimates-list-page`, title `span.payment-title`, done tab `div[tab="done"]`.
- deposit `span[data-qa="deposit-description"]` / `-paid`, amount `span[data-qa="deposit-amount"]`.
- actions `button[data-qa="approve-and-pay"]`, signature `div[data-qa="signature-container"] canvas` + `button[data-qa="approve-signature"]`, proceed `[data-qa="perform-payment-action"]`, mock submit `button[type=submit]`.
- success `[data-qa='payment-success-page']`, amount `span.paymet-text`.
