# CRM Mobile List - Detailed Script

## Initial State
- Owner logged in on the isolated account (from `_setup`).
- 10 clients seeded via API (from `_setup`).
- Default desktop context; this test switches to a mobile viewport first.

All CRM selectors below are the stable `data-qa` selectors that match the legacy
`newClients.js` page object exactly (`summary-text`, `VcEmptyState`, `VcTabs-tab-*`,
`CrmTable-<tab>-actionBar-searchBar`, `CrmTable-<tab>_mainClientName`,
`RolloutBottomSheet-footer-button`). The legacy `@mobile_web` ground-truth run passed
(1 scenario / 12 steps, 44s on directory `recurly`), and a live DOM probe under mobile
emulation confirmed every selector renders in the autotester mobile layout.

**Mobile layout note**: the mobile CRM does NOT render the desktop `.table-actions__filter`
toolbar that `crm_*_helpers.wait_for_clients_table` waits on, so those desktop helpers
cannot be reused for navigation/tab-select. `crm_mobile_helpers` provides mobile-local
`open_clients_list` / `select_tab` / counter / empty / search helpers whose readiness
signal is the active view's `summary-text` counter becoming visible. The counter/empty/
search selectors themselves are identical to the legacy page object and to the desktop
`crm_tabs_helpers`.

## Actions

### Step 1: Enable mobile emulation
- **Action**: Mobile-emulate the page
- **Helper**: `crm_mobile_helpers.set_mobile_viewport(page)`
- **Detail**: legacy `@mobile_web` used Chrome mobile-emulation (`deviceName: 'Nexus 5'`),
  which applies mobile device metrics + touch + a mobile user-agent together. A plain
  `set_viewport_size` at 390px was NOT enough — vcita kept the desktop layout (sidebar)
  mounted. The helper replicates Nexus 5 emulation via CDP
  (`Emulation.setDeviceMetricsOverride` with `mobile: true`, `setTouchEmulationEnabled`,
  `setUserAgentOverride`). The runner builds the context with `no_viewport=True`, so this
  per-page emulation takes effect. NEW pattern (no prior project precedent). Applied before
  navigation so the mobile CRM + welcome bottom-sheet mount on load.

**VERIFIED PLAYWRIGHT CODE**:
```python
set_mobile_viewport(page)
```

### Step 2: Open the CRM clients list
- **Action**: Navigate to `/app/clients` (legacy newClients.goto)
- **Helper**: `crm_mobile_helpers.open_clients_list(page)` (mobile-local)
- **Wait for**: `/app/clients` + the active view's `summary-text` counter visible
  (mobile readiness signal; desktop `.table-actions__filter` is absent in mobile).

**VERIFIED PLAYWRIGHT CODE**:
```python
open_clients_list(page)
```

### Step 3: Close the CRM mobile welcome modal
- **Action**: Click
- **Target**: welcome bottom-sheet footer button

**LOCATOR DECISION**:

| Option | Pros | Cons |
|--------|------|------|
| `[data-qa="RolloutBottomSheet-footer-button"]` | Stable data-qa, exact legacy selector | none |
| text "Got it"/"Close" | readable | label varies, not entity-agnostic |

**CHOSEN**: `[data-qa="RolloutBottomSheet-footer-button"]` — exact legacy
`newClients.closeCrmMobileWelcomeModal` selector, stable data-qa.

**VERIFIED PLAYWRIGHT CODE**:
```python
close_crm_mobile_welcome_modal(page)
```

- **How verified**: legacy ground-truth run closed this modal successfully on a fresh
  account; selector copied verbatim from the legacy page object.
- **Wait for**: modal footer button visible (5s), click, then hidden (5s).

### Step 4: Select "New inquiries" then "All" tab
- **Action**: Click tab x2
- **Helper**: `crm_mobile_helpers.select_tab(page, name)`
- **Detail**: both switches kept — switching tabs buys the seeker indexing time for the
  freshly API-seeded clients (legacy comment: "switching between tabs to give seeker more
  time to index new clients").

**VERIFIED PLAYWRIGHT CODE**:
```python
select_tab(page, "New inquiries")
select_tab(page, "All")
```

- **Wait for**: clients table re-renders after each tab click (inside select_tab).

### Step 5: Verify counter "10 CLIENTS"
- **Action**: Assert (bounded poll)
- **Helper**: `crm_mobile_helpers.assert_clients_counter(page, "10 CLIENTS")`
- **Target**: `.v-window-item--active [data-qa="summary-text"]` (legacy filteredClientsCounter)

**VERIFIED PLAYWRIGHT CODE**:
```python
assert_clients_counter(page, "10 CLIENTS")
```

### Step 6: Search "first7" in the "All" tab
- **Action**: Type + assert rows (bounded re-search ≤ SEARCH_ATTEMPTS for index lag)
- **Helper**: `crm_mobile_helpers.search_in_tab(page, "All", "first7", ["first7 last7"])`
- **Target**: `[data-qa="CrmTable-All-actionBar-searchBar"]`; rows from matter-name cells.

**VERIFIED PLAYWRIGHT CODE**:
```python
search_in_tab(page, "All", "first7", ["first7 last7"])
```

### Step 7: Verify counter "1 CLIENTS"
- **Action**: Assert (bounded poll)
- **Helper**: `crm_mobile_helpers.assert_clients_counter(page, "1 CLIENTS")`

**VERIFIED PLAYWRIGHT CODE**:
```python
assert_clients_counter(page, "1 CLIENTS")
```

### Step 8: Select "New inquiries" tab
- **Action**: Click tab
- **Helper**: `select_tab(page, "New inquiries")`

**VERIFIED PLAYWRIGHT CODE**:
```python
select_tab(page, "New inquiries")
```

### Step 9: Verify CRM table empty state
- **Action**: Assert visible
- **Helper**: `crm_mobile_helpers.assert_empty_state(page)`
- **Target**: `.v-window-item--active [data-qa="VcEmptyState"]` (legacy getCrmTableEmptyState)

**VERIFIED PLAYWRIGHT CODE**:
```python
assert_empty_state(page)
```

### Step 10: Verify counter "0 CLIENTS"
- **Action**: Assert (bounded poll)
- **Helper**: `crm_mobile_helpers.assert_clients_counter(page, "0 CLIENTS")`

**VERIFIED PLAYWRIGHT CODE**:
```python
assert_clients_counter(page, "0 CLIENTS")
```

## Success Verification
- Welcome modal hidden after close.
- Counter "10 CLIENTS" on All, "1 CLIENTS" after first7 search (row "first7 last7"),
  "0 CLIENTS" + empty state on New inquiries.
