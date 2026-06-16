# Set Auto-publish Setting — Steps

Migrates automation-js features/tempo/reviews.feature scenario 3
("Set review auto-publish settings").

Precondition (setup): a business created inside a directory that has an external
review site (`vcita`), plus a client for that business.

1. Log in to vcita as the in-directory business owner.
2. Select the review platform "Facebook" with platform ID "vcitainc" and save.
3. Toggle the auto-publish checkbox on and save.
4. Verify the auto-publish checkbox is checked (after reload).
5. Verify the auto-publish label shows the review site display name "vcita".
6. Verify the client's client-portal review page shows the auto-publish checkbox.
