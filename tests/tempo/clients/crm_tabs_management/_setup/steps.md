# Setup: CRM Tabs Management

Prepare an isolated account with a single self-client so the CRM tabs scenario has
deterministic data (mirrors the legacy Background: create account, leave details in
livesite as the owner, log in).

## Steps
1. Log in to the isolated account as the owner.
2. Create one client `form_first form_last` via API using the owner's own email, so the
   CRM row renders as `form_first form_last (You as a client)` (the legacy livesite
   leave-details submission used the owner email; this is out-of-scope setup data, so it
   is created via API).
3. Book an appointment for that client via API so it counts as "recently active" (the
   legacy livesite submission registered the same recent activity).
