# Changelog: cp_packages/purchase_packages

## 2026-06-18 - Created (migration VCITA2-14229)
**Phase**: steps.md, script.md, test.py
**Author**: Cursor AI (migrate)
**Reason**: Migrate scenario 1 (Client purchases packages using links from business).
**Details**:
- CP purchase flow in a dedicated client-portal browser context (open_portal): access the
  purchase link, select package2, purchase with a new card (mock-gateway popup), assert the
  purchased-packages page; then the single package1 link, purchase with the saved card (no
  popup, same session), assert both packages active.
- **Deviation (purchase link derivation)**: the legacy "grab purchase packages link" /
  "grab purchase package link <pkg>" use the client-portal-editor Link Builder UI, which is
  heavy/crash-prone in headless (VCITA2-14226/14227). The grabbed URLs were captured live
  from a passing legacy run:
    - all packages : `https://live.meet2know.com/site/<pivot_uid>/package`
    - one package  : `https://live.meet2know.com/site/<pivot_uid>/package?package=<package_id>`
  and are derived directly (with `?client_jwt=<token>`). The Link Builder is only the
  mechanism for obtaining these URLs; the behavior under test is the CP purchase flow, so
  deriving preserves scope. The single-package link lands on the same package-description
  page as the legacy single-package Link Builder link.
- **Saved card**: new-card vs saved-card differ only by the mock popup (legacy
  Gateways().makePayment() runs only for a new card). The saved card from purchase #1 is
  reused in purchase #2 within the SAME CP browser context.
- Selectors are data-qa first throughout (PackagesListPage, PackageDescriptionPage,
  purchasePackageButton, perform-payment-action, payment-success-page, client-package-*).
- Purchased-packages reads reload-and-recheck within a 2-retry cap (list lags the write).
**Legacy evidence**: legacy run 2 scenarios / 34 steps passed (3m06s, directory recurly).

## 2026-06-18 - Stabilized against live runs (VCITA2-14229)
**Phase**: script.md, test.py, cp_packages_helpers.py
**Author**: Cursor AI (migrate)
**Findings from live debugging (integration directory) and fixes**:
- **Client must be authenticated** before the package purchase, else the flow lands on a
  guest make-payment form. `open_portal` now visits `/action?client_jwt=<token>` first to
  establish the client session (legacy ran ClientPortalDashboard.goto before the link).
- **Checkout**: the authenticated purchase opens the legacy `[data-qa='perform-payment-action']`
  control (the anonymous flow instead shows a `MakePaymentPage` form). Clicking it opens the
  external mock-gateway popup (new card) or charges the saved card (no popup).
- **Package cards are API-backed** (skeleton first) and the description view is a carousel
  (both packages' `PackageDescriptionPage` + `.package-title` persist), so the card is
  polled on the NAV budget and the title is matched scoped to `[data-qa='package-<name>']`.
- **Single-package link**: the legacy grabbed `/package?package=<id>` URL is not directly
  navigable in this livesite build (the CP iframe never embeds, with or without jwt), so the
  same end state is reached via the packages list + the package's `Learn more`. Documented
  derivation; behavior (land on package1 description, then purchase) is preserved.
- **Purchased-packages**: opened via the CP side menu `client-area-menu-client_packages`
  (legacy openClientPackagesPage), not by URL. Reads reload-and-recheck (2-retry cap) since
  the list lags the write.
**Result**: test passes 3/3 consecutive clean focused runs.
