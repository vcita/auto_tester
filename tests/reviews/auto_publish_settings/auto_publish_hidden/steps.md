# Auto-publish Hidden Without Review Site — Steps

Migrates automation-js features/tempo/reviews.feature scenario 2
("Auto-publish settings does not appear in review settings page").

Precondition (setup): a business created inside a directory that has **no** external
review site, plus a client for that business.

1. Log in to vcita as the in-directory business owner.
2. Verify the reviews settings page does **not** show the auto-publish checkbox
   (the page itself still renders).
3. Verify the client's client-portal review page does **not** show the auto-publish
   checkbox.
