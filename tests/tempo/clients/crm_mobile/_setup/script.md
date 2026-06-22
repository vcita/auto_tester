# Setup: CRM Mobile - Detailed Script

## Initial State
- Isolated account auto-created by the runner (account_profile: isolated).
- `context["username"]` / `context["password"]` hold the owner credentials.

## Actions

### Step 1: Log in as the owner
- **Action**: Call function
- **Function**: fn_login
- **Parameters**: username = context["username"], password = context["password"]
- **Wait for**: dashboard (handled inside fn_login)

### Step 2: Seed 10 clients via API
- **Action**: API seed (legacy `user creates new clients via API | crm_mobile_clients.csv |`)
- **Helper**: `crm_mobile_helpers.seed_csv_clients(context, seq)`
- **Detail**: loops `account_api.create_client(context, first, last, email)` over the 10
  CSV rows (`first1 last1` .. `first10 last10`, row 4 first name `no-tag`). `seq` is a
  per-run suffix that keeps emails unique (the legacy `[seq]` token). CSV tags are NOT
  seeded — the only tag-using step is commented out / out of scope.

**VERIFIED PLAYWRIGHT CODE** (pattern reused from crm_tabs_management/_setup + crm_filters):
```python
seq = str(int(time.time()))
clients = seed_csv_clients(context, seq)
assert len(clients) == 10
context["crm_mobile_seq"] = seq
```

- **How verified**: same `account_api.create_client` (`POST /platform/v1/clients`) path
  used by crm_filters / crm_tabs_management setups, which are stable 10/10.
- **Save to context**: crm_mobile_seq

## Success Verification
- fn_login lands on the dashboard.
- 10 clients created (len check).
