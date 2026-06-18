# Script: purchase_packages

All CP UI renders inside `#cp_iframe`; helpers scan all frames (`_cp_frame_with`) because
the livesite shell can re-attach the iframe during hydration. Element waits ≤5s
(UI_TIMEOUT); CP (re)navigation, iframe boot, and the mock-gateway popup use
NAV_TIMEOUT/POPUP_TIMEOUT (20s, documented async readiness). Purchased-packages reads
reload-and-recheck within a 2-retry cap (LIST_RELOAD_ATTEMPTS=3).

Implemented in `tests/salsa/payments/cp_packages/cp_packages_helpers.py`.

### Setup: authenticated CP session
- `make_client(context)` creates the test's own client (legacy Background is per-scenario).
- `open_portal` opens a dedicated browser context and first visits the dashboard
  `{CP_VITRAGE}/site/{pivot_uid}/action?client_jwt={token}` to AUTHENTICATE the client
  session. Without this the purchase lands on a guest make-payment form; with it the
  purchase charges the logged-in client and the saved card persists across both purchases.

### Step 1: Access the purchase-packages link
- `open_packages_list` → goto `{CP_VITRAGE}/site/{pivot_uid}/package?client_jwt={token}`,
  wait for `[data-qa='PackagesListPage']`.

### Step 2: Select package2
- `select_package("package2")` → the API-backed card `[data-qa='package-package2']` loads
  after skeletons (poll on NAV budget), click its `Learn more`, assert the description page
  scoped to `[data-qa='package-package2'] .package-title` (both packages' description
  containers persist in a carousel, so the title is matched per package).

### Step 3: Purchase with a new card
- `purchase_package(new_card=True)` → click `[data-qa='purchasePackageButton']`, the
  checkout overlay opens with `[data-qa='perform-payment-action']`; clicking it opens the
  external mock-gateway popup, submit `button[type=submit]`, wait popup close, assert
  `[data-qa='payment-success-page']`.

### Step 4: Purchased-packages shows package2
- `assert_purchased_packages` → open via the CP side menu
  `[data-qa='client-area-menu-client_packages']`, wait/scroll until the expected card count
  renders, read active `[data-qa|='active-package']` / inactive `[data-qa|='inactive-package']`
  cards (title `[data-qa='client-package-title']`, credits `[data-qa='client-package-credits-text']`,
  status class `[data-qa='client-package-status-text']`). Match name/used/total/services/state.
  Expected: package2 0/2 [s2p_appointment] active.

### Step 5: Access the single package1 link
- `open_single_package` → the legacy grabbed `/package?package=<id>` URL is not directly
  navigable in this livesite build (the CP iframe never embeds), so the same end state is
  reached by opening the packages list and selecting package1's `Learn more`; assert the
  description page (package1).

### Step 6: Purchase with the saved card
- `purchase_package(new_card=False)` → same `perform-payment-action`, NO popup: the card
  saved in step 3 (same authenticated session) is charged directly; assert
  `[data-qa='payment-success-page']`.

### Step 7: Purchased-packages shows package1 + package2
- `assert_purchased_packages` expected:
  - package1 0/1 [r2p_appointment, s2p_appointment, r2p_event] active
  - package2 0/2 [s2p_appointment] active
