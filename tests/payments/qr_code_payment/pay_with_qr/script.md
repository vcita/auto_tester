# Script: pay_with_qr

Helpers in `tests/payments/qr_code_payment/qr_code_payment_helpers.py`. Mock gateway
via `tests/payments/tips_settings/tips_gateway.connect_mock_gateway`.

## Constants
- `EXPECTED_AMOUNT = "$100.00"`, `EXPECTED_TYPE = "Credit Card (Online)"`
- `payment_name = f"Payment for Sale #1 - {service_name}"`, `items = [service_name]`
- `service_name` / `client_name` / `client_first` come from setup context.

## Flow
1. `connect_mock_gateway(page, context)` — back-office payment providers, connect mock (prerequisite UI).
2. `grab_qr_link(page, context, service_name, client_name)`:
   Quick Actions (`vcMenu-QuickAction`) -> `VcLargeQuickAction-point_of_sale` -> client picker
   (`_select_client`); Services catalog tab `VcTabs-tab-content-0`, hover `catalog-item-{service}`
   and click nested `add-item`; `checkout-actions-activator` -> `checkout-action-qr`; read the
   `data-link` attribute from `.payment-content`.
3. `pay_via_link(page, link)`: fresh browser context (the "another tab"); `goto(link)`; wait
   `.continue-btn`; raise z-index of `.v-dialog__content--active`; click continue -> mock popup
   (`expect_page`), submit `button[type=submit]`, popup closes; confirm
   `.done-loading[data-qa='payment-success-page']` + `span.briliant`; close the context.
4. `assert_qr_dialog_success(page)`: poll back-office QR dialog `[data-qa='payment-received']`
   (payment propagation), then click `[data-qa='vc-footer-Done']`.
5. `assert_payment_page(page, search_term=client_first, name=payment_name, amount="$100.00",
   payment_type="Credit Card (Online)", items=[service_name])`: `open_payment_by_name` +
   billing iframe scope; read name `div.summary-header h3`, amount `div.summary-header h2 span`,
   type `div.entity-summary-row .icon-v + div span.caption.wrap`, items `span.invoice-item-content-title`.

## Selectors / fallbacks
- POS, checkout, QR action: data-qa (`catalog-item-*`, `add-item`, `checkout-actions-activator`,
  `checkout-action-qr`). Services tab panel `VcTabs-tab-content-0` (data-qa).
- QR link container `.payment-content` (`data-link`) has no data-qa — reused from legacy; should
  get a data-qa in product code.
- CP link page (`.continue-btn`, `.v-dialog__content--active`), mock popup (`button[type=submit]`),
  mobile success (`.done-loading[data-qa='payment-success-page']`, `span.briliant`): reused legacy
  selectors (public live-site page is direct, no `#cp_iframe`).
- BO payment-page summary rows have no data-qa — reused legacy selectors; should get data-qa.

## Waits
- Element/dialog/state waits <= 5s (`FAST_UI_TIMEOUT`); POS/app mounts use `LOAD_TIMEOUT` (15s)
  page-readiness budgets (mirrors deposits POS). The QR-link read (`_read_qr_link`) polls within
  the same 15s budget because clicking "Pay with QR code" generates the sale/payment-request and
  its link server-side (async eventual consistency), not a fixed sleep.
- `NAV_TIMEOUT` (20s) only for the public link-page navigation readiness; `PAYMENT_PROPAGATE_TIMEOUT`
  (20s) only for the external mock-gateway popup round-trip and the back-office payment-received
  propagation (eventual consistency). No fixed sleeps; retries <= 2.

## Intentional deviations
- "client pays via link on mobile in another tab" -> a fresh browser context/tab. The success
  selectors are shared across viewports (same selectors PR #56 used), so behavior/assertions are
  preserved without literal mobile-device emulation.
