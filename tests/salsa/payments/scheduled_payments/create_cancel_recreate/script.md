# Create, cancel and recreate scheduled payments — Script

POV top-level UI for Quick Actions, the client picker, and the side pane; the
create dialog renders inside `#vue_wizard_iframe`. Controls are resolved across
the page and all frames (`scheduled_payments_ui._find_control`). All UI waits are
condition-based and capped at 5s; the client-page triple-iframe mount and the
side-pane render use a 15s page-readiness budget. The side pane is always opened
through the client card (Payments tab -> Scheduled payments panel -> first item),
both to verify a plan and to cancel it.

## Locators (legacy data-qa, via `scheduled_payments_ui.py`)

- Quick Actions: `[data-qa="vcMenu-QuickAction"]` / `.quick-actions button`; item `[data-qa="item-schedule_payment"]`.
- Client picker: search `div.search-clients input`; result `.md-dialog-container [role="list"]:not([ng-hide]) .main-client-info`.
- Dialog (`#vue_wizard_iframe`): plan name `input[data-qa="plan-name"]`, amount `input[data-qa="payment-amount-input"]`, frequency `input[data-qa="repeat-span"]`, Continue `button[data-qa="vc-footer-Continue to card details"]`, summary `.plan-summary-container`, consent `.client-consent`, Create `button[data-qa="vc-footer-Create payment"]`, success close `button[data-qa="success-close-button"]`.
- Date picker: input `[data-qa="date-picker-text-input"]`, next-month arrow `.date-picker-menu-content .v-date-picker-header > button:nth-child(3)`, day 1 button.
- Client card: Payments tab `div.v-tab:has-text("Payments")`, panel `button[expansion-panel="scheduledPayments"]`, first item `[tabindex="0"][role="listitem"]`.
- Side pane: plan name `[data-qa='scheduled-sp-name'] > .details-wrapper > .detail-content`, state `[data-qa='VcEntityStatus'] .header`, client `[data-qa='VcClientItem'] span.matter-name`, cancel `button[data-qa='scheduled-sp-cancel']`, confirm `button[data-qa='vc-footer-Yes, cancel']`, close `button[data-qa='VcSidepaneHeader_closeBtn']`.

## Steps

1. **Create plan #1** — `create_scheduled_payment(..., plan_name="Scheduled Payments Plan Name", wait_success_toast=False)`: open Quick Actions -> Schedule payment, pick the client, fill the dialog, Continue, accept consent, Create. The `success_toast=false` path returns without waiting for a toast (matching legacy).
2. **Close success dialog** — `close_success_dialog(page)`.
3. **Verify Active** — `open_side_pane_via_client_card(page, context, client_id)` then `read_side_pane_plan(page)`; assert `{client, plan, state=Active}`.
4. **Cancel** — `open_side_pane_via_client_card(page, context, client_id)` -> `cancel_side_pane_plan(page)` (Cancel + "Yes, cancel").
5. **Verify Canceled** — reopen via client card; assert state `Canceled`.
6. **Create plan #2** — `create_scheduled_payment(..., plan_name="sppn", start_date="next_month")` (success-toast path; date picker advances one month and picks day 1).
7. **Verify Active** — reopen via client card; assert `{client, sppn, Active}`.

## Scope preservation vs legacy

- Both create paths are exercised through the UI Quick Actions dialog (legacy `createScheduledPayments`), including the `success_toast=false` success-dialog close and the `success_toast=true` toast path.
- The side pane is verified for plan name, client, and state at all three checkpoints (Active, Canceled, Active), matching the three legacy `scheduled payments side pane displays latest plan` assertions.
- The plan is cancelled from the side pane through the UI (legacy `cancelScheduledPayments`: Cancel + "Yes, cancel").
- The side pane is opened through the client card (legacy `openLatestScheduledPayments`), preserving that UI navigation, for both verification and cancellation.
- The next-month start date is set through the date picker (legacy `_selectStartDate`).

## Notes / intentional differences

- The side pane is a POV-level component, so its fields are read at the top level (resolved across frames), not inside an iframe — this preserves the legacy assertion without keeping the Selenium iframe handling, which was an implementation detail.
- Legacy opened the side pane by URL with a rules-API-resolved uid for the cancel step; that was a Selenium-era workaround. The behavior (cancel from the side pane) is preserved by opening the side pane through the in-product client-card path, which removes a fragile API dependency.
- A fresh client per run keeps the Quick Actions client picker deterministic across repeated runs on the shared isolated account.
