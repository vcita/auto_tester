# Setup — Contact Form Widget

Mirrors the legacy `contact-form-widget.feature` prerequisites:

1. Log in to the isolated automatic account.
2. Create the target client via API (`first last`, email `test+<seq>@vmeetme.com`)
   and store it in context so the scenario can mark it as spam and later assert the
   client's conversation is empty.
