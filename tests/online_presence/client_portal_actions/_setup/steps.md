# Setup — Client Portal Actions

Mirrors the legacy `client-portal-actions.feature` Background:

1. **Log in to the isolated account** (legacy `Given user logged in to automatic account`).
2. **Create the verification client via API** (legacy `And user creates new client via API`)
   — `first` / `test+[seq]@vmeetme.com`. The client's portal token is captured so the
   test can open the client portal livesite as that client (`?client_jwt=<token>`) to
   verify which actions are displayed.
