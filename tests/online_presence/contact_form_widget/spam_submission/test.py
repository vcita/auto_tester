"""Spam client contact form submission (VCITA2-14006).

Migrated from automation-js/features/tango/contact-form-widget.feature.

A client marked as spam who submits the public contact-form widget must not create
a message in the business inbox — the client's conversation stays empty.
"""

from playwright.sync_api import Page

from tests.online_presence.contact_form_widget.contact_form_helpers import (
    assert_no_message_from_client,
    mark_client_as_spam,
    submit_contact_form,
)


def test_spam_submission(page: Page, context: dict) -> None:
    cfw = context.get("cfw")
    if not cfw:
        raise ValueError("Setup context 'cfw' missing; was _setup run?")
    client_id = cfw["client_id"]

    mark_client_as_spam(page, context, client_id)
    print("  [OK] Marked target client as spam")

    submit_contact_form(page, context, cfw)
    print("  [OK] Submitted contact-form widget as the spam client")

    assert_no_message_from_client(page, context, client_id)
    print("  [OK] Business received no message from the spam client (conversation empty)")
