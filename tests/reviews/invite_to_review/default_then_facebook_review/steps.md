# Default then Facebook Review — Steps

Migrated from `automation-js/features/tempo/reviews.feature`
(scenario: *Set review settings and invite client to review*).

Precondition (from setup): an isolated account with the reviews flags enabled and a
client (`first last`) created via API (with a client-portal token).

1. The client leaves a review with text `very good` in the client portal.
2. Verify the **default** review submitted page appears (`Thanks for your review!`).
3. Verify the review `very good` shows in the client-portal conversation.
4. In back-office settings, select the review platform `Facebook` with platform id `vcitainc`.
5. The client leaves a review with text `still very good` in the client portal.
6. Verify the **Facebook** review submitted page appears (rate-on-Facebook button).
7. Verify the review `still very good` shows in the client-portal conversation.
