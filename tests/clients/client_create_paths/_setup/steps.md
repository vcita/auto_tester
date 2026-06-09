# Setup — Client Create Paths

Mirrors the legacy `client-create-new-CRM.feature` background.

## Steps
1. Log in to the isolated automatic account (the business owner).

The four client-creation channels are exercised by the test itself, so no client is
pre-created here. The business owner email (`context["username"]`) is the inbound
address used by the livesite leave-details channel.
