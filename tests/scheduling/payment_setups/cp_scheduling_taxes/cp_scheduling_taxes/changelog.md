# Changelog — CP Scheduling With Taxes

## 2026-06-09 — Initial migration (VCITA2-14008, scenario 4/4)

Migrated `payment-setups.feature` scenario "CP Scheduling with taxes".

**Built**
- Extended `account_api.create_service_via_api` with an optional `tax_uids` (attach business
  taxes to an API service; backward-compatible).
- `_setup/test.py`: create a default-for-services 10% tax + the taxed `suggest2pay` ($100)
  service via API, log in to the business.
- `cp_scheduling_helpers.py` (new): grab the service public link, open the anonymous CP
  scheduler, assert the calendar booking summary, book through the calendar + intake form, then
  open and assert the CP meeting page. Reuses `offset_fees_checkout.vitrage_base` and a generic
  frame scanner for the `cp_iframe`.
- `test.py`: orchestrates grab → calendar (+Tax / $100.00) → book → meeting page ($100.00 / +Tax).

**Scope/quality**
- Full legacy scope preserved: public-link grab, anonymous CP scheduler calendar tax/price, the
  anonymous booking, and the CP meeting-page tax/price.

**Fixes during build (found via focused runs)**
- The copy-link dialog no longer exposes `.link-container__link`; the link is read by scanning
  all frames for the http value (text element or readonly input property value).
- CP meeting price renders `$100.00`; the legacy `m_currency=USD` is the formatter input, not
  literal page text, so the assertion checks the formatted `$100.00` rather than a "USD" token.

**Run evidence**
- 2026-06-09 focused run: PASSED (2/2), body ~36s (grab link + anonymous CP booking + meeting
  page assertions).
